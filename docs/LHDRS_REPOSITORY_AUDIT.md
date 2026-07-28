# LHDRS Repository Audit

Date: 2026-07-26

Scope: audit of the existing `ladera-historical-environmental-investigation` repository
against `LHDRS_MASTER_PRD.md`, before beginning any new historical-development research.

## Executive Finding

The repository is substantial and reusable, but it is currently organized as LEHRP: an
environmental-health research platform with source grading, an evidence registry, GIS
layers, reports, a Next.js map application, and historical imagery. LHDRS can reuse much of
the provenance and mapping infrastructure, but the repository does not yet contain the
year-by-year physical development chronology required by the PRD.

The immediate next step should be a dedicated LHDRS data model and work area, not more
archival research. That work area should separate historical-development reconstruction
from environmental, exposure, toxicological, and health-risk claims.

## Audit Method

- Attached the local working directory to the GitHub repository and checked out `origin/main`.
- Counted files, extensions, top-level directory sizes, and large assets.
- Read the governing files: `README.md`, `CLAUDE.md`, `PROJECT_STATE.md`,
  `SOURCE_POLICY.md`, `DATA_DICTIONARY.md`, `packages/database/schema.prisma`,
  `research/historical_imagery/README.md`, and the research/evidence logs.
- Performed exact-hash duplicate detection across all non-`.git` files.
- Reviewed existing Ladera-specific development, imagery, school, land-use, GIS, report,
  and publication assets.

## Repository Inventory

### Whole-Repo Snapshot

| Metric | Value |
|---|---:|
| Total non-Git files | 898 |
| Total non-Git bytes | 527,342,580 bytes, about 503 MiB |
| JPG files | 430 |
| Markdown files | 166 |
| JSON files | 53 |
| PDF files | 40 |
| HTML files | 39 |
| Python files | 36 |
| CSV files | 31 |
| PNG files | 26 |
| TS/TSX files | 29 |
| GeoJSON files | 17 |
| TIF files | 7 |

### Top-Level Directories

| Area | Files | Bytes | LHDRS relevance |
|---|---:|---:|---|
| `evidence/` | 84 | 220,383,058 | Primary/archive copies of PDFs, maps, plats, aerials, photographs, and source images. High reuse. |
| `research/` | 237 | 154,309,942 | Research notes, CSV/JSON registries, historical imagery, land-use files, source registry, logs. High reuse. |
| `docs/` | 351 | 105,892,960 | Generated reports, publication chapters, publication assets, web-exported source files. Reusable but mostly generated/secondary. |
| `data/` | 17 | 22,134,955 | Geospatial layers, rasters, and map data. High reuse for base atlas layers. |
| `reports/` | 14 | 15,997,582 | Existing LEHRP HTML/PDF reports. Reusable as background, not as LHDRS canonical output. |
| `media/` | 26 | 4,293,704 | B-roll boards, video script/captions. Low to medium reuse for publication, not data. |
| `apps/` | 50 | 3,288,873 | Next.js app with MapLibre map and multiple data routes. High reuse for atlas UI. |
| `scripts/` | 30 | 396,208 | Report, imagery, GIS, and publication scripts. Medium to high reuse. |
| `pipelines/` | 8 | 38,322 | Python data pipelines. Medium reuse. |
| `packages/` | 1 | 7,044 | Prisma schema. Needs extension for LHDRS. |
| `tests/` | 1 | 7,031 | Integrity tests. Needs LHDRS provenance tests. |

### Existing Assets by PRD Category

