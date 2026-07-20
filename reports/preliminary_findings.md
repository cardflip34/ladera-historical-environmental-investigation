# LEHRP — Preliminary Public-Source Findings Report

**Date:** 2026-07-18 · **Status:** Preliminary, public-source only · **Version:** 0.3.0

> **This report does not provide medical advice and does not establish causation.** Publicly
> reported health events may not have been independently medically verified. Geographic and
> temporal overlap does not establish exposure or causation. It uses only the approved
> language in `CLAUDE.md` and is bound by `CLAIMS_AND_LIMITATIONS.md` and
> `ETHICS_AND_PRIVACY.md`.

This report answers the twelve required questions from the research protocol using only
public-source evidence gathered in Phases 0–10. Record counts: **45 sources** (graded A1–D),
**5 aggregate health events**, **22 literature entries**, **18 active ingredients**, **13
environmental sites**, **6 oil/gas wells**, **25 water-quality records**, **7 land-use
periods**, **8 inventoried sites**, **5 GIS layers**.

---

## 1. What is publicly verified?

- **An official multi-agency data review is underway.** The Orange County Health Care
  Agency's County Health Officer convened representatives of the **California Cancer
  Registry**, **UC Irvine Cancer Center**, and the **OC Agricultural Commissioner's Office**
  to conduct an **updated review of cancer data**; findings were pending as of retrieval.
  *(Officially reported; A2 statement via multiple B2 outlets.)*
- The agency's **initial** review "did not find a particular pattern"; a further review is
  planned. *(Officially reported.)*
- **A federal investigation was requested** — First Assistant U.S. Attorney Bill Essayli
  asked EPA to investigate on 2026-07-17. **No EPA response was found.** *(Confirmed request;
  outcome unknown.)*
- **LARMAC** announced a **60-day pause** on certain routine landscape products and formed an
  advisory committee, while stating it is unaware of any agency determination linking its
  practices to the illnesses. *(Officially reported by the HOA.)*
- **Demographics** (Confirmed, A1): Ladera Ranch CDP ≈ 23,793 residents; ~9,115 aged 0–19
  (38%); ~4,906 aged 10–19; 63.6% non-Hispanic white; built out ~1999–2010 on former Rancho
  Mission Viejo ranch land.
- **Drinking water** (Confirmed, A1/A2): served by Santa Margarita Water District, **100%
  imported treated surface water**, no local groundwater, **no chemical MCL violations** on
  record; disinfection byproducts (TTHM/HAA5) below MCLs; no chromium-6/PFAS/perchlorate/
  1,2,3-TCP detections.
