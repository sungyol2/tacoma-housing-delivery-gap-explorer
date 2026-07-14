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
    for chunk in summary["map_chunks"]:
        data = json.loads((args.app / "public/data" / chunk["file"]).read_text(encoding="utf-8"))
        feature_total += len(data["features"])
        feature_ids.update(feature["properties"]["parcel_id"] for feature in data["features"])
        detail_chunk = json.loads(
            (args.app / "public/data" / chunk["detail_file"]).read_text(encoding="utf-8")
        )
        detail_chunk_ids.update(detail_chunk)

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
        "conservative_removed_from_ui": 'value="conservative"' not in html,
        "split_filter_removed": "split-filter" not in html and "split-filter" not in js,
        "applications_not_in_funnel": "permit-signal" not in html,
        "housing_application_field_used": "housing_application_project_count" in js,
        "broad_permit_field_not_used": "permit_record_count" not in js,
        "physical_failure_not_financially_screened": "Not screened because the selected prototype physical screen did not pass" in js,
        "latest_javascript_asset": "app.js?v=20260713-34" in html,
        "latest_stylesheet_asset": "app.css?v=20260713-21" in html,
        "policy_comparison_visible": "Home in Tacoma comparison" in html,
        "application_mode_precedes_prototypes": html.find('data-mode="permits"') < html.find('data-mode="feasibility"'),
        "financial_mode_explicitly_qualified": "Scenario tests · not underwriting" in html and "transparent sensitivity demonstrations, not market findings" in html,
        "permit_mode_hides_irrelevant_controls": "updateModeUI" in js,
        "permit_mobile_reading_order": 'classList.toggle("permit-mode", permitMode)' in js and "body.permit-mode #permit-comparison { order: 2; }" in css and ".map-region { min-height: 62vh; }" in css,
        "policy_cohort_contract": policy.get("effective_date") == "2025-02-01" and set(policy.get("by_zone", {})) == {"all", "UR1", "UR2", "UR3"},
        "policy_annualization_correct": all(
            abs(policy_pre_average.get(metric, -1) - policy_pre_total.get(metric, 0) / 5) < 0.11
            for metric in ["permit_records", "projects", "reported_units"]
        ),
        "policy_official_benchmark_separate": policy.get("official_year_one_benchmark", {}).get("permit_records") == 213 and policy_all.get("home_in_tacoma_year_one", {}).get("permit_records") != 213,
        "stress_test_labeled": "Upside stress test" in html and "scenario-explanation" in js,
        "details_loaded_on_demand": "ensureParcelDetails(chunkId)" in js and "Loading the detailed parcel record on demand" in js,
        "details_chunked": "parcel_details_${chunk}.json.gz" in js and all("detail_gzip_file" in chunk for chunk in summary["map_chunks"]),
        "search_index_used": "ensureSearchIndex" in js,
        "prototype_comparison_visible": "Three-model comparison" in js,
        "financial_driver_visible": "Value / cost + target profit" in js,
        "rental_break_even_visible": "Break-even monthly rent / unit" in js,
        "keyboard_map_modes": 'document.querySelector(".mode-list").addEventListener("keydown"' in js,
        "live_status_regions": 'aria-live="polite"' in html,
        "comparison_table_captioned": "Physical and financial comparison of the three pilot prototypes" in js,
        "prototype_selector": "prototype-filter" in html and "four_unit_rowhouse_rental" in js,
        "critical_area_mode_published": "critical_area_screen_status" in js,
        "utility_easement_limitation_visible": "utility-easement geometry was not available" in html,
        "critical_area_stage_in_funnel": "metric-constraint-pass" in html and "mapped_constraint_pass_count" in js,
        "mit_license_present": (project_root / "LICENSE").exists() and "MIT License" in (project_root / "LICENSE").read_text(encoding="utf-8"),
        "data_terms_present": (project_root / "DATA_SOURCES_AND_TERMS.md").exists(),
        "independent_government_disclaimer": "not an official City or County product" in html,
        "exhibit_handoff_present": (project_root / "docs/portfolio_exhibits.md").exists(),
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
