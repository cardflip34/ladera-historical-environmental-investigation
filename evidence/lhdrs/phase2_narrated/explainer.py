import numpy as np, subprocess, math, os, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter
W,H=1080,1920; FPS=24; DUR=65.04; N=int(round(DUR*FPS))
FD="/System/Library/Fonts/Supplemental/"
def F(n,s): return ImageFont.truetype(FD+n,s)
GB=lambda s:F("Georgia Bold.ttf",s); GR=lambda s:F("Georgia.ttf",s); AB=lambda s:F("Arial Bold.ttf",s); AR=lambda s:F("Arial.ttf",s)
BG=(12,16,24); AMB=(240,196,120); INK=(232,234,238); MUT=(150,156,166); RED=(196,58,44); CYN=(150,220,255)
def ss(a,b,x):
    t=min(max((x-a)/(b-a),0),1); return t*t*(3-2*t)
def eo(a,b,x):  # ease-out
    t=min(max((x-a)/(b-a),0),1); return 1-(1-t)**3
def fmt(n): return f"{int(round(n)):,}"
random.seed(3)
STARS=[(random.uniform(0,W),random.uniform(0,H),random.uniform(0.3,1.0)) for _ in range(140)]
PH=Image.open("/private/tmp/claude-501/-Users-andystavros-Ladera-Ranch/11a645e3-0e32-4153-b26f-2484e88c6e14/scratchpad/vatvid/IMG_4497_1080.jpg").convert("RGB")
def header(d,t,kicker):
    d.text((W/2,150),"PHASE 2 · THE RECORD AND THE ARITHMETIC",font=AB(26),fill=AMB,anchor="ma")
    d.text((W/2,195),"every figure quoted or derived from documented sources · model estimates labeled",font=AR(22),fill=MUT,anchor="ma")
    if kicker: d.text((W/2,300),kicker,font=GB(56),fill=INK,anchor="ma")
def counter(d,x,y,val,font,fill,suffix="",prefix=""):
    d.text((x,y),f"{prefix}{fmt(val)}{suffix}",font=font,fill=fill,anchor="ma")
