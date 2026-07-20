#!/usr/bin/env python3
"""Test the proposition that modern housing occupies the same ground as the historic
water sources and cattle-working areas of the ranch period.

Method: derive the drainage network from a 3DEP DEM by flow accumulation, then compare
the terrain occupied by 10,618 real OSM building footprints against the terrain available
across the same extent. If housing were placed without regard to landform, the two
distributions would match. Reported as a ratio, with the null (available land) shown
alongside so the reader can see the comparison rather than take the ratio on trust.

This tests SPATIAL COINCIDENCE ONLY. It cannot and does not establish that a dip vat
existed, that arsenic is present, or that any exposure occurred.
"""
import json, math, os
import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = "/Users/andystavros/Ladera-Ranch"
DEM = os.path.join(ROOT, "data", "geospatial", "dem_3dep.tif")
W, E, S, N = -117.680, 33.520, -117.616, 33.575
W, E = -117.680, -117.616
S, N = 33.520, 33.575


def load_dem():
    im = Image.open(DEM)
    a = np.array(im, dtype=np.float64)
    a[a < -1e30] = np.nan
    return a


def slope_deg(z, xres_m, yres_m):
    gy, gx = np.gradient(z, yres_m, xres_m)
    return np.degrees(np.arctan(np.hypot(gx, gy)))


def flow_accum(z):
    """D8 accumulation on a pit-filled surface, processed in descending-elevation order."""
    zf = z.copy()
    for _ in range(60):                       # iterative pit filling
        mn = ndimage.minimum_filter(zf, 3)
        raised = np.maximum(zf, np.where(np.isfinite(mn), mn + 1e-4, zf))
        interior = np.zeros_like(zf, dtype=bool)
        interior[1:-1, 1:-1] = True
        new = np.where(interior, np.minimum(raised, np.nanmax(zf)), zf)
        if np.allclose(new, zf, equal_nan=True):
            break
        zf = new

    h, w = zf.shape
    acc = np.ones((h, w), dtype=np.float64)
    order = np.argsort(zf.ravel())[::-1]
    nb = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]
    for idx in order:
        r, c = divmod(int(idx), w)
        if not np.isfinite(zf[r, c]):
            continue
        best, bs = None, 0.0
        for dr, dc in nb:
            rr, cc = r + dr, c + dc
            if 0 <= rr < h and 0 <= cc < w and np.isfinite(zf[rr, cc]):
                d = (zf[r, c] - zf[rr, cc]) / math.hypot(dr, dc)
                if d > bs:
                    bs, best = d, (rr, cc)
        if best:
            acc[best] += acc[r, c]
    return acc


def main():
    z = load_dem()
    h, w = z.shape
    xres = (E - W) * 111320 * math.cos(math.radians(33.5467)) / w
    yres = (N - S) * 110540 / h
    print(f"DEM {w}x{h}  {xres:.1f} x {yres:.1f} m/px")
    print(f"elevation {np.nanmin(z):.0f}-{np.nanmax(z):.0f} m")

    sl = slope_deg(z, xres, yres)
    print("computing flow accumulation (D8)...")
    acc = flow_accum(z)

    # Channels: cells draining >= 12 ha. Valley bottom = within 120 m of a channel.
    cell_ha = xres * yres / 10000.0
    chan = acc * cell_ha >= 12.0
    dist_px = ndimage.distance_transform_edt(~chan, sampling=(yres, xres))
    valley = dist_px <= 120.0

    # Height above nearest drainage (HAND), approximated by nearest-channel elevation.
    _, inds = ndimage.distance_transform_edt(~chan, sampling=(yres, xres), return_indices=True)
    hand = z - z[inds[0], inds[1]]

    bl = json.load(open("/tmp/osm_bldg.json"))["elements"]
    pts = [(e["center"]["lat"], e["center"]["lon"]) for e in bl if "center" in e]
    print(f"buildings with centroids: {len(pts)}")

    def px(lat, lon):
        return (int((N - lat) / (N - S) * h), int((lon - W) / (E - W) * w))

    b_sl, b_hand, b_val, b_d = [], [], [], []
    for lat, lon in pts:
        r, c = px(lat, lon)
        if not (0 <= r < h and 0 <= c < w):
            continue
        b_sl.append(sl[r, c]); b_hand.append(hand[r, c])
        b_val.append(bool(valley[r, c])); b_d.append(dist_px[r, c])

    b_sl = np.array(b_sl); b_hand = np.array(b_hand)
    b_val = np.array(b_val); b_d = np.array(b_d)

    fin = np.isfinite(z)
    a_sl = sl[fin]; a_hand = hand[fin]; a_val = valley[fin]; a_d = dist_px[fin]

    res = {
        "n_buildings": int(len(b_sl)),
        "buildings": {
            "pct_in_valley_bottom": round(float(b_val.mean() * 100), 1),
            "median_slope_deg": round(float(np.median(b_sl)), 1),
            "median_dist_to_drainage_m": round(float(np.median(b_d)), 1),
            "median_height_above_drainage_m": round(float(np.median(b_hand)), 1),
        },
        "available_land": {
            "pct_in_valley_bottom": round(float(a_val.mean() * 100), 1),
            "median_slope_deg": round(float(np.median(a_sl)), 1),
            "median_dist_to_drainage_m": round(float(np.median(a_d)), 1),
            "median_height_above_drainage_m": round(float(np.median(a_hand)), 1),
        },
    }
    res["enrichment_valley_bottom"] = round(
        res["buildings"]["pct_in_valley_bottom"] / max(res["available_land"]["pct_in_valley_bottom"], 1e-9), 2)

    print("\n" + "=" * 66)
    print("HOUSING PLACEMENT vs AVAILABLE TERRAIN")
    print("=" * 66)
    b, a = res["buildings"], res["available_land"]
    print(f"{'':34}{'buildings':>12}{'all land':>12}")
    print(f"{'in valley bottom (<120 m of chan)':34}{b['pct_in_valley_bottom']:>11.1f}%{a['pct_in_valley_bottom']:>11.1f}%")
    print(f"{'median slope':34}{b['median_slope_deg']:>11.1f}°{a['median_slope_deg']:>11.1f}°")
    print(f"{'median distance to drainage':34}{b['median_dist_to_drainage_m']:>10.0f} m{a['median_dist_to_drainage_m']:>10.0f} m")
    print(f"{'median height above drainage':34}{b['median_height_above_drainage_m']:>10.1f} m{a['median_height_above_drainage_m']:>10.1f} m")
    print(f"\nvalley-bottom enrichment: {res['enrichment_valley_bottom']}x")

    np.save("/tmp/valley.npy", valley); np.save("/tmp/chan.npy", chan)
    np.save("/tmp/slope.npy", sl); np.save("/tmp/hand.npy", hand)
    json.dump(res, open(os.path.join(ROOT, "research", "historical_imagery",
                                     "premise_water_homes.json"), "w"), indent=1)
    print("\nwrote research/historical_imagery/premise_water_homes.json")


if __name__ == "__main__":
    main()
