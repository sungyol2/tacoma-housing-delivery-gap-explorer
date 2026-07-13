"""Build the Phase 2 canonical Tacoma parcel base table from audited raw pages."""

from __future__ import annotations

import argparse
import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import geopandas as gpd
import numpy as np
import pandas as pd
from shapely import union_all
from shapely.geometry import Polygon

ANALYSIS_CRS = "EPSG:2927"

RESIDENTIAL_CANDIDATE_PATTERN = (
    r"DWELLING|DUPLEX|TRIPLEX|FOURPLEX|MULTI FAM|OTHER RESIDENTIAL|"
    r"SUBSIDIZED UNITS|RES LND WITH IMPROV|RETIREMENT HOME"
)
DEVELOPABLE_VACANT_USES = {"VACANT LAND UNDEVELOPED"}
CONSTRAINED_USE_PATTERN = (
    r"PARKS|OPEN SPACE|GRNBELT|SCHOOL|UNIVERSIT|COLLEGE|CEMETER|"
    r"RIGHT OF WAY|UTILITIES|DRAINFLD|CATCH BASIN|GOLF COURSE"
)


def classify_redevelopment_eligibility(land_use: pd.Series) -> pd.DataFrame:
    """Conservative assessor-use screen; ambiguous nonresidential uses remain review items."""
    normalized = land_use.fillna("").str.strip().str.upper()
    candidate = normalized.str.contains(RESIDENTIAL_CANDIDATE_PATTERN, regex=True) | normalized.isin(
        DEVELOPABLE_VACANT_USES
    )
    constrained = normalized.str.contains(CONSTRAINED_USE_PATTERN, regex=True)
    status = np.select(
        [constrained, candidate],
        ["excluded_existing_use", "candidate"],
        default="manual_review",
    )
    reason = np.select(
        [constrained, candidate, normalized.eq("") | normalized.eq("UNKNOWN")],
        ["protected_or_institutional_use", "residential_or_developable_vacant", "missing_or_unknown_use"],
        default="ambiguous_nonresidential_use",
    )
    return pd.DataFrame(
        {
            "redevelopment_eligibility": status,
            "redevelopment_eligibility_reason": reason,
        },
        index=land_use.index,
    )


def load_geojson_pages(raw_root: Path, source_id: str) -> gpd.GeoDataFrame:
    source_dir = raw_root / source_id
    manifest = json.loads((source_dir / "manifest.json").read_text(encoding="utf-8"))
    frames = [gpd.read_file(source_dir / page["file"]) for page in manifest["pages"]]
    frame = gpd.GeoDataFrame(pd.concat(frames, ignore_index=True), crs=frames[0].crs)
    if len(frame) != manifest["total_features"]:
        raise ValueError(
            f"{source_id}: loaded {len(frame)} features, manifest has "
            f"{manifest['total_features']}"
        )
    return frame


def normalize_parcel_number(value: Any) -> str | None:
    if value is None or pd.isna(value):
        return None
    digits = re.sub(r"\D", "", str(value))
    return digits if len(digits) == 10 else None


def summarize_missing(frame: pd.DataFrame, columns: list[str]) -> dict[str, dict[str, float]]:
    return {
        column: {
            "missing": int(frame[column].isna().sum()),
            "missing_pct": round(float(frame[column].isna().mean() * 100), 2),
        }
        for column in columns
    }


