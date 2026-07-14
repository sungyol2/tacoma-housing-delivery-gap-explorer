# Portfolio Exhibit Handoff

Capture at 1920 × 1080 when possible. Keep the header, funnel, right-hand evidence panel, and bottom disclaimer visible. The local examples below assume the preview server is running at `http://127.0.0.1:4173`; replace the origin with the final GitHub Pages origin after deployment.

## 1. Home in Tacoma policy comparison

`/app/?mode=permits`

**Caption:** Active housing applications and reported proposed units increased in Home in Tacoma Year One relative to the prior five-year annual average; the housing-type table shows where the observed mix changed while keeping the City benchmark separate.

## 2. System overview

`/app/?mode=capacity&scenario=baseline&prototype=duplex_for_sale`

**Caption:** Current UR zoning provides broad legal capacity, but the funnel distinguishes existing-use candidates, mapped constraints, prototype fit, and the much smaller financially near-break-even subset.

## 3. Model correction

`/app/?mode=readiness&scenario=baseline&prototype=duplex_for_sale&parcel=6245000035`

**Caption:** A wooded parcel classified as vacant is screened out before feasibility because generalized City mapping shows steep-slope and biodiversity constraints with insufficient contiguous residual area.

## 4. Financial interpretation

`/app/?mode=feasibility&scenario=baseline&prototype=duplex_for_sale&parcel=0221237011`

**Caption:** A representative marginal for-sale duplex parcel exposes the complete residual-land-value calculation, acquisition benchmark, normalized margin, confidence, and three-model comparison.

## 5. Upside stress test

`/app/?mode=feasibility&scenario=favorable&prototype=duplex_for_sale&parcel=0221237011`

**Caption:** The upside stress test improves several inputs simultaneously and expands the near-break-even set, but remains a stacked sensitivity rather than a forecast.

## Capture QA

- Wait until all parcel sections render and the transient map-status badge disappears.
- For selected-parcel exhibits, wait for the on-demand detail section to finish loading.
- Do not crop the scenario label, evidence panel, funnel, or independent-project disclaimer.
- Use PNG and descriptive names: `01_home_in_tacoma_comparison.png`, `02_system_overview.png`, `03_constraint_correction.png`, `04_financial_interpretation.png`, and `05_upside_stress_test.png`.
