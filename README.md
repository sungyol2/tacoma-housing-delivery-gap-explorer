# Tacoma Housing Delivery Gap Explorer

Self-directed parcel-level housing policy and development-feasibility case study for Tacoma, Washington.

[Open the static explorer](app/) · [Methodology](docs/methodology.md) · [Case study](docs/portfolio_case_study.md) · [Exhibit handoff](docs/portfolio_exhibits.md) · [Data terms](DATA_SOURCES_AND_TERMS.md)

The project examines the gap between housing that is legally allowed, physically plausible, financially supportable under transparent scenarios, and visible in the permit pipeline. Results are planning-level screening outputs, not official capacity estimates, entitlement determinations, appraisals, or investment advice.

## 60-second review path

1. Open the app and read the bottom funnel from zoning through mapped constraints, prototype fit, and financial screening.
2. Switch to **Site constraints** and search `6245000035` to inspect a wooded vacant parcel screened out by steep-slope and biodiversity mapping.
3. Switch to **Prototype feasibility**, select a parcel, and use the three-model comparison to inspect physical fit, development value, margin, and classification. The selected model's pro forma also states how much of non-land cost plus target profit its modeled value covers; gray parcels did not pass the physical screen.
4. Open **Methodology** and **Limitations** in the app, then review the concise [case study](docs/portfolio_case_study.md) for findings and design decisions.

Key result: of 56,484 existing-use candidates, 3,553 are screened out by mapped constraints. Physical fit varies across the three pilot models: 50,672 for-sale duplex, 50,672 rental duplex, and 42,331 four-unit rental rowhouse parcels. At baseline, 43 for-sale duplex parcels are within $50,000 of break-even or above; both rental models are entirely very weak under current sourced proxies and illustrative costs.

## Current status

The reproducible parcel, zoning-capacity, physical-screen, financial-screen, housing-application, web-export, and QA pipelines are implemented. Financial outputs remain illustrative because market, cost, fee, and acquisition inputs are not underwriting-grade.

The public app registers parcel geometry in 16 map sections. Detailed evidence is also split into 16 compressed sections and fetched only after a parcel is selected; address search loads a separate 1.23 MB compressed index. This avoids downloading and parsing the former 318 MB expanded citywide detail dictionary at startup.

Current processed outputs (kept out of Git by default):

- `data_processed/parcels_base.parquet`: 73,326 unique Tacoma parcels; 58,319 in the UR1/UR2/UR3 zoning inventory, 56,484 existing-use candidates, and parcel-level mapped critical-area screening
- `data_processed/permits.parquet`: 109,614 Accela permit records
- `outputs/qa/parcels_base_qa.json`: machine-readable geometry, join, and missingness checks
- `data_processed/parcels_capacity.parquet`: simplified UR1/UR2/UR3 baseline capacity
- `data_processed/parcels_physical_fit.parquet`: three prototype-specific physical screens
- `data_processed/parcels_model.parquet`: illustrative RLV architecture; not yet a market finding
- `docs/findings.md`: current decision-oriented findings and qualifications
- `docs/financial_model_audit.md`: formula audit, corrected demolition treatment, and unresolved assumptions
- `docs/representative_parcel_qa.md`: reproducible parcel examples and identity checks

## License and source data

Original code and documentation are released under the [MIT License](LICENSE). Source data retain their own terms. Published derived parcel artifacts include City of Tacoma open data and Pierce County GIS/Assessor data; users must review the [source, attribution, disclaimer, and downstream-use notice](DATA_SOURCES_AND_TERMS.md). This project is not an official product of either government.

Run the pipeline with:

```powershell
uv sync --extra dev
uv run python src/data/download_arcgis.py tacoma_zoning tacoma_building_footprints_2024 tacoma_accela_permits pierce_tax_parcels tacoma_steep_slopes tacoma_wetland_inventory tacoma_biodiversity_areas tacoma_streams tacoma_flood_insurance_study_2017 tacoma_protected_waters_buffer
uv run python src/data/prepare_parcels.py
uv run python src/models/capacity.py
uv run python src/models/physical_fit.py
uv run python src/models/residual_land_value.py
uv run python src/export/web_data.py
uv run python src/qa/representative_parcels.py
uv run python src/qa/release_check.py
uv run python -m pytest -q
```

The current static MVP can be served from the repository root:

```powershell
uv run python -m http.server 4173 --bind 127.0.0.1
```

Then open `http://127.0.0.1:4173/app/`.

The web export divides the parcel map into 16 spatial chunks totaling about 3.6 MB compressed; the largest chunk is under 0.43 MB. A separate approximately 8.4 MB compressed detail dictionary loads in the background for address search and the evidence panel.

## Working principles

- Use only public data and independently documented assumptions.
- Keep raw data out of Git unless redistribution and file size are appropriate.
- Preserve source URLs, access dates, join keys, limitations, and confidence.
- Prefer reproducible Python scripts and machine-readable configuration.
- Qualify all parcel-level outputs as planning-level screening results.

See [PROJECT_BRIEF.md](PROJECT_BRIEF.md) for the complete scope and [docs/data_audit.md](docs/data_audit.md) for current data-readiness findings.

Key interpretation documents: [portfolio case study](docs/portfolio_case_study.md), [methodology](docs/methodology.md), [limitations](docs/limitations.md), [findings](docs/findings.md), [financial model audit](docs/financial_model_audit.md), and [validation audit](docs/validation_audit.md).
