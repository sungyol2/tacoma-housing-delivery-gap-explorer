"""Canonicalize and classify Tacoma Accela housing applications.

Accela's Residential/Commercial subtype is a building-code workflow distinction,
not a housing-product taxonomy.  Small multifamily projects can appear in either
subtype, while Residential/New Building also contains garages and other accessory
structures.  This module therefore uses both structured fields and permit text.
"""

from __future__ import annotations

import re

import numpy as np
import pandas as pd


BASELINE_START = pd.Timestamp("2020-02-01", tz="UTC")
HOME_IN_TACOMA_EFFECTIVE = pd.Timestamp("2025-02-01", tz="UTC")
HOME_IN_TACOMA_YEAR_ONE_END = pd.Timestamp("2026-02-01", tz="UTC")

HOUSING_TYPES = (
    "backyard_unit",
    "houseplex_2",
    "houseplex_3_6",
    "rowhouse",
    "courtyard_cottage",
    "multiplex_7_20",
    "larger_multifamily_21_plus",
    "detached_single_unit",
    "other_uncertain_housing",
)

_STATUS_RANK = {
    "c of o issued": 90,
    "cert of completion issued": 90,
    "finaled": 90,
    "permit finaled": 90,
    "final": 90,
    "final inspection": 80,
    "permit issued": 70,
    "temp co issued": 70,
    "ready to issue": 60,
    "precon meeting required": 55,
    "plan review in process": 50,
    "revision review in process": 50,
    "field revisions": 50,
    "awaiting resubmittal/revisions": 45,
    "revisions required": 45,
    "revisons required": 45,
    "waiting for information": 40,
    "permit fees due": 40,
    "complete application": 40,
    "missing required documents": 35,
    "missing or incorrect info": 35,
    "pending intake screening": 30,
    "pending internal action": 30,
    "expired": 20,
    "permit expired": 20,
    "closed": 20,
    "cancelled": 10,
    "canceled": 10,
    "cancelled - write off": 10,
    "permit canceled": 10,
    "voided": 0,
}

_CANCELLED_STATUSES = {
    "cancelled",
    "canceled",
    "cancelled - write off",
    "permit canceled",
    "voided",
}

