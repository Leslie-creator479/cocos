# 시안 B: 홈페이지 전체 문장을 '선생님 중심'으로 바꾼 판 (바뀐 곳은 노란 표시, 버튼으로 지금 문장과 비교)
import html as H

def chg(t, old, new, tag='span', cls=''):
    assert t.count(old) == 1, ('not unique', old[:60], t.count(old))
    el = f'<{tag} class="bchg{(" "+cls) if cls else ""}" data-orig="{H.escape(old, quote=True)}">{new}</{tag}>'
    return t.replace(old, el)

def add_after(t, anchor, new_p):
    assert t.count(anchor) == 1, ('anchor', anchor[:60])
    return t.replace(anchor, anchor + f'\n          <p class="bchg bnew" data-orig="">{new_p}</p>')

def chg_nth(t, old, new, n):
    """같은 문장이 여러 번 나올 때 n번째(0부터)만 바꾼다."""
    i = -1
    for _ in range(n + 1):
        i = t.index(old, i + 1)
    el = f'<span class="bchg" data-orig="{H.escape(old, quote=True)}">{new}</span>'
    return t[:i] + el + t[i + len(old):]

def apply(t, letter=True):
    if letter:
        # --- 원장 인사 ---
        t = chg(t, '이제 교재와 학원 시스템은 학원이 AI와 함께 맡아 만들고, 선생님은 그 시간을 온전히 수업과 학생에게 씁니다.',
                '그 자료를 바탕으로 학원은 AI와 함께 교재와 시스템을 만들어 왔고, 선생님은 그 시간을 온전히 수업과 학생에게 써 왔습니다.')
        t = add_after(t, '그 시간을 온전히 수업과 학생에게 써 왔습니다.</span></p>',
            '이제 코코스는 다음 장을 엽니다. 코코스 선생님은 한 분 한 분이 자기 이름을 걸고 맡은 반과 학교를 책임집니다. '
            '13년 동안 같은 교실을 지켜 온 선생님들이 학생과 학부모님 앞에 이름과 얼굴로 서고, 학원은 오랜 수업에서 다듬어 온 '
            '기본 설계와 자료, 출제 분석, 시스템과 컨설팅을 준비해 선생님께 드립니다. 무엇을 골라 어떻게 가르칠지는 선생님이 정합니다. '
            '<b>무대 위는 선생님이, 무대 뒤는 학원이.</b>')
        t = chg(t, '기술을 몰라서 하는 고집이 아니라, 어디에 쓰고 어디서 멈춰야 하는지 알기에 세운 기준입니다.',
                '기술을 몰라서 하는 고집이 아니라, 어디에 쓰고 어디서 멈춰야 하는지 알기에 코코스가 지켜 온 약속입니다.')
        t = chg(t, '<b>코코스학원 원장</b>', '<b>코코스학원 대표 ○○○ · ○○○</b>')
    # --- 수업 원칙: 교실 안 = 학생이 학원에서 지키는 규칙 / 교실 밖 = 코코스가 준비해 드리는 것 ---
    t = chg(t, '기술은 학원이 쓰고, 교실은 공부에 집중합니다. 오랫동안 아이들을 가르치며 지켜본 끝에 세운 기준입니다.',
            '기술은 학원이 쓰고, 교실은 공부에 집중합니다. 교실 안의 세 가지는 학생이 코코스에서 지키는 규칙이고, '
            '교실 밖의 두 가지는 코코스가 선생님과 학생에게 준비해 드리는 것입니다.')
    for k in range(3):
        t = chg_nth(t, '<span class="tag">교실 안</span>', '<span class="tag">교실 안 · 학원 규칙</span>', 0)
    for k in range(2):
        t = chg_nth(t, '<span class="tag out">교실 밖</span>', '<span class="tag out">교실 밖 · 코코스가 드리는 것</span>', 0)
    t = chg(t, '동영상·온라인 수업은 하지 않습니다. 영상이 있으니 빠져도 된다는 생각이 오히려 결석을 늘렸기 때문입니다.',
            '코코스는 동영상·온라인 수업 과정을 열지 않습니다. 영상이 있으니 빠져도 된다는 생각이 오히려 결석을 늘린다는 것을 오래 겪었기 때문입니다.')
    t = chg(t, '학원이 만든 종이 교재에 직접 필기하며 공부하고, 시험도 종이에 펜으로 봅니다.',
            '학생은 종이 교재에 직접 필기하며 공부하고, 시험도 종이에 펜으로 봅니다. 교재는 코코스가 만든 자료와 담당 선생님이 고른 교재 가운데서 씁니다.')
    t = chg(t, '종이 시험 결과를 학원이 직접 만든 시스템에 기록합니다. 학생은 시험마다 개인 리포트를 받고, 반 전체가 어려워한 문항은 다음 수업에서 다시 다룹니다.',
            '학원이 직접 만든 기록 시스템을 모든 반에 드립니다. 종이 시험 결과를 기록하면 학생은 시험마다 개인 리포트를 받고, 담당 선생님은 반 전체가 어려워한 문항을 한눈에 볼 수 있습니다.')
    t = chg(t, '지문별 온라인 학습지까지 학원이 AI와 함께 만듭니다. 선생님은 그 시간을 온전히 수업과 학생에게 씁니다.',
            '지문별 온라인 학습지까지 학원이 AI와 함께 만들어 선생님께 드립니다. 선생님은 수업에 맞는 자료를 골라 쓰고, 남는 시간을 온전히 수업과 학생에게 씁니다.')
    # --- 세 단계 관리 ---
    t = chg(t, '코코스학원은 같은 순서를 모든 학생에게 지킵니다.',
            '진단·설계·관리는 코코스가 오랜 수업에서 다듬어 온 기본 설계입니다. 학원은 레벨 테스트와 학교별 분석, 온라인 학습지를 준비하고, 담당 선생님이 이를 바탕으로 자기 반의 수업을 설계합니다.')
    # --- 학년별 프로그램 머리말 ---
    t = chg(t, '평소에는 레벨 테스트로 나눈 정규반에서, 내신 기간에는 학교별 내신대비반에서 수업합니다.',
            '레벨 테스트로 나눈 정규반에서 담당 선생님과 수업하고, 내신 기간에는 학교별 내신대비반을 엽니다.')
    # --- 중등부 수업 운영 ---
    t = chg(t, 'TEPS반·중등 COT반을 포함한 중등부 모든 반이 같은 시스템으로, 주 2회 고정 수업(월·금반 또는 화·목반)과 수요일 Special Lesson으로 진행합니다.',
            '코코스 중등부 기본 설계는 주 2회 고정 수업(월·금반 또는 화·목반)과 수요일 Special Lesson입니다. 지금 중등부 선생님들은 TEPS반·중등 COT반을 포함한 모든 반을 이 설계로 수업합니다.')
    # --- 입학 절차: 학원 일은 학원이 약속하고, 선생님 일은 '선생님이 정한 방식으로' ---
    t = chg(t, '과제와 테스트 관리는 잘 되는지, 아이가 잘 적응하는지 알 수가 없다.',
            '아이가 잘 적응하고 있는지, 궁금한 점은 누구에게 물어야 할지 알 수 없다.')
    t = chg(t, '교재 준비, 현재 진도, 과제 방법, 테스트 준비를 미리 안내하고, 수업에 필요한 기본 개념과 부족한 부분은 담당 선생님이 확인해 지도합니다. 첫 수업부터 바로 적응하도록 돕는 코코스만의 입학 프로그램입니다.',
            '교재 준비, 현재 진도, 과제 방법은 학원이 미리 안내해 드리고, 첫 수업 전에 담당 선생님을 만나 아이의 기본 개념과 부족한 부분을 함께 확인합니다. 첫 수업부터 바로 적응하도록 돕는 코코스의 입학 프로그램입니다.')
    t = chg(t, '첫 수업이 끝나면 담당 선생님이 학생·학부모님과 상담해 수업 이해도를 확인하고, 드러난 문제는 바로 바로잡습니다.',
            '첫 수업 뒤에는 담당 선생님이 정한 방식으로 수업 이해도와 앞으로의 계획을 안내해 드립니다.')
    t = chg(t, '2주 후 적응 점검', '2주 후 안부 연락')
    t = chg(t, '수업을 시작하고 2주가 지나면 담임 선생님이 그동안의 수업 상황을 다시 확인합니다. 아이가 수업과 학원에 얼마나 만족하는지, 학부모님께서 바라시는 점은 없는지 여쭙고, 아이가 학원에 잘 자리 잡을 때까지 함께 살핍니다.',
            '수업을 시작하고 2주가 지나면 학원이 학부모님께 연락드려, 아이가 학원에 잘 적응했는지, 바라시는 점은 없는지 여쭙습니다. 수업에 관한 말씀은 담당 선생님께 그대로 전해 드립니다.')
    return t

