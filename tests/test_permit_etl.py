import pandas as pd

from src.data.permit_etl import classify_housing_applications


def permits(rows):
    base = {
        "permit_number": "BLDRN25-0001",
        "permit_type": "Building",
        "permit_subtype": "Residential",
        "permit_category": "New Building",
        "current_status": "Plan Review in Process",
        "application_date": pd.Timestamp("2025-03-01", tz="UTC"),
        "issued_date": pd.NaT,
        "address_line_1": "1 TEST ST",
        "description": "",
        "housing_units": None,
        "parcel_id": "0000000001",
    }
    return pd.DataFrame([{**base, **row} for row in rows])


def test_residential_garage_is_not_a_housing_application():
    result = classify_housing_applications(
        permits([{"description": "Construct a new 528 sf detached garage."}])
    )
    assert not result.iloc[0].housing_application_record
    assert pd.isna(result.iloc[0].housing_type)


def test_garage_at_existing_triplex_is_not_a_new_triplex():
    result = classify_housing_applications(
        permits(
            [
                {
                    "permit_subtype": "Commercial",
                    "description": "Build a detached garage with storage at existing Triplex.",
                }
            ]
        )
    )
    assert not result.iloc[0].housing_application_record


def test_dadu_with_garage_is_retained_as_housing():
    result = classify_housing_applications(
        permits(
            [
                {
                    "description": "Demolish the garage and construct a new DADU with garage.",
                    "housing_units": 1,
                }
            ]
        )
    )
    assert result.iloc[0].housing_application_record
    assert result.iloc[0].housing_type == "backyard_unit"
    assert result.iloc[0].housing_application_reported_units == 1


def test_commercial_fourplex_is_included_and_classified():
    result = classify_housing_applications(
        permits(
            [
                {
                    "permit_number": "BLDCN25-0007",
                    "permit_subtype": "Commercial",
                    "description": "Construct a 2 story, 4-unit fourplex.",
                    "housing_units": 4,
                }
            ]
        )
    )
    row = result.iloc[0]
    assert row.housing_application_record
    assert row.housing_type == "houseplex_3_6"
    assert row.housing_application_reported_units == 4


def test_plural_duplex_project_is_classified():
    result = classify_housing_applications(
        permits(
            [
                {
                    "description": "Construction of 7 units on lot - 3 Duplexes; this is building 2 of 3.",
                    "housing_units": 1,
                }
            ]
        )
    )
    assert result.iloc[0].housing_application_record
    assert result.iloc[0].housing_type == "houseplex_2"
    assert result.iloc[0].housing_application_reported_units == 2


def test_numeric_unit_building_is_classified_without_a_named_housing_type():
    result = classify_housing_applications(
        permits(
            [
                {
                    "description": "Construct a new 8-unit building with site access.",
                    "housing_units": 8,
                }
            ]
        )
    )
    assert result.iloc[0].housing_application_record
    assert result.iloc[0].housing_type == "multiplex_7_20"
    assert result.iloc[0].housing_application_reported_units == 8


def test_structured_unit_new_building_is_retained_as_uncertain_housing():
    result = classify_housing_applications(
        permits(
            [
                {
                    "description": "Construct one of three identical 3-story buildings.",
                    "housing_units": 1,
                }
            ]
        )
    )
    assert result.iloc[0].housing_application_record
    assert result.iloc[0].housing_type == "other_uncertain_housing"
    assert result.iloc[0].housing_application_reported_units == 1


def test_adu_conversion_alteration_is_a_housing_application():
    result = classify_housing_applications(
        permits(
            [
                {
                    "permit_category": "Alteration",
                    "description": "Convert the existing garage into a legal DADU.",
                    "housing_units": 0,
                }
            ]
        )
    )
    assert result.iloc[0].housing_application_record
    assert result.iloc[0].housing_type == "backyard_unit"
    assert result.iloc[0].housing_application_reported_units == 1


def test_repair_to_existing_dadu_does_not_create_a_unit():
    result = classify_housing_applications(
        permits(
            [
                {
                    "permit_category": "Alteration",
                    "description": "Addition to second floor of fire-damaged DADU.",
                    "housing_units": 0,
                }
            ]
        )
    )
    assert not result.iloc[0].housing_application_record


