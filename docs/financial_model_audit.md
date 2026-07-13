# Financial Model Audit

## 2026-07-12 pilot prototype correction

The pilot now compares a for-sale duplex houseplex, rental duplex houseplex, and four-unit rental rowhouse cluster. Courtyard/cottage configurations are excluded because they require substantially more site-layout assumptions; 7+ multiplex is excluded because Tacoma permits it only in UR3. The for-sale calculation explicitly deducts a 6 percent sales, marketing, and closing-cost allowance.

Rental RLV uses stabilized NOI divided by a cap-rate proxy, then deducts non-land development cost and required profit. The baseline rent input is the FY2026 HUD Tacoma two-bedroom FMR of $1,971 per month (`sourced proxy`, medium confidence). The 5.7 percent cap rate is a Q1 2026 Puget Sound market proxy (`sourced proxy`, low confidence). Vacancy, operating expense, construction cost, fees, financing, and required return remain illustrative and low confidence.

For a selected physical-fit rental parcel, the interface also reports an implied break-even monthly rent per unit. It holds the selected scenario's vacancy, operating-expense ratio, cap rate, non-land cost, and target profit constant, adds the parcel acquisition benchmark, and solves backward for the potential rent required to cover that value. This is a diagnostic—not a rent forecast or claim that the market can support the result.

Under these inputs, every physical-fit rental parcel is `very weak` at baseline. This output has not been adjusted to create a more visually balanced result. It indicates that the current rent/value relationship does not cover modeled new-construction cost and land acquisition. It does not validate a categorical claim about Tacoma rental feasibility because the cost stack, rent premium for new product, tax treatment, financing structure, and parcel acquisition benchmark remain insufficiently validated.

## Audit conclusion

The arithmetic is internally consistent, but the outputs remain an illustrative screening architecture rather than a market finding. One parcel-level calculation error was identified and corrected: the original model charged every parcel a $40,000 demolition allowance, including parcels with no mapped building footprint. Demolition is now zero when mapped building footprint is effectively absent and $40,000 otherwise. Required profit and residual land value are recalculated from that parcel-specific cost.

## Confirmed calculation structure

- For-sale duplex revenue equals two units times sale price per unit; rental value capitalizes prototype NOI.
- Hard cost applies to 2,700 gross square feet for the for-sale duplex, 2,100 for the rental duplex, and 4,700 for the rental rowhouse.
- Soft cost and contingency apply to hard cost.
- Required profit is an explicit percentage of non-land cost.
- Parcel margin equals parcel-specific residual land value minus the acquisition benchmark.
- Normalized margin equals parcel margin divided by the acquisition benchmark.
- Higher hard cost, lower sale price, and higher profit requirement reduce RLV in unit tests.

## Inputs retained without cosmetic adjustment

The following inputs remain because no better public evidence has yet been established; retaining them does not imply validation.

| Input | Treatment | Material limitation |
|---|---|---|
| $450,000 sale price per unit | Baseline, low confidence | Small public evidence sample, not a duplex comparable-sales model |
| $200 per gross square foot for-sale hard cost | Illustrative, low confidence | No contractor or sourced regional duplex estimate |
| 18% soft cost | Transparent assumption | Scope may overlap some financing or fee items |
| $96,000 financing | Lump-sum assumption | Not a draw schedule or loan model |
| 15% required profit | Applied to non-land cost | Not a return-on-total-cost or IRR calculation |
| $55,000 fees | Bundled allowance | Does not calculate each permit, utility, impact, or right-of-way charge |
| Assessed total value | Acquisition benchmark | Not market value and may be temporally misaligned with recent development |

## Current Tacoma fee evidence

Tacoma's wastewater and stormwater system development charges took effect July 1, 2026. The City states that stormwater SDC is $0.53 per square foot of new impervious surface and wastewater SDC depends on water-meter size; a standard 5/8-inch meter example is $3,339. Applicability and meter configuration are project-specific. These figures do not justify replacing the bundled $55,000 allowance without calculating the remaining PDS, utility, and project-specific charges.

Sources: [City SDC announcement](https://tacoma.gov/news/system-development-charges-for-wastewater-and-stormwater-utilities-to-take-effect-on-july-1/), [City rates and services](https://tacoma.gov/government/departments/environmental-services/rates/), [Tacoma Title 2 fee framework](https://cms.tacoma.gov/cityclerk/Files/MunicipalCode/Title02-Buildings.pdf).

## One-factor sensitivity

The interface reports sale price and hard cost at plus or minus five percent with all other baseline inputs fixed. The former “Compound upside” view is now labeled **Upside stress test** because it changes several inputs simultaneously and does not imply that projects should pencil out. Downside stress remains in the analytical output but is not a spatial map choice because RLV is negative before land cost for every parcel.

## Deferred refinements

- Recent arm's-length parcel sales and parcel-lineage-aware acquisition benchmarks
- A sourced regional hard-cost range
- Explicit sales/marketing and closing costs
- Project-specific Tacoma fee calculation
- Financing draw schedule and construction duration
- Alternative profit basis or IRR analysis
- Separate demolition/site-work assumptions by structure and parcel condition

These are documented limitations, not values to tune until the results look plausible.
