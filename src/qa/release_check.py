"""Static release checks for the generated web application and data contract."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--app", type=Path, default=Path("app"))
    parser.add_argument("--output", type=Path, default=Path("outputs/qa/release_check.json"))
    args = parser.parse_args()

    summary = json.loads((args.app / "public/data/summary.json").read_text(encoding="utf-8"))
    details = json.loads((args.app / "public/data/parcel_details.json").read_text(encoding="utf-8"))
    feature_ids: set[str] = set()
    detail_chunk_ids: set[str] = set()
    feature_total = 0
    application_point_total = 0
    application_point_units = 0
    for chunk in summary["map_chunks"]:
        data = json.loads((args.app / "public/data" / chunk["file"]).read_text(encoding="utf-8"))
        feature_total += len(data["features"])
        feature_ids.update(feature["properties"]["parcel_id"] for feature in data["features"])
        detail_chunk = json.loads(
            (args.app / "public/data" / chunk["detail_file"]).read_text(encoding="utf-8")
        )
        detail_chunk_ids.update(detail_chunk)
        application_points = json.loads(
            (args.app / "public/data" / chunk["application_point_file"]).read_text(
                encoding="utf-8"
            )
        )
        application_point_total += len(application_points["features"])
        application_point_units += sum(
            int(
                feature["properties"][
                    "housing_cohort__home_in_tacoma_year_1_reported_units"
                ]
            )
            for feature in application_points["features"]
        )

    search_index = json.loads(
        (args.app / "public/data/parcel_search_index.json").read_text(encoding="utf-8")
    )
    search_ids = {item["parcel_id"] for item in search_index}

    html = (args.app / "index.html").read_text(encoding="utf-8")
    js = (args.app / "js/app.js").read_text(encoding="utf-8")
    css = (args.app / "css/app.css").read_text(encoding="utf-8")
    ids = re.findall(r'\bid="([^"]+)"', html)
    duplicate_html_ids = sorted(key for key, count in Counter(ids).items() if count > 1)
    project_root = args.app.parent
    policy = summary.get("housing_policy_comparison", {})
    policy_all = policy.get("by_zone", {}).get("all", {})
    policy_pre_total = policy_all.get("pre_policy_five_year_total", {})
    policy_pre_average = policy_all.get("pre_policy_annual_average", {})

    checks = {
        "summary_matches_map_features": feature_total == summary["parcel_count"],
        "map_ids_are_unique": len(feature_ids) == feature_total,
        "details_match_summary": len(details) == summary["parcel_count"],
        "detail_chunks_match_map": detail_chunk_ids == feature_ids,
        "search_index_matches_map": search_ids == feature_ids,
        "excluded_point_defiance_absent": "0221103000" not in feature_ids,
        "sixteen_map_chunks": summary["map_chunk_count"] == 16,
        "no_duplicate_html_ids": not duplicate_html_ids,
        "policy_mode_is_default": 'mode: "permits"' in js
        and 'data-mode="permits" role="radio" aria-checked="true"' in html,
        "prototype_mode_removed": 'data-mode="feasibility"' not in html
        and "prototype-filter" not in html
        and "prototypeMeta" not in js,
        "financial_ui_removed": "scenario-filter" not in html
        and "residual land value" not in js.lower(),
        "financial_fields_not_published": not any(
            "feasibility" in field or "prototype" in field
            for field in summary.get("published_fields", [])
        ),
        "latest_javascript_asset": "app.js?v=20260725-7" in html,
        "latest_stylesheet_asset": "app.css?v=20260725-7" in html,
        "policy_comparison_visible": (
            "Tacoma opened former single-family neighborhoods to more housing types"
            in html
        ),
        "applications_projects_units_visible": all(
            marker in html
            for marker in [
                "Permit applications",
                "Estimated projects",
                "Proposed units",
                "annual-table-body",
            ]
        ),
        "policy_map_uses_proposed_unit_circles": (
            "application-points-circle" in js
            and "circle-radius" in js
            and "housing_cohort__home_in_tacoma_year_1_reported_units" in js
            and application_point_total
            == sum(chunk["application_points"] for chunk in summary["map_chunks"])
            and application_point_total
            == summary["year_one_application_point_count"]
            and application_point_units == summary["year_one_application_point_units"]
        ),
        "policy_map_period_labeled": (
            "Each circle marks an application parcel" in js
        ),
        "map_headline_universe_caveat": (
            "map totals can differ from the headline application totals" in html.lower()
        ),
        "policy_mobile_reading_order": (
            'classList.toggle("policy-mode", policyMode)' in js
            and ".policy-comparison { order: 1;" in css
            and ".map-region { order: 3; min-height: 68vh; }" in css
        ),
        "policy_cohort_contract": policy.get("effective_date") == "2025-02-01"
        and set(policy.get("by_zone", {})) == {"all", "UR1", "UR2", "UR3"},
        "policy_annualization_correct": all(
            abs(
                policy_pre_average.get(metric, -1)
                - policy_pre_total.get(metric, 0) / 5
            )
            < 0.11
            for metric in ["permit_records", "projects", "reported_units"]
        ),
        "policy_annual_periods_visible_and_aligned": (
            len(policy_all.get("annual_periods", [])) == 6
            and sum(
                period.get("permit_records", 0)
                for period in policy_all.get("annual_periods", [])[:5]
            )
            == policy_pre_total.get("permit_records")
            and policy_all.get("annual_periods", [])[-1].get("permit_records")
            == policy_all.get("home_in_tacoma_year_one", {}).get("permit_records")
            and "comparison.annual_periods" in js
        ),
        "policy_official_benchmark_separate": policy.get(
            "official_year_one_benchmark", {}
        ).get("permit_records")
        == 213
        and policy_all.get("home_in_tacoma_year_one", {}).get("permit_records")
        != 213,
        "details_loaded_on_demand": (
            "ensureParcelDetails(chunkId)" in js
            and "Loading parcel details" in js
        ),
        "details_chunked": "parcel_details_${chunk}.json.gz" in js
        and all("detail_gzip_file" in chunk for chunk in summary["map_chunks"]),
        "search_index_used": "ensureSearchIndex" in js,
        "keyboard_map_modes": '.mode-list").addEventListener("keydown"' in js,
        "live_status_regions": 'aria-live="polite"' in html,
        "comparison_tables_captioned": (
            "Pre-policy annual average → first year after reform" in js
            and "Housing applications, estimated distinct projects, and proposed units"
            in html
        ),
        "short_year_labels_with_period_definition": (
            'period.start.slice(0, 4)' in js
            and "2020–2024</strong> each mean February" in html
        ),
        "applications_and_projects_explained": (
            "One development may require several permit applications" in html
            and "grouped into estimated projects" in html
        ),
        "pre_and_post_rows_contrasted": all(
            marker in css
            for marker in [
                "--rose-soft:",
                ".annual-table .average-row",
                "--teal-soft:",
                ".annual-table .year-one-row",
            ]
        ),
        "housing_type_projects_visible": "<th>Est. projects</th>" in js,
        "urban_residential_scope_explained": all(
            phrase in html
            for phrase in [
                "Urban Residential",
                "UR-1",
                "UR-2",
                "UR-3",
                "Downtown and mixed-use centers follow different zoning rules",
            ]
        ),
        "urban_residential_buttons_visible": (
            html.count('data-zone="') == 4
            and "All UR zoning districts" in html
            and "zone-filter" not in html + js
        ),
        "official_home_in_tacoma_link_visible": (
            'href="https://tacoma.gov/government/departments/'
            'planning-and-development-services/home-in-tacoma/"' in html
            and "Home in Tacoma Explorer" not in html
        ),
        "housing_type_labels_clean_and_unit_sorted": (
            all(
                label in js
                for label in [
                    'backyard_unit: "Accessory dwelling unit"',
                    'houseplex_2: "Duplex"',
                    'rowhouse: "Townhouse"',
                    "ordered by Year One proposed units",
                ]
            )
            and "Backyard / accessory" not in js
            and "Rowhouse / townhouse" not in js
            and "Duplex (2 units)" not in js
        ),
        "project_intensity_visible": "units per estimated project" in js,
        "capacity_context_published": summary.get("capacity_context", {}).get(
            "gross_modeled_units", 0
        )
        > 0,
        "capacity_excludes_mapped_environmental_constraints": (
            summary.get("capacity_context", {}).get("unconstrained_parcel_count")
            == summary.get("critical_area_status", {}).get("no_mapped_constraint")
            and summary.get("capacity_context", {}).get(
                "excluded_environmental_constraint_count"
            )
            == summary["parcel_count"]
            - summary.get("critical_area_status", {}).get("no_mapped_constraint", 0)
            and '["get", "critical_area_screen_status"], "no_mapped_constraint"' in js
        ),
        "capacity_language_and_palette_updated": (
            "Maximum housing number allowed by zoning" in html
            and "#4e2d66" in js
        ),
        "quiet_basemap_and_thin_boundaries": (
            "basemaps.cartocdn.com/light_all" in js
            and '"zoom"], 9, "rgba(72,84,91,0)", 10, "rgba(72,84,91,0.12)"' in js
            and '"zoom"], 9, 0.04, 10, 0.08, 11, 0.32, 13, 0.55, 17, 0.85' in js
            and "lineOpacity: 0.72" in js
        ),
        "clean_map_cursor": (
            "cursor: default !important" in css
            and "cursor: crosshair !important" in css
            and 'style.cursor = "pointer"' not in js
        ),
        "methods_placed_with_annual_table": (
            "intro-heading" not in html + css
            and html.index('class="evidence-heading"')
            < html.index('id="methodology-button"')
            < html.index('class="comparison-scroll"')
        ),
        "parcel_sidebar_reduced_and_activity_popup_added": (
            "showApplicationPopup" in js
            and "Housing application activity" in js
            and "applicationSection" not in js
            and "Building coverage" not in js
        ),
        "header_and_extra_tabs_removed": (
            "app-header" not in html
            and "limitations-button" not in html
            and "about-button" not in html
        ),
        "critical_area_mode_published": "critical_area_screen_status" in js,
        "utility_easement_limitation_visible": (
            "utility-easement boundaries were unavailable" in html.lower()
        ),
        "critical_area_context_visible": (
            "Environmental constraints change what land may be usable" in js
            and summary.get("mapped_constraint_intersection_count") == 11070
        ),
        "requested_jargon_removed": not any(
            phrase in html + js
            for phrase in [
                "Start here",
                ">Geography<",
                "Current UR zone",
                "Mapped intersections",
                "Constrained out",
                "likely projects",
            ]
        ),
        "mit_license_present": (project_root / "LICENSE").exists()
        and "MIT License"
        in (project_root / "LICENSE").read_text(encoding="utf-8"),
        "data_terms_present": (project_root / "DATA_SOURCES_AND_TERMS.md").exists(),
        "independent_scope_visible": "independent portfolio analysis" in html.lower(),
        "exhibit_handoff_present": (
            project_root / "docs/portfolio_exhibits.md"
        ).exists(),
    }
    failed = [key for key, value in checks.items() if not value]
    result = {
        "status": "pass" if not failed else "fail",
        "checks": checks,
        "failed": failed,
        "parcel_count": summary["parcel_count"],
        "map_feature_count": feature_total,
        "detail_count": len(details),
        "duplicate_html_ids": duplicate_html_ids,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
