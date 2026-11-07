"""도전 문제 진행표(tools/challenge-status/)를 홈페이지 실제 학습지에서 다시 만든다 (2026-11-08).

사용법: COCOS_LOCK_PW=… python3 _tools/challenge/status.py
  - 고등 교과서(textbook/, 중등 m… 제외)와 모의고사·수능(study/<연도>-<월>-g<학년>, study/suneung-…) 지문 학습지를
    하나씩 열어 DATA에 challenge 배열이 있는지 본다. 잠긴 교과서는 임시 폴더에 복사해 풀어서 본다(저장소 파일은 그대로).
  - 출제만 하고 검토 전인 지문은 _tools/challenge/drafts.json(보관 위치 메모 포함)에 적어 두면 '출제만' 칸으로 보인다.
  - 도전 문제를 넣고 올릴 때마다 한 번 돌리고 함께 커밋한다(선생님 자료함 '도전 문제 진행표').
"""
import glob, html, json, os, re, shutil, subprocess, sys, tempfile, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(ROOT)
OUT = 'tools/challenge-status/index.html'

BOOKS = [  # (약칭, 이름, 묶음)
    ('ce1min', '능률(민병천)', '공통영어1'), ('ce1oh', '능률(오선영)', '공통영어1'), ('ce1park', 'YBM(박준언)', '공통영어1'),
    ('ce1kang', '천재(강상구)', '공통영어1'), ('ce1cho', '천재(조수경)', '공통영어1'),
    ('ce2min', '능률(민병천)', '공통영어2'), ('ce2oh', '능률(오선영)', '공통영어2'), ('ce2park', 'YBM(박준언)', '공통영어2'),
    ('e1oh', '능률(오선영)', '영어I'), ('e1park', 'YBM(박준언)', '영어I'),
    ('neo2', '능률(오선영)', '영어II'), ('e2park', 'YBM(박준언)', '영어II'),
]


def nkey(s):
    return [int(t) if t.isdigit() else t for t in re.split(r'(\d+)', s)]


def has_ch(path):
    s = open(path, encoding='utf8').read()
    return bool(re.search(r'\n  challenge: \[', s))


drafts = {}
dj = '_tools/challenge/drafts.json'
if os.path.exists(dj):
    d = json.load(open(dj, encoding='utf8'))
    for k in d.get('items', []):
        drafts[k] = d.get('where', '')

# ---- 교과서 ----
tb_files = []
for b, _, _ in BOOKS:
    tb_files += sorted(glob.glob(f'textbook/{b}/*/*/index.html'), key=nkey)
locked = [f for f in tb_files if 'id="cocos-lock"' in open(f, encoding='utf8').read()]
tmp = tempfile.mkdtemp(prefix='chstat-')
state = {}
try:
    if locked:
        if not os.environ.get('COCOS_LOCK_PW'):
            sys.exit('잠긴 교과서를 확인하려면 COCOS_LOCK_PW가 필요합니다.')
        copies = []
        for f in locked:
            dst = os.path.join(tmp, f)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy(f, dst)
            copies.append(dst)
        r = subprocess.run(['node', '_tools/lock.mjs', 'unlock'] + copies, capture_output=True, text=True)
        if r.returncode:
            sys.exit('풀기 실패: ' + r.stderr[-500:])
    for f in tb_files:
        src = os.path.join(tmp, f) if f in locked else f
        state[f] = has_ch(src)
finally:
    shutil.rmtree(tmp, ignore_errors=True)

books = []
for b, name, grp in BOOKS:
    lessons = []
    for ld in sorted(glob.glob(f'textbook/{b}/*/'), key=nkey):
        l = ld.rstrip('/').split('/')[-1]
        ps = []
        for f in sorted(glob.glob(ld + '*/index.html'), key=nkey):
            n = f.split('/')[-2]
            key = f'textbook/{b}/{l}/{n}'
            st = 'done' if state.get(f) else ('draft' if key in drafts else 'none')
            ps.append({'n': n, 's': st})
        if ps:
            lab = ('스페셜' + (' ' + l[1:] if b != 'ce1oh' else '')) if l.startswith('s') else f'{l}과'
            lessons.append({'l': l, 'lab': lab, 'p': ps})
    books.append({'b': b, 'name': name, 'grp': grp, 'lessons': lessons})

