const state = {
  mode: "permits",
  zone: "all",
  selectedId: null,
  details: {},
  detailPromises: new Map(),
  searchIndex: null,
  searchPromise: null,
  summary: null,
  fillLayers: [],
  lineLayers: [],
  pointLayers: [],
  selectedFeature: null,
  mapReady: false,
  expectedSources: 0,
  loadedSources: new Set(),
  dataVersion: "",
  popup: null,
  handledMapClicks: new WeakSet()
};

const modeStyles = {
  permits: {
    paint: "#f7f5ef",
    fillOpacity: 0.12,
    lineWidth: ["interpolate", ["linear"], ["zoom"], 9, 0.26, 13, 0.45, 17, 0.72],
    lineOpacity: 0.5,
    legend: [["1 proposed home", "#247b83", 6], ["2–4 proposed homes", "#247b83", 9], ["5–9 proposed homes", "#247b83", 13], ["10+ proposed homes", "#247b83", 17]],
    note: "Each circle marks an application parcel; circle size represents proposed homes."
  },
  capacity: {
    paint: ["interpolate", ["linear"], ["get", "modeled_base_capacity_units"], 4, "#eee8f2", 6, "#c7acd3", 8, "#8a5ca2", 16, "#4e2d66"],
    fillOpacity: 0.64,
    lineWidth: ["interpolate", ["linear"], ["zoom"], 9, 0.04, 13, 0.1, 17, 0.24],
    lineOpacity: 0.38,
    legend: [["4 homes allowed", "#eee8f2"], ["6 homes allowed", "#c7acd3"], ["8 homes allowed", "#8a5ca2"], ["16 or more homes allowed", "#4e2d66"]],
    note: "Parcels with mapped environmental constraints are omitted. Existing homes are not subtracted."
  },
  readiness: {
    paint: ["match", ["get", "critical_area_screen_status"], "no_mapped_constraint", "#dce8c8", "moderate_slope_review", "#d3a12f", "mapped_constraint_review", "#c8794f", "constrained_out", "#815a68", "#a8a9a4"],
    fillOpacity: 0.64,
    lineWidth: ["interpolate", ["linear"], ["zoom"], 9, 0.04, 13, 0.1, 17, 0.24],
    lineOpacity: 0.38,
    legend: [["No listed environmental area or hazard", "#dce8c8"], ["Part of parcel has 25–40% slopes", "#d3a12f"], ["Mapped area or hazard; review needed", "#c8794f"], ["Less than 5,000 sq. ft. remains outside mapped areas", "#815a68"]],
    note: "A first screen using public environmental maps, not a site-specific determination."
  }
};

const map = new maplibregl.Map({
  container: "map",
  center: [-122.45, 47.245],
  zoom: 11.2,
  minZoom: 9,
  style: {
    version: 8,
    sources: {
      osm: {
        type: "raster",
        tiles: [
          "https://a.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png",
          "https://b.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png",
          "https://c.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png",
          "https://d.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"
        ],
        tileSize: 256,
        attribution: "© OpenStreetMap contributors © CARTO"
      }
    },
    layers: [{
      id: "osm",
      type: "raster",
      source: "osm",
      paint: { "raster-opacity": 0.94 }
    }]
  }
});
map.addControl(new maplibregl.NavigationControl({ visualizePitch: false }), "bottom-left");

async function loadCompressedJson(path) {
  if (!("DecompressionStream" in window)) {
    throw new Error("Compressed parcel details require a current browser.");
  }
  const response = await fetch(path);
  if (!response.ok) throw new Error(`Data request failed: ${response.status}`);
  const stream = response.body.pipeThrough(new DecompressionStream("gzip"));
  return JSON.parse(await new Response(stream).text());
}

function loadParcelDetails(chunkId) {
  const chunk = String(chunkId).padStart(2, "0");
  return loadCompressedJson(`./public/data/parcel_details_${chunk}.json.gz?v=${encodeURIComponent(state.dataVersion)}`);
}

function ensureParcelDetails(chunkId) {
  if (state.detailPromises.has(chunkId)) return state.detailPromises.get(chunkId);
  const promise = loadParcelDetails(chunkId)
    .then(details => {
      Object.assign(state.details, details);
      return details;
    })
    .catch(error => {
      state.detailPromises.delete(chunkId);
      throw error;
    });
  state.detailPromises.set(chunkId, promise);
  return promise;
}