_BACKYARD = re.compile(
    r"\b(?:a\.?d\.?u\.?|d\.?a\.?d\.?u\.?|accessory dwelling|backyard (?:house|building)|"
    r"garage apartment|apartment (?:over|above) (?:a |the )?garage)\b",
    re.I,
)
_INTEGRATED_BACKYARD = re.compile(
    r"\b(?:garage apartment|apartment (?:over|above) (?:a |the )?garage|"
    r"(?:adu|dadu|accessory dwelling).{0,40}(?:above|over|with).{0,25}garage|"
    r"garage.{0,40}(?:with|containing|includes?).{0,25}(?:adu|dadu|apartment))\b",
    re.I,
)
_ROWHOUSE = re.compile(r"\b(?:town ?homes?|town ?houses?|row ?houses?)\b", re.I)
_COURTYARD = re.compile(
    r"\b(?:courtyard (?:housing|building)|cottage housing|cottage cluster|clustered cottages?|cottages?)\b",
    re.I,
)
_DUPLEX = re.compile(
    r"\b(?:duplex(?:es)?|two[- ]family|two[- ]unit|2[- ]unit|2[- ]plex)\b", re.I
)
_THREE_TO_SIX = re.compile(
    r"\b(?:triplex|fourplex|fiveplex|sixplex|three[- ]unit|four[- ]unit|five[- ]unit|"
    r"six[- ]unit|[3-6][ -]unit|[3-6][ -]plex|house[- ]?plex)\b",
    re.I,
)
_DETACHED = re.compile(
    r"\b(?:single[- ]family|single family|sfr|sfd|detached (?:house|home|residence)|"
    r"new (?:house|home|residence)|(?:construct|build)(?: a)? new.{0,25}(?:house|home|residence)|"
    r"new construction.{0,30}(?:house|home|residence))\b",
    re.I,
)
_EXPLICIT_NEW_DETACHED = re.compile(
    r"\b(?:new construction of|construct(?:ion)?(?: a)? new|build(?:ing)?(?: a)? new)"
    r".{0,35}(?:single[- ]family|detached (?:house|home|residence)|sfr|sfd)\b",
    re.I,
)
_MULTIFAMILY = re.compile(
    r"\b(?:multi[- ]?family|apartments?|apartment (?:building|complex)|"
    r"residential (?:buildings?|structures?)|independent living|multiplex)\b",
    re.I,
)
_GENERIC_HOUSING = re.compile(
    r"\b(?:dwelling units?|residential units?|housing units?|live ?/ ?work units?|"
    r"\d{1,3}\s*[- ]?\s*units?|residence|dwelling)\b",
    re.I,
)
_NONHOUSING_ONLY = re.compile(
    r"\b(?:garage|carport|shed|deck|patio|pool|gazebo|greenhouse|workshop|"
    r"storage building|accessory structure|pole building|play structure|fence|"
    r"retaining wall|solar|window replacement|test permit)\b",
    re.I,
)
_UNCERTAIN_NEW_HOUSING = re.compile(
    r"\b(?:construct(?:ion)?|build(?:ing)?|new build(?:ing)?)\b.{0,80}\b(?:building|structure)s?\b",
    re.I,
)
_UNIT_PATTERNS = (
    re.compile(r"\b(\d{1,3})\s*[- ]\s*(?:unit|dwelling|apartment|townhome|townhouse)s?\b", re.I),
    re.compile(r"\b(?:containing|consisting of|with)\s*\(?\s*(\d{1,3})\s*\)?\s*(?:residential )?(?:units?|dwellings?|apartments?)\b", re.I),
    re.compile(r"\b\(?\s*(\d{1,3})\s*\)?\s*(?:residential )?(?:units?|dwellings?|apartments?)\b", re.I),
    re.compile(r"\b(single|one)\s+(?:residential )?dwelling unit\b", re.I),
)
_RELATED_PROJECT = re.compile(
    r"\b(SDEV|LU|PRE|WO)\s*#?\s*(\d{2})[- ]?(\d{4})\b", re.I
)
_ADU_CREATION_ACTION = re.compile(
    r"\b(?:add(?:ing|ed)?|alter(?:ed|ing)?|build(?:ing)?|construct(?:ion)?|"
    r"creat(?:e|ing)|convert(?:ed|ing)?|conversion|establish|finish(?:ing|ed)?|"
    r"remodel(?:ed|ing)?|new)\b",
    re.I,
)
_OTHER_UNIT_CREATION = re.compile(
    r"\b(?:convert(?:ed|ing)?|conversion|establish)\b.{0,140}"
    r"\b(?:(?:a|one|two|2)\s+(?:new\s+)?(?:residential\s+)?(?:dwelling\s+)?units?\b|"
    r"two[- ]unit house[- ]?plex\b)",
    re.I,
)


def _creates_adu(description: object) -> bool:
    """Identify alterations that create/legalize a unit, not repairs to an ADU."""

    text = "" if pd.isna(description) else str(description)
    if not _BACKYARD.search(text) or not _ADU_CREATION_ACTION.search(text):
        return False
    if re.search(r"\bnot\s+(?:an?\s+)?(?:adu|dadu)\b", text, re.I):
        return False
    if re.search(
        r"\bseparate permit (?:is )?required\b.{0,80}\b(?:adu|dadu)\b|"
        r"\bseparate permit required for (?:the )?(?:adu|dadu) conversion\b",
        text,
        re.I,
    ):
        return False
    if re.search(
        r"\brestore\b.{0,50}\b(?:adu|dadu)\b.{0,60}\bgarage\b|"
        r"\b(?:adu|dadu)\b.{0,40}\bto (?:the )?(?:original )?garage\b|"
        r"\bconvert\b.{0,30}\b(?:adu|dadu)\b.{0,30}\bto\b.{0,20}\bgarage\b",
        text,
        re.I,
    ):
        return False
    if re.search(r"\bfire[- ]damag\w*.{0,60}\b(?:adu|dadu)\b|\b(?:adu|dadu)\b.{0,60}\bfire[- ]damag", text, re.I):
        return False
    return True


def _creates_other_housing(description: object) -> bool:
    text = "" if pd.isna(description) else str(description)
    if re.search(r"\bno new\b.{0,50}\b(?:unit|dwelling|living area)", text, re.I):
        return False
    return bool(_OTHER_UNIT_CREATION.search(text))


