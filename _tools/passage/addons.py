"""코코스 온라인 학습지 추가 규칙을 한 번에 적용한다. 몇 번 실행해도 같은 결과(이미 된 것은 건너뜀).
사용법: python3 addons.py 원본.html 결과.html [brief.js]
  1) Artifact read(path)로 받은 파일이면 서버 겉틀을 뗀다.
  2) 결과 박스 CSS `.done{display:flex` → `div.done{display:flex`
  3) 문장 배열: 마지막 어구의 끝 기호(. ? ! + 닫는 따옴표)를 떼고 '내가 만든 문장' 칸 끝에 고정 표시
  4) brief.js를 주면 지문 앞에 '먼저 읽어 보세요' 칸을 넣는다(DATA.brief). 이미 있으면 DATA.brief만 바꾼다.
"""
import re, sys
src, out = sys.argv[1], sys.argv[2]
brief = sys.argv[3] if len(sys.argv) > 3 else None
s = open(src, encoding='utf8').read()
if s.startswith('<!doctype html><html><head>') and '<body>\n<title>' in s[:2000]:
    s = s[s.index('<body>\n') + 7:]
    assert s.rstrip().endswith('</body></html>')
    s = s.rstrip()[:-len('</body></html>')].rstrip() + '\n'
done = []
# 2) div.done
if 'div.done{display:flex' not in s:
    assert s.count('\n.done{display:flex') == 1, 'done CSS'
    s = s.replace('\n.done{display:flex', '\ndiv.done{display:flex'); done.append('div.done')
# 3) 문장 배열 끝 기호
ORD_CSS_ANCHOR = '.tray-empty{font-size:14px;color:var(--muted);align-self:center}'
ORD_CSS = '\n.tray-end{font-family:var(--serif-en);font-size:17px;color:var(--muted);align-self:center;margin-left:-3px;padding:0 2px}'
ORD = [
    ("function label(i){ return i===0?lc(cur.tk[0],cur.it):cur.tk[i]; }",
     "var END=/[.?!]+[\\u201D\\u2019\"')]*$/;\n"
     "  function tail(){ var m=cur.tk[cur.tk.length-1].match(END); return m?m[0]:''; }\n"
     "  function label(i){ var t=i===0?lc(cur.tk[0],cur.it):cur.tk[i]; if(i===cur.tk.length-1&&cur.tk.length>1){ var r=t.replace(END,''); if(r) t=r; } return t; }"),
    ("'<span class=\"tray-empty\">아래 어구를 순서대로 눌러 보세요.</span>')+'</div>';",
     "'<span class=\"tray-empty\">아래 어구를 순서대로 눌러 보세요.</span>')+(cur.tray.length&&tail()&&cur.tk.length>1?'<span class=\"tray-end\" aria-hidden=\"true\">'+esc(tail())+'</span>':'')+'</div>';"),
    ("else if(tray.lastElementChild!==el) tray.appendChild(el);",
     "else { var tl=tray.querySelector('.tray-end'); if(tl){ if(el.nextSibling!==tl) tray.insertBefore(el,tl); } else if(tray.lastElementChild!==el) tray.appendChild(el); }"),
]
if 'function tail(){' not in s:
    assert s.count(ORD_CSS_ANCHOR) == 1, 'order css'
    s = s.replace(ORD_CSS_ANCHOR, ORD_CSS_ANCHOR + ORD_CSS)
    for a, b in ORD:
        assert s.count(a) == 1, ('order code', a[:40])
        s = s.replace(a, b)
    done.append('끝 기호 숨김')
