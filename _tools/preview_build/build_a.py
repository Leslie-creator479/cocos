import re, os
SRC='/home/claude/cocos/index.html'; OUT='/home/claude/cocos/preview/care/index.html'
t=open(SRC,encoding='utf-8').read()
# preview head: noindex + base, drop canonical & analytics
t=t.replace('<head>','<head><meta name="robots" content="noindex"><base href="/">',1)
t=re.sub(r'<link rel="canonical"[^>]*>','',t)
t=re.sub(r'<!-- naver-analytics -->.*?<!-- /naver-analytics -->\n?','',t,flags=re.S)
t=re.sub(r'<title>(.*?)</title>',r'<title>시안 A · 학원 중심 — \1</title>',t,count=1)

old='<p class="consent"><b>학년 전담 선생님</b> — 고등부는 학년마다 담당 선생님이 그 학년의 학교별 내신과 모의고사를 꾸준히 맡아, 학생 한 명 한 명을 집중해서 관리합니다.</p>'
assert old in t
t=t.replace(old,'<p class="consent"><b>학년 전담 집중 케어 시스템</b> — 고1 때 만난 담당 선생님이 고3 졸업까지 3년 동안 함께합니다. 아래에서 자세히 소개합니다.</p>')

def ico(paths): return f'<svg class="ico" viewBox="0 0 64 64" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">{paths}</svg>'
I_TALK=ico('<path d="M8 12h28a4 4 0 0 1 4 4v14a4 4 0 0 1-4 4H22l-8 7v-7H8a4 4 0 0 1-4-4V16a4 4 0 0 1 4-4z"/><path d="M46 24h10a4 4 0 0 1 4 4v12a4 4 0 0 1-4 4h-2v7l-7-7H34a4 4 0 0 1-4-4v-2"/>')
I_SCHOOL=ico('<path d="M6 26 32 12l26 14"/><path d="M12 29v23h40V29"/><path d="M27 52V38h10v14"/><path d="M32 12V5h9v5h-9"/>')
I_CHART=ico('<path d="M8 54h48"/><path d="M14 46l12-12 9 8 17-20"/><path d="M44 22h8v8"/>')
I_COMPASS=ico('<circle cx="32" cy="32" r="24"/><path d="M40 24l-5 11-11 5 5-11z"/>')

