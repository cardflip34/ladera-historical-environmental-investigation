# CHANGELOG

All notable changes to LEHRP. Dates are ISO-8601. Newest first.

## [1.2.0] — 2026-07-18 — School-arsenic map layer; ancestry argument corrected downward

### Corrected — the ancestry / 63.6% argument was overweighted
Reviewer critique: many US communities have far higher European-descent shares without clusters.
That is correct, and it breaks the argument as previously framed. Now bounded three ways:
- **Magnitude is modest** — the adjustment moves expected 0.383 -> 0.510, SIR 15.7 -> 11.8. A
  **~25% correction against an apparent ~1,000% excess.**
- **63.6% is unremarkable** — the US averages **57.8%** non-Hispanic white; thousands of communities
  run 80-95%. If ancestry produced clusters they would concentrate there. They do not.
- **Baselines do not cluster** — a uniform elevation cannot concentrate cases in one subdivision.
  Ancestry explains the *level* of expected risk, never *why here*.
Its role is now stated narrowly: a denominator correction and a comparison-matching criterion.
The genuinely load-bearing fact — **Ewing sarcoma has no established environmental cause anywhere** —
is promoted in its place.

### Changed — probability allocation rebalanced
Removing a support from the chance branch: **55% -> 48%**; real-but-unattributable 20% -> 22%;
abandoned wells 8% -> 9%; legacy soil 7% -> 9%; herbicides 5% -> 6%; unknown 5% -> 6%.

### Added — map
- New `school_sites.geojson` layer. Map now marks **school sites where DTSC found arsenic in soil**
  with purple "As" markers (Carl Hankey 1.8 mi, Plant Depot 2.9 mi, San Juan Elementary 3.2 mi),
  and other legacy-residue school sites in grey (Ambuehl, El Toro HS).

### Added — dip-site location search (§9.2)
Searched directly; **could not be resolved from public records**, and that is itself the finding:
- **California has no public cattle dip-vat inventory** (Florida does).
- Vat locations were **generally never recorded** — Florida found 3,000+ named in minutes with no
  directions to any.
- **Cow Camp** is Rancho Mission Viejo's documented cattle-working hub, but sits on the remaining
  ranch toward Ortega Highway, **not** on the Ladera Ranch footprint.
- Historic USGS topo sheets **retrieved** (San Juan Capistrano quad, 1948/1949/1968/1974) but are
  scanned rasters; dip vats were rarely labelled even when present.
- **No speculative points plotted.** The method is documented instead: overlay the 1948-1974 topo
  sheets and 1952-2002 aerials, identify corrals/pens/water points, sample those.

## [1.1.0] — 2026-07-18 — Arsenic historical-use reconstruction (corrects an assumption)

### Added
- `research/soil/arsenic_historical_use.md` — how arsenic would actually have reached this land
  before the 1999-2006 grading. Combined report gains §9.1. Sources 63 -> **68**.

### Corrected
- **The orchard lead-arsenate mechanism is probably wrong for this land.** California citrus was
  managed for red scale with **cyanide tent fumigation and mineral-oil sprays, not arsenicals**.
  The inference "former farmland, therefore lead-arsenate arsenic" has been retired.
- **Two better-fitting mechanisms identified, one compulsory by law:**
  - **Arsenical cattle dips, 1907-1917.** California mandated arsenical dipping under a March 1907
    law ("cattlemen ... were given no choice as to its use"). **Orange County was among the last
    counties under tick quarantine** (still quarantined April 1910; programme ended June 1917) —
    a window sitting entirely inside Jerome O'Neill's management of the Rancho Mission Viejo cattle
    operation (1907-1926), then Southern California's largest. Dip-vat sites elsewhere measure
    **18-715 mg/kg (mean 332)**, one at **1,390 mg/kg**, against ~12 mg/kg regional background.
  - **Sodium arsenite herbicide / soil sterilant, ~1906-1960** — the standard herbicide of commerce
    for the period; soil sterilisation at **400-800 lbs/acre**.

### Changed — sampling design
- Expected spatial pattern is **point-source, not blanket**: hot spots where cattle were worked and
  chemicals mixed; elevated strips on firebreaks/corrals/roadsides; open grazing land near
  background. **A uniform grid survey would dilute a hot spot into the mean and miss it.** Gate G10
  revised: locate historic corrals, water points and vat structures from the 1952-2002 aerial series
  first, then sample those, measuring total *and* bioavailable arsenic plus lead.

