import json,urllib.parse,urllib.request,time,re,os,hashlib
UA={'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/131.0 Safari/537.36'}
BASE='https://www.loc.gov/collections/chronicling-america/'
def s(q,c=100,dates='1900/1920',pages=2):
    out=[]
    for pg in range(1,pages+1):
        p={'q':q,'fo':'json','c':str(c),'dates':dates,'at':'results,pagination','sp':str(pg)}
        u=BASE+'?'+urllib.parse.urlencode(p)+'&fa=location_state%3Acalifornia'
        try: d=json.load(urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=90))
        except Exception as e: print('ERR',q,e); break
        if pg==1: print(f'  "{q}" total={d.get("pagination",{}).get("of")}')
        out+=d.get('results',[])
        if not d.get('pagination',{}).get('next'): break
        time.sleep(1)
    return out
pages=json.load(open('pages.json'))
add=0
for q in ["\"O'Neil\" ranch cattle dip","\"O'Neil\" Texas fever tick","\"O'Neill\" Texas fever tick",
          "Jerome O'Neil ranch cattle","\"O'Neil ranch\" cattle","\"Santa Margarita ranch\" cattle dipping",
          "\"tick dip\"","\"dipping vats\" California cattle ranch","\"dipped\" \"Texas fever\" ranch",
          "Flood O'Neil ranch cattle quarantine"]:
    for r in s(q):
        rid=r.get('id')
        if rid and rid not in pages:
            pages[rid]={'date':r.get('date'),'paper':(r.get('partof_title') or [''])[0],'id':rid}; add+=1
    time.sleep(1)
json.dump(pages,open('pages.json','w'),indent=1)
print('added',add,'total',len(pages))