def _other_alteration_units(description: object) -> float:
    text = "" if pd.isna(description) else str(description)
    if re.search(
        r"\b(?:two|2)[- ]?(?:unit)?\s*(?:residential units?|dwelling units?|house[- ]?plex)\b|"
        r"\b(?:two|2)\s+residential units?\b",
        text,
        re.I,
    ):
        return 2.0
    return 1.0


def _description_unit_count(description: object) -> float:
    text = "" if pd.isna(description) else str(description)
    values: list[int] = []
    for pattern in _UNIT_PATTERNS:
        for value in pattern.findall(text):
            values.append(1 if str(value).lower() in {"single", "one"} else int(value))
    plausible = [value for value in values if 1 <= value <= 500]
    if plausible:
        return float(max(plausible))
    word_counts = {
        "duplex": 2,
        "triplex": 3,
        "fourplex": 4,
        "fiveplex": 5,
        "sixplex": 6,
    }
    lowered = text.lower()
    for word, value in word_counts.items():
        if re.search(rf"\b{word}\b", lowered):
            return float(value)
    return np.nan


def _related_project_key(description: object) -> str | None:
    text = "" if pd.isna(description) else str(description)
    matches = _RELATED_PROJECT.findall(text)
    if not matches:
        return None
    priority = {"SDEV": 0, "LU": 1, "PRE": 2, "WO": 3}
    prefix, year, sequence = sorted(
        ((p.upper(), y, s) for p, y, s in matches),
        key=lambda value: priority[value[0]],
    )[0]
    return f"{prefix}{year}-{sequence}"


def _status_group(status: object) -> str:
    value = "" if pd.isna(status) else str(status).strip().lower()
    if value in _CANCELLED_STATUSES:
        return "cancelled_or_voided"
    if value in {"c of o issued", "cert of completion issued", "finaled", "permit finaled", "final", "final inspection"}:
        return "completed_or_final"
    if value in {"permit issued", "temp co issued"}:
        return "issued"
    if value in {"expired", "permit expired", "closed"}:
        return "expired_or_closed"
    return "in_review"


def _cohort(application_date: object) -> str:
    if pd.isna(application_date):
        return "missing_date"
    value = pd.Timestamp(application_date)
    if value < BASELINE_START:
        return "earlier_context"
    if value < HOME_IN_TACOMA_EFFECTIVE:
        return "pre_home_in_tacoma_5yr"
    if value < HOME_IN_TACOMA_YEAR_ONE_END:
        return "home_in_tacoma_year_1"
    return "home_in_tacoma_current_partial"


def _housing_type(description: object, units: object) -> str | None:
    text = "" if pd.isna(description) else str(description)
    unit_count = float(units) if pd.notna(units) else np.nan

    if _INTEGRATED_BACKYARD.search(text):
        return "backyard_unit"
    # Accela descriptions often lead with demolition of a garage and mention the
    # new DADU later.  A positive unit field plus an ADU/DADU term is stronger
    # evidence of housing than the earlier accessory-structure word.
    if _BACKYARD.search(text) and pd.notna(unit_count) and unit_count >= 1:
        return "backyard_unit"
    housing_positions = [
        match.start()
        for pattern in (_BACKYARD, _ROWHOUSE, _COURTYARD, _DUPLEX, _THREE_TO_SIX, _DETACHED, _MULTIFAMILY, _GENERIC_HOUSING)
        if (match := pattern.search(text))
    ]
    nonhousing_match = _NONHOUSING_ONLY.search(text)
    if nonhousing_match and housing_positions and nonhousing_match.start() < min(housing_positions):
        return None
    if _BACKYARD.search(text):
        return "backyard_unit"
    if _COURTYARD.search(text):
        return "courtyard_cottage"
    if _ROWHOUSE.search(text):
        return "rowhouse"
    if _NONHOUSING_ONLY.search(text) and pd.isna(unit_count):
        return None
    if _EXPLICIT_NEW_DETACHED.search(text):
        return "detached_single_unit"
    if _THREE_TO_SIX.search(text):
        if re.search(r"\bhouse[- ]?plex\b", text, re.I) and (
            pd.isna(unit_count) or unit_count < 2
        ):
            return "other_uncertain_housing"
        if unit_count == 2:
            return "houseplex_2"
        if pd.notna(unit_count) and unit_count > 20:
            return "larger_multifamily_21_plus"
        if pd.notna(unit_count) and unit_count > 6:
            return "multiplex_7_20"
        return "houseplex_3_6"
    if _DUPLEX.search(text):
        return "houseplex_2"
    # A permit for one detached home may cite the total units in its related
    # subdivision; the named permit scope takes precedence over that total.
    if _DETACHED.search(text):
        return "detached_single_unit"
    if (_MULTIFAMILY.search(text) or _GENERIC_HOUSING.search(text)) and pd.notna(unit_count):
        if unit_count == 1:
            return "detached_single_unit"
        if unit_count == 2:
            return "houseplex_2"
        if unit_count <= 6:
            return "houseplex_3_6"
        if unit_count <= 20:
            return "multiplex_7_20"
        return "larger_multifamily_21_plus"
    if _GENERIC_HOUSING.search(text) and pd.notna(unit_count):
        return "other_uncertain_housing"
    if _NONHOUSING_ONLY.search(text):
        return None
    # Some Residential/New Building children contain only "one of three
    # buildings" and a structured one-unit value; retain these transparently as
    # uncertain housing instead of silently dropping them or inventing a type.
    if pd.notna(unit_count) and unit_count >= 1 and _UNCERTAIN_NEW_HOUSING.search(text):
        return "other_uncertain_housing"
    return None


