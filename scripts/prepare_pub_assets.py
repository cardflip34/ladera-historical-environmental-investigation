#!/usr/bin/env python3
"""Copy and optimise imagery into the publication asset tree, and write the image archive.

Full-resolution frames run to several megabytes each and there are 66 of them; serving those
directly would make the publication unusable on a phone. Each figure gets a web derivative
capped on the long edge, while the archive CSV records the original path so the full-resolution
file remains traceable from any figure.

Every entry carries date, repository, rights, and an interpretation boundary — an image without
provenance is not evidence, and this project does not publish images it cannot source.
"""
import csv
import os
import shutil

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "research", "historical_imagery")
DST = os.path.join(ROOT, "docs", "publication", "assets", "images")
ARCHIVE = os.path.join(ROOT, "docs", "publication", "data", "image-archive.csv")

OC = ("OC Survey Geospatial Services, County of Orange",
      "Public record, County of Orange. Retrieved from the county's public ArcGIS image service.")
USGS = ("U.S. Geological Survey",
        "Public domain (U.S. Government work).")
DERIVED = ("This investigation",
           "Derived figure. Underlying imagery credited in the caption; derived layout CC BY 4.0.")

# id, source relative path, date, repository, rights, caption title, interpretation boundary
FIGURES = [
    ("FIG-01", "11_timeseries_1929-2022_with_water.jpg", "1929-2022", *DERIVED,
     "The footprint across four epochs, with the 1968 water layer overprinted",
     "Panels share one extent and georeferencing. Cyan circles mark water bodies as drawn by the "
     "1968 USGS survey; they are centroids, not digitised outlines. The cyan box is an approximate "
     "screening boundary, not a legal boundary."),
    ("FIG-02", "oc_aerials/ann_1929.jpg", "1929", *OC,
     "1929 aerial photograph, South County Watersheds frame",
     "Twelve years after compulsory cattle dipping ended. Open rangeland; no structures resolvable "
     "inside Zone A. The dark wedge at upper left is outside the frame's coverage, not terrain."),
    ("FIG-03", "oc_aerials/ann_1937.jpg", "1937-1938", *OC,
     "1937-38 aerial photograph, 600-scale county series",
     "The sharpest frame available, at approximately 1.15 ft/px. Individual oaks, fence lines and "
     "wheel ruts are legible. No corral, pen or vat complex is resolvable inside Zone A."),
    ("FIG-04", "oc_aerials/ann_2022.jpg", "2022", *OC,
     "The same ground, built out",
     "Rendered to the identical extent as the historical frames. That Zone A lands on the real "
     "subdivisions is the independent check on georeferencing of the whole series."),
    ("FIG-05", "oc_aerials/z1_ranch_1937.jpg", "1937-1938", *OC,
     "The Trabuco Creek ranch node at 100 m scale, 1937-38",
     "Centred on 33.55505, -117.65492. The red ink label is the county cartographer's own and reads "
     "Trabuco Creek. A single structure at a trail convergence beside water is consistent with a "
     "ranch working area AND equally consistent with a line camp, barn or ranch house. It is NOT "
     "identified as a dip site."),
    ("FIG-06", "oc_aerials/z1_ranch_2022_modern.jpg", "2022", *OC,
     "The same location today",
     "For comparison with FIG-05 at identical extent and scale."),
    ("FIG-07", "03_topo_1968_footprint.jpg", "1968", *USGS,
     "USGS 7.5-minute San Juan Capistrano quadrangle, 1968 revision",
     "The source of the 41-body surface-water layer. Shows the impoundment chain down the Trabuco "
     "corridor, a labelled Water Tank, a Terminal Reservoir, a landing strip and a gaging station. "
     "The land grant is labelled MISSION VIEJO OR LA PAZ."),
    ("FIG-08", "01_topo_1948_footprint.jpg", "1948", *USGS,
     "USGS 7.5-minute San Juan Capistrano quadrangle, 1948 edition",
     "The earliest topographic sheet covering the footprint. Note that USGS symbology has no "
     "dipping-vat symbol, so absence of a vat on this sheet carries little evidential weight."),
    ("FIG-09", "04_aerial_1974_footprint.jpg", "1974", *USGS,
     "USGS orthophoto quadrangle, 1974",
     "Still open rangeland with dirt tracks and the riparian corridor. Mission Viejo's build-out is "
     "visible to the west."),
    ("FIG-10", "oc_aerials/tiles/1937_r1c1.jpg", "1937-1938", *OC,
     "One tile from the systematic survey grid",
     "Zone A was divided into a 4x3 grid and each tile examined at full resolution for both the 1929 "
     "and 1937-38 frames - 24 tiles in total. Each carries its own corner coordinates and a 200 m "
     "scale bar so any reader can return to the same ground. Pencil annotations are original survey "
     "marks on the county's working print."),
    ("FIG-11", "07_zoom_1948_ranch_structure_elev307.jpg", "1948", *USGS,
     "The ranch structure on the 1948 topographic sheet",
     "The single building inside the footprint, at a trail convergence near elevation 307. The map "
     "does not label it. Recorded as a ranch-activity node, not as a dip site."),
    ("FIG-12", "10_zoom_1948_south_false_positives.jpg", "1948", *USGS,
     "Why automated detection failed",
     "An automated detector returned 25 building-like candidates on the 1948 sheet. Visual review "
     "showed 24 were artifacts - letters from the MISSION VIEJO map label, red section-line dots, and "
     "a benchmark X. None of the rejected candidates is plotted anywhere in this publication."),
]

MAXPX = 1800


def main():
    os.makedirs(DST, exist_ok=True)
    os.makedirs(os.path.dirname(ARCHIVE), exist_ok=True)
    rows = []
    for fid, rel, date, repo, rights, title, boundary in FIGURES:
        src = os.path.join(SRC, rel)
        if not os.path.exists(src):
            print(f"  MISSING  {fid}  {rel}")
            continue
        out_name = f"{fid.lower()}.jpg"
        out_path = os.path.join(DST, out_name)
        im = Image.open(src).convert("RGB")
        ow, oh = im.size
        im.thumbnail((MAXPX, MAXPX), Image.LANCZOS)
        im.save(out_path, "JPEG", quality=84, optimize=True, progressive=True)
        kb = os.path.getsize(out_path) / 1024
        rows.append({
            "image_id": fid, "title": title, "date": date, "repository": repo,
            "rights": rights, "interpretation_boundary": boundary,
            "original_path": os.path.relpath(src, ROOT),
            "original_dimensions": f"{ow}x{oh}",
            "published_file": f"assets/images/{out_name}",
            "published_dimensions": f"{im.size[0]}x{im.size[1]}",
            "published_kb": f"{kb:.0f}",
            "confidence": "High - direct reproduction of source imagery",
        })
        print(f"  {fid}  {ow}x{oh} -> {im.size[0]}x{im.size[1]}  {kb:.0f} KB")

    with open(ARCHIVE, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    total = sum(float(r["published_kb"]) for r in rows)
    print(f"\n{len(rows)} figures, {total/1024:.1f} MB total")
    print(f"archive -> {os.path.relpath(ARCHIVE, ROOT)}")


if __name__ == "__main__":
    main()
