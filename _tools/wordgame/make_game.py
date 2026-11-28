# 단어게임 페이지 만들기: 게시된 단어게임(틀)의 DATA만 바꾼다.
# 사용: python3 -I make_game.py template.html game_data.json config.json out.html
# config.json: {"title":"[코코스학원] 2025 10월 고2 학평 단어게임","key":"cocos-wordgame-2025-10-g2","label":"2025 10월 고2",
#   "syn":"동의어·반의어 페이지 id(없으면 \"\")","meta":{"h1":…,"chips":[…],"gist":…,"links":[[이름,주소],…],"source":…},
#   "groups":[{"label":"18~26번","keys":["18",…]},…]}
import json, re, sys
tpl, gd, cfg, out = sys.argv[1:5]
s = open(tpl, encoding='utf8').read()
if '<body>' in s[:3000]: s = s.split('<body>', 1)[1].rsplit('</body></html>', 1)[0].lstrip('\n')
gd = json.load(open(gd, encoding='utf8')); c = json.load(open(cfg, encoding='utf8'))
a = s.index('/* ==== DATA:START ==== */'); b = s.index('/* ==== DATA:END ==== */')
head = s[a:s.index('var DATA = ', a)]
data = dict(key=c['key'], label=c['label'], syn=c.get('syn', ''), meta=c['meta'], groups=c.get('groups', []), P=gd['P'], W=gd['W'])
s = s[:a] + head + 'var DATA = ' + json.dumps(data, ensure_ascii=False, separators=(',', ':')) + ';\n' + s[b:]
s = re.sub(r'<title>[^<]*</title>', '<title>' + c['title'] + '</title>', s, count=1)
open(out, 'w', encoding='utf8').write(s)
open(out + '.js', 'w', encoding='utf8').write(re.search(r'<script>(.*)</script>', s, re.S).group(1))
print('ok', len(s))
