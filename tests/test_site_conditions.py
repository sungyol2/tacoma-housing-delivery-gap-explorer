import pandas as pd

from src.models.site_conditions import classify_site_conditions


def test_site_condition_classes_are_conservative() -> None:
    result = classify_site_conditions(
        pd.Series(["VACANT LAND UNDEVELOPED", "SINGLE FAMILY DWELLING", "SINGLE FAMILY DWELLING"]),
        pd.Series([0.0, 0.5, 0.8]),
        pd.Series([0.0, 0.2, 0.2]),
    )
    assert result.tolist() == [
        "vacant",
        "partially_vacant_proxy",
        "developed",
    ]