def assign_zoning_by_area(
    parcels: gpd.GeoDataFrame,
    zoning: gpd.GeoDataFrame,
    interim_root: Path,
) -> tuple[gpd.GeoDataFrame, pd.DataFrame]:
    """Attach dominant zoning while retaining every material zone-part area."""
    zoning = zoning.reset_index(drop=True).reset_index(names="zoning_polygon_id")
    zoning_fields = [
        "zoning_polygon_id",
        "Zoning",
        "BaseZone",
        "ACD",
        "CONS",
        "HIST",
        "PRD",
        "PTD",
        "STGPD",
        "STM_IC",
        "VSD",
        "ShorelineEnviroDesignation",
        "ShorelineZoningName",
        "AdoptionDate",
        "RegulatoryOrdinance",
        "SH",
        "zoning_polygon_area",
        "geometry",
    ]
    intersections = gpd.sjoin(
        parcels[["parcel_id", "geometry"]],
        zoning[zoning_fields],
        how="inner",
        predicate="intersects",
    )
    zone_geometries = gpd.GeoSeries(
        zoning.geometry.iloc[intersections["index_right"].to_numpy()].array,
        index=intersections.index,
        crs=ANALYSIS_CRS,
    )
    intersections["zone_part_area_sqft"] = intersections.geometry.intersection(
        zone_geometries, align=False
    ).area
    intersections = intersections.loc[intersections["zone_part_area_sqft"] > 1].copy()

    dominant = (
        intersections.sort_values(
            ["parcel_id", "zone_part_area_sqft"], ascending=[True, False]
        )
        .drop_duplicates("parcel_id", keep="first")
        .drop(columns=["geometry", "index_right"])
    )
    zone_parts = (
        intersections.groupby(["parcel_id", "BaseZone"], as_index=False)
        .agg(zone_area_sqft=("zone_part_area_sqft", "sum"))
    )
    zone_parts["zone_share"] = zone_parts["zone_area_sqft"] / zone_parts.groupby(
        "parcel_id"
    )["zone_area_sqft"].transform("sum")
    zone_parts = zone_parts.sort_values(
        ["parcel_id", "zone_area_sqft"], ascending=[True, False]
    )
    zone_parts["zone_rank"] = zone_parts.groupby("parcel_id").cumcount() + 1

    overlay_fields = ["ACD", "CONS", "HIST", "PRD", "PTD", "STGPD", "VSD", "SH"]
    intersections["zoning_overlay_any"] = intersections[overlay_fields].notna().any(axis=1)
    summary = intersections.groupby("parcel_id", as_index=False).agg(
        zoning_polygon_count=("zoning_polygon_id", "nunique"),
        zoning_covered_area_sqft=("zone_part_area_sqft", "sum"),
        zoning_overlay_any=("zoning_overlay_any", "any"),
    )
    base_summary = zone_parts.groupby("parcel_id", as_index=False).agg(
        base_zone_count=("BaseZone", "nunique"),
        dominant_zone_share=("zone_share", "max"),
    )
    second_share = (
        zone_parts.loc[zone_parts["zone_rank"].eq(2), ["parcel_id", "zone_share"]]
        .rename(columns={"zone_share": "second_zone_share"})
    )
    compositions = (
        zone_parts.assign(
            component=zone_parts.apply(
                lambda row: f"{row['BaseZone']}:{row['zone_share']:.6f}", axis=1
            )
        )
        .groupby("parcel_id")["component"]
        .agg("|".join)
        .rename("base_zone_composition")
        .reset_index()
    )
    summary = (
        summary.merge(base_summary, on="parcel_id", validate="one_to_one")
        .merge(second_share, on="parcel_id", how="left", validate="one_to_one")
        .merge(compositions, on="parcel_id", validate="one_to_one")
    )
    summary["second_zone_share"] = summary["second_zone_share"].fillna(0.0)
    summary["split_zoned"] = summary["base_zone_count"].gt(1)
    summary["meaningful_split_zoned"] = summary["second_zone_share"].ge(0.05)

    parcels = parcels.merge(dominant, on="parcel_id", how="inner", validate="one_to_one")
    parcels = parcels.merge(summary, on="parcel_id", validate="one_to_one")
    parcels = gpd.GeoDataFrame(parcels, geometry="geometry", crs=ANALYSIS_CRS)
    parcels["zoning_coverage_ratio_raw"] = (
        parcels["zoning_covered_area_sqft"] / parcels["parcel_area_sqft"]
    )
    parcels["zoning_coverage_ratio"] = parcels["zoning_coverage_ratio_raw"].clip(0, 1)
    parcels["partial_zoning_coverage"] = parcels["zoning_coverage_ratio"].lt(0.99)
    parcels["zoning_overlap_review"] = parcels["zoning_coverage_ratio_raw"].gt(1.001)
    included_ids = set(parcels.loc[parcels["zoning_coverage_ratio"].ge(0.5), "parcel_id"])
    parcels = parcels.loc[parcels["parcel_id"].isin(included_ids)].copy()
    zone_parts = zone_parts.loc[zone_parts["parcel_id"].isin(included_ids)].copy()
    interim_root.mkdir(parents=True, exist_ok=True)
    zone_parts.to_parquet(interim_root / "parcel_zoning_parts.parquet", index=False)
    return parcels, zone_parts