function ensureSearchIndex() {
  if (state.searchIndex) return Promise.resolve(state.searchIndex);
  if (!state.searchPromise) {
    state.searchPromise = loadCompressedJson(`./public/data/parcel_search_index.json.gz?v=${encodeURIComponent(state.dataVersion)}`)
      .then(index => {
        state.searchIndex = index;
        return index;
      })
      .catch(error => {
        state.searchPromise = null;
        throw error;
      });
  }
  return state.searchPromise;
}

async function loadSummary() {
  const response = await fetch("./public/data/summary.json", { cache: "no-store" });
  if (!response.ok) throw new Error(`Summary request failed: ${response.status}`);
  return response.json();
}

function number(value, digits = 0) {
  return value == null ? "Not available" : new Intl.NumberFormat("en-US", { maximumFractionDigits: digits }).format(value);
}

function signedPercent(value) {
  if (value == null) return "Not available";
  return `${value > 0 ? "+" : ""}${number(value, 1)}%`;
}

function counted(value, singular, plural = `${singular}s`) {
  return `${number(value)} ${Number(value) === 1 ? singular : plural}`;
}

function label(value) {
  return String(value ?? "Not available").replaceAll("_", " ");
}

function housingTypeLabel(value) {
  const names = {
    backyard_unit: "Accessory dwelling unit",
    houseplex_2: "Duplex",
    houseplex_3_6: "3–6 unit building",
    rowhouse: "Townhouse",
    courtyard_cottage: "Courtyard or cottage cluster",
    multiplex_7_20: "7–20 unit building",
    larger_multifamily_21_plus: "Apartment building (21+ units)",
    detached_single_unit: "Detached single-family house",
    other_uncertain_housing: "Other or unclear"
  };
  return names[value] || label(value);
}

function housingTypeLabels(value) {
  return value ? value.split("|").map(housingTypeLabel).join(" · ") : "None";
}

function zoneLabel(value) {
  const names = {
    all: "All three Urban Residential districts",
    UR1: "UR-1",
    UR2: "UR-2",
    UR3: "UR-3"
  };
  return names[value] || value;
}

function zoneCompositionLabel(value) {
  return String(value || "Not available").replaceAll(/UR([123])/g, "UR-$1");
}

function siteConditionLabel(value) {
  const names = {
    vacant: "Vacant",
    partially_vacant_proxy: "Partially developed (screening estimate)",
    developed: "Developed"
  };
  return names[value] || "Not available";
}

function constraintStatusLabel(value) {
  const names = {
    no_mapped_constraint: "No listed environmental area or hazard",
    moderate_slope_review: "Part of parcel has 25–40% slopes",
    mapped_constraint_review: "Mapped environmental area or hazard; site review needed",
    constrained_out: "Less than 5,000 sq. ft. remains outside mapped environmental areas"
  };
  return names[value] || "Not available";
}

function currentFilter() {
  const conditions = [];
  if (state.zone !== "all") conditions.push(["==", ["get", "BaseZone"], state.zone]);
  if (state.mode === "capacity") {
    conditions.push(["==", ["get", "critical_area_screen_status"], "no_mapped_constraint"]);
  }
  if (!conditions.length) return null;
  return conditions.length === 1 ? conditions[0] : ["all", ...conditions];
}

function currentPointFilter() {
  return state.zone === "all" ? null : ["==", ["get", "BaseZone"], state.zone];
}

function renderLegend() {
  const style = modeStyles[state.mode];
  document.querySelector("#legend").innerHTML = style.legend
    .map(([text, color, size]) => `<div class="legend-row"><span class="swatch${size ? " legend-circle" : ""}" style="background:${color};${size ? `width:${size}px;height:${size}px` : ""}"></span><span>${text}</span></div>`)
    .join("");
  document.querySelector("#legend-note").textContent = style.note;
}

function writeUrl() {
  const url = new URL(location.href);
  url.searchParams.set("mode", state.mode);
  if (state.zone !== "all") url.searchParams.set("zone", state.zone); else url.searchParams.delete("zone");
  if (state.selectedId) url.searchParams.set("parcel", state.selectedId); else url.searchParams.delete("parcel");
  url.searchParams.delete("scenario");
  url.searchParams.delete("prototype");
  history.replaceState(null, "", url);
}

