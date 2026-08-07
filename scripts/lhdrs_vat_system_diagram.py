#!/usr/bin/env python3
"""
Scale plan diagram of a complete 1911-spec dipping station, drawn from the federal instructions.

EVERY DIMENSION IS QUOTED, NOT INVENTED. Source: USDA Bureau of Animal Industry Circular 183
(1911), reproduced in Circular 207 (1912), held locally with full text and sha256.

    Vat            26 ft long at top, 12 ft at bottom; 3 ft wide at top, 1.5 ft at bottom;
                   6.5 ft deep; 1,470 gal at 5 ft 3 in fill
    Chute          30 inches wide, 20 feet long, leading to the vat
    Dripping pen   "about 12 by 15 feet at the head of the exit incline", CONCRETE floor,
                   pitched to a corner where a pipe carries drippings to a barrel sunk in
                   the ground, to be returned to the vat after settling
    Cover          two hinged leaves, each 2 ft 6 in wide, on posts set 3 ft into the ground,
                   doubling as splash boards
    Slide          entry, covered with a sheet of boiler iron fastened to the cement
    Pens           receiving and retaining, "of a size to take care of the animals to be dipped"

THE POINT THE DIAGRAM EXISTS TO MAKE
Read the bill of materials and the station splits cleanly by material:

    CONCRETE  - the vat, and the dripping-pen floor. That is all.
    TIMBER    - chute, pens, dripping-pen posts and rails (6x6 posts, 1x8 rails), cover leaves.
    IRON      - slide sheet, hinges, pipe, barrel hoops.

A century later the timber has rotted and the ironwork has largely gone. THE CONCRETE IS THE ONLY
PART THAT SURVIVES BY DEFAULT. So an isolated concrete channel in brush is exactly what the
surviving fragment of a complete station would look like - and the absence of pens, chute and
fencing is expected rather than evidence against.

This does NOT establish that the observed structure is a vat. It establishes that "only concrete
is left" is the predicted condition, not an anomaly.
"""
from __future__ import annotations
import os
from PIL import Image, ImageDraw, ImageFont

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO, "evidence/lhdrs/field_observations")
os.makedirs(OUT, exist_ok=True)

W, H = 1900, 1150
PPF = 17.5                      # pixels per foot
OX, OY = 120, 260               # origin

FD = "/System/Library/Fonts/Supplemental/"
def F(s, b=False):
    p = FD + ("Arial Bold" if b else "Arial") + ".ttf"
    return ImageFont.truetype(p, s) if os.path.exists(p) else ImageFont.load_default()

PAPER=(252,251,248); INK=(23,30,43); MUT=(110,116,126); RULE=(206,203,196)
CONC=(78,88,104); CONCF=(196,203,214)      # concrete - survives
WOOD=(168,124,64); WOODF=(238,224,202)     # timber - does not
IRON=(150,84,60)
RED=(176,58,42)

im = Image.new("RGB", (W, H), PAPER)
d = ImageDraw.Draw(im)
def ft(v): return v*PPF

d.rectangle([0,0,W,10], fill=RED)
d.text((OX-60, 40), "A complete 1911-specification dipping station, in plan",
       font=F(38, True), fill=INK)
d.text((OX-60, 92), "Every dimension quoted from USDA Bureau of Animal Industry Circular 183 (1911). "
                    "Drawn to scale.", font=F(19), fill=MUT)
d.text((OX-60, 122), "Solid = CONCRETE, the only material that survives a century. "
                     "Hatched = TIMBER and IRON, which do not.", font=F(19, True), fill=INK)

# ---------------- receiving / retaining pens (timber) -----------------------
px, py, pw, ph = OX, OY+ft(2), ft(17), ft(26)
for i in range(0, int(pw), 14):
    d.line([px+i, py, px+i+10, py+ph], fill=WOODF, width=2)
