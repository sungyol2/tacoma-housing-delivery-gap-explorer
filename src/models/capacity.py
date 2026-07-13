"""Simplified baseline legal-capacity model for Tacoma UR districts."""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import geopandas as gpd
import numpy as np
import pandas as pd
import yaml


def load_rules(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def baseline_capacity(area_sqft: pd.Series, zone: pd.Series, rules: dict[str, Any]) -> pd.Series:
    result = pd.Series(pd.NA, index=area_sqft.index, dtype="Int64")
    minimum = int(rules["shared"]["legal_lot_minimum_baseline_units"])
    for zone_name, zone_rules in rules["zones"].items():
        mask = zone.eq(zone_name) & area_sqft.notna() & area_sqft.gt(0)
        density_capacity = np.floor(
            area_sqft.loc[mask] / float(zone_rules["baseline_sqft_per_unit"])
        ).astype(int)
        result.loc[mask] = np.maximum(density_capacity, minimum)
    return result


def apply_capacity(
    parcels: gpd.GeoDataFrame,
    rules: dict[str, Any],
    zoning_parts: pd.DataFrame | None = None,
) -> gpd.GeoDataFrame:
    parcels = parcels.copy()
    far_map = {
        zone: float(values["baseline_far_3_plus_units"])
        for zone, values in rules["zones"].items()
    }
    divisor_map = {
        zone: float(values["baseline_sqft_per_unit"])
        for zone, values in rules["zones"].items()
    }
    if zoning_parts is None:
        parcels["modeled_base_capacity_units"] = baseline_capacity(
            parcels["parcel_area_sqft"], parcels["BaseZone"], rules
        )
        parcels["modeled_base_far"] = parcels["BaseZone"].map(far_map).astype("Float64")
        parcels["modeled_max_floor_area_sqft"] = (
            parcels["parcel_area_sqft"] * parcels["modeled_base_far"]
        )
        parcels["capacity_unmodeled_zone_share"] = 0.0
    else:
        parts = zoning_parts.copy()
        parcel_areas = parcels[["parcel_id", "parcel_area_sqft"]]
        parts = parts.merge(parcel_areas, on="parcel_id", how="inner", validate="many_to_one")
        parts["normalized_zone_area_sqft"] = parts["zone_share"] * parts["parcel_area_sqft"]
        parts["density_divisor"] = parts["BaseZone"].map(divisor_map)
        parts["zone_far"] = parts["BaseZone"].map(far_map)
        parts["density_equivalent"] = (
            parts["normalized_zone_area_sqft"] / parts["density_divisor"]
        ).fillna(0.0)
        parts["zone_floor_area_sqft"] = (
            parts["normalized_zone_area_sqft"] * parts["zone_far"]
        ).fillna(0.0)
        parts["unmodeled_share"] = np.where(
            parts["density_divisor"].isna(), parts["zone_share"], 0.0
        )
        modeled = parts.groupby("parcel_id", as_index=False).agg(
            modeled_density_equivalent=("density_equivalent", "sum"),
            modeled_max_floor_area_sqft=("zone_floor_area_sqft", "sum"),
            capacity_unmodeled_zone_share=("unmodeled_share", "sum"),
        )
        parcels = parcels.merge(modeled, on="parcel_id", how="left", validate="one_to_one")
        calculated = np.floor(parcels["modeled_density_equivalent"]).astype("Int64")
        parcels["modeled_base_capacity_units"] = calculated.where(
            parcels["is_primary_residential_scope"], pd.NA
        )
        minimum = int(rules["shared"]["legal_lot_minimum_baseline_units"])
        scope = parcels["is_primary_residential_scope"]
        parcels.loc[scope, "modeled_base_capacity_units"] = parcels.loc[
            scope, "modeled_base_capacity_units"
        ].clip(lower=minimum)
        parcels["modeled_base_far"] = (
            parcels["modeled_max_floor_area_sqft"] / parcels["parcel_area_sqft"]
        ).astype("Float64")
    minimum_lot_area = float(rules["shared"]["minimum_lot_area_sqft"])
    parcels["meets_standard_minimum_lot_area"] = parcels["parcel_area_sqft"].ge(
        minimum_lot_area
    )
    parcels["four_unit_legal_capacity"] = parcels["modeled_base_capacity_units"].ge(4).fillna(False)
    parcels["capacity_overlay_review"] = parcels["zoning_overlay_any"]
    parcels["capacity_model_status"] = np.where(
        parcels["is_primary_residential_scope"],
        np.where(
            parcels["meaningful_split_zoned"],
            "modeled_area_weighted_split",
            "modeled_area_weighted_single_or_sliver",
        ),
        "out_of_initial_scope",
    )
    return gpd.GeoDataFrame(parcels, geometry="geometry", crs=parcels.crs)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input", type=Path, default=Path("data_processed/parcels_base.parquet")
    )
    parser.add_argument(
        "--rules", type=Path, default=Path("config/zoning_rules.yaml")
    )
    parser.add_argument(
        "--zoning-parts",
        type=Path,
        default=Path("data_interim/parcel_zoning_parts.parquet"),
    )
    parser.add_argument(
        "--output", type=Path, default=Path("data_processed/parcels_capacity.parquet")
    )
    parser.add_argument("--qa", type=Path, default=Path("outputs/qa/capacity_qa.json"))
    args = parser.parse_args()

    parcels = gpd.read_parquet(args.input)
    zoning_parts = pd.read_parquet(args.zoning_parts)
    rules = load_rules(args.rules)
    result = apply_capacity(parcels, rules, zoning_parts)
    result.to_parquet(args.output, index=False)

    scoped = result.loc[result["is_primary_residential_scope"]]
    qa = {
        "generated_at": datetime.now(UTC).isoformat(),
        "source_rows": int(len(result)),
        "modeled_scope_rows": int(len(scoped)),
        "missing_capacity_in_scope": int(scoped["modeled_base_capacity_units"].isna().sum()),
        "capacity_below_four_in_scope": int(
            scoped["modeled_base_capacity_units"].lt(4).sum()
        ),
        "four_unit_legal_capacity": int(scoped["four_unit_legal_capacity"].sum()),
        "standard_minimum_lot_area": int(scoped["meets_standard_minimum_lot_area"].sum()),
        "overlay_review": int(scoped["capacity_overlay_review"].sum()),
        "meaningful_split_zoned": int(scoped["meaningful_split_zoned"].sum()),
        "capacity_with_unmodeled_zone_share": int(
            scoped["capacity_unmodeled_zone_share"].gt(0.05).sum()
        ),
        "capacity_by_zone": {
            zone: {
                "parcels": int(len(group)),
                "capacity_units": int(group["modeled_base_capacity_units"].sum()),
                "median_capacity": float(group["modeled_base_capacity_units"].median()),
            }
            for zone, group in scoped.groupby("BaseZone")
        },
    }
    args.qa.parent.mkdir(parents=True, exist_ok=True)
    args.qa.write_text(json.dumps(qa, indent=2), encoding="utf-8")
    print(json.dumps(qa, indent=2))


if __name__ == "__main__":
    main()
