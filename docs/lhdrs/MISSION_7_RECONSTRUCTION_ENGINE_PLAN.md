# Mission 7 — Historical Reconstruction Engine: implementation plan

**Prepared:** 2026-07-27 · **Status:** PLAN ONLY, no code written · **Scope:** physical reconstruction
of Ladera Ranch, approx. 1997 to build-out (~2006).

**Explicitly out of scope** (per mission constraints, and enforced in the data model below): no
contamination layers, no dust plume animation, no arsenic movement, no exposure inference, no health
outcome or cancer correlation. This engine reconstructs *what physically existed, where, and when*.
Nothing else.

---

## 0. Reality check — read this before anything else

The mission assumes imagery exists to reconstruct 1997 to 2006. **It does not, not in this
repository, and not currently in hand.** From `imagery_coverage_matrix.csv`:

| Year | Coverage of current CDP | Status |
|---|---|---|
| 1997 | 51.69% | one frame, **date ambiguous 1997/1998**, construction polygons `not_supported` |
| 1998 | 51.69% | same single ambiguous frame |
| **1999** | **0.00%** | not located |
| **2000** | **0.00%** | not located |
| **2001** | **0.00%** | not located |
| **2002** | **0.00%** | not located |
| **2003** | **0.00%** | not located |
| **2004** | **0.00%** | not located |
| 2005 | 100.00% | NAIP 2005-06-07, full coverage |
| 2006 | 0.00% | not located |

**The entire mass-grading and peak-construction window, 1999 through 2004, is blank.** That is
precisely the period the reconstruction is about. The County catalog is already marked
`County_catalog_exhausted_for_intersecting_development_era_frames` — the easy source is spent.

Two further gaps of the same kind:

- **No Assessor Year Built data exists anywhere in this repository.** Phase 4 (parcel-by-parcel
  fade-in) has no input dataset today.
- **Road chronology has 2 rows.** Phase 6 road-network evolution is effectively unstarted.

### What this means for sequencing

If the engine is built first, it will render **two real states (an ambiguous 1997/98, and 2005)
across a ten-year slider** and fill the other eight years with interpolation. A polished time slider
that smoothly "rebuilds the community" over blank years would be **the single most misleading artifact
this project could produce** — it would look authoritative, be screenshot and shared, and be
indefensible under exactly the technical and public scrutiny the mission says it must withstand.

**Therefore this plan inverts the mission's order: acquisition is the critical path, not software.**
The engine is designed now (so acquisition has a target schema), built as a thin vertical slice
against real held data, and only scaled once frames exist. The slider must render *gaps as gaps*.

---

## 1. What already exists — do not rebuild

Missions 4 to 6 already produced a substantial share of Phases 1, 5, 6, and 8:

| Asset | Rows / scale | Covers mission phase |
|---|---|---|
| `tract_lifecycle_reconstruction.csv` | 123 tracts | 4, 8 |
| Canonical tract appendix (Mission 6) | 123 + 1 conflicted | 4 |
| `neighborhood_chronology_mission5.csv` | 130 | 5 |
| `builder_product_chronology.csv` | 69 products | 4, 5 |
| `address_neighborhood_tract_points.csv` | 6,446 points | 4 |
| Mission 6 address crosswalk (deduped) | 6,368 | 4 |
| `school_timeline.csv` | 15 | 6 |
| `annual_snapshots.csv` / geojson | 12 | 8, 9 |
| `knowledge_graph.json` | 1,229 nodes / 1,614 edges | 8, 9 |
| Street/tract crosswalk (Mission 6) | 288 road features, 78 sources | 6 |
| Terrain, drainage, watersheds, wind | multiple layers | context |
| Historical land-use chapters (LEHRP) | Rancho era → dip era → ranch | 1 |

**Mission 7 is an integration and visualization layer over this, plus a targeted acquisition
program.** Phase 1 (historical base layer) is largely written already in the LEHRP California report
and needs porting, not researching.

---

## 2. Architecture

