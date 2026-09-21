import json,urllib.request,re,os,time,hashlib
UA={'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'}
pages=json.load(open('pages.json'))
os.makedirs('ocr',exist_ok=True)
def get(u,raw=False,tries=3,timeout=70):
    for a in range(tries):
        try:
            r=urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=timeout).read()
            return r.decode('utf-8','replace') if raw else json.loads(r)
        except Exception as e:
            if a==tries-1: return None
            time.sleep(3)
ok=err=0
for rid,meta in pages.items():
    h=hashlib.md5(rid.encode()).hexdigest()[:12]
    fp=f'ocr/{h}.txt'
    if os.path.exists(fp): ok+=1; continue
    u=rid.replace('http://','https://')
    u=u+('&' if '?' in u else '?')+'fo=json'
    d=get(u)
    if not d or 'resource' not in d or not d['resource'].get('fulltext_file'):
        err+=1; continue
    t=get(d['resource']['fulltext_file'],raw=True)
    if not t: err+=1; continue
    open(fp,'w').write(f'#ID {rid}\n#DATE {meta["date"]}\n#PAPER {meta["paper"]}\n'+t)
    ok+=1
    time.sleep(0.4)
print('fetched',ok,'errors',err)
