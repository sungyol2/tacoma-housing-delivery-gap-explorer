"""Transparent residual-land-value screening for pilot missing-middle prototypes."""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import geopandas as gpd
import numpy as np
import pandas as pd
import yaml

try:
    from src.models.site_conditions import classify_site_conditions
except ModuleNotFoundError:  # Direct script execution used by the documented pipeline.
    from site_conditions import classify_site_conditions


def load_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def assumption_values(config: dict[str, Any]) -> dict[str, float]:
    return {item["id"]: float(item["value"]) for item in config["assumptions"]}


def calculate_rlv(
    *,
    units: int,
    gross_building_area_sqft: float,
    sale_price_per_unit: float,
    hard_cost_per_sqft: float,
    soft_cost_pct: float,
    fee_allowance: float,
    financing_allowance: float,
    demolition_allowance: float,
    contingency_pct: float,
    required_profit_pct: float,
    sales_and_closing_cost_pct: float = 0.0,
) -> dict[str, float]:
    gross_revenue = units * sale_price_per_unit
    sales_and_closing_cost = gross_revenue * sales_and_closing_cost_pct
    hard_cost = gross_building_area_sqft * hard_cost_per_sqft
    soft_cost = hard_cost * soft_cost_pct
    contingency = hard_cost * contingency_pct
    non_land_cost = (
        hard_cost
        + soft_cost
        + fee_allowance
        + financing_allowance
        + demolition_allowance
        + contingency
        + sales_and_closing_cost
    )
    required_profit = non_land_cost * required_profit_pct
    residual_land_value = gross_revenue - non_land_cost - required_profit
    return {
        "gross_revenue": gross_revenue,
        "hard_cost": hard_cost,
        "sales_and_closing_cost": sales_and_closing_cost,
        "soft_cost": soft_cost,
        "fee_allowance": fee_allowance,
        "financing_allowance": financing_allowance,
        "demolition_allowance": demolition_allowance,
        "contingency": contingency,
        "non_land_cost": non_land_cost,
        "required_profit": required_profit,
        "residual_land_value": residual_land_value,
    }


def scenario_result(
    assumptions: dict[str, Any], prototype: dict[str, Any], scenario: str
) -> dict[str, float]:
    values = assumption_values(assumptions)
    adjustment = assumptions["scenario_adjustments"][scenario]
    scale = int(prototype["units"]) / 4
    return calculate_rlv(
        units=int(prototype["units"]),
        gross_building_area_sqft=float(prototype["gross_building_area_sqft"]),
        sale_price_per_unit=values["townhouse_sale_price_per_unit"]
        * adjustment["sale_price_multiplier"],
        hard_cost_per_sqft=values["townhouse_hard_cost_per_gross_sqft"]
        * adjustment["hard_cost_multiplier"],
        soft_cost_pct=values["soft_cost_pct_of_hard_cost"],
        fee_allowance=values["fee_allowance"] * scale,
        financing_allowance=values["financing_allowance"] * scale
        * adjustment["financing_multiplier"],
        demolition_allowance=values["demolition_allowance"],
        contingency_pct=values["contingency_pct_of_hard_cost"],
        required_profit_pct=values["required_developer_profit_pct"]
        * adjustment["required_profit_multiplier"],
        sales_and_closing_cost_pct=values["sales_and_closing_cost_pct"],
    )


def calculate_rental_rlv(
    *, units: int, gross_building_area_sqft: float, monthly_rent_per_unit: float,
    vacancy_pct: float, operating_expense_pct: float, cap_rate: float,
    hard_cost_per_sqft: float, soft_cost_pct: float, fee_allowance: float,
    financing_allowance: float, demolition_allowance: float, contingency_pct: float,
    required_profit_pct: float,
) -> dict[str, float]:
    potential_gross_income = units * monthly_rent_per_unit * 12
    effective_gross_income = potential_gross_income * (1 - vacancy_pct)
    operating_expenses = effective_gross_income * operating_expense_pct
    net_operating_income = effective_gross_income - operating_expenses
    stabilized_value = net_operating_income / cap_rate
    hard_cost = gross_building_area_sqft * hard_cost_per_sqft
    soft_cost = hard_cost * soft_cost_pct
    contingency = hard_cost * contingency_pct
    non_land_cost = hard_cost + soft_cost + fee_allowance + financing_allowance + demolition_allowance + contingency
    required_profit = non_land_cost * required_profit_pct
    residual_land_value = stabilized_value - non_land_cost - required_profit
    return {
        "potential_gross_income": potential_gross_income,
        "effective_gross_income": effective_gross_income,
        "operating_expenses": operating_expenses,
        "net_operating_income": net_operating_income,
        "cap_rate": cap_rate,
        "stabilized_value": stabilized_value,
        "gross_revenue": stabilized_value,
        "hard_cost": hard_cost,
        "soft_cost": soft_cost,
        "fee_allowance": fee_allowance,
        "financing_allowance": financing_allowance,
        "demolition_allowance": demolition_allowance,
        "contingency": contingency,
        "non_land_cost": non_land_cost,
        "required_profit": required_profit,
        "residual_land_value": residual_land_value,
    }


