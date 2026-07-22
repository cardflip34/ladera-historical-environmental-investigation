#!/usr/bin/env python3
"""Ladera Ranch — best pre-development aerial (1937-38, 1.15 ft/px) + 2022, with a GRADED-INFERENCE
best-guess of where a cattle dip would most plausibly have stood. NO vat was ever found on the imagery
and NO soil has been tested; the markers are reasoned candidates (ranch-activity node + stock water
where cattle concentrate), NOT located facilities. See research/historical_imagery/README.md."""
import os, math
from PIL import Image, ImageDraw, ImageFont
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AER=os.path.join(ROOT,"research/historical_imagery/oc_aerials")
OUT=os.path.join(ROOT,"research/ladera/imagery/ladera_dip_bestguess_thennow.jpg")

# shared frame bbox (all OC frames rendered to this identical extent)
WLON,ELON,SLAT,NLAT=-117.68,-117.616,33.52,33.575
# tighter crop around Zone A / western Trabuco corridor where the candidates cluster
CW0,CE0,CS0,CN0=-117.675,-117.630,33.535,33.570

def F(sz,b=True):
    p="/System/Library/Fonts/Supplemental/Arial Bold.ttf" if b else "/System/Library/Fonts/Supplemental/Arial.ttf"
    try: return ImageFont.truetype(p,sz)
    except: return ImageFont.load_default()

# best-guess candidates: (label, lat, lon, kind, area_m2)  kind: node|water
CAND=[
 ("A", 33.55505,-117.65492,"node",0),        # C01 ranch-activity node (1937 structure) — PRIMARY
 ("B", 33.54394,-117.66132,"water",24745),    # C02 largest impoundment
 ("C", 33.54802,-117.65992,"water",4661),     # C05
 ("D", 33.54123,-117.66061,"water",12395),    # C03
 ("E", 33.55857,-117.65281,"water",9111),     # C04
]
NODE=(228,60,54); WATER=(70,190,235); CORE=(255,210,70)

def build_panel(fname, disp_w, title, subtitle):
    im=Image.open(os.path.join(AER,fname)).convert("RGB"); W,H=im.size
    def gx(lon): return (lon-WLON)/(ELON-WLON)*W
    def gy(lat): return (NLAT-lat)/(NLAT-SLAT)*H
    x0,x1=gx(CW0),gx(CE0); y0,y1=gy(CN0),gy(CS0)
    crop=im.crop((int(x0),int(y0),int(x1),int(y1))); cw,ch=crop.size
    s=disp_w/cw; disp_h=int(ch*s)
    panel=crop.resize((disp_w,disp_h))
    dr=ImageDraw.Draw(panel,"RGBA")
    def px(lon,lat): return ((gx(lon)-x0)*s,(gy(lat)-y0)*s)
    # most-probable working core: dashed hull around node A + waters B,C,D (west corridor)
    core=[px(-117.65492,33.55505),px(-117.65281,33.55857),px(-117.65992,33.54802),
          px(-117.66132,33.54394),px(-117.66061,33.54123)]
    cx=sum(p[0] for p in core)/len(core); cy=sum(p[1] for p in core)/len(core)
    rr=max(math.hypot(p[0]-cx,p[1]-cy) for p in core)+42
    for a in range(0,360,9):
        x=cx+rr*math.cos(math.radians(a)); y=cy+rr*math.sin(math.radians(a))
        dr.ellipse([x-3,y-3,x+3,y+3],fill=CORE+(235,))
    # markers
    for lab,lat,lon,kind,area in CAND:
        x,y=px(lon,lat)
        if kind=="node":
            r=20
            dr.polygon([(x,y-r-6),(x+r+4,y),(x,y+r+6),(x-r-4,y)],fill=NODE+(235,),outline=(255,255,255))
            dr.text((x,y),lab,font=F(23),fill=(255,255,255),anchor="mm")
        else:
            r=int(11+ (area**0.5)/6.5)
            dr.ellipse([x-r,y-r,x+r,y+r],outline=WATER+(255,),width=5)
            dr.ellipse([x-r,y-r,x+r,y+r],fill=WATER+(70,))
            dr.text((x,y-r-14),lab,font=F(20),fill=(230,248,255),anchor="mm")
    # creek label along the corridor
    dr.text(px(-117.6685,33.560),"Trabuco Creek corridor",font=F(20,False),fill=(235,235,210),anchor="lm")
    # header
    dr.rectangle([0,0,disp_w,86],fill=(0,0,0,180))
    dr.text((20,14),title,font=F(30),fill=(255,255,255))
    dr.text((20,54),subtitle,font=F(18,False),fill=(210,220,232))
    return panel

left=build_panel("1937.jpg",1500,"1937–38 · sharpest pre-development frame","OC Survey aerial · 1.15 ft/px · open cattle rangeland (dipping ended ~1917)")
right=build_panel("2022_modern.jpg",1500,"2022 · same ground today","OC 1-ft imagery · Ladera Ranch built out; west corridor kept as open space")
# match heights
h=max(left.height,right.height)
def pad(p):
    if p.height==h: return p
    c=Image.new("RGB",(p.width,h),(15,17,20)); c.paste(p,(0,0)); return c
left,right=pad(left),pad(right)

GAP=18; TOP=118; BOT=150
W=left.width+right.width+GAP; Ht=h+TOP+BOT
canvas=Image.new("RGB",(W,Ht),(20,22,26))
canvas.paste(left,(0,TOP)); canvas.paste(right,(left.width+GAP,TOP))
dr=ImageDraw.Draw(canvas,"RGBA")
# master title
dr.text((22,20),"Ladera Ranch — where a cattle dip would most plausibly have stood",font=F(34),fill=(255,255,255))
dr.text((24,64),"GRADED INFERENCE (best guess) · No dip vat was found on any aerial 1929–2022 · No soil has been tested · These are reasoned candidates, NOT located facilities",
        font=F(17,False),fill=(255,200,170))
# legend (bottom)
ly=TOP+h+14
dr.rectangle([0,TOP+h,W,Ht],fill=(0,0,0,205))
lx=26
dr.polygon([(lx+14,ly+4),(lx+30,ly+18),(lx+14,ly+32),(lx-2,ly+18)],fill=NODE+(255,),outline=(255,255,255))
dr.text((lx+42,ly+18),"A  Ranch-activity node (only 1937 structure in Zone A) — the single strongest best-guess for a working/dip site",font=F(17,False),fill=(240,240,240),anchor="lm")
ly2=ly+40
dr.ellipse([lx+2,ly2+4,lx+30,ly2+32],outline=WATER+(255,),width=4); dr.ellipse([lx+2,ly2+4,lx+30,ly2+32],fill=WATER+(70,))
dr.text((lx+42,ly2+18),"B–E  Stock-water bodies (1968 survey) — cattle concentrate at water, so ranch working pens/vats tend to sit beside them",font=F(17,False),fill=(240,240,240),anchor="lm")
ly3=ly2+40
for i,a in enumerate(range(0,360,20)):
    x=lx+16+14*math.cos(math.radians(a)); y=ly3+18+14*math.sin(math.radians(a)); dr.ellipse([x-2,y-2,x+2,y+2],fill=CORE+(255,))
dr.text((lx+42,ly3+18),"Most-probable working core — the west Trabuco corridor (node + water clustered together). Endpoint everywhere: a soil arsenic test, not yet run.",font=F(17,False),fill=(240,240,240),anchor="lm")
canvas.save(OUT,quality=90)
print("wrote",OUT,canvas.size)
