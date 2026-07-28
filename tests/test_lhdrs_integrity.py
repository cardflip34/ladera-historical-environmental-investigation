#!/usr/bin/env python3
"""LHDRS integrity tests. Pure stdlib; runs under pytest or as a script."""

from __future__ import annotations

import csv
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import sys
from typing import Optional


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "research/development_chronology"
VALID_GRADES = {"A1", "A2", "B1", "B2", "C", "D"}
VALID_CONFIDENCE = {"high", "medium", "low", "unknown"}
VALID_PRECISION = {"day", "month", "year", "range", "unknown"}
VALID_STATEMENTS = {
    "documented_exact",
    "documented_approximate",
    "corroborated_secondary",
    "visual_interpretation",
    "estimate",
    "unresolved",
}


def rows(name: str) -> list[dict[str, str]]:
    with (BASE / name).open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def test_canonical_csv_rows_match_their_headers():
    for path in sorted(BASE.glob("*.csv")):
        with path.open(newline="", encoding="utf-8") as stream:
            data = list(csv.DictReader(stream))
        for index, row in enumerate(data, start=2):
            assert None not in row, f"extra columns in {path.name}:{index}"
            assert all(value is not None for value in row.values()), f"missing columns in {path.name}:{index}"


def source_ids() -> set[str]:
    return {row["id"] for row in rows("sources.csv")}


def split_ids(value: str) -> list[str]:
    return [item.strip() for item in re.split(r"[;,]", value) if item.strip()]


def parse_date(value: str) -> Optional[dt.date]:
    if not value:
        return None
    return dt.date.fromisoformat(value)


def test_source_registry_unique_and_graded():
    data = rows("sources.csv")
    ids = [row["id"] for row in data]
    assert len(ids) == len(set(ids)), "duplicate LHDRS source IDs"
    for row in data:
        assert row["reliabilityGrade"] in VALID_GRADES, f"bad source grade: {row['id']}"
        assert row["url"], f"source lacks URL: {row['id']}"
        assert row["knownLimitations"], f"source lacks limitations: {row['id']}"


def test_event_provenance_and_temporal_order():
    known = source_ids()
    for row in rows("events.csv"):
        assert row["sourceIds"], f"event lacks source: {row['id']}"
        assert set(split_ids(row["sourceIds"])) <= known, f"event has unknown source: {row['id']}"
        assert row["confidence"] in VALID_CONFIDENCE, f"event has bad confidence: {row['id']}"
        assert row["temporalPrecision"] in VALID_PRECISION, f"event has bad precision: {row['id']}"
        assert row["statementClass"] in VALID_STATEMENTS, f"event has bad statement class: {row['id']}"
        start = parse_date(row["dateStart"])
        end = parse_date(row["dateEnd"])
        assert start, f"event lacks start date: {row['id']}"
        assert not end or start <= end, f"event has reversed date range: {row['id']}"
        if row["statementClass"] in {"visual_interpretation", "estimate"}:
            assert row["interpretationMethod"], f"inferred event lacks method: {row['id']}"


def test_annual_snapshots_are_contiguous_and_sourced():
    known = source_ids()
    data = rows("annual_snapshots.csv")
    years = [int(row["year"]) for row in data]
    assert years == list(range(1997, 2009)), f"snapshot years not contiguous: {years}"
    for row in data:
        assert row["confidence"] in VALID_CONFIDENCE
        assert row["sourceIds"]
        assert set(split_ids(row["sourceIds"])) <= known
        assert row["limitations"]


def test_school_records_are_traceable():
    known = source_ids()
    for row in rows("schools.csv"):
        assert row["openDate"], f"school lacks opening date: {row['id']}"
        assert row["latitude"] and row["longitude"], f"school lacks coordinates: {row['id']}"
        assert row["geometryPrecision"], f"school lacks geometry precision: {row['id']}"
        assert set(split_ids(row["sourceIds"])) <= known


def test_all_nine_villages_are_explicit():
    data = rows("neighborhoods.csv")
    assert len(data) == 9, f"expected nine village records, found {len(data)}"
    for row in data:
        assert row["limitations"], f"village lacks limitations: {row['id']}"
        assert row["confidence"] in VALID_CONFIDENCE


