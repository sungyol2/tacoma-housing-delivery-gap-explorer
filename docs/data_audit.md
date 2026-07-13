# Phase 1 Data Availability Audit

**Audit date:** 2026-07-11  
**Status:** Initial audit and core GIS extraction complete; assessor bulk-file link extraction remains unresolved  
**Scope:** Public data needed for a Tacoma parcel-level legal-capacity, physical-fit, financial-screening, and permit-pipeline analysis.

## Preliminary readiness summary

Four core services are confirmed through live count queries:

- Pierce County tax parcels: 339,876 records countywide.
- Tacoma current zoning districts: 8,202 polygon records.
- Tacoma 2024 building footprints: 96,881 polygon records.
- Tacoma Accela permits: 109,614 point records.

This is enough to support a parcel spine, current zoning overlay, building-coverage measures, and an initial permit pipeline. The remaining critical gap is automated access to the detailed assessor tables for existing units, building age/characteristics, and sales; adopted zoning standards must also be encoded from the code rather than inferred from the GIS layer.

## Readiness matrix

| Dataset | Public metadata | Bulk/query access | Parcel join | Current assessment |
|---|---:|---:|---:|---|
| Pierce County tax parcels | Yes | Count query passed | Direct: `TaxParcelNumber` | Ready for paginated extraction |
| Pierce County assessor detail | Page and schema found | Embedded download blocked | Direct by parcel number | Critical unresolved access step |
| Tacoma zoning | Yes | Count query passed | Spatial | Ready; adoption/code interpretation still required |
| Tacoma 2024 building footprints | Yes | Count query passed | Spatial | Ready for coverage-based screening |
| Tacoma Accela permits | Yes | Count query passed | Direct + spatial/address fallback | Conditional go; `housing_units` is sparse |
| Environmental overlays | Yes, initial set | Count queries passed | Spatial | Flood and protected-water layers identified; expand only as needed |

## Confirmed source details

### Pierce County tax parcels

- Geometry: polygon
- CRS: Washington State Plane South, EPSG:2927
- Maximum records per response: 2,000
- Direct parcel key: `TaxParcelNumber` (10 characters)
- Useful published attributes: site address, land acres, land value, improvement value, taxable value, use code, land-use description, edit date
- Important limitation: parcel geometry is an administrative/cadastral representation and must not be treated as a survey.
- Modeling gap: the layer does not supply existing housing units, year built, detailed improvements, or sales history.

### Tacoma Accela permits

- Geometry: point
- Published CRS: EPSG:2927
- Maximum records per response: 1,000
- Candidate parcel key: `parcel_number`
- Useful published attributes: permit number/type/subtype/category, current status, application date, issue date, description, valuation, housing units, address, pull date
- Important limitations: no final/completion date, no explicit existing/demolished-unit fields, and parcel-key coverage has not yet been measured.
- Live null tests: `parcel_number` 0 of 109,614; `application_date` 0; `current_status` 1; `housing_units` 73,339 (66.9%). The unit field is therefore unsuitable as a universal measure and must be used only for relevant housing permit subsets with description-based QA.

### Tacoma zoning

The current City service exposes `BaseZone` separately from overlay fields such as historic review, conservation, planned residential development, groundwater protection, view-sensitive, airport compatibility, and shoreline designations. This is preferable to parsing the combined `Zoning` label. The residential base-zone inventory includes `UR1`, `UR2`, `UR3`, `R4`, and `R5`, among others. Exact development standards still require adopted-code review.

### Tacoma building footprints

A 2024 City layer was found after the initial 2005 result. It contains 96,881 polygons with footprint area and average elevation. It is suitable for building-coverage and residual-site-area screening after completeness and parcel-intersection QA, but it contains no parcel key or building-use classification.

### Pierce County assessor detail

The official page states that zipped, pipe-delimited files are updated weekly. Its published relationship diagram identifies Appraisal Account, Improvement, Improvement Built-As, Improvement Detail, and Sale tables joined by parcel number. Direct automated retrieval of the embedded download links was blocked by Cloudflare on 2026-07-11; no substitute data were fabricated. Resolving this access step is the main remaining Phase 1 task.

