#!/usr/bin/env python3
"""Build bounded Mission 4 chronology, lifecycle, and proximity-gate outputs."""

from __future__ import annotations

import csv
import json
import os
from pathlib import Path
import re
import tempfile


ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "research/development_chronology"
GIS = ROOT / "data/gis/ladera_development"
PROXIMITY = ROOT / "data/processed/proximity"
EXPORT = ROOT / "data/exports/atlas_second_edition"
DOCS = ROOT / "docs/lhdrs"
REPORTS = ROOT / "reports"
DISCLAIMER = (
    "This reconstruction documents historical development chronology and spatial relationships "
    "using available public records and imagery. Construction proximity, wind patterns, terrain, "
    "and drainage context are descriptive historical information. They are not measurements of "
    "individual exposure, contamination, health risk, or disease causation."
)


def read_csv(name: str) -> list[dict[str, str]]:
    with (BASE / name).open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def write_csv(name: str, rows: list[dict[str, object]], fields: list[str], directory: Path = BASE) -> None:
    path = directory / name
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w", newline="", encoding="utf-8", dir=path.parent, delete=False
    ) as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temporary = Path(stream.name)
    os.replace(temporary, path)


def write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", dir=path.parent, delete=False
    ) as stream:
        stream.write(value)
        temporary = Path(stream.name)
    os.replace(temporary, path)


def write_json(path: Path, value: object) -> None:
    write_text(path, json.dumps(value, indent=2, sort_keys=True) + "\n")


def source_count(value: str) -> int:
    return len({part.strip() for part in re.split(r"[;,]", value) if part.strip()})


def empty_layer(status: str, limitations: str, source_ids: list[str]) -> dict[str, object]:
    return {
        "type": "FeatureCollection",
        "features": [],
        "status": status,
        "notEvidenceOfAbsence": True,
        "sourceIds": source_ids,
        "limitations": limitations,
    }


def construction_registry() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = [
        {
            "constructionActivityId": "LH-CONSTRUCTION-COMMUNITY-1998",
            "activityClass": "unknown_construction",
            "canonicalName": "Community development begins",
            "relatedTractIds": "",
            "relatedNeighborhoodIds": "",
            "relatedPlanningAreaIds": "",
            "relatedBuilderIds": "",
            "geometryId": "",
            "geometryMethod": "not_available",
            "geometrySource": "",
            "earliestStart": "1998-01-01",
            "latestStart": "1998-12-31",
            "earliestEnd": "",
            "latestEnd": "",
            "datePrecision": "year",
            "lifecycleState": "reported_active_at_community_scale",
            "intensityClass": "unknown",
            "evidenceIds": "LH-EVT-002",
            "sourceIds": "LH-SRC-ULI-CASE",
            "confidence": "medium",
            "confidenceRationale": "Retrospective case study dates community development generally, not a physical activity footprint.",
            "limitations": "No tract, activity class, end date, or dated geometry is established.",
            "reviewStatus": "bounded_nonspatial_record",
            "version": "2.0",
            "proximityEligible": "false",
        },
        {
            "constructionActivityId": "LH-CONSTRUCTION-UTILITIES-1999",
            "activityClass": "utility_installation",
            "canonicalName": "Phase 1 utility package",
            "relatedTractIds": "",
            "relatedNeighborhoodIds": "",
            "relatedPlanningAreaIds": "",
            "relatedBuilderIds": "",
            "geometryId": "",
            "geometryMethod": "not_available",
            "geometrySource": "",
            "earliestStart": "",
            "latestStart": "",
            "earliestEnd": "",
            "latestEnd": "",
            "datePrecision": "unknown",
            "lifecycleState": "environmental_record_received",
            "intensityClass": "unknown",
            "evidenceIds": "LH-EVT-004",
            "sourceIds": "LH-SRC-CEQANET-UTILITIES",
            "confidence": "high",
            "confidenceRationale": "The official record directly establishes a proposed package and receipt date only.",
            "limitations": "The 1999-03-09 record date is not treated as construction start or completion.",
            "reviewStatus": "blocked_pending_as_built_records",
            "version": "2.0",
            "proximityEligible": "false",
        },
    ]
    for project in read_csv("school_project_registry.csv"):
        rows.append(
            {
                "constructionActivityId": f"LH-CONSTRUCTION-SCHOOL-{project['dsaOfficeId']}-{project['dsaApplicationId']}",
                "activityClass": "school_construction",
                "canonicalName": project["projectName"],
                "relatedTractIds": "",
                "relatedNeighborhoodIds": "",
                "relatedPlanningAreaIds": "",
                "relatedBuilderIds": "",
                "geometryId": "",
                "geometryMethod": "not_available",
                "geometrySource": "",
                "earliestStart": "",
                "latestStart": "",
                "earliestEnd": project["campusOpenEarliest"],
                "latestEnd": project["certificationDate"],
                "datePrecision": "range",
                "lifecycleState": "operational_before_final_closeout",
                "intensityClass": "unknown",
                "evidenceIds": project["schoolProjectId"],
                "sourceIds": project["sourceIds"],
                "confidence": "medium",
                "confidenceRationale": "Opening and DSA closeout bound completion concepts, but exact physical start and work footprint are absent.",
                "limitations": "The end range separates campus operation from later administrative closeout; it is not an active-construction interval.",
                "reviewStatus": "blocked_pending_permit_or_imagery_geometry",
                "version": "2.0",
                "proximityEligible": "false",
            }
        )
    return rows


