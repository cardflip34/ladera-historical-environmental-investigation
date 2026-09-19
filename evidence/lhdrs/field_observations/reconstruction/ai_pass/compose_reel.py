import numpy as np, subprocess, os, glob, math, sys
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import blueprint as BP
from PIL import Image, ImageDraw, ImageFont, ImageFilter
D=os.path.dirname(os.path.abspath(__file__))
W,H=1920,1080; VW,VH=1080,1920; FY=656; FPS=24; XF=0.6
FD="/System/Library/Fonts/Supplemental/"
def F(n,s): return ImageFont.truetype(FD+n,s)
SB=lambda s:F("Georgia Bold.ttf",s); SR=lambda s:F("Georgia.ttf",s); SA=lambda s:F("Arial.ttf",s); SAB=lambda s:F("Arial Bold.ttf",s)
def ss(a,b,x):
    t=min(max((x-a)/(b-a),0),1); return t*t*(3-2*t)
AMB=(255,190,70)
# ---------------- timeline ----------------
SEGS=[]  # (start,end,kind,src,offset)
def add(kind,src,L,off=0.0):
    a=SEGS[-1][1] if SEGS else 0.0; SEGS.append((a,a+L,kind,src,off))
add("intro","IMG_4499",3.0)
add("clip","clip_01_aerial.mp4",4.8); add("clip","clip_02_pens.mp4",4.8); add("clip","clip_03_chute.mp4",4.6)
add("clip","clip_07_pour.mp4",4.8)
add("clip","clip_04_vat.mp4",4.6,0.4)
add("revealA","photo_04_vat.png",4.5)
add("revealB","IMG_4497",4.0)
add("blueprint","IMG_4497",7.5)
add("clip","clip_05_drip.mp4",4.6); add("clip","clip_06_pullback.mp4",4.2)
add("wide","clip_08_wide.mp4",12.0)
OUTRO=3.2; END=SEGS[-1][1]+OUTRO; N=int(round(END*FPS))
def seg_at(kind): return next(s for s in SEGS if s[2]==kind and True)
tA=[s for s in SEGS if s[2]=="revealA"][0]; tB=[s for s in SEGS if s[2]=="revealB"][0]; tC=[s for s in SEGS if s[2]=="blueprint"][0]; tW=[s for s in SEGS if s[2]=="wide"][0]
import json
TRACK=json.load(open(os.path.join(D,"..","wide","site_track.json")))
WIDE=sorted(glob.glob(os.path.join(D,"..","wide","w_*.png")))
LAST=SEGS[-1][1]
CAPS=[(0.2,3.0,"LADERA RANCH OPEN SPACE · 2026","Iron pipe rails lead to a surviving concrete base in the brush"),
 (SEGS[1][0]+0.2,SEGS[1][1],"O'NEILL RANCH · c. 1910","AI-assisted reconstruction of a federal-specification cattle dipping station"),
 (SEGS[2][0]+0.1,SEGS[2][1],"RECEIVING & RETAINING PENS","Every animal, every 14 days, by order of the federal program"),
 (SEGS[3][0]+0.1,SEGS[3][1],"THE CHUTE","30 inches wide, 20 feet long, single file toward the vat"),
 (SEGS[4][0]+0.1,SEGS[4][1],"CHARGING THE VAT","8 lb of arsenic trioxide per 500 gallons, poured in by hand, as the state instructed"),
 (SEGS[5][0]+0.1,SEGS[5][1],"THE VAT","Concrete, 26 ft at the rim, 6.5 ft deep · every animal swims the full length"),
 (SEGS[9][0]+0.1,SEGS[9][1],"THE DRIPPING PEN","Drippings drain to a sunken barrel and are returned to the vat"),
 (SEGS[10][0]+0.1,SEGS[10][1]+0.2,"1907 – 1912","Five years of compulsory dipping on this land")]
