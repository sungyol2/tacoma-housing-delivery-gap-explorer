import pandas as pd

from src.export.web_data import _policy_comparison


def test_policy_comparison_uses_five_year_annual_average():
    rows = []
    for index in range(10):
        rows.append(
            {
                "permit_number": f"PRE-{index}",
                "housing_project_id": f"PRE-PROJECT-{index}",
                "housing_application_reported_units": 2,
                "housing_policy_cohort": "pre_home_in_tacoma_5yr",
                "housing_type": "houseplex_2",
                "application_date": pd.Timestamp("2024-01-01", tz="UTC"),
            }
        )
    for index in range(3):
        rows.append(
            {
                "permit_number": f"YEAR1-{index}",
                "housing_project_id": f"YEAR1-PROJECT-{index}",
                "housing_application_reported_units": 2,
                "housing_policy_cohort": "home_in_tacoma_year_1",
                "housing_type": "houseplex_2",
                "application_date": pd.Timestamp("2025-06-01", tz="UTC"),
            }
        )

    comparison = _policy_comparison(pd.DataFrame(rows))

    assert comparison["pre_policy_annual_average"]["permit_records"] == 2.0
    assert comparison["pre_policy_annual_average"]["projects"] == 2.0
    assert comparison["pre_policy_annual_average"]["reported_units"] == 4.0
    assert comparison["home_in_tacoma_year_one"]["permit_records"] == 3
    assert comparison["home_in_tacoma_year_one"]["projects"] == 3
    assert comparison["change_pct"]["permit_records"] == 50.0
    assert comparison["change_pct"]["projects"] == 50.0
    assert (
        comparison["by_type"]["houseplex_2"]["pre_policy_annual_average"][
            "reported_units"
        ]
        == 4.0
    )


def test_policy_comparison_publishes_six_aligned_annual_periods():
    rows = [
        {
            "permit_number": f"PERMIT-{year}",
            "housing_project_id": f"PROJECT-{year}",
            "housing_application_reported_units": year - 2018,
            "housing_policy_cohort": (
                "pre_home_in_tacoma_5yr"
                if year < 2025
                else "home_in_tacoma_year_1"
            ),
            "housing_type": "houseplex_2",
            "application_date": pd.Timestamp(f"{year}-06-01", tz="UTC"),
        }
        for year in range(2020, 2026)
    ]

    periods = _policy_comparison(pd.DataFrame(rows))["annual_periods"]

    assert [period["label"] for period in periods] == [
        "Feb. 2020–Jan. 2021",
        "Feb. 2021–Jan. 2022",
        "Feb. 2022–Jan. 2023",
        "Feb. 2023–Jan. 2024",
        "Feb. 2024–Jan. 2025",
        "Feb. 2025–Jan. 2026",
    ]
    assert [period["permit_records"] for period in periods] == [1] * 6
    assert periods[-1]["period_type"] == "year_one"
    assert periods[-1]["reported_units"] == 7
