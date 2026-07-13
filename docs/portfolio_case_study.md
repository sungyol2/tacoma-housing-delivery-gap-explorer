# Tacoma Housing Delivery Gap Explorer

## Pilot question

How do three representative, citywide-permitted missing-middle models—a for-sale duplex houseplex, rental duplex houseplex, and four-unit rental rowhouse cluster—compare in physical fit and planning-level financial screening?

| Stage or model | Parcels | Interpretation |
|---|---:|---|
| UR1–UR3 zoning inventory | 58,319 | Legal-policy starting point |
| Existing-use candidates | 56,484 | Residential and clearly developable vacant uses |
| Retain at least 5,000 sq ft after mapped constraints | 52,931 | Generalized critical-area screen |
| For-sale duplex physical fit | 50,672 | Area, FAR, and 25-ft width proxy |
| Rental duplex physical fit | 50,672 | Same form, rental valuation |
| Four-unit rental rowhouse physical fit | 42,331 | Four units, FAR, area, and 40-ft width proxy |
| For-sale duplex baseline near/above break-even | 43 | Margin of at least -$50,000 |

Both rental models are entirely very weak at baseline under current sourced rent/cap-rate proxies and illustrative costs. This prompts input validation; it does not prove rental missing-middle construction cannot occur.

## Consequential QA correction

Parcel `6245000035` at 3014 N Mildred St initially appeared vacant and promising. Official mapping showed approximately 78.8 percent overlap with slopes greater than 40 percent and essentially complete overlap with the West Tacoma biodiversity area. It is now screened out before prototype feasibility. `Vacant` describes improvement status, not developability.

## What this demonstrates

- Reproducible GIS and area-weighted split zoning
- Critical-area screening before prototype and financial results
- Prototype-specific unit, area, FAR, and width-proxy tests
- For-sale and stabilized-NOI rental RLV methods
- Explicit assumption confidence and sensitivity
- A performant MapLibre parcel interface
- Unit tests, representative-parcel QA, and release checks

This is not an official capacity estimate, entitlement determination, appraisal, contractor estimate, or redevelopment prediction.
