"""코코스 중등 문법 페이지 만들기 (2026-11-06, 원장님과 정함: 독해 회차와 엮고, 자주 틀리는 문장으로 끄는 질문형 제목).

화면은 공개 중등 독해 학습지(study/reading-m2-01/4)의 머리·글꼴·스타일·학원 카드·바닥글을 그대로 쓰고,
가운데 칸만 문법용으로 바꾼다: 먼저 풀어 보기(O/X) → 한눈에 정리 → 지문 속 문장(녹음) → 단계별 문제 →
틀린 곳 고쳐 쓰기 → 조건 영작(서술형 감점 체크) → 문장 배열 → (지난 문법 복습) → 독해로 이어 보기.

사용법 (저장소 폴더에서):
  python3 _tools/mid_sheet/make_gram.py data.js "<title>" 출력.html [--base 독해_학습지.html]
  - data.js: `var DATA = { … };` (chips·h1·enTitle·gist·footer·hook·rule·sentences·quiz·fix·write·check·order·review·links)
    sentences는 build_saudio.py가 읽는 꼴(한 줄에 `{ en: '…', …},`, 끝은 줄 첫머리 `  ],`)로 쓴다.
  - 다음: build_saudio.py 출력.html → node check_gram.js 출력.html → wrap.py → public_notice.py
  - 주소는 study/grammar-m<학년>-<회>/ (공개 규칙 자동).
"""
import os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
args = sys.argv[1:]
base = os.path.join(ROOT, 'study/reading-m2-01/4/index.html')
if '--base' in args:
    i = args.index('--base'); base = args[i + 1]; del args[i:i + 2]
data, title, out = open(args[0], encoding='utf8').read().strip(), args[1], args[2]
t = open(base, encoding='utf8').read()
assert 'id="cocos-lock"' not in t, '잠기지 않은 공개 학습지를 틀로 주세요'
head = t[t.index('<title>'):t.index('<div class="wrap">')]
head = re.sub(r'<title>.*?</title>', '<title>' + title + '</title>', head, count=1)
css = open(os.path.join(HERE, 'gram.css'), encoding='utf8').read()
head = re.sub(r'/\* ==== GRAM:START[\s\S]*?GRAM:END ==== \*/\n?', '', head)
i = head.rindex('</style>'); head = head[:i] + css + head[i:]
tail = t[t.index('<section id="academy"'):t.index('</footer>') + len('</footer>')]
tail = re.sub(r'<p class="copy">[\s\S]*?</p>', '<p class="copy">© <span id="yr">2026</span> 코코스학원. 이 온라인 학습지의 설명·예문·문제·해설은 코코스학원이 만들었어요.</p>', tail, count=1)
tail = tail.replace('시험 범위 지문마다 해석·단어·마인드맵·변형 문제까지 담은 온라인 학습지를 만들고 있어요.',
                    '코코스가 직접 쓴 독해 지문과 그 지문으로 배우는 문법 학습지를 매주 새로 올려요.')
tail = tail.replace('../../../', '../../')  # 지문 학습지(3단)와 달리 문법 페이지는 study/grammar-m…/(2단)
has_review = re.search(r'\breview\s*:\s*\[\s*\{', data) is not None

def sec(id_, h, p, inner, extra=''):
    return (f'  <section id="{id_}" aria-labelledby="h-{id_}">\n    <div class="sec-head"><div><h2 id="h-{id_}">{h}</h2><p{p[1]}>{p[0]}</p></div>{extra}</div>\n'
            f'    {inner}\n  </section>\n')

nav = [('hook', '먼저 풀어 보기'), ('rule', '한눈에 정리'), ('examples', '지문 속 문장'), ('quiz', '단계별 문제'),
       ('fix', '고쳐 쓰기'), ('write', '조건 영작'), ('order', '문장 배열')] + ([('review', '지난 문법 복습')] if has_review else []) + [('reading', '독해로 이어 보기'), ('academy', '코코스학원')]
