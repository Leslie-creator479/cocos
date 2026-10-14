"""자료실(library/index.html)에 회차 카드를 넣거나(같은 href면 바꿔) 정렬해서 저장한다.

사용법:
  python3 _tools/add_library.py <탭> "<제목>" <사이트 경로> <지문 수> [--group "<묶음 이름>"]

  탭: study(학력평가) | textbook(교과서) | school(학교별 시험 범위) | syn(동의어·반의어) | game(단어게임)
  제목: 학력평가·동의어·단어게임은 "2026년 10월 고1"처럼 연도·월·학년을 쓴다(자료실이 연도·학년으로 묶는다).
        학교별은 "동광고 1학년", 교과서는 "4과"처럼 쓰고 --group에 교재 이름("영어II NE능률(오선영)")을 준다.
  사이트 경로: 저장소 기준 폴더. 예) study/2026-10-g1 , syn/2026-10-g1 , game/2026-10-g1 , textbook/neo2/4
  예) python3 _tools/add_library.py study "2026년 10월 고1" study/2026-10-g1 22
"""
import json, re, sys

LIB = 'library/index.html'
args = [x for x in sys.argv[1:]]
grp = ''
if '--group' in args:
    i = args.index('--group'); grp = args[i + 1]; del args[i:i + 2]
tab, title, path, n = args[0], args[1], args[2].strip('/'), int(args[3])
assert tab in ('study', 'textbook', 'school', 'syn', 'game'), '탭 이름 확인'

s = open(LIB, encoding='utf8').read()
k = s.index('var D = ') + len('var D = ')
D, end = json.JSONDecoder().raw_decode(s[k:])
m = re.match(r'(\d{4})년 (\d+)월 고(\d)', title)
y = m.group(1) if m else '2026'
g = m.group(3) if m else ('1' if '1학년' in title else '2' if '2학년' in title else '')
card = {'t': title, 'y': y, 'g': g, 'n': n, 'href': '../' + path + '/', 'grp': grp}
D.setdefault(tab, [])
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
s = re.sub(r'(<div><b>)\d+(</b><span>학력평가 회차</span>)', lambda mm: mm.group(1) + str(len(D.get('study', []))) + mm.group(2), s)
open(LIB, 'w', encoding='utf8').write(s)
print('자료실', tab, title, '→', card['href'], '| 회차 수', {t: len(v) for t, v in D.items()})
