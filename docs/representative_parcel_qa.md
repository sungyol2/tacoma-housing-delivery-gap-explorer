# Representative Parcel QA

Reproducible model checks selected by parcel ID within each analytical type.

| Type | Parcel | Address | Use | Zone | Site status | Capacity | Fit | Baseline margin |
|---|---|---|---|---|---|---:|---|---:|
| vacant | 0220011003 | ELDON ST | VACANT LAND UNDEVELOPED | UR1 | vacant | 11 | Yes | $-298,624 |
| partially_vacant_proxy | 0220011000 | 731 S MASON AVE | SINGLE FAMILY DWELLING | UR1 | partially_vacant_proxy | 8 | Yes | $-635,624 |
| developed | 0220012007 | 816 N MASON AVE | SINGLE FAMILY DWELLING | UR2 | developed | 5 | Yes | $-642,924 |
| meaningful_split_zone | 0220044032 | 8440 6TH AVE | MULTI FAM APTS 5 UNITS OR MORE | UR2 | developed | 9 | Yes | $-1,291,824 |
| physical_fit_failure | 0220012046 | 822 N STEVENS ST | SINGLE FAMILY DWELLING | UR2 | developed | 4 | No | $-554,524 |
| baseline_marginal | 0320321169 | 8039 S K ST | VACANT LAND UNDEVELOPED | UR1 | vacant | 4 | Yes | $-49,324 |
| baseline_very_weak | 0220123052 | 4302 CENTER ST BLDG P-Z | MULTI FAM APTS 5 UNITS OR MORE | UR3 | developed | 1610 | Yes | $-77,503,924 |
| housing_application | 0220012152 | 821 S HUSON ST | SINGLE FAMILY DWELLING | UR1 | developed | 6 | Yes | $-690,724 |
| excluded_park | 0221103000 | 5400 N PEARL ST | PARKS | UR1 | partially_vacant_proxy | — | No | $-95,926,824 |
| critical_area_constrained_out | 6245000035 | 3014 N MILDRED ST | VACANT LAND UNDEVELOPED | UR1 | vacant | 44 | No | $-53,924 |

Automated checks confirm scope, capacity presence, demolition treatment, physical-fit status consistency, and the baseline RLV-minus-acquisition identity. Visual source review remains a separate release check.
