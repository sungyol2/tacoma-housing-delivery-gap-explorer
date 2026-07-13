# Portfolio Release Checklist

## Required before publishing

- [x] Reproducible parcel, zoning, building, critical-area, financial, permit, and web-export pipelines
- [x] Unit tests and machine-readable release checks pass
- [x] Methodology, findings, limitations, data audit, and representative-parcel QA are current
- [x] Oversized uncompressed parcel-detail artifact is excluded from Git
- [x] Apply an MIT license to original code and documentation
- [x] Confirm and publish source-specific reuse, attribution, downstream-notice, and warranty-disclaimer terms
- [ ] Add the final public app URL and repository URL to README after an external GitHub repository exists
- [x] Add a GitHub Pages workflow for the static explorer
- [x] Split parcel details into 16 compressed sections and load only the selected section; use a separate compressed search index
- [x] Add keyboard map-mode navigation, visible focus states, live status messaging, and a captioned model-comparison table
- [ ] Save the four prepared portfolio exhibits after the browser/Windows capture approval is available

## Required exhibits

Use a 1920 Ã— 1080 browser viewport where possible. Do not crop out the disclaimer or selected-parcel evidence.

1. **System overview:** Legal-capacity map with the five-stage funnel visible.
2. **Model correction:** Site-constraints mode with parcel `6245000035` selected; show the mapped constraint status and residual area.
3. **Financial interpretation:** Prototype-feasibility mode under Baseline with a representative marginal parcel selected.
4. **Sensitivity:** Same parcel under **Upside stress test**, retaining enough interface context to show that the scenario changed.

For each image, use a one-sentence evidence caption. Avoid decorative mockups that obscure map labels or methodological warnings.

## Final commands

```powershell
uv sync --extra dev
uv run python src/data/prepare_parcels.py
uv run python src/models/capacity.py
uv run python src/models/physical_fit.py
uv run python src/models/residual_land_value.py
uv run python src/export/web_data.py
uv run python src/qa/representative_parcels.py
uv run python src/qa/release_check.py
uv run python -m pytest -q
```

## Publish gate

Publish only when the app URL works in a clean browser session, the map loads all 16 chunks, the detail dictionary loads, methodology dialogs open without downloads, mobile controls remain usable, and all claims match `app/public/data/summary.json`.

The included Pages workflow publishes the repository root, so the deployed explorer URL ends in `/app/`. Enable **GitHub Actions** as the Pages source after the first push to `main`.