function updateMapStyle() {
  if (!state.fillLayers.length) return;
  const filter = currentFilter();
  for (const layerId of state.fillLayers) {
    if (!map.getLayer(layerId)) continue;
    map.setPaintProperty(layerId, "fill-color", modeStyles[state.mode].paint);
    map.setPaintProperty(layerId, "fill-opacity", modeStyles[state.mode].fillOpacity);
    map.setFilter(layerId, filter);
  }
  for (const layerId of state.lineLayers) {
    if (!map.getLayer(layerId)) continue;
    map.setPaintProperty(layerId, "line-width", ["case", ["boolean", ["feature-state", "selected"], false], 1.7, modeStyles[state.mode].lineWidth]);
    map.setPaintProperty(layerId, "line-opacity", ["case", ["boolean", ["feature-state", "selected"], false], 0.95, modeStyles[state.mode].lineOpacity]);
    map.setFilter(layerId, filter);
  }
  for (const layerId of state.pointLayers) {
    if (!map.getLayer(layerId)) continue;
    map.setLayoutProperty(layerId, "visibility", state.mode === "permits" ? "visible" : "none");
    map.setFilter(layerId, currentPointFilter());
  }
  renderLegend();
  writeUrl();
}

function policyComparison() {
  const zoneKey = state.zone === "all" ? "all" : state.zone;
  return state.summary?.housing_policy_comparison?.by_zone?.[zoneKey];
}

function updatePolicyComparison() {
  const comparison = policyComparison();
  if (!comparison) return;
  const pre = comparison.pre_policy_annual_average;
  const yearOne = comparison.home_in_tacoma_year_one;
  document.querySelector("#policy-geography").textContent = zoneLabel(state.zone);

  const prePeriods = comparison.annual_periods.filter(period => period.period_type === "pre_policy");
  const yearOnePeriod = comparison.annual_periods.find(period => period.period_type === "year_one");
  const periodRow = (period, className = "") => `<tr${className ? ` class="${className}"` : ""}>
    <td class="period-cell">${className === "year-one-row" ? "Year One" : period.start.slice(0, 4)}</td>
    <td data-label="Permit applications">${number(period.permit_records)}</td>
    <td data-label="Estimated projects">${number(period.projects)}</td>
    <td data-label="Proposed units">${number(period.reported_units)}</td>
  </tr>`;
  document.querySelector("#annual-table-body").innerHTML = [
    ...prePeriods.map(period => periodRow(period)),
    `<tr class="average-row"><td class="period-cell">Pre-policy average</td><td data-label="Permit applications">${number(pre.permit_records, 1)}</td><td data-label="Estimated projects">${number(pre.projects, 1)}</td><td data-label="Proposed units">${number(pre.reported_units, 1)}</td></tr>`,
    periodRow(yearOnePeriod, "year-one-row")
  ].join("");

  document.querySelector("#policy-finding").textContent = state.zone === "all"
    ? "Year One applications represented far more proposed homes, while the estimated number of distinct projects remained within the prior five-year range."
    : `In ${zoneLabel(state.zone)}, Year One recorded ${number(yearOne.permit_records)} applications representing ${number(yearOne.projects)} estimated projects and ${number(yearOne.reported_units)} proposed units.`;
  if (!state.selectedId) renderPolicyOverview();
}

function metricPair(values, metric) {
  return `${number(values.pre_policy_annual_average[metric], 1)} → ${number(values.home_in_tacoma_year_one[metric])}`;
}

function renderPolicyOverview() {
  const comparison = policyComparison();
  if (!comparison || state.selectedId) return;
  const typeRows = Object.entries(comparison.by_type)
    .filter(([, values]) => values.pre_policy_annual_average.permit_records || values.home_in_tacoma_year_one.permit_records)
    .sort(([, a], [, b]) => b.home_in_tacoma_year_one.reported_units - a.home_in_tacoma_year_one.reported_units)
    .map(([type, values]) => `<tr>
      <th scope="row">${housingTypeLabel(type)}</th>
      <td>${metricPair(values, "permit_records")}</td>
      <td>${metricPair(values, "projects")}</td>
      <td>${metricPair(values, "reported_units")}</td>
    </tr>`).join("");

  const pre = comparison.pre_policy_annual_average;
  const yearOne = comparison.home_in_tacoma_year_one;
  const unitsPerProjectPre = pre.projects ? pre.reported_units / pre.projects : null;
  const unitsPerProjectYearOne = yearOne.projects ? yearOne.reported_units / yearOne.projects : null;

  document.querySelector("#parcel-title").textContent = "How housing types changed";
  document.querySelector("#parcel-address").textContent = `${zoneLabel(state.zone)} · pre-policy average compared with Year One`;
  document.querySelector("#clear-selection").hidden = true;
  document.querySelector("#parcel-details").className = "parcel-details";
  document.querySelector("#parcel-details").innerHTML = `
    <div class="insight-card">
      <strong>${number(unitsPerProjectPre, 2)} → ${number(unitsPerProjectYearOne, 2)} units per estimated project</strong>
      <p>The clearest change is more proposed homes per project, not an unprecedented number of projects.</p>
    </div>
    <section class="detail-section"><h3>Housing type comparison</h3>
      <div class="comparison-scroll"><table class="evidence-table policy-type-table">
        <caption>Pre-policy annual average → first year after reform · ordered by Year One proposed units</caption>
        <thead><tr><th>Housing type</th><th>Permit applications</th><th>Est. projects</th><th>Proposed units</th></tr></thead>
        <tbody>${typeRows}</tbody>
      </table></div>
    </section>
    <p class="note">Each cell shows pre-policy annual average → Year One. Select a parcel to see its zoning allowance and existing site conditions. If the parcel has housing application activity, it appears in a map popup.</p>`;
}

