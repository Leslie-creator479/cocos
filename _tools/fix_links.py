"""페이지 안의 claude.ai 아티팩트 링크를 홈페이지 주소로 바꾼다.

- 옛 아티팩트 id(`https://claude.ai/artifact/KVmQ…`)는 _tools/artifact_map.json에서 저장소 경로를 찾는다.
- 아직 아티팩트가 없는 새 페이지는 스크립트에 **가짜 id**로 넘긴다: 저장소 경로의 `/`를 `_`로 바꾼 것
  (예: study/2026-10-g1/18 → `study_2026-10-g1_18`). 진짜 아티팩트 id에는 `_`가 없어서 구분된다.
- 기본은 상대 경로(페이지끼리 링크). `--absolute`를 주면 전체 주소(블로그·카카오톡용).
- `#앵커`는 그대로 남긴다. 찾지 못한 id는 바꾸지 않고 경고로 알린다.

사용법:
  python3 _tools/fix_links.py <이 페이지의 저장소 경로> <파일> [--absolute]
  예) python3 _tools/fix_links.py game/2026-10-g1 game/2026-10-g1/index.html
      python3 _tools/fix_links.py - blog_list.html --absolute      (경로 '-' : 전체 주소만 쓸 때)
"""
import json, os, re, sys

BASE = 'https://leslie-creator479.github.io/cocos/'
HERE = os.path.dirname(os.path.abspath(__file__))
MAP = json.load(open(os.path.join(HERE, 'artifact_map.json'), encoding='utf8'))

args = [a for a in sys.argv[1:] if not a.startswith('--')]
absolute = '--absolute' in sys.argv
page, files = args[0].strip('/'), args[1:]
missing = {}


def target(i):
    if i in MAP:
        return MAP[i]
    if '_' in i:
        return i.replace('_', '/')
    return None


def sub(m):
    p = target(m.group(1))
    if p is None:
        missing[m.group(1)] = missing.get(m.group(1), 0) + 1
        return m.group(0)
    if absolute or page == '-':
        return BASE + p + '/'
    return os.path.relpath(p, page) + '/'


for f in files:
    before = sum(missing.values())
    s = open(f, encoding='utf8').read()
    n = len(re.findall(r'https://claude\.ai/artifact/[A-Za-z0-9_-]+', s))
    s = re.sub(r'https://claude\.ai/artifact/([A-Za-z0-9_-]+)/?', sub, s)
    open(f, 'w', encoding='utf8').write(s)
    left = len(re.findall(r'https://claude\.ai/(?:code/)?artifact/', s))
    print(f'{f}: 링크 {n}개 중 {n - (sum(missing.values()) - before)}개 바꿈, 남은 claude.ai 링크 {left}개')
if missing:
    print('찾지 못한 id(바꾸지 않음):', missing)
