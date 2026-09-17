import bpy, bmesh, math, random, sys, os
from mathutils import Vector, Matrix, Euler, noise
OUT=os.environ.get("VAT_OUT","/tmp/vatframes/")
TEST=os.environ.get("VAT_TEST","")
random.seed(11)
FT=0.3048
def ss(e0,e1,x):
    t=min(max((x-e0)/(e1-e0),0.0),1.0); return t*t*(3-2*t)

# ---------------------------------------------------------------- reset
bpy.ops.wm.read_factory_settings(use_empty=True)
sc=bpy.context.scene
sc.render.engine='BLENDER_EEVEE_NEXT'
sc.render.resolution_x=1920; sc.render.resolution_y=1080
sc.render.resolution_percentage=100
sc.render.fps=24
sc.frame_start=0; sc.frame_end=383
sc.eevee.taa_render_samples=28
sc.view_settings.view_transform='AgX'
try: sc.view_settings.look='AgX - Medium High Contrast'
except Exception: pass
sc.render.image_settings.file_format='PNG'
sc.view_settings.exposure=-0.9
sc.render.filepath=OUT
try:
    sc.eevee.volumetric_end=3000.0
    sc.eevee.volumetric_tile_size='8'
except Exception: pass

# ---------------------------------------------------------------- materials
def mat(name,col,rough=0.8,metal=0.0,noise_amt=0.0,noise_scale=4.0,bump=0.0,col2=None):
    m=bpy.data.materials.new(name); m.use_nodes=True
    nt=m.node_tree; b=nt.nodes["Principled BSDF"]
    b.inputs["Roughness"].default_value=rough
    b.inputs["Metallic"].default_value=metal
    if noise_amt>0 or bump>0:
        tc=nt.nodes.new("ShaderNodeTexCoord")
        nz=nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value=noise_scale; nz.inputs["Detail"].default_value=8
        nt.links.new(tc.outputs["Object"],nz.inputs["Vector"])
        if noise_amt>0:
            mix=nt.nodes.new("ShaderNodeMix"); mix.data_type='RGBA'
            c2=col2 if col2 else tuple(max(0,c*(1-noise_amt)) for c in col)
            mix.inputs[6].default_value=(*col,1); mix.inputs[7].default_value=(*c2,1)
            nt.links.new(nz.outputs["Fac"],mix.inputs[0])
            nt.links.new(mix.outputs[2],b.inputs["Base Color"])
        else:
            b.inputs["Base Color"].default_value=(*col,1)
        if bump>0:
            bp=nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value=bump
            nt.links.new(nz.outputs["Fac"],bp.inputs["Height"]); nt.links.new(bp.outputs["Normal"],b.inputs["Normal"])
    else:
        b.inputs["Base Color"].default_value=(*col,1)
    return m
M={}
M['timber']=mat('timber',(0.30,0.21,0.13),0.85,noise_amt=0.35,noise_scale=9,bump=0.25,col2=(0.20,0.15,0.10))
M['timber_old']=mat('timber_old',(0.33,0.30,0.25),0.9,noise_amt=0.3,noise_scale=9,bump=0.25)
M['concrete']=mat('concrete',(0.36,0.345,0.31),0.92,noise_amt=0.18,noise_scale=6,bump=0.15)
M['iron']=mat('iron',(0.05,0.05,0.055),0.5,metal=0.8)
M['rust']=mat('rust',(0.22,0.10,0.05),0.8,metal=0.3,noise_amt=0.4,noise_scale=12)
M['dip']=mat('dip',(0.13,0.13,0.07),0.03,noise_amt=0.3,noise_scale=3,bump=0.05)
M['foliage']=mat('foliage',(0.09,0.13,0.05),0.9,noise_amt=0.4,noise_scale=3,bump=0.6)
M['syc']=mat('syc',(0.20,0.26,0.09),0.9,noise_amt=0.35,noise_scale=3,bump=0.6)
M['bark']=mat('bark',(0.16,0.12,0.09),0.9)
M['sycbark']=mat('sycbark',(0.62,0.60,0.54),0.8,noise_amt=0.4,noise_scale=5)
M['tuft']=mat('tuft',(0.42,0.31,0.13),0.9,noise_amt=0.3,noise_scale=2,col2=(0.30,0.22,0.09))
M['herf']=mat('herf',(0.23,0.075,0.025),0.75,noise_amt=0.2,noise_scale=6)
M['white']=mat('white',(0.72,0.69,0.62),0.8)
M['black']=mat('black',(0.025,0.022,0.02),0.7)
M['dun']=mat('dun',(0.34,0.22,0.11),0.8,noise_amt=0.25,noise_scale=6)
M['roan']=mat('roan',(0.22,0.12,0.08),0.8,noise_amt=0.35,noise_scale=40,col2=(0.32,0.26,0.22))
M['horn']=mat('horn',(0.72,0.66,0.52),0.5)
M['skin']=mat('skin',(0.42,0.27,0.18),0.7)
M['denim']=mat('denim',(0.10,0.12,0.18),0.9)
M['shirt']=mat('shirt',(0.55,0.50,0.40),0.9)
M['hat']=mat('hat',(0.30,0.24,0.16),0.9)
M['bay']=mat('bay',(0.20,0.09,0.035),0.7)
M['roof']=mat('roof',(0.26,0.24,0.22),0.9,noise_amt=0.3,noise_scale=14)
M['stone']=mat('stone',(0.40,0.38,0.34),0.95,noise_amt=0.4,noise_scale=8,bump=0.6)
M['keg']=mat('keg',(0.40,0.30,0.18),0.8,noise_amt=0.2,noise_scale=10)
M['paint']=mat('paint',(0.45,0.43,0.40),0.7)

