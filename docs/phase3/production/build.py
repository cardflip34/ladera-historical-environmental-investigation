#!/usr/bin/env python3
"""Phase 3 builder. Reuses the Phase 2 visual system: 1080x1920, 24fps, PIL frames piped to ffmpeg."""
import os, sys, json, math, subprocess, glob
from PIL import Image, ImageDraw, ImageFont, ImageFilter
Image.MAX_IMAGE_PIXELS=None
HERE=os.path.dirname(os.path.abspath(__file__))
IMG=HERE+"/img"; NAR=HERE+"/nar"; OUT=HERE+"/seg"; os.makedirs(OUT,exist_ok=True)
W,H,FPS=1080,1920,24
FD="/System/Library/Fonts/Supplemental/"
def F(s,b=False): return ImageFont.truetype(FD+("Arial Bold" if b else "Arial")+".ttf",s)
BG=(12,16,24); AMB=(236,160,70); INK=(236,238,242); MUT=(160,166,178)
RED=(230,70,50); CYAN=(0,200,230); GRN=(80,205,140); VIO=(190,130,240); BLU=(90,160,240)
DUR=json.load(open(NAR+"/durations.json"))

def fit_cover(im,w,h):
    r=max(w/im.width,h/im.height); im=im.resize((int(im.width*r)+1,int(im.height*r)+1),Image.LANCZOS)
    x=(im.width-w)//2; y=(im.height-h)//2; return im.crop((x,y,x+w,y+h))
def fit_contain(im,w,h):
    r=min(w/im.width,h/im.height); return im.resize((max(1,int(im.width*r)),max(1,int(im.height*r))),Image.LANCZOS)
def blur_bg(im):
    b=fit_cover(im,W,H).filter(ImageFilter.GaussianBlur(28)); return Image.blend(b,Image.new("RGB",(W,H),BG),0.55)
def ease(t): return t*t*(3-2*t)
def kb(im,t,z0,z1,cx=0.5,cy=0.5,box=(0,0,W,H)):
    bw,bh=box[2]-box[0],box[3]-box[1]; z=z0+(z1-z0)*ease(t)
    cov=fit_cover(im,int(bw*z)+2,int(bh*z)+2)
    x=int((cov.width-bw)*cx); y=int((cov.height-bh)*cy)
    return cov.crop((x,y,x+bw,y+bh))
def wrap(d,text,font,maxw):
    words=text.split(); lines=[]; cur=""
    for w in words:
        t=(cur+" "+w).strip()
        if d.textlength(t,font=font)<=maxw: cur=t
        else:
            if cur: lines.append(cur)
            cur=w
    if cur: lines.append(cur)
    return lines
def caption(fr,text,y,size=44,color=INK,bold=True,maxw=None,align="left",x=60,alpha=255,shadow=True):
    if alpha<=0: return y
    if maxw is None: maxw=W-x-60
    ov=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov); f=F(size,bold)
    lines=wrap(d,text,f,maxw); lh=int(size*1.24)
    for i,l in enumerate(lines):
        tx=x if align=="left" else (W-d.textlength(l,font=f))/2
        if shadow: d.text((tx+3,y+i*lh+3),l,font=f,fill=(0,0,0,int(alpha*0.85)))
        d.text((tx,y+i*lh),l,font=f,fill=tuple(color)+(alpha,))
    fr.paste(ov,(0,0),ov); return y+len(lines)*lh
def band(fr,y0,y1,alpha=175):
    ov=Image.new("RGBA",(W,H),(0,0,0,0)); ImageDraw.Draw(ov).rectangle([0,y0,W,y1],fill=(8,10,16,alpha)); fr.paste(ov,(0,0),ov)
def tag(fr,text,y=70,col=AMB):
    d=ImageDraw.Draw(fr); f=F(26,True); tw=d.textlength(text,font=f)
    d.rectangle([60,y,60+tw+36,y+50],fill=col); d.text((78,y+9),text,font=f,fill=(16,14,10))
CLS={"DOCUMENTED":GRN,"APPROXIMATE":AMB,"INFERRED":BLU,"MODEL":VIO,"TESTABLE":RED,"UNKNOWN":MUT}
def cls_badge(fr,kind,y=140):
    col=CLS.get(kind,MUT); d=ImageDraw.Draw(fr); f=F(24,True); tw=d.textlength(kind,font=f)
    d.rounded_rectangle([60,y,60+tw+30,y+44],12,fill=(10,12,18),outline=col,width=3)
    d.text((75,y+9),kind,font=f,fill=col)
def cite(fr,lines,y=None):
    f=F(22,False); d=ImageDraw.Draw(fr)
    n=len(lines); lh=30; y=y if y is not None else H-90-n*lh
    ov=Image.new("RGBA",(W,H),(0,0,0,0)); dd=ImageDraw.Draw(ov)
    wmax=max(d.textlength(l,font=f) for l in lines)
    dd.rectangle([50,y-12,50+wmax+30,y+n*lh+10],fill=(8,10,16,190))
    for i,l in enumerate(lines): dd.text((66,y+i*lh),l,font=f,fill=MUT+(255,))
    fr.paste(ov,(0,0),ov)
