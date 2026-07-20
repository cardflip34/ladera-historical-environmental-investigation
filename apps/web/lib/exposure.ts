// Non-causal EXPOSURE SCREENING score. This is a prioritization heuristic for locations x
// chemicals x time periods — NOT a dose, NOT proof of contact, NEVER applied to individuals.
// Every factor is explicit and configurable. See METHODOLOGY.md section 5.

export type Factors = {
  applicationEvidence: number;  // documented=1 ... unverified allegation ~0.2
  applicationIntensity: number; // frequency/amount proxy
  proximity: number;            // spatial overlap with population
  temporalRelevance: number;    // overlap with etiologically plausible window
  environmentalFate: number;    // persistence/mobility (higher = more available over time)
  siteUse: number;              // child-presence intensity at the site
  sourceConfidence: number;     // grade-derived
  // Added 2026-07-18. Everything above scores EXPOSURE OPPORTUNITY. None of it asks whether
  // the hazard plausibly causes THIS disease. Without this term the model will happily rank a
  // well-documented hazard highly even when its established cancer profile has nothing to do
  // with Ewing sarcoma. Scored against the disease actually under investigation.
  diseaseSpecificPlausibility: number;
};

export type ScreenRow = {
  id: string;
  location: string;
  chemicalOrHazard: string;
  period: string;
  factors: Factors;
  rationale: string;
};

export function score(f: Factors): number {
  return f.applicationEvidence * f.applicationIntensity * f.proximity *
    f.temporalRelevance * f.environmentalFate * f.siteUse * f.sourceConfidence *
    f.diseaseSpecificPlausibility;
}

/** Exposure opportunity alone, ignoring whether the hazard fits the disease. Shown alongside
 *  the full score so the two questions stay visibly separate. */
export function exposureOnlyScore(f: Factors): number {
  return f.applicationEvidence * f.applicationIntensity * f.proximity *
    f.temporalRelevance * f.environmentalFate * f.siteUse * f.sourceConfidence;
}

