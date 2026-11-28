# data.json → game_data.json (지문 P, 단어 W). 빈칸 문제용 오답 보기 후보까지 만든다.
# 사용: python3 -I build.py data.json game_data.json
# 오답 보기 규칙(선생님과 정함): 빈칸 자리와 같은 품사 + 같은 형태(명사 단·복수, 동사 원형/-s/-ing/-ed),
#   빈칸 앞이 a/an이면 같은 소리로 시작하는 말만, 다른 지문 단어 우선, 같은 문장에 이미 있는 말·철자 앞 5자가 같은 말 제외.
#   숙어(품사 '숙')와 ~·A·B·sb 같은 틀 표현, 불규칙 변화형은 형태를 맞출 수 없어 빈칸 문제에서만 뺀다.
import json, re, sys, collections
D = json.load(open(sys.argv[1], encoding='utf8'))
def variants(w):
    out = [w]
    if ' ' in w: return out
    out += [w+'s', w+'es', w+'d', w+'ed', w+'ing', w+'er', w+'est']
    if w.endswith('y'): out += [w[:-1]+'ies', w[:-1]+'ied', w[:-1]+'ier', w[:-1]+'iest']
    if w.endswith('e'): out += [w[:-1]+'ing']
    if len(w) > 2 and w[-1] not in 'aeiouwy' and w[-2] in 'aeiou' and w[-3] not in 'aeiou': out += [w+w[-1]+'ed', w+w[-1]+'ing']
    return out
BAD = re.compile(r"[~()/…]|\b(A|B|sb|sth|somebody|something|one's|oneself)\b")
words = []
for pi, d in enumerate(D):
    for v in d['vocab']:
        e = dict(w=v['w'], p=v['p'], m=v['m'], g=pi); words.append(e)
        if v['p'] == '숙' or BAD.search(v['w']): continue
        hit = None
        for si, s in enumerate(d['sentences']):
            for f in variants(v['w']):
                m = re.search(r"(?<![A-Za-z'’-])(" + re.escape(f) + r")(?![A-Za-z'’-])", s['en'], re.I)
                if m: hit = (si, m); break
            if hit: break
        if not hit: continue
        si, m = hit; f = m.group(1); w = v['w']; fl = f.lower(); p = v['p']
        if p == '명': cls = 'pl' if fl != w.lower() and fl.endswith('s') else 'sg'
        elif p == '동':
            if fl == w.lower(): cls = 'base'
            elif fl in (w+'s', w+'es', w[:-1]+'ies'): cls = 's'
            elif fl.endswith('ing'): cls = 'ing'
            elif fl.endswith('ed'): cls = 'ed'
            else: cls = 'irr'
        elif p in ('형', '부'): cls = 'base' if fl == w.lower() else 'cmp'
        else: continue
        pre = d['sentences'][si]['en'][:m.start()]
        art = re.search(r"\b(a|an)\s+$", pre, re.I)
        e.update(s=si, f=f, cls=cls, art=(art.group(1).lower() if art else None))
def vowel(x): return x[0].lower() in 'aeiou'
n_blank = 0
for e in words:
    if 'cls' not in e: continue
    def ok(o):
        if o is e or 'cls' not in o or o['p'] != e['p'] or o['cls'] != e['cls']: return False
        if o['f'].lower() == e['f'].lower() or o['w'][:5].lower() == e['w'][:5].lower(): return False
        if e['art'] and vowel(o['f']) != vowel(e['f']): return False
        if o['f'].lower() in D[e['g']]['sentences'][e['s']]['en'].lower(): return False
        return True
    pool = [i for i, o in enumerate(words) if ok(o) and o['g'] != e['g']]
    if len(pool) < 3: pool += [i for i, o in enumerate(words) if ok(o) and o['g'] == e['g']]
    if len(pool) >= 3: e['pool'] = pool; n_blank += 1
P = []
for d in D:
    p = dict(no=d['no'], topic=d['topic'], u=d.get('u', ''), s=[[x['en'], x['ko']] for x in d['sentences']])
    for k in ('k', 'lab', 'sa'):
        if d.get(k): p[k] = d[k]
    P.append(p)
W = []
for e in words:
    r = [e['w'], e['p'], e['m'], e['g']]
    if e.get('pool'): r += [e['s'], e['f'], e['pool']]
    W.append(r)
json.dump(dict(P=P, W=W), open(sys.argv[2], 'w', encoding='utf8'), ensure_ascii=False, separators=(',', ':'))
print('지문', len(P), '단어', len(W), '빈칸 문제 가능', n_blank)
print('지문별 빈칸 문제 수', [(D[g]['no'], sum(1 for e in words if e['g'] == g and e.get('pool'))) for g in range(len(D))])
