import asyncio, edge_tts, json, os, sys
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from script import BLOCKS, ORDER, tts_text
VOICE="en-GB-RyanNeural"
os.makedirs("nar",exist_ok=True)
async def one(key):
    txt=tts_text(BLOCKS[key]).replace("\n"," ").strip()
    mp3="nar/%s.mp3"%key; wj="nar/%s.json"%key
    if os.path.exists(mp3) and os.path.getsize(mp3)>8000 and os.path.exists(wj): return
    com=edge_tts.Communicate(txt,VOICE,rate="-4%")
    words=[]
    with open(mp3,"wb") as f:
        async for ch in com.stream():
            if ch["type"]=="audio": f.write(ch["data"])
            elif ch["type"]=="WordBoundary":
                words.append({"t":ch["offset"]/1e7,"d":ch["duration"]/1e7,"w":ch["text"]})
    json.dump(words,open(wj,"w"))
async def main():
    for k in ORDER:
        for attempt in range(3):
            try:
                await one(k); print("ok",k,flush=True); break
            except Exception as e:
                print("retry",k,attempt,e,flush=True); await asyncio.sleep(3)
asyncio.run(main())
