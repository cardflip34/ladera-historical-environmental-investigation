#!/usr/bin/env python3
"""Build deterministic LHDRS atlas datasets from canonical research records."""

from __future__ import annotations

import csv
import json
import os
from pathlib import Path
import shutil
import tempfile


ROOT = Path(__file__).resolve().parents[2]
RESEARCH = ROOT / "research/development_chronology"
DATA = ROOT / "data/development"
PUBLIC = ROOT / "apps/web/public/development"


def read_csv(name: str) -> list[dict[str, str]]:
    with (RESEARCH / name).open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def read_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as stream:
        return json.load(stream)


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = (json.dumps(value, indent=2, ensure_ascii=True) + "\n").encode("utf-8")
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as stream:
        stream.write(payload)
        temp_path = Path(stream.name)
    os.replace(temp_path, path)


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    with temp.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    os.replace(temp, path)


def update_snapshot_counts(tracts: dict) -> list[dict[str, str]]:
    rows = read_csv("annual_snapshots.csv")
    years = [feature["properties"].get("recordYear") for feature in tracts.get("features", [])]
    cumulative = 0
    for row in rows:
        year = int(row["year"])
        annual = sum(item == year for item in years)
        cumulative += annual
        row["tractMapsRecordedByYear"] = str(annual)
        row["tractMapsRecordedCumulative"] = str(cumulative)

    path = RESEARCH / "annual_snapshots.csv"
    fieldnames = list(rows[0])
    temp = path.with_suffix(".csv.tmp")
    with temp.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    os.replace(temp, path)
    return rows


def build_school_geojson() -> dict:
    features = []
    for row in read_csv("schools.csv"):
        if not row.get("latitude") or not row.get("longitude"):
            continue
        features.append(
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [float(row["longitude"]), float(row["latitude"])],
                },
                "properties": {
                    **row,
                    "openYear": int(row["openDate"][:4]),
                    "sourceId": row["sourceIds"],
                    "statementClass": "documented_exact",
                },
            }
        )
    output = {"type": "FeatureCollection", "features": features}
    write_json(DATA / "schools.geojson", output)
    return output


def build_tract_ledger(tracts: dict) -> list[dict[str, object]]:
    rows = []
    for feature in tracts.get("features", []):
        row = dict(feature.get("properties", {}))
        row["geometryType"] = feature.get("geometry", {}).get("type", "")
        rows.append(row)
    rows.sort(key=lambda row: (str(row.get("recordDate", "")), str(row.get("tractNumber", ""))))
    fieldnames = [
        "sourceId", "sourceObjectId", "tractNumber", "bookPage", "recordDate", "recordYear",
        "engineeringCompany", "engineerSurveyor", "licenseNumber", "jurisdiction",
        "georeferencedPages", "geometryType", "statementClass", "confidence",
        "geometryPrecision", "knownLimitations",
    ]
    write_csv(DATA / "tract_maps.csv", rows, fieldnames)
    return rows


def build_knowledge_graph() -> dict:
    rows = read_csv("knowledge_graph.csv")
    existing = read_json(DATA / "knowledge_graph.json") if (DATA / "knowledge_graph.json").exists() else {}
    nodes: dict[str, dict[str, str]] = {
        node["id"]: node for node in existing.get("nodes", []) if node.get("id")
    }
    edges = []
    for row in rows:
        nodes.setdefault(row["fromId"], {"id": row["fromId"], "type": row["fromType"]})
        nodes.setdefault(row["toId"], {"id": row["toId"], "type": row["toType"]})
        edges.append(
            {
                **row,
                "sourceIds": [item.strip() for item in row["sourceIds"].split(";") if item.strip()],
            }
        )
    output = {
        "version": existing.get("version", "2.0"),
        "nodes": sorted(nodes.values(), key=lambda node: node["id"]),
        "edges": edges,
    }
    write_json(DATA / "knowledge_graph.json", output)
    return output


def build_annual_geojson(cdp: dict, snapshots: list[dict[str, str]]) -> dict:
    geometry = cdp["features"][0]["geometry"]
    features = []
    for row in snapshots:
        features.append(
            {
                "type": "Feature",
                "geometry": geometry,
                "properties": {
                    **row,
                    "year": int(row["year"]),
                    "featureType": "community_snapshot",
                    "geometryPrecision": "current official CDP boundary used as display extent",
                    "statementClass": "documented_approximate",
                },
            }
        )
    output = {"type": "FeatureCollection", "features": features}
    write_json(DATA / "annual_snapshots.geojson", output)
    return output


