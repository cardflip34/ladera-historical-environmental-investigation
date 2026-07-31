#!/usr/bin/env python3
"""
Sampling-target map: where to look for a ranch-era arsenic signature, and why.

The distribution model says the signature - if there is one - is a POINT anomaly at places where
cattle concentrated, not a smear across pasture. So the useful map is not "here is Ladera Ranch",
it is "here are the specific places worth putting a hole in the ground, ranked".

THE TARGETING LOGIC, in order of strength:

  1. WATER. Cattle congregate at water, every day, in numbers. That is where dung concentrates,
     where hoof traffic concentrates, and where wet animals stood. The 1968 USGS field survey
     mapped 23 surface-water bodies inside this AOI - that layer is effectively a map of where
     cattle gathered on this ground, and it is the single best targeting layer we hold.
  2. WATER + DRAINAGE TOGETHER. A water body sitting on or beside the drainage line is both a
     congregation point AND a depositional trap. Highest priority.
  3. THE DRAINAGE ITSELF. Low-gradient and confluence reaches accumulate fine sediment, and
     anything bound to it.
  4. THE 1948 RANCH NODE. The one documented structure in the AOI. Explicitly NOT identified as
     a dip vat by the prior imagery audit - plotted because it is a known human-activity point,
     not because it is a candidate vat.

NOT MARKED ON THIS MAP: any vat. None has been located. Marking a guess would be fabrication.

Output: sampling_target_map.png
"""
from __future__ import annotations
import json, os, math, datetime
import numpy as np
from PIL import Image, ImageDraw, ImageFont
Image.MAX_IMAGE_PIXELS = None

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
M7 = os.path.join(REPO, "evidence/lhdrs/mission7")
TODAY = datetime.date.today().isoformat()
AOI = (-117.670, 33.524, -117.616, 33.575)

W, H = 1500, 2320
MAP_T, MAP_H = 250, 1420
MAP_L = 60
MAP_W = W - 2*MAP_L

FD = "/System/Library/Fonts/Supplemental/"
def F(s, b=False):
    p = FD + ("Arial Bold" if b else "Arial") + ".ttf"
    return ImageFont.truetype(p, s) if os.path.exists(p) else ImageFont.load_default()

INK=(18,26,40); PAPER=(252,251,249); MUT=(120,126,138); LINE=(214,218,226)
STREAM=(56,132,214); WATER=(0,190,220); HOT=(214,64,48); WARM=(232,148,40)
SCHOOL=(196,148,20); PARKC=(70,150,95)

# ---- geometry --------------------------------------------------------------
def latm(): return math.radians((AOI[1]+AOI[3])/2)
gw = (AOI[2]-AOI[0])*math.cos(latm()); gh = AOI[3]-AOI[1]
sc = min(MAP_W/gw, MAP_H/gh)
PW, PH = gw*sc, gh*sc
OX = MAP_L + (MAP_W-PW)/2
OY = MAP_T + (MAP_H-PH)/2
def xy(lon, lat):
    return (OX + (lon-AOI[0])*math.cos(latm())*sc, OY + (AOI[3]-lat)*sc)

im = Image.new("RGB", (W, H), PAPER)
# basemap: newest county imagery held - Eagle Aerial 2025 1-ft - falling back to 2004 if absent
p = os.path.join(M7, "oc_2025_aoi.jpg")
if not os.path.exists(p):
    p = os.path.join(M7, "hro_2004_aoi.png")
if os.path.exists(p):
    base = Image.open(p).convert("RGB").resize((int(PW), int(PH)), Image.LANCZOS)
    a = np.asarray(base).astype(float)
    g = a.mean(axis=2, keepdims=True)
    a = (g*0.72 + a*0.28)*0.55 + 255*0.45          # desaturate + lighten
    base = Image.fromarray(np.clip(a,0,255).astype("uint8"))
    im.paste(base, (int(OX), int(OY)))
d = ImageDraw.Draw(im)
d.rectangle([OX, OY, OX+PW, OY+PH], outline=LINE, width=1)

# ---- drainage --------------------------------------------------------------
def chan():
    fp = os.path.join(M7, "oc_flood_channels_aoi.geojson")
    out = {}
    if not os.path.exists(fp): return out
    for f in json.load(open(fp))["features"]:
        nm = ((f.get("properties") or {}).get("FACILITYNAME") or "").strip().upper()
        g = f.get("geometry")
        if not nm or not g: continue
        parts = [g["coordinates"]] if g["type"]=="LineString" else g["coordinates"]
        out.setdefault(nm, []).extend(parts)
    return out
