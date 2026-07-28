#!/usr/bin/env python3
"""
Mission 7 / Phase 3b - SPATIAL grading progression, 1997-2006.

The Phase 3a series answered "how much of the area was disturbed each year." This answers
"WHERE" - producing a per-year bare-soil mask clipped to the Ladera Ranch CDP, plus a ten-panel
progression figure showing the grading front move across the community.

Same provenance and limits as Phase 3a:
  provenanceGrade A+ (USGS/NASA Landsat C2 L2) · statementClass INTERPRETED (NDVI threshold)
  30 m pixels ~ one pixel per residential lot. NOT parcel-level. NOT a contamination/dust/exposure
  product. Bare soil has multiple causes; green-season scenes reduce but do not remove ambiguity.
"""
from __future__ import annotations
import json, os, ssl, glob, datetime, urllib.request, urllib.parse
import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO, "evidence/lhdrs/mission7")
MAPS = os.path.join(OUT, "grading_maps")
os.makedirs(MAPS, exist_ok=True)
BBOX = [-117.659017, 33.526791, -117.624136, 33.575504]
NDVI_BARE = 0.20
CTX = ssl.create_default_context()
UA = {"User-Agent": "LHDRS-Mission7/1.0", "Content-Type": "application/json"}
STAC = "https://planetarycomputer.microsoft.com/api/stac/v1/search"
SIGN = "https://planetarycomputer.microsoft.com/api/sas/v1/sign?href="
TODAY = datetime.date.today().isoformat()


def post(url, body):
    r = urllib.request.Request(url, headers=UA, data=json.dumps(body).encode())
    with urllib.request.urlopen(r, timeout=60, context=CTX) as f:
        return json.load(f)


def sign(h):
    r = urllib.request.Request(SIGN + urllib.parse.quote(h, safe=""), headers={"User-Agent": UA["User-Agent"]})
    with urllib.request.urlopen(r, timeout=60, context=CTX) as f:
        return json.load(f)["href"]


# reuse the exact scenes Phase 3a selected, so the two products cannot disagree
prev = sorted(glob.glob(os.path.join(OUT, "grading_progression_landsat_*.json")))[-1]
series = [r for r in json.load(open(prev))["series"] if "sceneId" in r]
print(f"using {len(series)} scenes selected by Phase 3a ({os.path.basename(prev)})\n")

import rasterio
from rasterio.warp import transform_bounds
from rasterio.windows import from_bounds
from rasterio.features import rasterize
from rasterio.transform import from_bounds as tf_from_bounds

# CDP mask
cdp = json.load(open(os.path.join(REPO, "data/development/ladera_ranch_cdp.geojson")))
geoms = [f["geometry"] for f in cdp["features"]]

panels = []
for r in series:
    d = post(STAC, {"collections": ["landsat-c2-l2"], "bbox": BBOX,
                    "datetime": f"{r['date']}T00:00:00Z/{r['date']}T23:59:59Z", "limit": 20})
    feat = next((f for f in d["features"] if f["id"] == r["sceneId"]), None)
    if feat is None:
        print(f"  {r['year']}: scene {r['sceneId']} not refound, skipping"); continue

    def band(n):
        return rasterio.open(sign(feat["assets"][n]["href"]))

    with band("red") as rr, band("nir08") as nn, band("qa_pixel") as qq:
        b = transform_bounds("EPSG:4326", rr.crs, *BBOX)
        w = from_bounds(*b, transform=rr.transform)
        red = rr.read(1, window=w).astype("float32") * 0.0000275 - 0.2
        nir = nn.read(1, window=from_bounds(*b, transform=nn.transform)).astype("float32") * 0.0000275 - 0.2
        qa = qq.read(1, window=from_bounds(*b, transform=qq.transform)).astype("uint16")
        crs = rr.crs
        win_tf = rr.window_transform(w)

    bad = ((qa & 1) | (qa & 2) | (qa & 8) | (qa & 16)) > 0
    valid = (~bad) & (red > -0.1) & (nir > -0.1)
    ndvi = np.where(valid, (nir - red) / np.maximum(nir + red, 1e-6), np.nan)

    # CDP mask in the scene's CRS/grid
    from rasterio.warp import transform_geom
    gs = [transform_geom("EPSG:4326", crs.to_string(), g) for g in geoms]
    mask = rasterize(gs, out_shape=ndvi.shape, transform=win_tf, fill=0, default_value=1).astype(bool)

    bare = (ndvi < NDVI_BARE) & valid & mask
    inside = mask & valid
    pct = 100.0 * bare.sum() / max(1, inside.sum())
    panels.append({"year": r["year"], "date": r["date"], "bare": bare, "mask": mask,
                   "valid": valid, "pct": pct})
    print(f"  {r['year']}  {r['date']}  in-CDP bare = {pct:5.1f}%   grid={ndvi.shape}")

