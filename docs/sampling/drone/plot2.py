# -*- coding: utf-8 -*-
import json, math
from PIL import Image, ImageDraw, ImageFont
Image.MAX_IMAGE_PIXELS=None
G=json.load(open('geo.json')); X0,X1,Y0,Y1=G['X0'],G['X1'],G['Y0'],G['Y1']
W,H,MPX=G['W'],G['H'],G['mpx']
base=Image.open('b25.jpg').convert('RGB')
FD='/System/Library/Fonts/Supplemental/'; AV='/System/Library/Fonts/Avenir Next Condensed.ttc'
def Fa(s): return ImageFont.truetype(AV,s,index=0)
def Fg(s,b=False): return ImageFont.truetype(FD+('Georgia Bold.ttf' if b else 'Georgia.ttf'),s)
def Fb(s): return ImageFont.truetype(FD+'Baskerville.ttc',s,index=1)
HEAD=420; FOOT=1460
CAN=Image.new('RGB',(W,H+HEAD+FOOT),(13,16,22))
CAN.paste(Image.blend(base,Image.new('RGB',(W,H),(8,11,18)),0.26),(0,HEAD))
ov=Image.new('RGBA',CAN.size,(0,0,0,0)); d=ImageDraw.Draw(ov)
def P(lon,lat): return ((lon-X0)/(X1-X0)*W, (1-(lat-Y0)/(Y1-Y0))*H+HEAD)
RED=(214,69,48); AMB=(240,176,42); GRN=(92,214,138); CYN=(72,206,214); WHT=(238,242,248)

ST=[('D2',-117.65492,33.55505,AMB,'1948 RANCH STRUCTURE','woodland in 1990 AND 2025 · unchanged','trail convergence beside the creek, elev 307'),
    ('D3',-117.65281,33.55857,GRN,'T6 · BELOW YOUR FIND','scrub in 1990 AND 2025 · unchanged','the slope anything from D1 drained across'),
    ('D4',-117.65992,33.54793,CYN,'T8 · CREEK CORRIDOR','unchanged · CLOSED OAK CANOPY','fly the channel and the gaps, not a grid'),
    ('D5',-117.65929,33.54763,CYN,'T2 · CREEK BENCH','unchanged · CLOSED OAK CANOPY','15 m off the drainage, on the trail'),
    ('D6',-117.66081,33.55057,AMB,'T11 + T12 · PROMOTED','unchanged · just south of the search area','the 1968 water points on this same slope'),
    ('D7',-117.65619,33.53482,GRN,'T19 · OPEN GROUND','unchanged · NO CANOPY, NOTHING BUILT','the clearest view of native grade in the set')]
EXTRA=[(-117.66048,33.55143)]
for lon,lat in EXTRA:
    x,y=P(lon,lat); d.ellipse([x-24,y-24,x+24,y+24],outline=CYN+(190,),width=7)
    d.ellipse([x-8,y-8,x+8,y+8],fill=CYN+(230,))


# ---- flight geometry: 40 m orbit ring, and the 150 m survey square where a grid is flown
import math as _m
MPX_=MPX
GRIDS={'D2','D3','D7'}
for sid,lon,lat,col,_a,_b,_c in ST:
    x,y=P(lon,lat)
    r=40.0/MPX_
    d.ellipse([x-r,y-r,x+r,y+r],outline=col+(205,),width=7)
    for i in range(8):
        th=2*_m.pi*i/8
        px_,py_=x+r*_m.sin(th), y-r*_m.cos(th)
        d.ellipse([px_-13,py_-13,px_+13,py_+13],fill=col+(235,),outline=(12,15,20,255),width=3)
    if sid in GRIDS:
        h=75.0/MPX_
        d.rectangle([x-h,y-h,x+h,y+h],outline=col+(170,),width=6)
        for li in range(6):
            yy=y-h+li*(2*h/5)
            d.line([(x-h,yy),(x+h,yy)],fill=col+(110,),width=4)