body = ('<div class="wrap">\n  <header>\n'
        '    <a class="brand" href="../../" title="코코스학원 홈페이지로"><span class="logo" role="img" aria-label="코코스학원"></span><span>코코스학원 온라인 학습지 · 학습과 컨설팅을 하나로</span></a>\n'
        '    <div class="src" id="chips"></div>\n    <h1 id="h1"></h1>\n    <p class="en-title" id="en-title"></p>\n    <p class="gist" id="gist"></p>\n'
        '    <nav class="jump" aria-label="바로가기">' + ''.join(f'<a href="#{a}">{b}</a>' for a, b in nav) + '</nav>\n  </header>\n\n')
body += sec('hook', '먼저 풀어 보기', ('', ' id="hook-intro"'), '<div class="g-list" id="hook-list"></div>')
body += sec('rule', '한눈에 정리', ('개념을 먼저 짧게 정리했어요. 표의 함께 쓰는 말을 꼭 기억하세요.', ''), '<div class="r-grid" id="rule-cards"></div>\n    <div id="rule-table" style="margin-top:16px"></div>\n    <ul class="r-tips" id="rule-tips" style="margin-top:14px"></ul>')
body += sec('examples', '지문 속 문장', ('독해 지문에 실제로 나온 문장이에요. ▶를 누르면 읽어 줘요. 같은 일기 안에서 과거형과 현재완료가 어떻게 나뉘는지 보세요.', ''), '<div class="g-list" id="ex-list"></div>')
body += sec('quiz', '단계별 문제', ('기본 → 표준 → 심화 순서예요. 한 번 고르면 바로 채점돼요.', ''), '<div class="qs" id="qs"></div>', '<div class="score" id="score"></div>')
body += sec('fix', '틀린 곳 고쳐 쓰기', ('어법상 틀린 곳이 하나씩 있어요. 고친 문장 전체를 써서 확인해 보세요.', ''), '<div class="g-list" id="fix-list"></div>')
body += sec('write', '조건 영작', ('학교 서술형처럼 조건에 맞춰 써 보세요. 단어 수는 쓰는 동안 아래에 세어 줘요.', ''), '<div class="g-list" id="write-list"></div>\n    <div class="g-card" style="margin-top:14px"><span class="b-lab">서술형 감점 체크</span><ul class="g-check" id="write-check"></ul></div>')
body += sec('order', '문장 배열', ('해석을 보고 어구를 순서대로 눌러 영어 문장을 완성하세요. 기간·때를 나타내는 말(for ~, since ~)은 문장 끝에 두세요.', ''), '<div class="ord" id="ord"></div>')
if has_review:
    body += sec('review', '지난 문법 복습', ('지난 편에서 배운 문법을 다시 꺼내 봐요. 잊을 때쯤 다시 풀면 오래 기억에 남아요.', ''), '<div class="qs" id="rv"></div>', '<div class="score" id="rv-score"></div>')
body += sec('reading', '독해로 이어 보기', ('이 문법이 나온 독해 지문을 함께 읽어 보세요.', ''), '<div class="gl" id="links"></div>')
body += '\n  ' + tail + '\n</div>\n\n'
engine = open(os.path.join(HERE, 'gram_engine.js'), encoding='utf8').read()
script = ('<script>\n/* ==== DATA:START ==== */\n' + data + '\n/* ==== DATA:END ==== */\n'
          '/* ==== AUDIO:START ==== */\nvar AUDIO = {};\n/* ==== AUDIO:END ==== */\n'
          '/* ==== SAUDIO:START ==== */\nvar SAUDIO = [];\n/* ==== SAUDIO:END ==== */\n' + engine + '</script>\n')
page = head + '\n' + body + script
os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
open(out, 'w', encoding='utf8').write(page)
print(out, len(page.encode()) // 1024, 'KB')
