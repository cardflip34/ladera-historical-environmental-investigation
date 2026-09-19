# Phase 2 — Source of truth

Single reference for everything the Phase 2 investigation produced, what each item asserts, its evidence grade,
and whether it is cleared for publication on californiasforgottenpast.org. If an item is not listed here, it is
not cleared. Last updated 19 September 2026.

Two working copies, one GitHub repo (`cardflip34/ladera-historical-environmental-investigation`):
- `~/Ladera-Ranch` — branch `main` — the public website.
- `~/Documents/Ladera Ranch` — branch `mission6/staging-integration` — the evidence and research archive.

---

## 1. The field discovery (the core of Phase 2)

| Item | Path (evidence repo) | Asserts | Grade | Publish |
|---|---|---|---|---|
| Field observation report | `evidence/lhdrs/field_observations/FIELD_OBSERVATION_v5.pdf` | A concrete rectangle with iron pipe rails was observed in ungraded open space, August 2026. Floor ≈12 ft, matching the floor length in USDA BAI Circular 183 (1911). | Field observation, **identification unestablished** | Yes, with the caveat |
| Field photographs | `evidence/lhdrs/field_observations/2026-08-07_*.jpg` (rim, rails, corner, timber post) | What was seen. | Verified field observation | Yes |
| Provenance record | `evidence/lhdrs/field_observations/2026-08-07_concrete_structure.provenance.json` | Explicitly lists what is NOT established: that this is a dipping vat, that arsenic is present, that any exposure occurred. | — | Reference |
| Trail-fork photo | `evidence/lhdrs/phase2_base/trail_fork.jpg` | Ranch-era post and rail beside a public trail. | Verified field observation | Yes |
| Drone photographs | `evidence/lhdrs/phase2_base/drone_pond_close.jpg`, `drone_pond_wide.jpg` | The golf-course pond, the dead-vegetation ring, the fairway. | Verified field observation | Yes |

**Hard rule:** the concrete feature is a *candidate*. Every public reference must say the identification is not
established until soil is tested. **No coordinates anywhere**, pending notification of the landowner and the State.

---

## 2. The reconstruction (AI-assisted imagery)

| Item | Path | Asserts | Grade | Publish |
|---|---|---|---|---|
| Reconstruction reel | `evidence/lhdrs/field_observations/reconstruction/ai_pass/Dipping_Station_Reel_9x16.mp4` | What a 1911-specification station looked like: pens, chute, 26 ft rim, 6.5 ft deep, ≈2,000 gal, drip pen. | **AI-assisted reconstruction after USDA Circular 183. Not historical footage.** | Yes, label required |
| Build scripts | `.../ai_pass/compose_reel.py`, `multi.py`, `site_track.json` | Reproducibility of the above. | — | Reference |
| Cross-section diagram | `evidence/lhdrs/field_observations/vat_cross_section_reconstruction.png` | Vat geometry from the federal plans. | A1 source, drawn | Yes |
| 1911 plan | `evidence/lhdrs/field_observations/dipping_station_plan_1911.png` | The federal drawing itself. | A1 | Yes |

**Hard rule:** every frame or still from the reel carries the label *"AI-assisted reconstruction after USDA
Bureau of Animal Industry Circular 183 (1911); not historical footage."* This is also a YouTube AI-disclosure
requirement already satisfied on the uploaded video.

---

## 3. The arithmetic

| Item | Path | Asserts | Grade |
|---|---|---|---|
| Mass-balance master | `reports/ARSENIC_QUANTIFICATION_MASTER.md` | 8 lb As₂O₃ per 500 gal; 14-day cadence; whole-ranch 6,692–39,748 lb; 1,338–7,949 lb at a vat footprint; 128–763 mg/kg vs California background 1–11 mg/kg. | **Model estimate** on A1 inputs |
| Herd size | Same | Circular 174 (1911) reports ~21,000 head on one quarantined ranch in 1910 (A1). The O'Neill family history says 25,000+ (B2, undated). | Mixed, cite both |
| Lethal-dose comparison | Phase 2 film, 5:12 | Central estimate ≈21,000 lb ÷ 100–300 mg = 32–96 million nominal doses. | **Arithmetic, not toxicology** |

