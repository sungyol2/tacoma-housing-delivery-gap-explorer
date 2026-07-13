const state = { mode: "capacity", scenario: "baseline", prototype: "duplex_for_sale", zone: "all", fitOnly: false, selectedId: null, details: {}, detailPromises: new Map(), searchIndex: null, searchPromise: null, summary: null, fillLayers: [], lineLayers: [], selectedFeature: null, mapReady: false, expectedSources: 0, loadedSources: new Set(), dataVersion: "" };
const prototypeMeta = {
  duplex_for_sale: { label: "Duplex houseplex — for sale", shortLabel: "Duplex sale", tenure: "for_sale", units: 2 },
  duplex_rental: { label: "Duplex houseplex — rental", shortLabel: "Duplex rent", tenure: "rental", units: 2 },
  four_unit_rowhouse_rental: { label: "4-unit rowhouse cluster — rental", shortLabel: "4-unit rowhouse", tenure: "rental", units: 4 }
};
function prototypeField(suffix) { return `${state.prototype}__${suffix}`; }

const modeStyles = {
  capacity: {
    property: "modeled_base_capacity_units",
    paint: ["interpolate", ["linear"], ["get", "modeled_base_capacity_units"], 4, "#d5e4ee", 6, "#8ab4ce", 8, "#397ca7", 16, "#173b5d"],
    legend: [["4 units", "#d5e4ee"], ["6 units", "#8ab4ce"], ["8 units", "#397ca7"], ["16+ units", "#173b5d"]]
  },
  readiness: {
    property: "critical_area_screen_status",
    paint: ["match", ["get", "critical_area_screen_status"], "no_mapped_constraint", "#dce8c8", "moderate_slope_review", "#d3a12f", "mapped_constraint_review", "#c8794f", "constrained_out", "#815a68", "#a8a9a4"],
    legend: [["No mapped constraint", "#dce8c8"], ["Moderate slope review", "#d3a12f"], ["Mapped constraint—site review", "#c8794f"], ["Constrained out (<5,000 sq ft residual)", "#815a68"]]
  },
  feasibility: {
    property: "feasibility_class",
    legend: [["Strong (>=$150k)", "#2b7b78"], ["Moderate ($50k to $150k)", "#72a06a"], ["Marginal (-$50k to $50k)", "#d3a12f"], ["Weak (-$250k to -$50k)", "#c8794f"], ["Very weak (<-$250k)", "#9f4b45"], ["No basic fit", "#a8a9a4"]]
  },
  permits: {
    property: "housing_pipeline_record_count",
    paint: ["interpolate", ["linear"], ["get", "housing_pipeline_record_count"], 0, "#e2e0d9", 1, "#9ebdca", 2, "#4f839f", 4, "#173b5d"],
    legend: [["No 2021–2026 housing application", "#e2e0d9"], ["1 application", "#9ebdca"], ["2–3 applications", "#4f839f"], ["4+ applications", "#173b5d"]]
  }
};

const map = new maplibregl.Map({
  container: "map",
  center: [-122.45, 47.245],
  zoom: 11.2,
  minZoom: 9,
  style: {
    version: 8,
    sources: { osm: { type: "raster", tiles: ["https://tile.openstreetmap.org/{z}/{x}/{y}.png"], tileSize: 256, attribution: "© OpenStreetMap contributors" } },
    layers: [{ id: "osm", type: "raster", source: "osm", paint: { "raster-saturation": -0.8, "raster-opacity": 0.67, "raster-contrast": -0.1 } }]
  }
});
map.addControl(new maplibregl.NavigationControl({ visualizePitch: false }), "bottom-left");

async function loadCompressedJson(compressedPath) {
  if ("DecompressionStream" in window) {
    const response = await fetch(compressedPath);
    if (!response.ok) throw new Error(`Data request failed: ${response.status}`);
    const stream = response.body.pipeThrough(new DecompressionStream("gzip"));
    return JSON.parse(await new Response(stream).text());
  }
  throw new Error("This browser does not support compressed parcel details. Use a current browser version.");
}

