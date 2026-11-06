/* ==== GRAM ENGINE (코코스 중등 문법, 2026-11-06) ==== */
(function(){
  var $=function(id){return document.getElementById(id)};
  var NUMS=['①','②','③','④','⑤','⑥'];
  var D=DATA;
  // 머리말
  $('chips').innerHTML=D.chips.map(function(c){return '<span class="chip">'+c+'</span>'}).join('');
  $('h1').innerHTML=D.h1; $('en-title').textContent=D.enTitle; $('gist').innerHTML=D.gist; $('footer').innerHTML=D.footer;
  var yr=$('yr'); if(yr) yr.textContent=new Date().getFullYear();

  // 비교용 정리: 대소문자·끝 문장부호·띄어쓰기·따옴표
  function soft(t){return String(t).replace(/[‘’]/g,"'").replace(/[“”]/g,'"').replace(/\s+/g,' ').replace(/\s+([,.?!])/g,'$1').trim();}
  function loose(t){return soft(t).toLowerCase().replace(/[.?!]+$/,'').trim();}
  function words(t){var s=soft(t).replace(/[.,?!"]/g,' ').trim(); return s?s.split(/\s+/).length:0;}

  // 1. 먼저 풀어 보기 (O/X)
  (function(){
    var H=D.hook, box=$('hook-list'); if(!H||!box) return;
    $('hook-intro').innerHTML=H.intro;
    var done=0, ok=0;
    H.items.forEach(function(it,i){
      var c=document.createElement('div'); c.className='g-card';
      c.innerHTML='<p class="g-en"><span class="g-n">'+(i+1)+'</span>'+it.en+'</p><div class="ox" role="group" aria-label="'+(i+1)+'번 문장 판단"><button type="button" data-v="1" aria-label="맞는 문장">O</button><button type="button" data-v="0" aria-label="틀린 문장">X</button></div>';
      box.appendChild(c);
      var bs=[].slice.call(c.querySelectorAll('.ox button'));
      bs.forEach(function(b){ b.addEventListener('click',function(){
        var v=b.getAttribute('data-v')==='1', right=v===it.ok;
        bs.forEach(function(x){x.disabled=true; if((x.getAttribute('data-v')==='1')===it.ok) x.classList.add('right');});
        if(!right) b.classList.add('wrong');
        var fb=document.createElement('div'); fb.className='fb';
        fb.innerHTML=(right?'<b class="ok">맞혔어요!</b> ':'<b class="no">아쉬워요. '+(it.ok?'맞는 문장이에요.':'틀린 문장이에요.')+'</b> ')+it.e;
        c.appendChild(fb);
        if(it.fix){ var f=document.createElement('p'); f.className='g-fix'; f.innerHTML=it.fix; c.appendChild(f); }
        done++; if(right) ok++;
        if(done===H.items.length){ var d=document.createElement('div'); d.className='done'; d.innerHTML='<span>'+H.items.length+'문장 중 '+ok+'문장 맞힘 · '+H.after+'</span>'; box.appendChild(d); }
      });});
    });
  })();

  // 2. 한눈에 정리
  (function(){
    var R=D.rule, g=$('rule-cards'); if(!R||!g) return;
    g.innerHTML=R.cards.map(function(c){
      var h='<div class="r-card'+(c.key?' key':'')+'"><span class="lab">'+c.lab+(c.sub?'<small>'+c.sub+'</small>':'')+'</span>';
      if(c.t) h+='<p>'+c.t+'</p>';
      if(c.w) h+='<div class="w">'+c.w.map(function(x){return '<span>'+x+'</span>'}).join('')+'</div>';
      if(c.ex) h+='<p class="ex">'+c.ex+(c.ko?'<small>'+c.ko+'</small>':'')+'</p>';
      return h+'</div>';
    }).join('');
    if(R.table){ var t='<div class="r-wrap"><table class="r-tbl"><thead><tr>'+R.table.head.map(function(x){return '<th>'+x+'</th>'}).join('')+'</tr></thead><tbody>'+R.table.rows.map(function(r){return '<tr>'+r.map(function(x){return '<td>'+x+'</td>'}).join('')+'</tr>'}).join('')+'</tbody></table></div>'; $('rule-table').innerHTML=(R.tableTitle?'<p class="r-tt">'+R.tableTitle+'</p>':'')+t; }
    if(R.tips) $('rule-tips').innerHTML=R.tips.map(function(x){return '<li>'+x+'</li>'}).join('');
  })();

  // 3. 지문 속 문장 (녹음)
  (function(){
    var S=D.sentences, box=$('ex-list'); if(!S||!box) return;
    var au=null, cur=null;
    function stop(){ if(au){au.pause(); au=null;} if(cur){cur.setAttribute('aria-pressed','false'); cur.textContent='▶'; cur=null;} }
    S.forEach(function(s,i){
      var c=document.createElement('div'); c.className='g-card';
      c.innerHTML='<div class="ex-row"><button type="button" class="play" aria-pressed="false" aria-label="'+(i+1)+'번 문장 듣기">▶</button><div class="ex-body"><span class="ex-tag'+(s.past?' past':'')+'">'+s.tag+'</span><p class="g-en">'+s.show+'</p><p class="g-ko">'+s.ko+'</p>'+(s.note?'<p class="ex-note">'+s.note+'</p>':'')+'</div></div>';
      box.appendChild(c);
      var b=c.querySelector('.play');
      b.addEventListener('click',function(){
        var was=cur===b; stop(); if(was) return;
        var src=(typeof SAUDIO!=='undefined'&&SAUDIO[i])||'';
        if(!src){ if(window.speechSynthesis){var u=new SpeechSynthesisUtterance(s.en.replace(/<[^>]+>/g,''));u.lang='en-US';speechSynthesis.cancel();speechSynthesis.speak(u);} return; }
        au=new Audio(src); cur=b; b.setAttribute('aria-pressed','true'); b.textContent='■';
        au.onended=stop; au.play().catch(stop);
      });
    });
  })();

  // 4. 단계별 문제 (객관식)
  function quiz(Q,boxId,scoreId,secId,doneMsg){
    var qs=$(boxId), scoreEl=$(scoreId); if(!Q||!qs) return;
    var answered=0, correct=0;
    function upd(){ if(scoreEl) scoreEl.innerHTML='<b>'+correct+'</b> / '+Q.length; }
    function render(){
      qs.innerHTML=''; answered=0; correct=0; upd();
      Q.forEach(function(q,i){
        var box=document.createElement('div'); box.className='q';
        var h='<div class="num">문항 '+(i+1)+'<span class="type" data-k="'+q.type.split(' ')[0]+'">'+q.type+'</span>'+(q.lv?'<span class="lv" data-lv="'+q.lv+'">'+q.lv+'</span>':'')+'</div><p class="prompt">'+q.p+'</p>';
        if(q.q) h+='<p class="quote">'+q.q+'</p>';
        h+='<div class="opts" role="group" aria-label="문항 '+(i+1)+' 선택지">';
        q.o.forEach(function(t,j){ var n=NUMS[j], same=(t===n);
          h+='<button class="opt'+(q.en?' en-o':'')+'" data-j="'+j+'"><span class="n">'+n+'</span>'+(same?'':'<span>'+t+'</span>')+'</button>'; });
        h+='</div>';
        if(q.h) h+='<button class="hint">힌트 보기</button>';
        box.innerHTML=h; qs.appendChild(box);
        if(q.h){ var hb=box.querySelector('.hint'); hb.addEventListener('click',function(){var p=document.createElement('p');p.className='hint-text';p.innerHTML='힌트: '+q.h;hb.replaceWith(p);}); }
        var opts=[].slice.call(box.querySelectorAll('.opt'));
        opts.forEach(function(b){ b.addEventListener('click',function(){
          var j=+b.getAttribute('data-j'), ok=j===q.a;
          opts.forEach(function(x){x.disabled=true});
          opts[q.a].classList.add('right'); if(!ok) b.classList.add('wrong');
          var hh=box.querySelector('.hint'); if(hh) hh.remove();
          var fb=document.createElement('div'); fb.className='fb';
          fb.innerHTML=(ok?'<b class="ok">정답이에요!</b> ':'<b class="no">아쉬워요. 정답은 '+NUMS[q.a]+'</b> ')+q.e;
          box.appendChild(fb); answered++; if(ok) correct++; upd();
          if(answered===Q.length){
            var d=document.createElement('div'); d.className='done'; var r=correct/Q.length;
            d.innerHTML='<span>'+Q.length+'문항 중 '+correct+'문항 정답 · '+(r===1?'모두 맞혔어요!':r>=0.7?'잘했어요. 틀린 문항의 해설을 한 번 더 읽어 보세요.':'‘한눈에 정리’를 다시 보고 한 번 더 풀어 봐요.')+'</span><button class="btn" type="button">다시 풀기</button>';
            qs.appendChild(d); d.querySelector('button').addEventListener('click',function(){render(); $(secId).scrollIntoView({behavior:'smooth'});});
          }
        });});
      });
    }
    render();
  }
  quiz(D.quiz,'qs','score','quiz');
  if(D.review&&D.review.length) quiz(D.review,'rv','rv-score','review');

  // 5·6. 고쳐 쓰기·조건 영작 (직접 쓰기)
  function typing(L,boxId,kind){
    var box=$(boxId); if(!L||!box) return;
    L.forEach(function(it,i){
      var c=document.createElement('div'); c.className='g-card';
      var h='<p class="g-en"><span class="g-n">'+(i+1)+'</span>'+(kind==='fix'?it.w:'<span style="font-family:var(--sans)">'+it.ko+'</span>')+'</p>';
      if(kind==='fix'&&it.ko) h+='<p class="g-ko">'+it.ko+'</p>';
      if(it.cond) h+='<ul class="g-cond">'+it.cond.map(function(x){return '<li>'+x+'</li>'}).join('')+'</ul>';
      h+='<div class="g-in"><input type="text" autocomplete="off" autocapitalize="off" spellcheck="false" aria-label="'+(i+1)+'번 답 쓰기" placeholder="'+(kind==='fix'?'고친 문장 전체를 써 보세요':'영어 문장을 써 보세요')+'"><button type="button" class="btn primary" data-a="ck">확인</button><button type="button" class="btn" data-a="show">정답 보기</button></div>';
      if(it.n) h+='<span class="g-cnt">단어 수 0 / '+it.n+'</span>';
      h+='<div class="g-out" aria-live="polite"></div>';
      c.innerHTML=h; box.appendChild(c);
      var inp=c.querySelector('input'), out=c.querySelector('.g-out'), cnt=c.querySelector('.g-cnt');
      if(cnt) inp.addEventListener('input',function(){ var n=words(inp.value); cnt.textContent='단어 수 '+n+' / '+it.n; cnt.className='g-cnt'+(n===it.n?' ok':''); });
      inp.addEventListener('keydown',function(e){ if(e.key==='Enter') check(); });
      function show(msg){
        var h='<div class="fb">'+msg+'</div><p class="g-model">'+it.a[0]+'</p>';
        if(it.e) h+='<div class="fb">'+it.e+'</div>';
        out.innerHTML=h;
      }
      function check(){
        var v=inp.value; if(!soft(v)){ inp.focus(); return; }
        var exact=it.a.some(function(a){return soft(a)===soft(v)});
        var near=!exact&&it.a.some(function(a){return loose(a)===loose(v)});
        inp.classList.remove('ok','no');
        if(exact){ inp.classList.add('ok'); show('<b class="ok">정답이에요!</b>'+(kind==='write'?' 감점 없이 완벽해요.':'')); }
        else if(near){ inp.classList.add('ok'); show('<b class="ok">거의 다 맞았어요!</b> 낱말은 모두 맞는데 <b>첫 글자 대문자나 끝 문장부호(. ?)</b>가 달라요. 서술형에서는 이것도 감점이에요.'); }
        else { inp.classList.add('no'); out.innerHTML='<div class="fb"><b class="no">다시 확인해 보세요.</b> '+(it.h||'')+(kind==='write'?' 아래 ‘서술형 감점 체크’로 하나씩 점검해 보세요.':'')+'</div>'; }
      }
      c.querySelector('[data-a="ck"]').addEventListener('click',check);
      c.querySelector('[data-a="show"]').addEventListener('click',function(){ show('<b>정답</b>'+(it.a.length>1?' (이렇게 써도 맞아요: '+it.a.slice(1).join(' / ')+')':'')); });
    });
  }
  typing(D.fix,'fix-list','fix');
  typing(D.write,'write-list','write');
  if(D.check&&$('write-check')) $('write-check').innerHTML=D.check.map(function(x){return '<li>'+x+'</li>'}).join('');

  // 7. 문장 배열 (중등 학습지와 같은 방식, 어구를 눌러 순서대로)
  (function(){
    var O=D.order, box=$('ord'); if(!O||!O.length||!box) return;
    var oi=0, solved={}, cur=null;
    function shuffle(a){a=a.slice();for(var i=a.length-1;i>0;i--){var j=Math.floor(Math.random()*(i+1));var t=a[i];a[i]=a[j];a[j]=t;}return a;}
    function esc(t){return String(t).replace(/&/g,'&amp;').replace(/</g,'&lt;')}
    var END=/[.?!]+[”’"')]*$/;
    function lc(t){ if(/^I\b/.test(t)) return t; return t.charAt(0).toLowerCase()+t.slice(1); }
    function setup(){ var it=O[oi], tk=it.c.slice(), ids=tk.map(function(_,i){return i}), bank=ids;
      if(ids.length>1){ var n=0; do{ bank=shuffle(ids); n++; }while(bank.join()===ids.join()&&n<20); }
      cur={it:it,tk:tk,slots:bank,bank:bank.slice(),tray:[],bad:{},tries:0,done:false,shown:false}; draw(); }
    function tail(){ var m=cur.tk[cur.tk.length-1].match(END); return m?m[0]:''; }
    function label(i){ var t=i===0&&!cur.it.keep?lc(cur.tk[0]):cur.tk[i]; if(i===cur.tk.length-1&&cur.tk.length>1){ var r=t.replace(END,''); if(r) t=r; } return t; }
    function draw(){
      var it=cur.it, total=O.length, nOk=Object.keys(solved).length;
      var dots=O.map(function(o,k){return '<button type="button" data-go="'+k+'" class="'+(k===oi?'cur ':'')+(solved[k]?'done':'')+'" aria-label="'+(k+1)+'번째 문장">'+(k+1)+'</button>'}).join('');
      var h='<div class="wq-top"><span>'+(oi+1)+' / '+total+' · 완성 '+nOk+'문장</span></div><div class="dots">'+dots+'</div>';
      h+='<p class="ord-ko">'+(it.src?'<small>'+it.src+'</small>':'')+it.ko+'</p>';
      h+='<div class="tray'+(cur.done?(cur.shown?' shown':' ok'):'')+'" id="ord-tray">'+(cur.tray.length?cur.tray.map(function(i,p){return '<button type="button" class="tok'+(cur.bad[p]?' bad':'')+'" data-t="'+i+'"'+(cur.done?' disabled':'')+'>'+esc(label(i))+'</button>'}).join(''):'<span class="tray-empty">아래 어구를 순서대로 눌러 보세요.</span>')+(cur.tray.length&&tail()?'<span class="tray-end" aria-hidden="true">'+esc(tail())+'</span>':'')+'</div>';
      h+=cur.done?'':'<div class="bank" id="ord-bank">'+cur.slots.map(function(i){var used=cur.bank.indexOf(i)<0;return '<button type="button" class="tok'+(used?' used':'')+'" data-b="'+i+'"'+(used?' disabled aria-hidden="true" tabindex="-1"':'')+'>'+esc(label(i))+'</button>'}).join('')+'</div>';
      var msg=''; if(cur.done) msg=cur.shown?'<b class="no">정답을 확인했어요.</b> 다음에 다시 도전해 보세요.':'<b class="ok">정답!</b> '+(cur.tries?'고쳐서 완성했어요.':'한 번에 맞혔어요.');
      else if(cur.tries&&Object.keys(cur.bad).length) msg='<b class="no">아쉬워요.</b> 빨간 어구부터 순서가 달라요. 눌러서 빼고 다시 배열해 보세요.';
      h+='<p class="ord-msg" aria-live="polite">'+msg+'</p>';
      if(cur.done) h+='<p class="ord-full">'+it.c.join(' ')+(it.e?'<br><small style="font-family:var(--sans);color:var(--muted)">'+it.e+'</small>':'')+'</p>';
      h+='<div class="ord-acts"><div class="l"><button type="button" class="btn" id="ord-prev"'+(oi===0?' disabled':'')+'>← 이전</button><button type="button" class="btn" id="ord-reset">'+(cur.done?'다시 풀기':'처음부터')+'</button>'+(cur.done?'':'<button type="button" class="btn" id="ord-undo"'+(cur.tray.length?'':' disabled')+'>↩ 한 칸 되돌리기</button><button type="button" class="btn" id="ord-show">정답 보기</button>')+'</div><div class="r">'+(cur.done?'':'<button type="button" class="btn primary" id="ord-check"'+(cur.bank.length?' disabled':'')+'>정답 확인</button>')+(oi<total-1?'<button type="button" class="btn'+(cur.done?' primary':'')+'" id="ord-next">다음 →</button>':'')+'</div></div>';
      if(oi===total-1&&cur.done) h+='<div class="done"><span>'+total+'문장 중 '+Object.keys(solved).length+'문장 완성 · '+(Object.keys(solved).length===total?'모든 문장을 완성했어요!':'못 푼 문장은 위 번호를 눌러 다시 도전해 보세요.')+'</span></div>';
      box.innerHTML=h;
    }
    box.addEventListener('click',function(e){
      var b=e.target.closest('button'); if(!b||b.disabled) return;
      if(b.hasAttribute('data-b')){ var i=+b.getAttribute('data-b'); cur.bank.splice(cur.bank.indexOf(i),1); cur.tray.push(i); cur.bad={}; draw(); return; }
      if(b.hasAttribute('data-t')){ var t=+b.getAttribute('data-t'); cur.tray.splice(cur.tray.indexOf(t),1); cur.bank.push(t); cur.bad={}; draw(); return; }
      if(b.hasAttribute('data-go')){ oi=+b.getAttribute('data-go'); setup(); return; }
      switch(b.id){
        case 'ord-prev': if(oi>0){oi--;setup();} break;
        case 'ord-next': if(oi<O.length-1){oi++;setup();} break;
        case 'ord-reset': setup(); break;
        case 'ord-undo': if(cur.tray.length){ cur.bank.push(cur.tray.pop()); cur.bad={}; draw(); } break;
        case 'ord-show': cur.tray=cur.tk.map(function(_,i){return i}); cur.bank=[]; cur.bad={}; cur.done=true; cur.shown=true; draw(); break;
        case 'ord-check':
          var bad={}, wrong=false;
          cur.tray.forEach(function(i,p){ if(wrong||cur.tk[i]!==cur.tk[p]){ wrong=true; bad[p]=true; } });
          if(wrong) cur.tries++; else { cur.done=true; solved[oi]=true; }
          cur.bad=bad; draw(); break;
      }
    });
    setup();
  })();

  // PDF로 저장은 다른 학습지와 같은 공용 PDF 스크립트(print-sheet)가 그린다(GRAM 분기, seo.py → print_btn.py가 붙임, 2026-11-06)

  // 8. 독해로 이어 보기
  (function(){ var L=D.links, box=$('links'); if(!L||!box) return;
    box.innerHTML=L.map(function(l){return '<a href="'+l.href+'"><b>'+l.t+'</b><small>'+l.d+'</small></a>'}).join(''); })();
})();