### Unchanged
- The disease filter. Arsenic's established cancers remain bladder, lung and skin, in adults, after
  decades. **No established arsenic-Ewing sarcoma association.** Exposure plausibility rose;
  disease-specific plausibility did not.
- **No dip-vat location on the Ladera Ranch footprint has been identified.** Testable hypothesis,
  not a finding.

## [1.0.0] — 2026-07-18 — Combined report; standalone distributable

### Added
- `scripts/build_combined.py` — merges Part I (public evidence) and Part II (hypothetical
  assessment) into one 18-section document with a jump-link table of contents.
- `reports/Ladera-Ranch-Report-STANDALONE.html` — **fully self-contained single file**: inline
  CSS, base64 map, system font stacks, zero external requests. Opens by double-click on any OS
  or from a phone's Files app; safe to email, AirDrop, or drop on any static host.
- `reports/Ladera-Ranch-Combined-Report.html` — body-only variant for Artifact publishing.

### Fixed — mobile
- Body-only HTML cannot declare a viewport meta, so phones fell back to a ~980px layout and
  shrank the text. The artifact variant now injects one at runtime; the standalone variant has
  a real one in `<head>`. Verified at a true 375px viewport.
- Tap targets raised from 23px to **40px**; table of contents collapses by column width rather
  than a breakpoint; all 20 data tables scroll inside their own containers so the page body
  never scrolls sideways.
- Contrast verified: 6.74:1 light, 7.50:1 dark — both clear WCAG AA.

## [0.8.1] — 2026-07-18 — Hypothetical assessment, formal edition

### Changed
- Rebuilt `scripts/build_hypothetical.py` in the LEHRP editorial system (navy/blue palette,
  serif body, blue tabular section numbers, stat cards, semantic callouts). 7 pp -> **11 pp**,
  15 data tables.
- Now carries the full quantitative record: ACS demographics and person-years; seven reference
  incidence rates incl. the ancestry IRR; the six-scenario SIR grid with exact Poisson intervals;
  the three-way case-count discrepancy with source grades; corrected environmental-site and
  oil/gas-well distance tables; the PUR location-precision table and the twelve-ingredient
  landscape-maintenance mix; the birth-cohort overlap series; seven arsenic benchmarks; an
  eight-study literature table with effect estimates and CIs; and four cluster-investigation
  precedents.
- Added a scoring matrix rendering each hypothesis against all five criteria.

## [0.8.0] — 2026-07-18 — Hypothetical causal assessment (analytical exercise)

### Added
- `scripts/build_hypothetical.py` + `reports/LEHRP_Hypothetical_Causal_Assessment.pdf` (7 pp).
  A forced-conclusion hypothesis-ranking exercise answering "if you had to name one most probable
  explanation, what would it be." Explicitly NOT a finding, NOT an agency determination, and it
  names no party as a cause.
- Scores each hypothesis on exposure opportunity, disease specificity, temporal fit, dose
  plausibility, and **base-rate fit** (how often this class of explanation has proved correct).
- Elicited subjective probability allocation summing to 100%:
  chance/ascertainment 55% · real-but-unattributable 20% · abandoned wells 8% · legacy soil 7% ·
  landscape herbicides 5% · unknown mechanism 5%.

### Conclusion reached
- Most probable: **no single environmental cause** — chance aggregation in a population with an
  elevated ancestry-specific baseline, amplified by media/attorney ascertainment and a boundary
  drawn around the observed cases.
- If a real excess is granted, the most probable environmental contributor is **abandoned oil & gas
  well proximity** — the only candidate with a Ewing-specific published association (weak,
  non-significant).
- The dominant public hypothesis, **landscape herbicides, ranks last** among environmental
  candidates: fails disease specificity, dose plausibility and temporal fit, and state data show the
  practice is regionally ordinary.
- Stated falsification: registry confirmation of counts/residency would move more probability than
  everything else combined (chance branch 55% -> plausibly <30%).

## [0.7.0] — 2026-07-18 — Arsenic exposure audit; screening model gains a disease-fit term

### Added
- `research/soil/arsenic_exposure_assessment.md` — full audit of arsenic persistence, residential
  exposure pathways, bioavailability, produce uptake, and comparison to landscape herbicides.
- `research/soil/regulatory_asymmetry.md` — why every legacy-pesticide soil record near Ladera
  Ranch is a *school* site: CA Education Code mandates Phase I + DTSC review for school
  acquisition; **no equivalent mandate applies to residential subdivisions.** The absence of data
  on the residential footprint is a regulatory artifact, not evidence of clean soil.
- Report §8 (PDF now 14 pp). Sources 50 -> **63**.

