#!/usr/bin/env python3
"""Build the LHDRS evidence graph, graph queries, and inspector index."""

from __future__ import annotations

from collections import Counter, defaultdict
import csv
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "research/development_chronology"
DATA = ROOT / "data/development"
PUBLIC = ROOT / "apps/web/public/development"
DOCS = ROOT / "docs/lhdrs"
ASSETS = ROOT / "reports/assets/lhdrs_graph"


def read_csv(name: str) -> list[dict[str, str]]:
    with (BASE / name).open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def split_ids(value: str) -> list[str]:
    return [item.strip() for item in re.split(r"[;,]", value or "") if item.strip()]


def slug(value: str) -> str:
    return re.sub(r"[^A-Z0-9]+", "-", value.upper()).strip("-")


def write_csv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
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


class Graph:
    fields = [
        "edgeId", "fromId", "fromType", "relationship", "toId", "toType", "validFrom",
        "validTo", "evidenceIds", "sourceIds", "confidence", "version", "reviewStatus",
        "limitations", "notes",
    ]

    def __init__(self) -> None:
        self.nodes: dict[str, dict[str, object]] = {}
        self.edges: list[dict[str, object]] = []
        self._keys: set[tuple[str, str, str]] = set()
        self._counter = 0

    def node(self, node_id: str, node_type: str, label: str = "", **properties: object) -> None:
        current = self.nodes.setdefault(
            node_id,
            {"id": node_id, "type": node_type, "label": label or node_id},
        )
        if label and current.get("label") == node_id:
            current["label"] = label
        current.update({key: value for key, value in properties.items() if value not in {None, ""}})

    def edge(
        self,
        from_id: str,
        from_type: str,
        relationship: str,
        to_id: str,
        to_type: str,
        source_ids: str,
        *,
        valid_from: str = "",
        valid_to: str = "",
        evidence_ids: str = "",
        confidence: str = "unknown",
        review_status: str = "reviewed",
        limitations: str = "",
        notes: str = "",
        edge_id: str = "",
        version: str = "3.0",
    ) -> None:
        key = (from_id, relationship, to_id)
        if key in self._keys:
            return
        self._keys.add(key)
        self._counter += 1
        self.node(from_id, from_type)
        self.node(to_id, to_type)
        self.edges.append(
            {
                "edgeId": edge_id or f"LH-EDGE-M5-{self._counter:05d}",
                "fromId": from_id,
                "fromType": from_type,
                "relationship": relationship,
                "toId": to_id,
                "toType": to_type,
                "validFrom": valid_from,
                "validTo": valid_to,
                "evidenceIds": evidence_ids,
                "sourceIds": source_ids,
                "confidence": confidence,
                "version": version,
                "reviewStatus": review_status,
                "limitations": limitations,
                "notes": notes,
            }
        )


def add_preserved_edges(graph: Graph) -> None:
    for row in read_csv("knowledge_graph.csv"):
        if not re.fullmatch(r"LH-EDGE-\d{3}", row["edgeId"]):
            continue
        graph.edge(
            row["fromId"], row["fromType"], row["relationship"], row["toId"], row["toType"],
            row["sourceIds"], confidence=row["confidence"], notes=row.get("notes", ""),
            evidence_ids=row["sourceIds"], review_status="preserved_first_edition_edge",
            limitations="First-edition relationship retained and normalized to the Mission 4 edge schema.",
            edge_id=row["edgeId"], version="1.0",
        )


def add_sources(graph: Graph) -> None:
    for source in read_csv("sources.csv"):
        graph.node(
            source["id"], "Source", source["title"], publisher=source["publisher"],
            reliabilityGrade=source["reliabilityGrade"], archiveStatus=source["archiveStatus"],
        )
        if source["localFilePath"]:
            archive_id = "LH-ARCHIVE-" + hashlib.sha1(source["localFilePath"].encode()).hexdigest()[:12].upper()
            graph.node(archive_id, "ArchivedFile", Path(source["localFilePath"]).name, localPath=source["localFilePath"])
            graph.edge(
                source["id"], "Source", "archived_as", archive_id, "ArchivedFile", source["id"],
                valid_from=source["retrievalDate"], evidence_ids=source["id"], confidence="high",
                limitations=source["knownLimitations"], notes=source["checksumSha256"],
            )


