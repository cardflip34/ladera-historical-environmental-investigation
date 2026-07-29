#!/usr/bin/env python3
"""
Mission 7 - full historical video: 1929 aerials through 2006 Landsat, one common crop.

CANONICAL AOI  [-117.670, 33.524, -117.616, 33.575]  (~5.0 x 5.7 km)
Intersection of all three source extents, so every frame is the identical ground area:
  OC Survey historical aerials  bbox -117.680,33.520,-117.616,33.575  (server-rectified)
  OC 1995/1998 georeferenced    bbox -117.670,33.520,-117.610,33.580
  Landsat square AOI            bbox -117.674,33.524,-117.609,33.578

ANNOTATION DISCIPLINE - this is the part that matters.
The prior imagery investigation (research/historical_imagery/README.md) concluded, after examining
frames down to 1.15 ft/px: the footprint was OPEN RANGELAND in every pre-1950 frame, and NO dip vat,
corral, pen or chute was resolvable inside Zone A. It states "nothing speculative has been plotted."

This video honours that. It labels ONLY what the source record documents:
  - grazing / rangeland land use and the features actually reported (stock trails, fence lines,
    wheel ruts, oak-sycamore riparian corridor, cultivated valley floor)
  - the 41 surface-water bodies mapped by the 1968 USGS field survey (real coordinates)
  - the four schools, at their real coordinates, in the modern era only
  - the absence of a vat, stated as the finding it is
NO invented ranch nodes, NO speculative vat markers, NO drawn structures.
"""
from __future__ import annotations
import json, os, glob, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import imageio.v2 as imageio
Image.MAX_IMAGE_PIXELS = None

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO, "evidence/lhdrs/mission7")
AER = os.path.join(REPO, "research/historical_imagery/oc_aerials")
FR = os.path.join(OUT, "timelapse_frames")

AOI = (-117.670, 33.524, -117.616, 33.575)
HIST_BBOX = (-117.680, 33.520, -117.616, 33.575)
TIF_BBOX = (-117.670, 33.520, -117.610, 33.580)
LAND_BBOX = (-117.674, 33.524, -117.609, 33.578)

SIZE, MAP, TOPBAR = 1080, 748, 96
MAPEND = TOPBAR + MAP
FD = "/System/Library/Fonts/Supplemental/"
def F(s, b=False):
    p = FD + ("Arial Bold" if b else "Arial") + ".ttf"
    return ImageFont.truetype(p, s) if os.path.exists(p) else ImageFont.load_default()

NAVY=(16,22,34); MUT=(150,156,168); ACC=(214,138,70); CYAN=(90,200,225); WHITE=(255,255,255)
SCHOOL=(255,205,80); NODE=(255,120,120)
# README section 9: "the single 1948 ranch structure at 33.55505, -117.65492, labelled a
# ranch-activity node and explicitly *not* a dip vat". Plotted exactly on those terms.
NODE_PT = (-117.65492, 33.55505)

water = json.load(open(os.path.join(REPO, "research/historical_imagery/topo1968_water.json")))
schools = json.load(open(os.path.join(REPO, "data/development/schools.geojson")))["features"]
# LRES and LRMS share a campus/coords - merge label so markers do not stack
SCH = []
seen = {}
for s in schools:
    c = tuple(s["geometry"]["coordinates"]); n = s["properties"]["name"]
    short = n.replace(" Elementary School", " ES").replace(" Middle School", " MS")
    if c in seen: seen[c]["label"] += " / " + short.split()[-1]
    else:
        seen[c] = {"lon": c[0], "lat": c[1], "label": short}; SCH.append(seen[c])


def crop_to_aoi(img, bbox):
    """Crop a north-up image with known geographic bbox down to the canonical AOI."""
    w, h = img.size
    x0 = (AOI[0]-bbox[0])/(bbox[2]-bbox[0])*w
    x1 = (AOI[2]-bbox[0])/(bbox[2]-bbox[0])*w
    y0 = (bbox[3]-AOI[3])/(bbox[3]-bbox[1])*h
    y1 = (bbox[3]-AOI[1])/(bbox[3]-bbox[1])*h
    return img.crop((int(x0), int(y0), int(x1), int(y1))).resize((MAP, MAP), Image.LANCZOS)


def xy(lon, lat):
    return (int((lon-AOI[0])/(AOI[2]-AOI[0])*MAP), int((AOI[3]-lat)/(AOI[3]-AOI[1])*MAP))


