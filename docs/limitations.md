# Limitations

The project is a self-directed portfolio case study built from public data and independently documented assumptions. It is not an official City of Tacoma capacity analysis, parcel-specific entitlement determination, appraisal, contractor estimate, lender-grade pro forma, or prediction of owner behavior.

Current material limitations:

- Detailed assessor building age, existing-unit, and sales tables have not been ingested.
- Assessed land plus improvement value is a low-confidence acquisition benchmark, not market value.
- Legal capacity omits bonuses and several site-specific code exceptions.
- Critical-area geometry is generalized screening data. It can omit unmapped resources and does not encode every site-specific buffer, geotechnical condition, or permitted modification.
- Public parcel-level utility-easement geometry was not available. Easements are not inferred from utility lines or land-use labels and require title review.
- Physical fit does not derive authoritative frontage, a surveyed building envelope, fire access, utility capacity, parking layout, or tree compliance.
- Financial inputs are partially anchored to public evidence but remain low-confidence screening inputs; they are not a local comparable-sales study, contractor estimate, fee quote, or loan quote.
- The pro forma uses a 4 percent selling-cost allowance, a 4 percent financing proxy rather than a draw schedule, and a 15 percent return-on-total-cost target rather than an IRR. These are screening inputs, not project quotes.
- Demolition is a binary mapped-building allowance rather than a structure-specific estimate.
- Tacoma wastewater and stormwater system development charges changed on July 1, 2026; the current cost-scaled fee proxy does not calculate project-specific applicability, meter size, impervious area, or other departmental charges.
- The five feasibility classes use common absolute-dollar cutoffs across prototypes of different sizes. They are communication bands, not directly comparable returns; normalized margin is shown as a companion diagnostic.
- Housing applications are a separate February 2020–2026 context layer, not a subsequent funnel stage or validation of any selected prototype. The ETL now canonicalizes permit numbers and groups likely projects, but description classification, project relationships, parcel lineage, historical zoning geography, and completion outcomes remain incomplete.
- Current zoning is not applied retroactively to interpret pre-policy applications. The product- and policy-aligned validation cohort is too small for a predictive claim.
