# 블로그 원고 페이지 만들기: 게시된 단어게임 블로그 원고(틀)의 D만 바꾼다.
# 사용: python3 -I make_blog.py template.html blog.json out.html
# blog.json: {"page_title":"2025 10월 고2 단어게임 블로그 원고","h1":"2025년 10월 고2 단어게임 블로그 원고",
#   "url":게임주소,"title":…,"tags":…,"count":지문수,"groups":[{"g":"범위별 바로가기","items":[[이름,주소],…]},…],"body":[[종류,…],…]}
# body 종류: ["p",문장] ["b",소제목(앞에 빈 줄)] ["link",보이는글,주소] ["br"](빈 줄) ["list"](바로가기 목록 자리, 앞뒤 빈 줄)
import json, re, sys
tpl, bj, out = sys.argv[1:4]
s = open(tpl, encoding='utf8').read()
if '<body>' in s[:3000]: s = s.split('<body>', 1)[1].rsplit('</body></html>', 1)[0].lstrip('\n')
B = json.load(open(bj, encoding='utf8'))
D = {k: B[k] for k in ('url', 'title', 'tags', 'count', 'groups', 'body')}
s = re.sub(r'var D=\{.*?\};\nfunction \$', lambda m: 'var D=' + json.dumps(D, ensure_ascii=False) + ';\nfunction $', s, count=1, flags=re.S)
s = re.sub(r'<title>[^<]*</title>', '<title>' + B['page_title'] + '</title>', s, count=1)
s = re.sub(r'<h1>[^<]*</h1>', '<h1>' + B['h1'] + '</h1>', s, count=1)
open(out, 'w', encoding='utf8').write(s)
open(out + '.js', 'w', encoding='utf8').write(re.search(r'<script>(.*)</script>', s, re.S).group(1))
print('ok', len(s))