| PRD category | Existing assets | Reuse assessment |
|---|---|---|
| HTML reports | `reports/*.html`, `docs/california/*.html`, `docs/publication/index.html`, `index.html` | Reuse only as legacy/background publication output. Do not treat generated HTML as canonical evidence. |
| GIS layers | `data/geospatial/*.geojson`, `apps/web/public/geo/*.geojson`, overlay JSON files | Strong base map reuse. Needs new temporal development layers. |
| PDFs | 40 PDFs across `evidence/`, `reports/`, `docs/`, and `arsenic-cancer-investigation/` | Strong source reuse for planning/environmental context. Needs OCR and source registration checks. |
| Planning documents | `evidence/documents/Ladera_Planned_Community_Program_Text_1995_rev2003.pdf`; references to missing EIR/Brandman materials | Partial. The central entitlement/EIR materials are not yet fully acquired or searchable. |
| Environmental reports | `evidence/documents/EIR589_AppendixI_PhaseI_ESA_PA1-9.pdf`, `OsoGrande_Phase1_2002.pdf`, addenda/DTSC letters | Reuse for chronology and land-use references only. LHDRS must not convert them into exposure claims. |
| Historical maps | USGS GeoTIFFs, Bancroft/CSA disenos, GLO/land-patent materials, 1948/1968 topo-derived layers | Strong pre-development context. Needs 1997-2006 development-era map sources. |
| Historical imagery | `research/historical_imagery/`, `research/ladera/imagery/`, `apps/web/public/geo/*overlay*` | Strong pre-development and modern comparison base. Needs late-1990s and 2000s staged development imagery. |
| Research notes | 166 Markdown files including logs, plans, corrections, land-use summaries, imagery README | Strong reuse, but existing notes emphasize environmental/cattle-dip questions. |
| Databases/registries | `research/source_registry/sources.csv`, `research/_logs/EVIDENCE_MATRIX.csv`, topic CSV/JSON files, Prisma schema | Strong provenance foundation. Needs LHDRS entities. |
| Scripts | `scripts/build_historical_overlay.py`, `scripts/pull_oc_historical_aerial.py`, GIS/report scripts, Python pipelines | Reuse selectively. Add LHDRS build/validation scripts after schema exists. |
| Animations | No clear data animation product found; only `scripts/build_broll_motion.py` and video cue materials | Missing for LHDRS atlas animation/timeline playback. |
| Publication assets | `docs/publication/`, `docs/california/assets/`, `research/plates/`, `media/broll/` | Useful for final publication, but often generated copies of canonical assets. |
| Evidence logs | `research/_logs/RESEARCH_LOG.md`, `DEAD_ENDS.md`, `EVIDENCE_MATRIX.csv`, `research/CORRECTIONS.md` | Excellent reuse. Needs parallel LHDRS development evidence log. |
| Timelines | `research/cancer_reports/timeline.json`, `media/video/BROLL_TIMELINE.md`, publication timeline chapter | Not adequate for LHDRS. Need development chronology, not cancer/reporting timeline. |
| Photographs | `evidence/images/`, `research/*/imagery/`, `docs/*/assets/` | Strong background collection. Needs development-stage photos by year/neighborhood. |
| Videos | `media/video/` scripts/captions; no source video archive detected | Low direct reuse for atlas data. |
| Generated HTML | Extensive under `reports/` and `docs/` | Keep generated status explicit; avoid editing by hand when generated from scripts. |
| Source registry | `research/source_registry/sources.csv` | Strong reuse. Needs LHDRS source-type expansion and checksums for development sources. |
| Interactive maps | `apps/web/app/map/page.tsx`, `apps/web/components/MapView.tsx` | Strong technical base. Missing time slider/snapshot behavior and development layers. |

## What Already Exists

### Governance and Evidence Discipline

The repository already has strong rules for source grading, provenance, confidence display,
privacy, uncertainty, and correction logging. The following should be reused for LHDRS with
minor additions:

- `SOURCE_POLICY.md`
- `research/source_registry/sources.csv`
- `research/_logs/EVIDENCE_MATRIX.csv`
- `research/_logs/RESEARCH_LOG.md`
- `research/_logs/DEAD_ENDS.md`
- `research/CORRECTIONS.md`
- `DATA_DICTIONARY.md`
- `packages/database/schema.prisma`

LHDRS should add statement classifications from the PRD directly into the data model:
`Established Fact`, `Documented Date`, `Estimated Date Range`, `Visual Interpretation`,
`Investigative Lead`, and `Open Question`.

