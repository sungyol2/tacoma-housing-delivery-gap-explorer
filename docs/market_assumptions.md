# Market and Cost Assumption Status

**Status:** Architecture implemented; market validation in progress.

The current residual-land-value results remain illustrative. They demonstrate formula design, scenario behavior, parcel-specific acquisition comparison, and interface communication, but they are not yet presented as market findings.

## Public evidence identified

### Small-project permit valuation cross-check

Tacoma Accela contains only a small usable set of 4â€“6 unit new-building records with positive valuation. Six four-unit records have a median reported valuation of about $645,000; two five-unit records about $593,000; and four six-unit records about $1.11 million. Descriptions allow three rough gross-area checks: a four-unit Yakima Avenue project reports about $171 per gross square foot, a five-unit S L Street project about $200, and a six-unit N 21st Street project about $214.

These figures support retaining $200 per gross square foot as a low-confidence for-sale construction proxy and $240 as a conservative rental-multiplex allowance. They do not validate total project cost: permit valuation may exclude land, financing, soft cost, portions of site work, or other development costs, and several records appear to describe multi-building projects inconsistently.

### Rental revenue and capitalization

- FY2026 HUD Tacoma HMFA two-bedroom FMR is $1,971 per month. The model uses it as a sourced proxy, not a new-construction asking-rent comp.
- A Q1 2026 Puget Sound multifamily report shows approximately $2,073 asking rent per unit and a 5.7 percent cap-rate observation. The model uses the cap rate as a regional proxy, not a Tacoma 3–6 unit transaction comp.
- A current official floor-plan page for a downtown Tacoma apartment building lists a 1,057-square-foot two-bedroom at approximately $2,485–$2,610 per month. This supports testing a new-product premium in future sensitivity work, but it is an amenitized conventional apartment asking rent—not a signed lease or a duplex/rowhouse comparable.
- Vacancy at 5 percent and operating expense at 32 percent remain independent low-confidence screening assumptions.

Even the observed $2,485–$2,610 asking range remains below the configured upside-stress-test median break-even rents of roughly $4,026 for the rental duplex and $3,435 for the four-unit rowhouse. However, the lowest-acquisition duplex parcels have a much lower implied threshold, so a better small-project rent sample could materially change a limited subset. The evidence supports retaining the weak citywide conclusion while avoiding a categorical claim that no rental prototype can work.

### Permit and development fees

- Tacoma Municipal Code Chapter 2.09 establishes the Planning and Development Services fee framework and annual adjustment mechanism.
- Tacoma provides a public fee estimator through Planning and Development Services.
- New wastewater and stormwater system development charges took effect July 1, 2026.
- The City describes a standard 5/8-inch wastewater connection charge of $3,339 and a stormwater charge of $0.53 per square foot of added impervious area. Project-specific meter configuration and applicability still require confirmation.

These findings show that the current flat `$55,000` fee allowance should remain a low-confidence scenario input rather than a claimed exact fee. A later refinement can calculate a prototype-specific range using meter count, added impervious area, building permit valuation, plan review, utility connection, and right-of-way assumptions.

## Inputs still requiring reasonable validation

| Input | Current status | Recommended portfolio treatment |
|---|---|---|
| Duplex sale price | Small public evidence sample; $450,000 baseline | Retain low confidence and expand to product-specific comps only if time permits |
| Hard cost per gross square foot | Cross-checked against a small Accela valuation sample | Retain low confidence; permit valuation is not a contractor bid or total cost |
| Rental rent and cap rate | HUD FMR and regional market-report proxies | Keep visible as sourced proxies, not project-specific evidence |
| Soft cost percentage | Independent screening assumption | Retain as a visible adjustable range |
| Financing allowance | Simplified lump sum | Retain as scenario allowance; do not represent as a loan quote |
| Developer profit | Simplified percentage | Retain as transparent scenario input |
| Acquisition benchmark | Assessed land plus improvement value | Label low confidence until recent sale or comparable evidence is available |

## Time-box decision

The project will not wait for contractor-grade cost data or a complete comparable-sales model. A small defensible public evidence sample plus baseline and stress-test ranges is sufficient for the portfolio version, provided the interface retains source, date, confidence, and limitations.

## Initial sale-price range

The initial citywide range is $405,000 / $450,000 / $495,000 per unit. It is anchored by a current $419,000 asking price for a 1,180-square-foot new Tacoma townhouse and a roughly $453,000 recent median sale price for all homes in New Tacoma. These observations are not treated as a formal comparable set; they justify replacing the concept mockup's $590,000 baseline with a more restrained low-confidence range.
