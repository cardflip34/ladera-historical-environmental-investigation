#!/usr/bin/env python3
"""
Render the Mission 7 grading progression as a chart with its limitations burned into the image.

Per the Mission 7 confidence rules, any rendered artifact must carry BOTH axes visibly:
provenance grade (A+, government imagery) AND statement class (interpreted, not documented).
The caveats are drawn into the PNG itself rather than added in post, so the chart cannot be
screenshotted free of its own caveats.
"""
from __future__ import annotations
import json, os, glob, datetime
from PIL import Image, ImageDraw, ImageFont

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO, "evidence/lhdrs/mission7")
src = sorted(glob.glob(os.path.join(OUT, "grading_progression_landsat_*.json")))
if not src:
    raise SystemExit("no grading progression json found - run lhdrs_m7_grading_landsat.py first")
d = json.load(open(src[-1]))
series = [r for r in d["series"] if "barePct" in r]
if not series:
    raise SystemExit("no usable years in series")

W, H = 1400, 900
NAVY = (22, 35, 58); PAPER = (250, 249, 246); GRID = (222, 226, 232)
BAR = (168, 106, 58); BARLO = (198, 160, 128); ACC = (47, 96, 135); MUT = (110, 116, 126)
FD = "/System/Library/Fonts/Supplemental/"


def F(sz, bold=False):
    for n in (["Arial Bold"] if bold else ["Arial"]):
        p = FD + n + ".ttf"
        if os.path.exists(p):
            return ImageFont.truetype(p, sz)
    return ImageFont.load_default()


im = Image.new("RGB", (W, H), PAPER)
dr = ImageDraw.Draw(im)

dr.text((60, 42), "Ground disturbance at Ladera Ranch, 1997 to 2006", font=F(34, True), fill=NAVY)
dr.text((60, 88), "Share of the study area reading as bare or recently disturbed soil (Landsat NDVI)",
        font=F(19), fill=MUT)

# confidence chips - BOTH axes, always
dr.rounded_rectangle([60, 122, 190, 152], 6, fill=(43, 120, 58))
dr.text((75, 129), "A+  imagery", font=F(15, True), fill=(255, 255, 255))
dr.rounded_rectangle([200, 122, 352, 152], 6, fill=(178, 120, 40))
dr.text((215, 129), "INTERPRETED", font=F(15, True), fill=(255, 255, 255))
dr.text((366, 130), "index threshold, not a documented fact", font=F(15), fill=MUT)

# plot frame
L, R, T, B = 90, W - 60, 200, H - 250
mx = max(r["barePct"] for r in series)
top = max(20, (int(mx / 10) + 1) * 10)
for i in range(0, top + 1, 10):
    y = B - (B - T) * i / top
    dr.line([L, y, R, y], fill=GRID, width=1)
    dr.text((L - 46, y - 9), f"{i}%", font=F(15), fill=MUT)
dr.line([L, T, L, B], fill=NAVY, width=2)
dr.line([L, B, R, B], fill=NAVY, width=2)

n = len(series)
slot = (R - L) / n
for i, r in enumerate(series):
    x = L + i * slot
    h = (B - T) * r["barePct"] / top
    lo = r["validPct"] < 85
    dr.rectangle([x + slot * 0.22, B - h, x + slot * 0.78, B], fill=BARLO if lo else BAR)
    dr.text((x + slot / 2, B - h - 26), f"{r['barePct']:.0f}%", font=F(17, True), fill=NAVY, anchor="ma")
    dr.text((x + slot / 2, B + 12), str(r["year"]), font=F(17, True), fill=NAVY, anchor="ma")
    dr.text((x + slot / 2, B + 34), r["date"][5:], font=F(13), fill=MUT, anchor="ma")
    plat = "L5" if "5" in r["platform"] else ("L7" if "7" in r["platform"] else "?")
    dr.text((x + slot / 2, B + 52), plat, font=F(12), fill=MUT, anchor="ma")

dr.text((L, B + 78), "lighter bar = under 85% valid pixels after cloud masking", font=F(14), fill=MUT)

# limitations, burned in
ly = B + 108
dr.line([60, ly - 14, W - 60, ly - 14], fill=GRID, width=1)
dr.text((60, ly), "Read this with the chart:", font=F(17, True), fill=NAVY)
lim = [
    "30 m pixels: roughly ONE PIXEL PER LOT. Rooftops are not resolvable and no parcel-level claim can be drawn from this.",
    "Bare soil is not only grading. Senescence, fire and fallow ground read the same way. Scenes are chosen in the green season to reduce, not remove, this.",
    "This measures ground disturbance only. It is not a contamination, dust or exposure product, and implies nothing about health.",
]
for i, t in enumerate(lim):
    dr.text((60, ly + 28 + i * 24), "- " + t, font=F(15), fill=(70, 78, 90))

dr.text((60, H - 34), f"Landsat Collection 2 Level-2 surface reflectance, USGS/NASA, via Microsoft Planetary Computer  ·  generated {d['generated']}",
        font=F(13), fill=MUT)

p = os.path.join(OUT, "grading_progression_chart.png")
im.save(p)
print("wrote", p)
for r in series:
    print(f"  {r['year']}  {r['date']}  {r['platform']:<10} bare={r['barePct']:>5.1f}%  valid={r['validPct']:>5.1f}%")
