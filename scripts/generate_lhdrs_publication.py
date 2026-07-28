#!/usr/bin/env python3
"""Generate citable LHDRS Markdown and print-ready HTML from canonical registries."""

from __future__ import annotations

import csv
from datetime import date
from html import escape
from pathlib import Path
import re
from typing import Optional


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "research/development_chronology"
REPORTS = ROOT / "reports"


def read_csv(name: str) -> list[dict[str, str]]:
    with (BASE / name).open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def source_tokens(value: str) -> list[str]:
    return [item.strip() for item in re.split(r"[;,]", value or "") if item.strip()]


def markdown_cell(value: str) -> str:
    return (value or "Unknown").replace("|", "\\|").replace("\n", " ")


def markdown_table(headers: list[str], rows: list[list[str]]) -> str:
    lines = ["| " + " | ".join(headers) + " |", "|" + "|".join(["---"] * len(headers)) + "|"]
    lines.extend("| " + " | ".join(markdown_cell(cell) for cell in row) + " |" for row in rows)
    return "\n".join(lines)


def citation_md(value: str) -> str:
    return ", ".join(f"`{item}`" for item in source_tokens(value)) or "No source registered"


def citation_html(value: str) -> str:
    tokens = source_tokens(value)
    if not tokens:
        return '<span class="citation missing">No source registered</span>'
    return " ".join(
        f'<a class="citation" href="#source-{escape(item)}">{escape(item)}</a>' for item in tokens
    )


def html_table(headers: list[str], rows: list[list[str]], raw_columns: Optional[set[int]] = None) -> str:
    raw_columns = raw_columns or set()
    head = "".join(f"<th>{escape(header)}</th>" for header in headers)
    body = []
    for row in rows:
        cells = "".join(
            f"<td>{cell if index in raw_columns else escape(cell or 'Unknown')}</td>"
            for index, cell in enumerate(row)
        )
        body.append(f"<tr>{cells}</tr>")
    return f'<div class="table-wrap"><table><thead><tr>{head}</tr></thead><tbody>{"".join(body)}</tbody></table></div>'