function setContextMetric(index, labelText, value, note) {
  document.querySelector(`#context-label-${index}`).textContent = labelText;
  document.querySelector(`#context-value-${index}`).textContent = value;
  document.querySelector(`#context-note-${index}`).textContent = note;
}

function updateContextSummary() {
  if (!state.summary || state.mode === "permits") return;
  if (state.mode === "capacity") {
    const capacity = state.summary.capacity_context;
    document.querySelector("#context-title").textContent = "Maximum housing number allowed by zoning";
    document.querySelector("#context-subtitle").textContent = "Parcels with mapped environmental constraints are excluded";
    setContextMetric(1, "Parcels shown", number(capacity.unconstrained_parcel_count), "No mapped environmental constraint");
    setContextMetric(2, "Parcels omitted", number(capacity.excluded_environmental_constraint_count), "Shown in the environmental constraints map");
    setContextMetric(3, "Total homes allowed by standard rules", number(capacity.gross_modeled_units), "Existing homes are not subtracted");
    setContextMetric(4, "Typical allowance per mapped parcel", number(capacity.median_modeled_units_per_candidate, 1), "Median, not a construction forecast");
    document.querySelector("#context-disclaimer").textContent = "This estimate does not account for existing homes, bonus programs, detailed site design, infrastructure, ownership, financing, or market timing.";
  } else {
    const status = state.summary.critical_area_status;
    document.querySelector("#context-title").textContent = "Environmental constraints change what land may be usable";
    document.querySelector("#context-subtitle").textContent = "A first screen using public maps";
    setContextMetric(1, "Parcels touching a mapped environmental area or hazard", number(state.summary.mapped_constraint_intersection_count), `${number(state.summary.mapped_constraint_intersection_count / state.summary.parcel_count * 100, 1)}% of mapped parcels`);
    setContextMetric(2, "Too little land remains outside mapped areas", number(status.constrained_out), "Less than 5,000 sq. ft.");
    setContextMetric(3, "Mapped area or hazard; site review needed", number(status.mapped_constraint_review), "At least 5,000 sq. ft. remains outside it");
    setContextMetric(4, "Parcels with 25–40% slopes", number(status.moderate_slope_review), "Flagged for review, not removed");
    document.querySelector("#context-disclaimer").textContent = "These public maps are a first screen, not a field survey, site approval, or complete inventory of buildable land.";
  }
}

function renderContextOverview() {
  if (state.selectedId) return;
  document.querySelector("#parcel-title").textContent = state.mode === "capacity" ? "How much housing is allowed?" : "Where might site review be needed?";
  document.querySelector("#parcel-address").textContent = state.mode === "capacity"
    ? "Gross allowance across the three Urban Residential districts"
    : "Public environmental maps applied to each parcel";
  const content = state.mode === "capacity"
    ? `<section class="detail-section"><p class="empty-state">The map shows how many homes the base zoning rules allow on parcels without a mapped environmental constraint. It does not subtract homes already there or predict whether construction will occur.</p></section>
       <section class="detail-section"><h3>Why this is supporting context</h3><p class="empty-state">Legal permission is only one condition for development. Ownership, environmental constraints, design, financing, and timing still matter.</p></section>`
    : `<section class="detail-section"><p class="empty-state">The map shows where wetlands, steep slopes, flood hazards, biodiversity areas, or protected-water buffers overlap parcels.</p></section>
       <section class="detail-section"><h3>Why this matters</h3><p class="empty-state">Vacant land is not automatically usable for housing. This screen removes obvious false positives and flags other parcels for closer review.</p></section>`;
  document.querySelector("#parcel-details").className = "parcel-details";
  document.querySelector("#parcel-details").innerHTML = content;
  document.querySelector("#clear-selection").hidden = true;
}

