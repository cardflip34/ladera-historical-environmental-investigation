# Historical Imagery — Cattle Dipping Areas, Water Sources, and Where the Homes Went

**Prepared:** 2026-07-18. Revised the same day after locating true pre-1940 aerial photography.

**Result up front.** Pre-1950 aerial photography of the footprint was located and retrieved —
**1929, 1931, 1937–38 and 1946–47** — closing most of the gap to the 1907–1917 dipping period.
The footprint was **open rangeland in every pre-1950 frame**. **No dip vat or corral complex
could be identified.** Separately, the 41 surface-water bodies mapped by the 1968 USGS field
survey were extracted and tested against 10,618 modern building footprints. The result is
reported in §6 and it is a **negative** one: homes are *not* preferentially sited on the old
water. Nothing speculative has been plotted.

---

## 1. Sources retrieved

### 1.1 Aerial photography — OC Survey (new, and the significant find)

The previous pass concluded that the earliest available imagery was the 1948 USGS topographic
sheet. **That was wrong.** Orange County operates a public ArcGIS image service holding scanned
historical aerials back to 1929:

```
https://ocgis.com/arcpub/rest/services/Historic_Imagery/Historic_Imagery_v2/ImageServer
```

Note the path is `/arcpub/`, not the conventional `/arcgis/`, which is why earlier attempts
404'd. Thirty-six frames intersect the footprint, spanning 1929–1997. The pre-1950 frames:

| File | Date | Frame | Native res. | Coverage |
|---|---|---|---|---|
| `oc_aerials/1929.jpg` | 1929 | South County Watersheds | 2.6 ft/px | full footprint |
| `oc_aerials/1931.jpg` | 1931 | Irvine Ranch | 2.5 ft/px | partial |
| `oc_aerials/1937.jpg` | 1937–38 | Orange County 600 Scale | **1.15 ft/px** | full footprint |
| `oc_aerials/1938.jpg` | 1938 | Orange County | 3.2 ft/px | full footprint |
| `oc_aerials/1946a.jpg` | 1946 | San Juan Capistrano 600 Scale | 2.2 ft/px | small inset |
| `oc_aerials/1946b.jpg` | 1946–47 | Orange County 1200 Scale | 4.3 ft/px | partial (NW gap) |
| `oc_aerials/2022_modern.jpg` | 2022 | OC 1-ft countywide | 1 ft/px | full footprint |

**Why 1929 matters.** It is **12 years** after compulsory dipping ended, not the 31-year gap of
the 1948 topographic sheet. A vat abandoned in 1917 stood a materially better chance of still
being visible.

### 1.2 Topographic sheets (previous pass, retained)

All four USGS 7.5-minute editions covering the footprint — **1948, 1949, 1968 (revised), and the
1974 orthophoto quad** — as georeferenced GeoTIFFs. Quad: San Juan Capistrano, 1:24,000, NAD27
polyconic. Files `01_`–`04_`, composite `00_`.

### 1.3 Supporting layers

- **3DEP DEM** (`data/geospatial/dem_3dep.tif`), 4.2 × 5.0 m/px.
- **10,618 OSM building footprints** across the same extent, via Overpass.

## 2. Georeferencing

**Aerials:** rectified server-side by OC Survey. Each frame was exported by locked raster ID over
the identical bbox (−117.680, 33.520 → −117.616, 33.575). The service echoes the extent it
actually rendered; it matched the request to **±25 m** (an aspect-ratio snap), so registration is
the county's own and needs no work from us. Verified independently: the modern 2022 export places
Zone A exactly over the real Ladera Ranch subdivisions, and I-5 and Mission Viejo fall where they
belong.

**Topographic sheets:** pixel→lon/lat built with `pyproj` from the `ModelPixelScale` /
`ModelTiepoint` / GeoKey tags and **validated against the quad neatline** to within a pixel. The
1968 sheet's 32′30″ latitude tick reproduces to ~1%.

## 3. What the imagery shows inside the footprint

**1929 — open rangeland.** Grazed hills, the riparian corridor picked out by tree clusters,
unimproved dirt roads, cultivated fields on the valley floor to the south-west toward San Juan
Capistrano. No structures resolvable inside Zone A.

**1937–38 — the best frame in the set.** At 1.15 ft/px, individual oaks, fence lines, wheel ruts
and the braided creek channel are all legible. The corridor along the west side of Zone A carries
dense oak and sycamore woodland. The county cartographer's red ink label reads **"Trabuco Creek"**
— see the correction in §7. Field boundaries and stock trails are visible on the eastern
grasslands. **No corral, pen, chute or vat complex is resolvable anywhere inside Zone A.**

**1946–47 — unchanged.** Still rangeland. The NW quarter falls outside this frame's coverage.

**1968 topographic sheet — water infrastructure is mapped.** A chain of impoundments down the
Trabuco corridor, plus a labelled **"Water Tank"**, a **"Terminal Reservoir"**, a landing strip,
and a gaging station.

**2022 — built out.** Ladera Ranch occupies the central and eastern portions of Zone A; the
western Trabuco corridor is preserved open space.

## 4. The 1968 surface-water layer

Rather than blob-detecting the aerials, hydrography was extracted from the 1968 sheet by
thresholding the **USGS cyan ink** (`pipelines/python/extract_topo_water.py`). Every polygon
recovered this way was drawn by a surveyor who visited the ground — a far stronger source than a
detector's guess about a dark patch.

**41 water bodies ≥350 m², of which 16 fall inside Zone A.** Largest: 24,745 m² at
33.54394, −117.66132. Published as `data/geospatial/topo1968_water.geojson` and live on the
interactive map, sized by mapped area.

