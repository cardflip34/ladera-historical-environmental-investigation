#!/usr/bin/env python3
"""Build the standalone statewide gallery/findings page served alongside the main report.

Assembles three things the main report references but does not display in full:
  1. the statewide context map (FIG-29),
  2. the complete 11-community review-gap ranking, and
  3. a provenance-graded gallery of every rights-clean image located in the archival hunt.

All content is hypothesis-neutral: the page states, repeatedly, that no community is
asserted to be contaminated and that no dip vat appears in any image. Output:
docs/publication/statewide.html (served by the same local server / tunnel as index.html).
"""
import json, html, os
from collections import OrderedDict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
M = json.load(open("/tmp/manifest.json"))
OUT = os.path.join(ROOT, "docs/publication/statewide.html")

def esc(s): return html.escape(str(s or ""))

# ---- ranch metadata (id -> label, county, region, residential?) --------------
RANCH = OrderedDict([
 ("T01-TRABUCO",       dict(name="Rancho Trabuco", county="Orange", region="Coto de Caza · Trabuco Canyon · south Orange County", res=True)),
 ("T02-IRVINE",        dict(name="Irvine Ranch", county="Orange", region="Irvine · Tustin · Newport Coast", res=True)),
 ("T03-SIMI",          dict(name="Rancho Simi", county="Ventura", region="Simi Valley", res=True)),
 ("T05-SANBERNARDO",   dict(name="Rancho San Bernardo", county="San Diego", region="Rancho Bernardo · Escondido", res=True)),
 ("T07-SESPE",         dict(name="Rancho Sespe", county="Ventura", region="Fillmore · Sespe", res=True)),
 ("T08-NEWHALL",       dict(name="Rancho San Francisco / Newhall Ranch", county="Los Angeles", region="Santa Clarita · Valencia · Newhall", res=True)),
 ("T10-LOSALAMITOS",   dict(name="Rancho Los Alamitos", county="Los Angeles", region="Long Beach · Los Alamitos", res=True)),
 ("T11-CUCAMONGA",     dict(name="Rancho Cucamonga", county="San Bernardino", region="Rancho Cucamonga", res=True)),
 ("T12-JURUPA",        dict(name="Rancho Jurupa", county="Riverside", region="Riverside · Jurupa Valley", res=True)),
 ("T13-SANTAMARGARITA",dict(name="Rancho Santa Margarita y Las Flores", county="San Diego", region="Camp Pendleton · San Onofre — federal land, NOT the Orange County city of the same name", res=False)),
 ("T14-TEJON",         dict(name="Tejon Ranch", county="Kern", region="Tejon · Lebec — largely unbuilt ranch land", res=False)),
 ("T15-MILLERLUX",     dict(name="Miller & Lux", county="Fresno", region="Los Baños · San Joaquin Valley — irrigated farmland", res=False)),
])

# ---- the complete ranking (from STATEWIDE_RANKING.md) -------------------------
RANK = [
 (1,"High","Rancho Bernardo, Poway edge","heavy","NEVER reviewed (pre-CEQA)","no vat named","never"),
 (2,"High","Rancho Santa Fe, Del Mar, Solana Beach","heavy","~34 yr","no vat named","wide"),
 (3,"High","Rancho Peñasquitos, Mira Mesa, Carmel Valley","heavy","~27 yr","no vat named","wide"),
 (4,"High","Coto de Caza, Wagon Wheel, Trabuco Canyon","heavy","~26 yr","no vat named","wide"),
 (5,"High","Irvine, Tustin, Newport Coast, Lake Forest","heavy","~26 yr","no vat named","wide"),
 (6,"Medium","Simi Valley, Moorpark edge","heavy","~15 yr","no vat named","mod"),
 (7,"Medium","Rancho Cucamonga","lesser","~26 yr","no vat named","wide"),
 (8,"Medium","Riverside, Jurupa Valley","lesser","~19 yr","no vat named","mod"),
 (9,"Medium","Long Beach, Los Alamitos, Rossmoor, Seal Beach","lesser","~16 yr","no vat named","mod"),
 (10,"Medium","Santa Clarita, Valencia, Newhall, Saugus","lesser","~15 yr","no vat named","mod"),
 (11,"Medium","Long Beach, Lakewood, Cerritos, Bellflower","lesser","~15 yr","sheep dip attested (chemistry unknown)","mod"),
]

