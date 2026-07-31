#!/usr/bin/env python3
"""
Vat hunt, stage 1 - pull the sharpest historical frames at NATIVE resolution, in tiles.

Why this is worth doing now and was not before:
Circular 174 tells us what to look for. A large range operation used a SWIM VAT - a long, narrow
excavation, up to 80-90 feet, with a holding corral, an approach chute and a drain pen attached.

The vat channel itself is ~1-1.5 m wide. At the ~1 m/px working resolution used so far it is ONE
PIXEL wide and simply cannot be resolved. That is a detection limit, not an absence, and the
earlier "no vat found" conclusion has to be read in that light.

The OC ImageServer reports a 30,000 px export limit, which over this AOI is ~0.2 m/px - five times
finer. At 0.2 m/px:
    a 27 m (90 ft) vat  = ~135 px long, 5-8 px wide      -> resolvable as a line
    a 30 m corral       = ~150 px across                  -> clearly resolvable
    a 10 m drain pen    = ~50 px                          -> resolvable

So the realistic target is the ASSEMBLY - a rectilinear enclosure cluster with a linear feature -
not the vat channel alone.

Frames chosen: 1937/38 is described in the project's own imagery audit as the sharpest in the set
(600-scale county series, 1.15 ft/px native). 1929 and 1947 give temporal corroboration - a real
structure should persist across frames; a film artefact will not.
"""
from __future__ import annotations
import json, os, ssl, hashlib, datetime, urllib.request, urllib.parse
import numpy as np
from PIL import Image
Image.MAX_IMAGE_PIXELS = None

SVC = "https://ocgis.com/arcpub/rest/services/Historic_Imagery/Historic_Imagery_v2/ImageServer"
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO, "evidence/lhdrs/vat_hunt")
os.makedirs(OUT, exist_ok=True)
CTX = ssl.create_default_context(); UA = {"User-Agent": "LHDRS-VatHunt/1.0"}
TODAY = datetime.date.today().isoformat()

AOI = (-117.680, 33.520, -117.616, 33.575)
NX, NY = 4, 4                 # tile grid
TILE_PX = 4000                # per tile -> ~0.21 m/px over this AOI

FRAMES = [(340, "1938"), (293, "1947"), (346, "1929")]

NODATA_YELLOW = lambda a: (a[:, :, 0] > 245) & (a[:, :, 1] > 245) & (a[:, :, 2] < 40)


def export(oid, bbox, px):
    p = {"bbox": ",".join(f"{v:.6f}" for v in bbox), "bboxSR": "4326", "imageSR": "4326",
         "size": f"{px},{px}", "format": "jpg", "f": "image",
         "mosaicRule": json.dumps({"mosaicMethod": "esriMosaicLockRaster", "lockRasterIds": [oid]})}
    url = SVC + "/exportImage?" + urllib.parse.urlencode(p)
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA),
                                  timeout=300, context=CTX).read()


manifest = []
dx = (AOI[2] - AOI[0]) / NX
dy = (AOI[3] - AOI[1]) / NY
gsd = (AOI[2] - AOI[0]) * 92500 / (NX * TILE_PX)
print(f"tiling {NX}x{NY} at {TILE_PX}px -> ~{gsd:.3f} m/px\n")

for oid, tag in FRAMES:
    tdir = os.path.join(OUT, tag)
    os.makedirs(tdir, exist_ok=True)
    kept = 0
    for iy in range(NY):
        for ix in range(NX):
            bb = (AOI[0] + ix*dx, AOI[1] + iy*dy, AOI[0] + (ix+1)*dx, AOI[1] + (iy+1)*dy)
            fp = os.path.join(tdir, f"{tag}_r{iy}c{ix}.jpg")
            if os.path.exists(fp) and os.path.getsize(fp) > 50000:
                kept += 1
                continue
            try:
                data = export(oid, bb, TILE_PX)
            except Exception as e:
                print(f"  {tag} r{iy}c{ix}: FAIL {str(e)[:60]}")
                continue
            if len(data) < 30000:
                continue
            open(fp, "wb").write(data)
            a = np.asarray(Image.open(fp).convert("RGB"))
            nod = float((NODATA_YELLOW(a) | (a.sum(2) < 24)).mean())
            if nod > 0.90:
                os.remove(fp)
                continue
            kept += 1
            manifest.append({"frame": tag, "objectId": oid, "row": iy, "col": ix,
                             "bbox": list(bb), "px": TILE_PX, "gsdMeters": round(gsd, 3),
                             "nodataFraction": round(nod, 4),
                             "path": os.path.relpath(fp, REPO),
                             "sha256": hashlib.sha256(open(fp, "rb").read()).hexdigest()})
            print(f"  {tag} r{iy}c{ix}  {len(data)/1e6:5.2f} MB  nodata {nod*100:5.1f}%")
    print(f"{tag}: {kept}/{NX*NY} tiles held\n")

json.dump({"generated": TODAY, "aoi": list(AOI), "grid": [NX, NY],
           "tilePx": TILE_PX, "gsdMeters": round(gsd, 3),
           "source": "OC Survey / OCGIS Historic_Imagery_v2 ImageServer, LockRaster",
           "provenanceGrade": "A+",
           "purpose": "Native-resolution search for swim-vat assemblies (vat + corral + drain pen)",
           "detectionLimitNote": ("At ~1 m/px a swim vat channel is 1 px wide and unresolvable. "
                                  "These tiles are ~0.2 m/px, where a 27 m vat is ~135 px long and "
                                  "a 30 m corral ~150 px across."),
           "tiles": manifest},
          open(os.path.join(OUT, "tile_manifest.json"), "w"), indent=1)
print(f"manifest -> {OUT}/tile_manifest.json  ({len(manifest)} new tiles)")