def base(panel, title, sub, era):
    im = Image.new("RGB", (SIZE, SIZE), NAVY)
    im.paste(panel, ((SIZE-MAP)//2, TOPBAR))
    d = ImageDraw.Draw(im)
    d.text((36, 20), title, font=F(38, True), fill=WHITE)
    d.text((36, 66), sub, font=F(16), fill=MUT)
    d.text((SIZE-36, 28), era, font=F(20, True), fill=ACC, anchor="ra")
    return im, d


def draw_water(d, note=True):
    n = 0
    for w in water:
        x, y = xy(w["lon"], w["lat"])
        if 0 <= x < MAP and 0 <= y < MAP:
            r = max(4, min(16, int(math.sqrt(w["area_m2"])/22)))
            d.ellipse([(SIZE-MAP)//2+x-r, TOPBAR+y-r, (SIZE-MAP)//2+x+r, TOPBAR+y+r],
                      outline=CYAN, width=2)
            n += 1
    if note:
        d.text((36, MAPEND+12), f"○  {n} surface-water bodies mapped by the 1968 USGS field survey",
               font=F(15), fill=CYAN)
    return n


def draw_schools(d):
    for s in SCH:
        x, y = xy(s["lon"], s["lat"])
        if not (0 <= x < MAP and 0 <= y < MAP):
            continue
        px, py = (SIZE-MAP)//2+x, TOPBAR+y
        d.ellipse([px-9, py-9, px+9, py+9], outline=SCHOOL, width=3)
        d.line([px, py-16, px, py-30], fill=SCHOOL, width=2)
        t = s["label"]
        w = d.textlength(t, font=F(15, True))
        bx = min(max(px-w/2-7, 4), SIZE-w-12)
        d.rectangle([bx, py-52, bx+w+14, py-30], fill=(28, 34, 48))
        d.text((bx+7, py-49), t, font=F(15, True), fill=SCHOOL)


def draw_node(d, note=True):
    x, y = xy(*NODE_PT)
    if not (0 <= x < MAP and 0 <= y < MAP): return
    px, py = (SIZE-MAP)//2+x, TOPBAR+y
    d.ellipse([px-16, py-16, px+16, py+16], outline=NODE, width=3)
    d.line([px-24, py, px-18, py], fill=NODE, width=3)
    d.line([px+18, py, px+24, py], fill=NODE, width=3)
    d.line([px, py-24, px, py-18], fill=NODE, width=3)
    d.line([px, py+18, px, py+24], fill=NODE, width=3)
    if note:
        d.text((36, MAPEND+34), "◎  1948 ranch-activity node - explicitly NOT identified as a dip vat",
               font=F(15), fill=NODE)


def caption(d, lines, color=(190,196,208)):
    y = MAPEND+62
    for t in lines:
        d.text((36, y), t, font=F(16), fill=color); y += 24


def foot(d, src):
    d.text((36, SIZE-30), src, font=F(13), fill=(120,128,142))
    d.text((SIZE-36, SIZE-30), "A+  documented imagery", font=F(13), fill=(120,128,142), anchor="ra")


FPS = 7
def hold(im, sec): return [np.asarray(im)]*int(FPS*sec)

frames = []

# ---------------- title ----------------
im = Image.new("RGB", (SIZE, SIZE), NAVY); d = ImageDraw.Draw(im)
d.text((SIZE//2, 380), "Ladera Ranch", font=F(66, True), fill=WHITE, anchor="ma")
d.text((SIZE//2, 470), "1929 to 2006", font=F(36), fill=ACC, anchor="ma")
for i, t in enumerate(["Aerial photography and satellite record of one square of ground",
                       "Identical extent and georeferencing in every frame",
                       "~5.0 x 5.7 km"]):
    d.text((SIZE//2, 560+i*30), t, font=F(17), fill=MUT, anchor="ma")
frames += hold(im, 3)

# ---------------- historical aerials ----------------
HIST = [
 ("1929.jpg", "1929", "Aerial photograph",
  ["Open rangeland. Grazed hills, riparian corridor picked out by tree clusters,",
   "unimproved dirt roads. No structures resolvable inside the future built area.",
   "Twelve years after compulsory arsenical cattle dipping ended."]),
 ("1937.jpg", "1937-38", "Aerial photograph, 600-scale county series - 1.15 ft/px",
  ["The sharpest frame in the set. Individual oaks, FENCE LINES, WHEEL RUTS and the",
   "braided creek channel are legible. FIELD BOUNDARIES and STOCK TRAILS visible on",
   "the eastern grasslands. No corral, pen, chute or vat resolvable anywhere."]),
 ("1946b.jpg", "1946-47", "Aerial photograph, 1200-scale county series",
  ["Unchanged. Still rangeland, still grazed.",
   "The north-west quarter falls outside this frame's coverage.",
   "Part of the historic O'Neill Ranch / Rancho Mission Viejo."]),
]
for fn, yr, srcdesc, cap in HIST:
    p = os.path.join(AER, fn)
    if not os.path.exists(p): continue
    panel = crop_to_aoi(Image.open(p).convert("RGB"), HIST_BBOX)
    im, d = base(panel, "Ladera Ranch", srcdesc, yr)
    draw_water(d)
    draw_node(d)
    caption(d, cap)
    foot(d, "OC Survey / OCGIS Historic_Imagery_v2, server-rectified")
    frames += hold(im, 3)

# ---------------- the finding card ----------------
im = Image.new("RGB", (SIZE, SIZE), NAVY); d = ImageDraw.Draw(im)
d.text((SIZE//2, 300), "What the aerials show", font=F(40, True), fill=WHITE, anchor="ma")
for i, t in enumerate([
    "At 1.15 ft/px a 2 m dip vat would be about 6 pixels across.",
    "A corral would be unmistakable.",
    "",
    "None was found inside the footprint in any pre-1950 frame.",
    "",
    "That is weak evidence against a large surviving surface facility,",
    "and no evidence at all about one demolished or buried.",
    "Dipping ran 1907 to 1917. The earliest frame is 1929."]):
    d.text((SIZE//2, 400+i*38), t, font=F(21 if t and not t.startswith("That") else 19),
           fill=WHITE if i in (3,) else MUT, anchor="ma")
frames += hold(im, 4)

# ---------------- water-siting question, answered honestly ----------------
im = Image.new("RGB", (SIZE, SIZE), NAVY); d = ImageDraw.Draw(im)
d.text((SIZE//2, 210), "Would a vat have been sited on the creek?", font=F(34, True), fill=WHITE, anchor="ma")
rows = [
 ("Yes, for water supply.", WHITE),
 ("The USDA formula was 8 lb arsenic to 500 gallons. Filling and", MUT),
 ("recharging a vat needed a source, and cattle already gathered at water.", MUT),
 ("", MUT),
 ("But not for flushing.", WHITE),
 ("The USDA placard posted at every vat read: \"Do not allow it to", MUT),
 ("contaminate any feed or water supply.\" Containment was the instruction.", MUT),
 ("", MUT),
 ("And if dip HAD been flushed to running water, arsenic binds to", (200,206,216)),
 ("sediment. It would concentrate downstream in depositional zones,", (200,206,216)),
 ("not in the soil at the vat. That changes where you would look.", (200,206,216)),
 ("", MUT),
 ("No vat has been located. This remains an open question.", ACC),
]
y = 300
for t, c in rows:
    d.text((SIZE//2, y), t, font=F(20 if c is WHITE else 18, c is WHITE), fill=c, anchor="ma"); y += 32
frames += hold(im, 6)

# ---------------- 1995 / 1998 georeferenced aerials ----------------
for tif, yr, cap in [
    ("oc_historical_aerial_ladera_1995.tif", "1995",
     ["Still open ground across most of the footprint.",
      "Antonio Parkway corridor under construction along the eastern edge."]),
    ("oc_historical_aerial_ladera_1998.tif", "1998",
     ["Grading has begun. Entitlement approved 1997; mass grading follows.",
      "The community is about to be built."])]:
    p = os.path.join(REPO, "evidence/lhdrs/mission6/imagery", tif)
    if not os.path.exists(p): continue
    panel = crop_to_aoi(Image.open(p).convert("RGB"), TIF_BBOX)
    im, d = base(panel, "Ladera Ranch", "Orange County aerial, georeferenced", yr)
    draw_water(d)
    draw_node(d)
    caption(d, cap)
    foot(d, "OC Survey historical imagery")
    frames += hold(im, 3)

# ---------------- Landsat monthly ----------------
im = Image.new("RGB", (SIZE, SIZE), NAVY); d = ImageDraw.Draw(im)
d.text((SIZE//2, 400), "1997 - 2006", font=F(58, True), fill=WHITE, anchor="ma")
d.text((SIZE//2, 490), "Monthly satellite record", font=F(26), fill=ACC, anchor="ma")
d.text((SIZE//2, 545), "102 cloud-free Landsat frames", font=F(18), fill=MUT, anchor="ma")
frames += hold(im, 2.5)

man = json.load(open(os.path.join(OUT, "timelapse_manifest.json")))
seq = man["videoSequence"]
T0, T1 = 1997.0, 2007.0
def dec(s): return int(s[:4]) + (int(s[5:7])-0.5)/12.0

for i, dt in enumerate(seq):
    g = glob.glob(os.path.join(FR, f"*_{dt}.png"))
    if not g: continue
    src = Image.open(g[0]).convert("RGB")
    src = src.crop((0, 0, src.width, src.height-34))
    panel = crop_to_aoi(src, LAND_BBOX)
    im, d = base(panel, "Ladera Ranch", "Landsat true colour, 30 m", dt[:7])
    # timeline
    bx0, bx1, by = 36, SIZE-36, MAPEND+22
    d.line([bx0, by, bx1, by], fill=(60,68,84), width=3)
    for yr in range(1997, 2008):
        x = bx0+(bx1-bx0)*(yr-T0)/(T1-T0)
        d.line([x, by-6, x, by+6], fill=(90,100,118), width=2)
        if yr % 2 == 1: d.text((x, by+11), str(yr), font=F(13), fill=MUT, anchor="ma")
    for s in seq:
        x = bx0+(bx1-bx0)*(dec(s)-T0)/(T1-T0)
        d.line([x, by-2, x, by+2], fill=(120,132,152), width=1)
    px = bx0+(bx1-bx0)*(dec(dt)-T0)/(T1-T0)
    d.ellipse([px-7, by-7, px+7, by+7], fill=ACC)
    # schools appear once they exist (Chaparral 2001, LRES/LRMS 2003, Oso Grande 2005)
    yr = int(dt[:4])
    live = [s for s in SCH if (("Chaparral" in s["label"] and yr >= 2001) or
                               ("Ladera Ranch" in s["label"] and yr >= 2003) or
                               ("Oso Grande" in s["label"] and yr >= 2005))]
    if live:
        old = SCH[:]; SCH[:] = live; draw_schools(d); SCH[:] = old
        d.text((36, MAPEND+46), "○  schools, shown from their opening year", font=F(15), fill=SCHOOL)
    caption(d, ["30 m pixels: grading and roads visible, individual houses are not.",
                "Ground conditions only. Not a contamination, dust or exposure product."][0:2])
    foot(d, "Landsat 5/7 - USGS/NASA")
    frames.append(np.asarray(im))

# ---------------- modern with schools ----------------
p = os.path.join(AER, "2022_modern.jpg")
if os.path.exists(p):
    panel = crop_to_aoi(Image.open(p).convert("RGB"), HIST_BBOX)
    for cap, showw in [ (["Built out. Ladera Ranch occupies the central and eastern footprint.",
                          "The western Trabuco corridor is preserved open space."], True),
                        (["The four public schools, at their mapped locations.",
                          "Chaparral 2001 - Ladera Ranch ES and MS 2003 - Oso Grande 2005."], False) ]:
        im, d = base(panel, "Ladera Ranch", "Orange County 1 ft countywide aerial", "2022")
        if showw: draw_water(d)
        else: draw_schools(d)
        caption(d, cap)
        foot(d, "OC Survey 2022")
        frames += hold(im, 3.5)

# ---------------- node zoom: same 100 m across 77 years ----------------
im = Image.new("RGB", (SIZE, SIZE), NAVY); d = ImageDraw.Draw(im)
d.text((SIZE//2, 330), "One point on the ground", font=F(40, True), fill=WHITE, anchor="ma")
for i, t in enumerate([
    "33.55505, -117.65492  -  Trabuco Creek corridor",
    "",
    "A single structure drawn by a USGS surveyor on the 1948 sheet.",
    "The only documented point of human construction in the footprint.",
    "",
    "What it was is unrecorded. It is NOT identified as a dip vat."]):
    d.text((SIZE//2, 420+i*34), t, font=F(20 if i in (0,) else 18),
           fill=ACC if i == 0 else MUT, anchor="ma")
frames += hold(im, 5)

NODEZ = [
 ("z1_ranch_1929.jpg", "1929",
  ["Creek corridor with unimproved dirt tracks converging through it.",
   "Twelve years after compulsory dipping ended."]),
 ("z1_ranch_1937.jpg", "1937-38",
  ["1.15 ft/px. Oak and sycamore woodland, braided channel, wheel ruts,",
   "fence lines on the grassland east. No pen, chute or vat resolvable."]),
 ("z1_ranch_1946b.jpg", "1946-47",
  ["Unchanged. Working ranch corridor, still grazed."]),
 ("z1_ranch_2022_modern.jpg", "2022",
  ["Today the corridor is PRESERVED OPEN SPACE, not housing.",
   "Golf course east, commercial to the north-west.",
   "The ground here was never built over - so it can still be tested."]),
]
for fn, yr, cap in NODEZ:
    fp = os.path.join(AER, fn)
    if not os.path.exists(fp): continue
    src = Image.open(fp).convert("RGB")
    w, h = src.size
    side = min(w, h)
    src = src.crop(((w-side)//2, (h-side)//2, (w+side)//2, (h+side)//2)).resize((MAP, MAP), Image.LANCZOS)
    im, d = base(src, "Trabuco Creek node", "100 m scale  -  33.55505, -117.65492", yr)
    px, py = (SIZE-MAP)//2+MAP//2, TOPBAR+MAP//2
    d.ellipse([px-26, py-26, px+26, py+26], outline=NODE, width=3)
    for dx, dy in ((-38,0),(38,0),(0,-38),(0,38)):
        d.line([px+dx*0.72, py+dy*0.72, px+dx, py+dy], fill=NODE, width=3)
    d.text((36, MAPEND+12), "◎  1948 ranch structure - unidentified, explicitly NOT a dip vat",
           font=F(15), fill=NODE)
    caption(d, cap)
    foot(d, "OC Survey / OCGIS Historic_Imagery_v2")
    frames += hold(im, 4)

# why it matters card
im = Image.new("RGB", (SIZE, SIZE), NAVY); d = ImageDraw.Draw(im)
d.text((SIZE//2, 250), "Why this point, and not another", font=F(34, True), fill=WHITE, anchor="ma")
for i, t in enumerate([
    "It is the only place in the footprint with all three at once:",
    "",
    "documented construction  -  water  -  where cattle gathered",
    "",
    "Ranch working facilities were built where stock already came to drink.",
    "That does not make it a vat. It makes it the least arbitrary place to look.",
    "",
    "It sits in preserved open space, so ground-penetrating radar and soil",
    "sampling remain possible without disturbing a single home.",
    "",
    "No vat has been found. The question is open, and it is testable."]):
    d.text((SIZE//2, 330+i*33), t, font=F(21 if i == 2 else 18, i == 2),
           fill=ACC if i == 2 else (MUT if i != 10 else (200,206,216)), anchor="ma")
frames += hold(im, 7)

# ---------------- end card ----------------
im = Image.new("RGB", (SIZE, SIZE), NAVY); d = ImageDraw.Draw(im)
d.text((SIZE//2, 330), "Ground disturbance peaked", font=F(34), fill=MUT, anchor="ma")
d.text((SIZE//2, 380), "in 2002", font=F(58, True), fill=WHITE, anchor="ma")
for i, t in enumerate([
    "Built from public imagery: OC Survey aerials 1929-2022",
    "and USGS/NASA Landsat 1997-2006.",
    "",
    "Only documented features are labelled.",
    "No dip vat, corral or ranch structure was identified",
    "inside the footprint in any pre-1950 frame.",
    "",
    "Ground conditions only. This implies nothing about health."]):
    d.text((SIZE//2, 500+i*32), t, font=F(18), fill=MUT if i != 4 else (200,206,216), anchor="ma")
frames += hold(im, 5)

print(f"composed {len(frames)} frames ({len(frames)/FPS:.0f}s)")
mp4 = os.path.join(OUT, "ladera_full_history_1929_2006.mp4")
imageio.mimsave(mp4, frames, fps=FPS, quality=9, macro_block_size=1)
print("wrote", mp4, f"{os.path.getsize(mp4)/1e6:.1f} MB")
