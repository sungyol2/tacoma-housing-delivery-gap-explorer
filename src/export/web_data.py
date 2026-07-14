"""Export a compact, privacy-conscious parcel layer for the static web MVP."""

from __future__ import annotations

import argparse
import gzip
import json
from datetime import UTC, datetime
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd

PROTOTYPE_IDS = [
    "duplex_for_sale",
    "duplex_rental",
    "four_unit_rowhouse_rental",
]

POLICY_COHORTS = [
    "pre_home_in_tacoma_5yr",
    "home_in_tacoma_year_1",
    "home_in_tacoma_current_partial",
]


def _application_metrics(applications: pd.DataFrame) -> dict[str, int]:
    return {
        "permit_records": int(len(applications)),
        "projects": int(applications["housing_project_id"].nunique()),
        "reported_units": int(
            applications["housing_application_reported_units"].sum()
        ),
    }


def _annualize_metrics(metrics: dict[str, int]) -> dict[str, float]:
    return {key: round(value / 5, 1) for key, value in metrics.items()}


def _policy_comparison(applications: pd.DataFrame) -> dict[str, object]:
    pre = applications.loc[
        applications["housing_policy_cohort"].eq("pre_home_in_tacoma_5yr")
    ]
    year_one = applications.loc[
        applications["housing_policy_cohort"].eq("home_in_tacoma_year_1")
    ]
    current = applications.loc[
        applications["housing_policy_cohort"].eq("home_in_tacoma_current_partial")
    ]
    pre_totals = _application_metrics(pre)
    pre_average = _annualize_metrics(pre_totals)
    year_one_totals = _application_metrics(year_one)

    def change(metric: str) -> float | None:
        baseline = pre_average[metric]
        if not baseline:
            return None
        return round((year_one_totals[metric] / baseline - 1) * 100, 1)

    type_keys = sorted(set(applications["housing_type"].dropna()))
    return {
        "pre_policy_five_year_total": pre_totals,
        "pre_policy_annual_average": pre_average,
        "home_in_tacoma_year_one": year_one_totals,
        "change_pct": {
            metric: change(metric)
            for metric in ["permit_records", "projects", "reported_units"]
        },
        "current_partial": {
            **_application_metrics(current),
            "through": (
                current["application_date"].max().date().isoformat()
                if len(current)
                else None
            ),
        },
        "by_type": {
            housing_type: {
                "pre_policy_annual_average": _annualize_metrics(
                    _application_metrics(
                        pre.loc[pre["housing_type"].eq(housing_type)]
                    )
                ),
                "home_in_tacoma_year_one": _application_metrics(
                    year_one.loc[year_one["housing_type"].eq(housing_type)]
                ),
            }
            for housing_type in type_keys
        },
    }

PUBLISH_FIELDS = [
    "parcel_id",
    "Site_Address",
    "TaxParcelType",
    "parcel_area_sqft",
    "Land_Value",
    "Improvement_Value",
    "improvement_value_ratio",
    "site_condition_class",
    "critical_area_screen_status",
    "mapped_constraint_overlap_sqft",
    "mapped_constraint_share",
    "largest_unconstrained_area_sqft",
    "constraint_steep_slope_40pct",
    "constraint_wetland",
    "constraint_biodiversity",
    "constraint_sfha_flood",
    "constraint_protected_water_buffer",
    "constraint_moderate_slope_review",
    "utility_easement_geometry_available",
    "Landuse_Description",
    "BaseZone",
    "base_zone_composition",
    "split_zoned",
    "meaningful_split_zoned",
    "partial_zoning_coverage",
    "zoning_overlap_review",
    "building_footprint_sqft",
    "building_coverage_ratio",
    "modeled_base_capacity_units",
    "modeled_max_floor_area_sqft",
    "capacity_overlay_review",
    "capacity_unmodeled_zone_share",
    "prototype_basic_fit",
    "prototype_fit_status",
    "parcel_demolition_allowance",
    "acquisition_benchmark",
    "acquisition_source",
    "acquisition_confidence",
    "conservative_feasibility_margin",
    "conservative_required_profit",
    "conservative_residual_land_value",
    "conservative_normalized_margin",
    "conservative_feasibility_class",
    "baseline_feasibility_margin",
    "baseline_required_profit",
    "baseline_residual_land_value",
    "baseline_normalized_margin",
    "baseline_feasibility_class",
    "favorable_feasibility_margin",
    "favorable_required_profit",
    "favorable_residual_land_value",
    "favorable_normalized_margin",
    "favorable_feasibility_class",
    "financial_screen_status",
    "housing_pipeline_record_count",
    "housing_pipeline_issued_count",
    "housing_pipeline_reported_units",
    "housing_pipeline_first_application",
    "housing_pipeline_latest_application",
    "housing_application_project_count",
    "housing_application_permit_count",
    "housing_application_issued_project_count",
    "housing_application_reported_units",
    "housing_application_first_application",
    "housing_application_latest_application",
    "housing_application_types",
    "map_center_lon",
    "map_center_lat",
]