CAT_LABEL = {"photo":"Photograph","map":"Map / diseño","document":"Survey / HABS","artifact":"Artifact","other":"Item"}

# group images by ranch, ordering photos first within each ranch
imgs = M["images"]
by = OrderedDict((tid, []) for tid in RANCH)
for it in imgs:
    by.setdefault(it["tid"], []).append(it)
catorder = {"photo":0,"artifact":1,"document":2,"map":3,"other":4}
for tid in by:
    by[tid].sort(key=lambda x: catorder.get(x.get("cat"),9))

n_photo = sum(1 for it in imgs if it.get("cat")=="photo")
n_map   = sum(1 for it in imgs if it.get("cat")=="map")
n_other = len(imgs) - n_photo - n_map

# ---- HTML -------------------------------------------------------------------
def rank_rows():
    out=[]
    tone={"never":"gap-never","wide":"gap-wide","mod":"gap-mod"}
    for rk,pri,comm,tier,gap,dip,g in RANK:
        pc = "pri-high" if pri=="High" else "pri-med"
        out.append(f"""<tr>
<td class="rk">{rk}</td>
<td><span class="pill {pc}">{esc(pri)}</span></td>
<td class="comm">{esc(comm)}</td>
<td><span class="tier tier-{tier}">{esc(tier)}</span></td>
<td><span class="gapcell {tone[g]}">{esc(gap)}</span></td>
<td class="dip">{esc(dip)}</td>
</tr>""")
    return "\n".join(out)

def gallery():
    blocks=[]
    for tid,meta in RANCH.items():
        items=by.get(tid,[])
        if not items: continue
        badge = '<span class="rbadge rbadge-res">residential today</span>' if meta["res"] \
                else '<span class="rbadge rbadge-non">federal / farm / unbuilt today</span>'
        tiles=[]
        for it in items:
            cap_bits=[]
            if it.get("date"): cap_bits.append(esc(it["date"]))
            if it.get("repo"): cap_bits.append(esc(it["repo"]))
            meta_line=" · ".join(cap_bits)
            tiles.append(f"""<figure class="tile" tabindex="0"
  data-full="{esc(it['view'])}" data-title="{esc(it['title'])}"
  data-meta="{esc(CAT_LABEL.get(it.get('cat'),'Item'))} · {esc(it.get('date'))} · {esc(it.get('repo'))}"
  data-depicts="{esc(it.get('depicts'))}" data-rights="{esc(it.get('rights'))}">
  <div class="thumbwrap"><img loading="lazy" src="{esc(it['thumb'])}" alt="{esc(it['title'])}"></div>
  <figcaption>
    <span class="cat cat-{esc(it.get('cat','other'))}">{esc(CAT_LABEL.get(it.get('cat'),'Item'))}</span>
    <span class="ttl">{esc(it['title'][:90])}</span>
    <span class="src">{meta_line}</span>
  </figcaption>
</figure>""")
        blocks.append(f"""<section class="ranch">
  <div class="ranch-head">
    <h3>{esc(meta['name'])} {badge}</h3>
    <p class="ranch-sub">{esc(meta['county'])} County — {esc(meta['region'])} · {len(items)} item{'s' if len(items)!=1 else ''}</p>
  </div>
  <div class="grid">{''.join(tiles)}</div>
</section>""")
    return "\n".join(blocks)

DISCLAIMER = ("This platform is an independent research and data-organization project. It does not "
 "provide medical advice and does not establish that any pesticide, property, organization, employer, "
 "school, water provider, government agency, or other party caused any illness. Publicly reported health "
 "events may not have been independently medically verified. Geographic and temporal overlap does not "
 "establish exposure or causation. Formal conclusions require authorized epidemiological analysis, verified "
 "medical information, exposure assessment, toxicological review, and independent scientific evaluation.")

