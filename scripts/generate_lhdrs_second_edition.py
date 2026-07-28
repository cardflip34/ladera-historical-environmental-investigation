#!/usr/bin/env python3
"""Generate the preserved LHDRS second-edition atlas from Mission 4 registries."""

from __future__ import annotations

import csv
from datetime import date
from html import escape
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import tempfile

import geopandas as gpd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "research/development_chronology"
REPORTS = ROOT / "reports"
EXPORT = ROOT / "data/exports/atlas_second_edition"
FIGURES = EXPORT / "figures"
DISCLAIMER = (
    "This reconstruction documents historical development chronology and spatial relationships "
    "using available public records and imagery. Construction proximity, wind patterns, terrain, "
    "and drainage context are descriptive historical information. They are not measurements of "
    "individual exposure, contamination, health risk, or disease causation."
)


def rows(name: str) -> list[dict[str, str]]:
    with (BASE / name).open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def split_ids(value: str) -> list[str]:
    return [part.strip() for part in re.split(r"[;,]", value or "") if part.strip()]


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


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def citation_md(value: str) -> str:
    return ", ".join(f"`{source_id}`" for source_id in split_ids(value)) or "No source registered"


def citation_html(value: str) -> str:
    return " ".join(
        f'<a class="cite" href="#source-{escape(source_id)}">{escape(source_id)}</a>'
        for source_id in split_ids(value)
    ) or '<span class="muted">No source registered</span>'


def md_cell(value: object) -> str:
    return str(value or "Unknown").replace("|", "\\|").replace("\n", " ")


def md_table(headers: list[str], values: list[list[object]]) -> str:
    lines = ["| " + " | ".join(headers) + " |", "|" + "|".join("---" for _ in headers) + "|"]
    lines.extend("| " + " | ".join(md_cell(cell) for cell in row) + " |" for row in values)
    return "\n".join(lines)


def html_table(headers: list[str], values: list[list[object]], raw: set[int] | None = None) -> str:
    raw = raw or set()
    head = "".join(f"<th>{escape(header)}</th>" for header in headers)
    body = []
    for row in values:
        body.append(
            "<tr>" + "".join(
                f"<td>{str(cell) if index in raw else escape(str(cell or 'Unknown'))}</td>"
                for index, cell in enumerate(row)
            ) + "</tr>"
        )
    return f'<div class="table-wrap"><table><thead><tr>{head}</tr></thead><tbody>{"".join(body)}</tbody></table></div>'


def annual_figures() -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    boundary = gpd.read_file(ROOT / "data/development/ladera_ranch_cdp.geojson")
    tracts = gpd.read_file(ROOT / "data/development/tract_maps.geojson")
    schools = gpd.read_file(ROOT / "data/development/schools.geojson")
    tracts["recordYear"] = tracts["recordYear"].astype(int)
    schools["openYear"] = schools["openYear"].astype(int)
    bounds = boundary.total_bounds
    for year in range(1997, 2011):
        recorded = tracts[tracts["recordYear"] <= year]
        current = tracts[tracts["recordYear"] == year]
        open_schools = schools[schools["openYear"] <= year]
        figure, axis = plt.subplots(figsize=(7.4, 7.4), constrained_layout=True)
        boundary.plot(ax=axis, color="#f7f8f4", edgecolor="#15211e", linewidth=1.4)
        if not recorded.empty:
            recorded.boundary.plot(ax=axis, color="#377f79", linewidth=0.55, alpha=0.7)
        if not current.empty:
            current.plot(ax=axis, color="#d66b48", edgecolor="#a73f2f", linewidth=1.5, alpha=0.45)
        if not open_schools.empty:
            open_schools.plot(ax=axis, color="#c64239", edgecolor="white", linewidth=0.8, markersize=38, zorder=4)
        axis.set_xlim(bounds[0] - 0.002, bounds[2] + 0.002)
        axis.set_ylim(bounds[1] - 0.002, bounds[3] + 0.002)
        axis.set_aspect("equal")
        axis.set_axis_off()
        axis.set_title(f"{year} | legal map recording and school-opening context", loc="left", fontsize=13, fontweight="bold", color="#15211e")
        axis.text(
            0.02, 0.02,
            "Teal: recorded by year  |  orange: recorded during year  |  red: school open by year\nNot physical construction or occupancy geometry",
            transform=axis.transAxes, fontsize=8, color="#33413c",
            bbox={"facecolor": "white", "edgecolor": "#ccd3cf", "alpha": 0.92, "pad": 5},
        )
        figure.savefig(FIGURES / f"annual_context_{year}.png", dpi=170, facecolor="white")
        plt.close(figure)


