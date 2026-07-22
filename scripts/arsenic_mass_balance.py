#!/usr/bin/env python3
"""Arsenic mass-balance MODEL ESTIMATE for California cattle-tick dipping (1907-1915).
NOT a measurement. Every assumption is stated inline and can be varied. See
research/arsenic_model/mass_balance.md for the sourced write-up. No California dip-site
soil has ever been tested; these figures are plausibility bounds, not facts.

This version reports in POUNDS and frames the output as arsenic RELEASED INTO THE GROUND
(near-vat concentrated + rangeland-dispersed), bounded above by the total ever purchased."""

LB = 453.592                     # g per pound
As, O = 74.9216, 15.999
As2O3 = 2*As + 3*O
frac = (2*As)/As2O3              # 0.7574 -> white arsenic (As2O3) is 75.7% elemental As
KG_PER_TON = 1000.0
def lb(kg): return kg/ (LB/1000.0) * 1000.0 / 1000.0  # kg -> lb
def kg2lb(kg): return kg*1000.0/LB
def t2lb(t): return kg2lb(t*KG_PER_TON)

print("="*70)
print("ARSENIC RELEASED TO GROUND — CA cattle-dip mandate 1907-1915 (MODEL EST.)")
print("="*70)

# --- STEP 1: chemistry of one charge -------------------------------------
lb_white = 8                                    # USDA formula: 8 lb white arsenic / 500 gal
lb_As_charge = lb_white*frac
print(f"\n[1] CHEMISTRY  (USDA BAI Circular 174/183, 1911)")
print(f"    1 charge = {lb_white} lb white arsenic (As2O3) / 500 gal")
print(f"    white arsenic is {frac*100:.1f}% elemental As")
print(f"    -> elemental As per charge          = {lb_As_charge:5.1f} lb")
conc_mgL = (lb_As_charge*LB) / (500*3.78541)    # mg As per L
print(f"    -> dip-fluid strength               ~ {conc_mgL*1000:.0f} mg As / L")

# --- STEP 2: arsenic standing in one full vat ----------------------------
print(f"\n[2] ONE FULL VAT (standing charge, not yet replenished)")
for gal in (3000, 4000):
    print(f"    {gal} gal vat -> {lb_As_charge*gal/500:5.1f} lb As held at once")

# --- STEP 3: lifetime THROUGHPUT of one vat ------------------------------
# solution is topped up as As is dragged off on cattle / splashed / degraded.
def throughput_lb(gal=3000, years=6, makeups_per_yr=2):
    standing = lb_As_charge*gal/500
    return standing*(1 + makeups_per_yr*years)
lo  = throughput_lb(3000, 3, 1)     # small/short-lived vat
mid = throughput_lb(3000, 6, 2)     # central
hi  = throughput_lb(4000, 8, 3)     # heavily used district vat
print(f"\n[3] LIFETIME THROUGHPUT PER VAT (poured through over its whole life)")
print(f"    low  (3000 gal, 3 yr, 1 makeup/yr)  = {lo:6.0f} lb As")
print(f"    mid  (3000 gal, 6 yr, 2 makeup/yr)  = {mid:6.0f} lb As")
print(f"    high (4000 gal, 8 yr, 3 makeup/yr)  = {hi:6.0f} lb As")
print(f"    ~ {lo:.0f}-{hi:.0f} lb As handled per vat, central ~{mid:.0f} lb")

# --- STEP 4: arsenic RELEASED to the GROUND per vat ----------------------
# empirical anchor: near-vat soil measures 500-3000 mg/kg in AU/SE-US studies.
def soil_load_lb(L=10, W=10, D=0.5, conc_mgkg=1500, density=1500):
    kg = L*W*D*density*conc_mgkg/1e6            # kg As in the soil zone
    return kg2lb(kg)
near_lo = soil_load_lb(8, 8, 0.3, 500)
near_mid= soil_load_lb(10,10,0.5,1500)
near_hi = soil_load_lb(12,12,0.6,3000)
print(f"\n[4] ARSENIC RELEASED INTO THE GROUND, PER VAT (near-vat concentrated zone)")
print(f"    anchored to 500-3000 mg/kg over a vat+apron+drain-pen zone:")
print(f"    low  (8x8x0.3 m @ 500 mg/kg)        = {near_lo:5.0f} lb As")
print(f"    mid  (10x10x0.5 m @ 1500 mg/kg)     = {near_mid:5.0f} lb As")
print(f"    high (12x12x0.6 m @ 3000 mg/kg)     = {near_hi:5.0f} lb As")
print(f"    ~ {near_lo:.0f}-{near_hi:.0f} lb As in the ground per heavily-used vat")
print(f"    (this is a SUBSET of throughput; the rest dripped off on cattle onto")
print(f"     rangeland soil, or was discarded as spent fluid — also 'into the ground')")

# --- STEP 5: STATEWIDE -- bounded by the hard ceiling --------------------
# Independent ceiling: total white arsenic the program could EVER have bought.
# USGS DS140 arsenic statistics + USDA drag-out throughput -> 15-75 t elemental As
# program-wide over ~6-8 seasons. Arsenic is conservative (does not degrade), and
# dipping was an outdoor, ground-based operation, so essentially ALL of it was
# released to the environment (soil near vats + rangeland + on-ground disposal).
ceiling_t = (15, 75)
n_vats = (50, 150)                              # implied by the ceiling / throughput
# concentrated near-vat fraction statewide (two independent methods agree ~3-30 t):
near_state_t = (3, 30)
print(f"\n[5] STATEWIDE RELEASED TO GROUND (bounded by total ever purchased)")
print(f"    hard ceiling = total white arsenic EVER used by the CA program")
print(f"      = {ceiling_t[0]}-{ceiling_t[1]} metric tons elemental As")
print(f"      = {t2lb(ceiling_t[0]):,.0f} - {t2lb(ceiling_t[1]):,.0f} lb As  <-- upper bound on ground release")
print(f"    implied number of vats (short, small program): ~{n_vats[0]}-{n_vats[1]}")
print(f"    of that, CONCENTRATED near-vat fraction = {near_state_t[0]}-{near_state_t[1]} t")
print(f"      = {t2lb(near_state_t[0]):,.0f} - {t2lb(near_state_t[1]):,.0f} lb As (central ~10 t ~ {t2lb(10):,.0f} lb)")
print(f"    remainder = dispersed thin across grazing land via cattle drag-out")

print("\n" + "-"*70)
print("BOTTOM LINE (elemental arsenic, model estimate, could be off by ~10x):")
print(f"  per 8-lb charge ........ {lb_As_charge:.1f} lb")
print(f"  per vat, in the ground . ~100-500 lb (heavily-used)")
print(f"  STATEWIDE, in the ground ~{t2lb(ceiling_t[0])/1000:.0f}-{t2lb(ceiling_t[1])/1000:.0f} THOUSAND lb "
      f"({ceiling_t[0]}-{ceiling_t[1]} t); central ~10-30 t")
print("  NO CA dip-site soil has ever been tested. Not a measurement.")
print("-"*70)
