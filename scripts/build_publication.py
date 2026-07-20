#!/usr/bin/env python3
"""Build the Version 1.0 investigation publication from chapter markdown.

Content lives in docs/publication/chapters/NN_slug.md and is assembled here into a single
self-navigable HTML document. Keeping content in markdown and assembly in code means a
chapter can be rewritten without touching the build, and the build can be changed without
risking the prose.

Custom block syntax, preprocessed before markdown rendering:

    ::: classification fact
    **EM-001 - ESTABLISHED FACT - Confidence: High**
    ...
    :::

renders as a labelled evidence card. Kinds: fact, context, lead, open, limit, correction.
"""
import csv
import html
import json
import os
import re
import sys

import markdown

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CH = os.path.join(ROOT, "docs", "publication", "chapters")
OUT = os.path.join(ROOT, "docs", "publication", "index.html")
MATRIX = os.path.join(ROOT, "research", "_logs", "EVIDENCE_MATRIX.csv")

KINDS = {
    "fact":       ("Established Fact",  "k-fact"),
    "context":    ("Historical Context", "k-context"),
    "lead":       ("Investigative Lead", "k-lead"),
    "open":       ("Open Question",      "k-open"),
    "limit":      ("Limitation",         "k-limit"),
    "correction": ("Correction Issued",  "k-correction"),
}

BLOCK = re.compile(r"^::: classification (\w+)\s*\n(.*?)^:::\s*$", re.S | re.M)
FIGREF = re.compile(r"^@figure\s+(FIG-\d+)\s*$", re.M)

_IMG_ARCHIVE = os.path.join(ROOT, "docs", "publication", "data", "image-archive.csv")


def load_images():
    """Figure metadata lives in the image archive so a caption can never drift from its
    provenance record — both are rendered from the same row."""
    if not os.path.exists(_IMG_ARCHIVE):
        return {}
    with open(_IMG_ARCHIVE, newline="", encoding="utf-8") as f:
        return {r["image_id"]: r for r in csv.DictReader(f)}


IMAGES = load_images()


def figure_html(fid):
    r = IMAGES.get(fid)
    if not r:
        return f'<p class="mx-none">[{html.escape(fid)} — not present in image archive]</p>'
    e = lambda k: html.escape(r.get(k, ""))
    return f"""
<figure id="{fid.lower()}">
  <img src="{e('published_file')}" alt="{e('title')}" loading="lazy"
       width="{r.get('published_dimensions','').split('x')[0]}"
       height="{r.get('published_dimensions','').split('x')[-1]}">
  <figcaption>
    <span class="cap-t">{e('image_id')} · {e('title')}</span>
    <span class="cap-m"><strong>Interpretation boundary:</strong> {e('interpretation_boundary')}</span>
    <span class="cap-m">Date {e('date')} · {e('repository')} · {e('rights')}
      · Original {e('original_dimensions')} at <code>{e('original_path')}</code></span>
  </figcaption>
</figure>"""


def preprocess(md_text):
    """Expand ::: classification blocks and @figure references before markdown rendering."""
    def repl(m):
        kind = m.group(1)
        body = m.group(2)
        label, cls = KINDS.get(kind, ("Note", "k-context"))
        inner = markdown.markdown(body, extensions=["tables", "attr_list"])
        return (f'\n<div class="ev {cls}">'
                f'<div class="ev-label">{html.escape(label)}</div>'
                f'<div class="ev-body">{inner}</div></div>\n')
    md_text = BLOCK.sub(repl, md_text)
    return FIGREF.sub(lambda m: figure_html(m.group(1)), md_text)