def chapter_data() -> list[dict[str, object]]:
    snapshots = rows("annual_phase_snapshot_manifest.csv")
    events = rows("events.csv")
    assets = rows("asset_chronology.csv")
    school_timeline = rows("school_timeline.csv")
    wind = {
        int(row["year"]): row
        for row in rows("wind_annual_summary.csv")
        if row["stationContextId"] == "LH-WIND-JOHN-WAYNE"
    }
    imagery = {int(row["year"]): row for row in rows("imagery_coverage_matrix.csv")}
    conflicts = rows("conflict_registry.csv")
    chapters = []
    for snapshot in snapshots:
        year = int(snapshot["year"])
        year_events = [event for event in events if int(event["dateStart"][:4]) == year]
        year_assets = [asset for asset in assets if int(asset["earliestDate"][:4]) == year]
        year_schools = [item for item in school_timeline if int(item["earliestDate"][:4]) == year]
        year_conflicts = [
            conflict for conflict in conflicts
            if any(event_id in conflict["positionAEvidenceIds"] + conflict["positionBEvidenceIds"] for event_id in split_ids(snapshot["milestoneEventIds"]))
        ]
        chapters.append(
            {
                "year": year,
                "snapshot": snapshot,
                "events": year_events,
                "assets": year_assets,
                "schoolTimeline": year_schools,
                "wind": wind.get(year),
                "imagery": imagery[year],
                "conflicts": year_conflicts,
            }
        )
    return chapters


