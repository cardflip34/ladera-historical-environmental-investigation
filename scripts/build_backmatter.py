#!/usr/bin/env python3
"""Generate the publication's back matter from the project's own data files.

Bibliography, image credits, and source library are rendered from sources.csv and
image-archive.csv rather than maintained by hand. A hand-written bibliography drifts out of
sync with the registry the moment either is edited; generating both from one file makes that
impossible by construction.

Version history is assembled from CORRECTIONS.md so a correction cannot be logged without
appearing in the publication.
"""
import csv
import os
import re
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CH = os.path.join(ROOT, "docs", "publication", "chapters")
SOURCES = os.path.join(ROOT, "research", "source_registry", "sources.csv")
IMAGES = os.path.join(ROOT, "docs", "publication", "data", "image-archive.csv")
CORRECTIONS = os.path.join(ROOT, "research", "CORRECTIONS.md")
MATRIX = os.path.join(ROOT, "research", "_logs", "EVIDENCE_MATRIX.csv")

GRADE_NOTE = {
    "A1": "Official machine-readable government dataset; peer-reviewed primary research; official registry publication; official agency report",
    "A2": "Official government webpage; regulatory filing; official meeting document; official GIS service",
    "B1": "University or research-institution report; systematic review; nonprofit technical report with transparent methodology",
    "B2": "Reputable news outlet quoting named sources or documents; public statements from identifiable stakeholders",
    "C":  "Advocacy materials; law-firm summaries; community petitions; social media; unverified case counts",
    "D":  "Speculation; unsourced reposts; unsupported online claims",
}


def esc(s):
    return (s or "").replace("|", "\\|").strip()


def build_bibliography():
    rows = list(csv.DictReader(open(SOURCES, encoding="utf-8")))
    by_grade = {}
    for r in rows:
        by_grade.setdefault(r.get("reliabilityGrade", "?").strip() or "?", []).append(r)

    out = ["# Full Bibliography\n",
           "Every source consulted, graded on the fixed hierarchy set out in the methodology "
           "chapter. A record carries exactly one grade, and **a lower grade is never silently "
           "promoted** — a claim that appears in a newspaper becomes A1 only when the underlying "
           "official record is located and read.\n",
           f"**{len(rows)} sources.** Generated directly from the project's source registry, so "
           "this list cannot drift out of step with the registry itself.\n"]

    counts = " · ".join(f"**{g}** {len(by_grade.get(g, []))}"
                        for g in ["A1", "A2", "B1", "B2", "C", "D"] if by_grade.get(g))
    out.append(f"Distribution: {counts}\n")

    for g in ["A1", "A2", "B1", "B2", "C", "D"]:
        rs = by_grade.get(g)
        if not rs:
            continue
        out.append(f"\n## Grade {g}\n")
        out.append(f"*{GRADE_NOTE.get(g, '')}*\n")
        for r in sorted(rs, key=lambda x: (x.get("publisher", ""), x.get("title", ""))):
            title = esc(r.get("title"))
            pub = esc(r.get("publisher"))
            auth = esc(r.get("author"))
            date = esc(r.get("publicationDate")) or "n.d."
            url = esc(r.get("url"))
            ret = esc(r.get("retrievalDate"))
            sid = esc(r.get("id"))
            lim = esc(r.get("knownLimitations"))
            line = f"**{title}**"
            if auth:
                line = f"{auth}. {line}"
            line += f" {pub}, {date}."
            if url:
                line += f" <{url}>"
            if ret:
                line += f" Retrieved {ret}."
            out.append(f"- {line}  \n  `{sid}`")
            if lim:
                out.append(f"  \n  *Known limitations:* {lim}")
            out.append("")
    return "\n".join(out)