def build_parcels(raw_root: Path, interim_root: Path) -> tuple[gpd.GeoDataFrame, dict[str, Any]]:
    parcels = load_geojson_pages(raw_root, "pierce_tax_parcels").to_crs(ANALYSIS_CRS)
    source_bbox_count = len(parcels)
    zoning = load_geojson_pages(raw_root, "tacoma_zoning").to_crs(ANALYSIS_CRS)

    for column in ["EffectiveDate", "RetiredDate", "EditDate"]:
        parcels[column] = pd.to_datetime(parcels[column], unit="ms", errors="coerce", utc=True)
    zoning["AdoptionDate"] = pd.to_datetime(
        zoning["AdoptionDate"], unit="ms", errors="coerce", utc=True
    )

    parcels["parcel_id"] = parcels["TaxParcelNumber"].map(normalize_parcel_number)
    parcels = parcels.loc[
        parcels["parcel_id"].notna()
        & parcels["RetiredDate"].isna()
        & parcels.geometry.notna()
        & ~parcels.geometry.is_empty
    ].copy()
    parcels["geometry_valid_before"] = parcels.geometry.is_valid
    parcels.geometry = parcels.geometry.make_valid()
    duplicate_source_parts = int(parcels["parcel_id"].duplicated(keep=False).sum())
    attribute_columns = [column for column in parcels.columns if column != "geometry"]
    parcels = parcels.dissolve(
        by="parcel_id",
        as_index=False,
        aggfunc={column: "first" for column in attribute_columns if column != "parcel_id"},
    )
    parcels["parcel_area_sqft"] = parcels.geometry.area
    parcels["parcel_acres_gis"] = parcels["parcel_area_sqft"] / 43_560

    zoning = zoning.loc[zoning.geometry.notna() & ~zoning.geometry.is_empty].copy()
    zoning.geometry = zoning.geometry.make_valid()
    zoning["zoning_polygon_area"] = zoning.geometry.area
    parcels, zone_parts = assign_zoning_by_area(parcels, zoning, interim_root)
    eligibility = classify_redevelopment_eligibility(parcels["Landuse_Description"])
    parcels[eligibility.columns] = eligibility
    parcels["is_ur_zoning_scope"] = (
        parcels["TaxParcelType"].eq("Base Parcel")
        & parcels["BaseZone"].isin(["UR1", "UR2", "UR3"])
        & ~parcels["partial_zoning_coverage"]
    )
    parcels["is_primary_residential_scope"] = (
        parcels["is_ur_zoning_scope"]
        & parcels["redevelopment_eligibility"].eq("candidate")
    )

    duplicate_ids = int(parcels["parcel_id"].duplicated().sum())
    qa = {
        "source_bbox_parcel_parts": int(source_bbox_count),
        "source_parts_with_duplicated_parcel_id": duplicate_source_parts,
        "tacoma_parcels_after_zoning_clip": int(len(parcels)),
        "primary_residential_scope_parcels": int(parcels["is_primary_residential_scope"].sum()),
        "ur_zoning_scope_parcels": int(parcels["is_ur_zoning_scope"].sum()),
        "ur_scope_existing_use_status": {
            key: int(value)
            for key, value in parcels.loc[
                parcels["is_ur_zoning_scope"], "redevelopment_eligibility"
            ].value_counts().items()
        },
        "split_zoned_parcels": int(parcels["split_zoned"].sum()),
        "meaningful_split_zoned_parcels": int(parcels["meaningful_split_zoned"].sum()),
        "maximum_base_zones_on_parcel": int(parcels["base_zone_count"].max()),
        "zoning_part_rows": int(len(zone_parts)),
        "partial_zoning_coverage_parcels": int(parcels["partial_zoning_coverage"].sum()),
        "zoning_overlap_review_parcels": int(parcels["zoning_overlap_review"].sum()),
        "duplicate_parcel_ids": duplicate_ids,
        "invalid_geometry_before_repair": int((~parcels["geometry_valid_before"]).sum()),
        "invalid_geometry_after_repair": int((~parcels.geometry.is_valid).sum()),
        "nonpositive_area": int((parcels["parcel_area_sqft"] <= 0).sum()),
        "missing": summarize_missing(
            parcels,
            [
                "parcel_id",
                "Site_Address",
                "Land_Acres",
                "Land_Value",
                "Improvement_Value",
                "Taxable_Value",
                "Use_Code",
                "BaseZone",
            ],
        ),
    }
    if duplicate_ids:
        raise ValueError(f"Canonical parcel ids are not unique: {duplicate_ids} duplicates")

    interim_root.mkdir(parents=True, exist_ok=True)
    zoning.to_parquet(interim_root / "zoning.parquet", index=False)
    return parcels, qa


