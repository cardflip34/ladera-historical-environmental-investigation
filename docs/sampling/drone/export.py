# -*- coding: utf-8 -*-
import json, math, os, zipfile, html
pts=json.load(open('pts.json'))
ORDER=['D2','D3','D4','D5','D6','D6b','D7']
NAME={'D2':'D2 1948 ranch structure','D3':'D3 T6 slope below the find','D4':'D4 T8 creek corridor',
      'D5':'D5 T2 creek bench','D6':'D6 T11 above the trail','D6b':'D6b T12 above the trail',
      'D7':'D7 T19 open ground'}
by={s:[p for p in pts if p['sid']==s] for s in ORDER}
for s in ORDER:
    c=[p for p in by[s] if p['kind']=='centre'][0]
    for p in by[s]:
        p['alt_cmd']=round(p['agl']+(p['gnd']-c['gnd']),1)   # relative to launch at centre
        p['dgnd']=round(p['gnd']-c['gnd'],1)
os.makedirs('out',exist_ok=True)

# ---------- 1. KML ----------
def kml_pt(p,n):
    d=(f"commanded altitude {p['alt_cmd']} m above the launch point&#10;"
       f"target {p['agl']:.0f} m AGL &#183; ground {p['gnd']:.1f} m &#183; {p['dgnd']:+.1f} m vs launch&#10;"
       f"gimbal {p['pitch']}&#176; &#183; heading {p['head']}&#176;")
    return (f"<Placemark><name>{html.escape(n)}</name><description>{d}</description>"
            f"<styleUrl>#{p['kind']}</styleUrl>"
            f"<Point><coordinates>{p['lon']:.7f},{p['lat']:.7f},{p['alt_cmd']}</coordinates></Point></Placemark>")
K=['<?xml version="1.0" encoding="UTF-8"?>','<kml xmlns="http://www.opengis.net/kml/2.2"><Document>',
   '<name>Ladera drone recon - ungraded stations</name>',
   '<Style id="centre"><IconStyle><scale>1.3</scale><color>ff3045d6</color></IconStyle></Style>',
   '<Style id="orbit"><IconStyle><scale>0.9</scale><color>ffd6ce48</color></IconStyle></Style>',
   '<Style id="grid"><IconStyle><scale>0.7</scale><color>ff8ad65c</color></IconStyle></Style>',
   '<Style id="ln"><LineStyle><color>ccd6ce48</color><width>3</width></LineStyle></Style>',
   '<Style id="lng"><LineStyle><color>cc8ad65c</color><width>2</width></LineStyle></Style>']
for s in ORDER:
    K.append(f'<Folder><name>{html.escape(NAME[s])}</name>')
    cen=[p for p in by[s] if p['kind']=='centre']
    orb=[p for p in by[s] if p['kind']=='orbit']
    grd=[p for p in by[s] if p['kind']=='grid']
    for p in cen: K.append(kml_pt(p,f"{s} CENTRE"))
    for p in orb: K.append(kml_pt(p,f"{s} orbit {p['idx']}"))
    if orb:
        co=' '.join(f"{p['lon']:.7f},{p['lat']:.7f},{p['alt_cmd']}" for p in orb+[orb[0]])
        K.append(f'<Placemark><name>{s} orbit path</name><styleUrl>#ln</styleUrl><LineString><tessellate>1</tessellate><altitudeMode>relativeToGround</altitudeMode><coordinates>{co}</coordinates></LineString></Placemark>')
    for p in grd: K.append(kml_pt(p,f"{s} grid {p['idx']}"))
    if grd:
        co=' '.join(f"{p['lon']:.7f},{p['lat']:.7f},{p['alt_cmd']}" for p in grd)
        K.append(f'<Placemark><name>{s} mapping grid</name><styleUrl>#lng</styleUrl><LineString><tessellate>1</tessellate><altitudeMode>relativeToGround</altitudeMode><coordinates>{co}</coordinates></LineString></Placemark>')
        la=[p['lat'] for p in grd]; lo=[p['lon'] for p in grd]
        ring=[(min(lo),min(la)),(max(lo),min(la)),(max(lo),max(la)),(min(lo),max(la)),(min(lo),min(la))]
        co=' '.join(f'{x:.7f},{y:.7f},0' for x,y in ring)
        K.append(f'<Placemark><name>{s} SURVEY AREA (draw this polygon in a mapping app)</name>'
                 f'<Style><LineStyle><color>ff5cd68a</color><width>3</width></LineStyle><PolyStyle><color>335cd68a</color></PolyStyle></Style>'
                 f'<Polygon><outerBoundaryIs><LinearRing><coordinates>{co}</coordinates></LinearRing></outerBoundaryIs></Polygon></Placemark>')
    K.append('</Folder>')
