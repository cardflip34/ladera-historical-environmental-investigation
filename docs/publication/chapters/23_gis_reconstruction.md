# GIS Reconstruction

## 23.1 What was built

A georeferenced reconstruction of the study area combining historical imagery, historical
cartography, modern terrain, and modern built form — all registered to a single common extent
so that any layer can be compared with any other without further transformation.

**Common extent (WGS84):** longitude −117.680 to −117.616, latitude 33.520 to 33.575.
Approximately 5.9 km east–west by 6.1 km north–south.

| Layer | Type | Epoch | Source | Grade |
|---|---|---|---|---|
| 1929 aerial | Raster | 1929 | OC Survey Historic_Imagery_v2, OID 346 | A1 |
| 1931 aerial | Raster | 1931 | OC Survey, OID 351 | A1 |
| 1937–38 aerial | Raster | 1937–38 | OC Survey, OID 310 | A1 |
| 1938 aerial | Raster | 1938 | OC Survey, OID 340 | A1 |
| 1946–47 aerial | Raster | 1946–47 | OC Survey, OID 286 / 293 | A1 |
| 1948 topographic sheet | Raster | 1948 | USGS 7.5′ San Juan Capistrano | A1 |
| 1968 topographic sheet | Raster | 1968 | USGS 7.5′ San Juan Capistrano, revised | A1 |
| 1974 orthophoto quad | Raster | 1974 | USGS | A1 |
| 2022 aerial | Raster | 2022 | OC Survey OC_Aerial_2022_1ft_WGS84 | A1 |
| Surface water 1968 | Point (41) | 1968 | Digitised from USGS hydrography ink | A2 |
| Ranch structure 1948 | Point (1) | 1948 | Digitised from USGS sheet | A2 |
| Environmental sites | Point | Current | DTSC EnviroStor | A1 |
| School sites, arsenic flagged | Point (5) | Current | DTSC EnviroStor | A1 |
| Oil & gas wells | Point (6) | Current | CalGEM WellSTAR | A1 |
| Terrain (DEM) | Raster | Current | USGS 3DEP, 4.2 × 5.0 m/px | A1 |
| Building footprints | Point (10,618) | Current | OpenStreetMap via Overpass | B2 |
| Zone A / Zone B | Polygon | — | Generated screening boundaries | Model estimate |

::: classification limit
**Zone A and Zone B are approximate screening aids, not legal boundaries.** Zone A is a
bounding box of about 5 square miles centred on the Ladera Ranch CDP centroid, against a
published CDP area of 4.945 square miles. It is fit for spatial screening and is not a
cadastral or jurisdictional boundary. It should never be used as one.
:::

## 23.2 Georeferencing confidence, layer by layer

Different layers carry genuinely different positional confidence, and treating them as
equivalent would be a mistake.

| Layer group | Method | Confidence | Residual |
|---|---|---|---|
| OC Survey aerials | Rectified server-side by the county; export extent echoed and checked | High (relative), Moderate (absolute) | ~±25 m from export snap, plus unpublished county rectification error |
| USGS topographic sheets | `pyproj` transform from GeoTIFF tags, validated against the quad neatline | High | Sub-pixel against the graticule |
| Digitised water bodies | Colour threshold on the georeferenced 1968 sheet | Moderate | Inherits sheet error plus centroid approximation |
| EnviroStor / CalGEM points | Agency-published coordinates | High | As published by the agency |
| OSM buildings | Community-mapped centroids | Moderate | Completeness not guaranteed uniform |

**The independent check on the whole raster stack:** the modern 2022 frame was exported through
the identical pipeline to the identical extent. Zone A lands on the real subdivisions;
Interstate 5 and Mission Viejo fall where they belong. A systematic registration error would
have displaced the modern frame too. It did not.

## 23.3 The correction that reshaped every distance

::: classification correction
**Correction C-001 — the study centroid was approximately 1.93 miles too far north.**

The project inherited a working centroid of 33.5747, −117.6353. The authoritative Ladera Ranch
CDP centroid is **33.5467, −117.6403**.