# ---------------- render ten-panel progression ----------------
from PIL import Image, ImageDraw, ImageFont
FD = "/System/Library/Fonts/Supplemental/"


def F(s, b=False):
    p = FD + ("Arial Bold" if b else "Arial") + ".ttf"
    return ImageFont.truetype(p, s) if os.path.exists(p) else ImageFont.load_default()


h, w = panels[0]["bare"].shape
SC = max(3, int(260 / max(h, w)))
pw, ph = w * SC, h * SC
COLS, PAD, TOPB = 5, 18, 150
rows = (len(panels) + COLS - 1) // COLS
W = COLS * pw + (COLS + 1) * PAD
H = TOPB + rows * (ph + 46) + PAD + 190
im = Image.new("RGB", (W, H), (250, 249, 246))
dr = ImageDraw.Draw(im)

dr.text((PAD, 30), "Where the ground was disturbed, 1997 to 2006", font=F(30, True), fill=(22, 35, 58))
dr.text((PAD, 72), "Orange = bare or recently disturbed soil inside Ladera Ranch (Landsat NDVI, 30 m)",
        font=F(17), fill=(110, 116, 126))
dr.rounded_rectangle([PAD, 102, PAD + 128, 130], 6, fill=(43, 120, 58))
dr.text((PAD + 14, 108), "A+  imagery", font=F(14, True), fill=(255, 255, 255))
dr.rounded_rectangle([PAD + 138, 102, PAD + 288, 130], 6, fill=(178, 120, 40))
dr.text((PAD + 152, 108), "INTERPRETED", font=F(14, True), fill=(255, 255, 255))

for i, p in enumerate(panels):
    cx, cy = i % COLS, i // COLS
    ox, oy = PAD + cx * (pw + PAD), TOPB + cy * (ph + 46)
    rgb = np.zeros((h, w, 3), dtype=np.uint8)
    rgb[...] = (238, 238, 234)                    # outside CDP
    rgb[p["mask"]] = (196, 214, 190)              # inside, vegetated
    rgb[p["bare"]] = (186, 104, 46)               # disturbed
    rgb[p["mask"] & ~p["valid"]] = (150, 150, 156)  # cloud/no-data
    tile = Image.fromarray(rgb).resize((pw, ph), Image.NEAREST)
    im.paste(tile, (ox, oy))
    dr.rectangle([ox, oy, ox + pw, oy + ph], outline=(205, 208, 214))
    dr.text((ox, oy + ph + 6), f"{p['year']}", font=F(19, True), fill=(22, 35, 58))
    dr.text((ox + 52, oy + ph + 10), f"{p['date'][5:]}   {p['pct']:.0f}% disturbed",
            font=F(14), fill=(110, 116, 126))

ly = TOPB + rows * (ph + 46) + 12
dr.line([PAD, ly, W - PAD, ly], fill=(222, 226, 232))
dr.text((PAD, ly + 14), "Read this with the maps:", font=F(16, True), fill=(22, 35, 58))
for i, t in enumerate([
    "30 m pixels: roughly ONE PIXEL PER LOT. Individual homes are not resolvable and no parcel-level claim can be drawn from this.",
    "Bare soil is not only grading. Senescence, fire and fallow ground read alike. Green-season scenes reduce, not remove, this.",
    "1998 was a wet El Nino year: its low disturbance is likely climate, not land use. 2006 is a February scene and not directly comparable.",
    "Ground disturbance only. Not a contamination, dust or exposure product, and it implies nothing about health.",
]):
    dr.text((PAD, ly + 40 + i * 22), "- " + t, font=F(14), fill=(70, 78, 90))
dr.text((PAD, H - 30), f"Landsat C2 L2, USGS/NASA via Microsoft Planetary Computer  ·  generated {TODAY}",
        font=F(12), fill=(110, 116, 126))

p = os.path.join(OUT, "grading_progression_maps.png")
im.save(p)
print(f"\nwrote {p}")

json.dump({"generated": TODAY, "provenanceGrade": "A+", "statementClass": "interpreted",
           "resolutionMeters": 30,
           "inCdpDisturbedPct": {str(x["year"]): round(x["pct"], 1) for x in panels}},
          open(os.path.join(OUT, "grading_maps_summary.json"), "w"), indent=1)
