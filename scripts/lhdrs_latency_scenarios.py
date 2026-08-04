#!/usr/bin/env python3
"""
Latency scenarios: back-calculate exposure windows from reported diagnosis dates.

THE QUESTION
If a reported Ewing sarcoma diagnosis occurred in year D, and the etiologically relevant exposure
happened L years earlier, what calendar window does that point to - and does it overlap the
1997-2006 grading period?

WHAT DRIVES THE MODEL
Ewing sarcoma age at diagnosis is well characterised: peak 10-15 years, median ~15, roughly 30% of
cases under 10 and 30% over 20. Three latency models are run:

  IN UTERO      exposure during gestation; diagnosis at the person's age.
                This is the user's hypothesis, and it is the one with actual published
                investigation behind it (see EVIDENCE below).
  EARLY LIFE    exposure ages 0-5; diagnosis at the person's age.
  PROXIMATE     exposure within ~2 years of diagnosis. Included as the null-ish comparator -
                if this fits best, a historic soil source is a poor explanation.

Each model is run across the age-at-diagnosis distribution, not at a single assumed age, because
the ages of the reported Ladera cases are NOT public and must not be guessed.

EVIDENCE ON THE IN-UTERO WINDOW - stated honestly, because it cuts both ways
  FOR:  Perinatal exposure HAS been formally studied for Ewing sarcoma in California. Wang et al.
        examined ambient PM2.5 in (1) gestation-to-birth and (2) the first year of life, for 388
        cases aged 0-19 diagnosed 1988-2015 against 19,341 controls. Rising incidence in the 0-9
        age band is cited in that literature as a reason to suspect prenatal or early-life
        exposures. So the window the user describes is a recognised research question, not a
        folk theory.
  AGAINST / LIMITS: that study found NO significant association overall. The only elevated
        estimates were in Hispanic children and were not statistically significant
        (gestational Q2 OR 1.53, 95% CI 0.94-2.51 - the interval crosses 1). The authors called it
        "new suggestive evidence" requiring replication.
  AND CRUCIALLY: this project's own literature review records that for Ewing sarcoma the
        etiologically relevant exposure window, IF ONE EXISTS, is unknown, and that the defining
        EWSR1-FLI1 fusion arises post-natally for unknown reasons. A post-natal fusion event is an
        argument against a purely in-utero mechanism.

WHAT THIS SCRIPT IS NOT
Not an epidemiological analysis. It has no denominator, no population at risk, no age structure,
no ancestry adjustment. It cannot say whether there is an excess of anything. It converts reported
dates into candidate exposure windows so those windows can be compared against a known land-use
timeline - and nothing more.

CASE DATA PROVENANCE: community-reported dates from a public map, GRADE C (unverified case
reports). No names, no ages, no addresses. Aggregate only.
"""
from __future__ import annotations
import json, os, datetime
from collections import Counter

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO, "research/latency_scenarios")
os.makedirs(OUT, exist_ok=True)
TODAY = datetime.date.today().isoformat()

# ---- reported dates, as published on the community map. GRADE C. -----------
# in_ladera=True for solid-amber (reported in Ladera Ranch); False for hollow (nearby community).
CASES = [
    {"date": 2008.3, "label": "Apr 2008", "dx": "Ewing sarcoma", "in_ladera": False},
    {"date": 2013.0, "label": "~2013",    "dx": "Ewing sarcoma", "in_ladera": True, "n": 4},
    {"date": 2015.0, "label": "2015",     "dx": "Ewing sarcoma", "in_ladera": False},
    {"date": 2016.1, "label": "Feb 2016", "dx": "Osteosarcoma",  "in_ladera": True},
    {"date": 2019.0, "label": "2019",     "dx": "Ewing sarcoma", "in_ladera": False},
    {"date": 2019.8, "label": "Oct 2019", "dx": "T-ALL / lymphoma", "in_ladera": True},
    {"date": 2020.3, "label": "Apr 2020", "dx": "Adrenocortical carcinoma", "in_ladera": True},
    {"date": 2022.7, "label": "Sept 2022","dx": "Ewing sarcoma", "in_ladera": False},
    {"date": 2023.7, "label": "Sept 2023","dx": "Ewing sarcoma", "in_ladera": True},
    {"date": 2024.6, "label": "Aug 2024", "dx": "Ewing sarcoma", "in_ladera": True},
    {"date": 2025.5, "label": "Jul 2025", "dx": "Glioblastoma",  "in_ladera": True},
]

