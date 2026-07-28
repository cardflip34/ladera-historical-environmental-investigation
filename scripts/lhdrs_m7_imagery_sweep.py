#!/usr/bin/env python3
"""
Mission 7 / Phase A1 - open-catalog imagery sweep for the 1999-2004 blackout.

Queries publicly accessible catalogs (no credentials) for any imagery intersecting the Ladera Ranch
AOI between 1997 and 2006. Logs EVERY result including negatives, with the exact query used, so the
search is reproducible and a null result is itself a recorded finding.

Catalogs queried:
  1. USGS TNM Access API        (open)  - National Map orthoimagery products
  2. Microsoft Planetary Computer STAC (open) - NAIP, Landsat C2 L2
  3. USGS LandsatLook STAC      (open)  - Landsat
EarthExplorer M2M is NOT queried here: it requires credentials. Logged as a gated source.

Output: evidence/lhdrs/mission7/imagery_sweep_<date>.json  +  a human-readable summary
"""
from __future__ import annotations
import json, os, sys, urllib.request, urllib.parse, datetime, ssl

AOI = {"minlon": -117.659017, "minlat": 33.526791, "maxlon": -117.624136, "maxlat": 33.575504}
BBOX = [AOI["minlon"], AOI["minlat"], AOI["maxlon"], AOI["maxlat"]]
START, END = "1997-01-01", "2006-12-31"
TODAY = datetime.date.today().isoformat()
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO, "evidence/lhdrs/mission7")
os.makedirs(OUT, exist_ok=True)

CTX = ssl.create_default_context()
UA = {"User-Agent": "LHDRS-Mission7/1.0 (historical reconstruction research)"}
results = {"generated": TODAY, "aoi": AOI, "window": [START, END], "catalogs": []}


def fetch(url, data=None, timeout=45):
    req = urllib.request.Request(url, headers={**UA, "Content-Type": "application/json"},
                                 data=json.dumps(data).encode() if data else None)
    with urllib.request.urlopen(req, timeout=timeout, context=CTX) as r:
        return json.load(r)


def log(name, query, status, items, note=""):
    results["catalogs"].append({
        "catalog": name, "query": query, "status": status,
        "itemCount": len(items), "items": items[:80], "note": note,
    })
    print(f"\n[{name}] {status} - {len(items)} item(s)")
    if note:
        print(f"    note: {note}")
    for it in items[:25]:
        print(f"    {it.get('date','?'):>12}  {it.get('id','')[:60]}  {it.get('collection','')}")


# ---------------------------------------------------------------- 1. USGS TNM Access
try:
    q = ("https://tnmaccess.nationalmap.gov/api/v1/products?"
         + urllib.parse.urlencode({
             "bbox": ",".join(str(x) for x in BBOX),
             "max": 250,
             "outputFormat": "JSON",
         }))
    d = fetch(q)
    items = []
    for p in d.get("items", []):
        pub = (p.get("publicationDate") or p.get("dateCreated") or "")[:10]
        items.append({"id": p.get("title", "")[:90], "date": pub,
                      "collection": p.get("datasets", [""])[0] if p.get("datasets") else p.get("format", ""),
                      "url": p.get("downloadURL", "")})
    era = [i for i in items if i["date"][:4].isdigit() and 1997 <= int(i["date"][:4]) <= 2006]
    log("USGS_TNM_Access", q, "ok", era,
        f"{len(items)} total products at AOI; {len(era)} within 1997-2006")
except Exception as e:
    log("USGS_TNM_Access", "see code", f"error: {e}", [])

# ---------------------------------------------------------------- 2. Planetary Computer STAC
for coll in ["naip", "landsat-c2-l2"]:
    try:
        body = {"collections": [coll], "bbox": BBOX,
                "datetime": f"{START}T00:00:00Z/{END}T23:59:59Z", "limit": 100}
        d = fetch("https://planetarycomputer.microsoft.com/api/stac/v1/search", body)
        items = [{"id": f["id"], "date": (f["properties"].get("datetime") or "")[:10],
                  "collection": coll,
                  "gsd": f["properties"].get("gsd"),
                  "cloud": f["properties"].get("eo:cloud_cover")}
                 for f in d.get("features", [])]
        items.sort(key=lambda x: x["date"])
        log(f"PlanetaryComputer_{coll}", json.dumps(body), "ok", items)
    except Exception as e:
        log(f"PlanetaryComputer_{coll}", coll, f"error: {e}", [])

# ---------------------------------------------------------------- 3. USGS LandsatLook STAC
try:
    body = {"bbox": BBOX, "datetime": f"{START}T00:00:00Z/{END}T23:59:59Z", "limit": 100}
    d = fetch("https://landsatlook.usgs.gov/stac-server/search", body)
    items = [{"id": f["id"], "date": (f["properties"].get("datetime") or "")[:10],
              "collection": f.get("collection", ""),
              "cloud": f["properties"].get("eo:cloud_cover")}
             for f in d.get("features", [])]
    items.sort(key=lambda x: x["date"])
    log("USGS_LandsatLook_STAC", json.dumps(body), "ok", items)
except Exception as e:
    log("USGS_LandsatLook_STAC", "landsatlook", f"error: {e}", [])

# ---------------------------------------------------------------- gated / credentialed
results["gatedSources"] = [
    {"source": "USGS EarthExplorer M2M API", "status": "requires_credentials",
     "note": "Free account. Holds NAPP/NHAP aerial single frames and DOQQ - the most likely "
             "free source of 1999-2004 frames. Must be queried with a logged-in session."},
    {"source": "Commercial vendors (I.K. Curtis, HJW/Pacific Aerial, AirPhotoUSA, EagleView)",
     "status": "paid_quote_required",
     "note": "Realistic source for the 1999-2004 blackout. RFQ drafted separately; not sent."},
]

# ---------------------------------------------------------------- write
path = os.path.join(OUT, f"imagery_sweep_{TODAY}.json")
with open(path, "w") as f:
    json.dump(results, f, indent=1)

# per-year coverage from what we found
by_year = {}
for c in results["catalogs"]:
    for it in c["items"]:
        y = it.get("date", "")[:4]
        if y.isdigit():
            by_year.setdefault(int(y), []).append(f"{c['catalog']}:{it.get('id','')[:40]}")

print("\n" + "=" * 62)
print("PER-YEAR RESULT, 1997-2006 (open catalogs only)")
print("=" * 62)
for y in range(1997, 2007):
    hits = by_year.get(y, [])
    flag = "" if hits else "   <-- STILL BLANK"
    print(f"  {y}: {len(hits):>3} item(s){flag}")
print(f"\nwrote {path}")
