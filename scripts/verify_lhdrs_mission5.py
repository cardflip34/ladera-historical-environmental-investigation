#!/usr/bin/env python3
"""Verify Mission 5 acquisition, reconstruction, graph, and publication outputs."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "research/development_chronology"
EVIDENCE = ROOT / "evidence/lhdrs/mission5"


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as stream:
        return list(csv.DictReader(stream))


def table(name: str) -> list[dict[str, str]]:
    return rows(BASE / name)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def split_ids(value: str) -> list[str]:
    return [item.strip() for item in re.split(r"[;,]", value or "") if item.strip()]


def check(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def verify() -> dict[str, int]:
    acquisition = rows(EVIDENCE / "acquisition_manifest.csv")
    acquisition_summary = json.loads((EVIDENCE / "acquisition_summary.json").read_text())
    check(len(acquisition) == 30, "expected 30 acquisition rows")
    check(all(row["archiveStatus"] == "retrieved" for row in acquisition), "an acquisition failed")
    check(
        digest(EVIDENCE / "acquisition_manifest.csv") == acquisition_summary["manifestChecksumSha256"],
        "acquisition manifest checksum does not match summary",
    )
    for row in acquisition:
        path = ROOT / row["localFilePath"]
        check(path.exists() and path.stat().st_size == int(row["bytes"]), f"bad acquisition size: {row['sourceId']}")
        check(digest(path) == row["checksumSha256"], f"bad acquisition checksum: {row['sourceId']}")

    extraction = rows(EVIDENCE / "extraction_log.csv")
    check(len(extraction) == 25 and all(row["status"] == "extracted" for row in extraction), "text extraction incomplete")
    for row in extraction:
        path = ROOT / row["outputFile"]
        check(path.exists() and digest(path) == row["outputChecksumSha256"], f"bad extraction: {row['sourceId']}")

    sources = table("sources.csv")
    source_ids = {row["id"] for row in sources}
    check({row["sourceId"] for row in acquisition} <= source_ids, "acquired source missing from registry")
    for row in sources:
        if row["archiveStatus"] in {"retrieved", "retrieved_collection", "local_copy"}:
            check((ROOT / row["localFilePath"]).exists(), f"registered archive missing: {row['id']}")

    check(len(table("street_neighborhood_registry.csv")) == 484, "street directory row drift")
    check(len(table("neighborhood_chronology_mission5.csv")) == 130, "neighborhood chronology row drift")
    products = table("builder_product_chronology.csv")
    primary = [row for row in products if row["cfdPhase"]]
    check(len(products) == 69 and len(primary) == 27, "builder product row drift")
    conflicts = table("conflict_registry.csv")
    check(sum(row["conflictId"].startswith("LH-CONFLICT-M5-BUILDER-") for row in conflicts) == 12, "builder conflicts not preserved")
    check(any(row["conflictId"] == "LH-CONFLICT-M5-FIRST-RESIDENT" for row in conflicts), "first-resident conflict missing")

    absorption = table("cfd_absorption_chronology.csv")
    totals: dict[str, int] = {}
    for row in absorption:
        totals[row["district"]] = totals.get(row["district"], 0) + int(row["builtAndOccupiedUnits"])
    check(totals == {
        "CFD 99-1 Phase I": 1129,
        "CFD 2002-1 Urban Activity Center": 386,
        "CFD 2003-1 Phase V": 1242,
        "CFD 2004-1 Phase VI": 892,
    }, f"absorption totals differ: {totals}")
    phase_v = [row for row in primary if row["cfdPhase"] == "Phase V"]
    phase_vi = [row for row in primary if row["cfdPhase"] == "Phase VI"]
    check(sum(int(row["unitsPlanned"]) for row in phase_v) == 1259, "Phase V planned total")
    check(sum(int(row["permitsBy2006"]) for row in phase_v) == 1259, "Phase V permit total")
    check(sum(int(row["escrowsBy2006"]) for row in phase_v) == 1242, "Phase V escrow total")
    check(sum(int(row["unitsPlanned"]) for row in phase_vi) == 1006, "Phase VI planned total")
    check(sum(int(row["permitsBy2006"] or 0) for row in phase_vi) == 731, "Phase VI permit total")
    check(sum(int(row["escrowsBy2006"]) for row in phase_vi) == 705, "Phase VI 2006 escrow total")
    check(sum(int(row["escrowsBy2011"] or 0) for row in phase_vi) == 892, "Phase VI 2011 escrow total")

    crosswalk = table("tract_neighborhood_crosswalk.csv")
    lifecycle = table("tract_lifecycle_reconstruction.csv")
    check(len(crosswalk) == 147 and len(lifecycle) == 123, "tract reconstruction row drift")
    check(sum(bool(row["neighborhoodCandidates"]) for row in lifecycle) == 116, "mapped tract count drift")
    check(all(row["firstOccupancy"] == "unknown" and row["verticalConstruction"] == "unknown" for row in lifecycle), "tract lifecycle overclaim")

    imagery = {row["id"]: row for row in table("imagery_inventory.csv")}
    for year in (2005, 2009, 2010):
        row = imagery[f"LH-IMG-NAIP-{year}"]
        check(row["coverage"] == "full current Ladera CDP and surrounding AOI", f"imagery coverage: {year}")
    check(len(table("commercial_asset_chronology_mission5.csv")) == 8, "commercial status row drift")

    observations = table("historical_observations.csv")
    claims = table("claim_registry.csv")
    convergence = table("source_convergence.csv")
    observation_ids = {row["observationId"] for row in observations}
    claim_ids = {row["claimId"] for row in claims}
    check(claim_ids == {row["claimId"] for row in convergence}, "claim/convergence mismatch")
    for row in observations:
        check(set(split_ids(row["sourceIds"])) <= source_ids, f"unknown observation source: {row['observationId']}")
    for row in claims:
        check(set(split_ids(row["supportingObservationIds"])) <= observation_ids, f"unknown claim observation: {row['claimId']}")

    for name in ("construction_activity_registry.csv", "occupancy_event_registry.csv", "lifecycle_intervals.csv"):
        for row in table(name):
            check(row["proximityEligible"] == "false", f"unexpected proximity eligibility in {name}")
    check(table("construction_proximity_results.csv") == [], "construction proximity results must remain empty")

    graph = json.loads((ROOT / "data/development/knowledge_graph.json").read_text())
    check(len(graph["nodes"]) >= 1200 and len(graph["edges"]) >= 1600, "Mission 5 graph incomplete")
    for edge in graph["edges"]:
        check(edge["sourceIds"] and set(edge["sourceIds"]) <= source_ids, f"unknown graph source: {edge['edgeId']}")
        check(edge["evidenceIds"], f"graph edge lacks evidence: {edge['edgeId']}")

    atlas_manifest = json.loads((ROOT / "data/exports/atlas_mission5/publication_manifest.json").read_text())
    check(atlas_manifest["proximityResultCount"] == 0, "atlas proximity result gate")
    for item in atlas_manifest["files"]:
        path = ROOT / item["path"]
        check(path.exists() and path.stat().st_size == item["bytes"], f"atlas file missing: {item['path']}")
        check(digest(path) == item["sha256"], f"atlas checksum: {item['path']}")
    for report_name in ("LHDRS_Historical_Evidence_Atlas_Mission_5.html", "LHDRS_Historical_Evidence_Atlas_Mission_5.md"):
        report = (ROOT / "reports" / report_name).read_text(encoding="utf-8")
        check("/Users/" not in report and "file://" not in report, f"private path in {report_name}")

    queue = table("highest_value_research_queue.csv")
    check(len(queue) == 7 and all(row["manualRecordRequired"] == "true" for row in queue), "manual queue incomplete")
    return {
        "acquisitions": len(acquisition), "sources": len(sources), "observations": len(observations),
        "claims": len(claims), "graphNodes": len(graph["nodes"]), "graphEdges": len(graph["edges"]),
        "atlasFiles": len(atlas_manifest["files"]), "manualQueueItems": len(queue),
    }


if __name__ == "__main__":
    try:
        result = verify()
    except AssertionError as exc:
        print(f"FAIL  {exc}")
        sys.exit(1)
    print("PASS  Mission 5 verification")
    print(json.dumps(result, indent=2))