def fade_a(i,n,fi=0.5,fo=0.6):
    t=i/FPS; T=n/FPS; a=1.0
    if t<fi: a=t/fi
    if t>T-fo: a=min(a,(T-t)/fo)
    return max(0.0,min(1.0,a))
def render(name,dur,fn,pad=1.1):
    n=int((dur+pad)*FPS)
    p=f"{OUT}/{name}.mp4"
    if os.path.exists(p) and os.path.getsize(p)>10000:
        print("skip",name); return p
    ff=subprocess.Popen(["ffmpeg","-y","-loglevel","error","-f","rawvideo","-pix_fmt","rgb24",
        "-s",f"{W}x{H}","-r",str(FPS),"-i","-","-c:v","libx264","-crf","17","-pix_fmt","yuv420p",
        "-video_track_timescale","12288",p],stdin=subprocess.PIPE)
    for i in range(n):
        fr=fn(i,n); a=fade_a(i,n)
        if a<1: fr=Image.blend(Image.new("RGB",(W,H),(0,0,0)),fr,a)
        ff.stdin.write(fr.tobytes())
    ff.stdin.close(); ff.wait(); print("wrote %-9s %5.1fs"%(name,n/FPS)); return p
def L(n): return Image.open(IMG+"/"+n).convert("RGB")

# ---------------- generic segment patterns ----------------
def seg_still(name,key,img,caps,cls=None,cites=None,z=(1.05,1.22),cx=0.5,cy=0.5,tagtxt=None):
    """One image, Ken Burns, captions timed across the block."""
    im=L(img); dur=DUR[key]
    def fn(i,n):
        t=i/max(1,n-1)
        fr=kb(im,t,z[0],z[1],cx,cy)
        band(fr,0,300,150); band(fr,H-560,H,165)
        if tagtxt: tag(fr,tagtxt)
        if cls: cls_badge(fr,cls)
        y=H-520
        k=int(t*len(caps))
        k=min(k,len(caps)-1)
        for j,c in enumerate(caps):
            a=255 if j<=k else 0
            if a: y=caption(fr,c,y,size=42 if j==0 else 36,color=INK if j==0 else MUT,bold=(j==0),alpha=a)+14
        if cites: cite(fr,cites)
        return fr
    return render(name,dur,fn)

def seg_seq(name,key,imgs,caps,cls=None,cites=None,tagtxt=None):
    """Sequence of images across the block with cross-fades."""
    ims=[L(x) for x in imgs]; dur=DUR[key]; n_im=len(ims)
    def fn(i,n):
        t=i/max(1,n-1); p=t*n_im; k=min(int(p),n_im-1); f=p-k
        a=kb(ims[k],min(1,f*0.6+0.2),1.06,1.18)
        if k+1<n_im and f>0.82:
            b=kb(ims[k+1],0.2,1.06,1.18); a=Image.blend(a,b,(f-0.82)/0.18)
        fr=a
        band(fr,0,300,150); band(fr,H-460,H,170)
        if tagtxt: tag(fr,tagtxt)
        if cls: cls_badge(fr,cls)
        c=caps[min(k,len(caps)-1)]
        caption(fr,c,H-420,size=40)
        if cites: cite(fr,cites)
        return fr
    return render(name,dur,fn)

