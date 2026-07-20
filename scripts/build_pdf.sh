#!/usr/bin/env bash
# Render the publication to print-quality PDF.
#
# Renders from file:// rather than through the dev server. An earlier version pointed Chrome at
# localhost, which silently produced a 1-page PDF when the dev server had died — the failure
# looked like a Chrome problem and was actually a dead port. file:// has no such dependency, and
# relative asset paths resolve correctly from docs/publication/.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC="$ROOT/docs/publication/index.html"
OUT="$ROOT/docs/publication/Ladera-Investigation-v1.0.pdf"

CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
[ -x "$CHROME" ] || CHROME="$(command -v chromium || command -v google-chrome || true)"
[ -n "$CHROME" ] || { echo "No Chrome/Chromium found" >&2; exit 1; }

[ -f "$SRC" ] || { echo "Build the publication first: python3 scripts/build_publication.py" >&2; exit 1; }

echo "Rendering $SRC ..."
"$CHROME" --headless --disable-gpu --no-sandbox --allow-file-access-from-files \
  --print-to-pdf="$OUT" --print-to-pdf-no-header --no-pdf-header-footer \
  --virtual-time-budget=90000 "file://$SRC" 2>/dev/null

python3 - "$OUT" <<'PY'
import sys
from pypdf import PdfReader
r = PdfReader(sys.argv[1])
blank = [i for i, p in enumerate(r.pages, 1) if not (p.extract_text() or "").strip()]
print(f"  {len(r.pages)} pages, {len(blank)} blank {blank if blank else ''}")
if len(r.pages) < 20:
    print("  FAIL: suspiciously short - check that index.html rendered fully")
    sys.exit(1)
if blank:
    print("  WARN: blank pages present")
PY
echo "  -> $OUT"
