#!/usr/bin/env python3
"""Build the Mission 4 school timeline from archived DSA and opening records."""

from __future__ import annotations

import csv
import datetime as dt
from html import unescape
import json
import os
from pathlib import Path
import re
import tempfile


ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "research/development_chronology"
EVIDENCE = ROOT / "evidence/lhdrs/schools/dsa"
GIS = ROOT / "data/gis/ladera_development/school_attendance_areas"
DOCS = ROOT / "docs/lhdrs"
DSA_SOURCE = "LH-SRC-DGS-DSA-TRACKER"
PROJECTS = [
    {
        "app": "101335",
        "stem": "chaparral_original_campus",
        "school_ids": "LH-SCHOOL-CHAPARRAL",
        "open_earliest": "2001-09-01",
        "open_latest": "2001-09-30",
        "opening_source": "LH-SRC-CUSD-CHAPARRAL",
    },
    {
        "app": "102435",
        "stem": "ladera_shared_original_campus",
        "school_ids": "LH-SCHOOL-LRES;LH-SCHOOL-LRMS",
        "open_earliest": "2003-08-27",
        "open_latest": "2003-08-27",
        "opening_source": "LH-SRC-CUSD-LRES;LH-SRC-CUSD-LRMS",
    },
    {
        "app": "105541",
        "stem": "oso_grande_original_campus",
        "school_ids": "LH-SCHOOL-OSO-GRANDE",
        "open_earliest": "2005-08-24",
        "open_latest": "2005-08-24",
        "opening_source": "LH-SRC-CDE-OSO",
    },
]


def write_csv(name: str, rows: list[dict[str, object]], fields: list[str]) -> None:
    path = BASE / name
    with tempfile.NamedTemporaryFile(
        mode="w", newline="", encoding="utf-8", dir=path.parent, delete=False
    ) as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temp_path = Path(stream.name)
    os.replace(temp_path, path)


def write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", dir=path.parent, delete=False
    ) as stream:
        stream.write(value)
        temp_path = Path(stream.name)
    os.replace(temp_path, path)


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", dir=path.parent, delete=False
    ) as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write("\n")
        temp_path = Path(stream.name)
    os.replace(temp_path, path)


def span_value(html: str, element_id: str) -> str:
    match = re.search(
        rf'<span[^>]+id="{re.escape(element_id)}"[^>]*>(.*?)</span>', html, flags=re.I | re.S
    )
    if not match:
        return ""
    value = re.sub(r"<[^>]+>", " ", match.group(1))
    return " ".join(unescape(value).split())


def iso_date(value: str) -> str:
    if not value:
        return ""
    return dt.datetime.strptime(value, "%m/%d/%Y").date().isoformat()


def load_page(stem: str, app: str, suffix: str) -> str:
    return (EVIDENCE / f"{stem}_04_{app}_{suffix}.html").read_text(
        encoding="utf-8", errors="replace"
    )


