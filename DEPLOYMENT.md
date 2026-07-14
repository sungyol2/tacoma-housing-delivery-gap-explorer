# Deployment Handoff

The repository includes a GitHub Pages workflow at `.github/workflows/pages.yml`. It deploys the repository root, and the explorer is served from `/app/`.

## First publication

1. Create an empty public GitHub repository.
2. Add it as the local `origin`.
3. Push the local `main` branch.
4. In GitHub repository settings, set **Pages → Build and deployment → Source** to **GitHub Actions**.
5. Run the Pages workflow if it did not start automatically.
6. Open `https://<account>.github.io/<repository>/app/` in a clean current browser.
7. Add the final repository and app URLs to `README.md`.
8. Capture the five states documented in `docs/portfolio_exhibits.md`, beginning with the Home in Tacoma policy comparison.

```powershell
git remote add origin https://github.com/<account>/<repository>.git
git push -u origin main
```

## Post-deployment acceptance

- All 16 parcel map sections render.
- Selecting a parcel loads only its compressed detail section.
- Parcel/address search loads the compressed search index and resolves a record.
- Methodology, Limitations, and About open as dialogs.
- The About dialog links to data terms and the MIT license.
- Housing Applications replaces the development funnel with the policy comparison, and the UR zone filter updates both the headline metrics and housing-type table.
- The all-UR policy comparison displays the independent 177.0-to-231 application change and 226.8-to-416 proposed-unit change while keeping the City 213/385 benchmark separate.
- Baseline and Upside stress test labels match the funnel and selected-parcel pro forma.
- The layout remains usable at desktop and mobile widths.
- The independent-project disclaimer remains visible.

Planned public repository: `https://github.com/sungyol2/tacoma-housing-delivery-gap-explorer`  
Planned live explorer: `https://sungyol2.github.io/tacoma-housing-delivery-gap-explorer/app/`
