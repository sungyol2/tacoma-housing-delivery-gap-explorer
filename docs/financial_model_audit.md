# Financial Model Audit

## 2026-07-12 pilot prototype correction

The pilot now compares a for-sale duplex houseplex, rental duplex houseplex, and four-unit rental rowhouse cluster. Courtyard/cottage configurations are excluded because they require substantially more site-layout assumptions; 7+ multiplex is excluded because Tacoma permits it only in UR3. The for-sale calculation deducts a 4 percent sales, marketing, and closing-cost allowance.

Rental RLV uses stabilized NOI divided by a cap-rate proxy, then deducts non-land development cost and required profit. The baseline rent input is the FY2026 HUD Tacoma two-bedroom FMR of $1,971 per month (`sourced proxy`, medium confidence). The cap rate is 5.0 percent, corrected on July 13 to match the cited Q1 2026 Puget Sound report (`sourced proxy`, low confidence); the prior 5.7 percent value was the report's Q1 2025 observation. Vacancy, operating expense, construction cost, fees, financing, and required return remain illustrative and low confidence.

The upside rent is now $2,295 per unit per month, taken from one active new-construction two-bedroom Tacoma townhome listing. It replaces the earlier arbitrary 5 percent uplift but remains low confidence because it is one asking rent, not an executed lease or a market-area comparable set.

For a selected physical-fit rental parcel, the interface also reports an implied break-even monthly rent per unit. It holds the selected scenario's vacancy, operating-expense ratio, cap rate, non-land cost, and target profit constant, adds the parcel acquisition benchmark, and solves backward for the potential rent required to cover that value. This is a diagnostic—not a rent forecast or claim that the market can support the result.

Under these inputs, neither rental prototype has a marginal-or-better parcel at baseline. This output has not been adjusted to create a more visually balanced result. It indicates that the current rent/value relationship does not cover modeled new-construction cost and land acquisition. It does not validate a categorical claim about Tacoma rental feasibility because the cost stack, rent premium for new product, tax treatment, financing structure, and parcel acquisition benchmark remain incompletely validated.

## Audit conclusion

The arithmetic and cost roles are now internally consistent, but the outputs remain a screening model rather than underwriting. The July 13 structural audit removed three unsupported shortcuts: tenure-specific hard cost for the same duplex form, unit-count-scaled fee and financing lump sums, and profit applied only to non-land cost. All prototypes now use a common $220 per gross-square-foot hard-cost proxy; fees equal 5 percent of hard cost; financing equals 4 percent of financeable cost; and the 15 percent target return applies to total development cost including supportable land. Demolition remains zero without a mapped building footprint and $40,000 otherwise.

## Confirmed calculation structure

- For-sale duplex revenue equals two units times sale price per unit; rental value capitalizes prototype NOI.
- Hard cost applies to 2,700 gross square feet for the for-sale duplex, 2,100 for the rental duplex, and 4,700 for the rental rowhouse.
- Soft cost, fees, and contingency each have separate documented scopes and scale from hard cost.
- Financing scales from financeable project cost rather than unit count.
- Required profit is an explicit percentage of total development cost including supportable land.
- Parcel margin equals parcel-specific residual land value minus the acquisition benchmark.
- Normalized margin equals parcel margin divided by the acquisition benchmark.
- Higher hard cost, lower sale price, and higher profit requirement reduce RLV in unit tests.

## Logic and necessity review

| Component | Decision | Reason |
|---|---|---|
| Gross sale revenue / stabilized rental value | Retain | The two tenures require different value methods; treating rent as sale revenue would be wrong. |
| Hard cost | Retain, unify | Physical construction cost should follow prototype size and specification, not tenure alone. |
| Scoped soft cost | Retain | Design, engineering, insurance, and administration are real costs; its scope now excludes every separately modeled line. |
| Fee proxy | Retain, simplify | Permit and utility charges are real, but a percentage proxy is more coherent than an arbitrary unit-count lump sum until a prototype fee calculation is available. |
| Financing | Retain, simplify | Ignoring carry would overstate RLV; a cost-scaled proxy is adequate for this screen and avoids pretending to be a loan schedule. |
| Contingency | Retain | It represents construction uncertainty and is distinct from scoped soft cost. |
| Demolition | Retain conditionally | It is applied only where a mapped structure exists and no longer claims to represent general site work. |
| Selling cost | Retain for sale only | Rental capitalization has no unit-sale transaction; applying this line to rental would double count. |
| Target return | Retain, correct basis | A zero-profit project is not financially feasible. Return now applies to total development cost including supportable land. |
| Acquisition benchmark | Retain with low confidence | Feasibility requires comparing supportable land value with the cost of controlling the parcel; assessed value is only a proxy. |
| Five margin bands | Retain as communication | Bands prevent false precision around zero but do not change RLV arithmetic. Because the same absolute-dollar cutoffs apply to two- and four-unit prototypes, bands are not a return metric and should not be used alone for cross-prototype ranking; the interface also reports margin divided by the acquisition benchmark. |

