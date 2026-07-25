# PHASED & GATED EXECUTION PLAN
**Arsenic & the reported cancers — physician-directed, attorney-supervised**
Version 1.0 · 2026-07-23 · hypothesis-neutral · no causation asserted

This plan sequences all 16 workstreams into **6 phases** separated by **decision gates**. It defines
what proceeds automatically at full authority versus what must stop at a human gate. It is designed so
independent experts can see exactly where the project is, what has been cleared, and what is blocked.

---

## 1. AUTHORITY MODEL ("full authority," scoped)

**Granted — Research Engine executes autonomously, at full authority, continuously:**
desk literature search across all named databases; source capture + grading + hashing; evidence /
mechanism / claims matrices; synthesis docs; **drafting** protocols, analysis plans, briefs, request
letters, and checklists; QA and reproducibility logging; committing/pushing to the repo **with the
private folder (04) excluded**.

**Reserved — never opens without the named gate owner's written authorization** (these are also the
standing prohibitions of this project):
| Reserved action | Gate owner |
|---|---|
| Collecting/handling any biological specimen (teeth, nails, blood spots, FFPE) | Physician lead + Ethics/IRB |
| Soil/dust/water sampling on any property | Attorney + landowner/agency permission |
| Any handling of PHI / case-identifying data (folder 04) | Physician lead + Ethics/IRB |
| Contacting families, witnesses, agencies, researchers, defendants | Attorney (project does **not** contact) |
| Legal conclusions or advocacy language | Attorney (out of scope for this engine) |
| Public release of any output | Physician lead + Attorney |
| Initiating lab/tumor testing | Physician lead + Ethics/IRB |

**Standing rules that never gate open:** no fabricated citations; absence-of-research recorded as a
finding; contradictory evidence weighted equally; source-before-significance; PHI stays private;
preserve originals + hashes. (See PROJECT_SCOPE.)

---

## 2. PHASE OVERVIEW

| Phase | Name | Nature | Authority | Exit gate |
|---|---|---|---|---|
| 0 | Governance & scaffold | desk | auto | — (complete) |
| 1 | Desk evidence base | desk | **auto (full authority)** | **GATE A** — scientific integrity review |
| 2 | Designs & protocols | desk | **auto (drafting)** | **GATE B** — expert + ethics + legal sign-off |
| 3 | Evidence preservation | real-world prep→action | draft auto / **act gated** | **GATE C** — holds executed |
| 4 | Acquisition & testing | real-world | **gated (experts/labs)** | **GATE D** — results QA'd |
| 5 | Integration & reporting | desk→gated release | auto draft / **gated release** | **GATE E** — release decision |

---

## 3. PHASES IN DETAIL

### PHASE 0 — Governance & scaffold  ✅ COMPLETE
Deliverables done: 24-folder repo; PROJECT_SCOPE, SEARCH_PROTOCOL, DATABASE_SCHEMA; SEARCH_LOG;
seeded matrices; privacy guard (04 gitignored).

### PHASE 1 — Desk evidence base  ◐ IN PROGRESS (~55%)  · authority: AUTO
**Objective:** exhaust the accessible literature; grade and cross-check every claim.
**Workstreams:** 1(taxonomy, public fields only) · 2 mechanisms · 3 direct As–Ewing · 4 bridge ·
5 other cancers · 6 cattle-dip chemistry · 7 environmental fate · 8 biomarkers · 9 molecular
signatures · 13 alternatives.
**Done:** 3,4,5,8 first pass; 10 design (Phase-2 item, pulled early); GIS schema.
**Remaining:** native-database re-runs (PubMed/Europe PMC/OpenAlex/etc.) with logged counts; 6, 7, 9,
13; complete matrices; **dual-review** consequential findings; CONTRADICTORY_EVIDENCE.md; TOP_100
sources; TOP_25 gaps; TOP_20 hypotheses; TOP_15 falsifiers.
**Exit criteria → GATE A:** every substantive claim cited + graded; searches reproducible; dual-review
done; contradictory evidence catalogued; no unresolved fabrication/integrity flags.

> **GATE A — Scientific integrity review.** Owner: independent scientific reviewers (toxicology,
> molecular oncology, environmental epidemiology). Criteria: reproducibility of SEARCH_LOG; source
> integrity; balanced capture of negative evidence; correct evidence levels. Output: sign-off or
> revise list. *Blocks Phase 2 protocolization until passed.*

### PHASE 2 — Designs & protocols  ○ NOT STARTED  · authority: AUTO (draft only; no execution)
**Objective:** convert findings into testable, review-ready protocols. No real-world action.
**Deliverables:** 14 critical-experiments dossier (design/controls/power/endpoints/blinding/ethics);
blinded tumor molecular + metallomics protocol (9); biomarker exposure-reconstruction protocol (8/10);
authorized soil-sampling SAP (analyte set: total+bioaccessible As, **lead**, speciation; 0–6 in);
**preregistration** of the epi plan (12); GIS build spec (11); 12 causal-inference weight-of-evidence
framework (Bradford Hill + source–pathway–receptor + mode-of-action + AOP).
**Exit criteria → GATE B:** protocols complete, powered, ethically specified, and internally consistent
with Phase-1 evidence.

