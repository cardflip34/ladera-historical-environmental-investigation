# -*- coding: utf-8 -*-
import json, math
from PIL import Image, ImageDraw, ImageFont
Image.MAX_IMAGE_PIXELS=None
X0,Y0,X1,Y1=-117.6760,33.5195,-117.6195,33.5745
base=Image.open("tmap/base.jpg").convert("RGB"); W,H=base.size
FD="/System/Library/Fonts/Supplemental/"
def F(s,b=False): return ImageFont.truetype(FD+("Arial Bold" if b else "Arial")+".ttf",s)
def xy(lon,lat): return ((lon-X0)/(X1-X0)*W,(1-(lat-Y0)/(Y1-Y0))*H)

T=json.load(open("/Users/andystavros/Ladera-Ranch/docs/sampling/targets_data.json"))
LOFF=json.load(open("tmap/loff.json"))
ROLE={"preserved":("UNDISTURBED",(80,215,140)),"open_rmv":("UNDISTURBED",(80,215,140)),
 "graded_ladera":("FILL OVER SOURCE",(190,130,240)),
 "golf":("SOURCE AREA",(250,175,45)),"golf_edge":("SOURCE AREA",(250,175,45)),
 "pre1990":("SOURCE AREA",(250,175,45)),"pre1990_edge":("SOURCE AREA",(250,175,45)),
 "rmv_new":("SOURCE AREA",(250,175,45))}

# water + sediment points (APPROXIMATE - schematic positions along the documented route)
WATER=[("W1",-117.6395,33.5735,"Horno upstream"),
       ("W2",-117.6505,33.5330,"Basin outlet"),
       ("W3",-117.6545,33.5268,"Wetland outlet"),
       ("W4",-117.6640,33.5560,"Pre-blend effluent"),
       ("W5",-117.6420,33.5615,"Post-blend storage"),
       ("W6",-117.6330,33.5520,"Sprinkler head"),
       ("W7",-117.6500,33.5360,"Irrigation return")]
SED=[("S1",-117.6515,33.5305,"Basin sediment core"),
     ("S2",-117.6550,33.5272,"Wetland sediment")]
LM=[(-117.6625,33.5790,"Arroyo Trabuco Golf Club"),
    (-117.6455,33.5540,"Ladera Ranch town centre"),
    (-117.6320,33.5490,"Ladera Ranch core"),
    (-117.6580,33.5230,"Oso Grande school site"),
    (-117.6250,33.5300,"open Rancho Mission Viejo")]

ov=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov)
base=Image.blend(base,Image.new("RGB",(W,H),(10,14,22)),0.16)

def halo(x,y,r,col,a=70):
    d.ellipse([x-r,y-r,x+r,y+r],outline=col+(a,),width=6)

# landmarks first (under)
for lon,lat,lab in LM:
    x,y=xy(lon,lat); f=F(52,True); tw=d.textlength(lab,font=f)
    d.rectangle([x-tw/2-16,y-34,x+tw/2+16,y+34],fill=(0,0,0,165))
    d.text((x-tw/2,y-26),lab,font=f,fill=(232,236,244,235))

# soil targets
for t in T:
    lab,col=ROLE.get(t["class"],("SOURCE AREA",(250,175,45)))
    ox,oy=xy(t["lon"],t["lat"])
    rec=t.get("rec") or {}
    halo(ox,oy,64,col,80)
    d.ellipse([ox-9,oy-9,ox+9,oy+9],fill=col+(150,))
    if rec.get("lat"):
        rx,ry=xy(rec["lon"],rec["lat"])
        if abs(rx-ox)+abs(ry-oy)>8: d.line([(ox,oy),(rx,ry)],fill=col+(210,),width=5)
        d.ellipse([rx-24,ry-24,rx+24,ry+24],outline=col+(255,),width=8)
        d.ellipse([rx-9,ry-9,rx+9,ry+9],fill=col+(255,))
        f=F(58,True); s="T%02d"%t["n"]; tw=d.textlength(s,font=f)
        oy2=LOFF.get(str(t["n"]),0)
        if oy2: d.line([(rx+26,ry),(rx+34,ry+oy2)],fill=col+(180,),width=3)
        d.rectangle([rx+32,ry-34+oy2,rx+32+tw+22,ry+34+oy2],fill=(0,0,0,215))
        d.text((rx+43,ry-26+oy2),s,font=f,fill=col+(255,))

