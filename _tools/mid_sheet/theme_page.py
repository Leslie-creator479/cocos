"""중등 동의어·반의어·단어게임 페이지에 중등 테마 입히기 (2026-10-24, 원장님 요청: 구성은 고등판 그대로, 화면만 중등 학습지처럼).
사용법: python3 _tools/mid_sheet/theme_page.py syn|game 파일.html [...]
  - 동의어·반의어(gen_quiz.py + finish_page.py로 만든 것)나 단어게임(make_game.py로 만든 것)에
    Jua·Nunito 글꼴 링크와 mid_common.css + mid_syn.css(또는 mid_game.css)를 넣는다.
  - 몇 번 돌려도 같다(넣어 둔 MID THEME 묶음을 지우고 새로 넣는다). 잠긴 페이지는 먼저 unlock.
  - gen_quiz.py·make_game.py로 다시 만들면 테마가 빠지니 이 도구를 다시 돌린다.
"""
import os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
kind, files = sys.argv[1], sys.argv[2:]
assert kind in ('syn', 'game'), 'syn 또는 game'
theme = open(os.path.join(HERE, 'mid_common.css'), encoding='utf8').read() + open(os.path.join(HERE, f'mid_{kind}.css'), encoding='utf8').read()
LINK = '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Jua&family=Nunito:wght@500;600;700;800&display=swap">'
for f in files:
    t = open(f, encoding='utf8').read()
    assert 'id="cocos-lock"' not in t, f + ': 잠긴 페이지는 먼저 unlock'
    if 'family=Jua' not in t:
        i = t.index('<style>'); t = t[:i] + LINK + '\n' + t[i:]
    t = re.sub(r'/\* ==== MID THEME:START[\s\S]*?MID THEME:END ==== \*/\n?', '', t)
    i = t.index('</style>'); t = t[:i] + theme + t[i:]
    open(f, 'w', encoding='utf8').write(t)
    print('중등 테마', kind, f)
