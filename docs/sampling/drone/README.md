# Drone reconnaissance — ungraded ground only

The first version of this map carried all ten stations the 1968 USGS water
survey suggested. **Four of them were golf course.** This version filters every
candidate against the **OC Survey 1990 countywide frame** (Historic_Imagery_v2,
OBJECTID 319), which predates both the Arroyo Trabuco golf course and the
1999–2003 Ladera mass grading, and keeps a station only where the ground is
unchanged between 1990 and 2025.

Sixteen of the twenty-three targets are excluded: four are golf course, eight
are under Ladera housing, four are pre-1990 Mission Viejo.

- `fetch2.py`   — 2025 and 1990 bases for the tightened corridor bbox
                  (-117.6680,-117.6480 / 33.5330,33.5620). Pixel dimensions are
                  computed from **true ground aspect** in metres, not degrees.
- `fetch1990.py`— the wider 1990 frame used for the first comparison sheet.
- `plot2.py`    — the seven surviving stations plus the exclusion callouts.
- `foot2.py`    — then/now evidence strip and field guidance.

## Two findings that came out of looking rather than computing

1. **D4 and D5 sit under closed oak canopy.** A nadir grid there maps treetops.
   Noted on the map and in the field card.
2. **T19 was bottom of the old list and is now D7, promoted.** The imagery shows
   it as the most open, least disturbed ground in the set — no canopy, nothing
   built — which makes it the best available picture of native grade.

An automated spectral split of irrigated turf from native vegetation was tried
and **abandoned**: in October the live oaks in the riparian corridor are as
green as the fairways, and the classifier flagged both. The 1990 comparison is
the honest filter.

Station sources: `data/geospatial/topo1968_water.geojson`,
`data/geospatial/topo1948_footprint.json` (EM-009), and
`docs/sampling/targets_data.json`.

**D1, the August 2026 concrete feature, is not plotted and its coordinates are
not in this repository.** Rendered output is not committed — it carries
locational data.

## Waypoints

`gen.py` builds the waypoint geometry for the six plotted stations (orbit: 8 points,
40 m radius, 28 m AGL, gimbal −35°, heading to centre; grid: 150 × 150 m, 30 m line
spacing, 60 m AGL, nadir, on D2/D3/D7 only) and queries the **USGS 1 m DEM**
(`epqs.nationalmap.gov`) for ground elevation at **every** waypoint.

`export.py` writes KML, per-station Litchi Mission Hub CSVs, GPX and a plain list.

**Altitudes are terrain-corrected and relative to a launch at the station centre.**
Each waypoint's commanded altitude is `target_AGL + (ground_wp − ground_centre)`, so
the aircraft holds constant height above ground. Relief inside a station set reaches
22.1 m at D7, 14.3 m at D6, 12.3 m at D6b, 11.6 m at D3. Launching anywhere other
than the centre invalidates the numbers.

`d1.py <lat> <lon>` regenerates the identical set for D1, whose coordinate is
deliberately not stored here.

No DJI WPML KMZ is generated: it cannot be tested from here, and a waypoint file
that imports with subtly wrong altitudes is worse than no file. DJI Pilot 2 users
should import the KML survey polygon into the built-in Mapping mission instead.

D4 and D5 get no grid by design — closed oak canopy.

Rendered map and waypoint exports are **not committed**: locational data.
