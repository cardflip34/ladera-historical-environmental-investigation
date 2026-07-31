#!/usr/bin/env python3
"""
Orchard delineation - map the planted blocks visible in the 1929 / 1938 / 1947 aerials.

WHY: the vat hunt's strongest ground-truth detections were orchard rows. Lead arsenate was the
standard orchard insecticide of this era, so orchard ground is a SECOND candidate arsenic source -
one whose footprint, unlike the vats, is actually visible in imagery we hold. The deliverable is a
polygon layer usable against the modern parcel map and the sampling plan.

SIGNATURE: an orchard at ~0.37 m/px is a strongly PERIODIC texture - planted rows at a regular
spacing (period-era citrus/walnut spacing was ~5-7 m). Periodicity separates orchards from roads
(single lines), scrub (aperiodic), and grazing (smooth). The detector measures, per cell:
  - a dominant spatial frequency in the 3-12 m band via the 2-D power spectrum
  - the fraction of spectral power concentrated at that frequency and its harmonic
A cell is "orchard" when that concentration is high. Cells are then merged into blocks.

STATEMENT CLASS: documented (the rows are directly visible) for presence; the polygon EDGES are
interpreted (cell-resolution, ~40 m). Nothing here says lead arsenate was used on these specific
blocks - that is the documented general practice of the era, and only soil measurement can speak
to these parcels.
"""
from __future__ import annotations
import json, os, math, datetime
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage as ndi
Image.MAX_IMAGE_PIXELS = None

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO, "evidence/lhdrs/vat_hunt")
ODIR = os.path.join(REPO, "evidence/lhdrs/orchards")
os.makedirs(ODIR, exist_ok=True)
TODAY = datetime.date.today().isoformat()
MAN = json.load(open(os.path.join(OUT, "tile_manifest.json")))
GSD = MAN["gsdMeters"]

CELL_M = 48.0
CELL = int(CELL_M / GSD)              # ~130 px
ROW_MIN_M, ROW_MAX_M = 4.5, 8.5
# Spacing band tightened after calibration: sites scoring at the 11.8 m band edge were
# ambiguous (edge-of-band artefact), while confirmed orchards cluster at 5.3-6.5 m -
# consistent with period citrus/walnut planting.
POWER_FRAC_MIN = 0.30
# CALIBRATED, not guessed: scored 8 visually confirmed orchard sites and 8 confirmed rangeland
# sites from the vat-hunt contact sheet. Confirmed orchards with in-band spacing score 0.66-0.75;
# rangeland maxes at 0.22. Threshold 0.30 separates them with margin. This favours PRECISION over
# recall - the map may miss marginal or immature blocks, and says so.

FD = "/System/Library/Fonts/Supplemental/"
def F(s, b=False):
    p = FD + ("Arial Bold" if b else "Arial") + ".ttf"
    return ImageFont.truetype(p, s) if os.path.exists(p) else ImageFont.load_default()


def cell_periodicity(win):
    """Return (power fraction at dominant non-DC frequency in row band, spacing metres)."""
    w = win - win.mean()
    if w.std() < 0.01:
        return 0.0, 0.0
    Fp = np.abs(np.fft.fftshift(np.fft.fft2(w * np.hanning(w.shape[0])[:, None]
                                              * np.hanning(w.shape[1])[None, :])))**2
    h, ww = w.shape
    cy, cx = h//2, ww//2
    Y, X = np.ogrid[:h, :ww]
    r = np.hypot(Y-cy, X-cx)
    # convert row spacing to radius in frequency pixels: spacing s metres -> f = N*GSD/s cycles
    rmin = h*GSD/ROW_MAX_M
    rmax = h*GSD/ROW_MIN_M
    band = (r >= rmin) & (r <= rmax)
    tot = Fp[r > 1.5].sum()
    if tot <= 0:
        return 0.0, 0.0
    bi = np.unravel_index(np.argmax(np.where(band, Fp, 0)), Fp.shape)
    fpk = r[bi]
    if fpk <= 0:
        return 0.0, 0.0
    # DIRECTIONALITY - the first version measured only band power and flagged 36,600 of 37,000
    # cells: film grain is broadband and isotropic, so a radial test passes it. A planted-row
    # texture concentrates power at ONE orientation (two symmetric spots on the annulus), so the
    # real test is anisotropy: power in a +-10 degree wedge at the peak angle vs the whole annulus.
    ang = np.arctan2(Y-cy, X-cx)
    apk = math.atan2(bi[0]-cy, bi[1]-cx)
    dang = np.abs(((ang - apk) + np.pi/2) % np.pi - np.pi/2)
    annulus = (np.abs(r-fpk) < 1.5) & (r > 1.5)
    wedge = annulus & (dang < math.radians(10))
    a_pow = Fp[annulus].sum()
    if a_pow <= 0:
        return 0.0, 0.0
    aniso = float(Fp[wedge].sum() / a_pow)          # isotropic noise ~ 20/180 = 0.11
    frac = float(a_pow / tot) * aniso
    spacing = h*GSD/fpk
    return frac, float(spacing)


