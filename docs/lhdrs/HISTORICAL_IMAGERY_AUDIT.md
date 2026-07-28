# Historical imagery audit

## Inventory result

The official County catalog query returned **25 imagery items** whose footprints intersect the current Ladera Ranch CDP. Only two are development-era candidates: **Antonio Parkway 1995** (`Date_On_Map=1994`, `DateCurrent=1995`) and **O'Neil Regional Park (June) 1998** (`Date_On_Map=1997`, `DateCurrent=1998`). Both are archived as PNG32 exports with alpha transparency.

The measured nontransparent footprint covers **49.44%** of the current CDP for the 1994/1995 frame and **51.69%** for the 1997/1998 frame. These percentages describe pixel availability, not visual interpretability.

## Interpretation decision

Both frames were reviewed with current CDP and tract overlays. The 1994/1995 strip is useful as pre-development context. The 1997/1998 frame shows broad undeveloped terrain in its covered area. Neither has an adjacent-date public image adequate for defensibly separating active disturbance from completed work or ordinary ranch roads. No construction polygon was digitized. The empty construction-observation layer explicitly means **unsupported**, not **no construction**.

## Annual completeness

`imagery_coverage_matrix.csv` contains every year from 1997 through 2010. The single 1997/1998 frame is not duplicated into two annual observations. No County catalog frame intersects Ladera for 1999-2010. USGS confirms that individual historical NAIP download through EarthExplorer requires an account; the public USDA current NAIP service contains no study-period frame at this location. Those access limits remain manual follow-ups.

## Reproducibility

- `research/development_chronology/imagery_inventory.csv`
- `research/development_chronology/imagery_coverage_matrix.csv`
- `research/development_chronology/construction_interpretation_log.csv`
- `data/processed/imagery_footprints/imagery_footprints.geojson`
- `data/gis/ladera_development/construction_observations/status.geojson`
- `research/development_chronology/imagery_source_manifest.csv`
