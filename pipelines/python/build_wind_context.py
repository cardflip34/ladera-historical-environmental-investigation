#!/usr/bin/env python3
"""Build regional wind context from archived NOAA Global Hourly observations."""

from __future__ import annotations

import calendar
import csv
import datetime as dt
import math
import os
from pathlib import Path
import statistics
import tempfile


ROOT = Path(__file__).resolve().parents[2]
RESEARCH = ROOT / "research/development_chronology"
HISTORY = ROOT / "evidence/lhdrs/noaa/isd-history.csv"
MANIFEST = RESEARCH / "wind_source_manifest.csv"
SITE_LAT = 33.55
SITE_LON = -117.64
START = "19970101"
END = "20101231"
SELECTED = {
    "69014093101": ("LH-WIND-EL-TORO", "closer_partial_context"),
    "99999993101": ("LH-WIND-EL-TORO", "closer_partial_context"),
    "72297793184": ("LH-WIND-JOHN-WAYNE", "continuous_regional_context"),
    "72297799999": ("LH-WIND-JOHN-WAYNE", "continuous_regional_context_alternate_file_id"),
}
JOHN_WAYNE_BY_YEAR = {
    **{year: "72297793184" for year in range(1997, 2000)},
    **{year: "72297799999" for year in range(2000, 2004)},
    **{year: "72297793184" for year in range(2004, 2011)},
}
SUMMARY_FILES = {
    *((year, station) for year, station in JOHN_WAYNE_BY_YEAR.items()),
    (1997, "69014093101"),
    (1999, "99999993101"),
    (2000, "99999993101"),
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as stream:
        return list(csv.DictReader(stream))


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


def write_text(path: Path, value: str) -> None:
    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", dir=path.parent, delete=False
    ) as stream:
        stream.write(value)
        temp_path = Path(stream.name)
    os.replace(temp_path, path)


def distance_km(lat: float, lon: float) -> float:
    dlat = math.radians(lat - SITE_LAT)
    dlon = math.radians(lon - SITE_LON)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(SITE_LAT))
        * math.cos(math.radians(lat))
        * math.sin(dlon / 2) ** 2
    )
    return 6371.0 * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def build_station_inventory() -> list[dict[str, object]]:
    rows = []
    for item in read_csv(HISTORY):
        try:
            lat = float(item["LAT"])
            lon = float(item["LON"])
        except ValueError:
            continue
        distance = distance_km(lat, lon)
        if distance > 70 or item["END"] < START or item["BEGIN"] > END:
            continue
        station_file_id = item["USAF"] + item["WBAN"]
        selected = station_file_id in SELECTED
        context_id, use = SELECTED.get(station_file_id, ("", "candidate_not_selected"))
        if selected:
            reason = (
                "Closest archived airport context; discontinuous study-period record"
                if context_id == "LH-WIND-EL-TORO"
                else "Nearest selected station with continuous 1997-2010 Global Hourly files"
            )
        else:
            reason = "Not selected because a nearer or more continuous airport context was available"
        rows.append(
            {
                "stationContextId": context_id,
                "stationFileId": station_file_id,
                "usaf": item["USAF"],
                "wban": item["WBAN"],
                "stationName": item["STATION NAME"],
                "latitude": item["LAT"],
                "longitude": item["LON"],
                "elevationM": item["ELEV(M)"],
                "distanceKm": f"{distance:.1f}",
                "recordBegin": item["BEGIN"],
                "recordEnd": item["END"],
                "selected": str(selected).lower(),
                "use": use,
                "selectionReason": reason,
                "sourceIds": "LH-SRC-NOAA-ISD-HISTORY",
                "confidence": "high",
                "limitations": (
                    "Distance and period of record do not establish site representativeness; "
                    "terrain, elevation, station moves, and instrumentation may differ."
                ),
            }
        )
    return sorted(rows, key=lambda row: (float(row["distanceKm"]), row["stationFileId"]))


def parse_wind(value: str) -> tuple[float | None, int | None]:
    parts = value.split(",")
    if len(parts) != 5:
        return None, None
    direction_text, direction_quality, _, speed_text, speed_quality = parts
    if speed_text == "9999" or speed_quality in {"2", "3", "6", "7"}:
        speed = None
    else:
        speed = int(speed_text) / 10.0
    if direction_text == "999" or direction_quality in {"2", "3", "6", "7"}:
        direction = None
    else:
        direction = int(direction_text)
    return speed, direction