function renderParcel(properties) {
  if (!properties) return;
  state.selectedId = properties.parcel_id;
  document.querySelector("#parcel-title").textContent = properties.parcel_id;
  document.querySelector("#parcel-address").textContent = properties.Site_Address || "Address not published";
  document.querySelector("#clear-selection").hidden = false;
  const constraintTypes = [
    properties.constraint_steep_slope_40pct ? "Slopes over 40%" : null,
    properties.constraint_wetland ? "Wetland" : null,
    properties.constraint_biodiversity ? "Biodiversity area" : null,
    properties.constraint_sfha_flood ? "Special flood hazard area" : null,
    properties.constraint_protected_water_buffer ? "Protected-water buffer" : null
  ].filter(Boolean);
  const flags = [
    properties.meaningful_split_zoned ? "Parcel has more than one zoning district" : null,
    properties.capacity_overlay_review ? "Additional zoning rule needs review" : null,
    properties.zoning_overlap_review ? "Zoning boundary needs review" : null,
    properties.constraint_moderate_slope_review ? "Part of parcel has 25–40% slopes" : null
  ].filter(Boolean);

  const capacitySection = `<section class="detail-section"><h3>Housing allowed by zoning</h3><div class="detail-grid">
    <span>Primary zoning district</span><strong>${zoneLabel(properties.BaseZone)}</strong>
    <span>Lot area</span><strong>${number(properties.parcel_area_sqft)} sq. ft.</strong>
    ${properties.meaningful_split_zoned ? `<span>Districts covering the parcel</span><strong>${zoneCompositionLabel(properties.base_zone_composition)}</strong>` : ""}
    <span>Maximum homes allowed by standard rules</span><strong>${number(properties.modeled_base_capacity_units)}</strong>
  </div><p class="note">This is a gross zoning allowance. Existing homes are not subtracted.</p></section>`;

  const siteSection = `<section class="detail-section"><h3>Existing use and environmental constraints</h3><div class="detail-grid">
    <span>Existing land use</span><strong>${properties.Landuse_Description || "Not available"}</strong>
    <span>Existing site condition</span><strong>${siteConditionLabel(properties.site_condition_class)}</strong>
    <span>Mapped environmental constraints</span><strong>${constraintTypes.length ? constraintTypes.join(" · ") : constraintStatusLabel(properties.critical_area_screen_status)}</strong>
    ${constraintTypes.length ? `<span>Largest area outside mapped constraints</span><strong>${number(properties.largest_unconstrained_area_sqft)} sq. ft.</strong>` : ""}
  </div><p class="note">This screen tests only the listed public environmental maps. Utility easement boundaries were not publicly available.</p></section>`;

  document.querySelector("#parcel-details").className = "parcel-details";
  document.querySelector("#parcel-details").innerHTML =
    [capacitySection, siteSection].join("") +
    (flags.length ? `<p class="warning"><strong>Review flags:</strong> ${flags.join(" · ")}</p>` : "") +
    `<p class="note">Planning-level information only; not a site approval or prediction of development.</p>`;
  writeUrl();
}

function showApplicationPopup(properties, lngLat) {
  state.popup?.remove();
  state.popup = null;
  if (!properties?.housing_application_permit_count) return;
  const latest = properties.housing_application_latest_application
    ? new Date(properties.housing_application_latest_application).toLocaleDateString()
    : "Not available";
  state.popup = new maplibregl.Popup({ closeButton: true, closeOnClick: false, maxWidth: "320px" })
    .setLngLat(lngLat)
    .setHTML(`<div class="application-popup">
      <h3>Housing application activity</h3>
      <p><strong>${counted(properties.housing_application_project_count, "estimated project")}</strong> · <strong>${counted(properties.housing_application_permit_count, "permit application")}</strong></p>
      <p><strong>${counted(properties.housing_application_reported_units, "proposed home")}</strong> · ${housingTypeLabels(properties.housing_application_types)}</p>
      <p>Most recent application: ${latest}</p>
      <p>Applications indicate development interest, not completed housing.</p>
    </div>`)
    .addTo(map);
}

