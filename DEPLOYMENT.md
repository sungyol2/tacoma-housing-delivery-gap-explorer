# Deployment Handoff

The repository uses `.github/workflows/pages.yml` to deploy the repository root. The explorer is served from `/app/`.

## Release commands

```powershell
uv run python src/export/web_data.py
uv run python src/qa/release_check.py
uv run python -m pytest -q
git add -A
git commit -m "Center explorer on Home in Tacoma evidence"
git push
```

## Post-deployment acceptance

- Housing change is the default mode.
- The headline shows applications, likely projects, and proposed units.
- The all-UR result is 177.0 → 231 applications, 170.2 → 193 projects, and 226.8 → 416 units.
- The map legend and encoding refer to Home in Tacoma Year One.
- Housing-type and zone tables update with the UR filter.
- Legal capacity and site constraints appear as supporting context.
- No prototype, financial scenario, feasibility, residual-land-value, or funnel UI appears.
- Parcel search and selection load on-demand detail records.
- Methodology, Limitations, and About open as dialogs.
- Desktop and mobile layouts preserve the explanatory reading order.

Public repository: `https://github.com/sungyol2/tacoma-housing-delivery-gap-explorer`

Live explorer: `https://sungyol2.github.io/tacoma-housing-delivery-gap-explorer/app/`
