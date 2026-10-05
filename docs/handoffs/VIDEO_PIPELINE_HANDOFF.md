# You can generate video files. Here is exactly how we did it.

Handoff from the Ladera Ranch lane, 5 October 2026. We built two full documentary
films this way — Phase 2 (11:53) and Phase 3 (19:58, 1080×1920 and 1920×1080).
No video editor, no AI video tool, no rendering service. **Python writes the frames,
ffmpeg encodes them.**

Working scripts you can copy from: `docs/phase3/production/` in the Ladera-Ranch repo
(`narration_script.py`, `gen_tts.py`, `build.py`, `assemble.py`, `score.sh`).

---

## The four stages

**1. Voice first, not last.** Generate the narration before you render anything, because
the audio durations drive the video. `edge-tts` is free, offline-ish, and gives you word
timings:

```python
import edge_tts
com = edge_tts.Communicate(text, "en-GB-RyanNeural", rate="-4%")
words = []
with open("nar/S1.mp3", "wb") as f:
    async for ch in com.stream():
        if ch["type"] == "audio":
            f.write(ch["data"])
        elif ch["type"] == "WordBoundary":
            words.append({"t": ch["offset"]/1e7, "d": ch["duration"]/1e7, "w": ch["text"]})
```

The `WordBoundary` events are the useful part — they give you **word-level timing** so
captions can be cut to the voice instead of guessed. Save a `durations.json` keyed by
scene; every scene renders to its own narration length.

**Pronunciation.** TTS mangles proper nouns. Substitute phonetically *in the string you
send to the voice only*, never in on-screen text. Ours: `Ladera → "Ladaira"`,
`Mission Viejo → "Mission Vee-ay-ho"`, `San Juan Capistrano → "San Wahn Capistrano"`.

**2. Render frames in PIL, pipe raw into ffmpeg.** No intermediate image files:

```python
ff = subprocess.Popen([
    "ffmpeg","-y","-loglevel","error",
    "-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r","24","-i","-",
    "-c:v","libx264","-crf","17","-pix_fmt","yuv420p",
    "-video_track_timescale","12288", out_path], stdin=subprocess.PIPE)
for i in range(nframes):
    frame = make_frame(i, nframes)      # returns a PIL RGB Image
    ff.stdin.write(frame.tobytes())
ff.stdin.close(); ff.wait()
```

`-video_track_timescale 12288` on **every** segment. Without it the concat step drifts.

Ken Burns is just a crop that moves — resize to cover at a zoom factor, crop a window,
ease the interpolation (`t*t*(3-2*t)`). Fade each segment in and out by blending toward
black over the first 0.5 s and last 0.6 s, and pad each segment ~1.1 s longer than its
narration so lines never collide with cuts.

**3. Concatenate, then lay the narration on top — do not glue audio to clips.**

```bash
ffmpeg -f concat -safe 0 -i list.txt -c copy video.mp4
```

Then place each narration block at its segment's start time plus a small lead-in
(we used 0.45 s), with `adelay`, and mix:

```
[1:a]adelay=12340|12340[a0];[2:a]adelay=45600|45600[a1]; ... amix=inputs=N:normalize=0:dropout_transition=0[nar]
```

Laying audio by absolute timestamp rather than per-clip means **re-rendering one scene
never desynchronises the rest.**

**4. Music bed with sidechain ducking.** Loop the bed to length, fade, then duck it
under the voice automatically:

```
[0:a]asplit=2[v1][v2];
[1:a]volume=0.16[m];
[m][v2]sidechaincompress=threshold=0.02:ratio=6:attack=30:release=900:makeup=1[md];
[v1][md]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.95[a]
```

The limiter at 0.95 is what stops clipping on the loud lines.

**Vertical → YouTube 16:9**, blurred pillarbox from the same source:

```
[0:v]split=2[a][b];
[a]scale=1920:1080,boxblur=30:5,eq=brightness=-0.15[bg];
[b]scale=-2:1080[fg];
[bg][fg]overlay=(W-w)/2:0,format=yuv420p[v]
```

---

## If your 17 scenes already exist as a live app

You have a shortcut we didn't. Rather than re-implementing the scenes in PIL, drive the
app in a headless browser and capture frames — Playwright or Puppeteer, fixed viewport,
screenshot per frame at a fixed timestep, then feed the PNG sequence to ffmpeg:

```bash
ffmpeg -framerate 24 -i frames/%05d.png -c:v libx264 -crf 17 -pix_fmt yuv420p scene.mp4
```

Same audio stages afterwards. **The advantage is that the film and the live app can
never disagree**, which matters a lot for a teaching piece where someone freezes a scene
and asks a kid what he saw.

---

## What bit us, so it doesn't bite you

- **Render to the narration, not the other way round.** Write the script, generate the
  voice, read the durations, *then* build scenes to fit. Trying to time narration to
  finished visuals costs a full rebuild.
- **Verify sync by transcribing the finished audio** at several timestamps and checking
  the words against the script. We used faster-whisper (small, int8, CPU). Eyeballing it
  does not catch a 0.4 s creep.
- **Check the music is actually audible in the gaps.** We measured it: the bed should be
  meaningfully louder between narration blocks than in a voice-only cut. Easy to ship a
  film where the duck swallows the music entirely.
- `ffprobe` may not be installed even where `ffmpeg` is. Parse `ffmpeg -i` stderr for
  duration instead.
- Fonts: hardcode absolute paths. `/System/Library/Fonts/Supplemental/` on macOS.

---

## On the voice

Casting is the human's call, and the instruction already given is the right one — nobody
should put on an accent that isn't theirs. If a synthetic voice is used as a placeholder
or for a narrator track, say so wherever the film is published. We disclosed AI-assisted
imagery on ours as a standing rule, and the same logic applies to a synthetic voice.