def build_markdown(data: dict[str, list[dict[str, str]]]) -> str:
    snapshots = data["snapshots"]
    events = data["events"]
    sources = data["sources"]
    planning = data["planning"]
    obligations = data["obligations"]
    schools = data["schools"]
    questions = data["questions"]
    tracts = list(csv.DictReader((ROOT / "data/development/tract_maps.csv").open(encoding="utf-8")))

    parts = [
        "# Ladera Ranch Historical Development Atlas",
        "",
        f"Generated {date.today().isoformat()} from the LHDRS canonical registries.",
        "",
        "> **Scope boundary:** This atlas reconstructs historical planning and development. It does not infer contamination, exposure, health effects, or causation. Tract-map recording is a legal subdivision milestone, not proof of grading, construction, sale, road opening, or occupancy.",
        "",
        "## Evidence at a Glance",
        "",
        markdown_table(
            ["Sources", "Chronology events", "Annual chapters", "Recorded tract polygons", "Schools", "Open questions"],
            [[str(len(sources)), str(len(events)), str(len(snapshots)), str(len(tracts)), str(len(schools)), str(sum(row["status"] != "resolved" for row in questions))]],
        ),
        "",
        "## Method",
        "",
        "The system separates source records, observed events, regulatory obligations, annual summaries, and generated geometry. Exact dates are not expanded into broader claims. Approximate or conflicting statements retain their source wording, confidence, and limitations. Blank neighborhood fields are unresolved rather than estimated.",
        "",
        "Distances from occupied neighborhoods to active construction are not calculated because the required dated polygon layers do not yet exist. The blocked gate is recorded in `proximity_analysis_status.csv`.",
        "",
        "![County Ladera Planned Community development plan](../evidence/lhdrs/figures/ladera_development_plan_1995.jpg)",
        "",
        "## Planned Baseline",
        "",
        markdown_table(
            ["PA", "Land use", "Max dwellings", "Residential net acres", "Gross acres", "Profile", "Source"],
            [[row["planningArea"], row["landUse"], row["maxDwellingUnits"], row["residentialNetAcres"], row["grossAcres"], row["communityProfileRange"], citation_md(row["sourceIds"])] for row in planning],
        ),
        "",
        "## Annual Reconstruction",
        "",
    ]

    for snapshot in snapshots:
        year = int(snapshot["year"])
        year_events = [event for event in events if event["dateStart"].startswith(str(year))]
        parts.extend(
            [
                f"### {year}: {snapshot['communityStatus'].replace('_', ' ').title()}",
                "",
                snapshot["documentedMilestones"],
                "",
                f"- Recorded tract maps: {snapshot['tractMapsRecordedByYear']} that year, {snapshot['tractMapsRecordedCumulative']} cumulative",
                f"- Homes sold as of published milestone: {snapshot['homesSoldAsOf'] or 'not published'}",
                f"- Schools open: {snapshot['activeSchoolCount']}",
                f"- Confidence: {snapshot['confidence']}",
                f"- Sources: {citation_md(snapshot['sourceIds'])}",
                f"- Limitations: {snapshot['limitations']}",
                "",
            ]
        )
        if year_events:
            parts.append(markdown_table(
                ["Date", "Event", "Class", "Confidence", "Sources", "Notes"],
                [[event["dateStart"], event["title"], event["statementClass"], event["confidence"], citation_md(event["sourceIds"]), event["notes"]] for event in year_events],
            ))
            parts.append("")

    parts.extend(
        [
            "## Schools",
            "",
            markdown_table(
                ["School", "Opened", "Location precision", "Confidence", "Sources", "Limitations"],
                [[row["name"], row["openDate"], row["geometryPrecision"], row["confidence"], citation_md(row["sourceIds"]), row["limitations"]] for row in schools],
            ),
            "",
            "## Infrastructure Requirements",
            "",
            "These are requirements in the County program, not completion events.",
            "",
            markdown_table(
                ["Trigger", "Value", "Requirement", "Source location", "Limitations"],
                [[row["triggerType"], row["triggerValue"], row["obligation"], row["sourceLocator"], row["limitations"]] for row in obligations],
            ),
            "",
            "## Open Research Questions",
            "",
            markdown_table(
                ["ID", "Priority", "Category", "Question", "Status", "Blocked output", "Next action"],
                [[row["id"], row["priority"], row["category"], row["question"], row["status"], row["blockedOutput"], row["nextAction"]] for row in questions],
            ),
            "",
            "## Bibliography and Source Registry",
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


def build_html(data: dict[str, list[dict[str, str]]]) -> str:
    snapshots = data["snapshots"]
    events = data["events"]
    sources = data["sources"]
    planning = data["planning"]
    obligations = data["obligations"]
    schools = data["schools"]
    questions = data["questions"]
    tract_count = sum(1 for _ in csv.DictReader((ROOT / "data/development/tract_maps.csv").open(encoding="utf-8")))

    annual = []
    for snapshot in snapshots:
        year = snapshot["year"]
        year_events = [event for event in events if event["dateStart"].startswith(year)]
        event_html = "".join(
            f'<li><time>{escape(event["dateStart"])}</time><div><strong>{escape(event["title"])}</strong><p>{escape(event["notes"])}</p>{citation_html(event["sourceIds"])}</div></li>'
            for event in year_events
        ) or '<li class="empty">No dated event registered for this year.</li>'
        annual.append(f"""
<section class="year" id="year-{year}">
  <div class="year-number">{year}</div>
  <div class="year-body">
    <p class="status">{escape(snapshot['communityStatus'].replace('_', ' '))}</p>
    <h2>{escape(snapshot['documentedMilestones'])}</h2>
    <div class="metrics"><span><b>{escape(snapshot['tractMapsRecordedByYear'])}</b> tracts recorded</span><span><b>{escape(snapshot['tractMapsRecordedCumulative'])}</b> cumulative</span><span><b>{escape(snapshot['homesSoldAsOf'] or 'n/a')}</b> homes sold milestone</span><span><b>{escape(snapshot['activeSchoolCount'])}</b> schools open</span></div>
    <p class="limit"><b>{escape(snapshot['confidence'])} confidence.</b> {escape(snapshot['limitations'])}</p>
    <p>{citation_html(snapshot['sourceIds'])}</p>
    <ol class="events">{event_html}</ol>
  </div>
</section>""")

    source_html = "".join(
        f"""<article class="source" id="source-{escape(source['id'])}"><p class="source-id">{escape(source['id'])} · {escape(source['reliabilityGrade'])}</p><h3>{escape(source['title'])}</h3><p>{escape(source['publisher'] or 'Publisher not stated')}</p><p><a href="{escape(source['url'])}">{escape(source['url'])}</a></p><dl><dt>Archive</dt><dd>{escape(source['localFilePath'] or 'Not archived')} ({escape(source['archiveStatus'])})</dd><dt>SHA-256</dt><dd class="checksum">{escape(source['checksumSha256'] or 'Unavailable')}</dd><dt>Limitations</dt><dd>{escape(source['knownLimitations'])}</dd></dl></article>"""
        for source in sources
    )

    planning_table = html_table(
        ["PA", "Use", "Max dwellings", "Residential acres", "Gross acres", "Profile", "Source"],
        [[row["planningArea"], row["landUse"], row["maxDwellingUnits"], row["residentialNetAcres"], row["grossAcres"], row["communityProfileRange"], citation_html(row["sourceIds"])] for row in planning],
        {6},
    )
    school_table = html_table(
        ["School", "Opened", "Location precision", "Confidence", "Sources", "Limitations"],
        [[row["name"], row["openDate"], row["geometryPrecision"], row["confidence"], citation_html(row["sourceIds"]), row["limitations"]] for row in schools],
        {4},
    )
    obligation_table = html_table(
        ["Trigger", "Value", "Requirement", "Source page", "Limitations"],
        [[row["triggerType"], row["triggerValue"], row["obligation"], row["sourceLocator"], row["limitations"]] for row in obligations],
    )
    question_table = html_table(
        ["ID", "Priority", "Category", "Question", "Status", "Blocked output", "Next action"],
        [[row["id"], row["priority"], row["category"], row["question"], row["status"], row["blockedOutput"], row["nextAction"]] for row in questions],
    )

    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Ladera Ranch Historical Development Atlas</title>
<style>
:root{{--ink:#172635;--navy:#17324d;--red:#b43f2f;--gold:#b07a27;--teal:#286f78;--paper:#f7f5ef;--line:#c9ced1;--muted:#5c6872}}*{{box-sizing:border-box}}html{{scroll-behavior:smooth}}body{{margin:0;color:var(--ink);background:var(--paper);font:16px/1.55 Arial,sans-serif;letter-spacing:0}}main{{max-width:1120px;margin:auto;padding:48px 32px 80px}}h1,h2,h3{{font-family:Georgia,serif;color:var(--navy);letter-spacing:0}}h1{{font-size:48px;line-height:1.05;max-width:16ch;margin:.25rem 0 1rem}}h2{{line-height:1.2}}a{{color:#155e75}}.eyebrow,.status,.source-id{{text-transform:uppercase;font:700 12px/1.3 Arial,sans-serif;color:var(--red)}}.lede{{font:21px/1.5 Georgia,serif;max-width:72ch}}.scope{{border-left:5px solid var(--red);background:#fff;padding:18px 22px;margin:30px 0}}.summary{{display:grid;grid-template-columns:repeat(6,1fr);border-block:1px solid var(--line);margin:34px 0}}.summary div{{padding:18px 10px;border-right:1px solid var(--line)}}.summary div:last-child{{border:0}}.summary b{{display:block;font:30px Georgia,serif;color:var(--navy)}}.hero-map{{display:block;width:100%;max-height:720px;object-fit:contain;background:#fff;border:1px solid var(--line);margin:25px 0 8px}}.caption,.muted,.limit{{color:var(--muted)}}.method,.section{{padding-top:48px}}.year{{display:grid;grid-template-columns:145px 1fr;border-top:1px solid var(--line);padding:34px 0}}.year-number{{font:56px/1 Georgia,serif;color:var(--red)}}.year-body h2{{margin:.15rem 0 1rem}}.metrics{{display:grid;grid-template-columns:repeat(4,1fr);gap:1px;background:var(--line);margin:18px 0}}.metrics span{{background:#fff;padding:12px}}.metrics b{{display:block;color:var(--teal);font-size:22px}}.citation{{display:inline-block;background:#e4eaeb;color:var(--navy);padding:2px 6px;margin:2px;text-decoration:none;font:700 10px Arial,sans-serif;border-radius:3px}}.events{{list-style:none;padding:0;margin:22px 0}}.events li{{display:grid;grid-template-columns:110px 1fr;border-top:1px solid #dde0e1;padding:12px 0}}.events time{{font:12px monospace;color:var(--gold)}}.events p{{margin:3px 0;color:var(--muted)}}.table-wrap{{overflow-x:auto;margin:18px 0 38px}}table{{width:100%;border-collapse:collapse;background:#fff;font-size:13px}}th,td{{text-align:left;vertical-align:top;border:1px solid var(--line);padding:9px}}th{{background:var(--navy);color:#fff}}.source{{background:#fff;border-top:3px solid var(--navy);padding:18px;margin:16px 0;break-inside:avoid}}.source p,.source a{{overflow-wrap:anywhere;word-break:break-word}}dl{{display:grid;grid-template-columns:100px 1fr;gap:4px 12px}}dt{{font-weight:bold}}dd{{margin:0;overflow-wrap:anywhere}}.checksum{{font:11px monospace}}@media(max-width:800px){{main{{padding:30px 18px}}h1{{font-size:38px}}.summary{{grid-template-columns:repeat(2,1fr)}}.year{{grid-template-columns:1fr}}.year-number{{font-size:38px;margin-bottom:12px}}.metrics{{grid-template-columns:repeat(2,1fr)}}}}@media print{{body{{background:#fff;font-size:10pt}}main{{max-width:none;padding:0}}.year{{break-inside:avoid}}a{{color:inherit;text-decoration:none}}@page{{size:letter;margin:.6in}}}}
</style></head><body><main>
<header><p class="eyebrow">LHDRS Evidence Publication</p><h1>Ladera Ranch Historical Development Atlas</h1><p class="lede">A source-traceable reconstruction of planning, recorded subdivisions, schools, facilities, sales, and occupancy milestones from 1997 through 2008.</p><p>Generated {date.today().isoformat()} from canonical research registries.</p></header>
<aside class="scope"><strong>Historical-development scope.</strong> This atlas does not infer contamination, exposure, health effects, or causation. A tract-map recording date is a legal subdivision milestone, not proof of grading, construction, sale, road opening, or occupancy.</aside>
<div class="summary"><div><b>{len(sources)}</b>sources</div><div><b>{len(events)}</b>events</div><div><b>{len(snapshots)}</b>years</div><div><b>{tract_count}</b>tracts</div><div><b>{len(schools)}</b>schools</div><div><b>{sum(row['status'] != 'resolved' for row in questions)}</b>open questions</div></div>
<section class="method"><p class="eyebrow">Method</p><h2>Evidence remains attached to every statement</h2><p>The system separates source records, observed events, regulatory obligations, annual summaries, and generated geometry. Conflicts retain both source claims. Blank fields are unresolved rather than estimated. Historical construction proximity is blocked until dated occupied-neighborhood and active-construction polygons exist.</p></section>
<section class="section"><p class="eyebrow">County Baseline</p><h2>Planned community framework</h2><img class="hero-map" src="../evidence/lhdrs/figures/ladera_development_plan_1995.jpg" alt="County Ladera Planned Community development plan"><p class="caption">County development plan. Planned allocations are not as-built quantities.</p>{planning_table}</section>
<section class="section"><p class="eyebrow">Annual Reconstruction</p><h2>Development chronology, 1997-2008</h2>{''.join(annual)}</section>
<section class="section"><p class="eyebrow">Public Facilities</p><h2>Documented school openings</h2>{school_table}</section>
<section class="section"><p class="eyebrow">Regulatory Baseline</p><h2>Infrastructure requirements, not completion events</h2>{obligation_table}</section>
<section class="section"><p class="eyebrow">Research Queue</p><h2>Open and blocked questions</h2>{question_table}</section>
<section class="section"><p class="eyebrow">Bibliography</p><h2>Source registry and archived evidence</h2>{source_html}</section>
</main></body></html>"""


def main() -> int:
    required = ROOT / "data/development/tract_maps.csv"
    if not required.exists():
        raise SystemExit("Missing generated tract ledger. Run python3 pipelines/python/build_lhdrs.py first.")
    data = {
        "sources": read_csv("sources.csv"),
        "events": read_csv("events.csv"),
        "snapshots": read_csv("annual_snapshots.csv"),
        "planning": read_csv("planning_areas.csv"),
        "obligations": read_csv("development_obligations.csv"),
        "schools": read_csv("schools.csv"),
        "questions": read_csv("unresolved_questions.csv"),
    }
    REPORTS.mkdir(parents=True, exist_ok=True)
    markdown_path = REPORTS / "LHDRS_Historical_Development_Atlas.md"
    html_path = REPORTS / "LHDRS_Historical_Development_Atlas.html"
    markdown_path.write_text(build_markdown(data), encoding="utf-8")
    html_path.write_text(build_html(data), encoding="utf-8")
    print(f"Published {markdown_path.relative_to(ROOT)}")
    print(f"Published {html_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
