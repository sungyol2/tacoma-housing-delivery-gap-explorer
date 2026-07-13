import pandas as pd

from src.data.prepare_parcels import classify_redevelopment_eligibility


def test_existing_use_eligibility_classes() -> None:
    result = classify_redevelopment_eligibility(
        pd.Series(
            ["SINGLE FAMILY DWELLING", "VACANT LAND UNDEVELOPED", "PARKS", "UNKNOWN", "RELIGIOUS SERVICES"],
            index=[10, 20, 30, 40, 50],
        )
    )
    assert result.index.tolist() == [10, 20, 30, 40, 50]
    assert result["redevelopment_eligibility"].tolist() == [
        "candidate",
        "candidate",
        "excluded_existing_use",
        "manual_review",
        "manual_review",
    ]
