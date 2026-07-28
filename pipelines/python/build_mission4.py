#!/usr/bin/env python3
"""Build Mission 4 tract-audit and geographic-crosswalk artifacts.

The County tract layer is a legal-map index, not a construction or occupancy
layer. This builder records geometric observations and review flags without
promoting them to lifecycle claims.
"""

from __future__ import annotations

import csv
from collections import Counter
from difflib import SequenceMatcher
import json
import os
from pathlib import Path
import re
import tempfile

from pyproj import Transformer
from shapely.geometry import shape
from shapely.ops import transform, unary_union
from shapely.validation import explain_validity, make_valid


ROOT = Path(__file__).resolve().parents[2]
RESEARCH = ROOT / "research/development_chronology"
DATA = ROOT / "data/development"
SOURCE_CRS = "EPSG:4326"
ANALYSIS_CRS = "EPSG:26946"  # NAD83 / California zone 6, metres.
OVERLAP_MIN_SQM = 1.0
CONTAINMENT_RATIO = 0.999
HIGH_OVERLAP_RATIO = 0.9
TITLE_OCR = ROOT / "evidence/lhdrs/tract_maps/title_sheet_ocr.txt"

OWNER_PATTERNS = {
    "DMB Ladera, L.L.C.": ("DMB LADERA", "OMB LADERA", "MB LADERA"),
    "Rancho Mission Viejo, L.L.C.": ("RANCHO MISSION VIEJO", "RANCHO MISSION VEJO", "RANCHO MISSION MEJO"),
    "Ladera Development Company": ("LADERA DEVELOPMENT COMPANY",),
    "Brookfield Wyeth, Inc.": ("BROOKFIELD WYETH",),
    "Brookfield Sarasota, Inc.": ("BROOKFIELD SARASOTA",),
    "Warmington Homes": ("WARMINGTON HOMES", "WARMINGTON LDR"),
    "Standard Pacific Corp.": ("STANDARD PACIFIC",),
    "Shea Homes": ("SHEA HOMES", "J.F. SHEA", "J F SHEA"),
    "Taylor Woodrow Homes, Inc.": ("TAYLOR WOODROW",),
    "William Lyon Homes, Inc.": ("WILLIAM LYON HOMES",),
    "John Laing Homes": ("JOHN LAING HOMES", "BA JOHN LAING HOMES"),
    "Richmond American Homes of California, Inc.": ("RICHMOND AMERICAN HOMES",),
}


def read_csv(name: str) -> list[dict[str, str]]:
    with (RESEARCH / name).open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def read_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as stream:
        return json.load(stream)


def write_csv(name: str, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path = RESEARCH / name
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w", newline="", encoding="utf-8", dir=path.parent, delete=False
    ) as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames, lineterminator="\n")
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


def tract_id(number: object) -> str:
    return f"LH-TRACT-{str(number).strip()}"


def joined(values: set[str]) -> str:
    return ";".join(sorted(values, key=lambda value: int(value.rsplit("-", 1)[-1])))


def measurement_geometry(geometry):
    if geometry.is_valid:
        return geometry, "original_valid"
    return make_valid(geometry), "original_invalid_repaired_for_measurement"


