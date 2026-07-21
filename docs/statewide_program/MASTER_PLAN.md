# Statewide Land-Use Screening Program — Master Plan

**A phased, repeatable replication of the Ladera Ranch methodology across California's former
cattle ranchos and the communities built on them.**

Prepared for review before execution. Nothing here asserts contamination anywhere. The program
produces a **prioritised screening and lead list** — where the deep, human-verified investigation
should point next — not finished conclusions.

---

## 1. What this is, and what it is honestly not

**It is:** an automated front-end that runs the *documentary and archival* half of the Ladera
process against many targets at once — confirming which ranchos fell in the dipping-quarantine
counties, finding the earliest imagery and maps, auditing how far back each community's
environmental review looked, searching for dipping records tied to each ranch, and grading it all
on the same A1–D scale with mandatory counter-evidence.

**It is not:** a machine that produces 15 finished, Ladera-quality reports overnight. The Ladera
report's credibility came from human verification, four-plus published corrections, and careful
framing. No autonomous sweep reproduces that. Specifically, the program does **not**:

- run the full per-target GIS/imagery pipeline (georeferencing, water extraction, candidate-region
  mapping) — that is a semi-manual follow-on for the top-ranked targets only;
- assert or imply that any community is contaminated;
- reach any causal or health conclusion.

Read every output as a **lead requiring verification**, exactly as the Ladera corrections log
teaches. The program's job is to tell you *where the 40-year-gap question is worth asking next* —
cheaply, in parallel, overnight — so human effort goes to the targets that earn it.

---

## 2. The unit of work: one "scrub" = the Ladera pipeline, per target

For each target (a rancho and the community/communities on it), one scrub answers the same
questions this project answered for Ladera:

| # | Question | Method | Ladera analogue |
|---|---|---|---|
| A | Was this rancho in a dipping-quarantine county? | Deterministic lookup vs. USDA Circular 174 county list | Ch. 8 |
| B | Is the land residential, or federal/farmland/unbuilt? | Public record | Deprioritises Camp Pendleton, Tejon, Miller & Lux |
| C | What is the earliest imagery/map of this land? | USGS topoView, OC/county GIS, UCSB FrameFinder | Ch. 14 (1899 map, 1929 aerial) |
| D | How far back did the environmental review look? | CEQAnet, EnviroStor, GeoTracker, EIR appendices | Ch. 16 (the 1952 finding — the core audit) |
| E | Any dipping record tied to *this* ranch by name? | CDNC, Chronicling America, State Vet reports | Ch. 8 (Joplin/Trabuco) |
| F | Water/ranching intensity → sampling-frame plausibility | GNIS, historic topo water, terrain | Ch. 15 |
| G | Grade every finding; mandatory counter-evidence | A1–D, the project's standing rules | Evidence matrix |

The single most portable and valuable output is **D**: the gap between when dipping ended
(~1912–1915) and how far back that community's Phase I review actually reached. That number, per
community, is the headline.

---

## 3. Phases

### Phase 0 — Target registry (largely done)
`target_registry.csv` holds 16 seeded targets (7 HIGH, 5 MED, 3 LOW, 1 DONE). Phase 0 in the
workflow *expands* it by enumerating additional ranchos in each quarantine county that are now
residential, so the list grows from the flagship ~16 toward the fuller set.

### Phase 1 — Triage (cheap, fully parallel)
One lightweight agent per target does a 10-minute scrub of questions A, B, and a first pass at C
and D, and returns a **priority score** and a `deep_dive_recommended` flag. Federal/agricultural/
unbuilt targets (Camp Pendleton, Tejon, Miller & Lux) triage *out* here — the land isn't under
homes. Output: one triage record per target.

### Phase 2 — Deep dive (expensive, parallel per prioritised target)
For each target Phase 1 flags, a dedicated agent runs the full documentary pipeline (C–G):
earliest imagery/maps, the environmental-review-window audit, dipping-record search, water/
ranching intensity, and a per-target evidence record with grades and counter-evidence.

