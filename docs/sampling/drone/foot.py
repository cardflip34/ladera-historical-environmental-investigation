# -*- coding: utf-8 -*-
from PIL import Image, ImageDraw, ImageFont
Image.MAX_IMAGE_PIXELS=None
im=Image.open('map_layer1.jpg').convert('RGB'); W,H=im.size
d=ImageDraw.Draw(im)
FD='/System/Library/Fonts/Supplemental/'; AV='/System/Library/Fonts/Avenir Next Condensed.ttc'
def Fa(s): return ImageFont.truetype(AV,s,index=0)
def Fg(s,b=False): return ImageFont.truetype(FD+('Georgia Bold.ttf' if b else 'Georgia.ttf'),s)
RED=(214,69,48); AMB=(240,176,42); CYN=(64,208,214); WHT=(238,242,248); MUT=(168,178,194)
FY=H-1430
d.rectangle([0,FY,W,H],fill=(14,17,23))
d.line([(70,FY+30),(W-70,FY+30)],fill=(90,102,120),width=5)
def wrap(t,f,mw):
    out=[];cur=''
    for w_ in t.split():
        c=(cur+' '+w_).strip()
        if d.textlength(c,font=f)<=mw: cur=c
        else: out.append(cur); cur=w_
    if cur: out.append(cur)
    return out
def col(x,y,mw,head,hc,items):
    d.text((x,y),head,font=Fa(56),fill=hc); yy=y+78
    for it in items:
        bullet = it.startswith('•')
        f=Fg(42)
        for i,ln in enumerate(wrap(it,f,mw)):
            d.text((x+(0 if i==0 else 26),yy),ln,font=f,fill=WHT if bullet else MUT)
            yy+=54
        yy+=12
    return yy
CW=(W-200-120)/3
c1,c2,c3=100,100+CW+60,100+2*(CW+60)
col(c1,FY+78,CW,'WHAT A DIPPING STATION LOOKS LIKE FROM 200 FEET',RED,[
 '• A narrow rectangle about 8 m long overall. USDA Circular 183 specifies 26 ft at the top of the vat, 12 ft at the bottom — your August floor measured about 12 ft.',
 '• A WIDER APRON at one end. The drip pen, two to four times the vat width, sloping back so the dip drained in. This is usually the largest surviving concrete.',
 '• A FUNNEL of pen lines converging on the entrance, fed by a straight narrow alley.',
 '• Often cut into a low bank so cattle entered at grade and climbed out a ramp.',
 '• Water within about 30 m. Every station needed it.',
 '• A bare or stunted vegetation patch that does not match slope or aspect — early October is the best soil-mark season of the year.'])
col(c2,FY+78,CW,'WHAT WOULD RULE IT OUT — SHOOT FOR THIS TOO',AMB,[
 'The point of the flight is to let the plan form decide, so photograph whatever is there rather than only what fits.',
 '• Shallow, open, with a pipe inlet and no ramp — a water trough.',
 '• Circular or square pad, anchor bolts, no apron — a tank base.',
 '• Walls on four sides with a doorway — a building foundation.',
 '• No ramp, no apron, no pen lines anywhere around it — probably not a dipping station at all.',
 'A negative that is well photographed is worth as much as a positive. It closes the question instead of leaving it open.'])
col(c3,FY+78,CW,'HOW TO SHOOT IT',CYN,[
 '• NADIR GRID at 60 m (200 ft), 75% front and 65% side overlap. That gives a measurable orthomosaic at roughly 1.5 cm/px — you can take dimensions off it later.',
 '• LOW OBLIQUES at 10–20 m from all four sides, about 35° down.',
 '• TWO SUN ANGLES, same ground. Shadow marks reverse between morning and evening and a feature invisible in one is obvious in the other. Today: before about 08:15, and after about 17:00.',
 '• RAW plus JPEG. Geotags ON. Note the clock time of each flight.',
 '• Put a 1 m scale object in at least one frame at D1.'])
# bottom rule bar
BY=H-370
d.rectangle([70,BY,W-70,H-40],fill=(26,10,8),outline=RED,width=5)
d.text((110,BY+26),'BEFORE YOU LAUNCH',font=Fa(50),fill=RED)
t1='Check B4UFLY or your LAANC app for airspace at the launch point — do not assume this corridor is uncontrolled. Stay at or below 400 ft AGL, keep visual line of sight, and do not fly over people.'
t2='Orange County Parks and the City of Mission Viejo both restrict launching and landing on their open space without a permit; the Arroyo Trabuco Golf Club and the Rancho Mission Viejo land east of the corridor are private. Launch from public right-of-way, or with permission. October is fire season — check for red-flag closures before you drive out.'
y=BY+90
for t in (t1,t2):
    for ln in wrap(t,Fg(40),W-260):
        d.text((110,y),ln,font=Fg(40),fill=(224,210,206)); y+=50
    y+=8
im.save('/Users/andystavros/Desktop/Ladera_Drone_Recon_Map.jpg',quality=92)
im.resize((W//6,H//6),Image.LANCZOS).save('prev2.jpg',quality=88)
print('saved',im.size)
