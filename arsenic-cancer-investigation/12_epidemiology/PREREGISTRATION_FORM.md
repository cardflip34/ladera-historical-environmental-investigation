# EPIDEMIOLOGY PREREGISTRATION FORM (DRAFT, to be time-stamped & locked BEFORE any observed counts)

**Status:** DRAFT. Purpose: register the design **before** analysts see case counts — the primary
defense against the Texas-Sharpshooter / silent-multiple-comparisons problem. Complete, date/version-
stamp, and lock (e.g., OSF or equivalent) prior to analysis. Derives from EPIDEMIOLOGICAL_ANALYSIS_PLAN.
No social-media counts. Uses verified California Cancer Registry (CCR) data only.

## 1. Title / version / date-locked
`[title]` · v`[x]` · locked `[YYYY-MM-DD HH:MM TZ]` · registry `[OSF/other ID]`

## 2. Primary question (pre-specified, singular)
Is the age/sex/ancestry-standardized incidence of **EWSR1::ETS-fusion-confirmed Ewing sarcoma** in
`[frozen geography]` during `[frozen period]` greater than expected from CCR/SEER reference rates?

## 3. Case definition (frozen)
- Ewing: pathology-confirmed, **EWSR1(FET)::ETS fusion-positive**, ICD-O-3 `9260/3` (+ specified PNET
  codes), ages `[0–39]`, bone or extraskeletal. Ascertained via **CCR**; de-duplicated; pathology
  verified. Secondary cancers analyzed **separately** (list): `[…]`. **No pooling of unrelated cancers.**

## 4. Geography (frozen; sensitivity set fixed now)
Primary `[Ladera Ranch CDP]`; sensitivity `[+Covenant Hills]`, `[92694 ZIP]`, `[5-mi ring]`, control
`[Zone-C matched community]`. Boundaries frozen before counts examined.

## 5. Time window (frozen)
Primary `[2005–present]`; extended `[2000–present]`. Etiologic-window residence (prenatal/early-life)
captured where available; distinguished from residence-at-diagnosis.

## 6. Denominator / person-time (pre-specified sources)
Census/ACS for frozen boundaries; strata 0–19 and 0–39; residency-duration + migration modeled.

## 7. Expected-rate reference & standardization (pre-specified)
SEER/CCR Ewing rates; **standardize by age, sex, and ancestry** (Ewing ~9× higher in white). State the
reference tables/years now.

## 8. Primary statistic + secondary
SIR with **exact Poisson/Byar 95% CI** (primary); **Bayesian** posterior with prior `[specify]`
(secondary); **SaTScan** Poisson/Bernoulli, circular+elliptic, max cluster sizes `[list]`, all scans
reported; small-area estimation. Multiplicity handling `[method]`.

## 9. Case-finding method (register to expose recruitment bias)
`[CCR query only / active outreach / …]` — pre-declare; flag any media-driven ascertainment.

## 10. Sensitivity analyses (pre-listed)
All §4 boundaries × §6/§7 assumptions; exclude/include borderline diagnoses; migration assumptions.

## 11. Negative controls (pre-specified)
Outcome control: `[common non-arsenic cancer]` analyzed identically (expect null).
Area control: `[Zone-C]` (expect null).

## 12. Decision rules (pre-specified; significance de-emphasized per CDC 2022)
State in advance what each result triggers (e.g., SIR + CI ranges → "further exposure assessment" vs
"no further action"), per the CDC 10-criteria framework — **not** a bright-line p-value.

## 13. Analyses declared INVALID (will not be run/reported)
Social-media/news counts; post-hoc boundary drawing; pooling unrelated cancers; denominator/ancestry
neglect; point SIR for <5 cases without exact CI + small-number caveat; causal inference from spatial
overlap alone.

## 14. Data governance
CCR authorization `[status]`; PHI in folder 04; public outputs masked/aggregated; analysts blinded to
hypothesis where feasible; code + seed archived for reproduction.

## 15. Authors / reviewers / roles
`[epidemiologist, biostatistician, registry liaison, physician lead]`. Dual-review before lock.

*DRAFT — complete, lock, and time-stamp before any count is analyzed. GATE A (design review) → lock →
authorized CCR analysis.*
