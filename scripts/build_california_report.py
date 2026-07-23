#!/usr/bin/env python3
"""Build The California Report: sectioned HTML (index + one page per chapter, cross-linked,
self-contained with embedded downscaled figures) + a single print HTML for the PDF.
Chapters: docs/california/chapters/*.md (NN_slug.md, ordered by NN)."""
import os, re, glob, base64, io, shutil, markdown
from PIL import Image
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CH=os.path.join(ROOT,"docs/california/chapters")
OUTD=os.path.join(ROOT,"docs/california"); os.makedirs(OUTD,exist_ok=True)
ASSETS=os.path.join(OUTD,"assets")
# Canonical production origin (custom domain; apex 308-redirects to www).
SITE="https://www.californiasforgottenpast.org"
OGIMG=SITE+"/share-card.jpg"

CSS="""
:root{--paper:#f7f5f0;--ink:#16233a;--ink2:#48586c;--line:#ddd7ca;--accent:#2f6087;--brass:#a97e1f}
*{box-sizing:border-box}body{margin:0;background:#e9e6df;color:var(--ink);font:15.5px/1.55 -apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
.page{max-width:900px;margin:22px auto;background:var(--paper);padding:44px 54px;box-shadow:0 2px 18px rgba(20,35,58,.12);border-radius:4px}
h1{font-family:Georgia,serif;font-size:30px;margin:.2em 0 .1em;letter-spacing:-.01em}
.subtitle{font-family:Georgia,serif;font-style:italic;font-size:19px;color:var(--ink2);margin:0 0 16px}
h2{font-family:Georgia,serif;font-size:19px;border-bottom:2px solid var(--brass);padding-bottom:4px;margin:26px 0 8px}
h3{font-size:15px;color:var(--accent);margin:16px 0 4px}
p{margin:7px 0}blockquote{border-left:3px solid var(--brass);background:#f4ecd6;margin:12px 0;padding:8px 14px;font-size:13px;color:#5a4a2c;border-radius:0 6px 6px 0}
table{border-collapse:collapse;width:100%;margin:10px 0;font-size:13.5px}
th,td{border:1px solid var(--line);padding:6px 9px;text-align:left;vertical-align:top}th{background:#efe9dc}
img{max-width:100%;border:1px solid var(--line);border-radius:6px;margin:8px 0}
code{background:#efe9dc;padding:1px 5px;border-radius:4px;font-size:12.5px}
ul,ol{margin:6px 0;padding-left:22px}li{margin:4px 0}
.nav{display:flex;justify-content:space-between;gap:10px;font-size:13px;margin:18px 0 0}
.nav a{color:var(--accent);text-decoration:none;border:1px solid var(--line);border-radius:6px;padding:6px 12px;background:#fff}
.crumb{font-size:12px;color:#7c8a9c;margin-bottom:6px}.crumb a{color:var(--accent);text-decoration:none}
.toc a{color:var(--accent);text-decoration:none}.toc li{margin:5px 0}
.foot{margin-top:22px;border-top:1px solid var(--line);padding-top:10px;color:var(--ink2);font-size:11px}
@media print{body{background:#fff}.page{box-shadow:none;margin:0;max-width:none;padding:.45in .6in}.nav,.crumb{display:none}h1{page-break-before:always}h2{page-break-after:avoid}img{max-height:6.2in}}
"""
FOOT=("Independent research & data-organization project. No medical advice; no causation established; "
      "geographic and temporal overlap does not establish exposure or causation. No CA dip-site soil has been tested. "
      "Source grades A1-D per chapter 73; registry: research/source_registry/sources.csv.")

def b64img(path,maxw=1080,q=68):
    im=Image.open(path); im=im.convert("RGB")
    if im.width>maxw: im=im.resize((maxw,int(im.height*maxw/im.width)))
    buf=io.BytesIO(); im.save(buf,"JPEG",quality=q)
    return "data:image/jpeg;base64,"+base64.b64encode(buf.getvalue()).decode()