def rental_scenario_result(assumptions: dict[str, Any], prototype: dict[str, Any], scenario: str) -> dict[str, float]:
    values = assumption_values(assumptions)
    adjustment = assumptions["scenario_adjustments"][scenario]
    scale = int(prototype["units"]) / 4
    return calculate_rental_rlv(
        units=int(prototype["units"]),
        gross_building_area_sqft=float(prototype["gross_building_area_sqft"]),
        monthly_rent_per_unit=values["rental_monthly_rent_per_unit"] * adjustment["rent_multiplier"],
        vacancy_pct=values["rental_vacancy_pct"] * adjustment["vacancy_multiplier"],
        operating_expense_pct=values["rental_operating_expense_pct"],
        cap_rate=values["rental_cap_rate"] * adjustment["cap_rate_multiplier"],
        hard_cost_per_sqft=values["rental_hard_cost_per_gross_sqft"] * adjustment["hard_cost_multiplier"],
        soft_cost_pct=values["soft_cost_pct_of_hard_cost"],
        fee_allowance=values["fee_allowance"] * scale,
        financing_allowance=values["financing_allowance"] * scale * adjustment["financing_multiplier"],
        demolition_allowance=values["demolition_allowance"],
        contingency_pct=values["contingency_pct_of_hard_cost"],
        required_profit_pct=values["required_developer_profit_pct"] * adjustment["required_profit_multiplier"],
    )


def one_factor_sensitivity(
    assumptions: dict[str, Any], prototype: dict[str, Any]
) -> dict[str, dict[str, float]]:
    """Hold baseline inputs fixed while moving one primary driver at a time."""
    values = assumption_values(assumptions)
    scale = int(prototype["units"]) / 4
    cases = {
        "sales_down_5": {"sale": 0.95, "hard": 1.0},
        "sales_up_5": {"sale": 1.05, "hard": 1.0},
        "hard_cost_up_5": {"sale": 1.0, "hard": 1.05},
        "hard_cost_down_5": {"sale": 1.0, "hard": 0.95},
    }
    return {
        case: calculate_rlv(
            units=int(prototype["units"]),
            gross_building_area_sqft=float(prototype["gross_building_area_sqft"]),
            sale_price_per_unit=values["townhouse_sale_price_per_unit"] * modifiers["sale"],
            hard_cost_per_sqft=values["townhouse_hard_cost_per_gross_sqft"]
            * modifiers["hard"],
            soft_cost_pct=values["soft_cost_pct_of_hard_cost"],
            fee_allowance=values["fee_allowance"] * scale,
            financing_allowance=values["financing_allowance"] * scale,
            demolition_allowance=values["demolition_allowance"],
            contingency_pct=values["contingency_pct_of_hard_cost"],
            required_profit_pct=values["required_developer_profit_pct"],
            sales_and_closing_cost_pct=values["sales_and_closing_cost_pct"],
        )
        for case, modifiers in cases.items()
    }


def classify_margin(margin: pd.Series) -> pd.Series:
    return pd.Series(
        np.select(
            [
                margin >= 150_000,
                margin >= 50_000,
                margin >= -50_000,
                margin >= -250_000,
            ],
            ["strong", "moderate", "marginal", "weak"],
            default="very_weak",
        ),
        index=margin.index,
    )


