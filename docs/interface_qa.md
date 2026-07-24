# Interface QA

## Scope

The primary reading path is explanatory policy comparison plus parcel geography. Housing change is the default mode; legal capacity and mapped constraints are supporting context.

## Required behavior

- The app opens in Housing change mode.
- The first summary shows applications, likely projects, and proposed units.
- The all-UR view displays 177.0 → 231 applications, 170.2 → 193 likely projects, and 226.8 → 416 proposed units.
- Housing-type evidence includes applications, projects, and units.
- Current-zone evidence compares UR1, UR2, and UR3.
- The map colors Home in Tacoma Year One likely projects, not cumulative 2020–current activity.
- Legal capacity is labeled gross and does not imply net added capacity.
- Site constraints are labeled generalized screening evidence.
- Prototype, financial scenario, feasibility, residual-land-value, and development-funnel UI are absent.
- URL state records mode, current zone, and selected parcel.
- Mobile reading order is controls, policy comparison, evidence, then map.
- Parcel details load on demand and retain application, legal-capacity, and constraint evidence.

## Automated coverage

`src/qa/release_check.py` validates the data contract, mode order, map field, policy metrics, caveats, responsive reading order, on-demand details, search index, and absence of prototype/financial fields.

The July 24, 2026 release pass reports:

- 47 Python tests passing;
- all static release-contract checks passing;
- 56,484 unique map, detail, and search records aligned across 16 chunks;
- JavaScript parsed successfully in QuickJS;
- the local app and summary endpoints returning HTTP 200.

## Deployment check

No controllable browser session was available for this release pass. A fresh deployment browser check should therefore confirm MapLibre rendering, parcel selection, UR-zone filtering, search, dialogs, and desktop/mobile layout. This limitation concerns interactive visual QA, not the data-contract checks above.
