# 중등부·공통 문구 시안: 지금 홈페이지에서 '학원이 시킨다' 말투만 '기본 설계·코코스가 드리는 것'으로 바꾼 판 (고등부·원장 인사는 그대로)
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b_text
from build_b import prep, ROOT
t = open(f'{ROOT}/index.html', encoding='utf-8').read()
t = b_text.apply(t, letter=False)
js = b_text.JS.replace('B 시안에서 바뀐 문장', '이 시안에서 바뀐 문장').replace("'B 시안 문장 보기'", "'시안 문장 보기'")
t = t.replace('</body>', js + '</body>', 1)
flag = '.preview-flag{position:fixed;left:12px;bottom:12px;z-index:99;background:#8A6C3C;color:#fff;font:600 12px/1 var(--sans);letter-spacing:.06em;padding:9px 12px}'
t = t.replace('</style>', b_text.CSS + flag + '</style>', 1)
t = prep(t, '중등부·공통 문구 시안 — 코코스학원', '중등부·공통 문구 시안 · 실제 홈페이지 아님')
os.makedirs(f'{ROOT}/preview/mid', exist_ok=True)
open(f'{ROOT}/preview/mid/index.html', 'w', encoding='utf-8').write(t)
print('mid ok')
