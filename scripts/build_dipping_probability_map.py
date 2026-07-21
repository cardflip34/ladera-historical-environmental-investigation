#!/usr/bin/env python3
"""California — graded PROBABILITY that arsenical cattle-dipping occurred on/near a ranch (1907-1915),
with the modern community there today.

This ranks the probability of the PRACTICE, from DOCUMENTED (a source names dipping) down through
HIGHLY PROBABLE / LIKELY / PLAUSIBLE (inference from quarantine-county intensity + documented cattle
operations). It is NOT a contamination map (no soil tested anywhere), NOT a map of vat locations
(unknown), and the practice occurring does NOT imply residue, exposure, or harm. The disclaimer is
burned into the image.
"""
import json, math, os
from PIL import Image, ImageDraw, ImageFont
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CA=json.load(open(os.path.join(ROOT,"data/geospatial/ca/ca_counties.geojson")))
OUT=os.path.join(ROOT,"research/statewide"); os.makedirs(OUT,exist_ok=True)

HEAVY={"San Luis Obispo","Santa Barbara","San Diego","Orange","Fresno","Ventura"}
LESSER={"Tulare","Kern","Kings","Los Angeles","Riverside","San Bernardino","Madera"}
BG=(247,244,239); INK=(24,30,40); INK2=(74,86,102); LINE=(198,190,176)
C_HEAVY=(232,214,196); C_LESS=(240,232,220); C_OTHER=(250,247,242)
# tier styles: color, radius, shape
TIER={
 "documented":      ((150,42,40),   16,"diamond"),   # arsenical dip named in the record (FACT)
 "documented_unk":  ((176,120,30),  16,"diamond"),   # dipping named, chemistry unconfirmed
 "highly":          ((205,96,42),   15,"circle"),
 "likely":          ((214,150,74),  13,"circle"),
 "plausible":       ((201,182,140), 11,"circle"),
}
# num, name, community label, prob_tier, not_under_housing, lat, lon  (numbered; keyed to side table)
R=[
 (1,"Joplin ranch · Trabuco Canyon","Coto de Caza / Trabuco","documented",False,33.66,-117.585),
 (2,"San Juan Capistrano","San Juan Capistrano","documented",False,33.501,-117.662),
 (3,"Yorba","Yorba Linda / Santa Ana Cyn","documented",False,33.885,-117.79),
 (4,"Bixby ranch · Santa Ana Canyon","Anaheim Hills area","documented",False,33.855,-117.75),
 (5,"Rancho Los Cerritos","LONG BEACH / Lakewood","documented_unk",False,33.815,-118.155),
 (6,"Irvine Ranch","Irvine / Tustin / Newport","highly",False,33.685,-117.79),
 (7,"Rancho Mission Viejo / La Paz","Ladera Ranch / RSM","highly",False,33.55,-117.64),
 (8,"Santa Margarita y Las Flores","Camp Pendleton (federal)","highly",True,33.30,-117.35),
 (9,"Rancho Simi","Simi Valley","likely",False,34.27,-118.78),
 (10,"Rancho Sespe","Fillmore","likely",False,34.40,-118.87),
 (11,"Rancho San Dieguito","Rancho Santa Fe / Del Mar","likely",False,33.01,-117.20),
 (12,"Rancho San Bernardo","Rancho Bernardo","likely",False,33.02,-117.07),
 (13,"Rancho Peñasquitos","Mira Mesa / Carmel Valley","likely",False,32.93,-117.10),
 (14,"Rancho Los Alamitos","Long Beach / Los Alamitos","plausible",False,33.785,-118.07),
 (15,"Rancho Cucamonga","Rancho Cucamonga","plausible",False,34.11,-117.59),
 (16,"Rancho Jurupa","Riverside / Jurupa Valley","plausible",False,33.99,-117.42),
 (17,"Rancho San Francisco / Newhall","Santa Clarita / Valencia","plausible",False,34.41,-118.55),
 (18,"Tejon Ranch","Lebec (largely unbuilt)","plausible",True,34.96,-118.75),
 (19,"Miller & Lux","Los Baños (farmland)","plausible",True,37.02,-120.72),
]
W,H=1680,1950; K=math.cos(math.radians(34.5))
# crop window: SoCal + southern Central Valley
WLON,ELON,SLAT,NLAT=-121.7,-116.5,32.35,37.35
def polys(f):
    g=f["geometry"]; return [g["coordinates"]] if g["type"]=="Polygon" else g["coordinates"]
