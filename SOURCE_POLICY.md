# SOURCE_POLICY.md

Defines what counts as an acceptable source, how sources are graded, and how conflicting
or secondary sources are handled. This policy governs every record in the platform.

## 1. Purpose

Environmental-health cluster investigation is unusually vulnerable to low-quality
evidence: viral news, advocacy framing, unverified case counts, and emotionally charged
claims circulate faster than official findings. This policy exists so that every claim in
the platform carries a permanent, visible statement of how trustworthy its source is, and
so that nothing is ever silently upgraded.

## 2. Reliability hierarchy

| Grade | Definition | Examples for this project |
|-------|-----------|---------------------------|
| **A1** | Official machine-readable government dataset; peer-reviewed primary research; official registry publication; official agency report. | California Pesticide Use Reporting (PUR) data files; SEER incidence tables; a peer-reviewed epidemiology paper; a California Cancer Registry report. |
| **A2** | Official government webpage; regulatory filing; official meeting document; official GIS service. | OC Health Care Agency statement page; DTSC EnviroStor site record; SMWD Consumer Confidence Report; a Board of Supervisors agenda item. |
| **B1** | University / research-institution report; systematic review; nonprofit technical report with transparent methodology. | A UCI cancer center technical summary; a Cochrane-style review; an EWG report *with* documented methodology. |
| **B2** | Reputable news outlet quoting **named** sources or documents. | OC Register / LA Times / Voice of OC reporting that quotes named officials or cites obtained records. |
| **C** | Advocacy materials; law-firm summaries; community petitions; social-media statements; unverified case counts; anonymous claims. | Children's Health Defense; plaintiff law-firm intake pages; Change.org petitions; Facebook group posts; hyperpartisan commentary sites. |
| **D** | Speculation; unsourced reposts; unsupported online claims. | Aggregator reposts with no attribution; comment-section assertions. |

## 3. Core rules

1. **Never discard a low-grade source.** Store it at its correct grade. Low-grade sources
   are legitimate *leads*; they are never *facts*.
2. **Never silently promote.** A claim first seen at grade C stays C until an independent
   A/B source corroborates it, at which point a **new** higher-grade record is created and
   the corroboration is documented — the C record is not edited into an A record.
3. **Grade the source, not the conclusion you want.** A well-sourced news article that
   undercuts the pesticide hypothesis gets the same B2 it would get if it supported it.
4. **Advocacy and partisan outlets are C by default**, regardless of whether their factual
   claims later prove correct. This includes outlets on all sides. When such an outlet
   reports a checkable fact (e.g., "the U.S. Attorney wrote to EPA"), we do not treat the
   outlet as the source — we locate and grade the underlying document.
5. **Prefer the event date over the article publication date** when building timelines.
6. **Check whether a source recycles an old claim as new**, and check archived versions for
   changed wording.

## 4. Handling secondary sources

- A secondary source that *quotes a named primary document* is graded on the strength of
  the primary document it quotes, but flagged `is_primary = false`. We then attempt to
  obtain the primary document and create a separate A/A2 record.
- A secondary source that quotes *anonymous* claims or "residents say" is C.
- Snippet-only knowledge (search-result previews) is never sufficient; the underlying page
  must be retrieved when accessible.

## 5. Conflicting sources

When two sources conflict (e.g., "6 cases" vs "about a dozen"):
1. Record **both** values, each with its own source and grade.
2. Prefer the higher-grade and more recent source for display, but never delete the other.
3. Document the discrepancy explicitly in the relevant registry and in
   `CLAIMS_AND_LIMITATIONS.md`. Case-count discrepancy is itself a finding about data
   quality, not noise to be smoothed away.

## 6. Provenance requirement

Every substantive record links to one or more `source_id`s. Every inferred record also
records inference method, input sources, assumptions, confidence, and creation date. See
`DATA_DICTIONARY.md`.

## 7. Archiving

When lawful, save a local copy (PDF/HTML) of each substantive public source, record its
URL, retrieval date, and a checksum, and note if the live page later changes or disappears.
Respect robots.txt, rate limits, terms of service, paywalls, and authentication. Never
bypass access controls or CAPTCHAs.