page=f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>The General Case — Statewide Screening &amp; Archive · LEHRP</title>
<style>
:root{{
 --paper:#f6f4ef; --card:#fffefb; --ink:#14243a; --ink2:#42566e; --ink3:#6b7c90;
 --line:#ded8ca; --line2:#ebe6da; --accent:#2f6087; --accent-soft:#e7eef4;
 --brass:#a97e1f; --brass-soft:#f3ead2; --amber:#b06a1c;
 --photo:#2f6087; --map:#3d7a63; --doc:#6b6f78; --artifact:#a97e1f;
 --shadow:0 1px 2px rgba(20,36,58,.06),0 6px 20px rgba(20,36,58,.06);
}}
@media (prefers-color-scheme:dark){{
 :root{{ --paper:#0d1420; --card:#141d2b; --ink:#e9ecf2; --ink2:#aab6c6; --ink3:#7f8 da0;
 --ink3:#7f8da0; --line:#26313f; --line2:#1d2734; --accent:#6fa9d6; --accent-soft:#182634;
 --brass:#d6b25a; --brass-soft:#241f14; --amber:#d78a44; --photo:#6fa9d6; --map:#67b199;
 --doc:#9aa2ad; --artifact:#d6b25a; --shadow:0 1px 2px rgba(0,0,0,.3),0 8px 24px rgba(0,0,0,.35);}}
}}
:root[data-theme="dark"]{{ --paper:#0d1420; --card:#141d2b; --ink:#e9ecf2; --ink2:#aab6c6;
 --line:#26313f; --line2:#1d2734; --accent:#6fa9d6; --accent-soft:#182634; --brass:#d6b25a;
 --brass-soft:#241f14; --amber:#d78a44; --photo:#6fa9d6; --map:#67b199; --doc:#9aa2ad;
 --artifact:#d6b25a; --shadow:0 1px 2px rgba(0,0,0,.3),0 8px 24px rgba(0,0,0,.35);}}
:root[data-theme="light"]{{ --paper:#f6f4ef; --card:#fffefb; --ink:#14243a; --ink2:#42566e;
 --line:#ded8ca; --line2:#ebe6da; --accent:#2f6087; --accent-soft:#e7eef4; --brass:#a97e1f;
 --brass-soft:#f3ead2; --amber:#b06a1c; --photo:#2f6087; --map:#3d7a63; --doc:#6b6f78;
 --artifact:#a97e1f; --shadow:0 1px 2px rgba(20,36,58,.06),0 6px 20px rgba(20,36,58,.06);}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--paper);color:var(--ink);
 font:16px/1.62 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
 -webkit-text-size-adjust:100%;}}
.serif{{font-family:"Iowan Old Style",Georgia,"Times New Roman",serif;}}
.wrap{{max-width:1080px;margin:0 auto;padding:0 20px;}}
a{{color:var(--accent);text-underline-offset:2px;}}
/* header */
header.top{{border-bottom:1px solid var(--line);background:linear-gradient(180deg,var(--card),var(--paper));}}
.eyebrow{{font-size:12.5px;letter-spacing:.14em;text-transform:uppercase;color:var(--accent);font-weight:600;margin:0 0 10px;}}
h1{{font-family:"Iowan Old Style",Georgia,serif;font-weight:600;font-size:clamp(28px,5vw,44px);
 line-height:1.12;margin:0 0 12px;text-wrap:balance;letter-spacing:-.01em;}}
.lede{{font-size:clamp(16px,2.3vw,19px);color:var(--ink2);max-width:64ch;margin:0 0 4px;}}
.topmeta{{display:flex;flex-wrap:wrap;gap:8px;margin:20px 0 4px;}}
.stat{{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:8px 13px;font-size:13px;color:var(--ink2);}}
.stat b{{color:var(--ink);font-variant-numeric:tabular-nums;font-size:15px;}}
.crumbs{{display:flex;gap:14px;flex-wrap:wrap;font-size:13.5px;padding:14px 0;}}
.crumbs a{{text-decoration:none;font-weight:500;}}
/* disclaimer strip */
.disc{{background:var(--brass-soft);border:1px solid var(--line);border-left:3px solid var(--brass);
 border-radius:8px;padding:13px 16px;margin:18px 0;font-size:13.5px;color:var(--ink2);}}
.disc b{{color:var(--ink);}}
section.band{{padding:38px 0;border-bottom:1px solid var(--line2);}}
h2{{font-family:"Iowan Old Style",Georgia,serif;font-size:clamp(21px,3.4vw,28px);font-weight:600;
 margin:0 0 6px;letter-spacing:-.01em;}}
.sub{{color:var(--ink2);margin:0 0 22px;max-width:70ch;}}
/* map */
.mapfig{{margin:0;border:1px solid var(--line);border-radius:14px;overflow:hidden;background:var(--card);box-shadow:var(--shadow);}}
.mapfig img{{width:100%;display:block;height:auto;cursor:zoom-in;}}
.mapfig figcaption{{padding:12px 16px;font-size:13px;color:var(--ink2);border-top:1px solid var(--line2);}}
/* table */
.tablewrap{{overflow-x:auto;border:1px solid var(--line);border-radius:12px;background:var(--card);box-shadow:var(--shadow);}}
table{{border-collapse:collapse;width:100%;min-width:640px;font-size:14px;}}
thead th{{text-align:left;font-size:11.5px;letter-spacing:.06em;text-transform:uppercase;color:var(--ink3);
 font-weight:600;padding:12px 14px;border-bottom:1px solid var(--line);white-space:nowrap;}}
tbody td{{padding:12px 14px;border-bottom:1px solid var(--line2);vertical-align:middle;}}
tbody tr:last-child td{{border-bottom:none;}}
.rk{{font-variant-numeric:tabular-nums;color:var(--ink3);font-weight:600;width:34px;}}
.comm{{font-weight:500;min-width:220px;}}
.dip{{color:var(--ink2);font-size:13px;}}
.pill{{display:inline-block;padding:2px 10px;border-radius:20px;font-size:12px;font-weight:600;white-space:nowrap;}}
.pri-high{{background:var(--accent-soft);color:var(--accent);border:1px solid var(--accent);}}
.pri-med{{background:transparent;color:var(--ink2);border:1px solid var(--line);}}
.tier{{font-size:12px;color:var(--ink2);}}
.tier-heavy{{color:var(--amber);font-weight:600;}}
.gapcell{{font-weight:600;font-variant-numeric:tabular-nums;white-space:nowrap;}}
.gap-never{{color:var(--amber);}} .gap-wide{{color:var(--brass);}} .gap-mod{{color:var(--ink2);}}
.note{{font-size:13px;color:var(--ink2);margin-top:14px;display:flex;gap:8px;align-items:flex-start;}}
.note::before{{content:"▲";color:var(--brass);font-size:10px;margin-top:4px;}}
/* gallery */
.ranch{{margin:0 0 30px;}}
.ranch-head h3{{font-family:"Iowan Old Style",Georgia,serif;font-size:19px;font-weight:600;margin:0 0 3px;display:flex;flex-wrap:wrap;gap:10px;align-items:baseline;}}
.ranch-sub{{color:var(--ink3);font-size:13px;margin:0 0 14px;}}
.rbadge{{font-size:11px;font-weight:600;padding:2px 9px;border-radius:20px;letter-spacing:.02em;}}
.rbadge-res{{background:var(--accent-soft);color:var(--accent);}}
.rbadge-non{{background:var(--brass-soft);color:var(--brass);}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(210px,1fr));gap:16px;}}
.tile{{margin:0;background:var(--card);border:1px solid var(--line);border-radius:12px;overflow:hidden;
 cursor:zoom-in;box-shadow:var(--shadow);transition:transform .12s ease,box-shadow .12s ease;outline:none;}}
.tile:hover,.tile:focus{{transform:translateY(-2px);box-shadow:0 4px 12px rgba(20,36,58,.14),0 12px 30px rgba(20,36,58,.12);border-color:var(--accent);}}
.thumbwrap{{aspect-ratio:4/3;background:var(--line2);overflow:hidden;display:flex;align-items:center;justify-content:center;}}
.thumbwrap img{{width:100%;height:100%;object-fit:cover;display:block;}}
figcaption{{padding:10px 12px 12px;display:flex;flex-direction:column;gap:4px;}}
.cat{{align-self:flex-start;font-size:10.5px;font-weight:700;letter-spacing:.05em;text-transform:uppercase;padding:1px 7px;border-radius:5px;color:#fff;}}
.cat-photo{{background:var(--photo);}} .cat-map{{background:var(--map);}} .cat-document{{background:var(--doc);}} .cat-artifact{{background:var(--artifact);}} .cat-other{{background:var(--doc);}}
.ttl{{font-size:13px;line-height:1.35;color:var(--ink);font-weight:500;}}
.src{{font-size:11.5px;color:var(--ink3);}}
/* lightbox */
.lb{{position:fixed;inset:0;background:rgba(8,12,18,.92);display:none;align-items:center;justify-content:center;
 z-index:100;padding:22px;flex-direction:column;}}
.lb.open{{display:flex;}}
.lb img{{max-width:100%;max-height:72vh;border-radius:8px;box-shadow:0 20px 60px rgba(0,0,0,.6);}}
.lb .cap{{color:#e9ecf2;max-width:760px;margin-top:16px;font-size:13.5px;line-height:1.55;text-align:center;}}
.lb .cap .lbt{{font-weight:600;font-size:15px;display:block;margin-bottom:4px;}}
.lb .cap .lbm{{color:#9fb0c2;}}
.lb .cap .lbr{{color:#7f8da0;font-size:12px;margin-top:6px;display:block;}}
.lb .x{{position:absolute;top:16px;right:20px;color:#cfd8e2;font-size:30px;cursor:pointer;line-height:1;background:none;border:none;}}
.lb a.open-src{{color:#8fc0e8;font-size:12.5px;margin-top:8px;display:inline-block;}}
/* footer */
footer{{padding:34px 0 60px;color:var(--ink3);font-size:12.5px;}}
footer .fdisc{{border-top:1px solid var(--line);padding-top:18px;max-width:78ch;}}
@media (max-width:560px){{ .grid{{grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:12px;}} }}
</style>
</head>
<body>

<header class="top">
 <div class="wrap">
  <div class="crumbs">
   <a href="index.html">← Full investigation (report)</a>
   <a href="index.html#the-general-case-why-this-isn-t-only-about-ladera-ranch">Ch. 24 · The General Case</a>
   <a href="Ladera-Investigation-v1.0.pdf">PDF (282 pp)</a>
  </div>
  <p class="eyebrow">Statewide screening · companion to the Ladera Ranch investigation</p>
  <h1 class="serif">The General Case, and the archive behind it</h1>
  <p class="lede">Eleven California communities were run through the same documentary pipeline as
  Ladera Ranch, and a parallel hunt located every rights-clean historical image of the ranches
  underneath them. This page holds the map, the ranking, and the pictures.</p>
  <div class="topmeta">
   <span class="stat"><b>11</b> communities screened</span>
   <span class="stat"><b>5</b> counties</span>
   <span class="stat"><b>2</b> never reviewed at all</span>
   <span class="stat"><b>{len(imgs)}</b> images located</span>
   <span class="stat"><b>{n_photo}</b> photographs · <b>{n_map}</b> maps · <b>{n_other}</b> other</span>
   <span class="stat"><b>0</b> dip vats visible in any image</span>
  </div>
  <div class="disc"><b>No community named on this page is asserted, implied, or found to be
  contaminated.</b> The only measured soil fact anywhere in this program is <b>“unstudied.”</b>
  What is ranked below is where an <em>unanswered question</em> is widest — never where any risk
  is higher. The single fact that would answer it, for any community, is a direct soil arsenic
  test, which has been run for none of them.</div>
 </div>
</header>

<section class="band"><div class="wrap">
 <h2 class="serif">Where the dipping program and modern development overlap</h2>
 <p class="sub">The 1907–1915 USDA cattle-tick program covered essentially all of developed
 Southern California. This is a <em>context</em> map of that county-level footprint against the
 communities built on former ranchos — not a map of dip vats (their locations were never
 inventoried) and not a map of contamination.</p>
 <figure class="mapfig">
  <img src="statewide_assets/CA_dipping_map.jpg" alt="California map: 1908 cattle-tick quarantine counties versus modern development"
   data-full="statewide_assets/CA_dipping_map.jpg" data-title="California cattle-tick dipping program, 1907–1915 — county footprint vs. modern development"
   data-meta="Context map · this investigation (FIG-29)" data-depicts="Statewide, all named counties" data-rights="Original figure, this project">
  <figcaption>The largest dipping-era ranches — Camp Pendleton, Tejon, the Miller &amp; Lux
  lands — became federal land, farmland, and unbuilt terrain, <em>not</em> housing. Tap to enlarge.</figcaption>
 </figure>
</div></section>

<section class="band"><div class="wrap">
 <h2 class="serif">The complete ranking — where the review gap is widest</h2>
 <p class="sub">Review gap = how many years fall between the ~1912 end of arsenical dipping and the
 earliest date any environmental review of that land actually reached. A high rank means
 “worth asking next,” never “likely contaminated.”</p>
 <div class="tablewrap">
  <table>
   <thead><tr><th>#</th><th>Priority</th><th>Community (rancho)</th><th>County tier</th><th>Review gap</th><th>Dipping tied to ranch?</th></tr></thead>
   <tbody>
   {rank_rows()}
   </tbody>
  </table>
 </div>
 <p class="note">Every row shares two facts: <b>no cattle-dip vat is named</b> to any of the eleven
 ranches, and <b>no soil arsenic test exists</b> for the dip question at any of them. “No vat named”
 is an absence of a located record — bounded by archive-access limits during the run — never proof
 of absence.</p>
</div></section>

<section class="band"><div class="wrap">
 <h2 class="serif">The archive — every image located, by ranch</h2>
 <p class="sub">A parallel hunt searched Calisphere, the Online Archive of California, the Bancroft,
 Huntington, USC, the Library of Congress, and David Rumsey by <em>owner family</em> and photographer
 — the way these collections are actually catalogued. Only clearly public-domain or openly-licensed
 items were downloaded; each tile shows repository, date, and rights. Tap any image to read its full
 provenance. <b>None depicts a cattle-dip vat</b> — the working-facility context the Ladera record lacked, but not the vat itself.</p>
 {gallery()}
 <p class="note">The richest photograph troves belong to <b>Tejon Ranch</b> and the <b>Santa Margarita
 y Las Flores</b> ranch (today Camp Pendleton) — land that is <em>not</em> under housing. The most
 valuable remaining material is physical and undigitised, held in the historical societies and
 title-company archives named in the report’s recommendations.</p>
</div></section>

<footer><div class="wrap">
 <p><a href="index.html">← Return to the full investigation</a> &nbsp;·&nbsp;
 <a href="index.html#the-general-case-why-this-isn-t-only-about-ladera-ranch">Chapter 24 in context</a> &nbsp;·&nbsp;
 <a href="Ladera-Investigation-v1.0.pdf">Download the 282-page PDF</a></p>
 <p class="fdisc">{esc(DISCLAIMER)}</p>
</div></footer>

<div class="lb" id="lb" role="dialog" aria-modal="true">
 <button class="x" id="lbx" aria-label="Close">×</button>
 <img id="lbi" src="" alt="">
 <div class="cap">
  <span class="lbt" id="lbt"></span>
  <span class="lbm" id="lbm"></span>
  <span class="lbr" id="lbr"></span>
  <a class="open-src" id="lbo" href="#" target="_blank" rel="noopener">Open full-size image ↗</a>
 </div>
</div>

<script>
(function(){{
 var lb=document.getElementById('lb'),lbi=document.getElementById('lbi'),
     lbt=document.getElementById('lbt'),lbm=document.getElementById('lbm'),
     lbr=document.getElementById('lbr'),lbo=document.getElementById('lbo');
 function open(el){{
   var full=el.getAttribute('data-full');
   lbi.src=full; lbo.href=full;
   lbt.textContent=el.getAttribute('data-title')||'';
   var meta=el.getAttribute('data-meta')||'', dep=el.getAttribute('data-depicts')||'';
   lbm.textContent=meta+(dep?'  ·  depicts: '+dep:'');
   var r=el.getAttribute('data-rights'); lbr.textContent=r?('Rights: '+r):'';
   lb.classList.add('open'); document.body.style.overflow='hidden';
 }}
 function close(){{ lb.classList.remove('open'); lbi.src=''; document.body.style.overflow=''; }}
 document.querySelectorAll('[data-full]').forEach(function(el){{
   el.addEventListener('click',function(){{open(el);}});
   el.addEventListener('keydown',function(e){{if(e.key==='Enter'||e.key===' '){{e.preventDefault();open(el);}}}});
 }});
 document.getElementById('lbx').addEventListener('click',close);
 lb.addEventListener('click',function(e){{if(e.target===lb)close();}});
 document.addEventListener('keydown',function(e){{if(e.key==='Escape')close();}});
}})();
</script>
</body>
</html>"""

open(OUT,"w").write(page)
print("wrote", OUT, f"({len(page)//1024} KB HTML) · {len(imgs)} images across {sum(1 for t in by if by[t])} ranches")
