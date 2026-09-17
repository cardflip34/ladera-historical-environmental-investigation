import numpy as np, subprocess, os, glob, math, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
D=os.path.dirname(os.path.abspath(__file__))
W,H=1920,1080; FPS=24
VW,VH=1080,1920; FY=656  # vertical canvas, video band top
FD="/System/Library/Fonts/Supplemental/"
def F(n,s): return ImageFont.truetype(FD+n,s)
SB=lambda s:F("Georgia Bold.ttf",s); SR=lambda s:F("Georgia.ttf",s); SA=lambda s:F("Arial.ttf",s); SAB=lambda s:F("Arial Bold.ttf",s)
def ss(a,b,x):
    t=min(max((x-a)/(b-a),0),1); return t*t*(3-2*t)
# ---- timeline (seconds) ----
INTRO=2.0; SEG=3.0; PULL=2.4; OUTRO=2.2; XF=0.45
CLIPS=[("clip_01_aerial.mp4",0.0),("clip_02_pens.mp4",0.0),("clip_03_chute.mp4",0.0),("clip_04_vat.mp4",0.4),("clip_05_drip.mp4",0.0),("clip_06_pullback.mp4",0.0)]
segs=[]; t=INTRO
for i,(fn,off) in enumerate(CLIPS):
    L=PULL if i==5 else SEG
    segs.append((t,t+L,fn,off)); t+=L
END=t+OUTRO; N=int(round(END*FPS))
CAPS=[(0.2,INTRO+0.3,"LADERA RANCH OPEN SPACE · 2026","Iron pipe rails lead to a surviving concrete base in the brush"),
 (segs[0][0]+0.2,segs[0][1],"O'NEILL RANCH · c. 1910","AI-assisted reconstruction of a federal-specification cattle dipping station"),
 (segs[1][0]+0.1,segs[1][1],"RECEIVING & RETAINING PENS","Every animal, every 14 days, by order of the federal program"),
 (segs[2][0]+0.1,segs[2][1],"THE CHUTE","30 inches wide, 20 feet long, single file toward the vat"),
 (segs[3][0]+0.1,segs[3][1],"THE VAT","Concrete, 26 ft at the rim, 6.5 ft deep · 8 lb arsenic trioxide per 500 gallons"),
 (segs[4][0]+0.1,segs[4][1],"THE DRIPPING PEN","Drippings drain to a sunken barrel and are returned to the vat"),
 (segs[5][0]+0.1,segs[5][1]+0.2,"1907 – 1912","Five years of compulsory dipping on this land")]