# ground with dirt mask around pens/station
def ground_mat():
    m=bpy.data.materials.new('ground'); m.use_nodes=True; nt=m.node_tree; b=nt.nodes["Principled BSDF"]
    b.inputs["Roughness"].default_value=0.95
    tc=nt.nodes.new("ShaderNodeTexCoord")
    nz=nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value=0.05; nz.inputs["Detail"].default_value=10
    nz2=nt.nodes.new("ShaderNodeTexNoise"); nz2.inputs["Scale"].default_value=0.9; nz2.inputs["Detail"].default_value=12
    nt.links.new(tc.outputs["Object"],nz.inputs["Vector"]); nt.links.new(tc.outputs["Object"],nz2.inputs["Vector"])
    ramp=nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position=0.30; ramp.color_ramp.elements[0].color=(0.24,0.17,0.07,1)
    ramp.color_ramp.elements[1].position=0.70; ramp.color_ramp.elements[1].color=(0.46,0.34,0.14,1)
    e=ramp.color_ramp.elements.new(0.5); e.color=(0.20,0.20,0.08,1)
    nt.links.new(nz.outputs["Fac"],ramp.inputs[0])
    # dirt mask
    sep=nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(tc.outputs["Object"],sep.inputs[0])
    def absoff(inp,off):
        a=nt.nodes.new("ShaderNodeMath"); a.operation='ADD'; a.inputs[1].default_value=off; nt.links.new(inp,a.inputs[0])
        b2=nt.nodes.new("ShaderNodeMath"); b2.operation='ABSOLUTE'; nt.links.new(a.outputs[0],b2.inputs[0]); return b2.outputs[0]
    def mr(inp,a,bb):
        n=nt.nodes.new("ShaderNodeMapRange"); n.interpolation_type='SMOOTHSTEP'
        n.inputs["From Min"].default_value=a; n.inputs["From Max"].default_value=bb
        n.inputs["To Min"].default_value=1; n.inputs["To Max"].default_value=0
        nt.links.new(inp,n.inputs["Value"]); return n.outputs["Result"]
    mx=mr(absoff(sep.outputs[0],12.0),30,40); my=mr(absoff(sep.outputs[1],0.0),18,26)
    mul=nt.nodes.new("ShaderNodeMath"); mul.operation='MULTIPLY'; nt.links.new(mx,mul.inputs[0]); nt.links.new(my,mul.inputs[1])
    mul2=nt.nodes.new("ShaderNodeMath"); mul2.operation='MULTIPLY'; nt.links.new(mul.outputs[0],mul2.inputs[0]); nt.links.new(nz2.outputs["Fac"],mul2.inputs[1])
    mul3=nt.nodes.new("ShaderNodeMath"); mul3.operation='MULTIPLY'; mul3.inputs[1].default_value=1.8; mul3.use_clamp=True
    nt.links.new(mul2.outputs[0],mul3.inputs[0])
    mix=nt.nodes.new("ShaderNodeMix"); mix.data_type='RGBA'
    nt.links.new(mul3.outputs[0],mix.inputs[0]); nt.links.new(ramp.outputs[0],mix.inputs[6])
    mix.inputs[7].default_value=(0.20,0.15,0.10,1)
    nt.links.new(mix.outputs[2],b.inputs["Base Color"])
    bp=nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value=0.5
    nt.links.new(nz2.outputs["Fac"],bp.inputs["Height"]); nt.links.new(bp.outputs["Normal"],b.inputs["Normal"])
    return m
M['ground']=ground_mat()

# ---------------------------------------------------------------- mesh builder
class MB:
    def __init__(s,mats): s.bm=bmesh.new(); s.mats=mats
    def _tag(s,before,k):
        s.bm.faces.ensure_lookup_table()
        for f in s.bm.faces[before:]: f.material_index=k
    def box(s,c,size,rot=(0,0,0),k=0):
        b=len(s.bm.faces)
        m=Matrix.Translation(Vector(c))@Euler(rot).to_matrix().to_4x4()@Matrix.Diagonal((size[0],size[1],size[2],1))
        bmesh.ops.create_cube(s.bm,size=1.0,matrix=m); s._tag(b,k)
    def beam(s,p0,p1,w,h,k=0,roll=0.0):
        p0=Vector(p0); p1=Vector(p1); d=p1-p0; L=d.length
        if L<1e-6: return
        yaw=math.atan2(d.y,d.x); pitch=-math.atan2(d.z,math.hypot(d.x,d.y))
        b=len(s.bm.faces)
        m=Matrix.Translation((p0+p1)/2)@Euler((roll,pitch,yaw),'XYZ').to_matrix().to_4x4()
        m=Matrix.Translation((p0+p1)/2)@(Matrix.Rotation(yaw,4,'Z')@Matrix.Rotation(pitch,4,'Y')@Matrix.Rotation(roll,4,'X'))@Matrix.Diagonal((L,w,h,1))
        bmesh.ops.create_cube(s.bm,size=1.0,matrix=m); s._tag(b,k)
    def cyl(s,p0,p1,r,k=0,seg=10,r2=None):
        p0=Vector(p0); p1=Vector(p1); d=p1-p0; L=d.length
        if L<1e-6: return
        q=Vector((0,0,1)).rotation_difference(d.normalized())
        m=Matrix.Translation((p0+p1)/2)@q.to_matrix().to_4x4()
        b=len(s.bm.faces)
        bmesh.ops.create_cone(s.bm,cap_ends=True,cap_tris=False,segments=seg,radius1=r,radius2=(r if r2 is None else r2),depth=L,matrix=m)
        s._tag(b,k)
    def sphere(s,c,sc3,k=0,u=14,v=9,rot=(0,0,0)):
        b=len(s.bm.faces)
        m=Matrix.Translation(Vector(c))@Euler(rot).to_matrix().to_4x4()@Matrix.Diagonal((sc3[0],sc3[1],sc3[2],1))
        bmesh.ops.create_uvsphere(s.bm,u_segments=u,v_segments=v,radius=1.0,matrix=m); s._tag(b,k)
    def poly(s,verts,k=0):
        vs=[s.bm.verts.new(Vector(v)) for v in verts]
        b=len(s.bm.faces)
        try: s.bm.faces.new(vs)
        except ValueError: return
        s._tag(b,k)
    def obj(s,name,smooth=False,collection=None):
        me=bpy.data.meshes.new(name); s.bm.to_mesh(me); s.bm.free()
        for mm in s.mats: me.materials.append(M[mm])
        if smooth:
            for p in me.polygons: p.use_smooth=True
        o=bpy.data.objects.new(name,me); (collection or sc.collection).objects.link(o); return o

