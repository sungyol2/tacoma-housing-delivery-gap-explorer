# Permit Classification Gold-Set Audit

This audit records a deterministic manual-review sample of Tacoma Home in Tacoma Year One applications. It is a regression fixture, not a statistically representative accuracy estimate.

- Active current-UR applications: **231**
- Likely projects: **193**
- Reported proposed units: **416**
- Gold-set records passing: **37 / 37**

## Active Year One classification

| housing_type | applications | likely_projects | proposed_units |
|---|---|---|---|
| backyard_unit | 116 | 112 | 129.0 |
| courtyard_cottage | 3 | 1 | 3.0 |
| detached_single_unit | 54 | 46 | 54.0 |
| houseplex_2 | 26 | 19 | 63.0 |
| houseplex_3_6 | 2 | 2 | 11.0 |
| multiplex_7_20 | 5 | 3 | 60.0 |
| other_uncertain_housing | 4 | 3 | 4.0 |
| rowhouse | 21 | 9 | 92.0 |

## Reviewed gold set

The fixed sample spans every housing type observed in the active current-UR Year One comparison. Rare categories use their full small population; common categories use multiple construction descriptions. Three deliberate nonhousing false positives are also retained.

| expected_type | reviewed_records | passing |
|---|---|---|
| backyard_unit | 6 | 6 |
| courtyard_cottage | 3 | 3 |
| detached_single_unit | 4 | 4 |
| houseplex_2 | 6 | 6 |
| houseplex_3_6 | 2 | 2 |
| multiplex_7_20 | 4 | 4 |
| other_uncertain_housing | 4 | 4 |
| rowhouse | 5 | 5 |

| permit | expected_type | expected_units | observed_type | observed_units | review_basis | result |
|---|---|---|---|---|---|---|
| BLDRN25-0040 | detached_single_unit | 1 | detached_single_unit | 1 | New SFD is the permit scope. | pass |
| BLDRN25-0104 | detached_single_unit | 1 | detached_single_unit | 1 | New SFD with explicit bedrooms and floor area. | pass |
| BLDRN25-0247 | detached_single_unit | 1 | detached_single_unit | 1 | One new two-story SFD. | pass |
| BLDRN25-0341 | detached_single_unit | 1 | detached_single_unit | 1 | One new three-bedroom SFD. | pass |
| BLDRN25-0036 | backyard_unit | 1 | backyard_unit | 1 | New ADU above a garage. | pass |
| BLDRA25-0080 | backyard_unit | 1 | backyard_unit | 1 | Garage addition explicitly adds one ADU above. | pass |
| BLDRA25-0293 | backyard_unit | 1 | backyard_unit | 1 | Garage conversion creates a DADU. | pass |
| BLDRN25-0058 | backyard_unit | 1 | backyard_unit | 1 | Detached building contains one upper-floor ADU. | pass |
| BLDRN25-0198 | backyard_unit | 1 | backyard_unit | 1 | One new DADU over a garage. | pass |
| BLDRN26-0035 | backyard_unit | 2 | backyard_unit | 2 | Explicit duplex of two DADUs. | pass |
| BLDRA25-0492 | houseplex_2 | 2 | houseplex_2 | 2 | Garage conversion creates two residential units. | pass |
| BLDRA26-0037 | houseplex_2 | 2 | houseplex_2 | 2 | After-the-fact legalization of a two-unit houseplex. | pass |
| BLDRN25-0222 | houseplex_2 | 2 | houseplex_2 | 2 | One duplex building permit within a larger project. | pass |
| BLDRN25-0216 | houseplex_2 | 2 | houseplex_2 | 2 | One duplex permit within a three-building project. | pass |
| BLDRN25-0293 | houseplex_2 | 2 | houseplex_2 | 2 | Explicit two-unit duplex. | pass |
| BLDRN26-0034 | houseplex_2 | 6 | houseplex_2 | 6 | Single permit explicitly constructs three duplexes. | pass |
| BLDRN25-0118 | other_uncertain_housing | 1 | other_uncertain_housing | 1 | Generic houseplex wording lacks a defensible unit count. | pass |
| BLDRN25-0295 | houseplex_3_6 | 5 | houseplex_3_6 | 5 | Fiveplex description controls the unit count. | pass |
| BLDRN25-0306 | houseplex_3_6 | 6 | houseplex_3_6 | 6 | Explicit six-unit houseplex. | pass |
| BLDRN25-0052 | rowhouse | 3 | rowhouse | 3 | Parenthesized three-townhome count. | pass |
| BLDRN25-0053 | rowhouse | 5 | rowhouse | 5 | Parenthesized five-townhome count. | pass |
| BLDRN25-0205 | rowhouse | 4 | rowhouse | 4 | Explicit four-unit rowhouse building. | pass |
| BLDRN25-0326 | rowhouse | 4 | rowhouse | 4 | Explicit four-unit rowhouse building. | pass |
| BLDRN25-0337 | rowhouse | 5 | rowhouse | 5 | Explicit five-unit rowhouse building. | pass |
| BLDRN25-0300 | courtyard_cottage | 1 | courtyard_cottage | 1 | One courtyard building permit. | pass |
| BLDRN25-0301 | courtyard_cottage | 1 | courtyard_cottage | 1 | One courtyard building within the shared project. | pass |
| BLDRN25-0302 | courtyard_cottage | 1 | courtyard_cottage | 1 | One courtyard building within the shared project. | pass |
| BLDCN25-0036 | multiplex_7_20 | 10 | multiplex_7_20 | 10 | Explicit ten-unit apartment building. | pass |
| BLDCN25-0037 | multiplex_7_20 | 8 | multiplex_7_20 | 8 | Explicit eight-unit multiplex building. | pass |
| BLDCN25-0038 | multiplex_7_20 | 16 | multiplex_7_20 | 16 | Commercial workflow, explicit 16-unit building. | pass |
| BLDCN25-0045 | multiplex_7_20 | 8 | multiplex_7_20 | 8 | Explicit eight-unit houseplex. | pass |
| BLDRN26-0017 | other_uncertain_housing | 1 | other_uncertain_housing | 1 | Housing building is clear; form is not stated. | pass |
| BLDRN26-0018 | other_uncertain_housing | 1 | other_uncertain_housing | 1 | Housing building is clear; form is not stated. | pass |
| BLDRN26-0019 | other_uncertain_housing | 1 | other_uncertain_housing | 1 | Housing building is clear; form is not stated. | pass |
| BLDRA25-0306 | excluded | n/a | excluded | n/a | Restores a DADU to a garage; no unit is created. | pass |
| BLDRA25-0475 | excluded | n/a | excluded | n/a | Patio scope only; DADU requires a separate permit. | pass |
| BLDRN25-0188 | excluded | n/a | excluded | n/a | Detached garage only. | pass |

## Deliberate exclusions

Repairs and remodels that do not create a unit remain excluded even when their descriptions mention an existing SFD, duplex, apartment, ADU, or DADU. Group sleeping facilities are also excluded because sleeping units are not shown to be independent dwelling units. Cancelled and voided applications remain in the canonical table but are excluded from the policy comparison.

## Remaining review risk

The gold set covers known difficult text patterns, but it does not measure full-population precision or recall. Project lineage, parcel changes, uncommon abbreviations, and incomplete source descriptions still require periodic manual review.
