"""Pharma preprocessing: procurement scenarios, candidate sites, constructed reference, split.

Protocol section 11 (amendment 2). Source: SCMS delivery history, direct-from-supplier
lines only. Everything here is deterministic.

A scenario is one purchase order for one product. Its candidates are N_CANDIDATES
manufacturing sites that had already delivered that product before the order date. Every
candidate feature is DERIVED from real shipment lines delivered strictly before the order
date, so nothing from the order's own outcome (or the future) enters a scenario.
`reference_slot` is a *constructed reference* (equal-weight multi-criteria score), not an
observation: the file records the site that was used, never the offers it was compared with.
"""
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from utils.datasets import ROOT, load_pharma_scms

N_CANDIDATES = 3
ACTIONS = tuple(f"candidate_{c + 1}" for c in range(N_CANDIDATES))   # slot order is hashed
CRITERIA = ("cost", "reliability", "lead_time", "logistics", "continuity")
# criterion -> (column, sign); utility = sign * column, min-max normalised over candidates
CRITERION_COLUMNS = {
    "cost": ("exp_unit_price", -1.0),
    "reliability": ("ontime_rate", 1.0),
    "lead_time": ("median_lead_days", -1.0),
    "logistics": ("freight_per_kg", -1.0),
    "continuity": ("n_product_lines", 1.0),
}
FEATURES = {
    "cost": ["exp_unit_price", "price_rel", "last_price_rel", "price_cv", "log_order_units"],
    "reliability": ["ontime_rate", "ontime_rel", "mean_late_days", "log_n_lines", "late_last5"],
    "lead_time": ["median_lead_days", "lead_rel", "lead_iqr", "log_n_lead",
                  "requested_lead_days"],
    "logistics": ["freight_per_kg", "freight_rel", "share_air", "share_freight_included",
                  "log_n_country_lines"],
    "continuity": ["log_n_product_lines", "product_share", "days_since_last", "n_countries",
                   "log_units_supplied"],
}
DEFAULT_REFERENCE = {"weights": {c: 0.2 for c in CRITERIA}, "recent_prices": 5,
                     "split": {"train": 0.5, "val": 0.1}}
PROCESSED_DIR = ROOT / "data" / "processed" / "pharma"
DATE_FORMATS = {"Scheduled Delivery Date": "%d-%b-%y", "Delivered to Client Date": "%d-%b-%y",
                "PO Sent to Vendor Date": "%m/%d/%Y"}
FREIGHT_INCLUDED = "Freight Included in Commodity Cost"


def clean_lines(raw=None):
    """Direct-from-supplier shipment lines with typed columns (no row is altered)."""
    raw = raw if raw is not None else load_pharma_scms()
    d = raw[raw["Fulfill Via"] == "Direct Drop"]
    out = pd.DataFrame({
        "line_id": d["ID"].astype(int),
        "po": d["PO / SO #"],
        "country": d["Country"],
        "site": d["Manufacturing Site"],
        "product": d["Molecule/Test Type"] + "|" + d["Dosage"] + "|" + d["Dosage Form"],
        "air": d["Shipment Mode"].isin(["Air", "Air Charter"]).astype(float),
        "freight_included": (d["Freight Cost (USD)"] == FREIGHT_INCLUDED).astype(float),
    })
    for column, name in (("PO Sent to Vendor Date", "po_date"),
                         ("Scheduled Delivery Date", "scheduled"),
                         ("Delivered to Client Date", "delivered")):
        out[name] = pd.to_datetime(d[column], format=DATE_FORMATS[column], errors="coerce")
    units_per_pack = d["Unit of Measure (Per Pack)"].astype(float)
    out["units"] = d["Line Item Quantity"].astype(float) * units_per_pack
    price = d["Pack Price"].astype(float) / units_per_pack
    out["unit_price"] = price.where(price > 0)                 # zero prices are unexplained
    delay = (out["delivered"] - out["scheduled"]).dt.days.astype(float)
    out["late"] = (delay > 0).astype(float)
    out["late_days"] = delay.clip(lower=0)
    lead = (out["delivered"] - out["po_date"]).dt.days.astype(float)
    out["lead_days"] = lead.where(lead >= 0)                   # delivery before order: unusable
    freight = pd.to_numeric(d["Freight Cost (USD)"], errors="coerce")
    weight = pd.to_numeric(d["Weight (Kilograms)"], errors="coerce")
    out["freight_per_kg"] = (freight / weight).where(weight > 0)
    return out.sort_values(["delivered", "line_id"], kind="stable").reset_index(drop=True)


def _orders(lines):
    """One row per (purchase order, product) that has an order date."""
    dated = lines[lines["po_date"].notna()].sort_values("line_id", kind="stable")
    orders = dated.groupby(["po", "product"], sort=False).agg(
        po_date=("po_date", "min"), scheduled=("scheduled", "min"), country=("country", "first"),
        units=("units", "sum"), observed_site=("site", "first"), first_line=("line_id", "min"))
    return orders.reset_index().sort_values(["po_date", "first_line"], kind="stable")


