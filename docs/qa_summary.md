# Phase 2 QA Summary

Generated from `outputs/qa/parcels_base_qa.json` on 2026-07-11/12.

## Result

The parcel base table passes the minimum gate for capacity-model development.

- 73,326 unique Tacoma parcels
- 58,319 UR1/UR2/UR3 base parcels in the initial residential scope
- No duplicate canonical parcel IDs
- Four invalid source geometries repaired; none invalid after repair
- No zero or negative parcel areas
- 69,306 parcels with at least one 2024 building footprint
- 92.8% exact permit-to-parcel match rate

## Observed source conditions

Pierce County represents some parcel IDs with multiple polygon parts. The pipeline dissolves 7,312 source parts associated with duplicated parcel IDs before enforcing one row per parcel.

Apparent footprint coverage slightly above 100% was numerical precision at shared boundaries. No parcel exceeded 100% by more than the defined `0.000001` tolerance; the published coverage field is bounded to 0–1 while the raw ratio is retained for QA.

Permit parcel identifiers are strong enough for the MVP, but 2,063 records have nonstandard identifiers and 66.91% of all permit records omit `housing_units`. Unit totals therefore require residential permit classification and must not be interpreted as complete production counts.

## Split zoning and boundary QA

- 3,200 parcels intersect more than one base zone.
- 836 have a second zone covering at least 5 percent of the normalized zoning area.
- Within the initial UR scope, 262 are meaningful split-zone parcels.
- Capacity and FAR are calculated from normalized zone-part areas rather than a representative point.
- 301 parcels touching Tacoma zoning on less than half their area are excluded as boundary contacts.
- 49 retained parcels have less than 99 percent Tacoma zoning coverage and are excluded from the initial capacity scope.
- 71 parcels have small polygon-overlap artifacts exceeding 0.1 percent; normalized shares prevent double counting and the QA flag remains published.

## Remaining checks before capacity results are published

- Review a stratified sample of parcel–zoning assignments near district boundaries.
- Compare assessor acreage and geometry-derived acreage for large discrepancies.
- Confirm the adopted UR1/UR2/UR3 rule subset and effective date.
- Identify parcels where condominium geometry or special parcel types should be excluded.
- Validate a sample of building-footprint intersections against recent imagery.
