# Terrain and drainage context

## Scope and result

This Mission 4 layer describes terrain and mapped drainage context; it does not reconstruct a pre-development ground surface or model transport. The County's 2018 DEM was exported at approximately five-meter horizontal spacing and sampled only inside the current Census-designated-place boundary.

The community sample contains **512,712 cells**. Elevation ranges from **64.6 to 237.8 m**, with a median of **148.3 m** and total sampled relief of **173.2 m**. Median slope is **4.24 degrees** and the 90th percentile is **23.49 degrees**. These are descriptive 2018 morphology statistics.

All **123 recorded-tract polygons** receive a terrain summary in `tract_terrain_summary.csv`. Recording geometry remains a legal-map geography; the terrain calculation does not imply that each polygon was physically developed on its recording date.

## Vertical-unit decision

The 2018 ImageServer metadata identifies a State Plane U.S.-foot coordinate system and a countywide band range of -21.087816 to 5688.329102, but its band-value unit element is blank. A companion County DEM item explicitly describes elevation in U.S. feet. The pipeline therefore records `inferred_us_survey_foot`, applies **1200/3937 m per U.S. survey foot**, and assigns medium confidence to converted elevations and slopes. The raw GeoTIFF and all service metadata are preserved so this interpretation is auditable.

## Drainage context

The current CDP intersects the County's **San Juan Creek** watershed polygon. Inside the boundary, the archived 2016 LiDAR-derived stream layer contributes **6 clipped reaches** totaling **2.97 km**. The flood-control layer contributes **40 clipped facilities** totaling **6.09 km**.

Flood-channel attributes contain drawing-year values **1999;2001** and as-built-year values **none**. Blank as-built values remain blank. Drawing years are document leads only and are not promoted to construction-completion, habitability, or occupancy milestones.

## Boundaries on interpretation

- The 2018 terrain surface postdates the 1997-2010 study window and may reflect grading.
- Stream centerlines derive from 2016 LiDAR and 2015 imagery; they do not establish historical flow persistence.
- Watershed and drainage geometry does not establish parcel-scale direction, discharge, exposure, or movement between sites.
- Aspect is the local downslope bearing from the DEM; `flat` means slope below two degrees.
- Overlapping cardinal-facing percentages intentionally group adjacent eight-way aspect sectors and therefore do not sum to 100 percent.

## Outputs

- `research/development_chronology/terrain_summary.csv`
- `research/development_chronology/tract_terrain_summary.csv`
- `research/development_chronology/drainage_context.csv`
- `data/development/tract_terrain.geojson`
- `data/development/drainage_features.geojson`
- `data/development/watersheds.geojson`
- `research/development_chronology/terrain_source_manifest.csv`