function updateModeUI() {
  const policyMode = state.mode === "permits";
  document.body.classList.toggle("policy-mode", policyMode);
  document.body.classList.toggle("capacity-mode", state.mode === "capacity");
  document.body.classList.toggle("readiness-mode", state.mode === "readiness");
  document.querySelector("#policy-comparison").hidden = !policyMode;
  document.querySelector("#context-summary").hidden = policyMode;
  if (policyMode) updatePolicyComparison(); else updateContextSummary();
  if (state.selectedId && state.details[state.selectedId]) renderParcel(state.details[state.selectedId]);
  else if (policyMode) renderPolicyOverview();
  else renderContextOverview();
}

function initializeFromUrl() {
  const params = new URLSearchParams(location.search);
  if (modeStyles[params.get("mode")]) state.mode = params.get("mode");
  if (["UR1", "UR2", "UR3"].includes(params.get("zone"))) state.zone = params.get("zone");
  state.selectedId = params.get("parcel");
  document.querySelectorAll(".mode-button").forEach(button => {
    const active = button.dataset.mode === state.mode;
    button.classList.toggle("active", active);
    button.setAttribute("aria-checked", String(active));
  });
  document.querySelectorAll(".zone-button").forEach(button => {
    const active = button.dataset.zone === state.zone;
    button.classList.toggle("active", active);
    button.setAttribute("aria-checked", String(active));
  });
}

function addParcelChunk(chunk) {
  const sourceId = `parcels-${chunk.id}`;
  const pointSourceId = `application-points-${chunk.id}`;
  const fillId = `parcels-fill-${chunk.id}`;
  const lineId = `parcels-line-${chunk.id}`;
  const pointId = `application-points-circle-${chunk.id}`;
  map.addSource(sourceId, {
    type: "geojson",
    data: `./public/data/${chunk.file}?v=${encodeURIComponent(state.dataVersion)}`,
    promoteId: "parcel_id"
  });
  map.addSource(pointSourceId, {
    type: "geojson",
    data: `./public/data/${chunk.application_point_file}?v=${encodeURIComponent(state.dataVersion)}`,
    promoteId: "parcel_id"
  });
  const filter = currentFilter();
  const fillLayer = {
    id: fillId,
    type: "fill",
    source: sourceId,
    paint: { "fill-color": modeStyles[state.mode].paint, "fill-opacity": modeStyles[state.mode].fillOpacity }
  };
  const lineLayer = {
    id: lineId,
    type: "line",
    source: sourceId,
    paint: {
      "line-color": ["case", ["boolean", ["feature-state", "selected"], false], "#ffffff", "#48545b"],
      "line-width": ["case", ["boolean", ["feature-state", "selected"], false], 1.7, modeStyles[state.mode].lineWidth],
      "line-opacity": ["case", ["boolean", ["feature-state", "selected"], false], 0.95, modeStyles[state.mode].lineOpacity]
    }
  };
  const pointLayer = {
    id: pointId,
    type: "circle",
    source: pointSourceId,
    layout: { visibility: state.mode === "permits" ? "visible" : "none" },
    paint: {
      "circle-radius": ["step", ["get", "housing_cohort__home_in_tacoma_year_1_reported_units"], 5, 2, 7, 5, 10, 10, 14, 20, 19],
      "circle-color": "#247b83",
      "circle-opacity": 0.85,
      "circle-stroke-color": "#ffffff",
      "circle-stroke-width": 1.4
    }
  };
  const pointFilter = currentPointFilter();
  if (pointFilter) pointLayer.filter = pointFilter;
  if (filter) {
    fillLayer.filter = filter;
    lineLayer.filter = filter;
  }
  map.addLayer(fillLayer);
  map.addLayer(lineLayer);
  map.addLayer(pointLayer);
  state.fillLayers.push(fillId);
  state.lineLayers.push(lineId);
  state.pointLayers.push(pointId);
  const selectParcel = async event => {
    if (event.originalEvent && state.handledMapClicks.has(event.originalEvent)) return;
    if (event.originalEvent) state.handledMapClicks.add(event.originalEvent);
    const feature = event.features?.[0];
    if (!feature) return;
    if (state.selectedFeature) map.setFeatureState(state.selectedFeature, { selected: false });
    state.popup?.remove();
    state.popup = null;
    state.selectedFeature = { source: sourceId, id: feature.id };
    map.setFeatureState(state.selectedFeature, { selected: true });
    const parcelId = feature.properties.parcel_id;
    state.selectedId = parcelId;
    document.querySelector("#parcel-title").textContent = parcelId;
    document.querySelector("#parcel-address").textContent = "Loading parcel details…";
    document.querySelector("#parcel-details").className = "parcel-details empty-state";
    document.querySelector("#parcel-details").textContent = "Loading parcel details…";
    writeUrl();
    try {
      const details = await ensureParcelDetails(chunk.id);
      const parcel = details[parcelId] || feature.properties;
      renderParcel(parcel);
      showApplicationPopup(parcel, event.lngLat);
    } catch (error) {
      document.querySelector("#parcel-details").textContent = `Parcel details unavailable: ${error.message}`;
    }
  };
  map.on("click", fillId, selectParcel);
  map.on("click", pointId, selectParcel);
  map.on("mouseenter", fillId, () => { map.getCanvas().style.cursor = "pointer"; });
  map.on("mouseleave", fillId, () => { map.getCanvas().style.cursor = ""; });
  map.on("mouseenter", pointId, () => { map.getCanvas().style.cursor = "pointer"; });
  map.on("mouseleave", pointId, () => { map.getCanvas().style.cursor = ""; });
}

