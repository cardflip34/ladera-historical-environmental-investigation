#!/usr/bin/env python3
"""Deep imagery pass over the EXACT Joplin 1909 homestead patent (T6S R7W Sec 24/25, BLM CadNSDI
polygons): 1938 600-scale (1.15 ft/px), 1953, and modern Esri, patent boundary on each. Purpose:
look for ranch-era structures/corrals INSIDE the patented ground now that it is precisely located.
Documentary recon only — no vat identification is claimed at this resolution."""
import json, io, math, os, urllib.parse, urllib.request
from pyproj import Transformer
from PIL import Image, ImageOps, ImageDraw, ImageFont
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTD=os.path.join(ROOT,"research/coto_de_caza/imagery"); os.makedirs(OUTD,exist_ok=True)
BASE="https://www.ocgis.com/arcpub/rest/services/Historic_Imagery/Historic_Imagery/ImageServer"
ESRI="https://services.arcgisonline.com/arcgis/rest/services/World_Imagery/MapServer/export"
UA={"User-Agent":"Mozilla/5.0 (research; land-use history)"}
secs=json.load(open(os.path.join(ROOT,"data/geospatial/joplin_patent_sections_T6SR7W.json")))["features"]

# patent extent + margin
WLON,ELON=-117.5800,-117.5500; SLAT,NLAT=33.6220,33.6480
T=Transformer.from_crs(4326,2230,always_xy=True)
x0,y0=T.transform(WLON,SLAT); x1,y1=T.transform(ELON,NLAT)
W=3600; H=int(W*(y1-y0)/(x1-x0))

def F(s,b=True):
    p="/System/Library/Fonts/Supplemental/Arial Bold.ttf" if b else "/System/Library/Fonts/Supplemental/Arial.ttf"
    try: return ImageFont.truetype(p,s)
    except: return ImageFont.load_default()

def get(url): return urllib.request.urlopen(urllib.request.Request(url,headers=UA),timeout=120).read()

def oc_frame(oid,label):
    ex={"bbox":f"{x0},{y0},{x1},{y1}","bboxSR":"2230","imageSR":"2230","size":f"{W},{H}",
        "format":"jpg","f":"image","mosaicRule":json.dumps({"mosaicMethod":"esriMosaicLockRaster","lockRasterIds":[oid]})}
    im=Image.open(io.BytesIO(get(BASE+"/exportImage?"+urllib.parse.urlencode(ex)))).convert("L")
    im=ImageOps.autocontrast(im,cutoff=0.5).convert("RGB")
    im.save(os.path.join(OUTD,f"joplin_patent_{label}.jpg"),quality=92)
    return im

def esri_frame():
    u=ESRI+"?"+urllib.parse.urlencode({"bbox":f"{WLON},{SLAT},{ELON},{NLAT}","bboxSR":"4326","imageSR":"4326",
        "size":f"{W},{H}","format":"jpg","f":"image"})
    im=Image.open(io.BytesIO(get(u))).convert("RGB")
    im.save(os.path.join(OUTD,"joplin_patent_modern.jpg"),quality=92)
    return im

def px_ft(lon,lat):
    x,y=T.transform(lon,lat); return ((x-x0)/(x1-x0)*W,(y1-y)/(y1-y0)*H)
def px_deg(lon,lat):
    return ((lon-WLON)/(ELON-WLON)*W,(NLAT-lat)/(NLAT-SLAT)*H)

def annotate(im,title,sub,pxf):
    dr=ImageDraw.Draw(im,"RGBA")
    for f in secs:
        for r in f["geometry"]["rings"]:
            pts=[pxf(p[0],p[1]) for p in r]
            dr.line(pts+[pts[0]],fill=(255,225,60,255),width=8)
        xs=[pxf(p[0],p[1])[0] for r in f["geometry"]["rings"] for p in r]
        ys=[pxf(p[0],p[1])[1] for r in f["geometry"]["rings"] for p in r]
        dr.text((sum(xs)/len(xs),sum(ys)/len(ys)),f"Sec {int(f['attributes']['FRSTDIVNO'])}",
                font=F(46),fill=(255,240,120),anchor="mm",stroke_width=4,stroke_fill=(40,30,0))
    dr.rectangle([0,0,im.width,120],fill=(0,0,0,185))
    dr.text((24,16),title,font=F(44),fill=(255,255,255))
    dr.text((26,74),sub,font=F(26,False),fill=(230,225,205))
    # scale bar 1000 ft
    mpp=(x1-x0)/im.width  # ft per px
    bar=1000/mpp; bx,by=40,im.height-60
    dr.rectangle([bx,by,bx+bar,by+10],fill=(255,255,255,240)); dr.text((bx,by-36),"1000 ft",font=F(26),fill=(255,255,255))
    return im

print("pulling 1938 600-scale (OID 310)…"); a38=oc_frame(310,"1938_600")
print("pulling 1953 (OID 357)…"); a53=oc_frame(357,"1953")
print("pulling modern…"); mod=esri_frame()

annotate(a38,"1938 — Joplin patent ground at 1.15 ft/px","OC Survey 'Orange County 600 Scale 1938' · yellow = 1909 homestead patent (BLM GLO SER-96513 / CadNSDI)",px_ft)
annotate(a53,"1953 — same ground","OC Survey 'Orange County 1953' · Starr era (family sold east lands 1927; Coto built 1968+)",px_ft)
annotate(mod,"Today — NE Coto de Caza","Esri World Imagery · west half of patent = homes/golf/reservoir · east half = open foothill",px_deg)
a38.save(os.path.join(OUTD,"joplin_patent_1938_annotated.jpg"),quality=90)
a53.save(os.path.join(OUTD,"joplin_patent_1953_annotated.jpg"),quality=90)
mod.save(os.path.join(OUTD,"joplin_patent_modern_annotated.jpg"),quality=90)

# 3-panel composite (downscaled)
PW=1240
panels=[]
for im in (a38,a53,mod):
    s=PW/im.width; panels.append(im.resize((PW,int(im.height*s))))
ph=max(p.height for p in panels)
cv=Image.new("RGB",(PW*3+32,ph+70),(18,20,24))
for i,p in enumerate(panels): cv.paste(p,(i*(PW+16),70))
dr=ImageDraw.Draw(cv,"RGBA")
dr.text((24,14),"The documented Joplin dip ranch (patent ground): 1938 → 1953 → today",font=F(38),fill=(255,255,255))
dr.text((cv.width-24,30),"GRADED RECON · no vat identified · no soil tested",font=F(22,False),fill=(255,200,170),anchor="rm")
cv.save(os.path.join(OUTD,"joplin_patent_triptych.jpg"),quality=88)
print("done:",OUTD)