function loadParcelDetails(chunkId) {
  const version = encodeURIComponent(state.dataVersion);
  const chunk = String(chunkId).padStart(2, "0");
  return loadCompressedJson(`./public/data/parcel_details_${chunk}.json.gz?v=${version}`);
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

function feasibilityPaint() {
  const field = prototypeField(`${state.scenario}_feasibility_class`);
  return ["case", ["!", ["get", prototypeField("prototype_basic_fit")]], "#a8a9a4", ["match", ["get", field], "strong", "#2b7b78", "moderate", "#72a06a", "marginal", "#d3a12f", "weak", "#c8794f", "very_weak", "#9f4b45", "#a8a9a4"]];
}

function currentFilter() {
  const filters = [];
  if (state.zone !== "all") filters.push(["==", ["get", "BaseZone"], state.zone]);
  if (state.fitOnly) filters.push(["==", ["get", prototypeField("prototype_basic_fit")], true]);
  return filters.length ? ["all", ...filters] : null;
}

function updateMapStyle() {
  if (!state.fillLayers.length) return;
  const style = modeStyles[state.mode];
  state.fillLayers.forEach(layerId => {
    if (!map.getLayer(layerId)) return;
    map.setPaintProperty(layerId, "fill-color", state.mode === "feasibility" ? feasibilityPaint() : style.paint);
    map.setFilter(layerId, currentFilter());
  });
  state.lineLayers.forEach(layerId => { if (map.getLayer(layerId)) map.setFilter(layerId, currentFilter()); });
  renderLegend();
  writeUrl();
}

function renderLegend() {
  document.querySelector("#legend").innerHTML = modeStyles[state.mode].legend.map(([label, color]) => `<div class="legend-row"><span class="swatch" style="background:${color}"></span><span>${label}</span></div>`).join("");
}

function updateFunnel() {
  if (!state.summary) return;
  const prototype = state.summary.prototypes[state.prototype];
  const scenario = prototype.scenario_funnel[state.scenario];
  const scenarioLabel = state.scenario === "favorable" ? "Upside stress test" : "Baseline";
  document.querySelector("#funnel-scenario").textContent = scenarioLabel;
  document.querySelector("#financial-scenario").textContent = scenarioLabel;
  document.querySelector("#metric-promising").textContent = number(scenario.near_or_above_break_even_count);
  document.querySelector("#metric-fit").textContent = number(prototype.basic_fit_count);
  document.querySelector("#share-fit").textContent = `${number(prototype.basic_fit_count / state.summary.parcel_count * 100, 1)}% of candidates`;
  document.querySelector("#share-promising").textContent = `${number(scenario.near_or_above_break_even_count / prototype.basic_fit_count * 100, 1)}% of physical-fit parcels`;
  const proForma = prototype.scenario_pro_forma[state.scenario];
  const rlv = proForma.residual_land_value;
  const count = scenario.near_or_above_break_even_count;
  const explanation = count === 0 && rlv < 0
    ? `0 of ${number(prototype.basic_fit_count)} physical-fit parcels are near break-even. The prototype is already ${money(Math.abs(rlv))} short before the acquisition benchmark.`
    : `${number(count)} of ${number(prototype.basic_fit_count)} physical-fit parcels are within $50,000 of break-even or above. Prototype RLV before acquisition is ${money(rlv)}.`;
  document.querySelector("#scenario-explanation").textContent = explanation;
}

function money(value) { return value == null ? "Not available" : new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 }).format(value); }
function number(value, digits = 0) { return value == null ? "Not available" : new Intl.NumberFormat("en-US", { maximumFractionDigits: digits }).format(value); }
function label(value) { return String(value ?? "Not available").replaceAll("_", " "); }
function parcelAdjustedRlv(values, properties) {
  if (!values) return null;
  const nonLand = values.non_land_cost - values.demolition_allowance + properties.parcel_demolition_allowance;
  const profitRate = values.required_profit / values.non_land_cost;
  return values.gross_revenue - nonLand * (1 + profitRate);
}

