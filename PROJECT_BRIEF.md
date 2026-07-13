# Tacoma Housing Delivery Gap Explorer
## Codex Project Brief and Working Context

> **Purpose:** Give Codex enough background, constraints, methodology, design direction, and implementation priorities to begin the project without requiring the user to re-explain the concept.

---

## 1. Project Summary

Build a polished, parcel-level interactive housing dashboard for Tacoma, Washington that examines the gap between:

1. Housing that is **legally allowed**
2. Housing that is **physically plausible**
3. Housing that appears **financially supportable under transparent scenarios**
4. Housing that is **actually entering the permit pipeline**

The project is a **self-directed portfolio case study**, not a City of Tacoma commission, official capacity analysis, appraisal, entitlement determination, or investment tool.

The primary audience is **Cascadia Partners**, as part of an application for a Senior Associate position. The project should demonstrate:

- Housing-policy knowledge
- Parcel-level GIS analysis
- Python
- SQL / DuckDB
- Development-feasibility reasoning
- Transparent assumptions and sensitivity analysis
- Interactive mapping
- Strong visual communication
- The ability to turn technical analysis into a decision-oriented story

The final product should feel like a credible consulting work sample, not a generic data dashboard and not an AI-generated startup UI.

---

## 2. Core Project Thesis

The app should communicate this idea:

> **Zoning capacity is not the same as housing delivery.** New zoning may create widespread legal capacity, but actual production depends on parcel conditions, existing property value, project type, market strength, development costs, policy assumptions, and owner behavior.

The app should not begin with a predetermined claim that Tacoma's policy succeeded or failed.

Instead, it should help answer:

> **Where did Tacoma create additional housing opportunity, where does representative development appear more or less plausible, and where is that opportunity beginning to translate into applications and permits?**

---

## 3. Central Analytical Framework

Use a four-stage framework.

### Stage 1 — Legal Capacity

Estimate what current zoning allows on each parcel.

Potential measures:

- Existing units
- Modeled base unit capacity
- Modeled bonus capacity, if included
- Net added unit capacity
- Applicable zoning category
- Relevant parking or overlay conditions

### Stage 2 — Physical Plausibility

Screen whether a representative prototype can reasonably fit.

Potential factors:

- Parcel area
- Parcel dimensions and geometry
- Setbacks
- Lot coverage or FAR
- Building footprint
- Existing units
- Access and parking assumptions
- Environmental constraints
- Building retention or demolition assumption

This is a planning-level screening model, not architectural site design.

### Stage 3 — Financial Screening

Apply a simplified, transparent residual-land-value model to one or two representative prototypes.

Do not claim exact parcel-level underwriting.

Use:

- Parcel-specific acquisition benchmark where possible
- Prototype-specific costs
- Market-area revenue assumptions
- Scenario-based financing and return assumptions
- Conservative / baseline / favorable cases

### Stage 4 — Observed Delivery

Where public permit data support it, show:

- Applications
- Proposed units
- Housing type
- Status
- Permit issuance
- Completion or finalization, if available
- Timing
- Relationship to modeled opportunity

---

## 4. What This Project Is — and Is Not

### This project is:

- A portfolio demonstration
- A parcel-level analytical screening tool
- A policy implementation explorer
- A reproducible Python and GIS project
- A scenario-testing interface
- A visual explanation of the housing-delivery process
- A self-directed case study built from public data and documented assumptions

### This project is not:

- An official Tacoma capacity estimate
- An appraisal
- A parcel-specific entitlement determination
- A contractor cost estimate
- A lender-grade pro forma
- A prediction that a parcel will redevelop
- A tool suitable for investment decisions
- A replica of an internal Commerce model
- A substitute for design, utility, title, environmental, or legal due diligence

Use language such as:

- “planning-level estimate”
- “screening result”
- “under baseline assumptions”
- “estimated acquisition benchmark”
- “representative development prototype”
- “stronger / marginal / weaker”
- “sensitive to costs or revenue assumptions”

Avoid:

- “this parcel will develop”
- “this project is feasible” without qualification
- “exact construction cost”
- “official city result”

---

## 5. Important Ethics and Employment Boundary

The user is lightly involved in a Washington State Department of Commerce ADU pro forma project that adapts an existing middle-housing pro forma.

Therefore:

### Do not use:

