"""중등 '대화문' 온라인 학습지로 바꾸기 (2026-10-26, 원장님과 정함).
make_mid.py로 만든 중등 학습지(본문 틀)를 대화문 화면으로 고친다. 몇 번 실행해도 같다.

사용법: python3 _tools/mid_sheet/make_dlg.py <make_mid.py 결과.html>
  DATA.sentences는 '말하는 차례(턴)' 하나가 한 줄이다:
    { en: 'Thanks. I love playing it.', ko: '고마워. 나는 기타 치는 것을 정말 좋아해.', sp: 'B' }
    sp  = 말하는 사람(B 남학생 · G 여학생 · M 남자 어른 · W 여자 어른, 녹음 목소리도 이걸로 고른다)
    dn  = (선택) 짧은 대화가 여러 개일 때 그 대화의 첫 줄에 '대화 1'·'Wrap Up 1' 같은 이름표
  - 화면: 줄마다 말하는 사람 동그라미(B·G·M·W 색 구분), dn 이름표, '지문' → '대화문' 문구
  - 확인 퀴즈는 대화문형 10문항(check_dlg.js), PDF는 print-sheet.js가 sp·dn을 읽어 대화 모양으로 찍는다.
"""
import re, sys
p = sys.argv[1]
t = open(p, encoding='utf8').read()

OLD = """'<li class="sent" data-s="'+(i+1)+'"><span class="sn">'+(i+1)+'</span><div><p class="se">'+s.en+'</p>"""
NEW = """(s.dn?'<li class="dn">'+s.dn+'</li>':'')+'<li class="sent'+(s.sp?' has-sp':'')+'" data-s="'+(i+1)+'"><span class="sn">'+(i+1)+'</span><div><p class="se">'+(s.sp?'<b class="spk" data-sp="'+s.sp+'">'+s.sp+'</b>':'')+s.en+'</p>"""
if NEW not in t:
    assert t.count(OLD) == 1, 'sentence render'
    t = t.replace(OLD, NEW)

CSS = """/* ==== DLG:START ==== */
.sents .dn{list-style:none;font-family:var(--round,inherit);font-size:15px;color:var(--accent-ink);background:var(--accent-soft);border-radius:999px;display:inline-block;padding:3px 14px;margin:14px 0 4px}
.sents .dn:first-child{margin-top:0}
.sents .dn + .sent{border-top:0}
.spk{display:inline-flex;align-items:center;justify-content:center;width:1.75em;height:1.75em;border-radius:50%;font-family:var(--round,inherit);font-weight:400;font-size:.8em;margin-right:8px;vertical-align:.12em;color:#fff;background:#2F6FD0}
.spk[data-sp="G"]{background:#E0567A}
.spk[data-sp="W"]{background:#8A5BD6}
.spk[data-sp="M"]{background:#1F4E8C}
/* ==== DLG:END ==== */
"""
t = re.sub(r'/\* ==== DLG:START[\s\S]*?DLG:END ==== \*/\n?', '', t)
assert t.count('</style>') == 1
t = t.replace('</style>', CSS + '</style>')

REP = [
    ('<a href="#passage">지문</a>', '<a href="#passage">대화문</a>'),
    ('<h2 id="h-passage">지문</h2><p>문장을 먼저 스스로 해석해 보고,',
     '<h2 id="h-passage">대화문</h2><p>말하는 사람(B 남학생 · G 여학생 · W 여자 어른 · M 남자 어른)을 보며 한 줄씩 스스로 해석해 보고,'),
    ('<p>지문을 읽기 전에 1분만 훑어보세요. 글의 뼈대를 알고 읽으면 훨씬 잘 읽혀요. 문장 번호를 누르면 지문에서 그 문장들이 표시돼요.</p>',
     '<p>대화를 읽기 전에 1분만 훑어보세요. 누가 어떤 상황에서 무슨 표현을 쓰는지 알고 읽으면 훨씬 잘 읽혀요. 번호를 누르면 대화문에서 그 줄들이 표시돼요.</p>'),
]
for a, b in REP:
    if b not in t:
        assert t.count(a) == 1, ('문구', a[:30])
        t = t.replace(a, b)
# 문장 배열(2026-10-26 원장님 지적): 한 줄(턴)에 문장이 여럿이면 가운데 마침표·대문자가 순서 힌트가 된다.
#   → 대화문은 문장 하나씩 배열한다. order 항목에 en(그 문장)·ko(그 문장 해석)를 넣으면 화면이 그 문장으로 낸다.
#   { s: 9, en: 'Did you bake them, Subin?', ko: '네가 이것들을 구웠니, 수빈아?', c: ['Did you', 'bake', 'them,', 'Subin?'] }
OA = "var it=cur.it, s=S[it.s-1], total=O.length"
OB = "var it=cur.it, s=it.en?{en:it.en,ko:it.ko}:S[it.s-1], total=O.length"
if OB not in t:
    assert t.count(OA) == 1, 'order draw'
    t = t.replace(OA, OB)
t = t.replace("<small>지문 '+it.s+'번 문장</small>", "<small>대화문 '+it.s+'번 줄</small>")
open(p, 'w', encoding='utf8').write(t)
print(p, '대화문 화면 적용')
