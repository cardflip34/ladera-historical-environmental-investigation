import { readCsv, readJson, readText } from "./csv";

export type Row = Record<string, string>;

export const getSources = () => readCsv("research/source_registry/sources.csv");
export const getHealthEvents = () => readCsv("research/cancer_reports/public_report_registry.csv");
export const getLiterature = () => readCsv("research/literature/literature_registry.csv");
export const getEvidenceMatrix = () => readCsv("research/literature/evidence_matrix.csv");
export const getChemicals = () => readCsv("research/pesticides/active_ingredients.csv");
export const getPesticideProducts = () => readCsv("research/pesticides/products.csv");
export const getApplicationEvents = () => readCsv("research/pesticides/application_events.csv");
export const getSites = () => readCsv("research/schools/sites.csv");
export const getEnvironmentalSites = () => readCsv("research/environmental_sites/sites.csv");
export const getWaterSystems = () => readCsv("research/water/water_systems.csv");
export const getWaterQuality = () => readCsv("research/water/water_quality.csv");
export const getDemographics = () => readCsv("research/demographics/population_estimates.csv");
export const getIncidenceRates = () => readCsv("research/demographics/incidence_rates.csv");
export const getLandUse = () => readCsv("research/land_use/historical_land_use.csv");

export const getTimeline = () =>
  readJson<Record<string, unknown>>("research/cancer_reports/timeline.json", {});

export const getProjectState = () =>
  readJson<Record<string, unknown>>("project_state.json", {});

export function getDoc(relPath: string): string {
  return readText(relPath);
}

/** Counts used across the dashboard. */
export function getCounts() {
  return {
    sources: getSources().length,
    healthEvents: getHealthEvents().length,
    literature: getLiterature().length,
    chemicals: getChemicals().length,
    products: getPesticideProducts().length,
    applications: getApplicationEvents().length,
    sites: getSites().length,
    environmentalSites: getEnvironmentalSites().length,
    waterQuality: getWaterQuality().length,
    demographics: getDemographics().length,
    landUse: getLandUse().length,
  };
}

export function gradeCounts() {
  const counts: Record<string, number> = {};
  for (const s of getSources()) {
    const g = (s.reliabilityGrade || "?").toUpperCase();
    counts[g] = (counts[g] || 0) + 1;
  }
  return counts;
}
