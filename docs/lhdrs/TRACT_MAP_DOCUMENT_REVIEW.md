# Recorded Tract Map Document Review

Generated from the 123 official County recorded-map PDFs archived by
`scripts/lhdrs_mission4_fetch.py`. Sheet 1 of every map was rendered at 150 DPI and OCRed
with macOS Vision; selected master and nested sheets were visually inspected.

| Metric | Count |
|---|---:|
| Official PDFs archived | 123 |
| Title sheets with normalized parent-tract wording | 52 |
| OCR parent numbers corrected against intersecting tract IDs | 12 |
| Geometric crosswalk rows upgraded with title-sheet evidence | 53 |

## Named Parties

| Title-sheet owner or interest holder | Maps mentioning party |
|---|---:|
| DMB Ladera, L.L.C. | 96 |
| Rancho Mission Viejo, L.L.C. | 61 |
| Standard Pacific Corp. | 11 |
| Warmington Homes | 8 |
| Shea Homes | 8 |
| William Lyon Homes, Inc. | 8 |
| Richmond American Homes of California, Inc. | 6 |
| John Laing Homes | 3 |
| Brookfield Wyeth, Inc. | 2 |
| Brookfield Sarasota, Inc. | 2 |
| Ladera Development Company | 2 |
| Taylor Woodrow Homes, Inc. | 1 |

These are documentary parties, not automatically builders. A deed beneficiary, owner,
or manager may differ from the homebuilder or sales brand.

## Parent Examples

| Child tract | Normalized parent | OCR context | Named parties |
|---|---|---|---|
| 15617 | LH-TRACT-15615 | LOT 2 TRACT NO. 15615 |  |
| 15620 | LH-TRACT-15615 | LOT 5 OF TRACT NO. 15615 | DMB Ladera, L.L.C.;Rancho Mission Viejo, L.L.C.;Warmington Homes |
| 15623 | LH-TRACT-15615 | LOT 8 OF TRACT NO. 15615 | Rancho Mission Viejo, L.L.C.;Warmington Homes |
| 15625 | LH-TRACT-15615 | LOT 10 OF TRACT NO. 15615 | DMB Ladera, L.L.C.;Brookfield Wyeth, Inc. |
| 15626 | LH-TRACT-15615 | LOT 11 OF TRACT NO. 15615 | DMB Ladera, L.L.C.;Rancho Mission Viejo, L.L.C.;Taylor Woodrow Homes, Inc. |
| 15627 | LH-TRACT-15615 | LOT 12 OF TRACT NO. 15615 | DMB Ladera, L.L.C.;Rancho Mission Viejo, L.L.C.;William Lyon Homes, Inc. |
| 15629 | LH-TRACT-15615 | LOT 14 OF TRACT NO. 15615 | DMB Ladera, L.L.C.;Rancho Mission Viejo, L.L.C.;Brookfield Sarasota, Inc. |
| 15631 | LH-TRACT-15615 | LOT 16 OF TRACT NO. 15615 | DMB Ladera, L.L.C.;Brookfield Sarasota, Inc. |
| 15632 | LH-TRACT-15615 | LOT 17 OF TRACT NO. 15615 | DMB Ladera, L.L.C.;Rancho Mission Viejo, L.L.C.;William Lyon Homes, Inc. |
| 15886 | LH-TRACT-15884 | LOTS 7, N, O AND P OF TRACT NO. 15884 | DMB Ladera, L.L.C.;Ladera Development Company |
| 15887 | LH-TRACT-15884 | LOT & OF TRACT NO. 16884 | DMB Ladera, L.L.C.;Rancho Mission Viejo, L.L.C. |
| 15888 | LH-TRACT-15884 | LOT 5 OF TRACT NO. 15884 | Rancho Mission Viejo, L.L.C. |
| 15901 | LH-TRACT-15813 | LOT 2 OF TRACT NO. 15813 | DMB Ladera, L.L.C. |
| 15902 | LH-TRACT-15813 | LOT 1 OF TRACT NO. 15813 | DMB Ladera, L.L.C. |
| 15907 | LH-TRACT-15813 | LOT IN THE UNINCORPORATED TERRITORY OF THE COUNTY OF ORANGE, STATE OF CALIFORNIA TIME 10:45 AM DATE AUGUST 25,200 _FEE $ | DMB Ladera, L.L.C. |
| 15908 | LH-TRACT-15813 | LOT 9 OF TRACT NO. 15813 | DMB Ladera, L.L.C.;Rancho Mission Viejo, L.L.C. |
| 15909 | LH-TRACT-15813 | LOT 10 OF TRACT NO. 15813 | DMB Ladera, L.L.C.;Rancho Mission Viejo, L.L.C. |
| 15911 | LH-TRACT-15813 | LOTS 12, "AH", "AX" AND "AY" OF TRACT NO. 15813 | DMB Ladera, L.L.C. |
| 15912 | LH-TRACT-15813 | LOT 11 OF TRACT NO. 15813 | DMB Ladera, L.L.C. |
| 15914 | LH-TRACT-15827 | LOT 12 OF TRACT NO. 15827 | Richmond American Homes of California, Inc. |
| 15915 | LH-TRACT-15827 | LOT 2 OF TRACT NO. 15827 | Richmond American Homes of California, Inc. |
| 16104 | LH-TRACT-16155 | LOT 6 OF TRACT NO. 18155 | DMB Ladera, L.L.C. |
| 16114 | LH-TRACT-16025 | LOT 3 OF TRACT NO. 16025 | DMB Ladera, L.L.C.;Rancho Mission Viejo, L.L.C. |
| 16116 | LH-TRACT-16025 | LOT B AND LETTERED LOTS L, "M, "N', "O", "P AND STATE OF CALIFORNIA DATE: MAY 16, 2002 22 THROUGH 29, INCLUSIVE, OF MISC | DMB Ladera, L.L.C.;Rancho Mission Viejo, L.L.C. |
| 16118 | LH-TRACT-16156 | LOT 3, TRACT NO. 16156 | DMB Ladera, L.L.C.;William Lyon Homes, Inc. |
| 16126 | LH-TRACT-16156 | LOTS TRACT NO. 18128 | LOTS 2, C AND D OF TRACT NO. 16165 | Rancho Mission Viejo, L.L.C.;Warmington Homes |
| 16236 | LH-TRACT-16234 | LOT 3 OF TRACT NO. 16234 | DMB Ladera, L.L.C. |
| 16237 | LH-TRACT-16234 | LOT 2 OF TRACT NO. 16234 | DMB Ladera, L.L.C.;Shea Homes |
| 16240 | LH-TRACT-16234 | LOT 6 OF TRACT NO. 16234 | Rancho Mission Viejo, L.L.C. |
| 16243 | LH-TRACT-16235 | LOT 1 OF TRACT NO. 16235 |  |

## Review Boundary

OCR output is an index, not a substitute for the image. Raw OCR candidates and every
numeric correction are retained in `tract_title_sheet_index.csv`. Title-sheet parent/child
language can establish legal map lineage, but it does not establish construction,
habitability, sale, or occupancy dates.
