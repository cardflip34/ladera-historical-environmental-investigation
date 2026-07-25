# GIS SCHEMA (Workstream 11) — spatial/temporal integration

**Privacy first:** exact case residences are **PHI** (folder 04, gitignored). Public/general layers use
**aggregation, jittering, or areal masking** (e.g., counts per ≥ block-group, or distance-to-source
bands) — never point locations. Analytic (private) layers may hold exact points under access control +
chain of custody only.

## Coordinate/analysis standard
CRS EPSG:2230 (CA State Plane VI, ftUS) for local work; store WGS84 too. Document positional accuracy
and source per feature (provenance rule).

## Layers (each: geometry, source_id, grade, date/coverage, accuracy, privacy_class)
### A. Health (PRIVATE — 04 only)
- Case residence(s) by exposure window (prenatal/early-life/at-dx); school/daycare attendance;
  diagnosis year; verified dx + EWSR1 status. **Public derivative = masked aggregate only.**
### B. Historical exposure geography
- Documented 1908 Joplin dip (Trabuco/Bell Canyon); probable dip grounds; corrals/chutes; livestock
  routes; historic ranch structures; drainages; historic roads (from the historical investigation).
### C. Development / earth-movement (exposure redistribution)
- Grading & cut-and-fill plans; development phases (1999–2006); imported/exported soil; utility
  corridors; foundation excavation; dust-generating construction footprints/timeline.
### D. Environmental measurements
- Soil-sampling points + results (**total & bioaccessible As, lead, speciation**, 0–6 in horizon);
  background/natural-arsenic geology; groundwater & surface water; wind climatology (dust pathway).
### E. Receptor/land-use
- Schools, daycares, parks, playgrounds, common areas, greenbelts, recycled-irrigation zones.
### F. Confounders/co-sources
- Former orchards (lead-arsenate signature), agricultural chemical use, oil & gas, other point sources.

## Core spatial questions (analysis, not proof)
1. Distance from masked case aggregates to documented/probable dip grounds vs matched controls.
2. Overlap of child-contact receptors (D/E) with historical exposure geography (B) and earth-movement (C).
3. Where soil sampling (D) should target — feeds 14_proposed_experiments & the epi denominators.

## Outputs
- **Public:** masked/aggregated maps only, each carrying the LEHRP-style neutrality caveat
  ("geographic overlap ≠ exposure ≠ causation").
- **Analytic (private):** exact-location layers, access-controlled.

## Sources
Historical-investigation geospatial layers (repo `research/…`, `data/geospatial/`); Census/ACS
boundaries; CA DTSC/EnviroStor; USGS geology; grading/PEIR records (per archive list).
