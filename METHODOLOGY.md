# METHODOLOGY.md

Analytical methods, their assumptions, and their limitations. Nothing here produces a
causal conclusion; these are descriptive and screening methods.

## 1. Expected-case estimation (Standardized Incidence Ratio, SIR)

**SIR = Observed / Expected.**

Expected cases are computed by applying age-, sex-, and (critically) race/ethnicity-specific
baseline incidence rates to the community's person-years:

```
Expected = Σ_strata ( baseline_rate[stratum] × person_years[stratum] )
SIR       = Observed / Expected
```

- **Baseline rates:** SEER / California Cancer Registry, stratified. For Ewing sarcoma the
  race/ethnicity stratification is essential — incidence in people of European ancestry is
  several-fold higher than in Black or Asian populations. Using an all-races national rate
  in a predominantly non-Hispanic-white community would understate the expected count and
  bias SIR upward.
- **Person-years:** built from annual population estimates × years at risk, by stratum, with
  explicit uncertainty for growth and turnover.

## 2. Poisson confidence intervals

Case counts are treated as Poisson. Exact (Garwood) 95% CIs for the observed count O:

```
lower = 0.5 * qchisq(0.025, 2*O) ;  upper = 0.5 * qchisq(0.975, 2*(O+1))
CI(SIR) = [ lower/Expected , upper/Expected ]
```

For small O the interval is wide and often includes 1.0 — this must be shown, not hidden.

## 3. Scenario & sensitivity analysis

Because Observed and Expected are both uncertain, the platform never reports a single SIR.
It reports a **grid** of scenarios varying:

- Observed count (e.g., 4 / 6 / 8 / 12, reflecting source discrepancies and case-definition
  choices),
- Time window (2013–2026, 2005–2026, other),
- Population denominator (±20%, different age/ancestry assumptions),
- Study boundary (Zone A only vs Zone A+adjacent).

Plus **leave-one-case-out** and **multiple-case-definition** analyses. Every cell is labeled
**HYPOTHETICAL — based on unverified public reports and estimated population.**

## 4. Spatial methods (screening only)

Where documented point/area data exist (application areas, sites, water features), the
platform supports proximity buffers and simple overlap counts. Formal spatial scan
statistics (e.g., Kulldorff / SaTScan) are described as the appropriate *authorized* method
but are **not** run on patient locations (which the platform does not hold). Any spatial
display is of locations and time periods, never of patients.

## 5. Exposure-screening score (non-causal prioritization)

```
score = application_evidence_weight
      × application_intensity_weight
      × proximity_weight
      × temporal_relevance_weight
      × environmental_fate_weight
      × site_use_weight
      × source_confidence_weight
```

Each weight ∈ [0,1], all visible and user-configurable. Multiple model versions, with
sensitivity analysis over weightings. **Never** a dose or proof of contact; **never** scored
for individual children — only for locations × chemicals × time periods.

## 6. Bias register (explicitly tracked)

- **Ecological fallacy** — area-level associations do not imply individual-level effects.
- **Multiple comparisons / Texas sharpshooter** — a boundary drawn around observed cases
  inflates apparent rate; comparison zones and pre-specified boundaries mitigate.
- **Ascertainment/selection bias** — community-led case finding over-counts; media attention
  surfaces cases that registries count differently.
- **Residential mobility & latency** — cancer may initiate before or after residence in the
  area; current residence ≠ exposure location.
- **Confounding** — ancestry, age structure, socioeconomic access to diagnosis.
- **Denominator error** — high growth/turnover makes person-years uncertain.

## 7. Reproducibility

Every chart, table, and map records: data source, retrieval date, processing script,
filters, assumptions, limitations. Pipelines are scripted; outputs are regenerable from raw
inputs. Task-runner targets (or documented equivalents): `bootstrap`, `ingest-public-data`,
`process-gis`, `test`, `dev`, `build-reports`.

## 8. What would upgrade this methodology

Registry-confirmed case counts with diagnosis dates and (securely, under IRB) residence
histories; DPR PUR extracts plus HOA/vendor application records; environmental sampling
(soil/water/dust); and an authorized individual-level epidemiological analysis. Until then,
all outputs are descriptive and hypothesis-generating.
