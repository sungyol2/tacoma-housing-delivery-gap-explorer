# Portfolio Summary

## Short description

Tacoma Housing Delivery Gap Explorer combines current zoning, assessor parcels, building footprints, three missing-middle prototype screens, and a narrow housing-application layer to examine why legal capacity does not automatically become housing production.

## What the project demonstrates

- Reproducible Python and GeoPandas parcel processing
- Area-weighted treatment of split zoning
- Transparent existing-use exclusions and current-site proxies
- City critical-area overlays applied before prototype and financial screening
- Rule-based legal-capacity and physical-fit screening
- Unit-tested residual-land-value and one-factor sensitivity calculations
- Explicit separation of screening outputs from observed housing applications
- MapLibre static-app performance at 56,484 parcel features
- Machine-readable QA, representative parcel audits, and release checks

## Current analytical takeaway

Physical fit is 50,672 parcels for each duplex tenure and 42,331 for the four-unit rental rowhouse. Only 43 for-sale duplex parcels are within $50,000 of break-even or above at baseline; both rental baselines are entirely very weak under current rent proxies and illustrative costs. This is a screening finding and a prompt for input validation, not a forecast.

## Appropriate claim

The project demonstrates how to build, audit, qualify, and communicate a parcel-level housing-policy screen. It does not claim an official Tacoma capacity estimate, a site-specific entitlement conclusion, an appraisal, a contractor estimate, or a prediction of redevelopment.

## Resume version

Built a 56,000-parcel Tacoma housing delivery explorer using Python, GeoPandas, public zoning, assessor, critical-area, and permit data; implemented area-weighted split-zone capacity, contiguous buildable-area screening, a unit-tested residual-land-value prototype, and a high-performance MapLibre interface with reproducible QA and explicit uncertainty.
