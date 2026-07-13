import geopandas as gpd
from shapely.geometry import box

from src.models.physical_fit import screen_physical_fit


PROTOTYPE = {
    "units": 4,
    "gross_building_area_sqft": 5400,
    "minimum_screening_site_area_sqft": 5000,
}


def test_basic_fit_requires_capacity_area_and_far() -> None:
    parcels = gpd.GeoDataFrame(
        {
            "is_primary_residential_scope": [True, True, True],
            "modeled_base_capacity_units": [4, 4, 4],
            "parcel_area_sqft": [6000.0, 4000.0, 6000.0],
            "modeled_max_floor_area_sqft": [6000.0, 6000.0, 5000.0],
            "capacity_overlay_review": [False, False, False],
        },
        geometry=[box(0, 0, 1, 1), box(2, 0, 3, 1), box(4, 0, 5, 1)],
        crs="EPSG:2927",
    )
    result = screen_physical_fit(parcels, PROTOTYPE)
    assert result["prototype_basic_fit"].tolist() == [True, False, False]
    assert result["prototype_fit_status"].tolist() == [
        "basic_fit",
        "site_area_screen_failed",
        "far_screen_failed",
    ]


def test_critical_area_residual_precedes_prototype_fit() -> None:
    parcels = gpd.GeoDataFrame(
        {
            "is_primary_residential_scope": [True, True],
            "modeled_base_capacity_units": [8, 8],
            "parcel_area_sqft": [20_000.0, 20_000.0],
            # A constrained-out parcel must fail even if a coarse residual-area
            # value is large enough for the prototype threshold.
            "largest_unconstrained_area_sqft": [8_000.0, 8_000.0],
            "critical_area_screen_status": ["constrained_out", "mapped_constraint_review"],
            "modeled_max_floor_area_sqft": [16_000.0, 16_000.0],
            "capacity_overlay_review": [False, False],
        },
        geometry=[box(0, 0, 1, 1), box(2, 0, 3, 1)],
        crs="EPSG:2927",
    )
    result = screen_physical_fit(parcels, PROTOTYPE)
    assert result["prototype_basic_fit"].tolist() == [False, True]
    assert result["prototype_fit_status"].tolist() == [
        "mapped_critical_area_screen_failed",
        "basic_fit_critical_area_review",
    ]
