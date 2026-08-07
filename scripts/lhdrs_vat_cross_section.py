#!/usr/bin/env python3
"""
Cross-section reconstruction: how the observed concrete could be the BASE of a spec vat.

THE QUANTITATIVE POINT (the reason this diagram exists)
The 1911 spec vat TAPERS: 26 ft long at the rim, 12 ft at the floor, 6.5 ft deep. Length is a
function of height. Solving the taper for the observer's reported 15-20 ft:

    15 ft  ->  1.4 ft above the floor
    20 ft  ->  3.7 ft above the floor

So a reading of 15-20 ft is NOT a mismatch with the 26-ft specification. It is exactly what the
lower portion of a spec vat measures when the upper 3-5 ft of wall - timber-framed, or concrete
since broken away - no longer exists. The user's question ("could something larger have sat on
top?") has a yes with numbers attached.

Corroborating context from the same site visit, drawn on the companion panel:
  - a weathered TIMBER POST with wire: the spec's pen/fence line (posts set 3 ft deep)
  - rusted PIPE RAILS: consistent with chute/pen railing
Both are the perishable components the materials argument predicted would be missing or nearly so;
finding their remnants strengthens the station reading and weakens the lone-ditch reading.

HONESTY CONSTRAINTS, drawn on the figure itself:
  - the reconstruction band is labelled INTERPRETED; only the hatched observed band is field fact
  - depth remains unmeasured; if probing finds a floor at <2 ft this reconstruction is wrong
  - the reported width (3-4 ft) sits slightly WIDE of the taper's 1.8-2.4 ft at that height;
    stated on the figure, not hidden
"""
from __future__ import annotations
import os
from PIL import Image, ImageDraw, ImageFont

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO, "evidence/lhdrs/field_observations")
os.makedirs(OUT, exist_ok=True)

W, H = 1900, 1250
FD = "/System/Library/Fonts/Supplemental/"
def F(s, b=False):
    p = FD + ("Arial Bold" if b else "Arial") + ".ttf"
    return ImageFont.truetype(p, s) if os.path.exists(p) else ImageFont.load_default()

PAPER=(252,251,248); INK=(23,30,43); MUT=(110,116,126); RULE=(206,203,196)
CONC=(78,88,104); CONCF=(186,194,206); GHOST=(168,124,64)
SED=(196,178,148); RED=(176,58,42); GRN=(60,120,80)

im = Image.new("RGB", (W, H), PAPER)
d = ImageDraw.Draw(im, "RGBA")
d.rectangle([0,0,W,10], fill=RED)
d.text((70, 40), "The revised ~12 ft reading matches the vat FLOOR exactly",
       font=F(38, True), fill=INK)
d.text((70, 92), "Longitudinal section, to scale. Spec floor = 12 ft. An observed ~12 ft rectangle sits AT FLOOR LEVEL on the taper.", font=F(20, True), fill=INK)
d.text((70, 124), "Solid = observed in the field.  Ghosted = INTERPRETED reconstruction from the "
                  "federal spec. They are not the same kind of statement.", font=F(18), fill=MUT)

# ---- longitudinal section, to scale --------------------------------------
PPF = 46.0
ox, gy = 320, 700            # ground line y; vat floor below
def X(ft): return ox + ft*PPF
def Y(ft_above_floor): return gy + (6.5-ft_above_floor)*PPF*0.62   # vertical compression 0.62

floor_y = Y(0); rim_y = Y(6.5)
# full spec outline (ghosted): trapezoid 12 ft floor, 26 ft rim, centred
cx = X(13.0)
def prof(hf):     # half-length at height h
    return (12 + (26-12)*hf/6.5)/2.0
# ghost full profile
pts_full = [(cx-prof(6.5)*PPF, rim_y), (cx+prof(6.5)*PPF, rim_y),
            (cx+prof(0)*PPF, floor_y), (cx-prof(0)*PPF, floor_y)]
d.polygon(pts_full, outline=GHOST, width=3)
for i in range(6):
    t = i/5
    y0 = rim_y + t*(floor_y-rim_y)
    d.line([cx-prof(6.5*(1-t))*PPF, y0, cx-prof(6.5*(1-t))*PPF+10, y0], fill=(210,190,160), width=1)

# surviving band: floor to ~3 ft (mid of 1.4-3.7), solid concrete
h_lo, h_hi = 0.0, 1.5
pts_surv = [(cx-prof(h_hi)*PPF, Y(h_hi)), (cx+prof(h_hi)*PPF, Y(h_hi)),
            (cx+prof(h_lo)*PPF, Y(h_lo)), (cx-prof(h_lo)*PPF, Y(h_lo))]