def build_markdown(chapters: list[dict[str, object]]) -> str:
    sources = rows("sources.csv")
    conflicts = rows("conflict_registry.csv")
    gaps = rows("research_gaps.csv")
    phases = rows("phase_snapshot_manifest.csv")
    terrain = rows("terrain_summary.csv")[0]
    parts = [
        "# Ladera Ranch Historical Development Atlas: Second Edition",
        "",
        f"Generated {date.today().isoformat()} from the Mission 4 structured reconstruction.",
        "",
        f"> **Required safeguard:** {DISCLAIMER}",
        "",
        "## Edition result",
        "",
        md_table(
            ["Sources", "Observations", "Claims", "Tracts", "Annual chapters", "Phase snapshots", "Graph edges", "Proximity results"],
            [[len(sources), len(rows("historical_observations.csv")), len(rows("claim_registry.csv")), len(rows("tract_development_matrix.csv")), len(chapters), len(phases), len(rows("knowledge_graph.csv")), 0]],
        ),
        "",
        "The first edition remains at `reports/LHDRS_Historical_Development_Atlas.html` and `.md`. This edition adds legal-map audit, imagery coverage, DSA school projects, regional NOAA wind summaries, County terrain/drainage context, evidence convergence, conflicts, gaps, graph queries, and an Evidence Inspector.",
        "",
        "Historical construction proximity remains blocked. Neither dated occupied/habitable geometry nor dated active-construction geometry passes the publication gate.",
        "",
        "## Phase snapshots",
        "",
        md_table(
            ["Phase", "Years", "Documented context", "Construction geometry", "Occupied geometry", "Confidence"],
            [[row["phaseName"], f"{row['validFromYear']}-{row['validToYear']}", row["summary"], row["activeConstructionGeometryStatus"], row["occupiedGeometryStatus"], row["confidence"]] for row in phases],
        ),
        "",
        "## Annual chapters",
        "",
    ]
    for chapter in chapters:
        year = chapter["year"]
        snapshot = chapter["snapshot"]
        events = chapter["events"]
        wind = chapter["wind"]
        imagery = chapter["imagery"]
        assets = chapter["assets"]
        school_timeline = chapter["schoolTimeline"]
        conflicts_for_year = chapter["conflicts"]
        assert isinstance(snapshot, dict) and isinstance(imagery, dict)
        parts.extend(
            [
                f"### {year}: {str(snapshot['communityStatus']).replace('_', ' ').title()}",
                "",
                f"**Historical context.** {snapshot['documentedMilestones']}",
                "",
                f"![{year} legal-map and school context](../data/exports/atlas_second_edition/figures/annual_context_{year}.png)",
                "",
                f"**Development-status map.** Derived counts show {snapshot['tractMapsRecordedByYear']} legal tract maps recorded during the year and {snapshot['tractMapsRecordedCumulative']} cumulatively. These are not physical-development states.",
                "",
                "**Construction map.** No supported active-construction geometry. The empty layer means unsupported, not no activity.",
                "",
                "**Habitability and occupancy map.** No supported residential geometry. Community sales or first-resident milestones are not assigned to a tract or neighborhood.",
                "",
                f"**Schools and attendance.** Open school IDs: {snapshot['openSchoolIds'] or 'none'}. Historical attendance boundaries were not retrieved; proximity is not substituted for assignment.",
                "",
                f"**Roads and infrastructure.** {', '.join(asset['assetName'] for asset in assets if asset['assetClass'] == 'utilities') or 'No new dated road or infrastructure completion record.'}",
                "",
                f"**Parks, facilities, and commercial.** {', '.join(asset['assetName'] for asset in assets if asset['assetClass'] in {'park', 'clubhouse', 'library', 'commercial'}) or 'No new dated opening milestone.'}",
                "",
                f"**Historical imagery.** {imagery['coverageStatus'].replace('_', ' ')}; available IDs: {imagery['availableImageryIds'] or 'none'}. {imagery['limitations']}",
                "",
                "**Construction proximity.** Blocked because no temporally overlapping subject and target geometry satisfies the evidence threshold; zero comparisons were calculated.",
                "",
                (f"**General wind context.** John Wayne Airport mean observed speed {wind['meanSpeedMS']} m/s; easterly {wind['easterlyPct']}%; westerly {wind['westerlyPct']}%; valid-speed coverage {wind['validSpeedCoveragePct']}%. Regional station observations are not downscaled." if wind else "**General wind context.** No annual selected-station summary."),
                "",
                f"**Terrain context.** The 2018 County DEM sample has a community median elevation of {terrain['medianElevationM']} m and median slope of {terrain['medianSlopeDeg']} degrees. This post-study surface is not assigned as the historical terrain state for {year}.",
                "",
                f"**Confidence.** {snapshot['confidence']}. {snapshot['limitations']}",
                "",
            ]
        )
        if events:
            parts.extend(
                [
                    "**Evidence table.**",
                    "",
                    md_table(
                        ["Date", "Milestone", "Statement class", "Confidence", "Sources", "Limitations"],
                        [[event["dateStart"], event["title"], event["statementClass"], event["confidence"], citation_md(event["sourceIds"]), event["notes"]] for event in events],
                    ),
                    "",
                ]
            )
        else:
            parts.extend(["**Evidence table.** No new dated community event is registered for this year.", ""])
        parts.extend(
            [
                f"**School project evidence.** {len(school_timeline)} DSA/opening milestones occur in this year; administrative dates are not exact physical construction dates.",
                "",
                f"**Conflicting evidence.** {', '.join(conflict['conflictId'] for conflict in conflicts_for_year) or 'No year-linked conflict in the registry.'}",
                "",
                "**Remaining gaps.** Construction geometry; habitability geometry; occupancy geometry; historical attendance boundary; historical facility footprints.",
                "",
                f"**Sources.** {citation_md(str(snapshot['sourceIds']))}",
                "",
            ]
        )
    parts.extend(
        [
            "## Wind and terrain figures",
            "",
            "![Observed annual regional wind context](assets/lhdrs_context/wind_annual_context.png)",
            "",
            "![2018 elevation context](assets/lhdrs_context/terrain_elevation.png)",
            "",
            "See `reports/LHDRS_Wind_and_Terrain_Context.html` for elevation, hillshade, slope, aspect, watershed, and drainage maps.",
            "",
            "## Conflict registry",
            "",
            md_table(["ID", "Subject", "Conflict", "Resolution", "Status"], [[row["conflictId"], row["subjectId"], row["conflictType"], row["resolution"], row["reviewStatus"]] for row in conflicts]),
            "",
            "## Research gaps",
            "",
            md_table(["Priority", "Topic", "Scope", "Evidence needed", "Access status", "Follow-up"], [[row["priority"], row["topic"], row["scope"], row["evidenceNeeded"], row["searchOrAccessStatus"], row["recommendedFollowUp"]] for row in gaps]),
            "",
            "## Source registry",
            "",
        ]
    )
    for source in sources:
        parts.extend(
            [
                f"### {source['id']}: {source['title']}",
                "",
                f"- Publisher: {source['publisher'] or 'Not stated'}",
                f"- URL: {source['url']}",
                f"- Reliability: {source['reliabilityGrade']}",
                f"- Archive: `{source['localFilePath'] or 'not archived'}` ({source['archiveStatus']})",
                f"- SHA-256: `{source['checksumSha256'] or 'unavailable'}`",
                f"- Limitations: {source['knownLimitations']}",
                "",
            ]
        )
    return "\n".join(parts).rstrip() + "\n"


