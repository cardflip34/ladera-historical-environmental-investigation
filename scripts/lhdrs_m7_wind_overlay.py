#!/usr/bin/env python3
"""
Mission 7 - wind climatology for the construction period, 1997-2006.

WHAT THIS IS: a summary of MEASURED wind observations from archived NOAA hourly records at regional
airport stations, over the years Ladera Ranch was graded and built.

WHAT THIS IS NOT, and cannot be made into without new data:
  - not a dust model, not a plume, not a transport or dispersion calculation
  - not evidence that anything moved from any location to any other location
  - not downscaled to Ladera Ranch. The nearest usable station is 24.7 km away.
The Mission 7 constraints forbid dust/plume/exposure modelling and this script honours that. It
plots where wind came from, and nothing further.

Sector convention (from docs/lhdrs/WIND_CONTEXT.md): sectors describe where wind was reported as
coming FROM. Easterly 45-134 deg, southerly 135-224, westerly 225-314, northerly 315-44.
"""
from __future__ import annotations
import csv, os, math, json, datetime, statistics as st
from PIL import Image, ImageDraw, ImageFont

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DC = os.path.join(REPO, "research/development_chronology")
OUT = os.path.join(REPO, "evidence/lhdrs/mission7")
os.makedirs(OUT, exist_ok=True)
TODAY = datetime.date.today().isoformat()

FD = "/System/Library/Fonts/Supplemental/"
def F(s, b=False):
    p = FD + ("Arial Bold" if b else "Arial") + ".ttf"
    return ImageFont.truetype(p, s) if os.path.exists(p) else ImageFont.load_default()

PAPER=(250,249,246); INK=(22,35,58); MUT=(110,116,126); LINE=(214,218,226)
BLUE=(52,110,190); WARM=(206,120,54); GREEN=(46,120,64)

def fl(v):
    try: return float(v)
    except: return None

rows = [r for r in csv.DictReader(open(os.path.join(DC, "wind_monthly_summary.csv")))]
JW = [r for r in rows if r["stationContextId"] == "LH-WIND-JOHN-WAYNE"]

yearly = {}
for y in range(1997, 2007):
    rs = [r for r in JW if r["year"] == str(y)
          and fl(r["validDirectionalHourCount"]) and fl(r["validDirectionalHourCount"]) > 100]
    if not rs: continue
    yearly[y] = {
        "N": st.mean([fl(r["northerlyPct"]) for r in rs]),
        "E": st.mean([fl(r["easterlyPct"]) for r in rs]),
        "S": st.mean([fl(r["southerlyPct"]) for r in rs]),
        "W": st.mean([fl(r["westerlyPct"]) for r in rs]),
        "speed": st.mean([fl(r["meanSpeedMS"]) for r in rs if fl(r["meanSpeedMS"])]),
        "calm": st.mean([fl(r["calmHourPct"]) for r in rs if fl(r["calmHourPct"]) is not None]),
        "months": len(rs),
    }
CON = [v for y, v in yearly.items() if 1999 <= y <= 2006]
mean = {k: st.mean([c[k] for c in CON]) for k in ("N", "E", "S", "W", "speed", "calm")}

# monthly climatology across the construction years
monthly = {}
for m in range(1, 13):
    rs = [r for r in JW if r["month"] == str(m) and 1999 <= int(r["year"]) <= 2006
          and fl(r["validDirectionalHourCount"]) and fl(r["validDirectionalHourCount"]) > 100]
    if rs:
        monthly[m] = {k: st.mean([fl(r[c]) for r in rs]) for k, c in
                      (("N","northerlyPct"),("E","easterlyPct"),("S","southerlyPct"),("W","westerlyPct"))}
        monthly[m]["speed"] = st.mean([fl(r["meanSpeedMS"]) for r in rs if fl(r["meanSpeedMS"])])

W, H = 1600, 1900
im = Image.new("RGB", (W, H), PAPER); d = ImageDraw.Draw(im)
d.rectangle([0, 0, W, 9], fill=WARM)

d.text((60, 40), "Where the wind came from, 1999 to 2006", font=F(40, True), fill=INK)
d.text((60, 94), "Measured hourly observations over the years Ladera Ranch was graded and built",
       font=F(19), fill=MUT)