def hourly_records(path: Path) -> tuple[int, list[dict[str, object]]]:
    raw = read_csv(path)
    by_hour: dict[str, dict[str, str]] = {}
    for item in raw:
        timestamp = dt.datetime.fromisoformat(item["DATE"])
        key = timestamp.strftime("%Y-%m-%dT%H")
        report_rank = 0 if item["REPORT_TYPE"].strip() in {"FM-12", "FM-15"} else 1
        rank = (report_rank, abs(timestamp.minute), item["DATE"])
        current = by_hour.get(key)
        if current is None or rank < current["_rank"]:
            by_hour[key] = {**item, "_rank": rank}
    output = []
    for key, item in sorted(by_hour.items()):
        speed, direction = parse_wind(item["WND"])
        output.append(
            {
                "hour": key,
                "month": int(key[5:7]),
                "speed": speed,
                "direction": direction,
            }
        )
    return len(raw), output


def percentile(values: list[float], fraction: float) -> float:
    if not values:
        return math.nan
    ordered = sorted(values)
    index = (len(ordered) - 1) * fraction
    lower = math.floor(index)
    upper = math.ceil(index)
    if lower == upper:
        return ordered[lower]
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (index - lower)


def summarize(
    station_id: str, station_file_id: str, year: int, month: int | None,
    raw_count: int, records: list[dict[str, object]],
) -> dict[str, object]:
    speeds = [float(row["speed"]) for row in records if row["speed"] is not None]
    directional = [
        int(row["direction"])
        for row in records
        if row["direction"] is not None and row["speed"] is not None and float(row["speed"]) > 0
    ]
    sectors = {
        "northerly": sum(value >= 315 or value < 45 for value in directional),
        "easterly": sum(45 <= value < 135 for value in directional),
        "southerly": sum(135 <= value < 225 for value in directional),
        "westerly": sum(225 <= value < 315 for value in directional),
    }
    denominator = len(directional) or 1
    expected = (
        calendar.monthrange(year, month)[1] * 24
        if month is not None
        else (366 if calendar.isleap(year) else 365) * 24
    )
    return {
        "stationContextId": station_id,
        "stationFileId": station_file_id,
        "year": year,
        "month": month or "",
        "rawReportCount": raw_count,
        "deduplicatedHourCount": len(records),
        "expectedCalendarHours": expected,
        "validSpeedHourCount": len(speeds),
        "validDirectionalHourCount": len(directional),
        "validSpeedCoveragePct": f"{len(speeds) / expected * 100:.2f}",
        "meanSpeedMS": f"{statistics.fmean(speeds):.3f}" if speeds else "",
        "medianSpeedMS": f"{statistics.median(speeds):.3f}" if speeds else "",
        "p90SpeedMS": f"{percentile(speeds, 0.9):.3f}" if speeds else "",
        "maxSustainedSpeedMS": f"{max(speeds):.3f}" if speeds else "",
        "calmHourPct": f"{sum(value == 0 for value in speeds) / len(speeds) * 100:.2f}" if speeds else "",
        "strongWindHourCountGe10MS": sum(value >= 10 for value in speeds),
        "northerlyPct": f"{sectors['northerly'] / denominator * 100:.2f}",
        "easterlyPct": f"{sectors['easterly'] / denominator * 100:.2f}",
        "southerlyPct": f"{sectors['southerly'] / denominator * 100:.2f}",
        "westerlyPct": f"{sectors['westerly'] / denominator * 100:.2f}",
        "prevailingSector": max(sectors, key=sectors.get) if directional else "",
        "timeBasis": "UTC",
        "sourceIds": "LH-SRC-NOAA-GLOBAL-HOURLY;LH-SRC-NOAA-ISD-HISTORY",
        "statementClass": "documented_approximate",
        "confidence": "medium",
        "limitations": (
            "Regional station observation; not downscaled to Ladera Ranch and not a model of "
            "air movement between locations."
        ),
    }


