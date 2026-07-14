# Housing Application ETL and Policy Cohorts

## Policy-aligned comparison dates

Washington's HB 1110 was signed in 2023 and took effect July 23, 2023. It is codified principally at RCW 36.70A.635. The statute requires covered cities to implement middle-housing authorization through comprehensive-plan and development-regulation updates on the schedule in RCW 36.70A.635(11); the state effective date is therefore not itself the date when Tacoma permit applicants could use the new local UR standards.

Tacoma adopted Home in Tacoma Phase 2 through Ordinance 28986 on November 19, 2024. The UR zoning and development regulations took effect February 1, 2025. The application cohorts use that local effective date:

- `pre_home_in_tacoma_5yr`: February 1, 2020 through January 31, 2025
- `home_in_tacoma_year_1`: February 1, 2025 through January 31, 2026
- `home_in_tacoma_current_partial`: February 1, 2026 through the latest extract

These cohorts describe timing; they do not by themselves establish that Home in Tacoma caused a change. Historical zoning geometry, project lead time, market conditions, and incomplete project lineage remain confounders.

Primary sources: [RCW 36.70A.635](https://app.leg.wa.gov/RCW/default.aspx?cite=36.70A.635), [HB 1110 bill history](https://app.leg.wa.gov/billsummary?BillNumber=1110&Year=2023), [Tacoma Home in Tacoma regulations](https://tacoma.gov/government/departments/planning-and-development-services/home-in-tacoma/), and [Tacoma Ordinance 28986 summary](https://tacoma.gov/government/departments/city-managers-office/affordable-housing-action-strategy/).

## Canonical permit universe

The prior filter treated every `Building / Residential / New Building` record since 2021 as housing. That included garages, sheds, decks, workshops, and similar structures, while omitting many 3–20-unit projects filed under the Commercial building workflow. It has been replaced.

The current ETL:

1. parses Accela epoch dates explicitly;
2. normalizes parcel identifiers;
3. reduces duplicate Accela rows to one canonical row per permit number while preserving the most advanced status and best available unit count;
4. considers both Residential and Commercial `Building / New Building` records and `Building / Alteration` records that explicitly create, convert, or legalize one or more dwelling units;
5. classifies the primary construction scope from structured fields and description text;
6. excludes repairs to existing housing, garages, and other nonhousing structures when they are the primary permit scope;
7. resolves unit counts from the permit scope rather than a related project's total where the text distinguishes them;
8. groups likely projects using related `SDEV`, `LU`, `PRE`, or `WO` identifiers, with parcel/date/type as a fallback; and
9. retains status groups so cancelled, issued, completed, expired, and in-review applications are distinguishable.

## Published housing types

- Backyard unit / ADU
- Duplex / two-unit houseplex
- Three-to-six-unit houseplex
- Rowhouse / townhouse
- Courtyard / cottage cluster
- Seven-to-20-unit multiplex
- Larger multifamily, 21+ units, as context outside the core middle-housing comparison
- Detached single-unit, as a comparison category

The categories translate historical permit terminology into the current Tacoma housing-type framework. They do not infer sale versus rental tenure.

## Current QA result

The July 2026 raw extract contains 109,614 rows and 109,415 canonical permit numbers. Of those, 1,835 classified housing-building permits representing 1,552 likely projects match a Tacoma parcel in the policy-period universe. The full matched citywide type counts are:

| Type | Canonical permits |
|---|---:|
| Backyard unit / ADU | 782 |
| Detached single-unit | 493 |
| Duplex / two-unit houseplex | 236 |
| Rowhouse / townhouse | 170 |
| Larger multifamily, 21+ | 51 |
| Seven-to-20-unit multiplex | 45 |
| Three-to-six-unit houseplex | 40 |
| Courtyard / cottage cluster | 12 |
| Housing type uncertain | 6 |

The public candidate-parcel map contains 1,485 permit records, 1,321 likely projects, and 2,006 reported proposed units after restricting to the mapped parcel scope. Larger multifamily generally falls outside that scope and remains contextual rather than a middle-housing map category.

## External benchmark and remaining limitation

Tacoma's Year One release reports 213 applications and 385 proposed units in the new UR zones for February 2025–January 2026, a 39 percent application increase and 62 percent proposed-unit increase relative to the prior five-year average. Using current UR parcel geography and excluding cancelled or voided records, this independent ETL finds 231 applications and 416 proposed units, versus a pre-policy annual average of 177.0 applications and 226.8 units. That is a 30.5 percent application increase and an 83.4 percent unit increase. The independent total is 18 applications and 31 units above the City result. The direction is consistent, but the residual is material enough that this should not be presented as a replication. Public Accela scope, current-parcel geography, text classification, and project grouping differ from the City's internal monitoring dataset, so the official result remains an external reasonableness benchmark rather than a calibration target.

Sources: [Tacoma Year One release](https://tacoma.gov/news/home-in-tacoma-sparks-62-increase-in-number-of-proposed-housing-units-in-first-year/) and [Washington Commerce middle-housing guidance](https://www.commerce.wa.gov/growth-management/housing-planning/middle-housing/).

The deterministic [permit classification gold-set audit](permit_sample_audit.md) records 37 reviewed Year One examples spanning every active housing type plus deliberate exclusions; all currently pass their expected type, unit-count, or exclusion result. It is a regression fixture, not a population-level accuracy estimate.

Remaining review needs include historical zoning boundaries, parcel lineage and assemblies, a larger stratified manual sample, manually verified project identifiers, and completion/final-unit outcomes.
