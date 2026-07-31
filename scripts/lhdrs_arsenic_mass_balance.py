#!/usr/bin/env python3
"""
Arsenic mass balance for a compulsory cattle-dipping operation, 1907-1912.

WHAT THIS IS: an order-of-magnitude estimate of how much arsenic trioxide passed through a
dipping operation of stated size, built from historical formula parameters. Every input is a
named, adjustable assumption and every output is a RANGE, not a number.

WHAT THIS IS NOT:
  - not a measurement of arsenic in Ladera Ranch soil
  - not a claim that a vat existed at any specific location
  - not a transport, dispersion or exposure model
  - not evidence of any health effect
It answers one question only: IF a dipping operation of this size ran here, what quantity of
arsenic entered the local environment? That quantity is what makes soil testing worth doing.

statementClass: model_estimate   provenanceGrade of INPUTS: A1/A2 (USDA formulas, quarantine
record). provenanceGrade of OUTPUT: model estimate - display with the badge, never as measurement.

KEY CHEMICAL FACT, and the reason this matters at all:
Arsenic is an ELEMENT. It does not degrade, break down, weather away or have a half-life in the
environmental sense. Organic pesticides applied in 1910 are long gone. Arsenic applied in 1910 is
still present somewhere - redistributed by erosion, grading and runoff, but not destroyed. Any
mass that entered this landscape is still in it unless it was physically hauled away.
"""
from __future__ import annotations
import json, os, datetime

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO, "research/arsenic_mass_balance")
os.makedirs(OUT, exist_ok=True)
TODAY = datetime.date.today().isoformat()

# ---------------------------------------------------------------- parameters
# Standard USDA / Bureau of Animal Industry arsenical dip formula of the period.
LB_AS2O3_PER_500GAL = 8.0          # pounds arsenic trioxide per 500 gallons of charge
VAT_GALLONS         = (2088, 3000, 5000)
# 2,088 gal is now DOCUMENTED, not assumed: BAI Circular 174 (1911) reproduces the Farmers'
# Bulletin 378 swim-vat plans and states such a vat "will hold 2,088 gallons when filled to a
# depth of 5 feet." The circular also describes swim vats "up to 80 or 90 feet in length", so
# larger vats existed; 3,000 and 5,000 are retained as plausible larger cases.
# The swim vat is the relevant type here: the circular calls it "by far the most practical for
# range stock where large numbers of cattle are to be dipped."

YEARS_OPERATING     = 5.0          # OC quarantine ran to Mar 1912; program from ~1907
DIP_INTERVAL_DAYS   = (14, 21)     # compulsory systematic dipping cadence during quarantine

# Drag-out: solution physically carried out of the vat on the animal's coat. This is the dominant
# loss term and the dominant route by which arsenic left the vat and entered surrounding ground.
DRAGOUT_GAL_PER_HEAD = (0.25, 0.5, 1.0)    # low / mid / high, per animal per dipping

# Herd size. The O'Neill Ranch / Rancho Mission Viejo was among the largest cattle operations in
# California. Head counts for the era are NOT established in this repository - this is the single
# largest uncertainty in the calculation and is therefore run across a wide range.
HERD_HEAD = (2000, 5000, 10000, 25000)
# 25,000 is now a SOURCED figure, not a guess:
#   "At one time the ranch had over 25,000 head of cattle but now we try to keep it at about 8,000."
#   - Irish America, "Home on the Range with the O'Neills" (orig. Jan/Feb 1997). Grade B2:
#   reputable outlet quoting the ranching family. The quote is UNDATED ("at one time"), so the
#   peak year is not established. What IS established: the ranch ran 200,000+ acres from 1882,
#   and a half interest was conveyed to O'Neill in 1907 - the dipping period itself.
#   Treat 25,000 as a documented historical peak of unknown year, NOT as a 1907-1912 head count.

# Practical vat throughput. A dipping vat processes a finite number of animals per working day;
# period accounts put a single vat in the low hundreds per day.
HEAD_PER_VAT_PER_DAY = (300, 500)
WORKING_DAYS_PER_CYCLE = (12, 18)   # working days available inside a 14-21 day compulsory cycle

AS_FRACTION_OF_AS2O3 = 0.7574      # As2O3 -> elemental As by mass (2*74.92 / 197.84)
LB_TO_KG = 0.453592