def test_planning_area_totals_match_verified_table():
    data = rows("planning_areas.csv")
    totals = next(row for row in data if row["planningArea"] == "total")
    assert totals["maxDwellingUnits"] == "8100"
    assert totals["residentialNetAcres"] == "1989"
    assert totals["grossAcres"] == "2390"
    assert totals["schoolNetAcres"] == "40"
    assert totals["arterialRoadNetAcres"] == "83"


def test_obligations_are_not_misclassified_as_events():
    obligations = rows("development_obligations.csv")
    assert obligations
    for row in obligations:
        assert row["status"] == "requirement"
        assert row["limitations"]
        assert row["statementClass"] in VALID_STATEMENTS
    event_titles = " ".join(row["title"] for row in rows("events.csv")).lower()
    assert "building permits exceed" not in event_titles


def test_generated_geojson_is_valid_and_precise():
    expected = [
        ROOT / "data/development/ladera_ranch_cdp.geojson",
        ROOT / "data/development/tract_maps.geojson",
        ROOT / "data/development/schools.geojson",
        ROOT / "data/development/annual_snapshots.geojson",
    ]
    for path in expected:
        assert path.exists(), f"missing generated GIS: {path.relative_to(ROOT)}"
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data.get("type") == "FeatureCollection"
        assert data.get("features"), f"empty generated GIS: {path.relative_to(ROOT)}"
        for feature in data["features"]:
            assert feature.get("geometry", {}).get("coordinates"), f"geometry absent in {path.name}"

    tracts = json.loads(expected[1].read_text(encoding="utf-8"))["features"]
    for feature in tracts:
        props = feature["properties"]
        assert props.get("sourceId") == "LH-SRC-OC-TRACTS"
        assert props.get("recordDate") and props.get("recordYear")
        assert props.get("geometryPrecision")
        assert props.get("knownLimitations")


def test_generated_search_and_graph_outputs():
    tract_rows = list(csv.DictReader((ROOT / "data/development/tract_maps.csv").open(encoding="utf-8")))
    assert len(tract_rows) == 123
    assert all(row["recordDate"] and row["knownLimitations"] for row in tract_rows)

    graph = json.loads((ROOT / "data/development/knowledge_graph.json").read_text(encoding="utf-8"))
    assert graph["nodes"] and graph["edges"]
    assert all(edge["sourceIds"] for edge in graph["edges"])


def test_lhdrs_tables_do_not_make_health_or_exposure_claims():
    forbidden = re.compile(r"\b(caused|causes|exposure|toxicology|health risk|contamination)\b", re.I)
    for name in ["events.csv", "annual_snapshots.csv", "schools.csv", "neighborhoods.csv"]:
        text = (BASE / name).read_text(encoding="utf-8")
        assert not forbidden.search(text), f"out-of-scope claim language in {name}"


def test_proximity_analysis_stays_blocked_without_required_geometry():
    todo = {row["id"]: row for row in rows("unresolved_questions.csv")}
    item = todo["LH-TODO-012"]
    assert item["status"] == "blocked"
    assert "occupied" in item["evidenceNeeded"] and "construction" in item["evidenceNeeded"]
    analysis = rows("proximity_analysis_status.csv")[0]
    assert analysis["status"] == "blocked"
    assert analysis["statementClass"] == "unresolved"
    assert "Do not calculate" in analysis["decision"]


def test_mission4_tract_audit_preserves_lifecycle_boundary():
    audit = rows("tract_audit.csv")
    assert len(audit) == 123
    assert len({row["tractId"] for row in audit}) == 123
    assert all(row["analysisCrs"] == "EPSG:26946" for row in audit)
    assert all(row["recordingObservation"] == "legal_tract_map_recorded" for row in audit)
    assert all(row["constructionConclusion"] == "not_established" for row in audit)
    assert all(row["habitabilityConclusion"] == "not_established" for row in audit)
    assert all(row["occupancyConclusion"] == "not_established" for row in audit)
    assert sum(row["originalGeometryValid"] == "false" for row in audit) == 8


