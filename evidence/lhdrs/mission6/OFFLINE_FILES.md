# Mission 6 files kept on disk but excluded from git

Per this repository's existing >50MB convention (see root `.gitignore` and
`evidence/documents/OFFLINE_LARGE_FILES.md`), the following verified capture is present on disk
but excluded from the git push. This is a size exclusion, not an access or integrity limitation:
the file is checksum-verified and listed in `acquisition_manifest.csv` like every other source.

| File | Size | SHA-256 (first 16) | Source |
|---|---|---|---|
| `imagery/oc_historical_aerial_ladera_1998.tif` | 55.1 MB | see manifest | County of Orange historical aerial explorer |

The 1995 aerial (30.3 MB) is committed normally.
