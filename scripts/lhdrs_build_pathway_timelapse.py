#!/usr/bin/env python3
"""
Construction-era timelapse with candidate source zones and a conceptual pathway diagram.

WHAT THIS SHOWS
  - the real Landsat record of grading and build-out, 1997-2006, 102 cloud-free months
  - the ranked SAMPLING TARGET zones (where cattle concentrated) carried across every frame
  - the drainage line, which ran through the site during every month of grading
  - a CONCEPTUAL panel of the physical pathways by which soil-bound material moves during
    earthworks

TWO THINGS THIS DELIBERATELY DOES NOT DO, and the video says so on its face:

1. IT DOES NOT MARK VAT LOCATIONS. A systematic search of the 1929/1938/1947 aerials found no vat
   in this frame. Drawing a vat somewhere plausible would be fabrication. What IS drawn are the
   candidate source zones - 1968 stock-water points, which are documented, and which are where
   cattle demonstrably concentrated.

2. IT DOES NOT ANIMATE A PLUME OVER THE MAP. A plume drawn on real terrain reads as a measurement
   of where material went. No such measurement exists. The pathway content is therefore a separate
   SCHEMATIC panel - a mechanism diagram, drawn abstractly, never registered to real ground.

The distinction matters: the mechanisms are textbook and real (wind erosion of exposed soil,
stormwater transport, hydraulic redistribution by earthmoving). What is unknown is whether there
was anything at these locations to move. That is what sampling would answer.
"""
from __future__ import annotations
import json, os, glob, math, datetime
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import imageio.v2 as imageio
Image.MAX_IMAGE_PIXELS = None

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
M7 = os.path.join(REPO, "evidence/lhdrs/mission7")
FR = os.path.join(M7, "timelapse_frames")
TODAY = datetime.date.today().isoformat()
AOI = (-117.670, 33.524, -117.616, 33.575)
LAND_BBOX = (-117.674, 33.524, -117.609, 33.578)

SIZE, MAP, TOP = 1080, 720, 150
MEND = TOP + MAP
FPS = 7
FD = "/System/Library/Fonts/Supplemental/"
def F(s, b=False):
    p = FD + ("Arial Bold" if b else "Arial") + ".ttf"
    return ImageFont.truetype(p, s) if os.path.exists(p) else ImageFont.load_default()

NAVY=(14,19,29); WHITE=(255,255,255); MUT=(150,157,170); ACC=(226,150,60)
HOT=(226,74,58); WARM=(236,158,52); STREAM=(74,150,228); RED=(196,58,44)

man = json.load(open(os.path.join(M7, "timelapse_manifest.json")))
seq = man["videoSequence"]
tgts = json.load(open(os.path.join(M7, "sampling_targets_reasoned.json")))
CH = {}
for f in json.load(open(os.path.join(M7, "oc_flood_channels_aoi.geojson")))["features"]:
    nm = ((f.get("properties") or {}).get("FACILITYNAME") or "").strip().upper()
    g = f.get("geometry")
    if not nm or not g: continue
    parts = [g["coordinates"]] if g["type"] == "LineString" else g["coordinates"]
    CH.setdefault(nm, []).extend(parts)

OX = (SIZE-MAP)//2
def xy(lon, lat):
    return (OX + (lon-AOI[0])/(AOI[2]-AOI[0])*MAP, TOP + (AOI[3]-lat)/(AOI[3]-AOI[1])*MAP)

def crop(img):
    w, h = img.size
    b = LAND_BBOX
    x0 = (AOI[0]-b[0])/(b[2]-b[0])*w; x1 = (AOI[2]-b[0])/(b[2]-b[0])*w
    y0 = (b[3]-AOI[3])/(b[3]-b[1])*h; y1 = (b[3]-AOI[1])/(b[3]-b[1])*h
    return img.crop((int(x0), int(y0), int(x1), int(y1))).resize((MAP, MAP), Image.LANCZOS)