def test_mission4_crosswalk_is_projected_and_review_gated():
    crosswalk = rows("tract_crosswalk.csv")
    assert crosswalk
    assert len({row["relationshipId"] for row in crosswalk}) == len(crosswalk)
    assert all(float(row["intersectionAreaSqM"]) > 1 for row in crosswalk)
    assert all(row["analysisCrs"] == "EPSG:26946" for row in crosswalk)
    assert all(
        row["reviewStatus"]
        in {"legal_map_relationship_review_required", "documented_title_sheet_relationship"}
        for row in crosswalk
    )
    assert all(row["lifecycleConclusion"] == "not_established" for row in crosswalk)
    assert not any("supersed" in row["relationshipType"].lower() for row in crosswalk)


def test_mission4_title_sheet_index_is_complete_and_bounded():
    title_sheets = rows("tract_title_sheet_index.csv")
    assert len(title_sheets) == 123
    assert all(row["sourceIds"] == "LH-SRC-OC-LMS-TRACT-PDFS" for row in title_sheets)
    assert all(row["constructionConclusion"] == "not_established" for row in title_sheets)
    assert all(row["occupancyConclusion"] == "not_established" for row in title_sheets)
    assert any(row["normalizedParentTractIds"] for row in title_sheets)
    assert all("not_necessarily_builder" in row["partyInterpretation"] for row in title_sheets)


def test_mission4_wind_context_is_observed_and_regionally_bounded():
    inventory = rows("wind_station_inventory.csv")
    annual = rows("wind_annual_summary.csv")
    monthly = rows("wind_monthly_summary.csv")
    assert any(row["stationContextId"] == "LH-WIND-EL-TORO" and row["selected"] == "true" for row in inventory)
    assert any(row["stationContextId"] == "LH-WIND-JOHN-WAYNE" and row["selected"] == "true" for row in inventory)
    john_wayne_years = [int(row["year"]) for row in annual if row["stationContextId"] == "LH-WIND-JOHN-WAYNE"]
    el_toro_years = [int(row["year"]) for row in annual if row["stationContextId"] == "LH-WIND-EL-TORO"]
    assert john_wayne_years == list(range(1997, 2011))
    assert el_toro_years == [1997, 1999, 2000]
    assert len(monthly) == 17 * 12
    for row in annual:
        assert 0 <= float(row["validSpeedCoveragePct"]) <= 100
        assert 0 <= float(row["easterlyPct"]) <= 100
        assert row["timeBasis"] == "UTC"
        assert "Regional station" in row["limitations"]


def test_mission4_terrain_context_is_complete_and_temporally_bounded():
    community = rows("terrain_summary.csv")
    tracts = rows("tract_terrain_summary.csv")
    drainage = rows("drainage_context.csv")
    assert len(community) == 1
    assert len(tracts) == 123
    assert all(int(row["pixelCount"]) > 0 for row in tracts)
    assert all(row["demNominalYear"] == "2018" for row in community + tracts)
    assert all(row["confidence"] == "medium" for row in community + tracts)
    assert all("not a 1997-2010 surface" in row["limitations"] for row in community + tracts)
    assert {row["contextType"] for row in drainage} == {
        "watershed_boundary",
        "lidar_derived_stream_centerline",
        "flood_control_infrastructure",
    }
    assert all("not evidence of material movement" in row["limitations"] for row in drainage)


def test_mission4_school_timeline_does_not_invent_boundaries_or_footprints():
    projects = rows("school_project_registry.csv")
    timeline = rows("school_timeline.csv")
    boundaries = rows("school_boundary_history.csv")
    assert len(projects) == 3
    assert len(timeline) == 15
    assert [int(row["year"]) for row in boundaries] == list(range(1997, 2011))
    assert all(row["constructionStartConclusion"] == "not_exactly_established" for row in projects)
    assert all(row["proximityEligible"] == "false" and not row["geometryId"] for row in projects)
    assert all(not row["documentedAssignedSchoolIds"] for row in boundaries)
    assert all(row["geometryStatus"] == "unavailable" for row in boundaries)
    assert all(row["reviewStatus"] == "blocked_pending_district_records" for row in boundaries)
    status = json.loads(
        (ROOT / "data/gis/ladera_development/school_attendance_areas/status.geojson").read_text()
    )
    assert status["features"] == []
    assert status["notEvidenceOfAbsence"] is True


