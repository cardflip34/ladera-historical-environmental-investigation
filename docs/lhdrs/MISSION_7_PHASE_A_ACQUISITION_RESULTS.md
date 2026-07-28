# Mission 7 / Phase A — acquisition results (A1, A3, A4)

**Run:** 2026-07-28 · reproducible via `scripts/lhdrs_m7_imagery_sweep.py` and
`scripts/lhdrs_m7_acquire_parcels.py` · AOI bbox `-117.659017, 33.526791, -117.624136, 33.575504`

Three acquisition tasks were executed back to back. Two produced hard, decision-changing findings.
Negative results are recorded as findings, per project rule.

---

## A1 — Open-catalog imagery sweep · **STATUS: partial success, with a major correction**

Catalogs queried without credentials: USGS TNM Access, Microsoft Planetary Computer STAC (NAIP,
Landsat C2 L2), USGS LandsatLook STAC.

### Correction to the Mission 7 plan
The plan stated the 1999-2004 window was "0.00% covered / not located." That was true **of the
County aerial catalog**. It is **not true of open federal satellite catalogs.** True per-year counts,
AOI-intersecting:

| Year | NAIP | Landsat scenes | Best cloud-free date |
|---|---|---|---|
| 1997 | 0 | 43 | 1997-08-05 (0%) |
| 1998 | 0 | 43 | 1998-01-21 (0%) |
| **1999** | 0 | **54** | 1999-10-31 (0%) |
| **2000** | 0 | **72** | 2000-01-27 (0%) |
| **2001** | 0 | **83** | 2001-05-04 (0%) |
| **2002** | 0 | **79** | 2002-01-24 (0%) |
| **2003** | 0 | **83** | 2003-02-03 (0%) |
| **2004** | 0 | **91** | 2004-01-14 (0%) |
| 2005 | 0 | 86 | 2005-01-15 (0%) |
| 2006 | 0 | 88 | 2006-01-10 (0%) |

**~460 Landsat scenes exist across 1999-2004, free and immediately downloadable, and every single
year has at least one 0% cloud scene.** NAIP returns 0 for all years in this catalog (the held 2005
NAIP came from a different source).

### What this does and does not unlock
Landsat is **30 m** ground sample distance. A Ladera Ranch lot is roughly 20-27 m across, so **one
pixel is about one house lot.**

- **Unlocked (Phase 3, mass grading):** bare soil versus vegetation is a strong, well-established
  spectral signal. Graded-area extent, vegetation removal, and the sequence in which the community's
  footprint was disturbed are **reconstructable at neighborhood scale, at 8-to-16-day cadence, for the
  entire previously-"blank" window.** This is a genuine and substantial upgrade to Phase 3.
- **NOT unlocked (Phase 4, parcels):** rooftops cannot be resolved at 30 m. No parcel-level
  construction state can be derived from Landsat, and none should be attempted. Any such output would
  be `inferred` at best and misleading at worst.

### Still gated
- **USGS EarthExplorer M2M** (NAPP/NHAP single frames, DOQQ) requires a free login and was not
  queried. It remains the **most likely free source of high-resolution 1999-2004 frames** and is the
  top remaining free action.
- Commercial vendors — see A4.

Raw output: `evidence/lhdrs/mission7/imagery_sweep_2026-07-28.json`

---

## A3 — Orange County parcel / Assessor acquisition · **STATUS: geometry acquired, chronology BLOCKED**

Source: `ocgis.com/arcpub/rest/services/Map_Layers/Parcels/FeatureServer/0` (official County service,
grade **A+**). Fields: `OBJECTID, SITE_ADDRESS, ASSESSMENT_NO (APN), YEAR_BUILT, NBR_BEDROOMS`.

**Acquired:** 7,469 parcel polygons in the AOI bbox (authoritative AOI count 7,611); **6,101 parcels
fall inside the actual Ladera Ranch CDP polygon**, each with APN and geometry.
File: `evidence/lhdrs/mission7/oc_parcels_ladera_2026-07-28.geojson` (sha256 recorded in the
accompanying `.provenance.json`).

### The blocking finding
Within the Ladera Ranch CDP, `YEAR_BUILT` is populated for **4 of 6,101 parcels (0.1%)**:

| Value | Count |
|---|---|
| `''` (empty) | 5,925 |
| `'0'` | 112 |
| `null` | 60 |
| `'86'`, `'2'` (malformed) | 3 |
| `'2002'` | 1 |

The populated `YEAR_BUILT` values found in the wider bbox (1975, 1976, 1990, 1984, 1988…) belong to
**surrounding older neighborhoods** caught by the rectangular bbox, not to Ladera Ranch. Ladera was
built 1999-2006; those values are pre-Ladera and are not this community.

**Conclusion: the County's public parcel service does not publish year-built for Ladera Ranch.**
Phase 4 (parcel-by-parcel chronological build-out) **cannot be driven by free public parcel data.**

### What this proves about the critical path
This is empirical confirmation, not opinion: **the drafted records request
`M6-REQ-OC-PERMIT-01` (permit / inspection / certificate-of-occupancy index) is not merely the
preferred route to parcel chronology, it is the only identified viable one.** Its six appendices are
already generated and it awaits only authorization to submit.

Net gain from A3 is still real: we now hold **6,101 APN-tagged parcel polygons** we did not have —
the spatial substrate for Phase 4. Only the dates are missing.

---

## A4 — Commercial historical aerial imagery · **STATUS: RFQ drafted, NOT sent**

An RFQ is drafted at `docs/lhdrs/MISSION_7_RFQ_HISTORICAL_AERIAL_DRAFT.md`.

**It has not been sent, and this engine will not send it.** Contacting outside commercial parties on
the project's behalf is an outward-facing action reserved for the principal, consistent with the
standing project rule that this lane drafts but does not contact. It is ready to send verbatim once
authorized.

---

## Net effect on Mission 7

| Phase | Before Phase A | After Phase A |
|---|---|---|
| 3 — mass grading | blocked, no imagery | **feasible at neighborhood scale**, free Landsat, 8-16 day cadence, 1999-2004 |
| 4 — parcels | blocked, no geometry, no dates | geometry **acquired** (6,101 APN polygons); **dates still blocked**, County permit request is the only path |
| 2 — high-res visual reconstruction | blocked | still blocked; EarthExplorer M2M and paid vendors are the remaining routes |

**Revised recommendation.** The go/no-go framing in the Mission 7 plan should shift. Phase 3 no
longer depends on a commercial imagery purchase, so the sequence is now:

1. **EarthExplorer M2M login sweep** — free, highest remaining value for high-resolution frames.
2. **Authorize `M6-REQ-OC-PERMIT-01`** — now demonstrably the sole path to parcel chronology.
3. **Landsat-based grading reconstruction** — buildable immediately, no acquisition dependency.
4. Commercial imagery quote — now a *quality* upgrade for Phase 2, no longer a blocker for Phase 3.