d.rectangle([px, py, px+pw, py+ph], outline=WOOD, width=3)
d.text((px+pw/2, py+ph/2-16), "RECEIVING &", font=F(20, True), fill=WOOD, anchor="ma")
d.text((px+pw/2, py+ph/2+8), "RETAINING PENS", font=F(20, True), fill=WOOD, anchor="ma")
d.text((px+pw/2, py+ph+12), "timber — size to suit the herd", font=F(15), fill=MUT, anchor="ma")

# ---------------- chute (timber) 30 in x 20 ft ------------------------------
cx, cy, cw, ch = px+pw, OY+ft(13), ft(20), ft(2.5)
for i in range(0, int(cw), 12):
    d.line([cx+i, cy, cx+i+8, cy+ch], fill=WOODF, width=2)
d.rectangle([cx, cy, cx+cw, cy+ch], outline=WOOD, width=3)
d.text((cx+cw/2, cy-32), "CHUTE", font=F(20, True), fill=WOOD, anchor="ma")
d.text((cx+cw/2, cy+ch+10), "30 in wide × 20 ft — timber", font=F(15), fill=MUT, anchor="ma")

# ---------------- the vat (CONCRETE) 26 ft x 3 ft ---------------------------
vx, vy, vw, vh = cx+cw, OY+ft(12.7), ft(26), ft(3)
d.rectangle([vx, vy, vx+vw, vy+vh], fill=CONCF, outline=CONC, width=5)
d.text((vx+vw/2, vy-70), "VAT — CONCRETE", font=F(26, True), fill=CONC, anchor="ma")
d.text((vx+vw/2, vy-40), "26 ft at top, 12 ft at bottom · 3 ft wide at top, 1.5 ft at bottom",
       font=F(16), fill=MUT, anchor="ma")
d.text((vx+vw/2, vy-20), "6 ft 6 in deep · 1,470 gal at 5 ft 3 in fill", font=F(16), fill=MUT, anchor="ma")
# entry slide
d.polygon([(vx, vy), (vx+ft(4), vy), (vx+ft(1), vy+vh), (vx, vy+vh)], fill=(226,214,190), outline=IRON)
d.text((vx+ft(2), vy+vh+14), "slide", font=F(14, True), fill=IRON, anchor="ma")
d.text((vx+ft(2), vy+vh+32), "boiler iron", font=F(13), fill=MUT, anchor="ma")
# exit incline with cleats
ex = vx+vw-ft(5)
d.polygon([(ex, vy), (vx+vw, vy), (vx+vw, vy+vh), (ex+ft(2), vy+vh)], fill=(214,220,228), outline=CONC)
for i in range(5):
    d.line([ex+ft(0.7)*i+6, vy+4, ex+ft(0.7)*i+ft(0.5), vy+vh-4], fill=CONC, width=2)
d.text((ex+ft(2.5), vy+vh+14), "exit incline, cleated", font=F(14, True), fill=CONC, anchor="ma")
# cover leaves / splash boards
d.line([vx, vy-ft(2.5), vx+vw, vy-ft(2.5)], fill=WOOD, width=2)
d.line([vx, vy+vh+ft(2.5), vx+vw, vy+vh+ft(2.5)], fill=WOOD, width=2)
d.text((vx+vw/2, vy+vh+ft(2.5)+8), "hinged cover leaves 2 ft 6 in — timber, double as splash boards",
       font=F(14), fill=WOOD, anchor="ma")

# ---------------- dripping pen: CONCRETE FLOOR, timber rails ---------------
dx, dy, dw, dh = vx+vw+ft(1), OY+ft(6), ft(15), ft(12)
d.rectangle([dx, dy, dx+dw, dy+dh], fill=CONCF, outline=CONC, width=5)
for i in range(0, int(dw), 16):
    d.line([dx+i, dy, dx+i+10, dy+dh], fill=(178,188,202), width=1)
