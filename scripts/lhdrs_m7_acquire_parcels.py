#!/usr/bin/env python3
"""
Mission 7 / Phase A3 - acquire Orange County Assessor parcel data (incl. YEAR_BUILT) for the AOI.

Source: https://ocgis.com/arcpub/rest/services/Map_Layers/Parcels/FeatureServer/0  (official County
ArcGIS service, provenance grade A+). Paginated, geometry included, saved unmodified alongside a
provenance record and sha256.

IMPORTANT - YEAR_BUILT IS NOT AN OCCUPANCY RECORD. It is stored with milestoneType
'assessor_year_built' and must render as a year-wide uncertainty band, never as a completion or
certificate-of-occupancy date. This rule is carried from Missions 5/6 and enforced downstream.
"""
from __future__ import annotations
import json, os, ssl, hashlib, datetime, urllib.request, urllib.parse

AOI = {"xmin": -117.659017, "ymin": 33.526791, "xmax": -117.624136, "ymax": 33.575504}
SVC = "https://ocgis.com/arcpub/rest/services/Map_Layers/Parcels/FeatureServer/0"
TODAY = datetime.date.today().isoformat()
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO, "evidence/lhdrs/mission7")
os.makedirs(OUT, exist_ok=True)
CTX = ssl.create_default_context(); UA = {"User-Agent": "LHDRS-Mission7/1.0"}


def get(url):
    r = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(r, timeout=90, context=CTX) as f:
        return json.load(f)


BASE = {
    "geometry": json.dumps(AOI), "geometryType": "esriGeometryEnvelope",
    "inSR": "4326", "spatialRel": "esriSpatialRelIntersects",
}


def ids():
    """Authoritative ID list - avoids resultOffset, which this service does not honour."""
    p = {**BASE, "where": "1=1", "returnIdsOnly": "true", "f": "json"}
    return get(SVC + "/query?" + urllib.parse.urlencode(p))


def by_ids(chunk):
    p = {**BASE, "where": "1=1",
         "objectIds": ",".join(str(i) for i in chunk),
         "outSR": "4326", "outFields": "*", "returnGeometry": "true", "f": "geojson"}
    return get(SVC + "/query?" + urllib.parse.urlencode(p))


print("Acquiring OC parcels for Ladera Ranch AOI...")
idd = ids()
oids = idd.get("objectIds") or idd.get("properties", {}).get("objectIds") or []
print(f"  authoritative AOI parcel count: {len(oids)}")
feats = []
CH = 400
for i in range(0, len(oids), CH):
    got = by_ids(oids[i:i + CH]).get("features", [])
    feats.extend(got)
    print(f"  {i + len(got):>6}/{len(oids)}")

fc = {"type": "FeatureCollection", "features": feats}
path = os.path.join(OUT, f"oc_parcels_ladera_{TODAY}.geojson")
raw = json.dumps(fc)
open(path, "w").write(raw)
sha = hashlib.sha256(raw.encode()).hexdigest()

# ---- provenance record
prov = {
    "acquiredAt": TODAY,
    "sourceService": SVC,
    "sourceName": "Orange County Parcels (Assessor-derived), official County ArcGIS service",
    "provenanceGrade": "A+",
    "statementClass": "documented",
    "aoi": AOI,
    "featureCount": len(feats),
    "sha256": sha,
    "fileBytes": len(raw),
    "criticalLimitation": (
        "YEAR_BUILT is an Assessor attribute, NOT a certificate of occupancy and NOT a construction "
        "completion record. Store as milestoneType='assessor_year_built'. Render only as a year-wide "
        "uncertainty band. Never use to assert a specific completion or move-in date."
    ),
}
open(os.path.join(OUT, f"oc_parcels_ladera_{TODAY}.provenance.json"), "w").write(json.dumps(prov, indent=1))

# ---- YEAR_BUILT distribution (the Phase 4 payload)
yb = {}
for f in feats:
    v = (f.get("properties") or {}).get("YEAR_BUILT")
    try:
        v = int(str(v).strip())
    except (TypeError, ValueError):
        v = None
    yb[v] = yb.get(v, 0) + 1

print(f"\nparcels: {len(feats)}   sha256: {sha[:16]}...")
print(f"wrote {path}")
print("\nYEAR_BUILT distribution (build-out era):")
known = {k: v for k, v in yb.items() if k}
for y in sorted(k for k in known if 1995 <= k <= 2010):
    print(f"  {y}: {known[y]:>5} parcels")
era = sum(v for k, v in known.items() if 1997 <= k <= 2006)
print(f"\n  1997-2006 total: {era}")
print(f"  outside window : {sum(v for k,v in known.items() if not (1997 <= k <= 2006))}")
print(f"  null/0 YEAR_BUILT: {yb.get(None,0) + known.get(0,0)}")
