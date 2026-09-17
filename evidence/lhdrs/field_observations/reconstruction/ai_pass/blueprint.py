import numpy as np, math
from PIL import Image, ImageDraw, ImageFilter
VW,VH=1080,1920
# concrete rim corners measured on the full-screen frame (canvas px): NL, NR, FR, FL
CORN=np.array([[115,1235],[400,1412],[695,690],[632,652]],float)
GND=np.array([[0,0],[3.5,0],[3.5,12],[0,12]],float)
def homog(src,dst):
    A=[]
    for (x,y),(u,v) in zip(src,dst):
        A.append([-x,-y,-1,0,0,0,u*x,u*y,u]); A.append([0,0,0,-x,-y,-1,v*x,v*y,v])
    _,_,Vt=np.linalg.svd(np.array(A)); h=Vt[-1].reshape(3,3); return h/h[2,2]
Hm=homog(GND,CORN)
NADIR=np.array([560.0,5600.0]); VSCALE=0.85
def g(x,y):
    p=Hm@np.array([x,y,1.0]); return p[:2]/p[2], p[2]
def P(x,y,z=0.0):
    base,w=g(x,y)
    if w<=0.02: return None
    a,_=g(x+0.5,y); b,_=g(x-0.5,y); s=np.linalg.norm(a-b)*VSCALE
    u=base-NADIR; u=u/np.linalg.norm(u)
    return (float(base[0]+u[0]*s*z), float(base[1]+u[1]*s*z))
AMB=(255,190,70); CYN=(150,220,255); WHT=(240,244,250)
def ss(a,b,x):
    t=min(max((x-a)/(b-a),0),1); return t*t*(3-2*t)
def glow(d,pts,col,fade,w=4,prog=1.0,closed=False):
    pts=[p for p in pts if p is not None]
    if len(pts)<2: return
    if closed: pts=pts+[pts[0]]
    if prog<1:
        L=[math.hypot(pts[i+1][0]-pts[i][0],pts[i+1][1]-pts[i][1]) for i in range(len(pts)-1)]
        tot=sum(L); tgt=prog*tot; out=[pts[0]]; acc=0
        for i in range(len(pts)-1):
            if acc+L[i]>=tgt:
                f=(tgt-acc)/max(L[i],1e-6); out.append((pts[i][0]+(pts[i+1][0]-pts[i][0])*f,pts[i][1]+(pts[i+1][1]-pts[i][1])*f)); break
            out.append(pts[i+1]); acc+=L[i]
        pts=out
    if len(pts)<2: return
    for ww,al in ((w*4,28),(w*2,80),(w,240)):
        d.line(pts,fill=col+(int(al*fade),),width=ww,joint="curve")
def seg3(p0,p1,n=12):
    return [P(p0[0]+(p1[0]-p0[0])*i/n,p0[1]+(p1[1]-p0[1])*i/n,p0[2]+(p1[2]-p0[2])*i/n) for i in range(n+1)]
def label(d,anchor,text,sub,col,fade,dx=40,dy=-60,font=None,fonts=None):
    if anchor is None or fade<=0: return
    A=int(255*fade); ax,ay=anchor; lx,ly=ax+dx,ay+dy
    lx=min(max(lx,40),VW-420); ly=min(max(ly,100),VH-160)
    d.line([(ax,ay),(lx,ly+40)],fill=col+(int(180*fade),),width=2)
    d.ellipse([ax-5,ay-5,ax+5,ay+5],fill=col+(A,))
    d.rounded_rectangle([lx-12,ly-6,lx+400,ly+(72 if sub else 40)],8,fill=(8,10,14,int(170*fade)))
    d.text((lx,ly),text,font=fonts[0],fill=col+(A,))
    if sub: d.text((lx,ly+34),sub,font=fonts[1],fill=WHT+(A,))