# ---- 모의고사·수능 ----
mock = {}
for d in sorted(glob.glob('study/*/')):
    s = d.rstrip('/').split('/')[-1]
    m = re.match(r'^(\d{4})-(\d{2})-g(\d)$', s)
    sn = re.match(r'^suneung-(\d{4})-(\d{2})$', s)
    if not (m or sn):
        continue
    fs = glob.glob(d + '*/index.html')
    done = sum(1 for f in fs if has_ch(f))
    if m:
        mock[s] = {'y': int(m.group(1)), 'mo': int(m.group(2)), 'g': int(m.group(3)), 'done': done, 'n': len(fs)}
    else:
        mock[s] = {'y': int(sn.group(1)), 'mo': 11, 'g': 3, 'done': done, 'n': len(fs), 'suneung': True}

tb_tot = sum(len(L['p']) for B in books for L in B['lessons'])
tb_done = sum(1 for B in books for L in B['lessons'] for p in L['p'] if p['s'] == 'done')
tb_draft = sum(1 for B in books for L in B['lessons'] for p in L['p'] if p['s'] == 'draft')
mk_tot = sum(v['n'] for v in mock.values())
mk_done = sum(v['done'] for v in mock.values())
now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).strftime('%Y-%m-%d %H:%M')
data = {'books': books, 'mock': mock, 'sum': {'tb': [tb_done, tb_draft, tb_tot], 'mk': [mk_done, mk_tot]},
        'now': now, 'draftWhere': sorted(set(drafts.values()))}

