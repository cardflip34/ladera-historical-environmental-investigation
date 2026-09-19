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
CAPX=int(os.environ.get("CAPX","60"))
def caption(fr,text,y,size=44,color=INK,bold=True,maxw=None,align="left",x=None,shadow=True,alpha=255):
    if alpha<=0: return y
    if x is None: x=CAPX if align=="left" else 0
    if maxw is None: maxw=(W-x-60) if align=="left" else 980
    if align=="left": maxw=min(maxw,int(os.environ.get("MAXW","2000")))
    ov=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov); f=F(size,bold)
    lines=wrap(d,text,f,maxw); lh=int(size*1.22)
    for i,l in enumerate(lines):
        tx=x if align=="left" else (W-d.textlength(l,font=f))/2
        if shadow: d.text((tx+3,y+i*lh+3),l,font=f,fill=(0,0,0,int(alpha*0.8)))
        d.text((tx,y+i*lh),l,font=f,fill=color+(alpha,))
    fr.paste(ov,(0,0),ov)
    return y+len(lines)*lh
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
    p=f"{OUT}/{os.environ.get('SEGPFX','')}{name}.mp4"
    ff=subprocess.Popen(["ffmpeg","-y","-loglevel","error","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-c:v","libx264","-crf","16","-pix_fmt","yuv420p","-video_track_timescale","12288",p],stdin=subprocess.PIPE)
    for i in range(nframes):
        fr=fn(i,nframes)
        a=fade_a(i,nframes)
        if a<1: fr=Image.blend(Image.new("RGB",(W,H),(0,0,0)),fr,a)
        ff.stdin.write(fr.tobytes())
    ff.stdin.close(); ff.wait(); print("wrote",name,round(nframes/FPS,2),"s"); return p

# ---------- SEGMENT: Florida ----------
def seg_florida(pages,caps,dur=float(os.environ.get("DUR_FL","31"))):
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
        y2=caption(fr,hl,1560,size=44,color=AMB)
        caption(fr,sub,y2+10,size=30,color=INK,bold=False,maxw=960)
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
def seg_pond(dur_lead=float(os.environ.get('DUR_PL','8')),per=float(os.environ.get('DUR_PP','3')),dur_end=float(os.environ.get('DUR_PE','7'))):
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
            y2=caption(fr,notes[y],1600,size=32,color=INK,bold=False,maxw=960)
            caption(fr,"Same ground, same window, every frame. Red ring = the pond. Cyan = 1968 USGS water point.",y2+8,size=24,color=MUT,bold=False,maxw=960)
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
def seg_trail(path,dur=18.0,rings=True):
    im=ImageOps.exif_transpose(Image.open(path)).convert("RGB"); n=int(dur*FPS)
    def fn(i,N):
        t=i/N; fr=blur_bg(im); box=(0,0,W,1400)
        fr.paste(kb_frame(im,ease(t),1.0,1.15,0.45,0.45,box),(0,0)); mp=kb_map(im,ease(t),1.0,1.15,0.45,0.45,box)
        if rings:
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
    im=Image.open(HERE+"/closing_card_v2.png").convert("RGB") if os.path.exists(HERE+"/closing_card_v2.png") else Image.open(DOC+"/closing_card.png").convert("RGB"); n=int(dur*FPS)
    return render("close",n,lambda i,N: fit_cover(im,W,H))

if __name__=="__main__":
    what=sys.argv[1:] or ["all"]
    if "fl" in what or "all" in what:
        pages=json.load(open(HERE+"/fl_pages.json")); seg_florida([p["path"] for p in pages],[(p["hl"],p["sub"]) for p in pages])
    if "tire" in what or "all" in what: seg_tire(SRC+"/tire_swing.jpg")
    if "pond" in what or "all" in what: seg_pond()
    if "trail" in what or "all" in what: seg_trail(SRC+"/threat/t1_IMG_4499.jpg",rings=False)
    if "close" in what or "all" in what: seg_close()

# ================= FULL-CUT EXTRA SEGMENTS =================
def seg_intro(dur=float(os.environ.get("DUR_INTRO","32"))):
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

