#!/usr/bin/env python3
"""
Mission 7 / Phase 3 - mass-grading progression from free Landsat, 1997-2006.

Measures the fraction of the Ladera Ranch AOI that is BARE / DISTURBED SOIL in each year, using
NDVI from Landsat Collection 2 Level-2 surface reflectance. Vegetated ground has high NDVI; graded,
scraped, or newly-built ground has low NDVI. The vegetated -> bare transition is the physical
signature of mass grading.

WHAT THIS IS
  A neighborhood-scale, documented-imagery measurement of ground disturbance over time.

WHAT THIS IS NOT
  - NOT parcel-level. Landsat is 30 m/pixel; a typical lot is ~20-27 m across, so ONE PIXEL IS
    ROUGHLY ONE LOT. Rooftops are not resolvable. No parcel claim may be derived from this.
  - NOT a contamination, dust, or exposure product. It measures bare soil extent, nothing else.
  - NOT a substitute for high-resolution aerials.

statementClass = 'interpreted' (index threshold on documented A+ imagery). Never 'documented'.

Method notes / honesty:
  * Landsat 7 ETM+ suffered the Scan Line Corrector failure on 2003-05-31. Post-SLC L7 scenes have
    ~22% striped data loss. This script PREFERS Landsat 5 for 2003+ and records which platform and
    how much valid data each chosen scene had.
  * Cloud/shadow masked via the QA_PIXEL bitmask.
  * Dry-season scenes are preferred so that seasonal grass senescence does not masquerade as
    grading. Southern California grassland browns naturally in summer, which would inflate a naive
    'bare soil' count. Selection therefore targets a consistent seasonal window and the limitation
    is recorded regardless.
"""
from __future__ import annotations
import json, os, ssl, datetime, urllib.request, urllib.parse
import numpy as np

BBOX = [-117.659017, 33.526791, -117.624136, 33.575504]
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO, "evidence/lhdrs/mission7")
os.makedirs(OUT, exist_ok=True)
TODAY = datetime.date.today().isoformat()
CTX = ssl.create_default_context()
UA = {"User-Agent": "LHDRS-Mission7/1.0", "Content-Type": "application/json"}
STAC = "https://planetarycomputer.microsoft.com/api/stac/v1/search"
SIGN = "https://planetarycomputer.microsoft.com/api/sas/v1/sign?href="

# Seasonal window: late winter / early spring. In SoCal this is when natural grassland is GREEN,
# so bare ground detected here is far more likely to be genuine disturbance than dry-season browning.
SEASON = (1, 5)          # months Jan-May inclusive
NDVI_BARE = 0.20         # below this = bare / disturbed
MIN_VALID = 0.60         # require 60% valid (non-cloud, non-gap) pixels in AOI


def post(url, body):
    r = urllib.request.Request(url, headers=UA, data=json.dumps(body).encode())
    with urllib.request.urlopen(r, timeout=60, context=CTX) as f:
        return json.load(f)


def sign(href):
    r = urllib.request.Request(SIGN + urllib.parse.quote(href, safe=""), headers={"User-Agent": UA["User-Agent"]})
    with urllib.request.urlopen(r, timeout=60, context=CTX) as f:
        return json.load(f)["href"]


def candidates(year):
    d = post(STAC, {"collections": ["landsat-c2-l2"], "bbox": BBOX,
                    "datetime": f"{year}-01-01T00:00:00Z/{year}-12-31T23:59:59Z", "limit": 500})
    out = []
    for f in d.get("features", []):
        p = f["properties"]
        dt = p.get("datetime", "")[:10]
        try:
            m = int(dt[5:7])
        except ValueError:
            continue
        cloud = p.get("eo:cloud_cover")
        if cloud is None:
            continue
        plat = p.get("platform", "")
        # Prefer in-season; prefer Landsat 5 once L7 SLC has failed
        slc_bad = (plat == "landsat-7" and dt >= "2003-05-31")
        score = cloud + (0 if SEASON[0] <= m <= SEASON[1] else 40) + (60 if slc_bad else 0)
        out.append((score, cloud, dt, plat, f))
    out.sort(key=lambda x: x[0])
    return out