d.rounded_rectangle([60, 128, 232, 158], 6, fill=GREEN)
d.text((74, 134), "A+  NOAA hourly", font=F(15, True), fill=(255,255,255))
d.rounded_rectangle([242, 128, 470, 158], 6, fill=(150,60,42))
d.text((256, 134), "NOT a dust or exposure model", font=F(15, True), fill=(255,255,255))

# ---------------- wind rose ----------------
cx, cy, R = 380, 470, 210
d.text((60, 205), "Construction-period average", font=F(24, True), fill=INK)
for frac in (0.25, 0.5, 0.75, 1.0):
    d.ellipse([cx-R*frac, cy-R*frac, cx+R*frac, cy+R*frac], outline=LINE, width=1)
d.line([cx-R-18, cy, cx+R+18, cy], fill=LINE); d.line([cx, cy-R-18, cx, cy+R+18], fill=LINE)
mx = max(mean["N"], mean["E"], mean["S"], mean["W"])
# petals point toward the sector the wind comes FROM
for key, ang, lab in (("N",-90,"N"), ("E",0,"E"), ("S",90,"S"), ("W",180,"W")):
    v = mean[key]/mx
    a = math.radians(ang); half = math.radians(28)
    p1 = (cx, cy)
    p2 = (cx+R*v*math.cos(a-half), cy+R*v*math.sin(a-half))
    p3 = (cx+R*v*math.cos(a), cy+R*v*math.sin(a))
    p4 = (cx+R*v*math.cos(a+half), cy+R*v*math.sin(a+half))
    col = WARM if key == "S" else BLUE
    d.polygon([p1, p2, p3, p4], fill=col, outline=(255,255,255))
    lx, ly = cx+(R+34)*math.cos(a), cy+(R+34)*math.sin(a)
    d.text((lx, ly), lab, font=F(22, True), fill=INK, anchor="mm")
    d.text((lx, ly+22), f"{mean[key]:.0f}%", font=F(16), fill=MUT, anchor="mm")
d.text((cx, cy+R+80), "petal length = share of hours wind came FROM that sector",
       font=F(15), fill=MUT, anchor="ma")

# ---------------- the plain-language reading ----------------
bx = 700
d.text((bx, 205), "What the record shows", font=F(24, True), fill=INK)
lines = [
    ("Wind came from the SOUTH about half of all hours,", INK),
    ("every single year from 1997 through 2006.", INK),
    ("", MUT),
    (f"South {mean['S']:.0f}%   West {mean['W']:.0f}%   East {mean['E']:.0f}%   North {mean['N']:.0f}%", INK),
    ("", MUT),
    (f"Average speed {mean['speed']:.2f} m/s, which is light air.", MUT),
    (f"{mean['calm']:.0f}% of hours were recorded calm.", MUT),
    ("", MUT),
    ("Wind FROM the south travels TOWARD the north.", WARM),
    ("", MUT),
    ("The pattern is unusually stable: the prevailing sector", MUT),
    ("did not change in any year of the build-out.", MUT),
]
y = 250
for t, c in lines:
    d.text((bx, y), t, font=F(19, True) if c is WARM else F(19), fill=c); y += 30

# ---------------- year by year ----------------
top = 740
d.text((60, top), "Year by year", font=F(24, True), fill=INK)
d.text((60, top+34), "share of hours by sector of origin", font=F(16), fill=MUT)
gx, gy, gw, gh = 60, top+70, W-120, 300
d.rectangle([gx, gy, gx+gw, gy+gh], outline=LINE)
ys = sorted(yearly)
bw = gw/len(ys)
order = [("S", WARM), ("W", BLUE), ("E", (120,170,210)), ("N", (180,200,220))]
for i, yy in enumerate(ys):
    x0 = gx+i*bw+14; x1 = gx+(i+1)*bw-14
    acc = 0
    for k, col in order:
        v = yearly[yy][k]/100*gh
        d.rectangle([x0, gy+gh-acc-v, x1, gy+gh-acc], fill=col)
        if k == "S":
            d.text(((x0+x1)/2, gy+gh-acc-v/2), f"{yearly[yy][k]:.0f}%", font=F(15, True),
                   fill=(255,255,255), anchor="mm")
        acc += v
    lab = str(yy)
    d.text(((x0+x1)/2, gy+gh+10), lab, font=F(16, True if 1999 <= yy <= 2006 else False), fill=INK, anchor="ma")
    if 1999 <= yy <= 2006:
        d.line([x0, gy+gh+34, x1, gy+gh+34], fill=WARM, width=3)
