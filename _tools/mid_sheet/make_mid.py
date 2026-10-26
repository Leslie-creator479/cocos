"""중등 온라인 학습지 만들기 (2026-10-24, 원장님과 정함).
고등 학습지와 기능은 같고, 화면만 아기자기한 중등 테마(mid_theme.css)이며 확인 퀴즈 15문항이 중등형이다.

사용법 (저장소 폴더에서):
  COCOS_LOCK_PW=… python3 _tools/mid_sheet/make_mid.py data.js "<title>" 출력.html [--base 풀린_학습지.html]
  - data.js: `var DATA = { … };` 한 덩어리 (chips·h1·enTitle·gist·footer·brief·sentences·gloss·vocab·map·quiz·order)
  - <title>: [코코스학원] 중2 동아(윤정미) 1과 본문 1번 · 인호의 NGO 가입
  - 틀은 이미 올린 중등 학습지(textbook/m2dayoon/1/1)를 임시로 풀어서 쓴다(--base로 다른 틀을 줄 수도 있다).
  - 겉틀은 떼고 <title>부터 시작하는 조각을 만든다 → wrap.py로 감싼다.
  - AUDIO·SAUDIO는 비운다(build_audio.py·build_saudio.py로 채운다). 끝의 print-sheet.js 줄은 뺀다(seo.py가 다시 붙인다).
  - mid_theme.css를 넣고, 확인 퀴즈 유형 표시에 색을 나누는 data-k를 붙인다(몇 번 실행해도 같다).
"""
import os, re, shutil, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
args = sys.argv[1:]
base = None
if '--base' in args:
    i = args.index('--base'); base = args[i + 1]; del args[i:i + 2]
data, title, out = open(args[0], encoding='utf8').read().strip(), args[1], args[2]
if not base:
    src = os.path.join(ROOT, 'textbook/m2dayoon/1/1/index.html')
    base = os.path.join(tempfile.mkdtemp(), 'base.html'); shutil.copy(src, base)
    if 'id="cocos-lock"' in open(base, encoding='utf8').read():
        assert os.environ.get('COCOS_LOCK_PW'), 'COCOS_LOCK_PW(학원생 비밀번호)를 함께 주세요'
        subprocess.run(['node', os.path.join(ROOT, '_tools/lock.mjs'), 'unlock', base], check=True, stdout=subprocess.DEVNULL)
t = open(base, encoding='utf8').read()
t = t[t.index('<title>'):]
t = t[:t.rindex('</body>')].rstrip() + '\n' if '</body>' in t else t
t = re.sub(r'\n?<!-- naver-analytics -->[\s\S]*?<!-- /naver-analytics -->\n?', '\n', t)
t = re.sub(r'\n<script src="[^"]*print-sheet\.js"></script>\s*$', '\n', t)
t = re.sub(r'<title>.*?</title>', '<title>' + title + '</title>', t, count=1)
link = '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Jua&family=Nunito:wght@500;600;700;800&display=swap">'
if 'family=Jua' not in t:
    i = t.index('<style>'); t = t[:i] + link + '\n' + t[i:]
theme = open(os.path.join(HERE, 'mid_theme.css'), encoding='utf8').read()
t = re.sub(r'/\* ==== MID THEME:START[\s\S]*?MID THEME:END ==== \*/\n?', '', t)
assert t.count('</style>') == 1
t = t.replace('</style>', theme + '</style>')
a = "'<span class=\"type'+(q.type.indexOf('변형')>-1?' var':'')+'\">'"
b = "'<span class=\"type'+(q.type.indexOf('변형')>-1?' var':'')+'\" data-k=\"'+q.type.split(' ')[0]+'\">'"
if b not in t:
    assert t.count(a) == 1, 'type span'; t = t.replace(a, b)
# 문장 배열: 따옴표로 시작하는 문장도 첫 글자를 소문자로 (첫 어구 힌트 막기, 2026-10-24)
LC_OLD = "function lc(t,it){ if(it.keep||/^I\\b/.test(t)) return t; return t.charAt(0).toLowerCase()+t.slice(1); }"
LC_NEW = "function lc(t,it){ if(it.keep) return t; var m=t.match(/^([\\u201c\\u2018\"'(]*)(.)/); if(!m||/^I\\b/.test(t.slice(m[1].length))) return t; return m[1]+m[2].toLowerCase()+t.slice(m[0].length); }"
t = t.replace(LC_OLD, LC_NEW)
# 문장 배열 항목에 en·ko가 있으면 그 문장으로 낸다(한 줄에 문장이 여럿일 때 문장 하나씩, 2026-10-26)
t = t.replace("var it=cur.it, s=S[it.s-1], total=O.length", "var it=cur.it, s=it.en?{en:it.en,ko:it.ko}:S[it.s-1], total=O.length")
t, n = re.subn(r'(/\* ==== DATA:START ==== \*/\n)[\s\S]*?(\n/\* ==== DATA:END ==== \*/)', lambda m: m.group(1) + data + m.group(2), t)
assert n == 1
t = re.sub(r'(/\* ==== AUDIO:START ==== \*/\n)[\s\S]*?(\n/\* ==== AUDIO:END ==== \*/)', lambda m: m.group(1) + 'var AUDIO = {};' + m.group(2), t)
t = re.sub(r'(/\* ==== SAUDIO:START ==== \*/\n)[\s\S]*?(\n/\* ==== SAUDIO:END ==== \*/)', lambda m: m.group(1) + 'var SAUDIO = [];' + m.group(2), t)
os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
open(out, 'w', encoding='utf8').write(t)
print(out, len(t.encode()) // 1024, 'KB')
