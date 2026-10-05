"""Dataset loading and schema validation against the raw files."""
import numpy as np
import pytest

from utils import datasets as ds


@pytest.fixture(scope="module")
def energy():
    return ds.load_energy()


def test_raw_files_match_recorded_hashes():
    assert ds.verify_raw_hashes()


def test_pharma_criteria_schema():
    df = ds.load_pharma_criteria()
    assert list(df.columns) == ["criterion_id", "main_criterion", "sub_criterion"]
    assert len(df) == 24 and not df.isna().any().any()
    assert df["main_criterion"].value_counts().to_dict() == {
        "Supplier profile": 10, "Quality": 5, "Cost": 3, "Services": 2, "Delivery": 2,
        "Overall personnel capabilities": 2}
    assert df.loc[0, "sub_criterion"] == "product price"
    assert not df["sub_criterion"].str.contains("<").any()


def test_pharma_file_has_no_numeric_observations():
    # Guards the audit finding (Gap P-1): the file is a criteria list only.
    df = ds.load_pharma_criteria()
    assert not any(df[c].dtype.kind in "iuf" for c in df.columns)


def test_energy_sheets_and_shapes(energy):
    assert set(energy) == set(ds.ENERGY_SHEETS)
    assert energy["Buses"].shape == (206, 22)
    assert energy["Profiles"].shape == (8760, 121)
    assert energy["EV_Parameters"].shape == (8760, 9)
    assert energy["Lines"].shape == (410, 14)
    assert energy["Adj_Matrix"].shape == (206, 207)


def test_energy_has_no_missing_values(energy):
    for name, df in energy.items():
        assert not df.isna().any().any(), name


def test_energy_users_consistent_across_sheets(energy):
    users = ds.energy_user_ids(energy["Profiles"])
    buses = energy["Buses"]
    assert len(users) == 55
    assert sorted(users) == sorted(buses.loc[buses["PL"] > 0, "bus_i"])
    assert int((buses["DG"] > 0).sum()) == 31
    assert int((buses["BT"] > 0).sum()) == 16
    assert int(buses["EV"].sum()) == 3


def test_energy_profile_ranges(energy):
    prof = energy["Profiles"]
    users = ds.energy_user_ids(prof)
    demand = prof[[f"P_{u}" for u in users]].to_numpy()
    assert demand.min() > 0 and demand.max() == 1.0
    assert prof["PG_max"].between(0, 1).all()
    assert (prof["Price_SG"] <= prof["Price"]).all()
    assert np.allclose(prof["Th_Factor"], prof["Beneficio"] - prof["Costo"])


def test_energy_network_is_a_tree(energy):
    adj = energy["Adj_Matrix"].iloc[:, 1:].to_numpy()
    assert (adj == adj.T).all() and adj.sum() // 2 == 205
    lines = energy["Lines"]
    assert len({tuple(sorted(t)) for t in zip(lines["fbus"], lines["tbus"])}) == 205