# ---------------------------------------------------------------- terrain
def H(x,y):
    r=math.hypot(x+8,y)
    w=ss(45,140,r)
    hills=38*noise.fractal(Vector((x/240,y/240,0.37)),1.0,2.0,5)+9*noise.fractal(Vector((x/70,y/70,1.7)),1.0,2.0,3)
    ridge=210*ss(300,900,y+0.25*x)*(0.65+0.35*noise.fractal(Vector((x/350,y/350,4.1)),1.0,2.0,4))
    ridge+=45*ss(250,700,-x+0.2*y)*(0.6+0.4*noise.fractal(Vector((x/200,y/200,7.1)),1.0,2.0,4))
    cy=-70+14*math.sin(x/55)
    creek=-4.0*math.exp(-((y-cy)/10)**2)
    return w*(hills+14)+ridge+creek*ss(30,60,abs(y))+0.0
def terrain():
    N=340; S=1900.0; cx,cy=150.0,300.0
    bm=bmesh.new(); grid={}
    for i in range(N+1):
        for j in range(N+1):
            x=cx-S/2+S*i/N; y=cy-S/2+S*j/N
            z=H(x,y)
            if -18<=x<=24 and -12<=y<=12: z=min(z,-0.04)
            grid[i,j]=bm.verts.new((x,y,z))
    for i in range(N):
        for j in range(N):
            xa=cx-S/2+S*(i+0.5)/N; ya=cy-S/2+S*(j+0.5)/N
            if -14<xa<20 and -8<ya<8: continue
            bm.faces.new((grid[i,j],grid[i+1,j],grid[i+1,j+1],grid[i,j+1]))
    me=bpy.data.meshes.new('terrain'); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth=True
    me.materials.append(M['ground'])
    o=bpy.data.objects.new('terrain',me); sc.collection.objects.link(o)
terrain()
# fine local pad around station (flat, 0.5 m grid), hole for the vat
def pad():
    bm=bmesh.new(); X0,X1,Y0,Y1=-20.0,26.0,-14.0,14.0; st=0.5
    nx=int((X1-X0)/st); ny=int((Y1-Y0)/st); g={}
    for i in range(nx+1):
        for j in range(ny+1):
            x=X0+i*st; y=Y0+j*st
            e=min(x-X0,X1-x,y-Y0,Y1-y)
            z=-0.04*ss(0,3,3-e)   # meet terrain at edges
            g[i,j]=bm.verts.new((x,y,z))
    for i in range(nx):
        for j in range(ny):
            xa=X0+(i+0.5)*st; ya=Y0+(j+0.5)*st
            if -0.55<xa<8.45 and -0.95<ya<0.95: continue
            bm.faces.new((g[i,j],g[i+1,j],g[i+1,j+1],g[i,j+1]))
    me=bpy.data.meshes.new('pad'); bm.to_mesh(me); bm.free(); me.materials.append(M['ground'])
    o=bpy.data.objects.new('pad',me); sc.collection.objects.link(o)
pad()

# ---------------------------------------------------------------- the vat (Circular 183 dims)
TOPL=26*FT; FLOORL=12*FT; DEP=6.5*FT; TW=3*FT; BW=1.5*FT
ENTRY=4*FT        # steep slide run
X_FS=ENTRY; X_FE=ENTRY+FLOORL   # floor start/end
def vat():
    mb=MB(['concrete','iron','timber'])
    # cavity walls built as explicit quads (inside faces) + coping + outer walls
    zt=0.10; zb=-DEP
    T=[(0,-TW/2,zt),(TOPL,-TW/2,zt),(TOPL,TW/2,zt),(0,TW/2,zt)]
    B=[(X_FS,-BW/2,zb),(X_FE,-BW/2,zb),(X_FE,BW/2,zb),(X_FS,BW/2,zb)]
    mb.poly([B[0],B[3],B[2],B[1]],0)                  # floor
    mb.poly([T[0],B[0],B[1],T[1]],0)                  # side -y
    mb.poly([T[2],B[2],B[3],T[3]],0)                  # side +y
    mb.poly([T[3],B[3],B[0],T[0]],1)                  # entry slide (iron plate)
    mb.poly([T[1],B[1],B[2],T[2]],0)                  # exit incline
    # coping rim
    cw=0.22
    mb.box((TOPL/2,-TW/2-cw/2,zt-0.12),(TOPL+2*cw,cw,0.24),k=0)
    mb.box((TOPL/2, TW/2+cw/2,zt-0.12),(TOPL+2*cw,cw,0.24),k=0)
    mb.box((-cw/2,0,zt-0.12),(cw,TW,0.24),k=0)
    mb.box((TOPL+cw/2,0,zt-0.12),(cw,TW,0.24),k=0)
    # cleats on exit incline
    for i in range(1,10):
        f=i/10.0
        x=X_FE+(TOPL-X_FE)*f; z=zb+(zt-zb)*f; w=BW+(TW-BW)*f
        mb.box((x,0,z+0.03),(0.05,w*0.92,0.06),k=2)
    o=mb.obj('vat')
    # dip solution surface at 5'3" fill
    fz=zb+5.25*FT; f=5.25/6.5
    xs=X_FS*(1-f); xe=X_FE+(TOPL-X_FE)*f; w=BW+(TW-BW)*f
    lq=MB(['dip']); lq.poly([(xs,-w/2,fz),(xe,-w/2,fz),(xe,w/2,fz),(xs,w/2,fz)],0); lq.obj('dip')
    return fz