### Existing Ladera Historical/Development Evidence

Useful starting points include:

- `evidence/documents/Ladera_Planned_Community_Program_Text_1995_rev2003.pdf`
- `research/land_use/historical_land_use.csv`
- `research/land_use/historical_land_use.md`
- `research/historical_imagery/README.md`
- `research/historical_imagery/oc_aerials/frames.json`
- `research/ladera/imagery/`
- `research/schools/AREA_SCHOOL_ROSTERS.md`
- `research/schools/sites.csv`
- `docs/publication/chapters/22_grading_and_soil_movement.md`
- `docs/publication/chapters/23_gis_reconstruction.md`

The existing chronology is broad. It records Ladera as entitled around 1997-1999 and built
out around 1999-2006, but it does not identify annual or monthly states of neighborhoods,
roads, grading, infrastructure, parks, commercial facilities, schools, or occupied areas.

### Existing Geospatial Base

Reusable layers include:

- `data/geospatial/zone_a_boundary.geojson`
- `data/geospatial/zone_b_buffer.geojson`
- `data/geospatial/historic_ranch_1948.geojson`
- `data/geospatial/topo1968_water.geojson`
- `data/geospatial/school_sites.geojson`
- `data/geospatial/aerial1929_overlay.json`
- `data/geospatial/aerial1937_overlay.json`
- `data/geospatial/topo1948_footprint.json`
- `apps/web/public/geo/*`

These establish footprint, reference imagery, a ranch activity node, water bodies, and
schools. They do not yet encode development phases or time-varying land states.

### Existing Software

The web app already has:

- Next.js 14 with App Router
- React/TypeScript
- MapLibre
- file-based data loading
- route pages for maps, land use, environmental sites, schools/sites, water, sources,
  status, and other LEHRP topics

This is a good foundation for a historical atlas, but the current UI is not a
date-addressable reconstruction system. There is no "March 2002" snapshot query, time slider,
state playback, temporal feature panel, or source-by-feature evidence drawer.

## Gap Analysis

### Product and Scope Gaps

| Requirement | Current state | Gap |
|---|---|---|
| Work inside existing repo | Satisfied | No gap. |
| No new research before audit | Satisfied by this document | Future work should cite this audit as the start point. |
| Historical reconstruction, not environmental investigation | Partially conflicted | Current repo identity and many reports are environmental-health oriented. LHDRS needs a clearly separated workstream and language discipline. |
| Year-by-year reconstruction from about 1997 through buildout | Not present | Only broad `1997-1999` and `1999-2006` rows exist. |
| Evidence-backed confidence for every conclusion | Foundation exists | Need LHDRS-specific records with source IDs, confidence, temporal precision, geometry precision, and statement class. |
| Searchable historical atlas | Not present | Current map is static/current-layer oriented. |

### Data Gaps by PRD Research Question

| Research question | Existing coverage | Missing |
|---|---|---|
| What remained ranchland each year? | Pre-development imagery and broad land-use rows | Annual polygons for 1997-final buildout. |
| Where was grading occurring? | Narrative chapter and broad 1999-2006 statement | Grading permit records, staged grading polygons, dates, contractors, confidence. |
| Where were roads under construction? | No dedicated dataset | Road opening/completion chronology, acceptance dates, construction-stage geometry. |
| Where were utilities being installed? | Water-system context only | Utility trenching/as-built chronology, reclaimed water/potable/stormwater infrastructure phases. |
| Where were homes under construction? | No dedicated dataset | Tract-level construction dates, parcel/building permit data, aerial interpretation by year. |
| Where were people living? | Broad buildout statement | Occupancy/opening dates by village, tract, or neighborhood; certificate-of-occupancy proxies. |
| Which schools were operating? | School roster with opening years for several schools | Machine-readable school operation table with date precision and source links. |
| Which schools were under construction? | Not present | School construction windows and phase status. |
| Which parks were open? | Park/site inventory only | Park opening dates, development status, boundaries, and source evidence. |
| Which community facilities existed? | Some LARMAC/common-area references | Facility inventory with dates and locations. |
| Which commercial facilities existed? | Not present | Mercantile/Town Green/retail opening chronology and tenant/source evidence. |
| Which roads were complete? | Not present | Road completion/opening/acceptance timeline. |
| What construction remained active nearby? | No dedicated dataset | Active construction layer by date, including adjacent Rancho Mission Viejo/Ranch Plan context where relevant. |
| What evidence supports each conclusion? | General source registry exists | DevelopmentFeature-to-Source many-to-many evidence table is missing. |

