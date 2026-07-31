#!/usr/bin/env python3
"""
Vat hunt, stage 2 - find rectilinear anomalies in rangeland.

WHAT IT LOOKS FOR, and why:
Nature is not straight. Rangeland at 0.2 m/px is dominated by curved drainage, scattered oaks,
grazing texture and slope shading. A dipping station is the opposite - a SWIM VAT is a long
straight channel, and it comes attached to a holding corral, an approach chute and a drain pen.
All of those are straight lines meeting at angles.

So the detector does not hunt for "a vat". It hunts for LOCAL CONCENTRATIONS OF STRAIGHT EDGES
in orthogonal pairs, which is the signature of built enclosure in an otherwise natural scene.

METHOD (deliberately simple and inspectable, not a black box):
  1. Sobel gradients -> edge magnitude and orientation
  2. Keep only strong edges
  3. Per cell, build an orientation histogram. Natural texture is broadly distributed;
     built structure concentrates into one or two dominant directions.
  4. Score = edge density x orientation concentration x orthogonality bonus
  5. Suppress the known false-positive classes explicitly (see below)

FALSE POSITIVES THIS WILL PRODUCE, and it is important to say so up front:
  - modern roads, field boundaries, fence lines, firebreaks, orchard rows
  - the image tile edges themselves
  - scan artefacts, film scratches, and the seams of the source photo mosaic
A high score means "rectilinear", NOT "vat". Every candidate needs a human eye, and persistence
across independent years is the only cheap filter that separates a real ground feature from a
film artefact.

OUTPUT: ranked candidates with coordinates + a contact sheet of crops for visual review.
NOTHING HERE IDENTIFIES A VAT. It narrows where to look.
"""
from __future__ import annotations
import json, os, math, datetime, glob
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage as ndi
Image.MAX_IMAGE_PIXELS = None

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO, "evidence/lhdrs/vat_hunt")
TODAY = datetime.date.today().isoformat()
MAN = json.load(open(os.path.join(OUT, "tile_manifest.json")))
GSD = MAN["gsdMeters"]

CELL_M = 40.0                      # analysis cell ~ the size of a corral + vat assembly
CELL = max(24, int(CELL_M / GSD))
EDGE_PCT = 88                      # keep the top N% of gradient magnitudes as "edges"
MIN_EDGE_FRAC = 0.04               # cell must actually contain edges

FD = "/System/Library/Fonts/Supplemental/"
def F(s, b=False):
    p = FD + ("Arial Bold" if b else "Arial") + ".ttf"
    return ImageFont.truetype(p, s) if os.path.exists(p) else ImageFont.load_default()


