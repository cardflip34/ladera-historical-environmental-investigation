#!/usr/bin/env python3
"""Build GeoJSON map layers for LEHRP from the research CSVs.

Pure standard library (no geopandas required) so it runs anywhere. Produces:
  data/geospatial/zone_a_boundary.geojson      (APPROXIMATE Ladera Ranch boundary)
  data/geospatial/zone_b_buffer.geojson        (APPROXIMATE 5-mile exposure ring)
  data/geospatial/environmental_sites.geojson  (real EnviroStor coordinates)
  data/geospatial/oil_gas_wells.geojson        (real CalGEM coordinates)
  data/geospatial/reference_points.geojson     (community centroid)
Outputs are also copied to apps/web/public/geo/ for the web map.

All coordinates are EPSG:4326 (lon, lat). Study-zone geometry is explicitly APPROXIMATE and
flagged as such in feature properties — it is a screening aid, not a legal boundary.
"""
import csv
import json
import math
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
GEO = os.path.join(ROOT, "data", "geospatial")
WEB_GEO = os.path.join(ROOT, "apps", "web", "public", "geo")

# Ladera Ranch CDP centroid, 33°32'48"N 117°38'25"W (Census/CDP). Corrected 2026-07-18:
# an earlier value of 33.5747,-117.6353 was ~1.93 mi too far north and placed the study
# zone outside the community. Verified against the OSM place label and BLM PLSS.
CENTER_LAT, CENTER_LON = 33.5467, -117.6403


def feature(geom, props):
    return {"type": "Feature", "geometry": geom, "properties": props}


def fc(features):
    return {"type": "FeatureCollection", "features": features}


def haversine_miles(lat1, lon1, lat2, lon2):
    r = 3958.7613
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def circle(lat, lon, miles, n=48):
    """Great-circle-ish polygon; adequate at this scale for a screening buffer."""
    coords = []
    r_lat = miles / 69.0
    r_lon = miles / (69.0 * math.cos(math.radians(lat)))
    for i in range(n + 1):
        a = 2 * math.pi * i / n
        coords.append([lon + r_lon * math.cos(a), lat + r_lat * math.sin(a)])
    return {"type": "Polygon", "coordinates": [coords]}


def read_csv(rel):
    path = os.path.join(ROOT, rel)
    if not os.path.exists(path):
        return []
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def build_zone_a():
    # APPROXIMATE bounding polygon (~2.5 mi E-W x 2 mi N-S ≈ 5 sq mi, vs the CDP's
    # published 4.945 sq mi), centred on the corrected CDP centroid. Flagged approximate.
    dlat = 1.0 / 69.0                                        # 1 mi N and S
    dlon = 1.25 / (69.0 * math.cos(math.radians(CENTER_LAT)))  # 1.25 mi E and W
    w, e = CENTER_LON - dlon, CENTER_LON + dlon
    s, n = CENTER_LAT - dlat, CENTER_LAT + dlat
    box = [[w, s], [e, s], [e, n], [w, n], [w, s]]
    return fc([feature(
        {"type": "Polygon", "coordinates": [box]},
        {"name": "Zone A — Ladera Ranch (core)", "zone": "A",
         "precision": "APPROXIMATE — screening boundary, not the legal CDP boundary",
         "source": "Approximate from CDP centroid + area; refine with Census TIGER",
         "confidence": "Model Estimate"},
    )])


def build_zone_b():
    return fc([feature(
        circle(CENTER_LAT, CENTER_LON, 5.0),
        {"name": "Zone B — 5-mile exposure ring", "zone": "B",
         "precision": "APPROXIMATE — 5-mi radius from community centroid",
         "source": "Generated buffer", "confidence": "Model Estimate"},
    )])


def build_env_sites():
    feats = []
    for r in read_csv("research/environmental_sites/sites.csv"):
        lat, lon = r.get("lat", ""), r.get("lng", "")
        if not lat or not lon:
            continue
        try:
            geom = {"type": "Point", "coordinates": [float(lon), float(lat)]}
        except ValueError:
            continue
        feats.append(feature(geom, {
            "id": r["id"], "name": r["name"], "siteType": r.get("siteType", ""),
            "database": r.get("database", ""), "status": r.get("status", ""),
            "contaminants": r.get("contaminants", ""),
            "distanceMiles": r.get("approxDistanceMiles", ""),
            "grade": r.get("grade", ""), "sourceId": r.get("sourceId", ""),
            "layer": "environmental_sites",
        }))
    return fc(feats)