```
                     ACQUISITION (critical path, mostly human/paid)
   USGS EarthExplorer · NAIP · Landsat · commercial vendors · EIR/planning exhibits
   County records requests (M6-REQ-*) · Assessor · CUSD · Public Works
                                    |
                                    v
   ┌────────────────────────────────────────────────────────────────────┐
   │  L0  IMMUTABLE SOURCE STORE                                        │
   │  original files, unmodified · sha256 · retrieval date · licence     │
   │  never edited, never overwritten                                    │
   └────────────────────────────────────────────────────────────────────┘
                                    |
   ┌────────────────────────────────────────────────────────────────────┐
   │  L1  NORMALIZED EVIDENCE                                            │
   │  georeferenced rasters (EPSG:26946) · parsed permits · parcels      │
   │  each record: sourceId, statementClass, provenanceGrade, confidence │
   └────────────────────────────────────────────────────────────────────┘
                                    |
   ┌────────────────────────────────────────────────────────────────────┐
   │  L2  INTERPRETATION  (clearly separated, never merged into L1)      │
   │  CV detections: rooftop, grading extent, vegetation loss, roads     │
   │  every output tagged interpreted|inferred + model + version         │
   └────────────────────────────────────────────────────────────────────┘
                                    |
   ┌────────────────────────────────────────────────────────────────────┐
   │  L3  RECONSTRUCTION STATE  (the queryable core)                     │
   │  state_at(t, geometry) -> objects with validity intervals           │
   │  returns KNOWN / UNKNOWN explicitly. Never interpolates silently.   │
   └────────────────────────────────────────────────────────────────────┘
                        |                         |
   ┌────────────────────────────┐   ┌────────────────────────────────────┐
   │ L4a  VIEWER                │   │ L4b  RENDER / VIDEO                │
   │ time slider, click-through │   │ deterministic frame export         │
   │ confidence chips, sources  │   │ 30s/60s/90s/5m/10m, flythrough     │
   └────────────────────────────┘   └────────────────────────────────────┘
```

**Hard rule between L1 and L2:** interpretation never writes back into evidence. A CV rooftop
polygon is not a building record. This separation is what makes the output defensible.

### Stack

Consistent with the existing repo (Next.js + MapLibre + Python/GeoPandas + file-based data, PostGIS
optional):

- **Raster:** GDAL/rasterio for georeferencing, COG tiling; PMTiles for web delivery.
- **Vector:** GeoPandas/Shapely; GeoJSON now, PostGIS when volume demands it.
- **Viewer:** existing Next.js app + MapLibre GL; deck.gl only if parcel counts demand GPU.
- **CV:** segmentation for grading extent / vegetation loss; rooftop detection only on imagery
  ≥0.6 m GSD. Below that resolution, rooftop detection is not attempted (see risk R4).
- **Video:** headless deterministic frame capture from the same L3 state, so every video frame is
  reproducible from data rather than hand-animated.

---

## 3. Data model

Every reconstructable object:

```
id                    stable, prefixed (LH-PARCEL-*, LH-ROAD-*, LH-SCHOOL-*)
geometry              GeoJSON, EPSG:26946 analysis / 4326 delivery
geometryPrecision     surveyed | official_polygon | digitized | approximate | unknown
validFrom / validTo   interval, each with:
  ├ value             date or null
  ├ bound             exact | earliest | latest | window
  └ basis             the milestone type, see below
milestoneType         map_recordation | grading_permit | building_permit | final_inspection
                      | certificate_of_occupancy | road_acceptance | first_sale | observed_in_imagery
statementClass        documented | interpreted | inferred | absent
provenanceGrade       A+ | A | B | C | D | F   (section 4)
confidence            high | medium | low
sourceIds[]           → L0 immutable store
limitations           free text, always populated
versionHistory[]      append-only; supersession recorded, never deleted
```

**Milestone separation is mandatory.** Mission 5/6 established the rule and it carries forward:
map recordation, road acceptance, year-built, first sale, and imagery observation are **each distinct
milestones and none of them is a certificate of occupancy.** The model stores them separately and the
viewer labels which one it is showing. A parcel may legitimately have a documented building permit and
an unknown occupancy date; that is a valid, displayable state.

### The "fade into existence" requirement, handled honestly

The mission asks each structure to fade in "only after documented completion." For most parcels we
will not have a documented completion date — at best a permit final, at worst a year-built integer.
So:

- Documented completion (CO or final inspection): structure appears **crisp** on that date.
- Known window only (e.g. permit issued 2002-03, first sale 2003-06): structure renders as a
  **hatched/translucent "under construction or unknown" state across the window**, resolving to solid
  at the later bound.
- Year Built only: renders as a **year-wide uncertainty band**, explicitly labelled "Assessor year
  built, not an occupancy record."
- Nothing known: parcel stays **grey/unknown**. It does not appear, and it does not disappear either
  — it is drawn as unknown.

This satisfies the intent (chronological build-out) without asserting precision we do not have.

---

## 4. Confidence methodology

The mission proposes A+/A/B/C/D/F. The repo already uses A1/A2/B1/B2/C/D (LEHRP source grading) and
`statementClass` + `confidence` (LHDRS). **Rather than introduce a fourth scheme, Mission 7 treats
these as two orthogonal axes**, because "where it came from" and "how we know it" are different
questions and conflating them is how reconstructions go wrong.

**Axis 1 — provenance grade (mission scheme, mapped to existing LEHRP grades):**