def apply_financial_screen(
    parcels: gpd.GeoDataFrame,
    assumptions: dict[str, Any],
    prototype: dict[str, Any],
    fit_column: str = "prototype_basic_fit",
) -> tuple[gpd.GeoDataFrame, dict[str, dict[str, float]]]:
    result = parcels.copy()
    result["acquisition_benchmark"] = result["Land_Value"] + result["Improvement_Value"]
    result["improvement_value_ratio"] = np.where(
        result["acquisition_benchmark"].gt(0),
        result["Improvement_Value"] / result["acquisition_benchmark"],
        np.nan,
    )
    result["site_condition_class"] = classify_site_conditions(
        result["Landuse_Description"],
        result["improvement_value_ratio"],
        result["building_coverage_ratio"],
    )
    result["parcel_demolition_allowance"] = np.where(
        result["building_footprint_sqft"].fillna(0).gt(1),
        assumption_values(assumptions)["demolition_allowance"],
        0.0,
    )
    result["acquisition_source"] = "assessed_land_plus_improvement"
    result["acquisition_confidence"] = "low"
    scenario_outputs: dict[str, dict[str, float]] = {}
    for scenario in ["conservative", "baseline", "favorable"]:
        values = (
            rental_scenario_result(assumptions, prototype, scenario)
            if prototype["tenure"] == "rental"
            else scenario_result(assumptions, prototype, scenario)
        )
        scenario_outputs[scenario] = values
        prefix = f"{scenario}_"
        parcel_non_land_cost = (
            values["non_land_cost"]
            - values["demolition_allowance"]
            + result["parcel_demolition_allowance"]
        )
        profit_rate = values["required_profit"] / values["non_land_cost"]
        result[f"{prefix}required_profit"] = parcel_non_land_cost * profit_rate
        result[f"{prefix}residual_land_value"] = (
            values["gross_revenue"]
            - parcel_non_land_cost
            - result[f"{prefix}required_profit"]
        )
        result[f"{prefix}feasibility_margin"] = (
            result[f"{prefix}residual_land_value"] - result["acquisition_benchmark"]
        )
        result[f"{prefix}normalized_margin"] = (
            result[f"{prefix}feasibility_margin"]
            / result["acquisition_benchmark"].replace(0, np.nan)
        )
        result[f"{prefix}feasibility_class"] = classify_margin(
            result[f"{prefix}feasibility_margin"]
        )
    result["financial_screen_status"] = np.where(
        result[fit_column],
        "illustrative_pending_market_validation",
        "not_screened_physical_fit_failed",
    )
    return gpd.GeoDataFrame(result, geometry="geometry", crs=parcels.crs), scenario_outputs


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input", type=Path, default=Path("data_processed/parcels_physical_fit.parquet")
    )
    parser.add_argument("--assumptions", type=Path, default=Path("config/assumptions.yaml"))
    parser.add_argument("--prototypes", type=Path, default=Path("config/prototypes.yaml"))
    parser.add_argument(
        "--output", type=Path, default=Path("data_processed/parcels_model.parquet")
    )
    parser.add_argument("--qa", type=Path, default=Path("outputs/qa/feasibility_qa.json"))
    args = parser.parse_args()

    parcels = gpd.read_parquet(args.input)
    assumptions = load_yaml(args.assumptions)
    prototypes = load_yaml(args.prototypes)
    default_id = "duplex_for_sale"
    result = parcels.copy()
    prototype_qa = {}
    scenario_outputs = {}
    for prototype_id, prototype in prototypes["prototypes"].items():
        fit_column = f"{prototype_id}__prototype_basic_fit"
        modeled, outputs = apply_financial_screen(parcels, assumptions, prototype, fit_column)
        scenario_outputs[prototype_id] = outputs
        fields = [
            "parcel_demolition_allowance", "acquisition_benchmark", "acquisition_source",
            "acquisition_confidence", "financial_screen_status",
        ] + [f"{scenario}_{suffix}" for scenario in ["conservative", "baseline", "favorable"] for suffix in ["required_profit", "residual_land_value", "feasibility_margin", "normalized_margin", "feasibility_class"]]
        for field in fields:
            result[f"{prototype_id}__{field}"] = modeled[field]
        screened = modeled.loc[modeled[fit_column]]
        prototype_qa[prototype_id] = {
            "tenure": prototype["tenure"],
            "screened_parcels": int(len(screened)),
            "scenario_pro_forma": outputs,
            "baseline_classes": {key: int(value) for key, value in screened["baseline_feasibility_class"].value_counts().items()},
        }
    default_modeled, _ = apply_financial_screen(
        parcels, assumptions, prototypes["prototypes"][default_id], f"{default_id}__prototype_basic_fit"
    )
    for field in [column for column in default_modeled.columns if column in {
        "site_condition_class", "parcel_demolition_allowance", "acquisition_benchmark", "acquisition_source", "acquisition_confidence", "financial_screen_status"
    } or any(column.startswith(f"{scenario}_") for scenario in ["conservative", "baseline", "favorable"])]:
        result[field] = default_modeled[field]
    sensitivity_outputs = one_factor_sensitivity(assumptions, prototypes["prototypes"][default_id])
    result.to_parquet(args.output, index=False)

    screened = result.loc[result[f"{default_id}__prototype_basic_fit"]]
    qa = {
        "generated_at": datetime.now(UTC).isoformat(),
        "status": assumptions["status"],
        "screened_parcels": int(len(screened)),
        "scenario_pro_forma": scenario_outputs[default_id],
        "prototypes": prototype_qa,
        "one_factor_sensitivity": sensitivity_outputs,
        "baseline_classes": {
            key: int(value)
            for key, value in screened["baseline_feasibility_class"].value_counts().items()
        },
        "monotonic_rlv": bool(
            scenario_outputs[default_id]["conservative"]["residual_land_value"]
            <= scenario_outputs[default_id]["baseline"]["residual_land_value"]
            <= scenario_outputs[default_id]["favorable"]["residual_land_value"]
        ),
    }
    args.qa.parent.mkdir(parents=True, exist_ok=True)
    args.qa.write_text(json.dumps(qa, indent=2), encoding="utf-8")
    print(json.dumps(qa, indent=2))


if __name__ == "__main__":
    main()
