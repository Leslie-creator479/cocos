import re, os
ROOT='/home/claude/cocos'
src=open(f'{ROOT}/index.html',encoding='utf-8').read()

def prep(t, title, flag):
    t=t.replace('<head>','<head><meta name="robots" content="noindex"><base href="/">',1)
    t=re.sub(r'<link rel="canonical"[^>]*>','',t)
    t=re.sub(r'<!-- naver-analytics -->.*?<!-- /naver-analytics -->\n?','',t,flags=re.S)
    t=re.sub(r'<title>(.*?)</title>',f'<title>{title}</title>',t,count=1)
    t=re.sub(r'(<body[^>]*>)',r'\1'+f'<div class="preview-flag">{flag}</div>',t,count=1)
    return t

def ico(p): return f'<svg class="ico" viewBox="0 0 64 64" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">{p}</svg>'
PERSON='<svg viewBox="0 0 120 140" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.4"><circle cx="60" cy="50" r="24"/><path d="M14 138c4-30 24-46 46-46s42 16 46 46"/></svg>'
I_BOOK=ico('<path d="M32 18c-6-5-14-6-24-5v36c10-1 18 0 24 5 6-5 14-6 24-5V13c-10-1-18 0-24 5z"/><path d="M32 18v36"/>')
I_SEARCH=ico('<circle cx="28" cy="28" r="16"/><path d="M40 40l14 14"/><path d="M21 28h14M28 21v14"/>')
I_SCREEN=ico('<rect x="8" y="12" width="48" height="32" rx="3"/><path d="M24 54h16M32 44v10"/><path d="M18 24h20M18 31h14"/>')
I_CHART=ico('<path d="M8 54h48"/><path d="M14 46l12-12 9 8 17-20"/><path d="M44 22h8v8"/>')
I_COMPASS=ico('<circle cx="32" cy="32" r="24"/><path d="M40 24l-5 11-11 5 5-11z"/>')
I_DESK=ico('<path d="M8 22h48v10H8z"/><path d="M14 32v22M50 32v22"/><path d="M24 22v-8h16v8"/>')

def tcard(i, grade):
    return f'''<article class="tc">
  <div class="tc-photo">{PERSON}<span>사진</span></div>
  <div class="tc-body">
    <span class="cap">Teacher {i}</span>
    <h4>○○○ 선생님</h4>
    <p class="tc-meta">{grade} · ○○고, ○○고</p>
    <p class="tc-line">[선생님이 직접 쓰는 수업 소개 한 줄]</p>
    <ul class="tc-tags"><li>[대표 프로그램]</li><li>강의 경력 ○○년</li></ul>
    <a class="tc-link" href="preview/teacher/sample/">선생님 소개 보기 <span aria-hidden="true">→</span></a>
  </div>
</article>'''

HIGH=f'''<div class="ppanel" id="course-high" role="tabpanel" aria-labelledby="tab-high">
        <section class="tb" aria-labelledby="t-tb">
          <div class="course-h">
            <div><span class="cap">High School · Teachers</span><h3 id="t-tb">고등부는 선생님의 이름으로 수업합니다</h3></div>
            <p>코코스 고등부 선생님은 각자 자기 이름을 걸고 맡은 학년과 학교를 책임집니다. 지금 고등부 선생님들은 하루 3시간(독해 45분·문법 45분·클리닉 90분)의 코코스 기본 설계로 수업하며, 반 구성과 교재, 세부 방식은 선생님 소개에서 확인할 수 있습니다.</p>
          </div>
          <div class="tb-grid">
            {tcard(1,'고○ 담당')}
            {tcard(2,'고○ 담당')}
            {tcard(3,'고○ 담당')}
          </div>
          <div class="tb-dir">
            <div><span class="cap">Directors</span><b>코코스 대표 ○○○ · ○○○</b></div>
            <p>2013년부터 성남 고등학교 내신을 맡아 온 두 대표가, 선생님들이 수업에만 온전히 힘을 쏟을 수 있도록 무대와 자료를 준비합니다.</p>
          </div>
        </section>

        <section class="sp" aria-labelledby="t-sp">
          <div class="course-h" style="margin-top:clamp(64px,7vw,96px)">
            <div><span class="cap">COCOS Support</span><h3 id="t-sp">코코스가 선생님과 함께 드리는 것</h3></div>
            <p>어느 선생님 반에서 공부하든, 13년 동안 쌓아 온 코코스의 자료와 도구를 함께 누릴 수 있습니다.</p>
          </div>
          <div class="sp-grid">
            <div class="sp-c">{I_BOOK}<b>13년 내신 자료</b><p>2013년부터 쌓아 온 학교별 시험 범위 자료와 자체 교재를 선생님이 수업에 맞게 골라 씁니다.</p></div>
            <div class="sp-c">{I_SEARCH}<b>학교별 출제 분석</b><p>학교별 기출 분석과 변형 문제 자료를 코코스 선생님들이 함께 나눕니다.</p></div>
            <div class="sp-c">{I_SCREEN}<b>온라인 학습지</b><p>문장별 해석·녹음·확인 문제가 담긴 코코스 자료실을 학생 누구나 쓸 수 있습니다.</p></div>
            <div class="sp-c">{I_CHART}<b>성적 분석 도구</b><p>모의고사 성적 분석표 양식으로 계속 틀리는 유형을 기록하고 상담에 활용합니다.</p></div>
            <div class="sp-c">{I_COMPASS}<b>입시 컨설팅센터</b><p>진로·입시 상담이 필요할 때 코코스 컨설팅센터가 함께합니다.</p></div>
            <div class="sp-c">{I_DESK}<b>상담·행정</b><p>입학 상담, 레벨 테스트, 수납과 안내는 학원이 맡아 선생님은 수업에 집중합니다.</p></div>
          </div>
        </section>
        </div>
        '''