- Unreleased Commerce files
- Internal formulas or assumptions
- Internal meeting notes
- Unpublished consultant work
- Internal market data
- Internal staff comments
- Any information accessible only through the user's employment
- Work time, work storage, or work devices for this project

### Safe basis:

- Public Tacoma documents
- Public Tacoma and Pierce County data
- Public zoning code
- Public fee schedules
- Public assessor and sales records
- Public permit records
- Public market reports
- Standard real-estate formulas
- Independently collected and documented assumptions

The financial module should be described as an **independent residual-land-value screening model**, not an adaptation of internal Commerce work.

---

## 6. Portfolio Goal

The project should prove that the user can integrate:

- Zoning interpretation
- Housing policy
- Parcel analytics
- Real-estate feasibility
- GIS
- Python
- SQL
- Interactive mapping
- Scenario analysis
- Data QA
- Consulting-style storytelling

The strongest work sample is not simply the live app. The project should eventually produce:

1. A public interactive app
2. A clean GitHub repository
3. A concise methodology and findings memo
4. Static screenshots or exhibits for the application package
5. A short project description suitable for a resume, portfolio, or LinkedIn post

---

## 7. Scope for the First Polished Version

Keep the first release intentionally bounded.

### Geography

- City of Tacoma
- Focus on residential parcels affected by relevant current residential zoning
- Confirm exact zoning categories before implementation

### Prototypes

Start with one primary prototype:

- **Four attached townhouses for sale**

Add one secondary prototype only after the first is working:

- **Four-unit rental multiplex**

Why start with townhouses:

- Revenue is easier to explain
- No capitalization-rate model is required
- Fewer operating assumptions
- Easier to validate visually and financially
- Tacoma's middle-housing context makes the prototype relevant

### Scenarios

Use three named scenarios:

- Conservative
- Baseline
- Favorable

Allow a limited number of user-adjustable assumptions:

- Sale price or rent
- Hard construction cost
- Soft-cost percentage
- Financing allowance or rate
- Required developer return
- Parking configuration
- Fee allowance

Do not expose too many controls in the first version.

---

## 8. Financial Feasibility Method

Use **residual land value (RLV)** as the primary screening metric.

### For-Sale Prototype

```text
Gross Sales Revenue
= Number of Units × Sale Price per Unit
```

```text
Development Costs
= Hard Costs
+ Soft Costs
+ Fees
+ Financing
+ Demolition
+ Contingency
```

```text
Residual Land Value
= Gross Sales Revenue
- Development Costs
- Required Developer Profit
```

```text
Feasibility Margin
= Residual Land Value
- Estimated Property Acquisition Cost
```

### Rental Prototype

```text
Potential Gross Income
= Sum(Monthly Rent × 12) + Other Income
```

```text
Effective Gross Income
= Potential Gross Income × (1 - Vacancy Rate)
```

```text
NOI
= Effective Gross Income - Operating Expenses
```

```text
Stabilized Value
= NOI / Capitalization Rate
```

```text
Residual Land Value
= Stabilized Value
- Non-Land Development Costs
- Required Developer Return
```

### Output Categories

Prefer categories such as:

- Stronger under baseline assumptions
- Marginal / highly sensitive
- Weaker under baseline assumptions
- Physically eligible but financially weak
- Insufficient data

Do not use a definitive yes/no label without a visible qualification.

### Sensitivity

Every result should be tested against at least:

- Lower revenue
- Higher construction cost
- Higher financing cost or return requirement

A parcel should be called “stronger” only when the result remains positive across a reasonable range.

---

## 9. Acquisition Benchmark

Do not compare RLV only with assessor land value when an existing structure is present.

Use this hierarchy:

1. Recent arm's-length sale of the parcel
2. Comparable-sales estimate
3. Total assessed value
4. Market-area fallback

Store an acquisition-source field:

- `recent_sale`
- `comparable_sales_model`
- `assessed_total_value`
- `market_area_fallback`

Also store a confidence category.

---

## 10. Data Strategy

### Core Public Data Categories

#### Parcel and Assessor

Candidate source:

- Pierce County tax parcel polygons
- Pierce County assessor tables
- Land value
- Improvement value
- Total assessed value
- Building characteristics
- Year built
- Existing units
- Sales history
- Land and improvement attributes

#### Zoning and Development Standards

Candidate source:

- City of Tacoma zoning GIS layers
- Current adopted zoning code
- Related zoning-intent or requirements tables
- Parking reduction areas
- Relevant overlays

