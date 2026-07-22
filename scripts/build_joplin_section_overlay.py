#!/usr/bin/env python3
"""Overlay the ACTUAL BLM PLSS survey polygons for Josiah C. Joplin's 1909 homestead patent
(T6S R7W SBM, Sections 24 & 25, Accession SER-96513) on modern satellite imagery, to state
precisely which present-day ground the DOCUMENTED 1908 dip ranch occupies. Section geometry from
BLM CadNSDI (A2). No contamination asserted; exact vat parcel within the homestead still unknown."""
import json, io, math, urllib.parse, urllib.request, os
from PIL import Image, ImageDraw, ImageFont
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT=os.path.join(ROOT,"research/coto_de_caza/joplin_patent_section_overlay.jpg")
UA={"User-Agent":"Mozilla/5.0 (research)"}
ESRI="https://services.arcgisonline.com/arcgis/rest/services/World_Imagery/MapServer/export"
rings_by_sec=json.load(open("/tmp/joplin_sections.json"))["features"]

WLON,ELON,SLAT,NLAT=-117.610,-117.520,33.605,33.658
W=1900; H=int(W*(NLAT-SLAT)/((ELON-WLON)*math.cos(math.radians(33.63))))
u=ESRI+"?"+urllib.parse.urlencode({"bbox":f"{WLON},{SLAT},{ELON},{NLAT}","bboxSR":"4326","imageSR":"4326","size":f"{W},{H}","format":"jpg","f":"image"})
base=Image.open(io.BytesIO(urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=90).read())).convert("RGB")
dr=ImageDraw.Draw(base,"RGBA")
def F(s,b=True):
    p="/System/Library/Fonts/Supplemental/Arial Bold.ttf" if b else "/System/Library/Fonts/Supplemental/Arial.ttf"
    try: return ImageFont.truetype(p,s)
    except: return ImageFont.load_default()
def px(lon,lat): return ((lon-WLON)/(ELON-WLON)*W,(NLAT-lat)/(NLAT-SLAT)*H)

# draw the patent section polygons
for f in rings_by_sec:
    sec=f["attributes"]["FRSTDIVNO"]
    for r in f["geometry"]["rings"]:
        pts=[px(p[0],p[1]) for p in r]
        dr.line(pts+[pts[0]],fill=(255,225,60,255),width=5)
        dr.polygon(pts,fill=(255,215,60,55))
    cx=sum(p[0] for r in f["geometry"]["rings"] for p in r)/sum(len(r) for r in f["geometry"]["rings"])
    cy=sum(px(p[0],p[1])[1] for r in f["geometry"]["rings"] for p in r)/sum(len(r) for r in f["geometry"]["rings"])
    # label section number at its centroid
    xs=[px(p[0],p[1])[0] for r in f["geometry"]["rings"] for p in r]; ys=[px(p[0],p[1])[1] for r in f["geometry"]["rings"] for p in r]
    mx=sum(xs)/len(xs); my=sum(ys)/len(ys)
    dr.text((mx,my),f"Sec {int(sec)}",font=F(30),fill=(255,240,120),anchor="mm",stroke_width=3,stroke_fill=(40,30,0))

# orientation landmarks
LM=[("COTO DE CAZA (gated community)",33.600,-117.586,(120,200,255)),
    ("Dove Canyon",33.646,-117.601,(120,200,255)),
    ("Starr Ranch Audubon Sanctuary",33.630,-117.527,(150,255,150)),
    ("Bell Canyon",33.620,-117.543,(200,235,200))]
for name,lat,lon,col in LM:
    x,y=px(lon,lat)
    dr.ellipse([x-7,y-7,x+7,y+7],fill=col+(255,),outline=(0,0,0))
    tw=dr.textlength(name,font=F(20))
    dr.rectangle([x+11,y-13,x+11+tw+10,y+13],fill=(0,0,0,160))
    dr.text((x+16,y),name,font=F(20),fill=col+(255,),anchor="lm")

# header
dr.rectangle([0,0,W,120],fill=(0,0,0,190))
dr.text((22,12),"The DOCUMENTED Joplin dip ranch, pinned to survey section",font=F(34),fill=(255,255,255))
dr.text((24,54),"Yellow = Josiah C. Joplin's 1909 homestead patent (BLM GLO SER-96513): T6S R7W SBM, Sections 24 & 25 — the actual BLM PLSS polygons.",font=F(18,False),fill=(255,235,150))
dr.text((24,82),"1908 press: county-ordered arsenical dip 'at the ranch of J. C. Joplin.'  No soil tested; exact vat parcel within the homestead unknown.  Imagery: Esri World Imagery.",font=F(16,False),fill=(220,226,234))
base.save(OUT,quality=90); print("wrote",OUT,base.size)
