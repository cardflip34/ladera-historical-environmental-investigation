#!/usr/bin/env python3
"""
Two questions, answered as directly as the evidence allows.

  1. Approximately how many POUNDS of arsenic entered the ground from the O'Neill Ranch
     dipping operation alone, 1907-1912?
  2. How does that compare to the acute lethal dose - the "poisoned wine glass" scale?

BOTH ARE MODEL ESTIMATES. Question 1 rests on a documented but undated herd figure and on
period formula parameters. Question 2 is a scale comparison and IS NOT A RISK ASSESSMENT.

READ THIS BEFORE USING THE LETHAL-DOSE NUMBER ANYWHERE PUBLIC
-------------------------------------------------------------
"N lethal doses" is arithmetic, not toxicology. It is a legitimate way to convey scale and an
illegitimate way to convey risk, for three reasons that any qualified critic will raise:

  a) BIOAVAILABILITY. Arsenic bound in soil is not arsenic dissolved in wine. Soil-bound
     arsenic is typically a small and variable fraction bioavailable when ingested - often
     well under 25%, sometimes a few percent, depending on mineral form and weathering.
  b) PATHWAY. Nobody drinks soil. Realistic exposure is incidental ingestion of small
     quantities of dust, dermal contact, and inhalation of resuspended particles. These are
     orders of magnitude below a poisoning scenario.
  c) MECHANISM. Acute lethality and chronic carcinogenicity are different endpoints with
     different dose-response relationships. The health concern in this investigation is
     chronic low-dose exposure, which the lethal dose says nothing about.

Used honestly the comparison says: THIS IS A LARGE QUANTITY OF A POISON THAT DOES NOT DEGRADE,
WHICH IS WHY IT SHOULD BE MEASURED. Used dishonestly it says people are being acutely poisoned,
which the evidence does not support and which would discredit the whole project.
"""
from __future__ import annotations
import json, os, datetime

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO, "research/arsenic_mass_balance")
os.makedirs(OUT, exist_ok=True)
TODAY = datetime.date.today().isoformat()

KG_TO_LB = 2.20462
AS_FRAC = 0.7574                      # elemental As as a fraction of As2O3 by mass

# ---- from lhdrs_arsenic_mass_balance.py, 25,000-head case -------------------
DRAGOUT_AS_KG = {"low": 2986.0, "mid": 7165.0, "high": 17914.0}

# ---- terminal disposal -----------------------------------------------------
# When the quarantine lifted in March 1912 the vats stopped being used. Period practice was
# frequently to abandon a vat in place and backfill it, or to dump the charge nearby, rather
# than haul several thousand gallons of arsenical solution away. The standing charge of every
# vat is therefore treated as entering the ground at decommissioning.
VATS = (3, 7)                          # throughput-derived for a 25,000 head herd
VAT_GAL = 3000
LB_AS2O3_PER_500GAL = 8.0
charge_as2o3_lb = LB_AS2O3_PER_500GAL * (VAT_GAL / 500.0)      # 48 lb per vat
charge_as_kg = charge_as2o3_lb * 0.453592 * AS_FRAC

# ---- acute lethal dose -----------------------------------------------------
# Standard toxicological reference range for a fatal oral dose of arsenic trioxide in an adult.
# This is textbook material, cited here only to give the environmental mass a familiar scale.
LETHAL_AS2O3_MG = (100.0, 300.0)


def rpt(label, kg):
    lb = kg * KG_TO_LB
    return f"{label:<24} {kg:10,.0f} kg   {lb:11,.0f} lb   ({lb/2000:6.1f} US tons)"


print("=" * 84)
print("HOW MUCH ARSENIC ENTERED THE GROUND - O'NEILL RANCH DIPPING OPERATION, 1907-1912")
print("MODEL ESTIMATE. Not a measurement of any soil anywhere.")
print("=" * 84)

print("\n-- 1. ELEMENTAL ARSENIC INTO THE GROUND, 25,000-head herd, 5 years --\n")
totals = {}
for k in ("low", "mid", "high"):
    v = VATS[0] if k == "low" else VATS[1]
    total = DRAGOUT_AS_KG[k] + charge_as_kg * v
    totals[k] = total
    print("   " + rpt(f"{k} case", total))
    print(f"      drag-out {DRAGOUT_AS_KG[k]:,.0f} kg  +  {v} vat charges abandoned "
          f"{charge_as_kg*v:,.0f} kg")

print("\n   AS ARSENIC TRIOXIDE (the compound actually purchased and poured):\n")
for k in ("low", "mid", "high"):
    t = totals[k] / AS_FRAC
    print("   " + rpt(f"{k} case, As2O3", t))

print("\n   >> HEADLINE: on the mid case, roughly "
      f"{totals['mid']*KG_TO_LB:,.0f} POUNDS of elemental arsenic")