MAP_FIELDS = [
    "parcel_id",
    "BaseZone",
    "modeled_base_capacity_units",
    "improvement_value_ratio",
    "critical_area_screen_status",
    "meaningful_split_zoned",
    "housing_application_project_count",
]

for housing_type in [
    "backyard_unit",
    "houseplex_2",
    "houseplex_3_6",
    "rowhouse",
    "courtyard_cottage",
    "multiplex_7_20",
    "larger_multifamily_21_plus",
    "detached_single_unit",
    "other_uncertain_housing",
]:
    PUBLISH_FIELDS.append(f"housing_type__{housing_type}_project_count")

for cohort in [
    "pre_home_in_tacoma_5yr",
    "home_in_tacoma_year_1",
    "home_in_tacoma_current_partial",
]:
    PUBLISH_FIELDS.append(f"housing_cohort__{cohort}_project_count")

for prototype_id in PROTOTYPE_IDS:
    PUBLISH_FIELDS.extend(
        [
            f"{prototype_id}__prototype_basic_fit",
            f"{prototype_id}__prototype_fit_status",
            f"{prototype_id}__financial_screen_status",
        ]
        + [
            f"{prototype_id}__{scenario}_{suffix}"
            for scenario in ["conservative", "baseline", "favorable"]
            for suffix in [
                "required_profit",
                "residual_land_value",
                "feasibility_margin",
                "normalized_margin",
                "feasibility_class",
            ]
        ]
    )
    MAP_FIELDS.extend(
        [f"{prototype_id}__prototype_basic_fit"]
        + [f"{prototype_id}__{scenario}_feasibility_class" for scenario in ["baseline", "favorable"]]
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=Path("data_processed/parcels_model.parquet"))
    parser.add_argument("--output-dir", type=Path, default=Path("app/public/data"))
    parser.add_argument("--simplify-feet", type=float, default=8.0)
    parser.add_argument(
        "--feasibility-qa", type=Path, default=Path("outputs/qa/feasibility_qa.json")
    )
    parser.add_argument(
        "--housing-applications",
        type=Path,
        default=Path("data_processed/housing_applications.parquet"),
    )
    args = parser.parse_args()

    parcels = gpd.read_parquet(args.input)
    ur_zoning_count = int(parcels["is_ur_zoning_scope"].sum())
    ur_existing_use_status = {
        key: int(value)
        for key, value in parcels.loc[
            parcels["is_ur_zoning_scope"], "redevelopment_eligibility"
        ].value_counts().items()
    }
    housing_applications_all = pd.read_parquet(args.housing_applications)
    policy_applications = housing_applications_all.merge(
        parcels[["parcel_id", "is_ur_zoning_scope", "BaseZone"]],
        on="parcel_id",
        how="inner",
        validate="many_to_one",
    )
    policy_applications = policy_applications.loc[
        policy_applications["is_ur_zoning_scope"]
        & policy_applications["housing_policy_cohort"].isin(POLICY_COHORTS)
        & policy_applications["housing_application_status"].ne("cancelled_or_voided")
    ].copy()
    policy_comparison = {
        "all": _policy_comparison(policy_applications),
        **{
            zone: _policy_comparison(
                policy_applications.loc[policy_applications["BaseZone"].eq(zone)]
            )
            for zone in ["UR1", "UR2", "UR3"]
        },
    }

    assessed_total = parcels["Land_Value"] + parcels["Improvement_Value"]
    parcels["improvement_value_ratio"] = np.where(
        assessed_total.gt(0), parcels["Improvement_Value"] / assessed_total, None
    )
    parcels = parcels.loc[parcels["is_primary_residential_scope"]].copy()
    candidate_parcel_ids = set(parcels["parcel_id"])
    housing_applications = housing_applications_all.loc[
        housing_applications_all["parcel_id"].isin(candidate_parcel_ids)
    ].copy()
    representative_points = parcels.geometry.representative_point().to_crs("EPSG:4326")
    parcels["map_center_lon"] = representative_points.x
    parcels["map_center_lat"] = representative_points.y
    centroids = parcels.geometry.centroid
    x_breaks = np.quantile(centroids.x, [0.25, 0.5, 0.75])
    y_breaks = np.quantile(centroids.y, [0.25, 0.5, 0.75])
    parcels["map_chunk"] = np.digitize(centroids.x, x_breaks) * 4 + np.digitize(
        centroids.y, y_breaks
    )
    parcels = parcels[PUBLISH_FIELDS + ["map_chunk", "geometry"]].copy()
    for column in [
        "housing_pipeline_first_application",
        "housing_pipeline_latest_application",
        "housing_application_first_application",
        "housing_application_latest_application",
    ]:
        parcels[column] = parcels[column].apply(
            lambda value: value.isoformat() if pd.notna(value) else None
        )
    parcels.geometry = parcels.geometry.simplify(args.simplify_feet, preserve_topology=True)
    parcels = parcels.to_crs("EPSG:4326")
    parcels = parcels.replace({np.nan: None})

    args.output_dir.mkdir(parents=True, exist_ok=True)
    map_chunks = []
    for chunk_id, chunk in parcels.groupby("map_chunk", sort=True):
        filename = f"parcels_map_{int(chunk_id):02d}.json"
        map_geojson_path = args.output_dir / filename
        map_geojson_path.write_text(
            chunk[MAP_FIELDS + ["geometry"]].to_json(drop_id=True), encoding="utf-8"
        )
        map_gzip_path = args.output_dir / f"{filename}.gz"
        with gzip.open(map_gzip_path, "wb", compresslevel=9) as output:
            output.write(map_geojson_path.read_bytes())
        detail_filename = f"parcel_details_{int(chunk_id):02d}.json"
        detail_path = args.output_dir / detail_filename
        chunk_details = chunk[PUBLISH_FIELDS].set_index("parcel_id").to_dict(orient="index")
        detail_path.write_text(json.dumps(chunk_details, separators=(",", ":")), encoding="utf-8")
        detail_gzip_path = args.output_dir / f"{detail_filename}.gz"
        with gzip.open(detail_gzip_path, "wb", compresslevel=9) as output:
            output.write(detail_path.read_bytes())
        bounds = chunk.total_bounds.tolist()
        map_chunks.append(
            {
                "id": int(chunk_id),
                "file": filename,
                "gzip_file": f"{filename}.gz",
                "detail_file": detail_filename,
                "detail_gzip_file": f"{detail_filename}.gz",
                "features": int(len(chunk)),
                "bytes": map_geojson_path.stat().st_size,
                "gzip_bytes": map_gzip_path.stat().st_size,
                "detail_bytes": detail_path.stat().st_size,
                "detail_gzip_bytes": detail_gzip_path.stat().st_size,
                "bounds": bounds,
            }
        )

    details_path = args.output_dir / "parcel_details.json"
    details = parcels[PUBLISH_FIELDS].set_index("parcel_id").to_dict(orient="index")
    details_path.write_text(json.dumps(details, separators=(",", ":")), encoding="utf-8")
    details_gzip_path = args.output_dir / "parcel_details.json.gz"
    with gzip.open(details_gzip_path, "wb", compresslevel=9) as output:
        output.write(details_path.read_bytes())

    search_index = parcels[
        ["parcel_id", "Site_Address", "map_center_lon", "map_center_lat", "map_chunk"]
    ].rename(columns={"map_chunk": "chunk"}).to_dict(orient="records")
    search_path = args.output_dir / "parcel_search_index.json"
    search_path.write_text(json.dumps(search_index, separators=(",", ":")), encoding="utf-8")
    search_gzip_path = args.output_dir / "parcel_search_index.json.gz"
    with gzip.open(search_gzip_path, "wb", compresslevel=9) as output:
        output.write(search_path.read_bytes())

    scenario_funnel = {}
    for scenario in ["conservative", "baseline", "favorable"]:
        screened = parcels[parcels["prototype_basic_fit"]]
        bands = {
            key: int(value)
            for key, value in screened[f"{scenario}_feasibility_class"]
            .value_counts()
            .items()
        }
        scenario_funnel[scenario] = {
            "near_or_above_break_even_count": sum(
                bands.get(key, 0) for key in ["marginal", "moderate", "strong"]
            ),
            "margin_bands": bands,
        }
    feasibility_qa = json.loads(args.feasibility_qa.read_text(encoding="utf-8"))
    sensitivity = feasibility_qa["one_factor_sensitivity"]
    sensitivity_summary = {}
    screened = parcels.loc[parcels["prototype_basic_fit"]]
    for case, values in sensitivity.items():
        profit_rate = values["required_profit"] / values["non_land_cost"]
        parcel_non_land = (
            values["non_land_cost"]
            - values["demolition_allowance"]
            + screened["parcel_demolition_allowance"]
        )
        parcel_rlv = values["gross_revenue"] - parcel_non_land * (1 + profit_rate)
        sensitivity_summary[case] = {
            **values,
            "near_or_above_break_even_count": int(
                (parcel_rlv - screened["acquisition_benchmark"]).ge(-50_000).sum()
            ),
        }
    summary = {
        "generated_at": datetime.now(UTC).isoformat(),
        "status": "illustrative_financial_results_pending_market_validation",
        "parcel_count": int(len(parcels)),
        "ur_zoning_count": ur_zoning_count,
        "ur_existing_use_status": ur_existing_use_status,
        "basic_fit_count": int(parcels["prototype_basic_fit"].sum()),
        "scenario_funnel": scenario_funnel,
        "scenario_pro_forma": feasibility_qa["scenario_pro_forma"],
        "one_factor_sensitivity": sensitivity_summary,
        "site_condition_classes": {
            key: int(value)
            for key, value in parcels["site_condition_class"].value_counts().items()
        },
        "critical_area_status": {
            key: int(value)
            for key, value in parcels["critical_area_screen_status"].value_counts().items()
        },
        "mapped_constraint_pass_count": int(
            parcels["critical_area_screen_status"].ne("constrained_out").sum()
        ),
        "split_zoned_count": int(parcels["split_zoned"].sum()),
        "meaningful_split_zoned_count": int(parcels["meaningful_split_zoned"].sum()),
        "housing_application_project_parcel_links": int(
            parcels["housing_application_project_count"].sum()
        ),
        "housing_policy_comparison": {
            "effective_date": "2025-02-01",
            "geography_note": "Current UR parcel geography; historical zoning geometry is unavailable.",
            "status_note": "Cancelled and voided applications are excluded from the comparison.",
            "official_year_one_benchmark": {
                "permit_records": 213,
                "reported_units": 385,
                "source": "City of Tacoma Home in Tacoma Year One review",
            },
            "by_zone": policy_comparison,
        },
        "housing_applications": {
            "permit_records": int(len(housing_applications)),
            "projects": int(housing_applications["housing_project_id"].nunique()),
            "reported_units": int(
                housing_applications["housing_application_reported_units"].sum()
            ),
            "by_type": {
                key: {
                    "permit_records": int(len(group)),
                    "projects": int(group["housing_project_id"].nunique()),
                    "reported_units": int(
                        group["housing_application_reported_units"].sum()
                    ),
                }
                for key, group in housing_applications.groupby("housing_type")
            },
            "by_cohort": {
                key: {
                    "permit_records": int(len(group)),
                    "projects": int(group["housing_project_id"].nunique()),
                    "reported_units": int(
                        group["housing_application_reported_units"].sum()
                    ),
                }
                for key, group in housing_applications.groupby("housing_policy_cohort")
            },
        },
        "zones": {
            key: int(value) for key, value in parcels["BaseZone"].value_counts().items()
        },
        "baseline_feasibility_classes": {
            key: int(value)
            for key, value in parcels.loc[
                parcels["prototype_basic_fit"], "baseline_feasibility_class"
            ].value_counts().items()
        },
        "prototypes": {
            prototype_id: {
                **feasibility_qa["prototypes"][prototype_id],
                "basic_fit_count": int(parcels[f"{prototype_id}__prototype_basic_fit"].sum()),
                "scenario_funnel": {
                    scenario: {
                        "near_or_above_break_even_count": int(
                            parcels.loc[
                                parcels[f"{prototype_id}__prototype_basic_fit"],
                                f"{prototype_id}__{scenario}_feasibility_class",
                            ].isin(["marginal", "moderate", "strong"]).sum()
                        ),
                        "margin_bands": {
                            key: int(value)
                            for key, value in parcels.loc[
                                parcels[f"{prototype_id}__prototype_basic_fit"],
                                f"{prototype_id}__{scenario}_feasibility_class",
                            ].value_counts().items()
                        },
                    }
                    for scenario in ["conservative", "baseline", "favorable"]
                },
            }
            for prototype_id in PROTOTYPE_IDS
        },
        "map_chunks": map_chunks,
        "map_chunk_count": len(map_chunks),
        "map_geojson_bytes": sum(chunk["bytes"] for chunk in map_chunks),
        "map_geojson_gzip_bytes": sum(chunk["gzip_bytes"] for chunk in map_chunks),
        "details_json_bytes": details_path.stat().st_size,
        "details_json_gzip_bytes": details_gzip_path.stat().st_size,
        "detail_chunk_gzip_bytes": sum(chunk["detail_gzip_bytes"] for chunk in map_chunks),
        "search_index_bytes": search_path.stat().st_size,
        "search_index_gzip_bytes": search_gzip_path.stat().st_size,
        "geometry_simplification_feet": args.simplify_feet,
        "map_fields": MAP_FIELDS,
        "published_fields": PUBLISH_FIELDS,
    }
    (args.output_dir / "summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
