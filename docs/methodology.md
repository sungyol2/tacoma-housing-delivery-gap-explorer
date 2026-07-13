# Methodology

# Methodology

All results are planning-level screening estimates under documented assumptions.

## Parcel base

Pierce County parcel features are downloaded within the Tacoma zoning bounding box. Multipart records sharing a normalized 10-digit parcel number are dissolved. Geometry calculations use EPSG:2927.

Every parcel–zoning polygon intersection greater than one square foot is measured. The largest intersection supplies the display/dominant zone, while all base-zone parts are retained in `parcel_zoning_parts.parquet`. A parcel is `meaningful_split_zoned` when its second-largest base-zone share is at least 5 percent.

Parcels with less than 50 percent Tacoma zoning coverage are treated as boundary contacts and excluded from the canonical Tacoma table. Parcels with 50–99 percent coverage remain available for QA but are excluded from the initial model scope. When zoning polygons overlap slightly, zone shares are normalized to the parcel area so capacity is not double-counted.

Building footprints are clipped to parcel boundaries before area is summed. Permit records are joined using an exact normalized 10-digit parcel number; nonstandard identifiers remain unmatched rather than being forced to a parcel.

## Baseline legal capacity

The first model begins with base parcels in UR1, UR2, and UR3, then applies a conservative assessor-use eligibility screen. Existing residential uses and clearly developable vacant land enter the candidate scope. Parks/open space, schools, cemeteries, rights-of-way, utilities, drainage facilities, and golf courses are excluded. Unknown and ambiguous nonresidential uses are retained in the canonical data as manual-review records but do not enter capacity or feasibility totals. This prevents zoning designation alone from turning public or constrained land into apparent housing supply.

The capacity model implements the November 2024 City standards effective February 1, 2025:

- UR1: one unit per 1,500 square feet of site area
- UR2: one unit per 1,000 square feet
- UR3: one unit per 750 square feet
- Legal lots of record receive a minimum baseline allowance of four dwellings

For single-zone parcels, capacity is the greater of four units and the floor of parcel area divided by the applicable density factor. For split-zone parcels, each normalized zone-part area is divided by its applicable density factor and the results are summed before flooring. FAR-supported floor area is likewise summed by zone part. Baseline FAR is 0.8, 1.0, and 1.2 respectively for projects of three or more units.

The first pass does not model bonuses, alley area credits, frontage, lot width, critical-area flexibility, tree-retention flexibility, PRD rules, or site-specific exceptions. Overlay flags remain visible for review.

## Mapped critical-area screen

Before prototype fit and financial feasibility, the model overlays current City of Tacoma screening geometry for slopes over 40 percent, known or high-probability wetlands, biodiversity areas, FEMA special flood hazard areas, and protected-water buffers. Overlapping polygons are unioned within each parcel so area is not double-counted. The mapped geometry is removed and the largest contiguous residual polygon is measured. A candidate is `constrained_out` when that residual is below the prototype's 5,000-square-foot screening threshold; otherwise it remains as `mapped_constraint_review`. Mapped 25â€“40 percent slopes receive a separate review flag but are not deducted.

This is deliberately a generalized GIS screen, not a critical-area delineation or entitlement decision. Utility easements are not modeled because a suitable public parcel-level easement geometry was not found; assessor parcels whose primary use is utilities are already excluded, but private easements across otherwise eligible parcels require title and utility review.

## Existing-site condition screen

The underlying site-condition classification uses current assessor and building-footprint data rather than importing Pierce County's January 2020 Buildable Lands Inventory as if it represented 2026 conditions. Assessor use marked `VACANT LAND UNDEVELOPED` is classified as vacant. A parcel with an existing use is a `partially_vacant_proxy` when its improvement-value share is at or below 55 percent and mapped building coverage is at or below 25 percent. Remaining candidates are classified as developed. This attribute is retained in parcel detail, while the second map mode now prioritizes the separate mapped critical-area screen. The three-category classification does not reproduce an official underutilized-land finding or measure owner intent, tenancy, building condition, demolition feasibility, or market availability.

## Prototype physical screens