def add_claims_and_observations(graph: Graph) -> None:
    observations = {row["observationId"]: row for row in read_csv("historical_observations.csv")}
    for observation in observations.values():
        graph.node(
            observation["observationId"], "HistoricalObservation", observation["observedValue"],
            observationType=observation["observationType"], confidence=observation["confidence"],
        )
        graph.edge(
            observation["observationId"], "HistoricalObservation", "observes",
            observation["observedEntityId"], "HistoricalObject", observation["sourceIds"],
            valid_from=observation["dateStart"], valid_to=observation["dateEnd"],
            evidence_ids=observation["observationId"], confidence=observation["confidence"],
            limitations=observation["limitations"],
        )
        for source_id in split_ids(observation["sourceIds"]):
            graph.edge(
                observation["observationId"], "HistoricalObservation", "derived_from",
                source_id, "Source", source_id, evidence_ids=observation["observationId"],
                confidence=observation["confidence"], limitations=observation["limitations"],
            )
    for claim in read_csv("claim_registry.csv"):
        graph.node(
            claim["claimId"], "Claim", claim["claimText"], claimType=claim["claimType"],
            confidence=claim["confidence"], reviewStatus=claim["reviewStatus"],
        )
        for observation_id in split_ids(claim["supportingObservationIds"]):
            graph.edge(
                claim["claimId"], "Claim", "supported_by", observation_id,
                "HistoricalObservation", claim["sourceIds"], valid_from=claim["dateStart"],
                valid_to=claim["dateEnd"], evidence_ids=observation_id,
                confidence=claim["confidence"], review_status=claim["reviewStatus"],
                limitations=claim["limitations"],
            )