function parcelFinancialDiagnostic(values, properties) {
  if (!values) return null;
  const nonLandCost = values.non_land_cost - values.demolition_allowance + properties.parcel_demolition_allowance;
  const profitRate = values.required_profit / values.non_land_cost;
  const requiredProfit = nonLandCost * profitRate;
  const value = values.gross_revenue;
  return {
    value,
    nonLandCost,
    requiredProfit,
    valueCoverage: value / (nonLandCost + requiredProfit),
    preLandGap: value - nonLandCost - requiredProfit
  };
}

function rentalBreakEvenRent(values, properties, units) {
  if (!values?.potential_gross_income || !values?.net_operating_income || !values?.cap_rate) return null;
  const diagnostic = parcelFinancialDiagnostic(values, properties);
  const noiShareOfPotentialRent = values.net_operating_income / values.potential_gross_income;
  const requiredDevelopmentValue = diagnostic.nonLandCost + diagnostic.requiredProfit + properties.acquisition_benchmark;
  return requiredDevelopmentValue * values.cap_rate / noiShareOfPotentialRent / 12 / units;
}

function renderPrototypeComparison(properties, scenario) {
  const rows = Object.entries(prototypeMeta).map(([prototypeId, meta]) => {
    const fit = properties[`${prototypeId}__prototype_basic_fit`];
    const proForma = state.summary?.prototypes?.[prototypeId]?.scenario_pro_forma?.[scenario];
    const diagnostic = parcelFinancialDiagnostic(proForma, properties);
    const margin = properties[`${prototypeId}__${scenario}_feasibility_margin`];
    const classification = properties[`${prototypeId}__${scenario}_feasibility_class`];
    return `<tr class="${prototypeId === state.prototype ? "selected-model" : ""}">
      <th scope="row">${meta.shortLabel}</th>
      <td>${fit ? "Pass" : "No fit"}</td>
      <td>${fit ? money(diagnostic?.value) : "—"}</td>
      <td>${fit ? money(margin) : "—"}</td>
      <td>${fit ? label(classification) : "—"}</td>
    </tr>`;
  }).join("");
  return `<section class="detail-section"><h3>Three-model comparison · ${scenario === "favorable" ? "upside stress test" : "baseline"}</h3>
    <div class="comparison-scroll"><table class="model-comparison"><caption class="visually-hidden">Physical and financial comparison of the three pilot prototypes for this parcel</caption>
      <thead><tr><th>Prototype</th><th>Fit</th><th>Development value</th><th>Margin</th><th>Class</th></tr></thead>
      <tbody>${rows}</tbody>
    </table></div>
    <p class="note">Development value means gross sales for the for-sale duplex and capitalized stabilized value for rental models. Margin deducts non-land cost, target profit, and the parcel acquisition benchmark.</p></section>`;
}