def build_image_credits():
    if not os.path.exists(IMAGES):
        return None
    rows = list(csv.DictReader(open(IMAGES, encoding="utf-8")))
    out = ["# Image Credits and Rights\n",
           "Every image published, with its repository, rights status **as the repository states "
           "it**, and its interpretation boundary. Rights statements are reproduced rather than "
           "summarised, because a paraphrased licence is not a licence.\n",
           f"**{len(rows)} published figures.**\n",
           "Images held in the evidence archive but **not** published for rights reasons are "
           "listed at the end.\n"]
    for r in rows:
        out.append(f"\n### {esc(r['image_id'])} — {esc(r['title'])}\n")
        out.append(f"| | |\n|---|---|")
        out.append(f"| Date | {esc(r.get('date'))} |")
        out.append(f"| Repository | {esc(r.get('repository'))} |")
        out.append(f"| Rights | {esc(r.get('rights'))} |")
        out.append(f"| Original | {esc(r.get('original_dimensions'))} — `{esc(r.get('original_path'))}` |")
        out.append(f"| Published as | {esc(r.get('published_file'))} ({esc(r.get('published_dimensions'))}) |")
        out.append(f"\n**Interpretation boundary.** {esc(r.get('interpretation_boundary'))}\n")
    out.append("\n---\n\n## Held but not published\n")
    out.append("These items were located and archived but are **not reproduced** in this "
               "publication, because their rights status does not permit it or is unclear.\n")
    out.append("| Item | Repository | Rights status |\n|---|---|---|")
    out.append("| Trabuco Mesa Adobe photographs (3) | Santa Ana Public Library | "
               "\"Copyright restrictions applying to use or reproduction of this image available "
               "from the Santa Ana Public Library\" — research use only |")
    out.append("| Trabuco Adobe ruins, O'Neill Park | OC Public Libraries / OC Archives | "
               "\"Copyright status is unknown\" |")
    out.append("\nA newspaper article discussed in this publication is **cited and briefly "
               "quoted, not reproduced as an image**. Reproducing a copyrighted article as a "
               "facsimile is a different act from quoting it under fair use.\n")
    return "\n".join(out)


def build_version_history():
    corr = open(CORRECTIONS, encoding="utf-8").read() if os.path.exists(CORRECTIONS) else ""
    ids = re.findall(r"^## (C-\d+) — (.+?) \((\d{4}-\d{2}-\d{2})\)", corr, re.M)

    try:
        log = subprocess.run(["git", "log", "--pretty=format:%h|%ad|%s", "--date=short"],
                             cwd=ROOT, capture_output=True, text=True, timeout=30).stdout.strip()
        commits = [l.split("|", 2) for l in log.split("\n") if "|" in l][:12]
    except Exception:
        commits = []

    n_claims = 0
    if os.path.exists(MATRIX):
        n_claims = len(list(csv.DictReader(open(MATRIX, encoding="utf-8"))))
    n_sources = len(list(csv.DictReader(open(SOURCES, encoding="utf-8"))))

    out = ["# Version History\n",
           "This project issues corrections **openly and in full**. Nothing is silently revised. "
           "Where a finding changed, the superseded reasoning is retained in the text alongside "
           "the correction, because a report that shows only what survived scrutiny is not an "
           "honest report.\n",
           f"**Version 1.0** — {n_claims} catalogued claims, {n_sources} registered sources.\n",
           "\n## Corrections issued\n"]

    if ids:
        out.append("| ID | Correction | Date |\n|---|---|---|")
        for cid, desc, date in ids:
            out.append(f"| **{cid}** | {esc(desc)} | {date} |")
    out.append("\nFull text of every correction, including what was affected and what was not, "
               "is retained in `research/CORRECTIONS.md`.\n")

    out.append("\n## The pattern in these corrections\n")
    out.append(
        "Four corrections have been issued. Three of them (C-001, C-003, C-004) share a shape "
        "worth naming: **an assumption about the physical evidence was adopted without checking "
        "it, and the assumption happened to make the analysis simpler.**\n\n"
        "- **C-001** — a centroid was inherited from a brief and never verified. It was 1.93 "
        "miles wrong, and correcting it moved two plugged wells from ~2 miles away to ~0.25 "
        "and ~0.77 miles.\n"
        "- **C-003** — the earliest imagery was assumed to be 1948, which conveniently made a "
        "dip vat undetectable *in principle*. Photography from 1929 existed the whole time.\n"
        "- **C-004** — having obtained that photography, the project then assumed the target "
        "would be large and declared the resolution objection resolved. USDA's own California "
        "circular documents wade tanks costing under ten dollars.\n\n"
        "Each was caught by going to a primary source or by rendering the data rather than "
        "trusting a table. That is the only countermeasure this project has found that works.\n")

    if commits:
        out.append("\n## Build history\n")
        out.append("| Commit | Date | Change |\n|---|---|---|")
        for h, d, s in commits:
            out.append(f"| `{h}` | {d} | {esc(s)} |")
    return "\n".join(out)


def main():
    written = []
    for fn, content in [("33_bibliography.md", build_bibliography()),
                        ("34_image_credits.md", build_image_credits()),
                        ("37_version_history.md", build_version_history())]:
        if content is None:
            continue
        path = os.path.join(CH, fn)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content + "\n")
        written.append((fn, len(content.split())))
    for fn, w in written:
        print(f"  generated {fn}  ({w:,} words)")


if __name__ == "__main__":
    main()