def seg_threat(dur=float(os.environ.get("DUR_THREAT","42"))):
    files=sorted(glob.glob(SRC+"/threat/*.jpg")); ims=[ImageOps.exif_transpose(Image.open(f)).convert("RGB") for f in files]
    caps=json.load(open(SRC+"/threat/caps.json")) if os.path.exists(SRC+"/threat/caps.json") else [("","")]*len(ims)
    n=int(dur*FPS); per=n/len(ims)
    def fn(i,N):
        k=min(len(ims)-1,int(i/per)); t=(i-k*per)/per; im=ims[k]; fr=blur_bg(im)
        box=(0,200,W,1480); fr.paste(kb_frame(im,ease(t),1.0,1.14,0.5,0.5,box),(box[0],box[1]))
        band(fr,1500,1920,200); hl,sub=caps[k]
        y2=caption(fr,hl,1540,size=46,color=AMB); caption(fr,sub,y2+12,size=32,color=INK,bold=False,maxw=960)
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

# ================= COVER + MAP OPEN =================
def _font(cands,size):
    for c in cands:
        for d in ["/System/Library/Fonts/Supplemental/","/Library/Fonts/",os.path.expanduser("~/Library/Fonts/"),"/System/Library/Fonts/"]:
            p=d+c
            if os.path.exists(p): return ImageFont.truetype(p,size)
    return F(size,True)