BLOCK=f'''
        <section class="cs" id="care-system" aria-labelledby="t-cs">
          <div class="cs-head">
            <span class="cap">Grade Care System · High School</span>
            <h3 id="t-cs">학년 전담 집중 케어 시스템</h3>
            <p class="cs-lead">고1 때 만난 담당 선생님이 <b>고3 졸업까지 3년 동안</b> 함께합니다.</p>
          </div>
          <div class="cs-why">
            <p class="cs-quote">3년을 아는<br>선생님</p>
            <div>
              <p>학년이 바뀔 때마다 선생님이 바뀌면, 새 선생님은 아이의 약점과 공부 습관을 처음부터 다시 알아가야 합니다.</p>
              <p>코코스 고등부는 <b>담당 선생님 한 명이 그 학년의 모든 반</b>(레벨반·내신대비반)을 맡아 고1부터 고3까지 함께 올라갑니다. 같은 학교, 같은 학생을 3년 내내 보기 때문에 아이가 어디서 자랐고 어디서 막히는지 누구보다 잘 압니다.</p>
            </div>
          </div>
          <ol class="cs-years">
            <li><span>Year 1</span><b>고1 · 시작</b><em>학교별 첫 내신 적응</em><em>레벨 진단과 성적 분석표 시작</em><em>고등 공부 습관 잡기</em></li>
            <li><span>Year 2</span><b>고2 · 심화</b><em>내신 심화와 모의고사 추이 관리</em><em>쌓인 기록으로 약한 유형 집중 보완</em><em>진로 방향 함께 고민</em></li>
            <li><span>Year 3</span><b>고3 · 완성</b><em>1학기 내신 마무리</em><em>2학기 수능 집중반</em><em>컨설팅센터와 입시 전략 연계</em></li>
          </ol>
          <div class="cs-care">
            <div class="cs-c">{I_TALK}<span>01</span><b>정기 학부모 상담</b><p>3년 동안 같은 선생님이 정기적으로 직접 상담합니다. 해마다 아이 이야기를 처음부터 다시 하실 필요가 없습니다.</p></div>
            <div class="cs-c">{I_SCHOOL}<span>02</span><b>학교별 내신·수행평가</b><p>같은 학교, 같은 학년을 3년 내내 맡아 출제 경향은 물론 수행평가 일정과 준비까지 챙깁니다.</p></div>
            <div class="cs-c">{I_CHART}<span>03</span><b>3년 성적·모의고사 추이</b><p>성적 분석표를 3년 동안 이어서 쌓아, 한 번의 점수가 아니라 성장의 흐름으로 봅니다.</p></div>
            <div class="cs-c">{I_COMPASS}<span>04</span><b>진로·입시 컨설팅 연계</b><p>고2·고3에는 코코스 컨설팅센터와 함께 3년의 기록을 바탕으로 수시·정시 전략을 세웁니다.</p></div>
          </div>
          <div class="cs-cycle">
            <div class="cs-cycle-h"><span class="cap">3-Year Cycle</span><p>고3을 졸업시킨 선생님은 다시 새 고1을 맡습니다. 세 선생님이 3년 주기로 돌아가며, 해마다 모든 학년에 3년을 책임질 담당 선생님이 있습니다.</p></div>
            <div class="cs-grid" role="table" aria-label="3년 순환 예시">
              <div class="h" role="columnheader"></div><div class="h">1년차</div><div class="h">2년차</div><div class="h">3년차</div><div class="h">4년차</div>
              <div class="t">선생님 A</div><div class="g1">고1</div><div class="g2">고2</div><div class="g3">고3</div><div class="g1 new">고1</div>
              <div class="t">선생님 B</div><div class="g2">고2</div><div class="g3">고3</div><div class="g1 new">고1</div><div class="g2">고2</div>
              <div class="t">선생님 C</div><div class="g3">고3</div><div class="g1 new">고1</div><div class="g2">고2</div><div class="g3">고3</div>
            </div>
            <p class="cs-note">순환 구조 예시 — 새 고1을 맡는 칸을 금색으로 표시했습니다.</p>
          </div>
          <div class="mock cs-dir">
            <div><span class="cap">Directors</span><h4>원장은 학년 선생님 뒤에서<br>코코스의 기준을 지킵니다</h4></div>
            <div class="mock-body">
              <p><b>교재·자료</b> — 2013년부터 쌓아 온 자료와 자체 교재의 기준을 만들고 감수합니다.</p>
              <p><b>출제 분석</b> — 학교별 기출 분석과 변형 문제의 방향을 잡습니다.</p>
              <p><b>수업 점검</b> — 학년 선생님의 수업과 클리닉을 함께 점검하고 돕습니다.</p>
              <p><b>상담·컨설팅</b> — 학부모 상담과 입시 컨설팅에 함께합니다.</p>
            </div>
          </div>
        </section>
'''
anchor='        <div class="course-h">\n          <div><span class="cap">High School · Regular Classes</span>'
assert t.count(anchor)==1
t=t.replace(anchor,BLOCK+anchor)

