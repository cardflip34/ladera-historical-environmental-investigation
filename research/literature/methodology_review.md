# Methodology Review — Investigating a Rare-Cancer Cluster

**Prepared:** 2026-07-18. Companion to `METHODOLOGY.md`. Draws on LIT-012–016, LIT-019,
LIT-021, LIT-022.

## Why most cancer-cluster investigations find no cause

State/local agencies receive on the order of **1,000 cluster inquiries per year**; most are
resolved at initial contact, and formal investigations are, per CDC/CSTE guidance,
**"unlikely to find an associated environmental contaminant."** *(LIT-013)* Canonical
examples — Fallon (NV) leukemia, McFarland (CA) mixed pediatric cancers — were statistically
real excesses with **no identifiable cause**. Two Ewing-sarcoma-specific investigations,
**Wake County (NC)** and **Washington County (PA)**, both declined to confirm an
environmental cause. *(LIT-014, LIT-015, LIT-016)*

This is not evidence that clusters are never real; it is evidence that the base rate of
"real, attributable environmental cause found" is low, and that confident causal claims are
usually premature.

## The core statistical traps

1. **Silent multiple comparisons / "Texas sharpshooter."** Drawing the boundary *after*
   seeing the cases inflates false positives. Nethery et al. argue the standard SIR protocol
   is "statistically backwards" — it tests for elevated risk before identifying a hazard
   source. Random spatial clustering of a rare disease is *expected* across many small areas.
   *(LIT-012)*
2. **Boundary/time/disease selection.** The choice of geography, time window, and which
   diagnoses "count" (Ewing only? all sarcomas? all pediatric cancer?) each move the apparent
   rate. Pre-specification and comparison zones mitigate this. *(LIT-012)*
3. **Small-number instability.** Crude SIRs for a ~1–3 per million disease in a small
   population have enormous chance variation. Bayesian shrinkage (BYM2/INLA) "borrows
   strength" across areas to stabilize estimates. *(LIT-022)*
4. **Latency.** The relevant exposure for a childhood cancer may precede diagnosis by years;
   a case who did not live in the area during the etiologic window cannot be tied to a local
   contaminant. *(LIT-013)*
5. **Residential mobility.** 55–58% of childhood-cancer cases move between birth and
   diagnosis; birth address is a poor exposure proxy and mobility can bias case-vs-control
   comparisons. *(LIT-019)*
6. **Ascertainment / selection bias.** Community-led, media-amplified case-finding
   oversamples cases and can inflate the numerator without a matching denominator. Controls
   must derive from the same population base.
7. **Ecological fallacy.** Area-level exposure does not imply individual-level exposure.
8. **Confounding by ancestry and age structure** — decisive for Ewing sarcoma (see
   `evidence_review.md` §1) and for a young, predominantly non-Hispanic-white community.

## What a valid analysis would require

- A **pre-specified exposure hypothesis and identified hazard source** before analysis.
  *(LIT-012)*
- **Age-, sex-, and ancestry-specific expected rates** from SEER / the California Cancer
  Registry — non-negotiable given the Ewing ancestry gradient.
- **Poisson-exact and/or Bayesian small-area** methods; **SaTScan** for space-time detection
  with a correct population-at-risk. *(LIT-021, LIT-022)*
- **Individual residential histories** across the etiologic window, not birth address alone.
- Explicit accounting for the **multiple-comparison and boundary-selection** process.
- Registry-confirmed diagnoses and dates (removing media/ascertainment noise).

## How LEHRP applies this now

LEHRP does **not** hold verified case data or individual residences, so it does **not**
compute a definitive SIR or run a spatial scan on patients. Instead it:

- Computes **scenario-based, explicitly hypothetical** SIRs over a grid of case counts, time
  windows, denominators, and — importantly — **ancestry-adjusted** expected rates, with
  Poisson CIs and leave-one-out sensitivity (`METHODOLOGY.md` §3, and the incidence notebook).
- Treats every apparent signal as hypothesis-generating, tags it with a claim level, and
  routes the analysis that *would* resolve it into `FUTURE_EVIDENCE_GATES.md`.
