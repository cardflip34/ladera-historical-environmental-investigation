#!/usr/bin/env python3
"""California arsenical-dip LEGACY — a mass-balance MODEL ESTIMATE map (NOT measured contamination).

Shades the 1908 tick-quarantine counties by infestation tier (the dipping footprint) and annotates
the mass-balance model's plausible arsenic tonnage. It is NOT a map of measured contamination, NOT a
map of dip-vat locations (never inventoried), and NOT a health/cancer map. It shows where the
arsenical-dip program operated and the ORDER OF MAGNITUDE of arsenic the model implies. The
disclaimer is burned into the image so it cannot travel without it.
"""
import json, math, os
from PIL import Image, ImageDraw, ImageFont
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CA = json.load(open(os.path.join(ROOT, "data/geospatial/ca/ca_counties.geojson")))
OUT = os.path.join(ROOT, "research/arsenic_model"); os.makedirs(OUT, exist_ok=True)

HEAVY = {"San Luis Obispo","Santa Barbara","San Diego","Orange","Fresno","Ventura"}
LESSER = {"Tulare","Kern","Kings","Los Angeles","Riverside","San Bernardino","Madera"}
BG=(12,16,23); INK=(233,230,224); DIM=(150,168,184)
C_HEAVY=(158,74,60); C_LESS=(120,86,58); C_OTHER=(28,36,48); LINE=(60,72,92)
BRASS=(200,169,81); WHITE=(255,255,255); AMBER=(214,140,70)
W,H=1500,2000; K=math.cos(math.radians(37.0))
def polys(f):
    g=f["geometry"]; return [g["coordinates"]] if g["type"]=="Polygon" else g["coordinates"]
xs=[];ys=[]
for f in CA["features"]:
    for poly in polys(f):
        for ring in poly:
            for lo,la in ring: xs.append(lo*K); ys.append(la)
minx,maxx,miny,maxy=min(xs),max(xs),min(ys),max(ys); mar=70
s=min((W-2*mar)/(maxx-minx),(H-2*mar)/(maxy-miny))
offx=(W-(maxx-minx)*s)/2; offy=(H-(maxy-miny)*s)/2
def px(lo,la): return (offx+(lo*K-minx)*s, offy+(maxy-la)*s)
im=Image.new("RGB",(W,H),BG); dr=ImageDraw.Draw(im,"RGBA")
def col(n): return C_HEAVY if n in HEAVY else C_LESS if n in LESSER else C_OTHER
for f in CA["features"]:
    n=f["properties"]["name"]
    for poly in polys(f):
        for ring in poly: dr.polygon([px(lo,la) for lo,la in ring], fill=col(n), outline=LINE)
def F(sz,b=True):
    p="/System/Library/Fonts/Supplemental/Arial Bold.ttf" if b else "/System/Library/Fonts/Supplemental/Arial.ttf"
    try: return ImageFont.truetype(p,sz)
    except: return ImageFont.load_default()
# focus markers (staggered labels + leader lines so the two coastal points don't collide)
for name,lat,lon,c,dx,dy,anch in [
    ("Newport Coast  (this next phase)",33.60,-117.83,AMBER,-30,-58,"rm"),
    ("Ladera Ranch  (screened)",33.5467,-117.6403,BRASS,40,42,"lm")]:
    x,y=px(lon,lat); r=14
    dr.line([x,y,x+(dx*0.5),y+dy],fill=c+(200,),width=2)
    dr.ellipse([x-r,y-r,x+r,y+r],fill=c,outline=WHITE,width=3)
    dr.text((x+dx,y+dy),name,font=F(28),fill=c,anchor=anch)
# title band
dr.rectangle([0,0,W,190],fill=(0,0,0,210))
dr.text((40,26),"California arsenical cattle-dip legacy",font=F(48),fill=WHITE)
dr.text((42,90),"a MASS-BALANCE MODEL ESTIMATE of where the arsenic went - not measured contamination",font=F(27,False),fill=AMBER)
dr.text((42,130),"1907-1915 tick-quarantine counties, shaded by infestation intensity (the dipping footprint)",font=F(25,False),fill=DIM)
# model callout box
bx,by,bw,bh=40,240,600,400
dr.rectangle([bx,by,bx+bw,by+bh],fill=(20,26,36,235),outline=BRASS)
dr.text((bx+20,by+18),"THE MODEL (plausibility, not fact)",font=F(26),fill=BRASS)
lines=[
 ("White arsenic = 75.7% elemental arsenic",DIM),
 ("USDA formula: 8 lb white arsenic / 500 gal",DIM),
 ("Full 3,000-4,000 gal vat: ~36-48 lb As standing",INK),
 ("Per vat over its life: ~150-1,500 lb As throughput",INK),
 ("In soil around one used vat: ~100-500 lb As",AMBER),
 ("  (anchored to AUS/SE measured 500-3,000 mg/kg)",DIM),
 ("Total As ever used, program-wide: ~15-75 t",INK),
 ("  (USGS output + cattle-throughput ceiling)",DIM),
 ("STATEWIDE near-vat soil, model: ~3-30 t (central ~10)",AMBER),
 ("  (~50-150 vats; most As dispersed on range)",DIM),
]
yy=by+58
for t,c in lines:
    dr.text((bx+20,yy),t,font=F(23,False),fill=c); yy+=30
# legend
lx,ly=40,H-360
def sw(y,c,t):
    dr.rectangle([lx,y,lx+34,y+34],fill=c,outline=LINE); dr.text((lx+46,y+17),t,font=F(25,False),fill=INK,anchor="lm")
sw(ly,C_HEAVY,"county 'heavily infested' (USDA Circular 174, 1911) - higher dip intensity")
sw(ly+46,C_LESS,"county infested 'to a lesser degree'")
dr.ellipse([lx+6,ly+96,lx+26,ly+116],fill=BRASS,outline=WHITE,width=2); dr.text((lx+46,ly+106),"Ladera Ranch (documentary screening done)",font=F(24,False),fill=INK,anchor="lm")
dr.ellipse([lx+6,ly+134,lx+26,ly+154],fill=AMBER,outline=WHITE,width=2); dr.text((lx+46,ly+144),"Newport Coast (this next phase)",font=F(24,False),fill=INK,anchor="lm")
# disclaimer
dr.rectangle([0,H-120,W,H],fill=(26,20,16,240))
for i,t in enumerate([
 "MODEL ESTIMATE, NOT A MEASUREMENT. No California dip-site soil has ever been tested. Vat locations were never",
 "inventoried and remain unknown. This is not a contamination map, not a dip-vat map, and not a health or cancer map.",
 "It shows the program's county footprint and the ORDER OF MAGNITUDE of arsenic implied by the published dip formula."]):
    dr.text((40,H-104+i*32),t,font=F(23,False),fill=(226,216,204),anchor="lm")
im.save(os.path.join(OUT,"CA_arsenic_legacy_model_map.jpg"),quality=90)
print("wrote", os.path.join(OUT,"CA_arsenic_legacy_model_map.jpg"), im.size)