CSS='''
.cs{margin:0 0 clamp(72px,8vw,112px)}
.cs-head{border-bottom:1px solid var(--ink);padding-bottom:18px}
.cs-head h3{font-size:clamp(26px,3vw,38px);font-weight:700;letter-spacing:-.02em;margin-top:10px}
.cs-lead{margin-top:10px;font-size:16px;color:var(--muted);line-height:1.7}
.cs-lead b{color:var(--ink)}
.cs-why{display:grid;grid-template-columns:minmax(0,.8fr) minmax(0,1.6fr);gap:20px 48px;padding:36px 0 32px;align-items:start}
.cs-why .cs-quote{font-size:clamp(30px,3.6vw,46px);font-weight:300;line-height:1.25;letter-spacing:-.02em;color:var(--ink)}
.cs-why p{font-size:15px;line-height:1.85;color:var(--muted)}
.cs-why p+p{margin-top:10px}
.cs-why b{color:var(--ink)}
.cs-years{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:6px}
.cs-years li{position:relative;background:var(--night);color:var(--on-night);padding:22px 22px 24px;display:flex;flex-direction:column;gap:6px}
.cs-years li:nth-child(2){background:var(--night-2)}
.cs-years li:nth-child(3){background:var(--night-3)}
.cs-years span{font-family:var(--latin);font-size:12px;letter-spacing:.2em;color:var(--gold)}
.cs-years b{font-size:20px;font-weight:600;margin-bottom:4px}
.cs-years em{font-style:normal;font-size:13.5px;color:var(--on-night-muted);line-height:1.6;padding-left:14px;position:relative}
.cs-years em::before{content:"";position:absolute;left:0;top:.75em;width:7px;height:1px;background:var(--gold)}
.cs-years li:not(:last-child)::after{content:"";position:absolute;right:-6px;top:50%;width:6px;height:1px;background:var(--gold)}
.cs-care{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:0;margin-top:40px;border-top:1px solid var(--line)}
.cs-c{position:relative;padding:24px 22px 26px 0;border-bottom:1px solid var(--line)}
.cs-c+.cs-c{padding-left:22px;border-left:1px solid var(--line)}
.cs-c .ico{width:34px;height:34px;color:var(--gold-deep)}
.cs-c span{display:block;font-family:var(--latin);font-size:12px;letter-spacing:.16em;color:var(--gold-deep);margin-top:14px}
.cs-c b{display:block;font-size:16.5px;font-weight:600;margin-top:4px}
.cs-c p{font-size:13.5px;line-height:1.75;color:var(--muted);margin-top:8px}
.cs-cycle{display:grid;grid-template-columns:minmax(0,.9fr) minmax(0,1.5fr);gap:20px 48px;margin-top:48px;align-items:start}
.cs-cycle-h p{font-size:14.5px;line-height:1.8;color:var(--muted);margin-top:10px}
.cs-grid{display:grid;grid-template-columns:84px repeat(4,minmax(0,1fr));gap:4px;font-size:13.5px}
.cs-grid>div{padding:12px 8px;text-align:center}
.cs-grid .h{font-family:var(--latin);font-size:12px;letter-spacing:.1em;color:var(--muted);padding:6px 4px}
.cs-grid .t{text-align:left;font-weight:600;color:var(--ink);padding-left:0;align-self:center}
.cs-grid .g1{background:var(--night-3);color:var(--on-night)}
.cs-grid .g2{background:var(--night-2);color:var(--on-night)}
.cs-grid .g3{background:var(--night);color:var(--on-night)}
.cs-grid .new{background:linear-gradient(135deg,rgba(195,164,108,.35),rgba(195,164,108,.15));color:var(--ink);font-weight:600;border:1px solid var(--gold-line)}
.cs-note{grid-column:2;font-size:12px;color:var(--muted);margin-top:-10px}
.cs-dir{margin-top:48px!important}
@media (max-width:860px){.cs-why,.cs-cycle{grid-template-columns:1fr}.cs-years{grid-template-columns:1fr}.cs-years li::after{display:none}.cs-care{grid-template-columns:1fr 1fr}.cs-c:nth-child(3){padding-left:0;border-left:0}.cs-note{grid-column:1;margin-top:0}}
@media (max-width:520px){.cs-care{grid-template-columns:1fr}.cs-c,.cs-c+.cs-c{padding-left:0;border-left:0}.cs-grid{grid-template-columns:64px repeat(4,minmax(0,1fr));font-size:12.5px}}
.preview-flag{position:fixed;left:12px;bottom:12px;z-index:99;background:#8A6C3C;color:#fff;font:600 12px/1 var(--sans);letter-spacing:.06em;padding:9px 12px}
'''
t=t.replace('</style>',CSS+'</style>',1)
t=t.replace('<body>','<body><div class="preview-flag">시안 A · 학원 중심 · 실제 홈페이지 아님</div>',1) if '<body>' in t else re.sub(r'(<body[^>]*>)',r'\1<div class="preview-flag">시안 A · 학원 중심 · 실제 홈페이지 아님</div>',t,count=1)
os.makedirs(os.path.dirname(OUT),exist_ok=True)
open(OUT,'w',encoding='utf-8').write(t)
print('ok', len(t))