def add_building_coverage(
    parcels: gpd.GeoDataFrame, raw_root: Path, interim_root: Path
) -> tuple[gpd.GeoDataFrame, dict[str, Any]]:
    buildings = load_geojson_pages(raw_root, "tacoma_building_footprints_2024").to_crs(
        ANALYSIS_CRS
    )
    buildings = buildings.loc[buildings.geometry.notna() & ~buildings.geometry.is_empty].copy()
    buildings.geometry = buildings.geometry.make_valid()
    buildings["footprint_id"] = np.arange(len(buildings), dtype=np.int64)

    candidates = gpd.sjoin(
        buildings[["footprint_id", "geometry"]],
        parcels[["parcel_id", "geometry"]],
        how="inner",
        predicate="intersects",
    )[["footprint_id", "parcel_id"]]
    candidate_geoms = candidates.merge(
        buildings[["footprint_id", "geometry"]], on="footprint_id", how="left"
    ).merge(
        parcels[["parcel_id", "geometry"]].rename(columns={"geometry": "parcel_geometry"}),
        on="parcel_id",
        how="left",
    )
    intersections = gpd.GeoSeries(candidate_geoms["geometry"], crs=ANALYSIS_CRS).intersection(
        gpd.GeoSeries(candidate_geoms["parcel_geometry"], crs=ANALYSIS_CRS), align=False
    )
    candidate_geoms["footprint_area_on_parcel_sqft"] = intersections.area
    coverage = candidate_geoms.groupby("parcel_id", as_index=False).agg(
        building_footprint_count=("footprint_id", "nunique"),
        building_footprint_sqft=("footprint_area_on_parcel_sqft", "sum"),
    )
    parcels = parcels.merge(coverage, on="parcel_id", how="left", validate="one_to_one")
    parcels["building_footprint_count"] = parcels["building_footprint_count"].fillna(0).astype(int)
    parcels["building_footprint_sqft"] = parcels["building_footprint_sqft"].fillna(0.0)
    parcels["building_coverage_ratio_raw"] = (
        parcels["building_footprint_sqft"] / parcels["parcel_area_sqft"]
    )
    parcels["building_coverage_ratio"] = parcels["building_coverage_ratio_raw"].clip(0, 1)
    parcels = gpd.GeoDataFrame(parcels, geometry="geometry", crs=ANALYSIS_CRS)

    interim_root.mkdir(parents=True, exist_ok=True)
    buildings.to_parquet(interim_root / "building_footprints.parquet", index=False)
    qa = {
        "building_features": int(len(buildings)),
        "parcel_building_intersections": int(len(candidates)),
        "parcels_with_buildings": int((parcels["building_footprint_count"] > 0).sum()),
        "coverage_above_100_pct_by_more_than_tolerance": int(
            (parcels["building_coverage_ratio_raw"] > 1.000001).sum()
        ),
    }
    return parcels, qa