function renderParcel(properties) {
  if (!properties) return;
  state.selectedId = properties.parcel_id;
  document.querySelector("#parcel-title").textContent = properties.parcel_id;
  document.querySelector("#parcel-address").textContent = properties.Site_Address || "Address not published";
  const scenario = state.scenario;
  const margin = properties[prototypeField(`${scenario}_feasibility_margin`)];
  const normalizedMargin = properties[prototypeField(`${scenario}_normalized_margin`)];
  const classification = properties[prototypeField(`${scenario}_feasibility_class`)];
  const proForma = state.summary?.prototypes?.[state.prototype]?.scenario_pro_forma?.[scenario];
  const diagnostic = parcelFinancialDiagnostic(proForma, properties);
  const sensitivity = state.summary?.one_factor_sensitivity;
  const scenarioLabel = scenario === "favorable" ? "Upside stress test" : "Baseline";
  const isRental = prototypeMeta[state.prototype].tenure === "rental";
  const breakEvenRent = isRental ? rentalBreakEvenRent(proForma, properties, prototypeMeta[state.prototype].units) : null;
  const financialSection = properties[prototypeField("prototype_basic_fit")] ? `
    <section class="detail-section"><h3>${scenarioLabel} illustrative pro forma</h3><div class="detail-grid pro-forma">
      ${isRental ? `<span>Potential annual rent</span><strong>${money(proForma?.potential_gross_income)}</strong><span>Current monthly rent / unit</span><strong>${money(proForma?.potential_gross_income / 12 / prototypeMeta[state.prototype].units)}</strong><span>Break-even monthly rent / unit</span><strong>${money(breakEvenRent)}</strong><span>NOI</span><strong>${money(proForma?.net_operating_income)}</strong><span>Cap rate</span><strong>${number(proForma?.cap_rate * 100, 2)}%</strong><span>Stabilized value</span><strong>${money(proForma?.stabilized_value)}</strong>` : `<span>Gross sales revenue</span><strong>${money(proForma?.gross_revenue)}</strong><span>Sales / closing</span><strong>-${money(proForma?.sales_and_closing_cost)}</strong>`}
      <span>Hard construction</span><strong>-${money(proForma?.hard_cost)}</strong>
      <span>Soft costs</span><strong>-${money(proForma?.soft_cost)}</strong>
      <span>Fees</span><strong>-${money(proForma?.fee_allowance)}</strong>
      <span>Financing</span><strong>-${money(proForma?.financing_allowance)}</strong>
      <span>Demolition</span><strong>-${money(properties.parcel_demolition_allowance)}</strong>
      <span>Contingency</span><strong>-${money(proForma?.contingency)}</strong>
      <span>Required profit</span><strong>-${money(properties[prototypeField(`${scenario}_required_profit`)])}</strong>
      <span>Value / cost + target profit</span><strong>${number(diagnostic?.valueCoverage * 100, 1)}%</strong>
      <span class="subtotal">Residual land value</span><strong class="subtotal">${money(properties[prototypeField(`${scenario}_residual_land_value`)])}</strong>
      <span>Acquisition benchmark</span><strong>-${money(properties.acquisition_benchmark)}</strong>
      <span class="result">Feasibility margin</span><strong class="result">${money(margin)}</strong>
      <span>Margin / acquisition benchmark</span><strong>${normalizedMargin == null ? "Not available" : `${number(normalizedMargin * 100, 1)}%`}</strong>
      <span>Classification</span><strong class="status-chip">${label(classification)}</strong>
    </div><p class="driver-note ${diagnostic?.preLandGap < 0 ? "negative" : "positive"}">${diagnostic?.preLandGap < 0 ? `Before paying for land, modeled development value is ${money(Math.abs(diagnostic.preLandGap))} below non-land cost plus target profit.` : `Modeled development value exceeds non-land cost plus target profit by ${money(diagnostic?.preLandGap)} before land.`}</p><p class="note">Benchmark: ${label(properties.acquisition_source)} · confidence: ${label(properties.acquisition_confidence)}</p></section>
    ${scenario === "baseline" && sensitivity && !isRental ? `<section class="detail-section"><h3>Baseline one-factor sensitivity</h3><div class="detail-grid">
      <span>Sales price -5%</span><strong>${money(parcelAdjustedRlv(sensitivity.sales_down_5, properties) - properties.acquisition_benchmark)}</strong>
      <span>Sales price +5%</span><strong>${money(parcelAdjustedRlv(sensitivity.sales_up_5, properties) - properties.acquisition_benchmark)}</strong>
      <span>Hard cost +5%</span><strong>${money(parcelAdjustedRlv(sensitivity.hard_cost_up_5, properties) - properties.acquisition_benchmark)}</strong>
      <span>Hard cost -5%</span><strong>${money(parcelAdjustedRlv(sensitivity.hard_cost_down_5, properties) - properties.acquisition_benchmark)}</strong>
    </div><p class="note">Parcel feasibility margin with all other baseline inputs held constant.</p></section>` : ""}` : `
    <section class="detail-section"><h3>Financial screen</h3><p class="empty-state">Not screened because the selected prototype physical screen did not pass.</p></section>`;
  const constraintTypes = [properties.constraint_steep_slope_40pct ? ">40% steep slope" : null, properties.constraint_wetland ? "wetland" : null, properties.constraint_biodiversity ? "biodiversity area" : null, properties.constraint_sfha_flood ? "special flood hazard area" : null, properties.constraint_protected_water_buffer ? "protected-water buffer" : null].filter(Boolean);
  const flags = [properties.meaningful_split_zoned ? "Meaningful split zoning" : null, properties.capacity_overlay_review ? "Overlay review" : null, properties.zoning_overlap_review ? "Zoning overlap QA" : null, properties.constraint_moderate_slope_review ? "25–40% slope review" : null].filter(Boolean);
  document.querySelector("#parcel-details").className = "parcel-details";
  document.querySelector("#parcel-details").innerHTML = `
    <section class="detail-section"><h3>Site and zoning</h3><div class="detail-grid">
      <span>Dominant base zone</span><strong>${properties.BaseZone}</strong><span>Zone composition</span><strong>${properties.base_zone_composition}</strong>
      <span>Lot area</span><strong>${number(properties.parcel_area_sqft)} sq ft</strong><span>Existing land use</span><strong>${properties.Landuse_Description || "Not available"}</strong>
      <span>Building coverage</span><strong>${number((properties.building_coverage_ratio || 0) * 100, 1)}%</strong><span>Improvement value share</span><strong>${number((properties.improvement_value_ratio || 0) * 100, 1)}%</strong>
      <span>Site-condition class</span><strong>${label(properties.site_condition_class)}</strong>
    </div></section>
    <section class="detail-section"><h3>Mapped development constraints</h3><div class="detail-grid">
      <span>Critical-area screen</span><strong>${label(properties.critical_area_screen_status)}</strong>
      <span>Mapped overlap</span><strong>${number(properties.mapped_constraint_share * 100, 1)}%</strong>
      <span>Largest residual area</span><strong>${number(properties.largest_unconstrained_area_sqft)} sq ft</strong>
      <span>Mapped types</span><strong>${constraintTypes.length ? constraintTypes.join(" · ") : "None mapped"}</strong>
      <span>Utility easements</span><strong>${properties.utility_easement_geometry_available ? "Screened" : "Not available in public parcel geometry"}</strong>
    </div><p class="note">Generalized City GIS screen only; mapped boundaries and buffers do not replace site delineation or title review.</p></section>
    <section class="detail-section"><h3>Baseline capacity</h3><div class="detail-grid">
      <span>Modeled units</span><strong>${number(properties.modeled_base_capacity_units)}</strong><span>Max floor area</span><strong>${number(properties.modeled_max_floor_area_sqft)} sq ft</strong>
      <span>Selected prototype</span><strong>${prototypeMeta[state.prototype].label}</strong><span>Prototype screen</span><strong>${label(properties[prototypeField("prototype_fit_status")])}</strong>
    </div></section>
    ${renderPrototypeComparison(properties, scenario)}
    ${financialSection}
    <section class="detail-section"><h3>Housing applications (2021–2026)</h3><div class="detail-grid"><span>New-building / unit-adding</span><strong>${number(properties.housing_pipeline_record_count)}</strong><span>With issue date</span><strong>${number(properties.housing_pipeline_issued_count)}</strong><span>Reported positive units</span><strong>${number(properties.housing_pipeline_reported_units)}</strong><span>Latest application</span><strong>${properties.housing_pipeline_latest_application ? new Date(properties.housing_pipeline_latest_application).toLocaleDateString() : "None"}</strong></div></section>
    ${flags.length ? `<p class="warning"><strong>Review flags:</strong> ${flags.join(" · ")}</p>` : ""}
    <p class="note">Financial values are illustrative pending market validation. Passing the basic fit screen is not an entitlement or site design conclusion.</p>`;
  writeUrl();
}

