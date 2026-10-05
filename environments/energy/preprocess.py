"""Energy preprocessing: hourly scenarios, constructed reference decision, split.

Protocol sections 2-3. Everything here is deterministic. Columns named in
DERIVED are computed from real columns; `reference_action` is a *constructed
reference* (perfect-foresight daily LP under simulated battery parameters),
not an observation.
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import linprog

from utils.datasets import ROOT, energy_user_ids, load_energy

ACTIONS = ("idle", "charge", "discharge")       # index order is also the tie-break order
ACTION_SIGN = np.array([0.0, 1.0, -1.0])        # s(a): +1 charge, -1 discharge
HOURS_PER_DAY = 24

REAL = ["Hour", "PG_max", "Price", "Price_SG", "Gas_Price", "Temperature",
        "TL_Flex_Availability"]
DERIVED = ["hour_of_day", "day", "load_mw", "pv_mw", "net_demand_mw", "thermal_total",
           "price_rank_day", "sell_rank_day", "spread", "ev_home",
           "price_day_median", "sell_day_median"]
DEFAULT_REFERENCE = {"c_rate": 0.5, "round_trip_efficiency": 0.9, "soc_min": 0.1,
                     "soc_max": 0.9, "soc_start": 0.5, "idle_band": 0.05}
PROCESSED_DIR = ROOT / "data" / "processed" / "energy"


def battery_parameters(buses, reference=None):
    """Aggregate battery: energy capacity B (sum of BT) and power limit q."""
    ref = {**DEFAULT_REFERENCE, **(reference or {})}
    capacity = float(buses["BT"].sum())
    return {"capacity": capacity, "power": capacity * ref["c_rate"], **ref}


def _rank_within_day(values):
    days = values.reshape(-1, HOURS_PER_DAY)
    ranks = pd.DataFrame(days).rank(axis=1, method="average").to_numpy()
    return ((ranks - 1) / (HOURS_PER_DAY - 1)).reshape(-1)


def build_features(data):
    """Hour-level table of the real columns used plus the derived variables."""
    prof, buses, ev = data["Profiles"], data["Buses"], data["EV_Parameters"]
    users = energy_user_ids(prof)
    peak = buses.set_index("bus_i").loc[users, "PL"].to_numpy()
    df = prof[REAL].copy()
    df["hour_of_day"] = (df["Hour"] - 1) % HOURS_PER_DAY
    df["day"] = (df["Hour"] - 1) // HOURS_PER_DAY
    df["load_mw"] = prof[[f"P_{u}" for u in users]].to_numpy() @ peak
    df["pv_mw"] = prof["PG_max"].to_numpy() * float(buses["DG"].sum())
    df["net_demand_mw"] = df["load_mw"] - df["pv_mw"]
    df["thermal_total"] = prof[[f"Th_{u}" for u in users]].to_numpy().sum(axis=1)
    df["price_rank_day"] = _rank_within_day(df["Price"].to_numpy())
    df["sell_rank_day"] = _rank_within_day(df["Price_SG"].to_numpy())
    df["spread"] = df["Price"] - df["Price_SG"]
    df["ev_home"] = ev["H_10"].to_numpy()
    df["price_day_median"] = df.groupby("day")["Price"].transform("median")
    df["sell_day_median"] = df.groupby("day")["Price_SG"].transform("median")
    return df


def solve_day(net_demand, price_buy, price_sell, battery):
    """Cost-minimising battery schedule for one day; returns net charge per hour."""
    T = len(net_demand)
    B, q = battery["capacity"], battery["power"]
    eta = battery["round_trip_efficiency"] ** 0.5
    # variables: import, export, charge, discharge, soc (each of length T)
    cost = np.concatenate([price_buy, -np.asarray(price_sell), np.zeros(3 * T)])
    a_eq = np.zeros((2 * T, 5 * T))
    b_eq = np.zeros(2 * T)
    for t in range(T):
        a_eq[t, [t, T + t, 2 * T + t, 3 * T + t]] = [1, -1, -1, 1]      # power balance
        b_eq[t] = net_demand[t]
        a_eq[T + t, [4 * T + t, 2 * T + t, 3 * T + t]] = [1, -eta, 1 / eta]  # SOC dynamics
        if t > 0:
            a_eq[T + t, 4 * T + t - 1] = -1
        else:
            b_eq[T + t] = battery["soc_start"] * B
    soc_end = battery["soc_start"] * B
    bounds = ([(0, None)] * (2 * T) + [(0, q)] * (2 * T)
              + [(battery["soc_min"] * B, battery["soc_max"] * B)] * (T - 1)
              + [(soc_end, soc_end)])
    res = linprog(cost, A_eq=a_eq, b_eq=b_eq, bounds=bounds, method="highs")
    if res.status != 0:
        raise RuntimeError(f"reference LP failed: {res.message}")
    return res.x[2 * T:3 * T] - res.x[3 * T:4 * T]


def reference_actions(df, battery):
    """Constructed reference action index (see ACTIONS) for every hour."""
    out = np.zeros(len(df), dtype=int)
    band = battery["idle_band"] * battery["power"]
    for _, idx in df.groupby("day").indices.items():
        net_charge = solve_day(df["net_demand_mw"].to_numpy()[idx], df["Price"].to_numpy()[idx],
                               df["Price_SG"].to_numpy()[idx], battery)
        out[idx] = np.where(net_charge > band, 1, np.where(net_charge < -band, 2, 0))
    return out


def assign_split(day):
    """Blocked weekly split: in each 5-week cycle weeks 0-2 train, 3 val, 4 test."""
    position = (np.asarray(day) // 7) % 5
    return np.where(position <= 2, "train", np.where(position == 3, "val", "test"))


def build_scenarios(reference=None, data=None):
    data = data if data is not None else load_energy(["Buses", "Profiles", "EV_Parameters"])
    battery = battery_parameters(data["Buses"], reference)
    df = build_features(data)
    df["reference_action"] = reference_actions(df, battery)
    df["split"] = assign_split(df["day"].to_numpy())
    return df, battery


def write_processed(reference=None, out_dir=PROCESSED_DIR):
    df, battery = build_scenarios(reference)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_dir / "scenarios.csv", index=False, lineterminator="\n")
    meta = {
        "source": "data/raw/energy/Case_Study_OptiREC.xlsx",
        "unit": "one hour of the community",
        "real_columns": REAL,
        "derived_columns": DERIVED,
        "constructed_reference": {"column": "reference_action", "actions": list(ACTIONS),
                                  "method": "daily perfect-foresight LP (protocol section 3)",
                                  "simulated_battery_parameters": battery},
        "split_counts": df["split"].value_counts().to_dict(),
        "reference_action_shares": {ACTIONS[k]: float(v) for k, v in
                                    df["reference_action"].value_counts(normalize=True).items()},
    }
    (out_dir / "scenarios_meta.json").write_text(json.dumps(meta, indent=2, sort_keys=True))
    return df, battery


if __name__ == "__main__":
    frame, _ = write_processed()
    print(frame["split"].value_counts().to_dict())