def test_reference_to_separate_dadu_permit_does_not_create_a_unit():
    result = classify_housing_applications(
        permits(
            [
                {
                    "permit_category": "Alteration",
                    "description": "Convert patio to heated space. Separate permit required for DADU conversion.",
                    "housing_units": 0,
                }
            ]
        )
    )
    assert not result.iloc[0].housing_application_record


def test_restoring_dadu_to_garage_does_not_create_a_unit():
    result = classify_housing_applications(
        permits(
            [
                {
                    "permit_category": "Alteration",
                    "description": "Restore DADU to original garage configuration and remove living space.",
                    "housing_units": 0,
                }
            ]
        )
    )
    assert not result.iloc[0].housing_application_record


def test_parenthesized_new_townhome_count_is_used():
    result = classify_housing_applications(
        permits(
            [
                {
                    "description": "Construct (3) New 4-bedroom 4-bathroom Townhomes.",
                    "housing_units": 1,
                },
                {
                    "permit_number": "BLDRN25-0002",
                    "description": "Construct four new townhomes.",
                    "housing_units": 1,
                },
            ]
        )
    ).set_index("permit_number")
    assert result.loc["BLDRN25-0001", "housing_application_reported_units"] == 3
    assert result.loc["BLDRN25-0002", "housing_application_reported_units"] == 4


def test_two_unit_dadu_word_form_is_used():
    result = classify_housing_applications(
        permits(
            [
                {
                    "description": "Construct a new two-unit DADU.",
                    "housing_units": 1,
                }
            ]
        )
    )
    assert result.iloc[0].housing_application_reported_units == 2


def test_new_single_family_permit_with_project_context_stays_detached():
    result = classify_housing_applications(
        permits(
            [
                {
                    "permit_subtype": "Commercial",
                    "description": "New construction of a single-family residence within a 4-plex.",
                    "housing_units": 1,
                }
            ]
        )
    )
    assert result.iloc[0].housing_type == "detached_single_unit"
    assert result.iloc[0].housing_application_reported_units == 1


def test_adu_creation_action_word_variants_are_included():
    descriptions = [
        "Alter existing detached garage into a DADU.",
        "Conversion of existing garage to detached accessory dwelling unit.",
        "Build DADU on existing garage.",
        "Remodel existing garage into DADU unit.",
    ]
    result = classify_housing_applications(
        permits(
            [
                {
                    "permit_number": f"BLDRA25-{index:04d}",
                    "permit_category": "Alteration",
                    "description": description,
                    "housing_units": 0,
                }
                for index, description in enumerate(descriptions, start=1)
            ]
        )
    )
    assert result.housing_application_record.all()
    assert result.housing_type.eq("backyard_unit").all()
    assert result.housing_application_reported_units.eq(1).all()


def test_two_unit_conversion_and_legalization_are_included():
    result = classify_housing_applications(
        permits(
            [
                {
                    "permit_category": "Alteration",
                    "description": "Conversion of detached garage structure to two residential units.",
                    "housing_units": 0,
                },
                {
                    "permit_number": "BLDRA25-0002",
                    "permit_category": "Alteration",
                    "description": "After-the-fact permit to establish property as a two-unit houseplex.",
                    "housing_units": 0,
                },
            ]
        )
    )
    assert result.housing_application_record.all()
    assert result.housing_type.eq("houseplex_2").all()
    assert result.housing_application_reported_units.eq(2).all()


def test_policy_cohorts_use_home_in_tacoma_effective_date():
    result = classify_housing_applications(
        permits(
            [
                {
                    "permit_number": "BLDRN24-0001",
                    "application_date": pd.Timestamp("2025-01-31", tz="UTC"),
                    "description": "Construct a new duplex.",
                },
                {
                    "permit_number": "BLDRN25-0002",
                    "application_date": pd.Timestamp("2025-02-01", tz="UTC"),
                    "description": "Construct a new duplex.",
                },
                {
                    "permit_number": "BLDRN26-0001",
                    "application_date": pd.Timestamp("2026-02-01", tz="UTC"),
                    "description": "Construct a new duplex.",
                },
            ]
        )
    ).set_index("permit_number")
    assert result.loc["BLDRN24-0001", "housing_policy_cohort"] == "pre_home_in_tacoma_5yr"
    assert result.loc["BLDRN25-0002", "housing_policy_cohort"] == "home_in_tacoma_year_1"
    assert result.loc["BLDRN26-0001", "housing_policy_cohort"] == "home_in_tacoma_current_partial"