function writeUrl() {
  const url = new URL(location.href);
  url.searchParams.set("mode", state.mode);
  url.searchParams.set("scenario", state.scenario);
  url.searchParams.set("prototype", state.prototype);
  if (state.zone !== "all") url.searchParams.set("zone", state.zone); else url.searchParams.delete("zone");
  if (state.selectedId) url.searchParams.set("parcel", state.selectedId); else url.searchParams.delete("parcel");
  history.replaceState(null, "", url);
}

function initializeFromUrl() {
  const params = new URLSearchParams(location.search);
  if (modeStyles[params.get("mode")]) state.mode = params.get("mode");
  if (["baseline", "favorable"].includes(params.get("scenario"))) state.scenario = params.get("scenario");
  if (prototypeMeta[params.get("prototype")]) state.prototype = params.get("prototype");
  if (["UR1", "UR2", "UR3"].includes(params.get("zone"))) state.zone = params.get("zone");
  state.selectedId = params.get("parcel");
  document.querySelector("#scenario-filter").value = state.scenario;
  document.querySelector("#prototype-filter").value = state.prototype;
  document.querySelector("#zone-filter").value = state.zone;
  document.querySelectorAll(".mode-button").forEach(button => { const active = button.dataset.mode === state.mode; button.classList.toggle("active", active); button.setAttribute("aria-checked", String(active)); });
}