| Grade | Definition | LEHRP equivalent |
|---|---|---|
| A+ | Government machine-readable dataset / official GIS service | A1 |
| A | Official public record, agency document, recorded map | A2 |
| B | Historic publication, university or institutional report | B1 |
| C | Developer / builder documentation, marketing collateral | C |
| D | Media source | B2 or C depending on sourcing |
| F | Unknown or unverifiable | D |

**Axis 2 — statement class (how the claim was derived):**

| Class | Meaning | May it drive a rendered date? |
|---|---|---|
| `documented` | stated explicitly in the source | yes |
| `interpreted` | read by a human from imagery/plans | yes, flagged, never crisp |
| `inferred` | derived by model or CV, or bounded between two knowns | yes, flagged, band only |
| `absent` | searched, not found | no — renders as UNKNOWN |

**Both axes render.** A rooftop detected by CV on a government orthophoto is `A+ / inferred` — high
provenance, low epistemic standing. Showing only the A+ would be misleading. The viewer displays both
chips, and `inferred`/`interpreted` objects are visually distinct (hatched, reduced opacity) at all
times, including in exported video.

**`absent` is a first-class value.** A searched-and-not-found result is recorded with its search
scope and date, never silently converted to a negative or an empty map.

---

## 5. Source inventory

### Held now
| Source | Coverage | Grade | Note |
|---|---|---|---|
| County aerial 1997/98 | 51.69% | A+ | date ambiguous, polygons not supported |
| NAIP 2005-06-07 | 100% | A+ | best held frame of the era |
| NAIP 2009, 2010 | 100% | A+ | post-build-out |
| 1929/1937/1946 aerials | varies | A+ | pre-development baseline (Phase 1) |
| OC tract maps | 123 tracts | A+ | recorded polygons + dates |
| OC road index (live + 2024) | 288 features | A+ | acceptance dates |
| LARMAC street directory | 484 | C | 2019 naming, not historical |
| Builder product directories | 69 | C/D | secondary, needs primary confirmation |

### Must acquire — ranked by value against the 1999-2004 blackout
| # | Source | Target | Grade | Cost | Realistic yield |
|---|---|---|---|---|---|
| 1 | **USGS EarthExplorer** (DOQQ, NAPP/NHAP, single frames) | 1999-2004 | A+ | free | **highest-value free option; not yet exhausted** |
| 2 | **Commercial historical aerial vendors** (I.K. Curtis, HJW/Pacific Aerial, AirPhotoUSA, EagleView) | 1999-2004 | A/C | **paid, $$** | the realistic way to actually fill the blackout |
| 3 | **OC Assessor** — Year Built, APN, sq ft | all parcels | A+ | free/low | unblocks Phase 4 entirely; **currently absent** |
| 4 | **OC permits/CO index** (M6-REQ-OC-PERMIT-01, drafted) | 1997-2011 | A+ | free | the only true occupancy source |
| 5 | **EIR / planning / grading exhibits** | 1997-2004 | A/C | free | dated aerial exhibits inside documents; underused |
| 6 | Google Earth Pro historical | varies | D | free | fast to check, weak provenance, licence limits |
| 7 | Landsat 5/7 | continuous, 16-day | A+ | free | 30 m — **too coarse for parcels**; usable only for gross disturbance extent |
| 8 | CUSD records (M6-REQ) | school construction | A+ | free | Phase 6 |
| 9 | OC Public Works / SMWD | road + utility acceptance | A+ | free | Phase 6 |

**Honest expectation on cadence:** the mission asks for monthly, then quarterly, then annual. For
suburban Orange County 1999-2004, **monthly public aerial coverage does not exist**. Landsat is the
only true high-cadence source and its 30 m resolution cannot see a rooftop. After a full and
successful acquisition program the realistic outcome is **roughly 6 to 12 usable frames across the
decade** — annual at best, with gaps. The engine must be built for that, not for monthly.

---

## 6. Risk assessment

| # | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| R1 | **Engine built over blank years, renders convincing fiction** | high if built first | **critical — project credibility** | Acquisition-first sequencing; gaps render as explicit UNKNOWN; no tweening between distant frames; ship the gap report alongside any video |
| R2 | 1999-2004 imagery unobtainable even after paid acquisition | medium | high | Fall back to non-imagery milestones (permits, tract acceptance, sales); state coverage honestly; a documented blackout is a finding |
| R3 | Assessor Year Built mistaken for occupancy | high (it is the intuitive error) | high | Model forbids it: separate `milestoneType`, mandatory label, uncertainty band rendering |
| R4 | CV detections treated as documented fact | medium | high | L1/L2 separation; `inferred` class; rooftop detection blocked below 0.6 m GSD; every detection carries model + version |
| R5 | Georeferencing error moves structures between parcels | medium | high | Publish RMSE per frame; refuse parcel-level attribution above an error threshold; ground-control from surveyed tract corners |
| R6 | Commercial imagery licence forbids publication | medium | medium | Check licence **before** purchase; keep licence text in L0; render restricted frames internally only |
| R7 | Scope drift into exposure/contamination modelling | medium | **critical — violates constraints and project ethics** | Schema has no contamination entity; adding one requires an explicit gate (section 8) |
| R8 | Three diverged repo clones cause split-brain data | **high — already true today** | medium | Resolve before Mission 7 code (section 7, step 0) |
| R9 | Video artifact circulates without caveats | medium | high | Confidence chips and coverage bar burned into exported frames, not overlaid in post |
| R10 | Parcel-level rendering re-identifies households | low | high | Aggregate/mask per existing ETHICS_AND_PRIVACY.md; parcels are public record but occupancy timing is not personal data and must stay non-personal |

---

## 7. Phased execution roadmap

**Step 0 — repo consolidation (blocking, ~1 session).** Three clones exist (`~/Ladera-Ranch`,
`~/ladera-historical-environmental-investigation`, `~/Documents/Ladera Ranch`) plus 125 uncommitted
files here. Pick one canonical, reconcile, then start. Building Mission 7 across a split brain will
produce contradictory reconstructions.

**Phase A — acquisition sprint (dominates the schedule; mostly not code)**
A1. Exhaust USGS EarthExplorer for 1999-2004 — free, highest value, not yet done.
A2. Submit M6-REQ-OC-PERMIT-01 (drafted, appendices complete, awaiting authorization).
A3. Acquire Assessor Year Built + APN + parcel geometry.
A4. Quote commercial vendors for 1999-2004; check licences before buying.
A5. Mine EIR/planning/grading documents for dated aerial exhibits.
A6. Record every negative result with search scope and date. **Exit:** a coverage matrix that is
honest, whatever it says.

**Phase B — evidence pipeline (code, small)**
L0 immutable store with hashing; georeferencing harness with published RMSE; L1 schema and loaders;
port the existing 1,229-node graph into the new model. **Exit:** any held frame reproducibly
georeferenced and queryable.

**Phase C — vertical slice**
One neighborhood, the two real frames (1997/98, 2005), plus tract/permit milestones. Prove
`state_at(t)` returns KNOWN/UNKNOWN correctly and the viewer renders gaps as gaps. **Exit:** a slice
a hostile reviewer cannot break. Do not scale before this passes.

**Phase D — interpretation layer (L2)**
Grading-extent and vegetation-loss segmentation on frames that support it; rooftop detection only
where GSD allows. Every output `inferred`, versioned, separately stored. **Exit:** detections
reproducible from a pinned model version.

**Phase E — full reconstruction**
Scale to all tracts/parcels/roads/schools; build the timeline; wire click-through to sources.

**Phase F — viewer and video**
Time slider with a permanent coverage bar; deterministic frame export; the 30s to 10m cuts.
**Exit:** every exported frame traceable to L3 state, and no frame asserts more than the data.

**Gate before Phase F publication:** a coverage-honesty review — does the artifact visibly
distinguish known from unknown, at every timestamp, without narration?

---

## 8. Future modules (architected for, disabled by default)

Soil testing, air monitoring, hydrology, groundwater, environmental sampling, public health studies.
These attach as **additional evidence layers keyed to the same geometry and time model**, and are
gated: no such layer may be enabled without real measured data, and enabling one does not license
exposure or health inference. The current schema deliberately contains no contamination entity.

---

## 9. Success criteria — feasibility today vs. after acquisition

| Mission question | Answerable now | After Phase A |
|---|---|---|
| "What did this parcel look like in March 2002?" | **No** — zero 2002 imagery | Only if a 2002 frame is acquired; otherwise answer is UNKNOWN with bounds |
| "When was this neighborhood under construction?" | Partially — from tract/builder records | Yes, with documented bounds |
| "When did this school first exist?" | Largely yes — 15-row school timeline | Yes, with CO dates |
| "What roads existed before Chaparral opened?" | Weakly — road chronology has 2 rows | Yes, from acceptance records |
| "What % complete by Sept 2003?" | **No** — would be fabrication | Yes as a bounded estimate, labelled `inferred` |
| "What infrastructure existed at a location on a date?" | Partially | Yes, with UNKNOWN where truly unknown |

**The honest headline:** the engine is buildable and the architecture is sound, but today it would be
a well-built empty vessel for eight of ten years. The work that determines whether this mission
succeeds is **Phase A acquisition**, not software. Recommend authorizing A1 (free, immediate) and A3
(Assessor) first, and treating the commercial imagery quote in A4 as the real go/no-go decision for
the whole reconstruction.
