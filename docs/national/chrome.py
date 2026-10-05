# -*- coding: utf-8 -*-
import json, collections
from PIL import Image, ImageDraw, ImageFont
im=Image.open('natmap_base.jpg').convert('RGB'); W,H=im.size
d=ImageDraw.Draw(im,'RGBA')
FD='/System/Library/Fonts/Supplemental/'; AV='/System/Library/Fonts/Avenir Next Condensed.ttc'
def Fa(s): return ImageFont.truetype(AV,s,index=0)
def Fg(s,b=False): return ImageFont.truetype(FD+('Georgia Bold.ttf' if b else 'Georgia.ttf'),s)
def Fb(s): return ImageFont.truetype(FD+'Baskerville.ttc',s,index=1)
INK=(22,32,46); MUT=(112,120,134); QEDGE=(176,86,66); VRED=(188,54,36); BLUE=(31,78,121); LINE=(206,202,192)
M=110
# header
d.rectangle([0,0,W,300],fill=(247,246,242))
d.text((M,56),'WHERE THE DIPPING HAPPENED',font=Fb(132),fill=INK)
d.text((M+6,214),'The federal cattle-fever tick eradication programme, and 1,918 dipping vats destroyed by the people who lived under it',font=Fg(44),fill=MUT)
d.line([(M,296),(W-M,296)],fill=LINE,width=4)
vats=json.load(open('vats_clean.json'))
for v in vats: v['state']=(v['state'] or '').strip()
BY=collections.Counter(); REC=collections.Counter()
for v in vats:
    try: n=int(v['n'])
    except: n=0
    BY[v['state']]+=n; REC[v['state']]+=1
# footer
FY=H-700
d.rectangle([0,FY,W,H],fill=(247,246,242))
d.line([(M,FY+16),(W-M,FY+16)],fill=LINE,width=4)
y=FY+54
def para(t,x,y,mw,fo,fill,lh):
    out=[];cur=''
    for w_ in t.split():
        c=(cur+' '+w_).strip()
        if d.textlength(c,font=fo)<=mw: cur=c
        else: out.append(cur); cur=w_
    if cur: out.append(cur)
    for ln in out: d.text((x,y),ln,font=fo,fill=fill); y+=lh
    return y
CW=(W-2*M-200)/3
# col 1 legend
d.text((M,y),'HOW TO READ IT',font=Fa(50),fill=QEDGE)
yy=y+70
d.rectangle([M,yy+6,M+58,yy+42],fill=(242,224,214),outline=QEDGE,width=4)
para('The fifteen states of the quarantined area, where dipping was compulsory.',M+78,yy,CW-90,Fg(33),INK,42)
yy+=100
d.ellipse([M+14,yy+8,M+44,yy+38],fill=VRED+(180,),outline=(255,255,255,220),width=3)
para('A place where vats were dynamited. The circle is sized by how many were destroyed there.',M+78,yy,CW-90,Fg(33),INK,42)
yy+=108
d.ellipse([M+8,yy+2,M+50,yy+44],outline=BLUE,width=7)
para('Orange County, California — the ground this project has been working.',M+78,yy,CW-90,Fg(33),INK,42)
# col 2 the fifteen
x2=M+CW+100
d.text((x2,y),'THE FIFTEEN STATES, AND WHERE THAT NUMBER COMES FROM',font=Fa(50),fill=QEDGE)
yy=para('Fourteen are named in one sentence of the Bureau of Animal Industry’s own report for the fiscal year 1907:',x2,y+70,CW,Fg(33),INK,42)
yy=para('“the work of eradicating cattle ticks has been pursued … in the States of Virginia, North Carolina, South '
        'Carolina, Georgia, Alabama, Tennessee, Kentucky, Arkansas, Texas, Missouri, California, Louisiana, and the '
        'Territory of Oklahoma” — with Mississippi named in the same report.',x2,yy+10,CW,Fg(32),(70,80,96),41)
para('Florida is the fifteenth, and is evidenced separately: its own state register lists 3,281 vats.',x2,yy+12,CW,Fg(33),INK,42)
# col 3 caveat + counts
x3=M+2*(CW+100)
d.text((x3,y),'WHAT THIS MAP IS NOT',font=Fa(50),fill=VRED)
yy=para('It is not an inventory of dipping vats. The red dots are only vats that somebody blew up and somebody else '
        'wrote down — 1,918 of them across 328 incidents, 1911 to 1936, in nine states.',x3,y+70,CW,Fg(33),INK,42)
yy=para('The real number built was far larger and mostly unrecorded. Florida alone holds 3,281 in a register; '
        'California, where vats were built by individual ranchers from a mailed circular, has no register at all.',x3,yy+10,CW,Fg(33),(70,80,96),41)
para('Absence of a dot means absence of a record, not absence of a vat.',x3,yy+12,CW,Fg(33,True) if False else Fg(33),VRED,42)
# counts strip
cy=H-176
d.line([(M,cy-22),(W-M,cy-22)],fill=LINE,width=3)
d.text((M,cy),'VATS DESTROYED, BY STATE',font=Fa(42),fill=MUT)
xx=M+520
for s,n in BY.most_common():
    if not s: continue
    ab={'Alabama':'AL','Mississippi':'MS','Arkansas':'AR','Louisiana':'LA','Texas':'TX','Oklahoma':'OK',
        'Georgia':'GA','North Carolina':'NC','Florida':'FL'}.get(s,s[:2].upper())
    d.text((xx,cy-10),ab,font=Fa(46),fill=INK)
    d.text((xx,cy+36),str(n),font=Fg(36),fill=VRED)
    xx+=175
d.text((W-M-760,cy+2),'Sources: Dynamited Dipping Vats in the War for the Southern Range,',font=Fg(27),fill=MUT)
d.text((W-M-760,cy+38),'W&M (328 records). USDA BAI, Operations for FY1907. Florida DEP',font=Fg(27),fill=MUT)
d.text((W-M-760,cy+74),'records response, 3,281 vats. Compiled 5 October 2026 · LEHRP',font=Fg(27),fill=MUT)
im.save('/Users/andystavros/Desktop/Dipping_Vats_National_Map.jpg',quality=93)
im.resize((W//4,H//4),Image.LANCZOS).save('prev2.jpg',quality=90)
print('saved',im.size)
