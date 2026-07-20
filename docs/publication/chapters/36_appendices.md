# Appendices

---

## Appendix A — Reproducing this investigation

Every quantitative claim can be regenerated from the repository.

| Script | Produces |
|---|---|
| `pipelines/python/extract_topo_water.py` | The 41-body surface-water layer from the 1968 sheet |
| `pipelines/python/premise_homes_on_water.py` | The water-proximity test and its null |
| `pipelines/python/premise_water_and_homes.py` | Terrain and drainage analysis (see the exclusion in Ch. 22) |
| `pipelines/python/detect_water_1930s.py` | **The abandoned detector.** Retained with its failure documented in the docstring so it is not naively retried |
| `pipelines/python/build_geojson.py` | All published GIS layers |
| `scripts/build_publication.py` | This publication from the chapter markdown |
| `scripts/build_backmatter.py` | Bibliography, image credits, evidence-category chapters, source library, version history — all from the data files |
| `scripts/prepare_pub_assets.py` | Figure derivatives and the image archive |
| `scripts/build_pdf.sh` | Print-quality PDF |
| `tests/test_data_integrity.py` | Privacy and provenance checks (7 tests) |

## Appendix B — The integrity tests

These run against the data, not the prose, and they encode the project's non-negotiable rules:

- `test_health_events_have_no_address_or_coordinate` — no health record may carry a location
- `test_health_events_aggregate_columns_only` — aggregate level only
- `test_every_source_has_valid_grade` — no ungraded source
- `test_records_reference_existing_sources` — no claim without a registered source
- `test_geojson_layers_valid` — published geometry parses
- `test_application_events_have_valid_evidence_class` — no unclassified assertion
- `test_no_bare_likely_application_events` — no inferred record published without a confidence marker

## Appendix C — Common misreadings, corrected in advance

| Misreading | What the report actually says |
|---|---|
| "They found a dipping vat at Ladera Ranch" | **No vat has been found anywhere.** The nearest documented 1908 dipping was at Capistrano, 3.4 miles away |
| "Trabuco Canyon dipping proves it happened here" | Trabuco Canyon is **8.4 miles away** and outside Zone B. It shares a drainage name, not a location |
| "The county never studied the land" | A Phase I assessment **was** performed. Its historical review began in **1952**. That is a window gap, not a failure |
| "Arsenic was found in Ladera Ranch soil" | **No soil measurement from the residential footprint exists.** Arsenic findings are from *school* sites on former agricultural land nearby |
| "The homes were built on the old cattle grounds" | Tested and **not supported** — 0.97×, p = 0.51 |
| "No contaminants were found at Oso Grande" | Correct, and it means **none were looked for in soil**. The site was cleared documentarily |
| "This links cattle dipping to the cancer cases" | **Nothing in this report bears on the illnesses.** No causal claim is made or supported |

## Appendix D — A note on structure

**The evidence matrix** is rendered as a searchable, filterable section following the final
chapter, generated directly from `EVIDENCE_MATRIX.csv`. Chapter 24 introduces it; Chapters 25–28
group the same claims by classification.

**Chapters 16–19 are deliberately layered rather than sequential.** Ch. 16 is the audit overview
and method; Ch. 17 examines the 1952 source window and the standard governing it; Ch. 18 records
what the review *did* cover; Ch. 19 records what does not appear in it. Reading 16 alone gives the
finding. Reading 17–19 gives the basis for it.

**Chapters 29 and 30 split archival from physical work**, because the sequencing between them is
itself a recommendation: archives first, ground second. This project learned that the hard way —
see Ch. 8 §8.8.

## Appendix E — Contact and contribution

See the **invitation at the front of this report**.

Materials welcome: documents, photographs, maps, surveys, ranch records, recollections, and
corrections.

**Not accepted:** medical information about any individual, residential addresses, or anything
identifying a specific child or household. This is a permanent constraint, not a preference.
