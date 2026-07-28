# LHDRS Development Chronology

This directory is the canonical research workspace for the Ladera Ranch Historical
Development Reconstruction System (LHDRS). It is intentionally separate from the
repository's environmental-health workstreams.

LHDRS reconstructs land use, entitlement, subdivision, construction, public-facility,
sales, and occupancy chronology. It describes spatial relationships only. It does not
infer contamination, exposure, health risk, or causation.

## Canonical Tables

| File | Purpose |
|---|---|
| `sources.csv` | Searchable LHDRS source registry with reliability, archive, checksum, and limitation fields. |
| `events.csv` | One record per dated or bounded historical event. |
| `annual_snapshots.csv` | Year-level summary used by the atlas. |
| `planning_areas.csv` | Visually verified 1995/2003 planned land-use and dwelling-unit table. |
| `development_obligations.csv` | Permit and infrastructure triggers kept separate from events. |
| `schools.csv` | School planning, construction, opening, location, and evidence fields. |
| `neighborhoods.csv` | Village milestone matrix; blanks are unresolved, never silently estimated. |
| `imagery_inventory.csv` | Available imagery, coverage, registration, and interpretation status. |
| `knowledge_graph.csv` | Evidence-graph edges linking conclusions back to sources. |
| `proximity_analysis_status.csv` | Machine-readable geometry gate for the requested historical distance analysis. |
| `tract_audit.csv` | Per-feature geometry, validity, overlap, and lifecycle-boundary audit of the County tract layer. |
| `tract_crosswalk.csv` | Pairwise projected-geometry observations; every possible legal-map relationship requires documentary review. |
| `tract_map_document_manifest.csv` | Checksummed archive manifest for the 123 official recorded-map PDFs. |
| `tract_title_sheet_index.csv` | OCR-assisted title-sheet lineage, acreage, lot, and named-party index with raw corrections retained. |
| `wind_source_manifest.csv` | Checksummed NOAA station-history, format, and selected annual Global Hourly files. |
| `wind_station_inventory.csv` | Candidate station distances, periods, selection decisions, and limitations. |
| `wind_annual_summary.csv` | Annual regional station summaries from deduplicated observed hours. |
| `wind_monthly_summary.csv` | Monthly regional station summaries with the same method and caveats. |
| `wind_station_comparison.csv` | Same-year El Toro and John Wayne descriptive comparisons. |
| `geographic_hierarchy.csv` | Community, planning-area, village, and tract nodes with unresolved parents left explicit. |
| `historical_observations.csv` | Source-level observations kept separate from analyst claims and lifecycle intervals. |
| `claim_registry.csv` | Traceable legal-recording and historical-event claims linked to observations. |
| `lifecycle_intervals.csv` | Bounded state intervals; rows lacking dated geometry are explicitly ineligible for proximity. |
| `construction_activity_registry.csv` | Evidence-bounded construction and enabling-work observations with geometry eligibility. |
| `occupancy_event_registry.csv` | Sales, opening, completion, and occupancy observations without invented parcel assignment. |
| `tract_development_matrix.csv` | Legal, physical-development, habitability, and occupancy fields for all 123 audited tracts. |
| `neighborhood_occupancy_matrix.csv` | Nine village/neighborhood records with unresolved dates and geometry preserved as blanks. |
| `school_project_registry.csv` | DSA project milestones kept distinct from physical construction and opening conclusions. |
| `terrain_summary.csv` | Present-day elevation, slope, aspect, watershed, drainage, and temporal-limit context. |
| `blocked_proximity_comparisons.csv` | Comparison classes that failed a named dated-geometry evidence gate. |
| `conflict_registry.csv` | Explicit source or date conflicts requiring review. |
| `research_gaps.csv` | Ranked unresolved questions, required evidence, and recommended acquisition path. |
| `unresolved_questions.csv` | Open questions and the evidence needed to resolve them. |
| `dead_ends.csv` | Bounded negative searches and access failures. |

## Controlled Values

`statementClass`:

- `documented_exact`: the source states an exact date or fact.
- `documented_approximate`: the source supports a bounded or year-level statement.
- `corroborated_secondary`: multiple credible secondary sources agree.
- `visual_interpretation`: an analyst interpreted registered imagery or a map.
- `estimate`: a transparent estimate; method notes are mandatory.
- `unresolved`: no defensible conclusion yet.

`confidence` is `high`, `medium`, `low`, or `unknown`. It evaluates the specific
statement, not the source in the abstract.

`temporalPrecision` is `day`, `month`, `year`, `range`, or `unknown`.

## Spatial Discipline

The County tract-map layer records legal-map recording dates. A recorded map is a
documented subdivision milestone. It does not by itself prove that grading, vertical
construction, road opening, home sale, or occupancy occurred on that date. Atlas labels
and generated data preserve this distinction.

The Census-designated-place boundary is a current statistical boundary, not the 1997
entitlement boundary. It is used as a reproducible query and display extent until the
County planned-community map is digitized.

## Rebuild

From the repository root:

```bash
make lhdrs-mission4-ingest LHDRS_PYTHON=/path/to/python
make lhdrs-mission4 LHDRS_PYTHON=/path/to/python
make lhdrs-mission4-publish LHDRS_PYTHON=/path/to/python
make lhdrs-mission4-docs LHDRS_PYTHON=/path/to/python
make lhdrs-mission4-verify LHDRS_PYTHON=/path/to/python
```

The fetch script performs network access and archives public records. The build script is
deterministic from the archived/canonical inputs and writes `data/development/` plus the
client-facing copies in `apps/web/public/development/`.

Generate the citable Markdown and print-ready HTML publication with:

```bash
python3 scripts/generate_lhdrs_publication.py
```

The command above regenerates the preserved first edition. Mission 4 publishes the second
edition separately through `make lhdrs-mission4-publish`; it does not overwrite the original.
