#!/usr/bin/env python3
"""Direct test: are modern homes built on the ranch-era water sites?

For each surface-water body mapped by USGS in 1968, count OSM building footprints within
100 m and record the nearest one. Then compare against a null: the same count computed at
random points drawn from the same extent. If housing ignored the old water sites, the
observed counts would look like the null.

Water sites matter here because cattle concentrate at water, and ranch working facilities
-- including, historically, dip vats -- were sited where stock already gathered. This
measures SPATIAL COINCIDENCE ONLY. It is not evidence that a vat existed or that any
contamination is present.
"""
import json, math, os, random
import numpy as np

ROOT = "/Users/andystavros/Ladera-Ranch"
random.seed(20260718)

water = json.load(open(os.path.join(ROOT, "research", "historical_imagery", "topo1968_water.json")))
bl = json.load(open("/tmp/osm_bldg.json"))["elements"]
B = np.array([[e["center"]["lat"], e["center"]["lon"]] for e in bl if "center" in e])
print(f"1968 water bodies: {len(water)}   modern buildings: {len(B)}")

LAT0 = 33.5467
MY = 110540.0
MX = 111320.0 * math.cos(math.radians(LAT0))
bx = B[:, 1] * MX
by = B[:, 0] * MY


def near(lat, lon, radius=100.0):
    d = np.hypot(bx - lon * MX, by - lat * MY)
    return int((d <= radius).sum()), float(d.min())


for wobj in water:
    wobj["n_bldg_100m"], wobj["nearest_bldg_m"] = near(wobj["lat"], wobj["lon"])

# Null: random points over the same extent.
W, E, S, N = -117.680, -117.616, 33.520, 33.575
null = [near(random.uniform(S, N), random.uniform(W, E))[0] for _ in range(4000)]
null = np.array(null)

za = [w for w in water if w["in_zone_a"]]
obs = np.array([w["n_bldg_100m"] for w in water])
obs_za = np.array([w["n_bldg_100m"] for w in za])

print("\n" + "=" * 74)
print("MODERN BUILDINGS WITHIN 100 m OF EACH 1968 SURFACE-WATER BODY")
print("=" * 74)
print(f"{'':38}{'mean':>9}{'median':>9}{'% with >0':>11}")
print(f"{'1968 water sites (all, n=%d)' % len(water):38}{obs.mean():>9.1f}{np.median(obs):>9.1f}"
      f"{(obs > 0).mean()*100:>10.0f}%")
print(f"{'1968 water sites in Zone A (n=%d)' % len(za):38}{obs_za.mean():>9.1f}{np.median(obs_za):>9.1f}"
      f"{(obs_za > 0).mean()*100:>10.0f}%")
print(f"{'random points, same extent (n=4000)':38}{null.mean():>9.1f}{np.median(null):>9.1f}"
      f"{(null > 0).mean()*100:>10.0f}%")

enr = obs.mean() / max(null.mean(), 1e-9)
enr_za = obs_za.mean() / max(null.mean(), 1e-9)
p = float((null.mean(keepdims=True) >= obs.mean()).mean()) if False else \
    float((np.array([np.random.choice(null, len(water)).mean() for _ in range(5000)]) >= obs.mean()).mean())
print(f"\nenrichment, all water sites : {enr:.2f}x")
print(f"enrichment, Zone A sites    : {enr_za:.2f}x")
print(f"permutation p (all sites)   : {p:.4f}")

print("\nWater sites now inside a subdivision (>=1 building within 100 m):")
hit = sorted([w for w in water if w["n_bldg_100m"] > 0], key=lambda x: -x["n_bldg_100m"])
for wobj in hit:
    print(f"  {wobj['lat']:.5f},{wobj['lon']:.5f}  {wobj['area_m2']:6d} m2  "
          f"{wobj['n_bldg_100m']:4d} bldg within 100 m  nearest {wobj['nearest_bldg_m']:6.0f} m"
          f"  {'[Zone A]' if wobj['in_zone_a'] else ''}")

print(f"\nUnbuilt water sites (nearest building >300 m): "
      f"{sum(1 for w in water if w['nearest_bldg_m'] > 300)}/{len(water)}")

res = {
    "n_water_1968": len(water), "n_buildings": int(len(B)),
    "mean_bldg_within_100m_water": round(float(obs.mean()), 2),
    "mean_bldg_within_100m_random": round(float(null.mean()), 2),
    "enrichment": round(float(enr), 2), "enrichment_zone_a": round(float(enr_za), 2),
    "permutation_p": round(p, 4),
    "pct_water_sites_built": round(float((obs > 0).mean()*100), 1),
    "pct_random_built": round(float((null > 0).mean()*100), 1),
    "sites": water,
}
json.dump(res, open(os.path.join(ROOT, "research", "historical_imagery", "premise_homes_on_water.json"), "w"), indent=1)
print("\nwrote research/historical_imagery/premise_homes_on_water.json")
