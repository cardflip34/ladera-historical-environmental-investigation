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



NODATA = (58, 64, 78)   # neutral - never a colour that reads as ground

def load_hist_jpg(path):
    """OC ImageServer exports fill out-of-coverage with pure yellow. Replace with neutral."""
    im = Image.open(path).convert("RGB")
    a = np.asarray(im).copy()
    m = (a[:, :, 0] > 245) & (a[:, :, 1] > 245) & (a[:, :, 2] < 40)
    a[m] = NODATA
    return Image.fromarray(a), float(m.mean())


def load_geotiff(path):
    """These are TILED RGBA. PIL mis-decodes them and .convert('RGB') exposes the
    undefined transparent region. Read with rasterio and honour the alpha band."""
    import rasterio
    with rasterio.open(path) as s:
        rgb = s.read([1, 2, 3]).transpose(1, 2, 0).astype("uint8")
        al = s.read(4) if s.count >= 4 else np.full(rgb.shape[:2], 255, "uint8")
    out = rgb.copy()
    out[al == 0] = NODATA
    return Image.fromarray(out), float((al == 0).mean())


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
    """Every frame is stamped with its own year. The year is the single most important thing on
    the frame - without it a viewer cannot tell a 1929 rangeland photo from a 1953 one - so it is
    set large in a filled badge rather than as small corner text."""
    im = Image.new("RGB", (SIZE, SIZE), NAVY)
    im.paste(panel, ((SIZE-MAP)//2, TOPBAR))
    d = ImageDraw.Draw(im)
    d.text((36, 20), title, font=F(38, True), fill=WHITE)
    d.text((36, 66), sub, font=F(16), fill=MUT)
    f = F(46, True)
    bb = d.textbbox((0, 0), era, font=f)
    w, h = bb[2]-bb[0], bb[3]-bb[1]
    x1, y0 = SIZE-30, 16
    d.rounded_rectangle([x1-w-26, y0, x1, y0+h+22], 8, fill=(38, 30, 18), outline=ACC, width=2)
    d.text((x1-13, y0+11), era, font=f, fill=ACC, anchor="ra")
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


SCH_DIST = {}
_p = os.path.join(OUT, "schools_channel_proximity.json")
if os.path.exists(_p):
    for r in json.load(open(_p)):
        k = r["school"].replace(" Elementary School", " ES").replace(" Middle School", " MS")
        SCH_DIST[k.split()[0] + " " + k.split()[-1]] = r["metresToChannel"]


def _sdist(label):
    """Match a merged label like 'Ladera Ranch ES / MS' back to a proximity record."""
    for k, v in SCH_DIST.items():
        if label.split()[0] == k.split()[0]:
            return v
    return None


def draw_schools(d, with_dist=False):
    for s in SCH:
        x, y = xy(s["lon"], s["lat"])
        if not (0 <= x < MAP and 0 <= y < MAP):
            continue
        px, py = (SIZE-MAP)//2+x, TOPBAR+y
        d.ellipse([px-9, py-9, px+9, py+9], outline=SCHOOL, width=3)
        d.line([px, py-16, px, py-30], fill=SCHOOL, width=2)
        t = s["label"]
        if with_dist:
            dv = _sdist(s["label"])
            if dv is not None:
                t = f"{t}  ·  {dv:.0f} m to creek"
        w = d.textlength(t, font=F(15, True))
        bx = min(max(px-w/2-7, 4), SIZE-w-12)
        d.rectangle([bx, py-52, bx+w+14, py-30], fill=(28, 34, 48))
        d.text((bx+7, py-49), t, font=F(15, True), fill=SCHOOL)



# Documented named features inside the AOI, with coordinates. Nothing inferred.
# NOTE: historic_ranch_1948.geojson still carries the pre-correction drainage name
# ("Canada Chiquita"). Correction C-002 established it is TRABUCO CREEK. Corrected here.
LANDMARKS = [
 {"lon": -117.65492, "lat": 33.55505, "label": "1948 ranch structure",
  "sub": "trail/water node - NOT a dip vat", "col": (255,120,120)},
 {"lon": -117.64400, "lat": 33.53600, "label": "O'Neill #1 well",
  "sub": "Union Oil - plugged dry hole", "col": (190,160,255)},
 {"lon": -117.63600, "lat": 33.54600, "label": "Citizens National Trust B-1",
  "sub": "plugged dry hole", "col": (190,160,255)},
 {"lon": -117.66200, "lat": 33.54200, "label": "Blue Diamond Materials",
  "sub": "asphalt plant", "col": (150,200,150)},
 {"lon": -117.65500, "lat": 33.56970, "label": "Carl Hankey ES",
  "sub": "DTSC: arsenic, lead - former orchard", "col": (255,205,80)},
]


def draw_landmarks(d):
    placed = []
    for m in LANDMARKS:
        x, y = xy(m["lon"], m["lat"])
        if not (0 <= x < MAP and 0 <= y < MAP):
            continue
        px, py = (SIZE-MAP)//2+x, TOPBAR+y
        c = m["col"]
        d.ellipse([px-8, py-8, px+8, py+8], outline=c, width=3)
        ty = py-46
        while any(abs(ty-q) < 34 for q in placed):
            ty -= 34
        placed.append(ty)
        d.line([px, py-10, px, ty+22], fill=c, width=2)
        w = max(d.textlength(m["label"], font=F(15, True)), d.textlength(m["sub"], font=F(12)))
        bx = min(max(px-w/2-8, 6), SIZE-w-18)
        d.rectangle([bx, ty-4, bx+w+16, ty+22], fill=(24, 30, 42))
        d.text((bx+8, ty-2), m["label"], font=F(15, True), fill=c)
        d.text((bx+8, ty+11), m["sub"], font=F(12), fill=(170,176,188))




# ---- Full mapped drainage network, OC Flood_Channels (MapServer), fetched 2026-07-29.
# The single Horno_3 lidar reach previously plotted was only 0.9 km in the far south. The county
# as-built channel layer carries the whole system. Horno Creek runs the southern 60% of the AOI and
# the SAME drainage line continues north as the Acjachema Storm Drain - which is why it reads as
# "all the way through" on the ground while appearing under two names in the record.
STREAM = (86, 158, 232)
DRAIN  = (120, 190, 235)
PARKC  = (110, 200, 140)

def _chan():
    p = os.path.join(OUT, "oc_flood_channels_aoi.geojson")
    if not os.path.exists(p): return {}
    d = json.load(open(p))
    out = {}
    for f in d["features"]:
        nm = (f.get("properties") or {}).get("FACILITYNAME")
        if not nm or not isinstance(nm, str) or len(nm) < 5: continue
        g = f.get("geometry")
        if not g: continue
        parts = [g["coordinates"]] if g["type"] == "LineString" else g["coordinates"]
        out.setdefault(nm.strip().upper(), []).extend(parts)
    return out
CHAN = _chan()

def _park():
    """County Park_Boundaries carries only O'Neill Regional Park here. Ladera Ranch's own parks are
    HOA / LARMAC facilities and are absent from the county layer, so they come from OpenStreetMap
    (B2, community-mapped) and are graded separately from the A+ county channel geometry."""
    out = []
    p = os.path.join(OUT, "oc_parks_aoi.geojson")
    if os.path.exists(p):
        for f in json.load(open(p))["features"]:
            g = f.get("geometry")
            if not g: continue
            nm = (f.get("properties") or {}).get("FACILITYNAME") or "Park"
            rings = [g["coordinates"][0]] if g["type"] == "Polygon" else [q[0] for q in g["coordinates"]]
            out.append((nm, rings, "county", 9e9))
    prox = {}
    pp = os.path.join(OUT, "parks_channel_proximity.json")
    if os.path.exists(pp):
        prox = {r["park"]: r["metresToChannel"] for r in json.load(open(pp))}
    p = os.path.join(OUT, "osm_parks_aoi.geojson")
    if os.path.exists(p):
        for f in json.load(open(p))["features"]:
            g = f.get("geometry"); nm = f["properties"].get("name") or "(unnamed)"
            if not g: continue
            out.append((nm, [g["coordinates"][0]], "osm", prox.get(nm, 9e9)))
    return out
PARKS = _park()
ONCHAN = 120.0            # metres. Parks at or inside this distance get named on the frame.


def _clip(x0, y0, x1, y1, L, T, R, B):
    """Liang-Barsky. Vectors must never render outside the map rectangle - previously the
    channel lines drew across the title bar and the caption."""
    dx, dy = x1-x0, y1-y0
    t0, t1 = 0.0, 1.0
    for pp, qq in ((-dx, x0-L), (dx, R-x0), (-dy, y0-T), (dy, B-y0)):
        if pp == 0:
            if qq < 0: return None
            continue
        r = qq/pp
        if pp < 0:
            if r > t1: return None
            t0 = max(t0, r)
        else:
            if r < t0: return None
            t1 = min(t1, r)
    return (x0+t0*dx, y0+t0*dy, x0+t1*dx, y0+t1*dy)


def _poly(d, seg, col, w):
    ox = (SIZE-MAP)//2
    L, T, R, B = ox, TOPBAR, ox+MAP, MAPEND
    pts = [(ox+xy(c[0], c[1])[0], TOPBAR+xy(c[0], c[1])[1]) for c in seg]
    for a, b in zip(pts, pts[1:]):
        c = _clip(a[0], a[1], b[0], b[1], L, T, R, B)
        if c:
            d.line([(c[0], c[1]), (c[2], c[3])], fill=col, width=w)


def draw_horno(d, note=True, w=4):
    """Horno Creek plus the drainage line that continues it north."""
    for seg in CHAN.get("HORNO CREEK CHANNEL", []):
        _poly(d, seg, STREAM, w)
    for seg in CHAN.get("ACJACHEMA STORM DRAIN", []):
        _poly(d, seg, DRAIN, max(2, w-1))
    if note:
        d.text((36, MAPEND+34), "—  Horno Creek (south)   —  Acjachema Storm Drain (through the built core)",
               font=F(15), fill=STREAM)


def draw_all_water(d, note=True, w=3):
    for nm, col in (("TRABUCO CREEK CHANNEL", (70,140,210)), ("CANADA CHIQUITA", (70,140,210)),
                    ("OSO CREEK CHANNEL", (70,140,210))):
        for seg in CHAN.get(nm, []):
            _poly(d, seg, col, max(2, w-1))
    draw_horno(d, note=False, w=w+1)
    if note:
        d.text((36, MAPEND+34), "—  Horno Creek    —  Acjachema Storm Drain    —  Trabuco / Canada Chiquita / Oso",
               font=F(14), fill=STREAM)


def draw_parks(d, note=True, labels=True):
    ox = (SIZE-MAP)//2
    lab = []
    for nm, rings, src, dist in PARKS:
        near = dist <= ONCHAN
        col = PARKC if near else (74, 118, 88)
        for r in rings:
            if len(r) > 2:
                _poly(d, list(r) + [r[0]], col, 3 if near else 1)
        if labels and near and nm != "(unnamed)":
            cx = sum(q[0] for q in rings[0]) / len(rings[0])
            cy = sum(q[1] for q in rings[0]) / len(rings[0])
            x, y = xy(cx, cy)
            lab.append((ox+x, TOPBAR+y, nm, dist))
    for x, y, nm, dist in lab:
        if not (ox+4 < x < ox+MAP-4 and TOPBAR+4 < y < MAPEND-4): continue
        t = f"{nm}  {dist:.0f} m"
        d.ellipse([x-4, y-4, x+4, y+4], fill=PARKC, outline=(255, 255, 255))
        bb = d.textbbox((0, 0), t, font=F(13, True))
        tx = min(x+9, ox+MAP-(bb[2]-bb[0])-6)
        d.rectangle([tx-3, y-9, tx+(bb[2]-bb[0])+3, y+9], fill=(12, 26, 20))
        d.text((tx, y-8), t, font=F(13, True), fill=PARKC)
    if note:
        n_on = sum(1 for _, _, _, dv in PARKS if dv <= 25)
        d.text((36, MAPEND+56),
               f"▢  parks    {n_on} of them sit within 25 m of the drainage",
               font=F(15), fill=PARKC)


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
        d.text((36, MAPEND+56), "◎  1948 ranch-activity node - explicitly NOT identified as a dip vat",
               font=F(15), fill=NODE)


def caption(d, lines, color=(190,196,208)):
    y = MAPEND+80
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
 ("1946b_filled.jpg", "1947", "Composite - 1947 county flight, north-west quarter from 1938",
  ["Unchanged. Still rangeland, still grazed, a decade on.",
   "COMPOSITE: the 1947 flight did not photograph the north-west quarter, so that",
   "area is the 1938 flight. Both dates show the same thing here - open grazing land."]),
]
for fn, yr, srcdesc, cap in HIST:
    p = os.path.join(AER, fn)
    if not os.path.exists(p): continue
    src, nod = load_hist_jpg(p)
    panel = crop_to_aoi(src, HIST_BBOX)
    im, d = base(panel, "Ladera Ranch", srcdesc, yr)
    draw_water(d)
    draw_horno(d)
    draw_node(d)
    if nod > 0.02:
        d.text((36, MAPEND+56), "■  grey = outside this frame's coverage", font=F(15), fill=NODATA)
    caption(d, cap)
    foot(d, "OC Survey / OCGIS Historic_Imagery_v2, server-rectified")
    frames += hold(im, 4)

# ---------------- complete-coverage OC frames, 1953-1990 ----------------
# These replace the Mission 6 1995/1998 rasters, which are narrow flight strips ~72% transparent
# over the AOI. Fetched by LockRaster on a single OBJECTID, same method as the 1929/1937 exports.
OCF = os.path.join(REPO, "evidence/lhdrs/mission7/oc_frames")
OCSEQ = [
 ("oc_1953_oid357.jpg", "1953", "Orange County countywide series",
  ["Still open rangeland. Grazing, unimproved tracks, the creek corridor intact.",
   "Thirty-six years after compulsory dipping ended."]),
 ("oc_1960_oid343.jpg", "1960", "Orange County countywide series",
  ["Unchanged inside the footprint. Development is arriving elsewhere in the county."]),
 ("oc_1969_oid315.jpg", "1969", "Orange County countywide series",
  ["Mission Viejo is building out to the west. The footprint itself is still ranch."]),
 ("oc_1980_oid320.jpg", "1980", "Orange County countywide series",
  ["Suburbia now reaches the western boundary and stops at the creek."]),
 ("oc_1990_oid319.jpg", "1990", "Orange County countywide series",
  ["Seven years before entitlement. The footprint is still undeveloped grazing land,",
   "with built Mission Viejo pressed against its western edge."]),
]
for fn, yr, srcdesc, cap in OCSEQ:
    fp = os.path.join(OCF, fn)
    if not os.path.exists(fp):
        continue
    src, nod = load_hist_jpg(fp)
    panel = crop_to_aoi(src, HIST_BBOX)
    im, d = base(panel, "Ladera Ranch", srcdesc, yr)
    draw_water(d)
    draw_horno(d)
    draw_node(d)
    caption(d, cap)
    foot(d, "OC Survey / OCGIS Historic_Imagery_v2, LockRaster export")
    frames += hold(im, 4)

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
    # The drainage, carried across the whole construction record. It is the one feature that was
    # running water through every month of grading shown in this sequence.
    draw_horno(d, note=False, w=4)
    d.text((36, MAPEND+46), "—  Horno Creek, continuing north as the Acjachema Storm Drain",
           font=F(15), fill=STREAM)
    # 1968 water bodies carried forward so you can see what was built over
    nw = draw_water(d, note=False)
    d.text((36, MAPEND+68), f"○  {nw} water bodies mapped in 1968, shown where they used to be",
           font=F(15), fill=CYAN)
    # schools appear once they exist (Chaparral 2001, LRES/LRMS 2003, Oso Grande 2005)
    yr = int(dt[:4])
    live = [s for s in SCH if (("Chaparral" in s["label"] and yr >= 2001) or
                               ("Ladera Ranch" in s["label"] and yr >= 2003) or
                               ("Oso Grande" in s["label"] and yr >= 2005))]
    if live:
        old = SCH[:]; SCH[:] = live; draw_schools(d); SCH[:] = old
        d.text((36, MAPEND+90), "○  schools, shown from their opening year", font=F(15), fill=SCHOOL)
    cy = MAPEND+118
    for t in ["30 m pixels: grading and roads visible, individual houses are not.",
              "Ground conditions only. Not a contamination, dust or exposure product."]:
        d.text((36, cy), t, font=F(16), fill=(190,196,208)); cy += 24
    foot(d, "Landsat 5/7 - USGS/NASA")
    frames.append(np.asarray(im))

# ---------------- modern with schools ----------------
p = os.path.join(AER, "2022_modern.jpg")
if os.path.exists(p):
    panel = crop_to_aoi(Image.open(p).convert("RGB"), HIST_BBOX)
    for mode, cap in [
        ("water", ["Built out. Ladera Ranch occupies the central and eastern footprint.",
                   "The western Trabuco corridor is preserved open space."]),
        ("schools", ["The four public schools, at their mapped locations.",
                     "Chaparral 2001 - Ladera Ranch ES and MS 2003 - Oso Grande 2005."]),
        ("landmarks", ["Every named feature this project holds with coordinates inside the frame.",
                       "The ranch itself is not a point: the whole footprint was O'Neill / Rancho",
                       "Mission Viejo grazing land. Only one structure was ever mapped on it."])]:
        im, d = base(panel, "Ladera Ranch", "Orange County 1 ft countywide aerial", "2022")
        draw_horno(d, note=(mode=="water"))
        if mode == "water": draw_water(d)
        elif mode == "schools": draw_schools(d)
        else:
            draw_landmarks(d)
            d.text((36, MAPEND+12), "documented features only - nothing inferred",
                   font=F(15), fill=(150,156,168))
        caption(d, cap)
        foot(d, "OC Survey 2022")
        frames += hold(im, 3.5 if mode != "landmarks" else 6)

# ---------------- 0.3 m orthoimagery, January 2004 ----------------
HRO = os.path.join(OUT, "hro_2004_aoi.png")
_cov = 1.0
_cj = os.path.join(OUT, "hro_2004_aoi.provenance.json")
if os.path.exists(_cj):
    _cov = json.load(open(_cj)).get("aoiCoverageFraction", 1.0)
COVERAGE_LINE = ("Complete coverage of the frame."
                 if _cov > 0.995 else
                 f"Held tiles cover {_cov*100:.0f}% of the frame; the rest is left blank, not filled in.")
if os.path.exists(HRO):
    im = Image.new("RGB", (SIZE, SIZE), NAVY); d = ImageDraw.Draw(im)
    d.text((SIZE//2, 330), "January 2004", font=F(58, True), fill=WHITE, anchor="ma")
    d.text((SIZE//2, 410), "0.3 metre orthoimagery", font=F(28), fill=ACC, anchor="ma")
    for i, t in enumerate([
        "One hundred times finer than the satellite frames.",
        "Inside the window this project had recorded as having no imagery at all.",
        COVERAGE_LINE]):
        d.text((SIZE//2, 480+i*32), t, font=F(18), fill=MUT, anchor="ma")
    frames += hold(im, 4)

    src = Image.open(HRO).convert("RGB")
    a = np.asarray(src).copy()
    a[(a.sum(axis=2) == 0)] = NODATA           # uncovered -> neutral, never ground
    panel = Image.fromarray(a).resize((MAP, MAP), Image.LANCZOS)

    for mode, cap in [
        ("plain", ["USGS High Resolution Orthoimagery, 21 January 2004.",
                   "North built out. Centre and south still raw graded pad and road.",
                   "Grey = outside the tiles held, not empty ground."]),
        ("creek", ["One continuous drainage crosses the community: Horno Creek in the south,",
                   "recorded by the County as the Acjachema Storm Drain through the built core.",
                   "Four parks sit within 25 m of it. It has never been sampled."]),
        ("all",   ["Every documented feature on one frame, at 0.3 m: schools, the drainage,",
                   "the parks along it, the 1948 ranch node and the 1968 water bodies.",
                   "Individual houses, pads and equipment are resolvable."])]:
        im, d = base(panel, "Ladera Ranch", "USGS orthoimagery, 0.3 m native", "Jan 2004")
        if mode == "plain":
            d.text((36, MAPEND+12), "■  grey = outside the tiles held", font=F(15), fill=NODATA)
        elif mode == "creek":
            draw_all_water(d, w=5)
            draw_parks(d, labels=False)
        else:
            draw_all_water(d, note=False, w=4)
            draw_parks(d, note=False, labels=False)
            draw_water(d, note=False)
            draw_node(d, note=False)
            draw_schools(d, with_dist=True)
            d.text((36, MAPEND+12),
                   "○ schools, with distance to the drainage   ◎ 1948 ranch node",
                   font=F(15), fill=MUT)
            d.text((36, MAPEND+34),
                   "— drainage   ▢ parks   ○ 1968 water bodies", font=F(15), fill=MUT)
        caption(d, cap)
        foot(d, "USGS EarthExplorer - High Resolution Orthoimagery 2004-01-21")
        frames += hold(im, 6)

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
    src, nod = load_hist_jpg(fp)
    if nod > 0.85:
        print(f"  skipping node zoom {yr}: {nod*100:.0f}% outside frame coverage")
        continue
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
