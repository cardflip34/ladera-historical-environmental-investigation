#!/usr/bin/env python3
"""Generate Mission 4 wind/terrain deliverables and bounded visual context."""

from __future__ import annotations

import csv
import html
import json
import os
from pathlib import Path
import shutil
import tempfile

import geopandas as gpd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LightSource
import numpy as np
import rasterio
from rasterio.features import geometry_mask
from shapely.geometry import mapping


ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "research/development_chronology"
RESEARCH_WIND = ROOT / "research/wind"
PROCESSED_WIND = ROOT / "data/processed/wind"
ASSETS = ROOT / "reports/assets/lhdrs_context"
REPORT = ROOT / "reports/LHDRS_Wind_and_Terrain_Context.html"
DEM = ROOT / "evidence/lhdrs/terrain/ladera_dem_2018_5m.tif"
CDP = ROOT / "data/development/ladera_ranch_cdp.geojson"
SCHOOLS = ROOT / "data/development/schools.geojson"
US_SURVEY_FOOT_M = 1200 / 3937
DISCLAIMER = (
    "This reconstruction documents historical development chronology and spatial relationships "
    "using available public records and imagery. Construction proximity, wind patterns, terrain, "
    "and drainage context are descriptive historical information. They are not measurements of "
    "individual exposure, contamination, health risk, or disease causation."
)


def rows(name: str) -> list[dict[str, str]]:
    with (BASE / name).open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


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


def style_axis(axis: plt.Axes, title: str) -> None:
    axis.set_title(title, loc="left", fontsize=13, fontweight="bold", color="#17221f", pad=10)
    axis.set_axis_off()


def save_map(
    values: np.ndarray,
    extent: tuple[float, float, float, float],
    boundary: gpd.GeoDataFrame,
    filename: str,
    title: str,
    cmap: str,
    label: str,
    vmin: float | None = None,
    vmax: float | None = None,
    schools: gpd.GeoDataFrame | None = None,
) -> None:
    figure, axis = plt.subplots(figsize=(8.4, 7.1), constrained_layout=True)
    image = axis.imshow(values, extent=extent, origin="upper", cmap=cmap, vmin=vmin, vmax=vmax)
    boundary.boundary.plot(ax=axis, color="#111816", linewidth=1.35)
    if schools is not None and not schools.empty:
        schools.plot(ax=axis, color="#c84b31", edgecolor="white", linewidth=0.8, markersize=34, zorder=4)
        axis.text(
            0.02, 0.02, "School points show current campus locations",
            transform=axis.transAxes, fontsize=8, color="#17221f",
            bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.85, "pad": 3},
        )
    colorbar = figure.colorbar(image, ax=axis, shrink=0.72, pad=0.02)
    colorbar.set_label(label)
    style_axis(axis, title)
    figure.savefig(ASSETS / filename, dpi=180, facecolor="white")
    plt.close(figure)


def terrain_figures() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    boundary = gpd.read_file(CDP).to_crs(26946)
    school_points = gpd.read_file(SCHOOLS).to_crs(26946)
    with rasterio.open(DEM) as dataset:
        native = dataset.read(1).astype("float64")
        elevation = native * US_SURVEY_FOOT_M
        mask = geometry_mask(
            [mapping(boundary.geometry.union_all())],
            out_shape=elevation.shape,
            transform=dataset.transform,
            invert=True,
        )
        elevation[~mask] = np.nan
        xres, yres = dataset.res
        dz_south, dz_east = np.gradient(elevation, yres, xres)
        slope = np.degrees(np.arctan(np.hypot(dz_east, dz_south)))
        aspect = (np.degrees(np.arctan2(-dz_east, dz_south)) + 360) % 360
        aspect[slope < 2] = np.nan
        extent = (dataset.bounds.left, dataset.bounds.right, dataset.bounds.bottom, dataset.bounds.top)
        filled = np.where(np.isfinite(elevation), elevation, np.nanmedian(elevation))
        hillshade = LightSource(azdeg=315, altdeg=40).hillshade(filled, vert_exag=1.4, dx=xres, dy=yres)
        hillshade[~mask] = np.nan

    save_map(
        elevation, extent, boundary, "terrain_elevation.png", "Elevation | 2018 County DEM",
        "viridis", "meters (inferred U.S.-survey-foot conversion)", schools=school_points,
    )
    save_map(hillshade, extent, boundary, "terrain_hillshade.png", "Hillshade | 2018 terrain context", "gray", "relative illumination")
    save_map(slope, extent, boundary, "terrain_slope.png", "Slope | 2018 terrain context", "magma", "degrees", vmin=0, vmax=35)
    save_map(aspect, extent, boundary, "terrain_aspect.png", "Aspect | downslope bearing", "twilight", "degrees clockwise from north", vmin=0, vmax=360)

    watershed = gpd.read_file(ROOT / "data/development/watersheds.geojson").to_crs(26946)
    drainage = gpd.read_file(ROOT / "data/development/drainage_features.geojson").to_crs(26946)
    figure, axis = plt.subplots(figsize=(8.4, 7.1), constrained_layout=True)
    watershed.plot(ax=axis, color="#dfe8cf", edgecolor="#56734e", linewidth=1.3)
    boundary.boundary.plot(ax=axis, color="#111816", linewidth=1.4)
    style_axis(axis, "Watershed | current County boundary context")
    axis.text(0.02, 0.02, "San Juan Creek watershed", transform=axis.transAxes, fontsize=9, color="#355039")
    figure.savefig(ASSETS / "terrain_watershed.png", dpi=180, facecolor="white")
    plt.close(figure)

    figure, axis = plt.subplots(figsize=(8.4, 7.1), constrained_layout=True)
    watershed.plot(ax=axis, color="#f1f2ec", edgecolor="#a7b09d", linewidth=0.9)
    streams = drainage[drainage["contextType"] == "lidar_derived_stream_centerline"]
    channels = drainage[drainage["contextType"] == "flood_control_infrastructure"]
    streams.plot(ax=axis, color="#2677a7", linewidth=1.5, label="2016 LiDAR-derived stream")
    channels.plot(ax=axis, color="#c45b34", linewidth=1.1, label="County flood-control feature")
    boundary.boundary.plot(ax=axis, color="#111816", linewidth=1.4)
    axis.legend(loc="lower left", frameon=True, fontsize=8)
    style_axis(axis, "Drainage features | current and post-study context")
    figure.savefig(ASSETS / "terrain_drainage.png", dpi=180, facecolor="white")
    plt.close(figure)


