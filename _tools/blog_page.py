"""블로그 원고 페이지 만들기 (2026-11-08, 원장님 결정: 블로그 글은 모두 이 원고 페이지로 드린다)

전용 도구가 없는 블로그 글(모의고사 학습지 글, 안내 글, 연재 글 등)을 홈페이지 원고 페이지로 만든다.
제목 복사 · 글 전체 복사(링크·굵게·표가 네이버 에디터에 그대로 붙음) · 태그 복사 버튼, 바로가기 목록(있을 때만).

    python3 _tools/blog_page.py 원고.json tools/blog/<slug>/index.html
    → 그다음 build_tools_index.py → seo.py → 커밋·푸시. 이미지는 저장소에 올리지 않고 원장님께 보낸다.

원고.json
  name   페이지 머리 제목(예 "2026년 10월 고1 학습지 블로그 원고")
  title  블로그 글 제목            tags  태그(띄어쓰기로 구분, # 없이)
  meta   글 칸 아래 작은 줄(없으면 '제목·본문·태그 · 이미지 N장'을 자동으로)
  body   블록 목록:
           ["p", 문단]  ["b", 굵은 소제목]  ["br"]  ["link", 보이는 글, 주소]
           ["ser", 연재 표시(네이비 굵게)]  ["hot", 강조(주황 굵게)]  ["note", 회색 설명]
           ["table", [[머리칸…], [칸…], …]]  ["list"] (바로가기 목록을 본문 그 자리에)
         이미지 자리는 ["p", "[대표 이미지: 파일.png]"], ["p", "[이미지: 파일.png]"]
  groups (선택) 바로가기 목록 [{"g": 묶음 이름, "items": [[보이는 글, 주소], …]}]
  url    (선택) '링크 복사' 버튼 주소       listMeta (선택) 바로가기 칸 아래 작은 줄
링크는 블로그에 붙이므로 https://cocosedu.kr/… 전체 주소로 쓴다.
"""
import html, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TPL = os.path.join(ROOT, 'tools', 'templates', 'blog', 'index.html')

src, dst = sys.argv[1], sys.argv[2]
C = json.load(open(src, encoding='utf8'))
for k in ('name', 'title', 'tags', 'body'):
    assert C.get(k), f'원고.json에 {k}가 없음'
groups = C.get('groups') or []
# 대표 이미지 자리 바로 뒤에 원장님께 드리는 안내(「네이버는 … 대표 …」)가 섞여 들어오면 뺀다(2026-11-08, 연재 1편에서 실제로 샘)
body = []
for i, b in enumerate(C['body']):
    prev = C['body'][i - 1] if i else None
    if prev and prev[0] == 'p' and str(prev[1]).startswith('[대표 이미지') and b[0] in ('p', 'note') \
            and '네이버' in str(b[1]) and '대표' in str(b[1]):
        print('뺀 줄(원장님께 드리는 안내):', b[1][:40])
        continue
    body.append(b)
C['body'] = body
imgs = sum(1 for b in C['body'] if b[0] == 'p' and re.match(r'\[(대표 )?이미지', str(b[1])))
D = {"title": C['title'], "tags": C['tags'].replace('#', ''),
     "meta": C.get('meta') or ('제목·본문·태그' + (f' · 이미지 {imgs}장' if imgs else '')),
     "url": C.get('url', ''), "count": sum(len(g['items']) for g in groups), "groups": groups,
     "listMeta": C.get('listMeta', ''), "body": C['body']}

s = open(TPL, encoding='utf8').read()
i = s.find('var D=') + 6
_, end = json.JSONDecoder().raw_decode(s[i:])
s = s[:i] + json.dumps(D, ensure_ascii=False) + s[i + end:]
s = re.sub(r'<title>[^<]*</title>', f"<title>{html.escape(C['name'])}</title>", s, count=1)
s = re.sub(r'<h1>[^<]*</h1>', f"<h1>{html.escape(C['name'])}</h1>", s, count=1)
if not groups:
    a = '<li>목록에서 한 줄을 눌러 링크가 제대로 열리는지 확인하고 발행해요.</li>'
    assert a in s, '원고 틀이 바뀜'
    s = s.replace(a, '<li>[이미지: …] 자리마다 같은 이름의 이미지를 끼우고 그 줄은 지운 뒤 발행해요.</li>')
os.makedirs(os.path.dirname(dst) or '.', exist_ok=True)
open(dst, 'w', encoding='utf8').write(s)
print(dst, '· 본문', len(C['body']), '블록 · 이미지', imgs, '장 · 바로가기', D['count'], '개 · 태그', len(D['tags'].split()), '개')