IMGPAT=re.compile(r'`((?:research|docs|media|evidence)/[^`]+?\.(?:jpg|png))`')
def embed_figures(md_text):
    """Replace `path/to/img.jpg` code-refs with embedded images + caption line."""
    def rep(m):
        p=os.path.join(ROOT,m.group(1))
        if os.path.exists(p):
            return f'![{os.path.basename(m.group(1))}]({b64img(p)})\n*{m.group(1)}*'
        return m.group(0)
    return IMGPAT.sub(rep,md_text)

def ext_img(relpath,maxw=1280,q=72):
    """Write an optimized external JPG for `relpath` into docs/california/assets/
    and return the report-relative URL. Keeps report.html text-light so images
    stream lazily instead of bloating the HTML with base64."""
    name=re.sub(r'[^A-Za-z0-9._-]','_',relpath)
    name=os.path.splitext(name)[0]+".jpg"
    out=os.path.join(ASSETS,name)
    im=Image.open(os.path.join(ROOT,relpath)).convert("RGB")
    if im.width>maxw: im=im.resize((maxw,int(im.height*maxw/im.width)))
    im.save(out,"JPEG",quality=q,optimize=True,progressive=True)
    return "assets/"+name

def ext_figures(md_text):
    """Like embed_figures, but references external optimized JPGs (for report.html)."""
    def rep(m):
        rel=m.group(1)
        if os.path.exists(os.path.join(ROOT,rel)):
            return f'![{os.path.basename(rel)}]({ext_img(rel)})\n*{rel}*'
        return m.group(0)
    return IMGPAT.sub(rep,md_text)

files=sorted(glob.glob(os.path.join(CH,"[0-9]*.md")))
chaps=[]
for f in files:
    raw=open(f).read()
    title=re.match(r'#\s*(.+)',raw)
    title=title.group(1).strip() if title else os.path.basename(f)
    slug=os.path.splitext(os.path.basename(f))[0]
    chaps.append((slug,title,raw))

# per-section pages
for i,(slug,title,raw) in enumerate(chaps):
    body=markdown.markdown(embed_figures(raw),extensions=["tables"])
    prev_=f'<a href="{chaps[i-1][0]}.html">← {chaps[i-1][1][:38]}</a>' if i>0 else '<span></span>'
    next_=f'<a href="{chaps[i+1][0]}.html">{chaps[i+1][1][:38]} →</a>' if i<len(chaps)-1 else '<span></span>'
    html=f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} · California's Forgotten Past</title><style>{CSS}</style></head><body><div class="page">
<div class="crumb"><a href="index.html">California's Forgotten Past</a> · section {i} of {len(chaps)-1}</div>
{body}
<div class="nav">{prev_}<a href="index.html">Contents</a>{next_}</div>
<div class="foot">{FOOT}</div></div></body></html>"""
    open(os.path.join(OUTD,f"{slug}.html"),"w").write(html)

# index
items="".join(f'<li><a href="{s}.html">{t}</a></li>' for s,t,_ in chaps)
idx=f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>California's Forgotten Past · The Arsenic Cattle-Dipping Era</title><style>{CSS}</style></head><body><div class="page">
<h1>California's Forgotten Past</h1>
<p class="subtitle">The Arsenic Cattle-Dipping Era</p>
<p>An independent, area-based investigation. Priority areas first. Each section is a self-contained page.</p>
<blockquote>{FOOT}</blockquote>
<h2>Contents</h2><ul class="toc">{items}</ul>
<p class="foot">Prefer one long page? Read <a href="report.html">the full report on a single page</a>.</p>
</div></body></html>"""
open(os.path.join(OUTD,"index.html"),"w").write(idx)

# single print HTML (for PDF)
allbody="".join(markdown.markdown(embed_figures(raw),extensions=["tables"]) for _,_,raw in chaps)
titleblock=("<div style=\"text-align:center;padding:1.7in 0 2.2in\">"
  "<div style=\"font-family:Georgia,serif;font-size:40px;color:#16233a;letter-spacing:-.01em\">California's Forgotten Past</div>"
  "<div style=\"font-family:Georgia,serif;font-style:italic;font-size:22px;color:#48586c;margin-top:10px\">The Arsenic Cattle-Dipping Era</div>"
  "<div style=\"width:60px;border-top:2px solid #a97e1f;margin:22px auto\"></div>"
  "<div style=\"font-size:13px;color:#7c8a9c\">An independent research &amp; data-organization project</div></div>")
