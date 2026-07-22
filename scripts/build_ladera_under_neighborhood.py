#!/usr/bin/env python3
"""Ladera Ranch, 2022 — which best-guess dip candidates fall UNDER today's residential neighborhoods vs
in the preserved Trabuco greenbelt. Candidates = the 1968 USGS surface-water bodies (cattle concentrate
at water) + the single 1937 ranch structure. GRADED INFERENCE; no vat located, no soil tested. Classes
from research/historical_imagery/premise_homes_on_water.json (buildings within 100 m / nearest building)."""
import os, math, json
from PIL import Image, ImageDraw, ImageFont
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AER=os.path.join(ROOT,"research/historical_imagery/oc_aerials")
OUT=os.path.join(ROOT,"research/ladera/imagery/ladera_candidates_under_neighborhood.jpg")
WLON,ELON,SLAT,NLAT=-117.68,-117.616,33.52,33.575
CW0,CE0,CS0,CN0=-117.668,-117.620,33.530,33.566   # crop across Zone A: corridor (W) -> east villages

sites=json.load(open(os.path.join(ROOT,"research/historical_imagery/premise_homes_on_water.json")))["sites"]
NODE=(33.55505,-117.65492)   # 1937 ranch structure (greenbelt)
def cls(s):
    if s["n_bldg_100m"]>=5: return "under"
    if s["nearest_bldg_m"]<70: return "edge"
    if s["nearest_bldg_m"]>140: return "green"
    return "fringe"
UNDER=(240,120,40); GREEN=(70,190,235); NODEC=(228,60,54); FR=(190,190,150)

def F(sz,b=True):
    p="/System/Library/Fonts/Supplemental/Arial Bold.ttf" if b else "/System/Library/Fonts/Supplemental/Arial.ttf"
    try: return ImageFont.truetype(p,sz)
    except: return ImageFont.load_default()

im=Image.open(os.path.join(AER,"2022_modern.jpg")).convert("RGB"); W,H=im.size
def gx(lon): return (lon-WLON)/(ELON-WLON)*W
def gy(lat): return (NLAT-lat)/(NLAT-SLAT)*H
x0,x1=gx(CW0),gx(CE0); y0,y1=gy(CN0),gy(CS0)
crop=im.crop((int(x0),int(y0),int(x1),int(y1))); cw,ch=crop.size
DW=1900; s=DW/cw; DH=int(ch*s)
panel=crop.resize((DW,DH)); dr=ImageDraw.Draw(panel,"RGBA")
def px(lon,lat): return ((gx(lon)-x0)*s,(gy(lat)-y0)*s)

# only Zone-A candidates (the "current residential neighborhood")
za=[s2 for s2 in sites if s2["in_zone_a"]]
# dashed hulls: greenbelt corridor cluster & east built cluster
under=[s2 for s2 in za if cls(s2)=="under"]
green=[s2 for s2 in za if cls(s2)=="green"]
def hull(pts,col,pad):
    P=[px(s2["lon"],s2["lat"]) for s2 in pts]
    cx=sum(p[0] for p in P)/len(P); cy=sum(p[1] for p in P)/len(P)
    rr=max(math.hypot(p[0]-cx,p[1]-cy) for p in P)+pad
    for a in range(0,360,7):
        x=cx+rr*math.cos(math.radians(a))*1.15; y=cy+rr*math.sin(math.radians(a))
        dr.ellipse([x-3,y-3,x+3,y+3],fill=col+(220,))
    return cx,cy,rr
gcx,gcy,grr=hull(green,GREEN,55)
ucx,ucy,urr=hull(under,UNDER,55)
dr.text((gcx,gcy-grr-4),"Trabuco greenbelt — OPEN SPACE",font=F(21),fill=(200,240,255),anchor="mb")
dr.text((ucx,ucy-urr-4),"central-east villages — BUILT OVER",font=F(21),fill=(255,215,180),anchor="mb")

for s2 in za:
    x,y=px(s2["lon"],s2["lat"]); c=cls(s2)
    col={"under":UNDER,"green":GREEN,"edge":UNDER,"fringe":FR}[c]
    r=int(9+(s2["area_m2"]**0.5)/7)
    dr.ellipse([x-r,y-r,x+r,y+r],outline=col+(255,),width=5); dr.ellipse([x-r,y-r,x+r,y+r],fill=col+(70,))
    if c=="under" and s2["n_bldg_100m"]>=13:
        dr.text((x,y+r+11),f"{s2['n_bldg_100m']} homes <100m",font=F(15,False),fill=(255,225,200),anchor="mt")
# ranch node
nx,ny=px(*NODE[::-1]); rr=19
dr.polygon([(nx,ny-rr-6),(nx+rr+4,ny),(nx,ny+rr+6),(nx-rr-4,ny)],fill=NODEC+(235,),outline=(255,255,255))
dr.text((nx,ny),"A",font=F(22),fill=(255,255,255),anchor="mm")
dr.text((nx,ny-rr-12),"ranch structure (1937)",font=F(16,False),fill=(255,210,205),anchor="mb")

# header
dr.rectangle([0,0,DW,150],fill=(0,0,0,190))
dr.text((22,14),"Ladera Ranch, 2022 — which best-guess dip candidates are under houses today?",font=F(31),fill=(255,255,255))
dr.text((22,54),"Candidates = 1968-mapped stock-water bodies (cattle gather at water) + the one 1937 ranch structure.  16 fall inside the Ladera footprint.",font=F(17,False),fill=(220,228,238))
dr.text((22,80),"GRADED INFERENCE (best guess) · No dip vat was ever found on the imagery · No soil has been tested · candidate ground, NOT located facilities",font=F(17,False),fill=(255,200,170))
# legend
lx=22; ly=110
dr.ellipse([lx,ly,lx+26,ly+26],outline=GREEN+(255,),width=4); dr.ellipse([lx,ly,lx+26,ly+26],fill=GREEN+(70,))
dr.text((lx+36,ly+13),"in GREENBELT / open space (9 of 16 — incl. the strongest node + main water)",font=F(17,False),fill=(235,235,235),anchor="lm")
dr.ellipse([lx+660,ly,lx+686,ly+26],outline=UNDER+(255,),width=4); dr.ellipse([lx+660,ly,lx+686,ly+26],fill=UNDER+(70,))
dr.text((lx+696,ly+13),"UNDER / inside the neighborhood (6 of 16 — houses within 8-35 m)",font=F(17,False),fill=(255,225,200),anchor="lm")
# footer
dr.rectangle([0,DH-46,DW,DH],fill=(0,0,0,205))
dr.text((22,DH-23),"Note: the 6 under-neighborhood features are SMALL stock ponds; a ranch's dip was usually ONE central facility at its working corral (the greenbelt node), so these are weaker dip candidates — but they are exactly where built-over ranch ground would now sit.  Resolver: a soil arsenic test, not yet run.  Imagery: OC Survey 2022 1-ft.",
        font=F(14,False),fill=(215,220,228),anchor="lm")
panel.save(OUT,quality=90); print("wrote",OUT,panel.size)