def occupancy_registry(events: list[dict[str, str]]) -> list[dict[str, object]]:
    rows = []
    for event in events:
        if event["eventType"] not in {"sales", "occupancy", "substantial_completion"}:
            continue
        quantity = ""
        match = re.search(r"(\d+) (?:total )?new homes sold", event["title"])
        if match:
            quantity = match.group(1)
        evidence_class = {
            "sales": "sale_count_not_occupancy",
            "occupancy": "first_documented_resident",
            "substantial_completion": "community_completion_not_occupancy",
        }[event["eventType"]]
        rows.append(
            {
                "occupancyEventId": event["id"].replace("LH-EVT", "LH-OCC-EVT"),
                "relatedEventId": event["id"],
                "geographyId": event["featureId"],
                "geographyType": "community_nonspatial",
                "eventClass": evidence_class,
                "eventTitle": event["title"],
                "earliestDate": event["dateStart"],
                "latestDate": event["dateEnd"] or event["dateStart"],
                "datePrecision": event["temporalPrecision"],
                "homeCount": quantity,
                "habitabilityConclusion": "not_established",
                "occupancyConclusion": "community_level_only" if event["eventType"] == "occupancy" else "not_established",
                "geometryId": "",
                "geometryStatus": "not_available",
                "sourceIds": event["sourceIds"],
                "statementClass": event["statementClass"],
                "confidence": event["confidence"],
                "confidenceRationale": "The source supports the stated community milestone; it does not locate homes or establish occupied-area extent.",
                "limitations": event["notes"] + " No tract or neighborhood occupancy geometry is inferred.",
                "reviewStatus": "bounded_nonspatial_record",
                "proximityEligible": "false",
            }
        )
    return rows


