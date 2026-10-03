#!/usr/bin/env python3
"""
Build the same waypoint set for D1 - the August 2026 concrete feature.

    python3 d1.py 33.558xxx -117.652xxx

Its coordinate is deliberately not stored in this repository. You supply it,
the script fetches real ground elevation from the USGS 1 m DEM for every
waypoint, corrects each altitude so the aircraft holds a constant height above
ground rather than above the launch point, and writes KML, Litchi CSV, GPX and
a plain list into ./out_D1/.
"""
import sys, math, json, os, urllib.request, time
from concurrent.futures import ThreadPoolExecutor
if len(sys.argv)<3:
    print(__doc__); sys.exit(1)
LAT,LON=float(sys.argv[1]),float(sys.argv[2])
UA={'User-Agent':'LEHRP-research/1.0'}; M_LAT=110950.0
def mlon(lat): return 111320.0*math.cos(math.radians(lat))
def off(lat,lon,dn,de): return lat+dn/M_LAT, lon+de/mlon(lat)
ORBIT_R,ORBIT_N,ORBIT_AGL,PITCH=40.0,8,28.0,-35
GRID_SIDE,GRID_SP,GRID_AGL=150.0,30.0,60.0
pts=[dict(kind='centre',idx=0,lat=LAT,lon=LON,agl=ORBIT_AGL,pitch=-90,head=0)]
for i in range(ORBIT_N):
    th=2*math.pi*i/ORBIT_N; dn,de=ORBIT_R*math.cos(th),ORBIT_R*math.sin(th)
    la,lo=off(LAT,LON,dn,de)
    pts.append(dict(kind='orbit',idx=i+1,lat=la,lon=lo,agl=ORBIT_AGL,pitch=PITCH,
                    head=round(math.degrees(math.atan2(-de,-dn))%360)))
half=GRID_SIDE/2; k=0
for li in range(int(GRID_SIDE/GRID_SP)+1):
    e=-half+li*GRID_SP
    for n_ in ([-half,half] if li%2==0 else [half,-half]):
        la,lo=off(LAT,LON,n_,e); k+=1
        pts.append(dict(kind='grid',idx=k,lat=la,lon=lo,agl=GRID_AGL,pitch=-90,head=0))
def elev(p):
    u=f"https://epqs.nationalmap.gov/v1/json?x={p['lon']:.7f}&y={p['lat']:.7f}&units=Meters&wkid=4326&includeDate=false"
    for a in range(4):
        try:
            v=json.loads(urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=45).read()).get('value')
            if v is not None: p['gnd']=float(v); return p
        except Exception: time.sleep(2+2*a)
    p['gnd']=None; return p
with ThreadPoolExecutor(max_workers=4) as ex: pts=list(ex.map(elev,pts))
bad=[p for p in pts if p['gnd'] is None]
if bad: print(f"WARNING: no elevation for {len(bad)} waypoints; their altitudes are uncorrected")
c=pts[0]
for p in pts:
    p['alt_cmd']=round(p['agl']+((p['gnd']-c['gnd']) if (p['gnd'] and c['gnd']) else 0),1)
os.makedirs('out_D1',exist_ok=True)
HDR=("latitude,longitude,altitude(m),heading(deg),curvesize(m),rotationdir,gimbalmode,gimbalpitchangle,"
     +','.join(f"actiontype{i},actionparam{i}" for i in range(1,16))
     +",altitudemode,speed(m/s),poi_latitude,poi_longitude,poi_altitude(m),poi_altitudemode,photo_timeinterval,photo_distinterval")
def litchi(rows,poi,fn):
    L=[HDR]
    for p in rows:
        acts=['1','0']+['-1','0']*14
        pn,pl=(poi[1],poi[0]) if poi else (0,0)
        L.append(','.join([f"{p['lat']:.7f}",f"{p['lon']:.7f}",f"{p['alt_cmd']}",f"{p['head']}","0.2","0",
                 "2" if poi else "0",f"{p['pitch']}"]+acts+["0","3.0",f"{pn:.7f}",f"{pl:.7f}","0","0","-1","-1"]))
    open(fn,'w').write('\n'.join(L))
litchi([p for p in pts if p['kind']=='orbit'],(LON,LAT),'out_D1/litchi_D1_orbit.csv')
litchi([p for p in pts if p['kind']=='grid'],None,'out_D1/litchi_D1_grid.csv')
K=['<?xml version="1.0" encoding="UTF-8"?>','<kml xmlns="http://www.opengis.net/kml/2.2"><Document><name>D1</name>']
for p in pts:
    K.append(f"<Placemark><name>D1 {p['kind']}{p['idx'] or ''}</name>"
             f"<description>cmd alt {p['alt_cmd']} m rel launch; {p['agl']:.0f} m AGL; gimbal {p['pitch']}; hdg {p['head']}</description>"
             f"<Point><coordinates>{p['lon']:.7f},{p['lat']:.7f},{p['alt_cmd']}</coordinates></Point></Placemark>")
grd=[p for p in pts if p['kind']=='grid']
la=[p['lat'] for p in grd]; lo=[p['lon'] for p in grd]
ring=[(min(lo),min(la)),(max(lo),min(la)),(max(lo),max(la)),(min(lo),max(la)),(min(lo),min(la))]
K.append('<Placemark><name>D1 SURVEY AREA</name><Style><LineStyle><color>ff3045d6</color><width>3</width></LineStyle>'
         '<PolyStyle><color>333045d6</color></PolyStyle></Style><Polygon><outerBoundaryIs><LinearRing><coordinates>'
         +' '.join(f'{x:.7f},{y:.7f},0' for x,y in ring)+'</coordinates></LinearRing></outerBoundaryIs></Polygon></Placemark>')
K.append('</Document></kml>'); open('out_D1/D1.kml','w').write('\n'.join(K))
G=['<?xml version="1.0" encoding="UTF-8"?>','<gpx version="1.1" creator="LEHRP" xmlns="http://www.topografix.com/GPX/1/1">']
for p in pts: G.append(f'<wpt lat="{p["lat"]:.7f}" lon="{p["lon"]:.7f}"><name>D1-{p["kind"]}{p["idx"] or ""}</name></wpt>')
G.append('</gpx>'); open('out_D1/D1.gpx','w').write('\n'.join(G))
T=[f'D1 - August 2026 concrete feature','',f'  CENTRE / LAUNCH   {LAT:.6f}, {LON:.6f}   ground {c["gnd"]:.1f} m','']
for p in pts[1:]:
    T.append(f"  {p['kind']} {p['idx']:>2}  {p['lat']:.6f}, {p['lon']:.6f}   set alt {p['alt_cmd']:>5} m   gimbal {p['pitch']}   hdg {p['head']}")
open('out_D1/D1.txt','w').write('\n'.join(T))
g=[p['gnd'] for p in pts if p['gnd']]
print(f"D1 written to out_D1/  -  {len(pts)} waypoints, ground {min(g):.1f} to {max(g):.1f} m (relief {max(g)-min(g):.1f} m)")