CH = chan()
def clip(pt): return OX-2 <= pt[0] <= OX+PW+2 and OY-2 <= pt[1] <= OY+PH+2
for nm, col, wd in (("TRABUCO CREEK CHANNEL",(120,170,210),3),
                    ("CANADA CHIQUITA",(120,170,210),3),
                    ("OSO CREEK CHANNEL",(120,170,210),3),
                    ("ACJACHEMA STORM DRAIN",(90,170,225),5),
                    ("HORNO CREEK CHANNEL",STREAM,6)):
    for seg in CH.get(nm, []):
        pts=[xy(c[0],c[1]) for c in seg]
        for a_,b_ in zip(pts,pts[1:]):
            if clip(a_) and clip(b_): d.line([a_,b_], fill=col, width=wd)

# ---- 1968 water bodies = where cattle gathered ------------------------------
water = json.load(open(os.path.join(REPO,"research/historical_imagery/topo1968_water.json")))
targets=[]
def near_drainage(lon,lat,limit_m=150):
    best=1e9
    for nm in ("HORNO CREEK CHANNEL","ACJACHEMA STORM DRAIN","CANADA CHIQUITA","TRABUCO CREEK CHANNEL"):
        for seg in CH.get(nm,[]):
            for c in seg:
                dd=math.hypot((c[0]-lon)*92500,(c[1]-lat)*111000)
                if dd<best: best=dd
    return best
for w in water:
    x,y = xy(w["lon"], w["lat"])
    if not (OX<=x<=OX+PW and OY<=y<=OY+PH): continue
    dist = near_drainage(w["lon"], w["lat"])
    pri = 1 if dist<=150 else 2
    targets.append({"lon":w["lon"],"lat":w["lat"],"areaM2":w.get("area_m2"),
                    "metresToDrainage":round(dist),"priority":pri})
    r = max(9, min(26, int(math.sqrt(w.get("area_m2",300))/8)))
    col = HOT if pri==1 else WARM
    d.ellipse([x-r,y-r,x+r,y+r], outline=col, width=4)
    d.ellipse([x-3,y-3,x+3,y+3], fill=col)

# ---- orchard blocks (the confounder), so the map shows where they are NOT --
_os = os.path.join(REPO, "evidence/lhdrs/orchards/orchard_summary.json")
if os.path.exists(_os):
    for b in json.load(open(_os))["blockSummary"]:
        la, lo = b["centroid"]
        x, y = xy(lo, la)
        if OX <= x <= OX+PW and OY <= y <= OY+PH:
            r = max(8, min(20, int(math.sqrt(b["areaHa"]*10000)/25)))
            d.rectangle([x-r, y-r, x+r, y+r], outline=PARKC, width=3)

# ---- the 1948 ranch node ---------------------------------------------------
nx,ny = xy(-117.65492, 33.55505)
d.ellipse([nx-16,ny-16,nx+16,ny+16], outline=(150,60,180), width=4)
d.line([nx-24,ny,nx+24,ny], fill=(150,60,180), width=3)
d.line([nx,ny-24,nx,ny+24], fill=(150,60,180), width=3)

# ---- schools, for exposure context only ------------------------------------
sch = json.load(open(os.path.join(REPO,"data/development/schools.geojson")))["features"]
seen=set()
for s in sch:
    c=s["geometry"]["coordinates"]
    if tuple(c) in seen: continue
    seen.add(tuple(c))
    x,y=xy(c[0],c[1])
    if not (OX<=x<=OX+PW and OY<=y<=OY+PH): continue
    d.rectangle([x-8,y-8,x+8,y+8], outline=SCHOOL, width=3)

# ---- title -----------------------------------------------------------------
d.rectangle([0,0,W,10], fill=HOT)
d.text((MAP_L, 44), "Where to sample for a ranch-era arsenic signature", font=F(42,True), fill=INK)
d.text((MAP_L, 100), "Ladera Ranch · targets ranked by where cattle concentrated, not by where a vat is assumed to be",
       font=F(20), fill=MUT)
d.rounded_rectangle([MAP_L,140,MAP_L+300,176], 6, fill=(150,60,42))
d.text((MAP_L+14,147), "NO VAT HAS BEEN LOCATED", font=F(17,True), fill=(255,255,255))
d.text((MAP_L+320,147), "Nothing on this map marks a vat. Marking a guess would be fabrication.",
       font=F(18), fill=MUT)
