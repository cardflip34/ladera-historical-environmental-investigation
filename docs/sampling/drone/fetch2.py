import math,urllib.request,urllib.parse,io as _io,json
from PIL import Image
Image.MAX_IMAGE_PIXELS=None
UA={'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/131.0 Safari/537.36'}
X0,X1,Y0,Y1=-117.6680,-117.6480,33.5330,33.5620
latm=(Y0+Y1)/2
MPLON=111320*math.cos(math.radians(latm)); MPLAT=110950
Wm=(X1-X0)*MPLON; Hm=(Y1-Y0)*MPLAT
W=5200; H=int(round(W*Hm/Wm))
print(f'ground {Wm:.0f} x {Hm:.0f} m -> {W} x {H} px ({Wm/W:.3f} m/px)')
def grab(svc,mr=None,fn='x.jpg'):
    N=3; hpx=[H//N]*N; hpx[-1]+=H-sum(hpx); rows=[]; y=Y1
    for i in range(N):
        y2=y-(Y1-Y0)*hpx[i]/H
        p={'bbox':f'{X0},{y2},{X1},{y}','bboxSR':'4326','imageSR':'4326',
           'size':f'{W},{hpx[i]}','format':'jpg','f':'image'}
        if mr: p['mosaicRule']=mr
        u=svc+'?'+urllib.parse.urlencode(p)
        b=urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=300).read()
        rows.append(Image.open(_io.BytesIO(b)).convert('RGB')); y=y2
    out=Image.new('RGB',(W,H)); yy=0
    for im in rows: out.paste(im,(0,yy)); yy+=im.size[1]
    out.save(fn,quality=92); print(' ',fn,out.size)
grab('https://www.ocgis.com/arcpub/rest/services/Aerial_Imagery_Countywide/Eagle_Aerial_2025_OC_1FT_sid/ImageServer/exportImage',None,'b25.jpg')
grab('https://www.ocgis.com/arcpub/rest/services/Historic_Imagery/Historic_Imagery_v2/ImageServer/exportImage',
     json.dumps({"mosaicMethod":"esriMosaicLockRaster","lockRasterIds":[319]}),'b90.jpg')
json.dump({'X0':X0,'X1':X1,'Y0':Y0,'Y1':Y1,'W':W,'H':H,'mpx':Wm/W},open('geo.json','w'))