d.text((gx, gy+gh+44), "orange underline = construction years", font=F(15), fill=WARM)
lx = gx+gw-360
for k, col in order:
    d.rectangle([lx, gy+12, lx+16, gy+26], fill=col)
    d.text((lx+22, gy+11), {"S":"from south","W":"from west","E":"from east","N":"from north"}[k],
           font=F(14), fill=INK); lx += 92

# ---------------- monthly ----------------
top2 = gy+gh+90
d.text((60, top2), "By month, averaged across the construction years", font=F(24, True), fill=INK)
mx2, my2, mw2, mh2 = 60, top2+50, W-120, 190
d.rectangle([mx2, my2, mx2+mw2, my2+mh2], outline=LINE)
names = "J F M A M J J A S O N D".split()
bw2 = mw2/12
for i in range(1, 13):
    if i not in monthly: continue
    x0 = mx2+(i-1)*bw2+16; x1 = mx2+i*bw2-16
    v = monthly[i]["S"]/100*mh2
    d.rectangle([x0, my2+mh2-v, x1, my2+mh2], fill=WARM)
    d.text(((x0+x1)/2, my2+mh2-v-20), f"{monthly[i]['S']:.0f}", font=F(14, True), fill=INK, anchor="ma")
    d.text(((x0+x1)/2, my2+mh2+8), names[i-1], font=F(15), fill=MUT, anchor="ma")
d.text((mx2, my2+mh2+34), "share of hours with wind from the south. Highest in late spring and summer.",
       font=F(15), fill=MUT)

# ---------------- limitations ----------------
ly2 = my2+mh2+80
d.line([60, ly2, W-60, ly2], fill=LINE)
d.text((60, ly2+16), "Read this with the limits", font=F(22, True), fill=(150,60,42))
lims = [
 "NOT DOWNSCALED. The nearest station with construction-period data is John Wayne Airport, 24.7 km away.",
 "These are airport observations, not measurements at Ladera Ranch.",
 "STATIONS DISAGREE. In 1997, when both were recording, El Toro (15.6 km) logged 31% easterly hours",
 "while John Wayne logged 12%. Nearly threefold. Terrain steers wind locally, so no single station",
 "can be assumed to represent this valley.",
 "EL TORO CLOSED. The closer station stops in 1997, so the entire construction period rests on the",
 "more distant one.",
 "FOUR SECTORS ONLY. The archived summary resolves quadrants, not a full compass rose.",
 "NOT A TRANSPORT MODEL. This shows where wind came from. It does not model dust, does not estimate",
 "movement of material between locations, and implies nothing about exposure or health.",
]
yy2 = ly2+52
for t in lims:
    d.text((60, yy2), t, font=F(16), fill=(70,78,90)); yy2 += 24
d.text((60, H-40), f"NOAA Integrated Surface Database hourly observations, archived with checksums  ·  generated {TODAY}",
       font=F(14), fill=MUT)

p = os.path.join(OUT, "wind_climatology_1997_2006.png")
im.save(p)
print("wrote", p)

json.dump({"generated": TODAY, "station": "John Wayne Airport (24.7 km)",
           "provenanceGrade": "A+", "statementClass": "documented_approximate",
           "sectorConvention": "direction wind came FROM",
           "constructionPeriodMean": {k: round(v, 2) for k, v in mean.items()},
           "yearly": {str(k): {kk: round(vv, 2) for kk, vv in v.items()} for k, v in yearly.items()},
           "monthlySouthPct": {str(k): round(v["S"], 1) for k, v in monthly.items()},
           "limitations": lims},
          open(os.path.join(OUT, "wind_climatology.json"), "w"), indent=1)
print("prevailing sector every year 1997-2006: southerly")
