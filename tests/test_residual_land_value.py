import pandas as pd

from src.models.residual_land_value import calculate_rental_rlv, calculate_rlv, classify_margin


BASE = {
    "units": 4,
    "gross_building_area_sqft": 5400,
    "sale_price_per_unit": 590000,
    "hard_cost_per_sqft": 200,
    "soft_cost_pct": 0.18,
    "fee_allowance": 55000,
    "financing_allowance": 96000,
    "demolition_allowance": 40000,
    "contingency_pct": 0.05,
    "required_profit_pct": 0.15,
}


def test_rlv_arithmetic_identity() -> None:
    result = calculate_rlv(**BASE)
    assert result["residual_land_value"] == (
        result["gross_revenue"] - result["non_land_cost"] - result["required_profit"]
    )


def test_lower_price_reduces_rlv() -> None:
    baseline = calculate_rlv(**BASE)["residual_land_value"]
    lower = calculate_rlv(**{**BASE, "sale_price_per_unit": 500000})["residual_land_value"]
    assert lower < baseline


def test_higher_hard_cost_reduces_rlv() -> None:
    baseline = calculate_rlv(**BASE)["residual_land_value"]
    higher = calculate_rlv(**{**BASE, "hard_cost_per_sqft": 240})["residual_land_value"]
    assert higher < baseline


def test_higher_profit_requirement_reduces_rlv() -> None:
    baseline = calculate_rlv(**BASE)["residual_land_value"]
    higher = calculate_rlv(**{**BASE, "required_profit_pct": 0.20})["residual_land_value"]
    assert higher < baseline


def test_margin_bands_include_uncertainty_around_zero() -> None:
    result = classify_margin(pd.Series([200_000, 75_000, 0, -100_000, -300_000]))
    assert result.tolist() == ["strong", "moderate", "marginal", "weak", "very_weak"]


def test_sales_costs_reduce_for_sale_rlv() -> None:
    without = calculate_rlv(**BASE)["residual_land_value"]
    with_costs = calculate_rlv(**BASE, sales_and_closing_cost_pct=0.06)["residual_land_value"]
    assert with_costs < without


def test_rental_value_identity_and_cap_rate_direction() -> None:
    inputs = {
        "units": 4, "gross_building_area_sqft": 4000, "monthly_rent_per_unit": 1971,
        "vacancy_pct": 0.05, "operating_expense_pct": 0.32, "cap_rate": 0.057,
        "hard_cost_per_sqft": 240, "soft_cost_pct": 0.18, "fee_allowance": 55000,
        "financing_allowance": 96000, "demolition_allowance": 40000,
        "contingency_pct": 0.05, "required_profit_pct": 0.15,
    }
    result = calculate_rental_rlv(**inputs)
    assert result["stabilized_value"] == result["net_operating_income"] / inputs["cap_rate"]
    assert result["residual_land_value"] == result["stabilized_value"] - result["non_land_cost"] - result["required_profit"]
    higher_cap = calculate_rental_rlv(**{**inputs, "cap_rate": 0.065})
    assert higher_cap["residual_land_value"] < result["residual_land_value"]
