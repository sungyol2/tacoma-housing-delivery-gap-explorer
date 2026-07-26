# Methodology

## Analytical question

How did the volume and mix of housing applications change after Tacoma's Home in Tacoma regulations took effect, and what do current zoning and mapped parcel constraints contribute as spatial context?

The public app is an explanatory policy-comparison and parcel-lookup tool. It does not estimate causation, financial feasibility, redevelopment probability, or completed housing production.

## Policy date and cohorts

Tacoma's Home in Tacoma zoning regulations took effect February 1, 2025. HB 1110 took effect July 23, 2023, but that state date is not treated as the date Tacoma's local UR regulations became available.

Applications are divided into:

- pre-policy: February 2020–January 2025;
- Home in Tacoma Year One: February 2025–January 2026;
- current partial period: February 2026 through the latest extract.

Cancelled and voided records are excluded from the comparison. Five-year pre-policy totals are divided by five before comparison with the complete first year. The current partial period is displayed but never annualized.

## Housing-application ETL

Accela rows are canonicalized to one record per permit number. The housing universe includes Residential and Commercial `Building / New Building` workflows plus `Building / Alteration` records whose descriptions show that a dwelling unit is created, converted, or legalized. Repairs, garages, and other nonhousing scopes are excluded.

Structured fields and description text classify:

- backyard unit / ADU;
- detached single-unit;
- duplex / two-unit houseplex;
- three-to-six-unit houseplex;
- rowhouse / townhouse;
- courtyard / cottage cluster;
- seven-to-20-unit multiplex;
- larger multifamily;
- other or uncertain housing.

Related `SDEV`, `LU`, `PRE`, and `WO` identifiers group applications into estimated distinct projects. Parcel, application date, and housing type provide a fallback project key. This is reproducible linkage, not authoritative City project identification. See [permit ETL](permit_etl.md) and the [classification gold set](permit_sample_audit.md).

## Policy comparison metrics

The app distinguishes:

- **applications:** canonical building permit records;
- **estimated projects:** reproducibly grouped related applications;
- **proposed units:** units reported or defensibly extracted from source descriptions.

Keeping all three visible prevents additional permits within one project from being mistaken for additional independent projects. Housing-type tables show the pre-policy annual average and Year One for each metric.

The comparison can be filtered by the parcel's primary district today: UR-1, UR-2, or UR-3. Historical parcel-level zoning boundaries are unavailable, so today's Urban Residential geography is applied to the earlier applications. Results are descriptive, not causal.

## Policy map

The default map colors existing-use candidate parcels by the number of estimated housing projects filed during Home in Tacoma Year One. It does not map cumulative 2020–current activity and does not encode before/after change.

The map universe is narrower than the headline comparison because protected, institutional, and other noncandidate existing uses are not published as candidate parcels. Headline and map totals therefore need not match.

## Parcel and zoning base

Pierce County parcel parts are combined into normalized parcel IDs. Every overlap between a parcel and a zoning district is measured. The district covering the largest share is displayed, while meaningful split-zone areas remain in the gross allowance calculation.

Existing residential and clearly developable vacant uses enter the candidate scope. Parks, open space, schools, cemeteries, rights-of-way, utilities, drainage facilities, and golf courses are excluded. Ambiguous nonresidential uses remain manual-review records outside public candidate totals.

Gross baseline density uses 1,500 square feet per unit in UR1, 1,000 in UR2, and 750 in UR3, subject to a four-unit minimum. Split-zone capacity is calculated by zone-part area before flooring. This is gross permission, not net added capacity; reliable existing-unit data are not subtracted.

## Existing use and mapped constraints

Assessor use marked `VACANT LAND UNDEVELOPED` is classified as vacant. A parcel with an existing use is a `partially_vacant_proxy` when improvement-value share is at or below 55 percent and mapped building coverage is at or below 25 percent. Remaining candidates are classified as developed. This is not an official Buildable Lands classification.

The constraint screen overlays:

- slopes above 40 percent;
- known or high-probability wetlands;
- biodiversity areas;
- FEMA special flood hazard areas;
- protected-water buffers.

Overlapping polygons are unioned within each parcel to prevent double counting. The mapped geometry is removed and the largest contiguous residual polygon is measured. A candidate is `constrained_out` when less than 5,000 square feet remains; otherwise it is retained for mapped-constraint site review. Mapped 25–40 percent slopes receive a review flag but are not deducted.

The threshold is an explicit portfolio screening assumption, not a code requirement. Public parcel-level utility-easement geometry was unavailable.

## Interpretation

Applications measure observed development interest and administrative activity. They are not permits issued, construction starts, completed units, net production, or proof that zoning caused the observed change. Current zoning and parcel constraints are explanatory context rather than stages in a predictive delivery funnel.
