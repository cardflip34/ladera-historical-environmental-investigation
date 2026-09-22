import json,urllib.parse,urllib.request,urllib.error,time,re,os,hashlib
UA={'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'}
BASE='https://www.loc.gov/collections/chronicling-america/'
def raw(u,t=90):
    return urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=t).read()
def patient(u,t=90):
    d=5
    for a in range(8):
        try: return raw(u,t)
        except urllib.error.HTTPError as e:
            if e.code in (429,503): time.sleep(d); d=min(d*2,240); continue
            return None
        except Exception: time.sleep(d); d=min(d*2,240)
    return None
def search(q,dates='1900/1925',c=100,state=True):
    p={'q':q,'fo':'json','c':str(c),'dates':dates,'at':'results,pagination'}
    u=BASE+'?'+urllib.parse.urlencode(p)+('&fa=location_state%3Acalifornia' if state else '')
    b=patient(u)
    if not b: print('  ERR',q,flush=True); return []
    d=json.loads(b)
    print(f'  "{q}" total={d.get("pagination",{}).get("of")}',flush=True)
    return d.get('results',[])

pages=json.load(open('pages.json'))
QS=['Selleck','"Selleck" cattle inspector','"dipping vat"','"dipping vats"','"dipping tank"',
    '"dipping tanks"','"dipping plant"','"cattle dipping"','"dipped for ticks"',
    '"Orme" county veterinarian','"state veterinarian" dipping','"cattle inspector" "San Diego"']
add=0
for q in QS:
    for r in search(q):
        rid=r.get('id')
        if rid and rid not in pages:
            pages[rid]={'date':r.get('date'),'paper':(r.get('partof_title') or [''])[0],'id':rid}; add+=1
    time.sleep(5)
json.dump(pages,open('pages.json','w'),indent=1)
print('NEW CANDIDATES',add,'TOTAL',len(pages),flush=True)

ok=err=0
for rid,meta in pages.items():
    fp='ocr/%s.txt'%hashlib.md5(rid.encode()).hexdigest()[:12]
    if os.path.exists(fp): continue
    u=rid.replace('http://','https://'); u+=('&' if '?' in u else '?')+'fo=json'
    b=patient(u)
    if not b: err+=1; time.sleep(4); continue
    ft=json.loads(b).get('resource',{}).get('fulltext_file')
    if not ft: err+=1; time.sleep(4); continue
    t=patient(ft)
    if not t: err+=1; time.sleep(4); continue
    open(fp,'w').write(f'#ID {rid}\n#DATE {meta["date"]}\n#PAPER {meta["paper"]}\n'+t.decode('utf-8','replace'))
    ok+=1; time.sleep(4)
print('FETCHED',ok,'FAILED',err,flush=True)