function reportParcelRendering() {
  const status = document.querySelector("#map-status");
  const rendered = map.queryRenderedFeatures({ layers: state.fillLayers }).length;
  const available = state.fillLayers.reduce((total, layerId) => {
    const sourceId = map.getLayer(layerId)?.source;
    return total + (sourceId ? map.querySourceFeatures(sourceId).length : 0);
  }, 0);
  status.hidden = false;
  if (rendered > 0) {
    status.classList.remove("error");
    status.textContent = `${rendered.toLocaleString()} visible parcels`;
    setTimeout(() => { status.hidden = true; }, 2500);
    return;
  }
  status.classList.add("error");
  status.textContent = available
    ? `${available.toLocaleString()} parcels loaded, but current filters show none`
    : "Parcel boundaries could not be drawn";
}

map.on("load", async () => {
  try {
    initializeFromUrl();
    state.summary = await loadSummary();
    state.dataVersion = state.summary.generated_at;
    state.expectedSources = state.summary.map_chunk_count;
    updatePolicyComparison();
    updateContextSummary();
    updateModeUI();
    document.querySelector("#loading-status").textContent = `Preparing ${state.summary.map_chunk_count} parts of the map…`;
    state.summary.map_chunks.forEach(addParcelChunk);
    state.mapReady = true;
    updateMapStyle();
    document.querySelector("#loading").hidden = true;
    map.once("idle", reportParcelRendering);
    if (state.selectedId) {
      document.querySelector("#parcel-details").textContent = "Loading selected parcel details…";
      ensureSearchIndex()
        .then(index => index.find(item => item.parcel_id === state.selectedId))
        .then(item => item ? ensureParcelDetails(item.chunk) : null)
        .then(details => {
          if (details?.[state.selectedId]) {
            const parcel = details[state.selectedId];
            renderParcel(parcel);
            showApplicationPopup(parcel, [parcel.map_center_lon, parcel.map_center_lat]);
          }
        })
        .catch(error => {
          document.querySelector("#parcel-details").textContent = `Parcel details unavailable: ${error.message}`;
        });
    }
  } catch (error) {
    const loading = document.querySelector("#loading");
    loading.hidden = false;
    loading.innerHTML = `<strong>Parcel data could not be loaded.</strong><span>${error.message}</span>`;
  }
});

map.on("sourcedata", event => {
  if (!event.sourceId?.startsWith("parcels-") || !event.isSourceLoaded) return;
  state.loadedSources.add(event.sourceId);
  const status = document.querySelector("#map-status");
  status.textContent = `Loading map ${state.loadedSources.size} / ${state.expectedSources}`;
  if (state.loadedSources.size === state.expectedSources) {
    status.textContent = "Map data loaded; drawing parcels…";
    map.once("idle", reportParcelRendering);
  }
});

map.on("error", event => {
  if (!event.sourceId?.startsWith("parcels-")) return;
  const status = document.querySelector("#map-status");
  status.hidden = false;
  status.classList.add("error");
  status.textContent = `Map data error: ${event.error?.message || "unknown error"}`;
});

document.querySelectorAll(".mode-button").forEach(button => button.addEventListener("click", () => {
  state.mode = button.dataset.mode;
  document.querySelectorAll(".mode-button").forEach(item => {
    const active = item === button;
    item.classList.toggle("active", active);
    item.setAttribute("aria-checked", String(active));
  });
  updateMapStyle();
  updateModeUI();
}));