// Illustrative rows built ONLY from what the platform actually documents. Values are
// transparent judgments, shown so they can be challenged — not hidden model internals.
export const SCREEN_ROWS: ScreenRow[] = [
  {
    id: "SCR-01",
    location: "LARMAC common areas (parks, slopes, medians)",
    chemicalOrHazard: "Glufosinate ('Lifeline')",
    period: "2023–2025 (documented)",
    factors: { applicationEvidence: 0.9, applicationIntensity: 0.6, proximity: 0.8, temporalRelevance: 0.5, environmentalFate: 0.3, siteUse: 0.8, sourceConfidence: 0.75, diseaseSpecificPlausibility: 0.1 },
    rationale: "Documented common-area application; children present; but glufosinate is non-persistent (~7.4 d soil) and no Ewing link established. Temporal relevance capped: 2023-25 may post-date the etiologic window for cases dx'd 2013-2024. Disease-specificity: glufosinate is not classified a carcinogen by any regulator and has NO established link to Ewing sarcoma or any sarcoma — the lowest plausibility term in the model.",
  },
  {
    id: "SCR-02",
    location: "Residential footprint, yards, parks (former citrus/orchard/grain land)",
    chemicalOrHazard: "Legacy soil residue — standing condition (arsenic, DDT/DDE, toxaphene)",
    period: "Ongoing — does not decay",
    factors: { applicationEvidence: 0.35, applicationIntensity: 0.5, proximity: 0.9, temporalRelevance: 0.85, environmentalFate: 0.95, siteUse: 0.9, sourceConfidence: 0.4, diseaseSpecificPlausibility: 0.15 },
    rationale: "Arsenic is an element and never degrades; organochlorines persist for decades — demonstrated locally, since DTSC found DDT/toxaphene/arsenic at former-farm school sites ~3 mi away long after cultivation ceased. Because this is a standing condition rather than an event, it applies to EVERY birth cohort and is unaffected by how long ago grading occurred. REVISED DOWN 2026-07-18: SoCal background arsenic runs to ~12 mg/kg, 18-110x above risk-based screening levels, so exceeding a screening level here is normal; measured bioavailability at the closest analogue (Barber Orchard) is ~0.31, not 1.0; lead arsenate was an apple/pear insecticide whereas this was citrus/barley/cattle land; mass grading likely diluted the plough layer; and biomarker studies at comparable concentrations found no correlation with children's urinary arsenic. Still the cheapest decisive test, but no longer the leading explanation. Disease-specificity: arsenic's established cancers are skin, lung and bladder — not bone or sarcoma — and organochlorines have no established Ewing link. Parental-farming proxy studies are the closest signal and are weak. So a real exposure pathway here would still not specifically explain Ewing sarcoma.",
  },
  {
    id: "SCR-06",
    location: "Residential footprint during mass grading",
    chemicalOrHazard: "Construction-era dust mobilising legacy residue (time-limited)",
    period: "1999–2006 only",
    factors: { applicationEvidence: 0.5, applicationIntensity: 0.6, proximity: 0.9, temporalRelevance: 0.25, environmentalFate: 0.9, siteUse: 0.9, sourceConfidence: 0.5, diseaseSpecificPlausibility: 0.2 },
    rationale: "A one-time event, not a standing condition. Only children born on or before ~2007 could have been present (incl. in utero). By diagnosis-year 2026 just ~7% of plausible pediatric ages still overlap the grading window, so this mechanism is substantially weakened for recent diagnoses and unavailable for children born after ~2007. Scored separately from SCR-02 precisely so the two are not conflated. Disease-specificity: same hazards as SCR-02, so the same weak fit to Ewing sarcoma.",
  },
  {
    id: "SCR-03",
    location: "Community area (within ~5 km)",
    chemicalOrHazard: "Abandoned/plugged oil & gas wells",
    period: "Chronic (legacy)",
    factors: { applicationEvidence: 0.8, applicationIntensity: 0.3, proximity: 0.6, temporalRelevance: 0.6, environmentalFate: 0.5, siteUse: 0.5, sourceConfidence: 0.8, diseaseSpecificPlausibility: 0.5 },
    rationale: "Well locations documented (CalGEM); the one environmental factor with even a suggestive published Ewing association — but only for abandoned wells and only in Hispanic children; these are low-leakage plugged dry holes. Disease-specificity: the ONLY candidate with a published, Ewing-sarcoma-specific association (Clark 2026, abandoned wells within 10 km, OR 1.27, 95% CI 0.96-1.66) — suggestive and non-significant, but disease-matched, which nothing else here is.",
  },
  {
    id: "SCR-04",
    location: "Common areas & schools (irrigated)",
    chemicalOrHazard: "Recycled irrigation water (constituents unknown)",
    period: "Ongoing",
    factors: { applicationEvidence: 0.7, applicationIntensity: 0.5, proximity: 0.8, temporalRelevance: 0.6, environmentalFate: 0.5, siteUse: 0.8, sourceConfidence: 0.4, diseaseSpecificPlausibility: 0.15 },
    rationale: "Extensive tertiary recycled-water irrigation is documented, but constituent-level quality data is not public — source confidence low. A pathway to characterize, not a known hazard. Disease-specificity: constituents unknown, so no disease-specific case can be made either way.",
  },
  {
    id: "SCR-05",
    location: "Individual residences",
    chemicalOrHazard: "Homeowner/consumer pesticide self-use",
    period: "Ongoing",
    factors: { applicationEvidence: 0.2, applicationIntensity: 0.4, proximity: 0.7, temporalRelevance: 0.6, environmentalFate: 0.4, siteUse: 0.7, sourceConfidence: 0.2, diseaseSpecificPlausibility: 0.1 },
    rationale: "Entirely exempt from PUR — invisible in public data. Low evidence/confidence, but a structural blind spot worth flagging rather than ignoring. Disease-specificity: same consumer pesticide classes as SCR-01; no Ewing link established.",
  },
];