### Changed — screening model
- `Factors` gains **`diseaseSpecificPlausibility`**. Everything else scores exposure *opportunity*;
  nothing asked whether a hazard plausibly causes *Ewing sarcoma*. Both rankings are now shown.
  Glufosinate falls from #2 to #5; abandoned oil/gas wells rise to #1 as the only candidate with a
  disease-matched published signal.

### Changed — arsenic hypothesis REVISED DOWN to low-prior
Six independent lines, all newly sourced:
- **Background swamps the screening levels.** SoCal background arsenic (DTSC, n=1,086 school-site
  samples) mean **1.51 mg/kg**, upper bound **12 mg/kg**; risk-based SLs are 0.11-0.68 mg/kg.
  Exceeding a screening level in Orange County is normal.
- **Bioavailability ~0.31** measured at Barber Orchard (former lead-arsenate site), not 1.0 —
  total soil arsenic overstates dose ~3x. EPA median across >100 soils is 30%, not the 60% default.
- **Crop mismatch:** lead arsenate was an *apple/pear* insecticide; this was citrus/barley/cattle
  land. Any arsenical here more plausibly came from sodium-arsenite *herbicide* use.
- **Mass grading (1999-2006)** likely diluted the historic plough layer.
- **Null biomarker evidence:** at Middleport NY, soil As 19.9 mg/kg showed no significant
  correlation with children's urinary arsenic (r=0.137, p=0.39); rice was the predictor.
- **Systematic review** finds the childhood-cancer literature does not support an arsenic link.

### Corrected
- Backyard produce pathway was **understated** in first draft — soil-to-plant transfer is *more*
  efficient for As than Pb (lettuce > carrot > bean > tomato); leafy greens can exceed standards.
- A blanket "no sarcoma link" was **overstated** — arsenic is named for soft-tissue sarcoma at
  occupational doses, though not for Ewing sarcoma or primary bone cancer.
- "Arsenic soil half-life 6.5-16 yr" framing debunked: those figures describe loss of the applied
  compound from the surface layer, not destruction. ATSDR: remains "indefinitely."

### Note
Two of three commissioned research agents died on API errors; load-bearing claims were verified
directly rather than accepted on an unreviewed draft. That verification changed two statements.

## [0.6.0] — 2026-07-18 — Exposure-timing analysis (birth-cohort logic)

### Added
- `pipelines/python/exposure_timing.py` + `research/land_use/exposure_timing_analysis.md`
  + `research/land_use/exposure_timing_matrix.csv`.
- Report §5.1 "Does the timing actually work?" (PDF now 12 pp).

### Changed — hypothesis split
- The "toxic soil" hypothesis was being conflated. It is now split into two mechanisms with
  **opposite birth-cohort predictions**:
  - **M1 construction-era dust (1999-2006)** — a time-bound event; requires the child to have
    been present (incl. in utero). Share of plausible pediatric ages whose birth cohort
    overlaps grading falls from **93% (dx 2013) to 7% (dx 2026)**. Substantially weakened for
    recent diagnoses; unavailable for children born after ~2007.
  - **M2 persistent soil residue** — a standing condition. Arsenic is an element and never
    degrades; organochlorines persist for decades (demonstrated locally by DTSC findings at
    former-farm school sites ~3 mi away). **Unaffected by the timing objection.**
- Exposure screening re-scoped: SCR-02 is now the standing-condition residue (rank 1); new
  SCR-06 isolates the time-limited grading event (rank 3, temporal weight cut to 0.25).
- The one datable Ewing case (dx Aug 2024, age ~17 => born ~Aug 2006-Aug 2007) is a
  **boundary case** and cannot discriminate between M1 and M2.
- **Gate G01 amended** to request *birth year* explicitly — the single field that would
  discriminate between the two mechanisms.

## [0.5.0] — 2026-07-18 — PDF report, map figure & centroid correction

### Added
- `scripts/build_report.py` — regenerates the preliminary report as HTML + PDF (headless
  Chrome), reading live registries. Output: `reports/LEHRP_Preliminary_Report.pdf` (11 pp).
- `apps/web/public/print-map.html` — reproducible full-bleed map figure generator.
- `reports/assets/map_figure.png` — study zones + EnviroStor sites + CalGEM wells over basemap.
- `research/CORRECTIONS.md` — open correction log.

### Fixed — material data correction (C-001)
- **Study centroid was ~1.93 miles too far north.** An inherited value (33.5747, -117.6353)
  placed the study zone outside the community; corrected to the CDP centroid
  (33.5467, -117.6403). Caught by rendering the map figure.
