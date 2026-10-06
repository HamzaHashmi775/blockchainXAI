"""Read-only loaders for the raw datasets, with schema validation.

Schemas below were recorded from the files as downloaded on 2026-10-05
(see docs/dataset_audit.md). Loaders never write to data/raw/.
"""
import hashlib
import json
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
METADATA = ROOT / "data" / "metadata" / "datasets.json"

PHARMA_FILE = RAW / "pharma" / "Table 1.xls"
ENERGY_FILE = RAW / "energy" / "Case_Study_OptiREC.xlsx"

ENERGY_SHEETS = ("Buses", "Profiles", "EV_Parameters", "Lines", "Adj_Matrix")
ENERGY_BUS_COLUMNS = [
    "bus_i", "type", "PL", "QL", "area", "Vm", "Va", "baseKV", "zone", "Vmax", "Vmin",
    "DG", "BT", "E_BT", "P_SG_max", "P_BG_max", "Th_Load", "EV", "PSI_EV", "HP_Max",
    "Boiler_Max", "THmax",
]
ENERGY_PROFILE_COMMON = [
    "Hour", "PG_max", "PG_max_Original", "Price", "Price_SG", "Gas_Price", "Temperature",
    "TL_Flex_Availability", "Beneficio", "Costo", "Th_Factor",
]
ENERGY_LINE_COLUMNS = [
    "fbus", "tbus", "r", "x", "b", "rateA", "rateB", "rateC", "ratio", "angle", "status",
    "angmin", "angmax", "Smax",
]
ENERGY_EV_COLUMNS = [
    "H_10", "H_133", "H_177", "SOC_min_EV_10", "SOC_max_EV_10", "SOC_min_EV_133",
    "SOC_max_EV_133", "SOC_min_EV_177", "SOC_max_EV_177",
]
ENERGY_N_USERS = 55
ENERGY_N_HOURS = 8760
PHARMA_N_CRITERIA = 24
PHARMA_MAIN_CRITERIA = [
    "Cost", "Quality", "Services", "Delivery", "Supplier profile",
    "Overall personnel capabilities",
]


class SchemaError(ValueError):
    pass


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def verify_raw_hashes():
    """Check every raw file against the SHA-256 recorded at download time."""
    records = json.loads(METADATA.read_text(encoding="utf-8"))["datasets"]
    for rec in records:
        actual = sha256_file(ROOT / rec["path"])
        if actual != rec["sha256"]:
            raise SchemaError(f"{rec['path']} hash mismatch: raw file was modified")
    return True


def _strip_markup(value):
    return re.sub(r"<[^>]+>", "", value).strip() if isinstance(value, str) else value


def load_pharma_criteria():
    """Supplier-selection criteria list (Forghani et al. 2018, Table 1).

    Returns one row per sub-criterion: `criterion_id` (c1..c24), `main_criterion`,
    `sub_criterion`. The file holds criteria *names* only -- no supplier-level
    observations and no numeric values. HTML markup in the raw cells is stripped
    and the merged main-criterion cells are forward-filled; nothing else changes.
    """
    raw = pd.read_excel(PHARMA_FILE, sheet_name="Table 1", header=None, dtype=str).fillna("")
    body = raw.iloc[1:].map(_strip_markup)
    df = pd.DataFrame({
        "criterion_id": body[1].to_numpy(),
        "main_criterion": body[0].replace("", pd.NA).ffill().to_numpy(),
        "sub_criterion": body[2].to_numpy(),
    })
    if len(df) != PHARMA_N_CRITERIA:
        raise SchemaError(f"expected {PHARMA_N_CRITERIA} criteria, found {len(df)}")
    if df["criterion_id"].tolist() != [f"c{i}" for i in range(1, PHARMA_N_CRITERIA + 1)]:
        raise SchemaError("criterion ids are not c1..c24 in order")
    if list(dict.fromkeys(df["main_criterion"])) != PHARMA_MAIN_CRITERIA:
        raise SchemaError("unexpected main-criteria groups")
    return df


def energy_user_ids(profiles):
    return [int(c[2:]) for c in profiles.columns if re.fullmatch(r"P_\d+", c)]


def load_energy(sheets=ENERGY_SHEETS):
    """Load sheets of the OptiREC energy-community workbook as DataFrames."""
    data = pd.read_excel(ENERGY_FILE, sheet_name=list(sheets))
    if "Buses" in data and list(data["Buses"].columns) != ENERGY_BUS_COLUMNS:
        raise SchemaError("Buses sheet columns differ from the audited schema")
    if "Lines" in data and list(data["Lines"].columns) != ENERGY_LINE_COLUMNS:
        raise SchemaError("Lines sheet columns differ from the audited schema")
    if "EV_Parameters" in data and list(data["EV_Parameters"].columns) != ENERGY_EV_COLUMNS:
        raise SchemaError("EV_Parameters sheet columns differ from the audited schema")
    if "Profiles" in data:
        prof = data["Profiles"]
        users = energy_user_ids(prof)
        expected = (ENERGY_PROFILE_COMMON + [f"P_{u}" for u in users]
                    + [f"Th_{u}" for u in users])
        if list(prof.columns) != expected or len(users) != ENERGY_N_USERS:
            raise SchemaError("Profiles sheet columns differ from the audited schema")
        if len(prof) != ENERGY_N_HOURS or prof["Hour"].tolist() != list(range(1, ENERGY_N_HOURS + 1)):
            raise SchemaError("Profiles sheet is not a complete 8760-hour series")
    return data


PHARMA_SCMS_FILE = RAW / "pharma_scms" / "SCMS_Delivery_History_Dataset_20150929.csv"
PHARMA_SCMS_SHAPE = (10324, 33)
PHARMA_SCMS_COLUMNS = [
    "ID", "Project Code", "PQ #", "PO / SO #", "ASN/DN #", "Country", "Managed By",
    "Fulfill Via", "Vendor INCO Term", "Shipment Mode", "PQ First Sent to Client Date",
    "PO Sent to Vendor Date", "Scheduled Delivery Date", "Delivered to Client Date",
    "Delivery Recorded Date", "Product Group", "Sub Classification", "Vendor",
    "Item Description", "Molecule/Test Type", "Brand", "Dosage", "Dosage Form",
    "Unit of Measure (Per Pack)", "Line Item Quantity", "Line Item Value", "Pack Price",
    "Unit Price", "Manufacturing Site", "First Line Designation", "Weight (Kilograms)",
    "Freight Cost (USD)", "Line Item Insurance (USD)"]


def load_pharma_scms():
    """SCMS delivery history exactly as published: every cell a string, nothing coerced.

    The file mixes numbers, dates and text codes in the same columns (docs/dataset_audit.md
    section 5), so typing is left to preprocessing.
    """
    df = pd.read_csv(PHARMA_SCMS_FILE, encoding="cp1252", dtype=str, keep_default_na=False)
    if list(df.columns) != PHARMA_SCMS_COLUMNS or df.shape != PHARMA_SCMS_SHAPE:
        raise SchemaError("SCMS delivery history does not match the audited schema")
    return df