def test_mission4_imagery_inventory_preserves_coverage_limits():
    inventory = rows("imagery_inventory.csv")
    matrix = rows("imagery_coverage_matrix.csv")
    reviews = rows("construction_interpretation_log.csv")
    assert len(inventory) >= 5
    assert [row["captureDateEarliest"] for row in inventory] == sorted(
        row["captureDateEarliest"] for row in inventory
    )
    development_frames = [row for row in inventory if row["id"].startswith("LH-IMG-199")]
    assert {row["id"] for row in development_frames} == {
        "LH-IMG-1994-1995",
        "LH-IMG-1997-1998",
    }
    assert all(row["coverage"] == "partial" for row in development_frames)
    assert [int(row["year"]) for row in matrix] == list(range(1997, 2011))
    assert all(
        row["constructionPolygonStatus"] in {"not_supported", "visible_disturbance_regions_not_proximity_eligible"}
        for row in matrix
    )
    mission5_frames = [row for row in inventory if row["id"].startswith("LH-IMG-NAIP-")]
    assert {row["id"] for row in mission5_frames} == {
        "LH-IMG-NAIP-2005", "LH-IMG-NAIP-2009", "LH-IMG-NAIP-2010"
    }
    assert all(row["proximityEligible"] == "false" and not row["geometryId"] for row in reviews)
    status = json.loads(
        (ROOT / "data/gis/ladera_development/construction_observations/status.geojson").read_text()
    )
    assert status["features"] == []
    assert status["notEvidenceOfAbsence"] is True


def test_mission4_reconstruction_matrices_preserve_unknowns():
    activities = rows("construction_activity_registry.csv")
    occupancy = rows("occupancy_event_registry.csv")
    tracts = rows("tract_development_matrix.csv")
    tract_evidence = rows("tract_milestone_evidence.csv")
    neighborhoods = rows("neighborhood_occupancy_matrix.csv")
    assert len(activities) >= 5
    assert all(row["proximityEligible"] == "false" and not row["geometryId"] for row in activities)
    assert len(occupancy) >= 13
    assert sum(row["eventClass"] == "first_documented_resident" for row in occupancy) == 1
    assert all(row["proximityEligible"] == "false" and not row["geometryId"] for row in occupancy)
    assert len(tracts) == len(tract_evidence) == 123
    physical_fields = [
        "gradingStartRange",
        "gradingEndRange",
        "infrastructureRange",
        "roadConstructionRange",
        "verticalConstructionRange",
        "earliestHabitabilityRange",
        "firstOccupancyRange",
        "completionRange",
    ]
    assert all(all(not row[field] for field in physical_fields) for row in tracts)
    assert all(row["physicalLifecycleMeaning"] == "none_established" for row in tract_evidence)
    assert len(neighborhoods) == 9
    assert all(row["geometryStatus"] == "not_available" for row in neighborhoods)
    assert all(not row["firstOccupancy"] for row in neighborhoods)


def test_mission4_proximity_gate_emits_no_false_results():
    assert rows("construction_proximity_results.csv") == []
    assert rows("school_proximity_results.csv") == []
    assert rows("neighborhood_overlap_results.csv") == []
    blocked = rows("blocked_proximity_comparisons.csv")
    assert len(blocked) == 6
    assert all(row["status"] == "blocked" for row in blocked)
    status = json.loads((ROOT / "data/processed/proximity/status.json").read_text())
    assert status["subjectGateSatisfied"] is False
    assert status["targetGateSatisfied"] is False
    assert status["resultCount"] == 0
    assert status["analysisCrs"] == "EPSG:26946"
    assert status["notEvidenceOfAbsence"] is True
    assert len(status["buffersFeetExact"]) == 6


