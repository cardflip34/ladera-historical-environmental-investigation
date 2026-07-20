#!/usr/bin/env python3
"""Detect impounded water and bare-ground disturbance in the 1929-1947 OC aerial frames.

Rationale for the discriminator: on panchromatic film, standing water is both DARK and
SMOOTH. Riparian vegetation is dark but strongly TEXTURED; hillslope shadow is dark but
elongated and attached to a ridge. Requiring low local variance alongside low brightness
separates ponds from the two things that otherwise dominate a naive dark-blob search.

Candidates are written out for visual verification. Nothing here is published to the map
until a human has looked at it — the topo-sheet detector in the previous pass returned
24/25 false positives, so automated output is treated as a shortlist, not a finding.
"""
import json, math, os
import numpy as np
from PIL import Image
from scipy import ndimage

D = "/Users/andystavros/Ladera-Ranch/research/historical_imagery/oc_aerials"
W, E = -117.680, -117.616
S, N = 33.51976666666666, 33.57523333333334

CLAT, CLON = 33.5467, -117.6403
DLAT = 1.0 / 69.0
DLON = 1.25 / (69.0 * math.cos(math.radians(CLAT)))
ZONE_A = (CLON - DLON, CLAT - DLAT, CLON + DLON, CLAT + DLAT)


def to_ll(x, y, sz):
    return (W + x / sz[0] * (E - W), N - y / sz[1] * (N - S))


def m_per_px(sz):
    return (E - W) * 111320 * math.cos(math.radians(CLAT)) / sz[0]


def detect(tag):
    im = Image.open(os.path.join(D, f"{tag}.jpg")).convert("L")
    a = np.asarray(im, dtype=np.float32)
    sz = im.size
    mpp = m_per_px(sz)

    # Local mean/variance over a ~25 m window.
    k = max(3, int(round(25.0 / mpp)) | 1)
    mean = ndimage.uniform_filter(a, k)
    sq = ndimage.uniform_filter(a * a, k)
    var = np.clip(sq - mean * mean, 0, None)
    std = np.sqrt(var)

    valid = a > 4                       # exclude the black no-data wedge
    dark = a < np.percentile(a[valid], 12)
    smooth = std < np.percentile(std[valid], 20)
    water = dark & smooth & valid

    water = ndimage.binary_opening(water, np.ones((3, 3)))
    water = ndimage.binary_closing(water, np.ones((3, 3)))
    lab, n = ndimage.label(water)

    # A stock pond is roughly 15-120 m across and compact.
    lo = (15.0 / mpp) ** 2 * 0.5
    hi = (120.0 / mpp) ** 2
    out = []
    for i, sl in enumerate(ndimage.find_objects(lab), start=1):
        m = lab[sl] == i
        area = int(m.sum())
        if not (lo <= area <= hi):
            continue
        h, w = m.shape
        if max(h, w) / max(1, min(h, w)) > 2.6:      # reject elongated shadow/channel
            continue
        fill = area / float(h * w)
        if fill < 0.45:
            continue
        cy = sl[0].start + ndimage.center_of_mass(m)[0]
        cx = sl[1].start + ndimage.center_of_mass(m)[1]
        lon, lat = to_ll(cx, cy, sz)
        in_a = ZONE_A[0] <= lon <= ZONE_A[2] and ZONE_A[1] <= lat <= ZONE_A[3]
        out.append({
            "year": tag, "lat": round(float(lat), 5), "lon": round(float(lon), 5),
            "area_px": area, "diam_m": round(math.sqrt(area / math.pi) * 2 * mpp, 1),
            "fill": round(float(fill), 2), "in_zone_a": bool(in_a),
            "mean_dn": round(float(a[sl][m].mean()), 1),
            "px": [int(cx), int(cy)],
        })
    out.sort(key=lambda r: -r["area_px"])
    print(f"  {tag}: {n} raw components -> {len(out)} pond-shaped candidates "
          f"({sum(1 for r in out if r['in_zone_a'])} inside Zone A), {mpp:.2f} m/px")
    return out


if __name__ == "__main__":
    print("Detecting impounded water in pre-1950 aerials (shortlist for visual review)...")
    res = {t: detect(t) for t in ["1929", "1937", "1946b"]}
    p = os.path.join(D, "water_candidates.json")
    json.dump(res, open(p, "w"), indent=1)
    print(f"\nwrote {p}")
    for t, rows in res.items():
        for r in rows[:8]:
            flag = "ZONE-A" if r["in_zone_a"] else "      "
            print(f"  {t} {flag} {r['lat']:.5f},{r['lon']:.5f}  {r['diam_m']:5.1f} m  fill {r['fill']}  DN {r['mean_dn']}")
