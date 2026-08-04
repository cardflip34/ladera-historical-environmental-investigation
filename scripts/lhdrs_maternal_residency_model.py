#!/usr/bin/env python3
"""
Maternal-residency model: could a mother have BEEN here during the window that matters?

This is the sharper version of the latency question. It does not ask "does a wide window overlap
the grading era" - almost any window does. It asks a question with real discriminating power:

    For a child diagnosed in year D at age A, gestation was ~D-A-0.75.
    HOW MANY HOUSEHOLDS EXISTED IN LADERA RANCH IN THAT YEAR?

If the answer is zero, the mother cannot have been exposed here in utero, regardless of what was
in the soil. That is a falsification test, and it is available for free.

THE OCCUPANCY CURVE - documented, from the project's own development chronology (A2):

    1997  0 sold      approval recalled by developer
    1998  0           development started
    1999  93          FIRST SALES AND OCCUPANCY
    2000  562
    2001  1,546
    2002  2,488       <- peak ground disturbance, 52.8% of CDP bare
    2003  3,987
    2004  5,087
    2005  5,879
    2006  6,380       substantially complete
    2007  6,585
    2008  6,631       sold out except custom

Two facts fall straight out of that curve and they pull in opposite directions:

  BEFORE 1999 there was nobody here. Any gestation window earlier than 1999 is incompatible with
  in-utero exposure AT THIS LOCATION, full stop.

  THE EXPOSURE-OPPORTUNITY PEAK IS NOT THE DISTURBANCE PEAK. Ground disturbance peaked in 2002,
  when only ~2,488 households existed. By the time most households existed (2005-2008) the grading
  was finished. The product of "how much bare ground" x "how many people" peaks somewhere in
  between - and that product is what an exposure-opportunity argument actually rests on.

MODEL OUTPUT is a grid: diagnosis year x assumed age at diagnosis -> gestation year, households
then, and whether that year was inside the active grading era.

WHAT THIS IS NOT: not an epidemiological analysis, no risk estimate, no denominator for incidence.
Ages are NOT known - they are the axis of the grid precisely because they cannot be guessed.
Case data is GRADE C, community-reported, aggregate, no names or addresses.
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
             2003: 41.3, 2004: 34.5, 2005: 18.4, 2006: 27.2}
FIRST_OCCUPANCY = 1999
GRADING = (1999, 2006)          # active construction with residents present

def hh(y):
    y = int(round(y))
    if y < 1997: return 0
    if y > 2008: return HOUSEHOLDS[2008]
    return HOUSEHOLDS[y]

def dist(y):
    y = int(round(y))
    return DISTURBED.get(y, 0.0)

# reported in-Ladera Ewing sarcoma dates (solid amber on the community map)
EWING_LADERA = [(2013.0, 4, "~2013"), (2023.7, 1, "Sept 2023"), (2024.6, 1, "Aug 2024")]
# PUBERTY-CENTRED BAND at 1-year resolution. Ewing sarcoma peaks 10-15 with median ~15, i.e.
# clinical onset clusters at puberty - the growth spurt. This is the biologically motivated
# window and is the band the user specified, so the grid is run finely enough to locate the
# exact age at which in-utero residency flips from impossible to possible.
AGES = list(range(10, 18))

# Approximate share of Ewing cases by single year of age within the puberty band, derived from the
# published pattern (peak 10-15, median ~15, ~30% under 10, ~30% over 20). Used only to weight
# which rows are MORE LIKELY, never to assert any individual's age.
AGE_WEIGHT = {10: 0.07, 11: 0.08, 12: 0.09, 13: 0.10, 14: 0.11, 15: 0.11, 16: 0.09, 17: 0.07}

print("=" * 96)
print("MATERNAL RESIDENCY MODEL - was there anyone here to be exposed?")
print("Case data GRADE C. Ages unknown - shown as a grid because they cannot be guessed.")
print("=" * 96)

print("\nEXPOSURE OPPORTUNITY BY YEAR  (disturbance x households - both must be non-zero)")
print(f"  {'year':<7}{'% CDP bare':>12}{'households':>13}{'opportunity index':>20}")
opp = {}
for y in range(1997, 2007):
    o = dist(y) * hh(y) / 1000.0
    opp[y] = o
    bar = "#" * int(o / 8)
    print(f"  {y:<7}{dist(y):>11.1f}%{hh(y):>13,}{o:>18.0f}  {bar}")
pk = max(opp, key=opp.get)
print(f"\n  -> exposure-opportunity peaks in {pk}, NOT at the 2002 disturbance peak.")
print("     In 2002 the ground was at its most disturbed but only ~2,488 households existed.")
print("     By 2005-2006 most households existed but grading was winding down.")

rows = []
print("\n" + "=" * 96)
print("BACK-CALCULATION: reported in-Ladera Ewing diagnoses")
print("=" * 96)
for dx, n, lbl in EWING_LADERA:
    print(f"\n  DIAGNOSED {lbl}  ({n} reported)")
    print(f"    {'age at dx':<12}{'born':<8}{'gestation':<12}{'households then':>17}{'  verdict'}")
    for a in AGES:
        born = dx - a
        gest = born - 0.75
        h = hh(gest)
        in_grading = GRADING[0] <= gest <= GRADING[1]
        if h == 0:
            verdict = "IMPOSSIBLE - nobody lived here"
        elif in_grading:
            verdict = f"possible, during active grading ({dist(gest):.0f}% bare)"
        else:
            verdict = "possible, but grading finished"
        w = AGE_WEIGHT.get(a, 0.0)
        rows.append({"dxYear": dx, "dxLabel": lbl, "reported": n, "assumedAge": a, "birthYear": round(born, 1),
                     "gestationYear": round(gest, 1), "householdsThen": h,
                     "ageLikelihoodWeight": w,
                     "duringActiveGrading": bool(in_grading and h > 0),
                     "verdict": verdict})
        print(f"    {a:<12}{born:<8.0f}{gest:<12.0f}{h:>17,}  {verdict}")
    # locate the flip point and the weighted split
    poss = [a for a in AGES if hh(dx - a - 0.75) > 0]
    imposs = [a for a in AGES if hh(dx - a - 0.75) == 0]
    wp = sum(AGE_WEIGHT.get(a, 0) for a in poss)
    wi = sum(AGE_WEIGHT.get(a, 0) for a in imposs)
    tw = wp + wi
    if imposs and poss:
        print(f"    >> FLIP POINT: age {max(poss)} possible, age {min(imposs)} impossible.")
    if tw > 0:
        print(f"    >> weighted across the puberty band: {wp/tw*100:.0f}% of likely ages are "
              f"compatible with in-utero residency, {wi/tw*100:.0f}% are not.")

print("""
================================================================================
RE-RUN ON THE PUBERTY BAND - and the 2013 cluster turns on a single year
================================================================================