CSS = '''
.bchg{background:rgba(195,164,108,.2);box-decoration-break:clone;-webkit-box-decoration-break:clone;padding:1px 2px}
p.bchg{display:block;padding:10px 12px;border-left:2px solid var(--gold)}
body.b-orig .bchg{background:transparent;padding:0;border:0}
body.b-orig .bnew{display:none}
.b-tool{position:fixed;right:12px;bottom:12px;z-index:99;display:flex;align-items:center;gap:10px;background:#0B1323;color:#ECEEF2;font:500 12.5px/1.4 var(--sans);padding:8px 8px 8px 14px;box-shadow:0 6px 20px rgba(0,0,0,.25)}
.b-tool i{display:inline-block;width:12px;height:12px;background:rgba(195,164,108,.55);vertical-align:-1px;margin-right:6px}
.b-tool button{font:600 12.5px/1 var(--sans);background:#C3A46C;color:#0B1323;border:0;padding:9px 12px;cursor:pointer}
@media (max-width:560px){.b-tool span{display:none}.b-tool{bottom:52px}}
'''

JS = '''<div class="b-tool"><span><i></i>B 시안에서 바뀐 문장</span><button type="button" id="b-toggle">지금 홈페이지 문장 보기</button></div>
<script>(function(){var b=document.getElementById('b-toggle'),els=[].slice.call(document.querySelectorAll('.bchg'));
els.forEach(function(e){e._new=e.innerHTML});var orig=false;
b.addEventListener('click',function(){orig=!orig;document.body.classList.toggle('b-orig',orig);
els.forEach(function(e){if(!e.classList.contains('bnew'))e.innerHTML=orig?e.getAttribute('data-orig'):e._new});
b.textContent=orig?'B 시안 문장 보기':'지금 홈페이지 문장 보기';});})();</script>
'''