LOFF={'D5':150,'D4':-130,'D6':-40}
for sid,lon,lat,col,t1,t2,t3 in ST:
    x,y=P(lon,lat)
    d.ellipse([x-150,y-150,x+150,y+150],outline=col+(70,),width=8)
    d.ellipse([x-92,y-92,x+92,y+92],outline=col+(130,),width=9)
    d.ellipse([x-40,y-40,x+40,y+40],outline=col+(255,),width=12)
    d.ellipse([x-13,y-13,x+13,y+13],fill=col+(255,))
    f1,f2,f3,f4=Fa(92),Fa(55),Fa(44),Fg(42)
    tw=max(d.textlength(sid,font=f1),d.textlength(t1,font=f2),d.textlength(t2,font=f3),d.textlength(t3,font=f4))
    bx=x+178; by=y-112+LOFF.get(sid,0)
    if bx+tw+56>W-30: bx=x-178-tw-56
    d.rounded_rectangle([bx-26,by-20,bx+tw+30,by+268],18,fill=(10,13,19,220),outline=col+(235,),width=5)
    d.text((bx,by-8),sid,font=f1,fill=col+(255,))
    d.text((bx,by+92),t1,font=f2,fill=WHT+(250,))
    d.text((bx,by+152),t2,font=f3,fill=col+(240,))
    d.text((bx,by+204),t3,font=f4,fill=(184,194,208,235))
    d.line([(x,y),(bx-26 if bx>x else bx+tw+30,by+120)],fill=col+(150,),width=5)

# ---- the located search area, from the Home Depot landmark in the 3 Oct drone photos
SA=(-117.6618,33.5516,-117.6566,33.5566)
ax0,ay0=P(SA[0],SA[3]); ax1,ay1=P(SA[2],SA[1])
d.rectangle([ax0,ay0,ax1,ay1],outline=RED+(255,),width=11)
for i in range(0,int(ay1-ay0),46):
    d.line([(ax0,ay0+i),(ax0+min(46,ax1-ax0),ay0+i+46)],fill=RED+(42,),width=5)
hdx,hdy=P(-117.66050,33.55675)
d.ellipse([hdx-30,hdy-30,hdx+30,hdy+30],outline=(255,255,255,255),width=10)
d.ellipse([hdx-10,hdy-10,hdx+10,hdy+10],fill=(255,255,255,255))
f1,f2=Fa(54),Fg(40)
lab='HOME DEPOT, 27952 HILLCREST'; sub='the landmark in your 3 Oct photos  \u00b7  33.55675, \u2212117.66050'
tw=max(d.textlength(lab,font=f1),d.textlength(sub,font=f2))
d.rounded_rectangle([hdx-tw/2-26,hdy-152,hdx+tw/2+26,hdy-36],14,fill=(12,15,21,225),outline=(255,255,255,235),width=5)
d.text((hdx-tw/2,hdy-142),lab,font=f1,fill=(255,255,255,255))
d.text((hdx-tw/2,hdy-82),sub,font=f2,fill=(198,206,218,235))

f3,f4,f5=Fa(76),Fa(50),Fg(42)
t1='D1 SEARCH AREA \u2014 LOCATED 3 OCT'
t2='the scrub south and south-east of the Home Depot'
t3='Your photos put the structure in here. Exact point still unresolved:'
t4='the files that reached me had their EXIF stripped and were downscaled.'
bw=max(d.textlength(t1,font=f3),d.textlength(t2,font=f4),d.textlength(t3,font=f5),d.textlength(t4,font=f5))+80
bx=ax0-bw-60
if bx<40: bx=ax1+60
by=ay0+40
d.rounded_rectangle([bx,by,bx+bw,by+286],20,fill=(32,10,8,236),outline=RED+(255,),width=8)
d.text((bx+40,by+18),t1,font=f3,fill=RED+(255,))
d.text((bx+40,by+106),t2,font=f4,fill=(236,206,200,250))
d.text((bx+40,by+172),t3,font=f5,fill=(214,190,186,240))
d.text((bx+40,by+222),t4,font=f5,fill=(214,190,186,240))

