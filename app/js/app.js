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
  selectedFeature: null,
  mapReady: false,
  expectedSources: 0,
  loadedSources: new Set(),
  dataVersion: ""
};

const modeStyles = {
  permits: {
    paint: ["interpolate", ["linear"], ["get", "housing_cohort__home_in_tacoma_year_1_project_count"], 0, "#e3e2dd", 1, "#91b7c9", 2, "#397ca7", 3, "#173b5d"],
    legend: [["No Year One project", "#e3e2dd"], ["1 likely project", "#91b7c9"], ["2 likely projects", "#397ca7"], ["3+ likely projects", "#173b5d"]],
    note: "Likely housing projects filed during Home in Tacoma Year One, February 2025–January 2026."
  },
  capacity: {
    paint: ["interpolate", ["linear"], ["get", "modeled_base_capacity_units"], 4, "#d5e4ee", 6, "#8ab4ce", 8, "#397ca7", 16, "#173b5d"],
    legend: [["4 modeled units", "#d5e4ee"], ["6 modeled units", "#8ab4ce"], ["8 modeled units", "#397ca7"], ["16+ modeled units", "#173b5d"]],
    note: "Gross current zoning allowance; existing units are not subtracted."
  },
  readiness: {
    paint: ["match", ["get", "critical_area_screen_status"], "no_mapped_constraint", "#dce8c8", "moderate_slope_review", "#d3a12f", "mapped_constraint_review", "#c8794f", "constrained_out", "#815a68", "#a8a9a4"],
    legend: [["No mapped constraint", "#dce8c8"], ["25–40% slope review", "#d3a12f"], ["Mapped constraint—site review", "#c8794f"], ["Constrained out", "#815a68"]],
    note: "Generalized mapped critical-area screen; site delineation and title review remain necessary."
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
        tiles: ["https://tile.openstreetmap.org/{z}/{x}/{y}.png"],
        tileSize: 256,
        attribution: "© OpenStreetMap contributors"
      }
    },
    layers: [{
      id: "osm",
      type: "raster",
      source: "osm",
      paint: { "raster-saturation": -0.8, "raster-opacity": 0.67, "raster-contrast": -0.1 }
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

function label(value) {
  return String(value ?? "Not available").replaceAll("_", " ");
}

function housingTypeLabel(value) {
  const names = {
    backyard_unit: "Backyard unit / ADU",
    houseplex_2: "Duplex / 2-unit houseplex",
    houseplex_3_6: "3–6 unit houseplex",
    rowhouse: "Rowhouse / townhouse",
    courtyard_cottage: "Courtyard / cottage cluster",
    multiplex_7_20: "7–20 unit multiplex",
    larger_multifamily_21_plus: "Larger multifamily (21+)",
    detached_single_unit: "Detached single-unit",
    other_uncertain_housing: "Housing type uncertain"
  };
  return names[value] || label(value);
}

function housingTypeLabels(value) {
  return value ? value.split("|").map(housingTypeLabel).join(" · ") : "None";
}

function currentFilter() {
  return state.zone === "all" ? null : ["==", ["get", "BaseZone"], state.zone];
}

function renderLegend() {
  const style = modeStyles[state.mode];
  document.querySelector("#legend").innerHTML = style.legend
    .map(([text, color]) => `<div class="legend-row"><span class="swatch" style="background:${color}"></span><span>${text}</span></div>`)
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
    map.setFilter(layerId, filter);
  }
  for (const layerId of state.lineLayers) {
    if (map.getLayer(layerId)) map.setFilter(layerId, filter);
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
  const change = comparison.change_pct;
  document.querySelector("#policy-geography").textContent = `${state.zone === "all" ? "All current UR zones" : state.zone} · active applications`;
  document.querySelector("#metric-pre-applications").textContent = number(pre.permit_records, 1);
  document.querySelector("#metric-year-one-applications").textContent = number(yearOne.permit_records);
  document.querySelector("#metric-application-change").textContent = signedPercent(change.permit_records);
  document.querySelector("#metric-pre-projects").textContent = number(pre.projects, 1);
  document.querySelector("#metric-year-one-projects").textContent = number(yearOne.projects);
  document.querySelector("#metric-project-change").textContent = signedPercent(change.projects);
  document.querySelector("#metric-pre-units").textContent = number(pre.reported_units, 1);
  document.querySelector("#metric-year-one-units").textContent = number(yearOne.reported_units);
  document.querySelector("#metric-unit-change").textContent = signedPercent(change.reported_units);
  const partial = comparison.current_partial;
  const through = partial.through
    ? new Date(`${partial.through}T00:00:00`).toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" })
    : "latest extract";
  document.querySelector("#policy-partial-period").textContent =
    `Current partial: ${number(partial.permit_records)} applications · ${number(partial.projects)} likely projects · ${number(partial.reported_units)} units through ${through}; not annualized`;
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

  const allComparison = state.summary.housing_policy_comparison.by_zone.all;
  const pre = comparison.pre_policy_annual_average;
  const yearOne = comparison.home_in_tacoma_year_one;
  const unitsPerProjectPre = pre.projects ? pre.reported_units / pre.projects : null;
  const unitsPerProjectYearOne = yearOne.projects ? yearOne.reported_units / yearOne.projects : null;
  const duplex = comparison.by_type.houseplex_2;
  const rowhouse = comparison.by_type.rowhouse;
  const detached = comparison.by_type.detached_single_unit;
  const zoneRows = ["UR1", "UR2", "UR3"].map(zone => {
    const values = state.summary.housing_policy_comparison.by_zone[zone];
    const selected = state.zone === zone ? " class=\"selected-row\"" : "";
    return `<tr${selected}><th scope="row">${zone}</th><td>${signedPercent(values.change_pct.permit_records)}</td><td>${signedPercent(values.change_pct.projects)}</td><td>${signedPercent(values.change_pct.reported_units)}</td></tr>`;
  }).join("");

  const insightCards = [
    `<div class="insight-card"><small>Units per likely project</small><strong>${number(unitsPerProjectPre, 2)} → ${number(unitsPerProjectYearOne, 2)}</strong><p>Unit intensity rose faster than project count.</p></div>`,
    duplex ? `<div class="insight-card"><small>Duplex projects</small><strong>${metricPair(duplex, "projects")}</strong><p>${metricPair(duplex, "reported_units")} proposed units.</p></div>` : "",
    rowhouse ? `<div class="insight-card"><small>Rowhouse projects / units</small><strong>${metricPair(rowhouse, "projects")} / ${metricPair(rowhouse, "reported_units")}</strong><p>More units without more likely projects.</p></div>` : "",
    detached ? `<div class="insight-card"><small>Detached applications</small><strong>${metricPair(detached, "permit_records")}</strong><p>The single-unit application count declined.</p></div>` : ""
  ].join("");

  document.querySelector("#panel-eyebrow").textContent = "Policy evidence";
  document.querySelector("#parcel-title").textContent = "What changed";
  document.querySelector("#parcel-address").textContent = `${state.zone === "all" ? "All current UR zones" : state.zone} · pre-policy annual average → Year One`;
  document.querySelector("#parcel-details").className = "parcel-details";
  document.querySelector("#parcel-details").innerHTML = `
    <section class="detail-section"><h3>Immediate takeaways</h3><div class="insight-stack">${insightCards}</div></section>
    <section class="detail-section"><h3>Housing type shift</h3>
      <div class="comparison-scroll"><table class="evidence-table policy-type-table">
        <caption>Pre-policy annual average → Home in Tacoma Year One</caption>
        <thead><tr><th>Housing type</th><th>Applications</th><th>Projects</th><th>Units</th></tr></thead>
        <tbody>${typeRows}</tbody>
      </table></div>
    </section>
    <section class="detail-section"><h3>Different change by current zone</h3>
      <div class="comparison-scroll"><table class="evidence-table">
        <caption>Year One change versus pre-policy annual average</caption>
        <thead><tr><th>Zone</th><th>Applications</th><th>Projects</th><th>Units</th></tr></thead>
        <tbody>${zoneRows}</tbody>
      </table></div>
      <p class="note">UR1 shows the largest application increase; UR2 and UR3 show larger increases in proposed units. Current zoning is applied retrospectively.</p>
    </section>
    <section class="detail-section"><h3>How to read the map</h3>
      <p class="empty-state">Darker parcels have more likely housing projects filed during Home in Tacoma Year One. Select a parcel to inspect its classified application history and site context.</p>
      <p class="note">The map contains existing-use candidate parcels. The headline comparison uses active applications across current UR geography, so map totals need not equal the headline. City benchmark: ${number(state.summary.housing_policy_comparison.official_year_one_benchmark.permit_records)} applications / ${number(state.summary.housing_policy_comparison.official_year_one_benchmark.reported_units)} units.</p>
    </section>`;

  // Keep the all-zone object referenced so unexpected export omissions surface during QA.
  if (!allComparison) throw new Error("All-zone policy comparison is missing.");
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
    document.querySelector("#context-eyebrow").textContent = "Legal context";
    document.querySelector("#context-title").textContent = "Broad permission is not production";
    document.querySelector("#context-subtitle").textContent = "Current UR zoning · gross modeled allowance";
    setContextMetric(1, "UR-zoned inventory", number(state.summary.ur_zoning_count), "Current legal-policy starting point");
    setContextMetric(2, "Existing-use candidates", number(state.summary.parcel_count), `${number(state.summary.parcel_count / state.summary.ur_zoning_count * 100, 1)}% of UR inventory`);
    setContextMetric(3, "Gross modeled units", number(capacity.gross_modeled_units), "Existing units are not subtracted");
    setContextMetric(4, "Median per candidate", number(capacity.median_modeled_units_per_candidate, 1), "Modeled units, not a delivery forecast");
    document.querySelector("#context-disclaimer").textContent = "Gross zoning allowance omits net existing units, bonuses, site design, infrastructure, ownership, financing, and market timing.";
  } else {
    const status = state.summary.critical_area_status;
    document.querySelector("#context-eyebrow").textContent = "Site context";
    document.querySelector("#context-title").textContent = "Mapped constraints remove false positives";
    document.querySelector("#context-subtitle").textContent = "Generalized critical-area screening";
    setContextMetric(1, "Mapped intersections", number(state.summary.mapped_constraint_intersection_count), `${number(state.summary.mapped_constraint_intersection_count / state.summary.parcel_count * 100, 1)}% of candidates`);
    setContextMetric(2, "Constrained out", number(status.constrained_out), "Less than 5,000 sq ft residual");
    setContextMetric(3, "Site review", number(status.mapped_constraint_review), "Residual area remains");
    setContextMetric(4, "25–40% slope review", number(status.moderate_slope_review), "Flagged, not deducted");
    document.querySelector("#context-disclaimer").textContent = "Mapped constraints are screening evidence, not field delineation, entitlement review, or a complete buildable-lands inventory.";
  }
}

function renderContextOverview() {
  if (state.selectedId) return;
  document.querySelector("#panel-eyebrow").textContent = state.mode === "capacity" ? "Legal context" : "Site context";
  document.querySelector("#parcel-title").textContent = state.mode === "capacity" ? "How much is allowed?" : "Where do mapped constraints matter?";
  document.querySelector("#parcel-address").textContent = state.mode === "capacity"
    ? "Gross zoning allowance across current UR parcels"
    : "Critical-area screening before interpreting vacant land";
  const content = state.mode === "capacity"
    ? `<section class="detail-section"><h3>Interpretation</h3><p class="empty-state">The map shows gross units allowed under current UR zoning. It establishes the scale of legal permission, but does not measure net added capacity or forecast development.</p></section>
       <section class="detail-section"><h3>Why it matters</h3><p class="empty-state">The application evidence should not be read as a direct conversion of theoretical capacity. Ownership, site constraints, project economics, and timing intervene between permission and delivery.</p></section>`
    : `<section class="detail-section"><h3>Interpretation</h3><p class="empty-state">The map identifies parcels where generalized critical-area geometry removes or complicates apparently available land.</p></section>
       <section class="detail-section"><h3>Why it matters</h3><p class="empty-state">Vacant does not mean developable. The screen is most useful for removing obvious false positives while retaining review flags where residual land remains.</p></section>`;
  document.querySelector("#parcel-details").className = "parcel-details";
  document.querySelector("#parcel-details").innerHTML = content;
}

function renderParcel(properties) {
  if (!properties) return;
  state.selectedId = properties.parcel_id;
  document.querySelector("#panel-eyebrow").textContent = "Selected parcel";
  document.querySelector("#parcel-title").textContent = properties.parcel_id;
  document.querySelector("#parcel-address").textContent = properties.Site_Address || "Address not published";
  const constraintTypes = [
    properties.constraint_steep_slope_40pct ? ">40% steep slope" : null,
    properties.constraint_wetland ? "wetland" : null,
    properties.constraint_biodiversity ? "biodiversity area" : null,
    properties.constraint_sfha_flood ? "special flood hazard area" : null,
    properties.constraint_protected_water_buffer ? "protected-water buffer" : null
  ].filter(Boolean);
  const flags = [
    properties.meaningful_split_zoned ? "Meaningful split zoning" : null,
    properties.capacity_overlay_review ? "Overlay review" : null,
    properties.zoning_overlap_review ? "Zoning overlap QA" : null,
    properties.constraint_moderate_slope_review ? "25–40% slope review" : null
  ].filter(Boolean);

  const applicationSection = `<section class="detail-section"><h3>Classified housing applications</h3><div class="detail-grid">
    <span>Home in Tacoma Year One projects</span><strong>${number(properties.housing_cohort__home_in_tacoma_year_1_project_count)}</strong>
    <span>Current partial-period projects</span><strong>${number(properties.housing_cohort__home_in_tacoma_current_partial_project_count)}</strong>
    <span>Pre-policy projects (5-year total)</span><strong>${number(properties.housing_cohort__pre_home_in_tacoma_5yr_project_count)}</strong>
    <span>Projects since Feb. 2020</span><strong>${number(properties.housing_application_project_count)}</strong>
    <span>Canonical building permits</span><strong>${number(properties.housing_application_permit_count)}</strong>
    <span>Reported proposed units</span><strong>${number(properties.housing_application_reported_units)}</strong>
    <span>Housing types</span><strong>${housingTypeLabels(properties.housing_application_types)}</strong>
    <span>Latest application</span><strong>${properties.housing_application_latest_application ? new Date(properties.housing_application_latest_application).toLocaleDateString() : "None"}</strong>
  </div><p class="note">Text-classified Residential and Commercial records. Applications indicate development interest, not completed production.</p></section>`;

  const capacitySection = `<section class="detail-section"><h3>Current legal capacity</h3><div class="detail-grid">
    <span>Dominant base zone</span><strong>${properties.BaseZone}</strong>
    <span>Zone composition</span><strong>${properties.base_zone_composition}</strong>
    <span>Gross modeled units</span><strong>${number(properties.modeled_base_capacity_units)}</strong>
    <span>Modeled max floor area</span><strong>${number(properties.modeled_max_floor_area_sqft)} sq ft</strong>
  </div><p class="note">Gross current zoning allowance; existing units are not subtracted.</p></section>`;

  const siteSection = `<section class="detail-section"><h3>Existing use and mapped constraints</h3><div class="detail-grid">
    <span>Lot area</span><strong>${number(properties.parcel_area_sqft)} sq ft</strong>
    <span>Existing land use</span><strong>${properties.Landuse_Description || "Not available"}</strong>
    <span>Site-condition class</span><strong>${label(properties.site_condition_class)}</strong>
    <span>Building coverage</span><strong>${number((properties.building_coverage_ratio || 0) * 100, 1)}%</strong>
    <span>Critical-area screen</span><strong>${label(properties.critical_area_screen_status)}</strong>
    <span>Mapped overlap</span><strong>${number(properties.mapped_constraint_share * 100, 1)}%</strong>
    <span>Largest residual area</span><strong>${number(properties.largest_unconstrained_area_sqft)} sq ft</strong>
    <span>Mapped types</span><strong>${constraintTypes.length ? constraintTypes.join(" · ") : "None mapped"}</strong>
    <span>Utility easements</span><strong>${properties.utility_easement_geometry_available ? "Screened" : "Public geometry unavailable"}</strong>
  </div><p class="note">Generalized City GIS screen only; mapped boundaries do not replace delineation or title review.</p></section>`;

  const orderedSections = state.mode === "permits"
    ? [applicationSection, capacitySection, siteSection]
    : state.mode === "capacity"
      ? [capacitySection, siteSection, applicationSection]
      : [siteSection, capacitySection, applicationSection];
  document.querySelector("#parcel-details").className = "parcel-details";
  document.querySelector("#parcel-details").innerHTML =
    orderedSections.join("") +
    (flags.length ? `<p class="warning"><strong>Review flags:</strong> ${flags.join(" · ")}</p>` : "") +
    `<p class="note">Independent planning-level evidence; not an entitlement determination or redevelopment prediction.</p>`;
  writeUrl();
}

function updateModeUI() {
  const policyMode = state.mode === "permits";
  document.body.classList.toggle("policy-mode", policyMode);
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
  document.querySelector("#zone-filter").value = state.zone;
  document.querySelectorAll(".mode-button").forEach(button => {
    const active = button.dataset.mode === state.mode;
    button.classList.toggle("active", active);
    button.setAttribute("aria-checked", String(active));
  });
}

function addParcelChunk(chunk) {
  const sourceId = `parcels-${chunk.id}`;
  const fillId = `parcels-fill-${chunk.id}`;
  const lineId = `parcels-line-${chunk.id}`;
  map.addSource(sourceId, {
    type: "geojson",
    data: `./public/data/${chunk.file}?v=${encodeURIComponent(state.dataVersion)}`,
    promoteId: "parcel_id"
  });
  const filter = currentFilter();
  const fillLayer = {
    id: fillId,
    type: "fill",
    source: sourceId,
    paint: { "fill-color": modeStyles[state.mode].paint, "fill-opacity": 0.76 }
  };
  const lineLayer = {
    id: lineId,
    type: "line",
    source: sourceId,
    paint: {
      "line-color": ["case", ["boolean", ["feature-state", "selected"], false], "#ffffff", "#344b5d"],
      "line-width": ["case", ["boolean", ["feature-state", "selected"], false], 2.4, 0.35],
      "line-opacity": 0.72
    }
  };
  if (filter) {
    fillLayer.filter = filter;
    lineLayer.filter = filter;
  }
  map.addLayer(fillLayer);
  map.addLayer(lineLayer);
  state.fillLayers.push(fillId);
  state.lineLayers.push(lineId);
  map.on("click", fillId, async event => {
    const feature = event.features?.[0];
    if (!feature) return;
    if (state.selectedFeature) map.setFeatureState(state.selectedFeature, { selected: false });
    state.selectedFeature = { source: sourceId, id: feature.id };
    map.setFeatureState(state.selectedFeature, { selected: true });
    const parcelId = feature.properties.parcel_id;
    state.selectedId = parcelId;
    document.querySelector("#panel-eyebrow").textContent = "Selected parcel";
    document.querySelector("#parcel-title").textContent = parcelId;
    document.querySelector("#parcel-address").textContent = "Loading parcel evidence…";
    document.querySelector("#parcel-details").className = "parcel-details empty-state";
    document.querySelector("#parcel-details").textContent = "Loading the detailed parcel record on demand…";
    writeUrl();
    try {
      const details = await ensureParcelDetails(chunk.id);
      renderParcel(details[parcelId] || feature.properties);
    } catch (error) {
      document.querySelector("#parcel-details").textContent = `Parcel details unavailable: ${error.message}`;
    }
  });
  map.on("mouseenter", fillId, () => { map.getCanvas().style.cursor = "pointer"; });
  map.on("mouseleave", fillId, () => { map.getCanvas().style.cursor = ""; });
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
    : "Parcel geometry did not reach the renderer";
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
    document.querySelector("#loading-status").textContent = `Registering ${state.summary.map_chunk_count} map sections…`;
    state.summary.map_chunks.forEach(addParcelChunk);
    state.mapReady = true;
    updateMapStyle();
    document.querySelector("#loading").hidden = true;
    map.once("idle", reportParcelRendering);
    if (state.selectedId) {
      document.querySelector("#parcel-details").textContent = "Loading selected parcel evidence…";
      ensureSearchIndex()
        .then(index => index.find(item => item.parcel_id === state.selectedId))
        .then(item => item ? ensureParcelDetails(item.chunk) : null)
        .then(details => {
          if (details?.[state.selectedId]) renderParcel(details[state.selectedId]);
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
  status.textContent = `Parcel sections ${state.loadedSources.size} / ${state.expectedSources}`;
  if (state.loadedSources.size === state.expectedSources) {
    status.textContent = "Parcel geometry loaded; drawing map…";
    map.once("idle", reportParcelRendering);
  }
});

map.on("error", event => {
  if (!event.sourceId?.startsWith("parcels-")) return;
  const status = document.querySelector("#map-status");
  status.hidden = false;
  status.classList.add("error");
  status.textContent = `Parcel layer error: ${event.error?.message || "unknown error"}`;
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

document.querySelector("#zone-filter").addEventListener("change", event => {
  state.zone = event.target.value;
  updateMapStyle();
  updatePolicyComparison();
  updateContextSummary();
  if (!state.selectedId) updateModeUI();
});

document.querySelector("#reset-filters").addEventListener("click", () => {
  state.zone = "all";
  document.querySelector("#zone-filter").value = "all";
  updateMapStyle();
  updatePolicyComparison();
  updateContextSummary();
  if (!state.selectedId) updateModeUI();
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
  ["about-button", "about-dialog"],
  ["methodology-button", "methodology-dialog"],
  ["limitations-button", "limitations-dialog"]
].forEach(([buttonId, dialogId]) => {
  const dialog = document.querySelector(`#${dialogId}`);
  document.querySelector(`#${buttonId}`).addEventListener("click", () => dialog.showModal());
  dialog.querySelector(".dialog-close").addEventListener("click", () => dialog.close());
  dialog.addEventListener("click", event => {
    if (event.target === dialog) dialog.close();
  });
});

renderLegend();

window.addEventListener("unhandledrejection", event => {
  const loading = document.querySelector("#loading");
  loading.hidden = false;
  loading.innerHTML = `<strong>Parcel map failed to initialize.</strong><span>${event.reason?.message || event.reason}</span>`;
});