def slugify(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def load_chapters():
    if not os.path.isdir(CH):
        return []
    out = []
    for fn in sorted(os.listdir(CH)):
        if not fn.endswith(".md"):
            continue
        path = os.path.join(CH, fn)
        raw = open(path, encoding="utf-8").read()
        m = re.search(r"^#\s+(.+)$", raw, re.M)
        title = m.group(1).strip() if m else fn[:-3]
        # Drop the H1; the template supplies the chapter header.
        body_md = re.sub(r"^#\s+.+$", "", raw, count=1, flags=re.M)
        num = fn.split("_")[0]
        body_html = markdown.markdown(
            preprocess(body_md),
            extensions=["tables", "attr_list", "fenced_code", "toc", "sane_lists"],
        )
        # Collect H2s for the in-page contents.
        subs = [(slugify(t), t) for t in re.findall(r"^##\s+(.+)$", body_md, re.M)]
        body_html = re.sub(
            r"<h2>(.*?)</h2>",
            lambda mm: f'<h2 id="{slugify(re.sub("<[^>]+>", "", mm.group(1)))}">{mm.group(1)}</h2>',
            body_html,
        )
        out.append({"file": fn, "num": num, "title": title,
                    "slug": slugify(title), "html": body_html, "subs": subs})
    return out


def load_matrix():
    if not os.path.exists(MATRIX):
        return []
    with open(MATRIX, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


CSS = r"""
:root{
  --bg:#0b0f16; --bg2:#0e141d; --panel:#131a24; --panel2:#18212d;
  --ink:#e9e6e0; --ink-dim:#9aa8b8; --ink-faint:#6b7a8c;
  --line:#202b3a; --line2:#2b394b;
  --accent:#c8a951;          /* aged brass - survey ink, archival */
  --water:#6ba9c4;
  --fact:#5fb37a; --context:#6ba9c4; --lead:#c8a951;
  --open:#c4756b; --limit:#9a8fb0; --correction:#d08a4f;
  --serif: "Iowan Old Style", "Palatino Linotype", Palatino, Georgia, "Times New Roman", serif;
  --sans: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  --mono: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace;
}
*{box-sizing:border-box}
html{scroll-behavior:smooth; scroll-padding-top:70px}
/* The off-canvas contents drawer sits at translateX(-100%); without this it widens the
   scroll area and the whole page slides sideways on narrow screens. */
body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--serif);
  font-size:17.5px;line-height:1.72;-webkit-text-size-adjust:100%;
  font-feature-settings:"kern" 1,"liga" 1;overflow-x:hidden}

/* ---- top bar ---- */
.topbar{position:sticky;top:0;z-index:50;background:rgba(11,15,22,.94);
  backdrop-filter:blur(10px);border-bottom:1px solid var(--line);
  display:flex;align-items:center;gap:14px;padding:11px 18px}
.topbar .brand{font-family:var(--sans);font-size:13px;font-weight:700;letter-spacing:.13em;
  text-transform:uppercase;color:var(--accent);white-space:nowrap;
  overflow:hidden;text-overflow:ellipsis;min-width:0}
.topbar .spacer{flex:1}
.topbar > button{flex:none}
.topbar button{font-family:var(--sans);font-size:12.5px;background:var(--panel);
  color:var(--ink-dim);border:1px solid var(--line2);border-radius:6px;
  padding:6px 12px;cursor:pointer}
.topbar button:hover{color:var(--ink);border-color:var(--accent)}
.topbar button:focus-visible{outline:2px solid var(--accent);outline-offset:2px}

.layout{display:grid;grid-template-columns:288px minmax(0,1fr);gap:0;max-width:1500px;margin:0 auto}

/* ---- sidebar ---- */
#toc{position:sticky;top:52px;height:calc(100vh - 52px);overflow-y:auto;
  border-right:1px solid var(--line);padding:24px 16px 60px;font-family:var(--sans)}
#toc h3{font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:var(--ink-faint);
  margin:0 0 12px;font-weight:700}
#toc ol{list-style:none;margin:0;padding:0}
#toc > ol > li{margin-bottom:2px}
#toc a{display:block;padding:6px 10px;border-radius:5px;color:var(--ink-dim);
  text-decoration:none;font-size:13.5px;line-height:1.35;border-left:2px solid transparent}
#toc .n{color:var(--ink-faint);font-variant-numeric:tabular-nums;
  font-size:12px;margin-right:5px}
#toc a:hover{background:var(--panel);color:var(--ink)}
#toc a.active{color:var(--accent);border-left-color:var(--accent);background:var(--panel)}
#toc .sub{list-style:none;padding-left:14px;margin:0 0 6px}
#toc .sub a{font-size:12.5px;padding:3px 10px;color:var(--ink-faint)}

main{padding:0 0 120px;min-width:0}
.wrap{max-width:820px;margin:0 auto;padding:0 30px}

/* ---- cover ---- */
.cover{padding:96px 30px 80px;border-bottom:1px solid var(--line);
  background:radial-gradient(ellipse at 22% -10%, #182333 0%, var(--bg) 62%)}
.cover .inner{max-width:820px;margin:0 auto}
.eyebrow{font-family:var(--sans);font-size:11.5px;letter-spacing:.2em;text-transform:uppercase;
  color:var(--accent);margin:0 0 22px;font-weight:700}
.cover h1{font-size:clamp(34px,6vw,62px);line-height:1.08;margin:0 0 22px;
  letter-spacing:-.022em;text-wrap:balance;font-weight:600}
.cover .deck{font-size:clamp(18px,2.4vw,22px);color:var(--ink-dim);margin:0 0 34px;
  max-width:60ch;line-height:1.55}
.meta{display:flex;flex-wrap:wrap;gap:10px;font-family:var(--sans);font-size:12px}
.meta span{border:1px solid var(--line2);border-radius:999px;padding:5px 13px;color:var(--ink-dim)}

/* ---- disclaimer ---- */
.disclaimer{background:#1a1410;border:1px solid #3a2a1c;border-left:3px solid var(--correction);
  border-radius:0 8px 8px 0;padding:20px 24px;margin:34px 0;font-size:15.5px;color:#e2d8cc}
.disclaimer strong{color:#f2e3d0}

/* ---- chapters ---- */
.chapter{padding:64px 0 20px;border-bottom:1px solid var(--line)}
.chapter-num{font-family:var(--sans);font-size:11.5px;letter-spacing:.18em;text-transform:uppercase;
  color:var(--accent);font-weight:700;margin-bottom:10px}
.chapter h1{font-size:clamp(27px,4.2vw,40px);line-height:1.14;margin:0 0 30px;
  letter-spacing:-.018em;text-wrap:balance;font-weight:600}
h2{font-size:clamp(21px,2.9vw,27px);margin:52px 0 16px;line-height:1.25;
  letter-spacing:-.012em;text-wrap:balance;font-weight:600;
  padding-top:14px;border-top:1px solid var(--line)}
h3{font-size:19px;margin:34px 0 12px;color:var(--ink);font-weight:600;line-height:1.32}
p{margin:0 0 20px}
a{color:var(--water);text-decoration:none;border-bottom:1px solid rgba(107,169,196,.32)}
a:hover{border-bottom-color:var(--water)}
strong{color:#fff;font-weight:600}
em{color:var(--ink)}
del{color:var(--ink-faint)}
ul,ol{margin:0 0 20px;padding-left:26px}
li{margin-bottom:9px}
hr{border:0;border-top:1px solid var(--line);margin:44px 0}
blockquote{margin:24px 0;padding:2px 0 2px 22px;border-left:3px solid var(--line2);
  color:var(--ink-dim);font-style:italic}
code{font-family:var(--mono);font-size:.845em;background:var(--panel2);
  padding:2px 6px;border-radius:4px;color:#d8c9a0;word-break:break-word}
pre{background:var(--panel);border:1px solid var(--line);border-radius:8px;
  padding:16px;overflow-x:auto}
pre code{background:none;padding:0}

/* ---- tables ---- */
.tw{overflow-x:auto;margin:24px 0;border:1px solid var(--line);border-radius:9px;
  background:var(--panel)}
table{width:100%;border-collapse:collapse;font-family:var(--sans);font-size:14.5px}
th,td{text-align:left;padding:11px 15px;border-bottom:1px solid var(--line);vertical-align:top}
th{color:var(--accent);font-weight:700;font-size:11.5px;letter-spacing:.075em;
  text-transform:uppercase;background:var(--panel2);white-space:nowrap}
tr:last-child td{border-bottom:none}
td:not(:first-child){font-variant-numeric:tabular-nums}

/* ---- evidence cards ---- */
.ev{margin:28px 0;border-radius:9px;border:1px solid var(--line2);
  background:var(--panel);overflow:hidden}
.ev-label{font-family:var(--sans);font-size:11px;letter-spacing:.15em;text-transform:uppercase;
  font-weight:700;padding:8px 18px;color:#0b0f16}
.ev-body{padding:18px 20px 4px;font-size:16px}
.ev-body p{margin-bottom:13px}
.ev-body p:last-child{margin-bottom:14px}
.k-fact{border-color:var(--fact)} .k-fact .ev-label{background:var(--fact)}
.k-context{border-color:var(--context)} .k-context .ev-label{background:var(--context)}
.k-lead{border-color:var(--lead)} .k-lead .ev-label{background:var(--lead)}
.k-open{border-color:var(--open)} .k-open .ev-label{background:var(--open)}
.k-limit{border-color:var(--limit)} .k-limit .ev-label{background:var(--limit)}
.k-correction{border-color:var(--correction)} .k-correction .ev-label{background:var(--correction)}

/* ---- figures ---- */
figure{margin:34px 0;background:var(--panel);border:1px solid var(--line);
  border-radius:9px;overflow:hidden}
figure img{display:block;width:100%;height:auto;cursor:zoom-in}
figcaption{padding:14px 18px;font-family:var(--sans);font-size:13.5px;
  color:var(--ink-dim);border-top:1px solid var(--line);line-height:1.55}
figcaption .cap-t{color:var(--ink);font-weight:600}
figcaption .cap-m{display:block;margin-top:7px;font-size:12px;color:var(--ink-faint)}

/* ---- lightbox ---- */
#lb{position:fixed;inset:0;background:rgba(5,8,12,.96);z-index:200;display:none;
  align-items:center;justify-content:center;padding:24px;cursor:zoom-out}
#lb.on{display:flex}
#lb img{max-width:100%;max-height:92vh;object-fit:contain}
#lb .x{position:absolute;top:16px;right:22px;color:var(--ink);font-size:34px;
  background:none;border:none;cursor:pointer;line-height:1}

/* ---- evidence matrix ---- */
.mx-tools{display:flex;gap:10px;flex-wrap:wrap;margin:20px 0}
.mx-tools input,.mx-tools select{font-family:var(--sans);font-size:14px;background:var(--panel);
  color:var(--ink);border:1px solid var(--line2);border-radius:6px;padding:9px 12px}
.mx-tools input{flex:1;min-width:200px}
.mx-tools input:focus,.mx-tools select:focus{outline:2px solid var(--accent);outline-offset:1px}
.mx-card{border:1px solid var(--line2);border-radius:9px;background:var(--panel);
  margin-bottom:14px;overflow:hidden}
.mx-head{padding:14px 18px;cursor:pointer;display:flex;gap:12px;align-items:flex-start}
.mx-head:hover{background:var(--panel2)}
.mx-id{font-family:var(--mono);font-size:12px;color:var(--accent);white-space:nowrap;padding-top:2px}
.mx-claim{flex:1;font-size:15.5px;line-height:1.5}
.mx-tag{font-family:var(--sans);font-size:10px;letter-spacing:.1em;text-transform:uppercase;
  font-weight:700;padding:3px 9px;border-radius:999px;white-space:nowrap;color:#0b0f16}
.mx-body{display:none;padding:2px 18px 16px;font-size:15px;border-top:1px solid var(--line)}
.mx-card.open .mx-body{display:block}
.mx-body dt{font-family:var(--sans);font-size:10.5px;letter-spacing:.11em;text-transform:uppercase;
  color:var(--ink-faint);margin-top:14px;font-weight:700}
.mx-body dd{margin:5px 0 0}
.mx-none{color:var(--ink-faint);font-style:italic;padding:20px}

footer{padding:56px 30px 90px;border-top:1px solid var(--line);color:var(--ink-faint);
  font-family:var(--sans);font-size:13px;max-width:820px;margin:0 auto;line-height:1.7}

@media(max-width:1000px){
  .layout{grid-template-columns:1fr}
  #toc{position:fixed;inset:52px auto 0 0;width:290px;background:var(--bg2);z-index:45;
    transform:translateX(-100%);transition:transform .22s ease;border-right:1px solid var(--line2)}
  #toc.open{transform:translateX(0)}
  .wrap{padding:0 20px}
  .cover{padding:60px 20px 50px}
  body{font-size:17px}
}
@media(min-width:1001px){ .menu-btn{display:none} }
@media(prefers-reduced-motion:reduce){ *{transition:none!important;scroll-behavior:auto!important} }

@media print{
  :root{--bg:#fff;--panel:#fff;--panel2:#f6f6f4;--ink:#111;--ink-dim:#333;
        --ink-faint:#555;--line:#ccc;--line2:#bbb}
  body{background:#fff;color:#111;font-size:10.5pt;line-height:1.5}
  .topbar,#toc,#lb,.mx-tools,.menu-btn{display:none!important}
  .layout{display:block;max-width:none}
  .wrap{max-width:none;padding:0}
  /* Trailing margin on a chapter's last block can spill past the page box and force an
     extra blank sheet before the next chapter's forced break. Collapse it. */
  .chapter{page-break-before:always;border:none;padding:0}
  .chapter:first-of-type{page-break-before:avoid}
  .chapter > .wrap > *:last-child{margin-bottom:0}
  .chapter hr:last-of-type{display:none}
  h1,h2,h3{page-break-after:avoid;color:#000}
  h2{border-top:1px solid #ccc}
  figure,.ev,.mx-card{page-break-inside:avoid}
  /* Long tables (the timeline runs to ~50 rows) cannot fit on one page. Forbidding a break
     inside them pushes the whole table to the next sheet and leaves a blank one behind, so
     let the table break and keep individual rows intact instead. */
  table{page-break-inside:auto}
  tr{page-break-inside:avoid;page-break-after:auto}
  thead{display:table-header-group}
  figure img{max-height:5in;object-fit:contain}
  .ev-label{color:#000;border:1px solid #666;background:#eee!important}
  a{color:#111;border:none}
  a[href^="http"]::after{content:" (" attr(href) ")";font-size:8pt;color:#666;word-break:break-all}
  .mx-body{display:block!important}
  .cover{background:none;padding:0 0 24pt}
  th{color:#000;background:#eee}
}
"""

JS = r"""
// Lightbox: any figure image opens full-size.
var lb=document.getElementById('lb'), lbi=lb.querySelector('img');
document.addEventListener('click',function(e){
  var t=e.target;
  if(t.tagName==='IMG'&&t.closest('figure')){ lbi.src=t.currentSrc||t.src; lb.classList.add('on'); }
  else if(t.closest('#lb')){ lb.classList.remove('on'); }
});
document.addEventListener('keydown',function(e){ if(e.key==='Escape') lb.classList.remove('on'); });

// Mobile drawer.
var toc=document.getElementById('toc'), mb=document.querySelector('.menu-btn');
if(mb) mb.addEventListener('click',function(){ toc.classList.toggle('open'); });
toc.addEventListener('click',function(e){ if(e.target.tagName==='A'&&innerWidth<=1000) toc.classList.remove('open'); });

// Scroll-spy on chapters.
var links={}, secs=[].slice.call(document.querySelectorAll('.chapter'));
[].forEach.call(toc.querySelectorAll('a[href^="#"]'),function(a){ links[a.getAttribute('href').slice(1)]=a; });
var io=new IntersectionObserver(function(es){
  es.forEach(function(en){
    var a=links[en.target.id]; if(!a) return;
    if(en.isIntersecting){
      for(var k in links) links[k].classList.remove('active');
      a.classList.add('active');
      if(a.scrollIntoView) a.scrollIntoView({block:'nearest'});
    }
  });
},{rootMargin:'-70px 0px -75% 0px'});
secs.forEach(function(s){ io.observe(s); });

// Evidence matrix: expand + filter.
var mxWrap=document.getElementById('mx-list');
if(mxWrap){
  mxWrap.addEventListener('click',function(e){
    var h=e.target.closest('.mx-head'); if(h) h.parentNode.classList.toggle('open');
  });
  var q=document.getElementById('mx-q'), f=document.getElementById('mx-f');
  function filt(){
    var s=(q.value||'').toLowerCase(), c=f.value, n=0;
    [].forEach.call(mxWrap.querySelectorAll('.mx-card'),function(el){
      var okc = !c || el.dataset.cls===c;
      var oks = !s || el.textContent.toLowerCase().indexOf(s)>-1;
      var show = okc&&oks; el.style.display = show?'':'none'; if(show) n++;
    });
    document.getElementById('mx-count').textContent = n+' of '+mxWrap.querySelectorAll('.mx-card').length+' claims';
  }
  q.addEventListener('input',filt); f.addEventListener('change',filt); filt();
}

// Print: expand every matrix card so nothing is hidden in the PDF.
window.addEventListener('beforeprint',function(){
  [].forEach.call(document.querySelectorAll('.mx-card'),function(c){ c.classList.add('open'); });
});
"""


def matrix_section(rows):
    if not rows:
        return ""
    tagcol = {"ESTABLISHED FACT": "var(--fact)", "HISTORICAL CONTEXT": "var(--context)",
              "INVESTIGATIVE LEAD": "var(--lead)", "OPEN QUESTION": "var(--open)"}
    cards = []
    for r in rows:
        cls = r.get("classification", "").strip()
        col = tagcol.get(cls, "var(--limit)")
        def esc(k):
            return html.escape(r.get(k, "") or "—")
        cards.append(f"""
<div class="mx-card" data-cls="{html.escape(cls)}">
  <div class="mx-head">
    <span class="mx-id">{esc('claim_id')}</span>
    <span class="mx-claim">{esc('claim')}</span>
    <span class="mx-tag" style="background:{col}">{html.escape(cls.split()[0] if cls else '—')}</span>
  </div>
  <div class="mx-body"><dl>
    <dt>Classification</dt><dd>{esc('classification')} &middot; confidence {esc('confidence')}</dd>
    <dt>Supporting evidence</dt><dd>{esc('supporting_evidence')}</dd>
    <dt>Limiting or contradictory evidence</dt><dd>{esc('counter_evidence')}</dd>
    <dt>Citation</dt><dd>{esc('citation')}</dd>
    <dt>Status</dt><dd>{esc('status')} &middot; added {esc('date_added')}</dd>
  </dl></div>
</div>""")
    opts = "".join(f'<option value="{html.escape(c)}">{html.escape(c.title())}</option>'
                   for c in sorted({r.get("classification", "") for r in rows} - {""}))
    return f"""
<div class="mx-tools">
  <input id="mx-q" type="search" placeholder="Search claims, evidence, citations&hellip;" aria-label="Search evidence matrix">
  <select id="mx-f" aria-label="Filter by classification"><option value="">All classifications</option>{opts}</select>
</div>
<p class="cap-m" id="mx-count" style="font-family:var(--sans);font-size:12.5px;color:var(--ink-faint)"></p>
<div id="mx-list">{''.join(cards)}</div>
"""


def build():
    chapters = load_chapters()
    rows = load_matrix()

    # Table of contents.
    toc_items = []
    for c in chapters:
        subs = "".join(f'<li><a href="#{s}">{html.escape(t)}</a></li>' for s, t in c["subs"][:9])
        sub_html = f'<ul class="sub">{subs}</ul>' if subs else ""
        toc_items.append(
            f'<li><a href="#{c["slug"]}">'
            f'<span class="n">{int(c["num"])}.</span>{html.escape(c["title"])}</a>{sub_html}</li>')
    if rows:
        toc_items.append('<li><a href="#evidence-matrix">Evidence Matrix</a></li>')

    body_html = []
    for c in chapters:
        body_html.append(f"""
<section class="chapter" id="{c['slug']}">
  <div class="wrap">
    <div class="chapter-num">Chapter {int(c['num'])}</div>
    <h1>{html.escape(c['title'])}</h1>
    {c['html']}
  </div>
</section>""")

    if rows:
        body_html.append(f"""
<section class="chapter" id="evidence-matrix">
  <div class="wrap">
    <div class="chapter-num">Evidence</div>
    <h1>Evidence Matrix</h1>
    <p>Every substantive claim in this investigation, with its classification, confidence,
    supporting sources, and — mandatorily — its limiting or contradictory evidence. Select a
    claim to expand it. The counter-evidence field is never left blank: where a claim has no
    meaningful counter-evidence, that is stated explicitly.</p>
    {matrix_section(rows)}
  </div>
</section>""")

    # Wrap bare tables for horizontal scroll on narrow screens.
    doc_body = "".join(body_html)
    doc_body = re.sub(r"<table>", '<div class="tw"><table>', doc_body)
    doc_body = re.sub(r"</table>", "</table></div>", doc_body)

    n_fact = sum(1 for r in rows if r.get("classification") == "ESTABLISHED FACT")
    n_open = sum(1 for r in rows if r.get("classification") == "OPEN QUESTION")

    doc = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Ladera Ranch &mdash; Historical Environmental Investigation</title>
<meta name="description" content="An independent historical land-use and environmental records investigation of Rancho Mission Viejo and present-day Ladera Ranch, Orange County, California.">
<style>{CSS}</style>
</head>
<body>
<div class="topbar">
  <button class="menu-btn" aria-label="Toggle contents">&#9776;</button>
  <span class="brand">Ladera Historical Environmental Investigation</span>
  <span class="spacer"></span>
  <button onclick="window.print()">Print / PDF</button>
</div>

<div class="layout">
<nav id="toc" aria-label="Table of contents">
  <h3>Contents</h3>
  <ol>{''.join(toc_items)}</ol>
</nav>

<main>
<header class="cover">
  <div class="inner">
    <p class="eyebrow">Independent Public-Records Investigation &middot; Version 1.0</p>
    <h1>The Ground Beneath Ladera Ranch</h1>
    <p class="deck">A historical land-use and environmental records investigation of Rancho
    Mission Viejo and the community built on it &mdash; what the public record shows, what it
    does not, and what remains genuinely unknown.</p>
    <div class="meta">
      <span>Orange County, California</span>
      <span>Land-use record: 1769&ndash;2026</span>
      <span>Photographic record: 1929&ndash;2022</span>
      <span>{len(rows)} catalogued claims</span>
      <span>{n_fact} established &middot; {n_open} open</span>
    </div>
    <div class="disclaimer">
      <p><strong>This publication does not establish that any pesticide, property,
      organization, employer, school, water provider, government agency, or other party caused
      any illness.</strong> It is an independent research and data-organization project. It does
      not provide medical advice. Publicly reported health events may not have been
      independently medically verified. Geographic and temporal overlap does not establish
      exposure or causation.</p>
      <p style="margin-bottom:0">Formal conclusions would require authorized epidemiological
      analysis, verified medical information, exposure assessment, toxicological review, and
      independent scientific evaluation &mdash; none of which this project performs. It contains
      no patient information, no residential addresses, and no case locations.</p>
    </div>
  </div>
</header>

{doc_body}

<footer>
  <p><strong>Ladera Historical Environmental Investigation</strong> &mdash; Version 1.0.
  An independent, hypothesis-neutral research project. Sources are graded A1&ndash;D; a lower
  grade is never silently promoted. Corrections are issued openly and retained in the version
  history rather than quietly revised.</p>
  <p>No patient locations, residential addresses, or identifying details of any child or family
  appear anywhere in this publication, by permanent policy of the project.</p>
</footer>
</main>
</div>

<div id="lb" role="dialog" aria-modal="true" aria-label="Enlarged image">
  <button class="x" aria-label="Close">&times;</button><img alt="">
</div>
<script>{JS}</script>
</body>
</html>"""

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(doc)

    size = os.path.getsize(OUT) / 1024
    print(f"Built {OUT}")
    print(f"  {len(chapters)} chapters, {len(rows)} evidence claims, {size:.0f} KB")
    for c in chapters:
        words = len(re.sub(r"<[^>]+>", " ", c["html"]).split())
        print(f"    ch{c['num']}  {words:>5,} words  {c['title'][:56]}")
    total = sum(len(re.sub(r"<[^>]+>", " ", c["html"]).split()) for c in chapters)
    print(f"  total {total:,} words (~{total/450:.0f} publication pages)")
    return 0


if __name__ == "__main__":
    sys.exit(build())
