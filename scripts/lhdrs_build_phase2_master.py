#!/usr/bin/env python3
"""
MASTER PHASE 2 VIDEO - the two working videos combined into one presentation.

Merges lhdrs_m7_build_video_v2.py (1929-2006 imagery record) and
lhdrs_build_pathway_timelapse.py (grading timelapse, quantification cards, mechanism schematic)
into a single narrative, ordered as a Phase 2 findings presentation rather than as two archives
played back to back.

WHAT CHANGED IN THE MERGE
  - ONE grading timelapse, not two. Both source videos contained the same 102-month Landsat
    sequence; it appears once here, and EARLY, as the focal point rather than buried mid-reel.
  - Narrative order follows a presentation arc: what we set out to test, what the ground did,
    what the land was before, what the record says, the numbers, the searches (including their
    negatives), the mechanism, and where to test.
  - Photo hold times are unchanged from the sources: 4s per historical aerial, 6s per 0.3 m
    frame, 3.5s per modern overlay, node zooms as before.
  - No frames dropped. Every section from both videos is present.

Preamble (asset loading, projection, and all draw_* helpers) is inherited verbatim from
lhdrs_m7_build_video_v2.py so geometry and styling stay identical across both products.
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


# ============================================================================
#                        PHASE 2 PRESENTATION SEQUENCE
# ============================================================================
import importlib.util as _il
_pw = os.path.join(REPO, "research/arsenic_mass_balance")
MB   = json.load(open(os.path.join(_pw, "arsenic_mass_balance.json")))
TOT  = json.load(open(os.path.join(_pw, "arsenic_total_and_scale.json")))
ORCH = json.load(open(os.path.join(OUT.replace("mission7", "orchards"), "orchard_summary.json")))
TGT  = json.load(open(os.path.join(OUT, "sampling_targets_reasoned.json")))
RED  = (196, 58, 44); HOT = (226, 74, 58); WARM = (236, 158, 52)

def bigcard(lines, sub=None, sec=5, rule=RED):
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

def datacard(title, sub, rows, foot_=None, sec=7, tcol=ACC):
    im = Image.new("RGB", (SIZE, SIZE), NAVY); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, SIZE, 8], fill=RED)
    d.text((60, 44), title, font=F(34, True), fill=WHITE)
    y = 96
    for t in sub:
        d.text((60, y), t, font=F(17), fill=MUT); y += 26
    y += 18
    for lab, val in rows:
        if lab == "--":
            d.line([60, y+8, SIZE-60, y+8], fill=(52,60,74), width=1); y += 26; continue
        d.text((60, y), lab, font=F(19), fill=(206,212,222))
        d.text((SIZE-60, y), val, font=F(21, True), fill=tcol, anchor="ra")
        y += 38
    if foot_:
        by = SIZE-52-len(foot_)*24
        d.rounded_rectangle([50, by-20, SIZE-50, SIZE-30], 8, fill=(38,24,20),
                            outline=(150,60,42), width=2)
        for i, t in enumerate(foot_):
            d.text((70, by+i*24), t, font=F(15), fill=(226,178,166))
    return hold(im, sec)

frames = []

# ---- ACT 0 : who we are and what phase 2 tested -----------------------------
frames += bigcard([("PHASE 2", 72, True), ("Findings", 38, False)],
    ["Ladera Ranch, Orange County, California",
     "The arsenical cattle-dipping era, and the ground it left behind",
     "",
     "An independent research and data-organization project.",
     "It does not provide medical advice and does not establish causation."], sec=7)

frames += bigcard([("What Phase 2 set out to test", 34, True)],
    ["Between 1907 and March 1912 the State of California and the USDA",
     "compelled every rancher in quarantined counties to dip every animal",
     "in an arsenical solution. Orange County was in the heaviest tier.",
     "",
     "Phase 2 asks three questions:",
     "How much arsenic would that have put into this landscape?",
     "Where would it have concentrated?",
     "And has anyone ever looked?"], sec=9)

# ---- ACT 1 : THE GROUND MOVED - timelapse as the focal point, early ---------
frames += bigcard([("First, what the ground did", 34, True)],
    ["1997 to 2006, month by month, from space.",
     "102 cloud-free Landsat observations of grading and build-out.",
     "",
     "The drainage and the candidate source zones are carried on every frame,",
     "so you can see what the earthworks moved through."], sec=7)

T0, T1 = 1997.0, 2007.0
def dec(s): return int(s[:4]) + (int(s[5:7])-0.5)/12.0
tl_man = json.load(open(os.path.join(OUT, "timelapse_manifest.json")))
tl_seq = tl_man["videoSequence"]
FRDIR = os.path.join(OUT, "timelapse_frames")
OXm = (SIZE-MAP)//2

for dt in tl_seq:
    g = glob.glob(os.path.join(FRDIR, f"*_{dt}.png"))
    if not g: continue
    src_ = Image.open(g[0]).convert("RGB")
    src_ = src_.crop((0, 0, src_.width, src_.height-34))
    panel = crop_to_aoi(src_, LAND_BBOX)
    im, d = base(panel, "Grading and build-out", "Landsat true colour, 30 m", dt[:7])
    draw_all_water(d, note=False, w=3)
    for t in TGT:
        x, y = xy(t["lon"], t["lat"])
        if not (0 <= x < MAP and 0 <= y < MAP): continue
        px_, py_ = OXm+x, TOPBAR+y
        col = HOT if t["p"] == 1 else WARM
        r = 9 if t["p"] == 1 else 7
        d.ellipse([px_-r, py_-r, px_+r, py_+r], outline=col, width=3)
    bx0, bx1, by = 36, SIZE-36, MAPEND+22
    d.line([bx0, by, bx1, by], fill=(60,68,84), width=3)
    for yr in range(1997, 2008):
        x = bx0+(bx1-bx0)*(yr-T0)/(T1-T0)
        d.line([x, by-6, x, by+6], fill=(90,100,118), width=2)
        if yr % 2 == 1: d.text((x, by+11), str(yr), font=F(13), fill=MUT, anchor="ma")
    px_ = bx0+(bx1-bx0)*(dec(dt)-T0)/(T1-T0)
    d.ellipse([px_-7, by-7, px_+7, by+7], fill=ACC)
    d.text((36, MAPEND+50), "○  candidate source zones — 1968 stock-water points, NOT vats",
           font=F(15), fill=HOT)
    d.text((36, MAPEND+72), "—  the drainage — ran through the site in every one of these months",
           font=F(15), fill=STREAM)
    for _i, _t in enumerate([
        "30 m pixels: grading extent and roads are visible; individual pads are not.",
        "Ground-surface condition only. Not a contamination, dust or exposure product."]):
        d.text((36, MAPEND+104+_i*24), _t, font=F(16), fill=(190,196,208))
    foot(d, "Landsat 5/7 - USGS/NASA")
    frames.append(np.asarray(im))

frames += bigcard([("Ground disturbance peaked", 32, False), ("in 2002", 58, True)],
    ["52.8% of the in-CDP area was bare, graded ground",
     "The drainage ran through it in every one of those months"], sec=6)

# ---- ACT 2 : what the land WAS before any of that ---------------------------
frames += bigcard([("What was graded", 36, True)],
    ["Before the earthmovers, this ground had one use for a century.",
     "The aerial record runs back to 1929."], sec=6)

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
    src_, nod = load_hist_jpg(p)
    panel = crop_to_aoi(src_, HIST_BBOX)
    im, d = base(panel, "Ladera Ranch", srcdesc, yr)
    draw_water(d); draw_horno(d); draw_node(d)
    caption(d, cap)
    foot(d, "OC Survey / OCGIS Historic_Imagery_v2, server-rectified")
    frames += hold(im, 4)

OCF = os.path.join(OUT, "oc_frames")
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
    if not os.path.exists(fp): continue
    src_, nod = load_hist_jpg(fp)
    panel = crop_to_aoi(src_, HIST_BBOX)
    im, d = base(panel, "Ladera Ranch", srcdesc, yr)
    draw_water(d); draw_horno(d); draw_node(d)
    caption(d, cap)
    foot(d, "OC Survey / OCGIS Historic_Imagery_v2, LockRaster export")
    frames += hold(im, 4)

# ---- ACT 3 : what the federal record says -----------------------------------
frames += bigcard([("What the record says", 36, True)],
    ["USDA Bureau of Animal Industry, Circular 174, 1911.",
     "Held locally with full text and checksum."], sec=6)

nv = [v for v in MB["vatsRequired"] if v["herdHead"] == 25000][0]
frames += datacard("The operation", [
    "Every figure below is quoted or derived from documented parameters"], [
    ("Orange County status", "HEAVILY INFESTED"),
    ("Herd, documented peak", "25,000+ head"),
    ("Formula", "8 lb As2O3 / 500 gal"),
    ("Range cattle allowance", "up to 10 lb / 500 gal"),
    ("Dipping cadence, compulsory", "every 14-21 days"),
    ("Swim vat capacity", "2,088 gallons"),
    ("--", ""),
    ("Vats required simultaneously", f"{nv['vatsRequiredLow']} - {nv['vatsRequiredHigh']}"),
    ], foot_=["One vat cannot cycle a herd this size inside the mandated interval.",
              "An operation at this scale needed a NETWORK of vats across 200,000 acres."], sec=9)

frames += bigcard([("And one line that matters", 32, True)],
    ['"Such vats may be constructed of lumber or cement.',
     'The latter is preferable, as it has not the disadvantage of',
     'LEAKING, WHICH IS COMMON IN WOODEN VATS."',
     "",
     "- USDA Circular 174, 1911",
     "",
     "A leaking vat is a continuous point discharge into the ground",
     "beneath it, for as long as it is in service."], sec=9)

# ---- ACT 4 : the numbers ----------------------------------------------------
TE = TOT["totalElementalArsenic"]
frames += datacard("Into the ground — whole ranch", [
    "Drag-out over five years, plus vat charges abandoned at decommissioning"], [
    ("Low case", f"{TE['low']['lb']:,} lb"),
    ("Mid case", f"{TE['mid']['lb']:,} lb"),
    ("High case", f"{TE['high']['lb']:,} lb"),
    ("--", ""),
    ("Mid case, as tons", f"{TE['mid']['lb']/2000:,.0f} US tons"),
    ("As arsenic trioxide, mid", f"{TOT['totalAsArsenicTrioxide']['mid']['lb']:,} lb"),
    ], foot_=["Arsenic is an ELEMENT. It has no half-life and does not degrade.",
              "Mass introduced in 1907-1912 is still in this landscape unless hauled away."], sec=9)

frames += datacard("How much of that is in Ladera?", [
    "Ladera Ranch is ~4,200 acres — 2.1% of the ~200,000-acre ranch.",
    "But the mass concentrates at vats, so the answer forks on one unknown."], [
    ("SCENARIO A — no vat here", ""),
    ("   reaches Ladera", "56 - 334 lb"),
    ("   concentration", "0.007 - 0.042 mg/kg"),
    ("   vs CA background 1-11", "UNDETECTABLE"),
    ("--", ""),
    ("SCENARIO B — one vat here", ""),
    ("   in vat, pen and corrals", "1,338 - 7,949 lb"),
    ("   over ~2.25 hectares", "128 - 763 mg/kg"),
    ("   vs CA background 1-11", "10x - 700x"),
    ], foot_=["The two scenarios differ by ~1,000x. No further desk work resolves which.",
              "ONLY SOIL MEASUREMENT DISTINGUISHES THEM."], sec=12)

frames += datacard("Scale — the poisoned cup", [
    "A fatal oral dose of arsenic trioxide is 100-300 mg. Less than a pea.",
    "That is why it was the classical poison."], [
    ("Whole-ranch mass, mid case", "32 - 96 million"),
    ("   nominal lethal doses", ""),
    ], foot_=["THIS IS ARITHMETIC, NOT TOXICOLOGY. Soil-bound arsenic is only partly",
              "bioavailable; nobody ingests soil in gram quantities; and acute lethality is a",
              "different endpoint from chronic risk. It conveys SCALE — a large quantity of a",
              "non-degrading poison — and it is NOT a claim that anyone is being poisoned."],
    sec=11, tcol=(236,140,120))

# ---- ACT 5 : the searches, and their negatives ------------------------------
frames += bigcard([("So we went looking", 36, True)],
    ["If a vat network existed, some of it might be visible",
     "in the aerial record. 37,228 cells were searched across",
     "the 1929, 1938 and 1947 frames at 0.37 m per pixel."], sec=7)

frames += bigcard([("We found nothing.", 46, True)],
    ["No vat-like assembly inside this frame.",
     "",
     "That is a negative, and it is reported as one.",
     "",
     "It is weak evidence of absence: the throughput math says 3-7 vats",
     "across 200,000+ acres, and this frame is ~28 square kilometres.",
     "A backfilled timber trench may leave no surface expression by 1929."], sec=10)

frames += bigcard([("What the search DID find", 34, True)],
    [f"{ORCH['blocks']} orchard blocks, 1929-1947, row spacing 5-8 m.",
     "Lead arsenate was the era's standard orchard insecticide,",
     "so orchard ground is a second candidate arsenic source.",
     "",
     "They sit almost entirely OUTSIDE the community.",
     "Nearest block to any school: 2,760 m. To the drainage: 1,439 m.",
     "",
     "Orchard ground carries LEAD with the arsenic. Dip ground does not.",
     "That ratio is the diagnostic that separates the two."], sec=11)

# ---- ACT 6 : mechanism ------------------------------------------------------
def schematic(step, sec=5):
    im = Image.new("RGB", (SIZE, SIZE), NAVY); d = ImageDraw.Draw(im, "RGBA")
    d.rectangle([0, 0, SIZE, 8], fill=(150,60,42))
    d.text((SIZE//2, 34), "How soil-bound material moves during earthworks",
           font=F(30, True), fill=WHITE, anchor="ma")
    d.text((SIZE//2, 76), "CONCEPTUAL SCHEMATIC — not a measurement, not registered to real ground",
           font=F(17), fill=(232,150,130), anchor="ma")
    gy = 560
    d.line([80, gy, SIZE-80, gy], fill=(120,110,96), width=5)
    d.rectangle([80, gy, SIZE-80, gy+130], fill=(92,80,66,255))
    d.text((SIZE-96, gy+104), "soil column", font=F(14), fill=(190,182,170), anchor="ra")
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

frames += bigcard([("If it was there,", 34, False), ("earthworks would have moved it", 34, True)],
    ["Three mechanisms, all textbook, none measured here."], sec=6)
for st in (1, 2, 3, 4):
    frames += schematic(st, sec=4.5 if st < 4 else 8)

# ---- ACT 7 : the modern ground and where to test ----------------------------
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
        draw_horno(d, note=(mode == "water"))
        if mode == "water": draw_water(d)
        elif mode == "schools": draw_schools(d)
        else:
            draw_landmarks(d)
            d.text((36, MAPEND+12), "documented features only - nothing inferred",
                   font=F(15), fill=(150,156,168))
        caption(d, cap)
        foot(d, "OC Survey 2022")
        frames += hold(im, 3.5 if mode != "landmarks" else 6)

HRO = os.path.join(OUT, "hro_2004_aoi.png")
_cov = 1.0
_cj = os.path.join(OUT, "hro_2004_aoi.provenance.json")
if os.path.exists(_cj):
    _cov = json.load(open(_cj)).get("aoiCoverageFraction", 1.0)
COVERAGE_LINE = ("Complete coverage of the frame." if _cov > 0.995 else
                 f"Held tiles cover {_cov*100:.0f}% of the frame; the rest is left blank.")
if os.path.exists(HRO):
    im = Image.new("RGB", (SIZE, SIZE), NAVY); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, SIZE, 8], fill=RED)
    d.text((SIZE//2, 330), "January 2004", font=F(58, True), fill=WHITE, anchor="ma")
    d.text((SIZE//2, 410), "0.3 metre orthoimagery", font=F(28), fill=ACC, anchor="ma")
    for i, t in enumerate([
        "One hundred times finer than the satellite frames.",
        "Acquired inside the window this project had recorded as having no imagery.",
        COVERAGE_LINE]):
        d.text((SIZE//2, 480+i*32), t, font=F(18), fill=MUT, anchor="ma")
    frames += hold(im, 4)

    src_ = Image.open(HRO).convert("RGB")
    a = np.asarray(src_).copy()
    a[(a.sum(axis=2) == 0)] = NODATA
    panel = Image.fromarray(a).resize((MAP, MAP), Image.LANCZOS)
    for mode, cap in [
        ("plain", ["USGS High Resolution Orthoimagery, 21 January 2004.",
                   "North built out. Centre and south still raw graded pad and road."]),
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
            draw_all_water(d, w=5); draw_parks(d, labels=False)
        else:
            draw_all_water(d, note=False, w=4)
            draw_parks(d, note=False, labels=False)
            draw_water(d, note=False); draw_node(d, note=False)
            draw_schools(d, with_dist=True)
            d.text((36, MAPEND+12), "○ schools, with distance to the drainage   ◎ 1948 ranch node",
                   font=F(15), fill=MUT)
            d.text((36, MAPEND+34), "— drainage   ▢ parks   ○ 1968 water bodies", font=F(15), fill=MUT)
        caption(d, cap)
        foot(d, "USGS EarthExplorer - High Resolution Orthoimagery 2004-01-21")
        frames += hold(im, 6)

# ---- ACT 8 : one point on the ground ---------------------------------------
im = Image.new("RGB", (SIZE, SIZE), NAVY); d = ImageDraw.Draw(im)
d.rectangle([0, 0, SIZE, 8], fill=RED)
d.text((SIZE//2, 330), "One point on the ground", font=F(40, True), fill=WHITE, anchor="ma")
for i, t in enumerate([
    "33.55505, -117.65492  -  Trabuco Creek corridor", "",
    "A single structure drawn by a USGS surveyor on the 1948 sheet.",
    "The only documented point of human construction in the footprint.", "",
    "What it was is unrecorded. It is NOT identified as a dip vat."]):
    d.text((SIZE//2, 420+i*34), t, font=F(20 if i == 0 else 18),
           fill=ACC if i == 0 else MUT, anchor="ma")
frames += hold(im, 5)

for fn, yr, cap in [
 ("z1_ranch_1929.jpg", "1929",
  ["Creek corridor with unimproved dirt tracks converging through it.",
   "Twelve years after compulsory dipping ended."]),
 ("z1_ranch_1937.jpg", "1937-38",
  ["The sharpest view ever taken of this spot. Tracks, trees and the",
   "channel are legible. No vat, pen or chute is resolvable."]),
 ("z1_ranch_2022_modern.jpg", "2022",
  ["The same 100 metres today. Built community and preserved corridor."]),
]:
    p = os.path.join(AER, fn)
    if not os.path.exists(p): continue
    zi = Image.open(p).convert("RGB").resize((MAP, MAP), Image.LANCZOS)
    im, d = base(zi, "The 1948 structure", "same 100 m of ground", yr)
    cx, cy = MAP//2, MAP//2
    d.ellipse([OXm+cx-26, TOPBAR+cy-26, OXm+cx+26, TOPBAR+cy+26], outline=NODE, width=3)
    caption(d, cap)
    foot(d, "OC Survey / OCGIS")
    frames += hold(im, 5)

# ---- ACT 9 : water, and what is left --------------------------------------
frames += bigcard([("We also checked the water", 34, True)],
    ["Ladera Ranch drinking water is 100% imported —",
     "Colorado River and State Water Project, treated hundreds of miles away.",
     "",
     "During construction it was ~99.8% imported. The district's one well",
     "served a single laboratory customer, and sits in the wrong basin.",
     "",
     "Arsenic is tested by law in every year on record: ND to 2.3 ppb,",
     "against a limit of 10. A local aquifer pathway to the tap did not exist."], sec=11)

p1 = sum(1 for t in TGT if t["p"] == 1)
frames += bigcard([("Where to test", 44, True)],
    [f"{len(TGT)} ranked ground targets, {p1} of them Priority 1.",
     "",
     "Chosen where cattle physically concentrated — the 1968 stock-water",
     "survey — weighted by proximity to the drainage, which is both a",
     "congregation point and a depositional trap.",
     "",
     "Depth-resolved cores. Arsenic AND lead. Matched comparison site.",
     "Accredited lab, blinded."], sec=11)

frames += bigcard([("A negative result", 34, False), ("is a real result", 44, True)],
    ["If cores from these zones come back at background,",
     "that materially weakens the hypothesis for this community —",
     "and saying so plainly is what makes everything else credible.",
     "",
     "A study that can only come back positive is not a study."], sec=10)

frames += bigcard([("PHASE 2", 56, True), ("Findings to date", 30, False)],
    ["Built entirely from public records: USDA Bureau of Animal Industry,",
     "USGS, NASA Landsat, OC Survey, OC Flood Control, SMWD.",
     "",
     "No vat has been located. No soil has been sampled.",
     "Nothing here establishes that any exposure or illness has any cause.",
     "",
     "The reported pattern warrants investigation.",
     "The available evidence does not yet establish causation."], sec=12)

print(f"composed {len(frames)} frames ({len(frames)/FPS:.0f}s)")
mp4 = os.path.join(OUT, "ladera_PHASE2_master.mp4")
imageio.mimsave(mp4, frames, fps=FPS, quality=9, macro_block_size=1)
print("wrote", mp4, f"{os.path.getsize(mp4)/1e6:.1f} MB")