#### Building Footprints

Candidate source:

- Tacoma or county building-footprint layer
- Prefer recent LiDAR-derived footprints when available

#### Permits

Candidate source:

- Tacoma Accela or permit open-data layer
- Confirm bulk access before depending on it
- Required fields should ideally include:
  - parcel number or address
  - application date
  - permit type
  - project description
  - proposed units
  - existing units
  - status
  - issue date
  - final date
  - valuation, if available

#### Housing Need and Equity

Candidate source:

- ACS five-year estimates
- HUD CHAS
- Block group or tract level
- Potential variables:
  - renter share
  - income
  - cost burden
  - tenure
  - housing age
  - household size
  - displacement vulnerability indicators

#### Market Evidence

Potential public or independently collected sources:

- Pierce County recent sales
- New townhouse and small-lot sales
- Curated rental listing sample
- Public construction cost indices
- Public market reports
- Tacoma fee schedules
- Utility fee schedules

### Data Availability Rule

Before building any major feature, create a short audit:

- Source
- Access method
- Update date
- Join key
- Geographic coverage
- Required fields
- Missingness
- Licensing or use restrictions
- Whether data are raw facts or assumptions

Do not assume a portal listing means the dataset can be downloaded in bulk.

---

## 11. Assumption Strategy

Not every input needs to be a directly observed parcel-level fact.

### Parcel-Specific

- Lot area
- Parcel geometry
- Zoning
- Existing building footprint
- Existing units
- Year built
- Assessed values
- Recent sale
- Environmental or overlay flags
- Permit activity

### Market-Area-Specific

- Sale price per square foot
- Sale price per unit
- Rent per square foot
- Vacancy
- Cap-rate range

### Prototype-Specific

- Unit count
- Unit size
- Gross building area
- Efficiency ratio
- Hard cost per square foot
- Parking configuration
- Construction period
- Soft-cost structure

### Scenario-Specific

- Interest rate
- Required profit
- Cost escalation
- Revenue adjustment
- Fee reduction
- Parking reform

Every assumption must have:

- Value
- Unit
- Source or rationale
- Date
- Scenario
- Notes
- Confidence level

Create a machine-readable assumptions file such as:

`config/assumptions.yaml`

---

## 12. Technical Stack

### Required Analytical Language

Use **Python**.

Reasons:

- Strong fit for geospatial ETL
- Strong fit for parcel-scale processing
- Natural integration with DuckDB and GeoParquet
- Easy to create reproducible scripts and QA checks
- Good fit with the user's existing skills
- Directly satisfies the job requirement for R or Python

Do not add R merely to show both languages.

### Python Libraries

Likely:

- `pandas` or `polars`
- `geopandas`
- `shapely`
- `pyogrio`
- `duckdb`
- `pyarrow`
- `numpy`
- `scipy`, if needed
- `pandera` or `pydantic` for validation
- `requests`
- `pytest`

### GIS

Do not require ArcGIS Pro.

The GIS work should be demonstrated through:

- CRS management
- Spatial joins
- Overlay analysis
- Parcel geometry
- Building-footprint analysis
- Proximity and accessibility calculations
- Cartography
- Interactive spatial filtering
- Spatial QA

QGIS may be used optionally for visual inspection, but should not be a dependency.

### Web Application

Do not use React or TypeScript for the first version.

Use:

- HTML
- CSS
- Modern JavaScript modules
- Vite
- MapLibre GL JS
- deck.gl if parcel scale requires it
- DuckDB-WASM if browser-side querying is useful
- GeoParquet, PMTiles, or optimized GeoJSON
- ECharts or Observable Plot for charts

The user does not currently know React or TypeScript. The project should not be delayed by learning a framework that is not required.

### Hosting

Prefer a static app:

- GitHub Pages
- No backend for the initial release
- Preprocess data in Python
- Load compact optimized assets in the browser

---

## 13. Suggested Repository Structure