def tract_matrices() -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    matrices = []
    evidence = []
    for tract in read_csv("tract_audit.csv"):
        matrices.append(
            {
                "tractId": tract["tractId"],
                "tentativeTract": "",
                "finalTract": tract["tractNumber"],
                "planningAreaId": "",
                "villageId": "",
                "neighborhoodId": "",
                "builderIds": "",
                "productIds": "",
                "approvalDate": "",
                "mapRecordingDate": tract["recordDate"],
                "gradingStartRange": "",
                "gradingEndRange": "",
                "infrastructureRange": "",
                "roadConstructionRange": "",
                "verticalConstructionRange": "",
                "modelOpeningRange": "",
                "firstSaleRange": "",
                "earliestHabitabilityRange": "",
                "firstOccupancyRange": "",
                "partialOccupancyRange": "",
                "substantialOccupancyRange": "",
                "completionRange": "",
                "associatedSchoolByYear": "",
                "nearestOpenSchoolByYear": "not_calculated_without_historical_assignment_or_subject_geometry",
                "activeConstructionOverlap": "not_calculated",
                "sourceIds": tract["sourceIds"],
                "evidenceCount": 1,
                "milestoneConfidence": "recording_high;physical_lifecycle_unknown",
                "unresolvedGaps": "approval;hierarchy;builder;grading;infrastructure;roads;vertical;models;sales;habitability;occupancy;completion",
                "reviewStatus": "blocked_pending_lifecycle_records",
            }
        )
        evidence.append(
            {
                "tractMilestoneEvidenceId": f"LH-TRACT-EVIDENCE-{tract['tractNumber']}-RECORDING",
                "tractId": tract["tractId"],
                "milestoneType": "legal_tract_map_recording",
                "earliestDate": tract["recordDate"],
                "latestDate": tract["recordDate"],
                "datePrecision": "day",
                "evidenceId": f"LH-OBS-TRACT-{tract['tractNumber']}",
                "sourceIds": "LH-SRC-OC-TRACTS;LH-SRC-OC-LMS-TRACT-PDFS",
                "directOrInferred": "direct",
                "confidence": "high",
                "confidenceRationale": "County GIS attribute and recorded map collection establish the legal recording milestone.",
                "physicalLifecycleMeaning": "none_established",
                "limitations": "Recording is not evidence of grading, construction, sale, habitability, or occupancy.",
                "reviewStatus": tract["titleSheetReviewStatus"],
            }
        )
    return matrices, evidence


def neighborhood_matrix() -> list[dict[str, object]]:
    rows = []
    for neighborhood in read_csv("neighborhoods.csv"):
        rows.append(
            {
                "neighborhoodId": neighborhood["id"],
                "officialName": neighborhood["name"],
                "alternateNames": "",
                "parentVillageId": "",
                "planningAreaId": neighborhood["planningArea"],
                "builderIds": neighborhood["builderOrBuilders"],
                "tractIds": neighborhood["tractMapIds"],
                "phaseNumber": "",
                "models": "",
                "advertisedOpening": neighborhood["modelOpening"],
                "firstSales": neighborhood["firstSales"],
                "earliestHabitability": "",
                "firstOccupancy": neighborhood["firstOccupancy"],
                "partialOccupancy": neighborhood["substantialOccupancy"],
                "substantialOccupancy": "",
                "buildout": neighborhood["buildout"],
                "documentaryEvidenceIds": "",
                "visualEvidenceIds": "",
                "sourceIds": neighborhood["sourceIds"],
                "evidenceCount": 0,
                "sourceDiversity": source_count(neighborhood["sourceIds"]),
                "confidence": "unknown",
                "confidenceRationale": "No tract-level neighborhood crosswalk or residential lifecycle record was retrieved.",
                "conflicts": "",
                "geometryStatus": "not_available",
                "limitations": neighborhood["limitations"],
                "reviewStatus": "blocked_pending_builder_and_occupancy_records",
            }
        )
    return rows


def asset_chronology(events: list[dict[str, str]]) -> list[dict[str, object]]:
    allowed = {"utilities", "clubhouse", "park", "commercial", "library", "school"}
    rows = []
    for event in events:
        if event["eventType"] not in allowed:
            continue
        rows.append(
            {
                "assetChronologyId": event["id"].replace("LH-EVT", "LH-ASSET-EVT"),
                "assetId": event["featureId"],
                "assetName": event["title"],
                "assetClass": event["eventType"],
                "milestoneState": event["status"],
                "earliestDate": event["dateStart"],
                "latestDate": event["dateEnd"] or event["dateStart"],
                "datePrecision": event["temporalPrecision"],
                "geometryId": "",
                "geometryStatus": "current_point_available" if event["eventType"] == "school" else "not_retrieved",
                "sourceIds": event["sourceIds"],
                "confidence": event["confidence"],
                "limitations": event["notes"] + " Construction interval and historical footprint are not established by this opening milestone.",
                "haulRouteStatus": "not_documented" if event["eventType"] == "utilities" else "not_applicable",
                "reviewStatus": "documented_opening_or_record_milestone",
            }
        )
    return rows


