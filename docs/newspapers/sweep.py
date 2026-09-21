import json,urllib.parse,urllib.request,time,os,re,sys
UA={'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'}
BASE='https://www.loc.gov/collections/chronicling-america/'
os.makedirs('ocr',exist_ok=True)

def get(url,timeout=90,tries=3,raw=False):
    req=urllib.request.Request(url,headers=UA)
    for a in range(tries):
        try:
            r=urllib.request.urlopen(req,timeout=timeout).read()
            return r if raw else json.loads(r)
        except Exception as e:
            if a==tries-1: return {'__err':str(e)} if not raw else b''
            time.sleep(4)

def search(q,c=100,dates='1905/1920',state='california',pages=3):
    out=[]
    for pg in range(1,pages+1):
        p={'q':q,'fo':'json','c':str(c),'dates':dates,'at':'results,pagination','sp':str(pg)}
        url=BASE+'?'+urllib.parse.urlencode(p)
        if state: url+='&fa=location_state%3A'+state
        d=get(url)
        if '__err' in d: print('ERR',q,d['__err']); break
        res=d.get('results',[])
        out+=res
        tot=d.get('pagination',{}).get('of')
        if pg==1: print(f'  query "{q}" total={tot}')
        if not d.get('pagination',{}).get('next'): break
        time.sleep(1)
    return out

QUERIES=[
 'Closson','"cattle tick"','"Texas fever"','"dipping vat"','"dipping vats"',
 '"tick inspector"','"cattle quarantine"','"tick eradication"','"dipping cattle"',
 'McFarlane cattle tick quarantine',
]
seen={}
for q in QUERIES:
    for r in search(q):
        rid=r.get('id')
        if rid and rid not in seen:
            seen[rid]=r
print('unique pages:',len(seen))
json.dump({k:{'date':v.get('date'),'paper':(v.get('partof_title') or [''])[0],'id':k} for k,v in seen.items()},open('pages.json','w'),indent=1)