```text
tacoma-housing-delivery-gap/
├── README.md
├── PROJECT_BRIEF.md
├── LICENSE
├── .gitignore
├── pyproject.toml
├── environment.yml
├── config/
│   ├── assumptions.yaml
│   ├── data_sources.yaml
│   └── prototypes.yaml
├── data_raw/
│   └── README.md
├── data_interim/
├── data_processed/
│   ├── parcels_model.parquet
│   ├── permits.parquet
│   ├── neighborhoods.parquet
│   └── metadata.json
├── notebooks/
│   ├── 01_data_audit.ipynb
│   ├── 02_capacity_prototype.ipynb
│   └── 03_feasibility_validation.ipynb
├── src/
│   ├── data/
│   │   ├── download.py
│   │   ├── assessor.py
│   │   ├── zoning.py
│   │   ├── permits.py
│   │   └── market.py
│   ├── spatial/
│   │   ├── parcels.py
│   │   ├── buildings.py
│   │   └── overlays.py
│   ├── models/
│   │   ├── capacity.py
│   │   ├── prototypes.py
│   │   ├── residual_land_value.py
│   │   └── scenarios.py
│   ├── qa/
│   │   ├── schema.py
│   │   ├── geometry.py
│   │   └── reports.py
│   └── export/
│       ├── parquet.py
│       └── metadata.py
├── tests/
│   ├── test_capacity.py
│   ├── test_feasibility.py
│   └── test_data_quality.py
├── app/
│   ├── index.html
│   ├── css/
│   │   ├── base.css
│   │   ├── layout.css
│   │   └── components.css
│   ├── js/
│   │   ├── app.js
│   │   ├── state.js
│   │   ├── map.js
│   │   ├── database.js
│   │   ├── filters.js
│   │   ├── scenarios.js
│   │   ├── charts.js
│   │   ├── parcel-panel.js
│   │   └── formatting.js
│   └── assets/
├── docs/
│   ├── methodology.md
│   ├── data_dictionary.md
│   ├── limitations.md
│   ├── findings.md
│   └── concept_mockup.png
└── outputs/
    ├── figures/
    ├── tables/
    └── memo/
```

Do not create every file immediately. Establish the structure, then build only what is needed.

---

## 14. Application Screens

The final visual product should remain close to the concept mockup.

### Opening View

A restrained, map-first interface with:

- Project title
- Short thesis
- Main map
- Mode selector
- Compact filter controls
- Selected-parcel panel
- Bottom analytical strip or linked charts

### Main Map Modes

1. **Added Capacity**
2. **Redevelopment Readiness**
3. **Prototype Feasibility**
4. **Permit Activity**
5. Optional: **Delivery Gap**
6. Optional: **Equity / Vulnerability**

### Selected Parcel Panel

#### Site

- Address
- Parcel number
- Lot area
- Zoning
- Existing use
- Existing units
- Year built
- Building footprint
- Assessed values
- Recent sale

#### Capacity

- Existing units
- Modeled base capacity
- Modeled bonus capacity
- Added capacity
- Physical fit result

#### Prototype

- Housing type
- Units
- Unit size
- Gross building area
- Parking assumption

#### Financial Screen

- Gross revenue
- Hard costs
- Soft costs
- Fees
- Financing
- Required return
- Residual land value
- Acquisition benchmark
- Feasibility margin
- Sensitivity classification

#### Evidence

- Acquisition estimate source
- Market-area source
- Cost source
- Confidence
- Known limitations

### Bottom Dashboard

Possible elements:

- Delivery funnel
- Feasibility by prototype
- Permit activity by zoning or market area
- Scenario change chart

Avoid decorative KPI cards with no analytical purpose.

---

## 15. Visual Design Direction

The product should look like a strong planning-consulting exhibit.

### Desired qualities

- Map-first
- Editorial
- Restrained
- Clear hierarchy
- Generous whitespace
- Compact controls
- Legible typography
- Minimal decoration
- Strong annotation
- Professional but not corporate-generic

### Avoid

- Glassmorphism
- Gradients
- Excessive rounded cards
- Oversized headings
- Bright startup colors
- Decorative icons everywhere
- Generic AI-dashboard appearance
- Too many KPI tiles
- Overly dense control panels

### Suggested visual palette

Use restrained neutral colors:

- Off-white background
- Charcoal text
- Blue-gray
- Muted terracotta
- Soft gray boundaries

Do not encode positive feasibility only as green and negative only as red. Use accessible diverging or categorical colors and text labels.

Reference mockup:

`docs/concept_mockup.png`

---

## 16. Redevelopment Readiness

Do not hide everything inside one opaque score.

Show components separately:

