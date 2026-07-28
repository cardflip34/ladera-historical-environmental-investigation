#!/usr/bin/env python3
"""Acquire and checksum Mission 5 historical evidence.

This script is intentionally archive-first. It stores the source response, request
metadata, and checksum before any downstream parser turns the material into claims.
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
from pathlib import Path
import ssl
import subprocess
import tempfile
import time
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence/lhdrs/mission5"
RETRIEVAL_DATE = "2026-07-27"
USER_AGENT = "LHDRS-Mission5/1.0 historical-research-archive"
AOI = (-117.675, 33.525, -117.610, 33.585)
SSL_CONTEXT = ssl.create_default_context()

SOURCES = [
    {
        "sourceId": "LH-SRC-OC-BOND-2006Q4",
        "title": "Orange County Bond Monitoring Program, Fourth Quarter 2006",
        "url": "https://www.ocgov.com/sites/default/files/import/data/files/4147.pdf",
        "path": "pdf/oc_bond_monitoring_2006_q4.pdf",
        "publisher": "County of Orange",
        "sourceType": "official_bond_monitoring_report",
        "publicationDate": "2007-01-01",
        "isOfficial": "true",
        "isPrimary": "true",
        "reliabilityGrade": "A1",
    },
    {
        "sourceId": "LH-SRC-OC-BOND-2011Q4",
        "title": "Orange County Bond Monitoring Program, Fourth Quarter 2011",
        "url": "https://cfo.oc.gov/sites/finance/files/import/data/files/4148.pdf",
        "path": "pdf/oc_bond_monitoring_2011_q4.pdf",
        "publisher": "County of Orange",
        "sourceType": "official_bond_monitoring_report",
        "publicationDate": "2012-01-01",
        "isOfficial": "true",
        "isPrimary": "true",
        "reliabilityGrade": "A1",
    },
    {
        "sourceId": "LH-SRC-OC-CFD-HISTORY",
        "title": "Orange County Community Facilities District Resolution History",
        "url": "https://cfo.oc.gov/sites/finance/files/import/data/files/49731.pdf",
        "path": "pdf/oc_cfd_resolution_history.pdf",
        "publisher": "County of Orange",
        "sourceType": "official_cfd_history",
        "publicationDate": "",
        "isOfficial": "true",
        "isPrimary": "true",
        "reliabilityGrade": "A2",
    },
    {
        "sourceId": "LH-SRC-OC-LADR-2018",
        "title": "Local Agency Special Tax and Bond Accountability Report 2018",
        "url": "https://cfo.ocgov.com/sites/finance/files/import/data/files/83680.pdf",
        "path": "pdf/oc_local_accountability_2018.pdf",
        "publisher": "County of Orange",
        "sourceType": "official_accountability_report",
        "publicationDate": "2018-12-31",
        "isOfficial": "true",
        "isPrimary": "true",
        "reliabilityGrade": "A2",
    },
    {
        "sourceId": "LH-SRC-LARMAC-STREETS-2019",
        "title": "LaderaLife Street and Neighborhood List",
        "url": "https://laderalife.com/assets//Neighborhood%20Street%20List%205.21.19.pdf",
        "path": "pdf/laderalife_street_neighborhood_list_2019.pdf",
        "publisher": "Ladera Ranch Maintenance Corporation",
        "sourceType": "official_community_directory",
        "publicationDate": "2019-05-21",
        "isOfficial": "true",
        "isPrimary": "true",
        "reliabilityGrade": "A2",
    },
    {
        "sourceId": "LH-SRC-LARMAC-CUSTOM-2006",
        "title": "Covenant Hills Custom Home Design Guidelines, Chapter 1",
        "url": "https://laderalife.com/upload/FormsAndDocument/Document/2019-01/Custom_Home_Design_Guidelines%2C_Chapter_1_-_Introduction-1.pdf",
        "path": "pdf/covenant_hills_design_guidelines_ch1_2006.pdf",
        "publisher": "Ladera Ranch Maintenance Corporation",
        "sourceType": "official_design_guidelines",
        "publicationDate": "2006-09-18",
        "isOfficial": "true",
        "isPrimary": "true",
        "reliabilityGrade": "A2",
    },
    {
        "sourceId": "LH-SRC-OC-TRANSPORT-2008",
        "title": "Ladera Ranch Transportation Survey Packet",
        "url": "https://bos.ocgov.com/legacy5/newsletters/pdf/ladera_ranch_transportation_survey_packet_2008.pdf",
        "path": "pdf/ladera_ranch_transportation_survey_2008.pdf",
        "publisher": "County of Orange",
        "sourceType": "official_transportation_survey",
        "publicationDate": "2008-01-01",
        "isOfficial": "true",
        "isPrimary": "true",
        "reliabilityGrade": "A2",
    },
    {
        "sourceId": "LH-SRC-LARMAC-RW-2019W",
        "title": "Roots and Wings, Winter 2019",
        "url": "https://laderalife.com/upload/RootsAndWing/Magazine/2019-12/0145%20Roots%20and%20Wings%20Winter%202019%20revised%20%28spreads%29.pdf",
        "path": "pdf/roots_and_wings_winter_2019.pdf",
        "publisher": "Ladera Ranch Community Services",
        "sourceType": "official_community_magazine",
        "publicationDate": "2019-12-01",
        "isOfficial": "true",
        "isPrimary": "false",
        "reliabilityGrade": "B1",
    },
    {
        "sourceId": "LH-SRC-LARMAC-RW-2020S",
        "title": "Roots and Wings, Spring 2020",
        "url": "https://laderalife.com/upload/RootsAndWing/Magazine/2020-03/RootsandWingsSpring2020.pdf",
        "path": "pdf/roots_and_wings_spring_2020.pdf",
        "publisher": "Ladera Ranch Community Services",
        "sourceType": "official_community_magazine",
        "publicationDate": "2020-03-01",
        "isOfficial": "true",
        "isPrimary": "false",
        "reliabilityGrade": "B1",
    },
    {
        "sourceId": "LH-SRC-LARMAC-TIMELINE-M5",
        "title": "Explore Ladera Ranch: Ladera Ranch Through the Years",
        "url": "https://laderalife.com/about/explore-ladera-ranch",
        "path": "html/laderalife_timeline_2026.html",
        "publisher": "Ladera Ranch Community Services",
        "sourceType": "official_community_timeline",
        "publicationDate": "",
        "isOfficial": "true",
        "isPrimary": "false",
        "reliabilityGrade": "B1",
    },
    {
        "sourceId": "LH-SRC-PROB-TRAILS-1999",
        "title": "Happy Trails at Ladera Ranch",
        "url": "https://www.probuilder.com/sales-marketing/article/55196745/happy-trails-at-ladera-ranch",
        "path": "html/probuilder_happy_trails_1999.html",
        "publisher": "Professional Builder",
        "sourceType": "contemporary_trade_publication",
        "publicationDate": "1999-11-03",
        "isOfficial": "false",
        "isPrimary": "false",
        "reliabilityGrade": "B1",
    },
    {
        "sourceId": "LH-SRC-LAT-BUILDERS-1998",
        "title": "Builders Chosen for Start of 8,100-Home Project",
        "url": "https://www.latimes.com/archives/la-xpm-1998-jan-20-fi-10079-story.html",
        "path": "html/latimes_builders_1998.html",
        "publisher": "Los Angeles Times",
        "sourceType": "contemporary_newspaper",
        "publicationDate": "1998-01-20",
        "isOfficial": "false",
        "isPrimary": "false",
        "reliabilityGrade": "B1",
    },
    {
        "sourceId": "LH-SRC-LAT-PHASE1-1999",
        "title": "Ladera Ranch Developer Picks Phase I Builders",
        "url": "https://www.latimes.com/archives/la-xpm-1999-may-04-fi-33910-story.html",
        "path": "html/latimes_phase1_builders_1999.html",
        "publisher": "Los Angeles Times",
        "sourceType": "contemporary_newspaper",
        "publicationDate": "1999-05-04",
        "isOfficial": "false",
        "isPrimary": "false",
        "reliabilityGrade": "B1",
    },
    {
        "sourceId": "LH-SRC-LAT-OPENING-1999",
        "title": "Small-Town Feel, Big-Time Crowds",
        "url": "https://www.latimes.com/archives/la-xpm-1999-aug-01-me-61604-story.html",
        "path": "html/latimes_grand_opening_1999.html",
        "publisher": "Los Angeles Times",
        "sourceType": "contemporary_newspaper",
        "publicationDate": "1999-08-01",
        "isOfficial": "false",
        "isPrimary": "false",
        "reliabilityGrade": "B1",
    },
    {
        "sourceId": "LH-SRC-LAT-FIRST-RESIDENT-1999",
        "title": "New Kids on Every Block",
        "url": "https://www.latimes.com/archives/la-xpm-1999-dec-12-me-43197-story.html",
        "path": "html/latimes_first_residents_1999.html",
        "publisher": "Los Angeles Times",
        "sourceType": "contemporary_newspaper",
        "publicationDate": "1999-12-12",
        "isOfficial": "false",
        "isPrimary": "false",
        "reliabilityGrade": "B1",
    },
    {
        "sourceId": "LH-SRC-ACTIVERAIN-2010",
        "title": "Ladera Ranch Village Information, Tract Name, Housing Type, Homes and Builder",
        "url": "https://activerain.com/blogsview/1743192/ladera-ranch-village-information---tract-name---housing-type-----of-homes---builder",
        "path": "html/activerain_builder_crosswalk_2010.html",
        "publisher": "ActiveRain",
        "sourceType": "secondary_real_estate_directory",
        "publicationDate": "2010-07-13",
        "isOfficial": "false",
        "isPrimary": "false",
        "reliabilityGrade": "C",
    },
]

VILLAGES = [
    "oak-knoll-village",
    "flintridge-village",
    "township-district",
    "avendale-village",
    "covenant-hills-village",
    "terramor-village",
    "echo-ridge-village",
    "wycliffe-district",
    "bridgepark-district",
]


def request_bytes(url: str, params: dict[str, Any] | None = None) -> bytes:
    if params:
        url = f"{url}?{urlencode(params)}"
    request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "*/*"})
    for attempt in range(4):
        try:
            with urlopen(request, timeout=180, context=SSL_CONTEXT) as response:
                return response.read()
        except Exception as exc:
            if "CERTIFICATE_VERIFY_FAILED" in str(exc):
                completed = subprocess.run(
                    [
                        "curl",
                        "--fail",
                        "--silent",
                        "--show-error",
                        "--location",
                        "--max-time",
                        "180",
                        "--user-agent",
                        USER_AGENT,
                        url,
                    ],
                    check=True,
                    capture_output=True,
                )
                return completed.stdout
            if attempt == 3:
                raise
            time.sleep(2**attempt)
    raise RuntimeError("unreachable")


def write_atomic(path: Path, value: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as stream:
        stream.write(value)
        temp_path = Path(stream.name)
    os.replace(temp_path, path)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def archive_source(source: dict[str, str]) -> dict[str, str]:
    path = EVIDENCE / source["path"]
    row = dict(source)
    row.update(
        {
            "retrievalDate": RETRIEVAL_DATE,
            "localFilePath": str(path.relative_to(ROOT)),
            "bytes": "",
            "checksumSha256": "",
            "archiveStatus": "failed",
            "error": "",
        }
    )
    try:
        value = request_bytes(source["url"])
        if source["path"].endswith(".pdf") and not value.startswith(b"%PDF"):
            raise RuntimeError("response is not a PDF")
        write_atomic(path, value)
        row.update(
            {
                "bytes": str(path.stat().st_size),
                "checksumSha256": sha256(path),
                "archiveStatus": "retrieved",
            }
        )
    except Exception as exc:
        row["error"] = f"{type(exc).__name__}: {exc}"
    return row


def query_features(service: str, filename: str) -> dict[str, Any]:
    features: list[dict[str, Any]] = []
    offset = 0
    while True:
        payload = json.loads(
            request_bytes(
                f"{service}/query",
                {
                    "where": "1=1",
                    "geometry": ",".join(str(value) for value in AOI),
                    "geometryType": "esriGeometryEnvelope",
                    "inSR": "4326",
                    "spatialRel": "esriSpatialRelIntersects",
                    "outFields": "*",
                    "returnGeometry": "true",
                    "outSR": "4326",
                    "resultOffset": offset,
                    "resultRecordCount": 2000,
                    "orderByFields": "OBJECTID",
                    "f": "json",
                },
            )
        )
        if payload.get("error"):
            raise RuntimeError(payload["error"])
        batch = payload.get("features", [])
        features.extend(batch)
        if not payload.get("exceededTransferLimit") or not batch:
            break
        offset += len(batch)
    result = {
        "sourceService": service,
        "retrievalDate": RETRIEVAL_DATE,
        "queryBbox4326": AOI,
        "featureCount": len(features),
        "geometryType": payload.get("geometryType"),
        "spatialReference": payload.get("spatialReference"),
        "fields": payload.get("fields", []),
        "features": features,
    }
    write_atomic(EVIDENCE / "gis" / filename, (json.dumps(result, indent=2, sort_keys=True) + "\n").encode())
    return result


def archive_gis(rows: list[dict[str, str]]) -> None:
    services = [
        (
            "LH-SRC-OC-ADDRESS-POINTS",
            "Orange County Final Planning Address Points",
            "https://ocgis.com/arcpub/rest/services/Map_Layers/Address_Point_Final_Planning_Addressing/FeatureServer/0",
            "oc_address_points_ladera.json",
        ),
        (
            "LH-SRC-OC-STREET-CENTERLINES",
            "Orange County Street Centerlines with Labels",
            "https://ocgis.com/arcpub/rest/services/Map_Layers/Street_Centerlines_With_Labels/FeatureServer/2",
            "oc_street_centerlines_ladera.json",
        ),
    ]
    for source_id, title, service, filename in services:
        path = EVIDENCE / "gis" / filename
        try:
            data = query_features(service, filename)
            rows.append(
                {
                    "sourceId": source_id,
                    "title": title,
                    "url": service,
                    "path": f"gis/{filename}",
                    "publisher": "County of Orange",
                    "sourceType": "official_current_gis_layer",
                    "publicationDate": "",
                    "isOfficial": "true",
                    "isPrimary": "true",
                    "reliabilityGrade": "A2",
                    "retrievalDate": RETRIEVAL_DATE,
                    "localFilePath": str(path.relative_to(ROOT)),
                    "bytes": str(path.stat().st_size),
                    "checksumSha256": sha256(path),
                    "archiveStatus": "retrieved",
                    "error": "",
                    "recordCount": str(data["featureCount"]),
                }
            )
        except Exception as exc:
            rows.append(
                {
                    "sourceId": source_id,
                    "title": title,
                    "url": service,
                    "path": f"gis/{filename}",
                    "publisher": "County of Orange",
                    "sourceType": "official_current_gis_layer",
                    "publicationDate": "",
                    "isOfficial": "true",
                    "isPrimary": "true",
                    "reliabilityGrade": "A2",
                    "retrievalDate": RETRIEVAL_DATE,
                    "localFilePath": str(path.relative_to(ROOT)),
                    "bytes": "",
                    "checksumSha256": "",
                    "archiveStatus": "failed",
                    "error": f"{type(exc).__name__}: {exc}",
                    "recordCount": "",
                }
            )


def archive_naip(rows: list[dict[str, str]]) -> None:
    for year in (2005, 2009, 2010):
        source_id = f"LH-SRC-CDFW-NAIP-{year}"
        service = (
            "https://gis.wildlife.ca.gov/images/rest/services/"
            f"Base_Remote_Sensing/NAIP_{year}/ImageServer"
        )
        service_path = EVIDENCE / "imagery" / f"naip_{year}_service.json"
        catalog_path = EVIDENCE / "imagery" / f"naip_{year}_ladera_catalog.json"
        image_path = EVIDENCE / "imagery" / f"ladera_naip_{year}.jpg"
        request_path = EVIDENCE / "imagery" / f"ladera_naip_{year}_export.json"
        try:
            service_data = json.loads(request_bytes(service, {"f": "pjson"}))
            write_atomic(service_path, (json.dumps(service_data, indent=2, sort_keys=True) + "\n").encode())
            catalog = json.loads(
                request_bytes(
                    f"{service}/query",
                    {
                        "where": "Category=1 AND LowPS<=1.1",
                        "geometry": ",".join(str(value) for value in AOI),
                        "geometryType": "esriGeometryEnvelope",
                        "inSR": "4326",
                        "spatialRel": "esriSpatialRelIntersects",
                        "outFields": "*",
                        "returnGeometry": "true",
                        "outSR": "4326",
                        "f": "json",
                    },
                )
            )
            write_atomic(catalog_path, (json.dumps(catalog, indent=2, sort_keys=True) + "\n").encode())
            params = {
                "bbox": ",".join(str(value) for value in AOI),
                "bboxSR": "4326",
                "imageSR": "4326",
                "size": "3600,4000",
                "format": "jpg",
                "compressionQuality": "92",
                "interpolation": "RSP_BilinearInterpolation",
                "f": "image",
            }
            value = request_bytes(f"{service}/exportImage", params)
            if not value.startswith(b"\xff\xd8") or len(value) < 100_000:
                raise RuntimeError("unexpected NAIP export response")
            write_atomic(image_path, value)
            request_data = {
                "sourceId": source_id,
                "service": service,
                "retrievalDate": RETRIEVAL_DATE,
                "queryBbox4326": AOI,
                "parameters": params,
                "catalogNames": [
                    feature.get("attributes", {}).get("Name", "")
                    for feature in catalog.get("features", [])
                ],
                "imageChecksumSha256": sha256(image_path),
            }
            write_atomic(request_path, (json.dumps(request_data, indent=2, sort_keys=True) + "\n").encode())
            rows.append(
                {
                    "sourceId": source_id,
                    "title": f"California NAIP {year} natural-color aerial imagery",
                    "url": service,
                    "path": f"imagery/ladera_naip_{year}.jpg",
                    "publisher": "California Department of Fish and Wildlife / USDA FSA",
                    "sourceType": "official_aerial_imagery",
                    "publicationDate": str(year),
                    "isOfficial": "true",
                    "isPrimary": "true",
                    "reliabilityGrade": "A1",
                    "retrievalDate": RETRIEVAL_DATE,
                    "localFilePath": str(image_path.relative_to(ROOT)),
                    "bytes": str(image_path.stat().st_size),
                    "checksumSha256": sha256(image_path),
                    "archiveStatus": "retrieved",
                    "error": "",
                    "recordCount": str(len(catalog.get("features", []))),
                }
            )
        except Exception as exc:
            rows.append(
                {
                    "sourceId": source_id,
                    "title": f"California NAIP {year} natural-color aerial imagery",
                    "url": service,
                    "path": f"imagery/ladera_naip_{year}.jpg",
                    "publisher": "California Department of Fish and Wildlife / USDA FSA",
                    "sourceType": "official_aerial_imagery",
                    "publicationDate": str(year),
                    "isOfficial": "true",
                    "isPrimary": "true",
                    "reliabilityGrade": "A1",
                    "retrievalDate": RETRIEVAL_DATE,
                    "localFilePath": str(image_path.relative_to(ROOT)),
                    "bytes": "",
                    "checksumSha256": "",
                    "archiveStatus": "failed",
                    "error": f"{type(exc).__name__}: {exc}",
                    "recordCount": "",
                }
            )


def main() -> int:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    source_rows = [archive_source(source) for source in SOURCES]
    for index, slug in enumerate(VILLAGES, start=1):
        source_rows.append(
            archive_source(
                {
                    "sourceId": f"LH-SRC-LARMAC-VILLAGE-{index}",
                    "title": f"LaderaLife village directory: {slug.replace('-', ' ').title()}",
                    "url": f"https://laderalife.com/villages/{slug}",
                    "path": f"html/laderalife_village_{index}_{slug}.html",
                    "publisher": "Ladera Ranch Maintenance Corporation",
                    "sourceType": "official_community_directory",
                    "publicationDate": "",
                    "isOfficial": "true",
                    "isPrimary": "true",
                    "reliabilityGrade": "A2",
                }
            )
        )
    archive_gis(source_rows)
    archive_naip(source_rows)

    fields = sorted({key for row in source_rows for key in row})
    manifest = EVIDENCE / "acquisition_manifest.csv"
    with tempfile.NamedTemporaryFile(
        mode="w", newline="", encoding="utf-8", dir=manifest.parent, delete=False
    ) as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(source_rows)
        temp_path = Path(stream.name)
    os.replace(temp_path, manifest)

    summary = {
        "retrievalDate": RETRIEVAL_DATE,
        "requested": len(source_rows),
        "retrieved": sum(row.get("archiveStatus") == "retrieved" for row in source_rows),
        "failed": sum(row.get("archiveStatus") != "retrieved" for row in source_rows),
        "manifestChecksumSha256": sha256(manifest),
    }
    write_atomic(EVIDENCE / "acquisition_summary.json", (json.dumps(summary, indent=2) + "\n").encode())
    print(json.dumps(summary, indent=2))
    return 0 if summary["failed"] == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