**Hard rule:** the lethal-dose figure never appears without its caveat verbatim: *"Soil-bound arsenic is only
partly bioavailable; nobody ingests soil in quantity; the number says one thing: the mass involved was large.
It says nothing about exposure, which has never been measured here."*

---

## 4. The pond and the drainage (corrected 18 September 2026)

| Item | Path | Asserts | Grade |
|---|---|---|---|
| Era tiles 1929–2025 | `evidence/lhdrs/phase2_base/pond_eras/era_*.jpg` + `win.json` | The same 660 m window in ten eras. | A+ imagery |
| Correction record | `evidence/lhdrs/phase2_base/NARRATION_AUDIT.md` § "Correction 2" | Full record of the error and the fix. | — |

**The corrected facts.** The golf-course pond was **built with the Arroyo Trabuco course, first visible January
2004**; it is absent in 1929, 1937, 1947, 1953, 1960, 1969, 1980 and 1990. It sits at the foot of the slope below
the find. On the 2018 county DEM: hillside ≈421 ft, pond ≈325 ft, creek ≈280 ft. The 1968 USGS survey mapped a
9,111 m² stock-water body on the creek **≈240 m upstream** (≈291 ft) — upstream, not downhill. That body no
longer appears as open water; the corridor is riparian woodland.

**Superseded wording, do not reuse:** "the same pond since 1929", "mapped by the 1968 survey as standing water",
"150 yards upstream", "just downhill". The dead-vegetation ring is tule and bulrush with a seasonal dieback
explanation; describe it as an observation, never as arsenic damage.

---

## 5. Florida: the answer key

| Item | Path | Asserts | Grade |
|---|---|---|---|
| FDEP records response | `research/national_crossreference/G11_response/` (+ SHA-256 manifest) | State inventory: **3,281 vats**; entries are ranch name and year only, no locations. **Palm Beach County absent entirely.** | A2 |
| Findings | `research/national_crossreference/phase2/FLORIDA_ANSWER_KEY_FINDINGS.md` | **11 of 12 tested sites exceeded** the soil standard; reuse as pesticide-mixing areas and swimming holes for children; vats found inside developments and at a school. | A2 |
| Vat photographs | `reports/EXHIBIT_FL_VAT_PHOTOS.pdf` | FDEP's own photographs. | A2 |
| National findings | `reports/NATIONAL_FINDINGS.pdf`, `research/oc_dipping_records/STATE_REGISTRY_CROSSREFERENCE.md` | 1 of 15 program states built a contamination registry. California built none. | A1/A2 |

---

## 6. The Ewing audit

| Item | Path | Asserts | Grade |
|---|---|---|---|
| Graded audit | `docs/lhdrs/science/EWING_ARSENIC_AUDIT.md`, `reports/EWING_ARSENIC_AUDIT.pdf` | Seven-link chain, scored. Two links have **no supporting literature at all**; one points the other way (ATO kills Ewing cells at drug doses); the three Ladera-specific links are **unmeasured**. | B1 / mixed |

**Verdict wording, use exactly:** *"a testable hypothesis, not a finding."* Ewing sarcoma has no established
environmental cause. The fusion is somatic, not inherited. Ancestry-linked incidence varies sevenfold and must be
adjusted for in any analysis.

---

## 7. Water: the purple-pipe loop

| Item | Path | Asserts | Grade |
|---|---|---|---|
| Report (HTML) | `research/water_supply/purple_pipe_loop_report.html` | The routing audit. | — |
| Report (PDF) | `reports/PURPLE_PIPE_LOOP.pdf` | Same. | — |
| Routing memo | `research/water_supply/HORNO_RUNOFF_ROUTING.md` | The documentary chain. | A2 |
| Regulatory source | `research/water_supply/RWQCB_Addendum4_Order97-52_Horno_UWRF.pdf` | Addendum 4 to Order 97-52. | **A1, primary** |
| Maps | `research/water_supply/horno_system_map_2025.jpg`, `resolved_route_map_2025.jpg`, `candidate_routes_map_2025.jpg`, `loop_schematic.png`, `loop_accumulation.png` | The routes, drawn on satellite. | A+ imagery |
| Phased plan | `docs/lhdrs/HORNO_CREEK_PHASED_INVESTIGATION.md` | What would resolve the open questions. | — |