print(f"      ({totals['mid']/AS_FRAC*KG_TO_LB:,.0f} lb as arsenic trioxide, about "
      f"{totals['mid']/AS_FRAC*KG_TO_LB/2000:.0f} tons of the compound)")
print(f"      Full plausible range: {totals['low']*KG_TO_LB:,.0f} - "
      f"{totals['high']*KG_TO_LB:,.0f} lb elemental arsenic.")

print("\n-- 2. SCALE COMPARISON: the poisoned-cup dose --\n")
print(f"   A fatal oral dose of arsenic trioxide for an adult is on the order of "
      f"{LETHAL_AS2O3_MG[0]:.0f}-{LETHAL_AS2O3_MG[1]:.0f} mg.")
print("   That is a quantity smaller than a pea - which is why it was the classical poison.\n")
scale = {}
for k in ("low", "mid", "high"):
    as2o3_mg = totals[k] / AS_FRAC * 1e6
    hi_n = as2o3_mg / LETHAL_AS2O3_MG[0]
    lo_n = as2o3_mg / LETHAL_AS2O3_MG[1]
    scale[k] = {"lethalDosesLow": round(lo_n), "lethalDosesHigh": round(hi_n)}
    print(f"   {k:<5} case  =  {lo_n/1e6:6.1f} - {hi_n/1e6:6.1f} MILLION nominal lethal doses")

print("""
   ------------------------------------------------------------------------
   WHAT THAT NUMBER MEANS, AND WHAT IT DOES NOT

   It means: the quantity of a non-degrading poison introduced to this
   landscape was very large in human terms. That is a legitimate reason to
   MEASURE the soil.

   It does NOT mean anyone is being acutely poisoned. Soil-bound arsenic is
   only partly bioavailable, nobody ingests soil in gram quantities, and
   acute lethality is a different endpoint from the chronic low-dose
   carcinogenic risk that actually matters here.

   Say the first sentence in public. Never say the second thing. A critic
   will reach for the bioavailability point within one sentence, and if the
   claim has been overstated the entire project loses credibility with it.
   ------------------------------------------------------------------------""")

print("\n-- 3. WHAT WOULD TURN THIS ESTIMATE INTO A FINDING --\n")
for t in ["Actual O'Neill Ranch head count for 1907-1912 (Census of Agriculture 1910;",
          "  county assessor livestock rolls; USDA Bureau of Animal Industry annual reports)",
          "Number and LOCATION of dipping stations in Orange County - not found in public",
          "  sources; likely in BAI annual reports or CDFA / county archives",
          "Whether vats were abandoned in place or removed at decommissioning",
          "AND ABOVE ALL: soil and sediment measurements. Everything above is arithmetic.",
          "  One accredited lab result outweighs the entire calculation."]:
    print("   - " + t if not t.startswith("  ") else "     " + t.strip())

json.dump({
 "generated": TODAY,
 "statementClass": "model_estimate",
 "question1": "Approximate pounds of arsenic into the ground, O'Neill Ranch dipping, 1907-1912",
 "totalElementalArsenic": {k: {"kg": round(v), "lb": round(v*KG_TO_LB)} for k, v in totals.items()},
 "totalAsArsenicTrioxide": {k: {"kg": round(v/AS_FRAC), "lb": round(v/AS_FRAC*KG_TO_LB)}
                            for k, v in totals.items()},
 "components": {"dragoutKg": DRAGOUT_AS_KG,
                "abandonedVatChargesKg": {"perVat": round(charge_as_kg, 1), "vats": list(VATS)}},
 "question2": "Scale comparison to the acute lethal dose",
 "lethalDoseAs2O3mg": list(LETHAL_AS2O3_MG),
 "nominalLethalDoseEquivalents": scale,
 "lethalDoseCaveat": ("SCALE DEVICE ONLY, NOT A RISK ASSESSMENT. Soil-bound arsenic is only "
   "partly bioavailable; the exposure pathway is incidental dust ingestion, not drinking; and "
   "acute lethality is a different endpoint from chronic carcinogenic risk. This comparison "
   "justifies measurement. It does not support any claim that anyone is being acutely poisoned."),
 "dominantUncertainties": ["herd size during 1907-1912 specifically (documented peak is undated)",
                           "number and location of dipping stations in Orange County - NOT found "
                           "in public sources",
                           "fate of vat charges at decommissioning",
                           "drag-out rate per animal"],
 "supersededBy": "Any accredited laboratory measurement of soil or sediment. This is arithmetic; "
                 "one real analytical result outweighs all of it.",
}, open(os.path.join(OUT, "arsenic_total_and_scale.json"), "w"), indent=1)
print(f"\nwrote {OUT}/arsenic_total_and_scale.json")