FZ=vat()

# ---------------------------------------------------------------- timber & iron structures
T=MB(['timber','iron','timber_old','concrete','keg','stone','roof','paint','rust'])
def fence(p0,p1,h=1.55,spacing=2.4,rails=(0.35,0.75,1.15,1.5),post=0.16,board=0.19,thick=0.035,k=0):
    p0=Vector((p0[0],p0[1],0)); p1=Vector((p1[0],p1[1],0)); d=p1-p0; L=d.length; n=max(1,int(round(L/spacing)))
    side=Vector((-d.y,d.x,0)).normalized()
    for i in range(n+1):
        p=p0+d*(i/n); T.box((p.x,p.y,(h+0.15)/2-0.1),(post,post,h+0.15),rot=(0,0,math.atan2(d.y,d.x)),k=k)
    for rz in rails:
        a=p0+side*(post/2+thick/2); b=p1+side*(post/2+thick/2)
        T.beam((a.x,a.y,rz),(b.x,b.y,rz),thick,board,k=k)
def solidwall(p0,p1,h=1.6,k=0):
    fence(p0,p1,h=h,spacing=1.8,rails=[0.12+0.205*i for i in range(8)],k=k)
def pipefence(p0,p1,h=1.0,spacing=2.4):
    p0=Vector((p0[0],p0[1],0)); p1=Vector((p1[0],p1[1],0)); d=p1-p0; n=max(1,int(round(d.length/spacing)))
    for i in range(n+1):
        p=p0+d*(i/n); T.cyl((p.x,p.y,-0.3),(p.x,p.y,h),0.045,k=1,seg=10)
    for rz in (0.55,h-0.05):
        T.cyl((p0.x,p0.y,rz),(p1.x,p1.y,rz),0.032,k=1,seg=10)

CH=30*0.0254     # chute inside width
CHL=20*FT
# chute (solid timber walls)
solidwall((-CHL,-CH/2-0.1),(0.0,-CH/2-0.1))
solidwall((-CHL, CH/2+0.1),(0.0, CH/2+0.1))
# iron pipe rails leading up to the concrete (as photographed today)
pipefence((-CHL-9.0,1.35),(0.35,1.35))
pipefence((-CHL-9.0,-1.35),(-CHL,-1.35))
# splash boards along the vat (hinged cover leaves, raised)
for sgn in (-1,1):
    y=sgn*(TW/2+0.26)
    for i in range(6):
        x=0.3+i*1.28
        T.box((x+0.6,y,0.62),(1.2,0.04,0.76),k=0)
        T.box((x,y,0.5),(0.12,0.12,1.0),k=0)
    T.box((TOPL-0.2,y,0.5),(0.12,0.12,1.0),k=0)
# crowding funnel
fence((-CHL,-0.6),(-CHL-9.0,-7.0)); fence((-CHL,0.6),(-CHL-9.0,7.0))
# receiving & retaining pens (two big corrals + alley)
PX0,PX1=-50.0,-CHL-9.0
fence((PX0,-20),(PX1,-20)); fence((PX0,20),(PX1,20)); fence((PX0,-20),(PX0,20))
fence((PX1,-20),(PX1,-7.0)); fence((PX1,7.0),(PX1,20))
fence((PX0+8,-2.5),(PX1,-2.5)); fence((PX0+8,2.5),(PX1,2.5))    # central alley
fence(((PX0+PX1)/2,-20),((PX0+PX1)/2,-2.5)); fence(((PX0+PX1)/2,2.5),((PX0+PX1)/2,20))
# dripping pen: 12 x 15 ft concrete floor, pitched to a corner, barrel sunk in ground
DX0=TOPL+0.25; DX1=DX0+15*FT; DY=12*FT/2
T.box(((DX0+DX1)/2,0,0.06),(DX1-DX0,2*DY,0.12),rot=(0.012,-0.012,0),k=3)
for yy in (-DY,DY): T.box(((DX0+DX1)/2,yy,0.16),(DX1-DX0,0.14,0.2),k=3)
T.box((DX1,0,0.16),(0.14,2*DY,0.2),k=3)
fence((DX0,-DY),(DX1,-DY),h=1.6,spacing=1.5,rails=(0.45,0.9,1.35))
fence((DX0,DY),(DX1,DY),h=1.6,spacing=1.5,rails=(0.45,0.9,1.35))
fence((DX1,-DY),(DX1,-0.9),h=1.6,spacing=1.2,rails=(0.45,0.9,1.35))
fence((DX1,0.9),(DX1,DY),h=1.6,spacing=1.2,rails=(0.45,0.9,1.35))
T.cyl((DX1-0.3,-DY-1.0,-0.6),(DX1-0.3,-DY-1.0,0.1),0.32,k=4,seg=16)
T.cyl((DX1-0.3,-DY-0.1,0.04),(DX1-0.3,-DY-0.75,0.04),0.05,k=1)
# release lot opening to the range
fence((DX1,-DY),(DX1+22,-14)); fence((DX1,DY),(DX1+22,14))
# mixing works: open shed, stone firebox + iron kettle, arsenic kegs, water barrels
SX,SY=5.0,9.5
for (x,y) in ((SX-2.5,SY-2),(SX+2.5,SY-2),(SX-2.5,SY+2),(SX+2.5,SY+2)):
    T.box((x,y,1.3),(0.18,0.18,2.6),k=0)