def build_projects() -> list[dict[str, object]]:
    rows = []
    for project in PROJECTS:
        app = project["app"]
        stem = project["stem"]
        summary = load_page(stem, app, "application_summary")
        field = load_page(stem, app, "field_review_status")
        closeout = load_page(stem, app, "project_certification")
        row = {
            "schoolProjectId": f"LH-SCHOOL-PROJECT-04-{app}",
            "dsaOfficeId": "04",
            "dsaApplicationId": app,
            "relatedSchoolIds": project["school_ids"],
            "projectName": span_value(summary, "ctl00_MainContent_lblPname"),
            "projectScope": span_value(summary, "ctl00_MainContent_lblProjectScope"),
            "addressAsFiled": span_value(summary, "ctl00_MainContent_lblAddress"),
            "cityAsFiled": span_value(summary, "ctl00_MainContent_lblCity"),
            "applicationReceivedDate": iso_date(span_value(summary, "ctl00_MainContent_lblRecvDate")),
            "planApprovedDate": iso_date(span_value(summary, "ctl00_MainContent_lblAppDate")),
            "fieldReviewStartDate": iso_date(
                span_value(field, "ctl00_MainContent_gdvF_ctl02_lblStartDate")
            ),
            "fieldReviewFinishDate": iso_date(
                span_value(field, "ctl00_MainContent_gdvF_ctl02_lblFinishDate")
            ),
            "projectClosedDate": iso_date(span_value(summary, "ctl00_MainContent_lblCloseDate")),
            "certificationDate": iso_date(span_value(closeout, "ctl00_MainContent_lblCloseDate")),
            "certificationType": span_value(closeout, "ctl00_MainContent_lblCloseLetType"),
            "campusOpenEarliest": project["open_earliest"],
            "campusOpenLatest": project["open_latest"],
            "constructionStartConclusion": "not_exactly_established",
            "constructionCompletionConclusion": "operational_by_opening_date;full_project_closeout_later",
            "proximityEligible": "false",
            "geometryId": "",
            "sourceIds": f"{DSA_SOURCE};{project['opening_source']}",
            "statementClass": "documented_exact",
            "confidence": "high",
            "confidenceRationale": (
                "DSA dates and scopes are direct official registry fields; opening dates are from official "
                "school sources. Exact physical construction start and campus work footprint are absent."
            ),
            "limitations": (
                "Administrative milestones are not interchangeable with physical construction dates. "
                "The campus could operate before all DSA field review and certification work concluded."
            ),
            "reviewStatus": "reviewed",
        }
        rows.append(row)
    return rows


def build_timeline(projects: list[dict[str, object]]) -> list[dict[str, object]]:
    rows = []
    sequence = 0
    for project in projects:
        milestones = [
            (
                "dsa_application_received",
                project["applicationReceivedDate"],
                project["applicationReceivedDate"],
                "DSA received the project application.",
                DSA_SOURCE,
                "documentary_date",
            ),
            (
                "dsa_plan_approved",
                project["planApprovedDate"],
                project["planApprovedDate"],
                "DSA approved the submitted plans.",
                DSA_SOURCE,
                "documentary_date",
            ),
            (
                "dsa_field_review_interval",
                project["fieldReviewStartDate"],
                project["fieldReviewFinishDate"],
                "DSA records a field-review interval for the project.",
                DSA_SOURCE,
                "documentary_date",
            ),
            (
                "school_operation_open",
                project["campusOpenEarliest"],
                project["campusOpenLatest"],
                "The official school source establishes campus operation by this date or month.",
                ";".join(str(project["sourceIds"]).split(";")[1:]),
                "school_opening",
            ),
            (
                "dsa_project_certified",
                project["certificationDate"],
                project["certificationDate"],
                "DSA issued certification and closed the project file.",
                DSA_SOURCE,
                "documentary_date",
            ),
        ]
        for milestone, earliest, latest, observation, source_ids, observation_type in milestones:
            sequence += 1
            rows.append(
                {
                    "schoolTimelineId": f"LH-SCHOOL-TIMELINE-{sequence:03d}",
                    "schoolProjectId": project["schoolProjectId"],
                    "schoolIds": project["relatedSchoolIds"],
                    "milestoneType": milestone,
                    "earliestDate": earliest,
                    "latestDate": latest,
                    "datePrecision": "day" if earliest == latest else "month_or_interval",
                    "observedState": observation,
                    "directOrInferred": "direct",
                    "geometryId": "" if milestone != "school_operation_open" else "school_centroid_only",
                    "sourceIds": source_ids,
                    "confidence": "high",
                    "confidenceRationale": "Direct official registry or official school opening statement.",
                    "limitations": (
                        "This milestone does not by itself establish active-construction geometry or "
                        "historical attendance assignment."
                    ),
                    "reviewStatus": "reviewed",
                }
            )
    return rows


