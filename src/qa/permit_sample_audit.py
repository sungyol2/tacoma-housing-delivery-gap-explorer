"""Generate a reproducible gold-set audit of Year One permit classification."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


REVIEWED_PERMITS = {
    "BLDRN25-0040": ("detached_single_unit", 1, "New SFD is the permit scope."),
    "BLDRN25-0104": ("detached_single_unit", 1, "New SFD with explicit bedrooms and floor area."),
    "BLDRN25-0247": ("detached_single_unit", 1, "One new two-story SFD."),
    "BLDRN25-0341": ("detached_single_unit", 1, "One new three-bedroom SFD."),
    "BLDRN25-0036": ("backyard_unit", 1, "New ADU above a garage."),
    "BLDRA25-0080": ("backyard_unit", 1, "Garage addition explicitly adds one ADU above."),
    "BLDRA25-0293": ("backyard_unit", 1, "Garage conversion creates a DADU."),
    "BLDRN25-0058": ("backyard_unit", 1, "Detached building contains one upper-floor ADU."),
    "BLDRN25-0198": ("backyard_unit", 1, "One new DADU over a garage."),
    "BLDRN26-0035": ("backyard_unit", 2, "Explicit duplex of two DADUs."),
    "BLDRA25-0492": ("houseplex_2", 2, "Garage conversion creates two residential units."),
    "BLDRA26-0037": ("houseplex_2", 2, "After-the-fact legalization of a two-unit houseplex."),
    "BLDRN25-0222": ("houseplex_2", 2, "One duplex building permit within a larger project."),
    "BLDRN25-0216": ("houseplex_2", 2, "One duplex permit within a three-building project."),
    "BLDRN25-0293": ("houseplex_2", 2, "Explicit two-unit duplex."),
    "BLDRN26-0034": ("houseplex_2", 6, "Single permit explicitly constructs three duplexes."),
    "BLDRN25-0118": ("other_uncertain_housing", 1, "Generic houseplex wording lacks a defensible unit count."),
    "BLDRN25-0295": ("houseplex_3_6", 5, "Fiveplex description controls the unit count."),
    "BLDRN25-0306": ("houseplex_3_6", 6, "Explicit six-unit houseplex."),
    "BLDRN25-0052": ("rowhouse", 3, "Parenthesized three-townhome count."),
    "BLDRN25-0053": ("rowhouse", 5, "Parenthesized five-townhome count."),
    "BLDRN25-0205": ("rowhouse", 4, "Explicit four-unit rowhouse building."),
    "BLDRN25-0326": ("rowhouse", 4, "Explicit four-unit rowhouse building."),
    "BLDRN25-0337": ("rowhouse", 5, "Explicit five-unit rowhouse building."),
    "BLDRN25-0300": ("courtyard_cottage", 1, "One courtyard building permit."),
    "BLDRN25-0301": ("courtyard_cottage", 1, "One courtyard building within the shared project."),
    "BLDRN25-0302": ("courtyard_cottage", 1, "One courtyard building within the shared project."),
    "BLDCN25-0036": ("multiplex_7_20", 10, "Explicit ten-unit apartment building."),
    "BLDCN25-0037": ("multiplex_7_20", 8, "Explicit eight-unit multiplex building."),
    "BLDCN25-0038": ("multiplex_7_20", 16, "Commercial workflow, explicit 16-unit building."),
    "BLDCN25-0045": ("multiplex_7_20", 8, "Explicit eight-unit houseplex."),
    "BLDRN26-0017": ("other_uncertain_housing", 1, "Housing building is clear; form is not stated."),
    "BLDRN26-0018": ("other_uncertain_housing", 1, "Housing building is clear; form is not stated."),
    "BLDRN26-0019": ("other_uncertain_housing", 1, "Housing building is clear; form is not stated."),
    "BLDRA25-0306": (None, None, "Restores a DADU to a garage; no unit is created."),
    "BLDRA25-0475": (None, None, "Patio scope only; DADU requires a separate permit."),
    "BLDRN25-0188": (None, None, "Detached garage only."),
}


def _markdown_table(frame: pd.DataFrame) -> str:
    columns = [str(column) for column in frame.columns]
    header = "| " + " | ".join(columns) + " |"
    divider = "|" + "|".join("---" for _ in columns) + "|"
    rows = [
        "| "
        + " | ".join(str(value).replace("|", "\\|").replace("\n", " ") for value in row)
        + " |"
        for row in frame.itertuples(index=False, name=None)
    ]
    return "\n".join([header, divider, *rows])


def main() -> None:
    permits = pd.read_parquet("data_processed/permits.parquet").set_index("permit_number")
    parcels = pd.read_parquet(
        "data_processed/parcels_base.parquet",
        columns=["parcel_id", "is_ur_zoning_scope"],
    )

    reviewed_rows = []
    failures = []
    for permit_number, (expected_type, expected_units, reason) in REVIEWED_PERMITS.items():
        row = permits.loc[permit_number]
        observed_type = row["housing_type"] if row["housing_application_record"] else None
        observed_units = (
            int(row["housing_application_reported_units"])
            if row["housing_application_record"]
            else None
        )
        passed = observed_type == expected_type and observed_units == expected_units
        if not passed:
            failures.append(permit_number)
        reviewed_rows.append(
            {
                "permit": permit_number,
                "expected_type": expected_type or "excluded",
                "expected_units": expected_units if expected_units is not None else "n/a",
                "observed_type": observed_type or "excluded",
                "observed_units": observed_units if observed_units is not None else "n/a",
                "review_basis": reason,
                "result": "pass" if passed else "FAIL",
            }
        )

    year_one = permits.loc[
        permits["housing_application_record"]
        & permits["housing_policy_cohort"].eq("home_in_tacoma_year_1")
        & permits["housing_application_status"].ne("cancelled_or_voided")
    ].reset_index().merge(parcels, on="parcel_id", how="inner")
    year_one = year_one.loc[year_one["is_ur_zoning_scope"]]

    type_summary = (
        year_one.groupby("housing_type")
        .agg(
            applications=("permit_number", "nunique"),
            likely_projects=("housing_project_id", "nunique"),
            proposed_units=("housing_application_reported_units", "sum"),
        )
        .reset_index()
    )
    reviewed = pd.DataFrame(reviewed_rows)
    coverage = (
        reviewed.loc[reviewed["expected_type"].ne("excluded")]
        .groupby("expected_type")
        .agg(reviewed_records=("permit", "nunique"), passing=("result", lambda values: int(values.eq("pass").sum())))
        .reset_index()
    )
    lines = [
        "# Permit Classification Gold-Set Audit",
        "",
        "This audit records a deterministic manual-review sample of Tacoma Home in Tacoma Year One applications. It is a regression fixture, not a statistically representative accuracy estimate.",
        "",
        f"- Active current-UR applications: **{len(year_one):,}**",
        f"- Likely projects: **{year_one['housing_project_id'].nunique():,}**",
        f"- Reported proposed units: **{int(year_one['housing_application_reported_units'].sum()):,}**",
        f"- Gold-set records passing: **{int(reviewed['result'].eq('pass').sum())} / {len(reviewed)}**",
        "",
        "## Active Year One classification",
        "",
        _markdown_table(type_summary),
        "",
        "## Reviewed gold set",
        "",
        "The fixed sample spans every housing type observed in the active current-UR Year One comparison. Rare categories use their full small population; common categories use multiple construction descriptions. Three deliberate nonhousing false positives are also retained.",
        "",
        _markdown_table(coverage),
        "",
        _markdown_table(reviewed),
        "",
        "## Deliberate exclusions",
        "",
        "Repairs and remodels that do not create a unit remain excluded even when their descriptions mention an existing SFD, duplex, apartment, ADU, or DADU. Group sleeping facilities are also excluded because sleeping units are not shown to be independent dwelling units. Cancelled and voided applications remain in the canonical table but are excluded from the policy comparison.",
        "",
        "## Remaining review risk",
        "",
        "The gold set covers known difficult text patterns, but it does not measure full-population precision or recall. Project lineage, parcel changes, uncommon abbreviations, and incomplete source descriptions still require periodic manual review.",
        "",
    ]
    output = Path("docs/permit_sample_audit.md")
    output.write_text("\n".join(lines), encoding="utf-8")
    if failures:
        raise AssertionError(f"Permit gold-set failures: {', '.join(failures)}")
    print(f"Wrote {output} with {len(reviewed)} reviewed records.")


if __name__ == "__main__":
    main()
