#!/usr/bin/env python3
"""
Every held era of imagery, cropped to the same ground: the stock-water sources in the Trabuco
corridor near the 1948 node and the observed concrete structure.

CENTRE: sampling target #6 - the 9,111 m2 water body mapped by the 1968 USGS field survey at
33.55857, -117.65281, 42 m off the drainage - with the 1948 node 437 m south-southwest. The crop
is sized to hold both, plus nearby 1968 water points.

Eras: 1929, 1937-38, 1947(comp), 1953, 1960, 1969, 1980, 1990 (OC Survey), Jan 2004 (USGS 0.3 m),
2025 (OC Eagle 1 ft). Same window every frame; 1968 water points and the node overlaid on all.
"""
from __future__ import annotations
import json, os, math, datetime
import numpy as np
from PIL import Image, ImageDraw, ImageFont
Image.MAX_IMAGE_PIXELS = None

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AER = os.path.join(REPO, "research/historical_imagery/oc_aerials")
OCF = os.path.join(REPO, "evidence/lhdrs/mission7/oc_frames")
M7  = os.path.join(REPO, "evidence/lhdrs/mission7")
OUTD = os.path.join(REPO, "evidence/lhdrs/field_observations")
TODAY = datetime.date.today().isoformat()

HIST_BBOX = (-117.680, 33.520, -117.616, 33.575)
AOI       = (-117.670, 33.524, -117.616, 33.575)

# window: centred between target #6 and the node, wide enough for both plus margin
CTR = (-117.65370, 33.55650)
HALF_M = 520.0                      # half-width metres
dlon = HALF_M/92500.0; dlat = HALF_M/111000.0
WIN = (CTR[0]-dlon, CTR[1]-dlat, CTR[0]+dlon, CTR[1]+dlat)

NODE = (-117.65492, 33.55505)
TGT6 = (-117.65281, 33.55857)
water = json.load(open(os.path.join(REPO, "research/historical_imagery/topo1968_water.json")))
WPTS = [(w["lon"], w["lat"], w.get("area_m2", 0)) for w in water
        if WIN[0] <= w["lon"] <= WIN[2] and WIN[1] <= w["lat"] <= WIN[3]]

FD = "/System/Library/Fonts/Supplemental/"
def F(s, b=False):
    p = FD + ("Arial Bold" if b else "Arial") + ".ttf"
    return ImageFont.truetype(p, s) if os.path.exists(p) else ImageFont.load_default()

TILE = 560
def crop_win(img, bbox):
    w, h = img.size
    x0 = (WIN[0]-bbox[0])/(bbox[2]-bbox[0])*w; x1 = (WIN[2]-bbox[0])/(bbox[2]-bbox[0])*w
    y0 = (bbox[3]-WIN[3])/(bbox[3]-bbox[1])*h; y1 = (bbox[3]-WIN[1])/(bbox[3]-bbox[1])*h
    return img.crop((int(x0), int(y0), int(x1), int(y1))).resize((TILE, TILE), Image.LANCZOS)

def annotate(tile, year, note):
    d = ImageDraw.Draw(tile)
    def xy(lon, lat):
        return ((lon-WIN[0])/(WIN[2]-WIN[0])*TILE, (WIN[3]-lat)/(WIN[3]-WIN[1])*TILE)
    for lon, lat, area in WPTS:
        x, y = xy(lon, lat)
        r = max(7, min(22, int(math.sqrt(max(area, 200))/6)))
        d.ellipse([x-r, y-r, x+r, y+r], outline=(0, 200, 230), width=3)
    x, y = xy(*TGT6)
    d.ellipse([x-26, y-26, x+26, y+26], outline=(230, 70, 50), width=4)
    x, y = xy(*NODE)
    d.line([x-16, y, x+16, y], fill=(200, 90, 220), width=3)
    d.line([x, y-16, x, y+16], fill=(200, 90, 220), width=3)
    d.rectangle([0, TILE-58, TILE, TILE], fill=(12, 16, 24))
    d.text((10, TILE-52), year, font=F(24, True), fill=(236, 160, 70))
    d.text((10, TILE-24), note, font=F(13), fill=(200, 205, 214))
    return tile

