#!/usr/bin/env python3
"""Pull an Orange County historical aerial over a point and enhance it for visual recon.

Uses the OC Survey public ArcGIS ImageServer (Historic_Imagery mosaic). Aerials available include
"Irvine Ranch 1931", "Orange County 1938/1947/1952/1953/1960", and later. This is documentary
land-use reconnaissance only — it does NOT identify contamination or dip vats.

Usage:
  python3 scripts/pull_oc_historical_aerial.py <lon> <lat> <half_window_ft> <name_substr> <out.jpg>
Example (Bommer Canyon, 1931 Irvine Ranch, ~800 ft window):
  python3 scripts/pull_oc_historical_aerial.py -117.80 33.63 800 "Irvine Ranch 1931" out.jpg
"""
import sys, json, urllib.parse, urllib.request
from pyproj import Transformer
from PIL import Image, ImageOps
import io

BASE = "https://www.ocgis.com/arcpub/rest/services/Historic_Imagery/Historic_Imagery/ImageServer"
UA = {"User-Agent": "Mozilla/5.0 (research; land-use history)"}

def get(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60).read()

def main():
    lon, lat, half, name_sub, out = float(sys.argv[1]), float(sys.argv[2]), float(sys.argv[3]), sys.argv[4], sys.argv[5]
    x, y = Transformer.from_crs(4326, 2230, always_xy=True).transform(lon, lat)
    # find the raster OBJECTID matching name_sub that covers the point
    q = {"geometry": f"{x},{y}", "geometryType": "esriGeometryPoint", "inSR": "2230",
         "spatialRel": "esriSpatialRelIntersects", "outFields": "OBJECTID,Name,Date_On_Map",
         "returnGeometry": "false", "f": "json"}
    feats = json.loads(get(BASE + "/query?" + urllib.parse.urlencode(q))).get("features", [])
    match = [f["attributes"] for f in feats if name_sub.lower() in str(f["attributes"].get("Name","")).lower()]
    if not match:
        print("No raster named ~", name_sub, "over this point. Available:",
              sorted({f["attributes"].get("Name") for f in feats})); sys.exit(1)
    oid = match[0]["OBJECTID"]; print("Using:", match[0]["Name"], "OBJECTID", oid)
    # export locked to that raster
    ex = {"bbox": f"{x-half},{y-half},{x+half},{y+half}", "bboxSR": "2230", "imageSR": "2230",
          "size": "1400,1400", "format": "jpg", "f": "image",
          "mosaicRule": json.dumps({"mosaicMethod": "esriMosaicLockRaster", "lockRasterIds": [oid]})}
    img = get(BASE + "/exportImage?" + urllib.parse.urlencode(ex))
    im = Image.open(io.BytesIO(img)).convert("L")
    ImageOps.autocontrast(im, cutoff=0.5).save(out, "JPEG", quality=92)  # stretch faded scan
    print("wrote", out, im.size)

if __name__ == "__main__":
    main()