_NUMBER_WORDS = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
}


def _number_value(value: str) -> int:
    return int(value) if value.isdigit() else _NUMBER_WORDS[value.lower()]


def _resolved_unit_count(
    description: object,
    source_units: object,
    description_units: object,
    housing_type: object,
) -> float:
    """Resolve units for the permit scope, not a related project's total."""

    text = "" if pd.isna(description) else str(description)
    source = float(source_units) if pd.notna(source_units) and 1 <= float(source_units) <= 500 else np.nan
    described = float(description_units) if pd.notna(description_units) else np.nan
    kind = None if pd.isna(housing_type) else str(housing_type)
    number = r"(\d{1,2}|one|two|three|four|five|six|seven|eight|nine|ten)"

    if kind == "backyard_unit":
        unit_form = re.search(
            rf"(?:\(\s*)?{number}(?:\s*\))?[- ]unit\s+"
            rf"(?:new\s+)?(?:detached\s+)?(?:adus?|dadus?|accessory dwellings?)\b",
            text,
            re.I,
        )
        if unit_form:
            return float(_number_value(unit_form.group(1)))
        match = re.search(
            rf"\b{number}\s+(?:new\s+)?(?:detached\s+)?(?:adus?|dadus?|accessory dwellings?)\b",
            text,
            re.I,
        )
        if match:
            return float(_number_value(match.group(1)))
        if re.search(r"\b(?:adu|dadu)\s*/?\s*duplex\b|\bduplex.{0,30}(?:adus?|dadus?)\b", text, re.I):
            return 2.0
        return source if pd.notna(source) and source <= 2 else 1.0

    if kind == "detached_single_unit":
        match = re.search(
            rf"\b{number}\s+(?:new\s+)?(?:detached\s+)?(?:single[- ]family\s+)?(?:homes?|houses?|residences?)\b",
            text,
            re.I,
        )
        return float(_number_value(match.group(1))) if match else 1.0

    if kind == "houseplex_2":
        multiple_duplexes = re.search(
            rf"\bconstruct(?:ion of)?\s+{number}\s+(?:new\s+)?duplex(?:es)?\b",
            text,
            re.I,
        )
        if multiple_duplexes:
            return float(_number_value(multiple_duplexes.group(1)) * 2)
        # Accela normally assigns one building permit per duplex even when each
        # child description repeats a multi-building project total.
        return 2.0

    if kind == "rowhouse":
        match = re.search(
            rf"(?:\(\s*)?{number}(?:\s*\))?\s+(?:new\s+)?"
            rf"(?:[a-z0-9]+[- ](?:bedroom|bathroom)s?\s+){{0,2}}(?:unit\s+)?"
            rf"(?:town ?homes?|town ?houses?|row ?houses?)\b",
            text,
            re.I,
        )
        if match:
            return float(_number_value(match.group(1)))
        return described if pd.notna(described) else source

    if kind == "courtyard_cottage":
        if re.search(r"\b1\s+of\s+\d{1,2}\b", text, re.I):
            return 1.0
        return described if pd.notna(described) else source

    if kind in {
        "houseplex_3_6",
        "multiplex_7_20",
        "larger_multifamily_21_plus",
        "other_uncertain_housing",
    }:
        return described if pd.notna(described) else source
    return np.nan