The pilot compares three Tacoma-permitted missing-middle test cases: a for-sale duplex houseplex (2,700 gross square feet), rental duplex houseplex (2,100 gross square feet), and four-unit rental rowhouse cluster (4,700 gross square feet). Each has its own unit count, gross area, minimum residual site area, FAR, and parcel-width proxy. Duplexes require a 25-foot proxy width and the rowhouse cluster 40 feet, matching the applicable minimum lot or cluster-width concept. Minimum rotated parcel width is not surveyed frontage or a buildable-envelope determination.

A parcel passes the basic screen when:

- it is an in-scope UR1/UR2/UR3 base parcel;
- baseline legal capacity is at least the prototype's two or four units;
- it is not classified `constrained_out` by the common 5,000-square-foot critical-area residual screen;
- the residual area also meets the prototype threshold (3,500 square feet for either duplex and 5,000 for the rowhouse);
- the parcel-width proxy meets 25 feet for either duplex or 40 feet for the rowhouse; and
- baseline FAR supports the prototype's 2,100, 2,700, or 4,700 gross square feet.

The common 5,000-square-foot critical-area residual threshold and the prototype site thresholds are explicit portfolio screening assumptions, not code requirements. Passing does not establish architectural feasibility, frontage, fire access, parking layout, utilities, trees, title, or environmental compliance.

## Residual land value

For each scenario:

```text
Gross revenue = units × sale price per unit
Non-land cost = hard cost + soft cost + fees + financing + demolition + contingency
Required profit = non-land cost × required profit rate
Residual land value = gross revenue - non-land cost - required profit
Feasibility margin = residual land value - acquisition benchmark
```

The current acquisition benchmark is assessed land value plus assessed improvement value, with low confidence. It is not treated as market value.

The demolition allowance is parcel-specific at screening level: it is zero when the mapped building footprint is effectively absent and $40,000 when a building footprint is present. For-sale results now also include an explicit 6 percent sales, marketing, and closing-cost allowance. These corrections do not estimate actual demolition scope, hazardous materials, grading, brokerage contracts, or site work.

Rental prototypes use potential rent less vacancy and operating expenses to estimate NOI, divide NOI by a cap-rate proxy to estimate stabilized value, then deduct non-land development cost and required profit. FY2026 HUD Tacoma two-bedroom FMR ($1,971/month) is used as a sourced rent proxy, not a new-construction rent comp. A 5.7 percent Puget Sound multifamily cap rate is a regional transaction proxy, not evidence specific to Tacoma duplex or four-unit rowhouse construction. Vacancy, operating expenses, hard cost, financing, fees, and return remain illustrative assumptions.

Feasibility is shown as five screening bands rather than a binary pass/fail: strong at $150,000 or more; moderate from $50,000 to $149,999; marginal from -$50,000 to $49,999; weak from -$250,000 to -$50,001; and very weak below -$250,000. The parcel panel also reports margin divided by the acquisition benchmark so the same dollar gap is not interpreted identically for low- and high-value parcels.

The sale-price range now uses a small public evidence sample documented in `config/market_evidence.yaml`: $405,000 conservative, $450,000 baseline, and $495,000 upside-stress-test per unit. This is not a formal comparable-sales model and remains low confidence. The upside stress test simultaneously applies a 10 percent sale-price increase, 10 percent hard-cost reduction, 15 percent financing reduction, and 10 percent required-return reduction. It is a stacked sensitivity, not a small market movement or a scenario expected to make projects feasible. Construction cost, financing, and several fee inputs remain illustrative architecture-testing values. Financial classifications must remain qualified until the cost side is validated.

## Permit activity

All Accela records remain in the processed permit table, but the map uses applications from January 1, 2021 onward and only residential Building permits categorized as `New Building`, plus residential Building `Alteration` records that report a positive housing-unit count. Mechanical, plumbing, sewer, right-of-way, utility, repair, demolition, and unrelated permit records are not included in the map count. ArcGIS epoch timestamps are parsed explicitly as milliseconds. Because unit reporting remains incomplete and no reliable completion field is available, the layer is described as observed housing-development activity rather than completed or net housing production.

Housing applications are not treated as the next stage of the financial screen or as validation of the three pilot prototypes. The application universe includes multiple housing products, most records predate the February 1, 2025 Home in Tacoma effective date, development decisions depend on owner and market timing, and exact parcel-ID matching can miss assemblies and parcel changes. Application geography remains an independent historical context layer until product-matched, policy-aligned validation cohorts are large enough.