### Source and Document Gaps

High-priority missing or incomplete sources for LHDRS:

- Ladera Ranch entitlement EIR / EIR 555 and appendices.
- Michael Brandman Associates May 1995 hazardous-materials assessment cited by existing
  notes.
- OCR/text extraction for `Ladera_Planned_Community_Program_Text_1995_rev2003.pdf`, which
  is scanned and not currently searchable.
- Orange County tract maps, final maps, parcel maps, subdivision maps, and grading permits.
- Building permit or certificate-of-occupancy proxies by tract/neighborhood.
- Road acceptance, improvement plans, and capital project records.
- Utility as-builts or public improvement plans where legally available.
- LARMAC/Rancho Mission Viejo village, park, clubhouse, and community facility opening
  materials.
- CUSD board agendas, school construction records, and official opening dates.
- Historical aerials or orthophotos for 1997, 1999, 2000, 2001, 2002, 2003, 2004, 2005,
  2006, and final buildout.
- Contemporary newspaper and developer marketing materials only as secondary corroboration,
  with source-grade discipline.

### Schema Gaps

The Prisma schema currently supports LEHRP entities such as `Source`, `Site`,
`EnvironmentalSite`, `WaterSystem`, and `ApplicationEvent`. It does not support core LHDRS
entities such as:

- `DevelopmentSource`
- `DevelopmentPhase`
- `DevelopmentFeature`
- `DevelopmentEvent`
- `TemporalSnapshot`
- `Neighborhood`
- `RoadSegment`
- `SchoolOperationPeriod`
- `ParkOperationPeriod`
- `ConstructionStatus`
- `EvidenceLink`

At minimum, each LHDRS feature needs:

- stable ID
- feature type
- geometry
- date or date range
- temporal precision
- development status
- statement classification
- confidence
- source IDs
- interpretation method
- known limitations
- conflict notes
- created/updated metadata

### Testing Gaps

Existing tests check LEHRP integrity, provenance, privacy, grading, and geometry. LHDRS needs
new tests that fail when:

- a development feature lacks a source ID
- a feature lacks temporal precision
- a feature lacks confidence
- an inferred/visual-interpretation feature lacks method notes
- a feature has geometry but no geometry precision
- a date range has invalid ordering
- generated public layers drift from canonical research data

## Duplicate Asset Report

Exact duplicate scan found 22 hash-identical groups, totaling about 1.5 MB of duplicate
bytes. No files were removed during this audit.

Most duplicates are intentional publication or web-app copies of canonical assets. The
problem is not storage size; the problem is unclear authority. Future work should mark which
copy is canonical and which copies are generated or distributable artifacts.