page = r'''<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="robots" content="noindex">
<title>도전 문제 진행표</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600&family=Jost:wght@400;500&display=swap">
<style>
:root{color-scheme:light;--night:#0A1424;--on-night:#ECEEF2;--muted-n:#97A2B4;--white:#F7F7F5;--ink:#0B1323;--muted:#5A616E;--line:#DADAD4;
  --gold:#C3A46C;--gold-deep:#8A6C3C;--done:#1F6B4F;--done-bg:#E3F0EA;--draft:#B07A1E;--draft-bg:#FBF0DA;--none-bg:#fff;
  --sans:"Noto Sans KR","Apple SD Gothic Neo","Malgun Gothic",system-ui,sans-serif;--latin:"Jost",system-ui,sans-serif}
*{box-sizing:border-box}
body{margin:0;background:var(--white);color:var(--ink);font-family:var(--sans);font-size:15.5px;line-height:1.6;word-break:keep-all}
a{color:inherit}
.wrap{max-width:1120px;margin:0 auto;padding-inline:clamp(16px,5vw,56px)}
header{background:var(--night);color:var(--on-night)}
header .wrap{padding-block:22px 34px;display:flex;flex-direction:column;gap:10px}
.top{display:flex;justify-content:space-between;gap:12px;font-size:14px;color:var(--muted-n)}
.top a{text-decoration:none;color:var(--muted-n)}
.cap{font-family:var(--latin);font-size:12px;letter-spacing:.22em;text-transform:uppercase;color:var(--gold)}
h1{margin:0;font-size:clamp(28px,4.6vw,44px);font-weight:600;letter-spacing:-.03em;line-height:1.2}
header p{margin:0;color:var(--muted-n);max-width:44em}
main .wrap{padding-block:30px 64px;display:flex;flex-direction:column;gap:40px}
.sum{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px}
@media (max-width:760px){.sum{grid-template-columns:1fr}}
.card{background:#fff;border:1px solid var(--line);padding:18px 20px;display:flex;flex-direction:column;gap:6px}
.card .k{font-size:13px;color:var(--muted)}
.card .v{font-size:28px;font-weight:600;letter-spacing:-.02em}
.card .v small{font-size:15px;font-weight:400;color:var(--muted)}
.bar{height:8px;background:#ECECE6;display:flex;overflow:hidden}
.bar i{display:block;height:100%}
.bar .d{background:var(--done)} .bar .f{background:var(--draft)}
.legend{display:flex;flex-wrap:wrap;gap:16px;font-size:13.5px;color:var(--muted);align-items:center}
.sq{display:inline-block;width:14px;height:14px;border:1px solid var(--line);vertical-align:-2px;margin-right:5px}
.sq.done{background:var(--done);border-color:var(--done)} .sq.draft{background:var(--draft-bg);border-color:var(--draft)} .sq.none{background:#fff}
h2{margin:0 0 4px;font-size:22px;font-weight:600;letter-spacing:-.02em;border-bottom:1px solid var(--ink);padding-bottom:10px;display:flex;justify-content:space-between;align-items:baseline;gap:12px;flex-wrap:wrap}
h2 small{font-size:14px;font-weight:400;color:var(--muted)}
.grp{margin-top:18px}
.grp h3{margin:0 0 8px;font-size:15px;color:var(--muted);font-weight:500}
.book{display:grid;grid-template-columns:150px minmax(0,1fr) 70px;gap:8px 18px;align-items:start;padding:12px 0;border-top:1px solid var(--line)}
@media (max-width:700px){.book{grid-template-columns:1fr auto}.book .ls{grid-column:1/-1}}
.book .t{font-weight:500}
.book .c{text-align:right;font-size:14px;color:var(--muted);font-variant-numeric:tabular-nums}
.ls{display:flex;flex-wrap:wrap;gap:6px 10px}
.l{display:inline-flex;align-items:center;gap:5px;padding:4px 8px;border:1px solid var(--line);background:#fff;font-size:13.5px}
.l.full{border-color:var(--done);background:var(--done-bg)}
.l b{font-weight:500;white-space:nowrap}
.l .dots{display:inline-flex;gap:2px}
.l .dots span{width:9px;height:9px;border:1px solid #C9C9C2;background:#fff}
.l .dots span.done{background:var(--done);border-color:var(--done)}
.l .dots span.draft{background:var(--draft-bg);border-color:var(--draft)}
table{border-collapse:collapse;width:100%;font-size:14px;font-variant-numeric:tabular-nums}
.tw{overflow-x:auto}
th,td{border-top:1px solid var(--line);padding:8px 6px;text-align:center;white-space:nowrap}
th{font-weight:500;color:var(--muted);font-size:13px}
td.y{text-align:left;font-weight:500}
td .cell{display:inline-block;min-width:54px;padding:3px 6px;border:1px solid var(--line);background:#fff}
td .cell.full{background:var(--done);color:#fff;border-color:var(--done)}
td .cell.part{background:var(--done-bg);border-color:var(--done)}
td .na{color:#C9C9C2}
.how{background:#fff;border:1px solid var(--line);padding:18px 20px;font-size:14.5px}
.how ul{margin:6px 0 0;padding-left:18px}
footer{color:var(--muted);font-size:13px}footer .wrap{padding-block:0 36px}
</style>
</head>
<body>
<header><div class="wrap">
  <div class="top"><span class="cap">For Teachers</span><a href="../">← 선생님 자료함</a></div>
  <h1>도전 문제 진행표</h1>
  <p>고등 교과서·모의고사 학습지마다 ‘도전 문제(고난도 10문항)’가 들어갔는지 홈페이지 실제 학습지를 읽어서 만든 표예요. 작업을 올릴 때마다 함께 새로 고칩니다. <span id="now"></span></p>
</div></header>
<main><div class="wrap">
  <div class="sum" id="sum"></div>
  <div class="legend"><span><span class="sq done"></span>도전 문제 있음</span><span><span class="sq draft"></span>출제만 해 둠(검토 전)</span><span><span class="sq none"></span>아직 없음</span></div>
  <section><h2>교과서<small id="tbc"></small></h2><div id="tb"></div></section>
  <section><h2>모의고사·수능<small id="mkc"></small></h2><div class="tw" id="mk"></div></section>
  <div class="how"><b>작업을 맡기실 때</b>
    <ul><li>이 표를 보고 “공통영어2 오선영 3·4과 도전 문제”, “2025년 9월 고2 도전 문제”처럼 말씀해 주시면 그 범위부터 합니다.</li>
    <li>한 번에 교과서 두 과(10지문 안팎) 또는 모의고사 한 회차(22지문)가 알맞아요. 출제와 검토를 거쳐 올리는 데 30분~1시간쯤 걸립니다(모의고사 한 회차는 조금 더).</li>
    <li id="dw"></li></ul></div>
</div></main>
<footer><div class="wrap">만드는 도구: _tools/challenge/status.py · 검색에는 나오지 않는 선생님용 페이지예요.</div></footer>
<script>
var D = __DATA__;
(function(){
  function esc(t){return String(t).replace(/&/g,'&amp;').replace(/</g,'&lt;')}
  function pct(a,b){return b?Math.round(a*100/b):0}
  document.getElementById('now').textContent='(마지막 갱신 '+D.now+')';
  var t=D.sum.tb,m=D.sum.mk,all=t[0]+m[0],tot=t[2]+m[1];
  function card(k,done,draft,n){return '<div class="card"><span class="k">'+k+'</span><span class="v">'+done+'<small> / '+n+' 지문 · '+pct(done,n)+'%</small></span>'+
    '<div class="bar"><i class="d" style="width:'+pct(done,n)+'%"></i><i class="f" style="width:'+pct(draft,n)+'%"></i></div>'+
    (draft?'<span class="k">출제만 해 둠 '+draft+'지문</span>':'')+'</div>'}
  document.getElementById('sum').innerHTML=card('전체',all,t[1],tot)+card('교과서',t[0],t[1],t[2])+card('모의고사·수능',m[0],0,m[1]);
  document.getElementById('tbc').textContent=t[0]+' / '+t[2]+' 지문';
  document.getElementById('mkc').textContent=m[0]+' / '+m[1]+' 지문';
  var groups=[],gi={};
  D.books.forEach(function(b){if(!(b.grp in gi)){gi[b.grp]=groups.length;groups.push({g:b.grp,bs:[]})}groups[gi[b.grp]].bs.push(b)});
  document.getElementById('tb').innerHTML=groups.map(function(G){
    return '<div class="grp"><h3>'+esc(G.g)+'</h3>'+G.bs.map(function(b){
      var n=0,d=0;
      var ls=b.lessons.map(function(L){
        var dd=L.p.filter(function(p){return p.s==='done'}).length;n+=L.p.length;d+=dd;
        return '<span class="l'+(dd===L.p.length?' full':'')+'" title="'+esc(L.lab)+' '+dd+'/'+L.p.length+'"><b>'+esc(L.lab)+'</b><span class="dots">'+
          L.p.map(function(p){return '<span class="'+p.s+'" title="'+esc(L.lab)+' '+esc(p.n)+'번"></span>'}).join('')+'</span></span>'}).join('');
      return '<div class="book"><span class="t">'+esc(b.name)+'</span><div class="ls">'+ls+'</div><span class="c">'+d+' / '+n+'</span></div>'}).join('')+'</div>'}).join('');
  var M=D.mock,years={},hasSn={};
  Object.keys(M).forEach(function(k){var v=M[k];(years[v.y]=years[v.y]||{})[v.suneung?'sn':(v.mo+'-'+v.g)]=v});
  var cols=[[3,1],[3,2],[6,1],[6,2],[9,1],[9,2],[10,1],[10,2],[11,1],[11,2]];
  function cell(v){if(!v)return '<span class="na">—</span>';var c=v.done===v.n?' full':(v.done?' part':'');return '<span class="cell'+c+'">'+v.done+'/'+v.n+'</span>'}
  var ys=Object.keys(years).sort(function(a,b){return b-a});
  document.getElementById('mk').innerHTML='<table><thead><tr><th></th>'+cols.map(function(c){return '<th>'+c[0]+'월 고'+c[1]+'</th>'}).join('')+'<th>수능</th></tr></thead><tbody>'+
    ys.map(function(y){var r=years[y];return '<tr><td class="y">'+y+'</td>'+cols.map(function(c){return '<td>'+cell(r[c[0]+'-'+c[1]])+'</td>'}).join('')+'<td>'+cell(r.sn)+'</td></tr>'}).join('')+'</tbody></table>'+
    '<p style="font-size:13px;color:var(--muted);margin:8px 0 0">수능은 시행 연도 줄에 있어요(예: 2025년 줄 = 2026학년도 수능).</p>';
  document.getElementById('dw').textContent=D.draftWhere.length?('‘출제만 해 둠’ 지문의 문제 파일 보관 위치: '+D.draftWhere.join(' / ')):'출제만 해 두고 검토 전인 지문은 없어요.';
})();
</script>
</body>
</html>
'''
os.makedirs(os.path.dirname(OUT), exist_ok=True)
open(OUT, 'w', encoding='utf8').write(page.replace('__DATA__', json.dumps(data, ensure_ascii=False)))
print(f'교과서 {tb_done}/{tb_tot} (출제만 {tb_draft}) · 모의고사·수능 {mk_done}/{mk_tot} → {OUT}')