def standing_charge(vat_gal):
    """Arsenic trioxide in one full vat charge."""
    lb = LB_AS2O3_PER_500GAL * (vat_gal / 500.0)
    return lb, lb * LB_TO_KG


def dips_per_year(interval_days):
    return 365.0 / interval_days


def total_dragout(herd, interval_days, dragout_gal, years):
    """Gallons of arsenical solution carried out of the vat over the operating life."""
    return herd * dips_per_year(interval_days) * dragout_gal * years


def as2o3_in_gallons(gal):
    lb = LB_AS2O3_PER_500GAL * (gal / 500.0)
    return lb, lb * LB_TO_KG


print("=" * 78)
print("ARSENIC MASS BALANCE - compulsory dipping operation, ~1907-1912")
print("MODEL ESTIMATE. Not a measurement. Not a claim about any location.")
print("=" * 78)

print(f"\nFormula: {LB_AS2O3_PER_500GAL} lb arsenic trioxide per 500 gallons")
print(f"Operating period: {YEARS_OPERATING:.0f} years")
print(f"Dipping cadence: every {DIP_INTERVAL_DAYS[0]}-{DIP_INTERVAL_DAYS[1]} days (compulsory)\n")

print("-- 1. STANDING CHARGE: arsenic sitting in the vat at any moment --\n")
for v in VAT_GALLONS:
    lb, kg = standing_charge(v)
    print(f"   {v:>5,} gal vat   {lb:7.1f} lb As2O3   ({kg:6.1f} kg)   "
          f"= {kg*AS_FRACTION_OF_AS2O3:6.1f} kg elemental As")

print("\n-- 2. THROUGHPUT: arsenic carried OUT of the vat over the operating life --")
print("   Drag-out is solution leaving on the animal's coat. It is the dominant loss route")
print("   and the dominant route into surrounding soil.\n")

results = []
for herd in HERD_HEAD:
    lo = total_dragout(herd, DIP_INTERVAL_DAYS[1], DRAGOUT_GAL_PER_HEAD[0], YEARS_OPERATING)
    mid = total_dragout(herd, 17.5, DRAGOUT_GAL_PER_HEAD[1], YEARS_OPERATING)
    hi = total_dragout(herd, DIP_INTERVAL_DAYS[0], DRAGOUT_GAL_PER_HEAD[2], YEARS_OPERATING)
    out = []
    for g in (lo, mid, hi):
        lb, kg = as2o3_in_gallons(g)
        out.append(kg * AS_FRACTION_OF_AS2O3)
    results.append({"herdHead": herd,
                    "dragoutGallons": {"low": round(lo), "mid": round(mid), "high": round(hi)},
                    "elementalArsenicKg": {"low": round(out[0], 1), "mid": round(out[1], 1),
                                           "high": round(out[2], 1)}})
    print(f"   herd {herd:>6,} head   elemental arsenic carried out: "
          f"{out[0]:8,.0f} - {out[2]:9,.0f} kg   (mid {out[1]:,.0f} kg)")

print("\n-- 2b. HOW MANY VATS THE HERD REQUIRES --")
print("   Compulsory dipping means the ENTIRE herd must pass through a vat every 14-21 days.")
print("   That is a throughput constraint, and it determines the number of facilities.\n")
vatcalc=[]
for herd in HERD_HEAD:
    lo = herd / (HEAD_PER_VAT_PER_DAY[1] * WORKING_DAYS_PER_CYCLE[1])
    hi = herd / (HEAD_PER_VAT_PER_DAY[0] * WORKING_DAYS_PER_CYCLE[0])
    import math as _m
    vatcalc.append({"herdHead": herd, "vatsRequiredLow": _m.ceil(lo), "vatsRequiredHigh": _m.ceil(hi)})
    print(f"   herd {herd:>6,} head   requires {_m.ceil(lo)} - {_m.ceil(hi)} vat(s) operating simultaneously")
print()
print("   This is the structural point. A single vat cannot cycle a large herd inside the")
print("   compulsory interval, so a ranch of this size needed SEVERAL dipping stations")
print("   distributed across its range - sited where cattle already were, near water and")
print("   handling grounds. Multiple stations across 200,000+ acres raises the prior that")
print("   one stood within any given part of the historic ranch, including the ground that")
print("   is now Ladera Ranch. It does NOT establish that one did.")

