import numpy as np
W,Hh=1080,1440
IMG=np.array([[205,890],[430,1075],[740,482],[622,382]],float)
GND=np.array([[0,0],[3.5,0],[3.5,12],[0,12]],float)
def homog(src,dst):
    A=[]
    for (x,y),(u,v) in zip(src,dst):
        A.append([-x,-y,-1,0,0,0,u*x,u*y,u]); A.append([0,0,0,-x,-y,-1,v*x,v*y,v])
    _,_,Vt=np.linalg.svd(np.array(A)); h=Vt[-1].reshape(3,3); return h/h[2,2]
Hm=homog(GND,IMG)
NADIR=np.array([560.0,3600.0])   # vertical vanishing point below frame (ultra-wide, tilted down)
VSCALE=0.80                      # vertical px/ft relative to local cross-axis ground scale
def g(x,y):
    p=Hm@np.array([x,y,1.0]); return p[:2]/p[2], p[2]
def P(x,y,z=0.0):
    base,w=g(x,y)
    if w<=0: return None
    a,_=g(x+0.5,y); b,_=g(x-0.5,y)
    s=np.linalg.norm(a-b)*VSCALE          # px per ft here
    u=base-NADIR; u=u/np.linalg.norm(u)   # 'up' points away from nadir
    return base+u*s*z
if __name__=="__main__":
    hz=np.linalg.inv(Hm)  # horizon: image line l = row 3 of H^-1? (points with w=0)
    l=Hm.T@np.array([0,0,1.0]) if False else np.linalg.inv(Hm).T@np.array([0,0,1.0])
    print("ground horizon line (a,b,c):",(np.linalg.inv(Hm)[2]).round(5))
    for lab,X in [("rim far end y=12",(1.75,12,0)),("incline top y=26",(1.75,26,0)),("drip pen far y=38",(1.75,38,0)),
                  ("pen far y=50",(1.75,50,0)),("floor y=6 z=-6.5",(1.75,6,-6.5)),("post top y=2 x=3.5 z=3.5",(3.5,2,3.5)),
                  ("post base same",(3.5,2,0)),("chute y=-3",(1.75,-3,0)),("chute y=-6",(1.75,-6,0))]:
        print(f"{lab:28s}",None if P(*X) is None else P(*X).round(0))
