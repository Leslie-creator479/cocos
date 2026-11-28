"""목차 온라인 학습지를 만든다.
사용법: python3 build_toc.py toc.json 출력.html "교재명" "짧은 이름"
  예: python3 build_toc.py toc.json out/toc/index.html "EBS 올림포스 기출 2" "올림포스 기출2"
toc.json: [{"g": "1강", "n": "3번", "t": "핵심 개념", "h": "한국어 제목(h1)", "e": "영어 제목", "u": "온라인 학습지 링크"}, ...] (보여 줄 순서대로)
템플릿(template.html)의 <style>(색·로고·학원 카드·바닥글)과 학원 소개 카드를 그대로 가져온다."""
import json, re, sys
items = json.load(open(sys.argv[1], encoding='utf8'))
out, book, short = sys.argv[2], sys.argv[3], sys.argv[4]
t = open('template.html', encoding='utf8').read()
style = re.search(r'<style>([\s\S]*?)</style>', t).group(1)
head = t[:t.index('<style>')]
head = re.sub(r'<title>.*?</title>', '<title>[코코스학원] ' + short + ' 온라인 학습지 목차</title>', head, count=1)
promo = re.search(r'  <section id="academy"[\s\S]*?</section>\n', t).group(0)
CSS = r'''
.toc-tools{display:flex;flex-wrap:wrap;gap:10px 16px;align-items:center;justify-content:space-between}
.inc{display:flex;flex-wrap:wrap;gap:6px;font-size:13px;color:var(--muted);align-items:center}
.inc span.pill{border:1px solid var(--line);background:var(--card);border-radius:999px;padding:2px 10px;color:var(--ink)}
.search{flex:1 1 220px;max-width:320px;font:inherit;font-size:15px;color:var(--ink);background:var(--card);border:1px solid var(--line);border-radius:10px;padding:9px 12px}
.search:focus-visible{outline:2px solid var(--accent);outline-offset:1px}
.lessons{display:flex;flex-direction:column;gap:32px}
.lesson h2{display:flex;align-items:baseline;gap:10px;margin-bottom:12px}
.lesson h2 small{font-family:var(--sans);font-size:14px;font-weight:500;color:var(--muted)}
.toc{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}
@media (max-width:640px){.toc{grid-template-columns:1fr}}
.toc a{display:grid;grid-template-columns:auto minmax(0,1fr) auto;gap:4px 14px;align-items:center;height:100%;text-decoration:none;color:inherit;background:var(--card);border:1px solid var(--line);border-radius:12px;padding:14px 16px;transition:border-color .15s,background-color .15s}
.toc a:hover{border-color:var(--accent);background:color-mix(in srgb,var(--accent-soft) 45%,var(--card))}
.toc a:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.toc .no{grid-row:1 / span 3;align-self:start;min-width:3.2em;text-align:center;font-size:13px;font-weight:700;color:var(--accent-ink);background:var(--accent-soft);border-radius:8px;padding:6px 8px;font-variant-numeric:tabular-nums}
.toc .kc{font-size:12.5px;font-weight:500;color:var(--ex-ink)}
.toc .ti{font-family:var(--serif-ko);font-size:17px;font-weight:700;line-height:1.45}
.toc .en{font-family:var(--serif-en);font-style:italic;font-size:14px;color:var(--muted);line-height:1.45}
.toc .go{grid-column:3;grid-row:1 / span 3;color:var(--accent);font-size:20px}
.empty{color:var(--muted);font-size:15px}
'''
BODY = '''
<div class="wrap">
  <header>
    <a class="brand" href="#academy"><span class="logo" role="img" aria-label="코코스학원"></span><span>코코스학원 온라인 학습지 · 학습과 컨설팅을 하나로</span></a>
    <div class="src" id="chips"></div>
    <h1 id="h1"></h1>
    <p class="gist" id="gist"></p>
    <nav class="jump" id="jump" aria-label="바로가기"></nav>
  </header>

  <section aria-label="온라인 학습지 목록" style="display:flex;flex-direction:column;gap:20px">
    <div class="toc-tools">
      <div class="inc"><span>지문마다 들어 있는 것</span><span class="pill">문장별 해석</span><span class="pill">문장 듣기</span><span class="pill">발음 단어장</span><span class="pill">단어 퀴즈</span><span class="pill">마인드맵</span><span class="pill">확인 퀴즈 15문항</span><span class="pill">문장 배열</span></div>
      <input class="search" id="q" type="search" placeholder="제목·주제로 찾기 (예: 공감, Thoreau)" aria-label="온라인 학습지 찾기">
    </div>
    <div class="lessons" id="lessons"></div>
  </section>

__PROMO__
  <footer>
    <p class="copy">© <span id="yr">2026</span> 코코스학원. 이 온라인 학습지의 문제·해설·단어 정리·마인드맵은 코코스학원이 만들었어요.</p>
    <p>링크는 누구에게나 자유롭게 공유해도 좋아요. 다만 내용을 복제·수정해 다른 곳에 올리거나 상업적으로 이용하는 것은 금지해요.</p>
    <p id="footer"></p>
  </footer>
</div>

<script>
/* ==== TOC:START ==== */
var TOC = __TOC__;
/* ==== TOC:END ==== */
(function(){
  var $=function(id){return document.getElementById(id)};
  function esc(t){return String(t).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/"/g,'&quot;')}
  $('yr').textContent=new Date().getFullYear();
  $('chips').innerHTML=TOC.chips.map(function(c){return '<span class="chip">'+esc(c)+'</span>'}).join('');
  $('h1').textContent=TOC.h1; $('gist').textContent=TOC.gist; $('footer').textContent=TOC.footer;
  var L=[]; TOC.items.forEach(function(it){ if(L.indexOf(it.g)<0) L.push(it.g); });
  $('jump').innerHTML=L.map(function(g,k){return '<a href="#g'+k+'">'+esc(g)+'</a>'}).join('')+'<a href="#academy">코코스학원</a>';
  function render(q){
    q=(q||'').trim().toLowerCase(); var html='', shown=0;
    L.forEach(function(g,k){
      var rows=TOC.items.filter(function(it){ return it.g===g && (!q || (it.t+' '+it.h+' '+it.e+' '+it.g+' '+it.n).toLowerCase().indexOf(q)>-1); });
      if(!rows.length) return; shown+=rows.length;
      html+='<section class="lesson" id="g'+k+'" aria-labelledby="hg'+k+'"><h2 id="hg'+k+'">'+esc(g)+' <small>'+rows.length+'개 지문</small></h2><ul class="toc">'+rows.map(function(it){
        return '<li><a href="'+esc(it.u)+'" target="_blank" rel="noopener"><span class="no">'+esc(it.n)+'</span><span class="kc">'+esc(it.t)+'</span><span class="ti">'+esc(it.h)+'</span><span class="en">'+esc(it.e)+'</span><span class="go" aria-hidden="true">→</span></a></li>'}).join('')+'</ul></section>';
    });
    $('lessons').innerHTML=html||'<p class="empty">찾는 지문이 없어요. 다른 말로 찾아보세요.</p>';
  }
  $('q').addEventListener('input',function(e){render(e.target.value)});
  render('');
})();
</script>
'''
toc = {'chips': [book, f'{len(items)}개 지문'],
       'h1': book.replace('EBS ', '') + ' 온라인 학습지',
       'gist': '공부할 지문을 눌러 들어가세요. 지문마다 해석, 문장 듣기, 단어, 마인드맵, 확인 퀴즈, 문장 배열까지 한 곳에서 공부할 수 있어요.',
       'footer': '지문 출처: ' + book,
       'items': items}
body = BODY.replace('__PROMO__', promo).replace('__TOC__', json.dumps(toc, ensure_ascii=False, indent=1))
html = head + '<style>' + style + CSS + '</style>\n' + body
open(out, 'w', encoding='utf8').write(html)
print(out, len(html.encode())//1024, 'KB')