def _median(values, fallback):
    values = values[~np.isnan(values)]
    return float(np.median(values)) if len(values) else fallback


def _candidate_row(site_hist, product_hist, order, neutral, recent_prices):
    """Derived features of one candidate site from lines delivered before the order."""
    prices = product_hist["unit_price"].to_numpy()
    prices = prices[~np.isnan(prices)]
    leads = site_hist["lead_days"].to_numpy()
    leads = leads[~np.isnan(leads)]
    n = len(site_hist)
    return {
        "exp_unit_price": float(np.median(prices[-recent_prices:])),
        "last_unit_price": float(prices[-1]),
        "price_cv": float(prices.std() / prices.mean()) if len(prices) > 1 else 0.0,
        "ontime_rate": float((n - site_hist["late"].sum() + 1.0) / (n + 2.0)),
        "mean_late_days": float(site_hist["late_days"].mean()),
        "log_n_lines": float(np.log1p(n)),
        "late_last5": float(site_hist["late"].to_numpy()[-5:].mean()),
        "median_lead_days": _median(leads, neutral["lead_days"]),
        "lead_iqr": float(np.subtract(*np.percentile(leads, [75, 25]))) if len(leads) > 1 else 0.0,
        "log_n_lead": float(np.log1p(len(leads))),
        "requested_lead_days": float((order.scheduled - order.po_date).days),
        "freight_per_kg": _median(site_hist["freight_per_kg"].to_numpy(),
                                  neutral["freight_per_kg"]),
        "share_air": float(site_hist["air"].mean()),
        "share_freight_included": float(site_hist["freight_included"].mean()),
        "log_n_country_lines": float(np.log1p((site_hist["country"] == order.country).sum())),
        "n_product_lines": float(len(product_hist)),
        "log_n_product_lines": float(np.log1p(len(product_hist))),
        "days_since_last": float((order.po_date - product_hist["delivered"].iloc[-1]).days),
        "n_countries": float(site_hist["country"].nunique()),
        "log_units_supplied": float(np.log1p(product_hist["units"].sum())),
        "log_order_units": float(np.log1p(order.units)),
    }


def _select_candidates(product_hist):
    """The N_CANDIDATES sites that delivered the product most recently."""
    priced = product_hist[product_hist["unit_price"].notna()]
    by_site = priced.groupby("site").agg(last=("delivered", "max"), n=("line_id", "size"))
    if len(by_site) < N_CANDIDATES:
        return None
    by_site = by_site.reset_index().sort_values(
        ["last", "n", "site"], ascending=[False, False, True], kind="stable")
    return list(by_site["site"].head(N_CANDIDATES))


def _slot_order(sites, po, product):
    """Deterministic pseudo-random slot order, so that slot index (and with it every
    lowest-index tie-break) carries no information about the site."""
    def key(site):
        return hashlib.sha256(f"{po}|{product}|{site}".encode("utf-8")).hexdigest()
    return sorted(sites, key=key)


def normalise_utilities(raw):
    """Min-max over the candidates of each scenario; 0.5 everywhere if all tie."""
    low = raw.min(axis=-1, keepdims=True)
    span = raw.max(axis=-1, keepdims=True) - low
    safe = np.where(span > 0, span, 1.0)
    return np.where(span > 0, (raw - low) / safe, 0.5)


def criterion_utilities(table):
    """u_i(c, t) for every criterion; array (n_scenarios, n_criteria, N_CANDIDATES)."""
    raw = np.stack([sign * table[column].to_numpy().reshape(-1, N_CANDIDATES)
                    for column, sign in (CRITERION_COLUMNS[c] for c in CRITERIA)], axis=1)
    return normalise_utilities(raw)


def reference_slots(utilities, weights):
    """Constructed reference: candidate with the highest weighted criterion score
    (ties resolve to the lowest slot)."""
    w = np.array([weights[c] for c in CRITERIA], dtype=float)
    score = np.einsum("i,tic->tc", w / w.sum(), utilities)
    return np.round(score, 12).argmax(axis=1)


def assign_split(po_dates, fractions):
    """Time-ordered split on order date; orders of the same day share a split."""
    dates = pd.Series(pd.to_datetime(po_dates)).reset_index(drop=True)
    ordered = dates.sort_values(kind="stable")
    train_end = ordered.iloc[int(np.ceil(fractions["train"] * len(dates))) - 1]
    val_end = ordered.iloc[int(np.ceil((fractions["train"] + fractions["val"]) * len(dates))) - 1]
    return np.where(dates <= train_end, "train", np.where(dates <= val_end, "val", "test"))


