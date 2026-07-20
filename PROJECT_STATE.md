# PROJECT_STATE.md

**Last updated:** 2026-07-18 · **Version:** 0.3.0

## Current phase

**Phases 0–13 first pass complete** (public-source). The platform now builds, runs, and
passes its integrity tests. Remaining work genuinely depends on final-stage evidence gates
(registry data, records requests, sampling) — see `reports/evidence_gate_package.md`.

## Completed

- **Phase 0 — Bootstrap & governance** ✅ Constitution + 7 governance docs + Prisma schema.
- **Phase 1 — Public fact base** ✅ 45 graded sources; 5 aggregate health events; case-count
  discrepancy documented.
- **Phase 2 — Literature** ✅ 22 entries; evidence matrix; narrative + methodology reviews.
- **Phase 3 — GIS foundation** ✅ 5 GeoJSON layers (zones + real EnviroStor/CalGEM points).
- **Phase 4 — Pesticide data + chemicals** ✅ 18 active ingredients; PUR coverage analysis;
  glufosinate deep-dive; documented "Lifeline" application recovered as a primary source.
- **Phase 5 — Site inventory** ✅ 8 sites (parks/schools/common areas) with vendor/maintenance.
- **Phase 6 — Land use + environmental sites** ✅ 7 land-use periods; 13 environmental sites;
  6 oil/gas wells; legacy-soil-residue hypothesis.
- **Phase 7 — Water** ✅ 2 systems; 25 water-quality records; recycled-water assessment.
- **Phase 8 — Demographics + incidence** ✅ Census/ACS; SEER baselines; SIR scenario notebook.
- **Phase 9 — Exposure screening** ✅ Configurable non-causal screening framework.
- **Phase 10 — Dashboard** ✅ Next.js app, 21 routes, MapLibre map, all pages wired to data.
- **Phase 11 — Tests** ✅ 7/7 integrity tests pass (provenance, privacy, grading, geometry).
- **Phase 12 — Preliminary findings** ✅ `reports/preliminary_findings.md` (12 questions).
- **Phase 13 — Evidence-gate package** ✅ `reports/evidence_gate_package.md` (ranked + 5 draft
  records requests).

## Record counts

Sources **50** · Health events 5 · Literature 22 · Chemicals 18 (+ **382** from PUR) ·
Products 4 · Application records 4 · Environmental sites 13 · Oil/gas wells 6 ·
Water-quality 25 · Land-use periods 7 · Site inventory 9 · GIS layers 5 ·
**PUR Orange County 2023 records analyzed: 79,473**.

## Phase 4b — PUR empirical analysis (added 2026-07-18)

Downloaded and processed DPR's 2023 PUR archive (248 MB, grade A1). This **corrected an
earlier working assumption** and produced the platform's most consequential coverage finding:

- **94.6%** of Orange County pesticide records carry **no location** at all.
- **Landscape maintenance: 15,383 records, only 22 (0.1%) geolocated.** Only agricultural/
  nursery categories are reliably located (~100%).
- BLM PLSS places Ladera Ranch in **T7S R7W / T7S R8W** with **no section number** —
  consistent with former land-grant land never subdivided into PLSS sections (inference;
  verify against DPR PLSSNET).
- **⇒ PUR is structurally incapable of placing an application inside Ladera Ranch.** The
  posted LARMAC/O'Connell notices are the only public location-specific evidence, which
  **raises the priority of gates G04/G05** (also high destruction risk).
- PUR **independently confirms glufosinate** as a major regional landscape herbicide (442
  records, 10,531.9 lbs; 336 records in landscape maintenance) — ordinary regional practice,
  not evidence of causation. Glyphosate is larger (~30,052 lbs across landscape).

Also closed: **Capistrano USD IPM Plan retrieved** (A2, primary). Covers structural *and*
landscape pests; names no products or contractor; the separate Annual Pesticide Notification
and Product List is publicly linked but requires sign-in (not retrievable — access controls
respected). Converts a vague gap into a specific CPRA request.

## Key findings (descriptive, not conclusions)

1. Official multi-agency review underway; no agency has declared a cluster or a cause.
2. Every pesticide-specific causal claim is advocacy/attorney-sourced (grade C); glufosinate
   is not classified a carcinogen by any regulator (EU non-renewal was on reprotoxicity).
3. Ewing sarcoma is ancestry-driven (~9× higher in European ancestry) → this
   63.6%-non-Hispanic-white community has an elevated baseline expectation.
4. Strongest testable environmental lead: **legacy agricultural soil residue** on former
   farmland — confirmed at neighboring sites, never tested on the footprint.
5. Drinking water low-plausibility (imported, no MCL violations); recycled water under-
   characterized.
6. Hypothetical SIR scenarios: reported count exceeds expectation, but rest on unverified
   counts and boundary/ascertainment bias — **warrants investigation, not conclusion.**

## Key limitations

No verified case data; no individual exposure data; PUR under-captures urban landscape use;
population denominators are estimates; small-number statistics; ancestry structure confounds
baseline expectation. See `CLAIMS_AND_LIMITATIONS.md`.

## Exact commands to resume

```bash
# Web app (file-based; no DB required)
cd apps/web && npm install && npm run dev

# Regenerate GIS layers after editing research CSVs
python3 pipelines/python/build_geojson.py

# Analyze a DPR PUR annual archive (download from files.cdpr.ca.gov/pub/outgoing/pur_archives/)
python3 pipelines/python/process_pur.py /path/to/pur2023.zip

# NOTE: never run `npm run build` while `npm run dev` is live — they share apps/web/.next
# and the production build clobbers the dev server's chunks. Stop dev, or rm -rf apps/web/.next.

# Run integrity tests
python3 tests/test_data_integrity.py

# Run the incidence scenario analysis
python3 notebooks/incidence_scenario_analysis.py

# Optional PostGIS
docker compose up -d
```

## Next executable steps (require evidence gates)

1. File the 5 drafted records requests (`reports/evidence_gate_package.md`) via authorized
   channels; preserve high-destruction-risk logs (G04/G05).
2. On receipt of registry data (G01), recompute SIR with verified counts + ancestry-specific
   rates and run SaTScan/BYM2 as appropriate.
3. Pursue soil sampling (G10) for arsenic/DDT/toxaphene on former-ag footprint.
4. Obtain DPR PUR extract for 92694 sections and normalize into ApplicationEvent.
5. Watch for the OCHCA/UCI/CCR review results and any EPA response.

## Concise warning

Do **not** draw causal conclusions prematurely. Geographic and temporal overlap does not
establish exposure or causation; the reported pattern warrants investigation, and the
available evidence does not yet establish causation.
