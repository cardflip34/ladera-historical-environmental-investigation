import json,urllib.request,urllib.error,hashlib,os,time
UA={'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'}
def raw(u,timeout=90):
    return urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=timeout).read()
def wait_until_open():
    probe='https://www.loc.gov/collections/chronicling-america/?q=a&fo=json&c=1&at=pagination'
    while True:
        try:
            raw(probe,45); return
        except urllib.error.HTTPError as e:
            if e.code in (429,503): time.sleep(300); continue
            return
        except Exception: time.sleep(120)
pages=json.load(open('pages.json'))
todo=[(r,m) for r,m in pages.items() if not os.path.exists('ocr/%s.txt'%hashlib.md5(r.encode()).hexdigest()[:12])]
print('to fetch:',len(todo),flush=True)
wait_until_open()
print('gate open, starting',flush=True)
ok=err=0
for rid,meta in todo:
    fp='ocr/%s.txt'%hashlib.md5(rid.encode()).hexdigest()[:12]
    u=rid.replace('http://','https://'); u+=('&' if '?' in u else '?')+'fo=json'
    try:
        d=json.loads(raw(u))
    except urllib.error.HTTPError as e:
        if e.code in (429,503): wait_until_open(); time.sleep(10); 
        err+=1; time.sleep(4); continue
    except Exception:
        err+=1; time.sleep(4); continue
    ft=d.get('resource',{}).get('fulltext_file')
    if not ft: err+=1; time.sleep(4); continue
    try:
        t=raw(ft).decode('utf-8','replace')
    except Exception:
        err+=1; time.sleep(4); continue
    open(fp,'w').write(f'#ID {rid}\n#DATE {meta["date"]}\n#PAPER {meta["paper"]}\n'+t)
    ok+=1
    if ok%20==0: print('fetched',ok,flush=True)
    time.sleep(4)
print('DONE newly fetched',ok,'failed',err,flush=True)
