#!/usr/bin/env python3
"""
Mission 6 - render Appendix C: the project AOI as a map image and a KML, for attaching to records
requests.

Three of the drafted requests (OC-AERIAL-03, SMWD-PLANS-07, USDA-11) attach "Appendix C" as a
polygon PLUS a rendered map. The polygon existed; the rendered map did not. An agency clerk should
not have to open a GeoJSON to see where the request is about, and several counters accept KML but
not GeoJSON, so both are produced here.

Reads:  data/development/mission6_appendices/appendix_C_aoi.geojson
Writes: appendix_C_aoi_MAP.png, appendix_C_aoi.kml, appendix_C_aoi_MAP.provenance.json

The map is deliberately plain: outline, corner coordinates, scale bar, north arrow, and the
statement of what it is. No basemap tiles are fetched, so nothing here depends on a third-party
service or carries a tile licence into an agency submission.
"""
from __future__ import annotations
import json, os, math, hashlib, datetime
from PIL import Image, ImageDraw, ImageFont

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP = os.path.join(REPO, "data/development/mission6_appendices")
SRC = os.path.join(APP, "appendix_C_aoi.geojson")
TODAY = datetime.date.today().isoformat()

FD = "/System/Library/Fonts/Supplemental/"
def F(s, b=False):
    p = FD + ("Arial Bold" if b else "Arial") + ".ttf"
    return ImageFont.truetype(p, s) if os.path.exists(p) else ImageFont.load_default()

INK = (22, 35, 58); MUT = (110, 116, 126); LINE = (206, 212, 222)
ACC = (52, 110, 190); PAPER = (255, 255, 255); FILL = (52, 110, 190, 38)

gj = json.load(open(SRC))
rings = []
for f in gj["features"]:
    g = f["geometry"]
    if g["type"] == "Polygon":
        rings.append(g["coordinates"][0])
    elif g["type"] == "MultiPolygon":
        rings.extend(p[0] for p in g["coordinates"])
pts = [p for r in rings for p in r]
lo0, lo1 = min(p[0] for p in pts), max(p[0] for p in pts)
la0, la1 = min(p[1] for p in pts), max(p[1] for p in pts)

W, H = 1700, 2000
M, TOP = 90, 250
MAPH = 1180
im = Image.new("RGB", (W, H), PAPER)
ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
d = ImageDraw.Draw(im); do = ImageDraw.Draw(ov)

# geographic aspect at this latitude, so the polygon is not stretched
latm = math.radians((la0 + la1) / 2)
gw = (lo1 - lo0) * math.cos(latm)
gh = (la1 - la0)
MAPW = W - 2 * M
sc = min(MAPW / gw, MAPH / gh)
pw, ph = gw * sc, gh * sc
ox = M + (MAPW - pw) / 2
oy = TOP + (MAPH - ph) / 2

def xy(lon, lat):
    return (ox + (lon - lo0) * math.cos(latm) * sc, oy + (la1 - lat) * sc)

d.rectangle([M, TOP, W - M, TOP + MAPH], outline=LINE, width=1)
for r in rings:
    poly = [xy(*p) for p in r]
    do.polygon(poly, fill=FILL)
    d.line(poly + [poly[0]], fill=ACC, width=4)
im = Image.alpha_composite(im.convert("RGBA"), ov).convert("RGB")
d = ImageDraw.Draw(im)
for r in rings:
    poly = [xy(*p) for p in r]
    d.line(poly + [poly[0]], fill=ACC, width=4)

d.text((M, 60), "Appendix C — Project area of interest", font=F(46, True), fill=INK)
d.text((M, 122), "Ladera Ranch, unincorporated Orange County, California", font=F(22), fill=MUT)
d.text((M, 156), "Attach with records requests. Independent historical land-development research.",
       font=F(19), fill=MUT)

# corner coordinates, labelled outside the frame
for lon, lat, ha, va in ((lo0, la1, "la", "d"), (lo1, la1, "ra", "d"),
                         (lo0, la0, "ld", "u"), (lo1, la0, "rd", "u")):
    x, y = xy(lon, lat)
    d.ellipse([x-6, y-6, x+6, y+6], fill=ACC)
    t = f"{lat:.4f}, {lon:.4f}"
    anc = "la" if ha[0] == "l" else "ra"
    dy = -30 if va == "d" else 12
    d.text((x + (10 if ha[0] == "l" else -10), y + dy), t, font=F(17, True), fill=INK, anchor=anc)

