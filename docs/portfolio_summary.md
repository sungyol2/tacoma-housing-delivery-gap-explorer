# Portfolio Summary

## Short description

Home in Tacoma Housing Application Explorer combines public Accela, parcel, zoning, building-footprint, and critical-area data to examine how housing application volume and mix changed during the first year of Tacoma's zoning reform.

## What the project demonstrates

- Canonical permit-number ETL across Residential and Commercial workflows
- Text classification of ADUs, detached houses, duplexes, houseplexes, rowhouses, cottages, and multiplexes
- Reproducible likely-project grouping and reported-unit correction
- A policy-aligned five-year annual average versus complete Year One comparison
- Separate application, likely-project, and proposed-unit measures
- Current-zone and housing-type change analysis
- Area-weighted split-zone capacity and mapped critical-area screening
- High-performance MapLibre delivery of more than 56,000 parcel records
- Classification gold-set, representative-parcel, unit-test, and release-contract QA

## Current analytical takeaway

Home in Tacoma Year One contains 231 active applications, 193 likely projects, and 416 reported proposed units, compared with pre-policy annual averages of 177.0, 170.2, and 226.8. Proposed units increased much faster than likely projects, and the mix shifted toward duplexes and larger rowhouse output. The observed change is descriptive and does not establish causation or completed production.

## Appropriate claim

“I built a reproducible permit ETL and parcel-GIS explorer that distinguishes application records, likely projects, and proposed units to evaluate early Home in Tacoma activity by housing type and current UR zone.”

## Resume version

Built a 56,000-parcel Tacoma housing-policy explorer using Python, GeoPandas, public zoning, assessor, critical-area, and Accela data; implemented canonical permit ETL, text-based housing-type classification, likely-project grouping, Home in Tacoma cohort comparisons, and a performant MapLibre interface with reproducible QA.