def build_wells():
    # Real CalGEM WellSTAR results (all plugged dry holes or idle). Directly relevant to the
    # published abandoned-well / Ewing sarcoma association (Clark et al. 2026).
    # Distances recomputed by haversine from the corrected CDP centroid (2026-07-18).
    wells = [
        ("0405901005", "Citizens National Trust B-1 / Exxon Mobil", "Plugged, Dry Hole", 33.546, -117.636),
        ("0405901270", "O'Neill #1 / Union Oil", "Plugged, Dry Hole", 33.536, -117.644),
        ("0405901016", "O'Neill Estate B-1 / Exxon Mobil", "Plugged, Dry Hole", 33.618, -117.673),
        ("0405900899", "Shumaker #1 / Conoco", "Plugged, Dry Hole", 33.549, -117.692),
        ("0405901091", "Norswing & Halvorson #1", "Idle, Oil & Gas", 33.501, -117.689),
        ("0405901153", "South Fullerton Oil Co. #1", "Idle, Oil & Gas", 33.593, -117.720),
    ]
    feats = []
    for api, lease, status, lat, lon in wells:
        dist = round(haversine_miles(CENTER_LAT, CENTER_LON, lat, lon), 2)
        feats.append(feature(
            {"type": "Point", "coordinates": [lon, lat]},
            {"api": api, "name": lease, "status": status, "distanceMiles": dist,
             "grade": "A1", "sourceId": "SRC-ENV-CALGEM", "layer": "oil_gas_wells",
             "note": "Plugged/idle exploratory well; relevant to abandoned-well Ewing association"},
        ))
    return fc(feats)




def build_school_sites():
    """DTSC school-site investigations on former agricultural land, split by whether ARSENIC
    was among the contaminants found. These are the only nearby places anyone was legally
    required to test (CA Education Code mandates assessment before a district buys land;
    residential subdivisions carry no equivalent duty)."""
    schools = [
        # name, lat, lon, contaminants, arsenic?, miles
        ("Carl Hankey Elementary", 33.5697, -117.6550, "Arsenic, lead, methane", True, 1.8,
         "Former orchard + row crops"),
        ("Plant Depot School Site", 33.508, -117.659, "Arsenic, nitrate", True, 2.9,
         "Former agricultural services"),
        ("San Juan Elementary", 33.504, -117.662, "Arsenic, chlordane, DDD, DDE, DDT, lead", True, 3.2,
         "Former orchard"),
        ("Ambuehl Elementary", 33.503, -117.645, "DDD, DDE, DDT, toxaphene", False, 3.0,
         "Former agricultural land"),
        ("El Toro High School", 33.637, -117.688, "PCBs, TPH-diesel", False, 6.8,
         "Former row crops"),
    ]
    feats = []
    for name, lat, lon, cont, has_as, dist, past in schools:
        feats.append(feature(
            {"type": "Point", "coordinates": [lon, lat]},
            {"name": name, "contaminants": cont, "arsenic": has_as,
             "distanceMiles": dist, "pastUse": past,
             "layer": "school_arsenic" if has_as else "school_other",
             "database": "DTSC EnviroStor", "grade": "A1",
             "sourceId": "SRC-ENV-ENVIROSTOR"},
        ))
    return fc(feats)


def build_reference():
    return fc([feature(
        {"type": "Point", "coordinates": [CENTER_LON, CENTER_LAT]},
        {"name": "Ladera Ranch (approx. center)", "layer": "reference",
         "sourceId": "SRC-DEM-001", "grade": "A1"},
    )])


def write(name, data):
    os.makedirs(GEO, exist_ok=True)
    os.makedirs(WEB_GEO, exist_ok=True)
    for d in (GEO, WEB_GEO):
        with open(os.path.join(d, name), "w", encoding="utf-8") as f:
            json.dump(data, f, indent=1)
    print(f"  wrote {name}: {len(data['features'])} feature(s)")


def main():
    print("Building GeoJSON layers...")
    write("zone_a_boundary.geojson", build_zone_a())
    write("zone_b_buffer.geojson", build_zone_b())
    write("environmental_sites.geojson", build_env_sites())
    write("school_sites.geojson", build_school_sites())
    write("oil_gas_wells.geojson", build_wells())
    write("reference_points.geojson", build_reference())
    print("Done.")


if __name__ == "__main__":
    main()
