#!/usr/bin/env python3
"""Archive official County terrain and drainage inputs for LHDRS Mission 4."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import os
from pathlib import Path
import tempfile
import time
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from pyproj import Transformer


ROOT = Path(__file__).resolve().parents[1]
BOUNDARY = ROOT / "data/development/ladera_ranch_cdp.geojson"
EVIDENCE = ROOT / "evidence/lhdrs/terrain"
RESEARCH = ROOT / "research/development_chronology"
REGISTRY = RESEARCH / "sources.csv"
MANIFEST = RESEARCH / "terrain_source_manifest.csv"

DEM_SERVICE = "https://ocgis.com/arcpub/rest/services/Elevation/oc_dem_1m_2018/ImageServer"
DEM_2021_ITEMINFO = (
    "https://ocgis.com/arcpub/rest/services/Elevation/"
    "oc_dem_1m_2021_tif_AGOL_Tile/ImageServer/info/iteminfo"
)
WATERSHED_LAYER = (
    "https://ocgis.com/arcpub/rest/services/Map_Layers/Watersheds/MapServer/0"
)
STREAM_LAYER = (
    "https://ocgis.com/arcpub/rest/services/Environmental_Resources/"
    "South_OC_Stream_Centerlines/FeatureServer/0"
)
FLOOD_CHANNEL_LAYER = (
    "https://ocgis.com/arcpub/rest/services/Map_Layers/Flood_Channels/MapServer/0"
)

SOURCE_ROWS = {
    "LH-SRC-OC-DEM-2018": {
        "title": "Orange County 2018 one-meter digital elevation model",
        "publisher": "Orange County Public Works OC Survey",
        "url": DEM_SERVICE,
        "publicationDate": "2018",
        "sourceType": "digital_elevation_model",
        "geographicCoverage": "Orange County, California",
        "timeCoverage": "2018",
        "isOfficial": "true",
        "isPrimary": "true",
        "dataFormat": "GeoTIFF and ArcGIS service metadata",
        "reliabilityGrade": "A1",
        "knownLimitations": (
            "Post-study-period terrain surface; grading may have changed landform since 1997-2010. "
            "The 2018 service metadata leaves the band-value unit element blank, so the U.S.-foot "
            "vertical interpretation is documented as an inference and converted explicitly."
        ),
        "notes": (
            "Five-meter analysis extract clipped around the current Census CDP from the official "
            "one-meter service; used only for terrain context."
        ),
    },
    "LH-SRC-OC-WATERSHEDS": {
        "title": "Orange County watershed boundaries",
        "publisher": "Orange County Public Works",
        "url": WATERSHED_LAYER,
        "publicationDate": "current",
        "sourceType": "watershed_gis",
        "geographicCoverage": "Orange County, California",
        "timeCoverage": "current",
        "isOfficial": "true",
        "isPrimary": "true",
        "dataFormat": "GeoJSON and ArcGIS service metadata",
        "reliabilityGrade": "A1",
        "knownLimitations": (
            "Current broad watershed boundary; does not establish historical site drainage, "
            "stormwater routing, or parcel-scale flow paths."
        ),
        "notes": "Used to identify the named watershed intersecting the current Ladera Ranch CDP.",
    },
    "LH-SRC-OC-STREAMS-2016": {
        "title": "South Orange County stream centerlines",
        "publisher": "Orange County Public Works",
        "url": STREAM_LAYER,
        "publicationDate": "2016",
        "sourceType": "lidar_derived_stream_gis",
        "geographicCoverage": "South Orange County, California",
        "timeCoverage": "2015-2016",
        "isOfficial": "true",
        "isPrimary": "true",
        "dataFormat": "GeoJSON and ArcGIS service metadata",
        "reliabilityGrade": "A1",
        "knownLimitations": (
            "LiDAR-derived 2016 hydrographic context, not a historical 1997-2010 drainage map; "
            "centerlines do not by themselves distinguish perennial flow."
        ),
        "notes": "County metadata identifies 2016 LiDAR and 2015 aerial imagery inputs.",
    },
    "LH-SRC-OC-FLOOD-CHANNELS": {
        "title": "Orange County flood channels and as-built drawing inventory",
        "publisher": "Orange County Public Works",
        "url": FLOOD_CHANNEL_LAYER,
        "publicationDate": "current",
        "sourceType": "flood_control_infrastructure_gis",
        "geographicCoverage": "Orange County, California",
        "timeCoverage": "various",
        "isOfficial": "true",
        "isPrimary": "true",
        "dataFormat": "GeoJSON and ArcGIS service metadata",
        "reliabilityGrade": "A1",
        "knownLimitations": (
            "Inventory attributes may include design drawing dates while as-built fields remain "
            "blank; a drawing year is not treated as construction completion or occupancy evidence."
        ),
        "notes": "Used for descriptive drainage-infrastructure context and document leads.",
    },
}


def request_bytes(url: str, params: dict[str, Any] | None = None) -> bytes:
    if params:
        url = f"{url}?{urlencode(params)}"
    request = Request(url, headers={"User-Agent": "LHDRS-Mission4/1.0"})
    last_error: Exception | None = None
    for attempt in range(4):
        try:
            with urlopen(request, timeout=120) as response:
                return response.read()
        except Exception as exc:  # network retry boundary
            last_error = exc
            if attempt == 3:
                raise
            time.sleep(2**attempt)
    raise RuntimeError(str(last_error))


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


def coordinate_pairs(value: Any):
    if (
        isinstance(value, list)
        and len(value) >= 2
        and isinstance(value[0], (int, float))
        and isinstance(value[1], (int, float))
    ):
        yield float(value[0]), float(value[1])
    elif isinstance(value, list):
        for item in value:
            yield from coordinate_pairs(item)


def boundary_extents() -> tuple[tuple[float, float, float, float], tuple[float, float, float, float]]:
    data = json.loads(BOUNDARY.read_text(encoding="utf-8"))
    lon_lat = []
    for feature in data["features"]:
        lon_lat.extend(coordinate_pairs(feature["geometry"]["coordinates"]))
    lon = [item[0] for item in lon_lat]
    lat = [item[1] for item in lon_lat]
    geographic = (min(lon), min(lat), max(lon), max(lat))
    transformer = Transformer.from_crs(4326, 26946, always_xy=True)
    projected = [transformer.transform(x, y) for x, y in lon_lat]
    east = [item[0] for item in projected]
    north = [item[1] for item in projected]
    projected_extent = (
        min(east) - 100,
        min(north) - 100,
        max(east) + 100,
        max(north) + 100,
    )
    return geographic, projected_extent


def archive_json(url: str, path: Path, params: dict[str, Any] | None = None) -> None:
    raw = request_bytes(url, params)
    parsed = json.loads(raw)
    write_atomic(path, (json.dumps(parsed, indent=2, sort_keys=True) + "\n").encode())


def archive_layer(
    source_id: str,
    layer_url: str,
    stem: str,
    bbox: tuple[float, float, float, float],
) -> list[dict[str, object]]:
    metadata_path = EVIDENCE / f"{stem}_service.json"
    geojson_path = EVIDENCE / f"{stem}.geojson"
    archive_json(layer_url, metadata_path, {"f": "pjson"})
    query = {
        "geometry": ",".join(f"{value:.8f}" for value in bbox),
        "geometryType": "esriGeometryEnvelope",
        "inSR": "4326",
        "spatialRel": "esriSpatialRelIntersects",
        "outFields": "*",
        "returnGeometry": "true",
        "outSR": "4326",
        "f": "geojson",
    }
    raw = request_bytes(f"{layer_url}/query", query)
    data = json.loads(raw)
    if data.get("type") != "FeatureCollection":
        raise RuntimeError(f"Unexpected {stem} response: {data}")
    write_atomic(geojson_path, (json.dumps(data, indent=2, sort_keys=True) + "\n").encode())
    return [manifest_row(source_id, layer_url, metadata_path), manifest_row(source_id, layer_url, geojson_path)]


def archive_dem(projected: tuple[float, float, float, float]) -> list[dict[str, object]]:
    metadata_paths = [
        (f"{DEM_SERVICE}", EVIDENCE / "oc_dem_1m_2018_service.json", {"f": "pjson"}),
        (
            f"{DEM_SERVICE}/info/iteminfo",
            EVIDENCE / "oc_dem_1m_2018_iteminfo.json",
            {"f": "pjson"},
        ),
        (
            DEM_2021_ITEMINFO,
            EVIDENCE / "oc_dem_1m_2021_iteminfo_unit_context.json",
            {"f": "pjson"},
        ),
    ]
    rows = []
    for url, path, params in metadata_paths:
        archive_json(url, path, params)
        rows.append(manifest_row("LH-SRC-OC-DEM-2018", url, path))
    xml_path = EVIDENCE / "oc_dem_1m_2018_metadata.xml"
    write_atomic(xml_path, request_bytes(f"{DEM_SERVICE}/info/metadata"))
    rows.append(manifest_row("LH-SRC-OC-DEM-2018", f"{DEM_SERVICE}/info/metadata", xml_path))

    xmin, ymin, xmax, ymax = projected
    resolution_m = 5.0
    width = math.ceil((xmax - xmin) / resolution_m)
    height = math.ceil((ymax - ymin) / resolution_m)
    export_params = {
        "bbox": f"{xmin:.3f},{ymin:.3f},{xmax:.3f},{ymax:.3f}",
        "bboxSR": "26946",
        "imageSR": "26946",
        "size": f"{width},{height}",
        "format": "tiff",
        "pixelType": "F32",
        "interpolation": "RSP_BilinearInterpolation",
        "f": "json",
    }
    export = json.loads(request_bytes(f"{DEM_SERVICE}/exportImage", export_params))
    if "href" not in export:
        raise RuntimeError(f"DEM export failed: {export}")
    request_path = EVIDENCE / "ladera_dem_2018_5m_export_request.json"
    request_record = {"service": DEM_SERVICE, "parameters": export_params, "response": export}
    write_atomic(request_path, (json.dumps(request_record, indent=2, sort_keys=True) + "\n").encode())
    rows.append(manifest_row("LH-SRC-OC-DEM-2018", f"{DEM_SERVICE}/exportImage", request_path))

    dem_path = EVIDENCE / "ladera_dem_2018_5m.tif"
    raster = request_bytes(export["href"])
    if raster[:4] not in {b"II*\x00", b"MM\x00*"}:
        raise RuntimeError("DEM response is not a TIFF")
    write_atomic(dem_path, raster)
    rows.append(manifest_row("LH-SRC-OC-DEM-2018", f"{DEM_SERVICE}/exportImage", dem_path))
    return rows


def manifest_row(source_id: str, url: str, path: Path) -> dict[str, object]:
    return {
        "sourceId": source_id,
        "url": url,
        "localFilePath": str(path.relative_to(ROOT)),
        "bytes": path.stat().st_size,
        "checksumSha256": sha256(path),
        "archiveStatus": "retrieved",
        "error": "",
    }


def write_csv_atomic(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w", newline="", encoding="utf-8", dir=path.parent, delete=False
    ) as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temp_path = Path(stream.name)
    os.replace(temp_path, path)


def update_registry(source_id: str) -> None:
    with REGISTRY.open(newline="", encoding="utf-8-sig") as stream:
        reader = csv.DictReader(stream)
        fields = list(reader.fieldnames or [])
        rows = list(reader)
    values = SOURCE_ROWS[source_id]
    registry_row = {field: "" for field in fields}
    registry_row.update(values)
    registry_row.update(
        {
            "id": source_id,
            "author": "",
            "archiveUrl": "",
            "retrievalDate": "2026-07-26",
            "localFilePath": str(MANIFEST.relative_to(ROOT)),
            "checksumSha256": sha256(MANIFEST),
            "archiveStatus": "retrieved_collection",
        }
    )
    for index, row in enumerate(rows):
        if row["id"] == source_id:
            rows[index] = registry_row
            break
    else:
        rows.append(registry_row)
    write_csv_atomic(REGISTRY, rows, fields)


def main() -> int:
    geographic, projected = boundary_extents()
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    rows = archive_dem(projected)
    rows.extend(archive_layer("LH-SRC-OC-WATERSHEDS", WATERSHED_LAYER, "watersheds", geographic))
    rows.extend(archive_layer("LH-SRC-OC-STREAMS-2016", STREAM_LAYER, "south_oc_stream_centerlines", geographic))
    rows.extend(archive_layer("LH-SRC-OC-FLOOD-CHANNELS", FLOOD_CHANNEL_LAYER, "flood_channels", geographic))
    rows.sort(key=lambda row: str(row["localFilePath"]))
    write_csv_atomic(MANIFEST, rows, list(rows[0]))
    for source_id in SOURCE_ROWS:
        update_registry(source_id)
    dem_bytes = next(
        row["bytes"] for row in rows if row["localFilePath"].endswith("ladera_dem_2018_5m.tif")
    )
    print(f"DONE  archived {len(rows)} terrain/drainage files; DEM extract {dem_bytes} bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