def copy_public() -> None:
    PUBLIC.mkdir(parents=True, exist_ok=True)
    copies = {
        DATA / "ladera_ranch_cdp.geojson": PUBLIC / "ladera_ranch_cdp.geojson",
        DATA / "tract_maps.geojson": PUBLIC / "tract_maps.geojson",
        DATA / "tract_maps.csv": PUBLIC / "tract_maps.csv",
        DATA / "schools.geojson": PUBLIC / "schools.geojson",
        DATA / "annual_snapshots.geojson": PUBLIC / "annual_snapshots.geojson",
        DATA / "knowledge_graph.json": PUBLIC / "knowledge_graph.json",
        DATA / "evidence_inspector.json": PUBLIC / "evidence_inspector.json",
        DATA / "graph_query_results.json": PUBLIC / "graph_query_results.json",
        DATA / "tract_terrain.geojson": PUBLIC / "tract_terrain.geojson",
        DATA / "drainage_features.geojson": PUBLIC / "drainage_features.geojson",
        DATA / "watersheds.geojson": PUBLIC / "watersheds.geojson",
        ROOT / "data/processed/imagery_footprints/imagery_footprints.geojson": PUBLIC / "imagery_footprints.geojson",
        DATA / "imagery_1998.json": PUBLIC / "imagery_1998.json",
        ROOT / "evidence/lhdrs/imagery/ladera_1997_1998.png": PUBLIC / "imagery_1998.png",
        ROOT / "evidence/lhdrs/figures/ladera_development_plan_1995.jpg": PUBLIC / "ladera_development_plan_1995.jpg",
        ROOT / "evidence/lhdrs/figures/ladera_statistical_table_2003.jpg": PUBLIC / "ladera_statistical_table_2003.jpg",
    }
    for source, target in copies.items():
        if source.exists():
            shutil.copy2(source, target)


def build_qa_summary(
    sources: list[dict[str, str]], events: list[dict[str, str]], snapshots: list[dict[str, str]],
    tracts: dict, schools: dict, graph: dict
) -> None:
    pending = [row for row in sources if row.get("archiveStatus") in {"pending_fetch", "fetch_failed"}]
    unresolved = read_csv("unresolved_questions.csv")
    critical = [row for row in unresolved if row["priority"] == "critical"]
    text = f"""# LHDRS Automated QA Summary

Generated by `pipelines/python/build_lhdrs.py`.

| Metric | Count |
|---|---:|
| Registered LHDRS sources | {len(sources)} |
| Chronology events | {len(events)} |
| Annual snapshots | {len(snapshots)} |
| 1998-2008 tract-map polygons | {len(tracts.get('features', []))} |
| School points | {len(schools.get('features', []))} |
| Evidence graph nodes / edges | {len(graph.get('nodes', []))} / {len(graph.get('edges', []))} |
| Pending or failed source archives | {len(pending)} |
| Open critical questions | {len(critical)} |

## Interpretation Boundary

Tract-map recording is a legal subdivision milestone. The atlas does not interpret a
recording date as a grading, construction, sale, road-opening, or occupancy date.

## Blocked Analyses

Historical construction-proximity tables remain blocked until dated occupied-neighborhood
and active-construction geometries exist. The missing inputs are tracked in
`unresolved_questions.csv`; no centroid or community-wide substitute is used.
"""
    path = ROOT / "docs/lhdrs/QA_REPORT.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main() -> int:
    required = [
        DATA / "ladera_ranch_cdp.geojson",
        DATA / "tract_maps.geojson",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.exists()]
    if missing:
        raise SystemExit(
            "Missing fetched GIS inputs: " + ", ".join(missing) +
            ". Run python3 scripts/lhdrs_fetch_sources.py first."
        )

    cdp = read_json(DATA / "ladera_ranch_cdp.geojson")
    tracts = read_json(DATA / "tract_maps.geojson")
    snapshots = update_snapshot_counts(tracts)
    build_tract_ledger(tracts)
    schools = build_school_geojson()
    build_annual_geojson(cdp, snapshots)
    graph = build_knowledge_graph()
    copy_public()
    sources = read_csv("sources.csv")
    events = read_csv("events.csv")
    build_qa_summary(sources, events, snapshots, tracts, schools, graph)
    print(
        f"Built LHDRS: {len(tracts.get('features', []))} tracts, "
        f"{len(schools.get('features', []))} schools, {len(snapshots)} years"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