def source_convergence() -> list[dict[str, object]]:
    rows = []
    for claim in read_csv("claim_registry.csv"):
        supporting = [part for part in claim["supportingObservationIds"].split(";") if part]
        sources = {part.strip() for part in re.split(r"[;,]", claim["sourceIds"]) if part.strip()}
        rows.append(
            {
                "claimId": claim["claimId"],
                "supportingObservationCount": len(supporting),
                "independentSourceOrganizationCount": len(sources),
                "primarySourceCount": len(sources) if claim["confidence"] == "high" else 0,
                "contemporarySourceCount": 0,
                "visualSourceCount": 0,
                "conflictingObservationCount": 1 if claim["conflictStatus"] != "no_conflict_identified" else 0,
                "geographicPrecision": "tract_polygon" if claim["claimScope"] == "legal_subdivision" else "community_nonspatial",
                "temporalPrecision": claim["temporalPrecision"],
                "directness": claim["supportType"],
                "sourceAuthority": "official_primary" if claim["confidence"] == "high" else "mixed_or_secondary",
                "completeness": "claim_bounded" if sources and supporting else "incomplete",
                "finalConfidence": claim["confidence"],
                "confidenceRationale": "Counts are based on independent registered source IDs; copies of one source are not counted separately.",
                "exhaustionStatus": "authoritative_single_source" if len(sources) == 1 and claim["confidence"] == "high" else "additional_corroboration_useful",
                "limitations": claim["limitations"],
            }
        )
    return rows


def conflicts() -> list[dict[str, object]]:
    return [
        {
            "conflictId": "LH-CONFLICT-EIR-APPROVAL-DATE",
            "subjectId": "LH-FEAT-COMMUNITY",
            "conflictType": "different_entitlement_milestones_or_date_conflict",
            "positionA": "Final EIR 555 certification occurred 1995-10-17.",
            "positionAEvidenceIds": "LH-EVT-001",
            "positionASourceIds": "LH-SRC-OC-EIR-CERT",
            "positionB": "Developer retrospective describes County approval in 1997 without naming the action.",
            "positionBEvidenceIds": "LH-EVT-001B",
            "positionBSourceIds": "LH-SRC-RMV-PLANNING",
            "resolution": "Preserve both; use 1995-10-17 only for EIR certification and leave the 1997 action unresolved.",
            "confidence": "high",
            "reviewStatus": "open_scope_distinction",
        },
        {
            "conflictId": "LH-CONFLICT-SHARED-SCHOOL-OPENING",
            "subjectId": "LH-SCHOOL-LRES;LH-SCHOOL-LRMS",
            "conflictType": "month_grouping_versus_exact_date",
            "positionA": "Community timeline groups the school milestone in July 2003.",
            "positionAEvidenceIds": "LH-EVT-020;LH-EVT-021",
            "positionASourceIds": "LH-SRC-LARMAC-TIMELINE",
            "positionB": "Official school reports state the shared campus opened 2003-08-27.",
            "positionBEvidenceIds": "LH-EVT-023",
            "positionBSourceIds": "LH-SRC-CUSD-LRES;LH-SRC-CUSD-LRMS",
            "resolution": "Use 2003-08-27 for the school opening; retain July community park/library milestones separately.",
            "confidence": "high",
            "reviewStatus": "resolved_by_authoritative_source",
        },
    ]