> **GATE B — Expert + Ethics/IRB + Legal review.** Owners: domain experts; Ethics/IRB (human subjects,
> specimens, PHI); Attorney (chain of custody, discovery, privilege). **This is the gate that can
> authorize real-world action.** Output: approved protocols + explicit authorizations (which
> specimens/sites/analyses, under what custody). *Nothing physical happens before GATE B.*

### PHASE 3 — Evidence preservation  ○ NOT STARTED · authority: DRAFT auto / ACT gated
**Objective:** stop loss of destroyable evidence (time-critical).
**Draft now (auto):** IMMEDIATE_EVIDENCE_PRESERVATION_CHECKLIST ✅; draft legal-hold letters, records
requests, specimen-retention guidance.
**Act (gated, human):** attorney issues legal holds (newborn blood-spot cards, FFPE blocks, ranch/
county/state archives); families retain keepsakes **via their own clinicians/counsel**; soil at
priority grounds secured **before any grading/remediation** under authorized chain of custody.
**Exit → GATE C:** holds in place; priority soil access permitted.

> **GATE C — Preservation confirmed.** Owner: Attorney + Physician lead. Criteria: holds executed;
> custody established. *Unblocks acquisition.*

### PHASE 4 — Acquisition & testing  ○ NOT STARTED · authority: GATED (experts/labs execute)
**Objective:** generate the missing measurements. **Executed by authorized clinicians/labs, not this
engine;** the engine supports design fidelity, data management, and blinded analysis interpretation.
**Activities (each pre-authorized at GATE B):** soil sampling + speciation; biomarker reconstruction
(teeth/nails/blood spots); blinded tumor WGS/long-read/RNA-seq/methylation + metallomics; CCR-based
epidemiology per the preregistered plan; GIS integration (masked public / private analytic).
**Exit → GATE D:** results quality-controlled, chain of custody intact, analyses per preregistration.

> **GATE D — Results integrity.** Owner: scientific reviewers + biostatistician. Criteria: QA/QC,
> no preregistration deviations unlogged, PHI protected. *Unblocks integration.*

### PHASE 5 — Integration & reporting  ○ NOT STARTED · authority: AUTO draft / GATED release
**Objective:** weigh all evidence; state exactly what is established / plausible / unresolved /
excluded.
**Deliverables:** updated 12 causal weight-of-evidence; final STUDY_EVIDENCE_MATRIX; updated
DOCTOR_TECHNICAL_BRIEF and ATTORNEY_SCIENCE_BRIEF; EXECUTIVE_SUMMARY; general vs specific causation
statement; research-gaps for any unresolved links.
**Exit → GATE E:** briefs internally consistent, dual-reviewed, PHI-clean.

> **GATE E — Release decision.** Owners: Physician lead + Attorney. Criteria: accuracy, privacy,
> appropriate hedging, no advocacy overreach. Decides what (if anything) is shared, with whom, and
> whether public materials in `23_..._hold` are ever released.

---

## 4. DEPENDENCIES (critical path)
Phase 1 → GATE A → Phase 2 → **GATE B (authorizes reality)** → Phase 3 preservation → Phase 4 testing
→ GATE D → Phase 5 → GATE E. Preservation (3) runs **in parallel and urgently** once GATE B clears the
relevant specimens/sites, because those items degrade.

## 5. RISK REGISTER (top)
| Risk | Impact | Mitigation |
|---|---|---|
| Specimens/soil lost before holds | irreversible | Phase 3 urgency; draft holds now; flag at every gate |
| Texas-Sharpshooter / cluster overreach | credibility, legal | preregistration (12); verified counts only |
| PHI leak to public repo | ethical/legal | 04 gitignored; pre-commit check every push |
| Over-strong causal language | Daubert/credibility | evidence levels a–g on every claim; dual review |
| Fabricated/incorrect citation | fatal to defensibility | never-fabricate rule; native-db verification at GATE A |
| Confounder neglect (orchard lead-arsenate, DDT, ancestry) | biased inference | Workstream 13 + ancestry standardization |

## 6. PROGRESS TRACKER
- Phase 0 ✅ · Phase 1 ◐ (WS 3,4,5,8,10,11 first pass done; 6,7,9,13, native-db, dual-review remaining)
- Gates A–E: not yet reached.

## 7. IMMEDIATE NEXT (auto, Phase 1) — proceeding under full authority
1. Workstream 12 causal-inference weight-of-evidence framework (Bradford Hill etc.).
2. Workstream 6 cattle-dip chemistry crosswalk (As trioxide vs arsenite/arsenate; CAS; soil fate).
3. Workstream 7 environmental fate & bioavailability.
4. Native-database confirmation of Priority-1/2 citations; begin CONTRADICTORY_EVIDENCE.md.
5. Assemble GATE-A package (TOP_100 sources, TOP_25 gaps, TOP_20 hypotheses, TOP_15 falsifiers).