minx,maxx=WLON*K,ELON*K; miny,maxy=SLAT,NLAT; mar=70
s=min((W-2*mar)/(maxx-minx),(H-2*mar)/(maxy-miny))
offx=(W-(maxx-minx)*s)/2; offy=(H-(maxy-miny)*s)/2
def px(lo,la): return (offx+(lo*K-minx)*s, offy+(maxy-la)*s)
im=Image.new("RGB",(W,H),BG); dr=ImageDraw.Draw(im,"RGBA")
def col(n): return C_HEAVY if n in HEAVY else C_LESS if n in LESSER else C_OTHER
for f in CA["features"]:
    n=f["properties"]["name"]
    for poly in polys(f):
        for ring in poly:
            pts=[px(lo,la) for lo,la in ring]
            dr.polygon(pts, fill=col(n), outline=LINE)
def F(sz,b=True):
    p="/System/Library/Fonts/Supplemental/Arial Bold.ttf" if b else "/System/Library/Fonts/Supplemental/Arial.ttf"
    try: return ImageFont.truetype(p,sz)
    except: return ImageFont.load_default()
def marker(x,y,num,tier,nothousing,rad=None):
    c,r,shape=TIER[tier]
    if rad: r=rad
    if nothousing: dr.ellipse([x-r-5,y-r-5,x+r+5,y+r+5],outline=(70,130,80),width=3)
    if shape=="diamond": dr.polygon([(x,y-r),(x+r,y),(x,y+r),(x-r,y)],fill=c,outline=(255,255,255),width=2)
    else: dr.ellipse([x-r,y-r,x+r,y+r],fill=c,outline=(255,255,255),width=2)
    dr.text((x,y),str(num),font=F(15),fill=(255,255,255),anchor="mm")
for num,name,comm,tier,nh,lat,lon in R:
    x,y=px(lon,lat); marker(x,y,num,tier,nh)

# title
dr.rectangle([0,0,W,132],fill=(255,255,255,230))
dr.text((36,24),"California: where arsenical cattle-dipping most probably occurred, 1907–1915",font=F(33),fill=INK)
dr.text((38,72),"a GRADED PROBABILITY of the dipping PRACTICE — with the community there today. NOT a contamination map.",font=F(21,False),fill=(150,70,40))

# keyed side table (over the empty ocean/left area)
TL={"documented":"DOCUMENTED — arsenical dip named (fact)",
 "documented_unk":"DOCUMENTED — dipping named, chemistry unconfirmed",
 "highly":"HIGHLY PROBABLE — big cattle op, heavy quarantine county",
 "likely":"LIKELY — cattle range, heavy quarantine county",
 "plausible":"PLAUSIBLE — lesser county / competing crop-arsenic vector"}
tx,ty,tw,th=40,232,742,1034
dr.rectangle([tx,ty,tx+tw,ty+th],fill=(255,255,255,238),outline=LINE)
yy=ty+18; last=None
for num,name,comm,tier,nh,lat,lon in R:
    if tier!=last:
        yy+=14; dr.text((tx+16,yy),TL[tier],font=F(17),fill=(120,60,40),anchor="lm"); yy+=30; last=tier
    bx=tx+32; marker(bx,yy,num,tier,nh,rad=12)
    dr.text((tx+58,yy-9),name,font=F(18),fill=INK,anchor="lm")
    dr.text((tx+58,yy+9),comm,font=F(15,False),fill=INK2,anchor="lm")
    yy+=40
dr.text((tx+16,ty+th-20),"green ring = land now federal/farm/unbuilt · county shading: darker = 'heavily infested' quarantine county (USDA 1911)",font=F(13,False),fill=INK2)
# disclaimer band
dr.rectangle([0,H-92,W,H],fill=(238,232,222,255))
for i,t in enumerate([
 "GRADED INFERENCE, not measurement. Only the DOCUMENTED tier is a fact; the rest rank the PROBABILITY the practice occurred, from mandatory-dipping",
 "quarantine intensity + documented cattle operations. This is NOT a contamination map (no soil tested anywhere), NOT a map of vat locations (unknown),",
 "and the practice occurring does NOT imply residue, exposure, or harm. Communities are shown as land-use history; nothing here asserts anything about them."]):
    dr.text((36,H-78+i*26),t,font=F(16,False),fill=(90,74,54),anchor="lm")
im.save(os.path.join(OUT,"CA_dipping_probability_map.jpg"),quality=92)
print("wrote",os.path.join(OUT,"CA_dipping_probability_map.jpg"),im.size,"·",len(R),"ranches")