def build_boundaries() -> list[dict[str, object]]:
    school_open = {
        "LH-SCHOOL-CHAPARRAL": 2001,
        "LH-SCHOOL-LRES": 2003,
        "LH-SCHOOL-LRMS": 2003,
        "LH-SCHOOL-OSO-GRANDE": 2005,
    }
    rows = []
    for year in range(1997, 2011):
        open_ids = [school_id for school_id, open_year in school_open.items() if open_year <= year]
        rows.append(
            {
                "schoolBoundaryHistoryId": f"LH-SCHOOL-BOUNDARY-{year}",
                "year": year,
                "geographyId": "LH-COMMUNITY-LADERA-RANCH",
                "openLocalSchoolIds": ";".join(open_ids),
                "documentedAssignedSchoolIds": "",
                "assignmentStatus": "historical_attendance_boundary_not_retrieved",
                "geometryStatus": "unavailable",
                "geometryId": "",
                "nearestSchoolInterpretation": "not_an_attendance_assignment",
                "sourceIds": "",
                "confidence": "unknown",
                "limitations": (
                    "School opening status is known separately; no historical attendance-boundary source "
                    "was retrieved, so assignment is not inferred from proximity."
                ),
                "reviewStatus": "blocked_pending_district_records",
            }
        )
    return rows


def main() -> int:
    projects = build_projects()
    timeline = build_timeline(projects)
    boundaries = build_boundaries()
    write_csv("school_project_registry.csv", projects, list(projects[0]))
    write_csv("school_timeline.csv", timeline, list(timeline[0]))
    write_csv("school_boundary_history.csv", boundaries, list(boundaries[0]))
    write_json(
        GIS / "status.geojson",
        {
            "type": "FeatureCollection",
            "features": [],
            "status": "historical_attendance_boundaries_not_retrieved",
            "notEvidenceOfAbsence": True,
            "limitations": (
                "No historical attendance-area geometry is published. Nearest-school calculations are "
                "not substitutes for district assignment records."
            ),
        },
    )

    project_lines = []
    for project in projects:
        project_lines.append(
            f"- **{project['projectName']} (DSA 04-{project['dsaApplicationId']}):** received "
            f"{project['applicationReceivedDate']}; plans approved {project['planApprovedDate']}; "
            f"field review {project['fieldReviewStartDate']} to {project['fieldReviewFinishDate']}; "
            f"campus open by {project['campusOpenLatest']}; certified {project['certificationDate']}."
        )
    doc = """# School reconstruction

## Result

The original public-campus projects are now tied to official Division of the State Architect records. Each administrative milestone remains separate from school operation and from physical construction.

""" + "\n".join(project_lines) + """

The first application is filed as “Ladera Ranch Elem. School # 1” at the Sienna Parkway site. It is associated with Chaparral Elementary because it is the first local campus, its official opening source places Chaparral in September 2001, and the DSA chronology precedes that opening. This name crosswalk is medium-confidence; the original DSA page does not itself use the later Chaparral name.

## Construction interpretation

DSA application receipt and plan approval are documentary facts. Field-review start and finish are official oversight fields, but they are not assumed to equal the first and last physical work on site. Opening establishes operation of the campus by the stated day or month; certification and file closeout can occur later. No campus construction polygon was recovered, so these project records remain ineligible for construction-proximity calculations.

## Attendance boundaries

No historical CUSD attendance-area maps for 1997-2010 were retrieved through public indexed sources. `school_boundary_history.csv` therefore reports the local schools known open each year but leaves assigned schools blank. It never converts the nearest campus into a documented or probable assignment.

## Manual follow-up

Request from Capistrano Unified School District the annual attendance-boundary maps, board facilities agenda packets, notices to proceed, substantial-completion records, and original campus site exhibits for 1998-2006. DSA project-related documentation other than restricted plan sets may also be requested through the Department of General Services public-records process.

## Outputs

- `research/development_chronology/school_project_registry.csv`
- `research/development_chronology/school_timeline.csv`
- `research/development_chronology/school_boundary_history.csv`
- `data/gis/ladera_development/school_attendance_areas/status.geojson`
- `research/development_chronology/school_source_manifest.csv`
"""
    write_text(DOCS / "SCHOOL_RECONSTRUCTION.md", doc)
    print(f"DONE  school reconstruction: {len(projects)} projects, {len(timeline)} milestones")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