def add_reconstruction(graph: Graph) -> None:
    for row in read_csv("tract_milestone_evidence.csv"):
        graph.node(row["tractId"], "RecordedTract", row["tractId"].replace("LH-TRACT-", "Tract "))
        graph.node(row["tractMilestoneEvidenceId"], "MilestoneEvidence", "Legal map recording")
        graph.edge(
            row["tractId"], "RecordedTract", "has_legal_milestone", row["tractMilestoneEvidenceId"],
            "MilestoneEvidence", row["sourceIds"], valid_from=row["earliestDate"],
            valid_to=row["latestDate"], evidence_ids=row["evidenceId"], confidence=row["confidence"],
            review_status=row["reviewStatus"], limitations=row["limitations"],
        )
    for row in read_csv("tract_crosswalk.csv"):
        if row["reviewStatus"] != "documented_title_sheet_relationship":
            continue
        graph.edge(
            row["fromTractId"], "RecordedTract", "title_sheet_references",
            row["toTractId"], "RecordedTract", row["sourceIds"],
            evidence_ids=row["relationshipId"], confidence=row["confidence"],
            review_status=row["reviewStatus"], limitations=row["limitations"],
            notes="Legal map relationship only; no lifecycle supersession is inferred.",
        )
    for row in read_csv("tract_neighborhood_crosswalk.csv"):
        neighborhood_id = f"LH-NEIGHBORHOOD-{slug(row['village'])}-{slug(row['neighborhood'])}"
        graph.node(neighborhood_id, "CurrentNeighborhood", row["neighborhood"], village=row["village"])
        graph.edge(
            row["tractId"], "RecordedTract", "current_address_crosswalk_to", neighborhood_id,
            "CurrentNeighborhood", row["sourceIds"], valid_from=row["validAt"],
            evidence_ids=row["crosswalkId"], confidence=row["confidence"],
            review_status=row["reviewStatus"], limitations=row["limitations"],
            notes=f"{row['matchedAddressPointCount']} matched current address points; {row['neighborhoodMatchedPointSharePct']}% of matched neighborhood points.",
        )
    for product in read_csv("builder_product_chronology.csv"):
        graph.node(
            product["builderProductId"], "BuilderProduct", product["canonicalProductName"],
            village=product["village"], cfdPhase=product["cfdPhase"], unitsPlanned=product["unitsPlanned"],
        )
        builder_id = f"LH-BUILDER-{slug(product['builder'])}"
        graph.node(builder_id, "Builder", product["builder"])
        graph.edge(
            product["builderProductId"], "BuilderProduct", "builder_reported_as", builder_id, "Builder",
            product["sourceIds"], valid_from=product["modelOpening"], valid_to=product["completionUpperBound"],
            evidence_ids=product["builderProductId"], confidence=product["confidence"],
            review_status="county_primary_controls" if product["cfdPhase"] else "secondary_directory_only",
            limitations=product["limitations"],
        )
        village_id = f"LH-VILLAGE-{slug(product['village'])}"
        graph.node(village_id, "Village", product["village"])
        graph.edge(
            product["builderProductId"], "BuilderProduct", "listed_in_current_village", village_id, "Village",
            product["sourceIds"], evidence_ids=product["builderProductId"], confidence=product["confidence"],
            review_status="current_name_product_crosswalk", limitations=product["limitations"],
        )
        for source_id in split_ids(product["sourceIds"]):
            graph.edge(
                product["builderProductId"], "BuilderProduct", "documented_by", source_id, "Source",
                source_id, evidence_ids=product["builderProductId"], confidence=product["confidence"],
                limitations=product["limitations"],
            )
    for tract in read_csv("tract_lifecycle_reconstruction.csv"):
        for product_id in split_ids(tract["builderProductCandidates"]):
            graph.edge(
                tract["tractId"], "RecordedTract", "current_address_product_candidate", product_id,
                "BuilderProduct", tract["sourceIds"], evidence_ids=tract["tractId"],
                confidence=tract["confidence"], review_status=tract["reviewStatus"],
                limitations=tract["limitations"],
            )
    school_projects = {row["schoolProjectId"]: row for row in read_csv("school_project_registry.csv")}
    for project in school_projects.values():
        graph.node(project["schoolProjectId"], "SchoolProject", project["projectName"])
        for school_id in split_ids(project["relatedSchoolIds"]):
            graph.edge(
                project["schoolProjectId"], "SchoolProject", "relates_to", school_id, "School",
                project["sourceIds"], evidence_ids=project["schoolProjectId"], confidence=project["confidence"],
                review_status=project["reviewStatus"], limitations=project["limitations"],
            )
        for source_id in split_ids(project["sourceIds"]):
            graph.edge(
                project["schoolProjectId"], "SchoolProject", "documented_by", source_id, "Source",
                source_id, evidence_ids=project["schoolProjectId"], confidence=project["confidence"],
                limitations=project["limitations"],
            )
    for item in read_csv("school_timeline.csv"):
        graph.node(item["schoolTimelineId"], "SchoolMilestone", item["observedState"])
        graph.edge(
            item["schoolTimelineId"], "SchoolMilestone", "milestone_of", item["schoolProjectId"],
            "SchoolProject", item["sourceIds"], valid_from=item["earliestDate"],
            valid_to=item["latestDate"], evidence_ids=item["schoolTimelineId"],
            confidence=item["confidence"], review_status=item["reviewStatus"],
            limitations=item["limitations"],
        )
    for activity in read_csv("construction_activity_registry.csv"):
        graph.node(activity["constructionActivityId"], "ConstructionActivity", activity["canonicalName"])
        for source_id in split_ids(activity["sourceIds"]):
            graph.edge(
                activity["constructionActivityId"], "ConstructionActivity", "documented_by",
                source_id, "Source", source_id, valid_from=activity["earliestStart"],
                valid_to=activity["latestEnd"], evidence_ids=activity["evidenceIds"],
                confidence=activity["confidence"], review_status=activity["reviewStatus"],
                limitations=activity["limitations"],
            )
    for event in read_csv("occupancy_event_registry.csv"):
        graph.node(event["occupancyEventId"], "OccupancyEvent", event["eventTitle"])
        graph.edge(
            event["occupancyEventId"], "OccupancyEvent", "concerns", event["geographyId"],
            "HistoricalObject", event["sourceIds"], valid_from=event["earliestDate"],
            valid_to=event["latestDate"], evidence_ids=event["relatedEventId"],
            confidence=event["confidence"], review_status=event["reviewStatus"],
            limitations=event["limitations"],
        )
    for asset in read_csv("asset_chronology.csv"):
        graph.node(asset["assetId"], "CommunityAsset", asset["assetName"])
        for source_id in split_ids(asset["sourceIds"]):
            graph.edge(
                asset["assetId"], "CommunityAsset", "opening_or_record_supported_by",
                source_id, "Source", source_id, valid_from=asset["earliestDate"],
                valid_to=asset["latestDate"], evidence_ids=asset["assetChronologyId"],
                confidence=asset["confidence"], review_status=asset["reviewStatus"],
                limitations=asset["limitations"],
            )
    for image in read_csv("imagery_inventory.csv"):
        graph.node(image["id"], "HistoricalImagery", image["sourceName"])
        graph.edge(
            image["id"], "HistoricalImagery", "provided_by", image["sourceIds"], "Source",
            image["sourceIds"], valid_from=image["captureDateEarliest"],
            valid_to=image["captureDateLatest"], evidence_ids=image["id"],
            confidence=image["confidence"], limitations=image["interpretiveLimitations"],
        )
    for review in read_csv("construction_interpretation_log.csv"):
        graph.node(review["interpretationId"], "ImageryReview", review["observedState"])
        graph.edge(
            review["interpretationId"], "ImageryReview", "reviews", review["imageryId"],
            "HistoricalImagery", review["sourceIds"], valid_from=review["reviewDate"],
            evidence_ids=review["interpretationId"], confidence=review["confidence"],
            review_status=review["reviewStatus"], limitations=review["limitations"],
        )
    for snapshot in read_csv("annual_phase_snapshot_manifest.csv"):
        graph.node(snapshot["snapshotId"], "AnnualSnapshot", snapshot["year"], year=snapshot["year"])
        for event_id in split_ids(snapshot["milestoneEventIds"]):
            graph.edge(
                snapshot["snapshotId"], "AnnualSnapshot", "includes_milestone", event_id,
                "DevelopmentEvent", snapshot["sourceIds"], valid_from=f"{snapshot['year']}-01-01",
                valid_to=f"{snapshot['year']}-12-31", evidence_ids=event_id,
                confidence=snapshot["confidence"], limitations=snapshot["limitations"],
            )


