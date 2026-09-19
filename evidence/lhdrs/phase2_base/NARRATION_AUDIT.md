# Phase 2 FULL narration: claim-by-claim audit (2026-09-17)

Every factual claim spoken in the narration, its source, and its grade. Two claims in the earlier
Phase 2 narration failed this audit and were corrected before the full cut was built:

| Earlier line | Problem | Corrected to |
|---|---|---|
| "The federal circular ... documents a herd of more than twenty-five thousand head" | 25,000 is the O'Neill family's undated figure (B2). The circular (A1) reports ~21,000 head on one large ranch in 1910 | "reports a single ranch of about twenty-one thousand head still under quarantine in 1910. The family's own history puts the herd at more than twenty-five thousand." |
| "more than half the community was bare, moving earth" | Landsat bare/disturbed peak was 41.3 % (2002) | "more than four in ten acres of the community were bare" |

| Block | Claim | Source | Grade |
|---|---|---|---|
| OPEN | Compulsory dipping in quarantined CA counties 1907 to March 1912 | USDA BAI Circular 174 (1911); OC release proclamation | A1 |
| OPEN | Ladera Ranch and ProtectLadera acting to keep the community safe since Phase 1 | Speaker's statement (Andy Stavros); stakeholder contact | Public statement |
| THREAT | Concrete rectangle with iron pipe rails; floor 12 ft | Field observation 2026-08-07/08 (FIELD_OBSERVATION_v5.pdf) | Verified field observation (identification NOT established) |
| THREAT | Federal vat floor = 12 ft | BAI Circular 183/207 plans | A1 |
| THREAT | Unfenced, unmarked, on public open space beside a trail | Field photos 2026-09 | Verified field observation |
| THREAT / 1b | 3 to 7 vats required for a herd of ~25,000 | ARSENIC_QUANTIFICATION_MASTER.md (cadence model) | Model-based estimate |
| FL | Florida inventoried >3,000 vats; 3,281 listed | FDEP county inventory (G11 response) | A2 |
| FL | 11 of 12 tested sites exceeded soil arsenic standard | Woodward-Clyde / FDEP CDV Assessment Program report | A2 |
| FL | Reuse as pesticide-mixing areas and swimming holes for children | Same FDEP report | A2 |
| FL | California never inventoried its vats | STATE_REGISTRY_CROSSREFERENCE.md (absence in EnviroStor/GeoTracker; no program) | Inference from absence (documented search) |
| 1 | Vat 26 ft rim, 6.5 ft deep, ~2,000 gal; 8 lb As2O3 per 500 gal; 14-day cadence | BAI Circulars 174/183/207 | A1 |
| 1 | "The outline we found matches the floor of this vat" | Field measurement vs spec | Inference; not an established identification (said on screen) |
| 2 | OC "heavily infested"; ~21,000 head on one ranch 1910 | Circular 174 | A1 |
| 2 | >25,000 head | Family history (Irish America) | B2 |
| 2 | 6,692 to 39,748 lb total; 1,338 to 7,949 lb at a vat; hundreds of times background (1 to 11 mg/kg) | ARSENIC_QUANTIFICATION_MASTER.md | Model-based estimate |
| 2 | Lethal dose a fraction of a gram | Toxicology reference (ATSDR) | A1 |
| 3 | Grading 1997 to 2007; 41.3 % bare at 2002 peak | MISSION_7_GRADING_PROGRESSION_FINDINGS.md (Landsat) | Model-based estimate on A1 imagery |
| 3 | No one tested for arsenic during grading | EnviroStor 30020004: paper-only, arsenic never an analyte | A2 (absence) |
| 4 | Three dispersal pathways; recycled runoff sprayed on slopes/parks | Purple-pipe report; RWQCB Order 97-52 Addendum 4 | A2 + inference |
| TS | Tire swing on the walk to the site | User photo IMG_4503 | Verified field observation |
| PD | 1968 USGS water body at/near the pond | topo1968_water.json (USGS field survey) | A1 |
| PD | Corridor never graded; same ground in every era 1929 to 2025 | OC Survey / USGS / Eagle imagery crops | A1 imagery; persistence is an inference |
| PD | Sediment never sampled | Absence in state databases | A2 (absence) |
| TR | Public trail past the fence line and concrete | User photo (trail fork) | Verified field observation |
| 5 | Drinking water imported and tested; soil never tested in 20 years | SMWD CCRs; EnviroStor/GeoTracker | A2 |
| 5 | 23 ranked targets | mission7/sampling_targets.json | Model-based |
| P3 | Homes 1999 to 2006; grading peak 2002 | Grading progression findings | A1-derived |
| P3 | Two-step Ewing model (in-utero initiation, pubertal emergence), 2025 | Cell Reports 2025 (EWING_ARSENIC_AUDIT.md) | B1 |
| P3 | In-utero arsenic causes cancers decades later (Chile) | Steinmaus/Smith cohorts (EWING_ARSENIC_AUDIT.md) | A1/B1 |
| P3 | No study connects these to each other or to Ladera | EWING_ARSENIC_AUDIT.md verdict | Missing evidence (stated) |
| P3 | Personal statement ("I am not an oncologist ... not mine to decide") | Speaker | Opinion, first person |
| 6 | Independent project; no causation established | Project disclaimer | — |

