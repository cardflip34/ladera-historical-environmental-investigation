#!/bin/bash
set -e
cd "$(dirname "$0")"
REEL=../vat3d/fal/Dipping_Station_Reel_9x16.mp4
dur(){ ffmpeg -i "$1" 2>&1 | grep -oE "Duration: [0-9:.]+" | awk -F'[: ]' '{print $3*3600+$4*60+$5}'; }
fadeit(){ L=$(dur $1); ST=$(python3 -c "print(max(0,$L-0.6))"); ffmpeg -y -loglevel error -i $1 -vf "fade=t=in:st=0:d=0.5,fade=t=out:st=$ST:d=0.6" -an -r 24 -c:v libx264 -crf 16 -pix_fmt yuv420p -video_track_timescale 12288 $2; }
fadeit seg0.mp4 f0.mp4; fadeit seg0b.mp4 f0b.mp4; fadeit explainer.mp4 fA.mp4; fadeit segB.mp4 fB.mp4; fadeit segC.mp4 fC.mp4; fadeit segD.mp4 fD.mp4; fadeit segE.mp4 fE.mp4
printf "file 'f0.mp4'\nfile 'f0b.mp4'\nfile 'fA.mp4'\nfile 'fB.mp4'\nfile 'fC.mp4'\nfile 'fD.mp4'\nfile 'fE.mp4'\n" > list.txt
ffmpeg -y -loglevel error -f concat -safe 0 -i list.txt -c copy video_only.mp4
T0=0; TA=$(python3 -c "print($(dur f0.mp4)+$(dur f0b.mp4))"); TB=$(python3 -c "print($TA+$(dur fA.mp4))"); TC=$(python3 -c "print($TB+$(dur fB.mp4))"); TD=$(python3 -c "print($TC+$(dur fC.mp4))"); TE=$(python3 -c "print($TD+$(dur fD.mp4))"); TOT=$(dur video_only.mp4)
echo "starts: A=$TA B=$TB C=$TC D=$TD E=$TE total=$TOT"
ms(){ python3 -c "print(int(($1+0.8)*1000))"; }
ffmpeg -y -loglevel error -i "$REEL" -i nar_1.mp3 -i nar_2.mp3 -i nar_3.mp3 -i nar_4.mp3 -i nar_5.mp3 -i nar_6.mp3 -i nar_1b.mp3 -filter_complex \
"[0:a]volume=0.32,afade=t=out:st=63:d=3,apad=whole_dur=$TOT[amb];\
[1:a]adelay=1200|1200[n1];[2:a]adelay=$(ms $TA)|$(ms $TA)[n2];[3:a]adelay=$(ms $TB)|$(ms $TB)[n3];\
[4:a]adelay=$(ms $TC)|$(ms $TC)[n4];[5:a]adelay=$(ms $TD)|$(ms $TD)[n5];[6:a]adelay=$(ms $TE)|$(ms $TE)[n6];[7:a]adelay=51700|51700[n7];\
[n1][n2][n3][n4][n5][n6][n7]amix=inputs=7:normalize=0,volume=1.4[nar];\
[amb][nar]amix=inputs=2:normalize=0,alimiter=limit=0.95,afade=t=out:st=$(python3 -c "print($TOT-2.5)"):d=2.5[aout]" -map "[aout]" -t $TOT -c:a aac -b:a 192k narration_mix.m4a
ffmpeg -y -loglevel error -i video_only.mp4 -i narration_mix.m4a -map 0:v -map 1:a -c:v copy -c:a copy -shortest -movflags +faststart Ladera_Phase2_Narrated.mp4
ffmpeg -i Ladera_Phase2_Narrated.mp4 2>&1 | grep -E "Duration"