# ---- age-at-diagnosis distribution for Ewing sarcoma -----------------------
# Published pattern: peak 10-15, median ~15, ~30% under 10, ~30% over 20.
AGE_BANDS = [(2, 9, 0.30), (10, 15, 0.40), (16, 19, 0.15), (20, 30, 0.15)]

GRADING_START, GRADING_END, GRADING_PEAK = 1997.0, 2006.0, 2002.0
OCCUPANCY_START = 1999.0     # first residents; earliest villages

def window(dx_year, lo_age, hi_age, model):
    """Return (earliest, latest) calendar year of the exposure window."""
    if model == "in_utero":
        # conception ~ (dx_year - age) - 0.75
        return (dx_year - hi_age - 0.75, dx_year - lo_age - 0.75)
    if model == "early_life":
        # exposure ages 0-5 -> birth .. birth+5
        return (dx_year - hi_age, dx_year - lo_age + 5)
    if model == "proximate":
        return (dx_year - 2.0, dx_year)
    raise ValueError(model)

def overlap(a, b, c, d):
    lo, hi = max(a, c), min(b, d)
    return max(0.0, hi - lo)

MODELS = ["in_utero", "early_life", "proximate"]
rows = []
print("=" * 92)
print("LATENCY SCENARIOS - candidate exposure windows implied by reported diagnosis dates")
print("Case data GRADE C (community-reported). Not an epidemiological analysis.")
print("=" * 92)

for m in MODELS:
    print(f"\n### MODEL: {m.upper().replace('_',' ')}")
    print(f"    {'reported':<12}{'dx':<26}{'exposure window':<26}{'overlaps grading?':<20}")
    hits = 0; tot = 0
    for c in CASES:
        n = c.get("n", 1)
        # weight across the age distribution: report the union window and the weighted overlap
        wlo = min(window(c["date"], a, b, m)[0] for a, b, _ in AGE_BANDS)
        whi = max(window(c["date"], a, b, m)[1] for a, b, _ in AGE_BANDS)
        wov = sum(w * (overlap(*window(c["date"], a, b, m), GRADING_START, GRADING_END) > 0)
                  for a, b, w in AGE_BANDS)
        tot += n
        hits += n * wov
        mark = f"{wov*100:.0f}% of age dist" if wov > 0 else "no"
        lbl = c["label"] + (f" (x{n})" if n > 1 else "")
        rows.append({"model": m, "label": c["label"], "n": n, "dx": c["dx"],
                     "inLadera": c["in_ladera"], "windowFrom": round(wlo, 1),
                     "windowTo": round(whi, 1), "gradingOverlapWeight": round(wov, 3)})
        print(f"    {lbl:<12}{c['dx'][:24]:<26}{wlo:.0f} - {whi:.0f}{'':<14}{mark:<20}")
    print(f"    -> weighted share of reported cases whose window can reach the grading era: "
          f"{hits/tot*100:.0f}%")

# ---- the Ewing-only view, since that is the coherent cluster question ------
print("\n" + "=" * 92)
print("EWING SARCOMA ONLY - in-Ladera reports (the coherent single-type question)")
print("=" * 92)
ew = [c for c in CASES if "Ewing" in c["dx"] and c["in_ladera"]]
n_ew = sum(c.get("n", 1) for c in ew)
print(f"\n{n_ew} reported in-Ladera Ewing diagnoses across {len(ew)} date entries: "
      f"{', '.join(c['label'] for c in ew)}")
for m in MODELS:
    lo = min(min(window(c['date'], a, b, m)[0] for a, b, _ in AGE_BANDS) for c in ew)
    hi = max(max(window(c['date'], a, b, m)[1] for a, b, _ in AGE_BANDS) for c in ew)
    ov = overlap(lo, hi, GRADING_START, GRADING_END)
    print(f"  {m:<12} combined candidate window {lo:.0f} - {hi:.0f}   "
          f"overlap with grading era: {ov:.0f} years")

