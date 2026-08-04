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
EWING_LADERA = [(2013, 4), (2023.7, 1), (2024.6, 1)]
AGES = [8, 10, 12, 14, 16, 18]

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
for dx, n in EWING_LADERA:
    print(f"\n  DIAGNOSED {dx:.0f}  ({n} reported)")
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
        rows.append({"dxYear": dx, "reported": n, "assumedAge": a, "birthYear": round(born, 1),
                     "gestationYear": round(gest, 1), "householdsThen": h,
                     "duringActiveGrading": bool(in_grading and h > 0),
                     "verdict": verdict})
        print(f"    {a:<12}{born:<8.0f}{gest:<12.0f}{h:>17,}  {verdict}")

print("""
================================================================================
WHAT THIS ACTUALLY SHOWS - and it splits the cases
================================================================================

THE ~2013 CLUSTER (4 reported Ewing diagnoses - the largest single entry)

  If those children were HIGH SCHOOL AGE at diagnosis (14-18), they were born
  1995-1999 and gestated 1994-1998. LADERA RANCH DID NOT EXIST THEN. First sales
  and occupancy were 1999. A mother could not have been exposed here in utero,
  whatever is in the soil.

  If they were 10-12, they were born 2001-2003, gestating 2000-2002 - which lands
  directly on the peak grading years, with 562-2,488 households already occupied.
  That is the single best fit in the entire dataset for an in-utero construction
  exposure.

  So your own observation - that many seem to have been in high school - argues
  AGAINST the in-utero pathway for the 2013 group, not for it. The younger they
  were, the better the hypothesis fits; the older they were, the worse.

THE 2023 AND 2024 DIAGNOSES

  At high-school age they gestated 2004-2009. Households existed in numbers by
  then (5,087-6,631), so residency is entirely plausible. But active grading had
  largely finished by 2006. So for these two the exposure route would have to be
  RESIDUAL SOIL rather than construction dust - a different mechanism with a
  different evidentiary requirement.

THE COUNTER-INTUITIVE FINDING WORTH KEEPING

  Exposure opportunity is disturbance MULTIPLIED BY people. Ground disturbance
  peaked in 2002 at 52.8% bare - but only ~2,488 households existed then. Most
  households arrived 2005-2008, after grading. The years when the most people
  were exposed to the most bare ground are the middle years, not the peak year.
  Any argument built on "peak grading" alone overstates the exposed population.

WHAT WOULD SETTLE IT - one variable

  AGE AT DIAGNOSIS. With ages, every row above collapses to one line per case and
  the 2013 cluster either becomes the strongest evidence in the project or is
  excluded outright. Without ages this stays a grid.

  Ages come from gate G01 - registry-confirmed diagnoses. They cannot be guessed,
  inferred from photographs, or asked of families informally without consent.
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