def test_mission4_snapshot_manifests_do_not_invent_annual_geometry():
    snapshots = rows("annual_phase_snapshot_manifest.csv")
    assert [int(row["year"]) for row in snapshots] == list(range(1997, 2011))
    assert all(row["activeConstructionGeometryStatus"] == "not_supported" for row in snapshots)
    assert all(row["habitableGeometryStatus"] == "not_supported" for row in snapshots)
    assert all(row["occupiedGeometryStatus"] == "not_supported" for row in snapshots)
    assert all(row["proximityStatus"].startswith("blocked") for row in snapshots)
    for row in snapshots:
        snapshot = json.loads(
            (ROOT / f"data/exports/atlas_second_edition/snapshots/{row['year']}.json").read_text()
        )
        assert snapshot["snapshotId"] == row["snapshotId"]


def test_mission4_convergence_conflicts_and_gaps_are_explicit():
    convergence = rows("source_convergence.csv")
    conflicts = rows("conflict_registry.csv")
    gaps = rows("research_gaps.csv")
    assert len(convergence) == len(rows("claim_registry.csv"))
    assert all(row["confidenceRationale"] for row in convergence)
    assert len(conflicts) >= 2
    assert all(row["positionAEvidenceIds"] and row["positionBEvidenceIds"] for row in conflicts)
    assert any(row["topic"] == "occupancy_geometry" and row["priority"] == "critical" for row in gaps)
    assert any(row["topic"] == "construction_geometry" and row["priority"] == "critical" for row in gaps)


def test_mission4_temporal_ordering_and_exceptions_are_explicit():
    for activity in rows("construction_activity_registry.csv"):
        earliest_start = parse_date(activity["earliestStart"])
        latest_start = parse_date(activity["latestStart"])
        earliest_end = parse_date(activity["earliestEnd"])
        latest_end = parse_date(activity["latestEnd"])
        assert not earliest_start or not latest_start or earliest_start <= latest_start
        assert not earliest_end or not latest_end or earliest_end <= latest_end
        assert not latest_start or not earliest_end or latest_start <= earliest_end
    for project in rows("school_project_registry.csv"):
        opening = parse_date(project["campusOpenEarliest"])
        certification = parse_date(project["certificationDate"])
        assert opening and certification and opening <= certification
        assert "administrative" in project["limitations"].lower()
        assert project["proximityEligible"] == "false"


def test_mission4_archives_and_public_paths_are_resolvable():
    for source in rows("sources.csv"):
        if source["archiveStatus"] in {"retrieved", "retrieved_collection", "local_copy"}:
            assert source["localFilePath"]
            assert not Path(source["localFilePath"]).is_absolute()
            assert (ROOT / source["localFilePath"]).exists(), source["id"]
    public_text_paths = [
        ROOT / "reports/LHDRS_Historical_Development_Atlas_Second_Edition.md",
        ROOT / "reports/LHDRS_Historical_Development_Atlas_Second_Edition.html",
        ROOT / "reports/LHDRS_Historical_Construction_Proximity_Report.md",
        ROOT / "reports/LHDRS_Historical_Construction_Proximity_Report.html",
        ROOT / "reports/LHDRS_Wind_and_Terrain_Context.html",
    ]
    for path in public_text_paths:
        text = path.read_text(encoding="utf-8")
        assert "/Users/" not in text
        assert "file://" not in text


def test_mission4_graph_edges_are_versioned_and_inspectable():
    graph_rows = rows("knowledge_graph.csv")
    assert len(graph_rows) > 18
    assert all(row["evidenceIds"] for row in graph_rows)
    assert all(row["sourceIds"] for row in graph_rows)
    assert all(row["confidence"] and row["version"] and row["reviewStatus"] for row in graph_rows)
    graph = json.loads((ROOT / "data/development/knowledge_graph.json").read_text())
    assert len(graph["nodes"]) >= 700
    assert len(graph["edges"]) == len(graph_rows)
    inspector = json.loads((ROOT / "data/development/evidence_inspector.json").read_text())
    assert inspector["recordCount"] == 127
    assert len(inspector["records"]) == 127
    assert all(record["whyShown"] and record["confidenceRationale"] for record in inspector["records"].values())


