#!/bin/bash
# Final edit: correct-aspect Andy (1920x1080), split layouts for talking-only parts, 16:9 window elsewhere.
set -e
cd "$(dirname "$0")"
P2=../p2; SEG=$P2/seg; TK=../../tasks
until grep -q REEL_DONE $TK/*.output 2>/dev/null && grep -q POND2_OK $P2/log_pp2.txt && grep -q TRCL_OK $P2/log_cl.txt && grep -q INTRO_THREAT_OK $P2/log_pt.txt && grep -q FL_OK $P2/log_pf.txt && grep -q OPEN_OK $P2/log_po.txt && grep -q POND_OK $P2/log_pp.txt; do sleep 5; done
( cd $P2 && python3 assemble.py uk Ladera_Phase2_FULL --full --open --rebuild 2>&1 | grep -E 'total|wrote' && cp Ladera_Phase2_FULL.mp4 ~/Desktop/Ladera_Phase2_FULL.mp4 )
VOPT="-c:v libx264 -preset fast -crf 18 -pix_fmt yuv420p -r 24 -video_track_timescale 12288"; AOPT="-c:a aac -b:a 192k -ar 48000 -ac 2"
cut(){ ffmpeg -y -loglevel error -ss $3 -to $4 -i $2 -af "afade=t=in:d=0.04,afade=t=out:st=$(python3 -c "print($4-$3-0.05)"):d=0.05" $VOPT $AOPT $1; }
cut r_1a.mp4 land_5555.mp4 1.30 47.40; cut r_1b.mp4 land_5555.mp4 51.25 60.35; cut r_1c.mp4 land_5555.mp4 71.35 74.80; cut r_2.mp4 land_5555.mp4 75.05 129.05
cut r_3a.mp4 land_5555.mp4 143.20 157.55; cut r_3b.mp4 land_5555.mp4 402.05 407.90; cut r_4a.mp4 land_5555.mp4 357.85 382.15; cut r_4b.mp4 land_5555.mp4 455.40 466.80
cut r_pond.mp4 land_5596.mp4 0.45 77.10; cut r_close.mp4 land_5641.mp4 1.60 98.40
join(){ out=$1; shift; : > l_$out.txt; for f in "$@"; do echo "file '$f'" >> l_$out.txt; done; ffmpeg -y -loglevel error -f concat -safe 0 -i l_$out.txt -c copy $out; }
join S1full.mp4 r_1a.mp4; join S1pip.mp4 r_1b.mp4 r_1c.mp4; join S2.mp4 r_2.mp4; join S3.mp4 r_3a.mp4 r_3b.mp4; join S4.mp4 r_4a.mp4 r_4b.mp4
# 16:9 window, lower-left: 560x315 + amber border
WIN='[1:v]scale=700:-2[p];[0:v][p]overlay=main_w-overlay_w:main_h-overlay_h:shortest=1[v]'
# split layout: top panel image (1080x1312) + Andy 1080x608 at y=1312
split(){ ffmpeg -y -loglevel error -loop 1 -i $2 -i $3 -filter_complex "[0:v]scale=1080:1312[t];[1:v]scale=1080:608[a];[t][a]vstack=inputs=2,format=yuv420p[v]" -map "[v]" -map 1:a $VOPT $AOPT -shortest $1; }
ffmpeg -y -loglevel error -loop 1 -i $P2/cover_9x16.jpg -f lavfi -i anullsrc=r=48000:cl=stereo -t 3 -vf "format=yuv420p,fade=t=out:st=2.5:d=0.5" $VOPT $AOPT -shortest A1.mp4
split A2.mp4 $P2/top_intro.png S1full.mp4
ffmpeg -y -loglevel error -i $SEG/pip_intro.mp4 -i S1pip.mp4 -filter_complex "$WIN" -map "[v]" -map 1:a $VOPT $AOPT A3.mp4
ffmpeg -y -loglevel error -ss 4 -to 33.3 -i $SEG/pip_open.mp4 -i S2.mp4 -filter_complex "[0:v]tpad=stop_mode=clone:stop_duration=26.8[bg];[1:v]scale=700:-2[p];[bg][p]overlay=main_w-overlay_w:main_h-overlay_h:shortest=1[v]" -map "[v]" -map 1:a $VOPT $AOPT B.mp4
ffmpeg -y -loglevel error -i $SEG/user.mp4 -i $SEG/user_audio.m4a -map 0:v -map 1:a $VOPT $AOPT -shortest C.mp4
ffmpeg -y -loglevel error -i $SEG/pip_threat.mp4 -i S3.mp4 -filter_complex "$WIN" -map "[v]" -map 1:a $VOPT $AOPT D.mp4
ffmpeg -y -loglevel error -i $SEG/pip_fl.mp4 -i S4.mp4 -filter_complex "$WIN" -map "[v]" -map 1:a $VOPT $AOPT E.mp4
printf "file 'A1.mp4'\nfile 'A2.mp4'\nfile 'A3.mp4'\nfile 'B.mp4'\nfile 'C.mp4'\nfile 'D.mp4'\nfile 'E.mp4'\n" > lAE.txt
ffmpeg -y -loglevel error -f concat -safe 0 -i lAE.txt -c copy AE_raw.mp4
music(){ T=$(ffmpeg -i $1 2>&1 | grep -oE "Duration: [0-9:.]+" | awk -F'[: ]' '{print $3*3600+$4*60+$5}'); ffmpeg -y -loglevel error -i $1 -i bed.m4a -filter_complex "[0:a]loudnorm=I=-16:TP=-1.5:LRA=11[voice];[1:a]volume=0.13,atrim=0:$T,afade=t=in:d=2,afade=t=out:st=$(python3 -c "print(max(0,$T-4))"):d=4[bed];[voice][bed]amix=inputs=2:normalize=0:duration=first[a]" -map 0:v -map "[a]" -c:v copy $AOPT $2; }
music AE_raw.mp4 AE.mp4
# F1: reel .. up to pond start ; H: trail .. P3 cut (British 'community.' at +47.33 s + 0.8 offset)
RS=$(python3 -c "import json;print(json.load(open('$P2/starts_full.json'))['starts']['REEL'])"); PD0=$(python3 -c "import json;print(json.load(open('$P2/starts_full.json'))['starts']['PD'])")
ffmpeg -y -loglevel error -ss $RS -to $PD0 -i $P2/Ladera_Phase2_FULL.mp4 -af "afade=t=out:st=$(python3 -c "print($PD0-$RS-0.8)"):d=0.8" $VOPT $AOPT F1.mp4
ffmpeg -y -loglevel error -i $SEG/pip_pond2.mp4 -i r_pond.mp4 -filter_complex "$WIN" -map "[v]" -map 1:a $VOPT $AOPT G_raw.mp4
music G_raw.mp4 G.mp4
PD=$(python3 -c "import json;print(json.load(open('$P2/starts_full.json'))['starts']['PD'])"); TR=$(python3 -c "import json;print(json.load(open('$P2/starts_full.json'))['starts']['TR'])"); P3=$(python3 -c "import json;print(json.load(open('$P2/starts_full.json'))['starts']['P3'])")
HL=$(python3 -c "print($P3+48.9-$TR)")
ffmpeg -y -loglevel error -ss $TR -i $P2/Ladera_Phase2_FULL.mp4 -t $HL -af "afade=t=out:st=$(python3 -c "print($HL-0.7)"):d=0.6" -vf "fade=t=out:st=$(python3 -c "print($HL-0.6)"):d=0.5" $VOPT $AOPT H.mp4
# I: closing split with music ; J: black + closing card + block 6 + music swell
split I_raw.mp4 $P2/top_close.png r_close_fixed.mp4
music I_raw.mp4 I.mp4
ffmpeg -y -loglevel error -f lavfi -i color=c=black:s=1080x1920:r=24 -f lavfi -i anullsrc=r=48000:cl=stereo -t 0.6 $VOPT $AOPT J0.mp4
ffmpeg -y -loglevel error -i $SEG/close.mp4 -i ../p2src/uk_6.mp3 -i bed.m4a -filter_complex "[1:a]adelay=800|800,volume=1.3[n];[2:a]volume=0.18,atrim=0:16,afade=t=in:d=1.5,afade=t=out:st=12:d=4[b];[n][b]amix=inputs=2:normalize=0:duration=longest,apad=whole_dur=16[a]" -map 0:v -map "[a]" -t 16 $VOPT $AOPT J1.mp4
printf "file 'AE.mp4'\nfile 'F1.mp4'\nfile 'G.mp4'\nfile 'H.mp4'\nfile 'I.mp4'\nfile 'J0.mp4'\nfile 'J1.mp4'\n" > lfin.txt
ffmpeg -y -loglevel error -f concat -safe 0 -i lfin.txt -c copy -movflags +faststart Ladera_Phase2_FINAL.mp4
ffmpeg -i Ladera_Phase2_FINAL.mp4 2>&1 | grep -oE "Duration: [0-9:.]+"
cp Ladera_Phase2_FINAL.mp4 ~/Desktop/Ladera_Phase2_FINAL.mp4
echo FINAL_DONE
