#!/usr/bin/env python3
"""
Mission 7 / Phase A1b - USGS EarthExplorer M2M sweep for HIGH-RESOLUTION aerial imagery, 1997-2006.

This is the sweep that could finally break the 30 m ceiling. USGS holds aerial photo and
orthoimagery collections at roughly 1 m that no open STAC catalog exposes:

  aerial_combin       Aerial Photo Single Frames  (scanned frames, sub-metre to ~1 m)
  napp                National Aerial Photography Program (~1 m, 1987-2007)
  nhap                National High Altitude Photography (1980-1989, pre-window but checked)
  doq / doqq          Digital Orthophoto (Quarter) Quads (~1 m, 1990s-2000s)
  high_res_ortho      High Resolution Orthoimagery (0.15-1 m, county/city flights)
  naip                NAIP (1 m, CA from ~2005)

RUN MODES
  default            INVENTORY ONLY. Reports what exists. Downloads nothing.
  --download         Requests downloads for the scenes found (can be large; confirm first).

CREDENTIALS
  Read from ~/.usgs_m2m (never from the command line, never hard-coded):
      USGS_USER=<your ERS username>
      USGS_TOKEN=<application token, NOT your password>
  Generate a token at https://ers.cr.usgs.gov/password/appgenerate
  M2M access must be separately approved at https://ers.cr.usgs.gov/profile/access

Nothing here writes to the evidence base automatically. Inventory is written to
evidence/lhdrs/mission7/ for review, and any imagery that is later ingested must carry its own
provenance record + sha256 like every other Mission 7 source.
"""
from __future__ import annotations
import json, os, ssl, sys, datetime, urllib.request

API = "https://m2m.cr.usgs.gov/api/api/json/stable/"
AOI = {"minlon": -117.674, "minlat": 33.524, "maxlon": -117.609, "maxlat": 33.578}
START, END = "1997-01-01", "2006-12-31"
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO, "evidence/lhdrs/mission7")
os.makedirs(OUT, exist_ok=True)
TODAY = datetime.date.today().isoformat()
CTX = ssl.create_default_context()
DOWNLOAD = "--download" in sys.argv

CANDIDATES = ["aerial_combin", "napp", "nhap", "doq", "doqq",
              "high_res_ortho", "naip", "ortho_photo", "single_frame"]


def creds():
    p = os.path.expanduser("~/.usgs_m2m")
    if not os.path.exists(p):
        sys.exit("No ~/.usgs_m2m found.\n"
                 "  Create it with:\n"
                 "  printf 'USGS_USER=you@example.com\\nUSGS_TOKEN=YOUR_APP_TOKEN\\n' > ~/.usgs_m2m && chmod 600 ~/.usgs_m2m")
    kv = {}
    for line in open(p):
        if "=" in line and not line.strip().startswith("#"):
            k, v = line.strip().split("=", 1)
            kv[k.strip()] = v.strip()
    if not kv.get("USGS_USER") or not kv.get("USGS_TOKEN"):
        sys.exit("~/.usgs_m2m must define USGS_USER and USGS_TOKEN")
    return kv["USGS_USER"], kv["USGS_TOKEN"]


def call(endpoint, payload, auth=None, timeout=180):
    r = urllib.request.Request(
        API + endpoint,
        headers={"Content-Type": "application/json", "User-Agent": "LHDRS-Mission7/1.0",
                 **({"X-Auth-Token": auth} if auth else {})},
        data=json.dumps(payload).encode())
    with urllib.request.urlopen(r, timeout=timeout, context=CTX) as f:
        d = json.load(f)
    if d.get("errorCode"):
        raise RuntimeError(f"{endpoint}: {d['errorCode']} - {d.get('errorMessage')}")
    return d.get("data")


spatial = {"filterType": "mbr",
           "lowerLeft":  {"latitude": AOI["minlat"], "longitude": AOI["minlon"]},
           "upperRight": {"latitude": AOI["maxlat"], "longitude": AOI["maxlon"]}}

user, token = creds()
print("Authenticating to USGS M2M...")
try:
    auth = call("login-token", {"username": user, "token": token})
