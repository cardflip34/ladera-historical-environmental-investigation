# Mission 6 local appendices

**Generated:** 2026-07-27 by `scripts/lhdrs_mission6_appendices.py` (reproducible; re-run to regenerate).
These are the six attachments required before any Mission 6 records request may be submitted.

**Nothing here has been submitted to any agency.** These are working attachments only.

| Appendix | File | Rows |
|---|---|---|
| A — canonical tract list + aliases | `appendix_A_canonical_tracts.csv` | 124 (123 canonical + 1 excluded/conflicted) |
| B — address crosswalk | `appendix_B_address_crosswalk.csv` | 6368 (from 6446 points) |
| C — project AOI | `appendix_C_aoi.geojson` + `_summary.json` | 1 feature(s) |
| D — street-to-tract crosswalk | `appendix_D_street_tract_crosswalk.csv` | 288 |
| E — known identifiers | `appendix_E_known_identifiers.csv` | 182 |
| F — party name variants | `appendix_F_party_name_variants.csv` | 91 |

## Disclosed limitations — read before sending anything

1. **No APN data exists in this repository.** Appendix B therefore has an empty `apn` column with
   `apnStatus = NOT_IN_REPOSITORY`. APNs must be obtained from the County; they must **not** be
   inferred, derived, or back-filled from address or tract data. The priority-1 request asks the
   County to supply APN linkage.
2. **TR 17588 is excluded from the canonical Ladera set** (decision: `exclude`), and is
   carried as an explicit conflict row. The 2024 Board-certified road index labels it Ladera Ranch;
   the live FeatureServer labels the same feature Rancho Mission Viejo. Both preserved.
3. **Multi-date tracts are preserved as separate rows, never collapsed.** Detected from the road
   index: ['15615', '16116', '16121']. A tract with several road-segment acceptance dates has no
   single "completion date" without a documented rule.
4. **Appendix C reuses the existing repository AOI** (Census CDP boundary). It was not redrawn. A
   CDP is an administrative/statistical boundary, not a legal subdivision or service-area boundary.
5. **Road acceptance, map recordation, sales dates, year-built values, school/facility openings, and
   aerial observations are NOT certificates of occupancy** and must never be substituted for one.

## Gate status — unchanged

Permit/occupancy: not satisfied · Address lifecycle: not satisfied ·
Construction-interval aerial: not satisfied · **Proximity analysis: BLOCKED**

Generating these appendices does not satisfy any gate. It unblocks *requesting* the records that
could.
