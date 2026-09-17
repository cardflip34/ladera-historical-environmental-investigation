import numpy as np, subprocess, os, glob, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter
D=os.path.dirname(os.path.abspath(__file__))
FR=sorted(glob.glob(os.path.join(D,"frames","f_*.png")))
assert len(FR)==384, len(FR)
W,H=1920,1080; FPS=24; N=480
FD="/System/Library/Fonts/Supplemental/"
def F(name,s): return ImageFont.truetype(FD+name,s)
SERIF_B=lambda s:F("Georgia Bold.ttf",s); SERIF=lambda s:F("Georgia.ttf",s); SANS=lambda s:F("Arial.ttf",s); SANS_B=lambda s:F("Arial Bold.ttf",s)
def ss(a,b,x):
    t=min(max((x-a)/(b-a),0),1); return t*t*(3-2*t)
# intro photo (today)
ph=Image.open(os.path.join(D,"..","vatvid","IMG_4499_1080.jpg")).convert("RGB")
bgp=ph.resize((W,int(W*ph.height/ph.width))).crop((0,300,W,300+H)).filter(ImageFilter.GaussianBlur(28))
bgp=Image.eval(bgp,lambda v:int(v*0.45))
def intro(t):
    z=1.0+0.05*t/2.6
    fh=int(H*z); fw=int(fh*ph.width/ph.height)
    f=ph.resize((fw,fh),Image.LANCZOS)
    im=bgp.copy()
    im.paste(f,((W-fw)//2,(H-fh)//2))
    return im
cache={}
def render(i):
    i=max(0,min(383,i))
    return Image.open(FR[i]).convert("RGB")
CAPS=[(0.25,2.3,"LADERA RANCH OPEN SPACE · 2026","Iron pipe rails lead to a surviving concrete base in the brush"),
      (2.9,6.1,"O'NEILL RANCH · c. 1910","Interpretive reconstruction of a federal-specification cattle dipping station"),
      (6.4,9.3,"RECEIVING & RETAINING PENS","Range herds gathered in for compulsory dipping, every animal every 14 days"),
      (9.5,11.3,"THE CHUTE","30 inches wide, 20 feet long, single file toward the vat"),
      (11.5,14.2,"THE VAT","Concrete, 26 ft at the rim, 6.5 ft deep · 8 lb arsenic trioxide per 500 gallons of dip"),
      (14.4,17.2,"THE DRIPPING PEN","12 × 15 ft concrete floor · drippings drain to a sunken barrel and return to the vat")]
def frame(o):
    t=o/FPS
    if o<48: im=intro(t)
    elif o<66:
        a=ss(48,66,o); im=Image.blend(intro(t),render(o-48),a)
    elif o<432: im=render(o-48)
    else: im=render(383)
    im=im.convert("RGBA")
    ov=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov)
    # lower-third gradient
    for y in range(760,H):
        a=int(170*((y-760)/(H-760))**1.3); d.line([(0,y),(W,y)],fill=(8,10,14,a))
    for a0,a1,ti,su in CAPS:
        al=min(ss(a0,a0+0.4,t),1-ss(a1-0.35,a1,t))
        if al<=0: continue
        A=int(255*al)
        d.text((86,905),ti,font=SERIF_B(54),fill=(240,196,120,A))
        d.text((88,978),su,font=SANS(34),fill=(232,234,238,A))
    if 2.9<=t<18.0:
        ba=int(255*min(ss(2.9,3.3,t),1-ss(17.6,18.0,t)))
        d.rounded_rectangle([60,50,760,104],10,fill=(8,10,14,int(150*ba/255)))
        d.text((80,63),"INTERPRETIVE RECONSTRUCTION · after USDA Circular 183 (1911)",font=SANS_B(24),fill=(240,196,120,ba))
    im=Image.alpha_composite(im,ov)
    if t>=17.6:
        k=ss(17.6,18.3,t)
        dark=Image.new("RGBA",(W,H),(8,10,14,int(200*k))); im=Image.alpha_composite(im,dark)
        d=ImageDraw.Draw(im); A=int(255*ss(17.9,18.6,t))
        d.text((W/2,360),"Only the concrete survives a century.",font=SERIF_B(66),fill=(240,196,120,A),anchor="ma")
        d.text((W/2,470),"Timber pens, chute and splash boards rot away.",font=SERIF(40),fill=(232,234,238,A),anchor="ma")
        d.text((W/2,525),"What remains is a concrete base and iron rails in the brush.",font=SERIF(40),fill=(232,234,238,A),anchor="ma")
        d.text((W/2,690),"Interpretive reconstruction · layout and dimensions from USDA Bureau of Animal Industry Circular 183 (1911)",font=SANS(26),fill=(170,176,186,A),anchor="ma")
        d.text((W/2,730),"Not an established identification of this site · depth unmeasured · soil untested",font=SANS(26),fill=(170,176,186,A),anchor="ma")
    return im.convert("RGB")
if __name__=="__main__":
    import sys
    if len(sys.argv)>1:
        for o in [int(x) for x in sys.argv[1:]]: frame(o).resize((960,540)).save(os.path.join(D,f"comp_{o}.jpg"),quality=85)
    else:
        out=os.path.join(D,"Dipping_Station_Reconstruction.mp4")
        p=subprocess.Popen(["ffmpeg","-y","-loglevel","error","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-",
            "-c:v","libx264","-pix_fmt","yuv420p","-crf","17","-preset","slow","-movflags","+faststart",out],stdin=subprocess.PIPE)
        for o in range(N): p.stdin.write(np.asarray(frame(o)).tobytes())
        p.stdin.close(); p.wait(); print("wrote",out)