Ewing sarcoma presents at puberty: peak 10-15, median ~15. Run at one-year
resolution across ages 10-17, the ~2013 cluster has an exact flip point.

  AGE 13 OR YOUNGER  gestation 1999 or later. Households existed (93 to 2,488).
                     Active grading, 12% to 53% of the CDP bare. POSSIBLE.

  AGE 14 OR OLDER    gestation 1998 or earlier. ZERO households. Ladera Ranch did
                     not exist. IMPOSSIBLE, whatever is in the soil.

  Weighted by the published age distribution: 47% of likely ages are compatible
  with in-utero residency here, 53% are not. It is close to a coin flip, and the
  coin is a single year of age.

THE 12-YEAR LATENCY YOU DESCRIBED FITS

  Age 12 at a 2013 diagnosis means gestation in 2000 - 562 households already
  occupied, 34% of the CDP bare, active grading all around them. That is a
  coherent scenario, and it is inside the compatible half of the band.

  Age 10 fits even better: gestation 2002, the peak disturbance year, 52.8% bare.

BUT THE 2023 AND 2024 DIAGNOSES POINT SOMEWHERE ELSE

  Across the whole puberty band, 100% of ages are compatible with residency -
  by then 6,380 to 6,631 households existed. But only age 17 reaches active
  grading. Every other age puts gestation AFTER construction finished.

  So those two cannot be explained by construction dust. If they belong to the
  same story at all, the route has to be RESIDUAL SOIL - material still in the
  ground years after the earthmovers left. That is a different mechanism with a
  different evidentiary burden, and it is the one soil testing speaks to directly.

WHAT THIS MEANS FOR THE INVESTIGATION

  The 2013 cluster is the highest-value case group in the dataset, because it is
  the only one where a single variable - age - flips it between the strongest
  evidence in the project and outright exclusion.

  Four diagnoses. One year of age decides it.

  And it cannot be guessed. Not from photographs, not from yearbooks, not from
  asking around. It comes from registry-confirmed records - gate G01 - or it does
  not come at all.

REMEMBER WHAT IS STILL MISSING, EVEN IF THE AGES FIT

  Compatibility is not evidence. A denominator is still absent; the community grew
  from 0 to ~25,000 people across exactly this period, so more children means more
  childhood cancers with no change in risk. And the reported diagnoses span five
  different tumour types, where a true environmental cluster is usually one.
""")

json.dump({"generated": TODAY, "statementClass": "model_estimate",
           "caseDataProvenance": "Community-reported, GRADE C. Aggregate only, no identifiers.",
           "householdsByYear": HOUSEHOLDS, "disturbedPctByYear": DISTURBED,
           "firstOccupancy": FIRST_OCCUPANCY,
           "exposureOpportunityIndex": {str(k): round(v, 1) for k, v in opp.items()},
           "exposureOpportunityPeakYear": pk,
           "grid": rows,
           "keyFinding": ("Age at diagnosis is decisive. High-school age at the ~2013 cluster "
                          "implies gestation 1994-1998, when Ladera Ranch had zero households - "
                          "incompatible with in-utero exposure at this location. Age 10-12 implies "
                          "gestation 2000-2002, the peak grading years with households present - "
                          "the best fit in the dataset."),
           "counterIntuitive": ("Exposure opportunity = disturbance x population. Disturbance "
                                "peaked 2002 with only ~2,488 households; most households arrived "
                                "2005-2008 after grading. Arguments resting on 'peak grading' "
                                "alone overstate the exposed population."),
           "notEstablished": ["ages of any reported case", "any exposure", "any excess",
                              "any causal relationship"],
           "resolvedBy": "Gate G01 - registry-confirmed diagnoses with ages."},
          open(os.path.join(OUT, "maternal_residency_model.json"), "w"), indent=1)
print(f"wrote {OUT}/maternal_residency_model.json")
