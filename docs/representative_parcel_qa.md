# Representative Parcel QA

Reproducible model checks selected by parcel ID within each analytical type.

| Type | Parcel | Address | Use | Zone | Site status | Capacity | Fit | Baseline margin |
|---|---|---|---|---|---|---:|---|---:|
| vacant | 0220011003 | ELDON ST | VACANT LAND UNDEVELOPED | UR1 | vacant | 11 | Yes | $-271,655 |
| partially_vacant_proxy | 0220011000 | 731 S MASON AVE | SINGLE FAMILY DWELLING | UR1 | partially_vacant_proxy | 8 | Yes | $-608,655 |
| developed | 0220012007 | 816 N MASON AVE | SINGLE FAMILY DWELLING | UR2 | developed | 5 | Yes | $-615,955 |
| meaningful_split_zone | 0220044032 | 8440 6TH AVE | MULTI FAM APTS 5 UNITS OR MORE | UR2 | developed | 9 | Yes | $-1,264,855 |
| physical_fit_failure | 0220012046 | 822 N STEVENS ST | SINGLE FAMILY DWELLING | UR2 | developed | 4 | No | $-527,555 |
| baseline_marginal | 0221237011 | 4344 N LEXINGTON ST | VACANT LAND UNDEVELOPED | UR1 | vacant | 12 | Yes | $-35,055 |
| baseline_very_weak | 0220123052 | 4302 CENTER ST BLDG P-Z | MULTI FAM APTS 5 UNITS OR MORE | UR3 | developed | 1610 | Yes | $-77,476,955 |
| housing_application | 0220012054 | 4312 N 9TH ST | SINGLE FAMILY DWELLING | UR2 | developed | 11 | Yes | $-864,355 |
| excluded_park | 0221103000 | 5400 N PEARL ST | PARKS | UR1 | partially_vacant_proxy | — | No | $-95,899,855 |
| critical_area_constrained_out | 6245000035 | 3014 N MILDRED ST | VACANT LAND UNDEVELOPED | UR1 | vacant | 44 | No | $-22,555 |

Automated checks confirm scope, capacity presence, demolition treatment, physical-fit status consistency, and the baseline RLV-minus-acquisition identity. Visual source review remains a separate release check.