# water points
for cd,lon,lat,lab in WATER:
    x,y=xy(lon,lat); col=(70,200,235)
    d.rectangle([x-30,y-30,x+30,y+30],outline=col+(255,),width=8)
    d.line([(x-12,y),(x+12,y)],fill=col+(255,),width=6)
    f=F(58,True); s="%s %s"%(cd,lab); tw=d.textlength(s,font=f)
    d.rectangle([x+40,y-34,x+40+tw+22,y+34],fill=(0,0,0,215))
    d.text((x+51,y-26),s,font=f,fill=col+(255,))
# sediment
for cd,lon,lat,lab in SED:
    x,y=xy(lon,lat); col=(235,90,80)
    d.polygon([(x,y-34),(x+32,y+24),(x-32,y+24)],outline=col+(255,))
    d.polygon([(x,y-34),(x+32,y+24),(x-32,y+24)],fill=col+(110,))
    f=F(58,True); s="%s %s"%(cd,lab); tw=d.textlength(s,font=f)
    d.rectangle([x+44,y-34,x+44+tw+22,y+34],fill=(0,0,0,215))
    d.text((x+55,y-26),s,font=f,fill=col+(255,))

base.paste(ov,(0,0),ov)
STRIP=620
canvas=Image.new("RGB",(W,H+STRIP),(8,11,18))
canvas.paste(base,(0,0))
base=canvas
d2=ImageDraw.Draw(base,"RGBA")
# legend
lw,lh=1520,560
LX,LY=60,H+30
d2.line([(0,H+4),(W,H+4)],fill=(255,255,255,90),width=6)
d2.text((LX+10,LY+25),"LADERA RANCH — RECOMMENDED TESTING LOCATIONS",font=F(64,True),fill=(255,255,255))
d2.text((LX+10,LY+100),"Base: Orange County aerial imagery, 2022   ·   23 soil targets, 7 water points, 2 sediment points",font=F(40),fill=(185,196,214))
rows=[((250,175,45),"circle","SOURCE AREA — historic water point (11)"),
      ((190,130,240),"circle","FILL OVER SOURCE — now under Ladera fill (7)"),
      ((80,215,140),"circle","UNDISTURBED / CONTROL — never graded (7)"),
      ((70,200,235),"square","WATER — purple-pipe loop, W1–W7"),
      ((235,90,80),"tri","SEDIMENT — S1 basin core, S2 wetland")]
yy=LY+150
for ri,(col,shape,lab) in enumerate(rows):
    colx = LX+10 if ri<3 else LX+1700
    yy2 = LY+150+(ri%3)*90
    cx,cy=colx+60,yy2+26
    if shape=="circle":
        d2.ellipse([cx-24,cy-24,cx+24,cy+24],outline=col+(255,),width=8)
        d2.ellipse([cx-8,cy-8,cx+8,cy+8],fill=col+(255,))
    elif shape=="square":
        d2.rectangle([cx-24,cy-24,cx+24,cy+24],outline=col+(255,),width=8)
        d2.line([(cx-10,cy),(cx+10,cy)],fill=col+(255,),width=6)
    else:
        d2.polygon([(cx,cy-28),(cx+26,cy+20),(cx-26,cy+20)],outline=col+(255,))
        d2.polygon([(cx,cy-28),(cx+26,cy+20),(cx-26,cy+20)],fill=col+(110,))
    d2.text((colx+120,yy2),lab,font=F(44,True),fill=col)
d2.text((LX+10,LY+430),"Faint halo = original 1968 water body.   Solid ring = recommended sample point.",font=F(38),fill=(185,196,214))
d2.text((LX+10,LY+485),"Water and sediment positions are APPROXIMATE, placed on the documented route.   Establishes no contamination; no location here is a known vat site.",font=F(38),fill=(250,175,45))
# scale bar
m=1000.0
dx=m/(111320.0*math.cos(math.radians(33.55)))
px=dx/(X1-X0)*W
sx,sy=W-px-220,H-170
d2.rectangle([sx,sy,sx+px,sy+26],fill=(255,255,255,235),outline=(0,0,0,220),width=3)
d2.text((sx,sy-62),"1 km",font=F(52,True),fill=(255,255,255))

base.save("tmap/Ladera_Testing_Map.jpg",quality=90)
print("saved",base.size)
base.resize((1400,int(1400*base.height/base.width)),Image.LANCZOS).save("tmap/view.jpg",quality=86)
