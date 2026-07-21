#!/usr/bin/env python3
"""Orange County cattle-dipping geography (1908-1912) — a context map.

Shows: (1) the four cattle-dipping sites NAMED in the 1908 press (district-level, NOT vat
coordinates); (2) the APPROXIMATE March-1912 quarantine district (the last-held tick zone,
reconstructed from the proclamation's metes-and-bounds — historical road alignments are not precisely
georeferenced); and (3) the three study communities. It is a quarantine/land-use history map, NOT a
map of vat locations (unknown) and NOT a contamination map (soil unstudied everywhere).
"""
import json, math, os
from PIL import Image, ImageDraw, ImageFont
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CA=json.load(open(os.path.join(ROOT,"data/geospatial/ca/ca_counties.geojson")))
OUT=os.path.join(ROOT,"research/oc_dipping_records"); os.makedirs(OUT,exist_ok=True)
oc=[f for f in CA["features"] if f["properties"].get("name")=="Orange"][0]
g=oc["geometry"]; rings=([g["coordinates"]] if g["type"]=="Polygon" else g["coordinates"])

BG=(247,244,239); INK=(20,36,58); INK2=(70,90,112); LINE=(150,140,120)
LAND=(233,228,216); DIST=(176,106,44); BRASS=(169,126,31); TEAL=(47,122,99); GREY=(120,132,146)
W,H=1600,1500; K=math.cos(math.radians(33.66))
xs=[];ys=[]
for poly in rings:
    for ring in poly:
        for lo,la in ring: xs.append(lo*K); ys.append(la)
minx,maxx,miny,maxy=min(xs),max(xs),min(ys),max(ys); mar=90
s=min((W-2*mar)/(maxx-minx),(H-2*mar)/(maxy-miny))
offx=(W-(maxx-minx)*s)/2; offy=(H-(maxy-miny)*s)/2
def px(lo,la): return (offx+(lo*K-minx)*s, offy+(maxy-la)*s)
im=Image.new("RGB",(W,H),BG); dr=ImageDraw.Draw(im,"RGBA")
for poly in rings:
    for ring in poly: dr.polygon([px(lo,la) for lo,la in ring], fill=LAND, outline=LINE)
def F(sz,b=True):
    p="/System/Library/Fonts/Supplemental/Arial Bold.ttf" if b else "/System/Library/Fonts/Supplemental/Arial.ttf"
    try: return ImageFont.truetype(p,sz)
    except: return ImageFont.load_default()

# approximate March-1912 quarantine district (SW/S Orange County), reconstructed
district=[(-117.929,33.605),(-117.80,33.735),(-117.68,33.66),(-117.60,33.685),(-117.43,33.685),
          (-117.51,33.427),(-117.63,33.44),(-117.783,33.542),(-117.929,33.605)]
dpts=[px(lo,la) for lo,la in district]
dr.polygon(dpts, fill=DIST+(70,))
# dashed-ish boundary (draw segments)
for i in range(len(dpts)-1):
    dr.line([dpts[i],dpts[i+1]], fill=DIST+(230,), width=4)
dr.text(px(-117.49,33.57),"approx. March-1912\nquarantine district\n(last-held tick zone)",font=F(23),fill=DIST,anchor="mm",align="center")

# named 1908 dip sites (district-level; teal diamonds)
sites=[("Joplin ranch · Trabuco Canyon",33.665,-117.585),
       ("San Juan Capistrano",33.501,-117.662),
       ("Yorba · Santa Ana Canyon",33.875,-117.79),
       ("Bixby ranch · Santa Ana Canyon",33.855,-117.752)]
for name,lat,lon in sites:
    x,y=px(lon,lat); r=13
    dr.polygon([(x,y-r),(x+r,y),(x,y+r),(x-r,y)], fill=TEAL, outline=(255,255,255), width=2)
    dr.text((x+r+6,y),name,font=F(22),fill=TEAL,anchor="lm")

# study communities (brass circles)
comm=[("Ladera Ranch",33.5467,-117.6403),("Newport Coast",33.60,-117.83),("Irvine (central)",33.685,-117.825)]
for name,lat,lon in comm:
    x,y=px(lon,lat); r=12
    dr.ellipse([x-r,y-r,x+r,y+r], fill=BRASS, outline=(255,255,255), width=3)
    dr.text((x,y+r+4),name,font=F(23),fill=INK,anchor="ma")

# orientation labels (grey)
for name,lat,lon in [("Santa Ana",33.749,-117.873),("Newport Beach",33.619,-117.929),
                     ("Anaheim",33.836,-117.914),("Tustin",33.746,-117.826),("San Clemente",33.427,-117.612)]:
    x,y=px(lon,lat); dr.ellipse([x-4,y-4,x+4,y+4],fill=GREY)
    dr.text((x+7,y),name,font=F(18,False),fill=GREY,anchor="lm")

# title + legend + disclaimer
dr.text((40,34),"Orange County cattle-dipping geography, 1908-1912",font=F(40),fill=INK)
dr.text((42,86),"the four dipping sites named in the 1908 press, the last-held quarantine district, and the three study communities",font=F(23,False),fill=INK2)
lx,ly=1130,1120
dr.rectangle([lx-16,ly-16,W-30,ly+200],fill=(255,255,255,220),outline=LINE)
dr.polygon([(lx+8,ly-8),(lx+20,ly),(lx+8,ly+8),(lx-4,ly)],fill=TEAL,outline=(255,255,255),width=2)
dr.text((lx+34,ly),"named 1908 dip site (district-level)",font=F(20,False),fill=INK,anchor="lm")
dr.ellipse([lx-4,ly+34,lx+16,ly+54],fill=BRASS,outline=(255,255,255),width=2)
dr.text((lx+34,ly+44),"study community",font=F(20,False),fill=INK,anchor="lm")
dr.rectangle([lx-4,ly+78,lx+16,ly+96],fill=DIST+(120,),outline=DIST)
dr.text((lx+34,ly+87),"approx. last-held district",font=F(20,False),fill=INK,anchor="lm")
dr.text((lx-4,ly+128),"Named sites span the county; the tick (and\nmandatory dipping) held out longest in the\nSW/S district - nearest Ladera & the coast.",font=F(18,False),fill=INK2)
dr.rectangle([0,H-92,W,H],fill=(238,232,222,255))
for i,t in enumerate([
 "District-level & APPROXIMATE. Named sites are ranches/districts from the 1908 press, NOT vat coordinates. The district boundary is reconstructed",
 "from the 1912 proclamation's metes-and-bounds; historical road alignments are not precisely georeferenced. This is quarantine/land-use history -",
 "NOT a map of vat locations (unknown, never inventoried) and NOT a contamination map (soil unstudied everywhere)."]):
    dr.text((40,H-78+i*26),t,font=F(18,False),fill=(90,74,54),anchor="lm")
im.save(os.path.join(OUT,"oc_dipping_geography_map.jpg"),quality=92)
print("wrote", os.path.join(OUT,"oc_dipping_geography_map.jpg"), im.size)