**What is established.** Runoff reaching the Horno basin goes to the Upper Chiquita / Horno urban water
reclamation facility, then to roughly 7 acres of HOA wetlands, then blends into the recycled ("purple pipe")
system that irrigates community slopes and parks — **bypassing Chiquita Creek**. Permit sampling under Order
97-52 covers salts and nutrients; **it does not include arsenic or other metals**. That is the finding: not that
anything harmful is circulating, but that the loop exists and has never been tested for the analyte in question.

**Language discipline.** "Confirmed by permit documents" applies to the route. The word *loop* describes
capture-treat-reuse-irrigate; it is not a claim that contaminants accumulate. Say "unmeasured", not "contaminated".
Do not name John Gresko in any public report.

---

## 8. Sampling strategy (new, 19 September 2026)

| Item | Path | Asserts |
|---|---|---|
| Full report | Desktop `Ladera_Soil_Sampling_Strategy/LADERA_SOIL_SAMPLING_STRATEGY.html` | Audit of Ladera Health Watch and the CSUF sampling; analyte explainer; grading-flow model; 23 targets re-tiered; per-target accessible stations; field and lab specification; decision rules. |
| Technical share version | `.../LADERA_SAMPLING_PLAN_TECHNICAL.html` | Same plan, engineer-facing. |
| Overview map | `.../assets/map_overview.jpg` | All 23 targets on 2025 imagery, tiered, with drainage and recommended stations. |
| Data | `.../targets_data.json` | Machine-readable targets with classification and recommended coordinates. |

**Key public-facing facts.** 7 of 23 targets sit on ungraded ground; 10 are under housing or fairway and need an
offset strategy; 6 are outside the Ladera build-out. The community's disturbed footprint peaked at **52.8 % in
2002** (Landsat, `evidence/lhdrs/mission7/grading_maps_summary.json`). **Do not publish the per-target
coordinates** on the website; they are for the sampling team.

---

## 9. The films

| Item | Location | Notes |
|---|---|---|
| Phase 2, vertical | Desktop `Ladera_Phase2_FINAL.mp4` | 12:42, captions burned in |
| Phase 2, YouTube | `https://youtu.be/XzIJ-pHr-JU` | Public. Title: *Is California's Soil Poisoned? I Found an Arsenic Vat Base Above Ladera Ranch \| Phase 2* |
| Phase 1, YouTube | `https://youtu.be/QDGB_R92jns` | Public, re-thumbnailed, links to Phase 2 |
| Captions | `Ladera_Phase2_BASE/Ladera_Phase2_FINAL_captions.srt` | Upload to YouTube Subtitles |
| Narration script | `evidence/lhdrs/phase2_base/phase2_script.txt` | Every spoken word |
| Claim audit | `evidence/lhdrs/phase2_base/NARRATION_AUDIT.md` | **Every spoken claim, its source, its grade, and two corrections made** |
| Covers | Desktop `Ladera_Phase2_COVER_9x16.jpg`, `Ladera_Phase1_COVER_9x16.jpg` | Matching pair |

---

## 10. Corrections log (publish these; they are the credibility)

1. **Herd size.** "The federal circular documents more than 25,000 head" was wrong. The circular (A1) reports
   ~21,000 on one ranch in 1910; 25,000+ is the family's undated figure (B2). Both are now cited separately.
2. **Grading peak.** "More than half the community was bare" became "more than four in ten acres", matching the
   41.3 % figure for 2003; the 2002 peak is 52.8 %.
3. **Pond age and position.** See §4. The pond is a golf-course feature from ~2004, and the 1968 water body is
   upstream, not downhill.
4. **"Never been tested."** Superseded. Correct form everywhere: *"was not tested for twenty years; some soil
   sampling is now under way."*

---

## Standing rules for anything published

- Hypothesis-neutral. No causal claims. "Reported cancer cluster", never "confirmed".
- No coordinates of the concrete feature, the pond, or the sampling targets.
- No identification of individual children or families. Health data at aggregate level only.
- Every figure carries a source line and an evidence grade.
- AI-assisted imagery is labelled as such, every time.
- A null result gets the same prominence as a positive one. This is stated publicly and must be honoured.
- The site remains password protected. Access line: *"This site is password protected while the work is
  reviewed. For access, message Andy on Instagram or email andystavros@icloud.com."*
