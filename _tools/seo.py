"""검색 노출 정리: 모의고사(학력평가) 자료만 검색에 열고, 나머지 학습 자료는 noindex로 막는다.

선생님 결정(2026-10-14): 교과서·부교재(올림포스 등)·학교별 시험 범위 자료는 저작권 때문에 네이버·구글 검색에
나오지 않게 한다. 학원생은 링크로 지금처럼 볼 수 있다(잠금이 아니라 '검색에 올리지 말라'는 표시다).

규칙(기본은 막기, 아래 목록에 맞는 것만 검색에 연다):
  검색에 연다 : 홈페이지 첫 화면, 자료실(library), study/<연도>-<월>-g<학년>(목차·지문),
                syn/<연도>-<월>-g<학년>, game/<연도>-<월>-g<학년>
  noindex     : 그 밖의 모든 index.html (textbook/, study/olympos…, 앞으로 생길 study/suteuk 같은 부교재,
                school/, 교과서·학교별 syn·game, tools/, preview/ …)

하는 일 (몇 번 돌려도 결과가 같다. 다른 방에서 새 페이지를 올린 뒤 다시 돌리면 빠진 것만 고친다):
  1) noindex 대상 페이지 <head>에 <meta name="robots" content="noindex"> 넣기, 검색 대상에서 이 스크립트가 넣은 표시는 빼기
  2) sitemap.xml 다시 만들기(검색에 여는 페이지만)
  0) 학습지에 'PDF로 저장' 버튼 붙이기(print_btn.py, 잠긴 페이지는 건너뜀)
  3) robots.txt 만들기: HTML이 아니라 표시를 달 수 없는 것(_tools/, CLAUDE.md, README.md)만 막고 sitemap 위치를 알린다.
     noindex 폴더를 robots.txt로 막지 않는 이유: 막으면 로봇이 페이지를 못 열어 noindex 표시를 못 보고,
     다른 곳(블로그 등)에 걸린 링크만 보고 주소를 검색 결과에 올릴 수 있다.

사용법: python3 _tools/seo.py          (저장소 폴더에서, 인자 없음)
        python3 _tools/seo.py --check  (고치지 않고 개수만 보기)
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = 'https://cocosedu.kr/'
META = '<meta name="robots" content="noindex">'
MOCK = r'\d{4}-\d{2}-g\d'
OPEN = [re.compile(p) for p in (
    r'^$', r'^library$',
    rf'^study/{MOCK}(/[^/]+)?$',
    rf'^syn/{MOCK}$', rf'^game/{MOCK}$',
)]
SKIP_DIRS = {'.git', '_tools', 'node_modules'}


def is_open(page):
    return any(p.match(page) for p in OPEN)


def pages():
    for d, dirs, files in os.walk(ROOT):
        dirs[:] = sorted(x for x in dirs if x not in SKIP_DIRS)
        if 'index.html' in files:
            rel = os.path.relpath(d, ROOT).replace(os.sep, '/')
            yield ('' if rel == '.' else rel), os.path.join(d, 'index.html')


def has_noindex(s):
    head = s[:s.find('</head>')] if '</head>' in s[:20000] else s[:4000]
    return re.search(r'<meta\s+name=["\']?robots["\']?\s+content=["\'][^"\']*noindex', head, re.I) is not None


def add_noindex(s):
    m = re.search(r'<meta\s+charset=[^>]*>', s[:3000], re.I)
    if m:
        return s[:m.end()] + META + s[m.end():]
    m = re.search(r'<head[^>]*>', s[:3000], re.I)
    if m:
        return s[:m.end()] + META + s[m.end():]
    return None


def main():
    check = '--check' in sys.argv
    # 학습지 'PDF로 저장' 버튼·안내 카드 오타도 함께 정리(_tools/print_btn.py, 선생님 결정 2026-10-15)
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import print_btn
    print_btn.run(check=check, quiet=True)
    opened, closed, changed, failed = [], [], [], []
    for page, path in pages():
        s = open(path, encoding='utf8').read()
        if is_open(page):
            opened.append(page)
            if META in s and not page.startswith(('tools', 'preview')):
                if not check:
                    open(path, 'w', encoding='utf8').write(s.replace(META, '', 1))
                changed.append('열기 ' + page)
        else:
            closed.append(page)
            if not has_noindex(s):
                t = add_noindex(s)
                if t is None:
                    failed.append(page); continue
                if not check:
                    open(path, 'w', encoding='utf8').write(t)
                changed.append('막기 ' + page)
    if not check:
        urls = '\n'.join(f'  <url><loc>{BASE}{p + "/" if p else ""}</loc></url>' for p in sorted(opened))
        open(os.path.join(ROOT, 'sitemap.xml'), 'w', encoding='utf8').write(
            '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + urls + '\n</urlset>\n')
        open(os.path.join(ROOT, 'robots.txt'), 'w', encoding='utf8').write(
            'User-agent: *\nDisallow: /_tools/\nDisallow: /CLAUDE.md\nDisallow: /README.md\n\n'
            f'Sitemap: {BASE}sitemap.xml\n')
    print(f'검색에 엶 {len(opened)}쪽 · noindex {len(closed)}쪽 · 이번에 고친 쪽 {len(changed)}' + (' (확인만)' if check else ''))
    if failed:
        print('head를 못 찾아 고치지 못함:', failed)
    for c in changed[:15]:
        print(' ', c)
    if len(changed) > 15:
        print(f'  … 외 {len(changed) - 15}쪽')


if __name__ == '__main__':
    main()