### Phase 3 — Adversarial verification (the Ladera lesson, enforced)
Every material finding is handed to a *second, skeptical* agent instructed to refute it —
default to "not established" when uncertain. This is the countermeasure for the exact failure the
Ladera corrections document: fluent, confident, wrong. Findings that don't survive are demoted.

### Phase 4 — Synthesis and ranking
A final agent assembles a **statewide priority ranking**: which communities have the largest
historical-review gap and the most plausible dipping proximity — i.e. where a real soil test
would matter most. This is a *prioritisation of unanswered questions*, not a contamination
ranking, and it is labelled as such on every row.

---

## 4. Quality gates (non-negotiable, enforced in every agent prompt)

1. **No fabrication.** Every claim cites a source or is marked "not found." Failed searches are
   reported as dead ends with the exact query.
2. **Mandatory counter-evidence.** Every finding carries its limiting/contradictory evidence, or
   an explicit "none identified."
3. **No contamination claims.** No output may state or imply arsenic/harm at any community. The
   only measured soil fact anywhere is "unstudied."
4. **Grading, no silent promotion.** A1–D on every source.
5. **Privacy.** No individual, address, parcel-owner, or health data.
6. **Distinguish absence-of-record from absence-of-fact.** "The searchable materials do not appear
   to identify…", never "they never studied…".

An output that violates a gate is demoted or dropped in Phase 3, not published.

---

## 5. Scale, cost, and runtime

- **Targets:** ~16 seeded, expandable to ~40–60 with Phase 0.
- **Agents:** roughly triage(N) + deep-dive(prioritised) + verify(findings) + 1 synthesis ≈
  **80–200 agent runs** depending on expansion and how many pass triage.
- **Tokens:** this is a **large** spend — plausibly several million output tokens for a full run.
  That is the trade for overnight breadth. Concurrency is capped (~10–16 agents at once), so it
  self-paces.
- **Runtime:** hours. Designed for exactly the overnight window you described.
- **Resumable:** the workflow is resumable — a killed or edited run re-uses the cached prefix, so
  you can stop, review partial output, and continue.

---

## 6. Output structure

```
docs/statewide_program/
  target_registry.csv            # the master list (this file's companion)
  results/
    <target_id>_triage.json      # Phase 1
    <target_id>_deepdive.json    # Phase 2 (evidence record, graded)
    <target_id>_verdict.json     # Phase 3
  STATEWIDE_RANKING.md           # Phase 4 — the headline: review-gap ranking
```

Each `deepdive` record mirrors the Ladera evidence matrix: claims, classification, confidence,
supporting evidence, counter-evidence, citation.

---

## 7. How to run it

The executable is `scripts/statewide_sweep.workflow.js`. It is launched as a single Workflow
call — one click, then it runs in the background and notifies on completion:

> "Run the statewide sweep" — and it launches `scripts/statewide_sweep.workflow.js`.

To run it truly unattended overnight, set the session to bypass/auto-accept permissions before
launching, so no prompt interrupts it. Review this plan and the registry first; edit
`target_registry.csv` to add/remove targets or change priorities; then say the word.

---

## 8. The honest expectation

When it finishes you will have, for each community, a graded first-pass answer to *"how far back
did anyone look, and is there any documented dipping nearby?"* — plus a statewide ranking of where
that gap is widest. You will **not** have proof of anything about any community, and the program
is built so that it cannot accidentally manufacture such proof.

The most likely headline result, based on Ladera: **most of these communities' environmental
reviews also began in the 1950s, also never reached the dipping era, and also never soil-tested
for arsenic** — because that is a structural feature of the review framework, not a fact about
any one place. If that is what comes back, the program will have shown, rigorously and at scale,
that the Ladera gap is the *general case* — which is the single most important thing this whole
investigation has to say.
