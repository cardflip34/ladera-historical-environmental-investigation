#!/usr/bin/env python3
"""SoCal satellite overview with the dipping-probability zone markers on one real satellite base.
Companion to the per-community satellite atlas. GRADED INFERENCE of the dipping PRACTICE — NOT a
contamination map, NOT vat locations; no soil tested anywhere. Imagery: Esri World Imagery (Maxar et al.)."""
import math, io, urllib.parse, urllib.request, os
from PIL import Image, ImageDraw, ImageFont
OUT="research/statewide"; UA={"User-Agent":"Mozilla/5.0 (research)"}
ESRI="https://services.arcgisonline.com/arcgis/rest/services/World_Imagery/MapServer/export"
TIER={"documented":(214,70,66),"documented_unk":(224,168,58),"highly":(240,120,58),"likely":(236,180,100),"plausible":(200,200,170)}
WLON,ELON,SLAT,NLAT=-118.68,-116.72,32.72,34.56
dlon=ELON-WLON; dlat=NLAT-SLAT
H=1900; W=int(H*dlon*math.cos(math.radians(33.6))/dlat)
u=ESRI+"?"+urllib.parse.urlencode({"bbox":f"{WLON},{SLAT},{ELON},{NLAT}","bboxSR":"4326","imageSR":"4326","size":f"{W},{H}","format":"jpg","f":"image"})
base=Image.open(io.BytesIO(urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=90).read())).convert("RGB")
dr=ImageDraw.Draw(base,"RGBA")
def F(sz,b=True):
    p="/System/Library/Fonts/Supplemental/Arial Bold.ttf" if b else "/System/Library/Fonts/Supplemental/Arial.ttf"
    try: return ImageFont.truetype(p,sz)
    except: return ImageFont.load_default()
def px(lon,lat): return ((lon-WLON)/dlon*W,(NLAT-lat)/dlat*H)
# num,name,tier,lat,lon,side(1=label right,-1=left,0=below)
M=[(1,"Coto de Caza","documented",33.600,-117.588,1),(2,"San Juan Capistrano","documented",33.501,-117.662,1),
 (3,"Yorba Linda","documented",33.888,-117.813,-1),(4,"Anaheim Hills","documented",33.856,-117.760,1),
 (5,"LONG BEACH (Los Cerritos)","documented_unk",33.817,-118.188,-1),(6,"Irvine","highly",33.685,-117.790,1),
 (7,"Ladera Ranch","highly",33.548,-117.635,1),(8,"Camp Pendleton","highly",33.300,-117.350,1),
 (9,"Simi Valley","likely",34.270,-118.550,1),(10,"Fillmore","likely",34.399,-118.700,-1),
 (11,"Rancho Santa Fe / Del Mar","likely",33.010,-117.200,0),(12,"Rancho Bernardo","likely",33.020,-117.075,1),
 (13,"Rancho Peñasquitos","likely",32.955,-117.100,1),(14,"Long Beach / Los Alamitos","plausible",33.786,-118.070,-1),
 (15,"Rancho Cucamonga","plausible",34.110,-117.575,1),(16,"Jurupa Valley","plausible",33.995,-117.450,1),
 (17,"Valencia / Santa Clarita","plausible",34.430,-118.560,1)]
for num,name,tier,lat,lon,side in M:
    x,y=px(lon,lat); c=TIER[tier]; r=16
    dr.ellipse([x-r,y-r,x+r,y+r],fill=c+(255,),outline=(255,255,255),width=3)
    dr.text((x,y),str(num),font=F(17),fill=(30,20,15),anchor="mm")
    tw=dr.textlength(name,font=F(19))
    if side==0:
        dr.rectangle([x-tw/2-8,y+20,x+tw/2+8,y+50],fill=(0,0,0,150)); dr.text((x,y+35),name,font=F(19),fill=(255,255,255),anchor="mm")
    else:
        lx=x+(22 if side>0 else -22); anch="lm" if side>0 else "rm"; bx0=lx if side>0 else lx-tw-14
        dr.rectangle([bx0-6,y-15,bx0+tw+14,y+15],fill=(0,0,0,150)); dr.text((lx if side>0 else lx-6,y),name,font=F(19),fill=(255,255,255),anchor=anch)
dr.rectangle([0,0,W,104],fill=(0,0,0,180))
dr.text((26,20),"Dipping-probability zones over satellite — Southern California",font=F(34),fill=(255,255,255))
dr.text((28,66),"graded PROBABILITY of the dipping practice · NOT contamination · (Tejon & Miller & Lux are in the atlas)",font=F(20,False),fill=(255,205,170))
ly=H-232; dr.rectangle([20,ly-16,470,ly+164],fill=(0,0,0,175))
for i,(tier,lab) in enumerate([("documented","DOCUMENTED — arsenical dip named"),("documented_unk","DOCUMENTED — dipping, chem. unconfirmed"),
 ("highly","HIGHLY PROBABLE"),("likely","LIKELY"),("plausible","PLAUSIBLE — lesser county / crop-arsenic vector")]):
    yy=ly+i*30; dr.ellipse([32,yy,54,yy+22],fill=TIER[tier]+(255,),outline=(255,255,255),width=2)
    dr.text((66,yy+11),lab,font=F(16,False),fill=(240,236,228),anchor="lm")
dr.rectangle([0,H-52,W,H],fill=(0,0,0,195))
dr.text((26,H-36),"GRADED INFERENCE, not measurement · NOT a contamination map · NOT vat locations · no soil tested anywhere · practice != residue != exposure · Imagery: Esri World Imagery (Maxar et al.)",font=F(15,False),fill=(220,214,205),anchor="lm")
base.save(os.path.join(OUT,"CA_dipping_satellite_overview.jpg"),quality=88)
print("wrote",os.path.join(OUT,"CA_dipping_satellite_overview.jpg"),base.size)