def gaps() -> list[dict[str, object]]:
    values = [
        ("tract_lifecycle", "123 tracts", "grading, building, final, and occupancy records", "Orange County Planning/Public Works and permit archives", "private_or_manual_record_request", "critical"),
        ("historical_imagery", "1999-2010 annual states", "dated overlapping aerial frames", "USGS EarthExplorer and County aerial archives", "account_or_manual_archive_search", "critical"),
        ("occupancy_geometry", "residential areas", "certificates of occupancy, closings, or address-level activation", "County building records, Recorder, builders, HOA", "nonpublic_or_manual_record_request", "critical"),
        ("construction_geometry", "active development areas", "dated grading/as-built plans or adjacent imagery", "County plan sets and historical aerial programs", "manual_record_request", "critical"),
        ("tract_hierarchy", "123 tracts", "planning-area, village, neighborhood, builder/product crosswalk", "recorded maps, improvement plans, builder archives", "manual_crosswalk_and_records", "high"),
        ("school_boundaries", "1997-2010 attendance assignments", "dated attendance maps and board actions", "Capistrano Unified School District", "manual_district_request", "high"),
        ("roads", "community streets and arterials", "construction, partial opening, full opening, and access records", "Orange County Public Works", "manual_record_request", "high"),
        ("haul_routes", "construction access", "explicit approved route plans", "grading plans and conditions of approval", "manual_record_request", "high"),
        ("parks_facilities", "community amenities", "construction windows and historical footprints", "LARMAC, County, developer archives", "manual_archive_search", "medium"),
        ("commercial", "Bridgepark and later centers", "tenant openings, construction intervals, historical footprints", "planning files and newspaper archives", "manual_archive_search", "medium"),
        ("terrain_vertical_units", "2018 DEM", "explicit band-value unit or vertical datum", "Orange County OC Survey", "metadata_clarification", "medium"),
        ("wind_locality", "Ladera Ranch", "on-site study-period station observations", "agency or environmental-review archives", "not_located_publicly", "medium"),
    ]
    return [
        {
            "gapId": f"LH-GAP-M4-{index:03d}",
            "topic": topic,
            "scope": scope,
            "evidenceNeeded": needed,
            "recommendedRepository": repository,
            "searchOrAccessStatus": status,
            "priority": priority,
            "analyticalImpact": "Blocks dated spatial reconstruction or reduces historical precision.",
            "recommendedFollowUp": "Request and archive the named record class; preserve a no-record response if applicable.",
            "reviewStatus": "open",
        }
        for index, (topic, scope, needed, repository, status, priority) in enumerate(values, start=1)
    ]


def snapshots(events: list[dict[str, str]]) -> list[dict[str, object]]:
    schools = read_csv("schools.csv")
    imagery = {int(row["year"]): row for row in read_csv("imagery_coverage_matrix.csv")}
    annual = {int(row["year"]): row for row in read_csv("annual_snapshots.csv")}
    tract_years = [int(row["recordYear"]) for row in read_csv("tract_audit.csv")]
    latest_homes_sold = "0"
    rows = []
    for year in range(1997, 2011):
        open_schools = sorted(
            school["id"] for school in schools if school["openDate"] and int(school["openDate"][:4]) <= year
        )
        source_ids = set()
        milestones = []
        for event in events:
            if int(event["dateStart"][:4]) == year:
                milestones.append(event["id"])
                source_ids.update(part for part in re.split(r"[;,]", event["sourceIds"]) if part)
        legacy = annual.get(year)
        if legacy and legacy["homesSoldAsOf"]:
            latest_homes_sold = legacy["homesSoldAsOf"]
        annual_tract_count = sum(record_year == year for record_year in tract_years)
        cumulative_tract_count = sum(record_year <= year for record_year in tract_years)
        row = {
            "snapshotId": f"LH-SNAPSHOT-M4-{year}",
            "year": year,
            "snapshotType": "annual_evidence_manifest",
            "communityState": legacy["communityStatus"] if legacy else "not_reconstructed",
            "communityStatus": legacy["communityStatus"] if legacy else "no_new_community_state_established",
            "tractMapsRecordedByYear": annual_tract_count,
            "tractMapsRecordedCumulative": cumulative_tract_count,
            "homesSoldAsOf": latest_homes_sold,
            "activeSchoolCount": len(open_schools),
            "documentedMilestones": "; ".join(
                event["title"] for event in events if int(event["dateStart"][:4]) == year
            ) or "No new dated community milestone registered.",
            "milestoneEventIds": ";".join(milestones),
            "activeConstructionGeometryStatus": "not_supported",
            "habitableGeometryStatus": "not_supported",
            "occupiedGeometryStatus": "not_supported",
            "openSchoolIds": ";".join(open_schools),
            "openParkAndFacilityIds": ";".join(
                event["featureId"]
                for event in events
                if event["eventType"] in {"park", "clubhouse", "library", "commercial"}
                and int(event["dateStart"][:4]) <= year
            ),
            "imageryIds": imagery[year]["availableImageryIds"],
            "imageryCoverageStatus": imagery[year]["coverageStatus"],
            "proximityStatus": "blocked_missing_dated_subject_and_target_geometry",
            "windContextStatus": "regional_station_summary_available",
            "terrainContextStatus": "2018_post_study_context_available",
            "confidence": legacy["confidence"] if legacy else "unknown",
            "sourceIds": ";".join(sorted(source_ids)),
            "missingData": "construction geometry;habitability geometry;occupancy geometry;historical attendance boundary;historical facility footprints",
            "limitations": "Annual records are evidence manifests; unchanged or unavailable fields do not imply historical absence.",
        }
        rows.append(row)
        write_json(EXPORT / "snapshots" / f"{year}.json", row)
    return rows


