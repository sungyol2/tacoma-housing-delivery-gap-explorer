# Home in Tacoma Housing Application Explorer

Self-directed housing-policy and parcel-GIS case study for Tacoma, Washington.

[Open the live explorer](https://sungyol2.github.io/tacoma-housing-delivery-gap-explorer/app/) · [Methodology](docs/methodology.md) · [Case study](docs/portfolio_case_study.md) · [Exhibit handoff](docs/portfolio_exhibits.md) · [Data terms](DATA_SOURCES_AND_TERMS.md)

The project asks how the volume and mix of housing applications changed after Tacoma's Home in Tacoma regulations took effect on February 1, 2025. Current zoning capacity and mapped parcel constraints provide spatial context; they are not presented as a development forecast.

## 60-second review path

1. Start with the six-year table showing applications, estimated projects, and proposed units.
2. Read the short reform introduction explaining why the explorer focuses on Urban Residential 1, 2, and 3.
3. Use the housing-type table and district filter to see which housing forms account for the change.
4. Switch to **Maximum housing number allowed by zoning** and **Environmental constraints** for supporting parcel context.
5. Select a parcel to see its zoning allowance and a short existing-use/environmental screen. Housing application activity appears in a map popup only when records are present.
6. Search parcel `6245000035` to inspect the wooded N Mildred St example screened by steep-slope and biodiversity mapping.

## Key result

Within the three Urban Residential districts, non-cancelled housing applications increased from a pre-policy annual average of **177.0** to **231** in Home in Tacoma Year One (**+30.5%**). Estimated distinct projects increased from **170.2** to **193** (**+13.4%**), while proposed units in those applications increased from **226.8** to **416** (**+83.4%**).

The divergence matters: units per estimated project rose from **1.33** to **2.16**. Year One proposed more homes than every preceding 12-month period, while its estimated project count remained within the prior five-year range. The comparison is descriptive and does not isolate causation.

## Current status

The reproducible parcel, zoning-capacity, critical-area, housing-application ETL, web-export, and QA pipelines are implemented. The public app:

- starts with a short policy explanation and six-year comparison table;
- maps Year One application parcels as circles sized by proposed homes;
- distinguishes applications, estimated projects, and proposed units;
- explains why the analysis covers the three Urban Residential districts;
- retains gross legal capacity and mapped constraints only as explanatory context;
- removes prototype-feasibility and residual-land-value results from the public interface.

Current processed outputs (kept out of Git by default):

- `data_processed/parcels_base.parquet`: 73,326 unique Tacoma parcels; 58,319 in today's three Urban Residential districts and 56,484 parcels included in the public map
- `data_processed/parcels_capacity.parquet`: gross housing allowance plus parcel application and environmental-map fields used by the public app
- `data_processed/permits.parquet`: 109,415 canonical permit numbers from 109,614 raw Accela rows
- `data_processed/housing_applications.parquet`: text-classified housing applications with policy cohorts, housing type, units, and estimated-project grouping keys
- `outputs/qa/parcels_base_qa.json`: geometry, join, and missingness checks
- `outputs/qa/release_check.json`: static app/data contract

## Reproduce the public app

```powershell
uv sync --extra dev
uv run python src/data/download_arcgis.py tacoma_zoning tacoma_building_footprints_2024 tacoma_accela_permits pierce_tax_parcels tacoma_steep_slopes tacoma_wetland_inventory tacoma_biodiversity_areas tacoma_streams tacoma_flood_insurance_study_2017 tacoma_protected_waters_buffer
uv run python src/data/prepare_parcels.py
uv run python src/models/capacity.py
uv run python src/export/web_data.py
uv run python src/qa/representative_parcels.py
uv run python src/qa/release_check.py
uv run python -m pytest -q
```

Serve the repository root:

```powershell
uv run python -m http.server 4173 --bind 127.0.0.1
```

Then open `http://127.0.0.1:4173/app/`.

The public export divides 56,484 parcel geometries into 16 map chunks totaling about 3.3 MB compressed. Parcel details are fetched on demand from 16 compressed sections totaling about 6.3 MB; address search uses a separate approximately 1.3 MB compressed index.

## Interpretation and terms

This is an independent portfolio case study, not an official City or County product, capacity estimate, causal policy evaluation, entitlement determination, or housing-production forecast. Original code and documentation use the [MIT License](LICENSE); source datasets retain their own terms. See [source attribution and downstream-use terms](DATA_SOURCES_AND_TERMS.md).

Key documents: [methodology](docs/methodology.md), [limitations](docs/limitations.md), [findings](docs/findings.md), [permit ETL](docs/permit_etl.md), [permit gold-set audit](docs/permit_sample_audit.md), and [interface QA](docs/interface_qa.md).
