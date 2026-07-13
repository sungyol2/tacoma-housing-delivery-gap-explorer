"""Observable existing-site condition classes for portfolio screening."""

from __future__ import annotations

import numpy as np
import pandas as pd


def classify_site_conditions(
    land_use: pd.Series,
    improvement_value_ratio: pd.Series,
    building_coverage_ratio: pd.Series,
) -> pd.Series:
    """Classify current site status without claiming parcel-level buildability."""
    use = land_use.fillna("").str.strip().str.upper()
    improvement = improvement_value_ratio.fillna(1.0)
    coverage = building_coverage_ratio.fillna(1.0)
    return pd.Series(
        np.select(
            [
                use.eq("VACANT LAND UNDEVELOPED"),
                improvement.le(0.55) & coverage.le(0.25),
            ],
            ["vacant", "partially_vacant_proxy"],
            default="developed",
        ),
        index=land_use.index,
    )
