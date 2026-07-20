#!/usr/bin/env python3
"""Birth-cohort / exposure-timing analysis for the legacy-soil hypothesis.

The question: mass grading of former agricultural land occurred ~1999-2006. Reported
diagnoses span 2013-2026. Do the ages work?

This script makes the timing logic explicit by computing, for each plausible
(diagnosis year x age-at-diagnosis) pair, the implied BIRTH YEAR, and flagging whether that
birth cohort could have been present during grading.

It distinguishes two mechanisms that make OPPOSITE predictions:

  M1  CONSTRUCTION-ERA DUST (acute, 1999-2006)
      Requires the child to have been alive/in utero and resident during grading.
      Predicts cases concentrated in birth cohorts <= ~2007.

  M2  PERSISTENT SOIL RESIDUE (chronic, no end date)
      Arsenic is an element and does not degrade; organochlorines (DDT/DDE, toxaphene,
      chlordane) persist for decades - as directly evidenced by DTSC finding them at
      neighbouring former-farm school sites investigated long after cultivation ceased.
      Predicts cases across ALL birth cohorts, with no relationship to the grading date.

Standard library only. Outputs a table to stdout and CSV.
"""
import csv
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

GRADING_START, GRADING_END = 1999, 2006
IN_UTERO_GRACE = 1          # born up to 1 yr after grading ends = in utero during it
DX_YEARS = range(2013, 2027)
# Ewing sarcoma age distribution: peak 10-15; ~30% <10, ~30% >20. Use the pediatric span.
AGES = range(5, 20)


def birth_year(dx, age):
    return dx - age


def present_during_grading(b):
    """Could a child born in year b have been present (incl. in utero) during grading?"""
    return b <= GRADING_END + IN_UTERO_GRACE


def main():
    rows = []
    for dx in DX_YEARS:
        for age in AGES:
            b = birth_year(dx, age)
            rows.append({
                "diagnosis_year": dx,
                "age_at_diagnosis": age,
                "implied_birth_year": b,
                "present_during_grading": "yes" if present_during_grading(b) else "no",
            })

    out = os.path.join(ROOT, "research", "land_use", "exposure_timing_matrix.csv")
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    print("=" * 78)
    print("EXPOSURE-TIMING ANALYSIS — could the reported cases have been present")
    print(f"during mass grading of former agricultural land ({GRADING_START}-{GRADING_END})?")
    print("=" * 78)
    print(f"Grading window: {GRADING_START}-{GRADING_END}. A child born on or before "
          f"{GRADING_END + IN_UTERO_GRACE} could have been present (incl. in utero).\n")

    # For each diagnosis year, what age would a case need to be to have been present?
    print("For a case diagnosed in year D, the child must be AT LEAST this old to have")
    print("been present during grading (younger than this => born after grading ended):\n")
    print(f"  {'dx year':<10}{'min age to overlap grading':<32}{'implied birth year'}")
    for dx in DX_YEARS:
        min_age = dx - (GRADING_END + IN_UTERO_GRACE)
        feasible = min_age <= max(AGES)
        note = "" if feasible else "   <-- impossible at pediatric ages"
        print(f"  {dx:<10}{min_age if min_age > 0 else 0:<32}{GRADING_END + IN_UTERO_GRACE}{note}")

    print("\n" + "=" * 78)
    print("SHARE OF PLAUSIBLE (dx year x age) COMBINATIONS THAT OVERLAP GRADING")
    print("=" * 78)
    for dx in DX_YEARS:
        cells = [present_during_grading(birth_year(dx, a)) for a in AGES]
        n = sum(cells)
        bar = "#" * n + "." * (len(cells) - n)
        print(f"  {dx}  {bar}  {n}/{len(cells)} ages ({100*n/len(cells):.0f}%)")

    print("\n" + "=" * 78)
    print("THE ONE DATABLE EWING CASE — a boundary case, not a decisive one")
    print("=" * 78)
    # Diagnosed Aug 2024 at age ~17 => born between ~Aug 2006 and ~Aug 2007.
    print("  Publicly reported: diagnosed Aug 2024, age ~17")
    print("  => birth window is roughly Aug 2006 - Aug 2007 (an age given as '17' spans a year).")
    print(f"  Grading window: {GRADING_START}-{GRADING_END}.")
    print("\n  Verdict: BOUNDARY / UNINFORMATIVE.")
    print("    - If born late 2006: in utero or newborn during the final months of grading,")
    print("      so an acute dust exposure (M1) is possible but only marginally.")
    print("    - If born 2007: born after grading ended; M1 is not available for this case.")
    print("    - Either way the case is fully compatible with persistent residue (M2),")
    print("      which does not depend on the grading event at all.")
    print("\n  A single case at the boundary cannot discriminate between M1 and M2.")

    print("\n" + "=" * 78)
    print("WHAT THIS DOES AND DOES NOT TELL US")
    print("=" * 78)
    print("  * Only 1 of the reported Ewing cases has BOTH a published age and diagnosis")
    print("    year. A birth-cohort distribution cannot be built from public data.")
    print("  * M1 and M2 make OPPOSITE predictions about birth cohorts, so the birth-year")
    print("    distribution is a DISCRIMINATING TEST - and it is exactly the data we lack.")
    print("  * Ewing sarcoma's etiologic window is UNKNOWN, so no latency assumption can")
    print("    be used to rule either mechanism in or out.")
    print(f"\nWrote {out}")


if __name__ == "__main__":
    main()