K.append('</Document></kml>')
open('out/Ladera_stations.kml','w').write('\n'.join(K))

# ---------- 2. Litchi CSV, one per station ----------
HDR=("latitude,longitude,altitude(m),heading(deg),curvesize(m),rotationdir,gimbalmode,gimbalpitchangle,"
     +','.join(f"actiontype{i},actionparam{i}" for i in range(1,16))
     +",altitudemode,speed(m/s),poi_latitude,poi_longitude,poi_altitude(m),poi_altitudemode,photo_timeinterval,photo_distinterval")
def litchi(rows,poi=None,fn='x.csv'):
    L=[HDR]
    for p in rows:
        acts=['1','0']+['-1','0']*14                       # action1 = take photo
        pl,pn,pa = (poi[1],poi[0],0) if poi else (0,0,0)
        L.append(','.join([f"{p['lat']:.7f}",f"{p['lon']:.7f}",f"{p['alt_cmd']}",f"{p['head']}","0.2","0",
                           "2" if poi else "0", f"{p['pitch']}"]+acts+["0","3.0",
                           f"{pn:.7f}",f"{pl:.7f}","0","0","-1","-1"]))
    open(fn,'w').write('\n'.join(L))
for s in ORDER:
    c=[p for p in by[s] if p['kind']=='centre'][0]
    orb=[p for p in by[s] if p['kind']=='orbit']
    litchi(orb,poi=(c['lon'],c['lat']),fn=f'out/litchi_{s}_orbit.csv')
    grd=[p for p in by[s] if p['kind']=='grid']
    if grd: litchi(grd,poi=None,fn=f'out/litchi_{s}_grid.csv')

# ---------- 3. GPX ----------
G=['<?xml version="1.0" encoding="UTF-8"?>','<gpx version="1.1" creator="LEHRP" xmlns="http://www.topografix.com/GPX/1/1">']
for s in ORDER:
    for p in by[s]:
        nm=f"{s}-{p['kind']}{p['idx'] if p['kind']!='centre' else ''}"
        G.append(f'<wpt lat="{p["lat"]:.7f}" lon="{p["lon"]:.7f}"><ele>{p["gnd"]:.1f}</ele><name>{nm}</name>'
                 f'<desc>cmd alt {p["alt_cmd"]} m rel launch; {p["agl"]:.0f} m AGL; gimbal {p["pitch"]}</desc></wpt>')
G.append('</gpx>')
open('out/Ladera_stations.gpx','w').write('\n'.join(G))

# ---------- 4. plain list for manual entry ----------
T=['LADERA DRONE STATIONS - decimal degrees for manual entry',''.ljust(0),
   'Paste a pair into Google Maps or Apple Maps to navigate to it on the ground.','']
for s in ORDER:
    c=[p for p in by[s] if p['kind']=='centre'][0]
    T.append(f"{NAME[s]}")
    T.append(f"  CENTRE            {c['lat']:.6f}, {c['lon']:.6f}      ground {c['gnd']:.1f} m")
    T.append(f"  launch here; all altitudes below are relative to this point")
    orb=[p for p in by[s] if p['kind']=='orbit']
    for p in orb:
        T.append(f"  orbit {p['idx']} hdg {p['head']:>3}   {p['lat']:.6f}, {p['lon']:.6f}   set alt {p['alt_cmd']:>5} m  gimbal {p['pitch']}")
    grd=[p for p in by[s] if p['kind']=='grid']
    if grd:
        T.append(f"  mapping grid, {len(grd)} points, 150 x 150 m, 30 m line spacing, nadir:")
        for p in grd:
            T.append(f"  grid {p['idx']:>2}          {p['lat']:.6f}, {p['lon']:.6f}   set alt {p['alt_cmd']:>5} m")
    T.append('')
open('out/Ladera_stations.txt','w').write('\n'.join(T))
print('written:'); [print('  ',f) for f in sorted(os.listdir('out'))]
