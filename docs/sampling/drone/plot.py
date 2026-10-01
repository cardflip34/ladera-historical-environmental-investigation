# -*- coding: utf-8 -*-
import math, json
from PIL import Image, ImageDraw, ImageFont, ImageFilter
Image.MAX_IMAGE_PIXELS=None
X0,X1,Y0,Y1=-117.6700,-117.6440,33.5300,33.5640
base=Image.open('base2025.jpg').convert('RGB'); W,H=base.size
latm=(Y0+Y1)/2
MPLON=111320*math.cos(math.radians(latm)); MPLAT=110950
MPX=(X1-X0)*MPLON/W                       # metres per pixel
def xy(lon,lat): return ((lon-X0)/(X1-X0)*W, (1-(lat-Y0)/(Y1-Y0))*H)

FD='/System/Library/Fonts/Supplemental/'
AV='/System/Library/Fonts/Avenir Next Condensed.ttc'
def Fa(s): return ImageFont.truetype(AV,s,index=0)
def Fg(s,b=False): return ImageFont.truetype(FD+('Georgia Bold.ttf' if b else 'Georgia.ttf'),s)
def Fb(s): return ImageFont.truetype(FD+'Baskerville.ttc',s,index=1)

HEAD=430; FOOT=1430
CAN=Image.new('RGB',(W,H+HEAD+FOOT),(14,17,23))
base=Image.blend(base,Image.new('RGB',(W,H),(8,11,18)),0.30)
CAN.paste(base,(0,HEAD))
ov=Image.new('RGBA',CAN.size,(0,0,0,0)); d=ImageDraw.Draw(ov)
def P(lon,lat):
    x,y=xy(lon,lat); return (x,y+HEAD)

RED=(214,69,48); AMB=(240,176,42); CYN=(64,208,214); GRN=(104,214,140); WHT=(238,242,248)

STATIONS=[
 # id, lon, lat, colour, title, oneliner
 ('D1', None, None, RED,'YOUR AUGUST FIND','concrete rectangle + iron pipe rails'),
 ('D2', -117.65492, 33.55505, AMB,'1948 RANCH STRUCTURE','building at a trail convergence, beside water, elev 307'),
 ('D3', -117.65281, 33.55857, CYN,'T6 · 9,111 m²','largest north water body; corridor below = top soil station'),
 ('D4', -117.65992, 33.54793, CYN,'T8 · 4,661 m²','never-graded slope + creek corridor'),
 ('D5', -117.65929, 33.54763, CYN,'T2 · 1,307 m²','never-graded creek bench, 15 m off the drainage'),
 ('D6', -117.66021, 33.54593, GRN,'T10 · ELONGATION 4.4','the most elongated small feature in the corridor'),
 ('D7', -117.66081, 33.55057, CYN,'T11 + T12','two small water points above the Trabuco Trail'),
 ('D8', -117.66132, 33.54394, CYN,'T13 · 24,745 m²','405 m impoundment — the catchment integrator'),
 ('D9', -117.66061, 33.54123, CYN,'T4 · 12,395 m²','second impoundment on the canyon floor'),
 ('D10',-117.65619, 33.53482, CYN,'T19','ungraded canyon south of the community'),
]
EXTRA=[(-117.66048,33.55143,'T12'),(-117.66258,33.53792,'T1')]

# ---- corridor hint: faint line down Trabuco Creek (schematic, from the station spread)
# ---- draw extra minor points
for lon,lat,lab in EXTRA:
    x,y=P(lon,lat)
    d.ellipse([x-26,y-26,x+26,y+26],outline=CYN+(180,),width=7)
    d.ellipse([x-8,y-8,x+8,y+8],fill=CYN+(220,))

def halo(x,y,r,c,a,w):
    d.ellipse([x-r,y-r,x+r,y+r],outline=c+(a,),width=w)

