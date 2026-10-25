import json,sys
# 사용법: python3 bound.py <동의어·게임 작업 폴더> <과…>  → 바꿔 넣을 낱말이 다른 낱말 속에서 먼저 잡히는 곳(rough/through)
import os
G = sys.argv[1]
for n in sys.argv[2:]:
    d=json.load(open(os.path.join(G, f'L{n}', 'content_syn.json')))
    for it in d['items']:
        p=it['passage']
        for w in it['words']:
            sp=w.get('span') or w['t']
            i=p.find(sp)
            if i<0 or (i>0 and p[i-1].isalpha()) or (i+len(sp)<len(p) and p[i+len(sp)].isalpha()): print('경계',n,it['no'],sp)