## Tests still required

1. Resolve the assessor weekly ZIP links and inspect table fields/missingness.
2. Run paginated sample extraction and normalize parcel identifiers.
3. Spatially restrict county parcels to Tacoma and measure zoning/footprint coverage.
4. Review adopted Tacoma code for the minimum defensible UR1/UR2/UR3 capacity rule subset.
5. Profile permit categories, statuses, duplicate permit numbers, unit values, and parcel matches.
6. Confirm reuse and redistribution terms before publishing any derived parcel data.

## Provisional permit decision

**Conditional go.** Bulk queries work and parcel number, application date, and status are essentially complete. However, `housing_units` is null for 66.9% of all records, so housing-unit analysis must first filter/classify relevant residential permit types and validate descriptions. Claims about completion or net unit production are not supportable from the current schema alone.

## Provisional minimum viable analytical scope

- Tacoma residential base parcels with valid county parcel identifiers
- Current residential zoning groups verified against the adopted code
- Existing assessed land and improvement values from the parcel layer
- Three pilot prototypes: for-sale duplex, rental duplex, and four-unit rental rowhouse
- Planning-level physical screening using parcel geometry and the best defensible footprint source available
- Baseline and upside-stress-test interface views, with downside retained in analytical output and assumptions stored outside model code
- Permit applications and issued permits joined by normalized parcel number, with spatial/address fallbacks reported separately
- No claims about completed units unless another public source supplies reliable finalization data

## Decision gate

The minimum data-readiness gate has passed. Detailed assessor tables remain desirable but are no longer a blocker for the portfolio MVP: total assessed value is available, while missing building age, existing units, and sales fields will receive explicit confidence flags or documented fallbacks.

## Completed extraction and join results

The reproducible extraction completed on 2026-07-11/12:

| Layer | Raw records | Processing result |
|---|---:|---|
| Pierce County parcel parts in Tacoma bounding box | 108,865 | Dissolved to unique parcel IDs, then clipped by zoning |
| Tacoma zoning polygons | 8,202 | Representative-point spatial join using separate base-zone and overlay fields |
| Tacoma 2024 building footprints | 96,881 | 112,948 parcel–footprint intersections |
| Tacoma Accela permits | 109,614 | Normalized exact parcel-number join |

The resulting `parcels_base.parquet` contains 73,326 unique Tacoma parcels. Of these, 58,319 are base parcels in the initial UR1/UR2/UR3 residential scope after partial-boundary exclusions.

QA results:

- Duplicate canonical parcel IDs: 0
- Invalid parcel geometries before repair: 4; after repair: 0
- Nonpositive parcel areas: 0
- Parcels with at least one building footprint: 69,306
- Building coverage exceeding 100% by more than numerical tolerance: 0
- Permit records exactly matched to a Tacoma parcel: 101,721 (92.8%)
- Permit records with invalid or nonstandard parcel-number formats: 2,063
- Permit records missing `housing_units`: 73,339 (66.91%)
- Split-zoned parcels: 3,200; meaningful split-zoned parcels at the 5% threshold: 836
- Partial zoning coverage retained for QA: 49; zoning-overlap review flags: 71

Raw responses are stored as paginated GeoJSON with per-page SHA-256 checksums. Processed geometry uses EPSG:2927; raw query responses were requested in EPSG:4326.

## Critical-area source refresh (2026-07-12)

The physical screen now uses City of Tacoma FeatureServer layers for steep slopes (106,828 source polygons; 11,751 over 40 percent), wetlands (481 inventory features; 382 known or high probability), biodiversity areas (102), the 2017 Pierce County Flood Insurance Study (128 SFHA polygons), and protected-water 200-foot buffers (36). The current stream layer (118 centerlines) is retained in the source catalog, while the City's protected-water buffer geometry is used for proximity screening. Every download has a paginated raw manifest and checksum.

These are generalized indicators under TMC 13.11, not surveyed boundaries. No suitable public parcel-level utility-easement geometry was identified. The model therefore does not infer private easements from utility networks; that issue remains a disclosed title-review limitation.
