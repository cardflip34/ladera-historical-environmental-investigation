import numpy as np, math, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from geo import P, W, Hh
FPS=30; DUR=10.5; N=int(FPS*DUR)
OUTW,OUTH=1080,1920; TOP=240
FD="/System/Library/Fonts/Supplemental/"
def F(s,b=False):
    return ImageFont.truetype(FD+("Arial Bold.ttf" if b else "Arial.ttf"),s)
photo=Image.open("IMG_4497_1080.jpg").convert("RGB")
A=np.asarray(photo).astype(np.float32)
# ---- period grading (grazed open range, warm light) ----
yy,xx=np.mgrid[0:Hh,0:W]
sky=((A[...,2]>A[...,0]+12)&(A[...,2]>125)&(yy<420)).astype(np.float32)
sky=np.asarray(Image.fromarray((sky*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(6))).astype(np.float32)/255
rng=np.random.default_rng(7)
n1=np.asarray(Image.fromarray((rng.random((Hh//6,W//6))*255).astype(np.uint8)).resize((W,Hh),Image.BICUBIC)).astype(np.float32)/255
n2=np.asarray(Image.fromarray((rng.random((Hh//2,W//2))*255).astype(np.uint8)).resize((W,Hh),Image.BICUBIC)).astype(np.float32)/255
tex=np.stack([178+34*(n1-.5)+26*(n2-.5),156+30*(n1-.5)+22*(n2-.5),104+22*(n1-.5)+16*(n2-.5)],-1)
# distant hills keep some structure; foreground becomes grazed grass
lum=A.mean(-1,keepdims=True)
warm=np.clip(A*0.55+lum*np.array([0.52,0.46,0.36]),0,255)
fg=np.clip((yy-180)/500,0,1)[...,None]
ground=warm*(0.82-0.40*fg)+tex*(0.18+0.40*fg)
skyc=np.clip(A*0.55+np.array([150,165,175])*0.45,0,255)
PERIOD=ground*(1-sky[...,None])+skyc*sky[...,None]
PERIOD=np.clip(PERIOD*0.96+np.array([10,6,0]),0,255)

def ease(t): t=min(max(t,0),1); return t*t*(3-2*t)
def seg(t,a,b): return ease((t-a)/(b-a))
def poly(pts3):
    out=[]
    for X in pts3:
        p=P(*X)
        if p is None: return None
        out.append((float(p[0]),float(p[1])))
    return out

def frame(i):
    t=i/FPS
    s_outline=seg(t,1.5,2.5)
    s_dig=seg(t,2.5,3.7); s_ext=seg(t,3.5,4.6)
    s_tim=seg(t,4.4,6.3)
    s_era=seg(t,6.1,7.2); s_fill=seg(t,6.4,7.6)
    s_card=seg(t,8.9,9.5)
    D=6.5*s_dig; k=max(D/6.5,1e-3); zf=-D
    L=12+14*s_ext
    base=A*(1-s_era)+PERIOD*s_era
    img=Image.fromarray(base.astype(np.uint8)).convert("RGBA")
    # ---------- pit ----------
    xl_b=0.5+0.5*k; xr_b=3.0-0.5*k
    yend=L-0.5
    if s_dig>0:
        pit=Image.new("RGBA",(W,Hh),(0,0,0,0)); d=ImageDraw.Draw(pit)
        yfe=min(14.0,yend)
        faces=[]
        faces.append(((52,50,46),[(xl_b,2,zf),(xr_b,2,zf),(xr_b,yfe,zf),(xl_b,yfe,zf)]))
        if yend>14.2:
            faces.append(((118,114,106),[(xl_b,14,zf),(xr_b,14,zf),(3.0,yend,0),(0.5,yend,0)]))
        else:
            faces.append(((104,100,94),[(0.5,yend,0),(3.0,yend,0),(xr_b,yend,zf),(xl_b,yend,zf)]))
        faces.append(((88,85,80),[(0.5,0.5,0),(3.0,0.5,0),(xr_b,2,zf),(xl_b,2,zf)]))
        prof=[(0.5,0),(2,zf),(min(14,yend),zf)]+([(yend,0)] if yend>14.2 else [(yend,zf)])
        for x_top,x_bot,col in ((0.5,xl_b,(136,131,122)),(3.0,xr_b,(96,93,87))):
            pts=[(x_top,0.5,0),(x_top,yend,0)]+[(x_bot,y,z) for (y,z) in reversed(prof)]
            faces.append((col,pts))
        for col,pts in faces:
            q=poly(pts)
            if q: d.polygon(q,fill=col+(255,))
        # dip solution
        if s_fill>0 and D>1:
            zl=zf+s_fill*(-1.25-zf)
            ys=0.5+1.5*(zl/zf)
            ye=14+(yend-14)*(1-zl/zf) if yend>14.2 else yend
            xl=0.5+(xl_b-0.5)*(zl/zf); xr=3.0+(xr_b-3.0)*(zl/zf)
            q=poly([(xl,ys,zl),(xr,ys,zl),(xr,ye,zl),(xl,ye,zl)])
            if q:
                d.polygon(q,fill=(74,70,46,238))
                for r in range(9):   # ripples
                    yr=ys+(ye-ys)*((r+0.5)/9)+0.35*math.sin(t*3+r)
                    a=poly([(xl+0.15,yr,zl),(xr-0.15,yr,zl)])
                    if a: d.line(a,fill=(120,114,82,110),width=2)
            # cattle swimming through the vat
            for c0 in (6.6,7.5,8.35):
                u=(t-c0)/2.1
                if 0<u<1 and s_fill>0.8:
                    yc=1.2+u*(ye-4.5)
                    zb=zl+0.25
                    body=[(1.75+0.95*math.cos(a2),yc+2.1*math.sin(a2),zb) for a2 in np.linspace(0,2*math.pi,18)]
                    head=[(1.75+0.42*math.cos(a2),yc+2.55+0.55*math.sin(a2),zb+0.45) for a2 in np.linspace(0,2*math.pi,14)]
                    qb=poly(body); qh=poly(head)
                    wake=poly([(1.2,yc-2.4,zl),(1.75,yc-1.6,zl),(2.3,yc-2.4,zl)])
                    if wake: d.line(wake,fill=(150,140,105,160),width=3)
                    if qb: d.polygon(qb,fill=(70,46,30,255))
                    ridge=poly([(1.75,yc-1.9,zb+0.25),(1.75,yc+1.9,zb+0.25)])
                    if ridge: d.line(ridge,fill=(118,86,58,255),width=5)
                    if qh: d.polygon(qh,fill=(58,38,26,255))
                    nose=poly([(1.75+0.22*math.cos(a2),yc+3.05+0.22*math.sin(a2),zb+0.35) for a2 in np.linspace(0,2*math.pi,10)])
                    if nose: d.polygon(nose,fill=(96,72,56,255))
                    for sx in (-1,1):
                        ear=poly([(1.75+sx*0.45,yc+2.35,zb+0.55),(1.75+sx*0.9,yc+2.2,zb+0.6),(1.75+sx*0.5,yc+2.05,zb+0.5)])
                        if ear: d.polygon(ear,fill=(48,31,22,255))
                    for sx in (-1,1):
                        h=poly([(1.75+sx*0.3,yc+2.75,zb+0.7),(1.75+sx*0.75,yc+2.9,zb+1.05)])
                        if h: d.line(h,fill=(225,214,188,255),width=4)
        # mask pit to the vat opening at ground level
        m=Image.new("L",(W,Hh),0); md=ImageDraw.Draw(m)
        q=poly([(0.5,0.5,0),(3.0,0.5,0),(3.0,yend,0),(0.5,yend,0)])
        if q: md.polygon(q,fill=int(255*min(1,s_dig*1.6)))
        m=m.filter(ImageFilter.GaussianBlur(1.2))
        img.paste(pit,(0,0),Image.fromarray((np.asarray(m).astype(np.float32)*np.asarray(pit.split()[3]).astype(np.float32)/255).astype(np.uint8)))
    ov=Image.new("RGBA",(W,Hh),(0,0,0,0)); d=ImageDraw.Draw(ov)
    # reconstructed rim on the extension
    if L>12.05:
        for x0,x1 in ((0,0.5),(3.0,3.5)):
            q=poly([(x0,12,0),(x1,12,0),(x1,L,0),(x0,L,0)])
            if q: d.polygon(q,fill=(178,168,146,245))
    # ---------- timber, iron, drip pen ----------
    items=[]
    def post(x,y,h,delay):
        p=seg(t,4.4+delay,5.2+delay)
        if p<=0: return
        hh=h*p
        items.append((y,(112,84,52,255),[(x-0.17,y,0),(x+0.17,y,0),(x+0.17,y,hh),(x-0.17,y,hh)]))
        items.append((y+0.01,(84,62,38,255),[(x+0.17,y,0),(x+0.17,y+0.3,0),(x+0.17,y+0.3,hh),(x+0.17,y,hh)]))
    def rail(x0,y0,x1,y1,z0,z1,delay,col=(128,98,62,255)):
        p=seg(t,4.9+delay,5.8+delay)
        if p<=0: return
        xe=x0+(x1-x0)*p; ye=y0+(y1-y0)*p
        items.append((max(y0,ye)-0.01,col,[(x0,y0,z0),(xe,ye,z0),(xe,ye,z1),(x0,y0,z1)]))
    if s_tim>0:
        for j,y in enumerate((7,13,19,25)): post(-0.3,y,3.4,0.08*j)
        for j,y in enumerate((1.2,7,13,19,25)): post(3.8,y,3.4,0.08*j+0.04)
        sb=seg(t,4.6,5.6)
        if sb>0:
            items.append((6.4,(122,94,60,235),[(3.55,1.5,0),(3.55,24.5*sb+1.5*(1-sb),0),(3.55,24.5*sb+1.5*(1-sb),1.3),(3.55,1.5,1.3)]))
        rail(-0.3,7,-0.3,25,1.7,2.4,0.0); rail(3.8,1.2,3.8,25,1.7,2.4,0.05)
        rail(-0.3,7,-0.3,25,2.9,3.4,0.15); rail(3.8,1.2,3.8,25,2.9,3.4,0.2)
        # chute fence continuing back from the entry (the surviving iron rails form the other side)
        for j,y in enumerate((-1.2,-2.6)): post(3.8,y,3.6,0.3+0.08*j)
        rail(3.8,1.2,3.8,-3.4,2.0,2.6,0.35); rail(3.8,1.2,3.8,-3.4,3.1,3.6,0.4)
        # drip pen: concrete floor + timber posts/rails + settling barrel
        pf=seg(t,5.0,5.9)
        if pf>0:
            q=poly([(-4.25,25.5,0),(7.75,25.5,0),(7.75,40.5,0),(-4.25,40.5,0)])
            if q: items.insert(0,(99,(172,164,146,int(235*pf)),q) if False else (99,(128,120,104,int(150*pf)),[(-4.25,25.5,0),(7.75,25.5,0),(7.75,40.5,0),(-4.25,40.5,0)]))
        per=[(-4.25,25.5),(-4.25,33),(-4.25,40.5),(1.75,40.5),(7.75,40.5),(7.75,33),(7.75,25.5)]
        for j,(x,y) in enumerate(per): post(x,y,4.0,0.5+0.06*j)
        for (xa,ya),(xb,yb) in zip(per[:-1],per[1:]):
            rail(xa,ya,xb,yb,2.4,2.8,0.7); rail(xa,ya,xb,yb,3.3,3.7,0.75)
        rail(-4.25,25.5,-0.3,25.5,2.4,2.8,0.8); rail(3.8,25.5,7.75,25.5,2.4,2.8,0.8)
        pb=seg(t,5.6,6.3)
        if pb>0:
            items.append((26.0,(92,70,48,255),[(-3.9,26.0,0),(-3.1,26.0,0),(-3.1,26.0,2.6*pb),(-3.9,26.0,2.6*pb)]))
    items.sort(key=lambda it:-it[0])
    for _,col,pts in items:
        q=poly(pts)
        if q: d.polygon(q,fill=col)
    # outline trace of the real concrete
    if 0<s_outline and t<5.0:
        fade=1-seg(t,4.2,5.0)
        rim=[(0,0),(3.5,0),(3.5,12),(0,12),(0,0)]
        pts=[P(x,y,0) for x,y in rim]
        segs=len(pts)-1; prog=s_outline*segs
        for si in range(segs):
            if prog<=si: break
            f=min(1,prog-si); a=pts[si]; b=a+(pts[si+1]-a)*f
            d.line([tuple(a),tuple(b)],fill=(255,176,40,int(255*fade)),width=7)
    img=Image.alpha_composite(img,ov).convert("RGB")
    # ---------- canvas, bands, text ----------
    cv=Image.new("RGB",(OUTW,OUTH),(14,18,26)); cv.paste(img,(0,TOP)); d=ImageDraw.Draw(cv,"RGBA")
    def cap(y,title,sub,alpha):
        if alpha<=0: return
        a=int(255*alpha)
        d.text((54,y),title,font=F(46,True),fill=(236,170,72,a))
        d.text((54,y+62),sub,font=F(34),fill=(214,218,226,a))
    stages=[(0.0,2.5,"LADERA RANCH OPEN SPACE · 2026","The surviving concrete base, about 12 ft long"),
            (2.5,4.4,"THE VAT, TO 1911 SPECIFICATION","6.5 ft deep · 26 ft at the rim · exit incline"),
            (4.4,6.2,"WHAT ROTTED AWAY","Timber chute, splash boards, drip pen with barrel"),
            (6.2,8.9,"c. 1910 · COMPULSORY DIPPING","Every 14 days · 8 lb arsenic trioxide per 500 gal"),
            (8.9,10.5,"INTERPRETIVE RECONSTRUCTION","Not an established identification of this site")]
    for a,b,ti,su in stages:
        al=min(seg(t,a,a+0.35),1-seg(t,b-0.3,b)) if b<10.5 else seg(t,a,a+0.35)
        cap(70,ti,su,al)
    d.text((54,TOP+1440+40),"Surviving concrete and iron rails: photographed 7 Aug 2026.",font=F(30),fill=(170,176,186,255))
    d.text((54,TOP+1440+86),"Reconstructed elements: USDA BAI Circular 183 (1911) dimensions.",font=F(30),fill=(170,176,186,255))
    d.text((54,TOP+1440+132),"LEHRP · depth and extent not yet measured on site",font=F(30),fill=(120,126,136,255))
    if t>=2.5:
        bw=470; d.rounded_rectangle([OUTW-bw-30,TOP+24,OUTW-30,TOP+84],10,fill=(14,18,26,190))
        d.text((OUTW-bw-10,TOP+38),"INTERPRETIVE RECONSTRUCTION",font=F(28,True),fill=(236,170,72,255))
    if s_card>0:
        a=int(230*s_card)
        d.rounded_rectangle([60,TOP+470,OUTW-60,TOP+960],22,fill=(14,18,26,a))
        ta=int(255*s_card)
        d.text((OUTW/2,TOP+530),"What the ranch may have seen",font=F(50,True),fill=(236,170,72,ta),anchor="ma")
        lines=["A concrete swim vat sunk into the range,","timber chute and splash boards above it,","cattle driven through arsenical dip","every two weeks, 1907 to 1912.","","Dimensions follow the 1911 federal plan.","This site's depth and full extent","are unmeasured. Soil untested."]
        for j,l in enumerate(lines):
            d.text((OUTW/2,TOP+610+j*40),l,font=F(33,j<4),fill=(226,229,235,ta),anchor="ma")
    return cv
if __name__=="__main__":
    for tt in [float(x) for x in sys.argv[1:]]:
        frame(int(tt*FPS)).resize((540,960)).save(f"test_{tt:.1f}.jpg",quality=85)
