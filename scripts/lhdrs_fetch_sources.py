#!/usr/bin/env python3
"""Archive LHDRS public sources and refresh official boundary/tract GIS.

This script performs network access. It is safe to rerun: canonical research tables are
preserved, downloaded evidence is replaced only by a successfully retrieved response, and
generated GIS is written atomically. Source-registry checksums and archive statuses are
updated with the CSV module rather than text substitution.
"""

from __future__ import annotations

import csv
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile
from typing import Optional
import urllib.error
import urllib.parse
import urllib.request


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "research/development_chronology/sources.csv"
USER_AGENT = "LHDRS/1.0 public historical-development research"

DOWNLOADS = {
    "LH-SRC-OC-MAP": (
        "https://pwds.oc.gov/sites/ocpwocds/files/import/data/files/9268.pdf",
        "evidence/lhdrs/county/Ladera_Ranch_Planned_Community_Map.pdf",
    ),
    "LH-SRC-OC-DA": (
        "https://pwds.oc.gov/sites/ocpwocds/files/import/data/files/9272.pdf",
        "evidence/lhdrs/county/Ladera_Ranch_Development_Agreement.pdf",
    ),
    "LH-SRC-OC-ADS": (
        "https://pwds.oc.gov/sites/ocpwocds/files/import/data/files/9270.pdf",
        "evidence/lhdrs/county/Ladera_Ranch_Alternative_Development_Standards.pdf",
    ),
    "LH-SRC-OC-EIR-CERT": (
        "https://ocds.ocpublicworks.com/sites/ocpwocds/files/import/data/files/80931.pdf",
        "evidence/lhdrs/county/PA180010_Zoning_Administrator_Record.pdf",
    ),
    "LH-SRC-CUSD-CHAPARRAL": (
        "https://www.capousd.org/documents/Schools/SARCS/Elementary/2022-SARC-Chaparral-Elementary-School.pdf",
        "evidence/lhdrs/schools/2022_SARC_Chaparral_Elementary.pdf",
    ),
    "LH-SRC-CUSD-LRES": (
        "https://www.capousd.org/documents/Schools/SARCS/Elementary/2022-SARC-Ladera-Ranch-Elementary-School.pdf",
        "evidence/lhdrs/schools/2022_SARC_Ladera_Ranch_Elementary.pdf",
    ),
    "LH-SRC-CUSD-LRMS": (
        "https://www.capousd.org/documents/Schools/SARCS/Middle/2022-SARC-Ladera-Ranch-Middle-School.pdf",
        "evidence/lhdrs/schools/2022_SARC_Ladera_Ranch_Middle.pdf",
    ),
    "LH-SRC-ULI-CASE": (
        "https://casestudies.uli.org/wp-content/uploads/2016/06/Ladera-Ranch.pdf",
        "evidence/lhdrs/publications/ULI_Ladera_Ranch_Case_Study.pdf",
    ),
    "LH-SRC-CEQANET-UTILITIES": (
        "https://ceqanet.lci.ca.gov/1999031033",
        "evidence/lhdrs/web/ceqanet_1999031033.html",
    ),
    "LH-SRC-RMV-PLANNING": (
        "https://www.ranchomissionviejo.com/about/responsible-planning",
        "evidence/lhdrs/web/rmv_responsible_planning.html",
    ),
    "LH-SRC-LARMAC-TIMELINE": (
        "https://laderalife.com/about/explore-ladera-ranch",
        "evidence/lhdrs/web/laderalife_timeline.html",
    ),
    "LH-SRC-CDE-OSO": (
        "https://www.cde.ca.gov/schooldirectory/details?cdscode=30664640108704",
        "evidence/lhdrs/web/cde_oso_grande.html",
    ),
    "LH-SRC-NWS-ELTORO": (
        "https://www.weather.gov/sgx/orange-eltoro",
        "evidence/lhdrs/web/nws_el_toro_climate.html",
    ),
    "LH-SRC-NWS-SANTA-ANA": (
        "https://www.weather.gov/safety/wind-mountain-valley",
        "evidence/lhdrs/web/nws_santa_ana_winds.html",
    ),
}

