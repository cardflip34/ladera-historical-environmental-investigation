# Mission 4 reproducibility

Use a Python environment containing GeoPandas, Shapely, pyproj, Rasterio, NumPy, Pillow, pandas, and Matplotlib. Set `LHDRS_PYTHON` to that interpreter when it is not the system `python3`.

Core commands:

```sh
make lhdrs-mission4-ingest
make lhdrs-mission4 LHDRS_PYTHON=/path/to/gis-python
make lhdrs-mission4-publish LHDRS_PYTHON=/path/to/gis-python
make lhdrs-mission4-verify LHDRS_PYTHON=/path/to/gis-python
```

Fetch scripts archive service metadata and checksums. Build scripts write deterministic IDs and atomically replace derived tables. Raw County, DSA, NOAA, imagery, and terrain inputs remain under `evidence/lhdrs/`. The proximity build always applies its evidence gate before calculation.