def build_inspector() -> dict[str, object]:
    records: dict[str, dict[str, object]] = {}
    matrices = {row["tractId"]: row for row in read_csv("tract_development_matrix.csv")}
    title_sheets = {f"LH-TRACT-{row['tractNumber']}": row for row in read_csv("tract_title_sheet_index.csv")}
    mission5 = {row["tractId"]: row for row in read_csv("tract_lifecycle_reconstruction.csv")}
    for audit in read_csv("tract_audit.csv"):
        tract_id = audit["tractId"]
        matrix = matrices[tract_id]
        title = title_sheets[tract_id]
        reconstruction = mission5[tract_id]
        current_places = "; ".join(filter(None, [reconstruction["villageCandidates"], reconstruction["neighborhoodCandidates"]]))
        records[tract_id] = {
            "id": tract_id,
            "canonicalName": f"Recorded Tract {audit['tractNumber']}",
            "alternateNames": [f"Tract {audit['tractNumber']}", audit["bookPage"]],
            "objectType": "Recorded tract map",
            "parentGeography": current_places or "Current neighborhood crosswalk unavailable; historical parent unresolved",
            "lifecycleTimeline": [
                {
                    "state": "Legal tract map recorded",
                    "date": audit["recordDate"],
                    "precision": "day",
                    "evidenceId": f"LH-OBS-TRACT-{audit['tractNumber']}",
                }
            ],
            "constructionHistory": "Not established",
            "occupancyHistory": "Not established",
            "schoolRelationship": "Historical assignment not established",
            "relatedBuilder": reconstruction["builderCandidates"] or "Not established; title-sheet parties are not automatically builders",
            "tractMapRelationship": title["normalizedParentTractIds"] or "No reviewed parent reference",
            "historicalImagery": ["LH-IMG-1994-1995", "LH-IMG-1997-1998", "LH-IMG-NAIP-2005", "LH-IMG-NAIP-2009", "LH-IMG-NAIP-2010"],
            "supportingSources": list(dict.fromkeys(split_ids(audit["sourceIds"]) + ["LH-SRC-OC-LMS-TRACT-PDFS"] + split_ids(reconstruction["sourceIds"]))),
            "evidenceObservations": [f"LH-OBS-TRACT-{audit['tractNumber']}"],
            "counterEvidence": [],
            "confidence": "high for legal recording and current address crosswalk where present; unknown for physical lifecycle",
            "confidenceRationale": matrix["milestoneConfidence"] + "; " + reconstruction["limitations"],
            "geometryProvenance": "Orange County tract GIS; audited in EPSG:26946; published in EPSG:4326",
            "temporalPrecision": "day for recording only",
            "spatialPrecision": audit["measurementGeometryStatus"],
            "unresolvedQuestions": matrix["unresolvedGaps"].split(";") + ["Current neighborhood/product candidates are not historical lifecycle proof"],
            "publicationFigures": [],
            "whyShown": "This geometry identifies the recorded legal subdivision. Mission 5 adds current address-based neighborhood and product candidates, but it does not depict a dated construction or occupied area.",
            "downloadRecord": "development/tract_maps.csv",
        }
    projects_by_school: dict[str, list[dict[str, str]]] = defaultdict(list)
    for project in read_csv("school_project_registry.csv"):
        for school_id in split_ids(project["relatedSchoolIds"]):
            projects_by_school[school_id].append(project)
    for school in read_csv("schools.csv"):
        projects = projects_by_school.get(school["id"], [])
        records[school["id"]] = {
            "id": school["id"],
            "canonicalName": school["name"],
            "alternateNames": [],
            "objectType": "School campus point",
            "parentGeography": "Ladera Ranch; historical attendance area unresolved",
            "lifecycleTimeline": [
                {"state": "Campus opened", "date": school["openDate"], "precision": school["temporalPrecision"], "evidenceId": ""}
            ],
            "constructionHistory": "Exact physical start and work footprint not established; DSA administrative milestones are available." if projects else "Not established",
            "occupancyHistory": "Not applicable",
            "schoolRelationship": "Attendance assignments by year not retrieved",
            "relatedBuilder": "Not applicable",
            "tractMapRelationship": "Not established",
            "historicalImagery": ["LH-IMG-1997-1998"],
            "supportingSources": split_ids(school["sourceIds"]) + sorted({source for project in projects for source in split_ids(project["sourceIds"])}),
            "evidenceObservations": [project["schoolProjectId"] for project in projects],
            "counterEvidence": [],
            "confidence": school["confidence"],
            "confidenceRationale": "Official opening record and current campus point; DSA dates do not establish exact active construction.",
            "geometryProvenance": school["geometryPrecision"],
            "temporalPrecision": school["temporalPrecision"],
            "spatialPrecision": "current point, not historical campus polygon",
            "unresolvedQuestions": ["Historical attendance boundary", "Exact construction start", "Historical construction footprint"],
            "publicationFigures": ["reports/assets/lhdrs_context/terrain_elevation.png"],
            "whyShown": "The point locates a school with an official opening date. It is not used as an attendance assignment or construction footprint.",
            "downloadRecord": "development/schools.geojson",
        }
    return {
        "version": "3.0",
        "generatedDate": "2026-07-27",
        "recordCount": len(records),
        "records": records,
    }


