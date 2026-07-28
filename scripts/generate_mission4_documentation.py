#!/usr/bin/env python3
"""Generate Mission 4 QA, completeness, gap, and implementation documentation."""

from __future__ import annotations

import csv
import json
import os
from pathlib import Path
import tempfile


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "research/development_chronology"
DOCS = ROOT / "docs/lhdrs"
VERIFY = ROOT / "data/exports/atlas_second_edition/verification_summary.json"


def rows(name: str) -> list[dict[str, str]]:
    with (BASE / name).open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", dir=path.parent, delete=False
    ) as stream:
        stream.write(value)
        temporary = Path(stream.name)
    os.replace(temporary, path)


def verification_section() -> str:
    if not VERIFY.exists():
        return "Complete verification has not yet been run. Execute `make lhdrs-mission4-verify`."
    summary = json.loads(VERIFY.read_text())
    lines = [
        f"Latest complete verification: **{summary['status']}** ({summary['passedCount']}/{summary['checkCount']} checks).",
        "",
        "| Check | Status | Duration | Log |",
        "|---|---|---:|---|",
    ]
    for check in summary["checks"]:
        lines.append(f"| `{check['id']}` | {check['status']} | {check['durationSeconds']} s | `{check['logPath']}` |")
    return "\n".join(lines)