except Exception as e:
    sys.exit(f"LOGIN FAILED: {e}\n"
             "  - AUTH_INVALID  -> token wrong/expired; regenerate at ers.cr.usgs.gov/password/appgenerate\n"
             "  - AUTH_UNAUTHORIZED -> M2M access not yet approved; request at ers.cr.usgs.gov/profile/access")
print("  authenticated\n")

report = {"generated": TODAY, "aoi": AOI, "window": [START, END], "datasets": []}
try:
    # ---- discover which datasets actually intersect this AOI/time
    print("Discovering datasets covering the AOI...")
    try:
        found = call("dataset-search", {"catalog": "EE", "spatialFilter": spatial,
                                        "temporalFilter": {"start": START, "end": END}}, auth) or []
        names = {d["datasetAlias"]: d.get("collectionName", "") for d in found}
        print(f"  {len(names)} dataset(s) intersect\n")
    except Exception as e:
        print(f"  dataset-search unavailable ({str(e)[:60]}); falling back to candidate list\n")
        names = {}

    targets = [a for a in CANDIDATES if a in names] or CANDIDATES
    grand = 0
    for alias in targets:
        try:
            res = call("scene-search", {
                "datasetName": alias,
                "sceneFilter": {"spatialFilter": spatial,
                                "acquisitionFilter": {"start": START, "end": END}},
                "maxResults": 500, "startingNumber": 1, "metadataType": "summary"}, auth)
        except Exception as e:
            print(f"  {alias:<18} unavailable ({str(e)[:55]})")
            report["datasets"].append({"alias": alias, "status": f"unavailable: {str(e)[:120]}", "sceneCount": 0})
            continue
        hits = (res or {}).get("results", []) or []
        total = (res or {}).get("totalHits", len(hits))
        grand += len(hits)
        scenes = []
        for s in hits:
            scenes.append({"entityId": s.get("entityId"), "displayId": s.get("displayId"),
                           "date": (s.get("temporalCoverage") or {}).get("startDate")
                                   or s.get("publishDate") or "",
                           "summary": (s.get("summary") or "")[:110]})
        scenes.sort(key=lambda x: x["date"] or "")
        status = "HITS" if hits else "none"
        print(f"  {alias:<18} {status:<6} {len(hits):>4} scene(s)  (totalHits {total})  {names.get(alias,'')[:44]}")
        for s in scenes[:12]:
            print(f"        {str(s['date'])[:10]:<12} {str(s['displayId'])[:52]}")
        report["datasets"].append({"alias": alias, "collectionName": names.get(alias, ""),
                                   "status": status, "sceneCount": len(hits),
                                   "totalHits": total, "scenes": scenes})

    print(f"\nTOTAL high-resolution scenes found in window: {grand}")
    if grand == 0:
        print("  A zero result is a FINDING, not a failure: it documents that USGS holds no\n"
              "  high-resolution aerial frames for this AOI in 1997-2006, which strengthens the\n"
              "  case for the commercial vendor RFQ (M7-RFQ-AERIAL-01).")

    # ---- optional download stage
    if DOWNLOAD and grand:
        print("\n--download set: requesting download options...")
        for ds in report["datasets"]:
            if not ds.get("scenes"):
                continue
            ids = [s["entityId"] for s in ds["scenes"] if s.get("entityId")]
            try:
                opts = call("download-options", {"datasetName": ds["alias"], "entityIds": ids}, auth) or []
                avail = [{"entityId": o["entityId"], "productId": o["id"],
                          "size": o.get("filesize"), "name": o.get("productName")}
                         for o in opts if o.get("available")]
                ds["downloadable"] = avail
                gb = sum(a["size"] or 0 for a in avail) / 1e9
                print(f"  {ds['alias']}: {len(avail)} downloadable product(s), ~{gb:.2f} GB")
            except Exception as e:
                print(f"  {ds['alias']}: download-options failed ({str(e)[:60]})")
        print("\nNOTE: download URLs are not auto-fetched. Review sizes above, then request\n"
              "explicitly. Large orders should go through the USGS bulk download queue.")
finally:
    try:
        call("logout", {}, auth)
        print("\nlogged out")
    except Exception:
        pass

p = os.path.join(OUT, f"m2m_aerial_sweep_{TODAY}.json")
json.dump(report, open(p, "w"), indent=1)
print(f"wrote {p}")