def test_mission4_second_edition_is_distinct_complete_and_checksummed():
    first_html = ROOT / "reports/LHDRS_Historical_Development_Atlas.html"
    second_html = ROOT / "reports/LHDRS_Historical_Development_Atlas_Second_Edition.html"
    second_md = ROOT / "reports/LHDRS_Historical_Development_Atlas_Second_Edition.md"
    assert first_html.exists() and second_html.exists() and second_md.exists()
    assert first_html.read_bytes() != second_html.read_bytes()
    markdown = second_md.read_text(encoding="utf-8")
    assert len(re.findall(r"^### (?:199[7-9]|200[0-9]|2010):", markdown, re.M)) == 14
    assert "They are not measurements of individual exposure, contamination, health risk, or disease causation." in markdown
    phases = rows("phase_snapshot_manifest.csv")
    assert len(phases) == 6
    assert all(row["activeConstructionGeometryStatus"] == "not_supported" for row in phases)
    manifest = json.loads((ROOT / "data/exports/atlas_second_edition/publication_manifest.json").read_text())
    assert manifest["annualChapterCount"] == 14
    assert manifest["firstEditionPreserved"] is True
    assert manifest["proximityResultCount"] == 0
    for item in manifest["files"]:
        path = ROOT / item["path"]
        assert path.exists()
        assert path.stat().st_size == item["bytes"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == item["sha256"]


def test_mission4_context_publication_assets_exist():
    expected = [
        "terrain_elevation.png",
        "terrain_hillshade.png",
        "terrain_slope.png",
        "terrain_aspect.png",
        "terrain_watershed.png",
        "terrain_drainage.png",
        "wind_annual_context.png",
    ]
    for name in expected:
        path = ROOT / "reports/assets/lhdrs_context" / name
        assert path.exists() and path.stat().st_size > 10_000
    assert (ROOT / "reports/LHDRS_Wind_and_Terrain_Context.html").exists()
    metadata = json.loads((ROOT / "data/processed/wind/metadata.json").read_text())
    assert metadata["regionalOnly"] is True
    assert metadata["downscaled"] is False
    assert metadata["movementModel"] is False


def test_mission4_geographic_hierarchy_keeps_unknown_parents_blank():
    hierarchy = rows("geographic_hierarchy.csv")
    assert sum(row["nodeType"] == "community" for row in hierarchy) == 1
    assert sum(row["nodeType"] == "planning_area" for row in hierarchy) == 8
    assert sum(row["nodeType"] == "village" for row in hierarchy) == 9
    tracts = [row for row in hierarchy if row["nodeType"] == "recorded_tract_map"]
    assert len(tracts) == 123
    assert all(not row["parentNodeId"] for row in tracts)
    assert all(row["relationshipStatus"] == "historical_parent_unresolved" for row in tracts)


def test_mission4_evidence_models_are_separate_and_traceable():
    observations = rows("historical_observations.csv")
    claims = rows("claim_registry.csv")
    intervals = rows("lifecycle_intervals.csv")
    observation_ids = {row["observationId"] for row in observations}
    assert len(observations) >= 157
    assert len(claims) == len(observations) == len(rows("source_convergence.csv"))
    assert all(set(split_ids(row["sourceIds"])) <= source_ids() for row in observations)
    assert all(set(split_ids(row["supportingObservationIds"])) <= observation_ids for row in claims)
    tract_claims = [row for row in claims if row["claimScope"] == "legal_subdivision"]
    assert len(tract_claims) == 123
    assert all("physical-development lifecycle" in row["limitations"] for row in tract_claims)
    assert len(intervals) >= 12
    assert all(row["proximityEligible"] == "false" for row in intervals)
    assert all(not row["geometryId"] for row in intervals)


def _run() -> int:
    tests = [value for name, value in sorted(globals().items()) if name.startswith("test_") and callable(value)]
    failures = 0
    for test in tests:
        try:
            test()
            print(f"  PASS  {test.__name__}")
        except (AssertionError, KeyError, ValueError) as exc:
            failures += 1
            print(f"  FAIL  {test.__name__}: {exc}")
    print(f"\n{len(tests) - failures}/{len(tests)} passed.")
    return failures


if __name__ == "__main__":
    sys.exit(1 if _run() else 0)
