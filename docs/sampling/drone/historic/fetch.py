import math,urllib.request,urllib.parse,io as _io,json,os,time
from PIL import Image
Image.MAX_IMAGE_PIXELS=None
UA={'User-Agent':'Mozilla/5.0'}
X0,X1,Y0,Y1=-117.6625,-117.6560,33.5510,33.5572
latm=(Y0+Y1)/2
Wm=(X1-X0)*111320*math.cos(math.radians(latm)); Hm=(Y1-Y0)*110950
W=3000; H=int(round(W*Hm/Wm))
print(f'AOI {Wm:.0f} x {Hm:.0f} m -> {W}x{H} ({Wm/W*100:.1f} cm/px)')
json.dump({'X0':X0,'X1':X1,'Y0':Y0,'Y1':Y1,'W':W,'H':H,'mpx':Wm/W},open('geo.json','w'))
HIST='https://www.ocgis.com/arcpub/rest/services/Historic_Imagery/Historic_Imagery_v2/ImageServer/exportImage'
FRAMES=[(346,'1929 South County Watersheds'),(351,'1931 Irvine Ranch'),
        (310,'1938 OC 600 scale'),(340,'1938 Orange County'),
        (293,'1947 OC 1200 scale'),(357,'1953 Orange County'),
        (324,'1959 South Orange County'),(343,'1960 Orange County'),
        (315,'1970 Orange County'),(302,'1977 SJH Corridor'),
        (320,'1980 Orange County'),(206,'1986 Trabuco Creek Channel'),
        (303,'1988 SJH Trans Corr'),(319,'1990 Orange County'),
        (314,'1991 CCSTWS Dec'),(33,'1998 O Neil Regional Park')]
MOD=[('https://www.ocgis.com/arcpub/rest/services/Aerial_Imagery_Countywide/Eagle_Aerial_2025_OC_1FT_sid/ImageServer/exportImage',None,'2025 OC 1ft'),
     ('https://www.ocgis.com/arcpub/rest/services/Aerial_Imagery_Countywide/OC_Aerial_3in_WGS84/ImageServer/exportImage',None,'2022 OC 3in')]
os.makedirs('f',exist_ok=True)
def grab(svc,mr,fn):
    p={'bbox':f'{X0},{Y0},{X1},{Y1}','bboxSR':'4326','imageSR':'4326',
       'size':f'{W},{H}','format':'jpg','f':'image'}
    if mr: p['mosaicRule']=mr
    u=svc+'?'+urllib.parse.urlencode(p)
    for a in range(3):
        try:
            b=urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=240).read()
            im=Image.open(_io.BytesIO(b)).convert('RGB'); im.save(fn,quality=95); return im
        except Exception as e:
            if a==2: print('  FAIL',fn,e); return None
            time.sleep(4)
res=[]
for oid,name in FRAMES:
    fn=f'f/{name.replace(" ","_")}.jpg'
    mr=json.dumps({"mosaicMethod":"esriMosaicLockRaster","lockRasterIds":[oid]})
    im=grab(HIST,mr,fn)
    if im:
        import numpy as np
        a=np.asarray(im.convert('L'))
        res.append((name,fn,float(a.mean()),float(a.std())))
        print(f'  {name:34s} mean {a.mean():6.1f} std {a.std():5.1f}')
    time.sleep(1)
for svc,mr,name in MOD:
    fn=f'f/{name.replace(" ","_")}.jpg'
    im=grab(svc,mr,fn)
    if im:
        import numpy as np
        a=np.asarray(im.convert('L'))
        res.append((name,fn,float(a.mean()),float(a.std())))
        print(f'  {name:34s} mean {a.mean():6.1f} std {a.std():5.1f}')
json.dump(res,open('frames.json','w'),indent=1)
print('done',len(res))