def wind_figure() -> None:
    annual = [row for row in rows("wind_annual_summary.csv") if row["stationContextId"] == "LH-WIND-JOHN-WAYNE"]
    years = [int(row["year"]) for row in annual]
    mean_speed = [float(row["meanSpeedMS"]) for row in annual]
    easterly = [float(row["easterlyPct"]) for row in annual]
    westerly = [float(row["westerlyPct"]) for row in annual]
    figure, axes = plt.subplots(2, 1, figsize=(10.5, 6.8), constrained_layout=True, sharex=True)
    axes[0].plot(years, mean_speed, color="#146b64", marker="o", linewidth=2)
    axes[0].set_ylabel("Mean speed (m/s)")
    axes[0].set_title("John Wayne Airport | observed annual wind context", loc="left", fontsize=13, fontweight="bold")
    axes[0].grid(axis="y", alpha=0.25)
    axes[1].plot(years, westerly, color="#2d6da3", marker="o", label="Westerly sector")
    axes[1].plot(years, easterly, color="#c45b34", marker="o", label="Easterly sector")
    axes[1].set_ylabel("Directional reports (%)")
    axes[1].set_xlabel("Year")
    axes[1].set_xticks(years)
    axes[1].tick_params(axis="x", rotation=45)
    axes[1].grid(axis="y", alpha=0.25)
    axes[1].legend(frameon=False, ncol=2)
    figure.savefig(ASSETS / "wind_annual_context.png", dpi=180, facecolor="white")
    plt.close(figure)


def publish_data() -> None:
    RESEARCH_WIND.mkdir(parents=True, exist_ok=True)
    PROCESSED_WIND.mkdir(parents=True, exist_ok=True)
    copies = {
        BASE / "wind_station_inventory.csv": RESEARCH_WIND / "station_inventory.csv",
        BASE / "wind_annual_summary.csv": RESEARCH_WIND / "wind_observations_summary.csv",
        BASE / "wind_monthly_summary.csv": PROCESSED_WIND / "wind_monthly_summary.csv",
        BASE / "wind_annual_summary.csv": PROCESSED_WIND / "wind_annual_summary.csv",
        ROOT / "docs/lhdrs/WIND_CONTEXT.md": RESEARCH_WIND / "wind_climatology.md",
    }
    for source, target in copies.items():
        shutil.copy2(source, target)
    write_json(
        PROCESSED_WIND / "metadata.json",
        {
            "analysisPeriod": "1997-2010",
            "timeBasis": "UTC",
            "selectedStationContexts": ["LH-WIND-EL-TORO", "LH-WIND-JOHN-WAYNE"],
            "regionalOnly": True,
            "downscaled": False,
            "movementModel": False,
            "sourceIds": ["LH-SRC-NOAA-ISD-HISTORY", "LH-SRC-NOAA-GLOBAL-HOURLY"],
        },
    )


def make_report() -> None:
    terrain = rows("terrain_summary.csv")[0]
    drainage = {row["contextType"]: row for row in rows("drainage_context.csv")}
    annual = rows("wind_annual_summary.csv")
    john = [row for row in annual if row["stationContextId"] == "LH-WIND-JOHN-WAYNE"]
    el_toro = [row for row in annual if row["stationContextId"] == "LH-WIND-EL-TORO" and row["validSpeedHourCount"] != "0"]
    html_text = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>LHDRS Wind and Terrain Context</title>
