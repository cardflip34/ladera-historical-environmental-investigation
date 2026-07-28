#!/usr/bin/env python3
"""Build bounded terrain and drainage context from archived County GIS inputs."""

from __future__ import annotations

import csv
import json
import math
import os
from pathlib import Path
import tempfile

import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio
from rasterio.features import geometry_mask
from shapely.geometry import mapping


ROOT = Path(__file__).resolve().parents[2]
RESEARCH = ROOT / "research/development_chronology"
EVIDENCE = ROOT / "evidence/lhdrs/terrain"
DATA = ROOT / "data/development"
DOCS = ROOT / "docs/lhdrs"
DEM = EVIDENCE / "ladera_dem_2018_5m.tif"
BOUNDARY = DATA / "ladera_ranch_cdp.geojson"
TRACTS = DATA / "tract_maps.geojson"
US_SURVEY_FOOT_M = 1200 / 3937
SOURCE_IDS = "LH-SRC-OC-DEM-2018;LH-SRC-CENSUS-CDP"
LIMITATIONS = (
    "2018 post-study terrain sampled within the current Census CDP; not a 1997-2010 surface, "
    "not parcel-scale hydrologic routing, and not evidence of material movement between locations."
)


def write_csv(name: str, rows: list[dict[str, object]], fields: list[str]) -> None:
    path = RESEARCH / name
    with tempfile.NamedTemporaryFile(
        mode="w", newline="", encoding="utf-8", dir=path.parent, delete=False
    ) as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
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


def write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", dir=path.parent, delete=False
    ) as stream:
        stream.write(value)
        temp_path = Path(stream.name)
    os.replace(temp_path, path)


