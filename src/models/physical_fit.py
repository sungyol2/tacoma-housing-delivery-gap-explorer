"""Planning-level physical screens for pilot missing-middle prototypes."""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import geopandas as gpd
import numpy as np
import yaml


def minimum_rotated_width(geometry: Any) -> float:
    rectangle = geometry.minimum_rotated_rectangle
    if rectangle.is_empty or rectangle.geom_type != "Polygon":
        return 0.0
    coordinates = list(rectangle.exterior.coords)
    lengths = [
        ((coordinates[i + 1][0] - coordinates[i][0]) ** 2 + (coordinates[i + 1][1] - coordinates[i][1]) ** 2) ** 0.5
        for i in range(4)
    ]
    return min(lengths)


def load_prototype(path: Path, prototype_id: str) -> dict[str, Any]:
    config = yaml.safe_load(path.read_text(encoding="utf-8"))
    return config["prototypes"][prototype_id]


def screen_physical_fit(
    parcels: gpd.GeoDataFrame, prototype: dict[str, Any], prototype_id: str = "prototype"
) -> gpd.GeoDataFrame:
    result = parcels.copy()
    if "critical_area_screen_status" not in result:
        result["critical_area_screen_status"] = "no_mapped_constraint"
    required_units = int(prototype["units"])
    required_gross_area = float(prototype["gross_building_area_sqft"])
    minimum_site_area = float(prototype["minimum_screening_site_area_sqft"])
    minimum_width = float(prototype.get("minimum_screening_width_ft", 0))

    result["prototype_id"] = prototype_id
    result["prototype_required_units"] = required_units
    result["prototype_gross_building_area_sqft"] = required_gross_area
    result["prototype_minimum_screening_site_area_sqft"] = minimum_site_area
    result["prototype_minimum_screening_width_ft"] = minimum_width
    result["prototype_units_allowed"] = (
        result["modeled_base_capacity_units"].ge(required_units).fillna(False)
    )
    available_site_area = result.get(
        "largest_unconstrained_area_sqft", result["parcel_area_sqft"]
    )
    result["prototype_available_site_area_sqft"] = available_site_area
    result["prototype_site_area_screen"] = available_site_area.ge(minimum_site_area)
    result["prototype_parcel_width_proxy_ft"] = result.geometry.map(minimum_rotated_width)
    result["prototype_dimension_screen"] = result["prototype_parcel_width_proxy_ft"].ge(minimum_width)
    result["prototype_far_screen"] = result["modeled_max_floor_area_sqft"].ge(
        required_gross_area
    ).fillna(False)
    result["prototype_basic_fit"] = (
        result["is_primary_residential_scope"]
        & result["prototype_units_allowed"]
        & ~result["critical_area_screen_status"].eq("constrained_out")
        & result["prototype_site_area_screen"]
        & result["prototype_dimension_screen"]
        & result["prototype_far_screen"]
    )
    result["prototype_fit_status"] = np.select(
        [
            ~result["is_primary_residential_scope"],
            ~result["prototype_units_allowed"],
            result["critical_area_screen_status"].eq("constrained_out"),
            ~result["prototype_site_area_screen"],
            ~result["prototype_dimension_screen"],
            ~result["prototype_far_screen"],
            result["critical_area_screen_status"].isin(
                ["mapped_constraint_review", "moderate_slope_review"]
            ),
            result["capacity_overlay_review"],
        ],
        [
            "out_of_scope",
            "insufficient_legal_capacity",
            "mapped_critical_area_screen_failed",
            "site_area_screen_failed",
            "parcel_width_proxy_failed",
            "far_screen_failed",
            "basic_fit_critical_area_review",
            "basic_fit_overlay_review",
        ],
        default="basic_fit",
    )
    result["prototype_fit_confidence"] = np.where(
        result["prototype_basic_fit"], "low", "screening_only"
    )
    return gpd.GeoDataFrame(result, geometry="geometry", crs=parcels.crs)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input", type=Path, default=Path("data_processed/parcels_capacity.parquet")
    )
    parser.add_argument("--config", type=Path, default=Path("config/prototypes.yaml"))
    parser.add_argument("--prototype", default="duplex_for_sale")
    parser.add_argument(
        "--output", type=Path, default=Path("data_processed/parcels_physical_fit.parquet")
    )
    parser.add_argument("--qa", type=Path, default=Path("outputs/qa/physical_fit_qa.json"))
    args = parser.parse_args()

    parcels = gpd.read_parquet(args.input)
    config = yaml.safe_load(args.config.read_text(encoding="utf-8"))
    prototype_results = {}
    result = parcels.copy()
    for prototype_id, prototype in config["prototypes"].items():
        screened = screen_physical_fit(parcels, prototype, prototype_id)
        prototype_results[prototype_id] = screened
        for column in [
            "prototype_required_units",
            "prototype_gross_building_area_sqft",
            "prototype_minimum_screening_site_area_sqft",
            "prototype_minimum_screening_width_ft",
            "prototype_available_site_area_sqft",
            "prototype_parcel_width_proxy_ft",
            "prototype_units_allowed",
            "prototype_site_area_screen",
            "prototype_dimension_screen",
            "prototype_far_screen",
            "prototype_basic_fit",
            "prototype_fit_status",
            "prototype_fit_confidence",
        ]:
            result[f"{prototype_id}__{column}"] = screened[column]
    default = prototype_results[args.prototype]
    for column in [column for column in default.columns if column.startswith("prototype_")]:
        result[column] = default[column]
    result["prototype_id"] = args.prototype
    result.to_parquet(args.output, index=False)

    scoped = result.loc[result["is_primary_residential_scope"]]
    qa = {
        "generated_at": datetime.now(UTC).isoformat(),
        "prototype": args.prototype,
        "scope_parcels": int(len(scoped)),
        "basic_fit": int(scoped["prototype_basic_fit"].sum()),
        "basic_fit_pct": round(float(scoped["prototype_basic_fit"].mean() * 100), 2),
        "status": {
            key: int(value)
            for key, value in scoped["prototype_fit_status"].value_counts().items()
        },
        "prototypes": {
            prototype_id: {
                "basic_fit": int(
                    screened.loc[screened["is_primary_residential_scope"], "prototype_basic_fit"].sum()
                ),
                "basic_fit_pct": round(
                    float(
                        screened.loc[
                            screened["is_primary_residential_scope"], "prototype_basic_fit"
                        ].mean()
                        * 100
                    ),
                    2,
                ),
            }
            for prototype_id, screened in prototype_results.items()
        },
    }
    args.qa.parent.mkdir(parents=True, exist_ok=True)
    args.qa.write_text(json.dumps(qa, indent=2), encoding="utf-8")
    print(json.dumps(qa, indent=2))


if __name__ == "__main__":
    main()