def phase_snapshots(annual_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    definitions = [
        ("predevelopment_context", 1994, 1995, "Partial pre-development imagery context"),
        ("initial_development", 1997, 1999, "Entitlement claim, reported development start, sales, and first resident"),
        ("early_occupancy", 2000, 2001, "Community sales growth and first local school and facilities"),
        ("central_buildout", 2002, 2004, "Community sales milestones, shared school campus, parks, library, and clubhouses"),
        ("later_village_construction", 2005, 2008, "Oso Grande opening, later facilities, substantial completion, and sellout milestones"),
        ("later_buildout_context", 2009, 2010, "No new dated community milestone registered in the current public record set"),
    ]
    rows = []
    for index, (name, start, end, summary) in enumerate(definitions, start=1):
        included = [row for row in annual_rows if start <= int(row["year"]) <= end]
        source_ids = sorted({source for row in included for source in split_source_ids(str(row["sourceIds"]))})
        row = {
            "phaseSnapshotId": f"LH-PHASE-M4-{index:02d}",
            "phaseName": name,
            "validFromYear": start,
            "validToYear": end,
            "summary": summary,
            "includedAnnualSnapshotIds": ";".join(str(row["snapshotId"]) for row in included),
            "activeConstructionGeometryStatus": "not_supported",
            "habitableGeometryStatus": "not_supported",
            "occupiedGeometryStatus": "not_supported",
            "proximityStatus": "blocked_missing_dated_subject_and_target_geometry",
            "sourceIds": ";".join(source_ids),
            "confidence": "medium" if included else "low",
            "limitations": "Phase grouping summarizes documented milestones and does not manufacture physical state transitions between observations.",
        }
        rows.append(row)
        write_json(EXPORT / "phases" / f"{name}.json", row)
    return rows


def split_source_ids(value: str) -> list[str]:
    return [part.strip() for part in re.split(r"[;,]", value or "") if part.strip()]


def write_proximity_gate() -> None:
    fields = [
        "resultId", "subjectId", "subjectClass", "constructionActivityId", "constructionClass",
        "validFrom", "validTo", "analysisCrs", "minimumEdgeDistanceM", "centroidDistanceM",
        "temporalOverlapDays", "buffer25m", "buffer50m", "buffer100m", "buffer250m",
        "buffer500m", "buffer1000m", "subjectGeometryConfidence", "targetGeometryConfidence",
        "evidenceIds", "sourceIds", "limitations",
    ]
    write_csv("construction_proximity_results.csv", [], fields)
    write_csv("school_proximity_results.csv", [], fields)
    write_csv("neighborhood_overlap_results.csv", [], fields)
    blocked = []
    for subject_class in [
        "habitable_residential", "occupied_residential", "substantially_occupied_neighborhood",
        "open_school_campus", "open_park", "open_community_facility",
    ]:
        blocked.append(
            {
                "comparisonId": f"LH-PROX-BLOCK-{len(blocked) + 1:02d}",
                "subjectClass": subject_class,
                "subjectGeometryStatus": "not_dated_or_not_available",
                "targetGeometryStatus": "no_supported_active_construction_geometry",
                "temporalOverlapStatus": "cannot_evaluate",
                "analysisCrs": "EPSG:26946 selected but no calculation performed",
                "status": "blocked",
                "decision": "Do not calculate or substitute current boundaries, tract recording dates, centroids, or community-wide milestones.",
                "limitations": "An empty result table means the evidence gate did not open; it is not evidence of no nearby construction.",
            }
        )
    write_csv("blocked_proximity_comparisons.csv", blocked, list(blocked[0]))
    write_json(
        PROXIMITY / "status.json",
        {
            "status": "blocked",
            "analysisCrs": "EPSG:26946",
            "analysisCrsReason": "NAD83 / California zone 6 provides projected meter units for local distance analysis.",
            "buffersMeters": [25, 50, 100, 250, 500, 1000],
            "buffersFeetExact": [value * 3.280839895013123 for value in [25, 50, 100, 250, 500, 1000]],
            "subjectGate": "dated geometry with supported habitable, occupied, school, park, or facility interval",
            "targetGate": "dated active-construction geometry with supported activity class and interval",
            "subjectGateSatisfied": False,
            "targetGateSatisfied": False,
            "resultCount": 0,
            "notEvidenceOfAbsence": True,
            "limitations": "No metric distances were calculated because both evidence gates are unsatisfied.",
        },
    )


def write_docs(tracts: list[dict[str, object]], neighborhoods: list[dict[str, object]]) -> None:
    write_text(
        DOCS / "CONSTRUCTION_POLYGON_METHOD.md",
        """# Construction polygon method

## Evidence threshold

An observation polygon requires a dated image or dated plan, interpretable activity indicators, a repeatable geometry method, and direct provenance. A derived active interval additionally requires temporal bracketing. Overlapping activity classes remain separate.

## Mission 4 result

The two development-era County frames cover only part of the current CDP and do not form an adjacent-date sequence. No active-construction polygon was digitized. Empty construction layers mean **unsupported**, not **no construction**. Community development, utilities, and DSA project milestones are retained as nonspatial records and are not proximity eligible.

Bare open space is not classified as construction. Legal tract recording is not classified as construction. No construction-access or haul route is labeled without an explicit source.
""",
    )
    write_text(
        DOCS / "OCCUPANCY_RECONSTRUCTION_METHOD.md",
        """# Occupancy reconstruction method

Habitability, first occupancy, partial occupancy, substantial occupancy, completion, and current status are separate lifecycle concepts. Sales counts are not occupancy counts, and visual completion alone is not definitive occupancy evidence.

The community timeline documents a first resident on 1999-12-14 and cumulative sales milestones through 2008. It does not identify the resident's tract, neighborhood, or occupied footprint. All residential geometry outputs therefore remain empty with an explicit unsupported status. No whole tract or village is represented as occupied from a community-level event.
""",
    )
    write_text(
        DOCS / "TRACT_DEVELOPMENT_CHRONOLOGY.md",
        f"""# Tract development chronology

The matrix contains **{len(tracts)} tract rows**. Every row preserves its exact County map recording date and links to the corresponding legal-map observation. Physical-development fields remain blank because no standard duration or sequence was imposed.

Planning-area, village, neighborhood, builder, and product fields remain unresolved. The title sheets establish legal parties and selected map relationships, but those parties are not automatically builders and nested polygons are not automatically supersession.
""",
    )
    write_text(
        DOCS / "NEIGHBORHOOD_AND_ASSET_CHRONOLOGY.md",
        f"""# Neighborhood and asset chronology

All **{len(neighborhoods)} named villages** are represented, but their tract, builder-product, and residential lifecycle crosswalks remain unresolved. Documented clubhouse, park, library, commercial, utility, and school milestones are preserved in `asset_chronology.csv`. Opening dates do not establish construction start or historical footprints.

Road grading, road opening, and haul-route records were not located in the public sources reviewed. No route is inferred from proximity or present-day alignment.
""",
    )
    proximity_md = f"""# Historical construction proximity report

## Result

**Blocked. Zero comparisons were calculated.**

The subject gate requires a dated habitable or occupied residential geometry, substantially occupied neighborhood geometry, or dated open school, park, or facility geometry. The target gate requires a dated active-construction geometry and supported activity class. Neither gate is currently satisfied for any common interval.

EPSG:26946 is reserved for a future local meter-based analysis. Required buffers are 25, 50, 100, 250, 500, and 1,000 meters; exact meter-to-foot conversions are recorded in `data/processed/proximity/status.json`. Current tract boundaries, legal recording dates, centroids, community sales milestones, and present-day facility locations were not substituted.

An empty result means unsupported, not that no nearby construction existed.

## Safeguard

{DISCLAIMER}
"""
    write_text(DOCS / "PROXIMITY_ANALYSIS_METHOD.md", proximity_md)
    write_text(REPORTS / "LHDRS_Historical_Construction_Proximity_Report.md", proximity_md)
    escaped = proximity_md.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    write_text(
        REPORTS / "LHDRS_Historical_Construction_Proximity_Report.html",
        "<!doctype html><html lang=\"en\"><meta charset=\"utf-8\"><title>LHDRS Historical Construction Proximity Report</title>"
        "<style>body{font:16px/1.55 system-ui;max-width:860px;margin:48px auto;padding:0 24px;color:#18201d}pre{white-space:pre-wrap}"
        "h1{font-size:2rem}h2{margin-top:2rem}</style><body><pre>" + escaped + "</pre></body></html>\n",
    )


def main() -> int:
    events = read_csv("events.csv")
    construction = construction_registry()
    occupancy = occupancy_registry(events)
    tracts, tract_evidence = tract_matrices()
    neighborhoods = neighborhood_matrix()
    assets = asset_chronology(events)
    convergence = source_convergence()
    conflict_rows = conflicts()
    gap_rows = gaps()
    snapshot_rows = snapshots(events)
    phase_rows = phase_snapshots(snapshot_rows)

    write_csv("construction_activity_registry.csv", construction, list(construction[0]))
    write_csv("occupancy_event_registry.csv", occupancy, list(occupancy[0]))
    write_csv("tract_development_matrix.csv", tracts, list(tracts[0]))
    write_csv("tract_milestone_evidence.csv", tract_evidence, list(tract_evidence[0]))
    write_csv("neighborhood_occupancy_matrix.csv", neighborhoods, list(neighborhoods[0]))
    write_csv("asset_chronology.csv", assets, list(assets[0]))
    write_csv("source_convergence.csv", convergence, list(convergence[0]))
    write_csv("conflict_registry.csv", conflict_rows, list(conflict_rows[0]))
    write_csv("research_gaps.csv", gap_rows, list(gap_rows[0]))
    write_csv("annual_phase_snapshot_manifest.csv", snapshot_rows, list(snapshot_rows[0]))
    write_csv("phase_snapshot_manifest.csv", phase_rows, list(phase_rows[0]))

    write_json(
        GIS / "construction_intervals/status.geojson",
        empty_layer(
            "no_supported_active_construction_intervals",
            "No construction observation has both a defensible geometry and temporal interval.",
            ["LH-SRC-OC-IMAGERY", "LH-SRC-DGS-DSA-TRACKER"],
        ),
    )
    write_json(
        GIS / "habitability_observations/status.geojson",
        empty_layer(
            "no_supported_habitability_geometry",
            "Community milestones and visible roofs do not establish lawful or practical habitability geometry.",
            ["LH-SRC-LARMAC-TIMELINE", "LH-SRC-OC-IMAGERY"],
        ),
    )
    write_json(
        GIS / "occupancy_intervals/status.geojson",
        empty_layer(
            "no_supported_occupancy_geometry",
            "The first-resident event is community-level and cannot be assigned to a tract or neighborhood.",
            ["LH-SRC-LARMAC-TIMELINE"],
        ),
    )
    write_proximity_gate()
    write_docs(tracts, neighborhoods)
    print(
        "DONE  reconstruction: "
        f"{len(construction)} activities, {len(occupancy)} occupancy/sales events, "
        f"{len(tracts)} tracts, {len(neighborhoods)} neighborhoods, {len(snapshot_rows)} annual and {len(phase_rows)} phase snapshots"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
