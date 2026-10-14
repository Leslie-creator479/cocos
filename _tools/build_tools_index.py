"""선생님용 첫 화면(tools/index.html)을 tools/ 폴더 안의 페이지들로 다시 만든다.
블로그 원고·목록 페이지를 새로 넣거나 지운 뒤 한 번 돌리면 된다. (검색 제외 페이지)

사용법: python3 _tools/build_tools_index.py
"""
import glob, html, json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
logo = re.search(r'url\((data:image/png;base64,[^)]+)\)', open('library/index.html', encoding='utf8').read()).group(1)

KIND = {'game-blog': '단어게임 블로그 원고', 'syn-blog': '동의어·반의어 블로그 원고'}
SCH = {'dongkwang': '동광고', 'seongnam': '성남고', 'seongnam-girls': '성남여고', 'seongil': '성일고', 'pungsaeng': '풍생고'}


def title_of(p):
    s = open(p, encoding='utf8').read(6000)
    m = re.search(r'<title>(.*?)</title>', s)
    return html.unescape(m.group(1)).strip() if m else p


def label(slug):
    m = re.match(r'(\d{4})-(\d{2})-g(\d)(-old)?$', slug)
    if m:
        return int(m.group(1)), f'{int(m.group(2))}월 고{m.group(3)}' + (' (예전 판)' if m.group(4) else ''), f'{m.group(1)}년'
    m = re.match(r'(\d{4})-(\d)-(mid|final)-(.+)-g(\d)$', slug)
    if m:
        term = f"{m.group(1)}년 {m.group(2)}학기 {'중간' if m.group(3) == 'mid' else '기말'}고사 · 학교별"
        return int(m.group(1)), f"{SCH.get(m.group(4), m.group(4))} {m.group(5)}학년", term
    return 0, slug, '기타'


sections = []
for kind, name in KIND.items():
    groups = {}
    for p in sorted(glob.glob(f'tools/{kind}/*/index.html')):
        slug = p.split('/')[2]
        y, lab, grp = label(slug)
        groups.setdefault(grp, []).append((y, slug, lab))
    order = sorted(groups, key=lambda g: (0 if '학교별' in g else 1, -int(re.match(r'\d+', g).group(0)) if re.match(r'\d+', g) else 0))
    sections.append({'name': name, 'groups': [{'g': g, 'items': [
        {'t': lab, 'href': f'{kind}/{slug}/'} for _, slug, lab in sorted(groups[g], key=lambda x: (x[1].replace('-old', '~')))
    ]} for g in order]})

lists = [
    {'t': '블로그 수록 지문 목록', 'd': '회차마다 학습지·동의어·단어게임 링크를 링크째 복사', 'href': 'blog-list/'},
    {'t': '교과서 지문 목록', 'd': '교과서 과별 학습지·동의어 링크 복사', 'href': 'textbook-list/'},
    {'t': '학생용 자료실', 'd': '학생에게 보내는 주소 cocosedu.kr/library', 'href': '../library/'},
]
n_drafts = sum(len(g['items']) for s in sections for g in s['groups'])
data = json.dumps({'lists': lists, 'sections': sections}, ensure_ascii=False)

