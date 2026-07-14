# Portfolio Summary

## Short description

Tacoma Housing Delivery Gap Explorer combines current zoning, assessor parcels, building footprints, critical areas, and a policy-aligned housing-application ETL to examine Tacoma's early implementation of Home in Tacoma. Three missing-middle financial prototypes remain as secondary sensitivity demonstrations.

## What the project demonstrates

- Reproducible Python and GeoPandas parcel processing
- Area-weighted treatment of split zoning
- Transparent existing-use exclusions and current-site proxies
- City critical-area overlays applied before prototype and financial screening
- Rule-based legal-capacity and physical-fit screening
- Canonical permit ETL spanning Residential and Commercial workflows, unit-creating alterations, status, housing type, and likely-project grouping
- Policy-aligned comparison of the five-year pre-policy annual average with Home in Tacoma Year One
- Unit-tested residual-land-value and one-factor sensitivity calculations, explicitly separated from observed applications
- MapLibre static-app performance at 56,484 parcel features
- Machine-readable QA, representative parcel audits, and release checks

## Current analytical takeaway

Within current UR parcel geography, the independent ETL finds 231 active applications and 416 reported proposed units during Home in Tacoma Year One, compared with pre-policy annual averages of 177.0 and 226.8. The direction is consistent with Tacoma's official 213 applications and 385 units, but the two datasets are not treated as identical and neither comparison establishes causation. Parcel constraints and prototype screens provide explanatory context rather than predictions.

## Appropriate claim

The project demonstrates how to build, audit, qualify, and communicate a parcel-level housing-policy screen. It does not claim an official Tacoma capacity estimate, a site-specific entitlement conclusion, an appraisal, a contractor estimate, or a prediction of redevelopment.

## Resume version

Built a 56,000-parcel Tacoma housing-policy explorer using Python, GeoPandas, public zoning, assessor, critical-area, and Accela data; implemented a canonical permit ETL and Home in Tacoma policy-period comparison, area-weighted split-zone capacity, contiguous buildable-area screening, prototype sensitivity tests, and a high-performance MapLibre interface with reproducible QA.
