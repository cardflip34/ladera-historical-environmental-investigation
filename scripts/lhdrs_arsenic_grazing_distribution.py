#!/usr/bin/env python3
"""
Where the arsenic actually went: a distribution model, not just a total.

The earlier mass balance answered HOW MUCH. It implicitly treated the mass as landing near the
vat. That is wrong, and the correction matters in both directions.

A dipped animal walks out of the vat soaked. It then:
  1. DRIPS for minutes to hours - heaviest in the drain pen, then along the trail out
  2. LICKS its own coat and its herd-mates, ingesting a portion
  3. GRAZES across the range for the next 14-21 days until the next dip
  4. EXCRETES absorbed and ingested arsenic in urine and dung across wherever it walked

So the mass is distributed across the whole grazing area, not concentrated at the vat. The
consequence cuts BOTH ways and the honest version says both:

  - MORE of the ranch is affected than a vat-centred picture implies. Arsenic reached ground
    that never saw a vat.
  - Any given acre of open range carries a LOWER concentration than a vat-side estimate,
    because the same mass is spread over a far larger area.

Cattle do not, however, distribute themselves evenly. They concentrate hard at water, shade,
salt, bedding grounds, corrals and gates. Those are where both dung and hoof traffic
concentrate, and they are therefore the secondary hotspots.

MODEL ESTIMATE. The compartment fractions below are REASONED ALLOCATIONS, not measurements.
They are the weakest numbers in this project and are labelled as such. Nothing here establishes
that arsenic is present anywhere, that anything moved, or that anyone was exposed.
"""
from __future__ import annotations
import json, os, datetime

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO, "research/arsenic_mass_balance")
os.makedirs(OUT, exist_ok=True)
TODAY = datetime.date.today().isoformat()

KG_TO_LB = 2.20462
TOTAL_AS_KG = {"low": 3035.0, "mid": 7280.0, "high": 18029.0}   # from the total-mass script

# ---------------------------------------------------------------------------
# Compartments. Fractions are reasoned allocations and MUST be presented as such.
# Rationale for each is carried in the record so a reviewer can argue with it.
COMPARTMENTS = [
 {"name": "Vat structure + immediate surround",
  "areaHa": 0.05, "frac": 0.10,
  "why": "Leakage through wooden staves (BAI Circular 174 states leaking is common in wooden "
         "vats), splash-out during plunging, and spillage while charging and topping up. Small "
         "footprint, sustained loss over the whole service life."},
 {"name": "Drain pen / drip pen",
  "areaHa": 0.2, "frac": 0.30,
  "why": "Purpose-built to catch drip. The heaviest single deposition zone by design - animals "
         "stand here specifically so solution runs off before they leave."},
 {"name": "Working corrals, chutes, approach lanes",
  "areaHa": 2.0, "frac": 0.20,
  "why": "Wet animals crowded and held; continued dripping; churned ground that absorbs readily."},
 {"name": "Trails, water, shade, salt, bedding grounds",
  "areaHa": 50.0, "frac": 0.25,
  "why": "Residual drip on the walk out, then concentrated dung and urine where cattle congregate. "
         "Cattle distribution is strongly clustered, not uniform - these are the secondary "
         "hotspots and they are also, notably, where WATER is."},
 {"name": "Open range - general grazing",
  "areaHa": 20000.0, "frac": 0.15,
  "why": "Excretion of absorbed and ingested arsenic across the wider range over the days "
         "following each dip. Largest area, smallest share, lowest concentration."},
]

SOIL_BULK_DENSITY = 1400.0   # kg/m3
DEPTH_M = 0.15

print("=" * 88)
print("WHERE THE ARSENIC WENT - distribution across a dipped grazing operation")
print("MODEL ESTIMATE. Compartment fractions are reasoned allocations, not measurements.")
print("=" * 88)

for case in ("low", "mid", "high"):
    tot = TOTAL_AS_KG[case]
    print(f"\n--- {case.upper()} case: {tot:,.0f} kg ({tot*KG_TO_LB:,.0f} lb) elemental arsenic total ---\n")
    print(f"   {'compartment':<44}{'area ha':>9}{'share':>7}{'kg As':>10}{'mg/kg soil':>13}")
    for c in COMPARTMENTS:
        kg = tot * c["frac"]
        soil_kg = c["areaHa"] * 10000 * DEPTH_M * SOIL_BULK_DENSITY
        ppm = kg / soil_kg * 1e6
        print(f"   {c['name']:<44}{c['areaHa']:>9,.2f}{c['frac']*100:>6.0f}%{kg:>10,.0f}{ppm:>13,.1f}")

print("""
CALIFORNIA CONTEXT: typical background soil arsenic runs roughly 1-11 mg/kg, and DTSC
residential screening levels sit in the single-digit mg/kg range.

WHAT THIS SAYS

  The vat, the drain pen and the corrals carry concentrations that are orders of magnitude
  above background even on the low case. Those are small, findable footprints - and a
  leaking wooden vat makes the vat compartment a point source rather than a smear.

  The open range carries a concentration that is LOW - at or near background once spread
  across tens of thousands of acres. That is the honest counterweight, and it must be said
  plainly: an arsenic signature on general grazing land is NOT expected to be dramatic.

  The trails/water/shade/bedding compartment is the one to think hardest about. It is where
  cattle congregated, where dung concentrated, and it is also WHERE THE WATER WAS. Drainage
  corridors are both a deposition zone and a transport path.

WHAT THIS DOES NOT SAY

  Nothing here establishes that arsenic is present at any location in Ladera Ranch, that any
  vat stood there, that anything moved anywhere, or that any person was exposed. Every
  compartment fraction is a reasoned guess. A single accredited soil result outweighs this
  entire table.""")

json.dump({
 "generated": TODAY,
 "statementClass": "model_estimate",
 "weakestLink": "Compartment fractions are REASONED ALLOCATIONS, not measurements. They are the "
                "least defensible numbers in this project and any reviewer should challenge them.",
 "totalElementalArsenicKg": TOTAL_AS_KG,
 "compartments": [{"name": c["name"], "areaHectares": c["areaHa"], "massFraction": c["frac"],
                   "rationale": c["why"],
                   "mgPerKgSoil": {k: round(TOTAL_AS_KG[k]*c["frac"] /
                                   (c["areaHa"]*10000*DEPTH_M*SOIL_BULK_DENSITY)*1e6, 2)
                                   for k in TOTAL_AS_KG}}
                  for c in COMPARTMENTS],
 "soilAssumptions": {"bulkDensityKgM3": SOIL_BULK_DENSITY, "depthM": DEPTH_M},
 "californiaBackgroundMgKg": [1, 11],
 "twoSidedFinding": {
   "supportsConcern": "Vat, drain pen and corral compartments exceed background by orders of "
                      "magnitude even on the low case, and a leaking wooden vat concentrates loss "
                      "at a point rather than spreading it.",
   "cutsAgainstConcern": "Open grazing range carries concentrations at or near background once "
                         "the same mass is spread over tens of thousands of acres. A dramatic "
                         "arsenic signature on general pasture is NOT the expectation."},
 "notEstablished": ["presence of arsenic at any Ladera Ranch location",
                    "existence of a vat within the study area",
                    "movement of any material",
                    "any human exposure",
                    "any health effect"],
 "supersededBy": "Any accredited laboratory soil or sediment measurement.",
}, open(os.path.join(OUT, "arsenic_grazing_distribution.json"), "w"), indent=1)
print(f"\nwrote {OUT}/arsenic_grazing_distribution.json")