d.text((MAP_L, 200), "Basemap: OC Survey Eagle Aerial 2025, 1 ft countywide · desaturated",
       font=F(16), fill=MUT)

# ---- legend ----------------------------------------------------------------
ly = MAP_T + MAP_H + 34
d.line([MAP_L, ly-14, W-MAP_L, ly-14], fill=LINE)
p1 = sum(1 for t in targets if t["priority"]==1)
p2 = sum(1 for t in targets if t["priority"]==2)
rows = [
 (HOT,   "circle", f"PRIORITY 1 — {p1} sites: 1968 water body within 150 m of the drainage.",
                   "Cattle congregation point AND a depositional trap. Sample these first."),
 (WARM,  "circle", f"PRIORITY 2 — {p2} sites: 1968 water body away from the drainage.",
                   "Congregation point only. Still a strong target."),
 (STREAM,"line",   "Horno Creek · Acjachema Storm Drain · Cañada Chiquita / Trabuco / Oso",
                   "Low-gradient and confluence reaches accumulate fine sediment."),
 ((150,60,180),"cross","1948 ranch structure — the one documented feature in the frame.",
                   "Explicitly NOT identified as a dip vat by the prior imagery audit."),
 (SCHOOL,"square", "Schools — shown for exposure context only.",
                   "Their presence is not evidence of anything being present."),
 (PARKC, "square", "Orchard blocks detected 1929–1947 — the lead-arsenate confounder.",
                   "All in the far south-west. Nearest block to any school: 2.8 km. To the drainage: 1.4 km."),
]
for col, shape, t1, t2 in rows:
    cx = MAP_L+16
    if shape=="circle": d.ellipse([cx-11,ly-11,cx+11,ly+11], outline=col, width=4)
    elif shape=="line": d.line([cx-14,ly,cx+14,ly], fill=col, width=6)
    elif shape=="cross":
        d.ellipse([cx-10,ly-10,cx+10,ly+10], outline=col, width=3)
        d.line([cx-15,ly,cx+15,ly], fill=col, width=2); d.line([cx,ly-15,cx,ly+15], fill=col, width=2)
    else: d.rectangle([cx-9,ly-9,cx+9,ly+9], outline=col, width=3)
    d.text((MAP_L+46, ly-16), t1, font=F(20,True), fill=INK)
    d.text((MAP_L+46, ly+8), t2, font=F(18), fill=MUT)
    ly += 62

d.line([MAP_L, ly-6, W-MAP_L, ly-6], fill=LINE)
d.text((MAP_L, ly+10), "Why water bodies are the targeting layer", font=F(22,True), fill=INK)
for i,t in enumerate([
  "A dipped animal drips for hours, then grazes for 14–21 days and excretes wherever it walks. The mass",
  "spreads — open range works out at essentially background. What does not spread is where cattle GATHERED:",
  "water, shade, salt and bedding ground. The 1968 USGS survey mapped 23 water bodies in this frame, and that",
  "layer is the closest thing we hold to a map of where cattle stood on this ground every single day.",
]):
    d.text((MAP_L, ly+44+i*26), t, font=F(19), fill=(60,66,78))

yy = ly+44+4*26+18
d.text((MAP_L, yy), "Model estimate · targets are reasoned, not measured · a single accredited soil result outweighs this entire map",
       font=F(17,True), fill=(150,60,42))
d.line([MAP_L, yy+40, W-MAP_L, yy+40], fill=LINE)
d.text((MAP_L, yy+56), f"LHDRS · generated {TODAY} · drainage A+ OC Flood_Channels · water bodies A1 USGS 1968 field survey",
       font=F(16), fill=MUT)

out = os.path.join(M7, "sampling_target_map.png")
im.save(out)
print("wrote", out)
targets.sort(key=lambda t:(t["priority"], t["metresToDrainage"]))
json.dump({"generated":TODAY,"statementClass":"model_estimate",
           "targetingLogic":"1968 surface-water bodies as a proxy for cattle congregation; "
                            "proximity to mapped drainage as a depositional-trap multiplier",
           "priority1Count":p1,"priority2Count":p2,"targets":targets,
           "notMarked":"No vat is marked. None has been located in the study area.",
           "supersededBy":"Any accredited laboratory soil or sediment measurement."},
          open(os.path.join(M7,"sampling_targets.json"),"w"), indent=1)
print(f"priority 1: {p1}   priority 2: {p2}")
