#!/usr/bin/env python3
"""
Mission 7 / Phase 3c - true-colour time-lapse frames over a SQUARE AOI centred on Ladera Ranch.

Pulls the best (AOI-clear) Landsat scene per month, 1997-2006, renders true-colour RGB, and writes
numbered frames plus a contact sheet. Frames feed the reconstruction engine's video export.

Cadence reality:
  Landsat 5 and Landsat 7 each revisit every 16 days, offset ~8 days, so the combined theoretical
  cadence is ~8 days. Practical cadence is set by cloud over this small AOI, not by orbit.

Scene-level cloud % is a POOR proxy here: the AOI is ~6 km across inside a ~180 km scene, so a 20%
cloudy scene may be perfectly clear over Ladera Ranch, or wholly obscured. This script therefore
tests ACTUAL per-AOI validity with QA_PIXEL and keeps only frames that pass.

provenanceGrade A+ (USGS/NASA) · statementClass documented (true-colour imagery, no index applied)
NOTE: unlike the NDVI products, a true-colour frame IS documented imagery. Interpretation only
enters if someone draws conclusions from it.
"""
from __future__ import annotations
import json, os, ssl, datetime, urllib.request, urllib.parse
import numpy as np

# ---- square AOI (~6 km x 6 km ground) centred on Ladera Ranch
CLON, CLAT = -117.641577, 33.551148
KM = 6.0
dlat = (KM / 2) / 111.0
dlon = (KM / 2) / (111.320 * np.cos(np.radians(CLAT)))
BBOX = [CLON - dlon, CLAT - dlat, CLON + dlon, CLAT + dlat]

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO, "evidence/lhdrs/mission7")
FRAMES = os.path.join(OUT, "timelapse_frames")
os.makedirs(FRAMES, exist_ok=True)
TODAY = datetime.date.today().isoformat()
CTX = ssl.create_default_context()
UA = {"User-Agent": "LHDRS-Mission7/1.0", "Content-Type": "application/json"}
STAC = "https://planetarycomputer.microsoft.com/api/stac/v1/search"
SIGN = "https://planetarycomputer.microsoft.com/api/sas/v1/sign?href="
MIN_CLEAR = 0.92          # require 92% of AOI pixels valid
TRY_PER_MONTH = 4         # scenes to attempt per month, best-cloud first


def post(b):
    r = urllib.request.Request(STAC, headers=UA, data=json.dumps(b).encode())
    with urllib.request.urlopen(r, timeout=60, context=CTX) as f:
        return json.load(f)


def sign(h):
    r = urllib.request.Request(SIGN + urllib.parse.quote(h, safe=""), headers={"User-Agent": UA["User-Agent"]})
    with urllib.request.urlopen(r, timeout=60, context=CTX) as f:
        return json.load(f)["href"]


import rasterio
from rasterio.warp import transform_bounds
from rasterio.windows import from_bounds
from PIL import Image, ImageDraw, ImageFont

FD = "/System/Library/Fonts/Supplemental/"


def F(s, b=False):
    p = FD + ("Arial Bold" if b else "Arial") + ".ttf"
    return ImageFont.truetype(p, s) if os.path.exists(p) else ImageFont.load_default()


def read_rgb(feat):
    def band(n):
        return rasterio.open(sign(feat["assets"][n]["href"]))
    out = {}
    with band("red") as r:
        b = transform_bounds("EPSG:4326", r.crs, *BBOX)
        w = from_bounds(*b, transform=r.transform)
        out["r"] = r.read(1, window=w).astype("float32")
        shape = out["r"].shape
    for k, a in (("g", "green"), ("b", "blue")):
        with band(a) as s:
            out[k] = s.read(1, window=from_bounds(*transform_bounds("EPSG:4326", s.crs, *BBOX),
                                                  transform=s.transform)).astype("float32")
    with band("qa_pixel") as q:
        qa = q.read(1, window=from_bounds(*transform_bounds("EPSG:4326", q.crs, *BBOX),
                                          transform=q.transform)).astype("uint16")
    # trim to common shape
    h = min(v.shape[0] for v in list(out.values()) + [qa])
    w_ = min(v.shape[1] for v in list(out.values()) + [qa])
    for k in out:
        out[k] = out[k][:h, :w_] * 0.0000275 - 0.2
    qa = qa[:h, :w_]
    bad = ((qa & 1) | (qa & 2) | (qa & 8) | (qa & 16)) > 0
    valid = (~bad) & np.isfinite(out["r"])
    return out, valid


def stretch(a, valid):
    v = a[valid]
    if v.size < 50:
        return np.zeros_like(a)
    lo, hi = np.percentile(v, 2), np.percentile(v, 98)
    return np.clip((a - lo) / max(hi - lo, 1e-6), 0, 1)


# ---------------- gather candidates by month ----------------
print(f"square AOI {KM} km: {[round(x,5) for x in BBOX]}\n")
cand = {}
for y in range(1997, 2007):
    d = post({"collections": ["landsat-c2-l2"], "bbox": BBOX,
              "datetime": f"{y}-01-01T00:00:00Z/{y}-12-31T23:59:59Z", "limit": 400})
    for f in d.get("features", []):
        dt = f["properties"].get("datetime", "")[:10]
        c = f["properties"].get("eo:cloud_cover")
        if not dt or c is None:
            continue
        cand.setdefault(dt[:7], []).append((c, dt, f["properties"].get("platform", ""), f))