def score_tile(path, bbox, px):
    im = Image.open(path).convert("L")
    a = np.asarray(im).astype(np.float32) / 255.0
    a = ndi.gaussian_filter(a, 1.0)

    gx = ndi.sobel(a, axis=1)
    gy = ndi.sobel(a, axis=0)
    mag = np.hypot(gx, gy)
    ang = (np.arctan2(gy, gx) % np.pi)                 # 0..pi, undirected

    thr = np.percentile(mag, EDGE_PCT)
    strong = mag > thr

    h, w = a.shape
    # EDGE SUPPRESSION. The first run's top candidates were almost all on tile seams and the AOI
    # boundary - the detector was finding its own crop edges, which are perfectly straight and
    # perfectly orthogonal, i.e. the ideal false positive. Skip a margin of one full cell.
    ny, nx = h // CELL, w // CELL
    MARGIN = 1
    NB = 18                                            # 10-degree orientation bins
    out = []
    for iy in range(MARGIN, ny-MARGIN):
        for ix in range(MARGIN, nx-MARGIN):
            ys, xs = iy*CELL, ix*CELL
            win = a[ys:ys+CELL, xs:xs+CELL]
            # nodata fill and blown highlights have hard straight borders - reject those windows
            if (win > 0.985).mean() > 0.10 or (win < 0.02).mean() > 0.10:
                continue
            m = strong[ys:ys+CELL, xs:xs+CELL]
            frac = float(m.mean())
            if frac < MIN_EDGE_FRAC:
                continue
            th = ang[ys:ys+CELL, xs:xs+CELL][m]
            wt = mag[ys:ys+CELL, xs:xs+CELL][m]
            hist, _ = np.histogram(th, bins=NB, range=(0, math.pi), weights=wt)
            if hist.sum() <= 0:
                continue
            hist = hist / hist.sum()
            # orientation concentration: 1 - normalised entropy. built = concentrated.
            ent = -(hist[hist > 0] * np.log(hist[hist > 0])).sum() / math.log(NB)
            conc = 1.0 - ent
            # orthogonality: is there a strong second peak ~90 degrees from the first?
            k = int(np.argmax(hist))
            ortho = float(hist[(k + NB // 2) % NB])
            # linearity: dominant bin share
            dom = float(hist[k])
            s = frac * (conc ** 1.5) * (1.0 + 4.0 * ortho) * (0.5 + dom)
            cx = xs + CELL/2; cy = ys + CELL/2
            lon = bbox[0] + (cx / px) * (bbox[2] - bbox[0])
            lat = bbox[3] - (cy / px) * (bbox[3] - bbox[1])
            out.append({"score": float(s), "edgeFrac": frac, "concentration": float(conc),
                        "orthoPeak": ortho, "dominantShare": dom,
                        "lon": round(lon, 6), "lat": round(lat, 6),
                        "tile": os.path.basename(path), "px": [int(cx), int(cy)]})
    return out


allc = []
for t in MAN["tiles"]:
    p = os.path.join(REPO, t["path"])
    if not os.path.exists(p):
        continue
    if t["nodataFraction"] > 0.5:
        continue
    c = score_tile(p, t["bbox"], t["px"])
    for x in c:
        x["frame"] = t["frame"]
    allc += c
    print(f"  {t['frame']} r{t['row']}c{t['col']}  {len(c)} cells scored")

if not allc:
    print("no tiles available yet - run lhdrs_vat_hunt_fetch.py first")
    raise SystemExit

# normalise per frame so frames of different contrast are comparable
for fr in set(c["frame"] for c in allc):
    s = np.array([c["score"] for c in allc if c["frame"] == fr])
    mu, sd = s.mean(), s.std() + 1e-9
    for c in allc:
        if c["frame"] == fr:
            c["z"] = float((c["score"] - mu) / sd)

allc.sort(key=lambda c: -c["z"])

# ---- cross-frame persistence: a real ground feature appears in more than one year -----------
def near(a, b, m=60):
    return math.hypot((a["lon"]-b["lon"])*92500, (a["lat"]-b["lat"])*111000) < m

top = [c for c in allc if c["z"] > 2.5]
clusters = []
for c in top:
    for cl in clusters:
        if near(c, cl["rep"]):
            cl["members"].append(c)
            cl["frames"].add(c["frame"])
            break
    else:
        clusters.append({"rep": c, "members": [c], "frames": {c["frame"]}})

# ---- COMPACTNESS FILTER -------------------------------------------------------------------
# Second run was still dominated by a single ~3 km straight line at lon -117.674 - a road or a
# field boundary, exactly the predicted false positive. A road makes a long CHAIN of high-score
# cells; a dipping station makes a compact BLOB about 50-100 m across. So reject candidates whose
# high-scoring neighbourhood extends like a line.
def neighbourhood_extent(c, radius_m=400):
    xs, ys = [], []
    for o in top:
        if o["frame"] != c["frame"]:
            continue
        dx = (o["lon"]-c["lon"])*92500; dy = (o["lat"]-c["lat"])*111000
        if math.hypot(dx, dy) <= radius_m:
            xs.append(dx); ys.append(dy)
    if len(xs) < 2:
        return 0.0, 1.0
    X = np.array(xs); Y = np.array(ys)
    pts = np.vstack([X, Y])
    pts = pts - pts.mean(axis=1, keepdims=True)
    cov = np.cov(pts) if pts.shape[1] > 1 else np.eye(2)
    ev = np.sort(np.linalg.eigvalsh(cov))[::-1]
    extent = float(2*math.sqrt(max(ev[0], 0)))
    elong = float(math.sqrt(max(ev[0], 1e-9) / max(ev[1], 1e-9)))
    return extent, elong

for cl in clusters:
    cl["nFrames"] = len(cl["frames"])
    cl["maxZ"] = max(m["z"] for m in cl["members"])
    ext, elong = neighbourhood_extent(cl["rep"])
    cl["neighbourhoodExtentM"] = round(ext, 1)
    cl["elongation"] = round(elong, 2)
    # a compact, isolated, orthogonal cluster is what we want
    compact = 1.0 if ext < 160 else (160.0/ext)
    linear_penalty = 1.0 if elong < 2.5 else (2.5/elong)
    cl["persistScore"] = cl["maxZ"] * (1 + 0.8*(cl["nFrames"]-1)) * compact * linear_penalty
clusters.sort(key=lambda c: -c["persistScore"])

print(f"\n{len(allc)} cells scored, {len(top)} above z=2.5, {len(clusters)} spatial clusters")
print(f"\nTOP CANDIDATES (persistence-weighted)\n")
print(f"  {'#':<4}{'lat':>10}{'lon':>12}{'maxZ':>7}{'yrs':>5}{'extent m':>10}{'elong':>7}  years")
rows = []
for i, cl in enumerate(clusters[:25], 1):
    r = cl["rep"]
    yrs = ",".join(sorted(cl["frames"]))
    print(f"  {i:<4}{r['lat']:>10.5f}{r['lon']:>12.5f}{cl['maxZ']:>7.1f}{cl['nFrames']:>5}{cl['neighbourhoodExtentM']:>10.0f}{cl['elongation']:>7.1f}  {yrs}")
    rows.append({"rank": i, "lat": r["lat"], "lon": r["lon"],
                 "maxZ": round(cl["maxZ"], 2), "framesSeen": sorted(cl["frames"]),
                 "nFrames": cl["nFrames"], "persistScore": round(cl["persistScore"], 2),
                 "neighbourhoodExtentM": cl["neighbourhoodExtentM"], "elongation": cl["elongation"],
                 "tile": r["tile"], "px": r["px"]})

json.dump({"generated": TODAY, "statementClass": "interpreted",
           "method": "Sobel gradient orientation concentration + orthogonality, per 40 m cell",
           "gsdMeters": GSD, "cellPx": CELL,
           "whatHighScoreMeans": "RECTILINEAR, not vat. Roads, fences, field boundaries, "
                                 "firebreaks, orchard rows, tile edges and film artefacts all "
                                 "score high. Human review is mandatory.",
           "persistenceLogic": "A real ground feature should appear in more than one independent "
                               "year of photography. A film artefact should not.",
           "cellsScored": len(allc), "aboveThreshold": len(top), "clusters": len(clusters),
           "candidates": rows},
          open(os.path.join(OUT, "vat_candidates.json"), "w"), indent=1)
print(f"\nwrote {OUT}/vat_candidates.json")

# ---- contact sheet of the top candidates for human review -----------------------------------
CROP_M = 120
half = int(CROP_M / GSD / 2)
cols, thumb = 5, 300
show = clusters[:20]
rowsN = (len(show) + cols - 1) // cols
sheet = Image.new("RGB", (cols*thumb + 40, rowsN*(thumb+52) + 90), (250, 249, 246))
sd = ImageDraw.Draw(sheet)
sd.rectangle([0, 0, sheet.width, 8], fill=(196, 55, 42))
sd.text((20, 24), "Rectilinear candidates for human review", font=F(28, True), fill=(20, 28, 42))
sd.text((20, 60), "High score = straight edges in orthogonal pairs. NOT an identification of a vat.",
        font=F(16), fill=(110, 116, 126))
for i, cl in enumerate(show):
    r = cl["rep"]
    tp = None
    for t in MAN["tiles"]:
        if os.path.basename(t["path"]) == r["tile"]:
            tp = t; break
    if not tp: continue
    im = Image.open(os.path.join(REPO, tp["path"])).convert("RGB")
    x, y = r["px"]
    crop = im.crop((max(0, x-half), max(0, y-half),
                    min(im.width, x+half), min(im.height, y+half))).resize((thumb, thumb), Image.LANCZOS)
    cx = 20 + (i % cols)*thumb
    cy = 90 + (i // cols)*(thumb+52)
    sheet.paste(crop, (cx, cy))
    dd = ImageDraw.Draw(sheet)
    dd.rectangle([cx, cy, cx+thumb-1, cy+thumb-1], outline=(196, 55, 42), width=2)
    dd.line([cx+thumb//2-10, cy+thumb//2, cx+thumb//2+10, cy+thumb//2], fill=(255, 80, 60), width=2)
    dd.line([cx+thumb//2, cy+thumb//2-10, cx+thumb//2, cy+thumb//2+10], fill=(255, 80, 60), width=2)
    dd.text((cx+3, cy+thumb+4), f"#{i+1}  z={cl['maxZ']:.1f}  {','.join(sorted(cl['frames']))}",
            font=F(14, True), fill=(20, 28, 42))
    dd.text((cx+3, cy+thumb+24), f"{r['lat']:.5f}, {r['lon']:.5f}", font=F(13), fill=(110, 116, 126))
sp = os.path.join(OUT, "vat_candidates_contact_sheet.png")
sheet.save(sp)
print("wrote", sp)