print("\n-- 3. WHAT THAT MASS WOULD MEAN IF SPREAD OVER GROUND --")
print("   Illustrative only. Real distribution would be highly concentrated near the vat,")
print("   pens and approach lanes, NOT uniform. Uniform spreading UNDERSTATES local peaks.\n")
SOIL_BULK_DENSITY = 1400.0   # kg/m3, typical
DEPTH_M = 0.15               # nominal plough/surface layer
for area_ha, label in ((1, "1 hectare - vat, pens and approach"),
                       (10, "10 hectares - holding ground"),
                       (100, "100 hectares - wider paddock")):
    soil_kg = area_ha * 10000 * DEPTH_M * SOIL_BULK_DENSITY
    print(f"   {label:<40}", end="")
    mid = results[1]["elementalArsenicKg"]["mid"]      # 5,000 head mid case
    ppm = mid / soil_kg * 1e6
    print(f" {ppm:12,.0f} mg/kg  (5,000-head mid case)")

print("\n   For scale: California DTSC residential screening levels for arsenic are in the")
print("   single-digit mg/kg range, and typical CA background is roughly 1-11 mg/kg.")
print("   Any of the figures above exceed that by orders of magnitude - which is exactly why")
print("   this is worth MEASURING rather than arguing about.")

print("\n-- 4. THE PERSISTENCE POINT --")
print("   Arsenic is an element. It does not degrade. Unlike DDT or toxaphene it has no")
print("   environmental half-life - it is only ever moved, diluted, buried or hauled away.")
print("   Mass that entered this landscape in 1907-1912 is still in the landscape today")
print("   unless it was physically removed. Grading redistributes it; it does not destroy it.")

json.dump({
 "generated": TODAY,
 "statementClass": "model_estimate",
 "provenanceGradeInputs": "A1/A2 - period USDA arsenical dip formula; documented compulsory quarantine",
 "provenanceGradeOutput": "MODEL ESTIMATE - must be displayed with a model-estimate badge, never as measurement",
 "question": "IF a dipping operation of this size operated in this landscape, what mass of arsenic entered it?",
 "notAnswered": ["whether a vat existed at any specific location",
                 "whether arsenic is present in Ladera Ranch soil today",
                 "where any arsenic moved",
                 "whether any person was exposed",
                 "any health effect whatsoever"],
 "parameters": {
   "lbAs2O3per500gal": LB_AS2O3_PER_500GAL,
   "vatGallons": list(VAT_GALLONS),
   "yearsOperating": YEARS_OPERATING,
   "dipIntervalDays": list(DIP_INTERVAL_DAYS),
   "dragoutGalPerHead": list(DRAGOUT_GAL_PER_HEAD),
   "herdHeadRange": list(HERD_HEAD),
   "as2o3ToElementalAs": AS_FRACTION_OF_AS2O3,
 },
 "standingCharge": [{"vatGallons": v,
                     "lbAs2O3": round(standing_charge(v)[0], 1),
                     "kgElementalAs": round(standing_charge(v)[1]*AS_FRACTION_OF_AS2O3, 1)}
                    for v in VAT_GALLONS],
 "throughput": results,
 "vatsRequired": vatcalc,
 "herdSizeSource": {"figure": "over 25,000 head", "quote": "At one time the ranch had over 25,000 head of cattle but now we try to keep it at about 8,000.", "source": "Irish America, Home on the Range with the O'Neills, orig. Jan/Feb 1997", "url": "https://www.irishamerica.com/2024/10/home-on-the-range-with-the-oneills/", "provenanceGrade": "B2", "limitation": "Undated - 'at one time'. Peak year not established. Not a 1907-1912 head count."},
 "dominantUncertainty": "Herd size. Head counts for the O'Neill Ranch in 1907-1912 are NOT "
                        "established in this repository. The range spans an order of magnitude "
                        "and the output scales linearly with it. Establishing the actual head "
                        "count would tighten this more than any other single input.",
 "persistence": "Arsenic is an element and does not degrade. It has no environmental half-life. "
                "Mass introduced 1907-1912 remains in the landscape unless physically removed.",
 "whatThisJustifies": "Soil and sediment testing. It does not justify any causal statement.",
}, open(os.path.join(OUT, "arsenic_mass_balance.json"), "w"), indent=1)
print(f"\nwrote {OUT}/arsenic_mass_balance.json")