months = sorted(cand)
print(f"candidate months: {len(months)}  (total scenes {sum(len(v) for v in cand.values())})\n")

frames = []
for m in months:
    lst = sorted(cand[m], key=lambda x: x[0])[:TRY_PER_MONTH]
    for c, dt, plat, feat in lst:
        try:
            bands, valid = read_rgb(feat)
        except Exception:
            continue
        clear = float(valid.mean())
        if clear < MIN_CLEAR:
            continue
        rgb = np.dstack([stretch(bands["r"], valid), stretch(bands["g"], valid), stretch(bands["b"], valid)])
        rgb = (np.clip(rgb, 0, 1) * 255).astype(np.uint8)
        rgb[~valid] = (90, 90, 96)
        frames.append({"month": m, "date": dt, "platform": plat, "clearPct": round(clear * 100, 1),
                       "sceneCloud": round(c, 1), "rgb": rgb})
        print(f"  {dt}  {plat:<10} AOI clear {clear*100:5.1f}%  (scene cloud {c:4.1f}%)")
        break

print(f"\nUSABLE FRAMES: {len(frames)} of {len(months)} months")

# ---------------- write frames ----------------
h, w = frames[0]["rgb"].shape[:2]
SC = max(1, int(520 / max(h, w)))
for i, fr in enumerate(frames):
    im = Image.fromarray(fr["rgb"]).resize((w * SC, h * SC), Image.LANCZOS)
    d = ImageDraw.Draw(im)
    d.rectangle([0, im.height - 34, im.width, im.height], fill=(15, 20, 30))
    d.text((10, im.height - 27), fr["date"], font=F(19, True), fill=(255, 255, 255))
    d.text((im.width - 150, im.height - 26), "Landsat  A+", font=F(13), fill=(190, 196, 206))
    im.save(os.path.join(FRAMES, f"frame_{i:03d}_{fr['date']}.png"))

# ---------------- contact sheet ----------------
COLS = 10
rows = (len(frames) + COLS - 1) // COLS
TW, TH, PAD, TOP = w * 2, h * 2, 6, 120
W = COLS * TW + (COLS + 1) * PAD
H = TOP + rows * (TH + 20) + PAD + 120
sheet = Image.new("RGB", (W, H), (250, 249, 246))
dr = ImageDraw.Draw(sheet)
dr.text((PAD + 6, 26), f"Ladera Ranch, Landsat true colour, {frames[0]['date'][:4]}-{frames[-1]['date'][:4]}",
        font=F(30, True), fill=(22, 35, 58))
dr.text((PAD + 6, 66), f"{len(frames)} cloud-free frames over a {KM:.0f} km square. 30 m pixels: neighbourhood scale, individual homes are not resolvable.",
        font=F(16), fill=(110, 116, 126))
dr.rounded_rectangle([PAD + 6, 92, PAD + 130, 118], 6, fill=(43, 120, 58))
dr.text((PAD + 20, 98), "A+  imagery", font=F(13, True), fill=(255, 255, 255))
for i, fr in enumerate(frames):
    cx, cy = i % COLS, i // COLS
    ox, oy = PAD + cx * (TW + PAD), TOP + cy * (TH + 20)
    sheet.paste(Image.fromarray(fr["rgb"]).resize((TW, TH), Image.LANCZOS), (ox, oy))
    dr.text((ox, oy + TH + 3), fr["date"], font=F(10), fill=(70, 78, 90))
ly = TOP + rows * (TH + 20) + 14
dr.line([PAD, ly, W - PAD, ly], fill=(222, 226, 232))
for i, t in enumerate([
    "True-colour Landsat surface reflectance. 30 m pixels: grading extent, road corridors and large structures are visible; individual houses are not.",
    "Frames are the clearest scene in each month that passed a 92% AOI-clear test. Months with no qualifying scene are absent, so spacing is uneven.",
    "Ground conditions only. Not a contamination, dust or exposure product.",
]):
    dr.text((PAD, ly + 14 + i * 22), "- " + t, font=F(14), fill=(70, 78, 90))
dr.text((PAD, H - 30), f"Landsat C2 L2, USGS/NASA via Microsoft Planetary Computer  ·  generated {TODAY}",
        font=F(12), fill=(110, 116, 126))
sheet.save(os.path.join(OUT, "timelapse_contact_sheet.png"))

json.dump({"generated": TODAY, "squareAoiKm": KM, "bbox": BBOX, "provenanceGrade": "A+",
           "statementClass": "documented",
           "frameCount": len(frames), "monthsWithCandidates": len(months),
           "frames": [{k: v for k, v in f.items() if k != "rgb"} for f in frames]},
          open(os.path.join(OUT, "timelapse_manifest.json"), "w"), indent=1)
print(f"wrote {len(frames)} frames + contact sheet")