def canonicalize_permits(permits: pd.DataFrame) -> pd.DataFrame:
    """Return one canonical row per Accela permit number."""

    result = permits.copy()
    result["_description_length"] = result["description"].fillna("").str.len()
    result["_status_rank"] = (
        result["current_status"].fillna("").str.strip().str.lower().map(_STATUS_RANK).fillna(25)
    )
    result["_source_units"] = pd.to_numeric(result["housing_units"], errors="coerce")
    max_units = result.groupby("permit_number", dropna=False)["_source_units"].transform("max")
    result = result.sort_values(
        ["permit_number", "_status_rank", "_description_length", "_source_units"],
        ascending=[True, False, False, False],
        na_position="last",
    ).drop_duplicates("permit_number", keep="first")
    result["housing_units"] = max_units.loc[result.index]
    return result.drop(columns=["_description_length", "_status_rank", "_source_units"])


def classify_housing_applications(permits: pd.DataFrame) -> pd.DataFrame:
    """Add policy cohort, housing type, unit, status, and project identifiers."""

    result = canonicalize_permits(permits)
    result["description_reported_units"] = result["description"].map(_description_unit_count)
    source_units = pd.to_numeric(result["housing_units"], errors="coerce").where(
        lambda values: values.between(1, 500)
    )
    initial_units = result[
        "description_reported_units"
    ].fillna(source_units)
    result["housing_type"] = [
        _housing_type(description, units)
        for description, units in zip(
            result["description"], initial_units
        )
    ]
    result["housing_application_reported_units"] = [
        _resolved_unit_count(description, source, described, housing_type)
        for description, source, described, housing_type in zip(
            result["description"],
            source_units,
            result["description_reported_units"],
            result["housing_type"],
        )
    ]

    new_building = (
        result["permit_type"].eq("Building")
        & result["permit_subtype"].isin(["Residential", "Commercial"])
        & result["permit_category"].eq("New Building")
    )
    unit_creating_alteration = (
        result["permit_type"].eq("Building")
        & result["permit_subtype"].isin(["Residential", "Commercial"])
        & result["permit_category"].eq("Alteration")
        & result["description"].map(_creates_adu)
    )
    other_unit_creating_alteration = (
        result["permit_type"].eq("Building")
        & result["permit_subtype"].isin(["Residential", "Commercial"])
        & result["permit_category"].eq("Alteration")
        & result["description"].map(_creates_other_housing)
    )
    result.loc[unit_creating_alteration, "housing_type"] = "backyard_unit"
    result.loc[unit_creating_alteration, "housing_application_reported_units"] = 1.0
    result.loc[other_unit_creating_alteration, "housing_type"] = "houseplex_2"
    if other_unit_creating_alteration.any():
        result.loc[
            other_unit_creating_alteration, "housing_application_reported_units"
        ] = result.loc[other_unit_creating_alteration, "description"].map(
            _other_alteration_units
        )
    test_record = result["description"].fillna("").str.contains(
        r"\btest permit\b|\bdo not process\b", case=False, regex=True
    )
    result["housing_application_record"] = (
        (new_building | unit_creating_alteration | other_unit_creating_alteration)
        & result["housing_type"].notna()
        & result["application_date"].ge(BASELINE_START)
        & ~test_record
    )
    result["housing_policy_cohort"] = result["application_date"].map(_cohort)
    result["housing_application_status"] = result["current_status"].map(_status_group)
    result["related_project_key"] = result["description"].map(_related_project_key)

    fallback_location = result["parcel_id"].fillna(
        result["address_line_1"].fillna("unknown-address").str.upper().str.strip()
    )
    fallback_date = result["application_date"].dt.strftime("%Y-%m-%d").fillna("unknown-date")
    fallback_project = (
        "SITE|" + fallback_location.astype(str) + "|" + fallback_date + "|" + result["housing_type"].fillna("unknown")
    )
    result["housing_project_id"] = result["related_project_key"].fillna(fallback_project)
    return result