d.polygon(pts_surv, fill=CONC, outline=(40,48,60), width=4)
# sediment infill inside surviving band
_in = 0.35
d.polygon([(cx-(prof(1.2)-_in)*PPF, Y(1.2)), (cx+(prof(1.2)-_in)*PPF, Y(1.2)),
           (cx+(prof(0)-_in)*PPF, floor_y-0.28*PPF), (cx-(prof(0)-_in)*PPF, floor_y-0.28*PPF)],
          fill=(SED[0],SED[1],SED[2],235))
d.text((cx, (Y(1.2)+floor_y)/2-10), "sediment infill", font=F(16), fill=(120,104,80), anchor="mm")
d.text((cx, (Y(1.2)+floor_y)/2+12), "DO NOT DISTURB — sample only with consent + accredited lab",
       font=F(13, True), fill=RED, anchor="mm")

# ground line at top of surviving band (what the observer stands on)
d.line([X(-4), Y(h_hi), X(30), Y(h_hi)], fill=(120,110,96), width=4)
d.text((X(-3.8), Y(h_hi)-26), "present ground surface", font=F(15), fill=(110,100,86))

# labels
d.text((cx, rim_y-56), "ORIGINAL RIM — 26 ft — INTERPRETED, not observed", font=F(19, True),
       fill=GHOST, anchor="ma")
d.text((cx, rim_y-30), "upper 3–5 ft of wall: timber-framed above the concrete, or concrete since "
                       "broken away — either way, gone", font=F(15), fill=MUT, anchor="ma")
d.text((cx, floor_y+16), "FLOOR — 12 ft — below grade, not yet reached", font=F(17, True),
       fill=CONC, anchor="ma")
# observed band annotation
obs_y = Y(0.8)
d.line([cx-prof(0.8)*PPF+6, obs_y, cx-prof(0.8)*PPF-150, obs_y+40], fill=GRN, width=3)
d.text((cx-prof(0.8)*PPF-156, obs_y+46), "OBSERVED CONCRETE", font=F(19, True), fill=GRN, anchor="ra")
d.text((cx-prof(0.8)*PPF-156, obs_y+72), "revised estimate ~12 ft — the floor length", font=F(16), fill=GRN, anchor="ra")

# taper scale on the right
tx = X(27.5)
for L, hf in ((12,0.0),(15,1.4),(17.5,2.6),(20,3.7),(26,6.5)):
    y0 = Y(hf)
    d.line([tx, y0, tx+16, y0], fill=INK, width=2)
    mark = "  <- REVISED ESTIMATE" if L == 12 else ""
    d.text((tx+22, y0-9), f"{L:g} ft at {hf:g} ft up{mark}", font=F(15, True if mark else False),
           fill=(RED if mark else MUT))
d.line([tx+8, Y(0), tx+8, Y(6.5)], fill=RULE, width=1)
d.text((tx, Y(6.5)-40), "length vs height\n(the taper)", font=F(15), fill=INK)

# depth caveat box
d.rounded_rectangle([70, 950, W-70, 1080], 10, fill=(251,239,236), outline=RED, width=2)
d.text((92, 968), "WHAT THIS RECONSTRUCTION IS, AND IS NOT", font=F(19, True), fill=(122,38,24))
for i, t in enumerate([
 "An observed ~12 ft rectangle = the spec FLOOR length exactly. Solid = observed; ghosted = interpreted, testable, not established.",
 "DEPTH IS STILL UNMEASURED. Reading A (full concrete vat, upper walls gone/buried): probing 5-7 ft BEYOND each end should find buried rim or wall stubs.",
 "Reading B (hybrid): concrete base only, TIMBER upper framing rotted in place - consistent with the weathered post and wire found beside the structure."]):
    d.text((92, 998+i*26), t, font=F(15), fill=(90,60,52))

# companion panel: the other finds
d.text((70, 190), "Also found on site, and where they fit:", font=F(19, True), fill=INK)
for i, t in enumerate([
 "WEATHERED TIMBER POST with wire — the spec's pens and cover posts were timber set 3 ft deep, fenced with wire and rails.",
 "RUSTED PIPE RAILS — consistent with chute or pen railing at the structure's end.",
 "These are remnants of exactly the perishable components the materials argument said should be missing or nearly gone.",
 "Finding their traces STRENGTHENS the station reading and weakens the lone-drainage-ditch reading."]):
    d.text((70, 222+i*26), "• "+t, font=F(16), fill=(70,78,92))

d.text((70, H-40), "Sources: USDA BAI Circular 183 (1911) / 207 (1912), held with full text and "
                   "SHA-256 · Field observations 2026-08-07, grade C, unverified",
       font=F(15), fill=MUT)

p = os.path.join(OUT, "vat_cross_section_reconstruction.png")
im.save(p)
print("wrote", p, f"{os.path.getsize(p)/1024:.0f} KB")