# D1 note
x3,y3=P(-117.65281,33.55857)
f=Fa(80)
msg='D1 — YOUR AUGUST 2026 CONCRETE FEATURE'
s1='Ungraded open space. Not plotted: the coordinates are deliberately'
s2='not held in the project files. Fly it first light and last light.'
bw=max(d.textlength(msg,font=f),d.textlength(s1,font=Fg(48)),d.textlength(s2,font=Fg(48)))+80
bx=max(50,x3-bw-250); by=y3-400
d.rounded_rectangle([bx,by,bx+bw,by+244],20,fill=(30,10,8,232),outline=RED+(255,),width=7)
d.text((bx+40,by+20),msg,font=f,fill=RED+(255,))
d.text((bx+40,by+118),s1,font=Fg(48),fill=(228,210,206,245))
d.text((bx+40,by+172),s2,font=Fg(48),fill=(228,210,206,245))

# EXCLUSION callouts
def excl(lon,lat,title,sub):
    x,y=P(lon,lat); f1,f2=Fa(62),Fg(40)
    tw=max(d.textlength(title,font=f1),d.textlength(sub,font=f2))
    d.rounded_rectangle([x-tw/2-28,y-20,x+tw/2+28,y+124],14,fill=(46,12,10,206),outline=(150,56,44,235),width=5)
    d.text((x-tw/2,y-6),title,font=f1,fill=(236,132,112,255))
    d.text((x-tw/2,y+68),sub,font=f2,fill=(208,168,160,235))
excl(-117.6600,33.5420,'ARROYO TRABUCO GOLF CLUB — SKIP','built after 1990. Fairway, bunkers, ponds, irrigation. Nothing native survives here')
excl(-117.6530,33.5370,'GOLF + CREEK WORKS — SKIP','the 1990 impoundments are now water features')
excl(-117.6520,33.5600,'LADERA RANCH — SKIP','mass graded 1999–2003')
excl(-117.6620,33.5560,'MISSION VIEJO — SKIP','developed before 1990')

hd=ImageDraw.Draw(ov)
hd.text((64,58),'UNGRADED GROUND ONLY',font=Fb(140),fill=WHT+(255,))
hd.text((68,226),'Seven stations. Every one checked against the 1990 aerial and kept only if the ground is unchanged.',font=Fg(56),fill=(178,188,202,255))
hd.text((68,302),'LEHRP field map · 1 October 2026 · 2025 OC Survey 1 ft, filtered against OC Survey 1990 · NOT FOR PUBLICATION',font=Fa(48),fill=(150,160,176,255))
hd.line([(64,392),(W-64,392)],fill=(90,102,120,255),width=5)

sb=500/MPX; sx,sy=W-sb-130,HEAD+H-140
d.rectangle([sx,sy,sx+sb,sy+24],fill=(255,255,255,235))
d.rectangle([sx,sy,sx+sb/2,sy+24],fill=(16,20,28,235))
d.rectangle([sx,sy,sx+sb,sy+24],outline=(255,255,255,255),width=4)
d.text((sx,sy-58),'0',font=Fa(50),fill=WHT+(255,)); d.text((sx+sb-36,sy-58),'500 m',font=Fa(50),fill=WHT+(255,))
nx,ny=W-150,HEAD+170
d.polygon([(nx,ny-96),(nx-32,ny+28),(nx,ny-6),(nx+32,ny+28)],fill=WHT+(245,))
d.text((nx-17,ny+40),'N',font=Fa(64),fill=WHT+(255,))
CAN=Image.alpha_composite(CAN.convert('RGBA'),ov).convert('RGB')
CAN.save('m2.jpg',quality=93); print('ok',CAN.size)
