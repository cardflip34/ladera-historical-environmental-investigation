# -*- coding: utf-8 -*-
import json, math, collections
from PIL import Image, ImageDraw, ImageFont
from pyproj import Transformer

QUAR=['Virginia','North Carolina','South Carolina','Georgia','Alabama','Tennessee','Kentucky',
      'Arkansas','Texas','Missouri','California','Louisiana','Oklahoma','Mississippi','Florida']
SRC={'Virginia':'BAI','North Carolina':'BAI','South Carolina':'BAI','Georgia':'BAI','Alabama':'BAI',
     'Tennessee':'BAI','Kentucky':'BAI','Arkansas':'BAI','Texas':'BAI','Missouri':'BAI',
     'California':'BAI','Louisiana':'BAI','Oklahoma':'BAI','Mississippi':'BAI','Florida':'FL-DEP'}

states=json.load(open('states.json'))['features']
vats=json.load(open('vats_clean.json'))
for v in vats: v['state']=(v['state'] or '').strip()
BYST=collections.Counter()
for v in vats:
    try: BYST[v['state']]+=int(v['n'])
    except: BYST[v['state']]+=0
RECS=collections.Counter(v['state'] for v in vats)

W,H=5200,3980
tr=Transformer.from_crs('EPSG:4326','ESRI:102003',always_xy=True)   # Albers Equal Area CONUS
def prj(lon,lat): return tr.transform(lon,lat)
pts=[]
for f in states:
    if f['properties']['name'] in ('Alaska','Hawaii','Puerto Rico'): continue
    g=f['geometry']; polys=g['coordinates'] if g['type']=='MultiPolygon' else [g['coordinates']]
    for poly in polys:
        for ring in poly:
            for c in ring: pts.append(prj(c[0],c[1]))
xs=[p[0] for p in pts]; ys=[p[1] for p in pts]
x0,x1,y0,y1=min(xs),max(xs),min(ys),max(ys)
PAD=0.055
sx=(W*(1-2*PAD))/(x1-x0); sy=(H*(1-2*PAD)-980)/(y1-y0); S=min(sx,sy)
ox=(W-(x1-x0)*S)/2 - x0*S
oy=(H-980-(y1-y0)*S)/2 + y1*S + 430
def XY(lon,lat):
    x,y=prj(lon,lat); return (x*S+ox, -y*S+oy)

GROUND=(247,246,242); INK=(22,32,46); MUT=(118,126,140); LINE=(206,202,192)
QFILL=(242,224,214); QEDGE=(176,86,66); OTHER=(232,231,226); VRED=(188,54,36); BLUE=(31,78,121)
img=Image.new('RGB',(W,H),GROUND); d=ImageDraw.Draw(img,'RGBA')
FD='/System/Library/Fonts/Supplemental/'; AV='/System/Library/Fonts/Avenir Next Condensed.ttc'
def Fa(s): return ImageFont.truetype(AV,s,index=0)
def Fg(s,b=False): return ImageFont.truetype(FD+('Georgia Bold.ttf' if b else 'Georgia.ttf'),s)
def Fb(s): return ImageFont.truetype(FD+'Baskerville.ttc',s,index=1)

for f in states:
    nm=f['properties']['name']
    if nm in ('Alaska','Hawaii','Puerto Rico'): continue
    g=f['geometry']; polys=g['coordinates'] if g['type']=='MultiPolygon' else [g['coordinates']]
    inq=nm in QUAR
    for poly in polys:
        ring=[XY(c[0],c[1]) for c in poly[0]]
        if len(ring)>2:
            d.polygon(ring,fill=(QFILL if inq else OTHER),outline=(QEDGE if inq else LINE),width=(5 if inq else 2))
# state labels for quarantine states
CENT={'Texas':(-99.3,31.3),'California':(-119.6,37.0),'Oklahoma':(-97.5,35.5),'Arkansas':(-92.4,34.8),
 'Louisiana':(-92.2,30.9),'Mississippi':(-89.7,32.7),'Alabama':(-86.8,32.7),'Georgia':(-83.4,32.6),
 'Florida':(-81.7,28.3),'South Carolina':(-80.9,33.9),'North Carolina':(-79.4,35.5),'Tennessee':(-86.3,35.8),
 'Kentucky':(-85.3,37.5),'Missouri':(-92.5,38.4),'Virginia':(-78.7,37.5)}
for nm,(lo,la) in CENT.items():
    x,y=XY(lo,la); n=BYST.get(nm,0)
    ab={'Texas':'TX','California':'CA','Oklahoma':'OK','Arkansas':'AR','Louisiana':'LA','Mississippi':'MS',
        'Alabama':'AL','Georgia':'GA','Florida':'FL','South Carolina':'SC','North Carolina':'NC',
        'Tennessee':'TN','Kentucky':'KY','Missouri':'MO','Virginia':'VA'}[nm]
    f1=Fa(66); tw=d.textlength(ab,font=f1)
    d.text((x-tw/2,y-34),ab,font=f1,fill=(150,66,48,220))

# vat points
mx=max(BYST.values()) if BYST else 1
for v in sorted(vats,key=lambda a:-(int(a['n']) if str(a['n']).isdigit() else 0)):
    try: n=int(v['n'])
    except: n=1
    x,y=XY(v['lon'],v['lat'])
    r=6+ 20*math.sqrt(max(n,1))/math.sqrt(60)
    r=min(r,34)
    d.ellipse([x-r,y-r,x+r,y+r],fill=VRED+(170,),outline=(255,255,255,210),width=3)

# California: this project's own documented ground
for lon,lat,lab in [(-117.46,33.63,'Joplin dip ranch, T6S R7W'),(-117.6592,33.5541,'Ladera / Arroyo Trabuco structure')]:
    x,y=XY(lon,lat)
    d.ellipse([x-26,y-26,x+26,y+26],outline=BLUE+(255,),width=9)
    d.ellipse([x-8,y-8,x+8,y+8],fill=BLUE+(255,))
x,y=XY(-117.55,33.59)
bx,by=x+300,y+170
d.line([(x+20,y+8),(bx-14,by+30)],fill=BLUE+(220,),width=5)
d.rounded_rectangle([bx-18,by-16,bx+900,by+150],14,fill=(255,255,255,228),outline=BLUE+(190,),width=4)
d.text((bx,by-4),'THIS PROJECT’S GROUND',font=Fa(50),fill=BLUE)
d.text((bx,by+52),'Orange County, California — the documented dip',font=Fg(36),fill=INK)
d.text((bx,by+98),'ranch and the 2026 concrete structure',font=Fg(36),fill=INK)
img.save('natmap_base.jpg',quality=94)
json.dump({'byst':dict(BYST),'recs':dict(RECS)},open('stats.json','w'),indent=1)
print('base saved', img.size)
print('states with points:',len([k for k in BYST if k]))
