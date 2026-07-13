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
8. Capture the four states documented in `docs/portfolio_exhibits.md`.

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
- Baseline and Upside stress test labels match the funnel and selected-parcel pro forma.
- The layout remains usable at desktop and mobile widths.
- The independent-project disclaimer remains visible.

No remote URL is embedded in the repository because none is configured locally yet.