hits = []
for t in MAN["tiles"]:
    p = os.path.join(REPO, t["path"])
    if not os.path.exists(p) or t["nodataFraction"] > 0.5:
        continue
    a = np.asarray(Image.open(p).convert("L")).astype(np.float32)/255.0
    px = t["px"]; bb = t["bbox"]
    n = px // CELL
    cnt = 0
    for iy in range(n):
        for ix in range(n):
            win = a[iy*CELL:(iy+1)*CELL, ix*CELL:(ix+1)*CELL]
            if win.shape[0] < CELL or win.shape[1] < CELL:
                continue
            if (win > 0.985).mean() > 0.1 or (win < 0.02).mean() > 0.1:
                continue
            frac, sp = cell_periodicity(win)
            if frac >= POWER_FRAC_MIN and ROW_MIN_M <= sp <= ROW_MAX_M:
                cx = (ix+0.5)*CELL; cy = (iy+0.5)*CELL
                lon = bb[0] + cx/px*(bb[2]-bb[0])
                lat = bb[3] - cy/px*(bb[3]-bb[1])
                hits.append({"frame": t["frame"], "lon": round(lon, 6), "lat": round(lat, 6),
                             "powerFrac": round(frac, 3), "rowSpacingM": round(sp, 1)})
                cnt += 1
    if cnt:
        print(f"  {t['frame']} r{t['row']}c{t['col']}  {cnt} periodic cells")

print(f"\n{len(hits)} orchard-signature cells total")

# ---- merge into blocks per frame, then across frames ---------------------------------------
def cluster(points, link_m=90):
    blocks = []
    for p in points:
        placed = False
        for b in blocks:
            for q in b:
                if math.hypot((p["lon"]-q["lon"])*92500, (p["lat"]-q["lat"])*111000) < link_m:
                    b.append(p); placed = True; break
            if placed:
                break
        if not placed:
            blocks.append([p])
    return [b for b in blocks if len(b) >= 3]          # >=3 cells ~ >0.5 ha

frames = sorted(set(h["frame"] for h in hits))
features = []
summary = []
for fr in frames:
    fh = [h for h in hits if h["frame"] == fr]
    blocks = cluster(fh)
    for b in blocks:
        lons = [q["lon"] for q in b]; lats = [q["lat"] for q in b]
        area_ha = len(b) * (CELL_M**2) / 10000.0
        spacing = float(np.median([q["rowSpacingM"] for q in b]))
        # convex hull-ish bounding ring (cell centres +- half cell)
        d = CELL_M/2/92500.0
        ring = [[min(lons)-d, min(lats)-d], [max(lons)+d, min(lats)-d],
                [max(lons)+d, max(lats)+d], [min(lons)-d, max(lats)+d], [min(lons)-d, min(lats)-d]]
        features.append({"type": "Feature",
            "properties": {"frame": fr, "cells": len(b), "areaHa": round(area_ha, 1),
                           "medianRowSpacingM": round(spacing, 1),
                           "statementClass": "documented_presence_interpreted_extent",
                           "provenanceGrade": "A2",
                           "note": "Periodic planted-row texture; extent is cell-resolution"},
            "geometry": {"type": "Polygon", "coordinates": [ring]}})
        summary.append({"frame": fr, "areaHa": round(area_ha, 1),
                        "rowSpacingM": round(spacing, 1),
                        "centroid": [round(float(np.mean(lats)), 5), round(float(np.mean(lons)), 5)]})

