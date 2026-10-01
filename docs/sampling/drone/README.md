# Drone reconnaissance map — Arroyo Trabuco

`fetch.py` pulls the OC Survey 2025 countywide 1-ft aerial for the corridor
(bbox -117.6700,-117.6440 / 33.5300,33.5640) as three vertical tiles and
stitches them. Pixel dimensions are computed from the **true ground aspect**
(metres, not degrees) — requesting a 4326 bbox at a degree-derived aspect is
what produced the vertical stretch in the earlier testing map.

`plot.py` draws the ten stations; `foot.py` adds the guidance panels.

Station sources:
- D2 — the 1948 USGS ranch structure, EM-009, `data/geospatial/topo1948_footprint.json`
- D3–D10 — 1968 USGS surface-water bodies, `data/geospatial/topo1968_water.geojson`,
  cross-referenced to the 23 sampling targets in `docs/sampling/targets_data.json`
- D1 — the August 2026 concrete feature. **Its coordinates are deliberately not
  held in this repository** and are not in these scripts.

Output is **not committed**: the rendered map carries locational data and the
project rule is that no coordinates of the concrete feature or the pond appear
on the public site.