# 4) 먼저 읽어 보세요
CSS = r'''.brief{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:22px clamp(16px,3.5vw,28px);display:flex;flex-direction:column;gap:20px}
.b-lab{display:block;font-size:12.5px;font-weight:700;letter-spacing:.04em;color:var(--accent-ink);margin:0 0 8px}
.b-one{background:var(--accent-soft);border-radius:10px;padding:14px 16px}
.b-one p{margin:0;font-family:var(--serif-ko);font-size:18px;line-height:1.7;color:var(--ink)}
.b-flow{list-style:none;margin:0;padding:0;display:flex;flex-direction:column}
.b-step{display:grid;grid-template-columns:5.6em minmax(0,1fr);gap:0 14px;position:relative;padding-bottom:16px}
.b-step:last-child{padding-bottom:0}
.b-step::before{content:"";position:absolute;left:2.8em;top:34px;bottom:2px;border-left:2px solid var(--line)}
.b-step:last-child::before{display:none}
.b-go{align-self:start;justify-self:stretch;position:relative;z-index:1;font-size:13px;font-weight:700;color:var(--accent-ink);background:var(--accent-soft);border:1px solid color-mix(in srgb,var(--accent) 35%,transparent);border-radius:999px;padding:4px 6px;font-variant-numeric:tabular-nums;white-space:nowrap}
.b-go:hover{border-color:var(--accent)}
.b-step .t{font-weight:700;font-size:15.5px;display:flex;flex-wrap:wrap;align-items:center;gap:6px;padding-top:3px}
.b-step .d{margin:3px 0 0;font-size:15px;color:var(--muted);line-height:1.7}
.b-turn{font-size:11.5px;font-weight:700;padding:1px 8px;border-radius:999px;background:var(--ex-soft);color:var(--ex-ink);border:1px solid var(--ex)}
.b-step.turn .b-go{background:var(--ex-soft);color:var(--ex-ink);border-color:color-mix(in srgb,var(--ex) 45%,transparent)}
.b-keys{display:flex;flex-wrap:wrap;gap:8px}
.b-keys span{border:1px solid var(--line);border-radius:999px;padding:4px 12px;font-size:14px}
.b-keys i{font-family:var(--serif-en);font-weight:600;margin-right:6px}
.b-tips{margin:0;padding:0;list-style:none;display:flex;flex-direction:column;gap:8px}
.b-tips li{display:grid;grid-template-columns:3.2em minmax(0,1fr);gap:10px;font-size:14.5px;line-height:1.7}
.b-tips b.n{font-size:13px;color:var(--accent-ink);padding-top:1px}
.b-tips i{font-family:var(--serif-en)}
.b-ask{display:flex;flex-direction:column;gap:8px}
.b-ask details{border:1px solid var(--line);border-radius:10px;padding:10px 14px;font-size:15px}
.b-ask summary{cursor:pointer;font-weight:500;list-style:none;display:flex;gap:8px;align-items:baseline}
.b-ask summary::-webkit-details-marker{display:none}
.b-ask summary .bq{flex:1 1 0;min-width:0}
.b-ask summary::after{content:"생각해 보고 눌러 확인";margin-left:auto;flex:none;font-size:12.5px;color:var(--accent);font-weight:400}
.b-ask details[open] summary::after{content:"접기"}
.b-ask details p{margin:8px 0 0;color:var(--accent-ink);background:var(--accent-soft);border-radius:8px;padding:8px 12px;font-size:14.5px}
@media (max-width:520px){.b-step{grid-template-columns:5.2em minmax(0,1fr);gap:0 10px}.b-step::before{left:2.6em}.b-ask summary{flex-wrap:wrap}.b-ask summary::after{margin-left:2.2em;flex-basis:100%}}
'''
SECTION = '''  <section id="brief" aria-labelledby="h-brief">
    <div class="sec-head"><div><h2 id="h-brief">먼저 읽어 보세요</h2><p>지문을 읽기 전에 1분만 훑어보세요. 글의 뼈대를 알고 읽으면 훨씬 잘 읽혀요. 문장 번호를 누르면 지문에서 그 문장들이 표시돼요.</p></div></div>
    <div class="brief">
      <div class="b-one"><span class="b-lab">한 줄로 말하면</span><p id="b-one"></p></div>
      <div><span class="b-lab">글의 흐름</span><ol class="b-flow" id="b-flow"></ol></div>
      <div><span class="b-lab">핵심어</span><div class="b-keys" id="b-keys"></div></div>
      <div><span class="b-lab">읽다가 막히기 쉬운 곳</span><ul class="b-tips" id="b-tips"></ul></div>
      <div><span class="b-lab">지문을 다 읽은 뒤에 스스로 답해 보기</span><div class="b-ask" id="b-ask"></div></div>
    </div>
  </section>

'''
JS = r'''
  /* ---- 먼저 읽어 보세요 ---- */
  (function(){
    var B=DATA.brief, sec=$('brief'); if(!B||!sec){ if(sec) sec.hidden=true; return; }
    function rng(a){ return a.length>1&&a[a.length-1]-a[0]===a.length-1 ? a[0]+'~'+a[a.length-1]+'번' : a.join('·')+'번'; }
    $('b-one').innerHTML=B.one;
    $('b-flow').innerHTML=B.flow.map(function(f){return '<li class="b-step'+(f.turn?' turn':'')+'"><button type="button" class="b-go" data-s="'+f.s.join(',')+'" aria-label="지문 '+rng(f.s)+' 문장 보기">'+rng(f.s)+'</button><div><div class="t">'+(f.turn?'<span class="b-turn">'+f.turn+'</span>':'')+f.t+'</div><p class="d">'+f.d+'</p></div></li>'}).join('');
    $('b-keys').innerHTML=B.keys.map(function(k){return '<span><i>'+k[0]+'</i>'+k[1]+'</span>'}).join('');
    $('b-tips').innerHTML=B.tips.map(function(t){return '<li><b class="n">'+t[0]+'</b><span>'+t[1]+'</span></li>'}).join('');
    $('b-ask').innerHTML=B.ask.map(function(q,i){return '<details><summary><b>Q'+(i+1)+'.</b><span class="bq">'+q[0]+'</span></summary><p>'+q[1]+'</p></details>'}).join('');
    $('b-flow').addEventListener('click',function(e){
      var b=e.target.closest('.b-go'); if(!b) return;
      var ids=b.getAttribute('data-s').split(',');
      document.querySelectorAll('.node.active').forEach(function(n){n.classList.remove('active')});
      document.querySelectorAll('#links path.on').forEach(function(p){p.classList.remove('on')});
      document.querySelectorAll('.sent').forEach(function(s){s.classList.toggle('hl',ids.indexOf(s.getAttribute('data-s'))>-1)});
      var first=document.querySelector('.sent[data-s="'+ids[0]+'"]');
      if(first){ try{ first.scrollIntoView({behavior:'smooth',block:'center'}); }catch(err){ first.scrollIntoView(); } }
    });
  })();
'''
if brief:
    b = open(brief, encoding='utf8').read().rstrip() + '\n'
    assert b.lstrip().startswith('brief: {') and b.rstrip().endswith('},'), 'brief.js 형식'
    if 'id="brief"' in s:
        s, k = re.subn(r"\n  brief: \{[\s\S]*?\n  \},\n", lambda m: '\n' + b, s, count=1)
        assert k == 1; done.append('먼저 읽어 보세요(내용 교체)')
    else:
        assert s.count('@media (prefers-reduced-motion:reduce)') == 1
        s = s.replace('@media (prefers-reduced-motion:reduce)', CSS + '@media (prefers-reduced-motion:reduce)')
        nav = '<nav class="jump" aria-label="바로가기"><a href="#passage">지문</a>'
        assert s.count(nav) == 1
        s = s.replace(nav, nav.replace('<a href="#passage">', '<a href="#brief">먼저 읽기</a><a href="#passage">'))
        assert s.count('  <section id="passage"') == 1
        s = s.replace('  <section id="passage"', SECTION + '  <section id="passage"')
        m = re.search(r"\n  footer: '[^\n]*',\n", s); assert m
        s = s[:m.end()] + b + s[m.end():]
        anchor = "$('footer').textContent=DATA.footer;\n"
        assert s.count(anchor) == 1
        s = s.replace(anchor, anchor + JS)
        done.append('먼저 읽어 보세요')
open(out, 'w', encoding='utf8').write(s)
print(out, len(s.encode()) // 1024, 'KB', '적용:', ', '.join(done) or '없음(이미 적용됨)')
