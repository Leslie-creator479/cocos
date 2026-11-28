# 블로그 수록 지문 목록에 단어게임 섹션(링크 포함 복사)과 작업 현황 '게임' 배지(아래 섹션으로 이동)를 넣는다.
# 사용: python3 -I add_wg.py 입력.html 출력.html games.json
#   games.json: [{"label":"2026 9월 고1","url":"https://claude.ai/artifact/…","words":459}, …]
# 입력은 뼈대가 있어도 없어도 된다. 이미 단어게임 기능이 있으면 코드는 두고 항목만 더하거나 바꾼다.
import json, re, sys
src, out, gj = sys.argv[1:4]
s = open(src, encoding='utf8').read()
if '<body>' in s[:3000]: s = s.split('<body>', 1)[1].rsplit('</body></html>', 1)[0].lstrip('\n')
G = json.load(open(gj, encoding='utf8'))
def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (a[:60], s.count(a)); s = s.replace(a, b)
if 'function info(ex)' in s and '단어게임' not in s.split('function info(ex)')[1][:400]:
    # 1) 색 토큰
    if '--game:' not in s:
        rep('--ok:#1F7A4D; --ok-soft:#E3F3EA;\n', '--ok:#1F7A4D; --ok-soft:#E3F3EA; --game:#B0540C; --game-soft:#FDEEDF;\n')
        rep('--ok:#6FCF9B; --ok-soft:#18301F; color-scheme:dark;', '--ok:#6FCF9B; --ok-soft:#18301F; --game:#F7B06A; --game-soft:#3A2614; color-scheme:dark;', 2)
    if '.ov td a.w{' not in s:
        rep('.ov td a.y{background:var(--ok-soft);color:var(--ok)}', '.ov td a.y{background:var(--ok-soft);color:var(--ok)}\n.ov td a.w{background:var(--game-soft);color:var(--game)}')
    # 2) 안내 문구
    s = s.replace('<b style="color:var(--game)">게임</b> = 단어게임(새 탭에서 열려요). 빈칸(—)', '<b style="color:var(--game)">게임</b> = 단어게임. 빈칸(—)')
    if '= 단어게임.' not in s:
        rep('<b style="color:var(--ok)">동의어</b> = 동의어·반의어. 빈칸(—)', '<b style="color:var(--ok)">동의어</b> = 동의어·반의어, <b style="color:var(--game)">게임</b> = 단어게임. 빈칸(—)')
    # 3) 분류: 단어게임 = cat 3, 순서는 학습지 → 동의어 → 단어게임 → 학교
    rep("var m=ex.title.match(/^(\\d{4})년 (\\d+)월 고(\\d) (학력평가|동의어·반의어)/);\n  if(m) return {cat:m[4]==='학력평가'?0:1,",
        "var m=ex.title.match(/^(\\d{4})년 (\\d+)월 고(\\d) (학력평가|동의어·반의어|단어게임)/);\n  if(m) return {cat:{'학력평가':0,'동의어·반의어':1,'단어게임':3}[m[4]],")
    rep("EXAMS.sort(function(a,b){var p=a._i,q=b._i;\n  return p.cat-q.cat ||",
        "var RANK={0:0,1:1,3:2,2:3};\nEXAMS.sort(function(a,b){var p=a._i,q=b._i;\n  return RANK[p.cat]-RANK[q.cat] ||")
    rep("var CATS=['모의고사 온라인 학습지','동의어·반의어 온라인 학습지','학교별 시험 범위'];",
        "var CATS=['모의고사 온라인 학습지','동의어·반의어 온라인 학습지','학교별 시험 범위','단어게임'];")
    # 4) 작업 현황: 게임 배지 → 아래 단어게임 섹션
    s = re.sub(r'// 단어게임 주소: "학년-연도-월"\nvar WG=\{.*?\};\n', '', s, flags=re.S)
    s = s.replace("var w=WG[g+'-'+y+'-'+mo];", "var w=EXAMS.filter(function(ex){return ex._i.cat===3&&ex._i.g===g&&ex._i.y===y&&ex._i.mo===mo})[0];")
    s = s.replace("""(w?'<a class="w" href="'+w+'" target="_blank" rel="noopener">게임</a>':'')""", """(w?'<a class="w" href="#'+w.id+'">게임</a>':'')""")
    if 'var w=EXAMS.filter' not in s:
        rep("""var c=(s?'<a class="s" href="#'+s.id+'">학습지</a>':'')+(n?'<a class="y" href="#'+n.id+'">동의어</a>':'');""",
            """var w=EXAMS.filter(function(ex){return ex._i.cat===3&&ex._i.g===g&&ex._i.y===y&&ex._i.mo===mo})[0];
        var c=(s?'<a class="s" href="#'+s.id+'">학습지</a>':'')+(n?'<a class="y" href="#'+n.id+'">동의어</a>':'')+(w?'<a class="w" href="#'+w.id+'">게임</a>':'');""")
    # 5) 바로가기 줄 이름
    rep("row=i.cat===2?CATS[2]:(['모의고사','동의어'][i.cat]+' 고'+i.g)", "row=i.cat===2?CATS[2]:(['모의고사','동의어','','단어게임'][i.cat]+' 고'+i.g)")
# 6) 단어게임 항목: 같은 회차 학습지 항목을 그대로 따라 지문별 링크를 게임 범위 링크(#번호)로 바꾼다
m = re.search(r'var EXAMS=(\[.*?\]);\n', s, re.S); E = json.loads(m.group(1))
for g in G:
    y, mth, gr = g['label'].split()
    mo = int(mth[:-1]); gn = int(gr[-1])
    base = next((e for e in E if e['title'] == f"{y}년 {mo}월 고{gn} 학력평가"), None)
    if not base: print('학습지 항목 없음:', g['label']); continue
    eid = base['id'] + 'wg'
    groups = [dict(g=gp['g'], items=[[it[0], it[1], g['url'] + '#' + re.match(r'[\d~]+', it[0]).group(0).replace('~', '-')] for it in gp['items']]) for gp in base['groups']]
    n = sum(len(gp['items']) for gp in groups)
    ent = dict(id=eid, title=f"{y}년 {mo}월 고{gn} 단어게임", toc=g['url'],
               meta=f"{n}개 지문 · 단어 {g['words']}개 · 지문별 단어게임 연결", tocLabel="게임 링크 복사",
               tocNote="단어게임 주소를 복사했어요. 본문의 ‘단어게임 바로가기’ 자리에 붙여 넣으세요.", groups=groups)
    E = [e for e in E if e['id'] != eid] + [ent]
    print('추가:', ent['title'], n, '지문')
s = s[:m.start(1)] + json.dumps(E, ensure_ascii=False) + s[m.end(1):]
open(out, 'w', encoding='utf8').write(s)
open(out + '.js', 'w', encoding='utf8').write('\n'.join(re.findall(r'<script>(.*?)</script>', s, re.S)))
print('ok', len(s))