def bar(d,x,y,w,h,frac,col,track=(28,34,46)):
    d.rounded_rectangle([x,y,x+w,y+h],h//2,fill=track)
    if frac>0: d.rounded_rectangle([x,y,x+max(h,w*frac),y+h],h//2,fill=col)
def sack(d,x,y,s,a=255):
    col=(150,118,72,a); d.rounded_rectangle([x,y,x+s,y+s*1.25],s*0.18,fill=col,outline=(90,68,40,a),width=2)
    d.rounded_rectangle([x+s*0.2,y-s*0.12,x+s*0.8,y+s*0.1],s*0.1,fill=(120,92,56,a))
    d.text((x+s/2,y+s*0.45),"8 lb",font=AB(int(s*0.28)),fill=(30,22,12,a),anchor="ma")
def scene_record(im,d,u):   # 0 - 14
    header(d,u,"THE RECORD")
    d.text((W/2,380),"is not a rumor",font=GR(38),fill=MUT,anchor="ma")
    # document card
    y0=470; d.rounded_rectangle([70,y0,W-70,y0+900],18,fill=(20,24,32),outline=(60,66,80),width=2)
    d.text((110,y0+40),"UNITED STATES DEPARTMENT OF AGRICULTURE",font=AB(24),fill=MUT)
    d.text((110,y0+76),"Bureau of Animal Industry · Circular 174 · 1911",font=GR(30),fill=INK)
    d.line([110,y0+130,W-110,y0+130],fill=(60,66,80),width=2)
    lines=[("Orange County","HEAVILY INFESTED",1.5),("Herd, documented","25,000+ head",3.6),("Dip formula","8 lb arsenic trioxide / 500 gal",5.8),("Cadence","every 14 days · compulsory",8.0),("Duration","1907 – March 1912 · five years",9.6)]
    for i,(k,v,t0) in enumerate(lines):
        a=eo(t0,t0+0.6,u)
        if a<=0: continue
        yy=y0+170+i*125; A=int(255*a)
        d.text((110,yy),k.upper(),font=AB(22),fill=(150,156,166,A))
        d.text((110,yy+34),v,font=GB(40) if i in (1,2) else GR(38),fill=(AMB if i in (1,2) else INK)+(A,))
        d.line([110,yy+96,110+(W-220)*a,yy+96],fill=(40,46,60),width=1)
    # stamp
    s=eo(11.2,11.7,u)
    if s>0:
        sc=1.6-0.6*s; A=int(230*s)
        st=Image.new("RGBA",(W,H),(0,0,0,0)); sd=ImageDraw.Draw(st)
        cx,cy=W/2,1560; ww,hh=560*sc,170*sc
        sd.rounded_rectangle([cx-ww/2,cy-hh/2,cx+ww/2,cy+hh/2],14,outline=RED+(A,),width=int(8*sc))
        sd.text((cx,cy-int(60*sc)),"STATE MANDATE",font=AB(int(58*sc)),fill=RED+(A,),anchor="ma")
        sd.text((cx,cy+int(12*sc)),"not optional · not local · every rancher",font=AR(int(24*sc)),fill=RED+(A,),anchor="ma")
        st=st.rotate(-7,resample=Image.BICUBIC,center=(cx,cy))
        im.alpha_composite(st)
def scene_math(im,d,u):     # 14 - 31
    header(d,u,"RUN THE ARITHMETIC")
    v=u-14
    # three factors
    fs=[("25,000",  "head of cattle",0.3),("× 130","dippings in five years\n(every 14 days)",2.2),("× 1 : 60","one part arsenic to\nsixty parts water",4.6)]
    for i,(big,small,t0) in enumerate(fs):
        a=eo(t0,t0+0.6,v)
        if a<=0: continue
        y=430+i*150; A=int(255*a); x=120+40*(1-a)
        d.text((x,y),big,font=GB(64),fill=AMB+(A,))
        d.text((x+420,y+8),small,font=AR(28),fill=INK+(A,))
    # ratio visual: 60 drops, one dark
    r=eo(5.0,6.4,v)
    if r>0:
        for i in range(60):
            cx=120+(i%20)*44; cy=930+(i//20)*50
            k=ss(0,1,(r*60-i)); 
            if k<=0: continue
            col=(40,44,30) if i==0 else (90,150,200)
            d.ellipse([cx-14,cy-14,cx+14,cy+14],fill=col+(int(255*k),))
        d.text((120,1100),"1 in 60 by weight · the federal dip",font=AR(24),fill=MUT)
    # the result counter
    c=eo(7.5,11.5,v)
    if c>0:
        lo=6692*c; hi=39748*c
        d.text((W/2,1210),"ARSENIC INTO THE DIP, 1907–1912",font=AB(26),fill=MUT,anchor="ma")
        d.text((W/2,1250),f"{fmt(lo)} – {fmt(hi)} lb",font=GB(78),fill=AMB,anchor="ma")
        d.text((W/2,1350),"low · mid · high documented-herd cases  ·  model estimate",font=AR(22),fill=MUT,anchor="ma")
    # sacks stacking
    s=eo(11.8,16.5,v)
    if s>0:
        n=int(60*s); d.text((120,1430),f"that is roughly {fmt(838+ (4875-838)*s)} eight-pound sacks",font=GR(34),fill=INK)
        for i in range(n):
            x=120+(i%15)*60; y=1500+(i//15)*78
            sack(d,x,y,44,int(255*min(1,(60*s-i))))
def scene_element(im,d,u):  # 31 - 41
    header(d,u,"IT DOES NOT GO AWAY")
    v=u-31; a=eo(0.2,1.0,v)
    # periodic tile
    cx,cy=W/2,720; s=int(360*(0.7+0.3*a)); A=int(255*a)
    d.rounded_rectangle([cx-s/2,cy-s/2,cx+s/2,cy+s/2],22,fill=(24,30,42,A),outline=AMB+(A,),width=6)
    d.text((cx-s/2+26,cy-s/2+20),"33",font=AB(int(s*0.11)),fill=INK+(A,))
    d.text((cx,cy-s*0.12),"As",font=GB(int(s*0.42)),fill=AMB+(A,),anchor="mm")
    d.text((cx,cy+s*0.30),"ARSENIC · an element",font=AB(int(s*0.075)),fill=INK+(A,),anchor="mm")
    b=eo(2.0,3.0,v)
    if b>0:
        A=int(255*b)
        d.text((W/2,980),"It does not break down. It does not go away.",font=GR(40),fill=INK+(A,),anchor="ma")
    # flat timeline 1907 -> 2026
    tl=eo(3.4,7.0,v)
    if tl>0:
        x0,x1,y=140,W-140,1250
        d.line([x0,y,x1,y],fill=(60,66,80),width=3)
        xe=x0+(x1-x0)*tl
        d.line([x0,y-120,xe,y-120],fill=AMB,width=8)
        d.text((x0,y+20),"1907",font=AB(30),fill=MUT); d.text((x1,y+20),"2026",font=AB(30),fill=MUT,anchor="ra")
        d.text((x0,y-175),"100% of what was introduced",font=AR(26),fill=AMB)
        for yr,lab in ((1912,"program ends"),(1999,"first homes"),(2007,"build-out")):
            xx=x0+(x1-x0)*(yr-1907)/119
            if xx<=xe:
                d.line([xx,y-12,xx,y+12],fill=INK,width=3); d.text((xx,y+60),f"{yr}\n{lab}",font=AR(22),fill=MUT,anchor="ma")
    c=eo(6.5,7.5,v)
    if c>0: d.text((W/2,1560),"Whatever was introduced is still somewhere on this landscape.",font=GR(34),fill=INK+(int(255*c),),anchor="ma")
def scene_vat(im,d,u):      # 41 - 55
    header(d,u,"IF A VAT STOOD HERE")
    v=u-41
    # photo thumbnail
    a=eo(0.2,1.0,v)
    if a>0:
        th=PH.resize((420,560)); box=Image.new("RGBA",(420,560),(0,0,0,0)); box.paste(th,(0,0))
        box.putalpha(int(255*a)); im.alpha_composite(box,(80,400))
        d.rectangle([80,400,500,960],outline=AMB+(int(255*a),),width=4)
        d.text((290,975),"the concrete base · 12 ft",font=AR(22),fill=MUT,anchor="ma")
    b=eo(1.0,2.0,v)
    if b>0:
        A=int(255*b)
        d.text((540,430),"concentrated in the vat,\nthe pens and the corrals:",font=GR(34),fill=INK+(A,))
        d.text((540,560),f"{fmt(1338*b)} – {fmt(7949*b)} lb",font=GB(64),fill=AMB+(A,))
        d.text((540,650),"over about 2.25 hectares\n(a few house lots) · model estimate",font=AR(24),fill=MUT+(A,))
    # concentration bars
    c=eo(3.0,8.0,v)
    if c>0:
        d.text((80,1060),"SOIL ARSENIC, mg/kg",font=AB(26),fill=MUT)
        d.text((80,1110),"California background",font=AR(28),fill=INK); bar(d,80,1150,W-160,34,min(1,11/763*c*8),(90,150,200)); d.text((W-80,1105),"1 – 11",font=AB(28),fill=INK,anchor="ra")
        d.text((80,1230),"At the vat, if it stood here",font=AR(28),fill=INK); bar(d,80,1270,W-160,34,c,AMB); d.text((W-80,1225),f"{fmt(128*c)} – {fmt(763*c)}",font=AB(28),fill=AMB,anchor="ra")
        d.text((W/2,1350),f"{fmt(10*c)}× to {fmt(700*c)}× background",font=GB(54),fill=AMB,anchor="ma")
    e=eo(9.0,10.0,v)
    if e>0: d.text((W/2,1500),"Comparable historic dip sites in Florida and Australia\nmeasured hundreds to thousands of mg/kg. (B1)",font=AR(26),fill=MUT+(int(255*e),),anchor="ma")
def scene_scale(im,d,u):    # 55 - 65
    header(d,u,"SCALE")
    v=u-55; a=eo(0.2,1.0,v)
    if a>0:
        A=int(255*a)
        d.text((W/2,420),"A lethal dose of arsenic trioxide",font=GR(36),fill=INK+(A,),anchor="ma")
        d.text((W/2,480),"100 – 300 milligrams",font=GB(70),fill=AMB+(A,),anchor="ma")
        d.text((W/2,580),"a fraction of a gram · a pinch",font=AR(28),fill=MUT+(A,),anchor="ma")
        # pinch visual
        for i in range(int(30*a)):
            ang=random.Random(i).uniform(0,6.28); r=random.Random(i+99).uniform(0,26)
            d.ellipse([W/2+r*math.cos(ang)-3,700+r*math.sin(ang)*0.5-3,W/2+r*math.cos(ang)+3,700+r*math.sin(ang)*0.5+3],fill=INK+(A,))
    b=eo(2.5,6.0,v)
    if b>0:
        d.text((W/2,860),"the whole-ranch mass, in nominal doses",font=GR(34),fill=INK+(int(255*b),),anchor="ma")
        d.text((W/2,920),f"{fmt(32e6*b)} – {fmt(96e6*b)}",font=GB(74),fill=AMB+(int(255*b),),anchor="ma")
    c=eo(6.0,7.0,v)
    if c>0:
        A=int(255*c)
        d.rounded_rectangle([70,1120,W-70,1420],16,fill=(40,24,20,A),outline=RED+(A,),width=3)
        d.text((100,1145),"THIS IS ARITHMETIC, NOT TOXICOLOGY",font=AB(26),fill=(255,150,130,A))
        d.text((100,1195),"Soil-bound arsenic is only partly bioavailable. Nobody ingests soil in quantity.\nThis number says one thing: the mass involved was large. It says nothing\nabout exposure, which has never been measured here.",font=AR(26),fill=INK+(A,))
def frame(i):
    u=i/FPS
    im=Image.new("RGBA",(W,H),BG+(255,)); d=ImageDraw.Draw(im,"RGBA")
    for (x,y,b) in STARS: d.point((x,(y+u*6*b)%H),fill=(40,48,64,int(120*b)))
    if u<14: scene_record(im,d,u)
    elif u<31: scene_math(im,d,u)
    elif u<41: scene_element(im,d,u)
    elif u<55: scene_vat(im,d,u)
    else: scene_scale(im,d,u)
    # scene fades
    for edge in (14,31,41,55):
        k=1-min(1,abs(u-edge)/0.35)
        if k>0: im.alpha_composite(Image.new("RGBA",(W,H),BG+(int(255*k),)))
    return im.convert("RGB")
if __name__=="__main__":
    import sys
    if len(sys.argv)>1:
        for t in [float(x) for x in sys.argv[1:]]: frame(int(t*FPS)).resize((540,960)).save(f"ex_{t:.0f}.jpg",quality=85)
    else:
        p=subprocess.Popen(["ffmpeg","-y","-loglevel","error","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-c:v","libx264","-crf","17","-pix_fmt","yuv420p","-video_track_timescale","12288","explainer.mp4"],stdin=subprocess.PIPE)
        for i in range(N): p.stdin.write(np.asarray(frame(i)).tobytes())
        p.stdin.close(); p.wait(); print("explainer.mp4 done")
