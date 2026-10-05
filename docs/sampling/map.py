# -*- coding: utf-8 -*-
import math,urllib.request,urllib.parse,io as _io,json
from PIL import Image, ImageDraw, ImageFont
Image.MAX_IMAGE_PIXELS=None
UA={'User-Agent':'Mozilla/5.0'}
X0,X1,Y0,Y1=-117.6700,-117.6200,33.5200,33.5730
latm=(Y0+Y1)/2
MPLON=111320*math.cos(math.radians(latm)); MPLAT=110950
Wm=(X1-X0)*MPLON; Hm=(Y1-Y0)*MPLAT
W=4200; H=int(round(W*Hm/Wm)); MPX=Wm/W
print(f'{Wm:.0f} x {Hm:.0f} m -> {W}x{H} ({MPX:.2f} m/px)')
SVC='https://www.ocgis.com/arcpub/rest/services/Aerial_Imagery_Countywide/Eagle_Aerial_2025_OC_1FT_sid/ImageServer/exportImage'
N=2; hpx=[H//N]*N; hpx[-1]+=H-sum(hpx); rows=[]; y=Y1
for i in range(N):
    y2=y-(Y1-Y0)*hpx[i]/H
    u=SVC+'?'+urllib.parse.urlencode({'bbox':f'{X0},{y2},{X1},{y}','bboxSR':'4326','imageSR':'4326',
        'size':f'{W},{hpx[i]}','format':'jpg','f':'image'})
    rows.append(Image.open(_io.BytesIO(urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=300).read())).convert('RGB')); y=y2
base=Image.new('RGB',(W,H)); yy=0
for im in rows: base.paste(im,(0,yy)); yy+=im.size[1]
base=Image.blend(base,Image.new('RGB',(W,H),(10,13,20)),0.22)
def P(lon,lat): return ((lon-X0)/(X1-X0)*W, (1-(lat-Y0)/(Y1-Y0))*H)

T=json.load(open('/Users/andystavros/Ladera-Ranch/docs/sampling/targets_data.json'))
R=json.load(open('/private/tmp/claude-501/-Users-andystavros-Ladera-Ranch/11a645e3-0e32-4153-b26f-2484e88c6e14/scratchpad/plan_rows.json'))
TIER={r['n']:r['tier'] for r in R}
COL={'A':(104,214,140),'B':(240,176,42),'C':(86,174,238),'D':(154,162,176)}
VRED=(226,74,52)
FD='/System/Library/Fonts/Supplemental/'; AV='/System/Library/Fonts/Avenir Next Condensed.ttc'
def Fa(s): return ImageFont.truetype(AV,s,index=0)
def Fg(s): return ImageFont.truetype(FD+'Georgia.ttf',s)
ov=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov)

# landmarks
for lon,lat,lab,sz in [(-117.6395,33.5520,'LADERA RANCH',76),(-117.6600,33.5420,'ARROYO TRABUCO GOLF CLUB',56),
                       (-117.6640,33.5640,'MISSION VIEJO',64),(-117.6290,33.5300,'RANCHO MISSION VIEJO',58),
                       (-117.6500,33.5250,'SAN JUAN CAPISTRANO',54)]:
    x,y=P(lon,lat); f=Fa(sz); tw=d.textlength(lab,font=f)
    d.text((x-tw/2,y),lab,font=f,fill=(236,240,248,150))

# V search area
SA=(-117.6618,33.5516,-117.6566,33.5566)
ax0,ay0=P(SA[0],SA[3]); ax1,ay1=P(SA[2],SA[1])
d.rectangle([ax0,ay0,ax1,ay1],outline=VRED+(255,),width=9)
f=Fa(52); lab='V'
d.ellipse([ax0-56,ay0-56,ax0+56,ay0+56],fill=VRED+(255,),outline=(255,255,255,255),width=5)
d.text((ax0-19,ay0-44),lab,font=Fa(78),fill=(255,255,255,255))

for t in T:
    n=t['n']; tier=TIER.get(n,'D'); col=COL[tier]
    rec=t.get('rec') or {}
    lo,la=(rec.get('lon') or t['lon']),(rec.get('lat') or t['lat'])
    x,y=P(lo,la)
    d.ellipse([x-52,y-52,x+52,y+52],fill=col+(240,),outline=(14,18,26,255),width=7)
    s=str(n); f=Fa(72); tw=d.textlength(s,font=f)
    d.text((x-tw/2,y-41),s,font=f,fill=(14,18,26,255))

# scale + north
sb=1000/MPX; sx,sy=W-sb-120,H-120
d.rectangle([sx,sy,sx+sb,sy+22],fill=(255,255,255,235))
d.rectangle([sx,sy,sx+sb/2,sy+22],fill=(16,20,28,235))
d.rectangle([sx,sy,sx+sb,sy+22],outline=(255,255,255,255),width=4)
d.text((sx,sy-54),'0',font=Fa(44),fill=(255,255,255,255))
d.text((sx+sb-56,sy-54),'1 km',font=Fa(44),fill=(255,255,255,255))
nx,ny=W-120,150
d.polygon([(nx,ny-80),(nx-26,ny+24),(nx,ny-6),(nx+26,ny+24)],fill=(255,255,255,245))
d.text((nx-14,ny+34),'N',font=Fa(56),fill=(255,255,255,255))
out=Image.alpha_composite(base.convert('RGBA'),ov).convert('RGB')
out.save('map.jpg',quality=92)
print('saved map.jpg',out.size)
