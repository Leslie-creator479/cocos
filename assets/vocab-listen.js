/* 코코스 온라인 학습지 '단어 전체 듣기' (모든 학습지가 함께 쓰는 파일, print-sheet.js가 불러온다)
   - 단어 정리 위에 '단어 전체 듣기' 막대를 넣는다: 재생/일시정지, 멈춤, 0.8배·1배, 따라 말하기.
   - 학습지에 이미 들어 있는 단어 발음 녹음(AUDIO)을 차례로 튼다. 녹음이 없는 단어는 기기 음성으로 읽고, 그것도 없으면 건너뛴다.
   - 지금 읽는 단어 칸에 표시를 하고, 화면 밖이면 그 칸으로 스크롤한다. 단어 정리를 벗어나면 아래에 작은 조작 막대가 뜬다.
   - 우리말 뜻은 읽지 않는다(선생님 결정 2026-10-22: 영어 발음 듣기용).
   이 파일 하나를 고치면 모든 학습지에 함께 반영된다. */
(function () {
  'use strict';
  if (window.__cocosVocabListen) return;
  function start() {
    var D = window.DATA, A = window.AUDIO || {};
    var box = document.getElementById('vocab'), sec = document.getElementById('words');
    if (!D || !D.vocab || !D.vocab.length || !box || !sec || document.getElementById('vl-bar')) return;
    var rows = [].slice.call(box.querySelectorAll('.vrow'));
    if (!rows.length) return;
    window.__cocosVocabListen = true;
    var V = D.vocab.slice(0, rows.length);
    var synth = ('speechSynthesis' in window) ? window.speechSynthesis : null;

    var css = document.createElement('style');
    css.textContent =
      '.vl{display:flex;flex-wrap:wrap;align-items:center;gap:8px;margin:0 0 6px}' +
      '.vl-main{display:inline-flex;align-items:center;gap:6px;border:1px solid var(--accent,#0A7FBF);background:var(--accent,#0A7FBF);color:var(--card,#fff);border-radius:999px;padding:7px 16px 7px 12px;font:inherit;font-size:14px;font-weight:700;cursor:pointer}' +
      '.vl-main.on{background:var(--card,#fff);color:var(--accent,#0A7FBF)}' +
      '.vl svg,.vl-mini svg{width:15px;height:15px}' +
      '.vl-stop{display:inline-flex;align-items:center;justify-content:center;width:34px;height:34px;border-radius:999px;border:1px solid var(--line,#DDE0EA);background:var(--card,#fff);color:var(--ink,#1B2033);padding:0;cursor:pointer}' +
      '.vl-stop[hidden]{display:none}' +
      '.vl-seg{display:inline-flex;border:1px solid var(--line,#DDE0EA);border-radius:999px;overflow:hidden}' +
      '.vl-seg button{border:0;background:var(--card,#fff);color:var(--ink,#1B2033);font:inherit;font-size:13px;padding:6px 12px;cursor:pointer}' +
      '.vl-seg button[aria-pressed="true"]{background:var(--accent,#0A7FBF);color:var(--card,#fff)}' +
      '.vl-sh{border:1px solid var(--line,#DDE0EA);background:var(--card,#fff);color:var(--ink,#1B2033);border-radius:999px;font:inherit;font-size:13px;padding:6px 12px;cursor:pointer}' +
      '.vl-sh[aria-pressed="true"]{background:var(--accent,#0A7FBF);border-color:var(--accent,#0A7FBF);color:var(--card,#fff)}' +
      '.vl-hint{margin:0 0 12px;font-size:13px;color:var(--muted,#5B6278)}' +
      '.vrow.vl-now{border-color:var(--accent,#0A7FBF);background:var(--accent-soft,#E2F3FC);box-shadow:inset 3px 0 0 var(--accent,#0A7FBF)}' +
      '.vrow.vl-wait{box-shadow:inset 3px 0 0 var(--accent,#0A7FBF),0 0 0 2px var(--mark,#FFE766)}' +
      '.vl-mini{position:fixed;left:50%;bottom:calc(14px + env(safe-area-inset-bottom,0px));transform:translateX(-50%);z-index:41;display:flex;align-items:center;gap:8px;padding:6px 6px 6px 14px;border-radius:999px;background:var(--ink,#1B2033);color:var(--paper,#F5F6FA);box-shadow:0 6px 20px rgba(0,0,0,.25);font-size:13px;font-weight:700;white-space:nowrap}' +
      '.vl-mini[hidden]{display:none}' +
      '.vl-mini button{display:inline-flex;align-items:center;justify-content:center;width:32px;height:32px;border-radius:999px;border:0;background:rgba(255,255,255,.14);color:inherit;padding:0;cursor:pointer}' +
      '.vl-mini .go{background:none;width:auto;padding:0 6px;font:inherit;font-size:13px;font-weight:700;text-decoration:underline;text-underline-offset:3px}' +
      '@media print{.vl,.vl-hint,.vl-mini{display:none!important}}';
    document.head.appendChild(css);

    var I_PLAY = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M7 4.5v15l13-7.5z"/></svg>';
    var I_PAUSE = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><rect x="6" y="4.5" width="4" height="15" rx="1"/><rect x="14" y="4.5" width="4" height="15" rx="1"/></svg>';
    var I_STOP = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><rect x="5.5" y="5.5" width="13" height="13" rx="2"/></svg>';

    var bar = document.createElement('div');
    bar.className = 'vl'; bar.id = 'vl-bar';
    bar.innerHTML = '<button type="button" class="vl-main" id="vl-all"></button>' +
      '<button type="button" class="vl-stop" id="vl-stop" aria-label="단어 듣기 멈추기" hidden>' + I_STOP + '</button>' +
      '<span class="vl-seg" role="group" aria-label="단어 듣기 속도"><button type="button" data-r="0.8" aria-pressed="false">0.8배</button><button type="button" data-r="1" aria-pressed="true">1배</button></span>' +
      '<button type="button" class="vl-sh" id="vl-sh" aria-pressed="false">따라 말하기</button>';
    var hint = document.createElement('p');
    hint.className = 'vl-hint';
    hint.textContent = '단어를 처음부터 차례로 읽어 줘요. ‘따라 말하기’를 켜면 단어마다 잠깐 멈추니 소리 내어 따라 해 보세요. ‘뜻 가리기’를 켜고 들으면 뜻을 떠올리는 연습이 돼요.';
    sec.insertBefore(hint, box);
    sec.insertBefore(bar, hint);

    var mini = document.createElement('div');
    mini.className = 'vl-mini'; mini.hidden = true;
    mini.innerHTML = '<button type="button" class="go" aria-label="단어 정리로 가기"></button><button type="button" class="pp"></button><button type="button" class="st" aria-label="단어 듣기 멈추기">' + I_STOP + '</button>';
    document.body.appendChild(mini);

    var allBtn = document.getElementById('vl-all'), stopBtn = document.getElementById('vl-stop'), shBtn = document.getElementById('vl-sh');
    var mGo = mini.querySelector('.go'), mPP = mini.querySelector('.pp');
    var au = new Audio(); au.preload = 'auto';
    var on = false, paused = false, idx = -1, rate = 1, shadow = false, timer = null, pend = false, seen = true, speaking = false;

    function setRate() { try { au.defaultPlaybackRate = rate; au.playbackRate = rate; if ('preservesPitch' in au) au.preservesPitch = true; } catch (e) {} }
    ['loadedmetadata', 'play', 'playing'].forEach(function (ev) { au.addEventListener(ev, setRate); });
    function ui() {
      allBtn.innerHTML = (on && !paused ? I_PAUSE : I_PLAY) + '<span>' + (on ? (paused ? '이어 듣기' : '일시정지') : '단어 전체 듣기') + '</span>';
      allBtn.classList.toggle('on', on);
      stopBtn.hidden = !on;
      mGo.textContent = '단어 듣기 ' + (idx + 1) + ' / ' + V.length;
      mPP.innerHTML = paused ? I_PLAY : I_PAUSE; mPP.setAttribute('aria-label', paused ? '이어 듣기' : '일시정지');
      mini.hidden = !(on && !seen);
    }
    function marks() { rows.forEach(function (r) { r.classList.remove('vl-now', 'vl-wait'); }); }
    function stop() {
      if (timer) { clearTimeout(timer); timer = null; }
      pend = false; on = false; paused = false; idx = -1;
      try { au.pause(); } catch (e) {}
      if (speaking && synth) { try { synth.cancel(); } catch (e) {} speaking = false; }
      marks(); ui();
    }
    function inView(el) { var r = el.getBoundingClientRect(); return r.top >= 60 && r.bottom <= window.innerHeight - 80; }
    function next() {
      timer = null;
      if (!on) return;
      if (paused) { pend = true; return; }
      go(idx + 1);
    }
    function done(dur) {
      if (!on) return;
      var row = rows[idx];
      var wait = shadow ? Math.round((dur > 0 ? dur : 1) / rate * 1000 + 1000) : 550;
      if (shadow && row) row.classList.add('vl-wait');
      timer = setTimeout(next, wait);
    }
    function speakWord(w) {
      if (!synth || typeof SpeechSynthesisUtterance === 'undefined') { done(0); return; }
      try {
        synth.cancel(); speaking = true;
        var u = new SpeechSynthesisUtterance(String(w).replace(/[~()]/g, ' '));
        u.lang = 'en-US'; u.rate = 0.85 * rate;
        var t0 = Date.now();
        u.onend = u.onerror = function () { speaking = false; done((Date.now() - t0) / 1000); };
        synth.speak(u);
      } catch (e) { speaking = false; done(0); }
    }
    function go(i) {
      marks();
      if (i >= V.length) { stop(); return; }
      idx = i; pend = false;
      var row = rows[i];
      row.classList.add('vl-now');
      if (!inView(row)) { try { row.scrollIntoView({ behavior: 'smooth', block: 'center' }); } catch (e) { row.scrollIntoView(); } }
      ui();
      var w = V[i].w, src = A[w];
      if (!src) { speakWord(w); return; }
      try {
        au.src = src; setRate();
        var p = au.play(); setRate();
        if (p && p.catch) p.catch(function (err) { if (err && err.name === 'AbortError') return; speakWord(w); });
      } catch (e) { speakWord(w); }
    }
    au.addEventListener('ended', function () { done(au.duration && isFinite(au.duration) ? au.duration : 1); });
    au.addEventListener('error', function () { if (on && idx >= 0 && au.src) { var w = V[idx].w; au.removeAttribute('src'); speakWord(w); } });
    function pause() {
      paused = true;
      if (timer) { clearTimeout(timer); timer = null; pend = true; marks(); if (rows[idx]) rows[idx].classList.add('vl-now'); }
      else { try { au.pause(); } catch (e) {} if (speaking && synth) { try { synth.cancel(); } catch (e) {} speaking = false; pend = true; } }
      ui();
    }
    function resume() {
      paused = false;
      if (pend) { pend = false; go(idx + 1); return; }
      var p = au.play(); if (p && p.catch) p.catch(function () { go(idx + 1); });
      ui();
    }
    allBtn.addEventListener('click', function () {
      if (!on) { stopOthers(); on = true; paused = false; go(0); }
      else if (paused) resume(); else pause();
    });
    stopBtn.addEventListener('click', stop);
    mini.querySelector('.st').addEventListener('click', stop);
    mPP.addEventListener('click', function () { if (paused) resume(); else pause(); });
    mGo.addEventListener('click', function () { var r = rows[idx] || bar; try { r.scrollIntoView({ behavior: 'smooth', block: 'center' }); } catch (e) { r.scrollIntoView(); } });
    [].forEach.call(bar.querySelectorAll('[data-r]'), function (b) {
      b.addEventListener('click', function () {
        rate = +b.getAttribute('data-r');
        [].forEach.call(bar.querySelectorAll('[data-r]'), function (x) { x.setAttribute('aria-pressed', String(x === b)); });
        setRate();
      });
    });
    shBtn.addEventListener('click', function () {
      shadow = !shadow; shBtn.setAttribute('aria-pressed', String(shadow));
      if (!shadow && timer && on && !paused) { clearTimeout(timer); timer = null; marks(); if (rows[idx]) rows[idx].classList.add('vl-now'); timer = setTimeout(next, 300); }
    });
    /* 다른 소리(단어 스피커·지문 듣기)를 누르면 단어 이어 듣기는 멈춘다. 단어 이어 듣기를 시작할 때는 지문 듣기를 멈춘다. */
    function stopOthers() {
      var s = document.getElementById('l-stop'); if (s && !s.hidden) s.click();
    }
    document.addEventListener('click', function (e) {
      if (!on) return;
      if (e.target.closest('button.say, a.say, .sbtn, #l-all, .lbar .pp')) stop();
    }, true);
    if ('IntersectionObserver' in window) {
      new IntersectionObserver(function (es) { seen = es[0].isIntersecting; ui(); }).observe(sec);
    } else { seen = false; }
    ui();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start);
  else start();
})();