| Group | Duplicate files | Assessment |
|---|---|---|
| 1 | `research/oc_dipping_records/proclamation_1912_johnson.pdf`; `evidence/documents/CA-Gov-Proclamation-1912-03-07-cattle-quarantine-PARTIAL-Orange-County-Johnson_CSL_4775-4777.pdf` | Canonical archival copy should live under `evidence/`; research copy should be documented or generated. |
| 2 | `research/statewide/CA_dipping_counties_vs_development.jpg`; `docs/publication/statewide_assets/CA_dipping_map.jpg` | Likely publication copy. Keep canonical in `research/` and generated copy in `docs/`. |
| 3 | `docs/publication/statewide_assets/view/T14-TEJON_52_LOC-2010645756.jpg`; `docs/publication/statewide_assets/view/T15-MILLERLUX_59_LOC-KernCounty-ranches-1888-britton-rey.jpg` | Suspicious: different logical IDs with identical bytes. Needs review before reuse. |
| 4 | `reports/Ladera-Ranch-Preliminary-Report.html`; `reports/lehrp_report_web.html` | Generated report duplicate. Keep one canonical output name or document alias. |
| 5 | `research/statewide/IMAGE_INDEX.md`; `docs/california/files/research_statewide_IMAGE_INDEX.md` | Generated publication copy. |
| 6 | `docs/publication/statewide_assets/thumbs/T14-TEJON_52_LOC-2010645756.jpg`; `docs/publication/statewide_assets/thumbs/T15-MILLERLUX_59_LOC-KernCounty-ranches-1888-britton-rey.jpg` | Suspicious companion to group 3. Needs review. |
| 7 | `research/source_registry/sources.csv`; `docs/california/files/research_source_registry_sources.csv` | Generated publication copy of source registry. Canonical should remain `research/source_registry/sources.csv`. |
| 8 | `data/geospatial/topo1968_water.geojson`; `apps/web/public/geo/topo1968_water.geojson` | Expected app-public copy. Needs generation rule. |
| 9 | `research/schools/AREA_SCHOOL_ROSTERS.md`; `docs/california/files/research_schools_AREA_SCHOOL_ROSTERS.md` | Generated publication copy. |
| 10 | `research/land_use/Ladera_Arsenic_Trioxide_Testing_HowWeKnow.pdf`; `docs/california/files/research_land_use_Ladera_Arsenic_Trioxide_Testing_HowWeKnow.pdf` | Generated publication copy. |
| 11 | `data/geospatial/environmental_sites.geojson`; `apps/web/public/geo/environmental_sites.geojson` | Expected app-public copy. Needs generation rule. |
| 12 | `research/land_use/ARSENIC_FULLTEXT_SEARCH_2026-07-26.md`; `docs/california/files/research_land_use_ARSENIC_FULLTEXT_SEARCH_2026-07-26.md` | Generated publication copy. |
| 13 | `research/statewide/DIPPING_PROBABILITY_RATIONALE.md`; `docs/california/files/research_statewide_DIPPING_PROBABILITY_RATIONALE.md` | Generated publication copy. |
| 14 | `data/geospatial/zone_b_buffer.geojson`; `apps/web/public/geo/zone_b_buffer.geojson` | Expected app-public copy. Needs generation rule. |
| 15 | `research/archives/RECORDS_REQUESTS_2026-07.md`; `docs/california/files/research_archives_RECORDS_REQUESTS_2026-07.md` | Generated publication copy. |
| 16 | `data/geospatial/oil_gas_wells.geojson`; `apps/web/public/geo/oil_gas_wells.geojson` | Expected app-public copy. Needs generation rule. |
| 17 | `data/geospatial/school_sites.geojson`; `apps/web/public/geo/school_sites.geojson` | Expected app-public copy. Needs generation rule. |
| 18 | `data/geospatial/zone_a_boundary.geojson`; `apps/web/public/geo/zone_a_boundary.geojson` | Expected app-public copy. Needs generation rule. |
| 19 | `data/geospatial/historic_ranch_1948.geojson`; `apps/web/public/geo/historic_ranch_1948.geojson` | Expected app-public copy. Needs generation rule. |
| 20 | `data/geospatial/aerial1937_overlay.json`; `apps/web/public/geo/aerial1937_overlay.json` | Expected app-public copy. Needs generation rule. |
| 21 | `data/geospatial/aerial1929_overlay.json`; `apps/web/public/geo/aerial1929_overlay.json` | Expected app-public copy. Needs generation rule. |
| 22 | `data/geospatial/reference_points.geojson`; `apps/web/public/geo/reference_points.geojson` | Expected app-public copy. Needs generation rule. |

## What Can Be Reused

