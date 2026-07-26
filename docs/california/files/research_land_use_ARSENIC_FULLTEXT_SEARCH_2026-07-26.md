# Full-text search: does any on-file environmental document mention arsenic trioxide / cattle dipping?

**Date:** 2026-07-26. **Method:** programmatic full-text extraction (pypdf) of every page, searched
against a fixed term list (arsenic/arsenical/arsenate/arsenite/trioxide, cattle dip/dipping vat/sheep
dip, lead-arsenate, organochlorine/DDT/DDE/DDD/toxaphene/chlordane, tick eradication/Texas fever/
quarantine, soil sampling/testing, "recognized environmental condition," EIR 555), plus a
whitespace-stripped safeguard pass (to catch OCR/extraction artifacts that insert stray spaces
mid-word). Every hit was opened and read in full context before being counted — see the false-positive
note below. This supersedes the "held offline, unread" note previously attached to these files; they
are excluded from the GitHub push only for file-size reasons, not access. Held to the same standard as
the rest of this project: no claim without a source; absence of a finding is itself logged.

## Documents searched this pass

| Document | Pages | Result |
|---|---|---|
| `RanchPlan_AffordableHousing_FinalPEIR_SCH2015051062_2016.pdf` | 1,737 | **Zero** hits for arsenic (any form/spacing), cattle dip, tick eradication, quarantine, lead-arsenate, organochlorines. 2 hits for "trioxide" — both **false positives** ("sulfur trioxide," an air-quality term; see below). Incorporates by reference the Phase I ESA framework from **FEIR 589** and references the TTM 17325 pistol-range remediation already known to this project. |
| `EIR589_AppendixI_PhaseI_ESA_PA1-9.pdf` | 218 | **One genuine "arsenic" hit** (page 119) — see full analysis below. Zero hits for cattle dip, tick eradication, quarantine, lead-arsenate, organochlorines, "EIR 555." |
| `Ladera_Planned_Community_Program_Text_1995_rev2003.pdf` | 136 | **NOT SEARCHABLE** — scanned image PDF, zero extractable text on every page (confirmed: 0 of 136 pages yielded any text via pypdf). No OCR toolchain was available in this session (no tesseract/pytesseract/pdftoppm). **This is a disclosed gap, not a null result** — treat as unsearched. Also note: the filename indicates this is very likely the Planned-Community **zoning** ordinance/program text, a different document type from an Environmental Impact Report, and would not be expected to contain soil-testing data even once read. |

## The one genuine "arsenic" hit — full characterization
Page 119 of the FEIR 589 Appendix I, under **Planning Area 5 ("Trampas/Oglebay Norton")** — a
**silica-sand mine and glass-sand processing plant**, a different parcel from, and unrelated to, the
Ladera Ranch residential footprint. Context: a 1999 Phase II investigation (URS Greiner Woodward
Clyde) of a mining-tailings retention dam, examining legacy industrial chemicals from **sand-washing
operations** (sulfuric acid, hydrochloric acid, hydrofluoric acid, sodium hydroxide, tallow diamine —
none agricultural/pesticide-related). Findings: soil trace metals were below EPA residential screening
levels; **groundwater** arsenic was reported above the drinking-water MCL. Method: standard "Title 22
metals" panel — **reports total arsenic, not speciated arsenic trioxide.**
**This is a real, accurate finding — not a false positive — but it is not evidence of soil arsenic
testing, not connected to cattle dipping, and not within the Ladera Ranch footprint.** It changes
nothing about the core conclusion.

## The false positive, precisely
The 2016 PEIR's 2 hits for "trioxide" were **"sulfur trioxide" (SO₃)**, an unrelated air-emissions
compound appearing in a glossary and an air-quality discussion. A keyword match alone would have
wrongly suggested arsenic trioxide was discussed; reading full context showed it was not. This is why
every hit in this project is read in context before being counted, never reported as a raw match count.

## Updated bottom line
No document we can currently read — across every environmental review examined to date, including
this pass's two newly-searched large documents — contains any testing for arsenic trioxide, or any
mention of the historical cattle-dipping program, anywhere in or immediately adjacent to the Ladera
Ranch footprint. The one real arsenic mention found this pass is unrelated (different site, different
media, different source, non-speciated method). See `10_ladera_ranch.md` / `20_bellcanyon_coto.md` for
the previously-established site-by-site table this supplements.

## Gaps this pass narrows, and what's still open
- **Narrowed:** the 2016 PEIR and the FEIR 589 Phase I ESA appendix (adjacent Ranch Plan lands) are now
  confirmed read, not merely "on file."
- **Still open:** the Ladera Ranch master entitlement EIR itself (referenced in county records as "EIR
  555," ~1997) has still not been located as a document we hold — the 1995 "Program Text" on file is
  very likely the zoning ordinance, not the EIR, and in any case cannot currently be searched (scanned,
  no OCR). Case 94IC011 remains a pre-digital county file, contents unknown. TTM 17325 lab appendices
  (BulkFile1/2) remain unconfirmed for arsenic. Physical/non-digitized archives (Sherman Library, OC
  Archives, CA State Archives, Starr Ranch/Audubon) remain un-visited.