def build_tract_audit() -> tuple[list[dict[str, object]], list[dict[str, object]], dict[str, int]]:
    source = read_json(DATA / "tract_maps.geojson")
    cdp_source = read_json(DATA / "ladera_ranch_cdp.geojson")
    project = Transformer.from_crs(SOURCE_CRS, ANALYSIS_CRS, always_xy=True).transform
    cdp = unary_union(
        [transform(project, shape(feature["geometry"])) for feature in cdp_source["features"]]
    )

    items: list[dict[str, object]] = []
    for feature in source["features"]:
        props = feature["properties"]
        original = shape(feature["geometry"])
        measured_wgs84, measurement_status = measurement_geometry(original)
        measured = transform(project, measured_wgs84)
        area = measured.area
        outside_area = measured.difference(cdp).area
        items.append(
            {
                "id": tract_id(props["tractNumber"]),
                "number": str(props["tractNumber"]),
                "props": props,
                "original": original,
                "geometry": measured,
                "measurementStatus": measurement_status,
                "validityReason": "Valid Geometry" if original.is_valid else explain_validity(original),
                "area": area,
                "outsideArea": outside_area,
                "overlaps": set(),
                "contains": set(),
                "containedBy": set(),
                "highOverlap": set(),
            }
        )

    crosswalk: list[dict[str, object]] = []
    relationship_number = 0
    for left_index, left in enumerate(items):
        for right in items[left_index + 1 :]:
            intersection_area = left["geometry"].intersection(right["geometry"]).area
            if intersection_area <= OVERLAP_MIN_SQM:
                continue
            relationship_number += 1
            left_ratio = intersection_area / left["area"] if left["area"] else 0.0
            right_ratio = intersection_area / right["area"] if right["area"] else 0.0
            smaller_ratio = max(left_ratio, right_ratio)
            left["overlaps"].add(right["id"])
            right["overlaps"].add(left["id"])

            from_item = left
            to_item = right
            if smaller_ratio >= CONTAINMENT_RATIO:
                if left["area"] < right["area"]:
                    from_item, to_item = right, left
                relationship_type = "contains_or_matches_extent"
                geometry_test = "intersection covers at least 99.9 percent of smaller measured geometry"
                from_item["contains"].add(to_item["id"])
                to_item["containedBy"].add(from_item["id"])
            elif smaller_ratio >= HIGH_OVERLAP_RATIO:
                if left["area"] < right["area"]:
                    from_item, to_item = right, left
                relationship_type = "high_overlap_possible_nested_map"
                geometry_test = "intersection covers 90.0-99.9 percent of smaller measured geometry"
                left["highOverlap"].add(right["id"])
                right["highOverlap"].add(left["id"])
            else:
                relationship_type = "partial_overlap"
                geometry_test = "intersection exceeds 1 square metre"

            chronology = "same_record_date"
            if from_item["props"]["recordDate"] < to_item["props"]["recordDate"]:
                chronology = "from_recorded_before_to"
            elif from_item["props"]["recordDate"] > to_item["props"]["recordDate"]:
                chronology = "from_recorded_after_to"

            crosswalk.append(
                {
                    "relationshipId": f"LH-XWALK-{relationship_number:04d}",
                    "fromTractId": from_item["id"],
                    "toTractId": to_item["id"],
                    "fromTractNumber": from_item["number"],
                    "toTractNumber": to_item["number"],
                    "relationshipType": relationship_type,
                    "intersectionAreaSqM": f"{intersection_area:.1f}",
                    "overlapPctOfFrom": f"{intersection_area / from_item['area'] * 100:.4f}",
                    "overlapPctOfTo": f"{intersection_area / to_item['area'] * 100:.4f}",
                    "chronology": chronology,
                    "geometryTest": geometry_test,
                    "analysisCrs": ANALYSIS_CRS,
                    "sourceIds": "LH-SRC-OC-TRACTS",
                    "statementClass": "visual_interpretation",
                    "confidence": "medium" if relationship_type != "partial_overlap" else "low",
                    "reviewStatus": "legal_map_relationship_review_required",
                    "lifecycleConclusion": "not_established",
                    "limitations": (
                        "Geometric overlap and recording order do not prove amendment, supersession, "
                        "grading, construction, sale, or occupancy. Review recorded map title sheets."
                    ),
                }
            )

    audit: list[dict[str, object]] = []
    for item in sorted(items, key=lambda value: int(value["number"])):
        contains_count = len(item["contains"])
        contained_count = len(item["containedBy"])
        high_overlap_count = len(item["highOverlap"])
        overlap_count = len(item["overlaps"])
        if contains_count and contained_count:
            role = "possible_intermediate_nested_map"
        elif contains_count:
            role = "possible_parent_map"
        elif contained_count:
            role = "possible_nested_subdivision_map"
        elif high_overlap_count:
            role = "possible_nested_map_review_required"
        elif overlap_count:
            role = "partial_overlap_review_required"
        else:
            role = "standalone_or_unresolved"
        props = item["props"]
        outside_ratio = item["outsideArea"] / item["area"] if item["area"] else 0.0
        audit.append(
            {
                "tractId": item["id"],
                "tractNumber": item["number"],
                "sourceObjectId": props["sourceObjectId"],
                "bookPage": props["bookPage"],
                "recordDate": props["recordDate"],
                "recordYear": props["recordYear"],
                "sourceCrs": SOURCE_CRS,
                "analysisCrs": ANALYSIS_CRS,
                "geometryType": item["original"].geom_type,
                "originalGeometryValid": str(item["original"].is_valid).lower(),
                "validityReason": item["validityReason"],
                "measurementGeometryStatus": item["measurementStatus"],
                "areaSqM": f"{item['area']:.1f}",
                "areaAcres": f"{item['area'] / 4046.8564224:.3f}",
                "outsideCurrentCdpSqM": f"{item['outsideArea']:.1f}",
                "outsideCurrentCdpPct": f"{outside_ratio * 100:.4f}",
                "overlapCount": overlap_count,
                "containsCount": contains_count,
                "containedByCount": contained_count,
                "highOverlapCount": high_overlap_count,
                "containsTractIds": joined(item["contains"]),
                "containedByTractIds": joined(item["containedBy"]),
                "highOverlapTractIds": joined(item["highOverlap"]),
                "allOverlapTractIds": joined(item["overlaps"]),
                "suspectedMapRole": role,
                "relationshipReviewStatus": (
                    "legal_map_relationship_review_required" if overlap_count else "no_material_overlap_found"
                ),
                "recordingObservation": "legal_tract_map_recorded",
                "constructionConclusion": "not_established",
                "habitabilityConclusion": "not_established",
                "occupancyConclusion": "not_established",
                "sourceIds": "LH-SRC-OC-TRACTS;LH-SRC-CENSUS-CDP",
                "statementClass": "documented_exact",
                "confidence": "high",
                "limitations": (
                    "Current CDP is a query extent, not the historical planned-community boundary. "
                    "Map recording and geometric relationships do not establish physical lifecycle dates."
                ),
            }
        )

    metrics = {
        "tracts": len(items),
        "invalid": sum(not item["original"].is_valid for item in items),
        "outside": sum(item["outsideArea"] > OVERLAP_MIN_SQM for item in items),
        "pairs": len(crosswalk),
        "containment": sum(row["relationshipType"] == "contains_or_matches_extent" for row in crosswalk),
        "highOverlap": sum(row["relationshipType"] == "high_overlap_possible_nested_map" for row in crosswalk),
        "partialOverlap": sum(row["relationshipType"] == "partial_overlap" for row in crosswalk),
    }
    return audit, crosswalk, metrics