- **One documented common-area pesticide** (Officially/primary, A2): a posted Notice of
  Pesticide Application (O'Connell Landscape, Dec 2023, continuing 2025) records **"Lifeline"
  (glufosinate-ammonium, EPA Reg. 70506-310)** applied to common-area SBA zones.

## 2. What is publicly reported but unverified?

- The **case counts themselves.** Public sources give "at least 6" Ewing sarcoma since 2013
  (Ladera Ranch, Ewing only), "about a dozen" rare cancers (mixed types **and** multiple
  cities), and a single-source "12 Ewing" outlier. No count is registry-verified. *(Publicly
  alleged.)* Two individual cases are datable (a 2024 Ewing diagnosis that progressed to
  fatal secondary AML in 2026; a 2026 synovial sarcoma).
- **"17 different pesticides applied in June, almost daily"** — an attorney/resident
  characterization of records reviewed, via the NY Post; the underlying records were
  reportedly withheld. *(Publicly alleged; C.)*
- **Glufosinate / "Lifeline" / "Attrimec" as the cause** — advanced by advocacy groups; not
  an agency finding. *(Publicly alleged.)*
- **That a true "cancer cluster" exists** — not confirmed by any official body.

## 3. What pesticide-use information is available?

California's **Pesticide Use Reporting (PUR)** is bulk-downloadable (1974–2023) at ~1-sq-mi
granularity. But coverage of **urban/landscape** use is partial: licensed common-area
applications by a business-for-hire *are* reportable, but **homeowner self-application is
exempt** and **structural pest control appears only as county monthly totals**. **Absence of
a PUR record is not evidence of non-application.** The most concrete primary evidence is the
posted LARMAC/O'Connell notice (§1). Restricted-materials permits and LARMAC's full history
are not publicly queryable (evidence gates).

**School pesticide program (updated 2026-07-18).** Capistrano USD's **Integrated Pest
Management Plan was obtained** (A2, primary). It confirms the program covers **both structural
and landscape pests** district-wide, states pesticides are used "only after other options have
been shown ineffective," and notes CUSD "may hire a contracted pest control company on an as
needed basis." Parents/staff may register for **72-hour advance** application notices. However
the plan **names no products and no contractor**, and the separate *Annual Pesticide
Notification and Product List* — though publicly linked from the district's site — resolves to
a document requiring sign-in and was therefore **not retrievable** (access controls respected).
This converts a vague gap into a specific, actionable CPRA request (see §12 and the
evidence-gate package).

## 4. What exact applications can be mapped?

**None at parcel precision — and, per an empirical test of the state's own dataset, none at
section precision either.**

We downloaded and processed DPR's 2023 PUR archive (A1; 79,473 Orange County records). The
result materially **corrects an earlier working assumption**:

| Site type | Records | Located | % located |
|---|---|---|---|
| Structural pest control | 55,442 | 0 | 0.0% |
| **Landscape maintenance** | **15,383** | **22** | **0.1%** |
| Nursery – outdoor containers | 2,990 | 2,982 | 99.7% |
| Golf course turf | 1,375 | 0 | 0.0% |
| Agriculture (fruiting pepper) | 183 | 183 | 100.0% |

Overall, **94.6% of Orange County pesticide records carry no location at all.** Landscape
maintenance *is* reported as a category (110,664 lbs) but is effectively county-level, not
COMTRS. Separately, a BLM PLSS lookup places Ladera Ranch in **T7S R7W / T7S R8W** with
**no section number** — consistent with former Mexican land-grant land never subdivided into
PLSS sections (inference; to be confirmed against DPR's PLSSNET).

**Conclusion: PUR is structurally incapable of placing a pesticide application inside Ladera
Ranch.** The documented "Lifeline" applications remain at **reporting-unit** precision
(village common-area SBA zones). This makes the posted LARMAC/O'Connell notices the *only*
public location-specific evidence and **raises the priority of gates G04/G05** (HOA and vendor
application logs), which also carry high destruction risk.

PUR does, however, **independently confirm glufosinate** as a major regional landscape
herbicide: 442 Orange County records / 10,531.9 lbs in 2023, of which 336 records (10,177 lbs)
were landscape maintenance — corroborating the documented pattern as *ordinary regional
practice*, not as evidence of causation. Glyphosate remains larger (1,361 landscape records,
~30,052 lbs).

## 5. What applications can only be located approximately?

The common-area glufosinate program (village-level SBA zones, 2023–2025); any PUR-reported
landscape applications (~1-sq-mi section); and structural pest control (county-month only).
Recycled-water irrigation footprint is community-wide but its constituent quality is unknown.

## 6. What products appear in policies, contracts, labels, or reports?

- **Lifeline** (glufosinate, UPL, EPA Reg. 70506-310) — documented in common-area notices;
  **Finale** (glufosinate) is the landscape-labeled analog.
- **"Attrimec"** — named in one grade-C source; EPA registration and active ingredient
  **not independently verified**.
- LARMAC confirms it contracts **O'Connell Landscape** for pest management including weeds.

## 7. What active ingredients deserve deeper review?

Prioritized on frequency/proximity/persistence/toxicology/literature — **not** on any
assumed causal role:

1. **Legacy organochlorines & arsenicals (DDT/DDE, toxaphene, chlordane, lead-arsenate,
   arsenic).** Persistent; confirmed at neighboring former-agricultural sites (§8); overlap
   the developmental window via construction-era soil disturbance. **Highest-priority
   testable hypothesis.**
2. **Glufosinate** — documented on-site, but non-persistent (~7.4 d soil), no Ewing link,
   recent timing may post-date etiologic windows.
3. **Glyphosate, 2,4-D, pyrethroids (bifenthrin/permethrin), MSMA (→ inorganic arsenic).**
   Plausibly present in landscape programs; varying carcinogenicity classifications; none
   linked to Ewing sarcoma.

## 8. What historical land-use factors exist?

Ladera Ranch sits on former Rancho Mission Viejo land — predominantly **cattle grazing** with
pockets of **dry-farmed barley, lemon/citrus orchard, and tree nurseries** (with stored
agricultural chemicals). Former California citrus/orchard land commonly carries legacy
arsenic and organochlorine residues, and **DTSC's own school-site investigations in the
immediate area repeatedly found them** — Carl Hankey (arsenic, lead), San Juan Elementary
(arsenic, chlordane, DDT), Ambuehl (DDT, toxaphene). The area's Phase I assessments **did not
test soil for these residues**, and whether the Ladera Ranch residential entitlement did is
**unknown** (evidence gate).

## 9. What water, drainage, soil, or air pathways are plausible?

- **Soil (highest plausibility):** legacy agricultural residue on former farmland, mobilizable
  as dust during 2000–2006 grading. *Testable.*
- **Recycled irrigation water:** extensive tertiary reuse on parks/slopes/schools; constituent
  data not public — a pathway to characterize, not a known hazard.
- **Drainage:** Cañada Chiquita → San Juan Creek; ambient (not drinking-water) monitoring found
  **DDE exceeding the CA Toxics Rule** in lower San Juan Creek (2003).
- **Drinking water: low plausibility** — imported, treated, no MCL violations, no local
  groundwater.
- **Air:** SR-241 corridor (traffic-related pollution) and construction-era dust.

## 10. What non-pesticide hypotheses remain viable?

- **Chance aggregation in a high-baseline-risk population.** Ewing sarcoma is ~9× more common
  in European than African ancestry; a 63.6% non-Hispanic-white community has an **elevated
  expected count**. *(Scientifically supported.)*
- **Germline genetic susceptibility** (GGAA-microsatellite/EWSR1 biology).
- **Post-hoc boundary / ascertainment artifact** (community-drawn boundary; media-amplified
  case-finding).
- **Residential-mobility exposure misclassification** (55–58% of pediatric cases move).
- **Abandoned oil/gas well proximity** — the one environmental factor with even a *suggestive*
  published Ewing association (abandoned wells; Hispanic children); six plugged/idle wells lie
  within ~6 miles.
- **Traffic-related air pollution; PM2.5** — plausible, weak/null direct Ewing evidence.

## 11. What conclusions cannot currently be reached?

The platform **cannot** confirm that a cluster exists in the epidemiological sense, establish
that any exposure occurred, attribute any illness to any cause, or rank hypotheses as if
causation were established. Hypothetical SIR scenarios (below) show the *reported* count
exceeds statistical expectation — a pattern that **warrants investigation** — but this rests
on unverified counts, a boundary drawn around the cases, uncertain residence-during-window,
and tiny numbers. **The available evidence does not yet establish causation.**

### Hypothetical SIR scenarios (Estimated; HYPOTHETICAL)

| Scenario | Observed | Rate /M/yr | Expected | SIR | 95% CI |
|---|---|---|---|---|---|
| Central (6, 0–19, 3.0/M) | 6 | 3.0 | 0.38 | 15.7 | 5.8–34.1 |
| Ancestry-adjusted (6, 4.0/M) | 6 | 4.0 | 0.51 | 11.8 | 4.3–25.6 |
| Peak-age (6, 10–19, 4.58/M) | 6 | 4.58 | 0.32 | 19.1 | 7.0–41.5 |
| Conservative count (4, 4.0/M) | 4 | 4.0 | 0.51 | 7.8 | 2.1–20.1 |
| Higher count (12, 3.0/M) | 12 | 3.0 | 0.38 | 31.3 | 16.2–54.8 |
| Leave-one-out (5, 4.0/M) | 5 | 4.0 | 0.51 | 9.8 | 3.2–22.9 |

*Person-years 0–19 ≈ 127,610 (2013–2026). All rows are model estimates on unverified counts.
Compare "conservative" vs "higher" to see how a few cases swing the SIR.*

## 12. What missing evidence would most improve the analysis?

In priority order (full ranking in `FUTURE_EVIDENCE_GATES.md`): **(1)** registry-confirmed
case counts, ages, diagnosis dates, and ancestry from the California Cancer Registry; **(2)**
individual residence histories across the etiologic window (consented, IRB); **(3)** soil
sampling on the residential footprint and common areas for arsenic/DDT/toxaphene; **(4)** the
Ladera Ranch entitlement/EIR soil-testing record and DPR PUR extract for the relevant
sections; **(5)** LARMAC/vendor full application logs and recycled-water constituent data.

---

## Strongest public-source findings (summary)

1. An official multi-agency review is underway; no agency has declared a cluster or a cause.
2. Every pesticide-specific causal claim is advocacy/attorney-sourced (grade C), not an
   agency finding; glufosinate is not classified as a carcinogen by any regulator.
3. The strongest *testable* environmental lead is **legacy agricultural soil residue** on
   former farmland — confirmed at neighboring sites, never tested on the footprint.
4. Drinking water is a low-plausibility pathway (imported, clean); recycled water is
   under-characterized.
5. Under transparent assumptions, the reported Ewing count exceeds expectation — but the
   ancestry-elevated baseline, unverified counts, and boundary/ascertainment biases mean this
   **warrants investigation, not conclusion.**

## Claims that remain unproven

Causation by any exposure · existence of a true cluster · the specific role of glufosinate or
any named chemical · the "17 pesticides" figure · that legacy soil residue is present on the
footprint · that recycled water carries any hazard.

**A formal individual-level epidemiological analysis with registry-confirmed cases would be
required to move any of these from hypothesis to finding.**
