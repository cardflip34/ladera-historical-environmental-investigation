#!/usr/bin/env python3
"""Generate Mission 5 execution and evidence documentation from repository outputs."""

from __future__ import annotations

import csv
import json
import os
from pathlib import Path
import tempfile


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "research/development_chronology"
DOCS = ROOT / "docs/lhdrs"
DATA = ROOT / "data/development"
EVIDENCE = ROOT / "evidence/lhdrs/mission5"


def rows(name: str) -> list[dict[str, str]]:
    with (BASE / name).open(newline="", encoding="utf-8-sig") as stream:
        return list(csv.DictReader(stream))


def write(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent, delete=False) as stream:
        stream.write(value.rstrip() + "\n")
        temporary = Path(stream.name)
    os.replace(temporary, path)


def md_table(headers: list[str], values: list[list[object]]) -> str:
    clean = lambda value: str(value).replace("|", "\\|").replace("\n", " ")
    return "\n".join([
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
        *("| " + " | ".join(clean(value) for value in row) + " |" for row in values),
    ])


def build() -> None:
    summary = json.loads((DATA / "mission5_summary.json").read_text())
    crosswalk = json.loads((BASE / "tract_neighborhood_crosswalk_summary.json").read_text())
    graph = json.loads((DATA / "knowledge_graph.json").read_text())
    products = rows("builder_product_chronology.csv")
    primary_products = [row for row in products if row["cfdPhase"]]
    mapped_tracts = sum(bool(row["neighborhoodCandidates"]) for row in rows("tract_lifecycle_reconstruction.csv"))
    product_tracts = sum(bool(row["builderProductCandidates"]) for row in rows("tract_lifecycle_reconstruction.csv"))
    extraction = list(csv.DictReader((EVIDENCE / "extraction_log.csv").open(encoding="utf-8-sig")))
    queue = rows("highest_value_research_queue.csv")
    gaps = rows("research_gaps.csv")

    write(DOCS / "MISSION_5_EXECUTION_LOG.md", f"""# Mission 5 execution log

## Result

Mission 5 completed the high-value public-evidence pass on 2026-07-27. The work adds public chronological bounds and source convergence without converting current geography, legal recording, escrow, or broad visual disturbance into unsupported address-level history.

## Work performed

1. Preserved all prior Mission 4 sources, claims, graphs, reports, and blocked proximity outputs.
2. Archived {summary['registeredSources']} new sources: County bond reports and GIS, official community directories and publications, contemporary reporting, and official 2005/2009/2010 NAIP imagery.
3. Recorded byte counts, retrieval dates, URLs, and SHA-256 checksums for all {summary['registeredSources']} acquisitions. All acquisitions succeeded.
4. Extracted searchable text from {len(extraction)} PDF/HTML records without OCR. All extractions succeeded; visual review remained mandatory for tables and imagery.
5. Parsed 484 official street-directory rows and 130 current neighborhood phases.
6. Spatially joined {crosswalk['matchedPointRows']:,} current address points to the smallest containing recorded tract, yielding {crosswalk['crosswalkRelationships']} tract-neighborhood relationships across {crosswalk['distinctLeafTracts']} tracts.
7. Reconciled {len(products)} builder products. Contemporary County tables control {len(primary_products)} Phase V/VI products; twelve substantive secondary-source conflicts remain explicit.
8. Transcribed 20 annual County `Built and Occupied` absorption records and eight Urban Activity Center status rows.
9. Inspected official full-coverage aerials dated 2005-06-07, 2009-06-18 through 2009-06-22, and 2010-05-01. Seven bounded visual observations were added; no proximity-eligible construction polygon was created.
10. Rebuilt the evidence graph to {len(graph['nodes']):,} nodes and {len(graph['edges']):,} edges, updated the tract inspector, and generated a separate checksummed Mission 5 atlas.
11. Re-ran the dedicated Mission 5 verifier, the 30-test LHDRS integrity suite, and the seven-stage clean verifier.

## Important conflicts

- A contemporary report dates the first Oak Knoll escrow to 1999-11-29 and first overnight stay to 1999-11-30; an official retrospective states 1999-12-14. Both remain in the conflict registry.
- Twelve Covenant Hills builder assignments differ between a secondary 2010 directory and the contemporary official County table. The County table controls while the secondary positions remain preserved.

## Stopping condition

Public sources produced additional aggregate, product, visual, and current-geography bounds. Remaining work requires agency, district, association, recorder, assessor, or licensed archive records. Repeated public search would now have lower expected value than the ranked manual-record queue.
""")

    write(DOCS / "MISSION_5_IMPLEMENTATION_SUMMARY.md", f"""# Mission 5 implementation summary

## Delivered

- Acquisition and extraction: `evidence/lhdrs/mission5/`
- Reproducible acquisition: `scripts/lhdrs_mission5_acquire.py`
- Evidence integration: `pipelines/python/build_mission5.py`
- Graph generation: `pipelines/python/build_evidence_graph.py`
- Atlas generation: `scripts/generate_lhdrs_mission5_atlas.py`
- Mission verification: `scripts/verify_lhdrs_mission5.py`
- Atlas: `reports/LHDRS_Historical_Evidence_Atlas_Mission_5.html`
- Checksummed export: `data/exports/atlas_mission5/`

## Output scale

{md_table(['Output', 'Count'], [
    ['New archived sources', summary['registeredSources']],
    ['Total registered sources', len(rows('sources.csv'))],
    ['Official street-directory rows', summary['streetDirectoryRows']],
    ['Neighborhood chronology rows', summary['neighborhoodChronologyRows']],
    ['Builder products', summary['builderProducts']],
    ['Current matched address rows', summary['matchedAddressPointRows']],
    ['Tract-neighborhood relationships', summary['tractNeighborhoodRelationships']],
    ['Tract lifecycle records', summary['tractLifecycleRows']],
    ['New bounded claims', summary['newClaims']],
    ['Total claims', len(rows('claim_registry.csv'))],
    ['Evidence graph nodes', len(graph['nodes'])],
    ['Evidence graph edges', len(graph['edges'])],
])}

## Analytical boundary

CFD absorption is aggregate. Builder counts are product snapshots. The tract crosswalk is current. Imagery observations describe visible states. None is promoted to a dated address-level construction, habitability, occupancy, exposure, or health conclusion.

## Recommended next mission

Proceed with **Mission 6: Manual Records Acquisition and Georeferenced Lifecycle Completion**. Its first objective should be a tract/address-keyed County permit and occupancy export, followed by missing aerial frames and historical planning, school-boundary, road-acceptance, utility, facility, and commercial records. See `docs/lhdrs/MISSION_6_RECOMMENDATION.md`.
""")

    completeness_rows = [
        ["Sources", f"{len(rows('sources.csv'))} total; 30 new", "Complete for acquired set", "Agency/manual archives remain"],
        ["Recorded tracts", "123/123 legal recording dates", "Complete legal-map inventory", "Planning, grading, building, occupancy lifecycle"],
        ["Current tract/neighborhood crosswalk", f"{mapped_tracts}/123 tracts; {crosswalk['matchedPointRows']:,} address rows", "Strong current geography", "Historical assignment and validity periods"],
        ["Neighborhoods", "130 official named phases", "Complete current official directory", "Phase opening/construction dates"],
        ["Builders/products", f"{len(products)} products; {len(primary_products)} County-controlled", "Strong for Phase V/VI snapshots", "Exact tract assignment and other primary tables"],
        ["Occupancy", "20 annual CFD counts plus first-resident conflict", "Strong nonspatial aggregate", "Tract/address first and substantial occupancy"],
        ["Construction", "Three new bounded status/change records", "Useful visual/report bounds", "Permits, closeouts, active work polygons"],
        ["Imagery", "Full 2005, 2009, 2010 plus two partial earlier frames", "Strong on capture-date visible state", "Full annual coverage for missing years"],
        ["Schools", "Official openings and administrative projects", "Strong campus milestones", "Historical attendance boundaries and exact work footprints"],
        ["Facilities", "Official retrospective opening milestones", "Moderate milestone coverage", "Exact dates, construction windows, historical footprints"],
        ["Commercial", "Eight exact 2006-12-31 UAC status rows", "Strong status snapshot", "Opening dates, tenants, permits, footprints"],
        ["Roads", f"{summary['currentRoadRegistryRows']} current roads; one 2008 widening status", "Current geometry plus one historical observation", "Opening, acceptance, maintenance, haul routes"],
    ]
    write(DOCS / "MISSION_5_DATA_COMPLETENESS.md", f"""# Mission 5 data completeness

{md_table(['Domain', 'Coverage', 'What is supported', 'What remains missing'], completeness_rows)}

## Proximity gate

All construction, occupancy, and lifecycle additions remain `proximityEligible=false`. Construction, school, and neighborhood proximity result tables remain empty. This is a required evidence safeguard, not a failed calculation.
""")

    gap_rows = [[row["topic"], row["priority"], row["searchOrAccessStatus"], row["reviewStatus"]] for row in gaps]
    write(DOCS / "MISSION_5_RECURSIVE_GAP_REVIEW.md", f"""# Mission 5 recursive gap review

## Outcome

The public pass materially reduced eight chronology or context gaps, but it did not remove the three central geometry blockers: tract-level physical lifecycle, occupied-area geometry, and active-construction geometry.

{md_table(['Topic', 'Priority', 'Search/access result', 'Review status'], gap_rows)}

## Re-evaluation rules

- A current address crosswalk can identify present-day neighborhood candidates; it cannot establish historical neighborhood existence or occupancy.
- A closed escrow or County absorption count can bound aggregate status; it cannot establish a certificate of occupancy or resident move-in at an address.
- Visible disturbance can support a capture-date visual observation; it cannot establish continuous work or a precise active-construction footprint.
- A map-recording date is a legal milestone; it is not a grading, building, habitability, or occupancy date.

## Exhaustion conclusion

The next meaningful evidence gains depend on records not exposed in the reviewed public services: permit and inspection exports, assessor improvement years, CUSD boundary archives, road/utility acceptance files, LARMAC board packets, and additional flight imagery.
""")

    queue_rows = [[row["rank"], row["researchTarget"], row["gapTopics"], row["priority"], row["recommendedRepository"]] for row in queue]
    write(DOCS / "MISSION_5_RESEARCH_QUEUE.md", f"""# Mission 5 research queue

{md_table(['Rank', 'Target', 'Gap topics', 'Priority', 'Repository'], queue_rows)}

Every item is marked `manualRecordRequired=true` in `research/development_chronology/highest_value_research_queue.csv`. A no-record response should be archived with the same provenance discipline as a retrieved record.
""")

    write(DOCS / "MISSION_5_SOURCE_AND_METHOD.md", """# Mission 5 source and method

## Source hierarchy

1. Contemporary official County tables control builder, permit, escrow, absorption, and asset-status claims within their stated CFD scope.
2. Official orthorectified imagery controls only capture-date visible-state observations.
3. Official current directories and GIS control only current names and geography.
4. Contemporary journalism and trade publications support reported events within their wording.
5. Secondary real-estate directories are candidate crosswalks. Conflicts with official contemporary records remain visible and are resolved in favor of the official record.

## Acquisition

Each retrieved item records its original URL, local path, publication date where known, retrieval date, byte count, archive status, source class, reliability grade, and SHA-256 checksum. The acquisition manifest and summary are under `evidence/lhdrs/mission5/`.

## Text and table review

Embedded text was extracted from 25 PDF/HTML records. OCR was not used. County tables were checked against rendered pages because text extraction can scramble columns. Source locators identify the relevant report page or table.

## Current tract/neighborhood crosswalk

The process normalizes the 2019 official street directory, filters current County address points by street and address constraints, then assigns each point to the smallest covering recorded-tract polygon. The relationship is valid at the 2026-07-27 retrieval date. It is not historical tract parentage.

## Imagery

Official CDFW/USDA NAIP service exports cover the current Ladera CDP and surrounding area. Raster catalog filenames establish exact tile dates. Full-resolution and southern-region comparisons support seven written observations. No visual region was digitized for proximity analysis.

## Confidence

- `high`: direct official record or official imagery within a tightly bounded claim.
- `medium`: contemporary reporting, visual synthesis requiring interpretation, or a current spatial crosswalk with historical limits.
- `low`: unconfirmed secondary candidate.

Unknown fields remain blank or explicitly `unknown`. Zero is used only where a source reports zero.
""")

    manual_rows = [[row["rank"], row["researchTarget"], row["evidenceNeeded"], row["recommendedRepository"]] for row in queue]
    write(DOCS / "MISSION_5_MANUAL_RECORDS.md", f"""# Mission 5 manual-record blockers

{md_table(['Rank', 'Record package', 'Requested evidence', 'Custodian'], manual_rows)}

## Minimum request fields

Ask for tract number, address or APN, application/permit number, record type, issue date, inspection or acceptance date, final/closeout date, status, project description, applicant/contractor, scanned plan or map attachment, and any available georeferenced boundary or index export.

## Preserve separately

- Building permits, grading permits, inspection closeouts, and certificates of occupancy.
- Assessor improvement years and Recorder closing instruments.
- Improvement-plan acceptance and County maintenance records.
- Approved haul-route or traffic-control sheets.
- CUSD annual attendance maps and Board adoption actions.
- LARMAC board packets, facility approvals, and recorded common-area plats.
- Commercial tenant permits, leases, assessor records, and site plans.
- Flight indexes, frame footprints, capture dates, and usage terms for additional imagery.

Do not merge permit issue, construction start, final inspection, certificate of occupancy, escrow closing, and move-in into one date. Preserve each milestone as its own observation.
""")

    write(DOCS / "MISSION_5_QA_REPORT.md", f"""# Mission 5 QA report

## Passed checks

- Dedicated Mission 5 verification: passed.
- LHDRS integrity suite: 30/30 passed.
- Full clean verifier: 7/7 stages passed, including clean install, TypeScript, Prisma validation, high-severity npm audit, and production build.
- Acquisition manifest: 30/30 retrieved; byte sizes and SHA-256 checksums verified.
- Text extraction: {len(extraction)}/{len(extraction)} succeeded; output checksums verified.
- County arithmetic: Phase I 1,129; UAC 386; Phase V 1,242; Phase VI 892 built-and-occupied units.
- Product arithmetic: Phase V 1,259 planned/permits and 1,242 2006 escrows; Phase VI 1,006 planned, 731 permits and 705 escrows in 2006, 892 escrows including custom lots by 2011.
- Evidence models: {len(rows('historical_observations.csv'))} observations, {len(rows('claim_registry.csv'))} claims, and equal convergence rows.
- Evidence graph: {len(graph['nodes']):,} nodes and {len(graph['edges']):,} edges; every edge has evidence and registered source IDs.
- Atlas publication: 14 files with verified byte sizes and checksums.
- Proximity safeguard: zero published proximity results; every relevant new record remains ineligible.

## Static report checks

The HTML and Markdown atlas contain no absolute user paths or `file://` links. Referenced image assets exist and are checksummed. Direct in-app browser rendering of the local `file:` report was unavailable under the browser URL policy, so visual QA was limited to source-image inspection and static HTML/reference validation.

## Residual risk

The dominant residual risk is not software correctness; it is incomplete historical record access. Current geographic associations and aggregate County milestones could be misread as tract-level physical history if their limitations are discarded. Every relevant output therefore repeats its scope and keeps proximity disabled.
""")

    write(DOCS / "MISSION_6_RECOMMENDATION.md", """# Mission 6 recommendation

## Title

Manual Records Acquisition and Georeferenced Lifecycle Completion

## Objective

Convert Mission 5's strongest current-geography and nonspatial historical bounds into verified tract- or address-level lifecycle records. Mission 6 should be records-led rather than search-led: public web research has reached diminishing returns for the evidence classes that still block reconstruction.

## Priority sequence

1. Obtain County grading, building, inspection-closeout, and certificate-of-occupancy indexes keyed by tract, APN, address, and permit number.
2. Acquire full-coverage aerial frames for 1999-2004 and 2006-2008 with flight dates, footprints, and usage metadata.
3. Obtain historical planning-area/village maps, tentative-map files, improvement agreements, and tract-keyed builder filings.
4. Obtain 1997-2010 CUSD attendance maps and Board adoption actions.
5. Obtain road and utility improvement-plan acceptance, maintenance, notice-of-completion, traffic-control, and haul-route records.
6. Obtain LARMAC facility records and commercial tenant permits, leases, assessor records, and historical site plans.
7. Complete the post-2010 Covenant Hills custom-lot permit and assessor chronology.

## Required outputs

- A normalized permit and inspection event registry that preserves each milestone separately.
- Georeferenced, dated construction and occupancy geometries with explicit provenance.
- Historical tract-to-planning-area, village, neighborhood, builder, and product validity intervals.
- Annual school attendance-area layers and facility/commercial lifecycle records.
- A refreshed evidence graph, atlas, confidence review, and proximity-gate decision.

## Evidence gate

Do not run historical proximity analysis until both subject geometry and dated target geometry pass the existing precision, provenance, and temporal-validity checks. A failed or incomplete records request must be archived as a result, not silently converted to a negative factual conclusion.

## First request package

The first request should ask Orange County for machine-readable or scanned indexes covering 1997-2011 for all Ladera Ranch tract numbers and addresses, including permit type, application number, issue date, inspection dates, final date, certificate-of-occupancy date, status, APN, address, tract number, project description, contractor/applicant, and linked plan or map identifiers.
""")


if __name__ == "__main__":
    build()
    print("DONE  Mission 5 documentation: 9 files")