<style>
:root{{--ink:#18211e;--muted:#59635f;--line:#cbd2ce;--paper:#fbfcfa;--accent:#146b64;--warm:#c45b34}}
*{{box-sizing:border-box}} body{{margin:0;background:var(--paper);color:var(--ink);font:16px/1.55 system-ui,sans-serif}}
header,section{{max-width:1080px;margin:auto;padding:36px 28px}} header{{padding-top:62px;border-bottom:1px solid var(--line)}}
h1{{font:700 42px/1.1 Georgia,serif;margin:0 0 14px}} h2{{font:700 26px/1.2 Georgia,serif;margin:0 0 14px}} h3{{margin:0 0 8px}}
.dek{{font-size:19px;color:var(--muted);max-width:820px}} .notice{{border-left:5px solid var(--warm);padding:12px 16px;background:#f8eee9}}
.metrics{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:1px;background:var(--line);border:1px solid var(--line);margin:24px 0}}
.metric{{background:white;padding:18px}} .metric b{{display:block;font-size:24px;color:var(--accent)}}
.grid{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:22px}} figure{{margin:0}} img{{display:block;width:100%;border:1px solid var(--line)}} figcaption{{color:var(--muted);font-size:13px;margin-top:7px}}
table{{width:100%;border-collapse:collapse}} th,td{{text-align:left;padding:10px;border-bottom:1px solid var(--line);vertical-align:top}} th{{font-size:13px;text-transform:uppercase}}
footer{{background:#18211e;color:white;padding:28px}} footer p{{max-width:1024px;margin:auto}}
@media(max-width:720px){{h1{{font-size:34px}}.metrics,.grid{{grid-template-columns:1fr}}header,section{{padding-left:18px;padding-right:18px}}}}
</style></head><body>
<header><p>LHDRS | Mission 4 technical context</p><h1>Wind and terrain context</h1>
<p class="dek">Observed regional airport winds and post-study County topography, presented as descriptive context with explicit temporal and spatial limits.</p></header>
<main><section><h2>Terrain summary</h2><div class="metrics">
<div class="metric"><b>{terrain['minElevationM']}-{terrain['maxElevationM']} m</b>sampled elevation range</div>
<div class="metric"><b>{terrain['medianSlopeDeg']} deg</b>median sampled slope</div>
<div class="metric"><b>{terrain['p90SlopeDeg']} deg</b>90th percentile slope</div>
<div class="metric"><b>{drainage['lidar_derived_stream_centerline']['featureCount']}</b>clipped mapped stream reaches</div></div>
<p class="notice"><strong>Temporal boundary:</strong> The DEM is from 2018, stream centerlines are based on 2016 LiDAR and 2015 imagery, and the watershed layer is current context. These are not reconstructed 1997-2010 surfaces.</p>
<div class="grid">
<figure><img src="assets/lhdrs_context/terrain_elevation.png" alt="Elevation map"><figcaption>Elevation, with current school campus points for orientation.</figcaption></figure>
<figure><img src="assets/lhdrs_context/terrain_hillshade.png" alt="Hillshade map"><figcaption>Relative illumination reveals the form of the 2018 surface.</figcaption></figure>
<figure><img src="assets/lhdrs_context/terrain_slope.png" alt="Slope map"><figcaption>Slope in degrees; values above 35 degrees share the highest display color.</figcaption></figure>
<figure><img src="assets/lhdrs_context/terrain_aspect.png" alt="Aspect map"><figcaption>Downslope bearing; cells below two degrees are omitted.</figcaption></figure>
<figure><img src="assets/lhdrs_context/terrain_watershed.png" alt="Watershed map"><figcaption>The current CDP falls within the San Juan Creek watershed.</figcaption></figure>
<figure><img src="assets/lhdrs_context/terrain_drainage.png" alt="Drainage feature map"><figcaption>Post-study stream and flood-control inventories; drawing dates are not as-built dates.</figcaption></figure>
</div></section>
<section><h2>Observed wind context</h2><p>John Wayne Airport supplies {len(john)} annual summaries for 1997-2010. El Toro supplies {len(el_toro)} year with usable wind observations. Reports are deduplicated to one routine record per UTC hour; invalid NOAA wind values and flagged quality codes are excluded.</p>
<figure><img src="assets/lhdrs_context/wind_annual_context.png" alt="Annual regional wind chart"><figcaption>Annual mean speed and easterly/westerly report frequency at John Wayne Airport. This is regional station context, not a neighborhood wind field.</figcaption></figure>
<table><thead><tr><th>Context</th><th>Use</th><th>Limit</th></tr></thead><tbody>
<tr><td>El Toro MCAS</td><td>Closer partial historical comparison</td><td>Only 1997 has usable archived study-period wind observations.</td></tr>
<tr><td>John Wayne Airport</td><td>Continuous 1997-2010 regional record</td><td>Approximately 25 km away; terrain and elevation differ.</td></tr>
<tr><td>Ladera Ranch</td><td>No on-site study-period station located</td><td>No local interpolation or directional assignment is made.</td></tr>
</tbody></table></section></main>
<footer><p>{html.escape(DISCLAIMER)}</p></footer></body></html>\n"""
    write_text(REPORT, html_text)


def main() -> int:
    terrain_figures()
    wind_figure()
    publish_data()
    make_report()
    print("DONE  context publication: 7 figures, wind deliverables, combined HTML report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