No pro forma line is retained solely to make the model look sophisticated. The remaining lines correspond to a distinct revenue, cost, return, or land-control concept. The model deliberately omits depreciation, income tax, permanent-debt proceeds, IRR, refinance, and detailed draw timing because those would add unsupported complexity without improving this planning-level comparison.

## Results after structural audit

- For-sale duplex baseline: 2 marginal parcels; none moderate or strong.
- Rental duplex baseline: 50,135 very weak and 537 weak; none marginal or better.
- Four-unit rental rowhouse baseline: all 42,331 physical-fit parcels very weak.
- Upside stress test marginal-or-better: 590 for-sale duplex, 714 rental duplex, and 600 rental rowhouse parcels.

The direction is analytically coherent: raising the shared for-sale hard-cost proxy reduces baseline for-sale feasibility, while replacing oversized unit-scaled financing and the higher rental hard-cost proxy improves the rental tail. Most parcels remain infeasible because acquisition benchmarks are still large relative to prototype supportable land value.

## Inputs retained without cosmetic adjustment

The following inputs remain because no better public evidence has yet been established; retaining them does not imply validation.

| Input | Treatment | Material limitation |
|---|---|---|
| $450,000 sale price per unit | Baseline, low confidence | Small public evidence sample, not a duplex comparable-sales model |
| $220 per gross square foot hard cost | Common prototype proxy, low confidence | No contractor or sourced regional duplex/rowhouse estimate |
| 18% scoped soft cost | Architecture, engineering, insurance, administration | Explicitly excludes separately modeled fees, financing, contingency, sales, and demolition |
| 5% of hard cost for fees | Cost-scaled proxy | Does not calculate each permit, utility, impact, fire, or right-of-way charge |
| 4% of financeable cost | Rounded carry-and-fee proxy | Not a construction draw schedule or loan quote |
| 15% target return | Applied to total development cost | Conservative relative to the NAHB national gross-profit observation; not an IRR |
| Assessed total value | Acquisition benchmark | Not market value and may be temporally misaligned with recent development |

## Current Tacoma fee evidence

Tacoma's wastewater and stormwater system development charges took effect July 1, 2026. The City states that stormwater SDC is $0.53 per square foot of new impervious surface and wastewater SDC depends on water-meter size; a standard 5/8-inch meter example is $3,339. Applicability and meter configuration are project-specific. The 5-percent fee proxy is therefore a scalable placeholder, not an exact Tacoma fee calculation.

For financing and profit reasonableness, the NAHB 2026 study reports 86 percent construction loan-to-cost, a 7.345 percent construction-loan rate under its March assumptions, a 70-basis-point initial fee, 6.3 months from construction start to completion, and a 9.8 percent national builder/developer gross-profit rate. Current Federal Reserve data show a 6.75 percent prime rate as of July 8, 2026. A rounded 4 percent of financeable cost is a transparent carry-and-fee proxy under partial draws; 15 percent return on total cost is intentionally conservative for small infill but remains low confidence.

Sources: [City SDC announcement](https://tacoma.gov/news/system-development-charges-for-wastewater-and-stormwater-utilities-to-take-effect-on-july-1/), [City rates and services](https://tacoma.gov/government/departments/environmental-services/rates/), [Tacoma Title 2 fee framework](https://cms.tacoma.gov/cityclerk/Files/MunicipalCode/Title02-Buildings.pdf).

## One-factor sensitivity

The interface reports sale price and hard cost at plus or minus five percent with all other baseline inputs fixed. The former “Compound upside” view is now labeled **Upside stress test** because it changes several inputs simultaneously and does not imply that projects should pencil out. Downside stress remains in the analytical output but is not a spatial map choice because RLV is negative before land cost for every parcel.

The three scenario packages are sensitivity bundles, not probability-weighted forecasts. Their simultaneous changes are useful for showing which conclusions are robust to input uncertainty, but they cannot identify which market variable caused a parcel to cross zero. The one-factor diagnostics are the appropriate view for that question.

## Deferred refinements

- Recent arm's-length parcel sales and parcel-lineage-aware acquisition benchmarks
- A sourced regional hard-cost range
- Project-specific Tacoma fee calculation
- Financing draw schedule and construction duration
- IRR analysis or a locally observed small-project return hurdle
- Separate demolition/site-work assumptions by structure and parcel condition

These are documented limitations, not values to tune until the results look plausible.
