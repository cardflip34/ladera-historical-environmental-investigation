# -*- coding: utf-8 -*-
import json
from PIL import Image, ImageDraw, ImageFont
Image.MAX_IMAGE_PIXELS=None
G=json.load(open('geo.json')); X0,X1,Y0,Y1=G['X0'],G['X1'],G['Y0'],G['Y1']; BW,BH=G['W'],G['H']
im=Image.open('m2.jpg').convert('RGB'); W,H=im.size
b90=Image.open('b90.jpg'); b25=Image.open('b25.jpg')
d=ImageDraw.Draw(im)
FD='/System/Library/Fonts/Supplemental/'; AV='/System/Library/Fonts/Avenir Next Condensed.ttc'
def Fa(s): return ImageFont.truetype(AV,s,index=0)
def Fg(s): return ImageFont.truetype(FD+'Georgia.ttf',s)
RED=(214,69,48); AMB=(240,176,42); CYN=(72,206,214); WHT=(238,242,248); MUT=(170,180,196)
FY=H-1460
d.rectangle([0,FY,W,H],fill=(13,16,22))
d.line([(64,FY+24),(W-64,FY+24)],fill=(90,102,120),width=5)
def wrap(t,f,mw):
    out=[];cur=''
    for w_ in t.split():
        c=(cur+' '+w_).strip()
        if d.textlength(c,font=f)<=mw: cur=c
        else: out.append(cur); cur=w_
    if cur: out.append(cur)
    return out

# --- then/now strip proving the cuts
def xy(lon,lat): return int((lon-X0)/(X1-X0)*BW), int((1-(lat-Y0)/(Y1-Y0))*BH)
CUTS=[('T10',-117.66021,33.54593),('T13',-117.66132,33.54394),('T1',-117.66258,33.53792)]
d.text((64,FY+64),'WHY THE GOLF STATIONS ARE GONE  —  1990 LEFT, 2025 RIGHT',font=Fa(54),fill=RED)
S=260; R=360; px=64
for n,lon,lat in CUTS:
    x,y=xy(lon,lat)
    box=(max(0,x-R),max(0,y-R),min(BW,x+R),min(BH,y+R))
    im.paste(b90.crop(box).resize((S,S),Image.LANCZOS),(px,FY+140))
    im.paste(b25.crop(box).resize((S,S),Image.LANCZOS),(px+S+4,FY+140))
    d.rectangle([px,FY+140,px+2*S+4,FY+140+S],outline=(150,56,44),width=4)
    d.text((px,FY+140+S+12),n+'  ·  open ground, then golf',font=Fa(42),fill=(224,150,132))
    px+=2*S+56
tx=px+20; mw=W-tx-80
yy=FY+150
for ln in wrap('These three stations were on the 1990 list because the 1968 USGS survey put stock water there. '
               'They are off this map because the ground they sat on no longer exists: it was cut, filled, shaped and planted '
               'when the course was built after 1990. Photographing a fairway tells you about the fairway.',Fg(44),mw):
    d.text((tx,yy),ln,font=Fg(44),fill=MUT); yy+=58
yy+=18
for ln in wrap('The same reasoning removes every station that now sits under Ladera housing, and every one in Mission Viejo, '
               'which was developed before 1990.',Fg(44),mw):
    d.text((tx,yy),ln,font=Fg(44),fill=MUT); yy+=58

# --- bottom guidance
GY=FY+620
d.line([(64,GY-14),(W-64,GY-14)],fill=(60,70,86),width=4)
CW=(W-128-100)/3
def col(x,head,hc,items):
    d.text((x,GY+14),head,font=Fa(50),fill=hc); y=GY+82
    for it in items:
        for i,ln in enumerate(wrap(it,Fg(40),CW)):
            d.text((x+(0 if i==0 else 24),y),ln,font=Fg(40),fill=WHT if it.startswith('•') else MUT); y+=52
        y+=10
col(64,'FLY IN THIS ORDER',RED,[
 '• D1 at first light — nadir grid, then obliques from four sides.',
 '• D2 and D3 next, while the sun is still low.',
 '• D7 in the middle of the day. It is open ground with no canopy, so it photographs well in flat light when nothing else does.',
 '• D4, D5, D6 after that — and read the canopy note.',
 '• D1 again after about 17:00. Same altitude, same track. The two sun angles are the comparison.'])
col(64+CW+50,'THE CANOPY PROBLEM',CYN,[
 'D4 and D5 sit under closed oak. A drone over closed canopy photographs treetops, and the ground stays invisible.',
 '• Do not waste a mapping grid there.',
 '• Fly the open channel and the gaps between crowns, low and slow.',
 '• Shoot obliques from outside the canopy edge, looking in under the branches.',
 '• D3 and D7 are scrub and open ground. That is where a nadir grid actually earns its battery.'])
col(64+2*(CW+50),'WHAT YOU ARE LOOKING FOR',AMB,[
 '• A narrow rectangle about 8 m long — USDA Circular 183 gives 26 ft at the top of the vat, 12 ft at the bottom.',
 '• A wider apron at one end sloping back toward it. That is the drip pen, and it is usually the largest surviving concrete.',
 '• A funnel of pen lines converging on the entrance.',
 '• A bare or stunted patch that slope and aspect do not explain.',
 'Rule-outs, shot just as carefully: a shallow basin with a pipe inlet is a trough; a pad with anchor bolts is a tank base; walls and a doorway are a building.'])

BY=H-250
d.rectangle([64,BY,W-64,H-40],fill=(28,10,8),outline=RED,width=5)
d.text((104,BY+22),'BEFORE YOU LAUNCH',font=Fa(46),fill=RED)
y=BY+82
for t in ['Check airspace at the launch point. At or below 400 ft AGL, visual line of sight, not over people.',
          'OC Parks and Mission Viejo restrict launching on their open space without a permit; the golf club and the RMV land east of the corridor are private. Launch from public right-of-way. October is fire season. Do not dig or probe anything — if the feature is what it might be, the soil is the evidence.']:
    for ln in wrap(t,Fg(38),W-240): d.text((104,y),ln,font=Fg(38),fill=(224,210,206)); y+=48
im.save('/Users/andystavros/Desktop/Ladera_Drone_Ungraded_Map.jpg',quality=92)
w=2300; im.resize((w,int(H*w/W)),Image.LANCZOS).save('/Users/andystavros/Desktop/Ladera_Drone_Ungraded_Map_phone.jpg',quality=88)
im.resize((W//6,H//6),Image.LANCZOS).save('prev3.jpg',quality=88)
print('saved',im.size)