def seg_title(name,key,big,small=None,col=AMB):
    dur=DUR[key]
    def fn(i,n):
        t=i/max(1,n-1)
        fr=Image.new("RGB",(W,H),BG); d=ImageDraw.Draw(fr)
        a=int(255*min(1,ease(min(1,t*2.5))))
        d.line([(60,H//2-150),(60+int(560*ease(min(1,t*2))),H//2-150)],fill=col+( ),width=6)
        caption(fr,big,H//2-110,size=86,color=col,alpha=a)
        if small: caption(fr,small,H//2+40,size=38,color=MUT,alpha=a)
        return fr
    return render(name,dur,fn,pad=0.6)

def seg_doczoom(name,key,img,quote,hl_frac,caps,cls="DOCUMENTED",cites=None,tagtxt=None):
    """Document page, slow push, highlight band sweeps over the quoted region, quote rises."""
    im=L(img); dur=DUR[key]
    def fn(i,n):
        t=i/max(1,n-1)
        page=fit_contain(im,W-80,H-520)
        fr=Image.new("RGB",(W,H),BG)
        sc=1.0+0.10*ease(t)
        pg=page.resize((int(page.width*sc),int(page.height*sc)),Image.LANCZOS)
        ox=(W-pg.width)//2; oy=140-int(60*ease(t))
        fr.paste(pg,(ox,oy))
        # highlight
        if t>0.12:
            hy0=oy+int(pg.height*hl_frac[0]); hy1=oy+int(pg.height*hl_frac[1])
            ov=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov)
            prog=min(1,(t-0.12)/0.30)
            d.rectangle([ox,hy0,ox+int(pg.width*prog),hy1],fill=(236,160,70,70))
            d.rectangle([ox,hy0,ox+int(pg.width*prog),hy1],outline=(236,160,70,220),width=4)
            fr.paste(ov,(0,0),ov)
        band(fr,H-540,H,190)
        if tagtxt: tag(fr,tagtxt)
        if cls: cls_badge(fr,cls)
        y=H-500
        if t>0.35:
            y=caption(fr,quote,y,size=40,color=AMB)+18
        if t>0.62:
            for c in caps: y=caption(fr,c,y,size=34,color=MUT,bold=False)+10
        if cites: cite(fr,cites)
        return fr
    return render(name,dur,fn)

# ---------------- diagram segments ----------------
X0,Y0,X1,Y1=-117.7000,33.5150,-117.5900,33.6000
def geo_to_px(lon,lat,src_w,src_h):
    return ((lon-X0)/(X1-X0)*src_w,(1-(lat-Y0)/(Y1-Y0))*src_h)

HORNO=[(-117.6400,33.5720,"1  Streets, roofs, lawns, slopes"),
       (-117.6440,33.5600,"2  Storm system / Sienna Botanica"),
       (-117.6480,33.5470,"3  Horno Creek"),
       (-117.6520,33.5330,"4  Horno Water Quality Basin"),
       (-117.6560,33.5270,"5  Seven acres of wetlands"),
       (-117.6300,33.5480,"6  Blend, then purple pipe")]

def seg_route(name,key):
    base=L("ae_2022.jpg"); dur=DUR[key]
    bw,bh=base.size
    pts=[(geo_to_px(l,a,bw,bh),t) for l,a,t in HORNO]
    def fn(i,n):
        t=i/max(1,n-1)
        z=1.30-0.22*ease(t)
        cov=fit_cover(base,int(W*z)+2,int(H*z)+2)
        sx=cov.width/bw; sy=cov.height/bh
        offx=(cov.width-W)*0.52; offy=(cov.height-H)*0.48
        fr=cov.crop((int(offx),int(offy),int(offx)+W,int(offy)+H))
        fr=Image.blend(fr,Image.new("RGB",(W,H),BG),0.28)
        ov=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov)
        k=min(len(pts)-1,int(t*len(pts)*1.05))
        prev=None
        for j,((px,py),lab) in enumerate(pts):
            x=px*sx-offx; y=py*sy-offy
            if j>k: break
            if prev is not None:
                d.line([prev,(x,y)],fill=CYAN+(210,),width=7)
            d.ellipse([x-20,y-20,x+20,y+20],outline=CYAN+(255,),width=6)
            d.ellipse([x-6,y-6,x+6,y+6],fill=CYAN+(255,))
            prev=(x,y)
        fr.paste(ov,(0,0),ov)
        band(fr,0,300,150); band(fr,H-470,H,180)
        tag(fr,"THE ROUTE"); cls_badge(fr,"DOCUMENTED")
        caption(fr,pts[k][1],H-430,size=44,color=CYAN)
        cite(fr,["Tentative Addendum No. 4 to Order No. 97-52,","San Diego RWQCB, certifying adoption 8 Oct 2008","(tentative copy held). Findings 3 and 4.",
                 "Base: Orange County aerial imagery."])
        return fr
    return render(name,dur,fn)

def seg_twosys(name,key):
    dur=DUR[key]
    def fn(i,n):
        t=i/max(1,n-1); fr=Image.new("RGB",(W,H),BG); d=ImageDraw.Draw(fr)
        caption(fr,"TWO SEPARATE SYSTEMS",120,size=52,color=INK,align="center",x=0)
        a1=ease(min(1,t*2.2)); a2=ease(max(0,min(1,(t-0.42)*2.2)))
        def chain(y0,col,title,items,alpha):
            if alpha<=0.01: return
            A=int(255*alpha)
            caption(fr,title,y0,size=40,color=col,alpha=A)
            yy=y0+80
            for idx,it in enumerate(items):
                d.rounded_rectangle([90,yy,W-90,yy+96],14,outline=col+(),width=4)
                dd=ImageDraw.Draw(fr); f=F(34,True)
                dd.text((124,yy+28),it,font=f,fill=col)
                if idx<len(items)-1:
                    d.line([(W//2,yy+96),(W//2,yy+132)],fill=col,width=5)
                    d.polygon([(W//2-12,yy+124),(W//2+12,yy+124),(W//2,yy+142)],fill=col)
                yy+=132
        chain(260,BLU,"POTABLE  ·  drinking water",["Imported source","Potable storage","Distribution main","Tap  ·  tested annually"],a1)
        chain(1050,VIO,"NON-POTABLE  ·  recycled",["Recycled + diversion water","Non-potable storage","Purple-pipe distribution","Landscape irrigation"],a2)
        if t>0.86:
            band(fr,H-190,H,200)
            caption(fr,"Different pipes. Different storage. Different testing history.",H-160,size=34,color=MUT,bold=False)
        cls_badge(fr,"DOCUMENTED",y=H-260)
        return fr
    return render(name,dur,fn)

def seg_blend(name,key):
    dur=DUR[key]
    def fn(i,n):
        t=i/max(1,n-1); fr=Image.new("RGB",(W,H),BG); d=ImageDraw.Draw(fr)
        caption(fr,"TWO STREAMS, ONE BLEND",110,size=48,color=INK,align="center",x=0)
        yA,yB,yM=520,900,710
        aA=ease(min(1,t*2.4)); aB=ease(max(0,min(1,(t-0.22)*2.4))); aM=ease(max(0,min(1,(t-0.5)*2.4)))
        if aA>0.01:
            d.rounded_rectangle([70,yA-70,600,yA+70],16,outline=CYAN,width=5)
            caption(fr,"Recycled water effluent",yA-46,size=34,color=CYAN,x=100)
            caption(fr,"Provision K.2 sampling point",yA+4,size=26,color=MUT,bold=False,x=100)
        if aB>0.01:
            d.rounded_rectangle([70,yB-70,600,yB+70],16,outline=GRN,width=5)
            caption(fr,"Horno diversion water",yB-46,size=34,color=GRN,x=100)
            caption(fr,"basin + 7 acres wetlands · K.1",yB+4,size=26,color=MUT,bold=False,x=100)
        if aM>0.01:
            d.line([(600,yA),(820,yM)],fill=CYAN,width=6)
            d.line([(600,yB),(820,yM)],fill=GRN,width=6)
            d.ellipse([820-46,yM-46,820+46,yM+46],outline=AMB,width=6)
            caption(fr,"BLEND",yM-18,size=30,color=AMB,x=880)
            d.line([(866,yM),(1000,yM)],fill=AMB,width=6)
        if t>0.70:
            band(fr,H-560,H,185)
            y=caption(fr,"Two monitoring points, for two streams, that meet downstream.",H-530,size=38,color=INK)
            y=caption(fr,"Incoherent if the runoff had already passed through the plant.",y+12,size=34,color=MUT,bold=False)
            caption(fr,"CHIQUITA WATER RECLAMATION PLANT  —  not in this stream's path",y+24,size=30,color=RED)
        cls_badge(fr,"INFERRED",y=H-660)
        cite(fr,["Provision K.1 and K.2, Tentative Addendum No. 4 to","Order No. 97-52 (tentative copy held)."])
        return fr
    return render(name,dur,fn)

def seg_audit(name,key):
    dur=DUR[key]
    def fn(i,n):
        t=i/max(1,n-1); fr=Image.new("RGB",(W,H),BG); d=ImageDraw.Draw(fr)
        caption(fr,"TWO DIFFERENT QUESTIONS",100,size=46,color=INK,align="center",x=0)
        # left: compounding fails
        bx0,bx1=80,W-80
        d.rounded_rectangle([bx0,240,bx1,830],16,outline=MUT,width=3)
        caption(fr,"WATER CONCENTRATION",280,size=34,color=MUT,x=120)
        ax0,ay0,ax1,ay1=140,760,bx1-60,400
        d.line([(ax0,ay0),(ax0,ay1)],fill=MUT,width=3); d.line([(ax0,ay0),(ax1,ay0)],fill=MUT,width=3)
        pts=[]
        prog=min(1,max(0,(t-0.05)/0.38))
        for s in range(0,int(60*prog)+1):
            u=s/60.0
            v=1.0+0.13*(1-math.exp(-4*u))
            x=ax0+(ax1-ax0)*u; y=ay0-(ay0-ay1)*((v-1.0)/0.30)
            pts.append((x,y))
        if len(pts)>1: d.line(pts,fill=VIO,width=6)
        if prog>0.9:
            caption(fr,"caps at ×1.02 – ×1.28",640,size=32,color=VIO,x=180)
            caption(fr,"FAILS",700,size=44,color=RED,x=180)
        # right: deposition survives
        d.rounded_rectangle([bx0,880,bx1,1470],16,outline=MUT,width=3)
        caption(fr,"SOIL DEPOSITION",920,size=34,color=MUT,x=120)
        bx,by0,by1=140,1400,1040
        d.line([(bx,by0),(bx,by1)],fill=MUT,width=3); d.line([(bx,by0),(ax1,by0)],fill=MUT,width=3)
        prog2=min(1,max(0,(t-0.46)/0.40))
        if prog2>0:
            pts2=[(bx+(ax1-bx)*(s/60.0),by0-(by0-by1)*(s/60.0)) for s in range(int(60*prog2)+1)]
            if len(pts2)>1: d.line(pts2,fill=GRN,width=6)
        if prog2>0.85:
            caption(fr,"linear, over two decades",1280,size=32,color=GRN,x=180)
            caption(fr,"TESTABLE",1340,size=44,color=RED,x=180)
        if t>0.88:
            band(fr,H-260,H,190)
            caption(fr,"Whether anything of concern is present at all remains unknown without testing.",H-230,size=34,color=MUT,bold=False)
        cls_badge(fr,"MODEL",y=1520)
        return fr
    return render(name,dur,fn)

def seg_soilcols(name,key):
    dur=DUR[key]
    def fn(i,n):
        t=i/max(1,n-1); fr=Image.new("RGB",(W,H),BG); d=ImageDraw.Draw(fr)
        caption(fr,"THREE KINDS OF GROUND",110,size=48,color=INK,align="center",x=0)
        cols=[("Ploughed, then graded",[("mixed",AMB),("cut or buried",RED)],RED),
              ("Ploughed, never graded",[("mixed",AMB),("intact",GRN)],AMB),
              ("Never farmed, never cut",[("intact",GRN),("intact",GRN)],GRN)]
        cw=300; gap=40; x0=(W-(cw*3+gap*2))//2
        for j,(title,layers,col) in enumerate(cols):
            a=ease(max(0,min(1,(t-j*0.22)*3.0)))
            if a<0.01: continue
            x=x0+j*(cw+gap); yTop=380; hgt=820
            d.rectangle([x,yTop,x+cw,yTop+hgt],outline=col,width=4)
            d.rectangle([x+3,yTop+3,x+cw-3,yTop+int(hgt*0.22)],fill=(90,70,40))
            d.rectangle([x+3,yTop+int(hgt*0.22),x+cw-3,yTop+hgt-3],fill=(52,58,68) if j<1 else (60,72,58))
            caption(fr,title,yTop+hgt+40,size=28,color=col,x=x,maxw=cw)
            caption(fr,"plough zone ≈ 1 ft",yTop+int(hgt*0.09),size=22,color=INK,x=x+14,maxw=cw-20,bold=False)
        if t>0.70:
            band(fr,H-300,H,190)
            y=caption(fr,"The third column still holds its original surface.",H-270,size=40,color=GRN)
            caption(fr,"It is the most informative ground on the map.",y+10,size=34,color=MUT,bold=False)
        cls_badge(fr,"INFERRED",y=H-380)
        return fr
    return render(name,dur,fn)

def seg_control(name,key):
    dur=DUR[key]
    def fn(i,n):
        t=i/max(1,n-1); fr=Image.new("RGB",(W,H),BG); d=ImageDraw.Draw(fr)
        caption(fr,"A NUMBER ONLY MEANS SOMETHING",110,size=44,color=INK,align="center",x=0)
        caption(fr,"NEXT TO ANOTHER NUMBER",165,size=44,color=INK,align="center",x=0)
        labs=[("Source area",AMB),("Undisturbed control",GRN),("Regional background",BLU)]
        bx=160; bw=200; base=1180
        for j,(lab,col) in enumerate(labs):
            a=ease(max(0,min(1,(t-0.10-j*0.14)*3.2)))
            if a<0.01: continue
            hgt=int(360*a) if j==0 else int(330*a)
            x=bx+j*(bw+80)
            d.rectangle([x,base-hgt,x+bw,base],fill=col)
            caption(fr,lab,base+30,size=26,color=col,x=x,maxw=bw+40)
        if t>0.62:
            d.line([(140,base-330),(W-140,base-330)],fill=MUT,width=3)
            caption(fr,"If these read the same, that is an answer.",base+140,size=38,color=GRN,align="center",x=0)
            caption(fr,"A real one — and the most valuable result this could produce.",base+200,size=32,color=MUT,bold=False,align="center",x=0)
        cls_badge(fr,"TESTABLE",y=H-200)
        return fr
    return render(name,dur,fn)

def seg_network(name,key):
    """Seven-point water testing network, schematic."""
    dur=DUR[key]
    PTS=[("W1","Horno upstream","before any treatment"),
         ("W2","Basin outlet","what settling removes"),
         ("W3","Wetland outlet","the whole treatment train"),
         ("W4","Recycled effluent","the other input, alone"),
         ("W5","Post-blend storage","what enters the pipes"),
         ("W6","Sprinkler head","what reaches the ground"),
         ("W7","Irrigation return","what the soil kept")]
    def fn(i,n):
        t=i/max(1,n-1); fr=Image.new("RGB",(W,H),BG); d=ImageDraw.Draw(fr)
        caption(fr,"SEVEN POINTS",100,size=54,color=INK,align="center",x=0)
        caption(fr,"the smallest design that can tell sources apart",162,size=30,color=MUT,bold=False,align="center",x=0)
        y0=300; step=190
        k=int(t*len(PTS)*1.08)
        for j,(cd,lab,why) in enumerate(PTS):
            if j>k: break
            y=y0+j*step
            col=RED if cd in ("W6","W3") else CYAN
            d.ellipse([90,y-34,158,y+34],outline=col,width=5)
            f=F(28,True); d.text((104,y-15),cd,font=f,fill=col)
            caption(fr,lab,y-34,size=38,color=INK,x=190)
            caption(fr,why,y+10,size=28,color=MUT,bold=False,x=190)
            if j<len(PTS)-1 and j<k:
                d.line([(124,y+34),(124,y+step-34)],fill=(70,80,95),width=4)
        if t>0.86:
            band(fr,H-170,H,195)
            caption(fr,"W6 and S1 first, if only two are funded.",H-140,size=34,color=AMB)
        cls_badge(fr,"TESTABLE",y=H-250)
        return fr
    return render(name,dur,fn)

def seg_layers(name,key):
    """Final integrated map: eight layers building on the 2022 aerial."""
    base=L("ae_2022.jpg"); dur=DUR[key]; bw,bh=base.size
    LAY=[("Possible concrete structures","APPROXIMATE",AMB),
         ("23 historical water-source targets","DOCUMENTED",GRN),
         ("Grading · cut and fill","MODEL",VIO),
         ("Horno drainage system","DOCUMENTED",CYAN),
         ("Basin + constructed wetlands","DOCUMENTED",CYAN),
         ("Recycled / purple-pipe system","DOCUMENTED",VIO),
         ("Proposed water testing","TESTABLE",RED),
         ("Proposed soil / sediment testing","TESTABLE",RED)]
    import random
    rnd=random.Random(7)
    seeds=[[(rnd.uniform(0.18,0.82),rnd.uniform(0.18,0.82)) for _ in range(6)] for _ in LAY]
    def fn(i,n):
        t=i/max(1,n-1)
        z=1.34-0.26*ease(t)
        cov=fit_cover(base,int(W*z)+2,int(H*z)+2)
        offx=(cov.width-W)*0.52; offy=(cov.height-H)*0.46
        fr=cov.crop((int(offx),int(offy),int(offx)+W,int(offy)+H))
        fr=Image.blend(fr,Image.new("RGB",(W,H),BG),0.34)
        ov=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov)
        k=min(len(LAY)-1,int(t*len(LAY)*1.03))
        for j in range(k+1):
            lab,cls,col=LAY[j]
            for (fx,fy) in seeds[j]:
                x=fx*W; y=fy*H
                if cls=="APPROXIMATE":
                    d.ellipse([x-46,y-46,x+46,y+46],outline=col+(120,),width=3)
                    d.ellipse([x-16,y-16,x+16,y+16],outline=col+(240,),width=4)
                elif cls=="TESTABLE":
                    d.polygon([(x,y-20),(x+18,y+14),(x-18,y+14)],outline=col+(245,))
                    d.polygon([(x,y-20),(x+18,y+14),(x-18,y+14)],fill=col+(90,))
                elif cls=="MODEL":
                    d.rectangle([x-24,y-16,x+24,y+16],fill=col+(70,),outline=col+(170,),width=2)
                else:
                    d.ellipse([x-13,y-13,x+13,y+13],fill=col+(235,))
        fr.paste(ov,(0,0),ov)
        band(fr,0,260,155); band(fr,H-430,H,185)
        tag(fr,"ALL LAYERS")
        lab,cls,col=LAY[k]
        cls_badge(fr,cls)
        caption(fr,"%d / 8   %s"%(k+1,lab),H-390,size=42,color=col)
        caption(fr,"Legend distinguishes documented, approximate, model and proposed by shape and colour.",H-320,size=26,color=MUT,bold=False)
        return fr
    return render(name,dur,fn)

def seg_end(name,key):
    base=L("ae_2022.jpg"); dur=DUR[key]
    def fn(i,n):
        t=i/max(1,n-1)
        fr=kb(base,t,1.18,1.02,0.52,0.46)
        g=fr.convert("L").convert("RGB")
        fr=Image.blend(fr,g,min(1,ease(t)*1.1))
        fr=Image.blend(fr,Image.new("RGB",(W,H),BG),0.30+0.30*ease(t))
        ov=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov)
        import random
        rnd=random.Random(11)
        for _ in range(9):
            x=rnd.uniform(0.15,0.85)*W; y=rnd.uniform(0.2,0.8)*H
            a=int(255*min(1,max(0,(t-0.25)*2.0)))
            d.polygon([(x,y-22),(x+19,y+15),(x-19,y+15)],outline=RED+(a,))
            d.polygon([(x,y-22),(x+19,y+15),(x-19,y+15)],fill=RED+(int(a*0.35),))
        fr.paste(ov,(0,0),ov)
        band(fr,H-720,H,int(150+90*ease(t)))
        y=H-680
        lines=[("It has not shown you a dipping vat.",38,MUT),
               ("It has not shown you contamination.",38,MUT),
               ("It has not shown you a single laboratory result —",38,MUT),
               ("because there aren't any.",40,INK),
               ("",10,MUT),
               ("The records tell us where to look.",52,AMB),
               ("Someone should look.",52,AMB)]
        show=int(min(len(lines),max(0,(t-0.18)/0.62*len(lines))+1))
        for j,(s,sz,col) in enumerate(lines[:show]):
            if not s: y+=20; continue
            y=caption(fr,s,y,size=sz,color=col,bold=(col is AMB))+14
        return fr
    return render(name,dur,fn)

# ---------------- the film ----------------
def main():
    C_NMG=["NMG Geotechnical, Phase I ESA, project 01079-02,","4 February 2002 · DTSC EnviroStor 30020004."]
    C_589=["EIR 589 Appendix I, Phase I ESA,","Rancho Mission Viejo, 2003 rev. Feb 2004."]
    C_PCT=["Ladera Planned Community Program Text,","17 Oct 1995 rev. 30 Jul 2003 · recovered by OCR."]
    C_USDA=["USDA Bureau of Animal Industry, Circular 207, 1912.","Public domain."]
    C_FDEP=["Florida Dept. of Environmental Protection,","Cattle Dip Vat programme photographs, 2016–18.","FLORIDA — not Ladera Ranch."]
    C_PERMIT=["Tentative Addendum No. 4 to Order No. 97-52,","San Diego RWQCB, certifying adoption 8 Oct 2008","(tentative copy held)."]
    C_AER=["Orange County Historic Imagery, OID 310 (1937),","357 (1953), 315 (1969). Native 1.15 ft/px at best."]

    seg_still("01_open","OPEN","vat_plan.jpg",
        ["In 1911 the federal government ordered ranchers here to build a concrete trough and fill it with arsenic.",
         "A concrete base was found on a public trail in Ladera Ranch.",
         "Nobody has ever tested the soil around it."],
        cls="DOCUMENTED",cites=C_USDA,tagtxt="PHASE 3",z=(1.35,1.06))
    seg_title("02_p1","P1TITLE","PART ONE","The concrete structures")
    seg_seq("03_whatisvat","S2",["vat_plan.jpg","vat_1912.jpg","vat_1941.jpg","fl_overgrown.jpg","fl_trench.jpg","fl_flooded.jpg","fl_drippad.jpg"],
        ["26 feet long · 6½ feet deep · sloped entry, ramp, drip pen",
         "A vat in use, May 1912","The sloped concrete entry, 1941",
         "The state agency that photographed this called it an overgrown cattle dip vat — FLORIDA",
         "Reeds mark the line of the trench — FLORIDA",
         "A well-preserved example, with the stepped ramp — FLORIDA",
         "And beside the trough, the drip pad slab — FLORIDA"],
        cls="DOCUMENTED",cites=C_FDEP,tagtxt="WHAT SURVIVES")
    seg_still("04_sweep","S3","doc_eir589toc.jpg",
        ["159 terms. Seven registers. 470 pages.",
         "22 of them are the correct names: dip vat, cattle dip, plunge vat, tick eradication, sodium arsenite.",
         "0 / 22.  Not once."],
        cls="DOCUMENTED",cites=["LEHRP terminology sweep, 20 Sept 2026.","159 terms · 6 documents · 470 pages."],tagtxt="THE SWEEP",z=(1.02,1.18))
    seg_doczoom("05_trw","S4","doc_trw.jpg",
        "“two large concrete-lined containment sumps”",
        (0.42,0.62),
        ["Every concrete passage in the record names what the concrete was for.",
         "For open grazing land the wording is a petroleum-and-drums checklist."],
        cites=C_589,tagtxt="THE VOCABULARY EXISTS")
    seg_doczoom("06_quest","S5","doc_quest1.jpg",
        "“any pits, ponds, or lagoons … in connection with waste treatment or waste disposal”",
        (0.55,0.68),
        ["A vat is a pit. The answer was no.",
         "Two questions earlier the same person volunteered: “we used to dump oil off the corner of the shop building.”",
         "Nobody was hiding anything. The question did not reach."],
        cites=C_589,tagtxt="THE QUESTIONNAIRE")
    seg_still("07_kino","S6","kino_vault.jpg",
        ["San Juan Capistrano, February 2009.",
         "Mobilised 20 Feb · concrete pad demolished 23 Feb. Three days.",
         "Identified in the record as the farmer's tank containment, out of service.",
         "The photograph itself is undated in the report."],
        cls="DOCUMENTED",cites=["Environ Strategy Consultants, Soil Excavation Report,","Kinoshita Farm, project 476, 3 April 2009, §§4–5, Appendix E.","GeoTracker case T10000000266."],tagtxt="PHOTOGRAPHED FIRST",z=(1.06,1.20))
    seg_seq("08_ladera02","S7",["lad_01.jpg","lad_03.jpg","lad_09.jpg","lad_10.jpg","lad_12.jpg","lad_16.jpg"],
        ["“East view of site's northern portion” — 31 January 2002",
         "“South view of site's western side”",
         "“Desilting basin” — the only structure on the site",
         "“East view of roadway located north of site”",
         "“Northeast view of property located east of site”",
         "“Structures west of site” — described as temporary in appearance"],
        cls="DOCUMENTED",cites=C_NMG,tagtxt="LADERA RANCH, 2002")
    seg_doczoom("09_cond22","S8","doc_cond22.jpg",
        "“… and observance of grading activities …”",
        (0.30,0.52),
        ["Condition 22, on every Area Plan and every tract map.",
         "Board of Supervisors Resolution 77-866.",
         "Those reports have never been read."],
        cites=C_PCT,tagtxt="SOMEBODY WAS REQUIRED TO WATCH")
    seg_still("10_p1map","S9","map_zoning.jpg",
        ["One concrete base, located approximately.",
         "Two wells named in the record.",
         "Ten aerial anomalies tested — all resolved as drainage, brush or ranch track.",
         "So where would you test?"],
        cls="APPROXIMATE",cites=C_PCT,tagtxt="PART ONE · THE MAP",z=(1.04,1.16))

    seg_title("11_p2","P2TITLE","PART TWO","Where should the soil be tested")
    seg_seq("12_farm","S10",["ae37_sw.jpg","ae53_sw.jpg","ann_block.png","ann_fields.png"],
        ["1937 — open rangeland. No field boundaries.",
         "1953 — contour ploughing across the ridgetops and valley floors.",
         "A surname. 230.0 acres. 1945. And a crop.",
         "Field numbers circled in ink, and the word “Beans”, over and over."],
        cls="DOCUMENTED",cites=C_AER,tagtxt="THE LAND WAS FARMED")
    seg_still("13_grading","S11","lad_siteplan.jpg",
        ["Mass grading 1999 to summer 2001.",
         "“up to 110 feet of soil fill”",
         "“removed prior to fill placement … placed at lower depths during fill placement”",
         "The plans say how much earth moved. Not which earth went where."],
        cls="DOCUMENTED",cites=C_NMG,tagtxt="THEN IT WAS MOVED",z=(1.03,1.15))
    seg_soilcols("14_cols","S12")
    seg_still("15_targets","S13","map_disturb.png",
        ["Every surface water body recorded by the 1968 survey.",
         "A vat needs thousands of gallons on a fortnightly cycle. You build it where the water is.",
         "23 locations — each re-examined against what is there today, and offset to accessible ground."],
        cls="APPROXIMATE",cites=["LEHRP soil sampling strategy · targets_data.json","Water bodies: 1968 USGS survey."],tagtxt="THE TWENTY-THREE",z=(1.22,1.02))
    seg_control("16_control","S14")
    seg_still("17_methods","S15","fl_drippad.jpg",
        ["0–6 inches, where a child's hand reaches. Plus a fill-depth interval.",
         "EPA 3050B / 3051A digestion · 6020B ICP-MS · speciation by HPLC-ICP-MS where warranted.",
         "Standard methods. Ordinary laboratories."],
        cls="TESTABLE",cites=["Analytical methods per the project sampling plan."],tagtxt="WHAT A SAMPLE IS",z=(1.10,1.24))

    seg_title("18_p3","P3TITLE","PART THREE","The purple pipe loop",col=VIO)
    seg_twosys("19_twosys","S16")
    seg_route("20_route","S17")
    seg_blend("21_blend","S18")
    seg_doczoom("22_tested","S19","permit_p1.png",
        "TDS 686 · Sulfate 349 · Sodium 57 · Chloride 48.5 · Boron 0.22 · Nitrate 0.6 · Fluoride 0.275 · Phosphorus 0.4",
        (0.72,0.95),
        ["Salts and nutrients. November 2004 to April 2005.",
         "Not on the list: arsenic · a pesticide panel · pharmaceuticals.",
         "It does not mean they are there. It means nobody looked."],
        cites=C_PERMIT,tagtxt="WHAT WAS MEASURED")
    seg_audit("23_audit","S20")
    seg_still("24_pest","S21","ann_fields.png",
        ["Beans and barley for decades. Intensively landscaped now.",
         "Both are reasons to TEST for pesticides.",
         "Neither is evidence that pesticides are circulating."],
        cls="UNKNOWN",cites=C_AER,tagtxt="PESTICIDES, CAREFULLY",z=(1.05,1.18))
    seg_network("25_network","S22")
    seg_layers("26_layers","S23")
    seg_end("27_end","END")

if __name__=="__main__":
    main()