for yy in (SY-2,):
    for i in range(10): T.box((SX-2.4+i*0.53,yy,1.25),(0.5,0.03,2.5),k=2)
for xx in (SX-2.5,SX+2.5):
    for i in range(8): T.box((xx,SY-1.75+i*0.5,1.25),(0.03,0.48,2.5),k=2)
T.box((SX,SY-0.9,2.95),(5.6,2.6,0.06),rot=(0.32,0,0),k=6)
T.box((SX,SY+1.1,2.95),(5.6,2.4,0.06),rot=(-0.32,0,0),k=6)
T.box((SX-0.8,SY+0.4,0.35),(1.3,1.3,0.7),k=5)
T.sphere((SX-0.8,SY+0.4,0.9),(0.55,0.55,0.42),k=1)
for i in range(6):
    T.cyl((SX+0.8+(i%3)*0.55,SY-0.6+(i//3)*0.6,0.0),(SX+0.8+(i%3)*0.55,SY-0.6+(i//3)*0.6,0.75),0.26,k=4,seg=14)
for i in range(7): T.box((SX-2.0,SY+2.6+i*0.0,0.2+i*0.17),(1.8,0.9,0.15),rot=(0,0,0.05*i),k=0)
# windmill + elevated tank + supply pipe to vat
WX,WY=-6.0,-12.0
for (dx,dy) in ((-1.4,-1.4),(1.4,-1.4),(1.4,1.4),(-1.4,1.4)):
    T.beam((WX+dx,WY+dy,0),(WX+dx*0.25,WY+dy*0.25,11.5),0.12,0.12,k=2)
for zz in (3,6,9):
    s=1.4*(1-zz/11.5*0.75)
    for a,b in (((-s,-s),(s,-s)),((s,-s),(s,s)),((s,s),(-s,s)),((-s,s),(-s,-s))):
        T.beam((WX+a[0],WY+a[1],zz),(WX+b[0],WY+b[1],zz),0.07,0.07,k=2)
TX,TY=-10.5,-12.5
for (dx,dy) in ((-1.2,-1.2),(1.2,-1.2),(1.2,1.2),(-1.2,1.2)):
    T.box((TX+dx,TY+dy,2.0),(0.22,0.22,4.0),k=0)
T.box((TX,TY,4.05),(3.0,3.0,0.15),k=0)
T.cyl((TX,TY,4.1),(TX,TY,6.4),1.65,k=0,seg=28)
T.cyl((TX,TY,6.4),(TX,TY,6.9),1.7,k=2,seg=28,r2=0.3)
T.cyl((TX+1.5,TY,0.08),(0.2,-1.2,0.08),0.05,k=1)
T.cyl((0.2,-1.2,0.08),(1.0,-0.62,0.08),0.05,k=1)
T.obj('station_timber')
# windmill wheel (animated)
wheel=MB(['paint','iron'])
for i in range(18):
    a=i/18*2*math.pi
    wheel.beam((0,0,0),(0,1.8*math.cos(a),1.8*math.sin(a)),0.02,0.28,k=0,roll=a)
wheel.cyl((-0.1,0,0),(0.3,0,0),0.15,k=1)
wheel.box((-1.4,0,0),(2.2,0.03,0.9),k=0)
wh=wheel.obj('wheel'); wh.location=(WX,WY-0.1,11.8); wh.rotation_euler=(0,0,math.radians(-60))
wh.keyframe_insert('rotation_euler',frame=0)
# spin: separate child empty
spin=bpy.data.objects.new('spin',None); sc.collection.objects.link(spin)
spin.location=(WX,WY-0.1,11.8); spin.rotation_euler=(0,0,math.radians(-60))
wh.location=(0,0,0); wh.rotation_euler=(0,0,0); wh.parent=spin
wh.animation_data_clear()
wh.rotation_euler=(0,0,0); wh.keyframe_insert('rotation_euler',frame=0)
wh.rotation_euler=(40.0,0,0); wh.keyframe_insert('rotation_euler',frame=383)
for fc in wh.animation_data.action.fcurves:
    for kp in fc.keyframe_points: kp.interpolation='LINEAR'

# ---------------------------------------------------------------- cattle
def cow_mesh(name,body,face,horn=True):
    c=MB([body,face,'horn','black'])
    c.sphere((0,0,0.99),(1.02,0.37,0.44),k=0,u=28,v=16)
    c.sphere((0.42,0,1.05),(0.52,0.355,0.43),k=0,u=24,v=14)
    c.sphere((-0.58,0,1.01),(0.46,0.34,0.41),k=0,u=24,v=14)
    c.sphere((0.55,0,0.78),(0.35,0.12,0.2),k=0,u=16,v=10)
    c.cyl((0.75,0,1.08),(1.05,0,1.2),0.24,k=0,r2=0.18)
    c.sphere((1.2,0,1.12),(0.26,0.15,0.17),rot=(0,0.5,0),k=1)
    c.sphere((1.36,0,1.0),(0.13,0.11,0.1),k=3 if face=='white' else 1)
    for sy in (-1,1):
        c.cyl((1.08,sy*0.12,1.26),(1.05,sy*0.42,1.38),0.035,k=2,r2=0.008)
        c.sphere((1.02,sy*0.2,1.2),(0.09,0.05,0.04),k=0)
    for (lx,ly) in ((0.55,-0.18),(0.55,0.18),(-0.65,-0.18),(-0.65,0.18)):
        c.cyl((lx,ly,0.0),(lx,ly,0.72),0.075,k=0,seg=8)
        c.cyl((lx,ly,0.0),(lx,ly,0.1),0.08,k=3,seg=8)
    c.cyl((-1.0,0,1.08),(-1.12,0,0.45),0.03,k=0,seg=6)
    o=c.obj(name,smooth=True)
    o.hide_render=True; o.hide_viewport=True
    return o.data
COWS=[cow_mesh('cow_h','herf','white'),cow_mesh('cow_b','black','black'),cow_mesh('cow_d','dun','dun'),
      cow_mesh('cow_r','roan','white'),cow_mesh('cow_h2','herf','white')]
def cow(x,y,yaw,z=0.0,scale=1.0,name='cow'):
    o=bpy.data.objects.new(name,random.choice(COWS)); sc.collection.objects.link(o)
    o.location=(x,y,z); o.rotation_euler=(0,0,yaw); s=scale*random.uniform(0.9,1.08); o.scale=(s,s,s)
    return o
# pens: dense herd, keep the alley clear
placed=[]
def free(x,y,r=1.5):
    return all((x-a)**2+(y-b)**2>r*r for a,b in placed)
for _ in range(900):
    x=random.uniform(PX0+1.5,PX1-1.5); y=random.uniform(-19,19)
    if abs(y)<3.3: continue
    if free(x,y,1.55):
        placed.append((x,y)); cow(x,y,random.uniform(0,2*math.pi))
    if len(placed)>150: break
# crowding funnel waiting
for i in range(10):
    x=-CHL-random.uniform(2.5,8.5); w=0.6+(-CHL-x)*0.6
    y=random.uniform(-w,w)
    if free(x,y,1.5): placed.append((x,y)); cow(x,y,random.uniform(-0.4,0.4))
# grazing herds on the open range
for (hx,hy,n) in ((140,60,40),(-120,110,30),(60,-190,35),(260,210,30),(-60,-150,25)):
    for i in range(n):
        x=hx+random.gauss(0,16); y=hy+random.gauss(0,12)
        cow(x,y,random.uniform(0,2*math.pi),z=H(x,y))

# the moving line: pens -> alley -> chute -> slide -> swim -> incline -> drip pen -> release
def speed(x):
    if 0.0<=x<X_FE: return 1.0
    if X_FE<=x<TOPL: return 0.9
    return 1.35
def zprof(x):
    if x<0.0: return 0.0
    if x<X_FS+0.6: return -DEP*ss(0.0,X_FS+0.6,x)
    if x<X_FE: return -DEP+0.36*ss(X_FS+0.6,X_FS+2.0,x)
    if x<TOPL: return max(-DEP+0.36,-DEP+(x-X_FE)/(TOPL-X_FE)*DEP)
    if x<DX1: return 0.12
    return 0.0
# integrate one master trajectory: time -> x
traj=[(0.0,-46.0)]
t=0.0; x=-46.0; dt=0.02
while x<75:
    x+=speed(x)*dt; t+=dt; traj.append((t,x))
import bisect
TT=[a for a,_ in traj]
def x_at(tm):
    if tm<=0: return -46.0
    i=bisect.bisect_left(TT,tm)
    if i>=len(traj): return 75.0
    return traj[i][1]
T_VAT=next(a for a,b in traj if b>=0.0)
FPS=24.0; CLIP=384/FPS
line=[]
k=0
for tc in [c*2.9 for c in range(-2,12)]:
    toff=T_VAT-tc          # this animal crosses x=0 at clip time tc
    ang_side=random.uniform(-1,1)
    o=cow(0,0,0,name=f'line{k}'); k+=1
    for fr in range(0,384,2):
        tm=fr/FPS+toff
        xx=x_at(tm); zz=zprof(xx)
        yy=0.0; yaw=0.0
        if xx>DX1+1.0:
            u=xx-DX1-1.0; yy=ang_side*0.55*u; yaw=math.atan2(ang_side*0.55,1.0)
        if xx< -CHL-9.0:
            yy=0.0
        if xx< -46.0+0.01: o.hide_render=False
        # pitch from slope
        x2=xx+0.4; z2=zprof(x2); pitch=-math.atan2(z2-zz,0.4)
        bob=0.035*math.sin(tm*5.0) if (X_FS+0.6<xx<X_FE) else 0.0
        o.location=(xx-0.3,yy,zz+bob); o.rotation_euler=(0,pitch*0.8,yaw)
        o.keyframe_insert('location',frame=fr); o.keyframe_insert('rotation_euler',frame=fr)
    for fc in o.animation_data.action.fcurves:
        for kp in fc.keyframe_points: kp.interpolation='LINEAR'
    line.append(o)

# ---------------------------------------------------------------- people & horses
def person(x,y,yaw,pole=None,name='man'):
    p=MB(['denim','shirt','skin','hat','timber'])
    p.cyl((0,-0.1,0),(0,-0.1,0.85),0.075,k=0,seg=8); p.cyl((0,0.1,0),(0,0.1,0.85),0.075,k=0,seg=8)
    p.cyl((0,0,0.85),(0,0,1.45),0.19,k=1,seg=10,r2=0.2)
    p.sphere((0,0,1.6),(0.12,0.11,0.13),k=2)
    p.cyl((0,0,1.68),(0,0,1.7),0.3,k=3,seg=16); p.cyl((0,0,1.7),(0,0,1.84),0.13,k=3,seg=12)
    for sy in (-1,1): p.cyl((0,sy*0.22,1.42),(0.25,sy*0.28,1.05),0.05,k=1,seg=6)
    if pole: p.cyl(pole[0],pole[1],0.025,k=4,seg=6)
    o=p.obj(name,smooth=True); o.location=(x,y,0); o.rotation_euler=(0,0,yaw); return o
person(2.2,-1.25,math.pi/2,pole=((0.2,0.3,1.3),(0.3,1.5,-0.7)),name='dipper1')
person(4.6, 1.3,-math.pi/2,pole=((0.2,-0.3,1.3),(-0.2,-1.5,-0.9)),name='dipper2')
person(-3.0,-1.9,0.2,name='chuteman')
person(SX-0.3,SY+1.3,2.2,name='mixer')
def rider(x,y,yaw,name):
    h=MB(['bay','black','denim','shirt','skin','hat'])
    h.sphere((0,0,1.25),(0.95,0.3,0.36),k=0)
    h.cyl((0.75,0,1.35),(1.15,0,1.85),0.17,k=0,r2=0.12)
    h.sphere((1.28,0,1.85),(0.3,0.12,0.14),rot=(0,0.7,0),k=0)
    for (lx,ly) in ((0.6,-0.15),(0.6,0.15),(-0.65,-0.15),(-0.65,0.15)): h.cyl((lx,ly,0),(lx,ly,1.0),0.06,k=1,seg=6)
    h.cyl((-0.95,0,1.35),(-1.15,0,0.7),0.06,k=1,seg=6)
    h.cyl((0,0,1.55),(0,0,2.2),0.18,k=3,seg=10)
    h.sphere((0,0,2.35),(0.12,0.11,0.13),k=4)
    h.cyl((0,0,2.43),(0,0,2.45),0.3,k=5,seg=16); h.cyl((0,0,2.45),(0,0,2.58),0.13,k=5,seg=12)
    for sy in (-1,1): h.cyl((0,sy*0.12,1.55),(0.25,sy*0.34,1.1),0.06,k=2,seg=6)
    o=h.obj(name,smooth=True); o.location=(x,y,0); o.rotation_euler=(0,0,yaw); return o
r1=rider(-40,-1.0,0.0,'rider1')
r2=rider(-36,8.0,-0.6,'rider2')
for o,(x0,x1) in ((r1,(-44,-30)),):
    o.location.x=x0; o.keyframe_insert('location',frame=0); o.location.x=x1; o.keyframe_insert('location',frame=383)
rider(90,40,2.0,'rider3'); rider(96,52,2.4,'rider4')

# ---------------------------------------------------------------- trees
def oak(name,m_fol,m_bark,height):
    t=MB([m_bark,m_fol])
    t.cyl((0,0,0),(0,0,height*0.35),0.35*height/9,k=0,seg=10,r2=0.25*height/9)
    for i in range(3):
        a=i*2.1+random.uniform(-.3,.3)
        t.cyl((0,0,height*0.3),(math.cos(a)*height*0.28,math.sin(a)*height*0.28,height*0.55),0.14*height/9,k=0,seg=8)
    for i in range(9):
        a=random.uniform(0,2*math.pi); r=random.uniform(0,height*0.42)
        t.sphere((math.cos(a)*r,math.sin(a)*r,height*random.uniform(0.55,0.85)),
                 (height*random.uniform(0.22,0.34),height*random.uniform(0.22,0.34),height*random.uniform(0.16,0.24)),k=1,u=10,v=7)
    o=t.obj(name,smooth=True); o.hide_render=True; o.hide_viewport=True
    me=o.data
    return me
OAKS=[oak(f'oak{i}','foliage','bark',random.uniform(7,11)) for i in range(4)]
SYCS=[oak(f'syc{i}','syc','sycbark',random.uniform(11,15)) for i in range(3)]
def place_tree(meshes,x,y,s=1.0,name='tree'):
    o=bpy.data.objects.new(name,random.choice(meshes)); sc.collection.objects.link(o)
    o.location=(x,y,H(x,y)-0.3); o.rotation_euler=(0,0,random.uniform(0,6.28)); ss_=s*random.uniform(0.8,1.25); o.scale=(ss_,ss_,ss_)
n=0
while n<170:
    x=random.uniform(-500,700); y=random.uniform(-400,650)
    if abs(y-(-70+14*math.sin(x/55)))<25: continue
    if -70<x<50 and -35<y<35: continue
    if noise.noise(Vector((x/120,y/120,3.3)))<-0.05: continue
    place_tree(OAKS,x,y); n+=1
for i in range(55):
    x=-300+i*13+random.uniform(-4,4); y=-70+14*math.sin(x/55)+random.uniform(-8,8)
    place_tree(SYCS,x,y,1.0)
for (x,y) in ((-30,-30),(22,24),(35,-28)):
    place_tree(OAKS,x,y,1.15)

# ---------------------------------------------------------------- grass tufts (particles)
def tufts():
    t=MB(['tuft'])
    for i in range(7):
        a=i/7*2*math.pi
        t.cyl((0,0,0),(math.cos(a)*0.12,math.sin(a)*0.12,random.uniform(0.3,0.55)),0.03,k=0,seg=4,r2=0.002)
    tuft=t.obj('tuft'); tuft.hide_render=True; tuft.hide_viewport=True
    bm=bmesh.new(); X0,X1,Y0,Y1=-110,130,-110,110; st=2.0; g={}
    nx=int((X1-X0)/st); ny=int((Y1-Y0)/st)
    for i in range(nx+1):
        for j in range(ny+1):
            x=X0+i*st; y=Y0+j*st
            z=H(x,y) if not (-20<=x<=26 and -14<=y<=14) else 0.0
            g[i,j]=bm.verts.new((x,y,z))
    for i in range(nx):
        for j in range(ny):
            bm.faces.new((g[i,j],g[i+1,j],g[i+1,j+1],g[i,j+1]))
    me=bpy.data.meshes.new('scatter'); bm.to_mesh(me); bm.free()
    o=bpy.data.objects.new('scatter',me); sc.collection.objects.link(o)
    vg=o.vertex_groups.new(name='dens')
    for v in me.vertices:
        x,y,_=v.co
        w=1.0
        if PX0-3<x<PX1+3 and -23<y<23: w=0.0
        if -32<x<DX1+25 and -16<y<16: w=min(w,ss(0,6,max(abs(y)-10,0)))
        if SX-6<x<SX+6 and SY-5<y<SY+5: w=0.0
        vg.add([v.index],w,'REPLACE')
    ps=o.modifiers.new('tufts','PARTICLE_SYSTEM').particle_system
    st_=ps.settings
    st_.type='HAIR'; st_.use_advanced_hair=True; st_.count=45000; st_.hair_length=1.0
    st_.render_type='OBJECT'; st_.instance_object=tuft
    st_.particle_size=1.0; st_.size_random=0.6
    st_.use_rotations=True; st_.rotation_mode='NOR'; st_.phase_factor_random=2.0
    st_.emit_from='FACE'; st_.use_emit_random=True
    ps.vertex_group_density='dens'
    o.show_instancer_for_render=False
tufts()

# ---------------------------------------------------------------- lighting & world
sun_d=bpy.data.lights.new('sun','SUN'); sun_d.energy=3.2; sun_d.angle=math.radians(1.2); sun_d.color=(1.0,0.93,0.82)
sun=bpy.data.objects.new('sun',sun_d); sc.collection.objects.link(sun)
sun.rotation_euler=(math.radians(52),0,math.radians(-38))
w=bpy.data.worlds.new('world'); sc.world=w; w.use_nodes=True; nt=w.node_tree
bg=nt.nodes["Background"]
sky=nt.nodes.new("ShaderNodeTexSky"); sky.sky_type='NISHITA'
sky.sun_elevation=math.radians(38); sky.sun_rotation=math.radians(128); sky.altitude=200; sky.air_density=1.2; sky.dust_density=2.2
nt.links.new(sky.outputs[0],bg.inputs[0]); bg.inputs[1].default_value=0.12
vol=nt.nodes.new("ShaderNodeVolumePrincipled")
vol.inputs["Density"].default_value=0.00055
vol.inputs["Color"].default_value=(0.75,0.82,0.95,1)


# ---------------------------------------------------------------- camera
cam_d=bpy.data.cameras.new('cam'); cam_d.lens=26; cam_d.clip_end=5000; cam_d.clip_start=0.1
cam=bpy.data.objects.new('cam',cam_d); sc.collection.objects.link(cam); sc.camera=cam
tgt=bpy.data.objects.new('tgt',None); sc.collection.objects.link(tgt)
con=cam.constraints.new('TRACK_TO'); con.target=tgt; con.track_axis='TRACK_NEGATIVE_Z'; con.up_axis='UP_Y'
KEYS=[ #frame, cam loc, target loc, lens
 (0,   (-105,-128,62),(-12,4,0),28),
 (80,  (-86,-66,42),(-22,0,0),28),
 (150, (-56,-34,17),(-28,0,0),26),
 (210, (-24,-10,7.5),(-3,0,0),24),
 (262, (3.4,-4.6,8.8),(3.9,0,-1.1),24),
 (312, (9.5,-7.4,7.2),(9.0,0,-0.3),24),
 (350, (18,-13,8),(8,0,0),24),
 (383, (52,-60,34),(4,0,0),26),
]
for f,cl,tl,lens in KEYS:
    cam.location=cl; cam.keyframe_insert('location',frame=f)
    tgt.location=tl; tgt.keyframe_insert('location',frame=f)
    cam_d.lens=lens; cam_d.keyframe_insert('lens',frame=f)
for ob in (cam,tgt,cam_d):
    ad=ob.animation_data
    for fc in ad.action.fcurves:
        for kp in fc.keyframe_points:
            kp.interpolation='BEZIER'; kp.handle_left_type='AUTO_CLAMPED'; kp.handle_right_type='AUTO_CLAMPED'

bpy.ops.wm.save_as_mainfile(filepath=os.path.join(os.path.dirname(OUT.rstrip('/')),'dipping_station.blend'))
if TEST:
    for f in [int(v) for v in TEST.split(',')]:
        sc.frame_set(f); sc.render.filepath=os.path.join(OUT,f'test_{f:04d}.png')
        bpy.ops.render.render(write_still=True)
else:
    sc.render.filepath=os.path.join(OUT,'f_')
    bpy.ops.render.render(animation=True)