Language discipline: the reel is labeled AI-assisted reconstruction on screen; no coordinates are shown;
no individual child or family is referenced; Ewing sarcoma is described as having no established
environmental cause; the Phase 3 question is framed as a hypothesis for a medical-records study.

## Correction, 2026-09-17 (pond)
The golf-course pond at the edge of the open space is NOT visible in any aerial before January 2004; it appears with the
Arroyo Trabuco golf course build-out (~2003-2004). Earlier narration and captions saying "the same pond, 1929 to 2025" and
"mapped by the 1968 survey as standing water" were wrong and have been replaced. The 2018 county DEM (EPSG:26946, feet)
puts the hillside where the concrete base was found at ~421 ft, the pond at ~334 ft and the 1968 USGS water body on the
creek floor at ~291 ft: the 1968 water body is DOWNHILL of the pond, not upstream. Corrected wording: the pond was built
with the golf course; it sits at the foot of the slope, between the hillside and the creek where the 1968 survey mapped
standing water; runoff from the slope passes through it. The grey vegetation ring is tule/bulrush, which dies back
seasonally; "looks dead" is stated as observation only.

## Correction 2, 2026-09-18 (pond position)
The pond coordinate used in the first Phase 2 cut (33.55756, -117.65184) was the earlier estimate of the target #6
remnant, not the pond in Andy's drone photos. Matching the drone frames and Andy's marked-up aerial against the OC 2025
1-ft orthoimage places the pond ~130 m south-south-west, immediately north-west of the bunker at the head of the
fairway (approx. 33.5565, -117.6523; kept off the site). All ten era tiles, the drainage graphic and the narration were
rebuilt on the corrected point. The USGS 2004 HRO mosaic was found to sit ~44 m north of the 2025 image at this spot
and its crop is shifted accordingly. Findings at the corrected point: no pond in 1929, 1937, 1947, 1953, 1960, 1969,
1980 or 1990 (field edge, then brush); the pond appears with the golf course (2004). Elevations (2018 county DEM, ft):
hillside where the base was found ~421; pond ~325; creek west of the pond ~280; the 1968 USGS water body (9,111 m2,
253 m long) lies on the creek floor ~240 m NORTH (upstream), ~291 ft. The creek flows south, so the 1968 body is
upstream of the pond, not downstream; earlier wording "just downhill" was wrong and is replaced with "on that creek,
about 260 yards upstream". The 1968 body is a large surface-water feature, two orders of magnitude bigger than a vat
(~2,000 gal); it is not the concrete base. It no longer appears as open water in any later imagery; the corridor
there is riparian woodland. Whether it was a seasonal pool or an impounded stock pond that silted in is not established.