d.text((dx+dw/2, dy-60), "DRIPPING PEN", font=F(24, True), fill=CONC, anchor="ma")
d.text((dx+dw/2, dy-32), "12 × 15 ft — CONCRETE FLOOR", font=F(17, True), fill=CONC, anchor="ma")
d.text((dx+dw/2, dy+dh+12), "timber posts (6×6) and rails (1×8) — gone", font=F(15), fill=WOOD, anchor="ma")
# pitch arrows to corner
for i in range(4):
    x0 = dx+ft(2)+i*ft(3)
    d.line([x0, dy+ft(2), dx+ft(1.5), dy+dh-ft(1.5)], fill=(120,132,150), width=1)
d.text((dx+dw/2, dy+dh/2-10), "floor pitched", font=F(15), fill=(90,100,118), anchor="mm")
d.text((dx+dw/2, dy+dh/2+10), "to one corner", font=F(15), fill=(90,100,118), anchor="mm")

# ---------------- barrel sunk in ground ------------------------------------
bx, by = dx+ft(1.5), dy+dh+ft(3.5)
d.ellipse([bx-ft(1.6), by-ft(1.6), bx+ft(1.6), by+ft(1.6)], fill=(226,214,196), outline=IRON, width=3)
d.line([dx+ft(1.5), dy+dh, bx, by-ft(1.6)], fill=IRON, width=3)
d.text((bx, by+ft(2.2)), "BARREL sunk in ground", font=F(15, True), fill=IRON, anchor="ma")
d.text((bx, by+ft(2.2)+20), "drippings settle, then return to the vat", font=F(13), fill=MUT, anchor="ma")

# ---------------- flow arrows ----------------------------------------------
ay = OY+ft(14)
for x0, x1 in ((px+pw-ft(1), cx+ft(1)), (cx+cw-ft(1), vx+ft(1)), (vx+vw-ft(1), dx+ft(1))):
    d.line([x0, ay, x1, ay], fill=(60,70,86), width=3)
    d.polygon([(x1, ay), (x1-12, ay-7), (x1-12, ay+7)], fill=(60,70,86))
d.text((OX+ft(2), ay-ft(9)), "cattle →", font=F(18, True), fill=(60,70,86))

# ---------------- scale bar -------------------------------------------------
sx, sy = OX, H-190
d.line([sx, sy, sx+ft(20), sy], fill=INK, width=4)
for t_ in (0, 10, 20):
    d.line([sx+ft(t_), sy-9, sx+ft(t_), sy+9], fill=INK, width=3)
    d.text((sx+ft(t_), sy+14), f"{t_} ft", font=F(15), fill=INK, anchor="ma")

# ---------------- legend / the point ---------------------------------------
ly = H-150
d.line([OX+ft(22), ly-20, W-90, ly-20], fill=RULE, width=1)
d.rectangle([OX+ft(22), ly, OX+ft(22)+30, ly+20], fill=CONCF, outline=CONC, width=3)
d.text((OX+ft(22)+42, ly-1), "CONCRETE — the vat and the dripping-pen floor. Survives indefinitely.",
       font=F(19, True), fill=INK)
d.rectangle([OX+ft(22), ly+32, OX+ft(22)+30, ly+52], outline=WOOD, width=3)
for i in range(0, 30, 8): d.line([OX+ft(22)+i, ly+32, OX+ft(22)+i+6, ly+52], fill=WOODF, width=2)
d.text((OX+ft(22)+42, ly+31), "TIMBER & IRON — chute, pens, rails, cover, slide. Rots and rusts away.",
       font=F(19, True), fill=INK)
d.text((OX+ft(22), ly+66),
       "A century on, only the concrete is expected to remain. An isolated concrete channel in brush is",
       font=F(18), fill=(70,78,92))
d.text((OX+ft(22), ly+90),
       "what the surviving fragment of a complete station looks like — the missing pens are not evidence against.",
       font=F(18), fill=(70,78,92))

d.text((OX-60, H-40), "Source: USDA Bureau of Animal Industry Circular 183 (1911), repeated in "
                      "Circular 207 (1912). Held locally with full text and SHA-256.",
       font=F(15), fill=MUT)

p = os.path.join(OUT, "dipping_station_plan_1911.png")
im.save(p)
print("wrote", p, f"{os.path.getsize(p)/1024:.0f} KB")
