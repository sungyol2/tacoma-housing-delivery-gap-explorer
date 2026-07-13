from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely.geometry import box

from src.models.capacity import apply_capacity, baseline_capacity, load_rules


RULES = load_rules(Path("config/zoning_rules.yaml"))


def test_legal_lots_receive_minimum_four_units() -> None:
    area = pd.Series([1000.0, 2499.0, 2500.0])
    zone = pd.Series(["UR1", "UR2", "UR3"])
    assert baseline_capacity(area, zone, RULES).tolist() == [4, 4, 4]


def test_density_capacity_uses_zone_divisors() -> None:
    area = pd.Series([6000.0, 6000.0, 6000.0])
    zone = pd.Series(["UR1", "UR2", "UR3"])
    assert baseline_capacity(area, zone, RULES).tolist() == [4, 6, 8]


def test_capacity_is_monotonic_with_lot_area() -> None:
    area = pd.Series([3000.0, 6000.0, 9000.0])
    zone = pd.Series(["UR2", "UR2", "UR2"])
    capacity = baseline_capacity(area, zone, RULES)
    assert capacity.is_monotonic_increasing


def test_out_of_scope_zone_is_null() -> None:
    capacity = baseline_capacity(pd.Series([6000.0]), pd.Series(["C2"]), RULES)
    assert capacity.isna().all()


def test_split_zone_capacity_uses_part_areas() -> None:
    parcels = gpd.GeoDataFrame(
        {
            "parcel_id": ["1234567890"],
            "parcel_area_sqft": [6000.0],
            "BaseZone": ["UR1"],
            "is_primary_residential_scope": [True],
            "zoning_overlay_any": [False],
            "meaningful_split_zoned": [True],
        },
        geometry=[box(0, 0, 1, 1)],
        crs="EPSG:2927",
    )
    parts = pd.DataFrame(
        {
            "parcel_id": ["1234567890", "1234567890"],
            "BaseZone": ["UR1", "UR3"],
            "zone_area_sqft": [3000.0, 3000.0],
            "zone_share": [0.5, 0.5],
        }
    )
    result = apply_capacity(parcels, RULES, parts)
    assert result.loc[0, "modeled_base_capacity_units"] == 6
    assert result.loc[0, "modeled_max_floor_area_sqft"] == 6000.0