## 5. Why a dip vat still cannot be found

The resolution objection is now **gone** — at 1.15 ft/px a 2 m vat is roughly 6 pixels across and
a corral would be unmistakable. Two limits remain, and the second is decisive:

1. **Cartographic convention.** Vats were essentially never mapped; USGS symbology has no vat
   symbol.
2. **Timing, still.** Dipping ran **1907–1917**. The earliest frame is **1929**. Twelve years is
   much better than thirty-one, but a vat backfilled at the end of the programme would already be
   gone from the surface. Wooden corrals rot; concrete vats were commonly broken up and buried.

So the honest reading is: **the imagery is now good enough that a surviving vat inside Zone A
would probably have been seen, and none was.** That is weak evidence *against* a large surviving
surface facility inside the footprint — and no evidence at all about a demolished or buried one,
which is the more likely state of affairs.

## 6. Testing the premise: were the homes built where the water was?

The proposition — noticed independently from property listings — was that Ladera Ranch and Rancho
Mission Viejo housing sits exactly where the historic water sources and cattle-working areas were.
It matters because cattle concentrate at water, and ranch working facilities were sited where
stock already gathered.

Tested directly (`pipelines/python/premise_homes_on_water.py`): for each 1968 water body, count
modern buildings within 100 m, against a null of random points drawn from the same area.

**Descriptively, the observation holds.**

| Nearest modern building to a 1968 water body | Sites |
|---|---|
| within 100 m | 24 / 41 (59%) |
| within 200 m | 34 / 41 (83%) |
| within 300 m | 40 / 41 (98%) |
| within 500 m | **41 / 41 (100%)** |

Median distance from a ranch-era water body to the nearest house today: **66 m**.

**Causally, the targeting story does not hold.**

| | Buildings within 100 m |
|---|---|
| 1968 water sites in Zone A (n=16) | 9.0 |
| Random points in Zone A (n=6,000) | 9.3 |
| **Enrichment** | **0.97× (p = 0.51)** |

Water sites are **no more built-over than random ground**. The reason both statements are true at
once: development was so near-total that being close to a house stopped carrying information.
Essentially everything in the footprint is close to a house.

**A separate terrain result, and why it cannot be used.** Buildings sit on a median slope of
**1.7°** against **6.7°** for available land. That looks like strong evidence of valley-bottom
siting, but it is **circular** — Ladera Ranch was mass-graded, so the flatness under a house was
manufactured by the grading, not selected for. Recorded here so the figure is not mistaken for a
finding later. Testing original landform would require reconstructing pre-1980 elevations from
the topographic contours.

**What this does and does not change.** It removes "developers built on the cattle-working
grounds" as a *mechanism*. It does **not** reduce exposure potential — arguably the opposite. If
ranch-era ground contamination exists anywhere in this footprint, near-total development means it
now sits under or beside housing **regardless of whether anyone targeted it**. The exposure
concern survives; the targeting explanation does not.

## 7. Correction issued this pass

**C-002 — creek misidentified.** The corridor containing the 1948 ranch structure was described
as **Cañada Chiquita**. The 1937 aerial carries the county cartographer's own label: it is
**Trabuco Creek**. Cañada Chiquita lies further east. Corrected in the map layer label and logged
in `research/CORRECTIONS.md`. The structure's coordinates are unaffected.

## 8. What would actually locate a dip site

In descending order of likely success:

1. **Rancho Mission Viejo's own ranch records.** The O'Neill/Moiso operation kept accounts, and
   dipping was a mandated activity that generated paperwork. **This is now the top-ranked lead** —
   the imagery avenue is close to exhausted.
2. **County Agricultural Commissioner / State Veterinarian tick-eradication archives.** Florida's
   vats are named in state meeting minutes; California's equivalents may name locations.
3. **Targeted geophysics** (GPR / EM) over the ranch-activity node and the water bodies, which
   detects buried concrete and disturbed fill directly.
4. **Soil sampling** at those nodes for total *and* bioavailable arsenic, plus lead.

## 9. What is plotted on the map, and what is not

**Plotted:** the 1929, 1937–38 and 1948 rasters as toggleable georeferenced overlays with an
opacity control; the 41 surface-water bodies from the 1968 survey, sized by area; the single 1948
ranch structure at 33.55505, −117.65492, labelled a ranch-activity node and explicitly *not* a
dip vat; school sites where DTSC found arsenic.

**Not plotted:** any point represented as a cattle dip vat — **none was found**; the 24 rejected
topo-detector candidates from the previous pass; the ~100 shadow artifacts returned by the aerial
water detector in `pipelines/python/detect_water_1930s.py`, which was **abandoned** in favour of
the 1968 ink extraction after visual review showed it was keying on hillslope shadow.

Marking a speculative vat location would manufacture precision the evidence does not support, on
a question that matters to real families. The map shows what the record shows.

## 10. Figures

| File | Contents |
|---|---|
| `11_timeseries_1929-2022_with_water.jpg` | **Four-panel 1929 / 1937–38 / 1946–47 / 2022**, identical extent, Zone A and all 41 water bodies overprinted |
| `oc_aerials/ann_1929.jpg`, `ann_1937.jpg`, `ann_2022.jpg` | Full-resolution annotated frames |
| `oc_aerials/z1_ranch_*.jpg` | The Trabuco ranch node across four epochs at 100 m scale |
| `oc_aerials/tiles/` | 24 systematic survey tiles (4×3 grid × 1929 and 1937) covering Zone A |
| `00_`–`10_` | Topographic-sheet figures from the previous pass |
