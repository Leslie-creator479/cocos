"""블로그 발행함 아티팩트 만들기 (원장님 결정 2026-11-11: 블로그 원고는 모두 네이버 서식 + 그림 한 장씩 복사)

원고 종류마다 아티팩트 하나(발행함)를 두고 같은 주소에 다시 올린다. 아티팩트 개수가 늘지 않는다.
  발행함 설정  _tools/blog_box/<종류>.json   (url = 발행함 아티팩트 주소, 처음 만들 때는 비워 둠)
  화면 틀      _tools/blog_box/template.html (그 방의 '학교별 한 장 발행' 아티팩트와 같은 화면, 서식은 cocos-naver-blog-format 스킬)

원고 글은 지금처럼 각 도구가 만드는 홈페이지 원고 페이지(tools/…/index.html의 var D)에서 읽는다.
그림은 저장소에 올리지 않고 발행함 아티팩트의 파일(img/<slug>/<파일>)로 함께 올린다.

    python3 _tools/blog_box.py _tools/blog_box/<종류>.json -o <스크래치>/<종류>.html
    → <스크래치>/<종류>.files.json 이 함께 생긴다(이번에 올릴 그림 목록).
    → Artifact 발행: file_path=<종류>.html, files=<files.json 내용>, url=설정의 url(처음이면 빼고 icon을 넣음)
      처음 만든 뒤 받은 주소를 설정 파일 url에 적고 커밋한다.
    그림은 한 번 올리면 아티팩트에 남으므로, 다시 올릴 때는 새 글의 그림만 있으면 된다
    (files에 없는 그림은 그대로 남는다. 내린 글의 그림을 지우려면 files에 null).

설정 파일
  title   발행함 이름(예 "시험 분석 블로그 발행함")    badge  글 카드의 주황 칩 앞말(예 "시험 분석")
  url     발행함 아티팩트 주소
  posts   [{"page": "tools/blog/<slug>/index.html",   원고 페이지(이 페이지의 D를 읽음)
            "name": "성일고 1학년",                      맨 위 칩·글 카드 이름
            "imgdir": "그림 폴더(이번에 올릴 때만)",      없으면 그림은 이미 올라가 있다고 봄
            "thumb": "대표.png"}]                        [대표 이미지]처럼 파일 이름이 없는 자리일 때만
          블로그에 올린 글은 posts에서 빼고 다시 올린다(원고 글은 홈페이지 원고 페이지에 남아 있음).
"""
import argparse, html, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TPL = os.path.join(ROOT, '_tools', 'blog_box', 'template.html')
IMG = re.compile(r'^\[(대표 )?이미지(?:\s*[:：]\s*(.+?))?\]$')


def load_D(page):
    s = open(os.path.join(ROOT, page), encoding='utf8').read()
    i = s.index('var D=') + 6
    D, _ = json.JSONDecoder().raw_decode(s[i:])
    return D


def list_block(D):
    h, t = [], []
    for i, g in enumerate(D.get('groups') or []):
        if i:
            h.append('<p><br></p>')
        h.append('<p><span style="color:#000000"><b>[' + html.escape(g['g']) + ']</b></span></p>')
        t.append('[' + g['g'] + ']')
        for it in g['items']:
            h.append('<p><span style="font-weight:normal"><a href="%s" target="_blank" rel="noopener">%s</a></span></p>' % (html.escape(it[1]), html.escape(it[0])))
            t.append(it[0] + '\r\n' + it[1])
    return {'k': 'raw', 'h': ''.join(h), 't': '\r\n'.join(t)}


def convert(D, slug, thumb_name=None):
    """옛 원고 블록(D.body) → 발행함 글(parts). 그림 자리에서 본문을 끊는다."""
    parts, cur, thumb, need = [], [], None, []
    for b in D['body']:
        k, t = b[0], (b[1] if len(b) > 1 else '')
        m = IMG.match(str(t).strip()) if k == 'p' else None
        if k == 'br':
            continue
        if m:
            name = m.group(2) or (thumb_name if m.group(1) else None)
            if not name:
                sys.exit(f'{slug}: 그림 자리 "{t}"에 파일 이름이 없음(설정에 thumb를 넣거나 원고에 파일 이름을 적을 것)')
            need.append(name)
            if m.group(1) and thumb is None and not parts and not cur:
                thumb = name
            else:
                parts.append({'body': cur, 'img': name, 'src': f'img/{slug}/{name}'})
                cur = []
            continue
        if k in ('b', 'ser'):
            cur.append({'k': 'h', 't': re.sub(r'^■\s*', '', t)})
        elif k == 'hot':
            cur.append({'k': 's' if re.match(r'^[①-⑳]', t) else 'hot', 't': t})
        elif k == 'note':
            cur.append({'k': 'note', 't': t})
        elif k == 'link':
            cur.append({'k': 'a', 't': t, 'u': b[2]})
        elif k == 'list':
            if D.get('groups'):
                cur.append(list_block(D))
        elif k == 'table':
            cur.append({'k': 'tbl', 'rows': t})
        else:
            cur.append({'k': 'p', 't': t})
    parts.append({'body': cur, 'img': None})
    return parts, thumb, need


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('config')
    ap.add_argument('-o', required=True)
    a = ap.parse_args()
    C = json.load(open(a.config, encoding='utf8'))
    posts, files, missing = [], {}, []
    for n, P in enumerate(C['posts'], 1):
        slug = os.path.basename(os.path.dirname(P['page']))
        D = load_D(P['page'])
        parts, thumb, need = convert(D, slug, P.get('thumb'))
        posts.append({'no': n, 'name': P['name'], 'full': P['name'], 'badge': f"{C['badge']} {n}",
                      'title': D['title'], 'tags': ' '.join('#' + x.lstrip('#') for x in D['tags'].split()),
                      'thumb': thumb, 'thumb_src': f'img/{slug}/{thumb}' if thumb else None, 'parts': parts})
        d = P.get('imgdir')
        for name in need:
            if d and os.path.exists(os.path.join(d, name)):
                files[f'img/{slug}/{name}'] = os.path.abspath(os.path.join(d, name))
            else:
                missing.append(f'img/{slug}/{name}')
    s = open(TPL, encoding='utf8').read()
    s = s.replace('__TITLE__', html.escape(C['title'])).replace('__H1__', html.escape(C['title']) + ' — 네이버에 올리기')
    s = s.replace('__POSTS__', json.dumps(posts, ensure_ascii=False).replace('</', '<\\/'))
    open(a.o, 'w', encoding='utf8').write(s)
    fj = re.sub(r'\.html$', '', a.o) + '.files.json'
    json.dump(files, open(fj, 'w', encoding='utf8'), ensure_ascii=False, indent=1)
    print(a.o, '· 글', len(posts), '편 · 이번에 올릴 그림', len(files), '장 →', fj)
    if missing:
        print('그림 파일이 없음(이미 아티팩트에 올라가 있어야 함):', *missing, sep='\n  ')


if __name__ == '__main__':
    main()
