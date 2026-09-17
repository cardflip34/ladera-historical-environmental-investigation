#!/usr/bin/env python3
"""Phase 2 BASE video builder (vertical 1080x1920, 24 fps). Segments rendered as PIL frames piped to ffmpeg."""
import os, sys, json, math, subprocess, glob
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
Image.MAX_IMAGE_PIXELS=None
HERE=os.path.dirname(os.path.abspath(__file__)); SP=os.path.dirname(HERE)
SRC=SP+"/p2src"; DOC=SP+"/doc"; OUT=HERE+"/seg"; os.makedirs(OUT,exist_ok=True)
W,H,FPS=1080,1920,24
FD="/System/Library/Fonts/Supplemental/"
def F(s,b=False): return ImageFont.truetype(FD+("Arial Bold" if b else "Arial")+".ttf",s)
BG=(12,16,24); AMB=(236,160,70); INK=(236,238,242); MUT=(160,166,178); RED=(230,70,50); CYAN=(0,200,230)

def fit_cover(im,w,h):
    r=max(w/im.width,h/im.height); im=im.resize((int(im.width*r)+1,int(im.height*r)+1),Image.LANCZOS)
    x=(im.width-w)//2; y=(im.height-h)//2; return im.crop((x,y,x+w,y+h))
def fit_contain(im,w,h):
    r=min(w/im.width,h/im.height); return im.resize((int(im.width*r),int(im.height*r)),Image.LANCZOS)
def blur_bg(im):
    b=fit_cover(im,W,H).filter(ImageFilter.GaussianBlur(28)); return Image.blend(b,Image.new("RGB",(W,H),BG),0.55)
def kb_frame(im,t,z0,z1,cx=0.5,cy=0.5,box=(0,0,W,H)):
    """Ken Burns: crop of `im` with zoom factor z (1=fit cover) placed in box."""
    bw,bh=box[2]-box[0],box[3]-box[1]
    z=z0+(z1-z0)*t
    cov=fit_cover(im,int(bw*z)+2,int(bh*z)+2)
    x=int((cov.width-bw)*cx); y=int((cov.height-bh)*cy)
    return cov.crop((x,y,x+bw,y+bh))
def ease(t): return t*t*(3-2*t)
def kb_map(im,t,z0,z1,cx,cy,box):
    bw,bh=box[2]-box[0],box[3]-box[1]; z=z0+(z1-z0)*t
    r=max((int(bw*z)+2)/im.width,(int(bh*z)+2)/im.height); sw,sh=int(im.width*r)+1,int(im.height*r)+1
    x0=int((sw-bw)*cx); y0=int((sh-bh)*cy)
    return lambda px,py:(px*r-x0+box[0],py*r-y0+box[1])