- All environmental-site and oil/gas-well distances recomputed by haversine.
  **Two plugged/abandoned wells are within ~1 mile of the centroid (0.25 / 0.77 mi)**, not
  ~2-2.7 mi — placing the community inside the exposure contrast of the 2026 abandoned-well /
  Ewing sarcoma study. Former-agricultural sites with DDT/toxaphene/arsenic are ~3 mi, not ~5.
- PLSS re-queried at the corrected point: still T7S R7W, section 00 — finding stands.
- Report styling hardened against forced dark mode (low-contrast rendering in mobile WebViews).

## [0.4.0] — 2026-07-18 — PUR empirical analysis & CUSD primary source

### Added
- `pipelines/python/process_pur.py` — downloads/processes DPR PUR annual archives.
- Processed **pur2023.zip** (248 MB, A1): **79,473 Orange County records**, 382 chemicals,
  45 site types → `research/pesticides/pur_orange_county_2023{,_sites}.csv` and
  `research/pesticides/pur_analysis.md`.
- Retrieved **Capistrano USD IPM Plan** (A2, primary) → `research/schools/cusd_ipm_findings.md`.
- Sources 45 → **50** (adds PUR 2023, BLM PLSS service, CUSD IPM Plan/notices, CCR methodology).

### Changed — material correction
- **Corrected the PUR coverage assumption.** Landscape maintenance *is* reported (15,383
  records) but **99.9% carries no township/range/section**; overall **94.6%** of Orange County
  records are unlocated. With Ladera Ranch in unsectioned PLSS land (T7S R7W/R8W, section=00),
  **PUR cannot place an application inside the community.** This elevates gates G04/G05.
- Glufosinate independently confirmed as a major regional landscape herbicide — corroborating
  ordinary regional practice, not causation.
- `data_coverage.md`, `preliminary_findings.md`, `evidence_gate_package.md`, the Pesticides and
  Sites pages, and `PROJECT_STATE.md` updated accordingly.

### Fixed
- Documented that `npm run build` must not run while `npm run dev` is live (shared `.next`).

## [0.3.0] — 2026-07-18 — Phases 1–13 first pass (public-source)

### Added
- **Research registries** (all source-graded): 45 sources; 5 aggregate health events; 22
  literature entries + evidence matrix + reviews; 18 active ingredients; 4 products; 4
  application records; 13 environmental sites; 6 oil/gas wells; 25 water-quality records; 7
  land-use periods; 8 inventoried sites; 3 demographic snapshots.
- **GIS**: dependency-free `build_geojson.py`; 5 GeoJSON layers (approx zones + real
  EnviroStor/CalGEM coordinates).
- **Web app** (`apps/web`): Next.js 14 App Router, 21 routes, MapLibre map, confidence/grade
  badges, source citations, data tables, and a live file-based data layer reading the
  research CSVs. Builds and runs.
- **Analysis**: `notebooks/incidence_scenario_analysis.py` (exact Poisson CI, SIR scenarios,
  leave-one-out); in-app hypothetical SIR grid; configurable exposure-screening framework.
- **Tests**: `tests/test_data_integrity.py` — 7/7 pass (provenance, privacy, grading,
  language discipline, geometry).
- **Reports**: `reports/preliminary_findings.md` (12 questions); `reports/evidence_gate_package.md`
  (ranked gates + 5 drafted records requests).
- `Makefile`, `pipelines/python/requirements.txt`.

### Key finding (descriptive, not a conclusion)
- Ewing sarcoma is ancestry-driven; this predominantly non-Hispanic-white community has an
  elevated baseline expectation. No agency has declared a cluster or cause; the strongest
  testable environmental lead is legacy agricultural soil residue, never tested on the
  footprint. The reported pattern warrants investigation; the evidence does not establish
  causation.

## [0.1.0] — 2026-07-18 — Phase 0: Bootstrap & governance

### Added
- Repository structure (apps/packages/research/data/pipelines/notebooks/reports/tests).
- Project constitution `CLAUDE.md`.
- Governance docs: SOURCE_POLICY, ETHICS_AND_PRIVACY, CLAIMS_AND_LIMITATIONS,
  RESEARCH_PROTOCOL, METHODOLOGY, DATA_DICTIONARY, FUTURE_EVIDENCE_GATES.
- Prisma schema (`packages/database/schema.prisma`) with 10 core models.
- `.gitignore`, `.env.example`, `docker-compose.yml` (PostGIS), `README.md`.
- Initial parallel public-source research launched (official statements, literature,
  pesticide-data systems, land use/environmental sites, water/demographics).
