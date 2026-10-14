"""학습지·목차·동의어·단어게임 페이지의 로고와 아래 학원 안내 카드 링크를 홈페이지에 맞게 바꾼다.

- 위쪽 로고(a.brand): 그 페이지 맨 아래 카드(#academy)로 내려가던 것을 → 홈페이지 첫 화면으로
- 학원 안내 카드 버튼: 자료실에서 다른 학습지 보기(파란 버튼) · 블로그에서 수업 소식 보기 · 인스타그램 보기 ·
  학원 홈페이지 · 상담·위치(네이버 플레이스). 다섯 버튼은 같은 크기(굵은 제목 + 작은 설명 두 줄). 블로그 방문도 적극 권하므로 다른 버튼과 같은 크기로 둔다(선생님 결정 2026-10-14)
- 공유 안내 줄('친구에게도 … 공유해 주세요!')이 없으면 넣는다(단어게임). 잠그는 교과서·부교재 페이지는 lock.mjs가 배포 금지 문구로 바꾼다.
- 카드 안내 문구를 지금 상황에 맞게 고침. 학원명·등록번호·교습비 표시는 그대로.
링크는 상대 경로라 페이지 위치에서 계산한다. 몇 번 실행해도 결과가 같다(이미 바뀐 페이지는 건너뜀).

사용법: python3 _tools/brand_links.py <페이지 index.html> [...]
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BLOG = 'https://blog.naver.com/cocosedu'
PLACE = 'https://map.naver.com/p/entry/place/38464695'
INSTA = 'https://www.instagram.com/cocos_sujin/'
# 버튼 다섯 개를 같은 크기로(선생님 요청 2026-10-14): 굵은 제목 + 작은 설명 두 줄, 넓으면 5칸, 좁으면 한 줄에 하나
CTA_CSS = ('/* brand-ctas */'
           '.promo .ctas{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:8px}'
           '.promo .ctas a{flex-direction:column;justify-content:center;align-items:center;text-align:center;gap:2px;min-height:66px;padding:10px 6px;line-height:1.35}'
           '.promo .ctas a b{font-size:15px;font-weight:700;white-space:nowrap}'
           '.promo .ctas a small{font-size:12.5px;font-weight:400;opacity:.85;white-space:nowrap}'
           '.promo .share{font-size:13.5px;color:var(--muted)}'
           '@media (max-width:720px){.promo .ctas{grid-template-columns:repeat(2,minmax(0,1fr))}.promo .ctas a.primary{grid-column:1 / -1}}')


def convert(path):
    s = open(path, encoding='utf8').read()
    if 'class="brand" href="#academy"' not in s and 'title="코코스학원 홈페이지로"' not in s:
        return 'skip(다른 양식)'
    page = os.path.relpath(os.path.dirname(os.path.abspath(path)), ROOT)
    home = os.path.relpath(ROOT, os.path.join(ROOT, page)).replace(os.sep, '/') + '/'
    lib = home + 'library/'
    n = 0
    s, k = re.subn(r'<a class="brand" href="(?:#academy|[./]*)"(?: title="코코스학원 홈페이지로")?>', f'<a class="brand" href="{home}" title="코코스학원 홈페이지로">', s, count=1); n += k
    # 안내 문구 (단어게임 페이지는 단어게임도 함께 말한다)
    what = '온라인 학습지와 단어를 재미있게 익히는 단어게임' if re.search(r'<h2 id="h-academy">[^<]*단어게임', s) else '온라인 학습지'
    msg = (f'시험 범위 지문마다 해석·단어·마인드맵·변형 문제까지 담은 {what}을 만들고 있어요. '
           '더 많은 자료는 자료실에서, 수업 소식은 블로그와 인스타그램에서, 학원 소개와 설명회 소식은 홈페이지에서 볼 수 있어요.')
    s, k = re.subn(r'(<h2 id="h-academy">[^<]*</h2>\s*<p>)[^<]*(</p>)', lambda m: m.group(1) + msg + m.group(2), s, count=1); n += k
    # 버튼
    def btn(cls, href, title, sub, ext=False, i=''):
        t = ' target="_blank" rel="noopener"' if ext else ''
        idv = f' id="{i}"' if i else ''
        return f'      <a class="{cls}"{idv} href="{href}"{t}><b>{title}</b><small>{sub}</small></a>\n'
    new_ctas = ('<div class="ctas">\n'
                + btn('primary', lib, '자료실', '다른 학습지 보기')
                + btn('ghost', BLOG, '블로그', '수업 소식 보기', True, 'go-blog')
                + btn('ghost', INSTA, '인스타그램', '학원 일상 보기', True, 'go-insta')
                + btn('ghost', home, '홈페이지', '학원 소개·설명회')
                + btn('ghost', PLACE, '네이버 플레이스', '상담·위치 보기', True, 'go-place')
                + '    </div>')
    s, k = re.subn(r'<div class="ctas">\s*<a class="primary"[\s\S]*?</div>(?:\s*<p class="more">[\s\S]*?</p>)?', lambda m: new_ctas, s, count=1); n += k
    # 공유 안내 줄: 단어게임 템플릿에는 빠져 있어서 넣는다(교과서·부교재 페이지는 lock.mjs가 '학원 밖 배포 금지' 문구로 바꾼다)
    if 'class="share"' not in s:
        thing = '단어게임' if what != '온라인 학습지' else '온라인 학습지'
        s, k = re.subn(r'(<div class="ctas">[\s\S]*?</div>)', lambda m: m.group(1) + f'\n    <p class="share">도움이 됐다면 친구에게도 이 {thing} 링크를 공유해 주세요!</p>', s, count=1)
    css = CTA_CSS
    if '/* brand-ctas */' in s:
        s = re.sub(r'/\* brand-ctas \*/[^\n]*', lambda m: css, s, count=1)
    else:
        k = 0
        for anchor in (r'(\.promo \.share\{[^}]*\})', r'(\.promo \.ctas a\.ghost\{[^}]*\})', r'(\.ctas a\.ghost\{[^}]*\})'):
            s, k = re.subn(anchor, lambda m: m.group(1) + '\n' + css, s, count=1)
            if k:
                break
        if not k:
            return 'FAIL(버튼 CSS 자리 없음)'
    if n != 3:
        return f'FAIL(바꾼 곳 {n}/3)'
    open(path, 'w', encoding='utf8').write(s)
    return f'ok (홈 {home})'


if __name__ == '__main__':
    for p in sys.argv[1:]:
        print(p, convert(p))