def clipped(d, seg, col, w):
    pts = [xy(c[0], c[1]) for c in seg]
    for a, b in zip(pts, pts[1:]):
        if all(OX <= p[0] <= OX+MAP and TOP <= p[1] <= MEND for p in (a, b)):
            d.line([a, b], fill=col, width=w)

def hold(im, sec): return [np.asarray(im)]*int(FPS*sec)

def card(lines, sub=None, sec=4, rule=RED):
    im = Image.new("RGB", (SIZE, SIZE), NAVY); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, SIZE, 8], fill=rule)
    y = 300
    for t, s, b in lines:
        d.text((SIZE//2, y), t, font=F(s, b), fill=WHITE, anchor="ma"); y += int(s*1.45)
    if sub:
        y += 26
        for t in sub:
            d.text((SIZE//2, y), t, font=F(18), fill=MUT, anchor="ma"); y += 30
    return hold(im, sec)

frames = []

# ---------------- opening ----------------
frames += card([("Ladera Ranch", 60, True), ("1997 to 2006", 34, False)],
    ["The grading and build-out years, month by month",
     "102 cloud-free Landsat observations",
     "",
     "Candidate source zones and the drainage, carried on every frame"], sec=5)

frames += card([("Before anything else", 34, True)],
    ["A systematic search of the 1929, 1938 and 1947 aerials",
     "found NO dipping vat inside this frame.",
     "",
     "Nothing in this video marks a vat.",
     "What is marked are documented 1968 stock-water points -",
     "where cattle demonstrably gathered every day.",
     "",
     "These are targets for testing. Not findings."], sec=7)

# ---------------- the timelapse ----------------
T0, T1 = 1997.0, 2007.0
def dec(s): return int(s[:4]) + (int(s[5:7])-0.5)/12.0

for dt in seq:
    g = glob.glob(os.path.join(FR, f"*_{dt}.png"))
    if not g: continue
    src = Image.open(g[0]).convert("RGB")
    src = src.crop((0, 0, src.width, src.height-34))
    im = Image.new("RGB", (SIZE, SIZE), NAVY)
    im.paste(crop(src), (OX, TOP))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, SIZE, 8], fill=RED)
    d.text((36, 30), "Grading and build-out", font=F(34, True), fill=WHITE)
    d.text((36, 74), "Landsat true colour, 30 m  ·  candidate source zones carried throughout",
           font=F(16), fill=MUT)
    f = F(42, True); bb = d.textbbox((0, 0), dt[:7], font=f)
    w0, h0 = bb[2]-bb[0], bb[3]-bb[1]
    d.rounded_rectangle([SIZE-40-w0-24, 24, SIZE-30, 24+h0+20], 7, fill=(38, 30, 18), outline=ACC, width=2)
    d.text((SIZE-42, 34), dt[:7], font=f, fill=ACC, anchor="ra")

    for nm, col, wd in (("TRABUCO CREEK CHANNEL", (96,150,200), 2),
                        ("CANADA CHIQUITA", (96,150,200), 2),
                        ("ACJACHEMA STORM DRAIN", (86,160,220), 3),
                        ("HORNO CREEK CHANNEL", STREAM, 4)):
        for s_ in CH.get(nm, []): clipped(d, s_, col, wd)

    for t in tgts:
        x, y = xy(t["lon"], t["lat"])
        if not (OX <= x <= OX+MAP and TOP <= y <= MEND): continue
        col = HOT if t["p"] == 1 else WARM
        r = 9 if t["p"] == 1 else 7
        d.ellipse([x-r, y-r, x+r, y+r], outline=col, width=3)

    # timeline
    bx0, bx1, by = 36, SIZE-36, MEND+26
    d.line([bx0, by, bx1, by], fill=(56,64,80), width=3)
    for yr in range(1997, 2008):
        x = bx0+(bx1-bx0)*(yr-T0)/(T1-T0)
        d.line([x, by-6, x, by+6], fill=(88,98,116), width=2)
        if yr % 2 == 1: d.text((x, by+11), str(yr), font=F(13), fill=MUT, anchor="ma")
    px = bx0+(bx1-bx0)*(dec(dt)-T0)/(T1-T0)
    d.ellipse([px-7, by-7, px+7, by+7], fill=ACC)

    d.text((36, MEND+62), "○  candidate source zones — 1968 stock-water points, NOT vats",
           font=F(15), fill=HOT)
    d.text((36, MEND+84), "—  Horno Creek / Acjachema Storm Drain — ran through the site throughout",
           font=F(15), fill=STREAM)
    for i, t in enumerate([
        "30 m pixels: grading extent and roads are visible; individual pads are not.",
        "Ground-surface condition only. Not a contamination, dust or exposure product."]):
        d.text((36, MEND+118+i*24), t, font=F(15), fill=(184,190,202))
    d.text((SIZE-36, SIZE-34), "Landsat 5/7 · USGS/NASA · A+", font=F(13), fill=MUT, anchor="ra")
    frames.append(np.asarray(im))

frames += card([("Ground disturbance peaked", 32, False), ("in 2002", 56, True)],
    ["52.8% of the in-CDP area showed bare, graded ground",
     "The drainage ran through it in every one of those months"], sec=5)

# ---------------- conceptual pathway schematic ----------------
# Drawn ABSTRACTLY - never over real terrain - because no transport measurement exists.
def schematic(step, sec=5):
    im = Image.new("RGB", (SIZE, SIZE), NAVY); d = ImageDraw.Draw(im, "RGBA")
    d.rectangle([0, 0, SIZE, 8], fill=(150,60,42))
    d.text((SIZE//2, 34), "How soil-bound material moves during earthworks",
           font=F(30, True), fill=WHITE, anchor="ma")
    d.text((SIZE//2, 76), "CONCEPTUAL SCHEMATIC — not a measurement, not registered to real ground",
           font=F(17), fill=(232,150,130), anchor="ma")

    gy = 560                       # ground line - lowered so the text block above never collides
    d.line([80, gy, SIZE-80, gy], fill=(120,110,96), width=5)
    d.rectangle([80, gy, SIZE-80, gy+130], fill=(92,80,66,255))
    d.text((SIZE-96, gy+104), "soil column", font=F(14), fill=(190,182,170), anchor="ra")

    # the buried source, drawn as an unknown
    sx = 300
    d.rectangle([sx-58, gy+34, sx+58, gy+82], fill=(150,60,60,190), outline=(226,120,110), width=2)
    d.text((sx, gy+46), "?", font=F(30, True), fill=WHITE, anchor="ma")
    d.text((sx, gy+96), "hypothetical historic residue — presence UNKNOWN",
           font=F(14), fill=(226,150,140), anchor="ma")

    if step >= 1:
        d.text((110, 126), "1 · EARTHMOVING", font=F(22, True), fill=ACC)
        d.text((110, 158), "Grading cuts, mixes and relocates the soil column. Material at depth can be",
               font=F(16), fill=(200,206,216))
        d.text((110, 180), "brought to surface; surface material can be buried. Depth order is not preserved.",
               font=F(16), fill=(200,206,216))
        for x0 in range(sx-40, sx+200, 60):
            d.line([x0, gy+24, x0+46, gy-8], fill=ACC, width=3)
            d.polygon([(x0+52, gy-12), (x0+38, gy-6), (x0+44, gy+4)], fill=ACC)

    if step >= 2:
        d.text((110, 226), "2 · WIND — exposed surfaces", font=F(22, True), fill=(220,196,140))
        d.text((110, 258), "Bare graded ground is erodible. Fine particles are entrained and redeposited.",
               font=F(16), fill=(200,206,216))
        d.text((110, 280), "Prevailing wind here was FROM THE SOUTH in every construction year.",
               font=F(16), fill=(220,196,140))
        # arrows live in their own band, clear of all text
        for i in range(8):
            x0 = 150+i*90; y0 = 470-i*4
            d.line([x0, y0, x0+52, y0-12], fill=(220,196,140,210), width=3)
        d.polygon([(910, 440), (886, 432), (890, 450)], fill=(220,196,140))

    if step >= 3:
        d.text((110, 326), "3 · WATER — stormwater and the drainage", font=F(22, True), fill=STREAM)
        d.text((110, 358), "Rain mobilises fine sediment from disturbed ground into the channel, which",
               font=F(16), fill=(200,206,216))
        d.text((110, 380), "then transports and DEPOSITS it wherever gradient falls — the sampling targets.",
               font=F(16), fill=(200,206,216))
        for i in range(9):
            x0 = 200+i*72
            d.line([x0, gy-46, x0+16, gy-8], fill=(STREAM[0],STREAM[1],STREAM[2],210), width=3)
        d.ellipse([SIZE-250, gy-18, SIZE-120, gy+18], outline=STREAM, width=3)
        d.text((SIZE-185, gy-11), "deposition zone", font=F(14, True), fill=STREAM, anchor="ma")

    if step >= 4:
        d.rounded_rectangle([80, SIZE-186, SIZE-80, SIZE-36], 8,
                            fill=(42,26,22,255), outline=(196,74,58), width=2)
        d.text((104, SIZE-168), "WHAT THIS SCHEMATIC DOES NOT SAY", font=F(19, True), fill=(240,150,132))
        for i, t in enumerate([
            "It does not say arsenic is present in this soil. Nothing has been sampled.",
            "It does not say anything moved. No transport has been measured or modelled.",
            "It does not say anyone was exposed. These are textbook mechanisms only,",
            "shown to explain why WHERE you sample matters as much as WHETHER you sample."]):
            d.text((104, SIZE-138+i*25), t, font=F(15), fill=(214,206,204))
    return hold(im, sec)

for st in (1, 2, 3, 4):
    frames += schematic(st, sec=4.5 if st < 4 else 8)

# ---------------- closing ----------------
frames += card([("The question this video frames", 30, True)],
    ["Grading redistributes soil. It does not destroy arsenic —",
     "arsenic is an element and has no half-life.",
     "",
     "IF a historic residue existed here, earthworks would have moved it.",
     "Whether one existed is unknown and untested.",
     "",
     "23 ranked sampling targets are published with this project.",
     "A negative result is a real and publishable result."], sec=9)

print(f"composed {len(frames)} frames ({len(frames)/FPS:.0f}s)")
out = os.path.join(M7, "ladera_pathway_timelapse_1997_2006.mp4")
imageio.mimsave(out, frames, fps=FPS, quality=9, macro_block_size=1)
print("wrote", out, f"{os.path.getsize(out)/1e6:.1f} MB")

json.dump({"generated": TODAY, "frames": len(frames), "seconds": round(len(frames)/FPS, 1),
           "statementClass": "documented_imagery_with_conceptual_schematic",
           "imagery": "Landsat 5/7 Collection 2 Level-2, 102 cloud-free months 1997-2006, A+",
           "overlays": {"candidateSourceZones": "1968 USGS surface-water points (A1) - NOT vats",
                        "drainage": "OC Flood_Channels as-built (A+)"},
           "schematicIsConceptual": True,
           "notEstablished": ["presence of arsenic anywhere in the study area",
                              "existence of a vat within the study area",
                              "any transport of any material",
                              "any human exposure", "any health effect"],
           "noVatMarked": "A systematic search of the 1929/1938/1947 aerials found none; marking a "
                          "guess would be fabrication."},
          open(os.path.join(M7, "pathway_timelapse.provenance.json"), "w"), indent=1)
