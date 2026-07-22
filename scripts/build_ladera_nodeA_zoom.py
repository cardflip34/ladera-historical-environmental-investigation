#!/usr/bin/env python3
"""Node A zoom — the single 1937 ranch structure inside the Ladera footprint, at full native resolution,
then the same ground in 2022 (preserved Trabuco greenbelt). This is the strongest single best-guess for a
ranch working / dip location. GRADED INFERENCE: it is a structure, NOT an identified vat; no soil tested."""
import os, math
from PIL import Image, ImageDraw, ImageFont
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AER=os.path.join(ROOT,"research/historical_imagery/oc_aerials")
OUT=os.path.join(ROOT,"research/ladera/imagery/ladera_nodeA_zoom_thennow.jpg")
WLON,ELON,SLAT,NLAT=-117.68,-117.616,33.52,33.575
NLAT_A,NLON_A=33.55505,-117.65492
CW0,CE0,CS0,CN0=-117.6587,-117.6511,33.5519,33.5582   # ~700 m box around node A

def F(sz,b=True):
    p="/System/Library/Fonts/Supplemental/Arial Bold.ttf" if b else "/System/Library/Fonts/Supplemental/Arial.ttf"
    try: return ImageFont.truetype(p,sz)
    except: return ImageFont.load_default()

def panel(fname, dw, title, sub, ring):
    im=Image.open(os.path.join(AER,fname)).convert("RGB"); W,H=im.size
    def gx(lon): return (lon-WLON)/(ELON-WLON)*W
    def gy(lat): return (NLAT-lat)/(NLAT-SLAT)*H
    x0,x1=gx(CW0),gx(CE0); y0,y1=gy(CN0),gy(CS0)
    crop=im.crop((int(x0),int(y0),int(x1),int(y1))); cw,ch=crop.size
    s=dw/cw; dh=int(ch*s); p=crop.resize((dw,dh)); dr=ImageDraw.Draw(p,"RGBA")
    ax=(gx(NLON_A)-x0)*s; ay=(gy(NLAT_A)-y0)*s
    if ring:  # circle the structure on 1937
        r=42
        dr.ellipse([ax-r,ay-r,ax+r,ay+r],outline=(255,80,70,255),width=5)
        dr.text((ax,ay-r-10),"only structure in Zone A (1937)",font=F(19),fill=(255,210,205),anchor="mb")
    else:
        r=17
        dr.polygon([(ax,ay-r-5),(ax+r+3,ay),(ax,ay+r+5),(ax-r-3,ay)],fill=(228,60,54,235),outline=(255,255,255))
        dr.text((ax,ay-r-10),"same spot — now greenbelt",font=F(19),fill=(255,210,205),anchor="mb")
    # ~100 m scale bar
    mppx=(111320*(CE0-CW0)*math.cos(math.radians(33.55)))/dw   # meters per display px
    barpx=100/mppx
    bx,by=28,dh-40
    dr.rectangle([bx,by,bx+barpx,by+7],fill=(255,255,255,235)); dr.text((bx,by-19),"100 m",font=F(16),fill=(255,255,255))
    dr.rectangle([0,0,dw,74],fill=(0,0,0,180))
    dr.text((16,10),title,font=F(26),fill=(255,255,255)); dr.text((16,46),sub,font=F(15,False),fill=(215,222,232))
    return p

L=panel("1937.jpg",1300,"1937–38  ·  node A at full resolution","OC Survey 1.15 ft/px — structure on the Trabuco corridor amid open rangeland",True)
R=panel("2022_modern.jpg",1300,"2022  ·  the same ground","preserved open space between Ladera villages — NOT under houses",False)
h=max(L.height,R.height)
def padH(p):
    if p.height==h: return p
    c=Image.new("RGB",(p.width,h),(15,17,20)); c.paste(p,(0,0)); return c
L,R=padH(L),padH(R)
GAP=16; TOP=98; BOT=78; Wt=L.width+R.width+GAP; Ht=h+TOP+BOT
cv=Image.new("RGB",(Wt,Ht),(20,22,26)); cv.paste(L,(0,TOP)); cv.paste(R,(L.width+GAP,TOP))
dr=ImageDraw.Draw(cv,"RGBA")
dr.text((20,16),"Ladera Ranch — node A close-up (the strongest single best-guess)",font=F(31),fill=(255,255,255))
dr.text((22,58),"GRADED INFERENCE · This is the one man-made structure resolvable in Zone A on the 1937 frame — a ranch-activity node, NOT an identified dip vat. No soil tested.",font=F(16,False),fill=(255,200,170))
dr.rectangle([0,Ht-BOT,Wt,Ht],fill=(0,0,0,200))
dr.text((20,Ht-BOT+27),"Why it matters: a ranch's dip vat sat at its central working corral — the likeliest spot here — and this node is preserved open space, so the ground is intact and testable.  Coordinates held at node level only; no residential address implied.  Imagery: OC Survey.",
        font=F(14,False),fill=(215,220,228),anchor="lm")
cv.save(OUT,quality=92); print("wrote",OUT,cv.size)
