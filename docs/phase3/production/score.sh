#!/bin/bash
set -e; cd "$(dirname "$0")"
BED=../p3/bed.m4a
SRC=out/voice.mp4
T=$(ffmpeg -i $SRC 2>&1 | grep -oE "Duration: [0-9:.]+" | head -1 | awk -F'[: ]' '{print $3*3600+$4*60+$5}')
echo "film length ${T}s"
ffmpeg -y -loglevel error -stream_loop 12 -i "$BED" -t $T -af "afade=t=in:d=3,afade=t=out:st=$(python3 -c "print(max(0,$T-6))"):d=6" -ar 48000 -ac 2 -c:a aac -b:a 192k out/music_full.m4a
ffmpeg -y -loglevel error -i $SRC -i out/music_full.m4a -filter_complex \
 "[0:a]asplit=2[v1][v2];[1:a]volume=0.16[m];[m][v2]sidechaincompress=threshold=0.02:ratio=6:attack=30:release=900:makeup=1[md];[v1][md]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.95[a]" \
 -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -movflags +faststart out/Ladera_Phase3_FINAL.mp4
ffmpeg -y -loglevel error -i out/Ladera_Phase3_FINAL.mp4 -filter_complex \
 "[0:v]split=2[a][b];[a]scale=1920:1080,boxblur=30:5,eq=brightness=-0.15[bg];[b]scale=-2:1080[fg];[bg][fg]overlay=(W-w)/2:0,format=yuv420p[v]" \
 -map "[v]" -map 0:a -c:v libx264 -preset fast -crf 18 -r 24 -c:a copy -movflags +faststart out/Ladera_Phase3_FINAL_16x9_YouTube.mp4
echo SCORE_DONE
