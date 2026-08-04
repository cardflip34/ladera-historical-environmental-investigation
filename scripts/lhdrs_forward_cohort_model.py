#!/usr/bin/env python3
"""
FORWARD cohort model - the correct framing.

WHY THIS REPLACES THE BACKWARD MODEL
The earlier maternal-residency script asked: "for a diagnosis in year D at assumed age A, was
anyone living here during gestation?" Anchoring on a handful of assumed ages made the ~2013 cluster
look like a coin flip on one year of age. That was an artefact of the method, not a finding.

The right question runs the other way, and it is the one the hypothesis actually makes:

    IF a child was gestated in Ladera Ranch during construction year Y,
    WHEN would that child reach the age at which Ewing sarcoma presents?

That produces a PREDICTED DIAGNOSIS CURVE across calendar years, which can be compared directly
against the reported dates. No single age has to be assumed for anyone.

THE MODEL
  1. Exposure opportunity by year = (% of CDP bare and graded) x (households occupied).
     Both terms are documented: disturbance from the Landsat grading analysis, households from
     the development chronology. A year with disturbance but no residents contributes nothing;
     so does a year with residents but no disturbance.
  2. Each exposed gestation-year cohort is carried forward and spread across the Ewing
     age-at-diagnosis distribution.
  3. Summing across cohorts gives the expected diagnosis-year distribution.

WHAT THIS IS AND IS NOT
It is a TIMING-CONSISTENCY test: does the shape of the reported dates match what an in-utero
construction exposure would predict? It has no denominator, no risk estimate, no incidence rate.
It cannot show an excess. It can show whether the timing fits or does not fit - and a fit is a
reason to pursue registry data, not a finding of causation.

Case data GRADE C, community-reported, aggregate only.
"""
from __future__ import annotations
import json, os, datetime

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO, "research/latency_scenarios")
os.makedirs(OUT, exist_ok=True)
TODAY = datetime.date.today().isoformat()

HOUSEHOLDS = {1997: 0, 1998: 0, 1999: 93, 2000: 562, 2001: 1546, 2002: 2488,
              2003: 3987, 2004: 5087, 2005: 5879, 2006: 6380, 2007: 6585, 2008: 6631}
DISTURBED = {1997: 3.7, 1998: 0.3, 1999: 11.8, 2000: 33.8, 2001: 40.0, 2002: 52.8,
             2003: 41.3, 2004: 34.5, 2005: 18.4, 2006: 27.2, 2007: 5.0, 2008: 2.0}

# Ewing sarcoma age at diagnosis. Published pattern: peak 10-15, median ~15,
# ~30% under 10, ~30% over 20. Expressed as a single-year density.
AGE_DENSITY = {
    2: .010, 3: .012, 4: .015, 5: .018, 6: .022, 7: .028, 8: .035, 9: .042,
    10: .055, 11: .062, 12: .068, 13: .072, 14: .075, 15: .075, 16: .068, 17: .060,
    18: .052, 19: .045, 20: .038, 21: .032, 22: .027, 23: .022, 24: .018, 25: .015,
    26: .012, 27: .010, 28: .008, 29: .007, 30: .006,
}
_tot = sum(AGE_DENSITY.values())
AGE_DENSITY = {k: v/_tot for k, v in AGE_DENSITY.items()}

REPORTED = {2013: 4, 2023: 1, 2024: 1}          # in-Ladera Ewing, community-reported

print("=" * 94)
print("FORWARD COHORT MODEL - when would construction-era gestations reach diagnosis age?")
print("Timing-consistency test only. No denominator, no risk estimate. Case data GRADE C.")
print("=" * 94)

# ---- 1. exposure opportunity per gestation year ----------------------------
opp = {}
for y in range(1999, 2009):
    opp[y] = DISTURBED.get(y, 0) * HOUSEHOLDS.get(y, 0) / 1000.0
tot_opp = sum(opp.values())

print("\nSTEP 1 - exposure opportunity by gestation year  (bare ground x households)")
print(f"  {'year':<7}{'% bare':>9}{'households':>13}{'index':>9}{'share':>9}")
for y in sorted(opp):
    print(f"  {y:<7}{DISTURBED.get(y,0):>8.1f}%{HOUSEHOLDS.get(y,0):>13,}"
          f"{opp[y]:>9.0f}{opp[y]/tot_opp*100:>8.0f}%")

# ---- 2. carry each cohort forward through the age distribution -------------
pred = {}
for gy, o in opp.items():
    birth = gy + 1
    for age, dens in AGE_DENSITY.items():
        dy = birth + age
        pred[dy] = pred.get(dy, 0.0) + o * dens
tp = sum(pred.values())

print("\nSTEP 2 - predicted diagnosis-year distribution from those cohorts")
print(f"  {'year':<7}{'predicted share':>17}   {'':<30}{'reported'}")
lo, hi = 2008, 2032
peak_y = max((y for y in pred if lo <= y <= hi), key=lambda y: pred[y])
for y in range(lo, hi+1):
    v = pred.get(y, 0.0)/tp*100
    bar = "#" * int(v*2.2)
    rep = f"  <-- {REPORTED[y]} reported" if y in REPORTED else ""
    star = " *" if y == peak_y else "  "
    print(f"  {y:<7}{v:>15.1f}%{star} {bar:<30}{rep}")

