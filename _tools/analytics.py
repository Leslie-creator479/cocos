"""모든 학생용 페이지에 네이버 애널리틱스 코드를 붙인다 (선생님 결정 2026-10-18).

페이지(주소)마다 조회 수가 따로 잡혀서, 애널리틱스 '페이지분석'에서 어떤 회차·지문·단어게임을 많이 보는지 볼 수 있다.
계정 cocosedu, 발급 ID 1c961abfe2e9f50.

- 잠기지 않은 페이지: </body> 바로 앞에 코드를 넣는다.
- 잠긴 페이지(id="cocos-lock"): 암호문은 건드리지 않고 겉의 안내 화면(</body></html> 앞)에만 넣는다.
  잠금이 풀리면 document.write로 본문이 바뀌는데, 본문에는 코드가 없어서 한 번만 센다.
  lock.mjs도 잠글 때 본문의 코드를 빼고 겉 화면에 넣으므로 새로 잠그는 페이지도 한 번만 센다.
- tools/(선생님 자료함)·preview/(시안)는 세지 않는다.

seo.py가 돌 때마다 함께 돈다(올리기 전 항상 seo.py를 돌리므로 새 페이지에도 자동으로 붙는다). 여러 번 돌려도 같다.
사용법: python3 _tools/analytics.py [--check]
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WA = '1c961abfe2e9f50'
SNIP = ('<!-- naver-analytics -->\n<script src="https://wcs.pstatic.net/wcslog.js"></script>\n'
        '<script>if(!wcs_add) var wcs_add = {};wcs_add["wa"] = "' + WA + '";if(window.wcs) {wcs_do();}</script>\n<!-- /naver-analytics -->\n')
SKIP = {'.git', '_tools', 'tools', 'preview', 'node_modules', 'assets', 'forms'}
MARK = 'id="cocos-lock"'


def pages():
    for d, dirs, files in os.walk(ROOT):
        rel = os.path.relpath(d, ROOT)
        if rel.split(os.sep)[0] in SKIP:
            dirs[:] = []; continue
        dirs.sort()
        if 'index.html' in files:
            yield os.path.join(d, 'index.html')


def add(s):
    if 'wcs_add["wa"]' in s:
        return None
    if MARK in s:
        i = s.rfind('</body></html>')
        return s[:i] + SNIP + s[i:] if i >= 0 else None
    i = s.rfind('</body>')
    return s[:i] + SNIP + s[i:] if i >= 0 else s.rstrip('\n') + '\n' + SNIP


def run(check=False, quiet=False):
    n = locked = 0
    for f in pages():
        s = open(f, encoding='utf8').read()
        t = add(s)
        if t is None:
            continue
        n += 1; locked += MARK in s
        if not check:
            open(f, 'w', encoding='utf8').write(t)
    if n or not quiet:
        print(f'애널리틱스: 이번에 붙인 페이지 {n}쪽 (잠긴 페이지 겉 화면 {locked}쪽)' + (' [확인만]' if check else ''))


if __name__ == '__main__':
    run(check='--check' in sys.argv)