def main() -> int:
    graph = rows("knowledge_graph.csv")
    gaps = rows("research_gaps.csv")
    conflicts = rows("conflict_registry.csv")
    imagery = rows("imagery_inventory.csv")
    activities = rows("construction_activity_registry.csv")
    occupancy = rows("occupancy_event_registry.csv")
    schools = rows("school_project_registry.csv")
    wind = rows("wind_annual_summary.csv")
    qa = f"""# Mission 4 QA report

## Verification

{verification_section()}

## Automated evidence gates

- The LHDRS suite contains 30 integrity tests covering canonical CSV structure, source registration, chronology order, tract geometry, title sheets, imagery coverage, school-project boundaries, wind coverage, terrain bounds, reconstruction matrices, proximity blocking, graph edges, public paths, publication safeguards, and export checksums.
- All 123 tract rows must leave physical lifecycle dates blank unless separate evidence exists.
- Empty construction, habitability, occupancy, and attendance layers must carry `notEvidenceOfAbsence=true`.
- Proximity output tables must remain empty until both geometry gates pass; the selected future analysis CRS is EPSG:26946.
- Every Mission 4 graph edge must include evidence, source, confidence, version, and review status.
- The second edition must contain exactly 14 annual chapters and six phase snapshots while preserving the first edition under its original filenames.

## Manual visual QA scope

The terrain, drainage, wind, graph, annual publication figures, second-edition report, and interactive atlas require desktop/mobile render review. Results and any residual risks are recorded in the execution log after the browser pass.
"""
    write_text(DOCS / "MISSION_4_QA_REPORT.md", qa)

    completeness = f"""# Mission 4 data completeness

| Component | Records | Status | Analytical boundary |
|---|---:|---|---|
| Recorded tract audit | 123 | Complete for County polygons and recording attributes | Legal geography, not physical lifecycle |
| Recorded tract PDFs/title sheets | 123 | Archived and OCR indexed | Legal relationships and parties only |
| Historical observations / claims | {len(rows('historical_observations.csv'))} / {len(rows('claim_registry.csv'))} | Complete for registered evidence | Claim scope remains bounded |
| Construction activities | {len(activities)} | Partial, nonspatial | Zero proximity-eligible activities |
| Construction polygons | 0 | Blocked | Partial nonadjacent imagery cannot support digitization |
| Occupancy/sales events | {len(occupancy)} | Partial, community scale | Zero occupied or habitable geometries |
| Neighborhood occupancy | 9 named rows | Blocked | Tract, builder, and lifecycle crosswalk unresolved |
| School projects | {len(schools)} DSA projects / 4 schools | Partial | Openings supported; exact construction starts and attendance boundaries unresolved |
| Historical imagery | {len(imagery)} frames / contexts | Partial | Two development-era frames each cover about half the current CDP |
| Regional wind | {len(wind)} annual summaries | Complete for selected archived records | Airport observations are not local downscaling |
| Terrain/drainage | 123 tract summaries | Complete as current/post-study context | 2018 DEM and later GIS are not historical surfaces |
| Proximity | 0 results / 6 blocked subject classes | Blocked | Both dated geometry gates are unsatisfied |
| Annual / phase manifests | 14 / 6 | Complete with explicit unknown states | No annual state is manufactured from an undated source |
| Evidence graph | {len(graph)} edges | Complete for registered Mission 4 relationships | Blocked graph queries remain blocked |

The highest-value completeness gain would come from dated grading/as-built plans, building finals or certificates of occupancy, address-level closings or utility activation, and 1999-2010 overlapping historical aerial frames.
"""
    write_text(DOCS / "MISSION_4_DATA_COMPLETENESS.md", completeness)

    conflict_lines = [
        "# Mission 4 conflict report",
        "",
        f"The registry contains **{len(conflicts)} explicit conflicts or scope distinctions**. Neither side is deleted.",
        "",
    ]
    for conflict in conflicts:
        conflict_lines.extend(
            [
                f"## {conflict['conflictId']}",
                "",
                f"- Subject: `{conflict['subjectId']}`",
                f"- Position A: {conflict['positionA']} (`{conflict['positionASourceIds']}`)",
                f"- Position B: {conflict['positionB']} (`{conflict['positionBSourceIds']}`)",
                f"- Resolution: {conflict['resolution']}",
                f"- Review status: `{conflict['reviewStatus']}`",
                "",
            ]
        )
    write_text(DOCS / "MISSION_4_CONFLICT_REPORT.md", "\n".join(conflict_lines))

    gap_lines = [
        "# Mission 4 gap review",
        "",
        f"The recursive review records **{len(gaps)} open gaps** after tract-map, County imagery, DSA, NOAA, terrain, watershed, stream, and flood-control acquisition.",
        "",
        "| Priority | Topic | Scope | Access status | Analytical impact |",
        "|---|---|---|---|---|",
    ]
    for gap in gaps:
        gap_lines.append(f"| {gap['priority']} | {gap['topic']} | {gap['scope']} | {gap['searchOrAccessStatus']} | {gap['analyticalImpact']} |")
    gap_lines.extend(
        [
            "",
            "Public web avenues are at diminishing returns for the two critical geometry layers. The next useful work is record retrieval, not extrapolation from tract recording dates or present-day maps.",
        ]
    )
    write_text(DOCS / "MISSION_4_GAP_REVIEW.md", "\n".join(gap_lines) + "\n")

    requests = """# Recommended manual record requests

## 1. Orange County building and occupancy records

Request permit issue, final inspection, certificate of occupancy, address, parcel, tract, unit count, and status records for Ladera Ranch from 1997-2010. Ask for native tabular data and field definitions. This is the highest-value source for habitability and first-occupancy bounds.

## 2. Orange County grading and improvement plans

Request mass-grading permits, rough/final grading approvals, improvement-plan sheets, as-built plan dates, storm-drain and utility acceptance records, and plan geometry keyed to tract or project number. Include project extents and revision histories where available.

## 3. Historical aerial frames

Ask Orange County Survey/Archives and USGS EarthExplorer staff for overlapping, georeferenced frames covering the full planned community for 1999-2010, including flight date, project, image number, scale, scan resolution, footprint, and use terms.

## 4. Capistrano Unified attendance records

Request annual attendance-boundary maps, boundary-change board items, temporary-campus arrangements, transportation notices, opening calendars, and facilities-project files for 1997-2010. Nearest-school calculations are not a substitute.

## 5. Builder, developer, and HOA chronology

Request neighborhood-to-tract crosswalks, builder/product lists, model openings, sales releases, first closings, phase maps, newsletters, and buildout summaries from LARMAC, Rancho Mission Viejo, and identified builders.

## 6. Roads, facilities, and construction access

Request road-improvement acceptance dates, partial/full opening notices, traffic-control plans, approved construction-access or haul-route exhibits, park/facility notices, and commercial tenant-opening files. Do not infer haul routes from location alone.

For every request, ask the custodian to preserve a no-record or exemption response, identify retention schedules, and provide record-system field definitions. Authentication, paywalls, CAPTCHAs, and access controls must not be bypassed.
"""
    write_text(DOCS / "RECOMMENDED_MANUAL_RECORD_REQUESTS.md", requests)

    implementation = f"""# Mission 4 implementation summary

Mission 4 preserved the first edition and added a source-bounded second edition. It archived 123 official tract-map PDFs, audited all 123 County tract polygons, indexed title sheets, added County development-era imagery, reconstructed three original school-campus DSA projects, processed NOAA station observations, and generated County terrain/drainage context.

The structured layer now includes {len(activities)} construction records, {len(occupancy)} sales/occupancy records, 123 tract chronologies, nine neighborhood rows, 14 annual manifests, six phase manifests, {len(graph)} graph edges, 127 Evidence Inspector records, {len(conflicts)} conflicts, and {len(gaps)} research gaps.

No dated active-construction, habitable, or occupied polygon passed the evidence threshold. Proximity therefore remains blocked with zero results. This is a completed gate decision, not a claim that no construction coexistence occurred.

Major publications:

- `reports/LHDRS_Historical_Development_Atlas_Second_Edition.html`
- `reports/LHDRS_Historical_Development_Atlas_Second_Edition.md`
- `reports/LHDRS_Historical_Construction_Proximity_Report.html`
- `reports/LHDRS_Wind_and_Terrain_Context.html`
- `data/exports/atlas_second_edition/`
"""
    write_text(DOCS / "MISSION_4_IMPLEMENTATION_SUMMARY.md", implementation)

    reproducibility = """# Mission 4 reproducibility

Use a Python environment containing GeoPandas, Shapely, pyproj, Rasterio, NumPy, Pillow, pandas, and Matplotlib. Set `LHDRS_PYTHON` to that interpreter when it is not the system `python3`.

Core commands:

```sh
make lhdrs-mission4-ingest
make lhdrs-mission4 LHDRS_PYTHON=/path/to/gis-python
make lhdrs-mission4-publish LHDRS_PYTHON=/path/to/gis-python
make lhdrs-mission4-verify LHDRS_PYTHON=/path/to/gis-python
```

Fetch scripts archive service metadata and checksums. Build scripts write deterministic IDs and atomically replace derived tables. Raw County, DSA, NOAA, imagery, and terrain inputs remain under `evidence/lhdrs/`. The proximity build always applies its evidence gate before calculation.
"""
    write_text(DOCS / "MISSION_4_REPRODUCIBILITY.md", reproducibility)
    print("DONE  Mission 4 QA, completeness, conflict, gap, request, implementation, and reproducibility docs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