TIGER_QUERY = (
    "https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/"
    "Places_CouSub_ConCity_SubMCD/MapServer/5/query"
)
TRACT_QUERY = (
    "https://ocgis.com/arcpub/rest/services/Map_Layers/Tract_Maps/MapServer/0/query"
)
IMAGERY_EXPORT = (
    "https://ocgis.com/arcpub/rest/services/Historic_Imagery/"
    "Historic_Imagery_v2/ImageServer/exportImage"
)


def request_bytes(url: str, params: Optional[dict[str, str]] = None, post: bool = False) -> bytes:
    encoded = urllib.parse.urlencode(params or {}).encode("utf-8")
    if post:
        request = urllib.request.Request(url, data=encoded, headers={"User-Agent": USER_AGENT})
    else:
        suffix = ("?" + encoded.decode("utf-8")) if params else ""
        request = urllib.request.Request(url + suffix, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=90) as response:
        return response.read()


def request_json(url: str, params: dict[str, str], post: bool = False) -> dict:
    return json.loads(request_bytes(url, params=params, post=post))


def write_bytes_atomic(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as stream:
        stream.write(content)
        temp_path = Path(stream.name)
    os.replace(temp_path, path)


def write_json_atomic(path: Path, value: object) -> None:
    content = (json.dumps(value, indent=2, ensure_ascii=True) + "\n").encode("utf-8")
    write_bytes_atomic(path, content)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def archive_downloads(manifest: list[dict]) -> None:
    for source_id, (url, relative_path) in DOWNLOADS.items():
        target = ROOT / relative_path
        try:
            payload = request_bytes(url)
            if len(payload) < 200:
                raise ValueError(f"response unexpectedly short ({len(payload)} bytes)")
            write_bytes_atomic(target, payload)
            record = {
                "sourceId": source_id,
                "url": url,
                "localFilePath": relative_path,
                "bytes": len(payload),
                "checksumSha256": sha256(target),
                "status": "retrieved",
            }
            print(f"FETCH {source_id}: {len(payload):,} bytes")
        except (OSError, ValueError, urllib.error.URLError) as exc:
            record = {
                "sourceId": source_id,
                "url": url,
                "localFilePath": relative_path,
                "status": "failed",
                "error": str(exc),
            }
            print(f"WARN  {source_id}: {exc}")
        manifest.append(record)


def fetch_cdp_boundary(manifest: list[dict]) -> dict:
    data = request_json(
        TIGER_QUERY,
        {
            "where": "BASENAME='Ladera Ranch' AND STATE='06'",
            "outFields": "*",
            "outSR": "4326",
            "f": "geojson",
        },
    )
    if len(data.get("features", [])) != 1:
        raise RuntimeError("TIGERweb did not return exactly one Ladera Ranch CDP")
    feature = data["features"][0]
    feature["properties"]["sourceId"] = "LH-SRC-CENSUS-CDP"
    feature["properties"]["geometryPrecision"] = "official current CDP boundary"
    feature["properties"]["knownLimitations"] = (
        "Current statistical boundary; not the 1997 entitlement boundary"
    )
    output = {"type": "FeatureCollection", "features": [feature]}
    path = ROOT / "data/development/ladera_ranch_cdp.geojson"
    write_json_atomic(path, output)
    manifest.append(
        {
            "sourceId": "LH-SRC-CENSUS-CDP",
            "url": TIGER_QUERY,
            "localFilePath": str(path.relative_to(ROOT)),
            "checksumSha256": sha256(path),
            "status": "generated_archive",
        }
    )
    print("GIS   LH-SRC-CENSUS-CDP: 1 official boundary")
    return output


def epoch_date(value: Optional[int]) -> str:
    if value is None:
        return ""
    return dt.datetime.fromtimestamp(value / 1000, tz=dt.timezone.utc).date().isoformat()


def fetch_tract_maps(cdp: dict, manifest: list[dict]) -> None:
    rings = cdp["features"][0]["geometry"]["coordinates"]
    geometry = json.dumps(
        {"rings": rings, "spatialReference": {"wkid": 4326}}, separators=(",", ":")
    )
    raw = request_json(
        TRACT_QUERY,
        {
            "where": "1=1",
            "geometry": geometry,
            "geometryType": "esriGeometryPolygon",
            "inSR": "4326",
            "spatialRel": "esriSpatialRelIntersects",
            "outFields": (
                "OBJECTID,BPNUM,RECORDDATE,TRACTNUM,ENGCO,ENGSVYNAME,"
                "ENGSVYNUM,CITIES,GEOPAGE"
            ),
            "outSR": "4326",
            "returnGeometry": "true",
            "f": "geojson",
        },
        post=True,
    )
    if raw.get("error"):
        raise RuntimeError(f"tract service error: {raw['error']}")

    all_features = []
    atlas_features = []
    for feature in raw.get("features", []):
        source = feature.get("properties", {})
        record_date = epoch_date(source.get("RECORDDATE"))
        year = int(record_date[:4]) if record_date else None
        feature["properties"] = {
            "sourceId": "LH-SRC-OC-TRACTS",
            "sourceObjectId": source.get("OBJECTID"),
            "tractNumber": (source.get("TRACTNUM") or "").replace("TR ", ""),
            "bookPage": source.get("BPNUM") or "",
            "recordDate": record_date,
            "recordYear": year,
            "engineeringCompany": source.get("ENGCO") or "",
            "engineerSurveyor": source.get("ENGSVYNAME") or "",
            "licenseNumber": source.get("ENGSVYNUM") or "",
            "jurisdiction": source.get("CITIES") or "",
            "georeferencedPages": source.get("GEOPAGE") or "",
            "statementClass": "documented_exact",
            "confidence": "high",
            "geometryPrecision": "official County tract-map polygon",
            "knownLimitations": (
                "Map recording is a legal subdivision milestone; it does not establish "
                "grading, construction, sale, road opening, or occupancy"
            ),
        }
        all_features.append(feature)
        if year is not None and 1998 <= year <= 2008:
            atlas_features.append(feature)

    all_output = {"type": "FeatureCollection", "features": all_features}
    atlas_output = {"type": "FeatureCollection", "features": atlas_features}
    all_path = ROOT / "data/development/tract_maps_all_cdp_intersections.geojson"
    atlas_path = ROOT / "data/development/tract_maps.geojson"
    write_json_atomic(all_path, all_output)
    write_json_atomic(atlas_path, atlas_output)
    manifest.append(
        {
            "sourceId": "LH-SRC-OC-TRACTS",
            "url": TRACT_QUERY,
            "localFilePath": str(atlas_path.relative_to(ROOT)),
            "checksumSha256": sha256(atlas_path),
            "status": "generated_archive",
            "featureCount": len(atlas_features),
            "allIntersectingFeatureCount": len(all_features),
        }
    )
    print(
        f"GIS   LH-SRC-OC-TRACTS: {len(atlas_features)} records from 1998-2008 "
        f"({len(all_features)} all-date intersections)"
    )


def fetch_1998_imagery(cdp: dict, manifest: list[dict]) -> None:
    coords = cdp["features"][0]["geometry"]["coordinates"][0]
    min_lon = min(point[0] for point in coords)
    max_lon = max(point[0] for point in coords)
    min_lat = min(point[1] for point in coords)
    max_lat = max(point[1] for point in coords)
    padding = 0.002
    bbox = f"{min_lon-padding},{min_lat-padding},{max_lon+padding},{max_lat+padding}"
    params = {
        "bbox": bbox,
        "bboxSR": "4326",
        "imageSR": "4326",
        "size": "1800,2400",
        "format": "png32",
        "transparent": "true",
        "interpolation": "RSP_BilinearInterpolation",
        "mosaicRule": json.dumps(
            {"mosaicMethod": "esriMosaicLockRaster", "lockRasterIds": [33]},
            separators=(",", ":"),
        ),
        "f": "image",
    }
    try:
        payload = request_bytes(IMAGERY_EXPORT, params)
        if len(payload) < 10_000:
            raise ValueError(f"image response unexpectedly short ({len(payload)} bytes)")
        image_path = ROOT / "evidence/lhdrs/imagery/ladera_1997_1998.png"
        write_bytes_atomic(image_path, payload)
        metadata = {
            "id": "LH-IMG-1997-1998",
            "sourceId": "LH-SRC-OC-IMAGERY",
            "sourceObjectId": 33,
            "sourceName": "O'Neil Regional Park (June) 1998",
            "dateOnMap": 1997,
            "dateCurrent": 1998,
            "coordinates": [
                [min_lon - padding, max_lat + padding],
                [max_lon + padding, max_lat + padding],
                [max_lon + padding, min_lat - padding],
                [min_lon - padding, min_lat - padding],
            ],
            "registration": "County rectified ImageServer export",
            "coverage": "Partial flight footprint; transparent pixels mark no-data areas",
            "knownLimitations": "Frame date metadata distinguishes 1997 date-on-map and June 1998 current date; coverage does not fill the full display extent",
        }
        meta_path = ROOT / "data/development/imagery_1998.json"
        write_json_atomic(meta_path, metadata)
        manifest.append(
            {
                "sourceId": "LH-SRC-OC-IMAGERY",
                "url": IMAGERY_EXPORT,
                "localFilePath": str(image_path.relative_to(ROOT)),
                "checksumSha256": sha256(image_path),
                "status": "retrieved",
                "bytes": len(payload),
            }
        )
        print(f"FETCH LH-SRC-OC-IMAGERY: {len(payload):,} bytes")
    except (OSError, ValueError, urllib.error.URLError) as exc:
        manifest.append(
            {
                "sourceId": "LH-SRC-OC-IMAGERY",
                "url": IMAGERY_EXPORT,
                "localFilePath": "evidence/lhdrs/imagery/ladera_1997_1998.png",
                "status": "failed",
                "error": str(exc),
            }
        )
        print(f"WARN  LH-SRC-OC-IMAGERY: {exc}")


def update_source_registry(manifest: list[dict]) -> None:
    with REGISTRY.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        fieldnames = reader.fieldnames or []
        rows = list(reader)

    by_id = {item["sourceId"]: item for item in manifest if item.get("sourceId")}
    for row in rows:
        local = ROOT / row["localFilePath"] if row.get("localFilePath") else None
        result = by_id.get(row["id"])
        if local and local.exists():
            row["checksumSha256"] = sha256(local)
            row["archiveStatus"] = (
                result.get("status", "local_copy") if result else "local_copy"
            )
        elif result and result.get("status") == "failed":
            row["archiveStatus"] = "fetch_failed"

    temp = REGISTRY.with_suffix(".csv.tmp")
    with temp.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    os.replace(temp, REGISTRY)


def main() -> int:
    manifest: list[dict] = []
    archive_downloads(manifest)
    cdp = fetch_cdp_boundary(manifest)
    fetch_tract_maps(cdp, manifest)
    fetch_1998_imagery(cdp, manifest)

    # Register the already archived planning program even though this run does not duplicate it.
    planning_path = ROOT / "evidence/documents/Ladera_Planned_Community_Program_Text_1995_rev2003.pdf"
    if planning_path.exists():
        manifest.append(
            {
                "sourceId": "LH-SRC-OC-PC",
                "localFilePath": str(planning_path.relative_to(ROOT)),
                "checksumSha256": sha256(planning_path),
                "status": "local_copy",
            }
        )

    update_source_registry(manifest)
    manifest_path = ROOT / "evidence/lhdrs/fetch_manifest.json"
    write_json_atomic(
        manifest_path,
        {
            "retrievedAt": dt.datetime.now(tz=dt.timezone.utc).isoformat(),
            "userAgent": USER_AGENT,
            "records": manifest,
        },
    )
    failures = sum(item.get("status") == "failed" for item in manifest)
    print(f"DONE  {len(manifest)} source operations; {failures} failed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
