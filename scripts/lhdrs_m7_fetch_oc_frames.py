#!/usr/bin/env python3
"""
Mission 7 - pull COMPLETE-coverage frames from the OC Historic_Imagery ImageServer.

The 1995/1998 rasters currently in the video came from Mission 6 and are narrow flight strips
("Antonio Parkway 1995", "O'Neil Regional Park June 1998") that are ~72% transparent over the AOI.
This fetches full-footprint frames by LockRaster on a single OBJECTID, exactly as the 1929/1937
exports were made, so coverage is complete rather than a strip.

Every frame is exported over the identical bbox and saved with a provenance record + sha256.
"""
from __future__ import annotations
import json, os, ssl, hashlib, datetime, urllib.request, urllib.parse

SVC = "https://ocgis.com/arcpub/rest/services/Historic_Imagery/Historic_Imagery_v2/ImageServer"
BBOX = (-117.680, 33.520, -117.616, 33.575)          # same extent as the 1929/1937 exports
SIZE = (3000, 2578)                                   # matches the source aspect
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO, "evidence/lhdrs/mission7/oc_frames")
os.makedirs(OUT, exist_ok=True)
CTX = ssl.create_default_context(); UA = {"User-Agent": "LHDRS-Mission7/1.0"}
TODAY = datetime.date.today().isoformat()

# Frames chosen for COMPLETE footprint coverage across the pre-Landsat era.
FRAMES = [
    (319, "1990", "Orange County 1990"),
    (320, "1980", "Orange County 1980"),
    (315, "1969", "Orange County 1970"),
    (343, "1960", "Orange County 1960"),
    (357, "1953", "Orange County 1953"),
]


def export(oid, tag, name):
    p = {
        "bbox": ",".join(str(x) for x in BBOX),
        "bboxSR": "4326", "imageSR": "4326",
        "size": f"{SIZE[0]},{SIZE[1]}",
        "format": "jpg", "f": "image",
        "mosaicRule": json.dumps({"mosaicMethod": "esriMosaicLockRaster", "lockRasterIds": [oid]}),
    }
    url = SVC + "/exportImage?" + urllib.parse.urlencode(p)
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=180, context=CTX) as f:
        data = f.read()
    if len(data) < 20000:
        return None, 0
    path = os.path.join(OUT, f"oc_{tag}_oid{oid}.jpg")
    open(path, "wb").write(data)
    return path, len(data)


records = []
for oid, tag, name in FRAMES:
    try:
        path, n = export(oid, tag, name)
        if not path:
            print(f"  {tag}: empty response, skipped"); continue
        sha = hashlib.sha256(open(path, "rb").read()).hexdigest()
        # measure real coverage: the service returns black where a locked raster has no data
        from PIL import Image
        import numpy as np
        Image.MAX_IMAGE_PIXELS = None
        a = np.asarray(Image.open(path).convert("L"))
        nod = float((a < 8).mean())
        print(f"  {tag}  oid={oid:<5} {n/1e6:5.1f} MB   nodata {nod*100:5.1f}%   {name}")
        records.append({"tag": tag, "objectId": oid, "name": name, "path": os.path.relpath(path, REPO),
                        "bytes": n, "sha256": sha, "nodataFraction": round(nod, 4),
                        "bbox": list(BBOX), "provenanceGrade": "A+",
                        "source": "OC Survey / OCGIS Historic_Imagery_v2 ImageServer, LockRaster"})
    except Exception as e:
        print(f"  {tag}: FAILED {str(e)[:80]}")

json.dump({"generated": TODAY, "bbox": list(BBOX), "frames": records},
          open(os.path.join(OUT, "manifest.json"), "w"), indent=1)
print(f"\n{len(records)} frame(s) -> {OUT}")
