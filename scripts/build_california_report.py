#!/usr/bin/env python3
"""Build The California Report: sectioned HTML (index + one page per chapter, cross-linked,
self-contained with embedded downscaled figures) + a single print HTML for the PDF.
Chapters: docs/california/chapters/*.md (NN_slug.md, ordered by NN)."""
import os, re, glob, base64, io, markdown
from PIL import Image
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CH=os.path.join(ROOT,"docs/california/chapters")
OUTD=os.path.join(ROOT,"docs/california"); os.makedirs(OUTD,exist_ok=True)

CSS="""
:root{--paper:#f7f5f0;--ink:#16233a;--ink2:#48586c;--line:#ddd7ca;--accent:#2f6087;--brass:#a97e1f}
*{box-sizing:border-box}body{margin:0;background:#e9e6df;color:var(--ink);font:15.5px/1.55 -apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
.page{max-width:900px;margin:22px auto;background:var(--paper);padding:44px 54px;box-shadow:0 2px 18px rgba(20,35,58,.12);border-radius:4px}
h1{font-family:Georgia,serif;font-size:27px;margin:.2em 0 .4em}
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
      "Source grades A1–D per chapter 73; registry: research/source_registry/sources.csv.")

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
<title>{title} — The California Report</title><style>{CSS}</style></head><body><div class="page">
<div class="crumb"><a href="index.html">The California Report</a> · section {i} of {len(chaps)-1}</div>
{body}
<div class="nav">{prev_}<a href="index.html">Contents</a>{next_}</div>
<div class="foot">{FOOT}</div></div></body></html>"""
    open(os.path.join(OUTD,f"{slug}.html"),"w").write(html)

# index
items="".join(f'<li><a href="{s}.html">{t}</a></li>' for s,t,_ in chaps)
idx=f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>The California Report — contents</title><style>{CSS}</style></head><body><div class="page">
<h1>The Arsenic Under the Master Plan — a California investigation</h1>
<p>Condensed, area-based report. Priority areas first. Each section is a self-contained page.</p>
<blockquote>{FOOT}</blockquote>
<h2>Contents</h2><ul class="toc">{items}</ul>
<p class="foot">Also available as a single PDF: <a href="California_Report.pdf">California_Report.pdf</a></p>
</div></body></html>"""
open(os.path.join(OUTD,"index.html"),"w").write(idx)

# single print HTML (for PDF)
allbody="".join(markdown.markdown(embed_figures(raw),extensions=["tables"]) for _,_,raw in chaps)
print_html=f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><title>The California Report</title>
<style>{CSS}</style></head><body><div class="page">{allbody}<div class="foot">{FOOT}</div></div></body></html>"""
open(os.path.join(OUTD,"_print.html"),"w").write(print_html)
print("built",len(chaps),"sections + index + _print.html")