- Added legal capacity
- Improvement-to-total-value ratio
- Existing units versus allowed units
- Building age
- Parcel area
- Building coverage
- Recent sale
- Prototype fit
- Environmental constraints

If a composite measure is added, make it transparent and decomposable.

Possible categories:

- Higher redevelopment readiness
- Moderate
- Lower
- Constrained
- Insufficient data

Do not imply causation.

---

## 17. Delivery Gap Logic

The signature analytical layer can classify parcels or areas by the relationship between capacity, feasibility, and observed activity.

Possible categories:

- High capacity / stronger feasibility / active pipeline
- High capacity / stronger feasibility / no activity
- High capacity / weaker feasibility
- Low capacity / active redevelopment
- Physically constrained
- Insufficient evidence

This is more useful than a single continuous score.

---

## 18. Data Quality and QA Principles

Every processing step should be reproducible.

### Required QA

- CRS validation
- Geometry validity
- Duplicate parcel IDs
- Missing join keys
- Parcel–zoning join coverage
- Assessor join coverage
- Permit geocoding or parcel-match coverage
- Unit-count outliers
- Negative or impossible values
- Building footprint outside parcel
- Capacity lower than existing units
- Feasibility arithmetic checks
- Scenario monotonicity checks

Examples:

- Higher construction cost should not improve feasibility.
- Lower sale price should not improve RLV.
- Higher acquisition cost should not improve margin.
- Bonus capacity should not reduce legal unit count unless a separate cost rule explains it.

Generate a QA summary after every pipeline run.

---

## 19. Documentation Requirements

The repository should contain:

### Methodology

Explain:

- Legal-capacity calculation
- Physical-fit logic
- Prototype assumptions
- RLV formula
- Acquisition benchmark
- Scenarios
- Permit processing
- Equity variables
- Limitations

### Data Dictionary

For every published field:

- Name
- Type
- Unit
- Description
- Source
- Date
- Null meaning

### Assumption Register

For every assumption:

- Value
- Unit
- Source
- Date
- Scenario
- Confidence
- Notes

### Limitations

State clearly:

- Planning-level screening
- No site-specific entitlement review
- No appraisal
- No contractor bid
- No owner-intent prediction
- No utility-capacity confirmation
- No title or environmental due diligence
- Permit data may be incomplete
- Assumptions may become outdated

---

## 20. Development Principles for Codex

1. **Do not change the core project goal.**
2. Build incrementally.
3. Prefer reproducible scripts over manual steps.
4. Keep raw data out of Git when files are large or redistributability is unclear.
5. Create download scripts and documentation instead.
6. Do not fabricate data or findings.
7. Mark all illustrative values clearly.
8. Keep assumptions outside model code.
9. Write tests for financial formulas.
10. Create outputs only after validating joins and units.
11. Do not over-engineer the frontend.
12. Do not introduce React or TypeScript unless the user later requests it.
13. Do not introduce ArcGIS Pro as a dependency.
14. Keep app and analysis loosely coupled.
15. Preserve a clear provenance trail for every public result.
16. Before adding a feature, ask whether it strengthens the application work sample.
17. Prefer a smaller complete product over a large unfinished system.
18. Do not make the interface look generically AI-generated.
19. Do not claim city-grade accuracy.
20. Be transparent about unresolved data limitations.

---

## 21. Ordered Implementation Plan

### Phase 0 — Repository and Project Setup

- Create repository structure
- Add project brief
- Add environment files
- Add data-source registry
- Add assumptions schema
- Add placeholder methodology documentation
- Add concept mockup

### Phase 1 — Data Availability Audit

Deliver:

- Data-source inventory
- Download/access test
- Field inventory
- Join-key assessment
- Coverage and missingness summary
- Permit-data go/no-go decision

Do not begin frontend development before this audit.

### Phase 2 — Parcel Base Table

Build one canonical parcel table with:

- Parcel ID
- Geometry
- Address
- Zoning
- Lot area
- Existing units
- Building footprint
- Year built
- Assessed values
- Recent sale
- Relevant overlays

Deliver:

- `parcels_base.parquet`
- QA summary
- Data dictionary

### Phase 3 — Legal Capacity Model

Start with a simplified, clearly documented rule set.

Deliver:

- Modeled capacity fields
- Capacity QA
- Static map
- Example parcel checks

Do not attempt every edge case in the first pass.

### Phase 4 — Prototype Physical Fit

Implement the four-townhouse prototype.