*How it was caught:* rendering the map. The Zone A polygon sat visibly *north* of the
OpenStreetMap "Ladera Ranch" place label — a contradiction that a table of coordinates would
never have surfaced. This is the single strongest argument in this project for rendering
spatial data rather than trusting it.

*Magnitude:* 1.93 miles north–south, 0.29 miles east–west.
:::

Every distance-to-community figure in the project was recomputed. The consequences were not
cosmetic:

| Site | Was (mi) | Now (mi) |
|---|---|---|
| Citizens National Trust B-1 (plugged well) | 2.0 | **0.25** |
| O'Neill #1 (plugged well) | 2.7 | **0.77** |
| Blue Diamond Materials Plant | 3.1 | **1.3** |
| Plant Depot School Site (arsenic, nitrate) | 4.8 | **2.9** |
| Ambuehl Elementary (DDT, toxaphene) | 5.0 | **3.0** |
| San Juan Elementary (arsenic, chlordane, DDT) | 5.1 | **3.2** |

**Two plugged wells turned out to lie within about a mile of the community centroid**, one
effectively within the footprint — rather than the two to three miles previously recorded. The
former-agricultural school sites carrying legacy residues are roughly three miles away, not
five.

That correction is what placed this community inside the exposure contrast of the published
Ewing sarcoma / abandoned-well study discussed in the alternative-pathways chapter. It came
from fixing an error, not from looking for a result.

**What the correction did not affect:** demographics and person-years (CDP-based), the
incidence scenarios and Poisson intervals, the pesticide-reporting analysis, and the PLSS
finding — re-queried at the corrected point, the community still sits on unsectioned
land-grant land.

## 23.4 The terrain analysis, and why its headline result is unusable

A drainage network was derived from the 3DEP DEM by D8 flow accumulation over a pit-filled
surface, and building placement was compared against available terrain.

**The measured result:** buildings sit at a median slope of **1.7°** against **6.7°** for
available land across the same extent — roughly four times flatter than the landscape average.

**Why it cannot be used:** Ladera Ranch was mass-graded. The pads were cut flat. The measurement
describes engineered surfaces, not siting decisions relative to natural landform. It is
circular with respect to the very activity under investigation.

::: classification limit
**EM-008 · Methodological exclusion.** This figure is recorded rather than omitted precisely
because it is persuasive and will be rediscovered. Anyone who recomputes it should meet this
note. Recovering the original landform requires reconstructing pre-1980 elevations from the
1948 and 1968 topographic contours — which is tractable, and is listed as recommended work.
:::

A second-order caution from the same analysis: the derived channel network proved sparse
relative to the visible drainage pattern (median distance to a channel of ~914 m across an area
with drainages every few hundred metres), indicating the accumulation threshold was too
conservative. The valley-bottom enrichment figure computed from it (1.15×) is therefore **not
reported as a finding** anywhere in this publication. The water-proximity analysis in the water
chapter, which does not depend on the derived network, is unaffected.

## 23.5 The interactive map

The project's web map presents these layers with the three historical rasters selectable and an
opacity control for blending against a modern basemap. Water bodies are scaled by mapped
surface area. Every point carries its source grade and provenance in its popup.

A note on its construction, because it is a genuine robustness lesson: the data layers were
originally attached to MapLibre's `load` event. That event waits on sprites, glyphs, and the
first tile batch — so a stalled font or sprite fetch on a slow connection would leave **every
research layer silently invisible over a perfectly functional basemap**. A reader would see a
map, notice nothing wrong, and draw conclusions from an empty overlay. Layers now attach to
`styledata`, which fires as soon as the style is parsed.

::: classification limit
**No patient locations, residential addresses, or case locations appear on any map layer**, by
permanent policy. Where a dataset would permit finer resolution than the project's privacy rules
allow, the rules take precedence.
:::

## 23.6 The GIS package

All layers are published as GeoJSON in WGS84, with the derived rasters and their corner
coordinates, so the analysis can be reproduced or contradicted independently. Every feature
carries a `source_id` linking to the source registry; features with no traceable source are not
published.

The most useful product is not any single layer but the **sampling frame**: 41 water bodies plus
one structure, in a single file, representing the places where the historical activity of
interest would have concentrated if it occurred at all.
