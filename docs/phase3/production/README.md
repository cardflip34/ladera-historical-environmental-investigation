# Phase 3 production source

Rebuild the film from these five files.

| File | Role |
|---|---|
| `narration_script.py` | All 27 narration blocks + the TTS pronunciation substitution |
| `gen_tts.py` | Generates the voice with edge-tts `en-GB-RyanNeural`, rate -4% |
| `build.py` | Renders all 27 visual segments, 1080x1920 @ 24fps, PIL frames piped to ffmpeg |
| `assemble.py` | Concatenates segments, lays each narration block at its segment start + 0.45 s |
| `score.sh` | Music bed, sidechain duck, both masters |

Order: `gen_tts.py` → `build.py` → `assemble.py` → `score.sh`.

## Verified output
- **19:58.76**, 1080x1920 and 1920x1080, 48 kHz stereo
- Narration 19:31 across 27 blocks
- Sync confirmed by transcribing the finished audio at 30 s, 224 s, 405 s, 692 s, 1110 s
- Music verified present: 14 dB louder in narration gaps than in the voice-only cut, level-matched under speech

## Part boundaries
Part 1 opens at 0:00 · Part 2 at 6:43 · Part 3 at 11:30 · closing at 18:28

## Standing constraints honoured in the cut
- Every Florida frame captioned **FLORIDA — not Ladera Ranch**
- Every permit citation reads **tentative copy held**
- Kinoshita scene says three days, not four, and calls the structure what the record calls it
- No frame asserts any contaminant is present in any soil, runoff, recycled water or irrigation water

## Gate still open
Base Order 97-52 Table A-1 has not been checked, so the testing scene says
"the publicly identified testing reviewed in this project," never "no testing exists."
