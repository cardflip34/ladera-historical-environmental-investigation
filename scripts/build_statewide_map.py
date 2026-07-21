#!/usr/bin/env python3
"""California statewide map: 1908 cattle-tick quarantine counties vs. modern development.

This is a CONTEXT map. It shades the counties the USDA named in the tick-eradication program
(Circular 174, 1911) and marks major modern communities built on former land-grant ranchos in
those counties. It is NOT a map of dip vats (locations unknown, never inventoried) and NOT a map
of contamination (unstudied anywhere but the one Ladera Ranch footprint). The disclaimer is drawn
onto the image so it cannot travel without it.
"""
import json, math, os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CA = json.load(open(os.path.join(ROOT, "data/geospatial/ca/ca_counties.geojson")))
OUT = os.path.join(ROOT, "research/statewide")
os.makedirs(OUT, exist_ok=True)

HEAVY = {"San Luis Obispo","Santa Barbara","San Diego","Orange","Fresno","Ventura"}
LESSER = {"Tulare","Kern","Kings","Los Angeles","Riverside","San Bernardino","Madera"}

BG=(11,15,22); INK=(233,230,224); DIM=(150,168,184)
C_HEAVY=(150,74,64); C_LESS=(92,64,58); C_OTHER=(30,38,50); LINE=(60,72,92)
BRASS=(200,169,81); CYAN=(79,195,232); WHITE=(255,255,255)

W,H=1500,2000
K=math.cos(math.radians(37.0))
def polys(f):
    g=f["geometry"]; t=g["type"]; cs=g["coordinates"]
    return [cs] if t=="Polygon" else cs
# bounds
xs=[];ys=[]
for f in CA["features"]:
    for poly in polys(f):
        for ring in poly:
            for lon,lat in ring:
                xs.append(lon*K); ys.append(lat)
minx,maxx,miny,maxy=min(xs),max(xs),min(ys),max(ys)
mar=70
sx=(W-2*mar)/(maxx-minx); sy=(H-2*mar)/(maxy-miny); s=min(sx,sy)
offx=(W-(maxx-minx)*s)/2; offy=(H-(maxy-miny)*s)/2
def px(lon,lat):
    return (offx+(lon*K-minx)*s, offy+(maxy-lat)*s)

im=Image.new("RGB",(W,H),BG); dr=ImageDraw.Draw(im,"RGBA")
def col(name):
    return C_HEAVY if name in HEAVY else C_LESS if name in LESSER else C_OTHER
for f in CA["features"]:
    name=f["properties"]["name"]
    for poly in polys(f):
        for ring in poly:
            pts=[px(lo,la) for lo,la in ring]
            dr.polygon(pts, fill=col(name), outline=LINE)

def F(sz,bold=True):
    p="/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf"
    try: return ImageFont.truetype(p,sz)
    except: return ImageFont.load_default()

# community markers (approx coords). kind: 'ladera', 'mpc' (residential), 'nonres' (federal/farm/unbuilt)
GREEN=(120,170,120)
COMM=[
 ("Ladera Ranch",33.5467,-117.6403,"ladera",None),
 ("Irvine / Tustin",33.68,-117.80,"mpc",None),
 ("Mission Viejo · RSM · Coto",33.63,-117.62,"mpc",None),
 ("Santa Clarita / Valencia",34.41,-118.51,"mpc",None),
 ("Simi Valley",34.27,-118.78,"mpc",None),
 ("Long Beach · Lakewood",33.80,-118.13,"mpc",None),
 ("Rancho Cucamonga",34.11,-117.55,"mpc",None),
 ("Riverside · Jurupa",33.95,-117.40,"mpc",None),
 ("Rancho Bernardo · Peñasquitos · Santa Fe",33.02,-117.08,"mpc",None),
 ("Camp Pendleton",33.30,-117.40,"nonres","federal — undeveloped"),
 ("Tejon Ranch",34.96,-118.75,"nonres","largely unbuilt"),
 ("Miller & Lux lands",37.06,-120.85,"nonres","irrigated farmland"),
]
for name,lat,lon,kind,note in COMM:
    x,y=px(lon,lat)
    if kind=="ladera":
        r=15; dr.ellipse([x-r,y-r,x+r,y+r],fill=BRASS,outline=WHITE,width=3)
        dr.text((x+r+8,y-10),name,font=F(30),fill=BRASS,anchor="lm")
    elif kind=="nonres":
        r=9; dr.ellipse([x-r,y-r,x+r,y+r],fill=GREEN+(255,),outline=WHITE,width=2)
        dr.text((x+r+7,y-19),name,font=F(24,False),fill=GREEN,anchor="lm")
        dr.text((x+r+7,y+7),note,font=F(19,False),fill=(150,168,184),anchor="lm")
    else:
        r=9; dr.ellipse([x-r,y-r,x+r,y+r],fill=WHITE+(235,),outline=(0,0,0,180),width=2)
        dr.text((x+r+7,y-9),name,font=F(23,False),fill=INK,anchor="lm")

# title + legend + disclaimer
dr.rectangle([0,0,W,150],fill=(0,0,0,205))
dr.text((40,28),"California cattle-tick dipping program, 1907–1915",font=F(46),fill=WHITE)
dr.text((42,92),"the county-level footprint of arsenical dipping, and modern development on it",font=F(30,False),fill=DIM)
# legend
lx,ly=40,H-320
def sw(y,c,t):
    dr.rectangle([lx,y,lx+34,y+34],fill=c,outline=LINE); dr.text((lx+46,y+17),t,font=F(26,False),fill=INK,anchor="lm")
sw(ly,C_HEAVY,"county 'heavily infested' (USDA Circular 174, 1911)")
sw(ly+46,C_LESS,"county infested 'to a lesser degree'")
dr.ellipse([lx+6,ly+96,lx+26,ly+116],fill=(255,255,255,235),outline=(0,0,0,180),width=2); dr.text((lx+46,ly+106),"residential master-planned community on former rancho",font=F(24,False),fill=INK,anchor="lm")
dr.ellipse([lx+6,ly+134,lx+26,ly+154],fill=(120,170,120,255),outline=WHITE,width=2); dr.text((lx+46,ly+144),"big dipping-era ranch now federal / farmland / unbuilt",font=F(24,False),fill=INK,anchor="lm")
dr.ellipse([lx+6,ly+172,lx+26,ly+192],fill=BRASS,outline=WHITE,width=2); dr.text((lx+46,ly+182),"Ladera Ranch (this investigation)",font=F(24,False),fill=INK,anchor="lm")
# disclaimer band
dr.rectangle([0,H-90,W,H],fill=(26,20,16,235))
dr.text((40,H-72),"NOT a map of dip vats or contamination. Vat locations were never inventoried and remain unknown;",font=F(24,False),fill=(226,216,204),anchor="lm")
dr.text((40,H-40),"soil is unstudied everywhere except the one Ladera Ranch footprint. This shows program reach vs. development only.",font=F(24,False),fill=(226,216,204),anchor="lm")

im.save(os.path.join(OUT,"CA_dipping_counties_vs_development.jpg"),quality=90)
print("wrote", os.path.join(OUT,"CA_dipping_counties_vs_development.jpg"), im.size)
