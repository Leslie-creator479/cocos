/* 코코스 단어게임 '단어 전체 듣기' (모든 단어게임·단어장 페이지가 함께 쓰는 파일, print-game.js가 불러온다, 2026-10-23)
   - 1단계 '단어 먼저 익히기' 화면의 단어 목록 위에 '단어 전체 듣기' 막대를 넣는다: 재생/일시정지, 멈춤, 0.8배·1배, 따라 말하기.
   - 단어마다 달린 스피커와 같은 녹음(assets/say/<단어>.mp3)을 화면에 보이는 순서대로 튼다. 녹음이 없으면 기기 음성, 그것도 없으면 건너뛴다.
   - 지금 읽는 단어 칸에 표시를 하고, 화면 밖이면 그 칸으로 스크롤한다. 단어 목록을 벗어나면 아래에 작은 조작 막대가 뜬다.
   - 우리말 뜻은 읽지 않는다(학습지 vocab-listen.js와 같은 규칙).
   - '뜻 가리기'·'틀린 단어만'으로 목록이 다시 그려지거나 게임 화면을 나가면 멈춘다. 단어 스피커를 눌러도 멈춘다.
   이 파일 하나를 고치면 모든 단어게임에 함께 반영된다. */
(function () {
  'use strict';
  if (window.__cocosGameListen) return;
  window.__cocosGameListen = true;
  var D = window.DATA || {};
  var SAY = D.say != null ? D.say : '../../assets/say/';
  var synth = ('speechSynthesis' in window) ? window.speechSynthesis : null;
  function slug(w) { return String(w).toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, ''); }

  var css = document.createElement('style');
  css.textContent =
    '.gl{display:flex;flex-wrap:wrap;align-items:center;gap:8px;margin:2px 0 6px}' +
    '.gl-main{display:inline-flex;align-items:center;gap:6px;border:1px solid var(--accent,#0A7FBF);background:var(--accent,#0A7FBF);color:var(--card,#fff);border-radius:999px;padding:7px 16px 7px 12px;font:inherit;font-size:14px;font-weight:700;cursor:pointer}' +
    '.gl-main.on{background:var(--card,#fff);color:var(--accent,#0A7FBF)}' +
    '.gl svg,.gl-mini svg{width:15px;height:15px}' +
    '.gl-stop{display:inline-flex;align-items:center;justify-content:center;width:34px;height:34px;border-radius:999px;border:1px solid var(--line,#DDE0EA);background:var(--card,#fff);color:var(--ink,#1B2033);padding:0;cursor:pointer}' +
    '.gl-stop[hidden]{display:none}' +
    '.gl-seg{display:inline-flex;border:1px solid var(--line,#DDE0EA);border-radius:999px;overflow:hidden}' +
    '.gl-seg button{border:0;background:var(--card,#fff);color:var(--ink,#1B2033);font:inherit;font-size:13px;padding:6px 12px;cursor:pointer}' +
    '.gl-seg button[aria-pressed="true"]{background:var(--accent,#0A7FBF);color:var(--card,#fff)}' +
    '.gl-sh{border:1px solid var(--line,#DDE0EA);background:var(--card,#fff);color:var(--ink,#1B2033);border-radius:999px;font:inherit;font-size:13px;padding:6px 12px;cursor:pointer}' +
    '.gl-sh[aria-pressed="true"]{background:var(--accent,#0A7FBF);border-color:var(--accent,#0A7FBF);color:var(--card,#fff)}' +
    '.gl-hint{margin:0 0 4px;font-size:13px;color:var(--muted,#5B6278)}' +
    '.vocab .vrow.gl-now{background:var(--accent-soft,#E2F3FC);box-shadow:inset 3px 0 0 var(--accent,#0A7FBF);border-radius:8px;padding-left:10px}' +
    '.vocab .vrow.gl-wait{box-shadow:inset 3px 0 0 var(--accent,#0A7FBF),0 0 0 2px var(--sun,#FEE101)}' +
    '.gl-mini{position:fixed;left:50%;bottom:calc(14px + env(safe-area-inset-bottom,0px));transform:translateX(-50%);z-index:41;display:flex;align-items:center;gap:8px;padding:6px 6px 6px 14px;border-radius:999px;background:var(--ink,#1B2033);color:var(--paper,#F5F6FA);box-shadow:0 6px 20px rgba(0,0,0,.25);font-size:13px;font-weight:700;white-space:nowrap}' +
    '.gl-mini[hidden]{display:none}' +
    '.gl-mini button{display:inline-flex;align-items:center;justify-content:center;width:32px;height:32px;border-radius:999px;border:0;background:rgba(255,255,255,.14);color:inherit;padding:0;cursor:pointer}' +
    '.gl-mini .go{background:none;width:auto;padding:0 6px;font:inherit;font-size:13px;font-weight:700;text-decoration:underline;text-underline-offset:3px}' +
    '@media print{.gl,.gl-hint,.gl-mini{display:none!important}}';
  document.head.appendChild(css);

  var I_PLAY = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M7 4.5v15l13-7.5z"/></svg>';
  var I_PAUSE = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><rect x="6" y="4.5" width="4" height="15" rx="1"/><rect x="14" y="4.5" width="4" height="15" rx="1"/></svg>';
  var I_STOP = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><rect x="5.5" y="5.5" width="13" height="13" rx="2"/></svg>';

  var list = null, bar = null, allBtn = null, stopBtn = null, shBtn = null, listObs = null, visObs = null;
  var mini = document.createElement('div');
  mini.className = 'gl-mini'; mini.hidden = true;
  mini.innerHTML = '<button type="button" class="go" aria-label="단어 목록으로 가기"></button><button type="button" class="pp"></button><button type="button" class="st" aria-label="단어 듣기 멈추기">' + I_STOP + '</button>';
  var mGo = mini.querySelector('.go'), mPP = mini.querySelector('.pp');
  var au = new Audio(); au.preload = 'auto';
  var on = false, paused = false, idx = -1, rate = 1, shadow = false, timer = null, pend = false, seen = true, speaking = false, rows = [];

  function setRate() { try { au.defaultPlaybackRate = rate; au.playbackRate = rate; if ('preservesPitch' in au) au.preservesPitch = true; } catch (e) {} }
  ['loadedmetadata', 'play', 'playing'].forEach(function (ev) { au.addEventListener(ev, setRate); });
  function ui() {
    if (allBtn) {
      allBtn.innerHTML = (on && !paused ? I_PAUSE : I_PLAY) + '<span>' + (on ? (paused ? '이어 듣기' : '일시정지') : '단어 전체 듣기') + '</span>';
      allBtn.classList.toggle('on', on);
      stopBtn.hidden = !on;
    }
    mGo.textContent = '단어 듣기 ' + (idx + 1) + ' / ' + rows.length;
    mPP.innerHTML = paused ? I_PLAY : I_PAUSE; mPP.setAttribute('aria-label', paused ? '이어 듣기' : '일시정지');
    mini.hidden = !(on && !seen && list && list.isConnected);
  }
  function marks() { if (list) [].forEach.call(list.querySelectorAll('.vrow.gl-now,.vrow.gl-wait'), function (r) { r.classList.remove('gl-now', 'gl-wait'); }); }
  function stop() {
    if (timer) { clearTimeout(timer); timer = null; }
    pend = false; on = false; paused = false; idx = -1;
    try { au.pause(); } catch (e) {}
    if (speaking && synth) { try { synth.cancel(); } catch (e) {} speaking = false; }
    marks(); ui();
  }
  function inView(el) { var r = el.getBoundingClientRect(); return r.top >= 60 && r.bottom <= window.innerHeight - 80; }
  function next() { timer = null; if (!on) return; if (paused) { pend = true; return; } go(idx + 1); }
  function done(dur) {
    if (!on) return;
    var row = rows[idx];
    var wait = shadow ? Math.round((dur > 0 ? dur : 1) / rate * 1000 + 1000) : 550;
    if (shadow && row) row.classList.add('gl-wait');
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
  function word(row) { var t = row.querySelector('.wt'); return t ? t.textContent.trim() : ''; }
  function go(i) {
    marks();
    if (!list || !list.isConnected || i >= rows.length) { stop(); return; }
    idx = i; pend = false;
    var row = rows[i], w = word(row);
    row.classList.add('gl-now');
    if (!inView(row)) { try { row.scrollIntoView({ behavior: 'smooth', block: 'center' }); } catch (e) { row.scrollIntoView(); } }
    ui();
    if (!w) { done(0); return; }
    if (!SAY) { speakWord(w); return; }
    try {
      au.src = SAY + slug(w) + '.mp3'; setRate();
      var p = au.play(); setRate();
      if (p && p.catch) p.catch(function (err) { if (err && err.name === 'AbortError') return; speakWord(w); });
    } catch (e) { speakWord(w); }
  }
  au.addEventListener('ended', function () { done(au.duration && isFinite(au.duration) ? au.duration : 1); });
  au.addEventListener('error', function () { if (on && idx >= 0 && au.src && rows[idx]) { var w = word(rows[idx]); au.removeAttribute('src'); speakWord(w); } });
  function pause() {
    paused = true;
    if (timer) { clearTimeout(timer); timer = null; pend = true; marks(); if (rows[idx]) rows[idx].classList.add('gl-now'); }
    else { try { au.pause(); } catch (e) {} if (speaking && synth) { try { synth.cancel(); } catch (e) {} speaking = false; pend = true; } }
    ui();
  }
  function resume() {
    paused = false;
    if (pend) { pend = false; go(idx + 1); return; }
    var p = au.play(); if (p && p.catch) p.catch(function () { go(idx + 1); });
    ui();
  }
  function start() {
    rows = list ? [].slice.call(list.querySelectorAll('.vrow')) : [];
    if (!rows.length) return;
    on = true; paused = false; go(0);
  }
  mini.querySelector('.st').addEventListener('click', stop);
  mPP.addEventListener('click', function () { if (paused) resume(); else pause(); });
  mGo.addEventListener('click', function () { var r = rows[idx] || bar; if (!r) return; try { r.scrollIntoView({ behavior: 'smooth', block: 'center' }); } catch (e) { r.scrollIntoView(); } });
  /* 단어 스피커(button.say)를 누르면 이어 듣기는 멈춘다 */
  document.addEventListener('click', function (e) { if (on && e.target.closest && e.target.closest('.vocab button.say')) stop(); }, true);

  function attach(l) {
    if (on) stop();
    list = l;
    bar = document.createElement('div');
    bar.className = 'gl';
    bar.innerHTML = '<button type="button" class="gl-main"></button>' +
      '<button type="button" class="gl-stop" aria-label="단어 듣기 멈추기" hidden>' + I_STOP + '</button>' +
      '<span class="gl-seg" role="group" aria-label="단어 듣기 속도"><button type="button" data-r="0.8" aria-pressed="' + (rate === 0.8) + '">0.8배</button><button type="button" data-r="1" aria-pressed="' + (rate === 1) + '">1배</button></span>' +
      '<button type="button" class="gl-sh" aria-pressed="' + shadow + '">따라 말하기</button>';
    var hint = document.createElement('p');
    hint.className = 'gl-hint';
    hint.textContent = '단어를 처음부터 차례로 읽어 줘요. ‘따라 말하기’를 켜면 단어마다 잠깐 멈추니 소리 내어 따라 해 보세요. ‘뜻 가리기’를 켜고 들으면 뜻을 떠올리는 연습이 돼요.';
    l.parentNode.insertBefore(bar, l);
    l.parentNode.insertBefore(hint, l);
    allBtn = bar.querySelector('.gl-main'); stopBtn = bar.querySelector('.gl-stop'); shBtn = bar.querySelector('.gl-sh');
    allBtn.addEventListener('click', function () { if (!on) start(); else if (paused) resume(); else pause(); });
    stopBtn.addEventListener('click', stop);
    [].forEach.call(bar.querySelectorAll('[data-r]'), function (b) {
      b.addEventListener('click', function () {
        rate = +b.getAttribute('data-r');
        [].forEach.call(bar.querySelectorAll('[data-r]'), function (x) { x.setAttribute('aria-pressed', String(x === b)); });
        setRate();
      });
    });
    shBtn.addEventListener('click', function () {
      shadow = !shadow; shBtn.setAttribute('aria-pressed', String(shadow));
      if (!shadow && timer && on && !paused) { clearTimeout(timer); timer = null; marks(); if (rows[idx]) rows[idx].classList.add('gl-now'); timer = setTimeout(next, 300); }
    });
    /* '뜻 가리기'·'틀린 단어만' 등으로 목록이 다시 그려지면 멈춘다 */
    if (listObs) listObs.disconnect();
    listObs = new MutationObserver(function () { if (on) stop(); });
    listObs.observe(l, { childList: true });
    if (visObs) visObs.disconnect();
    if ('IntersectionObserver' in window) {
      visObs = new IntersectionObserver(function (es) { seen = es[0].isIntersecting; ui(); });
      visObs.observe(l);
    } else { seen = false; }
    ui();
  }

  function scan() {
    var st = document.getElementById('stage');
    if (on && st && st.hidden) { stop(); return; }      // 게임 화면을 닫으면 멈춘다
    var l = document.querySelector('#stage .vocab');
    if (l && l !== list) attach(l);
    else if (on && list && !list.isConnected) stop();   // 게임 화면을 나가면 멈춘다
    else if (list && !list.isConnected) ui();
  }
  function init() {
    document.body.appendChild(mini);
    var stage = document.getElementById('stage');
    if (!stage) return;
    new MutationObserver(scan).observe(stage, { childList: true, subtree: true, attributes: true, attributeFilter: ['hidden'] });
    scan();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