# frame caches
def clip_frames(fn,off,L):
    out=os.path.join(D,"tmp_"+fn.replace(".mp4",""))
    os.makedirs(out,exist_ok=True)
    if not glob.glob(out+"/*.png"):
        subprocess.run(["ffmpeg","-y","-loglevel","error","-ss",str(off),"-t",str(L+0.2),"-i",os.path.join(D,fn),"-vf",f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}","-r",str(FPS),out+"/f_%04d.png"],check=True)
    return sorted(glob.glob(out+"/*.png"))
FRAMES={}
for (a,b,fn,off) in segs:
    FRAMES[fn]=clip_frames(fn,off,b-a)
ph=Image.open(os.path.join(D,"..","..","vatvid","IMG_4499_1080.jpg")).convert("RGB")
bgp=ph.resize((W,int(W*ph.height/ph.width))).crop((0,300,W,300+H)).filter(ImageFilter.GaussianBlur(28))
bgp=Image.eval(bgp,lambda v:int(v*0.45))
def intro_v(t):
    z=1.0+0.06*t/INTRO
    fw=int(VW*z); fh=int(fw*ph.height/ph.width)
    im=ph.resize((fw,fh),Image.LANCZOS)
    x=(fw-VW)//2; y=max(0,(fh-VH)//2)
    im=im.crop((x,y,x+VW,y+VH))
    if im.height<VH:
        c=Image.new("RGB",(VW,VH),(8,10,14)); c.paste(im,(0,(VH-im.height)//2)); im=c
    return im
def to_vertical(im16):
    bg=im16.resize((int(VH*W/H),VH),Image.BILINEAR)
    x=(bg.width-VW)//2; bg=bg.crop((x,0,x+VW,VH)).filter(ImageFilter.GaussianBlur(34))
    bg=Image.eval(bg,lambda v:int(v*0.42))
    band=im16.resize((VW,int(VW*H/W)),Image.LANCZOS)
    bg.paste(band,(0,FY)); return bg
def seg_frame(t):
    for (a,b,fn,off) in segs:
        if a<=t<b:
            i=min(len(FRAMES[fn])-1,int((t-a)*FPS)); return Image.open(FRAMES[fn][i]).convert("RGB"),(a,b)
    a,b,fn,off=segs[-1]; return Image.open(FRAMES[fn][-1]).convert("RGB"),(a,b)
def base(t):
    if t<INTRO-XF: return intro_v(t)
    if t<INTRO:
        k=ss(INTRO-XF,INTRO,t); nxt,_=seg_frame(INTRO); return Image.blend(intro_v(t),to_vertical(nxt),k)
    im,(a,b)=seg_frame(t)
    if b-XF<=t<b and b<segs[-1][1]:
        k=ss(b-XF,b,t); nxt,_=seg_frame(b); im=Image.blend(im,nxt,k)
    return to_vertical(im)
def frame(o):
    t=o/FPS
    im=base(min(t,segs[-1][1]-0.001)).convert("RGBA")
    ov=Image.new("RGBA",(VW,VH),(0,0,0,0)); d=ImageDraw.Draw(ov)
    intro_phase=t<INTRO
    if intro_phase:
        for y in range(1200,VH):
            a=int(200*((y-1200)/(VH-1200))**1.1); d.line([(0,y),(VW,y)],fill=(8,10,14,a))
    for a0,a1,ti,su in CAPS:
        al=min(ss(a0,a0+0.4,t),1-ss(a1-0.35,a1,t))
        if al<=0: continue
        A=int(255*al)
        d.text((VW/2,1330),ti,font=SB(52),fill=(240,196,120,A),anchor="ma")
        # wrap subtitle to two lines if long
        words=su.split(); lines=[]; cur=""
        for w_ in words:
            if len(cur)+len(w_)+1>44: lines.append(cur); cur=w_
            else: cur=(cur+" "+w_).strip()
        lines.append(cur)
        for j,l in enumerate(lines): d.text((VW/2,1405+j*44),l,font=SA(33),fill=(232,234,238,A),anchor="ma")
    if INTRO<=t<segs[-1][1]:
        ba=int(255*min(ss(INTRO,INTRO+0.4,t),1-ss(segs[-1][1]-0.4,segs[-1][1],t)))
        d.text((VW/2,470),"AI-ASSISTED RECONSTRUCTION",font=SAB(30),fill=(240,196,120,ba),anchor="ma")
        d.text((VW/2,515),"not historical footage · after USDA Circular 183 (1911)",font=SA(24),fill=(200,204,212,ba),anchor="ma")
        d.text((VW/2,300),"What the O'Neill Ranch may have looked like",font=SB(40),fill=(232,234,238,ba),anchor="ma")
        d.text((VW/2,355),"during compulsory arsenic cattle dipping, 1907–1912",font=SR(32),fill=(232,234,238,ba),anchor="ma")
    im=Image.alpha_composite(im,ov)
    t0=segs[-1][1]-0.4
    if t>=t0:
        k=ss(t0,t0+0.7,t); im=Image.alpha_composite(im,Image.new("RGBA",(VW,VH),(8,10,14,int(215*k))))
        d=ImageDraw.Draw(im); A=int(255*ss(t0+0.3,t0+0.9,t))
        d.text((VW/2,700),"Only the concrete",font=SB(70),fill=(240,196,120,A),anchor="ma")
        d.text((VW/2,785),"survives a century.",font=SB(70),fill=(240,196,120,A),anchor="ma")
        d.text((VW/2,920),"Timber pens, chute and splash boards rot away.",font=SR(36),fill=(232,234,238,A),anchor="ma")
        d.text((VW/2,970),"What remains is a concrete base",font=SR(36),fill=(232,234,238,A),anchor="ma")
        d.text((VW/2,1020),"and iron rails in the brush.",font=SR(36),fill=(232,234,238,A),anchor="ma")
        d.text((VW/2,1130),"The soil has never been tested.",font=SB(48),fill=(240,196,120,A),anchor="ma")
        d.text((VW/2,1300),"AI-assisted reconstruction, not historical footage",font=SA(26),fill=(170,176,186,A),anchor="ma")
        d.text((VW/2,1340),"Layout and dimensions: USDA Bureau of Animal Industry Circular 183 (1911)",font=SA(24),fill=(170,176,186,A),anchor="ma")
        d.text((VW/2,1380),"Not an established identification of this site · depth unmeasured",font=SA(24),fill=(170,176,186,A),anchor="ma")
    return im.convert("RGB")
if __name__=="__main__":
    if len(sys.argv)>1 and sys.argv[1] not in ("all","--mux"):
        for o in [int(x) for x in sys.argv[1:]]: frame(o).resize((540,960)).save(os.path.join(D,f"fcomp_{o}.jpg"),quality=85)
        print("segments:",[(round(a,1),round(b,1),fn) for a,b,fn,_ in segs],"END",round(END,1)); sys.exit()
    vid=os.path.join(D,"fal_video_only.mp4")
    if "--mux" in sys.argv and os.path.exists(vid): p=None
    else: p=subprocess.Popen(["ffmpeg","-y","-loglevel","error","-f","rawvideo","-pix_fmt","rgb24","-s",f"{VW}x{VH}","-r",str(FPS),"-i","-","-c:v","libx264","-pix_fmt","yuv420p","-crf","17","-preset","slow",vid],stdin=subprocess.PIPE)
    if p:
        for o in range(N): p.stdin.write(np.asarray(frame(o)).tobytes())
        p.stdin.close(); p.wait()
    # audio: each clip's own ambient sound placed on the timeline, faded, mixed
    inputs=[]; fc=[]; labels=[]
    for i,(a,b,fn,off) in enumerate(segs):
        inputs+=["-i",os.path.join(D,fn)]
        L=b-a
        fc.append(f"[{i+1}:a]atrim=start={off}:end={off+L},asetpts=PTS-STARTPTS,afade=t=in:d=0.4,afade=t=out:st={L-0.5}:d=0.5,adelay={int(a*1000)}|{int(a*1000)},volume=0.9[a{i}]")
        labels.append(f"[a{i}]")
    fc.append("".join(labels)+f"amix=inputs={len(segs)}:normalize=0,afade=t=out:st={END-1.5}:d=1.5[aout]")
    out=os.path.join(D,"Dipping_Station_Reel_9x16.mp4")
    subprocess.run(["ffmpeg","-y","-loglevel","error","-i",vid]+inputs+["-filter_complex",";".join(fc),"-map","0:v","-map","[aout]","-c:v","copy","-c:a","aac","-b:a","192k","-t",str(END),"-movflags","+faststart",out],check=True)
    print("wrote",out)
