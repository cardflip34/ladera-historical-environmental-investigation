// Hypothetical Standardized Incidence Ratio (SIR) scenario analysis for Ewing sarcoma.
// EVERY output here is HYPOTHETICAL — based on unverified public case reports and estimated
// population. Nothing here is a finding or a confirmed cluster. See METHODOLOGY.md.

// Exact (Garwood) Poisson 95% confidence limits for the mean, given an observed count.
// Precomputed standard values for small counts (the only regime relevant to a rare cancer).
const POISSON_95: Record<number, [number, number]> = {
  0: [0.0, 3.6889],
  1: [0.0253, 5.5716],
  2: [0.2422, 7.2247],
  3: [0.6187, 8.7673],
  4: [1.0899, 10.2416],
  5: [1.6235, 11.6683],
  6: [2.2019, 13.0595],
  7: [2.8144, 14.4227],
  8: [3.4538, 15.7632],
  9: [4.1154, 17.0848],
  10: [4.7954, 18.3904],
  11: [5.4912, 19.6820],
  12: [6.2006, 20.9616],
};

export function poissonCI(observed: number): [number, number] {
  return POISSON_95[observed] ?? [observed - 1.96 * Math.sqrt(observed), observed + 1.96 * Math.sqrt(observed)];
}

export type Scenario = {
  label: string;
  observed: number;
  personYears: number; // ages at risk, over the window
  ratePerMillion: number; // per person-year
  note: string;
};

export type ScenarioResult = Scenario & {
  expected: number;
  sir: number;
  sirLow: number;
  sirHigh: number;
  excludesOne: boolean; // does the 95% CI exclude SIR = 1?
};

export function computeScenario(s: Scenario): ScenarioResult {
  const expected = s.personYears * (s.ratePerMillion / 1_000_000);
  const [lo, hi] = poissonCI(s.observed);
  const sir = expected > 0 ? s.observed / expected : 0;
  const sirLow = expected > 0 ? lo / expected : 0;
  const sirHigh = expected > 0 ? hi / expected : 0;
  return { ...s, expected, sir, sirLow, sirHigh, excludesOne: sirLow > 1 || sirHigh < 1 };
}

// Base inputs (verified) — see research/demographics/. Person-years for ages 0-19 over
// 2013-2026 (~14 yr) estimated from ACS child population (~9,000) held roughly constant.
export const BASE = {
  childPop0to19: 9115,
  childPop10to19: 4906,
  years: 14,
  windowLabel: "2013–2026 (~14 yr)",
  personYears0to19: 9115 * 14, // ~127,610
  personYears10to19: 4906 * 14, // ~68,684
  rateAllRaces: 3.0, // per million/yr, ages 0-19 (SEER central)
  rateWhiteAdj: 4.0, // ancestry-adjusted upper for a NH-white-majority community
  ratePeak10to19: 4.58, // per million/yr, ages 10-19 North America
};

export function defaultScenarios(): Scenario[] {
  const py = BASE.personYears0to19;
  const pyPeak = BASE.personYears10to19;
  return [
    { label: "S1 — central", observed: 6, personYears: py, ratePerMillion: BASE.rateAllRaces,
      note: "6 Ewing cases (NBC), ages 0-19 person-years, all-races SEER rate 3.0/M" },
    { label: "S2 — ancestry-adjusted", observed: 6, personYears: py, ratePerMillion: BASE.rateWhiteAdj,
      note: "Same, but rate raised to 4.0/M for a non-Hispanic-white-majority community" },
    { label: "S3 — peak-age denominator", observed: 6, personYears: pyPeak, ratePerMillion: BASE.ratePeak10to19,
      note: "Ages 10-19 only, peak-age rate 4.58/M (narrower, higher-rate window)" },
    { label: "S4 — conservative count", observed: 4, personYears: py, ratePerMillion: BASE.rateWhiteAdj,
      note: "Only 4 cases counted (case-definition sensitivity), ancestry-adjusted rate" },
    { label: "S5 — higher count", observed: 12, personYears: py, ratePerMillion: BASE.rateAllRaces,
      note: "12 (single-source outlier count), all-races rate — shows count sensitivity" },
    { label: "S6 — leave-one-out", observed: 5, personYears: py, ratePerMillion: BASE.rateWhiteAdj,
      note: "One reported case removed (e.g., non-resident during window), ancestry-adjusted" },
  ];
}