print_html=f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><title>California's Forgotten Past · The Arsenic Cattle-Dipping Era</title>
<style>{CSS}</style></head><body><div class="page">{titleblock}{allbody}<div class="foot">{FOOT}</div></div></body></html>"""
open(os.path.join(OUTD,"_print.html"),"w").write(print_html)

# single long-scroll report page (whole report, external lazy-loaded images)
shutil.rmtree(ASSETS,ignore_errors=True); os.makedirs(ASSETS,exist_ok=True)
REPORT_CSS="""
/* Match the landing page palette (blue accent), and support light + dark like it does. */
:root{--paper:#f7f5f0;--ink:#16233a;--ink2:#48586c;--line:#ddd7ca;--accent:#2f6087;--brass:#a97e1f;
  --brassbg:#f4ecd6;--card:#fffdf8;--mat:#e9e6df;--chip:#efe9dc;--quote:#5a4a2c;--muted:#7c8a9c;
  --barbg:rgba(247,245,240,.94);--shadow:0 2px 18px rgba(20,35,58,.12)}
@media (prefers-color-scheme:dark){:root{--paper:#141a24;--ink:#eef2f7;--ink2:#a9b6c6;--line:#2b3746;--accent:#7fb0d6;
  --brass:#d8b662;--brassbg:#20293a;--card:#1b2330;--mat:#0e131b;--chip:#202a38;--quote:#d7c8a4;--muted:#8493a6;
  --barbg:rgba(20,26,36,.92);--shadow:0 2px 20px rgba(0,0,0,.45)}}