def test_duplicate_accela_rows_are_canonicalized_without_losing_unit_count():
    result = classify_housing_applications(
        permits(
            [
                {
                    "permit_number": "BLDCN24-0070",
                    "permit_subtype": "Commercial",
                    "current_status": "Precon Meeting Required",
                    "description": "Construct new 225-unit apartment building.",
                    "housing_units": 226,
                },
                {
                    "permit_number": "BLDCN24-0070",
                    "permit_subtype": "Commercial",
                    "current_status": "Permit Issued",
                    "description": "Construct new 225-unit apartment building.",
                    "housing_units": 1,
                },
            ]
        )
    )
    assert len(result) == 1
    assert result.iloc[0].housing_application_reported_units == 225
    assert result.iloc[0].housing_application_status == "issued"


def test_description_units_override_bad_structured_unit_count():
    result = classify_housing_applications(
        permits(
            [
                {
                    "permit_subtype": "Commercial",
                    "description": "Construct an apartment building with one hundred and ten (110) units.",
                    "housing_units": 1,
                }
            ]
        )
    )
    assert result.iloc[0].housing_application_reported_units == 110
    assert result.iloc[0].housing_type == "larger_multifamily_21_plus"


def test_permit_scope_units_override_related_project_total():
    result = classify_housing_applications(
        permits(
            [
                {
                    "description": "Construction of duplex (part of 7 units).",
                    "housing_units": 7,
                },
                {
                    "permit_number": "BLDRN25-0002",
                    "description": "New single-family home within a unit lot subdivision of 4 units total.",
                    "housing_units": 4,
                },
                {
                    "permit_number": "BLDRN25-0003",
                    "description": "New detached garage with 2 bed/1 bath DADU; primary structure is triplex.",
                    "housing_units": 3,
                },
            ]
        )
    ).set_index("permit_number")
    assert result.loc["BLDRN25-0001", "housing_application_reported_units"] == 2
    assert result.loc["BLDRN25-0002", "housing_application_reported_units"] == 1
    assert result.loc["BLDRN25-0003", "housing_application_reported_units"] == 1


def test_plural_rowhouses_are_classified():
    result = classify_housing_applications(
        permits(
            [
                {
                    "description": "Construct three new rowhouses with associated site development.",
                    "housing_units": 3,
                }
            ]
        )
    )
    assert result.iloc[0].housing_type == "rowhouse"
    assert result.iloc[0].housing_application_reported_units == 3


def test_multiple_duplexes_use_the_explicit_permit_scope_count():
    result = classify_housing_applications(
        permits(
            [
                {
                    "description": "Construct three new duplexes of SFD. Each duplex consists of two units.",
                    "housing_units": 1,
                }
            ]
        )
    )
    assert result.iloc[0].housing_type == "houseplex_2"
    assert result.iloc[0].housing_application_reported_units == 6


def test_generic_houseplex_without_a_plausible_unit_count_stays_uncertain():
    result = classify_housing_applications(
        permits(
            [
                {
                    "description": "Construct a new two-story houseplex; each unit is 1178 SF.",
                    "housing_units": 1,
                }
            ]
        )
    )
    assert result.iloc[0].housing_type == "other_uncertain_housing"
    assert result.iloc[0].housing_application_reported_units == 1


def test_existing_residence_context_does_not_create_housing_application():
    result = classify_housing_applications(
        permits(
            [
                {
                    "description": "Construct a kitchen behind an existing residence for a home business.",
                    "housing_units": None,
                }
            ]
        )
    )
    assert not result.iloc[0].housing_application_record


def test_one_of_four_cottages_counts_the_permit_scope_only():
    result = classify_housing_applications(
        permits(
            [
                {
                    "description": "Residential infill pilot: 1 of 4 small cottages with shared common space.",
                    "housing_units": 4,
                }
            ]
        )
    )
    assert result.iloc[0].housing_type == "courtyard_cottage"
    assert result.iloc[0].housing_application_reported_units == 1


def test_related_site_development_number_groups_project():
    result = classify_housing_applications(
        permits(
            [
                {
                    "permit_number": "BLDRN23-0001",
                    "description": "Construct townhome related to SDEV22-0204.",
                    "housing_units": 1,
                },
                {
                    "permit_number": "BLDRN23-0002",
                    "description": "Construct townhome; related SDEV22-0204.",
                    "housing_units": 1,
                },
            ]
        )
    )
    assert result.housing_project_id.nunique() == 1
    assert result.iloc[0].housing_project_id == "SDEV22-0204"