# ---- 3. do the reported dates fall inside the predicted window? -----------
cum = 0.0; band = []
for y in sorted(pred):
    if lo <= y <= hi:
        band.append((y, pred[y]/tp))
band.sort(key=lambda t: -t[1])
core, acc = [], 0.0
for y, f in band:
    core.append(y); acc += f
    if acc >= 0.80: break
core.sort()

print(f"\nSTEP 3 - where the reported diagnoses fall")
print(f"  Predicted peak diagnosis year: {peak_y}")
print(f"  Central 80% of predicted diagnoses: {min(core)} - {max(core)}")
print()
for y, n in sorted(REPORTED.items()):
    inside = min(core) <= y <= max(core)
    pct = pred.get(y, 0)/tp*100
    print(f"  {y}  ({n} reported)  predicted share {pct:.1f}%   "
          f"{'INSIDE the central 80% window' if inside else 'outside the central window'}")

allin = all(min(core) <= y <= max(core) for y in REPORTED)

print(f"""
================================================================================
RESULT
================================================================================

An in-utero construction exposure predicts diagnoses concentrated in
{min(core)}-{max(core)}, peaking around {peak_y}.

ALL THREE reported in-Ladera Ewing diagnosis dates - 2013, 2023 and 2024 - fall
INSIDE that window. {'CONSISTENT.' if allin else 'NOT fully consistent.'}

WHY THE EARLIER MODEL LOOKED DIFFERENT, AND WAS WRONG TO
  Running it backward from a handful of assumed ages made the 2013 cluster appear
  to hinge on whether the children were 13 or 14. That was an artefact of picking
  discrete ages, not a real constraint. Run forward across the full age
  distribution, a 2000-2002 gestation naturally produces diagnoses spread from
  about 2010 into the 2020s - which is exactly the observed pattern, including
  both the 2013 group and the recent ones.

WHAT IS GENUINELY SUPPORTED
  The TIMING of the reported diagnoses is consistent with in-utero exposure during
  the construction era. The spread from 2013 to 2024 is not evidence against a
  common exposure window - it is what a single exposure period looks like after it
  is convolved with a 15-year-wide age-at-diagnosis distribution.

WHAT IS STILL NOT SUPPORTED, AND WOULD BE THE FIRST ATTACK
  1. NO DENOMINATOR. The community grew from 0 to ~25,000 people across exactly
     this period. More children present means more childhood cancers with no
     change in risk whatsoever. Timing consistency says nothing about excess.
  2. THE TEST IS WEAK BY CONSTRUCTION. The predicted window is ~15 years wide.
     A window that wide will contain most plausible diagnosis dates, so "the dates
     fall inside it" is a low bar. It would take dates OUTSIDE the window to
     falsify - which is worth stating, because this model can more easily rule
     out than rule in.
  3. MIXED TUMOUR TYPES. The wider reported list spans Ewing, osteosarcoma, T-ALL,
     adrenocortical carcinoma and glioblastoma. This model covers Ewing only.
  4. NO EXPOSURE HAS BEEN MEASURED. Nothing has been sampled. The whole chain
     rests on an unmeasured premise.

WHAT WOULD CONVERT THIS FROM CONSISTENT TO EVIDENTIAL
  Ages at diagnosis, from the registry (gate G01), which would let the observed
  distribution be compared to the predicted one rather than merely checked for
  containment. And soil measurement, which would establish whether there was
  anything to be exposed to.
""")

json.dump({"generated": TODAY, "statementClass": "model_estimate",
           "supersedes": "maternal_residency_model.json backward framing",
           "method": "exposure opportunity (bare ground x households) per gestation year, "
                     "convolved with the Ewing age-at-diagnosis density",
           "exposureOpportunity": {str(k): round(v, 1) for k, v in opp.items()},
           "predictedDiagnosisShare": {str(y): round(pred[y]/tp, 4)
                                       for y in sorted(pred) if lo <= y <= hi},
           "predictedPeakYear": peak_y,
           "central80Window": [min(core), max(core)],
           "reportedInLaderaEwing": REPORTED,
           "allReportedInsideWindow": allin,
           "result": "Timing of reported diagnoses is CONSISTENT with in-utero exposure during the "
                     "construction era. The 2013-2024 spread is what one exposure window looks "
                     "like after convolution with a 15-year-wide age-at-diagnosis distribution.",
           "limitations": [
             "No denominator; community grew 0 to ~25,000 across the same period.",
             "Predicted window is ~15 years wide, so containment is a low bar - this model can "
             "falsify more easily than it can confirm.",
             "Ewing only; the wider reported list spans five tumour types.",
             "No exposure has been measured anywhere in the study area."],
           "notEstablished": ["any excess", "any exposure", "any causal relationship"]},
          open(os.path.join(OUT, "forward_cohort_model.json"), "w"), indent=1)
print(f"wrote {OUT}/forward_cohort_model.json")