def read_ndvi(feat):
    """Read red+nir+qa for the AOI window; return (ndvi, valid_mask, meta)."""
    import rasterio
    from rasterio.warp import transform_bounds
    from rasterio.windows import from_bounds

    def band(name):
        href = sign(feat["assets"][name]["href"])
        return rasterio.open(href)

    with band("red") as r, band("nir08") as n, band("qa_pixel") as q:
        b = transform_bounds("EPSG:4326", r.crs, *BBOX)
        win = from_bounds(*b, transform=r.transform)
        red = r.read(1, window=win).astype("float32")
        nir = n.read(1, window=from_bounds(*b, transform=n.transform)).astype("float32")
        qa = q.read(1, window=from_bounds(*b, transform=q.transform)).astype("uint16")

    # Collection-2 L2 scaling
    red = red * 0.0000275 - 0.2
    nir = nir * 0.0000275 - 0.2
    # QA_PIXEL bits: 1=dilated cloud, 3=cloud, 4=cloud shadow; 0 = fill
    bad = ((qa & (1 << 0)) | (qa & (1 << 1)) | (qa & (1 << 3)) | (qa & (1 << 4))) > 0
    valid = (~bad) & (red > -0.1) & (nir > -0.1) & np.isfinite(red) & np.isfinite(nir)
    ndvi = np.where(valid, (nir - red) / np.maximum(nir + red, 1e-6), np.nan)
    return ndvi, valid, {"shape": list(ndvi.shape)}


print("Mass-grading progression from Landsat NDVI\n")
rows = []
for year in range(1997, 2007):
    picked = None
    for score, cloud, dt, plat, feat in candidates(year)[:6]:
        try:
            ndvi, valid, meta = read_ndvi(feat)
        except Exception as e:
            print(f"  {year} {dt} {plat}: read failed ({str(e)[:60]})")
            continue
        frac_valid = float(valid.mean())
        if frac_valid < MIN_VALID:
            print(f"  {year} {dt} {plat}: only {frac_valid:.0%} valid, skipping")
            continue
        bare = float(np.nansum(ndvi < NDVI_BARE) / max(1, np.sum(valid)))
        picked = {"year": year, "date": dt, "platform": plat, "cloudPct": round(cloud, 1),
                  "validPct": round(frac_valid * 100, 1), "barePct": round(bare * 100, 1),
                  "medianNDVI": round(float(np.nanmedian(ndvi)), 3),
                  "sceneId": feat["id"], "pixels": meta["shape"]}
        break
    if picked:
        rows.append(picked)
        print(f"  {year}  {picked['date']}  {picked['platform']:<10} "
              f"cloud={picked['cloudPct']:>4}%  valid={picked['validPct']:>5}%  "
              f"BARE={picked['barePct']:>5}%  medNDVI={picked['medianNDVI']}")
    else:
        rows.append({"year": year, "status": "no_usable_scene"})
        print(f"  {year}  no usable scene")

result = {
    "generated": TODAY,
    "method": "Landsat C2 L2 surface reflectance; NDVI = (NIR-Red)/(NIR+Red); "
              f"bare/disturbed = NDVI < {NDVI_BARE}; cloud/shadow masked via QA_PIXEL; "
              f"seasonal window months {SEASON[0]}-{SEASON[1]} preferred",
    "aoi": BBOX,
    "provenanceGrade": "A+",
    "statementClass": "interpreted",
    "resolutionMeters": 30,
    "criticalLimitations": [
        "30 m pixels: approximately ONE PIXEL PER RESIDENTIAL LOT. Rooftops are NOT resolvable. "
        "No parcel-level claim may be derived from this product.",
        "NDVI threshold is an interpretation, not a documented fact. statementClass='interpreted'.",
        "Bare soil can arise from grading, natural senescence, fire, or fallow agriculture. "
        "Seasonal window selection reduces but does not eliminate this ambiguity.",
        "Landsat 7 SLC failure (2003-05-31) causes ~22% striping; Landsat 5 preferred for 2003+.",
        "This measures ground disturbance only. It is NOT a contamination, dust, or exposure product.",
    ],
    "series": rows,
}
p = os.path.join(OUT, f"grading_progression_landsat_{TODAY}.json")
json.dump(result, open(p, "w"), indent=1)
print(f"\nwrote {p}")
