# Tacoma Housing Delivery Gap Explorer

Self-directed parcel-level housing policy and development-feasibility case study for Tacoma, Washington.

[Open the live explorer](https://sungyol2.github.io/tacoma-housing-delivery-gap-explorer/app/) · [Methodology](docs/methodology.md) · [Case study](docs/portfolio_case_study.md) · [Exhibit handoff](docs/portfolio_exhibits.md) · [Data terms](DATA_SOURCES_AND_TERMS.md)

The project examines Tacoma's transition from citywide zoning reform to early housing-application activity, then uses parcel constraints and transparent prototype scenarios to explore why legal capacity does not automatically become housing delivery. Results are planning-level screening outputs, not official capacity estimates, causal policy estimates, entitlement determinations, appraisals, or investment advice.

## 60-second review path

1. Open **Housing applications** and compare the five-year pre-policy annual average with Home in Tacoma Year One; use the right panel to see which housing types changed.
2. Change the UR zone filter and note that the policy comparison and type table update together.
3. Switch to **Site constraints** and search `6245000035` to inspect a wooded vacant parcel screened out by steep-slope and biodiversity mapping.
4. Open **Illustrative prototypes** only as a secondary sensitivity demonstration; the financial outputs are not presented as market findings.
5. Open **Methodology** and **Limitations**, then review the concise [case study](docs/portfolio_case_study.md).

Key result: within current UR parcel geography, active housing applications increased from a pre-policy annual average of 177 to 231 in Home in Tacoma Year One, while reported proposed units increased from 226.8 to 416. Tacoma's official review reports 213 applications and 385 units; the independent ETL is shown separately rather than tuned to reproduce the City result. Of 56,484 existing-use candidates, 3,553 are also screened out by mapped constraints. Financial prototype outputs remain an input-sensitive secondary demonstration.

## Current status

The reproducible parcel, zoning-capacity, physical-screen, financial-screen, housing-application, web-export, and QA pipelines are implemented. Financial outputs remain illustrative because market, cost, fee, and acquisition inputs are not underwriting-grade.

The public app registers parcel geometry in 16 map sections. Detailed evidence is also split into 16 compressed sections and fetched only after a parcel is selected; address search loads a separate 1.23 MB compressed index. This avoids downloading and parsing the former 318 MB expanded citywide detail dictionary at startup.

Current processed outputs (kept out of Git by default):

- `data_processed/parcels_base.parquet`: 73,326 unique Tacoma parcels; 58,319 in the UR1/UR2/UR3 zoning inventory, 56,484 existing-use candidates, and parcel-level mapped critical-area screening
- `data_processed/permits.parquet`: 109,415 canonical permit numbers from 109,614 raw Accela rows
- `data_processed/housing_applications.parquet`: canonical, text-classified housing applications from Residential and Commercial workflows, including new buildings and alterations that explicitly create or legalize dwelling units, with Home in Tacoma policy cohorts and likely-project keys
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

The web export divides the parcel map into 16 spatial chunks totaling about 3.8 MB compressed. Parcel details are split into 16 on-demand compressed sections totaling about 18.3 MB; address search uses a separate approximately 1.3 MB compressed index.

## Working principles

- Use only public data and independently documented assumptions.
- Keep raw data out of Git unless redistribution and file size are appropriate.
- Preserve source URLs, access dates, join keys, limitations, and confidence.
- Prefer reproducible Python scripts and machine-readable configuration.
- Qualify all parcel-level outputs as planning-level screening results.

See [PROJECT_BRIEF.md](PROJECT_BRIEF.md) for the complete scope and [docs/data_audit.md](docs/data_audit.md) for current data-readiness findings.

Key interpretation documents: [portfolio case study](docs/portfolio_case_study.md), [methodology](docs/methodology.md), [limitations](docs/limitations.md), [findings](docs/findings.md), [financial model audit](docs/financial_model_audit.md), and [validation audit](docs/validation_audit.md).

Permit classification and the HB 1110/Home in Tacoma timeline are documented in [housing application ETL](docs/permit_etl.md), with difficult examples preserved in the [permit classification gold-set audit](docs/permit_sample_audit.md). Desktop and mobile behavior is recorded in the [interface QA](docs/interface_qa.md).
