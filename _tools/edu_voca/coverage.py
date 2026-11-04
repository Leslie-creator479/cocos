"""지문이 2022 개정 교육과정 기본 어휘(3,000개)를 얼마나 쓰는지 센다. (2026-11-04, 코코스 중등 독해 오리지널 지문 수준 확인용)

교육과정 지침: 학습·평가에 쓰는 어휘는 중학교에서 90% 이상을 기본 어휘 목록에서 쓰기를 권장한다.
단어군(대표형 + 굴절형 + 36개 파생 접사형)으로 센다. 고유 명사(문장 첫머리가 아닌 대문자 낱말)와 숫자는 빼고 센다.

    python3 _tools/edu_voca/coverage.py 지문.txt            # 또는 data.js(학습지 DATA, sentences의 en을 읽음)
    python3 _tools/edu_voca/coverage.py --text "Flamingos are ..."
출력: 낱말 수, 기본 어휘 비율(토큰 기준), 별표별 개수(** 중학교 권장, * 초등 권장, 표시 없음 = 그 밖의 과목 권장), 목록 밖 낱말.
lemminflect가 필요하다(pip install lemminflect --break-system-packages).
"""
import json, os, re, sys
from lemminflect import getAllLemmas

HERE = os.path.dirname(os.path.abspath(__file__))
L = json.load(open(os.path.join(HERE, 'basic3000.json'), encoding='utf8'))
FAM = {}
for e in L:
    for w in e['w'] + e['d']:
        for part in [w.lower()]:
            FAM.setdefault(part, e['lv'])
PRE = ['un', 'in', 'im', 'il', 'ir', 'en', 'em', 'inter', 'mis', 're', 'dis']
SUF = ['ably', 'ingly', 'fully', 'ically', 'ation', 'ication', 'ness', 'ment', 'ship', 'able', 'less', 'ful', 'ish', 'ist', 'ism', 'ity',
       'ize', 'ise', 'ous', 'ance', 'ence', 'ant', 'ent', 'ary', 'ify', 'ion', 'ive', 'ure', 'ical', 'ual', 'al', 'ic', 'ly', 'er', 'or', 'th', 'y']
PRON = {'its': 'it', 'their': 'they', 'them': 'they', 'theirs': 'they', 'themselves': 'they', 'these': 'this', 'those': 'that', 'us': 'we',
        'our': 'we', 'ours': 'we', 'ourselves': 'we', 'me': 'i', 'my': 'i', 'mine': 'i', 'myself': 'i', 'his': 'he', 'him': 'he', 'himself': 'he',
        'her': 'she', 'hers': 'she', 'herself': 'she', 'your': 'you', 'yours': 'you', 'yourself': 'you', 'itself': 'it'}  # 지침 예시: they의 굴절형
NUM = set('zero one two three four five six seven eight nine ten eleven twelve thirteen twenty thirty hundred thousand million billion first second third'.split())


def cands(w):
    out = {w, PRON.get(w, w)}
    for ls in getAllLemmas(w).values():
        out.update(ls)
    base = set(out)
    for b in list(base):
        for s in SUF:
            if b.endswith(s) and len(b) - len(s) >= 3:
                r = b[:-len(s)]
                out.update({r, r + 'e', r + 'y', r[:-1] if len(r) > 3 and r[-1] == r[-2] else r})
                if r.endswith('i'):
                    out.add(r[:-1] + 'y')
        for p in PRE:
            if b.startswith(p) and len(b) - len(p) >= 3:
                out.add(b[len(p):])
    return out


def level(w):
    best = None
    for c in cands(w):
        if c in FAM:
            lv = FAM[c]
            if best is None or lv > best:  # 별표가 많은 쪽(쉬운 쪽)을 먼저
                best = lv
    return best


def tokens(text):
    out = []
    for sent in re.split(r'(?<=[.!?])\s+', text):
        ws = re.findall(r"[A-Za-z][A-Za-z’'\-]*", sent)
        for i, w in enumerate(ws):
            w = re.sub(r"[’']s?$", '', w)
            if not w:
                continue
            if i > 0 and w[0].isupper() and w.lower() not in FAM and w != 'I':
                continue  # 고유 명사
            for part in w.split('-'):
                if part:
                    out.append(part.lower())
    return out


def report(text):
    toks = tokens(text)
    from collections import Counter
    cnt = Counter(); miss = Counter()
    for t in toks:
        if t in NUM:
            continue
        lv = level(t)
        if lv is None:
            miss[t] += 1; cnt['밖'] += 1
        else:
            cnt[lv] += 1
    n = sum(cnt.values())
    inl = n - cnt['밖']
    return dict(words=len(toks), counted=n, pct=round(100 * inl / n, 1) if n else 0,
                lv2=cnt[2], lv1=cnt[1], lv0=cnt[0], out=dict(miss.most_common()))


if __name__ == '__main__':
    a = sys.argv[1:]
    if a[0] == '--text':
        text = ' '.join(a[1:])
    else:
        s = open(a[0], encoding='utf8').read()
        if 'var DATA' in s:
            text = ' '.join(re.findall(r"en:\s*'((?:[^'\\]|\\.)*)'", s.split('sentences', 1)[1].split('gloss', 1)[0]))
        else:
            text = s
    r = report(text)
    print(f"낱말 {r['words']}개 · 기본 어휘 {r['pct']}% (**중학교 권장 {r['lv2']} · *초등 권장 {r['lv1']} · 그 밖의 과목 권장 {r['lv0']} · 목록 밖 {r['counted'] - r['lv2'] - r['lv1'] - r['lv0']})")
    print('목록 밖:', ', '.join(f'{k}×{v}' if v > 1 else k for k, v in r['out'].items()) or '없음')
