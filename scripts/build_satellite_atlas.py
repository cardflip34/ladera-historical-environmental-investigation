#!/usr/bin/env python3
"""Satellite atlas: a real-satellite tile of each community in the dipping-probability map, with its
zone/tier labeled on it. Shows the actual houses/neighborhoods under each graded zone.

Imagery: Esri World Imagery (Maxar et al.), used as a reference basemap. This is land-use/probability
context only — a GRADED INFERENCE of where the dipping PRACTICE most probably occurred, NOT a
contamination map, NOT vat locations, and nothing here asserts anything about any home or resident.
"""
import math, io, urllib.parse, urllib.request
from PIL import Image, ImageDraw, ImageFont
import os
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT=os.path.join(ROOT,"research/statewide"); os.makedirs(OUT,exist_ok=True)
UA={"User-Agent":"Mozilla/5.0 (land-use history research)"}
ESRI="https://services.arcgisonline.com/arcgis/rest/services/World_Imagery/MapServer/export"

TIER={"documented":(176,52,50),"documented_unk":(196,140,40),"highly":(224,110,48),
      "likely":(226,164,86),"plausible":(150,150,120)}
TLAB={"documented":"DOCUMENTED — arsenical dip named","documented_unk":"DOCUMENTED — dipping named, chem. unconfirmed",
      "highly":"HIGHLY PROBABLE","likely":"LIKELY","plausible":"PLAUSIBLE"}
# num, community (what you see), ranch, tier, lat, lon
C=[
 (1,"Coto de Caza / Trabuco","Joplin ranch · Trabuco Cyn","documented",33.600,-117.588),
 (2,"San Juan Capistrano","San Juan Capistrano","documented",33.501,-117.662),
 (3,"Yorba Linda","Yorba · Santa Ana Cyn","documented",33.888,-117.813),
 (4,"Anaheim Hills","Bixby ranch · Santa Ana Cyn","documented",33.856,-117.760),
 (5,"LONG BEACH (Los Cerritos)","Rancho Los Cerritos","documented_unk",33.817,-118.188),
 (6,"Irvine","Irvine Ranch","highly",33.685,-117.790),
 (7,"Ladera Ranch","Rancho Mission Viejo / La Paz","highly",33.548,-117.635),
 (8,"Camp Pendleton (federal)","Santa Margarita y Las Flores","highly",33.300,-117.350),
 (9,"Simi Valley","Rancho Simi","likely",34.270,-118.750),
 (10,"Fillmore","Rancho Sespe","likely",34.399,-118.918),
 (11,"Rancho Santa Fe / Del Mar","Rancho San Dieguito","likely",33.010,-117.200),
 (12,"Rancho Bernardo","Rancho San Bernardo","likely",33.020,-117.075),
 (13,"Rancho Peñasquitos","Rancho Peñasquitos","likely",32.955,-117.100),
 (14,"Long Beach / Los Alamitos","Rancho Los Alamitos","plausible",33.786,-118.070),
 (15,"Rancho Cucamonga","Rancho Cucamonga","plausible",34.110,-117.575),
 (16,"Jurupa Valley","Rancho Jurupa","plausible",33.995,-117.450),
 (17,"Valencia / Santa Clarita","Rancho San Francisco / Newhall","plausible",34.430,-118.560),
 (18,"Lebec (Tejon, unbuilt)","Tejon Ranch","plausible",34.840,-118.870),
 (19,"Los Baños (farmland)","Miller & Lux","plausible",37.060,-120.850),
]
def F(sz,b=True):
    p="/System/Library/Fonts/Supplemental/Arial Bold.ttf" if b else "/System/Library/Fonts/Supplemental/Arial.ttf"
    try: return ImageFont.truetype(p,sz)
    except: return ImageFont.load_default()
def sat(lat,lon,half_km=0.9,px=760):
    dlat=half_km/111.0; dlon=half_km/(111.0*math.cos(math.radians(lat)))
    bbox=f"{lon-dlon},{lat-dlat},{lon+dlon},{lat+dlat}"
    u=ESRI+"?"+urllib.parse.urlencode({"bbox":bbox,"bboxSR":"4326","imageSR":"3857",
        "size":f"{px},{px}","format":"jpg","f":"image"})
    try:
        return Image.open(io.BytesIO(urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=60).read())).convert("RGB")
    except Exception as e:
        print("tile err",lat,lon,e); return Image.new("RGB",(px,px),(40,40,40))

TS=620; BAR=78; COLS=4; PADX=14; PADY=14
HEAD=150; FOOT=92
ROWS=math.ceil(len(C)/COLS)
W=COLS*TS+(COLS+1)*PADX
Hh=HEAD+ROWS*(TS+BAR)+(ROWS+1)*PADY+FOOT
atlas=Image.new("RGB",(W,Hh),(18,20,26)); dr=ImageDraw.Draw(atlas)
dr.text((30,26),"Satellite atlas — communities under the dipping-probability zones",font=F(38),fill=(240,238,232))
dr.text((32,80),"real satellite imagery of each community, tagged with its graded zone. A PROBABILITY of the dipping practice — NOT contamination.",font=F(21,False),fill=(224,150,110))
for i,(num,comm,ranch,tier,lat,lon) in enumerate(C):
    r,c=divmod(i,COLS)
    x=PADX+c*(TS+PADX); y=HEAD+PADY+r*(TS+BAR+PADY)
    tile=sat(lat,lon).resize((TS,TS))
    atlas.paste(tile,(x,y))
    col=TIER[tier]
    dr.rectangle([x,y,x+TS,y+TS],outline=col,width=6)                 # tier border
    dr.rectangle([x,y+TS,x+TS,y+TS+BAR],fill=col)                     # label bar
    # number badge
    dr.ellipse([x+10,y+TS+14,x+10+50,y+TS+64],fill=(255,255,255))
    dr.text((x+35,y+TS+39),str(num),font=F(26),fill=col,anchor="mm")
    dr.text((x+74,y+TS+22),comm,font=F(23),fill=(255,255,255),anchor="lm")
    dr.text((x+74,y+TS+52),f"{ranch}  ·  {TLAB[tier]}",font=F(15,False),fill=(255,255,255),anchor="lm")
    print("placed",num,comm)
# footer / legend
dr.rectangle([0,Hh-FOOT,W,Hh],fill=(28,24,20))
lx=30; ly=Hh-FOOT+16
for tier in ["documented","documented_unk","highly","likely","plausible"]:
    dr.rectangle([lx,ly,lx+26,ly+22],fill=TIER[tier]); dr.text((lx+34,ly+11),TLAB[tier],font=F(15,False),fill=(224,220,212),anchor="lm")
    lx+= 40+ dr.textlength(TLAB[tier],font=F(15,False)) +26
dr.text((30,Hh-40),"GRADED INFERENCE, not measurement. NOT a contamination map · NOT vat locations · practice != residue != exposure · no soil tested anywhere. Imagery: Esri World Imagery (Maxar et al.).",font=F(15,False),fill=(150,140,124))
atlas.save(os.path.join(OUT,"CA_dipping_satellite_atlas.jpg"),quality=88)
print("wrote",os.path.join(OUT,"CA_dipping_satellite_atlas.jpg"),atlas.size)