def make_cover(out9,out16):
    base=Image.open(os.path.expanduser("~/Desktop/Ladera_Ranch_Broll_Pack/Promo_Instagram_9x16.jpg")).convert("RGB").resize((W,H),Image.LANCZOS)
    # keep only the textured blue ground: blur the old title away
    bg=base.filter(ImageFilter.GaussianBlur(40)); bg=Image.blend(bg,Image.new("RGB",(W,H),(38,48,62)),0.62)
    fr=bg.copy(); d=ImageDraw.Draw(fr)
    disp=lambda s:_font(["Didot.ttc","Bodoni 72.ttc","Baskerville.ttc","Georgia Bold.ttf"],s)
    def ctext(y,txt,font,fill,spacing=0):
        tw=d.textlength(txt,font=font)+spacing*max(0,len(txt)-1); x=(W-tw)/2
        if spacing:
            for ch in txt: d.text((x,y),ch,font=font,fill=fill); x+=d.textlength(ch,font=font)+spacing
        else: d.text((x,y),txt,font=font,fill=fill)
    ctext(150,"PHASE 2  ·  AN INDEPENDENT INVESTIGATION",F(30,True),(214,168,84),spacing=6)
    fs=150
    while d.textlength("LADERA RANCH",font=disp(fs))>960: fs-=4
    ctext(230+(150-fs)//2,"LADERA RANCH",disp(fs),(245,240,228))
    d.line([W/2-60,410,W/2+60,410],fill=(214,168,84),width=4)
    ctext(440,"ARSENIC",_font(["Arial Black.ttf","Arial Bold.ttf"],190),(214,168,84))
    ctext(660,"1907 to 1912. Eight pounds per five hundred gallons.",F(34),(210,214,222))
    ctext(720,"Every cow. Every fourteen days. On this ground.",F(34),(210,214,222))
    # the concrete base found
    ctext(830,"A CONCRETE DIP-VAT BASE.",F(58,True),(245,240,228))
    ctext(905,"FOUND.",disp(170),(214,168,84))
    # 1911 warning notice, quoted from the federal report
    bx=(110,1140,970,1440); d.rounded_rectangle(bx,radius=10,outline=(245,240,228),width=3,fill=(18,24,34))
    ctext(1165,"WARNING!",F(40,True),(245,240,228))
    ctext(1218,"The fluid in this vat is",F(30),(210,214,222))
    ctext(1262,"POISONOUS",disp(84),(214,168,84))
    ctext(1360,"to man and all animals.",F(30),(210,214,222))
    ctext(1400,"USDA Bureau of Animal Industry, 1911: the notice posted on every California vat",F(20),(150,156,168))
    ctext(1520,"UNTESTED FOR TWENTY YEARS.",F(46,True),(245,240,228))
    ctext(1600,"CALIFORNIA: TEST THE SOIL.",F(46,True),(214,168,84))
    ctext(1760,"SOUTH ORANGE COUNTY, CALIFORNIA",F(26,True),(150,156,168),spacing=5)
    fr.save(out9,quality=95)
    # 16x9 variant
    w16=Image.new("RGB",(1920,1080),(38,48,62)); c=fr.crop((0,120,W,1700)).resize((int(1080*W/1580),1080),Image.LANCZOS)
    side=bg.resize((1920,1080)).filter(ImageFilter.GaussianBlur(20)); w16.paste(side,(0,0)); w16.paste(c,((1920-c.width)//2,0)); w16.save(out16,quality=95)
    return fr

def seg_open(dur_cover=4.0,dur_map=13.0,dur_sat=17.0):
    cover=make_cover(HERE+"/cover_9x16.jpg",HERE+"/cover_16x9.jpg")
    mp=Image.open(os.path.expanduser("~/Documents/Ladera Ranch/evidence/lhdrs/mission7/sampling_target_map.png")).convert("RGB")
    sat=Image.open(os.path.expanduser("~/Documents/Ladera Ranch/evidence/lhdrs/mission7/oc_2025_aoi.jpg")).convert("RGB")
    AOI=(-117.670,33.524,-117.616,33.575); NODE=(-117.65492,33.55505)
    nx=(NODE[0]-AOI[0])/(AOI[2]-AOI[0])*sat.width; ny=(AOI[3]-NODE[1])/(AOI[3]-AOI[1])*sat.height
    mpp_x=(AOI[2]-AOI[0])*92500/sat.width  # metres per pixel
    nc=int(dur_cover*FPS); nm=int(dur_map*FPS); ns=int(dur_sat*FPS); n=nc+nm+ns
    def fn(i,N):
        if i<nc: return cover
        if i<nc+nm:
            t=ease((i-nc)/nm); fr=Image.new("RGB",(W,H),BG)
            # slow pan down the map at a zoom that fills the width
            mc=mp.crop((108,236,1188,1438)); cov=mc.resize((W,int(W*mc.height/mc.width)),Image.LANCZOS); y0=int(max(0,cov.height-1560)*t)
            fr.paste(cov.crop((0,y0,W,min(cov.height,y0+1560))),(0,0))
            band(fr,1560,1920,210); caption(fr,"WHERE TO TEST",1600,size=60,color=AMB)
            caption(fr,"Phase 2 map: 23 recommended sampling sites, ranked by where cattle gathered. The purple cross marks the 1948 ranch structure.",1680,size=30,color=INK,bold=False,maxw=960)
            tag(fr,"PHASE 2 · THE MAP THAT SENT ME OUT THERE",90); return fr
        t=ease((i-nc-nm)/ns)
        half=1400*(1-t)+380*t  # metres half-width: zoom from 2.8 km to 760 m
        hp=half/mpp_x; box=(int(nx-hp),int(ny-hp),int(nx+hp),int(ny+hp))
        tile=sat.crop(box).resize((W,W),Image.LANCZOS); fr=Image.new("RGB",(W,H),BG); oy=300; fr.paste(tile,(0,oy))
        ov=Image.new("RGBA",(W,H),(0,0,0,0)); od=ImageDraw.Draw(ov); cx,cy=W/2,oy+W/2
        r=max(60,int(160/mpp_x*W/(2*hp)))  # 160 m radius ring
        a=int(255*min(1,max(0,(t-0.15)*4)))
        od.ellipse([cx-r,cy-r,cx+r,cy+r],outline=RED+(a,),width=8); od.ellipse([cx-r-20,cy-r-20,cx+r+20,cy+r+20],outline=RED+(a//2,),width=3)
        fr.paste(ov,(0,0),ov)
        band(fr,1560,1920,210); caption(fr,"THE NODE",1600,size=60,color=AMB,alpha=a)
        caption(fr,"Open space above the community: a 1948 ranch structure and the 1968 stock-water points, on the drainage. The top-ranked area on the map.",1680,size=30,color=INK,bold=False,maxw=960,alpha=a)
        a2=int(255*min(1,max(0,(t-0.7)*6)))
        caption(fr,"So I took a hike.",1490,size=64,color=INK,align="center",x=0,alpha=a2)
        tag(fr,"ORANGE COUNTY AERIAL · 2025",90); return fr
    return render("open",n,fn)

if __name__=="__main__" and "open" in sys.argv: seg_open()

# ================= TOP PANELS for split layout (1080 x 1312) =================
def make_top_panels():
    TH=1312
    base=Image.open(os.path.expanduser("~/Desktop/Ladera_Ranch_Broll_Pack/Promo_Instagram_9x16.jpg")).convert("RGB").resize((W,H),Image.LANCZOS)
    bg=base.filter(ImageFilter.GaussianBlur(40)); bg=Image.blend(bg,Image.new("RGB",(W,H),(38,48,62)),0.62).crop((0,0,W,TH))
    disp=lambda s:_font(["Didot.ttc","Bodoni 72.ttc","Georgia Bold.ttf"],s)
    def panel(fr,items):
        d=ImageDraw.Draw(fr)
        for y,txt,font,fill,sp in items:
            tw=d.textlength(txt,font=font)+sp*max(0,len(txt)-1); x=(W-tw)/2
            if sp:
                for ch in txt: d.text((x,y),ch,font=font,fill=fill); x+=d.textlength(ch,font=font)+sp
            else: d.text((x,y),txt,font=font,fill=fill)
    # intro top
    fr=bg.copy(); d=ImageDraw.Draw(fr); fs=150
    while d.textlength("LADERA RANCH",font=disp(fs))>960: fs-=4
    panel(fr,[(70,"PHASE 2  ·  AN INDEPENDENT INVESTIGATION",F(28,True),(214,168,84),6),(130,"LADERA RANCH",disp(fs),(245,240,228),0),
              (330,"ARSENIC",_font(["Arial Black.ttf","Arial Bold.ttf"],170),(214,168,84),0),(520,"1907 to 1912. Eight pounds per five hundred gallons.",F(32),(210,214,222),0),
              (570,"Every cow. Every fourteen days. On this ground.",F(32),(210,214,222),0),(680,"A CONCRETE DIP-VAT BASE.",F(54,True),(245,240,228),0),(745,"FOUND.",disp(150),(214,168,84),0)])
    d.line([W/2-60,308,W/2+60,308],fill=(214,168,84),width=4)
    bx=(110,960,970,1180); d.rounded_rectangle(bx,radius=10,outline=(245,240,228),width=3,fill=(18,24,34))
    panel(fr,[(978,"WARNING!  The fluid in this vat is",F(30,True),(245,240,228),0),(1018,"POISONOUS",disp(80),(214,168,84),0),(1112,"to man and all animals.   USDA Bureau of Animal Industry, 1911",F(24),(210,214,222),0)])
    panel(fr,[(1225,"UNTESTED FOR TWENTY YEARS.  CALIFORNIA: TEST THE SOIL.",F(30,True),(214,168,84),0)])
    fr.save(HERE+"/top_intro.png")
    # closing top
    fr=bg.copy(); d=ImageDraw.Draw(fr)
    fs=260
    while d.textlength("THE SOIL.",font=disp(fs))>980: fs-=6
    panel(fr,[(120,"LADERA RANCH  ·  PHASE 2",F(30,True),(214,168,84),6),(230,"TEST",disp(fs),(245,240,228),0),(230+fs*0.95,"THE SOIL.",disp(fs),(214,168,84),0),
              (800,"A federal arsenic dipping program ran here, 1907 to 1912.",F(34),(210,214,222),0),(850,"A concrete vat base has been found.",F(34),(210,214,222),0),
              (900,"For twenty years, no one tested the ground.",F(34,True),(245,240,228),0),
              (1080,"Independent research project  ·  not medical advice  ·  establishes no causation",F(22),(150,156,168),0),
              (1115,"Figures are model estimates from documented herd sizes and the federal formula",F(22),(150,156,168),0),
              (1200,"CALIFORNIA: TEST THE SOIL.",F(34,True),(214,168,84),2)])
    fr.save(HERE+"/top_close.png"); print("top panels ok")
if __name__=="__main__" and "tops" in sys.argv: make_top_panels()


# ================= POND v2: scheduled to Andy's drone piece =================
def seg_pond2(total=77.6):
    win=json.load(open(SRC+"/pond/win.json")); WIN=win["WIN"]; P=win["pond"]; T6=win["tgt6"]
    years=["1929","1937","1947","1953","1960","1969","1980","1990","2004","2025"]
    tiles={y:Image.open(f"{SRC}/pond/era_{y}.jpg").convert("RGB") for y in years}
    tf=ImageOps.exif_transpose(Image.open(SRC+"/trail_fork.jpg")).convert("RGB")
    d20=Image.open(SRC+"/dji_0320.jpg").convert("RGB"); d21=Image.open(SRC+"/dji_0321.jpg").convert("RGB")
    S=W
    def xy(lon,lat): return ((lon-WIN[0])/(WIN[2]-WIN[0])*S,(WIN[3]-lat)/(WIN[3]-WIN[1])*S)
    def marks(fr,off):
        d=ImageDraw.Draw(fr); x,y=xy(*P); x+=off[0]; y+=off[1]
        for r,wd in [(70,6),(84,2)]: d.ellipse([x-r,y-r,x+r,y+r],outline=RED,width=wd)
        x6,y6=xy(*T6); x6+=off[0]; y6+=off[1]; d.ellipse([x6-40,y6-40,x6+40,y6+40],outline=CYAN,width=4)
    SCH=[(0,9.9,"tile2025"),(9.9,27.6,"post"),(27.6,34.6,"d20"),(34.6,44.0,"d21"),(44.0,71.0,"eras"),(71.0,total,"end")]
    n=int(total*FPS)
    def fn(i,N):
        t=i/FPS; fr=Image.new("RGB",(W,H),BG); box=(0,240,W,1540)
        for a,b,kind in SCH:
            if a<=t<b: break
        u=(t-a)/(b-a)
        if kind=="tile2025":
            fr.paste(tiles["2025"],(0,300)); marks(fr,(0,300)); tag(fr,"THE POND · BELOW THE VAT SITE",90)
            caption(fr,"The same ground, from the air",1440,size=48,color=AMB)
        elif kind=="post":
            fr=blur_bg(tf); fr.paste(kb_frame(tf,ease(u),1.0,1.12,0.45,0.45,box),(box[0],box[1])); mp=kb_map(tf,ease(u),1.0,1.12,0.45,0.45,box)
            ring(fr,mp(482,215),r=120,col=AMB,label="RANCH-ERA POST AND RAIL",lab_dx=150,lab_dy=-190)
            ring(fr,mp(505,590),r=80,col=CYAN,label="BIKE PATH MARKER",alpha=int(255*min(1,max(0,(u-0.2)*4))),lab_dx=120,lab_dy=60)
            tag(fr,"THE POST BY THE BIKE PATH",90); y2=caption(fr,"An old post and rail",1580,size=44,color=AMB); caption(fr,"Right beside the public trail.",y2+10,size=30,color=INK,bold=False)
        elif kind=="d20":
            fr=blur_bg(d20); fr.paste(kb_frame(d20,ease(u),1.0,1.08,0.72,0.5,box),(box[0],box[1])); mp=kb_map(d20,ease(u),1.0,1.08,0.72,0.5,box)
            ring(fr,mp(1186,773),r=90,col=CYAN,label="THE POND",lab_dx=-330,lab_dy=-160)
            ring(fr,mp(1700,760),r=150,col=(120,230,140),label="GOLF COURSE",alpha=int(255*min(1,max(0,(u-0.3)*4))),lab_dx=-320,lab_dy=170)
            tag(fr,"DRONE · THE POND AND THE FAIRWAY",90); caption(fr,"Next to the golf course",1580,size=44,color=AMB)
        elif kind=="d21":
            fr=blur_bg(d21); fr.paste(kb_frame(d21,ease(u),1.0,1.10,0.9,0.5,box),(box[0],box[1])); mp=kb_map(d21,ease(u),1.0,1.10,0.9,0.5,box)
            ring(fr,mp(1344,715),r=100,col=CYAN,label="STANDING WATER",lab_dx=-360,lab_dy=-200)
            ring(fr,mp(1000,824),r=330,col=AMB,label="DEAD VEGETATION",alpha=int(255*min(1,max(0,(u-0.25)*4))),lab_dx=-380,lab_dy=300)
            tag(fr,"DRONE · BELOW THE VAT SITE",90); caption(fr,"It all looks dead",1580,size=44,color=AMB)
        elif kind=="eras":
            per=(b-a)/len(years); k=min(len(years)-1,int((t-a)/per)); y=years[k]
            fr.paste(tiles[y],(0,300)); marks(fr,(0,300)); tag(fr,"THE SAME POND, 1929 TO 2025",90)
            caption(fr,y,1440,size=140,color=AMB)
            d=ImageDraw.Draw(fr); d.rectangle([60,1800,1020,1808],fill=(40,46,58)); d.rectangle([60,1800,60+960*((t-a)/(b-a)),1808],fill=AMB)
        else:
            fr.paste(tiles["2025"],(0,300)); marks(fr,(0,300)); d=ImageDraw.Draw(fr); x,y=xy(*P); y+=300
            ov=Image.new("RGBA",(W,H),(0,0,0,0)); od=ImageDraw.Draw(ov); a2=int(255*min(1,u*3))
            od.line([x+70,y-40,x+300,y-200],fill=AMB+(a2,),width=4); od.text((x+120,y-250),"DEAD VEGETATION RING",font=F(30,True),fill=AMB+(a2,))
            gx,gy=520,960; od.line([gx,gy,gx-260,gy+230],fill=(120,230,140,a2),width=4); od.text((80,gy+240),"GOLF COURSE FAIRWAY",font=F(30,True),fill=(120,230,140,a2))
            fr.paste(ov,(0,0),ov); tag(fr,"TEST THE POND · TEST AROUND IT",90); caption(fr,"2025",1440,size=140,color=AMB)
        return fr
    return render("pond2",n,fn)

def make_closing_card():
    base=Image.open(os.path.expanduser("~/Desktop/Ladera_Ranch_Broll_Pack/Promo_Instagram_9x16.jpg")).convert("RGB").resize((W,H),Image.LANCZOS)
    fr=Image.blend(base.filter(ImageFilter.GaussianBlur(40)),Image.new("RGB",(W,H),(38,48,62)),0.62); d=ImageDraw.Draw(fr)
    disp=lambda s:_font(["Didot.ttc","Bodoni 72.ttc","Georgia Bold.ttf"],s)
    def ctext(y,txt,font,fill,sp=0):
        tw=d.textlength(txt,font=font)+sp*max(0,len(txt)-1); x=(W-tw)/2
        if sp:
            for ch in txt: d.text((x,y),ch,font=font,fill=fill); x+=d.textlength(ch,font=font)+sp
        else: d.text((x,y),txt,font=font,fill=fill)
    fs=260
    while d.textlength("THE SOIL.",font=disp(fs))>980: fs-=6
    ctext(330,"LADERA RANCH  ·  PHASE 2",F(30,True),(214,168,84),6); ctext(440,"TEST",disp(fs),(245,240,228)); ctext(440+fs*0.95,"THE SOIL.",disp(fs),(214,168,84))
    ctext(1000,"A federal arsenic dipping program ran here, 1907 to 1912.",F(34),(210,214,222)); ctext(1050,"A concrete vat base has been found.",F(34),(210,214,222))
    ctext(1100,"For twenty years, no one tested the ground.",F(34,True),(245,240,228))
    ctext(1300,"Independent research project  ·  not medical advice  ·  establishes no causation",F(22),(150,156,168))
    ctext(1335,"Reconstruction imagery is AI-assisted, after USDA Circular 183 (1911); not historical footage",F(22),(150,156,168))
    ctext(1370,"Figures are model estimates from documented herd sizes and the federal formula",F(22),(150,156,168))
    ctext(1520,"CALIFORNIA: TEST THE SOIL.",F(40,True),(214,168,84),2)
    fr.save(HERE+"/closing_card_v2.png"); print("closing card v2 ok")
if __name__=="__main__" and "pond2" in sys.argv: seg_pond2()
if __name__=="__main__" and "card" in sys.argv: make_closing_card()