def _largest_polygon_area(geometry: Any) -> float:
    if geometry is None or geometry.is_empty:
        return 0.0
    if isinstance(geometry, Polygon):
        return float(geometry.area)
    return float(max((part.area for part in geometry.geoms if isinstance(part, Polygon)), default=0.0))


def add_critical_area_constraints(
    parcels: gpd.GeoDataFrame, raw_root: Path, interim_root: Path
) -> tuple[gpd.GeoDataFrame, dict[str, Any]]:
    """Apply generalized City critical-area mapping before physical-fit screening.

    Mapped geometry is a planning screen, not a site delineation. The model removes
    mapped constrained geometry, retains the largest contiguous residual polygon,
    and distinguishes parcels screened out from parcels requiring review.
    """
    steep = load_geojson_pages(raw_root, "tacoma_steep_slopes").to_crs(ANALYSIS_CRS)
    wetlands = load_geojson_pages(raw_root, "tacoma_wetland_inventory").to_crs(ANALYSIS_CRS)
    biodiversity = load_geojson_pages(raw_root, "tacoma_biodiversity_areas").to_crs(ANALYSIS_CRS)
    flood = load_geojson_pages(raw_root, "tacoma_flood_insurance_study_2017").to_crs(
        ANALYSIS_CRS
    )
    protected_water = load_geojson_pages(
        raw_root, "tacoma_protected_waters_buffer"
    ).to_crs(ANALYSIS_CRS)

    layers = {
        "steep_slope_40pct": steep.loc[steep["slopecategory"].str.startswith("Over 40", na=False)],
        "wetland": wetlands.loc[wetlands["Status"].isin(["Known", "High Probability"])],
        "biodiversity": biodiversity,
        "sfha_flood": flood.loc[flood["sfha_tf"].eq("T")],
        "protected_water_buffer": protected_water,
    }
    review_slope = steep.loc[
        steep["slopecategory"].str.startswith("25% to 40%", na=False)
    ]

    constraint_parts = []
    for constraint_type, frame in layers.items():
        clean = frame.loc[frame.geometry.notna() & ~frame.geometry.is_empty, ["geometry"]].copy()
        clean.geometry = clean.geometry.make_valid()
        clean["constraint_type"] = constraint_type
        constraint_parts.append(clean)
    constraints = gpd.GeoDataFrame(
        pd.concat(constraint_parts, ignore_index=True), geometry="geometry", crs=ANALYSIS_CRS
    )
    pairs = gpd.sjoin(
        parcels[["parcel_id", "geometry"]],
        constraints[["constraint_type", "geometry"]],
        how="inner",
        predicate="intersects",
    )[["parcel_id", "index_right"]]
    pair_geometries = pairs.merge(
        parcels[["parcel_id", "geometry"]].rename(columns={"geometry": "parcel_geometry"}),
        on="parcel_id",
        validate="many_to_one",
    )
    pair_geometries["constraint_geometry"] = constraints.geometry.iloc[
        pair_geometries["index_right"].to_numpy()
    ].array
    intersections = gpd.GeoSeries(
        pair_geometries["parcel_geometry"], crs=ANALYSIS_CRS
    ).intersection(
        gpd.GeoSeries(pair_geometries["constraint_geometry"], crs=ANALYSIS_CRS),
        align=False,
    )
    pair_geometries["intersection_geometry"] = intersections.array
    parcel_constraints = (
        pair_geometries.groupby("parcel_id")["intersection_geometry"]
        .agg(lambda values: union_all(values.to_list()))
        .rename("mapped_constraint_geometry")
        .reset_index()
    )
    parcels = parcels.merge(parcel_constraints, on="parcel_id", how="left", validate="one_to_one")
    constrained = parcels["mapped_constraint_geometry"].notna()
    parcels["mapped_constraint_overlap_sqft"] = 0.0
    parcels.loc[constrained, "mapped_constraint_overlap_sqft"] = parcels.loc[
        constrained, "mapped_constraint_geometry"
    ].map(lambda geometry: geometry.area)
    parcels["mapped_constraint_share"] = (
        parcels["mapped_constraint_overlap_sqft"] / parcels["parcel_area_sqft"]
    ).clip(0, 1)
    parcels["largest_unconstrained_area_sqft"] = parcels["parcel_area_sqft"]
    parcels.loc[constrained, "largest_unconstrained_area_sqft"] = [
        _largest_polygon_area(parcel.difference(constraint))
        for parcel, constraint in zip(
            parcels.loc[constrained, "geometry"],
            parcels.loc[constrained, "mapped_constraint_geometry"],
        )
    ]

    for constraint_type, frame in layers.items():
        hit_ids = set(
            gpd.sjoin(
                parcels[["parcel_id", "geometry"]],
                frame[["geometry"]],
                how="inner",
                predicate="intersects",
            )["parcel_id"]
        )
        parcels[f"constraint_{constraint_type}"] = parcels["parcel_id"].isin(hit_ids)
    moderate_hit_ids = set(
        gpd.sjoin(
            parcels[["parcel_id", "geometry"]],
            review_slope[["geometry"]],
            how="inner",
            predicate="intersects",
        )["parcel_id"]
    )
    parcels["constraint_moderate_slope_review"] = parcels["parcel_id"].isin(
        moderate_hit_ids
    )
    parcels["mapped_constraint_any"] = parcels["mapped_constraint_overlap_sqft"].gt(1.0)
    parcels["critical_area_screen_status"] = np.select(
        [
            parcels["mapped_constraint_any"]
            & parcels["largest_unconstrained_area_sqft"].lt(5_000),
            parcels["mapped_constraint_any"],
            parcels["constraint_moderate_slope_review"],
        ],
        ["constrained_out", "mapped_constraint_review", "moderate_slope_review"],
        default="no_mapped_constraint",
    )
    parcels["utility_easement_geometry_available"] = False
    parcels = parcels.drop(columns="mapped_constraint_geometry")

    interim_root.mkdir(parents=True, exist_ok=True)
    constraints.to_parquet(interim_root / "critical_area_constraints.parquet", index=False)
    qa_scope = parcels.loc[parcels["is_primary_residential_scope"]]
    qa = {
        "constraint_features": {key: int(len(value)) for key, value in layers.items()},
        "moderate_slope_review_features": int(len(review_slope)),
        "scope_status": {
            key: int(value)
            for key, value in qa_scope["critical_area_screen_status"].value_counts().items()
        },
        "scope_with_mapped_constraint": int(qa_scope["mapped_constraint_any"].sum()),
        "utility_easement_geometry_available": False,
        "target_6245000035": parcels.loc[
            parcels["parcel_id"].eq("6245000035"),
            [
                "mapped_constraint_overlap_sqft",
                "mapped_constraint_share",
                "largest_unconstrained_area_sqft",
                "critical_area_screen_status",
                "constraint_steep_slope_40pct",
                "constraint_wetland",
                "constraint_biodiversity",
                "constraint_sfha_flood",
                "constraint_protected_water_buffer",
            ],
        ].to_dict("records"),
    }
    return gpd.GeoDataFrame(parcels, geometry="geometry", crs=ANALYSIS_CRS), qa


