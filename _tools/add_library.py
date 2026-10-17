"""자료실(library/index.html)에 회차 카드를 넣거나(같은 href면 바꿔) 정렬해서 저장한다.
화면은 모의고사/교과서/학교별 시험 범위 × 학습지/동의어·반의어/단어게임으로 보이며, 분류는 카드 주소로 자동으로 정해진다.

사용법:
  python3 _tools/add_library.py <탭> "<제목>" <사이트 경로> <지문 수> [--group "<묶음 이름>"]

  탭: study(모의고사, 화면 표시는 '모의고사') | textbook(교과서) | school(학교별 시험 범위) | syn(동의어·반의어) | game(단어게임)
  제목: 학력평가·동의어·단어게임은 "2026년 10월 고1"처럼 연도·월·학년을 쓴다(자료실이 연도·학년으로 묶는다).
        학교별은 "동광고 1학년", 교과서는 "4과"처럼 쓰고 --group에 교재 이름("영어II NE능률(오선영)")을 준다.
  사이트 경로: 저장소 기준 폴더. 예) study/2026-10-g1 , syn/2026-10-g1 , game/2026-10-g1 , textbook/neo2/4
  예) python3 _tools/add_library.py study "2026년 10월 고1" study/2026-10-g1 22
  단어장(학원에서 쓰는 시중 단어장): 경로를 game/voca-<영문 약칭>으로 하면 자료실 '단어장' 분류에 들어간다. 지문 수 자리는 Day 수.
     --buy "<구매 주소>" --buy-label "정규반 단어 교재: …"를 주면 카드 아래에 구매 링크가 붙는다.
  예) python3 _tools/add_library.py game "능률VOCA 고등기본" game/voca-nehs-basic 3 --group "정규반 단어장" --buy "https://…" --buy-label "정규반 단어 교재: 능률VOCA 고등기본 · 교보문고에서 사기"
"""
import json, re, sys

LIB = 'library/index.html'
args = [x for x in sys.argv[1:]]
def opt(name):
    if name in args:
        i = args.index(name); v = args[i + 1]; del args[i:i + 2]; return v
    return ''
grp = opt('--group'); buy = opt('--buy'); buy_label = opt('--buy-label')
tab, title, path, n = args[0], args[1], args[2].strip('/'), int(args[3])
assert tab in ('study', 'textbook', 'school', 'syn', 'game'), '탭 이름 확인'

s = open(LIB, encoding='utf8').read()
k = s.index('var D = ') + len('var D = ')
D, end = json.JSONDecoder().raw_decode(s[k:])
m = re.match(r'(\d{4})년 (\d+)월 고(\d)', title)
y = m.group(1) if m else '2026'
g = m.group(3) if m else ('1' if '1학년' in title else '2' if '2학년' in title else '')
D.setdefault(tab, [])
if not g and grp:  # 교과서처럼 제목에 학년이 없으면 같은 교재(--group) 카드의 학년을 따른다
    g = next((c['g'] for cs in D.values() for c in cs if c.get('grp') == grp and c.get('g')), '')
card = {'t': title, 'y': y, 'g': g, 'n': n, 'href': '../' + path + '/', 'grp': grp}
if buy: card['buy'] = buy
if buy_label: card['buyLabel'] = buy_label
D[tab] = [c for c in D[tab] if c['href'] != card['href']] + [card]


def key(c):
    mm = re.match(r'(\d{4})년 (\d+)월 고(\d)', c['t'])
    if mm:
        return (0, -int(mm.group(1)), int(mm.group(3)), int(mm.group(2)), '')
    return (1, 0, 0, 0, c.get('grp', '') + c['t'])


for t in D:
    D[t].sort(key=key)
s = s[:k] + json.dumps(D, ensure_ascii=False) + s[k + end:]
# 지문 수 숫자 갱신
import glob
tot = len(glob.glob('study/*/*/index.html')) + len(glob.glob('textbook/*/*/*/index.html'))
s = re.sub(r'(<div><b>)\d+(</b><span>지문별 학습지</span>)', lambda mm: mm.group(1) + str(tot) + mm.group(2), s)
s = re.sub(r'(<div><b>)\d+(</b><span>모의고사 회차</span>)', lambda mm: mm.group(1) + str(len(D.get('study', []))) + mm.group(2), s)
open(LIB, 'w', encoding='utf8').write(s)
print('자료실', tab, title, '→', card['href'], '| 회차 수', {t: len(v) for t, v in D.items()})