def build_scenarios(reference=None, lines=None):
    """Long table: one row per (scenario, candidate slot)."""
    ref = {**DEFAULT_REFERENCE, **(reference or {})}
    lines = lines if lines is not None else clean_lines()
    delivered = lines["delivered"].to_numpy()
    rows, scenario_id = [], 0
    for order in _orders(lines).itertuples(index=False):
        hist = lines.iloc[:np.searchsorted(delivered, np.datetime64(order.po_date), "left")]
        product_hist = hist[hist["product"] == order.product]
        sites = _select_candidates(product_hist)
        neutral = {"lead_days": _median(hist["lead_days"].to_numpy(), np.nan),
                   "freight_per_kg": _median(hist["freight_per_kg"].to_numpy(), np.nan)}
        if sites is None or np.isnan(list(neutral.values())).any():
            continue
        for slot, site in enumerate(_slot_order(sites, order.po, order.product)):
            site_product = product_hist[(product_hist["site"] == site)
                                        & product_hist["unit_price"].notna()]
            rows.append({"scenario_id": scenario_id, "slot": slot, "site": site,
                         "po": order.po, "product": order.product, "po_date": order.po_date,
                         "country": order.country,
                         "observed_site_is_candidate": order.observed_site == site,
                         **_candidate_row(hist[hist["site"] == site], site_product, order,
                                          neutral, ref["recent_prices"])})
        scenario_id += 1
    table = pd.DataFrame(rows)
    grouped = table.groupby("scenario_id", sort=False)
    table["price_rel"] = table["exp_unit_price"] / grouped["exp_unit_price"].transform("mean")
    table["last_price_rel"] = (table["last_unit_price"]
                               / grouped["exp_unit_price"].transform("mean"))
    table["ontime_rel"] = table["ontime_rate"] - grouped["ontime_rate"].transform("mean")
    table["lead_rel"] = _ratio(table["median_lead_days"],
                               grouped["median_lead_days"].transform("mean"))
    table["freight_rel"] = _ratio(table["freight_per_kg"],
                                  grouped["freight_per_kg"].transform("mean"))
    table["product_share"] = (table["n_product_lines"]
                              / grouped["n_product_lines"].transform("sum"))
    utilities = criterion_utilities(table)
    for i, criterion in enumerate(CRITERIA):
        table[f"u_{criterion}"] = utilities[:, i, :].reshape(-1)
    slots = reference_slots(utilities, ref["weights"])
    table["reference_slot"] = np.repeat(slots, N_CANDIDATES)
    table["is_reference"] = (table["slot"] == table["reference_slot"]).astype(int)
    first = table[table["slot"] == 0]
    table["split"] = np.repeat(assign_split(first["po_date"], ref["split"]), N_CANDIDATES)
    return table


def _ratio(values, mean):
    return np.where(mean > 0, values / np.where(mean > 0, mean, 1.0), 1.0)


def reference_sensitivity(table):
    """Share of scenarios whose reference is unchanged when one criterion is dropped or
    given double weight (constructed-reference sensitivity, CLAUDE.md step 07)."""
    utilities = criterion_utilities(table)
    base = table.loc[table["slot"] == 0, "reference_slot"].to_numpy()
    out = {}
    for criterion in CRITERIA:
        for label, value in (("drop", 0.0), ("double", 2.0)):
            weights = {c: (value if c == criterion else 1.0) for c in CRITERIA}
            out[f"{label}_{criterion}"] = float((reference_slots(utilities, weights) == base).mean())
    return out


def write_processed(reference=None, out_dir=PROCESSED_DIR):
    table = build_scenarios(reference)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    table.to_csv(out_dir / "scenarios.csv", index=False, lineterminator="\n")
    first = table[table["slot"] == 0]
    observed = table.groupby("scenario_id")["observed_site_is_candidate"].any().to_numpy()
    agrees = table[table["observed_site_is_candidate"]]["is_reference"]
    meta = {
        "source": "data/raw/pharma_scms/SCMS_Delivery_History_Dataset_20150929.csv",
        "unit": "one purchase order for one product, with three candidate manufacturing sites",
        "lines_used": "Fulfill Via == 'Direct Drop'",
        "derived_columns": sorted({f for v in FEATURES.values() for f in v}
                                  | {"last_unit_price", "n_product_lines"}),
        "constructed_reference": {"column": "reference_slot", "method":
                                  "equal-weight sum of min-max normalised criteria "
                                  "(protocol section 11)", "parameters":
                                  {**DEFAULT_REFERENCE, **(reference or {})}},
        "n_scenarios": int(len(first)),
        "n_products": int(first["product"].nunique()),
        "n_sites": int(table["site"].nunique()),
        "order_dates": [str(first["po_date"].min().date()), str(first["po_date"].max().date())],
        "split_counts": first["split"].value_counts().to_dict(),
        "reference_slot_shares": {ACTIONS[k]: float(v) for k, v in
                                  first["reference_slot"].value_counts(normalize=True).items()},
        "observed_site_among_candidates": float(observed.mean()),
        "reference_equals_observed_site_when_candidate": float(agrees.mean()),
        "reference_sensitivity_share_unchanged": reference_sensitivity(table),
    }
    (out_dir / "scenarios_meta.json").write_text(json.dumps(meta, indent=2, sort_keys=True))
    return table, meta


if __name__ == "__main__":
    _, summary = write_processed()
    print(json.dumps(summary, indent=2, sort_keys=True))