# ---------------- sources ----------------
def clip_frames(fn,off,L):
    out=os.path.join(D,"tmp_"+fn.replace(".mp4",""))
    os.makedirs(out,exist_ok=True)
    if not glob.glob(out+"/*.png"):
        subprocess.run(["ffmpeg","-y","-loglevel","error","-ss",str(off),"-t",str(L+0.3),"-i",os.path.join(D,fn),"-vf",f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}","-r",str(FPS),out+"/f_%04d.png"],check=True)
    return sorted(glob.glob(out+"/*.png"))
FR={s[3]:clip_frames(s[3],s[4],s[1]-s[0]) for s in SEGS if s[2]=="clip"}
PH99=Image.open(os.path.join(D,"..","..","vatvid","IMG_4499_1080.jpg")).convert("RGB")
PH97=Image.open(os.path.join(D,"..","..","vatvid","IMG_4497_1080.jpg")).convert("RGB")
VAT=Image.open(os.path.join(D,"photo_04_vat.png")).convert("RGB").resize((W,H),Image.LANCZOS)
def fit_portrait(ph,z=1.0):
    fh=int(VH*z); fw=int(fh*ph.width/ph.height); im=ph.resize((fw,fh),Image.LANCZOS)
    x=(fw-VW)//2; y=(fh-VH)//2; return im.crop((x,y,x+VW,y+VH))
def to_vertical(im16):
    bg=im16.resize((int(VH*W/H),VH),Image.BILINEAR); x=(bg.width-VW)//2
    bg=bg.crop((x,0,x+VW,VH)).filter(ImageFilter.GaussianBlur(34)); bg=Image.eval(bg,lambda v:int(v*0.42))
    bg.paste(im16.resize((VW,int(VW*H/W)),Image.LANCZOS),(0,FY)); return bg
# geometry: concrete floor section on the vat still (16:9 px) -> vertical canvas
QUAD_VAT=[(x*VW/W, y*VW/W+FY) for x,y in [(366,940),(889,430),(1258,430),(1235,940)]]
# rim of the real concrete base in IMG_4497 (1080x1440 px) -> full-bleed vertical (scale 1.3333, x-180)
QUAD_TODAY=[tuple(p) for p in BP.CORN]
def raw(t):
    for a,b,kind,src,off in SEGS:
        if a<=t<b:
            if kind=="intro": return fit_portrait(PH99,1.0+0.06*t/2.0),(a,b,kind)
            if kind=="clip":
                i=min(len(FR[src])-1,int((t-a)*FPS)); return to_vertical(Image.open(FR[src][i]).convert("RGB")),(a,b,kind)
            if kind=="revealA": return to_vertical(VAT),(a,b,kind)
            if kind=="revealB": return fit_portrait(PH97,1.0),(a,b,kind)
            if kind=="blueprint": return fit_portrait(PH97,1.0),(a,b,kind)
            if kind=="wide":
                i=min(len(WIDE)-1,int((t-a)*FPS/2)); return to_vertical(Image.open(WIDE[i]).convert("RGB")),(a,b,kind)
    a,b,kind,src,off=SEGS[-1]; return to_vertical(Image.open(FR[src][-1]).convert("RGB")),(a,b,kind)
def base(t):
    im,(a,b,kind)=raw(t)
    if b-XF<=t<b and b<LAST:
        nxt,_=raw(b); im=Image.blend(im,nxt,ss(b-XF,b,t))
    return im
def glow_poly(d,pts,prog,fade,fill_alpha=0):
    closed=pts+[pts[0]]
    L=[math.hypot(closed[i+1][0]-closed[i][0],closed[i+1][1]-closed[i][1]) for i in range(len(pts))]
    tot=sum(L); target=prog*tot; out=[closed[0]]; acc=0
    for i in range(len(pts)):
        if acc+L[i]>=target:
            f=(target-acc)/L[i]; out.append((closed[i][0]+(closed[i+1][0]-closed[i][0])*f, closed[i][1]+(closed[i+1][1]-closed[i][1])*f)); break
        out.append(closed[i+1]); acc+=L[i]
    if fill_alpha>0 and prog>=1: d.polygon(pts,fill=AMB+(int(fill_alpha*fade),))
    for wdt,al in ((22,45),(12,110),(5,255)):
        if len(out)>1: d.line(out,fill=AMB+(int(al*fade),),width=wdt,joint="curve")
    tip=out[-1]
    if prog<1:
        for r,al in ((26,40),(15,110),(7,255)): d.ellipse([tip[0]-r,tip[1]-r,tip[0]+r,tip[1]+r],fill=(255,240,200,int(al*fade)))
def wrap(d,text,y,font,fill,maxc):
    words=text.split(); lines=[]; cur=""
    for w_ in words:
        if len(cur)+len(w_)+1>maxc: lines.append(cur); cur=w_
        else: cur=(cur+" "+w_).strip()
    lines.append(cur)
    for j,l in enumerate(lines): d.text((VW/2,y+j*(font.size+10)),l,font=font,fill=fill,anchor="ma")
def frame(o):
    t=o/FPS
    im=base(min(t,LAST-0.001)).convert("RGBA")
    ov=Image.new("RGBA",(VW,VH),(0,0,0,0)); d=ImageDraw.Draw(ov)
    a,b,kind=raw(min(t,LAST-0.001))[1]
    if kind in ("intro","revealB","blueprint"):
        for y in range(1150,VH):
            al=int(215*((y-1150)/(VH-1150))**1.1); d.line([(0,y),(VW,y)],fill=(8,10,14,al))
    # standard captions
    for a0,a1,ti,su in CAPS:
        al=min(ss(a0,a0+0.4,t),1-ss(a1-0.35,a1,t))
        if al<=0: continue
        A=int(255*al); d.text((VW/2,1330),ti,font=SB(52),fill=AMB+(A,),anchor="ma"); wrap(d,su,1405,SA(33),(232,234,238,A),44)
    # header (reconstruction segments only)
    if SEGS[1][0]<=t<tA[0] or SEGS[9][0]-XF<=t<LAST:
        ba=int(255*min(ss(SEGS[1][0],SEGS[1][0]+0.4,t),1-ss(tA[0]-0.4,tA[0],t)) if t<tA[0] else 255*min(ss(SEGS[9][0]-XF,SEGS[9][0],t),1-ss(LAST-0.4,LAST,t)))
        d.text((VW/2,300),"What the O'Neill Ranch may have looked like",font=SB(40),fill=(232,234,238,ba),anchor="ma")
        d.text((VW/2,355),"during compulsory arsenic cattle dipping, 1907–1912",font=SR(32),fill=(232,234,238,ba),anchor="ma")
        d.text((VW/2,470),"AI-ASSISTED RECONSTRUCTION",font=SAB(30),fill=AMB+(ba,),anchor="ma")
        d.text((VW/2,515),"not historical footage · after USDA Circular 183 (1911)",font=SA(24),fill=(200,204,212,ba),anchor="ma")
    # ---------- REVEAL A: the concrete floor section on the reconstructed vat ----------
    if tA[0]-XF<=t<tA[1]+XF:
        u=t-tA[0]
        vis=min(ss(tA[0]-0.2,tA[0]+0.3,t),1-ss(tA[1]-0.25,tA[1]+0.2,t))
        # darken everything except the section
        dark=Image.new("RGBA",(VW,VH),(8,10,14,int(150*ss(0.2,1.0,u)*vis)))
        m=Image.new("L",(VW,VH),255); ImageDraw.Draw(m).polygon(QUAD_VAT,fill=0)
        m=m.filter(ImageFilter.GaussianBlur(6)); dark.putalpha(Image.fromarray((np.asarray(dark.split()[3]).astype(np.float32)*np.asarray(m).astype(np.float32)/255).astype(np.uint8)))
        ov=Image.alpha_composite(ov,dark); d=ImageDraw.Draw(ov)
        glow_poly(d,QUAD_VAT,ss(0.3,1.5,u),vis,fill_alpha=55+25*math.sin(t*4))
        A=int(255*ss(1.2,1.7,u)*vis)
        d.text((VW/2,150),"THIS IS WHAT SURVIVED",font=SB(64),fill=AMB+(A,),anchor="ma")
        d.text((VW/2,250),"The 12-foot concrete floor of the vat",font=SR(40),fill=(232,234,238,A),anchor="ma")
        d.text((VW/2,310),"is the piece of concrete found in Ladera Ranch today",font=SR(34),fill=(232,234,238,A),anchor="ma")
        d.text((VW/2,1330),"TIMBER ROTS · IRON RUSTS · CONCRETE STAYS",font=SAB(30),fill=AMB+(A,),anchor="ma")
        wrap(d,"The pens, chute and splash boards are long gone. The concrete base beneath the dip solution is what a century leaves behind.",1395,SA(31),(232,234,238,A),46)
    # ---------- REVEAL B: the real photo, same outline ----------
    if tB[0]-XF<=t<tB[1]+XF:
        u=t-tB[0]
        vis=min(ss(tB[0]-0.2,tB[0]+0.3,t),1-ss(tB[1]-0.25,tB[1]+0.05,t))
        q=QUAD_TODAY
        glow_poly(d,q,ss(0.2,1.5,u),vis,fill_alpha=40)
        A=int(255*ss(0.1,0.6,u)*vis)
        if A>0: d.rounded_rectangle([60,120,VW-60,330],16,fill=(8,10,14,int(165*A/255)))
        d.text((VW/2,140),"LADERA RANCH OPEN SPACE · 2026",font=SB(44),fill=AMB+(A,),anchor="ma")
        d.text((VW/2,205),"The same shape, 115 years later.",font=SR(40),fill=(232,234,238,A),anchor="ma")
        d.text((VW/2,262),"A 12-foot concrete rectangle, hidden in the brush.",font=SR(34),fill=(232,234,238,A),anchor="ma")
        A2=int(255*ss(1.6,2.1,u)*vis)
        if A2>0: d.rounded_rectangle([60,1295,VW-60,1520],16,fill=(8,10,14,int(175*A2/255)))
        d.text((VW/2,1330),"FOUND · PHOTOGRAPHED · UNTESTED",font=SAB(30),fill=AMB+(A2,),anchor="ma")
        wrap(d,"Iron pipe rails still run up to it. Its depth has not been measured. The soil around it has never been tested for arsenic.",1395,SA(31),(232,234,238,A2),46)

    # ---------- BLUEPRINT: build the station back, in perspective, on the real photo ----------
    if tC[0]<=t<tC[1]+XF:
        u=t-tC[0]
        vis=min(ss(tC[0],tC[0]+0.3,t),1-ss(tC[1]-0.3,tC[1]+0.1,t))
        dim=Image.new("RGBA",(VW,VH),(6,8,14,int(150*ss(0.0,0.8,u)*vis)))
        ov=Image.alpha_composite(ov,dim)
        d=BP.draw_blueprint(ov,u,vis,(SAB(24),SA(20),SB(48),SR(30)))
        A=int(255*ss(0.2,0.7,u)*vis)
        if A>0:
            d.rounded_rectangle([60,110,VW-60,300],16,fill=(8,10,14,int(170*A/255)))
            d.text((VW/2,128),"REBUILT TO THE FEDERAL PLAN",font=SB(50),fill=AMB+(A,),anchor="ma")
            d.text((VW/2,200),"From the concrete that survives, the 1911 station",font=SR(32),fill=(232,234,238,A),anchor="ma")
            d.text((VW/2,244),"drawn back in place, in true perspective",font=SR(32),fill=(232,234,238,A),anchor="ma")
        A2=int(255*ss(5.8,6.3,u)*vis)
        if A2>0:
            d.rounded_rectangle([60,1600,VW-60,1800],16,fill=(8,10,14,int(175*A2/255)))
            d.rectangle([100,1640,140,1680],fill=AMB+(A2,)); d.text((160,1642),"OBSERVED  ·  concrete photographed 2026",font=SAB(28),fill=(232,234,238,A2))
            d.rectangle([100,1712,140,1752],fill=(150,220,255,A2)); d.text((160,1714),"INTERPRETED  ·  USDA Circular 183 (1911) dimensions",font=SAB(28),fill=(232,234,238,A2))

    # ---------- WIDE: the whole ranch, multiple stations ----------
    if tW[0]<=t<tW[1]+XF:
        u=t-tW[0]; fi=min(len(WIDE)-1,int(u*FPS/2))
        vis=min(ss(tW[0],tW[0]+0.3,t),1-ss(tW[1]-0.3,tW[1]+0.1,t))
        pts=TRACK[str(fi)]
        sc_=VW/W
        for k,(px,py) in enumerate(pts):
            x=px*W*sc_; y=py*H*sc_+FY
            if not (0<x<VW and FY<y<FY+VW*H/W): continue
            col=AMB if k==0 else (150,220,255)
            r=int((26 if k==0 else 22)*(1+0.12*math.sin(t*5+k)))
            show=ss(0.2,0.8,u) if k==0 else ss(3.0+1.2*k,3.6+1.2*k,u)
            A=int(255*show*vis)
            if A<=0: continue
            for rr,al in ((r+14,40),(r+6,110),(r,255)): d.ellipse([x-rr,y-rr,x+rr,y+rr],outline=col+(int(al*show*vis),),width=4)
            lab="CONCRETE BASE FOUND · 2026" if k==0 else "CANDIDATE STATION"
            sub="the vat you saw rebuilt" if k==0 else "1968 stock-water point · unconfirmed"
            lx=min(max(x-160,30),VW-360); ly=y-r-92 if y-r-92>FY+20 else y+r+14
            d.rounded_rectangle([lx-10,ly-6,lx+340,ly+62],8,fill=(8,10,14,int(170*show*vis)))
            d.text((lx,ly),lab,font=SAB(24),fill=col+(A,)); d.text((lx,ly+32),sub,font=SA(20),fill=(232,234,238,A))
        A2=int(255*ss(1.0,1.6,u)*vis)
        if A2>0:
            d.text((VW/2,1330),"THREE TO SEVEN VATS",font=SB(52),fill=AMB+(A2,),anchor="ma")
            wrap(d,"A herd of 25,000 could not be dipped at one station. Candidate sites follow the ranch's mapped water points and drainages. Positions illustrative; only one has been found.",1405,SA(31),(232,234,238,A2),46)
    im=Image.alpha_composite(im,ov)
    t0=LAST-0.4
    if t>=t0:
        k=ss(t0,t0+0.7,t); im=Image.alpha_composite(im,Image.new("RGBA",(VW,VH),(8,10,14,int(215*k))))
        d=ImageDraw.Draw(im); A=int(255*ss(t0+0.3,t0+0.9,t))
        d.text((VW/2,700),"Only the concrete",font=SB(70),fill=AMB+(A,),anchor="ma")
        d.text((VW/2,785),"survives a century.",font=SB(70),fill=AMB+(A,),anchor="ma")
        d.text((VW/2,920),"Timber pens, chute and splash boards rot away.",font=SR(36),fill=(232,234,238,A),anchor="ma")
        d.text((VW/2,970),"What remains is a concrete base",font=SR(36),fill=(232,234,238,A),anchor="ma")
        d.text((VW/2,1020),"and iron rails in the brush.",font=SR(36),fill=(232,234,238,A),anchor="ma")
        d.text((VW/2,1130),"The soil has never been tested.",font=SB(48),fill=AMB+(A,),anchor="ma")
        d.text((VW/2,1300),"AI-assisted reconstruction, not historical footage",font=SA(26),fill=(170,176,186,A),anchor="ma")
        d.text((VW/2,1340),"Layout and dimensions: USDA Bureau of Animal Industry Circular 183 (1911)",font=SA(24),fill=(170,176,186,A),anchor="ma")
        d.text((VW/2,1380),"Not an established identification of this site · depth unmeasured",font=SA(24),fill=(170,176,186,A),anchor="ma")
    return im.convert("RGB")
if __name__=="__main__":
    if len(sys.argv)>1 and sys.argv[1] not in ("all","--mux"):
        for o in [int(x) for x in sys.argv[1:]]: frame(o).resize((540,960)).save(os.path.join(D,f"rcomp_{o}.jpg"),quality=85)
        print([(round(a,1),round(b,1),k) for a,b,k,_,_ in SEGS],"END",round(END,1)); sys.exit()
    vid=os.path.join(D,"reel_video_only.mp4")
    if not ("--mux" in sys.argv and os.path.exists(vid)):
        p=subprocess.Popen(["ffmpeg","-y","-loglevel","error","-f","rawvideo","-pix_fmt","rgb24","-s",f"{VW}x{VH}","-r",str(FPS),"-i","-","-c:v","libx264","-pix_fmt","yuv420p","-crf","17","-preset","slow",vid],stdin=subprocess.PIPE)
        for o in range(N): p.stdin.write(np.asarray(frame(o)).tobytes())
        p.stdin.close(); p.wait()
    inputs=[]; fc=[]; labels=[]; k=1
    def has_audio(p):
        r=subprocess.run(["ffmpeg","-i",p],capture_output=True,text=True).stderr
        return "Audio:" in r
    for a,b,kind,src,off in SEGS:
        if kind!="clip" or not has_audio(os.path.join(D,src)): continue
        L=(b-a)+(0.0)   # let the vat ambience carry under Reveal A
        L=min(L,5.1-off)
        inputs+=["-i",os.path.join(D,src)]
        fc.append(f"[{k}:a]atrim=start={off}:end={off+L},asetpts=PTS-STARTPTS,afade=t=in:d=0.4,afade=t=out:st={L-0.8}:d=0.8,adelay={int(a*1000)}|{int(a*1000)},volume=0.9[a{k}]"); labels.append(f"[a{k}]"); k+=1
    fc.append("".join(labels)+f"amix=inputs={k-1}:normalize=0,afade=t=out:st={END-1.5}:d=1.5[aout]")
    out=os.path.join(D,"Dipping_Station_Reel_9x16.mp4")
    subprocess.run(["ffmpeg","-y","-loglevel","error","-i",vid]+inputs+["-filter_complex",";".join(fc),"-map","0:v","-map","[aout]","-c:v","copy","-c:a","aac","-b:a","192k","-t",str(END),"-movflags","+faststart",out],check=True)
    print("wrote",out)