def query_results() -> dict[str, object]:
    convergence = read_csv("source_convergence.csv")
    unresolved_tracts = [row["tractId"] for row in read_csv("tract_development_matrix.csv") if not row["firstOccupancyRange"]]
    single_source = [row["claimId"] for row in convergence if row["independentSourceOrganizationCount"] == "1"]
    return {
        "queries": [
            {
                "id": "LH-GRAPH-QUERY-01",
                "question": "Which neighborhoods were occupied while another planning area was under mass grading?",
                "status": "blocked",
                "result": [],
                "reason": "No neighborhood occupancy geometry, planning-area crosswalk, or dated mass-grading polygon satisfies the evidence gate.",
            },
            {
                "id": "LH-GRAPH-QUERY-02",
                "question": "Which schools were open within 500 meters of active construction in a selected year?",
                "status": "blocked",
                "result": [],
                "reason": "School opening dates exist, but no dated active-construction geometry exists; zero is not asserted.",
            },
            {
                "id": "LH-GRAPH-QUERY-03",
                "question": "Which imagery supports a selected construction polygon?",
                "status": "no_supported_construction_polygons",
                "result": [],
                "reason": "Two partial predevelopment frames and three full-coverage 2005/2009/2010 frames were reviewed. They support bounded visible-state observations, but no precise active-construction polygon passed the proximity gate.",
            },
            {
                "id": "LH-GRAPH-QUERY-04",
                "question": "Which claims rely on only one independent source?",
                "status": "answered",
                "resultCount": len(single_source),
                "result": single_source,
            },
            {
                "id": "LH-GRAPH-QUERY-05",
                "question": "Which tracts have unresolved occupancy dates?",
                "status": "answered",
                "resultCount": len(unresolved_tracts),
                "result": unresolved_tracts,
            },
            {
                "id": "LH-GRAPH-QUERY-06",
                "question": "Which public figures use estimated geometry?",
                "status": "answered",
                "result": [],
                "reason": "No estimated historical geometry is published. Terrain figures use measured post-study context and imagery figures use measured alpha footprints.",
            },
            {
                "id": "LH-GRAPH-QUERY-07",
                "question": "Which historical conclusions changed after new evidence was added?",
                "status": "answered",
                "result": [
                    "CFD annual built-and-occupied counts now bound aggregate occupancy",
                    "County product tables now bound Phase V and Phase VI permit/escrow status",
                    "2005, 2009, and 2010 full-coverage imagery now bounds visible development change",
                    "The first-resident date conflict is explicitly retained",
                ],
                "reason": "Mission 5 adds aggregate and product-level bounds without transferring them to tract/address occupancy or active-construction geometry.",
            },
        ]
    }


