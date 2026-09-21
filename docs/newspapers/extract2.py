import re,os,glob,json
from collections import Counter
TERMS={
 'Closson':r'closson',
 'McFarlane':r'mc\s?farlane',
 'stock inspector':r'(?:live\s?stock|stock|cattle)\s+inspector',
 'county veterinarian':r'county\s+veterinar',
 'state veterinarian':r'state\s+veterinar',
 'Keane':r'\bkeane\b',
 'cattle tick':r'\bcattle\s+ticks?\b|\bticks?\s+(?:on|in|among)\s+cattle',
 'tick fever':r'\btick\s+fever\b|\bsplenetic\b|\btexas\s+fever\b',
 'bare tick':r'\btick(?:s)?\b(?!et)',
 'dipping':r'\bdipp?ing\s+(?:vat|tank|plant|pen|cattle|of\s+cattle)|\bcattle\s+(?:were\s+|are\s+)?dipp?ed\b|\bdip\s+(?:the\s+)?cattle\b',
 'arsenic':r'arsenic',
 'quarantine+cattle':r'quarantin\w*[^.]{0,120}cattle|cattle[^.]{0,120}quarantin\w*',
 'Santa Margarita':r'santa\s+margarita',
 'Mission Viejo':r'mission\s+vie?jo',
 "O'Neill ranch":r"o[’'`]?\s?neill?[^.]{0,60}(ranch|rancho)|(ranch|rancho)[^.]{0,60}o[’'`]?\s?neill?",
 'Las Flores':r'las\s+flores',
 'Flood ranch':r'flood[^.]{0,40}(ranch|rancho)',
}
CTX=300
out=[]
for fp in sorted(glob.glob('sar/*.txt')):
    flat=re.sub(r'\s+',' ',open(fp,errors='replace').read())
    for name,pat in TERMS.items():
        for m in re.finditer(pat,flat,re.I):
            out.append({'file':os.path.basename(fp)[:-4],'term':name,
                        'match':flat[m.start():m.end()][:60],
                        'ctx':flat[max(0,m.start()-CTX):m.end()+CTX]})
json.dump(out,open('sar_hits2.json','w'),indent=1)
c=Counter(h['term'] for h in out)
for k in TERMS: print(f'  {k:22s} {c.get(k,0)}')
print('total',len(out))