page = '''<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="robots" content="noindex">
<title>코코스 선생님 자료함</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;600&family=Jost:wght@300;400;500&display=swap">
<style>
/* 선생님 자료함: 남색 머리 → 목록 페이지 세 개 → 원고 검색과 회차별 목록 */
:root{color-scheme:light;--night:#0A1424;--night-line:rgba(214,222,236,.14);--on-night:#ECEEF2;--on-night-muted:#97A2B4;
  --white:#F7F7F5;--ink:#0B1323;--muted:#5A616E;--line:#DADAD4;--gold:#C3A46C;--gold-deep:#8A6C3C;
  --sans:"Noto Sans KR","Apple SD Gothic Neo","Malgun Gothic",system-ui,sans-serif;--latin:"Jost","Futura","Avenir Next",system-ui,sans-serif}
*{box-sizing:border-box}
html{padding-top:env(safe-area-inset-top,0px)}
body{margin:0;background:var(--white);color:var(--ink);font-family:var(--sans);font-size:16px;line-height:1.7;word-break:keep-all;overflow-wrap:break-word}
a{color:inherit}
a:focus-visible,input:focus-visible{outline:2px solid var(--gold);outline-offset:3px}
.wrap{max-width:1120px;margin:0 auto;padding-inline:clamp(16px,5vw,64px)}
.cap{font-family:var(--latin);font-size:12px;font-weight:500;letter-spacing:.22em;text-transform:uppercase;color:var(--gold)}
header{background:var(--night);color:var(--on-night)}
header .wrap{padding-block:22px 40px;display:flex;flex-direction:column;gap:14px}
.top{display:flex;justify-content:space-between;align-items:center;gap:16px;margin-bottom:24px}
.logo{display:inline-block;width:104px;height:23px;background:url(__LOGO__) left center/contain no-repeat;filter:brightness(0) invert(1)}
.top a.home{color:var(--on-night-muted);font-size:14px;text-decoration:none}
h1{margin:0;font-weight:600;font-size:clamp(30px,5vw,52px);line-height:1.15;letter-spacing:-.03em}
header p{margin:0;color:var(--on-night-muted);font-weight:300;max-width:40em}
main .wrap{padding-block:40px 72px;display:flex;flex-direction:column;gap:48px}
.lists{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px}
@media (max-width:820px){.lists{grid-template-columns:1fr}}
.lists a{display:flex;flex-direction:column;gap:4px;padding:20px 22px;background:#fff;border:1px solid var(--line);text-decoration:none}
.lists a:hover{border-color:var(--gold-deep)}
.lists b{font-size:18px;font-weight:600}
.lists span{font-size:14px;color:var(--muted)}
.tools{display:flex;flex-wrap:wrap;gap:12px;align-items:baseline;justify-content:space-between;border-bottom:1px solid var(--ink);padding-bottom:12px}
.tools h2{margin:0;font-size:24px;font-weight:600;letter-spacing:-.02em}
.tools small{color:var(--muted);font-size:14px;margin-left:8px}
.search{flex:1 1 220px;max-width:320px;font:inherit;font-size:15px;background:transparent;border:0;border-bottom:1px solid var(--line);padding:8px 2px;color:var(--ink)}
section.kind{display:flex;flex-direction:column;gap:22px}
section.kind h3{margin:0;font-size:19px;font-weight:600}
.grp{display:grid;grid-template-columns:200px minmax(0,1fr);gap:8px 24px;align-items:baseline;padding-top:14px;border-top:1px solid var(--line)}
@media (max-width:640px){.grp{grid-template-columns:1fr}}
.grp .g{font-size:14px;color:var(--muted)}
.items{display:flex;flex-wrap:wrap;gap:8px}
.items a{font-size:14.5px;padding:6px 12px;border:1px solid var(--line);background:#fff;text-decoration:none;white-space:nowrap}
.items a:hover{border-color:var(--gold-deep);color:var(--gold-deep)}
.empty{color:var(--muted)}
footer{color:var(--muted);font-size:13px}
footer .wrap{padding-block:0 40px}
</style>
</head>
<body>
<header>
  <div class="wrap">
    <div class="top"><span class="logo" role="img" aria-label="COCOS"></span><a class="home" href="../">홈페이지</a></div>
    <p class="cap">For Teachers</p>
    <h1>선생님 자료함</h1>
    <p>블로그에 글을 올릴 때 쓰는 페이지를 모아 두었어요. 검색에는 나오지 않는 선생님용 페이지예요. 이 주소를 즐겨찾기에 넣어 두세요: cocosedu.kr/tools</p>
  </div>
</header>
<main>
  <div class="wrap">
    <div class="lists" id="lists"></div>
    <div>
      <div class="tools"><h2>블로그 원고<small>__N__개</small></h2>
        <input class="search" id="q" type="search" placeholder="찾기 (예: 2025 3월, 고2, 동광고)" aria-label="원고 찾기"></div>
    </div>
    <div id="sections" style="display:flex;flex-direction:column;gap:48px"></div>
  </div>
</main>
<footer><div class="wrap">원고나 목록이 새로 생기면 Claude가 이 페이지도 함께 고쳐요.</div></footer>
<script>
var D = __DATA__;
(function(){
  function esc(t){return String(t).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/"/g,'&quot;')}
  document.getElementById('lists').innerHTML=D.lists.map(function(l){return '<a href="'+esc(l.href)+'"><b>'+esc(l.t)+'</b><span>'+esc(l.d)+'</span></a>'}).join('');
  function render(){
    var q=document.getElementById('q').value.trim().toLowerCase().replace(/\\s+/g,'');
    var out=D.sections.map(function(s){
      var gs=s.groups.map(function(g){
        var it=g.items.filter(function(x){return !q||(g.g+x.t).toLowerCase().replace(/\\s+/g,'').indexOf(q)>-1});
        if(!it.length) return '';
        return '<div class="grp"><span class="g">'+esc(g.g)+'</span><div class="items">'+it.map(function(x){return '<a href="'+esc(x.href)+'">'+esc(x.t)+'</a>'}).join('')+'</div></div>';
      }).join('');
      return gs?'<section class="kind"><h3>'+esc(s.name)+'</h3>'+gs+'</section>':'';
    }).join('');
    document.getElementById('sections').innerHTML=out||'<p class="empty">찾는 원고가 없어요.</p>';
  }
  document.getElementById('q').addEventListener('input',render);
  render();
})();
</script>
</body>
</html>
'''
page = page.replace('__LOGO__', logo).replace('__DATA__', data).replace('__N__', str(n_drafts))
open('tools/index.html', 'w', encoding='utf8').write(page)
print('tools/index.html', '원고', n_drafts, '개', {s['name']: sum(len(g['items']) for g in s['groups']) for s in sections})