def build_hierarchy(audit: list[dict[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = [
        {
            "nodeId": "LH-COMMUNITY-LADERA-RANCH",
            "nodeType": "community",
            "name": "Ladera Ranch",
            "parentNodeId": "",
            "parentRelationship": "",
            "relationshipStatus": "root",
            "sourceIds": "LH-SRC-OC-PC;LH-SRC-CENSUS-CDP",
            "geometryStatus": "current_cdp_display_extent_only",
            "validFrom": "1995-10-17",
            "validTo": "",
            "confidence": "high",
            "limitations": "Current Census geometry is not the 1995 planned-community boundary.",
            "notes": "Root research entity; validFrom is plan approval, not construction or occupancy.",
        }
    ]
    for item in read_csv("planning_areas.csv"):
        if item["planningArea"] == "total":
            continue
        rows.append(
            {
                "nodeId": item["id"],
                "nodeType": "planning_area",
                "name": f"Planning Area {item['planningArea']}",
                "parentNodeId": "LH-COMMUNITY-LADERA-RANCH",
                "parentRelationship": "planned_component_of",
                "relationshipStatus": "documented_nonspatial",
                "sourceIds": item["sourceIds"],
                "geometryStatus": "boundary_not_yet_digitized",
                "validFrom": "1995-10-17",
                "validTo": "",
                "confidence": item["confidence"],
                "limitations": item["limitations"],
                "notes": item["sourceLocator"],
            }
        )
    for item in read_csv("neighborhoods.csv"):
        rows.append(
            {
                "nodeId": item["id"],
                "nodeType": "village",
                "name": item["name"],
                "parentNodeId": "LH-COMMUNITY-LADERA-RANCH",
                "parentRelationship": "named_village_of",
                "relationshipStatus": "documented_nonspatial_parent_planning_area_unresolved",
                "sourceIds": item["sourceIds"],
                "geometryStatus": "boundary_not_yet_sourced",
                "validFrom": "",
                "validTo": "",
                "confidence": item["confidence"],
                "limitations": item["limitations"],
                "notes": item["notes"],
            }
        )
    for item in audit:
        rows.append(
            {
                "nodeId": item["tractId"],
                "nodeType": "recorded_tract_map",
                "name": f"Tract {item['tractNumber']}",
                "parentNodeId": "",
                "parentRelationship": "",
                "relationshipStatus": "historical_parent_unresolved",
                "sourceIds": "LH-SRC-OC-TRACTS",
                "geometryStatus": item["measurementGeometryStatus"],
                "validFrom": item["recordDate"],
                "validTo": "",
                "confidence": "high",
                "limitations": (
                    "Feature intersects the current CDP query extent, but planning-area, village, "
                    "amendment, and lifecycle relationships require documentary crosswalks."
                ),
                "notes": f"County book/page {item['bookPage']}; {item['suspectedMapRole']}.",
            }
        )
    return rows


def parse_title_sheets(
    audit: list[dict[str, object]], crosswalk: list[dict[str, object]]
) -> list[dict[str, object]]:
    if not TITLE_OCR.exists():
        return []
    text = TITLE_OCR.read_text(encoding="utf-8")
    parts = re.split(r"=== PAGE \d+: TR_(\d+)[.]jpg ===", text)
    chunks = {parts[index]: parts[index + 1] for index in range(1, len(parts), 2)}
    known = {str(row["tractNumber"]) for row in audit}
    neighbors = {
        str(row["tractNumber"]): set(str(row["allOverlapTractIds"]).replace("LH-TRACT-", "").split(";"))
        - {""}
        for row in audit
    }
    by_number = {str(row["tractNumber"]): row for row in audit}
    manifest = {
        row["tractNumber"]: row
        for row in read_csv("tract_map_document_manifest.csv")
    }
    visually_verified_parents = {"16395": ["15986"], "16687": ["15988"]}
    rows: list[dict[str, object]] = []
    parent_pairs: dict[tuple[str, str], str] = {}

    for number in sorted(known, key=int):
        raw = chunks.get(number, "")
        normalized = " ".join(raw.upper().split())
        raw_candidates: list[str] = []
        parent_contexts: list[str] = []
        for match in re.finditer(
            r"(?:LOT|LOTS) .{0,180}?TRACT(?: NO[.]?)?\s*(\d{4,5})",
            normalized[:3500],
        ):
            candidate = match.group(1)
            if candidate == number or candidate in raw_candidates:
                continue
            raw_candidates.append(candidate)
            parent_contexts.append(match.group(0)[:220])

        resolved: list[str] = []
        corrections: list[str] = []
        for candidate in raw_candidates:
            if candidate in known:
                chosen = candidate
                status = "exact_ocr_match"
            else:
                pool = neighbors.get(number, set()) or known
                scored = sorted(
                    (
                        (SequenceMatcher(None, candidate, option).ratio(), option)
                        for option in pool
                    ),
                    reverse=True,
                )
                score, chosen = scored[0]
                if score < 0.72:
                    corrections.append(f"{candidate}->unresolved")
                    continue
                status = "ocr_corrected_against_intersecting_tract_ids"
                corrections.append(f"{candidate}->{chosen}")
            if chosen not in resolved:
                resolved.append(chosen)
                parent_pairs[(chosen, number)] = status

        if number in visually_verified_parents:
            resolved = visually_verified_parents[number]
            corrections.append("parent_number_visually_verified_from_title_sheet")
            for parent in resolved:
                parent_pairs[(parent, number)] = "visually_verified_title_sheet"

        owners = [
            owner
            for owner, patterns in OWNER_PATTERNS.items()
            if any(pattern in normalized for pattern in patterns)
        ]
        sheet_match = re.search(r"SHEET\s+1\s+OF\s+(\d+)\s+SHEETS", normalized)
        acreage_match = re.search(
            r"(?:TOTAL\s+ACRES?\s*:\s*)?(\d{1,4}[.,]\d{3})\s+AC(?:RES?|[.])",
            normalized[:2200],
        )
        numbered_match = re.search(
            r"(?:(\d+)\s+NUMBERED\s+LOTS|NUMBERED\s+LOTS\s*:\s*(\d+))",
            normalized[:2200],
        )
        lettered_match = re.search(r"(\d+)\s+LETTERED\s+LOTS", normalized[:2200])
        statement_class = "documented_exact"
        confidence = "high"
        if corrections or any(parent not in neighbors.get(number, set()) for parent in resolved):
            statement_class = "visual_interpretation"
            confidence = "medium"
        rows.append(
            {
                "tractId": f"LH-TRACT-{number}",
                "tractNumber": number,
                "sourceFile": manifest[number]["localFilePath"],
                "sheetCount": sheet_match.group(1) if sheet_match else "",
                "titledAreaAcres": acreage_match.group(1).replace(",", ".") if acreage_match else "",
                "numberedLots": next((value for value in numbered_match.groups() if value), "") if numbered_match else "",
                "letteredLots": lettered_match.group(1) if lettered_match else "",
                "rawParentTractCandidates": ";".join(raw_candidates),
                "normalizedParentTractIds": ";".join(f"LH-TRACT-{value}" for value in resolved),
                "parentLotContext": " | ".join(parent_contexts),
                "ocrCorrections": ";".join(corrections),
                "titleSheetParties": ";".join(owners),
                "partyInterpretation": "title_sheet_owner_or_interest_holder_not_necessarily_builder",
                "recordDate": by_number[number]["recordDate"],
                "sourceIds": "LH-SRC-OC-LMS-TRACT-PDFS",
                "method": "macOS Vision OCR of sheet 1 with geometry-assisted numeric review",
                "statementClass": statement_class,
                "confidence": confidence,
                "reviewStatus": "ocr_structured_visual_spot_check_required",
                "constructionConclusion": "not_established",
                "occupancyConclusion": "not_established",
                "limitations": (
                    "OCR may misread survey text and digits. Parent-map normalization uses only "
                    "known intersecting tract IDs; title-sheet parties are not assumed to be builders."
                ),
            }
        )

    for row in crosswalk:
        left = str(row["fromTractNumber"])
        right = str(row["toTractNumber"])
        pair = None
        if (left, right) in parent_pairs:
            pair = (left, right)
        elif (right, left) in parent_pairs:
            pair = (right, left)
            row["fromTractId"], row["toTractId"] = row["toTractId"], row["fromTractId"]
            row["fromTractNumber"], row["toTractNumber"] = right, left
            row["overlapPctOfFrom"], row["overlapPctOfTo"] = (
                row["overlapPctOfTo"], row["overlapPctOfFrom"]
            )
        if pair:
            status = parent_pairs[pair]
            row["relationshipType"] = "documented_parent_child_map"
            row["sourceIds"] = "LH-SRC-OC-TRACTS;LH-SRC-OC-LMS-TRACT-PDFS"
            row["statementClass"] = (
                "documented_exact"
                if status in {"exact_ocr_match", "visually_verified_title_sheet"}
                else "visual_interpretation"
            )
            row["confidence"] = (
                "high" if status in {"exact_ocr_match", "visually_verified_title_sheet"} else "medium"
            )
            row["reviewStatus"] = "documented_title_sheet_relationship"
            row["geometryTest"] += "; parent/child wording recovered from recorded-map title sheet"
            row["chronology"] = (
                "from_recorded_before_to"
                if by_number[str(row["fromTractNumber"])]["recordDate"]
                < by_number[str(row["toTractNumber"])]["recordDate"]
                else "from_recorded_after_to"
            )
            row["limitations"] = (
                "Title-sheet wording documents legal map lineage. It does not establish grading, "
                "construction, sale, habitability, or occupancy."
            )

    title_by_tract = {str(row["tractNumber"]): row for row in rows}
    for row in audit:
        title = title_by_tract[str(row["tractNumber"])]
        row["documentedParentTractIds"] = title["normalizedParentTractIds"]
        row["titleSheetParties"] = title["titleSheetParties"]
        row["titleSheetReviewStatus"] = title["reviewStatus"]
        if title["normalizedParentTractIds"]:
            row["suspectedMapRole"] = "documented_or_interpreted_nested_subdivision_map"
    return rows


def title_sheet_markdown(rows: list[dict[str, object]], crosswalk: list[dict[str, object]]) -> str:
    documented = [row for row in rows if row["normalizedParentTractIds"]]
    corrected = [row for row in rows if row["ocrCorrections"]]
    owners = Counter(
        owner
        for row in rows
        for owner in str(row["titleSheetParties"]).split(";")
        if owner
    )
    owner_rows = "\n".join(f"| {owner} | {count} |" for owner, count in owners.most_common())
    sample_rows = "\n".join(
        f"| {row['tractNumber']} | {row['normalizedParentTractIds']} | "
        f"{row['parentLotContext'][:120]} | {row['titleSheetParties']} |"
        for row in documented[:30]
    )
    upgraded = sum(row["reviewStatus"] == "documented_title_sheet_relationship" for row in crosswalk)
    return f"""# Recorded Tract Map Document Review

Generated from the 123 official County recorded-map PDFs archived by
`scripts/lhdrs_mission4_fetch.py`. Sheet 1 of every map was rendered at 150 DPI and OCRed
with macOS Vision; selected master and nested sheets were visually inspected.

| Metric | Count |
|---|---:|
| Official PDFs archived | {len(rows)} |
| Title sheets with normalized parent-tract wording | {len(documented)} |
| OCR parent numbers corrected against intersecting tract IDs | {len(corrected)} |
| Geometric crosswalk rows upgraded with title-sheet evidence | {upgraded} |

## Named Parties

| Title-sheet owner or interest holder | Maps mentioning party |
|---|---:|
{owner_rows}

These are documentary parties, not automatically builders. A deed beneficiary, owner,
or manager may differ from the homebuilder or sales brand.

## Parent Examples

| Child tract | Normalized parent | OCR context | Named parties |
|---|---|---|---|
{sample_rows}

## Review Boundary

OCR output is an index, not a substitute for the image. Raw OCR candidates and every
numeric correction are retained in `tract_title_sheet_index.csv`. Title-sheet parent/child
language can establish legal map lineage, but it does not establish construction,
habitability, sale, or occupancy dates.
"""


def build_evidence_models(
    audit: list[dict[str, object]],
) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]]:
    observations: list[dict[str, object]] = []
    claims: list[dict[str, object]] = []
    for item in audit:
        observation_id = f"LH-OBS-TRACT-{item['tractNumber']}"
        observations.append(
            {
                "observationId": observation_id,
                "observedEntityId": item["tractId"],
                "observationType": "legal_tract_map_recording",
                "observedValue": f"Tract {item['tractNumber']} recorded as {item['bookPage']}",
                "dateStart": item["recordDate"],
                "dateEnd": "",
                "temporalPrecision": "day",
                "geometryId": item["tractId"],
                "geometryType": item["geometryType"],
                "geometryStatus": item["measurementGeometryStatus"],
                "method": "direct County attribute transcription and source-geometry audit",
                "sourceIds": "LH-SRC-OC-TRACTS",
                "sourceLocator": f"County object ID {item['sourceObjectId']}; {item['bookPage']}",
                "statementClass": "documented_exact",
                "confidence": "high",
                "limitations": (
                    "Recording is a legal subdivision milestone only; it does not date construction, "
                    "habitability, sale, or occupancy."
                ),
                "notes": item["suspectedMapRole"],
            }
        )
        claims.append(
            {
                "claimId": f"LH-CLM-TRACT-{item['tractNumber']}",
                "subjectEntityId": item["tractId"],
                "claimType": "legal_recording_milestone",
                "claimText": f"County tract map {item['tractNumber']} was recorded {item['recordDate']}.",
                "dateStart": item["recordDate"],
                "dateEnd": "",
                "temporalPrecision": "day",
                "claimScope": "legal_subdivision",
                "supportingObservationIds": observation_id,
                "sourceIds": "LH-SRC-OC-TRACTS",
                "supportType": "direct_observation",
                "statementClass": "documented_exact",
                "confidence": "high",
                "conflictStatus": "no_conflict_identified",
                "reviewStatus": item["relationshipReviewStatus"],
                "limitations": (
                    "The claim is limited to recording and carries no physical-development lifecycle meaning."
                ),
                "notes": item["bookPage"],
            }
        )

    for item in read_csv("events.csv"):
        observation_id = f"LH-OBS-{item['id']}"
        is_spatial = item["featureId"].startswith("LH-SCHOOL-")
        observations.append(
            {
                "observationId": observation_id,
                "observedEntityId": item["featureId"],
                "observationType": item["eventType"],
                "observedValue": item["title"],
                "dateStart": item["dateStart"],
                "dateEnd": item["dateEnd"],
                "temporalPrecision": item["temporalPrecision"],
                "geometryId": item["featureId"] if is_spatial else "",
                "geometryType": "Point" if is_spatial else "",
                "geometryStatus": "current_facility_centroid" if is_spatial else "nonspatial_observation",
                "method": item["interpretationMethod"],
                "sourceIds": item["sourceIds"],
                "sourceLocator": item["sourceLocator"],
                "statementClass": item["statementClass"],
                "confidence": item["confidence"],
                "limitations": item["conflictNotes"],
                "notes": item["notes"],
            }
        )
        claims.append(
            {
                "claimId": f"LH-CLM-{item['id']}",
                "subjectEntityId": item["featureId"],
                "claimType": item["eventType"],
                "claimText": item["title"],
                "dateStart": item["dateStart"],
                "dateEnd": item["dateEnd"],
                "temporalPrecision": item["temporalPrecision"],
                "claimScope": "historical_event",
                "supportingObservationIds": observation_id,
                "sourceIds": item["sourceIds"],
                "supportType": "direct_observation",
                "statementClass": item["statementClass"],
                "confidence": item["confidence"],
                "conflictStatus": "conflict_documented" if item["conflictNotes"] else "no_conflict_identified",
                "reviewStatus": "reviewed_first_edition",
                "limitations": item["conflictNotes"],
                "notes": item["notes"],
            }
        )

    intervals: list[dict[str, object]] = []
    for item in read_csv("annual_snapshots.csv"):
        year = int(item["year"])
        intervals.append(
            {
                "intervalId": f"LH-LIFE-COMMUNITY-{year}",
                "entityId": "LH-COMMUNITY-LADERA-RANCH",
                "stateDimension": "community_development_summary",
                "stateValue": item["communityStatus"],
                "validFrom": f"{year}-01-01",
                "validTo": f"{year}-12-31",
                "startBoundType": "calendar_year_start",
                "endBoundType": "calendar_year_end",
                "temporalPrecision": "year",
                "geometryId": "",
                "geometryStatus": "nonspatial_community_summary",
                "sourceIds": item["sourceIds"],
                "supportingClaimIds": "",
                "statementClass": "documented_approximate",
                "confidence": item["confidence"],
                "proximityEligible": "false",
                "limitations": item["limitations"],
                "notes": item["documentedMilestones"],
            }
        )
    return observations, claims, intervals


def audit_markdown(
    audit: list[dict[str, object]], crosswalk: list[dict[str, object]], metrics: dict[str, int]
) -> str:
    invalid = [row for row in audit if row["originalGeometryValid"] == "false"]
    outside = sorted(audit, key=lambda row: float(row["outsideCurrentCdpPct"]), reverse=True)
    top = sorted(crosswalk, key=lambda row: float(row["intersectionAreaSqM"]), reverse=True)[:12]
    invalid_rows = "\n".join(
        f"| {row['tractNumber']} | {row['sourceObjectId']} | {row['validityReason']} |"
        for row in invalid
    )
    outside_rows = "\n".join(
        f"| {row['tractNumber']} | {float(row['outsideCurrentCdpSqM']):,.1f} | "
        f"{float(row['outsideCurrentCdpPct']):.3f}% |"
        for row in outside
        if float(row["outsideCurrentCdpSqM"]) > OVERLAP_MIN_SQM
    )
    top_rows = "\n".join(
        f"| {row['fromTractNumber']} | {row['toTractNumber']} | {row['relationshipType']} | "
        f"{float(row['intersectionAreaSqM']):,.1f} | {float(row['overlapPctOfFrom']):.2f}% | "
        f"{float(row['overlapPctOfTo']):.2f}% |"
        for row in top
    )
    return f"""# Tract and Geography Audit

Generated by `pipelines/python/build_mission4.py` from the archived County tract-map
layer and the current Census CDP boundary.

## Result

| Metric | Count |
|---|---:|
| County tract features audited | {metrics['tracts']} |
| Invalid original geometries | {metrics['invalid']} |
| Features extending more than 1 m2 outside the current CDP | {metrics['outside']} |
| Material intersecting pairs | {metrics['pairs']} |
| At least 99.9% containment or matching-extent pairs | {metrics['containment']} |
| 90.0-99.9% high-overlap pairs | {metrics['highOverlap']} |
| Other partial-overlap pairs | {metrics['partialOverlap']} |

The 123 County features are not 123 mutually exclusive development areas. Their nested
and overlapping shapes are consistent with a legal-map index that may include parent,
later subdivision, and amendment relationships. Geometry alone does not establish those
legal relationships, so every intersecting pair remains flagged for title-sheet review.

## Method

- Source coordinates: `EPSG:4326`.
- Measurement coordinates: `EPSG:26946` (NAD83 / California zone 6), in metres.
- Original validity is reported before repair. Invalid geometry is repaired only in
  memory for measurement; the archived source geometry is not overwritten.
- A material intersection exceeds {OVERLAP_MIN_SQM:.0f} square metre.
- `contains_or_matches_extent` means the intersection covers at least 99.9% of the
  smaller measured geometry. It is a geometric review flag, not a supersession claim.
- `high_overlap_possible_nested_map` means 90.0-99.9% coverage of the smaller geometry.
- The present-day CDP is used only as a repeatable query/display extent.

## Invalid Source Geometries

| Tract | County object ID | Original validity reason |
|---|---:|---|
{invalid_rows}

## Current-CDP Edge Review

| Tract | Area outside current CDP (m2) | Share of tract geometry |
|---|---:|---:|
{outside_rows}

These are not necessarily source errors because the current Census boundary is not the
historical planned-community boundary.

## Largest Measured Intersections

| From tract | To tract | Review relationship | Area (m2) | From share | To share |
|---|---|---|---:|---:|---:|
{top_rows}

## Lifecycle Boundary

A recording date documents a legal subdivision milestone only. This audit does not
convert it into a grading, vertical-construction, road-opening, sale, habitability, or
occupancy date. `tract_crosswalk.csv` records measured relationships and their review
status; `geographic_hierarchy.csv` leaves unknown tract-to-planning-area and
tract-to-village parents unresolved.
"""


def main() -> int:
    required = [DATA / "tract_maps.geojson", DATA / "ladera_ranch_cdp.geojson"]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.exists()]
    if missing:
        raise SystemExit("Missing Mission 4 GIS inputs: " + ", ".join(missing))

    audit, crosswalk, metrics = build_tract_audit()
    title_sheets = parse_title_sheets(audit, crosswalk)
    hierarchy = build_hierarchy(audit)
    observations, claims, intervals = build_evidence_models(audit)
    write_csv("tract_audit.csv", audit, list(audit[0]))
    write_csv("tract_crosswalk.csv", crosswalk, list(crosswalk[0]))
    write_csv("geographic_hierarchy.csv", hierarchy, list(hierarchy[0]))
    if title_sheets:
        write_csv("tract_title_sheet_index.csv", title_sheets, list(title_sheets[0]))
    write_csv("historical_observations.csv", observations, list(observations[0]))
    write_csv("claim_registry.csv", claims, list(claims[0]))
    write_csv("lifecycle_intervals.csv", intervals, list(intervals[0]))
    write_text(
        ROOT / "docs/lhdrs/TRACT_AND_GEOGRAPHY_AUDIT.md",
        audit_markdown(audit, crosswalk, metrics),
    )
    if title_sheets:
        write_text(
            ROOT / "docs/lhdrs/TRACT_MAP_DOCUMENT_REVIEW.md",
            title_sheet_markdown(title_sheets, crosswalk),
        )
    print(
        f"Mission 4 tract audit: {metrics['tracts']} tracts, {metrics['pairs']} "
        f"material intersecting pairs, {metrics['invalid']} invalid source geometries, "
        f"{len(observations)} observations"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
