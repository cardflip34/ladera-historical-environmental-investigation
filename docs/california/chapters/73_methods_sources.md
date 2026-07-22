# 73 · Methods and Sources

> The single methods chapter for The California Report. Every rule that governs the other chapters
> is stated here once, so the area and history chapters can carry a one-line footer instead of
> repeating boilerplate. This chapter is hypothesis-neutral by design: the grading and
> counter-evidence rules exist to keep any single hypothesis from being silently favored.

---

## 73.1 Source grading (A1–D)

Every record carries **exactly one** grade. A lower grade is never silently promoted to a higher
one.

| Grade | Definition |
|---|---|
| **A1** | Official machine-readable government dataset; peer-reviewed primary research; official registry publication; official agency report. |
| **A2** | Official government webpage; regulatory filing; official meeting document; official GIS service. |
| **B1** | University / research-institution report; systematic review; nonprofit technical report with transparent methodology. |
| **B2** | Reputable news outlet quoting **named** sources or documents; public statements from identifiable stakeholders. |
| **C** | Advocacy materials; law-firm summaries; community petitions; social-media statements; unverified case counts; anonymous claims. |
| **D** | Speculation; unsourced reposts; unsupported online claims. |

Worked examples from this report: the USDA circulars and the 1912 Johnson proclamation are **A1**;
the DTSC 2008 Interim Guidance and NSW dip-site register are **A2**; the statewide screening layer
and the Pulling 1965 corroboration are **B1**; the 1908 *Los Angeles Herald* dipping items are
**B2** (press quoting a named state officer).

## 73.2 Provenance and the source_id rule

No map object, database row, chemical assertion, case report, chart, or finding exists without a
`source_id` linking to the source registry. Every **inferred** record additionally records:
inference method, input sources, assumptions, confidence, and date created. OCR-corrected spellings
(e.g. "Joplln" → Joplin) are flagged as this project's readings, not the source's text.

## 73.3 The counter-evidence rule

Every finding of substance carries an explicit **counter-evidence and limits** note. A finding is
not allowed to stand on supporting evidence alone. Two absence-vs-proof cautions apply throughout:

- **Absence of record ≠ absence of fact.** "No California dip inventory located" means no located
  record — not proof none exists (a county agricultural-commissioner or historical-society file
  could hold one).
- **County-level ≠ site-level.** Every primary source in this report names *counties, districts,
  and ranches* — never a vat coordinate. The gap between "the program reached this county" and "a
  vat stood at this parcel" is never bridged by documentary evidence in the located record.

## 73.4 Confidence display and badges

Inferred or "likely" data is never displayed as an actual measurement. Every claim shows its
confidence. Language is always disciplined to distinguish: **Verified fact · Credible report ·
Official statement · Scientific finding · Public allegation · Unverified case report · Model-based
estimate · Inference · Hypothesis · Missing evidence.** Model figures (chapter 72) are labelled
**MODEL ESTIMATE** and carry the "could be off by ~10×" caveat wherever they appear. Confidence
badges in the platform: Verified Official · Primary Scientific · Official Public Record · Credible
Secondary · Public Allegation · Model Estimate · Unknown.

## 73.5 Time scope

Land-use and program history reach as far back as reliable public records allow (the tick program
is 1907–1912 in Orange County). The health/investigation window is primary **Jan 2005–present**,
extended **Jan 2000–present**. Every dataset records: publication date, observation/coverage
period, retrieval date, temporal precision, and whether the record is current / historical /
inferred / archived.

## 73.6 The source registry

The full graded source list — **109 rows** — is in `research/source_registry/sources.csv`, one row
per source with: id, title, publisher, author, url, publication date, retrieval date, source type,
geographic and time coverage, official/primary/peer-reviewed flags, data format, reliability grade,
known limitations, and notes. Key IDs used across chapters 70–72: **S-USDA-C174** and
**S-USDA-C183** (USDA BAI circulars, A1); the **1912 Johnson proclamation** (California State
Library scan, A1/A2); the **State Veterinarian Biennial Reports** (A1/A2); **S-NSW-DIP** (A2),
**S-UF-VATS** (B2/A1), **S-ITRC-CDV** (B1) for the jurisdiction comparison; **S-STATEWIDE** (B1)
for the eleven-community screening layer; and the CDNC press items (B2).

## 73.7 Disclaimer

> This platform is an independent research and data-organization project. It does not provide
> medical advice and does not establish that any pesticide, property, organization, employer,
> school, water provider, government agency, or other party caused any illness. Publicly reported
> health events may not have been independently medically verified. Geographic and temporal overlap
> does not establish exposure or causation. Formal conclusions require authorized epidemiological
> analysis, verified medical information, exposure assessment, toxicological review, and independent
> scientific evaluation.

*This is the standard disclaimer for The California Report. It appears once here; other chapters
carry a one-line footer pointing to it.*