Deliver:

- Prototype config
- Fit logic
- Physical-fit result
- Example parcel diagrams or checks
- Limitations

### Phase 5 — Financial Model

Implement RLV in Python.

Deliver:

- Unit-tested formulas
- Assumptions file
- Conservative / baseline / favorable scenarios
- Parcel-level screening output
- Sensitivity results

Validate one example manually.

### Phase 6 — Permit Integration

If bulk permit data are usable:

- Clean
- Match to parcels
- Classify project type
- Derive pipeline stages
- Create activity summaries

If not usable:

- Document limitation
- Continue with capacity and feasibility
- Rename or qualify “delivery” claims

### Phase 7 — Web App MVP

Implement:

- Map
- Mode selector
- Parcel click
- Parcel panel
- Scenario selector
- One chart
- Methodology link

### Phase 8 — Visual Refinement

- Improve typography
- Reduce control clutter
- Add annotations
- Add linked charts
- Add delivery funnel
- Refine color and interaction
- Test desktop layout first

### Phase 9 — Findings and Application Package

Create:

- Three to five findings
- Static screenshots
- Short memo
- README
- Portfolio description
- Application-ready work sample

---

## 22. MVP Acceptance Criteria

The first convincing version is complete when:

- A Tacoma parcel map loads reliably
- At least one residential zoning group is modeled
- Clicking a parcel opens a useful detail panel
- Existing units and modeled capacity are shown
- One prototype is physically screened
- One transparent RLV scenario is calculated
- Three scenarios are available
- Feasibility output is qualified, not absolute
- One permit layer or documented permit limitation exists
- At least one linked chart works
- Methodology and limitations are visible
- All published numbers can be traced to public data or assumptions
- The interface is polished enough for screenshots

---

## 23. Questions Codex Should Resolve Early

1. Can Tacoma permit records be downloaded and matched in bulk?
2. Which exact current zoning categories should be included?
3. What rule subset is sufficient for a defensible first-pass capacity model?
4. Which assessor tables contain current units, year built, values, and sales?
5. Is parcel ID consistent across city and county sources?
6. What data format is best for the app at Tacoma scale?
7. Is MapLibre alone sufficient, or is deck.gl needed?
8. Should scenarios be precomputed in Python or calculated in the browser?
9. What minimum rental or sales evidence is sufficient for the portfolio version?
10. Which findings would best align with Cascadia's work?

---

## 24. First Codex Assignment

Begin with **Phase 0 and Phase 1 only**.

### Tasks

1. Create the proposed repository structure, but do not create unnecessary empty files.
2. Copy this brief into `PROJECT_BRIEF.md`.
3. Add the concept mockup to `docs/concept_mockup.png`.
4. Create:
   - `config/data_sources.yaml`
   - `config/assumptions.yaml`
   - `docs/data_audit.md`
5. Research and test public access to:
   - Pierce County parcels
   - Pierce County assessor downloads
   - Tacoma zoning
   - Tacoma building footprints
   - Tacoma permit records
   - Relevant parking or environmental overlays
6. Record:
   - URL
   - access method
   - file or service type
   - update date
   - key fields
   - join key
   - licensing
   - download success
   - limitations
7. Do not begin the capacity model until the audit is complete.
8. Do not invent substitute data when access fails. Document the failure and propose alternatives.

### First Deliverable

A concise data-readiness report answering:

- Which required datasets are publicly accessible?
- Which can be joined at the parcel level?
- Which fields are missing?
- Is the permit layer usable?
- What is the recommended minimum viable analytical scope?

---

## 25. Suggested Public-Facing Description

> **Tacoma Housing Delivery Gap Explorer** is a self-directed housing-policy and development-feasibility case study. The project combines parcel data, zoning regulations, assessor records, permit activity, and a transparent residual-land-value model to examine the difference between housing that is legally allowed and housing that appears more likely to be delivered under alternative market and policy assumptions. Results are intended for exploratory planning analysis rather than site-specific entitlement, appraisal, or investment decisions.

---

## 26. Final Reminder

The project succeeds if it presents a coherent, defensible analysis and communicates it beautifully.

It does not need to solve Tacoma's housing market.

It needs to show that the user understands how to:

- frame the right question,
- construct a parcel-level analytical model,
- handle uncertainty,
- connect policy to implementation,
- and communicate the results in a convincing interactive product.