print("""
================================================================================
READING THIS HONESTLY
================================================================================

WHAT THE TABLE SHOWS
  Under an in-utero or early-life model, the reported diagnosis dates DO generate
  candidate exposure windows that reach back into the 1997-2006 grading era. That
  is arithmetic, and it is the reason the question is worth asking.

WHY THAT IS NOT EVIDENCE OF ANYTHING YET - four reasons, each fatal on its own:

  1. NO DENOMINATOR. Ladera Ranch grew from ~0 to ~25,000 people between 1999 and
     2006. A community with more children in it will report more childhood cancers
     with no change whatsoever in risk. Counts without a population-at-risk and an
     age structure cannot indicate an excess.

  2. THE WINDOWS ARE WIDE ENOUGH TO HIT ANYTHING. Because the age at diagnosis
     spans roughly 2-30 years, an in-utero window for a 2023 diagnosis spans about
     1993-2021. A window that wide will overlap almost any candidate period,
     including periods when nothing happened. Overlap is therefore weak evidence.

  3. MIXED TUMOUR TYPES ARGUE AGAINST A SINGLE CAUSE. The reported list includes
     Ewing sarcoma, osteosarcoma, T-ALL, adrenocortical carcinoma and glioblastoma.
     These have different cells of origin and different biology. A genuine
     environmental cluster is usually ONE tumour type. A mix is more consistent with
     the ordinary background rates of a large community.

  4. THE IN-UTERO WINDOW IS A HYPOTHESIS, NOT AN ESTABLISHED FACT, FOR EWING.
     It has been formally studied - Wang et al. examined gestational and first-year
     PM2.5 exposure in 388 California Ewing cases. The result was NULL overall; the
     only elevated estimates were in Hispanic children and were NOT statistically
     significant (gestational Q2 OR 1.53, 95% CI 0.94-2.51). And Ewing's defining
     EWSR1-FLI1 fusion is understood to arise POST-natally, which argues against a
     purely in-utero mechanism.

WHAT WOULD ACTUALLY TEST THIS
  Registry-confirmed diagnoses with dates AND AGES, against an age- and
  ancestry-appropriate denominator for this specific population. That is gate G01
  (California Cancer Registry). Ages are the missing variable that would collapse
  these windows from 28 years wide to a few years wide - and it is precisely the
  variable that cannot be guessed or inferred.

  Until then this script does one useful thing only: it shows that the reported
  dates are CONSISTENT with a grading-era exposure window, which is a reason to
  pursue G01 and soil testing - and is not, by itself, evidence of a cause.
""")

json.dump({
 "generated": TODAY,
 "statementClass": "model_estimate",
 "caseDataProvenance": "Community-reported public map. GRADE C, unverified case reports. "
                       "No names, ages, or addresses. Aggregate only.",
 "ewingAgeDistributionUsed": [{"ageLow": a, "ageHigh": b, "weight": w} for a, b, w in AGE_BANDS],
 "gradingEra": {"start": GRADING_START, "end": GRADING_END, "peakDisturbance": GRADING_PEAK},
 "models": {"in_utero": "exposure during gestation",
            "early_life": "exposure ages 0-5",
            "proximate": "exposure within 2 years of diagnosis (comparator)"},
 "windows": rows,
 "keyLimitations": [
   "No denominator: Ladera grew from ~0 to ~25,000 residents 1999-2006.",
   "Windows are 25+ years wide because age at diagnosis is unknown; wide windows overlap almost "
   "any period and so carry little discriminating power.",
   "Reported tumour types are mixed (Ewing, osteosarcoma, T-ALL, adrenocortical, glioblastoma); a "
   "genuine environmental cluster is usually a single type.",
   "The in-utero window for Ewing is a research hypothesis with a NULL primary result in the one "
   "California perinatal study located (Wang et al., 388 cases): no significant association "
   "overall; Hispanic-specific estimates not significant, gestational Q2 OR 1.53 (0.94-2.51).",
   "Ewing's defining EWSR1-FLI1 fusion is understood to arise post-natally, arguing against a "
   "purely in-utero mechanism.",
 ],
 "whatWouldTestIt": "Registry-confirmed diagnoses with dates AND ages against an age- and "
                    "ancestry-appropriate denominator (gate G01, California Cancer Registry). "
                    "Ages would collapse these windows from ~28 years to a few years.",
 "notEstablished": ["any excess of any cancer in this community",
                    "any environmental cause of any diagnosis",
                    "that any exposure occurred at any time"],
}, open(os.path.join(OUT, "latency_scenarios.json"), "w"), indent=1)
print(f"wrote {OUT}/latency_scenarios.json")