LOFF={'D5':120,'D4':-120,'D7':-30,'D9':90}
for sid,lon,lat,col,title,sub in STATIONS:
    if lon is None: continue
    x,y=P(lon,lat)
    halo(x,y,150,col,70,8); halo(x,y,92,col,120,9)
    d.ellipse([x-40,y-40,x+40,y+40],outline=col+(255,),width=12)
    d.ellipse([x-13,y-13,x+13,y+13],fill=col+(255,))
    f1=Fa(96); f2=Fa(58); f3=Fg(46)
    tw=max(d.textlength(sid,font=f1), d.textlength(title,font=f2), d.textlength(sub,font=f3))
    bx=x+176; by=y-104+LOFF.get(sid,0)
    if bx+tw+54>W-40: bx=x-176-tw-54
    d.rounded_rectangle([bx-26,by-20,bx+tw+30,by+232],18,fill=(10,13,19,214),outline=col+(230,),width=5)
    d.text((bx,by-6),sid,font=f1,fill=col+(255,))
    d.text((bx,by+96),title,font=f2,fill=WHT+(248,))
    d.text((bx,by+154),sub,font=f3,fill=(186,196,210,235))
    d.line([(x,y),(bx-26 if bx>x else bx+tw+30, by+94)],fill=col+(150,),width=5)

# ---- D1 guidance arrow: from D3 toward upslope open space
x3,y3=P(-117.65281,33.55857)
f=Fa(84); msg='D1  —  YOUR AUGUST 2026 CONCRETE FEATURE'
sub1='Coordinates are deliberately not held in the project files.'
sub2='You know the ground. Fly it FIRST, in the first light of the day.'
bw=max(d.textlength(msg,font=f),d.textlength(sub1,font=Fg(50)),d.textlength(sub2,font=Fg(50)))+80
bx,by=x3-bw-240, y3-430
if bx<60: bx=60
d.rounded_rectangle([bx,by,bx+bw,by+250],20,fill=(28,10,8,230),outline=RED+(255,),width=7)
d.text((bx+40,by+22),msg,font=f,fill=RED+(255,))
d.text((bx+40,by+124),sub1,font=Fg(50),fill=(226,208,204,240))
d.text((bx+40,by+180),sub2,font=Fg(50),fill=(226,208,204,240))

# ---- header
hd=ImageDraw.Draw(ov)
hd.text((70,62),'ARROYO TRABUCO — DRONE RECONNAISSANCE',font=Fb(132),fill=WHT+(255,))
hd.text((74,224),'Ten stations, ranked. What to look for at each, and what would rule it out.',font=Fg(60),fill=(176,186,200,255))
hd.text((74,306),'LEHRP field map · 1 October 2026 · Base: OC Survey 2025 countywide aerial, 1 ft · '
                 'NOT FOR PUBLICATION — contains locational data',font=Fa(50),fill=(150,160,176,255))
hd.line([(70,400),(W-70,400)],fill=(90,102,120,255),width=5)

# ---- scale bar + north
sb_m=500; sb_px=sb_m/MPX
sx,sy=W-sb_px-150, HEAD+H-150
d.rectangle([sx,sy,sx+sb_px,sy+26],fill=(255,255,255,235))
d.rectangle([sx,sy,sx+sb_px/2,sy+26],fill=(16,20,28,235))
d.rectangle([sx,sy,sx+sb_px,sy+26],outline=(255,255,255,255),width=4)
d.text((sx,sy-62),'0',font=Fa(52),fill=WHT+(255,))
d.text((sx+sb_px-40,sy-62),'500 m',font=Fa(52),fill=WHT+(255,))
nx,ny=W-170,HEAD+190
d.polygon([(nx,ny-100),(nx-34,ny+30),(nx,ny-6),(nx+34,ny+30)],fill=WHT+(245,))
d.text((nx-18,ny+42),'N',font=Fa(68),fill=WHT+(255,))

CAN=Image.alpha_composite(CAN.convert('RGBA'),ov).convert('RGB')
CAN.save('map_layer1.jpg',quality=93)
print('layer1',CAN.size,'m/px',round(MPX,3))
