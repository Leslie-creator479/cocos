"""학습지·목차·동의어·단어게임 페이지의 로고와 아래 학원 안내 카드 링크를 홈페이지에 맞게 바꾼다.

- 위쪽 로고(a.brand): 그 페이지 맨 아래 카드(#academy)로 내려가던 것을 → 홈페이지 첫 화면으로
- 학원 안내 카드 버튼: 자료실에서 다른 학습지 보기(파란 버튼) · 블로그에서 수업 소식 보기 · 인스타그램 보기 ·
  학원 홈페이지 · 상담·위치(네이버 플레이스). 블로그 방문도 적극 권하므로 다른 버튼과 같은 크기로 둔다(선생님 결정 2026-10-14)
- 카드 안내 문구를 지금 상황에 맞게 고침. 학원명·등록번호·교습비 표시는 그대로.
링크는 상대 경로라 페이지 위치에서 계산한다. 몇 번 실행해도 결과가 같다(이미 바뀐 페이지는 건너뜀).

사용법: python3 _tools/brand_links.py <페이지 index.html> [...]
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BLOG = 'https://blog.naver.com/cocosedu'
PLACE = 'https://map.naver.com/p/entry/place/38464695'
INSTA = 'https://www.instagram.com/cocos_sujin/'


def convert(path):
    s = open(path, encoding='utf8').read()
    if 'class="brand" href="#academy"' not in s and 'title="코코스학원 홈페이지로"' not in s:
        return 'skip(다른 양식)'
    page = os.path.relpath(os.path.dirname(os.path.abspath(path)), ROOT)
    home = os.path.relpath(ROOT, os.path.join(ROOT, page)).replace(os.sep, '/') + '/'
    lib = home + 'library/'
    n = 0
    s, k = re.subn(r'<a class="brand" href="(?:#academy|[./]*)"(?: title="코코스학원 홈페이지로")?>', f'<a class="brand" href="{home}" title="코코스학원 홈페이지로">', s, count=1); n += k
    # 안내 문구
    s, k = re.subn(r'(<h2 id="h-academy">[^<]*</h2>\s*<p>)[^<]*(</p>)',
                   r'\1시험 범위 지문마다 해석·단어·마인드맵·변형 문제까지 담은 온라인 학습지를 만들고 있어요. 더 많은 학습지는 자료실에서, 수업 소식은 블로그와 인스타그램에서, 학원 소개와 설명회 소식은 홈페이지에서 볼 수 있어요.\2', s, count=1); n += k
    # 버튼
    new_ctas = ('<div class="ctas">\n'
                f'      <a class="primary" href="{lib}">자료실에서 다른 학습지 보기</a>\n'
                f'      <a class="ghost" id="go-blog" href="{BLOG}" target="_blank" rel="noopener">블로그에서 수업 소식 보기</a>\n'
                f'      <a class="ghost" id="go-insta" href="{INSTA}" target="_blank" rel="noopener">인스타그램 보기</a>\n'
                f'      <a class="ghost" href="{home}">학원 홈페이지</a>\n'
                f'      <a class="ghost" id="go-place" href="{PLACE}" target="_blank" rel="noopener">상담·위치 보기 (네이버 플레이스)</a>\n'
                '    </div>')
    s, k = re.subn(r'<div class="ctas">\s*<a class="primary"[\s\S]*?</div>(?:\s*<p class="more">[\s\S]*?</p>)?', lambda m: new_ctas, s, count=1); n += k
    if n != 3:
        return f'FAIL(바꾼 곳 {n}/3)'
    open(path, 'w', encoding='utf8').write(s)
    return f'ok (홈 {home})'


if __name__ == '__main__':
    for p in sys.argv[1:]:
        print(p, convert(p))
