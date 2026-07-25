# PREREGISTERED EPIDEMIOLOGICAL ANALYSIS PLAN (Workstream 10)

**Date:** 2026-07-23 · single-reviewer · **hypothesis-neutral, no cluster asserted.** This is a
*design* to be registered **before** any observed counts are analyzed, per CDC/ATSDR guidance and to
defuse the Texas-Sharpshooter (silent multiple-comparisons) problem. Levels: a fact · b strong ·
c suggestive · d plausible · e hypothesis · g unknown.

## 0. Governing framework
- **CDC 2022 "Guidelines for Examining Unusual Patterns of Cancer and Environmental Concerns"** —
  cancer cluster = "a greater-than-expected number of the same or **etiologically related** cancer
  cases in a group of people in a geographic area over a defined period." Uses a **10-criteria
  decision form**; **de-emphasizes statistical significance** as the gate; emphasizes community input
  and proactive registry review. (cdc.gov/cancer-environment/php/guidelines)
- Analysis must be **authorized** and use the **California Cancer Registry (CCR)**, not tallies from
  media or social platforms (governance rule).

## 1. Case definition (pre-specified; do NOT pool biologically unrelated cancers)
- **Primary:** Ewing sarcoma — **pathology-confirmed, EWSR1(FET)::ETS-fusion-positive**, ICD-O-3
  morphology 9260/3 (+ related PNET codes), any primary site (bone or extraskeletal), age 0–39 at dx.
- **Secondary (separate analyses, never merged with Ewing):** each other verified diagnosis handled in
  its own etiologically-defined stratum (osteosarcoma, leukemia, etc.). Rare-cancer heterogeneity is a
  known cluster-inflation trap; "any rare cancer" is **not** a valid case definition.

## 2. Geographic boundaries — PRE-SPECIFIED, with sensitivity set (not drawn around cases)
Primary: **Ladera Ranch CDP.** Sensitivity boundaries fixed in advance: (a) Ladera CDP; (b) Ladera +
Covenant Hills; (c) 92694 ZIP; (d) 5-mile exposure ring (Zone B); (e) South-OC comparison set (Zone C:
Talega, Aliso Viejo, Foothill Ranch — matched by development age/demographics, **never by case
counts**). Boundaries are frozen before observed counts are examined.

## 3. Time boundaries
Primary dx window **2005–present** (community build-out); extended **2000–present**. Report by
single years and rolling windows fixed in advance. Distinguish **residence at diagnosis** from
**residence during the etiologic window** (for Ewing: prenatal/early-life — see §6).

## 4. Denominator & person-time (the usual failure point)
- Source: **U.S. Census / ACS** for the frozen boundaries; child/adolescent (0–19) and 0–39 strata;
  **residency-duration** and in/out-**migration** modeled (master-planned community → high turnover).
- Person-years, not headcount, drive expected counts.

## 5. Expected incidence (SEER baseline, adjusted)
- Ewing **~2.93–3.0 per million/year, ages <20** (SEER). Peak **10–15 y**; **M:F ≈ 3:1**; incidence
  **~9× higher in white than Black** individuals. → **age, sex, and ancestry standardization are
  mandatory** (an affluent, higher-white-proportion community raises the *expected* baseline; failing
  to adjust would bias toward a false excess).

### Illustrative expected-count math (FRAMEWORK ONLY — not an observed result)
For a hypothetical 0–19 population P over T years at rate r = 2.93×10⁻⁶/yr:
`Expected E = P × r × T`. Example P≈10,000, T=20 → **E ≈ 0.59 cases**; ancestry-adjusted upward
perhaps ~0.7–1.0. **Interpretation caution:** with E<1, Poisson confidence intervals are very wide and
any single observed count is statistically unstable — a defensible analysis reports the **exact
Poisson/Byar CI and the SIR**, never a point estimate alone, and never treats small numbers as proof.
**Observed counts must come from verified CCR case ascertainment, not this illustration.**

## 6. Etiologic-window handling
Ewing likely initiates early (embryonic/pediatric mesenchymal progenitor; see 07_). Exposure-relevant
residence is the **prenatal/early-life** window, which may differ from residence at diagnosis. Analyses
that use only address-at-diagnosis will misclassify exposure.

## 7. Statistical methods
- **Standardized Incidence Ratio (SIR)** with **exact Poisson (Byar) 95% CI**; age/sex/ancestry
  standardized to CCR/SEER.
- **Rare one-off cluster:** report **Bayesian** posterior (weakly-informative prior) alongside
  frequentist, per the one-off-cluster literature (PMC2694210).
- **Spatial/space-time:** **SaTScan** (Kulldorff) Poisson/Bernoulli, circular **and** elliptic windows,
  multiple max-cluster scales (report all scans run), plus a Bayesian spatial model as cross-check.
- **Small-area estimation** for stability. Correct for **multiple comparisons** explicitly.

## 8. Bias controls
Ascertainment/verification bias (require pathology + CCR match; de-duplicate); **media-driven
recruitment** bias (register case-finding method); residential-mobility; boundary/multiplicity
(pre-registration + report the search space); confounding by ancestry/SES.

## 9. Sensitivity analyses & negative controls
- Re-run across all §2 boundaries and §3 windows.
- **Negative-control outcome:** a common cancer with **no** arsenic hypothesis, analyzed identically —
  an excess there flags ascertainment artifact.
- **Negative-control area:** matched Zone-C community; expect null.

## 10. Analyses that would be INVALID or misleading (do not perform / do not cite)
- Cluster statistics from **social-media / news case counts** (governance red line).
- **Post-hoc boundaries** drawn to encircle known cases (Texas Sharpshooter).
- **Pooling biologically unrelated rare cancers** into one "cancer" count.
- Ignoring the **denominator**, **person-time**, or **ancestry** standardization.
- Reporting a **point SIR** for <5 cases without the exact CI and small-number caveat.
- Inferring causation from a spatial association (overlap ≠ exposure ≠ causation).

## 11. Preregistration & causal framing
Register this plan (boundaries, definitions, methods) before observed-count analysis. A statistically
unusual pattern, if found, is a **signal to investigate exposure**, not evidence of arsenic causation;
integrate with the source–pathway–receptor and Bradford-Hill work (14_causal_inference).

## Sources
CDC 2022 guidelines (cdc.gov/cancer-environment); Ewing incidence SEER/ACS (StatPearls NBK559183;
ACS key statistics); SaTScan/Kulldorff (satscan.org; PMC3965324); one-off cluster Bayesian PMC2694210;
cluster causal-inference framework PMC8276584; challenges/limitations (CDC Challenges-and-Limitations PDF).