def build_html(chapters: list[dict[str, object]]) -> str:
    sources = rows("sources.csv")
    gaps = rows("research_gaps.csv")
    conflicts = rows("conflict_registry.csv")
    terrain = rows("terrain_summary.csv")[0]
    annual_html = []
    for chapter in chapters:
        year = int(chapter["year"])
        snapshot = chapter["snapshot"]
        events = chapter["events"]
        imagery = chapter["imagery"]
        wind = chapter["wind"]
        assets = chapter["assets"]
        conflicts_for_year = chapter["conflicts"]
        assert isinstance(snapshot, dict) and isinstance(imagery, dict)
        event_table = html_table(
            ["Date", "Milestone", "Class", "Confidence", "Sources", "Limits"],
            [[event["dateStart"], event["title"], event["statementClass"], event["confidence"], citation_html(event["sourceIds"]), event["notes"]] for event in events],
            {4},
        ) if events else '<p class="empty">No new dated community event is registered for this year.</p>'
        wind_text = (
            f"John Wayne Airport: {wind['meanSpeedMS']} m/s mean speed; {wind['easterlyPct']}% easterly; {wind['westerlyPct']}% westerly; {wind['validSpeedCoveragePct']}% valid-speed coverage."
            if wind else "No annual selected-station summary."
        )
        asset_text = "; ".join(asset["assetName"] for asset in assets) or "No new dated facility or infrastructure milestone."
        annual_html.append(f"""
<section class="chapter" id="year-{year}"><div class="chapter-year">{year}</div><div class="chapter-body">
<p class="status">{escape(str(snapshot['communityStatus']).replace('_', ' '))}</p><h2>{escape(str(snapshot['documentedMilestones']))}</h2>
<img class="annual-map" src="../data/exports/atlas_second_edition/figures/annual_context_{year}.png" alt="{year} legal tract recording and school opening context">
<div class="chapter-grid">
<article><h3>Development status</h3><p><b>Derived:</b> {snapshot['tractMapsRecordedByYear']} legal tract maps recorded this year; {snapshot['tractMapsRecordedCumulative']} cumulatively. Not a physical lifecycle state.</p></article>
<article class="blocked"><h3>Construction</h3><p>No supported active-construction geometry. Empty means unsupported, not absent.</p></article>
<article class="blocked"><h3>Habitability and occupancy</h3><p>No supported residential geometry. Community milestones are not assigned to tracts or villages.</p></article>
<article><h3>Schools and attendance</h3><p>Open IDs: {escape(str(snapshot['openSchoolIds']) or 'none')}. Historical attendance boundaries were not retrieved.</p></article>
<article><h3>Roads, facilities, commercial</h3><p>{escape(asset_text)}</p></article>
<article><h3>Historical imagery</h3><p>{escape(str(imagery['coverageStatus']).replace('_', ' '))}. {escape(str(imagery['limitations']))}</p></article>
<article class="blocked"><h3>Construction proximity</h3><p>Blocked. Zero comparisons calculated because subject and target geometry gates are unsatisfied.</p></article>
<article><h3>Wind context</h3><p>{escape(wind_text)} Regional station context; not downscaled.</p></article>
<article><h3>Terrain context</h3><p>2018 median elevation {terrain['medianElevationM']} m; median slope {terrain['medianSlopeDeg']} degrees. Post-study context, not a {year} surface.</p></article>
<article><h3>Confidence</h3><p><b>{escape(str(snapshot['confidence']))}.</b> {escape(str(snapshot['limitations']))}</p></article>
<article><h3>Conflicts</h3><p>{escape(', '.join(conflict['conflictId'] for conflict in conflicts_for_year) or 'No year-linked conflict in the registry.')}</p></article>
<article><h3>Remaining gaps</h3><p>Construction, habitability, and occupancy geometry; attendance boundaries; historical facility footprints.</p></article>
</div><h3>Evidence table</h3>{event_table}<p>{citation_html(str(snapshot['sourceIds']))}</p></div></section>""")
    source_html = "".join(
        f'<article class="source" id="source-{escape(source["id"])}"><p class="source-id">{escape(source["id"])} | {escape(source["reliabilityGrade"])}</p><h3>{escape(source["title"])}</h3><p>{escape(source["publisher"] or "Publisher not stated")}</p><p><a href="{escape(source["url"])}">Official/public source</a></p><dl><dt>Archive</dt><dd>{escape(source["localFilePath"] or "Not archived")} ({escape(source["archiveStatus"])})</dd><dt>SHA-256</dt><dd class="checksum">{escape(source["checksumSha256"] or "Unavailable")}</dd><dt>Limits</dt><dd>{escape(source["knownLimitations"])}</dd></dl></article>'
        for source in sources
    )
    conflict_table = html_table(["ID", "Subject", "Conflict", "Resolution", "Status"], [[row["conflictId"], row["subjectId"], row["conflictType"], row["resolution"], row["reviewStatus"]] for row in conflicts])
    gap_table = html_table(["Priority", "Topic", "Scope", "Evidence needed", "Access", "Follow-up"], [[row["priority"], row["topic"], row["scope"], row["evidenceNeeded"], row["searchOrAccessStatus"], row["recommendedFollowUp"]] for row in gaps])
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Ladera Ranch Historical Development Atlas | Second Edition</title><style>
:root{{--ink:#17211e;--muted:#59635f;--paper:#f8f9f6;--surface:#fff;--line:#cbd2ce;--teal:#28796f;--red:#b64332;--blue:#315e85;--gold:#a36a19}}
*{{box-sizing:border-box}}html{{scroll-behavior:smooth}}body{{margin:0;background:var(--paper);color:var(--ink);font:16px/1.55 system-ui,sans-serif;letter-spacing:0}}
main{{max-width:1120px;margin:auto;padding:54px 28px 84px}}h1,h2{{font-family:Georgia,serif;letter-spacing:0}}h1{{font-size:50px;line-height:1.06;max-width:19ch;margin:.2rem 0 1rem}}h2{{font-size:29px}}h3{{font-size:15px;margin:.1rem 0 .5rem}}a{{color:var(--blue)}}
.eyebrow,.status,.source-id{{text-transform:uppercase;font-size:12px;font-weight:750;color:var(--red)}}.lede{{font:21px/1.5 Georgia,serif;max-width:76ch}}.scope{{border-left:5px solid var(--red);background:#fff;padding:18px 22px;margin:28px 0}}
.summary{{display:grid;grid-template-columns:repeat(5,1fr);gap:1px;background:var(--line);border:1px solid var(--line);margin:30px 0}}.summary div{{background:#fff;padding:15px}}.summary b{{display:block;font-size:26px;color:var(--teal)}}
.context-grid{{display:grid;grid-template-columns:1fr 1fr;gap:18px;margin:24px 0}}.context-grid img{{width:100%;border:1px solid var(--line)}}
.chapter{{display:grid;grid-template-columns:125px minmax(0,1fr);gap:24px;border-top:1px solid var(--line);padding:44px 0}}.chapter-year{{font:52px/1 Georgia,serif;color:var(--red);position:sticky;top:16px;height:max-content}}.chapter-body>h2{{margin:.15rem 0 1rem}}.annual-map{{display:block;width:100%;max-height:690px;object-fit:contain;background:#fff;border:1px solid var(--line)}}
.chapter-grid{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:0;border-top:1px solid var(--line);border-left:1px solid var(--line);margin:20px 0}}.chapter-grid article{{padding:14px;border-right:1px solid var(--line);border-bottom:1px solid var(--line);background:#fff}}.chapter-grid article.blocked{{background:#fff7e9;border-left:4px solid var(--gold)}}.chapter-grid p{{font-size:13px;margin:0;color:var(--muted)}}
.cite{{display:inline-block;background:#e7efec;color:#184f4a;padding:2px 6px;margin:2px;border-radius:3px;font:700 10px system-ui;text-decoration:none}}.table-wrap{{overflow:auto;margin:14px 0 28px}}table{{width:100%;border-collapse:collapse;background:#fff;font-size:12px}}th,td{{padding:8px;text-align:left;vertical-align:top;border:1px solid var(--line)}}th{{background:#233a33;color:#fff}}.source{{background:#fff;border-top:3px solid var(--teal);padding:17px;margin:14px 0;break-inside:avoid}}dl{{display:grid;grid-template-columns:90px 1fr;gap:4px 10px}}dd{{margin:0;overflow-wrap:anywhere}}.checksum{{font:10px monospace}}.muted,.empty{{color:var(--muted)}}
@media(max-width:760px){{main{{padding:32px 17px}}h1{{font-size:37px}}.summary{{grid-template-columns:1fr 1fr}}.context-grid,.chapter-grid{{grid-template-columns:1fr}}.chapter{{grid-template-columns:1fr}}.chapter-year{{position:static;font-size:38px}}}}
@media print{{body{{background:#fff;font-size:9pt}}main{{max-width:none;padding:0}}.chapter{{break-before:page}}.chapter-year{{position:static}}.chapter-grid article{{break-inside:avoid}}a{{color:inherit;text-decoration:none}}@page{{size:letter;margin:.55in}}}}
</style></head><body><main><header><p class="eyebrow">LHDRS Evidence Publication | Second Edition</p><h1>Ladera Ranch Historical Development Atlas</h1><p class="lede">A source-traceable 1997-2010 reconstruction that distinguishes documented milestones from unavailable physical-development geometry.</p><p>Generated {date.today().isoformat()}.</p></header>
<aside class="scope"><strong>Required safeguard.</strong> {escape(DISCLAIMER)}</aside>
<div class="summary"><div><b>{len(sources)}</b>sources</div><div><b>{len(rows('historical_observations.csv'))}</b>observations</div><div><b>{len(rows('claim_registry.csv'))}</b>claims</div><div><b>123</b>tracts</div><div><b>0</b>proximity results</div></div>
<section><p class="eyebrow">Edition result</p><h2>More evidence, firmer boundaries</h2><p>The legal-map, school, imagery, wind, terrain, graph, conflict, and gap layers are materially expanded. The first edition remains preserved. No active-construction, habitability, or occupancy polygon passed the evidence gate, so spatial proximity remains blocked.</p><div class="context-grid"><img src="assets/lhdrs_context/wind_annual_context.png" alt="Observed regional wind context"><img src="assets/lhdrs_context/terrain_elevation.png" alt="2018 elevation context"></div></section>
<section><p class="eyebrow">Annual reconstruction</p><h2>Fourteen evidence manifests, 1997-2010</h2>{''.join(annual_html)}</section>
<section><p class="eyebrow">Conflict registry</p><h2>Both sides remain visible</h2>{conflict_table}</section>
<section><p class="eyebrow">Gap review</p><h2>What would change the reconstruction</h2>{gap_table}</section>
<section><p class="eyebrow">Bibliography</p><h2>Source registry and archives</h2>{source_html}</section>
</main></body></html>\n"""


def export_tables() -> None:
    table_dir = EXPORT / "tables"
    table_dir.mkdir(parents=True, exist_ok=True)
    for name in [
        "annual_phase_snapshot_manifest.csv", "phase_snapshot_manifest.csv", "tract_development_matrix.csv",
        "tract_milestone_evidence.csv", "construction_activity_registry.csv", "occupancy_event_registry.csv",
        "neighborhood_occupancy_matrix.csv", "school_timeline.csv", "asset_chronology.csv",
        "construction_proximity_results.csv", "source_convergence.csv", "conflict_registry.csv", "research_gaps.csv",
    ]:
        shutil.copy2(BASE / name, table_dir / name)


def main() -> int:
    annual_figures()
    export_tables()
    chapters = chapter_data()
    markdown = build_markdown(chapters)
    html_report = build_html(chapters)
    markdown_path = REPORTS / "LHDRS_Historical_Development_Atlas_Second_Edition.md"
    html_path = REPORTS / "LHDRS_Historical_Development_Atlas_Second_Edition.html"
    write_text(markdown_path, markdown)
    write_text(html_path, html_report)
    manifest_files = sorted(
        path for path in EXPORT.rglob("*")
        if path.is_file() and path.name != "publication_manifest.json"
    )
    write_json(
        EXPORT / "publication_manifest.json",
        {
            "edition": "second",
            "generatedDate": date.today().isoformat(),
            "annualChapterCount": len(chapters),
            "firstEditionPreserved": True,
            "proximityStatus": "blocked",
            "proximityResultCount": 0,
            "files": [
                {"path": str(path.relative_to(ROOT)), "bytes": path.stat().st_size, "sha256": sha256(path)}
                for path in manifest_files
            ],
            "reports": [str(markdown_path.relative_to(ROOT)), str(html_path.relative_to(ROOT))],
        },
    )
    print(f"DONE  second edition: {len(chapters)} annual chapters, {len(manifest_files)} exported files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
