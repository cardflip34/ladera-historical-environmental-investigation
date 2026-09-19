import bpy, bmesh, math, json, os, random
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
OUT=os.environ.get("VAT_OUT"); TEST=os.environ.get("VAT_TEST","")
sc=bpy.context.scene
random.seed(21)
# ---- collect the station objects into a collection for instancing
names=["vat","dip","station_timber","spin","wheel","dipper1","dipper2","chuteman","mixer","pad"]
station=bpy.data.collections.new("station"); sc.collection.children.link(station)
for o in list(sc.objects):
    if o.name in names or o.name.startswith("line") or (o.name.startswith("cow") and abs(o.location.x)<60 and abs(o.location.y)<25 and o.name!="cow_h"):
        for c in o.users_collection: c.objects.unlink(o)
        station.objects.link(o)
terrain=bpy.data.objects["terrain"]
def Hxy(x,y):
    # sample terrain height by nearest vertex
    best=None; bd=1e9
    for v in terrain.data.vertices:
        d=(v.co.x-x)**2+(v.co.y-y)**2
        if d<bd: bd=d; best=v.co.z
    return best
SITES=[(-250.0,-110.0,0.35),(190.0,-30.0,-0.6),(400.0,160.0,0.2)]
# flatten terrain around each site (smooth pad), then instance the station there
me=terrain.data
for (sx,sy,rot) in SITES:
    z0=Hxy(sx,sy)
    for v in me.vertices:
        d=math.hypot(v.co.x-sx,v.co.y-sy)
        if d<75:
            w=1.0 if d<45 else 1-((d-45)/30)
            w=w*w*(3-2*w)
            v.co.z=v.co.z*(1-w)+(z0-0.04)*w
for i,(sx,sy,rot) in enumerate(SITES):
    e=bpy.data.objects.new(f"site{i+1}",None); sc.collection.objects.link(e)
    e.instance_type='COLLECTION'; e.instance_collection=station
    e.location=(sx,sy,Hxy(sx,sy)); e.rotation_euler=(0,0,rot)
# ---- camera: rise from the found station and reveal the ranch
cam=bpy.data.objects["cam"]; tgt=bpy.data.objects["tgt"]; cam_d=cam.data
for ob in (cam,tgt,cam_d): ob.animation_data_clear()
sc.frame_start=0; sc.frame_end=143
KEYS=[(0,(60,-75,42),(0,0,2),26),(60,(140,-260,170),(40,-10,0),28),(143,(300,-560,400),(80,0,0),30)]
for f,cl,tl,lens in KEYS:
    cam.location=cl; cam.keyframe_insert('location',frame=f)
    tgt.location=tl; tgt.keyframe_insert('location',frame=f)
    cam_d.lens=lens; cam_d.keyframe_insert('lens',frame=f)
for ob in (cam,tgt,cam_d):
    for fc in ob.animation_data.action.fcurves:
        for kp in fc.keyframe_points: kp.interpolation='BEZIER'; kp.handle_left_type='AUTO_CLAMPED'; kp.handle_right_type='AUTO_CLAMPED'
# ---- record screen positions of the 4 sites per frame
track={}
for f in range(0,144):
    sc.frame_set(f)
    pts=[]
    for (x,y) in [(4,0)]+[(s[0],s[1]) for s in SITES]:
        z=Hxy(x,y) if (x,y)!=(4,0) else 0.0
        p=world_to_camera_view(sc,cam,Vector((x,y,z)))
        pts.append((round(p.x,4),round(1-p.y,4)))
    track[f]=pts
json.dump(track,open(os.path.join(OUT,"site_track.json"),"w"))
sc.render.filepath=os.path.join(OUT,"w_")
if TEST:
    for f in [int(v) for v in TEST.split(",")]:
        sc.frame_set(f); sc.render.filepath=os.path.join(OUT,f"test_{f:04d}.png"); bpy.ops.render.render(write_still=True)
else:
    bpy.ops.render.render(animation=True)