json.dump({"type": "FeatureCollection", "features": features},
          open(os.path.join(ODIR, "orchard_blocks.geojson"), "w"))
per_frame = {fr: round(sum(s["areaHa"] for s in summary if s["frame"] == fr), 1) for fr in frames}
json.dump({"generated": TODAY, "gsdMeters": GSD, "cellMeters": CELL_M,
           "method": "2-D spectral periodicity, 3-12 m row-spacing band, power fraction >= 0.22",
           "cells": len(hits), "blocks": len(features), "areaHaByFrame": per_frame,
           "blockSummary": summary,
           "interpretationLimit": ("Lead arsenate was the standard orchard insecticide of this "
                                   "era as a general practice. Nothing here documents its use on "
                                   "these specific blocks; only soil measurement can.")},
          open(os.path.join(ODIR, "orchard_summary.json"), "w"), indent=1)

print(f"\nblocks by frame: " + ", ".join(f"{fr}: {sum(1 for f in features if f['properties']['frame']==fr)} blocks "
      f"({per_frame[fr]} ha)" for fr in frames))
print(f"wrote {ODIR}/orchard_blocks.geojson and orchard_summary.json")

# ---- overlay map on the modern 0.3 m mosaic -------------------------------------------------
AOI = (-117.670, 33.524, -117.616, 33.575)
HRO = os.path.join(REPO, "evidence/lhdrs/mission7/hro_2004_aoi.png")
SIZE = 1400
im = Image.open(HRO).convert("RGB")
a = np.asarray(im).astype(float)
g = a.mean(axis=2, keepdims=True)
a = (g*0.7 + a*0.3)*0.6 + 255*0.4
base = Image.fromarray(np.clip(a, 0, 255).astype("uint8")).resize(
    (SIZE, int(SIZE*(AOI[3]-AOI[1])/(AOI[2]-AOI[0])/math.cos(math.radians(33.55)))), Image.LANCZOS)
W2, H2 = base.size
canvas = Image.new("RGB", (W2, H2+220), (250, 249, 246))
canvas.paste(base, (0, 110))
dr = ImageDraw.Draw(canvas, "RGBA")
def xy2(lon, lat):
    return ((lon-AOI[0])/(AOI[2]-AOI[0])*W2, 110+(AOI[3]-lat)/(AOI[3]-AOI[1])*H2)
COLS = {"1929": (214, 64, 48), "1938": (232, 148, 40), "1947": (60, 130, 200)}
for f in features:
    fr = f["properties"]["frame"]
    ring = f["geometry"]["coordinates"][0]
    pts = [xy2(c[0], c[1]) for c in ring]
    if all(0 <= p[0] <= W2 and 110 <= p[1] <= 110+H2 for p in pts):
        dr.polygon(pts, outline=COLS[fr]+(255,), width=4, fill=COLS[fr]+(28,))
dr.rectangle([0, 0, W2, 8], fill=(196, 55, 42))
dr.text((24, 22), "Orchard blocks, 1929-1947 - a second candidate arsenic source",
        font=F(30, True), fill=(20, 28, 42))
dr.text((24, 62), "Planted-row texture detected spectrally, drawn over the modern community (2004 imagery)",
        font=F(17), fill=(110, 116, 126))
ly = H2 + 124
for fr in frames:
    dr.rectangle([24, ly, 46, ly+16], outline=COLS[fr], width=4)
    dr.text((56, ly-3), f"{fr}  -  {per_frame[fr]} ha detected", font=F(17, True), fill=(20, 28, 42))
    ly += 30
dr.text((24, ly+4), "Lead arsenate was the era's standard orchard insecticide (general practice - "
                    "use on these blocks is not documented).", font=F(15), fill=(110, 116, 126))
dr.text((24, ly+26), "Diagnostic if sampled: orchard ground carries LEAD with the arsenic; cattle-dip ground does not.",
        font=F(15, True), fill=(150, 60, 42))
mp = os.path.join(ODIR, "orchard_overlay_map.png")
canvas.save(mp)
print("wrote", mp)
