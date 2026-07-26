# Phase 2 Data Dictionary

## `data_processed/parcels_base.parquet`

One row per unique Tacoma parcel after multipart parcel records are dissolved and zoning is assigned by measured intersection area. Geometry is stored in EPSG:2927 (Washington State Plane South, US feet).

| Field | Type/unit | Description | Source |
|---|---|---|---|
| `parcel_id` | string | Normalized 10-digit Pierce County parcel number; canonical key | Pierce County parcels |
| `geometry` | polygon/multipolygon | Dissolved parcel geometry | Pierce County parcels |
| `TaxParcelType` | string | Base parcel, condominium, airspace condominium, or other county type | Pierce County parcels |
| `Site_Address` | string | Published site address | Pierce County parcels |
| `Land_Acres` | acres | County-published land area | Pierce County parcels |
| `parcel_area_sqft` | square feet | Area calculated from EPSG:2927 geometry | Derived |
| `parcel_acres_gis` | acres | Geometry-derived area | Derived |
| `Land_Value` | USD, current published vintage | Assessed land value | Pierce County parcels |
| `Improvement_Value` | USD, current published vintage | Assessed improvement value | Pierce County parcels |
| `Taxable_Value` | USD, current published vintage | Published taxable value | Pierce County parcels |
| `Use_Code` | string | County property-use code | Pierce County parcels |
| `Landuse_Description` | string | County property-use description | Pierce County parcels |
| `Zoning` | string | Combined zoning label including overlays | Tacoma zoning |
| `BaseZone` | string | Base zoning district used for rule lookup | Tacoma zoning |
| `ACD`, `CONS`, `HIST`, `PRD`, `PTD`, `STGPD`, `STM_IC`, `VSD`, `SH` | string | Published zoning/overlay flags | Tacoma zoning |
| `ShorelineEnviroDesignation` | string | Shoreline environment designation | Tacoma zoning |
| `RegulatoryOrdinance` | string | Published zoning ordinance reference | Tacoma zoning |
| `base_zone_composition` | string | Ordered base-zone shares, e.g. `UR2:0.750000|UR3:0.250000` | Derived from intersection area |
| `split_zoned` | boolean | More than one base zone intersects by over one square foot | Derived |
| `meaningful_split_zoned` | boolean | Second-largest base-zone share is at least 5 percent | Derived |
| `zoning_coverage_ratio` | ratio, 0–1 | Share of parcel covered by Tacoma zoning after numeric bounding | Derived |
| `partial_zoning_coverage` | boolean | Tacoma zoning covers less than 99 percent of parcel | Derived |
| `zoning_overlap_review` | boolean | Summed zoning intersections exceed parcel area by over 0.1 percent | Derived QA flag |
| `is_primary_residential_scope` | boolean | Base parcel in UR1, UR2, or UR3; initial MVP scope flag | Derived |
| `is_ur_zoning_scope` | boolean | Base parcel in UR1, UR2, or UR3 before the existing-use screen | Derived |
| `redevelopment_eligibility` | string | `candidate`, `excluded_existing_use`, or `manual_review` based on assessor use | Derived |
| `redevelopment_eligibility_reason` | string | Transparent reason for the existing-use classification | Derived |
| `building_footprint_count` | count | Distinct 2024 footprint polygons intersecting the parcel | Tacoma 2024 footprints |
| `building_footprint_sqft` | square feet | Sum of footprint area clipped to parcel geometry | Derived |
| `building_coverage_ratio_raw` | ratio | Clipped footprint area divided by parcel area before display capping | Derived |
| `building_coverage_ratio` | ratio, 0–1 | Numerically bounded building-coverage ratio | Derived |
| `housing_application_project_count` | count | Likely housing projects matched to the parcel since February 2020 | Tacoma Accela + derived grouping |
| `housing_application_permit_count` | count | Canonical Residential or Commercial permits classified as new housing, including alterations that explicitly create or legalize dwelling units | Tacoma Accela + derived classification |
| `housing_application_first_application` | UTC datetime | Earliest classified housing application | Tacoma Accela |
| `housing_application_latest_application` | UTC datetime | Latest classified housing application | Tacoma Accela |
| `housing_application_issued_project_count` | count | Estimated projects with at least one issued or completed permit | Derived |
| `housing_application_reported_units` | units, nullable | Sum of permit-scope proposed units after structured-field and description reconciliation | Derived from Tacoma Accela |
| `housing_application_types` | pipe-delimited string | Housing categories observed on the parcel | Derived |
| `housing_type__*__project_count` | count | Estimated projects by classified housing type | Derived |
| `housing_cohort__*__project_count` | count | Estimated projects in the five-year pre-policy, Home in Tacoma Year One, or current partial cohort | Derived |

## Modeled extensions

`parcels_capacity.parquet`, `parcels_physical_fit.parquet`, and `parcels_model.parquet` extend the base table with:

| Field family | Meaning |
|---|---|
| `modeled_base_capacity_units` | Simplified baseline legal unit allowance for UR1/UR2/UR3 |
| `parcel_demolition_allowance` | $0 without a mapped footprint; otherwise the documented prototype demolition allowance |
| `*_residual_land_value` | Scenario RLV after parcel-specific demolition treatment |
| `*_normalized_margin` | Feasibility margin divided by acquisition benchmark |
| `modeled_base_far`, `modeled_max_floor_area_sqft` | Baseline 3+-unit FAR and corresponding floor-area envelope |
| `capacity_overlay_review` | At least one published overlay flag requiring additional review |
| `prototype_*` | Default for-sale duplex assumptions and physical-screen results |
| `<prototype_id>__prototype_*` | Prototype-specific results for the two duplex tenures and four-unit rental rowhouse |
| `acquisition_*` | Assessed-value acquisition benchmark, source, and confidence |
| `conservative_*`, `baseline_*`, `favorable_*` | Scenario RLV, feasibility margin, and classification |
| `financial_screen_status` | Explicitly identifies illustrative results pending market validation |

`data_interim/parcel_zoning_parts.parquet` contains one record per parcel and intersecting base zone, with raw intersection area, normalized share, and within-parcel rank. It is the capacity model's authoritative zoning input.

## Web delivery artifacts

| Artifact | Purpose |
|---|---|
| `parcels_map_00.json` … `parcels_map_15.json` | MapLibre parcel geometry and map-mode attributes |
| `parcel_details_00.json.gz` … `parcel_details_15.json.gz` | Compressed on-demand evidence for the selected map section |
| `parcel_search_index.json.gz` | Compressed parcel ID, address, center point, and detail-section lookup |
| `summary.json` | Citywide funnel, prototype results, pro formas, data version, and artifact manifest |

The uncompressed citywide detail dictionary is retained only as a local QA artifact and is excluded from publication.

## Important null semantics

- A null assessor or zoning value means the source did not publish a usable value for that parcel.
- Zero building footprints means no 2024 footprint intersected the parcel; it does not prove the parcel is vacant.
- Zero housing-application projects means no classified project was matched to that parcel in the February 2020–2026 policy-period extract.
- Null `housing_application_reported_units` means the permit scope did not provide a defensible proposed-unit count. It must not be converted to zero for production analysis.