FRAMES = [
    (os.path.join(AER, "1929.jpg"),          HIST_BBOX, "1929",    "open range - pond band visible along corridor"),
    (os.path.join(AER, "1937.jpg"),          HIST_BBOX, "1937-38", "sharpest frame - 1.15 ft/px"),
    (os.path.join(AER, "1946b_filled.jpg"),  HIST_BBOX, "1947",    "composite (NW quarter 1938)"),
    (os.path.join(OCF, "oc_1953_oid357.jpg"),HIST_BBOX, "1953",    "countywide series"),
    (os.path.join(OCF, "oc_1960_oid343.jpg"),HIST_BBOX, "1960",    "countywide series"),
    (os.path.join(OCF, "oc_1969_oid315.jpg"),HIST_BBOX, "1969",    "one year after the USGS water survey"),
    (os.path.join(OCF, "oc_1980_oid320.jpg"),HIST_BBOX, "1980",    "countywide series"),
    (os.path.join(OCF, "oc_1990_oid319.jpg"),HIST_BBOX, "1990",    "pre-entitlement"),
    (os.path.join(M7,  "hro_2004_aoi.png"),  AOI,       "Jan 2004","USGS 0.3 m - during build-out"),
    (os.path.join(M7,  "oc_2025_aoi.jpg"),   AOI,       "2025",    "OC Eagle 1 ft - present day"),
]

tiles = []
for path, bbox, yr, note in FRAMES:
    if not os.path.exists(path):
        print("missing:", path); continue
    im = Image.open(path).convert("RGB")
    tiles.append(annotate(crop_win(im, bbox), yr, note))

COLS = 5
ROWS = math.ceil(len(tiles)/COLS)
PAD = 8; HDR = 150
W = COLS*TILE + (COLS+1)*PAD
H = HDR + ROWS*TILE + (ROWS+1)*PAD + 120
sheet = Image.new("RGB", (W, H), (250, 249, 246))
d = ImageDraw.Draw(sheet)
d.rectangle([0, 0, W, 8], fill=(196, 58, 44))
d.text((24, 26), "The same ground, 1929-2025: stock-water sources near the node and the concrete structure",
       font=F(34, True), fill=(23, 30, 43))
d.text((24, 76), f"Window ~1.04 x 1.04 km centred {CTR[1]:.5f}, {CTR[0]:.5f}  ·  red = sampling "
                 "target #6 (9,111 m2 pond, 42 m off the drainage)  ·  cyan = 1968 USGS water "
                 "points  ·  purple + = 1948 structure", font=F(16), fill=(110, 116, 126))
d.text((24, 102), "The 1968 water points were mapped by federal field survey - they are the "
                  "targeting layer, drawn identically on every era so persistence is visible.",
       font=F(16), fill=(110, 116, 126))
for i, t in enumerate(tiles):
    r, c = divmod(i, COLS)
    sheet.paste(t, (PAD + c*(TILE+PAD), HDR + PAD + r*(TILE+PAD)))
d.text((24, H-96), "How target #6 was chosen (independent of any field find): 1968 USGS field-survey water body (A1)  ->  cattle congregate at water daily  ->  "
                   "42 m from the mapped drainage = congregation point AND sediment trap.", font=F(16), fill=(70, 78, 92))
d.text((24, H-70), "The concrete structure was found AFTERWARDS, near this cluster. Convergence of independent layers - 1968 water mapping, the 1948 structure, "
                   "and a physical find - is what makes this ground the top sampling priority.", font=F(16), fill=(70, 78, 92))
d.text((24, H-38), f"LHDRS · generated {TODAY} · imagery A+/A1 · water points A1 (USGS 1968) · no vat is marked anywhere in this figure",
       font=F(14), fill=(140, 146, 158))

p = os.path.join(OUTD, "water_sources_timeseries_node_area.png")
sheet.save(p)
print("wrote", p, f"{os.path.getsize(p)/1048576:.1f} MB, {len(tiles)} eras, {len(WPTS)} water points in window")