def valid_geometry(frame: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    result = frame.copy()
    result["geometry"] = result.geometry.make_valid()
    return result[result.geometry.notna() & ~result.geometry.is_empty]


def percent(numerator: int, denominator: int) -> str:
    return f"{numerator / denominator * 100:.2f}" if denominator else ""


def aspect_sector(aspect: np.ndarray, slope: np.ndarray) -> np.ndarray:
    sectors = np.full(aspect.shape, "flat", dtype=object)
    active = slope >= 2
    sector_index = ((aspect + 22.5) // 45).astype(int) % 8
    labels = np.array(["N", "NE", "E", "SE", "S", "SW", "W", "NW"], dtype=object)
    sectors[active] = labels[sector_index[active]]
    return sectors


def summarize_mask(
    mask: np.ndarray,
    elevation_m: np.ndarray,
    slope: np.ndarray,
    sectors: np.ndarray,
    pixel_area: float,
) -> dict[str, object]:
    finite = mask & np.isfinite(elevation_m) & np.isfinite(slope)
    elevations = elevation_m[finite]
    slopes = slope[finite]
    local_sectors = sectors[finite]
    count = int(finite.sum())
    if not count:
        return {"pixelCount": 0}
    sector_counts = {label: int(np.sum(local_sectors == label)) for label in ["flat", "N", "NE", "E", "SE", "S", "SW", "W", "NW"]}
    facing = {
        "north": sector_counts["NW"] + sector_counts["N"] + sector_counts["NE"],
        "east": sector_counts["NE"] + sector_counts["E"] + sector_counts["SE"],
        "south": sector_counts["SE"] + sector_counts["S"] + sector_counts["SW"],
        "west": sector_counts["SW"] + sector_counts["W"] + sector_counts["NW"],
    }
    dominant = max(sector_counts, key=sector_counts.get)
    return {
        "pixelCount": count,
        "sampledAreaSqM": f"{count * pixel_area:.1f}",
        "minElevationM": f"{np.min(elevations):.1f}",
        "medianElevationM": f"{np.median(elevations):.1f}",
        "meanElevationM": f"{np.mean(elevations):.1f}",
        "maxElevationM": f"{np.max(elevations):.1f}",
        "reliefM": f"{np.max(elevations) - np.min(elevations):.1f}",
        "meanSlopeDeg": f"{np.mean(slopes):.2f}",
        "medianSlopeDeg": f"{np.median(slopes):.2f}",
        "p90SlopeDeg": f"{np.percentile(slopes, 90):.2f}",
        "steepSlopeGe20DegPct": percent(int(np.sum(slopes >= 20)), count),
        "dominantAspectSector": dominant,
        "flatLt2DegPct": percent(sector_counts["flat"], count),
        "northFacingPct": percent(facing["north"], count),
        "eastFacingPct": percent(facing["east"], count),
        "southFacingPct": percent(facing["south"], count),
        "westFacingPct": percent(facing["west"], count),
    }


def terrain_rows() -> tuple[list[dict[str, object]], dict[str, object], gpd.GeoDataFrame]:
    boundary = valid_geometry(gpd.read_file(BOUNDARY).to_crs(26946))
    tracts = valid_geometry(gpd.read_file(TRACTS).to_crs(26946))
    with rasterio.open(DEM) as dataset:
        native = dataset.read(1).astype("float64")
        elevation_m = native * US_SURVEY_FOOT_M
        xres, yres = dataset.res
        dz_south, dz_east = np.gradient(elevation_m, yres, xres)
        slope = np.degrees(np.arctan(np.hypot(dz_east, dz_south)))
        aspect = (np.degrees(np.arctan2(-dz_east, dz_south)) + 360) % 360
        sectors = aspect_sector(aspect, slope)
        transform = dataset.transform
        shape = native.shape
        crs = dataset.crs
        pixel_area = abs(transform.a * transform.e)

    community_geometry = boundary.geometry.union_all()
    community_mask = geometry_mask(
        [mapping(community_geometry)], out_shape=shape, transform=transform, invert=True
    )
    community = {
        "terrainContextId": "LH-TERRAIN-COMMUNITY-2018",
        "geographyId": "LH-COMMUNITY-LADERA-RANCH",
        "geographyType": "current_census_cdp",
        **summarize_mask(community_mask, elevation_m, slope, sectors, pixel_area),
        "demNominalYear": 2018,
        "analysisCrs": str(crs),
        "horizontalPixelSizeM": f"{math.sqrt(pixel_area):.3f}",
        "nativeVerticalUnitInterpretation": "inferred_us_survey_foot",
        "verticalConversionToM": f"{US_SURVEY_FOOT_M:.12f}",
        "sourceIds": SOURCE_IDS,
        "statementClass": "documented_approximate",
        "confidence": "medium",
        "limitations": LIMITATIONS,
    }

    rows = []
    summaries = []
    for _, tract in tracts.sort_values("tractNumber").iterrows():
        tract_mask = geometry_mask(
            [mapping(tract.geometry)], out_shape=shape, transform=transform, invert=True
        )
        stats = summarize_mask(tract_mask & community_mask, elevation_m, slope, sectors, pixel_area)
        tract_id = f"LH-TRACT-{tract['tractNumber']}"
        row = {
            "terrainContextId": f"LH-TERRAIN-TRACT-{tract['tractNumber']}-2018",
            "tractId": tract_id,
            "tractNumber": tract["tractNumber"],
            "recordDate": (
                tract["recordDate"].strftime("%Y-%m-%d")
                if hasattr(tract.get("recordDate", ""), "strftime")
                else tract.get("recordDate", "")
            ),
            **stats,
            "demNominalYear": 2018,
            "analysisCrs": str(crs),
            "horizontalPixelSizeM": f"{math.sqrt(pixel_area):.3f}",
            "sourceIds": f"{SOURCE_IDS};LH-SRC-OC-TRACTS",
            "statementClass": "documented_approximate",
            "confidence": "medium",
            "limitations": LIMITATIONS,
        }
        rows.append(row)
        summaries.append(row)
    lookup = {str(row["tractNumber"]): row for row in summaries}
    keep = [
        "minElevationM",
        "medianElevationM",
        "maxElevationM",
        "reliefM",
        "meanSlopeDeg",
        "p90SlopeDeg",
        "dominantAspectSector",
        "terrainContextId",
    ]
    for key in keep:
        tracts[key] = tracts["tractNumber"].astype(str).map(lambda value: lookup[value].get(key, ""))
    tracts = tracts.to_crs(4326)
    tracts["sourceIds"] = f"{SOURCE_IDS};LH-SRC-OC-TRACTS"
    tracts["knownLimitations"] = LIMITATIONS
    return rows, community, tracts


def build_drainage() -> tuple[list[dict[str, object]], gpd.GeoDataFrame, gpd.GeoDataFrame]:
    boundary = valid_geometry(gpd.read_file(BOUNDARY).to_crs(26946))
    boundary_geometry = boundary.geometry.union_all()
    sources = [
        (
            "watershed_boundary",
            EVIDENCE / "watersheds.geojson",
            "LH-SRC-OC-WATERSHEDS",
        ),
        (
            "lidar_derived_stream_centerline",
            EVIDENCE / "south_oc_stream_centerlines.geojson",
            "LH-SRC-OC-STREAMS-2016",
        ),
        (
            "flood_control_infrastructure",
            EVIDENCE / "flood_channels.geojson",
            "LH-SRC-OC-FLOOD-CHANNELS",
        ),
    ]
    output_rows = []
    line_frames = []
    watershed_frame = gpd.GeoDataFrame()
    for context_type, path, source_id in sources:
        frame = valid_geometry(gpd.read_file(path).to_crs(26946))
        frame["geometry"] = frame.geometry.intersection(boundary_geometry)
        frame = frame[~frame.geometry.is_empty].copy()
        if context_type == "watershed_boundary":
            watershed_frame = frame
            names = ";".join(sorted(set(frame["Watershed"].dropna().astype(str))))
            measure = float(frame.geometry.area.sum())
            measure_name = "clippedAreaSqM"
        else:
            names_field = "REACH_ID" if context_type == "lidar_derived_stream_centerline" else "FACILITYNAME"
            names = ";".join(sorted(set(frame[names_field].dropna().astype(str))))
            measure = float(frame.geometry.length.sum())
            measure_name = "clippedLengthM"
            frame["contextType"] = context_type
            frame["sourceId"] = source_id
            frame["statementClass"] = "documented_approximate"
            frame["knownLimitations"] = (
                "Current or post-study drainage context; geometry does not establish historical "
                "flow, completion date, or movement between locations."
            )
            line_frames.append(frame)
        row = {
            "drainageContextId": f"LH-DRAINAGE-{context_type.upper().replace('_', '-')}",
            "contextType": context_type,
            "featureCount": len(frame),
            "featureNames": names,
            "clippedAreaSqM": "",
            "clippedLengthM": "",
            "drawingYearValues": "",
            "asBuiltYearValues": "",
            "sourceIds": f"{source_id};LH-SRC-CENSUS-CDP",
            "statementClass": "documented_approximate",
            "confidence": "high",
            "limitations": (
                "Current or post-study drainage context; not parcel-scale historical flow routing "
                "and not evidence of material movement between locations."
            ),
        }
        row[measure_name] = f"{measure:.1f}"
        if context_type == "flood_control_infrastructure":
            drawing_years = frame["Dwg_Year"].dropna().astype(str).str.strip()
            as_built_years = frame["As_Blt_Year"].dropna().astype(str).str.strip()
            row["drawingYearValues"] = ";".join(sorted(set(drawing_years[drawing_years != ""])))
            row["asBuiltYearValues"] = ";".join(sorted(set(as_built_years[as_built_years != ""])))
        output_rows.append(row)
    drainage = gpd.GeoDataFrame(
        pd.concat(line_frames, ignore_index=True), crs=line_frames[0].crs
    ).to_crs(4326)
    watershed_frame = watershed_frame.to_crs(4326)
    return output_rows, drainage, watershed_frame


def dataframe_geojson(frame: gpd.GeoDataFrame) -> dict[str, object]:
    normalized = frame.copy()
    for column in normalized.columns:
        if pd.api.types.is_datetime64_any_dtype(normalized[column]):
            normalized[column] = normalized[column].dt.strftime("%Y-%m-%d")
    return json.loads(normalized.to_json(drop_id=True, to_wgs84=True))


def main() -> int:
    tract_rows, community, tract_frame = terrain_rows()
    fields = list(tract_rows[0])
    write_csv("tract_terrain_summary.csv", tract_rows, fields)
    write_csv("terrain_summary.csv", [community], list(community))
    write_json(DATA / "tract_terrain.geojson", dataframe_geojson(tract_frame))

    drainage_rows, drainage_frame, watershed_frame = build_drainage()
    write_csv("drainage_context.csv", drainage_rows, list(drainage_rows[0]))
    write_json(DATA / "drainage_features.geojson", dataframe_geojson(drainage_frame))
    write_json(DATA / "watersheds.geojson", dataframe_geojson(watershed_frame))

    flood = next(row for row in drainage_rows if row["contextType"] == "flood_control_infrastructure")
    streams = next(row for row in drainage_rows if row["contextType"] == "lidar_derived_stream_centerline")
    watershed = next(row for row in drainage_rows if row["contextType"] == "watershed_boundary")
    doc = f"""# Terrain and drainage context

## Scope and result

This Mission 4 layer describes terrain and mapped drainage context; it does not reconstruct a pre-development ground surface or model transport. The County's 2018 DEM was exported at approximately five-meter horizontal spacing and sampled only inside the current Census-designated-place boundary.

The community sample contains **{community['pixelCount']:,} cells**. Elevation ranges from **{community['minElevationM']} to {community['maxElevationM']} m**, with a median of **{community['medianElevationM']} m** and total sampled relief of **{community['reliefM']} m**. Median slope is **{community['medianSlopeDeg']} degrees** and the 90th percentile is **{community['p90SlopeDeg']} degrees**. These are descriptive 2018 morphology statistics.

All **{len(tract_rows)} recorded-tract polygons** receive a terrain summary in `tract_terrain_summary.csv`. Recording geometry remains a legal-map geography; the terrain calculation does not imply that each polygon was physically developed on its recording date.

## Vertical-unit decision

The 2018 ImageServer metadata identifies a State Plane U.S.-foot coordinate system and a countywide band range of -21.087816 to 5688.329102, but its band-value unit element is blank. A companion County DEM item explicitly describes elevation in U.S. feet. The pipeline therefore records `inferred_us_survey_foot`, applies **1200/3937 m per U.S. survey foot**, and assigns medium confidence to converted elevations and slopes. The raw GeoTIFF and all service metadata are preserved so this interpretation is auditable.

## Drainage context

The current CDP intersects the County's **{watershed['featureNames']}** watershed polygon. Inside the boundary, the archived 2016 LiDAR-derived stream layer contributes **{streams['featureCount']} clipped reaches** totaling **{float(streams['clippedLengthM']) / 1000:.2f} km**. The flood-control layer contributes **{flood['featureCount']} clipped facilities** totaling **{float(flood['clippedLengthM']) / 1000:.2f} km**.

Flood-channel attributes contain drawing-year values **{flood['drawingYearValues'] or 'none'}** and as-built-year values **{flood['asBuiltYearValues'] or 'none'}**. Blank as-built values remain blank. Drawing years are document leads only and are not promoted to construction-completion, habitability, or occupancy milestones.

## Boundaries on interpretation

- The 2018 terrain surface postdates the 1997-2010 study window and may reflect grading.
- Stream centerlines derive from 2016 LiDAR and 2015 imagery; they do not establish historical flow persistence.
- Watershed and drainage geometry does not establish parcel-scale direction, discharge, exposure, or movement between sites.
- Aspect is the local downslope bearing from the DEM; `flat` means slope below two degrees.
- Overlapping cardinal-facing percentages intentionally group adjacent eight-way aspect sectors and therefore do not sum to 100 percent.

## Outputs

- `research/development_chronology/terrain_summary.csv`
- `research/development_chronology/tract_terrain_summary.csv`
- `research/development_chronology/drainage_context.csv`
- `data/development/tract_terrain.geojson`
- `data/development/drainage_features.geojson`
- `data/development/watersheds.geojson`
- `research/development_chronology/terrain_source_manifest.csv`
"""
    write_text(DOCS / "TERRAIN_AND_DRAINAGE_CONTEXT.md", doc)
    print(
        f"DONE  terrain: {len(tract_rows)} tract summaries, "
        f"{len(drainage_frame)} drainage features, {len(watershed_frame)} watershed feature"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