def draw_blueprint(ov,u,vis,fonts):
    """u: seconds into the segment; vis: overall fade. fonts=(bold24, reg20, title48, reg30)"""
    u=u/1.25
    d=ImageDraw.Draw(ov)
    fb,fr,ft,fs=fonts
    # 0. perspective ground grid
    ga=ss(0.1,0.9,u)*vis
    if ga>0:
        gcol=CYN+(int(26*ga),)
        for gx in range(-12,20,4):
            pts=[q for q in (P(gx,gy,0) for gy in np.linspace(-4,36,20)) if q is not None]
            if len(pts)>1: d.line(pts,fill=gcol,width=1)
        for gy in range(-4,38,4):
            pts=[q for q in (P(gx,gy,0) for gx in np.linspace(-12,20,16)) if q is not None]
            if len(pts)>1: d.line(pts,fill=gcol,width=1)
    # 1. observed floor (amber, always on)
    floor=[P(0,0,0),P(3.5,0,0),P(3.5,12,0),P(0,12,0)]
    glow(d,floor,AMB,vis,w=5,closed=True)
    # 2. vat walls taper up to the 26-ft rim, 6.5 ft up
    pw=ss(0.5,1.7,u)*vis
    RIM=[(-0.25,-7,6.5),(3.75,-7,6.5),(3.75,19,6.5),(-0.25,19,6.5)]
    FLR=[(0,0,0),(3.5,0,0),(3.5,12,0),(0,12,0)]
    if pw>0:
        fa=int(38*ss(0.8,1.6,u)*vis)
        for i in range(4):
            a,b=FLR[i],FLR[(i+1)%4]; c,e=RIM[(i+1)%4],RIM[i]
            face=[P(*a),P(*b),P(*c),P(*e)]
            if all(q is not None for q in face): d.polygon(face,fill=(120,190,240,fa))
        for a,b in zip(FLR,RIM): glow(d,seg3(a,b),CYN,vis,w=4,prog=ss(0.5,1.2,u))
        rimpts=seg3(RIM[0],RIM[1])+seg3(RIM[1],RIM[2])+seg3(RIM[2],RIM[3])+seg3(RIM[3],RIM[0])
        glow(d,rimpts,CYN,vis,w=6,prog=ss(1.0,1.9,u))
        # dip solution level plane at 5 ft 3 in (semi-transparent)
        dp=ss(1.6,2.3,u)*vis
        if dp>0:
            f=5.25/6.5
            quad=[P(-0.25*f,-7*f,5.25),P(3.5+0.25*f,-7*f,5.25),P(3.5+0.25*f,12+7*f,5.25),P(-0.25*f,12+7*f,5.25)]
            if all(q is not None for q in quad): d.polygon(quad,fill=(60,110,140,int(70*dp)))
        # splash boards along the rim
        sb=ss(1.9,2.6,u)*vis
        if sb>0:
            for xs in (-0.25,3.75):
                top=seg3((xs,-7,8.6),(xs,19,8.6)); glow(d,top,CYN,sb*0.8,w=2)
                for yy in range(-7,20,4): glow(d,seg3((xs,yy,6.5),(xs,yy,8.6),2),CYN,sb*0.8,w=2)
    # 3. chute toward the camera (only the stretch in front of the lens)
    ch=ss(2.4,3.2,u)*vis
    if ch>0:
        for xs in (0.5,3.0):
            glow(d,seg3((xs,-7,6.5),(xs,-11,6.5)),CYN,ch,w=3,prog=ch)
            glow(d,seg3((xs,-7,11.5),(xs,-11,11.5)),CYN,ch,w=3,prog=ch)
            for yy in (-7,-9,-11): glow(d,seg3((xs,yy,6.5),(xs,yy,11.5),2),CYN,ch,w=2)
    # 4. dripping pen beyond the exit incline
    dpn=ss(3.1,4.2,u)*vis
    if dpn>0:
        PEN=[(-4.25,19.5,6.5),(7.75,19.5,6.5),(7.75,34.5,6.5),(-4.25,34.5,6.5)]
        penpts=seg3(PEN[0],PEN[1])+seg3(PEN[1],PEN[2])+seg3(PEN[2],PEN[3])+seg3(PEN[3],PEN[0])
        glow(d,penpts,CYN,vis,w=3,prog=dpn)
        for c in PEN: glow(d,seg3(c,(c[0],c[1],10.5),2),CYN,dpn*0.8,w=2)
        top=[(c[0],c[1],10.5) for c in PEN]
        glow(d,seg3(top[0],top[1])+seg3(top[1],top[2])+seg3(top[2],top[3])+seg3(top[3],top[0]),CYN,dpn*0.7,w=2)
        # barrel at the pen corner
        bc=(7.75+1.0,20.5)
        for zz in (5.0,6.5):
            ring=[P(bc[0]+0.9*math.cos(a),bc[1]+0.9*math.sin(a),zz) for a in np.linspace(0,2*math.pi,14)]
            glow(d,ring,CYN,dpn*0.8,w=2)
    # labels
    label(d,P(1.75,6,0),"OBSERVED · 12 ft concrete floor","the rectangle in this photo",AMB,ss(0.2,0.6,u)*vis,dx=-450,dy=-90,fonts=(fb,fr))
    label(d,P(3.75,4,6.5),"VAT · 26 ft at the rim · 6.5 ft deep","interpreted · USDA Circular 183 (1911)",CYN,ss(1.5,2.0,u)*vis,dx=60,dy=-120,fonts=(fb,fr))
    label(d,P(3.0,-8,9.0),"CHUTE · 30 in × 20 ft","the surviving pipe rails run along it",CYN,ss(3.0,3.4,u)*vis,dx=-380,dy=40,fonts=(fb,fr))
    label(d,P(1.75,27,10.5),"DRIPPING PEN · 12 × 15 ft","concrete floor · barrel sunk at the corner",CYN,ss(4.0,4.4,u)*vis,dx=-160,dy=-150,fonts=(fb,fr))
    return d
