# Home in Tacoma Housing Application Explorer

## Case-study question

How did the volume and mix of housing applications change after Home in Tacoma took effect, and what do current zoning and mapped parcel constraints reveal about the geography in which that change occurred?

## Core evidence

| Measure | Pre-policy annual average | Home in Tacoma Year One | Change |
|---|---:|---:|---:|
| Active applications | 177.0 | 231 | +30.5% |
| Estimated projects | 170.2 | 193 | +13.4% |
| Reported proposed units | 226.8 | 416 | +83.4% |
| Units per likely project | 1.33 | 2.16 | +61.7% |

The most important result is the divergence: proposed units increased much faster than applications, and applications increased faster than estimated projects. Early Home in Tacoma activity therefore reflects a shift in project and permit structure as well as application volume.

Estimated duplex projects increased from 2.0 annually to 19, with proposed units increasing from 4.4 to 63. Rowhouse proposed units increased from 17.8 to 92 even though estimated rowhouse projects declined from 10.8 to 9. Detached-house applications declined from 69.6 to 54.

UR1 shows the largest application increase (+54.7%). UR2 and UR3 show larger proposed-unit increases (+96.3% and +126.1%) than application increases (+20.2% and +17.5%).

Tacoma's official Year One review reports 213 applications and 385 proposed units. The independent ETL result of 231 and 416 has the same direction but is not a replication.

## Spatial context

The current UR inventory contains 58,319 parcels and 56,484 existing-use candidates. Their gross modeled allowance is 418,264 units, but existing units are not subtracted and the result is not a production forecast.

Of the candidates, 11,070 intersect mapped critical-area geometry. The generalized screen removes 3,553 parcels with less than 5,000 square feet of contiguous residual area and retains 7,517 for site review.

Parcel `6245000035` at 3014 N Mildred St demonstrates the consequence: land that appeared vacant was screened by steep-slope and biodiversity mapping. `Vacant` does not mean `developable`.

## What this demonstrates

- Canonical permit ETL across Residential and Commercial workflows
- Text classification into policy-relevant housing types
- Reproducible likely-project grouping
- Policy-cohort comparison with correct annualization
- Separation of applications, projects, and proposed units
- Urban Residential district and housing-type comparison
- Parcel GIS, area-weighted split zoning, and critical-area overlays
- A performant MapLibre interface with on-demand parcel evidence
- Unit tests, gold-set classification review, and release-contract QA

The analysis does not establish causation or measure completed housing delivery.
