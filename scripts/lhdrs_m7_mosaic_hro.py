#!/usr/bin/env python3
"""
Mission 7 - mosaic the 2004-01-21 High Resolution Orthoimagery tiles to the canonical AOI.

Source: USGS High Resolution Orthoimagery, 0.3 m/px, EPSG:26911, acquired via EarthExplorer.
This is the finest imagery in the whole project - 100x finer than the 30 m Landsat series - and it
falls inside the 1999-2004 window the Mission 7 plan had recorded as having no coverage at all.

Output: a single AOI-aligned RGB image in EPSG:4326, plus a coverage report stating honestly how
much of the AOI the held tiles actually cover.
"""
from __future__ import annotations
import os, glob, json, datetime, hashlib
import numpy as np
import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling, transform_bounds
from rasterio.merge import merge

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO, "evidence/lhdrs/mission7")
os.makedirs(OUT, exist_ok=True)
AOI = (-117.670, 33.524, -117.616, 33.575)
SRC = glob.glob(os.path.expanduser("~/Downloads/hro_extract/**/*.tif"), recursive=True)
TODAY = datetime.date.today().isoformat()

print(f"tiles found: {len(SRC)}")
srcs = [rasterio.open(p) for p in sorted(SRC)]
for s in srcs:
    b = transform_bounds(s.crs, "EPSG:4326", *s.bounds)
    print(f"  {os.path.basename(s.name):<24} {[round(v,4) for v in b]}")

mos, tf = merge(srcs)
crs = srcs[0].crs
print(f"\nmosaic: {mos.shape} in {crs}")

# reproject the mosaic to EPSG:4326 on a grid covering exactly the AOI
W = 3000
H = int(W * (AOI[3]-AOI[1]) / (AOI[2]-AOI[0]))
dst_tf = rasterio.transform.from_bounds(*AOI, W, H)
dst = np.zeros((3, H, W), dtype="uint8")
for i in range(3):
    reproject(source=mos[i], destination=dst[i],
              src_transform=tf, src_crs=crs,
              dst_transform=dst_tf, dst_crs="EPSG:4326",
              resampling=Resampling.bilinear)
for s in srcs:
    s.close()

covered = float((dst.sum(axis=0) > 0).mean())
print(f"AOI coverage by held tiles: {covered*100:.1f}%")

from PIL import Image
Image.MAX_IMAGE_PIXELS = None
img = Image.fromarray(dst.transpose(1, 2, 0))
p = os.path.join(OUT, "hro_2004_aoi.png")
img.save(p)
sha = hashlib.sha256(open(p, "rb").read()).hexdigest()
print("wrote", p, f"{os.path.getsize(p)/1e6:.1f} MB")

json.dump({
    "generated": TODAY,
    "source": "USGS High Resolution Orthoimagery, 2004-01-21, via EarthExplorer",
    "provenanceGrade": "A+", "statementClass": "documented",
    "nativeResolutionMeters": 0.3, "sourceCRS": "EPSG:26911",
    "tileCount": len(SRC), "tiles": [os.path.basename(x) for x in sorted(SRC)],
    "aoi": list(AOI), "outputSize": [W, H], "aoiCoverageFraction": round(covered, 4),
    "sha256": sha,
    "limitation": ("Held tiles do not cover the entire AOI. Uncovered area is rendered as nodata, "
                   "never as ground. 0.3 m is the NATIVE tile resolution; the AOI render is "
                   "downsampled to fit the video grid."),
}, open(os.path.join(OUT, "hro_2004_aoi.provenance.json"), "w"), indent=1)
