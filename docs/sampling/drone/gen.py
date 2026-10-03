# -*- coding: utf-8 -*-
import math, json, urllib.request, time, os, sys
from concurrent.futures import ThreadPoolExecutor

UA={'User-Agent':'LEHRP-research/1.0'}
M_LAT=110950.0
def mlon(lat): return 111320.0*math.cos(math.radians(lat))
def off(lat,lon,dn,de):           # metres north, metres east
    return lat+dn/M_LAT, lon+de/mlon(lat)

STATIONS=[
 # id, lat, lon, name, grid? , note
 ('D2',33.55505,-117.65492,'1948 ranch structure',True ,'trail convergence beside the creek'),
 ('D3',33.55857,-117.65281,'T6 slope below the find',True ,'scrub, open enough to map'),
 ('D4',33.54793,-117.65992,'T8 creek corridor',False,'CLOSED OAK CANOPY - no grid'),
 ('D5',33.54763,-117.65929,'T2 creek bench',False,'CLOSED OAK CANOPY - no grid'),
 ('D6',33.55057,-117.66081,'T11 above the trail',False,'houses within 150 m'),
 ('D6b',33.55143,-117.66048,'T12 above the trail',False,'houses within 150 m'),
 ('D7',33.53482,-117.65619,'T19 open ground',True ,'no canopy, nothing built'),
]
ORBIT_R=40.0; ORBIT_N=8; ORBIT_AGL=28.0; ORBIT_PITCH=-35
GRID_SIDE=150.0; GRID_SPACING=30.0; GRID_AGL=60.0

pts=[]   # dicts: sid,kind,idx,lat,lon,agl,pitch,head
for sid,lat,lon,name,grid,note in STATIONS:
    pts.append(dict(sid=sid,kind='centre',idx=0,lat=lat,lon=lon,agl=ORBIT_AGL,pitch=-90,head=0,name=name))
    for i in range(ORBIT_N):
        th=2*math.pi*i/ORBIT_N
        dn,de=ORBIT_R*math.cos(th),ORBIT_R*math.sin(th)
        la,lo=off(lat,lon,dn,de)
        head=(math.degrees(math.atan2(-de,-dn)))%360        # face the centre
        pts.append(dict(sid=sid,kind='orbit',idx=i+1,lat=la,lon=lo,agl=ORBIT_AGL,pitch=ORBIT_PITCH,head=round(head),name=name))
    if grid:
        half=GRID_SIDE/2; nlines=int(GRID_SIDE/GRID_SPACING)+1
        k=0
        for li in range(nlines):
            e=-half+li*GRID_SPACING
            ends=[-half,half] if li%2==0 else [half,-half]
            for n_ in ends:
                la,lo=off(lat,lon,n_,e)
                k+=1
                pts.append(dict(sid=sid,kind='grid',idx=k,lat=la,lon=lo,agl=GRID_AGL,pitch=-90,head=0,name=name))

def elev(p):
    u=f"https://epqs.nationalmap.gov/v1/json?x={p['lon']:.7f}&y={p['lat']:.7f}&units=Meters&wkid=4326&includeDate=false"
    for a in range(4):
        try:
            d=json.loads(urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=45).read())
            v=d.get('value')
            if v is not None: p['gnd']=float(v); return p
        except Exception: time.sleep(2+2*a)
    p['gnd']=None; return p
print('waypoints:',len(pts),flush=True)
with ThreadPoolExecutor(max_workers=4) as ex:
    pts=list(ex.map(elev,pts))
miss=[p for p in pts if p['gnd'] is None]
print('elevations fetched, missing:',len(miss),flush=True)
json.dump(pts,open('pts.json','w'),indent=1)
for sid,lat,lon,name,grid,note in STATIONS:
    g=[p['gnd'] for p in pts if p['sid']==sid and p['gnd'] is not None]
    c=[p for p in pts if p['sid']==sid and p['kind']=='centre'][0]
    print(f"  {sid:4s} centre {c['gnd']:6.1f} m   range {min(g):6.1f} - {max(g):6.1f}   relief {max(g)-min(g):5.1f} m   n={len(g)}")