t=src
i=t.index('<div class="ppanel" id="course-high"'); j=t.index('<div class="ppanel" id="course-mid"')
t=t[:i]+HIGH+t[j:]
import b_text
t=b_text.apply(t)
t=t.replace('</body>',b_text.JS+'</body>',1)
CSS='''
.tb-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px;margin-top:28px}
.tc{background:#fff;border:1px solid var(--line);display:flex;flex-direction:column}
.tc-photo{aspect-ratio:4/3.4;background:linear-gradient(160deg,var(--night-3),var(--night));color:rgba(236,238,242,.35);display:flex;align-items:flex-end;justify-content:center;position:relative;overflow:hidden}
.tc-photo svg{width:46%;height:auto;margin-bottom:-2px}
.tc-photo span{position:absolute;top:12px;left:14px;font-size:11px;letter-spacing:.2em;color:var(--gold)}
.tc-body{padding:22px 22px 24px;display:flex;flex-direction:column;gap:6px;flex:1}
.tc-body .cap{color:var(--gold-deep)}
.tc-body h4{font-size:22px;font-weight:700;letter-spacing:-.02em}
.tc-meta{font-size:13.5px;color:var(--muted)}
.tc-line{font-size:14.5px;line-height:1.7;margin-top:6px;color:var(--ink)}
.tc-tags{list-style:none;display:flex;flex-wrap:wrap;gap:6px;margin:8px 0 0;padding:0}
.tc-tags li{font-size:12px;border:1px solid var(--gold-line);color:var(--gold-deep);padding:4px 9px}
.tc-link{margin-top:auto;padding-top:16px;font-size:13.5px;font-weight:600;color:var(--ink);text-decoration:none;border-top:1px solid var(--line)}
.tb-dir{display:grid;grid-template-columns:minmax(0,.9fr) minmax(0,1.6fr);gap:10px 40px;margin-top:16px;background:var(--night);color:var(--on-night);padding:24px 28px;align-items:center}
.tb-dir .cap{color:var(--gold);display:block;margin-bottom:6px}
.tb-dir b{font-size:17px;font-weight:600}
.tb-dir p{font-size:14px;line-height:1.75;color:var(--on-night-muted)}
.sp-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));border-top:0}
.sp-c{padding:26px 24px 28px 0;border-bottom:1px solid var(--line)}
.sp-c:not(:nth-child(3n+1)){padding-left:24px;border-left:1px solid var(--line)}
.sp-c .ico{width:34px;height:34px;color:var(--gold-deep)}
.sp-c b{display:block;font-size:16.5px;font-weight:600;margin-top:14px}
.sp-c p{font-size:13.5px;line-height:1.75;color:var(--muted);margin-top:8px}
@media (max-width:860px){.tb-grid{grid-template-columns:1fr 1fr}.tb-dir{grid-template-columns:1fr}.sp-grid{grid-template-columns:1fr 1fr}.sp-c,.sp-c:not(:nth-child(3n+1)){padding-left:0;border-left:0}.sp-c:nth-child(2n){padding-left:20px;border-left:1px solid var(--line)}}
@media (max-width:560px){.tb-grid,.sp-grid{grid-template-columns:1fr}.sp-c:nth-child(2n){padding-left:0;border-left:0}}
.preview-flag{position:fixed;left:12px;bottom:12px;z-index:99;background:#8A6C3C;color:#fff;font:600 12px/1 var(--sans);letter-spacing:.06em;padding:9px 12px}
'''
t=t.replace('</style>',CSS+b_text.CSS+'</style>',1)
t=prep(t,'시안 B · 선생님 중심 — 코코스학원','시안 B · 선생님 중심 · 실제 홈페이지 아님')
os.makedirs(f'{ROOT}/preview/teacher',exist_ok=True)
open(f'{ROOT}/preview/teacher/index.html','w',encoding='utf-8').write(t)

