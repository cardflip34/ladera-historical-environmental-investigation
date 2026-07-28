#!/usr/bin/env python3
"""Render a Markdown report to a branded PDF.

Every report carries the project masthead in a running header on each page:

    California's Forgotten Past  ·  The Arsenic Cattle-Dipping Era
    <Report name>

Usage:
    python3 scripts/build_report_pdf.py INPUT.md OUTPUT.pdf \
        --title "Report name" [--subtitle "..."] [--date 2026-07-28] \
        [--footnote "Internal review document."]

Markdown -> HTML is done here; the PDF is rendered by headless Chromium via
Playwright (installed globally in this environment), which is what gives us a
true repeating header/footer on every page rather than a one-off banner.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile

import markdown

# Project identity — keep in sync with the site palette (index.html / REPORT_CSS).
BRAND = "California&rsquo;s Forgotten Past"
BRAND_SUB = "The Arsenic Cattle-Dipping Era"
INK = "#16233a"
INK2 = "#48586c"
BRASS = "#a97e1f"
ACCENT = "#2f6087"
LINE = "#ddd7ca"
MUTED = "#7c8a9c"

NODE_PLAYWRIGHT = "/opt/node22/lib/node_modules/playwright"
CHROMIUM = "/opt/pw-browsers/chromium"

CSS = f"""
@page {{ size: Letter; }}
* {{ box-sizing: border-box; }}
body {{
  margin: 0;
  color: {INK};
  font: 10.6pt/1.55 -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  -webkit-print-color-adjust: exact; print-color-adjust: exact;
}}
/* ---- cover block (first page only) ---- */
.cover {{ border-bottom: 3px solid {BRASS}; padding-bottom: 16px; margin-bottom: 22px; }}
.cover .eyebrow {{
  font-size: 8pt; letter-spacing: .15em; text-transform: uppercase;
  color: {BRASS}; font-weight: 700; margin: 0 0 10px;
}}
.cover h1.doc-title {{
  font-family: "Iowan Old Style", Georgia, serif; font-weight: 600;
  font-size: 22pt; line-height: 1.15; letter-spacing: -.012em;
  color: {INK}; margin: 0 0 6px; border: 0;
}}
.cover .doc-sub {{
  font-family: "Iowan Old Style", Georgia, serif; font-style: italic;
  font-size: 12pt; color: {BRASS}; margin: 0 0 12px;
}}
.cover .doc-meta {{ font-size: 8.8pt; color: {MUTED}; margin: 0; }}
/* ---- body ---- */
h1 {{
  font-family: "Iowan Old Style", Georgia, serif; font-size: 15pt; color: {INK};
  margin: 20px 0 6px; line-height: 1.2; page-break-after: avoid;
}}
h2 {{
  font-family: "Iowan Old Style", Georgia, serif; font-size: 12.6pt; color: {INK};
  border-bottom: 2px solid {BRASS}; padding-bottom: 3px;
  margin: 20px 0 8px; page-break-after: avoid;
}}
h3 {{
  font-size: 10.8pt; color: {ACCENT}; margin: 14px 0 4px;
  page-break-after: avoid; letter-spacing: .005em;
}}
p {{ margin: 0 0 8px; orphans: 2; widows: 2; }}
strong {{ color: {INK}; font-weight: 700; }}
em {{ color: {INK2}; }}
ul, ol {{ margin: 0 0 10px; padding-left: 20px; }}
li {{ margin: 0 0 5px; }}
li > strong:first-child {{ color: {INK}; }}
hr {{ border: 0; border-top: 1px solid {LINE}; margin: 18px 0; }}
a {{ color: {ACCENT}; text-decoration: none; }}
code {{
  background: #efe9dc; padding: 1px 4px; border-radius: 3px;
  font-size: 9pt; color: {INK};
}}
blockquote {{
  border-left: 3px solid {BRASS}; background: #f7f2e4; margin: 10px 0;
  padding: 8px 13px; font-size: 9.6pt; color: #5a4a2c; border-radius: 0 5px 5px 0;
}}
table {{ border-collapse: collapse; width: 100%; margin: 10px 0; font-size: 9.2pt; }}
th, td {{ border: 1px solid {LINE}; padding: 5px 8px; text-align: left; vertical-align: top; }}
th {{ background: #efe9dc; font-weight: 700; }}
/* the closing italic note */
p em:only-child {{ color: {MUTED}; font-size: 9.2pt; }}
"""

HEADER_TMPL = """
<div style="width:100%; font-family:-apple-system,'Segoe UI',Helvetica,Arial,sans-serif;
            padding:0 0.72in; margin:0; -webkit-print-color-adjust:exact;">
  <div style="border-bottom:1px solid {LINE}; padding-bottom:5px;">
    <div style="font-family:Georgia,'Iowan Old Style',serif; font-size:8.4pt; color:{INK};
                letter-spacing:.01em;">
      <span style="font-weight:700;">{BRAND}</span>
      <span style="color:{BRASS};">&nbsp;&middot;&nbsp;</span>
      <span style="font-style:italic; color:{BRASS};">{BRAND_SUB}</span>
    </div>
    <div style="font-size:7.4pt; color:{MUTED}; margin-top:2px; letter-spacing:.05em;
                text-transform:uppercase;">{REPORT}</div>
  </div>
</div>
"""

FOOTER_TMPL = """
<div style="width:100%; font-family:-apple-system,'Segoe UI',Helvetica,Arial,sans-serif;
            padding:0 0.72in; margin:0; font-size:7.4pt; color:{MUTED};
            -webkit-print-color-adjust:exact;">
  <div style="border-top:1px solid {LINE}; padding-top:5px; display:flex;
              justify-content:space-between;">
    <span>{NOTE}</span>
    <span>Page <span class="pageNumber"></span> of <span class="totalPages"></span></span>
  </div>
</div>
"""

RENDER_JS = r"""
import { createRequire } from 'module';
const require = createRequire(import.meta.url);
const { chromium } = require(process.env.PW_PATH);
const cfg = JSON.parse(process.env.PDF_CFG);

const browser = await chromium.launch({ executablePath: process.env.CHROMIUM_PATH });
const page = await browser.newPage();
await page.goto('file://' + cfg.html, { waitUntil: 'load' });
await page.pdf({
  path: cfg.pdf,
  format: 'Letter',
  printBackground: true,
  displayHeaderFooter: true,
  headerTemplate: cfg.header,
  footerTemplate: cfg.footer,
  margin: { top: '1.02in', bottom: '0.78in', left: '0.72in', right: '0.72in' },
});
await browser.close();
console.log('ok');
"""


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build(md_path, pdf_path, title, subtitle, date, footnote):
    if not shutil.which("node"):
        sys.exit("node not found; required to render the PDF")
    if not os.path.isdir(NODE_PLAYWRIGHT):
        sys.exit(f"playwright not found at {NODE_PLAYWRIGHT}")

    raw = open(md_path, encoding="utf-8").read()

    # Drop a leading H1/H2 pair — the cover block already states the title.
    lines = raw.split("\n")
    while lines and (lines[0].startswith("# ") or lines[0].startswith("## ") or not lines[0].strip()):
        if lines[0].startswith("# ") or lines[0].startswith("## "):
            lines.pop(0)
            continue
        if not lines[0].strip():
            lines.pop(0)
            continue
        break
    body_md = "\n".join(lines)

    body_html = markdown.markdown(
        body_md, extensions=["tables", "fenced_code", "sane_lists"]
    )

    meta_bits = [b for b in [date, footnote] if b]
    cover = f"""
<div class="cover">
  <p class="eyebrow">{BRAND} &middot; Independent research &amp; data-organization project</p>
  <h1 class="doc-title">{esc(title)}</h1>
  {f'<p class="doc-sub">{esc(subtitle)}</p>' if subtitle else ''}
  {f'<p class="doc-meta">{esc(" &middot; ".join(meta_bits))}</p>'.replace("&amp;middot;", "&middot;") if meta_bits else ''}
</div>
"""

    html = (
        "<!doctype html><html lang='en'><head><meta charset='utf-8'>"
        f"<title>{esc(title)}</title><style>{CSS}</style></head><body>"
        f"{cover}{body_html}</body></html>"
    )

    tmpdir = tempfile.mkdtemp(prefix="reportpdf_")
    html_path = os.path.join(tmpdir, "report.html")
    open(html_path, "w", encoding="utf-8").write(html)

    header = HEADER_TMPL.format(
        LINE=LINE, INK=INK, BRASS=BRASS, MUTED=MUTED,
        BRAND=BRAND, BRAND_SUB=BRAND_SUB, REPORT=esc(title),
    )
    footer = FOOTER_TMPL.format(
        LINE=LINE, MUTED=MUTED,
        NOTE=esc(footnote or "Independent research &amp; data-organization project"),
    )

    js_path = os.path.join(tmpdir, "render.mjs")
    open(js_path, "w", encoding="utf-8").write(RENDER_JS)

    env = dict(os.environ)
    env["PW_PATH"] = NODE_PLAYWRIGHT
    env["CHROMIUM_PATH"] = CHROMIUM
    env["PDF_CFG"] = json.dumps(
        {"html": html_path, "pdf": os.path.abspath(pdf_path),
         "header": header, "footer": footer}
    )

    res = subprocess.run(["node", js_path], env=env, capture_output=True, text=True)
    if res.returncode != 0:
        sys.exit(f"PDF render failed:\n{res.stderr[-2000:]}")

    size = os.path.getsize(pdf_path)
    print(f"wrote {pdf_path} ({size:,} bytes)")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("input")
    ap.add_argument("output")
    ap.add_argument("--title", required=True, help="Report name (shown in the running header)")
    ap.add_argument("--subtitle", default="")
    ap.add_argument("--date", default="")
    ap.add_argument("--footnote", default="")
    a = ap.parse_args()
    build(a.input, a.output, a.title, a.subtitle, a.date, a.footnote)


if __name__ == "__main__":
    main()