- Source registry and grading policy.
- Correction, dead-end, and research-log conventions.
- MapLibre/Next.js app shell.
- Zone boundary and reference geospatial layers.
- Historical imagery acquisition notes and OC imagery service knowledge.
- Ladera Planned Community PDF as a planning source, after OCR.
- School roster as a seed for school-operation chronology.
- Existing land-use CSV as a broad seed, not as final LHDRS chronology.
- Existing publication scripts and assets for later output generation.

## What Requires Updating

- Project navigation and README should distinguish LEHRP from LHDRS workstreams.
- Data dictionary and Prisma schema need LHDRS entities.
- Source registry needs development-specific source types and consistent local file paths.
- Public web map needs temporal controls and feature-level evidence panels.
- Generated app-public GeoJSON copies need an explicit build command and test.
- Existing Ladera land-use chronology needs replacement or extension from broad periods to
  year-by-year states.
- Scanned PDFs need OCR and checksum/provenance metadata before being relied on for
  negative findings.

## What Is Missing

- Canonical LHDRS research folder.
- Canonical LHDRS schema.
- Development-feature registry.
- Year-by-year 1997-final buildout snapshot table.
- Monthly/date-specific query model.
- Development-era aerial/orthophoto inventory.
- Grading phase polygons.
- Residential construction polygons or tract statuses.
- Occupancy/opening chronology by neighborhood/village.
- Road completion and construction chronology.
- Utility installation chronology.
- School construction and operating-period table.
- Park/community-facility/commercial opening table.
- Remaining-ranchland polygons by year.
- Confidence taxonomy wired into code and tests.
- Atlas UI for "what did Ladera Ranch look like on date X?"

## Improvement Recommendations

1. Create a dedicated LHDRS namespace:
   - `research/development_chronology/`
   - `data/development/`
   - `apps/web/app/atlas/`
   - `apps/web/public/development/`

2. Add a first-pass LHDRS data dictionary before research resumes:
   - `development_sources.csv`
   - `development_features.csv`
   - `development_events.csv`
   - `development_snapshots.csv`
   - `evidence_links.csv`

3. Extend the source and confidence model:
   - add PRD statement classes
   - add temporal precision
   - add geometry precision
   - add visual-interpretation method
   - add conflict/counter-evidence notes

4. OCR and register planning documents:
   - OCR the Ladera Planned Community Program Text
   - locate/register EIR 555 and appendices
   - locate/register Brandman 1995 Appendix H
   - add checksums and text-search status to source records

5. Build the development-era imagery inventory before interpreting imagery:
   - list every available frame from 1997 through final buildout
   - record coverage, resolution, source URL/service, raster ID, export parameters, and
     georeferencing notes
   - do not digitize features until the imagery inventory is stable

6. Define canonical-vs-generated asset policy:
   - canonical research data in `research/` or `data/`
   - app-distribution copies generated into `apps/web/public/`
   - publication copies generated into `docs/`
   - tests to detect drift between canonical and generated copies

7. Implement LHDRS tests before adding large datasets:
   - source required
   - confidence required
   - temporal precision required
   - geometry precision required
   - generated-copy drift detection

8. Build the atlas in stages:
   - Stage 1: static year snapshots
   - Stage 2: map time slider and layer toggles
   - Stage 3: feature evidence drawer
   - Stage 4: date query such as "March 2002"
   - Stage 5: uncertainty/conflict visualization

9. Keep language boundaries explicit:
   - LHDRS documents what existed, when, where, and with what evidence
   - LHDRS does not infer contamination, exposure, health effects, or causation
   - environmental documents can be sources for land-use/construction facts only when the
     cited passage supports those facts

10. Do not begin new external research until the LHDRS schema and canonical folders exist.
    Otherwise the project will accumulate more evidence without a stable way to represent
    uncertainty, time, and spatial state.

## Recommended Next Commit Scope

The next implementation commit should be small and structural:

- add `research/development_chronology/README.md`
- add draft CSV schemas under `research/development_chronology/schema/`
- add a development-source registry seeded only with sources already present in the repo
- add tests that enforce `source_id`, `confidence`, `statement_classification`,
  `temporal_precision`, and `geometry_precision`

After that, begin the first evidence-backed chronology pass for 1997-2006.
