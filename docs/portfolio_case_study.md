# Tacoma Housing Delivery Gap Explorer

## Case-study question

How did the volume and mix of housing applications change after Home in Tacoma took effect, and what do current zoning capacity, parcel constraints, and representative prototypes reveal about the gap between legal opportunity and delivery?

| Stage or model | Parcels | Interpretation |
|---|---:|---|
| UR1–UR3 zoning inventory | 58,319 | Legal-policy starting point |
| Existing-use candidates | 56,484 | Residential and clearly developable vacant uses |
| Retain at least 5,000 sq ft after mapped constraints | 52,931 | Generalized critical-area screen |
| For-sale duplex physical fit | 50,672 | Area, FAR, and 25-ft width proxy |
| Rental duplex physical fit | 50,672 | Same form, rental valuation |
| Four-unit rental rowhouse physical fit | 42,331 | Four units, FAR, area, and 40-ft width proxy |
| Pre-policy active applications, annual average | 177.0 | February 2020–January 2025 in current UR geography |
| Home in Tacoma Year One active applications | 231 | February 2025–January 2026 |
| Pre-policy proposed units, annual average | 226.8 | Reported units; annualized over five years |
| Home in Tacoma Year One proposed units | 416 | Independent classified Accela result |

Tacoma's official Year One review reports 213 applications and 385 proposed units. The independent ETL produces the same direction but is not a replication: current zoning is applied retrospectively, public Accela descriptions require classification, and project and parcel lineage remain incomplete. The observed change is descriptive and does not isolate the effect of zoning from market conditions, owner decisions, financing, or development lead time.

The three financial prototypes remain available to demonstrate transparent residual-land-value logic and sensitivity. Their extreme baseline results are not presented as the project's central empirical finding.

## Consequential QA correction

Parcel `6245000035` at 3014 N Mildred St initially appeared vacant and promising. Official mapping showed approximately 78.8 percent overlap with slopes greater than 40 percent and essentially complete overlap with the West Tacoma biodiversity area. It is now screened out before prototype feasibility. `Vacant` describes improvement status, not developability.

## What this demonstrates

- Reproducible GIS and area-weighted split zoning
- Canonical housing-application ETL across Residential and Commercial workflows
- Policy-period and housing-type comparisons with an external City benchmark
- Critical-area screening before prototype and financial results
- Prototype-specific unit, area, FAR, and width-proxy tests
- For-sale and stabilized-NOI rental RLV methods
- Explicit assumption confidence and sensitivity
- A performant MapLibre parcel interface with mode-specific analytical summaries
- Unit tests, representative-parcel QA, and release checks

This is not an official capacity estimate, entitlement determination, appraisal, contractor estimate, or redevelopment prediction.
