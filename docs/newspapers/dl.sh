#!/bin/bash
UA='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/131.0 Safari/537.36'
id="$1"
out="sar/${id}.txt"
[ -s "$out" ] && exit 0
curl -sL -A "$UA" --max-time 90 --retry 2 -o "$out" "https://archive.org/download/${id}/${id}_djvu.txt"
[ -s "$out" ] || rm -f "$out"
