#!/usr/bin/env python3
"""Overlay a historical OC aerial on the current aerial at the identical extent.

Shows where old ranch features (water bodies, drainages, farmsteads, roads) sit under today's
neighborhoods. Land-use history only, at neighborhood scale — NOT addresses, NOT individuals, NOT a
contamination map.

Usage:
  python3 scripts/build_historical_overlay.py <lon> <lat> <half_ft> "Orange County 1938" <out_prefix>
Outputs <out_prefix>_overlay.jpg (3-panel: historic | blend | modern) and <out_prefix>_blend.jpg.
"""
import sys, json, urllib.parse, urllib.request, io
from pyproj import Transformer
from PIL import Image, ImageOps, ImageDraw, ImageFont

HIST="https://www.ocgis.com/arcpub/rest/services/Historic_Imagery/Historic_Imagery/ImageServer"
MODERN="https://www.ocgis.com/arcpub/rest/services/Aerial_Imagery_Countywide/OC_Aerial_2022_1ft_WGS84/ImageServer"
UA={"User-Agent":"Mozilla/5.0 (land-use history research)"}
def get(u): return urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=90).read()
def F(sz):
    try: return ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf",sz)
    except: return ImageFont.load_default()

def main():
    lon,lat,half,name,pref=float(sys.argv[1]),float(sys.argv[2]),float(sys.argv[3]),sys.argv[4],sys.argv[5]
    x,y=Transformer.from_crs(4326,2230,always_xy=True).transform(lon,lat)
    bbox=f"{x-half},{y-half},{x+half},{y+half}"
    # historic raster OBJECTID by name over the point
    q={"geometry":f"{x},{y}","geometryType":"esriGeometryPoint","inSR":"2230","spatialRel":"esriSpatialRelIntersects",
       "outFields":"OBJECTID,Name","returnGeometry":"false","f":"json"}
    feats=json.loads(get(HIST+"/query?"+urllib.parse.urlencode(q)))["features"]
    oid=[f["attributes"]["OBJECTID"] for f in feats if name.lower() in str(f["attributes"].get("Name","")).lower()][0]
    def export(base,extra=""):
        p={"bbox":bbox,"bboxSR":"2230","imageSR":"2230","size":"1400,1400","format":"jpg","f":"image"}
        return Image.open(io.BytesIO(get(base+"/exportImage?"+urllib.parse.urlencode(p)+extra)))
    hist=ImageOps.autocontrast(export(HIST,"&"+urllib.parse.urlencode(
        {"mosaicRule":json.dumps({"mosaicMethod":"esriMosaicLockRaster","lockRasterIds":[oid]})})).convert("L"),cutoff=0.5)
    modern=export(MODERN).convert("RGB").resize((1400,1400))
    hist_rgb=Image.merge("RGB",(hist,hist,hist))
    blend=Image.blend(modern,hist_rgb,0.5); blend.save(pref+"_blend.jpg","JPEG",quality=90)
    P=760;g=8;W=P*3+g*2;H=P+86;c=Image.new("RGB",(W,H),(12,16,23));dr=ImageDraw.Draw(c)
    for i,(im,lab,col) in enumerate([(hist_rgb,f"historic ({name})",(214,140,70)),
        (blend,"OVERLAY on today's streets",(200,169,81)),(modern,"current neighborhood",(121,195,232))]):
        c.paste(im.resize((P,P)),(i*(P+g),44)); dr.text((i*(P+g)+12,12),lab,font=F(21),fill=col)
    dr.text((12,H-32),"OC Survey historic + 2022 aerials, identical extent (EPSG:2230). Land-use history only; neighborhood scale; no addresses/individuals; no contamination implied.",font=F(16),fill=(150,168,184))
    c.save(pref+"_overlay.jpg","JPEG",quality=90); print("wrote",pref+"_overlay.jpg")

if __name__=="__main__": main()
