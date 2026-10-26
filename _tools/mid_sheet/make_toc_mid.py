"""중등 과(課) 목차 만들기 (2026-10-24).
사용법: COCOS_LOCK_PW=… python3 _tools/mid_sheet/make_toc_mid.py toc.json "<title>" 출력.html [--base 풀린_목차.html]
  toc.json: {"chips":["중2 동아(윤정미) 1과","4개 지문"], "h1":"중2 동아(윤정미) 1과 온라인 학습지", "gist":"…", "footer":"지문 출처: …",
             "items":[{"g":"1과 <과 제목>","n":"본문 1번","t":"핵심 개념","h":"DATA.h1","e":"DATA.enTitle","u":"1/"}, …]}
  <title>: [코코스학원] 중2 동아(윤정미) 1과 온라인 학습지 목차
  틀은 이미 올린 중등 목차(textbook/m2dayoon/1)를 임시로 풀어서 쓴다.
"""
import json, os, re, shutil, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
args = sys.argv[1:]
base = None
if '--base' in args:
    i = args.index('--base'); base = args[i + 1]; del args[i:i + 2]
toc, title, out = json.load(open(args[0], encoding='utf8')), args[1], args[2]
if not base:
    base = os.path.join(tempfile.mkdtemp(), 'toc.html'); shutil.copy(os.path.join(ROOT, 'textbook/m2dayoon/1/index.html'), base)
    if 'id="cocos-lock"' in open(base, encoding='utf8').read():
        assert os.environ.get('COCOS_LOCK_PW'), 'COCOS_LOCK_PW(학원생 비밀번호)를 함께 주세요'
        subprocess.run(['node', os.path.join(ROOT, '_tools/lock.mjs'), 'unlock', base], check=True, stdout=subprocess.DEVNULL)
t = open(base, encoding='utf8').read()
t = t[t.index('<title>'):]
t = t[:t.rindex('</body>')].rstrip() + '\n' if '</body>' in t else t
t = re.sub(r'\n?<!-- naver-analytics -->[\s\S]*?<!-- /naver-analytics -->\n?', '\n', t)
t = re.sub(r'<title>.*?</title>', '<title>' + title + '</title>', t, count=1)
link = '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Jua&family=Nunito:wght@500;600;700;800&display=swap">'
if 'family=Jua' not in t:
    i = t.index('<style>'); t = t[:i] + link + '\n' + t[i:]
theme = open(os.path.join(HERE, 'mid_theme.css'), encoding='utf8').read()
extra = ('.toc a{border-width:2px;border-radius:18px;box-shadow:0 4px 0 var(--line)}\n.toc .no{border-radius:12px;background:var(--mint-soft);color:var(--mint-ink)}\n'
         '.toc .ti{font-family:var(--round);font-weight:400}\n.toc .en{font-style:normal}\n.lesson h2::before{content:"📘";background:var(--accent-soft)}\n.search{border-width:2px;border-radius:999px}\n')
t = re.sub(r'/\* ==== MID THEME:START[\s\S]*?MID THEME:END ==== \*/\n?', '', t)
t = t.replace('</style>', theme.replace('/* ==== MID THEME:END ==== */', extra + '/* ==== MID THEME:END ==== */') + '</style>', 1)
t, n = re.subn(r'var TOC = [\s\S]*?;\n/\* ==== TOC:END', lambda m: 'var TOC = ' + json.dumps(toc, ensure_ascii=False, indent=1) + ';\n/* ==== TOC:END', t)
assert n == 1
if any(str(x.get('n', '')).startswith('대화문') for x in toc['items']):  # 대화문 확인 퀴즈는 10문항(2026-10-26)
    t = t.replace('<span class="pill">확인 퀴즈 15문항</span>', '<span class="pill">확인 퀴즈(본문 15 · 대화문 10문항)</span>')
t = re.sub(r'placeholder="제목·주제로 찾기 \(예: [^)]*\)"', 'placeholder="제목·주제로 찾기 (예: 핵심어, 영어 낱말)"', t)
os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
open(out, 'w', encoding='utf8').write(t); print(out, len(t.encode()) // 1024, 'KB')
