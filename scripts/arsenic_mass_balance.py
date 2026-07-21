#!/usr/bin/env python3
"""Arsenic mass-balance MODEL ESTIMATE for California cattle-tick dipping (1907-1915).
NOT a measurement. Every assumption is stated inline and can be varied. See
research/arsenic_model/mass_balance.md for the sourced write-up. No California dip-site
soil has ever been tested; these figures are plausibility bounds, not facts."""
LB = 453.592
As, O = 74.9216, 15.999
As2O3 = 2*As + 3*O
frac = (2*As)/As2O3  # 0.7574 — white arsenic is 75.7% elemental arsenic

def fluid_conc(lb_white=8, gal=500):
    g_As = lb_white*frac*LB
    L = gal*3.78541
    return g_As/L  # mg/L == g/L*1000? -> g_As grams / L => g/L; *1000 for mg/L

def standing(gal, lb_white=8):
    return lb_white*frac*(gal/500)*LB/1000  # kg As standing in a full vat

def throughput(gal=3000, years=6, makeups_per_yr=2, lb_white=8):
    return standing(gal, lb_white)*(1 + makeups_per_yr*years)  # kg As over life

def soil_load(L=10, W=10, D=0.5, conc_mgkg=1500, density=1500):
    return L*W*D*density*conc_mgkg/1e6  # kg As in a soil zone

if __name__ == "__main__":
    print(f"white arsenic = {frac*100:.1f}% elemental As")
    print(f"dip fluid ~ {fluid_conc()*1000:.0f} mg As/L")
    print(f"standing (3000 gal) = {standing(3000):.1f} kg;  (4000 gal) = {standing(4000):.1f} kg")
    print(f"throughput (3000 gal, 6 yr, 2x/yr) = {throughput():.0f} kg As per vat over life")
    print(f"soil load (10x10x0.5 m @ 1500 mg/kg) = {soil_load():.0f} kg As near one vat")
    print(f"8 lb white arsenic = {8*frac*LB:.0f} g As; ~{8*LB/0.2:.0f}-{8*LB/0.07:.0f} adult lethal doses of raw material (As2O3 lethal ~70-200 mg)")
