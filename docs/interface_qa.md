# Interface QA

## Scope

The browser pass tests the explanatory reading path of the Housing Applications mode at desktop (1,920 × 1,080) and mobile portrait (390 × 844). The analytical job is policy-period comparison plus housing-type composition; the parcel map remains a spatial lookup surface rather than the primary evidence.

## Verified behavior

- Housing Applications mode replaces the development funnel with the Home in Tacoma comparison.
- Financial scenario, prototype, and physical-fit controls are hidden because they do not affect the permit comparison.
- The all-UR view displays 177.0 pre-policy applications per year, 231 Year One applications, a 30.5 percent increase, 226.8 pre-policy units per year, 416 Year One units, and an 83.4 percent increase.
- The right panel directly labels the pre-policy annual average and Year One values for every observed housing type.
- URL state records `mode=permits`; zone selection continues to drive both the comparison and the type table.
- Mobile portrait has no horizontal overflow.
- Mobile Housing Applications mode reads in this order: controls, core policy comparison, parcel map, housing-type detail.
- The parcel map retains a 62-viewport-height minimum on mobile after the comparison is moved earlier in the reading order.

## Test limitation

The isolated browser could not reach the external MapLibre and OpenStreetMap hosts. The interface pass therefore substituted a non-rendering MapLibre test double so application state, controls, metrics, responsive ordering, and page errors could be checked without altering production code. Actual parcel geometry is covered by the release contract (56,484 unique map and detail records across 16 chunks) and prior interactive review, but a fresh automated basemap/cartography screenshot remains a deployment-environment check.