def add_permit_activity(
    parcels: gpd.GeoDataFrame, raw_root: Path, processed_root: Path
) -> tuple[gpd.GeoDataFrame, dict[str, Any]]:
    permits = load_geojson_pages(raw_root, "tacoma_accela_permits")
    permits["parcel_id"] = permits["parcel_number"].map(normalize_parcel_number)
    permits["application_date"] = pd.to_datetime(
        permits["application_date"], unit="ms", errors="coerce", utc=True
    )
    permits["issued_date"] = pd.to_datetime(
        permits["issued_date"], unit="ms", errors="coerce", utc=True
    )
    permits["pull_date"] = pd.to_datetime(
        permits["pull_date"], unit="ms", errors="coerce", utc=True
    )
    residential_building = permits["permit_type"].eq("Building") & permits[
        "permit_subtype"
    ].eq("Residential")
    permits["housing_pipeline_record"] = (
        residential_building
        & permits["application_date"].ge("2021-01-01")
        & (
            permits["permit_category"].eq("New Building")
            | (
                permits["permit_category"].eq("Alteration")
                & permits["housing_units"].gt(0)
            )
        )
    )
    permits["housing_pipeline_reported_units"] = permits["housing_units"].where(
        permits["housing_pipeline_record"] & permits["housing_units"].gt(0)
    )
    parcel_ids = set(parcels["parcel_id"])
    permits["parcel_match"] = permits["parcel_id"].isin(parcel_ids)

    activity = (
        permits.loc[permits["parcel_match"] & permits["housing_pipeline_record"]]
        .groupby("parcel_id", as_index=False)
        .agg(
            housing_pipeline_record_count=("permit_number", "count"),
            housing_pipeline_first_application=("application_date", "min"),
            housing_pipeline_latest_application=("application_date", "max"),
            housing_pipeline_issued_count=("issued_date", "count"),
            housing_pipeline_reported_units=(
                "housing_pipeline_reported_units",
                lambda values: values.sum(min_count=1),
            ),
        )
    )
    parcels = parcels.merge(activity, on="parcel_id", how="left", validate="one_to_one")
    parcels["housing_pipeline_record_count"] = (
        parcels["housing_pipeline_record_count"].fillna(0).astype(int)
    )
    parcels["housing_pipeline_issued_count"] = (
        parcels["housing_pipeline_issued_count"].fillna(0).astype(int)
    )

    processed_root.mkdir(parents=True, exist_ok=True)
    permits.to_parquet(processed_root / "permits.parquet", index=False)
    qa = {
        "permit_records": int(len(permits)),
        "invalid_or_nonstandard_parcel_number": int(permits["parcel_id"].isna().sum()),
        "matched_to_tacoma_parcel": int(permits["parcel_match"].sum()),
        "housing_pipeline_records": int(permits["housing_pipeline_record"].sum()),
        "housing_pipeline_start_date": "2021-01-01",
        "housing_pipeline_records_matched": int(
            (permits["housing_pipeline_record"] & permits["parcel_match"]).sum()
        ),
        "parcel_match_pct": round(float(permits["parcel_match"].mean() * 100), 2),
        "missing_housing_units": int(permits["housing_units"].isna().sum()),
        "missing_housing_units_pct": round(float(permits["housing_units"].isna().mean() * 100), 2),
    }
    return gpd.GeoDataFrame(parcels, geometry="geometry", crs=ANALYSIS_CRS), qa


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-root", type=Path, default=Path("data_raw"))
    parser.add_argument("--interim-root", type=Path, default=Path("data_interim"))
    parser.add_argument("--processed-root", type=Path, default=Path("data_processed"))
    parser.add_argument("--qa-root", type=Path, default=Path("outputs/qa"))
    args = parser.parse_args()

    parcels, parcel_qa = build_parcels(args.raw_root, args.interim_root)
    parcels, building_qa = add_building_coverage(parcels, args.raw_root, args.interim_root)
    parcels, critical_area_qa = add_critical_area_constraints(
        parcels, args.raw_root, args.interim_root
    )
    parcels, permit_qa = add_permit_activity(parcels, args.raw_root, args.processed_root)
    parcels.to_parquet(args.processed_root / "parcels_base.parquet", index=False)

    qa = {
        "generated_at": datetime.now(UTC).isoformat(),
        "analysis_crs": ANALYSIS_CRS,
        "parcels": parcel_qa,
        "buildings": building_qa,
        "critical_areas": critical_area_qa,
        "permits": permit_qa,
    }
    args.qa_root.mkdir(parents=True, exist_ok=True)
    (args.qa_root / "parcels_base_qa.json").write_text(
        json.dumps(qa, indent=2, default=str), encoding="utf-8"
    )
    print(json.dumps(qa, indent=2, default=str))


if __name__ == "__main__":
    main()