document.querySelector(".mode-list").addEventListener("keydown", event => {
  if (!["ArrowDown", "ArrowRight", "ArrowUp", "ArrowLeft"].includes(event.key)) return;
  event.preventDefault();
  const buttons = [...document.querySelectorAll(".mode-button")];
  const current = buttons.indexOf(document.activeElement);
  const direction = ["ArrowDown", "ArrowRight"].includes(event.key) ? 1 : -1;
  const next = buttons[(current + direction + buttons.length) % buttons.length];
  next.focus();
  next.click();
});

document.querySelectorAll(".zone-button").forEach(button => button.addEventListener("click", () => {
  state.zone = button.dataset.zone;
  document.querySelectorAll(".zone-button").forEach(item => {
    const active = item === button;
    item.classList.toggle("active", active);
    item.setAttribute("aria-checked", String(active));
  });
  updateMapStyle();
  updatePolicyComparison();
  updateContextSummary();
  if (!state.selectedId) updateModeUI();
}));

document.querySelector(".zone-buttons").addEventListener("keydown", event => {
  if (!["ArrowDown", "ArrowRight", "ArrowUp", "ArrowLeft"].includes(event.key)) return;
  event.preventDefault();
  const buttons = [...document.querySelectorAll(".zone-button")];
  const current = buttons.indexOf(document.activeElement);
  const direction = ["ArrowDown", "ArrowRight"].includes(event.key) ? 1 : -1;
  const next = buttons[(current + direction + buttons.length) % buttons.length];
  next.focus();
  next.click();
});

async function runSearch() {
  const term = document.querySelector("#parcel-search").value.trim().toLowerCase();
  if (!term) return;
  const button = document.querySelector("#search-button");
  button.disabled = true;
  button.textContent = "Loading…";
  try {
    const index = await ensureSearchIndex();
    const normalized = term.replaceAll(/\D/g, "");
    const matched = index.find(item => item.parcel_id === normalized || String(item.Site_Address || "").toLowerCase().includes(term));
    if (!matched) {
      const status = document.querySelector("#map-status");
      status.hidden = false;
      status.classList.add("error");
      status.textContent = "No matching parcel or address";
      return;
    }
    const details = await ensureParcelDetails(matched.chunk);
    const detail = details[matched.parcel_id];
    map.flyTo({ center: [detail.map_center_lon, detail.map_center_lat], zoom: 16 });
    if (state.selectedFeature) map.setFeatureState(state.selectedFeature, { selected: false });
    state.selectedFeature = { source: `parcels-${matched.chunk}`, id: matched.parcel_id };
    map.setFeatureState(state.selectedFeature, { selected: true });
    renderParcel(detail);
    showApplicationPopup(detail, [detail.map_center_lon, detail.map_center_lat]);
  } catch (error) {
    const status = document.querySelector("#map-status");
    status.hidden = false;
    status.classList.add("error");
    status.textContent = `Search data unavailable: ${error.message}`;
  } finally {
    button.disabled = false;
    button.textContent = "Search";
  }
}

document.querySelector("#search-button").addEventListener("click", runSearch);
document.querySelector("#parcel-search").addEventListener("keydown", event => {
  if (event.key === "Enter") runSearch();
});

[
  ["methodology-button", "methodology-dialog"]
].forEach(([buttonId, dialogId]) => {
  const dialog = document.querySelector(`#${dialogId}`);
  document.querySelector(`#${buttonId}`).addEventListener("click", () => dialog.showModal());
  dialog.querySelector(".dialog-close").addEventListener("click", () => dialog.close());
  dialog.addEventListener("click", event => {
    if (event.target === dialog) dialog.close();
  });
});

document.querySelector("#clear-selection").addEventListener("click", () => {
  if (state.selectedFeature) map.setFeatureState(state.selectedFeature, { selected: false });
  state.selectedFeature = null;
  state.selectedId = null;
  state.popup?.remove();
  state.popup = null;
  writeUrl();
  if (state.mode === "permits") renderPolicyOverview(); else renderContextOverview();
});

renderLegend();

window.addEventListener("unhandledrejection", event => {
  const loading = document.querySelector("#loading");
  loading.hidden = false;
  loading.innerHTML = `<strong>Parcel map failed to initialize.</strong><span>${event.reason?.message || event.reason}</span>`;
});