# scale bar, computed from the projection actually used
km = 1.0
px_per_km = sc * (1000 / 111320.0)
bx, by = M + 24, TOP + MAPH - 44
d.line([bx, by, bx + px_per_km * km, by], fill=INK, width=5)
for t_ in (0, km):
    d.line([bx + px_per_km * t_, by - 9, bx + px_per_km * t_, by + 9], fill=INK, width=3)
d.text((bx + px_per_km * km / 2, by - 34), f"{km:.0f} km", font=F(19, True), fill=INK, anchor="ma")

# north arrow
nx, ny = W - M - 54, TOP + 54
d.line([nx, ny + 44, nx, ny - 26], fill=INK, width=4)
d.polygon([(nx, ny - 40), (nx - 12, ny - 18), (nx + 12, ny - 18)], fill=INK)
d.text((nx, ny + 50), "N", font=F(21, True), fill=INK, anchor="ma")

wkm = gw * 111.320 * 1  # already cos-scaled
hkm = gh * 110.574
y = TOP + MAPH + 46
d.line([M, y - 22, W - M, y - 22], fill=LINE)
for t_ in [
    f"Extent   {la0:.4f} to {la1:.4f} N   ·   {lo0:.4f} to {lo1:.4f} E",
    f"Approximate size   {wkm:.1f} km east-west  ×  {hkm:.1f} km north-south",
    "Coordinate reference system   WGS 84 (EPSG:4326), decimal degrees",
    "",
    "This polygon is the study area only. It is not a property boundary, not a parcel, and",
    "asserts no interest in any land. Machine-readable versions accompany this sheet as",
    "appendix_C_aoi.geojson and appendix_C_aoi.kml.",
]:
    d.text((M, y), t_, font=F(21, True) if t_.startswith(("Extent", "Approximate", "Coordinate")) else F(20), fill=INK if t_ else MUT)
    y += 34

d.text((M, H - 54), f"Generated {TODAY} · LHDRS Mission 6 · appendix_C_aoi.geojson",
       font=F(17), fill=MUT)

out_png = os.path.join(APP, "appendix_C_aoi_MAP.png")
im.save(out_png)
print("wrote", out_png)

# KML, because several agency counters take KML but not GeoJSON
def kml_ring(r):
    return " ".join(f"{p[0]:.6f},{p[1]:.6f},0" for p in r)
k = ['<?xml version="1.0" encoding="UTF-8"?>',
     '<kml xmlns="http://www.opengis.net/kml/2.2"><Document>',
     '<name>Appendix C - LHDRS project AOI, Ladera Ranch</name>',
     '<description>Study area for an independent historical land-development research project. '
     'Not a property boundary and not a parcel.</description>',
     '<Style id="aoi"><LineStyle><color>ff be6e34</color><width>3</width></LineStyle>'
     '<PolyStyle><color>26be6e34</color></PolyStyle></Style>']
for i, r in enumerate(rings):
    k += [f'<Placemark><name>AOI {i+1}</name><styleUrl>#aoi</styleUrl><Polygon>'
          f'<outerBoundaryIs><LinearRing><coordinates>{kml_ring(r)}</coordinates>'
          f'</LinearRing></outerBoundaryIs></Polygon></Placemark>']
k += ['</Document></kml>']
out_kml = os.path.join(APP, "appendix_C_aoi.kml")
open(out_kml, "w").write("\n".join(k).replace("ff be6e34", "ffbe6e34"))
print("wrote", out_kml)

json.dump({
 "generated": TODAY,
 "derivedFrom": "data/development/mission6_appendices/appendix_C_aoi.geojson",
 "outputs": ["appendix_C_aoi_MAP.png", "appendix_C_aoi.kml"],
 "extent": {"west": lo0, "east": lo1, "south": la0, "north": la1},
 "approxSizeKm": {"eastWest": round(wkm, 2), "northSouth": round(hkm, 2)},
 "crs": "EPSG:4326",
 "basemap": "none - no third-party tiles fetched, so no tile licence travels with an agency submission",
 "provenanceGrade": "A2", "statementClass": "documented",
 "note": "Study area only. Not a property boundary, not a parcel, asserts no interest in any land.",
 "sha256_png": hashlib.sha256(open(out_png, "rb").read()).hexdigest(),
 "sha256_kml": hashlib.sha256(open(out_kml, "rb").read()).hexdigest(),
}, open(os.path.join(APP, "appendix_C_aoi_MAP.provenance.json"), "w"), indent=1)
print("provenance written")
