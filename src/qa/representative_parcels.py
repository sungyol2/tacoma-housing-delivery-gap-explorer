"""Select reproducible representative parcels and verify published model identities."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


def first_sorted(frame: pd.DataFrame) -> pd.Series:
    return frame.sort_values("parcel_id").iloc[0]


def select_samples(parcels: pd.DataFrame) -> list[tuple[str, pd.Series]]:
    candidate = parcels[parcels["is_primary_residential_scope"]]
    selections = [
        ("vacant", first_sorted(candidate[candidate["site_condition_class"].eq("vacant")])),
        (
            "partially_vacant_proxy",
            first_sorted(candidate[candidate["site_condition_class"].eq("partially_vacant_proxy")]),
        ),
        ("developed", first_sorted(candidate[candidate["site_condition_class"].eq("developed")])),
        ("meaningful_split_zone", first_sorted(candidate[candidate["meaningful_split_zoned"]])),
        ("physical_fit_failure", first_sorted(candidate[~candidate["prototype_basic_fit"]])),
        (
            "baseline_marginal",
            first_sorted(
                candidate[
                    candidate["prototype_basic_fit"]
                    & candidate["baseline_feasibility_class"].eq("marginal")
                ]
            ),
        ),
        (
            "baseline_very_weak",
            candidate[candidate["baseline_feasibility_class"].eq("very_weak")]
            .nsmallest(1, "baseline_feasibility_margin")
            .iloc[0],
        ),
        (
            "housing_application",
            first_sorted(candidate[candidate["housing_application_project_count"].gt(0)]),
        ),
        (
            "excluded_park",
            parcels.loc[parcels["parcel_id"].eq("0221103000")].iloc[0],
        ),
        (
            "critical_area_constrained_out",
            parcels.loc[parcels["parcel_id"].eq("6245000035")].iloc[0],
        ),
    ]
    return selections


def validate_sample(label: str, row: pd.Series) -> list[str]:
    checks: list[str] = []
    if label == "excluded_park":
        assert row["Landuse_Description"] == "PARKS"
        assert not row["is_primary_residential_scope"]
        checks.extend(["assessor use is PARKS", "excluded from candidate scope"])
        return checks

    assert row["is_primary_residential_scope"]
    assert pd.notna(row["modeled_base_capacity_units"])
    assert row["modeled_base_capacity_units"] >= 4
    checks.extend(["candidate scope", "capacity is present and at least four units"])

    if label == "critical_area_constrained_out":
        assert row["critical_area_screen_status"] == "constrained_out"
        assert row["constraint_steep_slope_40pct"]
        assert row["constraint_biodiversity"]
        assert row["largest_unconstrained_area_sqft"] < 5_000
        checks.append("mapped steep slope and biodiversity constraints screen parcel out")

    expected_demo = 40_000 if row["building_footprint_sqft"] > 1 else 0
    assert row["parcel_demolition_allowance"] == expected_demo
    checks.append("demolition allowance matches mapped building presence")

    margin_identity = row["baseline_residual_land_value"] - row["acquisition_benchmark"]
    assert abs(margin_identity - row["baseline_feasibility_margin"]) < 0.01
    checks.append("baseline margin equals RLV minus acquisition benchmark")

    if row["prototype_basic_fit"]:
        assert row["prototype_fit_status"] in {
            "basic_fit",
            "basic_fit_overlay_review",
            "basic_fit_critical_area_review",
        }
    else:
        assert row["prototype_fit_status"] not in {
            "basic_fit",
            "basic_fit_overlay_review",
            "basic_fit_critical_area_review",
        }
    checks.append("physical-fit flag and status agree")
    return checks


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=Path("data_processed/parcels_model.parquet"))
    parser.add_argument("--json", type=Path, default=Path("outputs/qa/representative_parcels.json"))
    parser.add_argument("--markdown", type=Path, default=Path("docs/representative_parcel_qa.md"))
    args = parser.parse_args()

    parcels = pd.read_parquet(args.input)
    records = []
    for sample_type, row in select_samples(parcels):
        checks = validate_sample(sample_type, row)
        records.append(
            {
                "sample_type": sample_type,
                "parcel_id": row["parcel_id"],
                "address": row["Site_Address"],
                "land_use": row["Landuse_Description"],
                "zone": row["BaseZone"],
                "site_condition": row["site_condition_class"],
                "lot_sqft": round(float(row["parcel_area_sqft"])),
                "capacity_units": None
                if pd.isna(row["modeled_base_capacity_units"])
                else int(row["modeled_base_capacity_units"]),
                "physical_fit": bool(row["prototype_basic_fit"]),
                "baseline_class": row["baseline_feasibility_class"],
                "baseline_margin": None
                if pd.isna(row["baseline_feasibility_margin"])
                else round(float(row["baseline_feasibility_margin"])),
                "checks": checks,
            }
        )

    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(records, indent=2), encoding="utf-8")
    lines = [
        "# Representative Parcel QA",
        "",
        "Reproducible model checks selected by parcel ID within each analytical type.",
        "",
        "| Type | Parcel | Address | Use | Zone | Site status | Capacity | Fit | Baseline margin |",
        "|---|---|---|---|---|---|---:|---|---:|",
    ]
    for record in records:
        margin = "—" if record["baseline_margin"] is None else f'${record["baseline_margin"]:,.0f}'
        lines.append(
            f'| {record["sample_type"]} | {record["parcel_id"]} | '
            f'{record["address"] or "—"} | {record["land_use"]} | {record["zone"]} | '
            f'{record["site_condition"]} | {record["capacity_units"] or "—"} | '
            f'{"Yes" if record["physical_fit"] else "No"} | {margin} |'
        )
    lines.extend(
        [
            "",
            "Automated checks confirm scope, capacity presence, demolition treatment, physical-fit status consistency, and the baseline RLV-minus-acquisition identity. Visual source review remains a separate release check.",
        ]
    )
    args.markdown.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(records, indent=2))


if __name__ == "__main__":
    main()
