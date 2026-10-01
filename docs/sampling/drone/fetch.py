import math,urllib.request,io as _io
from PIL import Image
Image.MAX_IMAGE_PIXELS=None
UA={'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/131.0 Safari/537.36'}
X0,X1,Y0,Y1=-117.6700,-117.6440,33.5300,33.5640
latm=(Y0+Y1)/2
MPLON=111320*math.cos(math.radians(latm)); MPLAT=110950
Wm=(X1-X0)*MPLON; Hm=(Y1-Y0)*MPLAT
W=6000; H=int(round(W*Hm/Wm))
print(f'ground {Wm:.0f} x {Hm:.0f} m  ->  {W} x {H} px  ({Wm/W:.3f} m/px)')
SVC='https://www.ocgis.com/arcpub/rest/services/Aerial_Imagery_Countywide/Eagle_Aerial_2025_OC_1FT_sid/ImageServer/exportImage'
N=3; rows=[]
hpx=[H//N]*N; hpx[-1]+=H-sum(hpx)
y=Y1
for i in range(N):
    frac=hpx[i]/H
    y2=y-(Y1-Y0)*frac
    u=f'{SVC}?bbox={X0},{y2},{X1},{y}&bboxSR=4326&imageSR=4326&size={W},{hpx[i]}&format=jpg&f=image'
    b=urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=300).read()
    im=Image.open(_io.BytesIO(b)).convert('RGB')
    print('  tile',i,im.size,len(b)//1024,'KB')
    rows.append(im); y=y2
out=Image.new('RGB',(W,H)); yy=0
for im in rows: out.paste(im,(0,yy)); yy+=im.size[1]
out.save('base2025.jpg',quality=92)
print('saved base2025.jpg',out.size)