def graph_figure(graph: Graph) -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    node_counts = Counter(str(node["type"]) for node in graph.nodes.values())
    edge_counts = Counter(str(edge["relationship"]) for edge in graph.edges)
    nodes = node_counts.most_common(10)
    edges = edge_counts.most_common(10)
    image = Image.new("RGB", (2160, 1000), "white")
    draw = ImageDraw.Draw(image)
    try:
        title_font = ImageFont.truetype("DejaVuSans-Bold.ttf", 34)
        label_font = ImageFont.truetype("DejaVuSans.ttf", 22)
        count_font = ImageFont.truetype("DejaVuSans-Bold.ttf", 21)
    except OSError:
        title_font = label_font = count_font = ImageFont.load_default()

    def panel(x: int, title: str, values: list[tuple[str, int]], color: str) -> None:
        draw.text((x, 45), title, fill="#17212b", font=title_font)
        label_width = 300
        bar_width = 650
        maximum = max((count for _, count in values), default=1)
        for index, (name, count) in enumerate(values):
            y = 115 + index * 80
            label = name.replace("_", " ")
            draw.text((x, y + 10), label[:25], fill="#24313d", font=label_font)
            left = x + label_width
            width = max(3, int(bar_width * count / maximum))
            draw.rounded_rectangle((left, y, left + width, y + 48), radius=4, fill=color)
            draw.text((left + width + 12, y + 10), str(count), fill="#17212b", font=count_font)
        draw.line((x + label_width, 105, x + label_width, 920), fill="#aeb8c2", width=2)

    panel(70, "Graph nodes by type", nodes, "#28796f")
    panel(1110, "Graph edges by relationship", edges, "#c45b34")
    image.save(ASSETS / "graph_summary.png", optimize=True)


def main() -> int:
    graph = Graph()
    add_preserved_edges(graph)
    add_sources(graph)
    add_claims_and_observations(graph)
    add_reconstruction(graph)
    graph.edges.sort(key=lambda row: str(row["edgeId"]))
    write_csv(BASE / "knowledge_graph.csv", graph.edges, Graph.fields)
    graph_json = {
        "version": "3.0",
        "nodes": sorted(graph.nodes.values(), key=lambda node: str(node["id"])),
        "edges": [{**edge, "sourceIds": split_ids(str(edge["sourceIds"])), "evidenceIds": split_ids(str(edge["evidenceIds"]))} for edge in graph.edges],
    }
    write_json(DATA / "knowledge_graph.json", graph_json)
    inspector = build_inspector()
    write_json(DATA / "evidence_inspector.json", inspector)
    queries = query_results()
    write_json(DATA / "graph_query_results.json", queries)
    PUBLIC.mkdir(parents=True, exist_ok=True)
    write_json(PUBLIC / "knowledge_graph.json", graph_json)
    write_json(PUBLIC / "evidence_inspector.json", inspector)
    write_json(PUBLIC / "graph_query_results.json", queries)
    graph_figure(graph)
    relation_count = len({edge["relationship"] for edge in graph.edges})
    write_text(
        DOCS / "MISSION_5_GRAPH_SUMMARY.md",
        f"""# Mission 5 evidence graph summary

The normalized graph contains **{len(graph.nodes):,} nodes**, **{len(graph.edges):,} edges**, and **{relation_count} relationship types**. All 18 first-edition edges are preserved. Mission 5 adds current address-based tract/neighborhood candidates, builder products, County permit and escrow snapshots, aggregate built-and-occupied counts, commercial status snapshots, and full-coverage 2005/2009/2010 imagery observations.

Every edge carries valid-time fields, evidence IDs, source IDs, confidence, version, review status, and limitations. Blank valid-time values mean the relationship is not temporally bounded; they are not interpreted as indefinite historical truth. Current crosswalk edges are not historical parentage or lifecycle edges.

The seven required example queries are stored in `data/development/graph_query_results.json`. Queries that require dated occupancy or active-construction geometry return `blocked`, not an empty factual answer.

![Graph summary](../../reports/assets/lhdrs_graph/graph_summary.png)
""",
    )
    print(f"DONE  graph: {len(graph.nodes)} nodes, {len(graph.edges)} edges, {inspector['recordCount']} inspector records")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