map.on("load", async () => {
  try {
    initializeFromUrl();
    const summary = await loadSummary();
    state.summary = summary;
    state.dataVersion = summary.generated_at;
    document.querySelector("#metric-zoned").textContent = number(summary.ur_zoning_count);
    document.querySelector("#metric-parcels").textContent = number(summary.parcel_count);
    document.querySelector("#metric-constraint-pass").textContent = number(summary.mapped_constraint_pass_count);
    document.querySelector("#metric-fit").textContent = number(summary.basic_fit_count);
    document.querySelector("#share-candidates").textContent = `${number(summary.parcel_count / summary.ur_zoning_count * 100, 1)}% of inventory`;
    document.querySelector("#share-constraint-pass").textContent = `${number(summary.mapped_constraint_pass_count / summary.parcel_count * 100, 1)}% retain ≥5,000 sq ft`;
    document.querySelector("#share-fit").textContent = `${number(summary.basic_fit_count / summary.parcel_count * 100, 1)}% of candidates`;
    updateFunnel();
    state.expectedSources = summary.map_chunk_count;
    document.querySelector("#loading-status").textContent = `Registering ${summary.map_chunk_count} map sections…`;
    summary.map_chunks.forEach(chunk => addParcelChunk(chunk));
    state.mapReady = true;
    updateMapStyle();
    document.querySelector("#loading").hidden = true;
    map.once("idle", reportParcelRendering);
    if (state.selectedId) {
      document.querySelector("#parcel-details").textContent = "Loading selected parcel evidence…";
      ensureSearchIndex()
        .then(index => index.find(item => item.parcel_id === state.selectedId))
        .then(item => item ? ensureParcelDetails(item.chunk) : null)
        .then(details => { if (details?.[state.selectedId]) renderParcel(details[state.selectedId]); })
        .catch(error => { document.querySelector("#parcel-details").textContent = `Parcel details unavailable: ${error.message}`; });
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

map.on("error", event => {
  if (!event.sourceId?.startsWith("parcels-")) return;
  const status = document.querySelector("#map-status");
  status.hidden = false;
  status.classList.add("error");
  status.textContent = `Parcel layer error: ${event.error?.message || "unknown error"}`;
});

function addParcelChunk(chunk) {
  const sourceId = `parcels-${chunk.id}`;
  const fillId = `parcels-fill-${chunk.id}`;
  const lineId = `parcels-line-${chunk.id}`;
  map.addSource(sourceId, { type: "geojson", data: `./public/data/${chunk.file}?v=${encodeURIComponent(state.dataVersion)}`, promoteId: "parcel_id" });
  const filter = currentFilter();
  const fillLayer = { id: fillId, type: "fill", source: sourceId, paint: { "fill-color": state.mode === "feasibility" ? feasibilityPaint() : modeStyles[state.mode].paint, "fill-opacity": .76 } };
  const lineLayer = { id: lineId, type: "line", source: sourceId, paint: { "line-color": ["case", ["boolean", ["feature-state", "selected"], false], "#ffffff", "#344b5d"], "line-width": ["case", ["boolean", ["feature-state", "selected"], false], 2.4, .35], "line-opacity": .72 } };
  if (filter) { fillLayer.filter = filter; lineLayer.filter = filter; }
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

document.querySelectorAll(".mode-button").forEach(button => button.addEventListener("click", () => {
  state.mode = button.dataset.mode;
  document.querySelectorAll(".mode-button").forEach(item => { const active = item === button; item.classList.toggle("active", active); item.setAttribute("aria-checked", String(active)); });
  updateMapStyle();
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
document.querySelector("#scenario-filter").addEventListener("change", event => {
  state.scenario = event.target.value;
  updateMapStyle();
  updateFunnel();
  if (state.selectedId && state.details?.[state.selectedId]) renderParcel(state.details[state.selectedId]);
});
document.querySelector("#prototype-filter").addEventListener("change", event => {
  state.prototype = event.target.value;
  updateMapStyle();
  updateFunnel();
  if (state.selectedId && state.details?.[state.selectedId]) renderParcel(state.details[state.selectedId]);
});
document.querySelector("#zone-filter").addEventListener("change", event => { state.zone = event.target.value; updateMapStyle(); });
document.querySelector("#fit-filter").addEventListener("change", event => { state.fitOnly = event.target.checked; updateMapStyle(); });
document.querySelector("#reset-filters").addEventListener("click", () => { state.zone = "all"; state.fitOnly = false; document.querySelector("#zone-filter").value = "all"; document.querySelector("#fit-filter").checked = false; updateMapStyle(); });

async function runSearch() {
  const term = document.querySelector("#parcel-search").value.trim().toLowerCase();
  if (!term) return;
  const searchButton = document.querySelector("#search-button");
  searchButton.disabled = true;
  searchButton.textContent = "Loading…";
  let details;
  try {
    details = await ensureSearchIndex();
  } catch (error) {
    document.querySelector("#map-status").hidden = false;
    document.querySelector("#map-status").classList.add("error");
    document.querySelector("#map-status").textContent = `Search data unavailable: ${error.message}`;
    searchButton.disabled = false;
    searchButton.textContent = "Search";
    return;
  }
  const normalized = term.replaceAll(/\D/g, "");
  const matched = details.find(item => item.parcel_id === normalized || String(item.Site_Address || "").toLowerCase().includes(term));
  searchButton.disabled = false;
  searchButton.textContent = "Search";
  if (!matched) {
    document.querySelector("#map-status").hidden = false;
    document.querySelector("#map-status").classList.add("error");
    document.querySelector("#map-status").textContent = "No matching parcel or address";
    return;
  }
  let detail;
  try {
    const chunkDetails = await ensureParcelDetails(matched.chunk);
    detail = chunkDetails[matched.parcel_id];
  } catch (error) {
    document.querySelector("#map-status").hidden = false;
    document.querySelector("#map-status").classList.add("error");
    document.querySelector("#map-status").textContent = `Parcel details unavailable: ${error.message}`;
    return;
  }
  map.flyTo({ center: [detail.map_center_lon, detail.map_center_lat], zoom: 16 });
  renderParcel(detail);
}
document.querySelector("#search-button").addEventListener("click", runSearch);
document.querySelector("#parcel-search").addEventListener("keydown", event => { if (event.key === "Enter") runSearch(); });
[
  ["about-button", "about-dialog"],
  ["methodology-button", "methodology-dialog"],
  ["limitations-button", "limitations-dialog"]
].forEach(([buttonId, dialogId]) => {
  const dialog = document.querySelector(`#${dialogId}`);
  document.querySelector(`#${buttonId}`).addEventListener("click", () => dialog.showModal());
  dialog.querySelector(".dialog-close").addEventListener("click", () => dialog.close());
  dialog.addEventListener("click", event => { if (event.target === dialog) dialog.close(); });
});
renderLegend();

window.addEventListener("unhandledrejection", event => {
  const loading = document.querySelector("#loading");
  loading.hidden = false;
  loading.innerHTML = `<strong>Parcel map failed to initialize.</strong><span>${event.reason?.message || event.reason}</span>`;
});
