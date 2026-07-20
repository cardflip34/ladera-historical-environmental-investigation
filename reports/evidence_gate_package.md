# LEHRP — Final-Stage Evidence-Gate Package

**Date:** 2026-07-18. Produced only after the public-source investigation identified exact
gaps. Rankings use: **SI** Scientific importance · **AV** Availability · **CO** Cost · **LD**
Legal difficulty · **TS** Time sensitivity · **DR** Destruction risk · **CC** Ability to
change conclusions · **PI** Privacy impact. (H/M/L)

## Ranked evidence gates

| # | Evidence | SI | AV | CO | LD | TS | DR | CC | PI |
|---|----------|----|----|----|----|----|----|----|----|
| G01 | Registry-confirmed case counts/dates/ages/ancestry (CCR) | H | M | L | M | H | L | **H** | M |
| G03 | Individual residence histories (consented, IRB) | H | L | M | H | H | M | **H** | H |
| G10 | Soil sampling (arsenic, DDT/toxaphene) on footprint/common areas | H | M | M | M | M | M | **H** | L |
| G13/G14 | Ladera Ranch entitlement/EIR soil-testing record & CEQA appendices | H | M | L | L | M | M | H | L |
| G06 | DPR PUR extract for relevant sections/years | M | H | L | L | M | L | M | L |
| G04 | LARMAC/sub-HOA landscape application logs | M | L | L | M | H | **H** | M | L |
| G05 | Landscape/pest-control vendor records (O'Connell) | M | L | L | M | H | **H** | M | L |
| G11 | Recycled-water constituent monitoring (SMWD/RWQCB) | M | M | L | L | L | L | M | L |
| G02 | Medical/pathology confirmation of diagnoses | H | L | M | H | M | L | H | H |
| G07 | OC Ag Commissioner restricted-materials permits/use reports | M | M | L | L | M | M | M | L |
| G08/G09 | Capistrano USD Healthy Schools Act data & facilities contracts | M | M | L | L | M | M | M | L |
| G16 | OCHCA/UCI/CCR review methods & results | H | M | L | L | H | L | H | L |
| G17 | U.S. Attorney → EPA correspondence & EPA response | M | M | L | L | H | L | M | L |

**Top priorities** (high scientific importance × high ability-to-change-conclusions):
G01, G03, G10, and G16. Two gates carry **high destruction risk** (G04, G05 — application
logs can be discarded), raising their time-sensitivity independent of their scientific rank.

---

## Drafted records requests (top 5)

> These are narrow, gap-specific requests. They are drafts for authorized human review — the
> platform does not send them. Any request touching individual health data requires IRB
> review and appropriate legal channels (see `ETHICS_AND_PRIVACY.md`).

### 1. California Cancer Registry / CDPH — aggregate small-area case data (G01, G16)
*Amended 2026-07-18 to add birth year — see `research/land_use/exposure_timing_analysis.md`.*
> Requesting, under an authorized epidemiological data request, an aggregate small-area
> analysis of Ewing sarcoma and other pediatric sarcoma incidence for the Ladera Ranch area
> (Census tracts comprising CDP 0639114) and comparison South Orange County communities, for
> diagnosis years 2005–2026: observed counts by 5-year age band, sex, and race/ethnicity;
> **birth year (or age at diagnosis together with diagnosis year) for each confirmed case**;
> and, if lawfully releasable, **duration and period of residence**. Also requesting expected
> counts using standard SEER/CCR reference rates; SIR with exact Poisson 95% CI; and the
> registry's own assessment of case-definition and boundary sensitivity. We ask that results be
> released at the most granular level consistent with CDPH's small-numbers suppression policy,
> and that the analysis note any cases whose residence at diagnosis differs from residence
> during the etiologically relevant window.
>
> **Why birth year specifically.** The two leading versions of the environmental hypothesis
> make *opposite* predictions about birth cohorts: a one-time construction-era dust exposure
> (1999–2006) requires cases born on or before ~2007, whereas persistent soil residue —
> arsenic does not degrade — predicts cases across all birth cohorts. Birth year alone would
> discriminate between them. No other requested field does this.

### 2. Orange County Agricultural Commissioner — CPRA request (G07, G06)
> Under the California Public Records Act, requesting: (a) all Pesticide Use Reports submitted
> for Orange County sections overlapping ZIP 92694 for 2005–2026 (or direction to the DPR PUR
> extract if more complete); (b) restricted-materials permits and notices of intent for those
> sections; (c) any enforcement or complaint records concerning landscape or structural
> pesticide application in Ladera Ranch. Electronic/CSV format preferred.

### 3. LARMAC (voluntary) — common-area application history (G04, G05)
> Respectfully requesting, on a voluntary basis given the community concern, LARMAC's and its
> contracted vendors' (including O'Connell Landscape) records of pesticide/herbicide
> applications to Ladera Ranch common areas for 2005–2026: product names, EPA registration
> numbers, active ingredients, application dates, treated locations (village/SBA zone), rates,
> and applicator licenses; the landscape maintenance contract(s) and IPM policy; and the
> posted application notices. Because such logs are at risk of routine disposal, we ask that
> existing records be preserved.

### 4. Santa Margarita Water District — recycled-water quality (G11)
> Under CPRA, requesting Title 22 recycled-water monitoring data for the Chiquita Water
> Reclamation Plant and the recycled-water distribution system serving Ladera Ranch, 2005–2026:
> constituent-level results (nitrogen species, TDS, metals, disinfection byproducts, and any
> organic-compound scans), the governing Water Recycling Requirements order, and any exceedance
> or violation records. This complements the public drinking-water CCRs, which do not cover the
> recycled system.

### 4b. Capistrano Unified School District — pesticide product list & school application records (G08/G09)
*Refined 2026-07-18 after retrieving the district's IPM Plan.* The district's IPM Plan was
obtained and confirms it covers **structural and landscape pests** and that CUSD "may hire a
contracted pest control company on an as needed basis" — but the plan **names no products and
no contractor**. The separate "Annual Pesticide Notification and Product List" is publicly
linked from the district's site but the linked document **requires a Google sign-in**, so it is
not publicly readable. Hence a narrow, specific request:
> Under the California Public Records Act, requesting: (1) the **Annual Pesticide Notification
> and Product List** for school years 2013–14 through 2025–26, in an openly accessible format;
> (2) **Healthy Schools Act annual pesticide use reports** submitted to DPR for the same years
> for school sites serving Ladera Ranch; (3) the identity of any **contracted pest control
> business** and the associated contracts; and (4) **site-specific application records and the
> 72-hour advance notices** issued for those school sites.

### 5. Orange County Development Services — Ladera Ranch entitlement soils record (G13/G14)
> Under CPRA, requesting the environmental and geotechnical record for the Ladera Ranch Planned
> Community entitlement (referenced as EIR 555) and associated grading permits: any Phase I/II
> Environmental Site Assessment, soils or agricultural-residue testing (arsenic, lead,
> organochlorine pesticides), imported-fill documentation, and the SCH number for the program
> EIR. Goal: determine whether the residential footprint was ever tested for legacy
> agricultural soil residues before development.

---

## What must NOT be requested yet

Per the online-first rule and ethics policy, the platform does **not** at this stage seek
individual medical records, patient addresses, family interviews, or anything requiring
family consent or a subpoena. Those (G02, G03, G12, G15) belong to a later, IRB-governed,
consented phase — and only after the aggregate registry analysis (G01) establishes whether a
formal individual-level study is warranted.