:root[data-theme="light"]{--paper:#f7f5f0;--ink:#16233a;--ink2:#48586c;--line:#ddd7ca;--accent:#2f6087;--brass:#a97e1f;--brassbg:#f4ecd6;--card:#fffdf8;--mat:#e9e6df;--chip:#efe9dc;--quote:#5a4a2c;--muted:#7c8a9c;--barbg:rgba(247,245,240,.94);--shadow:0 2px 18px rgba(20,35,58,.12)}
:root[data-theme="dark"]{--paper:#141a24;--ink:#eef2f7;--ink2:#a9b6c6;--line:#2b3746;--accent:#7fb0d6;--brass:#d8b662;--brassbg:#20293a;--card:#1b2330;--mat:#0e131b;--chip:#202a38;--quote:#d7c8a4;--muted:#8493a6;--barbg:rgba(20,26,36,.92);--shadow:0 2px 20px rgba(0,0,0,.45)}
/* re-skin the shared base rules so they follow the theme and lead with blue */
body{background:var(--mat)}
.page{background:var(--paper);box-shadow:var(--shadow)}
a{color:var(--accent)}
h2{border-bottom-color:var(--accent)}
h3{color:var(--accent)}
blockquote{background:var(--brassbg);border-left-color:var(--accent);color:var(--quote)}
th{background:var(--chip)}
th,td{border-color:var(--line)}
img{border-color:var(--line)}
code{background:var(--chip);color:var(--ink)}
.foot{border-top-color:var(--line);color:var(--ink2)}
.topbar{position:sticky;top:0;z-index:50;display:flex;align-items:center;justify-content:space-between;gap:12px;
  background:var(--barbg);backdrop-filter:blur(7px);-webkit-backdrop-filter:blur(7px);
  border-bottom:1px solid var(--line);padding:9px clamp(14px,4vw,26px)}
.tb-title{font-family:Georgia,serif;font-weight:700;color:var(--ink);text-decoration:none;font-size:15px;
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis;min-width:0}
.tb-actions{display:flex;align-items:center;gap:16px;flex:0 0 auto}
.tb-link{color:var(--accent);text-decoration:none;font-size:13.5px;font-weight:700;white-space:nowrap}
.tb-link:hover{text-decoration:underline}
.hero{padding:8px 0 2px}
.eyebrow{font-size:12px;letter-spacing:.14em;text-transform:uppercase;color:var(--brass);font-weight:700;margin:0 0 10px}
.hero h1{font-size:clamp(28px,5.6vw,42px);line-height:1.08;margin:0 0 6px;border:0;color:var(--ink)}
.tagline{font-family:Georgia,serif;font-style:italic;font-size:clamp(17px,3vw,23px);color:var(--brass);margin:0 0 14px}
.hero .sub{color:var(--ink2);font-size:16.5px;max-width:62ch;margin:0 0 16px}
/* video slot: swap the .videobox for the real thumbnail/embed when ready */
.videobox{position:relative;width:100%;max-width:680px;aspect-ratio:16/9;margin:6px 0 16px;border-radius:12px;
  border:1px solid var(--line);background:linear-gradient(150deg,var(--card),var(--paper));
  display:flex;align-items:center;justify-content:center;overflow:hidden}
.videobox .glow{position:absolute;inset:0;background:radial-gradient(60% 55% at 50% 42%,rgba(47,96,135,.16),transparent 70%)}
.vb-inner{position:relative;text-align:center;padding:16px}
.vb-play{width:66px;height:66px;border-radius:50%;background:var(--accent);display:flex;align-items:center;
  justify-content:center;margin:0 auto 12px;box-shadow:0 6px 18px rgba(20,35,58,.28)}
.vb-play::after{content:"";border-style:solid;border-width:11px 0 11px 19px;
  border-color:transparent transparent transparent #fff;margin-left:5px}
.vb-label{color:var(--ink2);font-size:13px;font-weight:700;letter-spacing:.05em;text-transform:uppercase}
.hero-actions{display:flex;flex-wrap:wrap;gap:10px;margin:0 0 6px}
.hero-actions a{display:inline-flex;align-items:center;gap:7px;text-decoration:none;font-weight:600;font-size:14.5px;
  padding:10px 17px;border-radius:9px;border:1px solid var(--line);color:var(--ink);background:var(--card)}
.hero-actions a:hover{border-color:var(--accent)}
.hero-actions a.primary{background:var(--accent);border-color:var(--accent);color:#fff}
.disc{background:var(--brassbg);border:1px solid var(--line);border-left:3px solid var(--accent);border-radius:8px;
  padding:13px 16px;font-size:12.5px;color:var(--quote);margin:16px 0}
.disc b{color:var(--ink)}
.contents{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:12px 20px;margin:18px 0 8px}
.contents h2{border:0;margin:2px 0 8px;font-size:16px;color:var(--ink)}
.contents ol{columns:2;column-gap:28px;margin:0;padding-left:20px;font-size:14px}
.contents li{margin:5px 0;break-inside:avoid}
.contents a{color:var(--accent);text-decoration:none}
.contents a:hover{text-decoration:underline}
.chapter{scroll-margin-top:62px;border-top:1px solid var(--line);margin-top:30px;padding-top:8px}
.chapter:first-of-type{border-top:0;margin-top:10px}
.chapter h1{font-size:26px;page-break-before:auto;color:var(--ink)}
.fig-cap{color:var(--muted);font-size:11.5px;font-style:italic}
@media (max-width:600px){
  .page{margin:0;padding:22px 18px;border-radius:0;box-shadow:none}
  .contents ol{columns:1}
  .tb-title{max-width:56vw}
}
"""
secs=[]
for slug,title,raw in chaps:
    body=markdown.markdown(ext_figures(raw),extensions=["tables"])
    secs.append(f'<section id="{slug}" class="chapter">{body}</section>')
sections="".join(secs)
sections=sections.replace('<img ','<img loading="lazy" ')
# tag only image-provenance captions (the <em> right after an <img>), not body emphasis
sections=re.sub(r'(<img[^>]*>)\s*<em>',r'\1<br><em class="fig-cap">',sections)
contents="".join(f'<li><a href="#{s}">{t}</a></li>' for s,t,_ in chaps)
DESC=("An independent, hypothesis-neutral investigation into California's state-mandated arsenical "
      "cattle-tick dipping program (1907 to 1912) and the South Orange County communities built on the former ranch land.")
report_html=f"""<!doctype html><html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>California's Forgotten Past: The Arsenic Cattle-Dipping Era</title>
<meta name="description" content="{DESC}">
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" type="image/png" href="/favicon.png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<meta property="og:type" content="article">
<meta property="og:site_name" content="California's Forgotten Past">
<meta property="og:title" content="California's Forgotten Past: The Arsenic Cattle-Dipping Era">
<meta property="og:description" content="{DESC}">
<meta property="og:image" content="{OGIMG}">
<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta property="og:url" content="{SITE}/docs/california/report.html">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="California's Forgotten Past: The Arsenic Cattle-Dipping Era">
<meta name="twitter:description" content="{DESC}">
<meta name="twitter:image" content="{OGIMG}">
<style>{CSS}{REPORT_CSS}</style></head><body>
<div class="topbar">
  <a class="tb-title" href="#top">California's Forgotten Past</a>
  <div class="tb-actions">
    <a class="tb-link" href="#contents">Contents</a>
    <a class="tb-link" href="/contact.html">Contact</a>
  </div>
</div>
<div class="page" id="top">
  <div class="hero">
    <p class="eyebrow">Independent research &amp; data-organization project</p>
    <h1>California's Forgotten Past</h1>
    <p class="tagline">The Arsenic Cattle-Dipping Era</p>
    <p class="sub">{DESC}</p>
    <!-- VIDEO: replace this .videobox with the real thumbnail or embed when the video is ready,
         e.g. <a href="VIDEO_URL"><img src="/path/to/thumbnail.jpg" alt="Watch the documentary"></a> -->
    <div class="videobox" role="img" aria-label="Documentary video coming soon">
      <span class="glow"></span>
      <div class="vb-inner">
        <div class="vb-play"></div>
        <div class="vb-label">Documentary video coming soon</div>
      </div>
    </div>
    <div class="hero-actions">
      <a href="#contents">Jump to contents</a>
      <a href="index.html">Section-by-section view</a>
      <a href="/contact.html">Contact</a>
    </div>
  </div>
  <div class="disc"><b>This is an independent research and data-organization project. It does not provide
    medical advice and does not establish that any pesticide, property, organization, school, water provider,
    agency, or other party caused any illness.</b> Arsenic is not a known cause of Ewing sarcoma. Publicly
    reported health events may not have been independently medically verified. Geographic and temporal overlap
    does not establish exposure or causation. No dip-site soil has been tested and no contamination is asserted
    for any community named here.</div>
  <nav class="contents" id="contents"><h2>Contents</h2><ol>{contents}</ol></nav>
  {sections}
  <div class="foot">{FOOT}</div>
</div></body></html>"""
open(os.path.join(OUTD,"report.html"),"w").write(report_html)

# sitemap.xml + robots.txt at the site root (for search engines / social crawlers)
urls=[("/",1.0),("/docs/california/report.html",0.9),("/docs/california/index.html",0.7),
      ("/contact.html",0.6)]
urls+=[(f"/docs/california/{s}.html",0.5) for s,_,_ in chaps]
sm=['<?xml version="1.0" encoding="UTF-8"?>','<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
sm+=[f'  <url><loc>{SITE}{u}</loc><changefreq>monthly</changefreq><priority>{p}</priority></url>' for u,p in urls]
sm+=['</urlset>','']
open(os.path.join(ROOT,"sitemap.xml"),"w").write("\n".join(sm))
open(os.path.join(ROOT,"robots.txt"),"w").write(f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n")

nimg=len(glob.glob(os.path.join(ASSETS,"*.jpg")))
print("built",len(chaps),"sections + index + _print.html + report.html (",nimg,"external assets ) + sitemap + robots")
