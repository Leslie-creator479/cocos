import json, sys, re
# 사용법: python3 antchk.py <동의어·게임 작업 폴더> <과…>  → 반의어·동의어를 넣은 문장을 찍어 어색한 곳을 눈으로 찾는다
G = sys.argv[1]
for n in sys.argv[2:]:
    d = json.load(open(f'{G}/L{n}/content_syn.json', encoding='utf8'))
    for it in d['items']:
        sents = re.split(r'(?<=[.!?”])\s+', it['passage'])
        for w in it.get('words', []):
            sp = w.get('span') or w['t']
            s = next((x for x in sents if sp in x), it['passage'])
            mark = '★' if w.get('star') else ' '
            print(f"{it['no']} {mark} [{sp} → {w['ant_t']} | ≒ {w['syn_t'][0]}]  " + s.replace(sp, '<<' + w['ant_t'] + '>>', 1))
