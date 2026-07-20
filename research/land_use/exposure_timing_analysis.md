# Exposure Timing — Does the Grading Hypothesis Survive the Ages?

**Prepared:** 2026-07-18. Reproduce: `python3 pipelines/python/exposure_timing.py`.
Companion data: `exposure_timing_matrix.csv`.

## The objection

Mass grading of the former agricultural land occurred roughly **1999–2006** — twenty to
twenty-seven years before the present. Reported diagnoses span **2013–2026**. If children are
being diagnosed now, many of them were not born when the earth was moved. Does the timeline
actually work?

**It is a fair and important objection, and it does real damage — but only to one of two
mechanisms that have been getting conflated.**

## Two mechanisms, opposite predictions

| | **M1 — Construction-era dust** | **M2 — Persistent soil residue** |
|---|---|---|
| What it is | Grading mobilised buried residue as respirable/ingestible dust | Arsenic and organochlorines remain in surface soil indefinitely |
| Time-bound? | **Yes** — an event, 1999–2006 | **No** — a standing condition |
| Requires child present during grading? | **Yes** (incl. in utero) | **No** |
| Predicts | Cases concentrated in birth cohorts ≤ ~2007 | Cases across **all** birth cohorts, unrelated to grading date |
| Effect of time passing | Weakens steadily | Does not weaken |

The user's objection is fatal-ish to **M1** and **irrelevant to M2**. They have been treated as
one hypothesis ("toxic soil from grading"); they are not, and separating them changes what the
evidence can support.

### Why M2 does not decay with time

- **Arsenic is a chemical element.** It does not degrade, ever. Lead-arsenate residues from
  orchard spraying persist indefinitely in surface soil.
- **Organochlorines (DDT/DDE, toxaphene, chlordane) persist for decades.** The strongest
  evidence here is local and empirical, not theoretical: DTSC's own investigations found exactly
  these compounds in soil at **neighbouring former-farm school sites** — San Juan Elementary
  (arsenic, chlordane, DDT), Ambuehl (DDT, toxaphene), Plant Depot (arsenic) — decades after
  cultivation ceased. Persistence is demonstrated on the ground, roughly three miles away.

So a child born in 2012 playing in soil containing 1960s arsenic has the same contact
opportunity as a child born in 2000. **M2 has no expiry date.**

## The arithmetic on M1

For a case diagnosed in year *D* at age *A*, birth year = *D − A*. A child could have been
present during grading (including in utero) if born on or before ~2007.

Share of plausible pediatric ages (5–19) whose birth cohort overlaps grading, by diagnosis year:

| Diagnosis year | Ages overlapping grading | Share |
|---|---|---|
| 2013 | 14 of 15 | 93% |
| 2016 | 11 of 15 | 73% |
| 2019 | 8 of 15 | 53% |
| 2022 | 5 of 15 | 33% |
| 2024 | 3 of 15 | 20% |
| 2026 | 1 of 15 | 7% |

**The M1 window is closing fast.** By 2026, a case would have to be ~19 years old to have been
present during grading at all. Diagnoses in young children in recent years are simply
incompatible with M1.

## The one datable Ewing case

Public reporting gives exactly one Ewing case with both an age and a date: **diagnosed August
2024 at age ~17**, which implies a birth window of roughly **August 2006 – August 2007**.

**Verdict: boundary case, uninformative.** If born late 2006, the child was in utero or newborn
during the final months of grading — M1 is marginally possible. If born in 2007, M1 is
unavailable for that case. Either way it is fully compatible with M2. A single case sitting on
the boundary cannot discriminate.

## What this means for the platform's leading hypothesis

The legacy-soil-residue hypothesis **survives this objection, but in narrowed form**:

- The claim "grading mobilised contaminated dust and that caused these cancers" is
  **substantially weakened** by the timing for recent diagnoses, and cannot apply at all to
  children born after ~2007.
- The claim "the community sits on soil that may still contain arsenic and organochlorine
  residues, which children contact through ordinary play" is **untouched** by the timing
  objection, because the hazard does not decay.

The platform's exposure-screening entry for legacy soil residue is therefore re-scoped to
emphasise **M2 (standing residue)** rather than M1 (the grading event), with construction-era
dust retained as a separate, time-limited sub-hypothesis relevant only to the earliest birth
cohorts.

## The decisive missing data

Because M1 and M2 make **opposite** predictions about birth cohorts, the **birth-year
distribution of the cases is a discriminating test**:

- Cases clustered in births ≤2007 → supports M1 (and by extension the grading event).
- Cases spread across birth years, including post-2010 → refutes M1, leaves M2 intact.
- Cases clustered by *village* and its specific grading date → strong M1 signal.

**We cannot run this test.** Only one of the reported Ewing cases has a published age and
diagnosis year. This raises the value of registry data (gate **G01**) beyond simply confirming
counts: **birth years alone would discriminate between the two leading versions of the
environmental hypothesis.**

A further caveat cuts both ways: **Ewing sarcoma's etiologic window is unknown.** The fusion
event arises postnatally for reasons not established, so no latency assumption can be used to
rule either mechanism in or out. Anyone asserting "the exposure must have occurred N years
before diagnosis" is asserting something the literature does not support.

## Added to the evidence-gate request

Gate G01 (California Cancer Registry) is amended to request, in aggregate and subject to
small-numbers suppression: **birth year (or age at diagnosis with diagnosis year)** for
confirmed cases, and — if lawfully releasable — **duration and period of residence**. That
single field set would materially discriminate between the hypotheses currently in play.
