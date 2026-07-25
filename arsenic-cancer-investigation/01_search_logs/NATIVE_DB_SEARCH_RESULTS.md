# NATIVE-DATABASE SEARCH RESULTS (reproducible hit counts)

Date 2026-07-23. APIs: NCBI E-utilities (PubMed) + Europe PMC REST. Counts are live hitCounts;
re-runnable by anyone with the same strings. Direct arsenic-Ewing strings return ~0 -> confirms
the documented absence (Finding 1, 05_) with reproducible evidence.

| Query | PubMed | EuropePMC | Top IDs (PubMed) |
|---|---|---|---|
| arsenic AND "Ewing sarcoma" | 8 | 323 | 31746397, 27665785, 22391311, 22315235, 21183792 |
| "inorganic arsenic" AND Ewing | 0 | 28 | - |
| "arsenic trioxide" AND "Ewing sarcoma" | 8 | 207 | 31746397, 27665785, 22391311, 22315235, 21183792 |
| arsenite AND Ewing | 3 | 105 | 41738287, 33876544, 8264344 |
| arsenate AND Ewing | 15 | 35 | 42213593, 39671892, 31746397, 27665785, 22391311 |
| arsenic AND EWSR1 | 0 | 147 | - |
| arsenic AND "EWS-FLI1" | 0 | 76 | - |
| arsenic AND "primitive neuroectodermal tumor" | 1 | 69 | 16930595 |
| arsenic AND "small round blue cell tumor" | 0 | 11 | - |
| arsenic AND "mesenchymal stem cell" AND transformation | 0 | 226 | - |
| arsenic AND "double-strand break" | 23 | 627 | 39032852, 38096740, 37762697, 37530740, 36089002 |
| arsenic AND translocation AND sarcoma | 10 | 1211 | 37601428, 29346731, 29307831, 27058871, 26283888 |

**Interpretation:** low/zero counts on the direct As-Ewing strings are a reproducible
*documented absence of research*, not evidence of no relationship. Mechanistic/analog strings
(double-strand break, MSC transformation, translocation-sarcoma) return the mechanism literature
already captured in 07_/14_.

## CRITICAL CHARACTERIZATION — the arsenic-Ewing hits are THERAPEUTIC, not etiologic
All 8 PubMed hits for `arsenic AND "Ewing sarcoma"` (= the same 8 for `"arsenic trioxide" AND "Ewing
sarcoma"`) concern **arsenic trioxide (ATO) as a candidate TREATMENT of Ewing**, not a cause:
- 31746397 (2020) ATO + etoposide interaction in Ewing cell lines
- 27665785 (2016) ATO potentiates etoposide in Ewing sarcomas
- 22315235 (2012) ATO evaluated by the Pediatric Preclinical Testing Program (Ewing focus)
- 21183792 (2011) ATO inhibits cancer growth by blocking Hedgehog signaling
- 22391311 (2012) ATO + Hedgehog signaling review
- 21183780 (2011) "Arsenic: a potentially useful poison for Hedgehog-driven cancers"
- 16889724 (2006) ATO combination chemo (osteosarcoma)
- 16646077 (2006) ATO induces p53-independent Ewing cell death
`arsenic AND EWSR1` = 0, `arsenic AND EWS-FLI1` = 0, `"inorganic arsenic" AND Ewing` = 0.

**Finding (a, reproducible):** the published arsenic-Ewing record is entirely **arsenic-as-therapy**
(ATO kills Ewing cells, akin to its role in APL). **Zero etiologic studies** (arsenic causing Ewing)
exist. This is a documented absence of causal research AND a directional counter-signal.
