import math,urllib.request,urllib.parse,io as _io,json
from PIL import Image
Image.MAX_IMAGE_PIXELS=None
UA={'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/131.0 Safari/537.36'}
X0,X1,Y0,Y1=-117.6700,-117.6440,33.5300,33.5640
W=6000; H=9383
SVC='https://www.ocgis.com/arcpub/rest/services/Historic_Imagery/Historic_Imagery_v2/ImageServer/exportImage'
mr=json.dumps({"mosaicMethod":"esriMosaicLockRaster","lockRasterIds":[319]})
N=3; hpx=[H//N]*N; hpx[-1]+=H-sum(hpx); rows=[]; y=Y1
for i in range(N):
    y2=y-(Y1-Y0)*hpx[i]/H
    p={'bbox':f'{X0},{y2},{X1},{y}','bboxSR':'4326','imageSR':'4326',
       'size':f'{W},{hpx[i]}','format':'jpg','f':'image','mosaicRule':mr}
    u=SVC+'?'+urllib.parse.urlencode(p)
    b=urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=300).read()
    im=Image.open(_io.BytesIO(b)).convert('RGB')
    print(' tile',i,im.size,len(b)//1024,'KB'); rows.append(im); y=y2
out=Image.new('RGB',(W,H)); yy=0
for im in rows: out.paste(im,(0,yy)); yy+=im.size[1]
out.save('base1990.jpg',quality=92); print('saved',out.size)
