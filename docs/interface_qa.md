# Interface QA

## Scope

The primary reading path is reform introduction, six-year application table, and parcel geography. Year One housing applications is the default map; housing allowed by zoning and environmental constraints are supporting context.

## Required behavior

- The app opens with the policy explanation and annual comparison before the map controls.
- The first table shows all five pre-policy 12-month periods, their average, and Year One.
- The all-district view displays 177.0 → 231 applications, 170.2 → 193 estimated projects, and 226.8 → 416 proposed units.
- Urban Residential is written out, and the interface explains why UR-1, UR-2, and UR-3 define the study area.
- Housing-type evidence includes applications, estimated projects, and proposed units.
- The map colors Home in Tacoma Year One estimated projects, not cumulative 2020–current activity.
- Housing allowed by zoning is labeled gross and does not imply net added capacity.
- Environmental constraints are labeled as public-map screening evidence.
- Prototype, financial scenario, feasibility, residual-land-value, and development-funnel UI are absent.
- URL state records mode, selected district, and selected parcel.
- Mobile reading order is reform explanation, annual evidence, controls, map, then parcel details.
- The mobile annual table becomes readable row cards so all three metrics remain visible without horizontal scrolling.
- Parcel details load on demand and retain application, zoning-allowance, and environmental evidence.

## Automated coverage

`src/qa/release_check.py` validates the data contract, mode order, map field, policy metrics, caveats, responsive reading order, on-demand details, search index, and absence of prototype/financial fields.

The July 25, 2026 release pass reports:

- 48 Python tests passing;
- all static release-contract checks passing;
- 56,484 unique map, detail, and search records aligned across 16 chunks;
- JavaScript parsed successfully in QuickJS;
- the local app and summary endpoints returning HTTP 200.

## Browser check

The local app was checked at desktop and 390-pixel mobile widths. The annual table, district filter, environmental-constraint mode, map rendering, readable type sizes, mobile order, and removal of the identified jargon were confirmed in the browser.