# ---- sample teacher page ----
s=src
mi=s.index('<main id="home">'); mj=s.index('</main>')+len('</main>')
MAIN=f'''<main id="home">
  <section class="sec on-night tp-hero">
    <div class="wrap pad tp-hero-in">
      <div class="tp-photo">{PERSON}<span>사진</span></div>
      <div>
        <span class="cap">COCOS High School · Teacher</span>
        <h1>○○○ 선생님</h1>
        <p class="tp-sub">고○ 담당 · ○○고, ○○고 · 강의 경력 ○○년</p>
        <p class="tp-line">[선생님이 직접 쓰는 수업 소개 한두 문장. 어떤 학생을, 어떤 방식으로, 어디까지 끌어올리는지]</p>
        <div class="tp-btns"><a href="tel:031-752-3334">이 선생님 반 상담 문의</a><a class="ghost" href="preview/teacher/#course">고등부 선생님 모두 보기</a></div>
      </div>
    </div>
  </section>
  <section class="sec on-white">
    <div class="wrap pad">
      <div class="course-h"><div><span class="cap">Philosophy</span><h3>수업 철학</h3></div><p>선생님이 직접 씁니다.</p></div>
      <p class="tp-ph">[예: 내신은 한 문장의 차이에서 갈립니다. 시험 범위 지문을 문장 단위로 끝까지 다루고, 학생이 스스로 설명할 수 있을 때까지 확인합니다. …]</p>

      <div class="course-h" style="margin-top:72px"><div><span class="cap">My Classes</span><h3>담당 반과 수업 시간</h3></div><p>반 구성과 시간은 선생님이 학원과 협의해 정합니다.</p></div>
      <div class="tp-table">
        <div class="h">반</div><div class="h">대상</div><div class="h">요일·시간</div><div class="h">교재</div>
        <div>[반 이름]</div><div>고○ · ○○고</div><div>월·금반 · 오후 ○시</div><div>[선생님 선택 교재]</div>
        <div>[반 이름]</div><div>고○ · ○○고</div><div>화·목반 · 오후 ○시</div><div>[선생님 선택 교재]</div>
        <div>[내신대비반]</div><div>시험 ○주 전</div><div>[선생님이 정함]</div><div>[학교별 자료]</div>
      </div>

      <div class="course-h" style="margin-top:72px"><div><span class="cap">How I Teach</span><h3>이렇게 수업합니다</h3></div><p>예시로 지금 코코스 고등부의 하루 3시간 구성을 넣었습니다. 선생님마다 바꿔 씁니다.</p></div>
      <div class="tp-steps">
        <div><span>45 MIN</span><b>독해</b><p>[선생님 방식]</p></div>
        <div><span>45 MIN</span><b>문법</b><p>[선생님 방식]</p></div>
        <div class="g"><span>90 MIN</span><b>클리닉</b><p>단어 시험 → 모의고사 50분 → 채점 → 유형별 오답 기록 [선생님이 고침]</p></div>
      </div>

      <div class="course-h" style="margin-top:72px"><div><span class="cap">With COCOS</span><h3>이 선생님 반이 함께 쓰는 코코스 자료</h3></div><p>코코스가 준비한 도구 가운데 선생님이 고른 것을 표시합니다.</p></div>
      <ul class="tp-chips"><li>13년 내신 자료</li><li>학교별 출제 분석</li><li>온라인 학습지</li><li>성적 분석표</li><li>입시 컨설팅센터</li></ul>

      <div class="course-h" style="margin-top:72px"><div><span class="cap">Parents</span><h3>학부모 상담</h3></div><p>상담 방식과 시기는 선생님이 정해 안내합니다.</p></div>
      <p class="tp-ph">[예: 내신 시험이 끝날 때마다 성적 분석표를 바탕으로 직접 상담합니다.]</p>
    </div>
  </section>
</main>'''
s=s[:mi]+MAIN+s[mj:]
CSS2='''
.tp-hero-in{display:grid;grid-template-columns:minmax(0,320px) minmax(0,1fr);gap:48px;align-items:center;padding-top:clamp(56px,7vw,96px);padding-bottom:clamp(56px,7vw,96px)}
.tp-photo{aspect-ratio:4/5;background:linear-gradient(160deg,var(--night-3),var(--night-2));border:1px solid var(--gold-line);color:rgba(236,238,242,.3);display:flex;align-items:flex-end;justify-content:center;position:relative}
.tp-photo svg{width:62%}.tp-photo span{position:absolute;top:14px;left:16px;font-size:11px;letter-spacing:.2em;color:var(--gold)}
.tp-hero .cap{color:var(--gold)}
.tp-hero h1{font-size:clamp(40px,5vw,64px);font-weight:700;letter-spacing:-.03em;margin-top:12px;color:var(--on-night)}
.tp-sub{color:var(--on-night-muted);margin-top:10px;font-size:15px}
.tp-line{color:var(--on-night);margin-top:22px;font-size:17px;line-height:1.8;max-width:36em}
.tp-btns{display:flex;flex-wrap:wrap;gap:10px;margin-top:28px}
.tp-btns a{background:var(--foil);color:#0B1323;font-weight:600;font-size:14px;padding:14px 20px;text-decoration:none;letter-spacing:.04em}
.tp-btns a.ghost{background:transparent;color:var(--on-night);border:1px solid var(--night-line)}
.tp-ph{margin-top:22px;font-size:16px;line-height:1.9;color:var(--muted);max-width:46em}
.tp-table{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));margin-top:22px;border-top:1px solid var(--line)}
.tp-table>div{padding:14px 10px;border-bottom:1px solid var(--line);font-size:14px}
.tp-table .h{font-size:12px;letter-spacing:.12em;color:var(--gold-deep)}
.tp-steps{display:grid;grid-template-columns:1fr 1fr 2fr;gap:6px;margin-top:22px}
.tp-steps>div{background:var(--night-2);color:var(--on-night);padding:20px}
.tp-steps>div.g{background:linear-gradient(135deg,rgba(195,164,108,.22),rgba(195,164,108,.08));color:var(--ink);border:1px solid var(--gold-line)}
.tp-steps span{font-size:12px;letter-spacing:.16em;opacity:.75}.tp-steps b{display:block;font-size:18px;margin-top:6px}.tp-steps p{font-size:13px;margin-top:8px;opacity:.85;line-height:1.6}
.tp-chips{list-style:none;display:flex;flex-wrap:wrap;gap:8px;margin:22px 0 0;padding:0}
.tp-chips li{border:1px solid var(--gold-line);color:var(--gold-deep);font-size:13.5px;padding:8px 14px}
@media (max-width:860px){.tp-hero-in{grid-template-columns:1fr}.tp-photo{max-width:260px}.tp-table{grid-template-columns:1fr 1fr}.tp-table .h:nth-child(n+3){display:none}.tp-steps{grid-template-columns:1fr}}
.preview-flag{position:fixed;left:12px;bottom:12px;z-index:99;background:#8A6C3C;color:#fff;font:600 12px/1 var(--sans);letter-spacing:.06em;padding:9px 12px}
'''
s=s.replace('</style>',CSS2+'</style>',1)
s=prep(s,'시안 B · 선생님 소개 페이지 예시 — 코코스학원','시안 B · 선생님 소개 페이지 예시 · 실제 홈페이지 아님')
os.makedirs(f'{ROOT}/preview/teacher/sample',exist_ok=True)
open(f'{ROOT}/preview/teacher/sample/index.html','w',encoding='utf-8').write(s)
print('ok')