def build_summaries() -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    annual = []
    monthly = []
    for item in read_csv(MANIFEST):
        if item["sourceId"] != "LH-SRC-NOAA-GLOBAL-HOURLY" or item["archiveStatus"] == "fetch_failed":
            continue
        path = ROOT / item["localFilePath"]
        year = int(path.parent.name)
        station_file_id = path.stem
        if (year, station_file_id) not in SUMMARY_FILES:
            continue
        station_id = SELECTED[station_file_id][0]
        raw_count, records = hourly_records(path)
        annual.append(summarize(station_id, station_file_id, year, None, raw_count, records))
        for month in range(1, 13):
            subset = [row for row in records if row["month"] == month]
            monthly.append(summarize(station_id, station_file_id, year, month, len(subset), subset))
    annual.sort(key=lambda row: (row["stationContextId"], row["year"]))
    monthly.sort(key=lambda row: (row["stationContextId"], row["year"], row["month"]))
    return annual, monthly


def comparison_rows(annual: list[dict[str, object]]) -> list[dict[str, object]]:
    indexed = {(row["stationContextId"], row["year"]): row for row in annual}
    rows = []
    for year in range(1997, 2011):
        el_toro = indexed.get(("LH-WIND-EL-TORO", year))
        john_wayne = indexed.get(("LH-WIND-JOHN-WAYNE", year))
        if not el_toro or not john_wayne:
            continue
        if not el_toro["meanSpeedMS"] or not john_wayne["meanSpeedMS"]:
            continue
        rows.append(
            {
                "year": year,
                "elToroValidSpeedHours": el_toro["validSpeedHourCount"],
                "johnWayneValidSpeedHours": john_wayne["validSpeedHourCount"],
                "elToroMeanSpeedMS": el_toro["meanSpeedMS"],
                "johnWayneMeanSpeedMS": john_wayne["meanSpeedMS"],
                "meanSpeedDifferenceMS": f"{float(el_toro['meanSpeedMS']) - float(john_wayne['meanSpeedMS']):.3f}",
                "elToroEasterlyPct": el_toro["easterlyPct"],
                "johnWayneEasterlyPct": john_wayne["easterlyPct"],
                "sourceIds": "LH-SRC-NOAA-GLOBAL-HOURLY",
                "interpretation": "regional_station_comparison_only",
                "limitations": "Station differences do not quantify conditions at Ladera Ranch.",
            }
        )
    return rows


def main() -> int:
    inventory = build_station_inventory()
    annual, monthly = build_summaries()
    comparisons = comparison_rows(annual)
    write_csv("wind_station_inventory.csv", inventory, list(inventory[0]))
    write_csv("wind_annual_summary.csv", annual, list(annual[0]))
    write_csv("wind_monthly_summary.csv", monthly, list(monthly[0]))
    write_csv("wind_station_comparison.csv", comparisons, list(comparisons[0]))
    write_text(
        ROOT / "docs/lhdrs/WIND_CONTEXT.md",
        f"""# Regional Wind Context

Generated from archived NOAA Integrated Surface Database station metadata and Global
Hourly files. The study uses El Toro MCAS as the closer partial record and John Wayne
Airport as the continuous 1997-2010 regional record.

| Output | Rows |
|---|---:|
| Candidate station-history records within 70 km | {len(inventory)} |
| Selected annual station summaries | {len(annual)} |
| Selected monthly station summaries | {len(monthly)} |
| Same-year El Toro / John Wayne comparisons | {len(comparisons)} |

## Processing

- One routine report is selected per UTC hour, preferring `FM-12` or `FM-15` and then
  the observation nearest the top of the hour.
- Wind speed uses the NOAA `WND` field in tenths of metres per second after rejecting
  missing values and suspect or erroneous quality codes 2, 3, 6, and 7.
- Direction sectors describe where wind was reported as coming from. Easterly is
  45-134 degrees and westerly is 225-314 degrees.
- Calm means reported sustained speed equals 0.0 m/s. Strong-wind counts use 10 m/s.
- El Toro files are available for 1997, 1999, and 2000 only. The 1999-2000 files contain
  daily/monthly precipitation summaries but no valid `WND` observations, so only 1997
  supports wind statistics. The gap is not interpolated.
- John Wayne observations use file ID `72297793184` in 1997-1999 and 2004-2010 and
  the same station's `72297799999` identity in 2000-2003. Summary-only companion files
  are archived but excluded from wind statistics.

## Interpretation Boundary

Airport observations are regional historical context. Ladera Ranch terrain, elevation,
and local flow can differ. These summaries do not downscale wind, reconstruct parcel-level
conditions, or model movement between places.
""",
    )
    print(f"Wind context: {len(inventory)} candidates, {len(annual)} annual summaries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