def ring(fr,xy,r=70,col=AMB,label=None,alpha=255,lab_dx=90,lab_dy=-30):
    ov=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov); x,y=xy
    d.ellipse([x-r,y-r,x+r,y+r],outline=col+(alpha,),width=6); d.ellipse([x-r-14,y-r-14,x+r+14,y+r+14],outline=col+(alpha//2,),width=2)
    if label:
        f=F(30,True); tw=d.textlength(label,font=f); lx=x+lab_dx if x+lab_dx+tw<W-30 else x-lab_dx-tw; lx=max(30,min(W-30-tw,lx)); ly=y+lab_dy
        d.line([x+(r if lx>x else -r),y,lx+(0 if lx>x else tw),ly+40],fill=col+(alpha,),width=3)
        d.rectangle([lx-10,ly-6,lx+tw+10,ly+44],fill=(8,10,16,int(alpha*0.75))); d.text((lx,ly),label,font=f,fill=col+(alpha,))
    fr.paste(ov,(0,0),ov)
def wrap(d,text,font,maxw):
    words=text.split(); lines=[]; cur=""
    for w in words:
        t=(cur+" "+w).strip()
        if d.textlength(t,font=font)<=maxw: cur=t
        else: lines.append(cur); cur=w
    if cur: lines.append(cur)
    return lines
def caption(fr,text,y,size=44,color=INK,bold=True,maxw=960,align="left",x=60,shadow=True,alpha=255):
    if alpha<=0: return
    ov=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov); f=F(size,bold)
    lines=wrap(d,text,f,maxw); lh=int(size*1.22)
    for i,l in enumerate(lines):
        tx=x if align=="left" else (W-d.textlength(l,font=f))/2
        if shadow: d.text((tx+3,y+i*lh+3),l,font=f,fill=(0,0,0,int(alpha*0.8)))
        d.text((tx,y+i*lh),l,font=f,fill=color+(alpha,))
    fr.paste(ov,(0,0),ov)
def band(fr,y0,y1,alpha=170):
    ov=Image.new("RGBA",(W,H),(0,0,0,0)); ImageDraw.Draw(ov).rectangle([0,y0,W,y1],fill=(8,10,16,alpha)); fr.paste(ov,(0,0),ov)
def tag(fr,text,y=70):
    d=ImageDraw.Draw(fr); f=F(26,True); tw=d.textlength(text,font=f)
    d.rectangle([60,y,60+tw+36,y+50],fill=AMB); d.text((78,y+9),text,font=f,fill=(20,16,10))
def fade_a(i,n,fi=0.5,fo=0.6):
    t=i/FPS; T=n/FPS; a=1.0
    if t<fi: a=t/fi
    if t>T-fo: a=min(a,(T-t)/fo)
    return max(0,min(1,a))

def render(name,nframes,fn):
    p=f"{OUT}/{name}.mp4"
    ff=subprocess.Popen(["ffmpeg","-y","-loglevel","error","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-c:v","libx264","-crf","16","-pix_fmt","yuv420p","-video_track_timescale","12288",p],stdin=subprocess.PIPE)
    for i in range(nframes):
        fr=fn(i,nframes)
        a=fade_a(i,nframes)
        if a<1: fr=Image.blend(Image.new("RGB",(W,H),(0,0,0)),fr,a)
        ff.stdin.write(fr.tobytes())
    ff.stdin.close(); ff.wait(); print("wrote",name,round(nframes/FPS,2),"s"); return p

# ---------- SEGMENT: Florida ----------
def seg_florida(pages,caps,dur=31.0):
    """pages: list of image paths; caps: list of (headline, sub)."""
    ims=[Image.open(p).convert("RGB") for p in pages]
    n=int(dur*FPS); intro=int(4.0*FPS); per=(n-intro)/len(ims)
    def fn(i,N):
        if i<intro:
            fr=Image.new("RGB",(W,H),BG); t=i/intro
            caption(fr,"FLORIDA KEPT RECORDS",520,size=84,color=AMB,align="center",x=0,alpha=int(255*min(1,t*3)))
            caption(fr,"The same federal dipping program. The one state that inventoried its vats.",720,size=40,color=INK,align="center",x=0,bold=False,maxw=900,alpha=int(255*max(0,min(1,(t-0.25)*3))))
            caption(fr,"3,281 vats listed  ·  12 tested  ·  11 failed the soil standard for arsenic",900,size=34,color=MUT,align="center",x=0,bold=False,maxw=940,alpha=int(255*max(0,min(1,(t-0.5)*3))))
            caption(fr,"Source: Florida DEP, Cattle Dip Vat Assessment Program (public records, 2026)",1040,size=24,color=MUT,align="center",x=0,bold=False,alpha=int(255*max(0,min(1,(t-0.6)*3))))
            return fr
        k=min(len(ims)-1,int((i-intro)/per)); t=((i-intro)-k*per)/per
        im=ims[k]; fr=blur_bg(im)
        box=(40,220,W-40,1500)
        kb=kb_frame(im,ease(t),1.0,1.12,0.5,0.45,box); fr.paste(kb,(box[0],box[1]))
        hl,sub=caps[k]
        band(fr,1520,1920,190)
        caption(fr,hl,1560,size=44,color=AMB)
        caption(fr,sub,1630,size=30,color=INK,bold=False,maxw=960)
        tag(fr,f"FLORIDA · STATE VAT PROGRAM  ·  {k+1}/{len(ims)}",130)
        return fr
    return render("fl",n,fn)

# ---------- SEGMENT: tire swing ----------
def seg_tire(path,dur=17.0):
    im=ImageOps.exif_transpose(Image.open(path)).convert("RGB")
    n=int(dur*FPS)
    def fn(i,N):
        t=i/N; fr=blur_bg(im); box=(0,0,W,1460)
        fr.paste(kb_frame(im,ease(t),1.0,1.18,0.5,0.4,box),(0,0))
        band(fr,1440,1920,200)
        tag(fr,"ON THE WALK DOWN TO THE CONCRETE BASE",90)
        caption(fr,"A tire swing. Children play here.",1480,size=46,color=INK)
        a=int(255*max(0,min(1,(t-0.35)*4)))
        caption(fr,"TEST THIS AREA",1570,size=60,color=AMB,alpha=a)
        caption(fr,"Alert the State of California. Independent of Ladera Ranch and of Rancho Mission Viejo.",1660,size=32,color=INK,bold=False,maxw=960,alpha=a)
        return fr
    return render("tire",n,fn)

# ---------- SEGMENT: pond time series ----------
def seg_pond(dur_lead=8.0,per=3.0,dur_end=7.0):
    win=json.load(open(SRC+"/pond/win.json")); WIN=win["WIN"]; P=win["pond"]; T6=win["tgt6"]
    years=["1929","1937","1947","1953","1960","1969","1980","1990","2004","2025"]
    notes={"1929":"earliest aerial survey · open range","1937":"sharpest ranch-era frame · 1.15 ft per pixel","1947":"post-war composite","1953":"Orange County series","1960":"Orange County series","1969":"one year after the USGS field survey mapped water here","1980":"Orange County series","1990":"before entitlement","2004":"USGS 0.3 m · during build-out","2025":"present day · 1 ft"}
    tiles={y:Image.open(f"{SRC}/pond/era_{y}.jpg").convert("RGB") for y in years}
    d1=Image.open(SRC+"/drone_pond_close.jpg").convert("RGB"); d2=Image.open(SRC+"/drone_pond_wide.jpg").convert("RGB")
    S=W
    def xy(lon,lat): return ((lon-WIN[0])/(WIN[2]-WIN[0])*S,(WIN[3]-lat)/(WIN[3]-WIN[1])*S)
    nl=int(dur_lead*FPS); nt=int(per*FPS); ne=int(dur_end*FPS); n=nl+nt*len(years)+ne
    def draw_marks(fr,off,ring=True,t6=True,labels=False):
        d=ImageDraw.Draw(fr); x,y=xy(*P); x+=off[0]; y+=off[1]
        if ring:
            for r,wd in [(70,6),(84,2)]: d.ellipse([x-r,y-r,x+r,y+r],outline=RED,width=wd)
        if t6:
            x6,y6=xy(*T6); x6+=off[0]; y6+=off[1]; d.ellipse([x6-40,y6-40,x6+40,y6+40],outline=CYAN,width=4)
        if labels:
            d.text((x+95,y-30),"POND",font=F(34,True),fill=RED)
            d.text((x6-40,y6-90),"1968 USGS WATER POINT",font=F(24,True),fill=CYAN)
    def fn(i,N):
        fr=Image.new("RGB",(W,H),BG)
        if i<nl:
            half=nl//2; box=(0,240,W,240+1300)
            if i<half:
                t=i/half; im=d1; fr.paste(kb_frame(im,ease(t),1.0,1.12,0.6,0.45,box),(box[0],box[1])); mp=kb_map(im,ease(t),1.0,1.12,0.6,0.45,box)
                ring(fr,mp(745,415),r=110,col=CYAN,label="STANDING WATER",lab_dx=130,lab_dy=-200)
                ring(fr,mp(560,560),r=200,col=AMB,label="DEAD VEGETATION RING",alpha=int(255*min(1,max(0,(t-0.3)*4))),lab_dx=-420,lab_dy=230)
                tag(fr,"DRONE · BELOW THE VAT SITE · EDGE OF THE GOLF COURSE",90)
            else:
                t=(i-half)/(nl-half); im=d2; fr.paste(kb_frame(im,ease(t),1.0,1.10,0.6,0.5,box),(box[0],box[1])); mp=kb_map(im,ease(t),1.0,1.10,0.6,0.5,box)
                ring(fr,mp(890,570),r=90,col=CYAN,label="THE POND",lab_dx=-330,lab_dy=-160)
                ring(fr,mp(1250,720),r=150,col=(120,230,140),label="GOLF COURSE",alpha=int(255*min(1,max(0,(t-0.3)*4))),lab_dx=-320,lab_dy=170)
                tag(fr,"DRONE · THE POND AND THE FAIRWAY",90)
            caption(fr,"The pond",1590,size=64,color=AMB)
            caption(fr,"Mapped by the 1968 USGS field survey as standing water: a stock-water point.",1680,size=32,color=INK,bold=False,maxw=960)
            return fr
        j=i-nl
        if j<nt*len(years):
            k=j//nt; t=(j-k*nt)/nt; y=years[k]; off=(0,300)
            fr.paste(tiles[y],off); draw_marks(fr,off,labels=(k==0))
            band(fr,1380,1920,0)
            caption(fr,y,1440,size=140,color=AMB)
            caption(fr,notes[y],1620,size=32,color=INK,bold=False,maxw=960)
            caption(fr,"Same ground, same window, every frame. Red ring = the pond. Cyan = 1968 USGS water point.",1700,size=24,color=MUT,bold=False,maxw=960)
            # progress bar
            d=ImageDraw.Draw(fr); d.rectangle([60,1800,1020,1808],fill=(40,46,58)); d.rectangle([60,1800,60+960*((k+t)/len(years)),1808],fill=AMB)
            tag(fr,"THE SAME POND, 1929 TO 2025",90)
            return fr
        t=(j-nt*len(years))/ne; off=(0,300); fr.paste(tiles["2025"],off); draw_marks(fr,off)
        d=ImageDraw.Draw(fr); x,y=xy(*P); x+=off[0]; y+=off[1]
        a=int(255*min(1,t*3)); ov=Image.new("RGBA",(W,H),(0,0,0,0)); od=ImageDraw.Draw(ov)
        od.line([x+70,y-40,x+300,y-200],fill=AMB+(a,),width=4); od.text((x+120,y-250),"DEAD VEGETATION RING",font=F(30,True),fill=AMB+(a,))
        gx,gy=520,300+660; od.line([gx,gy,gx-260,gy+230],fill=(120,230,140,a),width=4); od.text((80,gy+240),"GOLF COURSE FAIRWAY",font=F(30,True),fill=(120,230,140,a))
        fr.paste(ov,(0,0),ov)
        caption(fr,"2025",1440,size=140,color=AMB)
        caption(fr,"A century of runoff from the slope above settles here. Its sediment has never been sampled.",1620,size=32,color=INK,bold=False,maxw=960)
        tag(fr,"THE SAME POND, 1929 TO 2025",90)
        return fr
    return render("pond",n,fn)

# ---------- SEGMENT: trail ----------
def seg_trail(path,dur=18.0):
    im=ImageOps.exif_transpose(Image.open(path)).convert("RGB"); n=int(dur*FPS)
    def fn(i,N):
        t=i/N; fr=blur_bg(im); box=(0,0,W,1400)
        fr.paste(kb_frame(im,ease(t),1.0,1.15,0.45,0.45,box),(0,0)); mp=kb_map(im,ease(t),1.0,1.15,0.45,0.45,box)
        ring(fr,mp(482,215),r=120,col=AMB,label="RANCH-ERA POST AND RAIL",lab_dx=150,lab_dy=-190)
        ring(fr,mp(505,590),r=80,col=CYAN,label="PUBLIC TRAIL MARKER · PATH FORK",alpha=int(255*min(1,max(0,(t-0.15)*4))),lab_dx=-560,lab_dy=140)
        band(fr,1380,1920,200)
        tag(fr,"PUBLIC TRAIL · DIPPING-ERA FENCE LINE · CONCRETE BASE NEARBY",90)
        caption(fr,"Families walk and ride past this every weekend.",1420,size=40,color=INK)
        a=int(255*max(0,min(1,(t-0.3)*4)))
        for k,(txt,c) in enumerate([("CLOSE IT",AMB),("MARK IT",AMB),("TEST THE SOIL",AMB)]):
            caption(fr,txt,1510+k*82,size=64,color=c,alpha=int(255*max(0,min(1,(t-0.3-k*0.12)*4))))
        caption(fr,"Sampling under hazardous-materials protocol, by the State of California.",1770,size=30,color=INK,bold=False,maxw=960,alpha=a)
        return fr
    return render("trail",n,fn)

# ---------- SEGMENT: closing ----------
def seg_close(dur=16.0):
    im=Image.open(DOC+"/closing_card.png").convert("RGB"); n=int(dur*FPS)
    return render("close",n,lambda i,N: fit_cover(im,W,H))

if __name__=="__main__":
    what=sys.argv[1:] or ["all"]
    if "fl" in what or "all" in what:
        pages=json.load(open(HERE+"/fl_pages.json")); seg_florida([p["path"] for p in pages],[(p["hl"],p["sub"]) for p in pages])
    if "tire" in what or "all" in what: seg_tire(SRC+"/tire_swing.jpg")
    if "pond" in what or "all" in what: seg_pond()
    if "trail" in what or "all" in what: seg_trail(SRC+"/trail_fork.jpg")
    if "close" in what or "all" in what: seg_close()

# ================= FULL-CUT EXTRA SEGMENTS =================
def seg_intro(dur=32.0):
    bg=Image.new("RGB",(W,H),BG)
    bg=fit_cover(bg,W,H); n=int(dur*FPS)
    cards=[(0.0,"PHASE 1 · THE RECORD",["1907 to 1912: compulsory arsenic cattle dipping,","ordered by the State of California and the USDA,","on the land that became Ladera Ranch."]),
           (0.36,"SINCE PHASE 1",["Ladera Ranch and ProtectLadera are doing what they can","to keep this community safe going forward.","That work matters."]),
           (0.72,"PHASE 2 · THE GROUND",["This video is about something more immediate:","a dipping-station site, found. Unfenced. Untested.","And possibly others."])]
    def fn(i,N):
        t=i/N; fr=Image.blend(bg,Image.new("RGB",(W,H),BG),0.35)
        for k,(t0,hd,lines) in enumerate(cards):
            t1=cards[k+1][0] if k+1<len(cards) else 1.01
            if t0<=t<t1:
                a=int(255*min(1,(t-t0)*12)); y=700
                caption(fr,hd,y,size=54,color=AMB,align="center",x=0,alpha=a)
                for j,l in enumerate(lines): caption(fr,l,y+110+j*58,size=36,color=INK,bold=False,align="center",x=0,maxw=980,alpha=int(255*min(1,max(0,(t-t0-0.03*(j+1))*12))))
        d=ImageDraw.Draw(fr); d.rectangle([60,1800,1020,1806],fill=(40,46,58)); d.rectangle([60,1800,60+960*t,1806],fill=AMB)
        tag(fr,"LADERA RANCH · PHASE 2",90)
        return fr
    return render("intro",n,fn)

def seg_threat(dur=42.0):
    files=sorted(glob.glob(SRC+"/threat/*.jpg")); ims=[ImageOps.exif_transpose(Image.open(f)).convert("RGB") for f in files]
    caps=json.load(open(SRC+"/threat/caps.json")) if os.path.exists(SRC+"/threat/caps.json") else [("","")]*len(ims)
    n=int(dur*FPS); per=n/len(ims)
    def fn(i,N):
        k=min(len(ims)-1,int(i/per)); t=(i-k*per)/per; im=ims[k]; fr=blur_bg(im)
        box=(0,200,W,1480); fr.paste(kb_frame(im,ease(t),1.0,1.14,0.5,0.5,box),(box[0],box[1]))
        band(fr,1500,1920,200); hl,sub=caps[k]
        caption(fr,hl,1540,size=46,color=AMB); caption(fr,sub,1610,size=32,color=INK,bold=False,maxw=960)
        tag(fr,f"THE IMMEDIATE QUESTION · FIELD RECORD, AUGUST 2026  ·  {k+1}/{len(ims)}",90)
        return fr
    return render("threat",n,fn)

def seg_p3(dur=78.0):
    n=int(dur*FPS)
    def fn(i,N):
        t=i/N; fr=Image.new("RGB",(W,H),BG); d=ImageDraw.Draw(fr)
        tag(fr,"THE HARDEST PART TO SAY CAREFULLY",90)
        # timeline 1996-2026
        x0,x1,yb=100,980,760; yr=lambda y:(x0+(y-1996)/(2026-1996)*(x1-x0))
        d.line([x0,yb,x1,yb],fill=MUT,width=3)
        for y in range(1996,2027,5): d.line([yr(y),yb-10,yr(y),yb+10],fill=MUT,width=2); d.text((yr(y)-28,yb+18),str(y),font=F(24),fill=MUT)
        def bar(ya,yb2,y,h,col,label,alpha):
            if alpha<=0: return
            ov=Image.new("RGBA",(W,H),(0,0,0,0)); od=ImageDraw.Draw(ov)
            od.rectangle([yr(ya),y,yr(yb2),y+h],fill=col+(int(alpha*0.55),)); od.rectangle([yr(ya),y,yr(yb2),y+h],outline=col+(alpha,),width=2)
            tw=od.textlength(label,font=F(26,True)); lx=yr(ya) if yr(ya)+tw<W-40 else max(40,yr(yb2)-tw); od.text((lx,y-36),label,font=F(26,True),fill=col+(alpha,)); fr.paste(ov,(0,0),ov)
        A=lambda s:int(255*min(1,max(0,(t-s)*6)))
        bar(1999,2007,yb-330,70,AMB,"HOMES BUILT 1999 to 2006 · GRADING PEAK 2002",A(0.04))
        d.line([yr(2002),yb-340,yr(2002),yb-260],fill=AMB,width=4) if t>0.06 else None
        bar(1999,2007,yb-220,60,(120,180,240),"PREGNANCIES DURING BUILD-OUT (a question, not a dataset)",A(0.16))
        bar(2009,2026,yb-110,60,(200,120,220),"AGES 10 to 19 FOR CHILDREN BORN 1999 to 2007",A(0.24))
        # two-step model
        a=A(0.38)
        if a>0:
            ov=Image.new("RGBA",(W,H),(0,0,0,0)); od=ImageDraw.Draw(ov)
            for k,(hd,sub) in enumerate([("BEFORE BIRTH","initiating event  (two-step model, Cell Reports 2025)"),("PUBERTY","emergence, hormone-driven")]):
                bx=100+k*500; od.rounded_rectangle([bx,900,bx+420,1080],radius=18,outline=INK+(a,),width=3)
                od.text((bx+24,924),hd,font=F(36,True),fill=AMB+(a,)); 
                for j,l in enumerate(wrap(od,sub,F(24),380)): od.text((bx+24,980+j*30),l,font=F(24),fill=INK+(a,))
            od.line([520,990,600,990],fill=AMB+(a,),width=5); od.polygon([(600,978),(622,990),(600,1002)],fill=AMB+(a,))
            fr.paste(ov,(0,0),ov)
        a2=A(0.5)
        caption(fr,"Chile cohorts: arsenic in the womb, cancers decades later.",1130,size=32,color=INK,bold=False,alpha=a2)
        caption(fr,"Two separate findings. No study has connected them to each other, or to this community.",1185,size=28,color=MUT,bold=False,maxw=960,alpha=a2)
        a3=A(0.66)
        caption(fr,"PHASE 3?",1330,size=64,color=AMB,alpha=a3)
        caption(fr,"Whether mothers were on this ground during pregnancy is a medical-records question. It needs real data and real statistics. It is not ours to decide, and not our focus now.",1420,size=32,color=INK,bold=False,maxw=960,alpha=a3)
        caption(fr,"OUR FOCUS IS THE GROUND.",1640,size=52,color=AMB,alpha=A(0.86))
        caption(fr,"Hypothesis, not finding. Ewing sarcoma has no established environmental cause. Sources graded in the project audit.",1780,size=22,color=MUT,bold=False,maxw=960)
        return fr
    return render("p3",n,fn)

if __name__=="__main__" and any(w in sys.argv for w in ("intro","threat","p3")):
    if "intro" in sys.argv: seg_intro()
    if "threat" in sys.argv: seg_threat()
    if "p3" in sys.argv: seg_p3()
