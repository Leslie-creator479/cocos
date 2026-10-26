/* 코코스 온라인 학습지 'PDF로 저장' (모든 학습지가 함께 쓰는 파일)
   - 학습지 머리에 'PDF로 저장' 버튼을 넣는다.
   - 누르면 학습지 데이터(DATA)로 인쇄용 화면을 만들고 인쇄 창을 연다(학생 기기에서 PDF로 저장).
   - 홈페이지에는 아무 파일도 저장하지 않는다. Ctrl+P·공유 → 프린트로 열어도 같은 화면이 나온다.
   이 파일 하나를 고치면 모든 학습지의 PDF 모양이 함께 바뀐다. */
/* 밑줄이 g·p·q·y 같은 글자 아래에서 끊기지 않게(2026-10-25 원장님 요청): 화면·PDF 모두 */
(function () {
  try {
    if (document.getElementById('cocos-ul-fix')) return;
    var s = document.createElement('style'); s.id = 'cocos-ul-fix';
    s.textContent = 'u,ins,.u,[style*="underline"]{text-decoration-skip-ink:none;-webkit-text-decoration-skip:none;text-decoration-skip:none}';
    (document.head || document.documentElement).appendChild(s);
  } catch (e) {}
})();

/* 단어 퀴즈 칸에 '동의어·반의어 / 단어게임' 바로 가기(2026-10-26 원장님 요청).
   학습지 주소로 짝 페이지 주소를 만들고, 실제로 있는 페이지만 보여 준다(없으면 아무것도 안 나옴). */
(function () {
  try {
    var me = document.currentScript;
    if (!me || !me.src || window.__cocosStudyLinks) return;
    window.__cocosStudyLinks = true;
    var root = new URL('..', me.src);
    var rel = decodeURIComponent(location.pathname).replace(root.pathname, '').replace(/^\/+|\/+$/g, '').split('/');
    var syn = null, game = null, anc = '';
    if (rel[0] === 'study' && rel.length === 3) { syn = 'syn/' + rel[1] + '/'; game = 'game/' + rel[1] + '/'; anc = 'p' + rel[2]; }
    else if (rel[0] === 'textbook' && rel.length === 4 && !/^d\d/.test(rel[3])) { /* 대화문(d1·d2)은 동의어·단어게임 짝이 없음 */ var b = rel[1] + '-' + rel[2]; syn = 'syn/' + b + '/'; game = 'game/' + b + '/'; anc = 'p' + rel[2] + '-' + rel[3]; }
    if (!syn) return;
    var go = function () {
      var sec = document.getElementById('wordquiz');
      if (!sec || document.getElementById('more-study')) return;
      var box = document.createElement('div');
      box.id = 'more-study';
      box.style.cssText = 'display:none;flex-wrap:wrap;align-items:center;gap:8px;margin:0 0 14px;padding:10px 14px;border-radius:10px;background:var(--paper,#F6F4EE);font-size:14px;line-height:1.5';
      box.innerHTML = '<span style="font-weight:600">이 지문 단어를 더 공부하려면</span>';
      var head = sec.querySelector('.sec-head');
      (head && head.nextSibling) ? sec.insertBefore(box, head.nextSibling) : sec.appendChild(box);
      [[syn, '동의어·반의어 →', '#' + anc], [game, '단어게임 →', '']].forEach(function (x) {
        var url = new URL(x[0], root).href;
        var a = document.createElement('a');
        a.href = url + x[2]; a.textContent = x[1]; a.hidden = true;
        a.style.cssText = 'padding:4px 12px;border-radius:999px;border:1px solid var(--accent,#2F5DA8);color:var(--accent,#2F5DA8);text-decoration:none;font-weight:600;background:var(--card,#fff)';
        box.appendChild(a);
        fetch(url, { method: 'HEAD' }).then(function (r) { if (r.ok) { a.hidden = false; box.style.display = 'flex'; } }).catch(function () {});
      });
    };
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', go); else go();
  } catch (e) {}
})();
/* 단어 정리 '단어 전체 듣기'(assets/vocab-listen.js)를 함께 불러온다(2026-10-22). */
(function () {
  try {
    var me = document.currentScript;
    if (!me || !me.src || window.__cocosVocabListenLoad) return;
    window.__cocosVocabListenLoad = true;
    var s = document.createElement('script');
    s.src = me.src.replace(/print-sheet\.js([?#].*)?$/, 'vocab-listen.js');
    (document.body || document.head).appendChild(s);
    /* 도전 문제(assets/challenge.js, 2026-10-25): DATA.challenge가 있는 학습지에만 칸을 만든다 */
    if (window.DATA && window.DATA.challenge && window.DATA.challenge.length) {
      var c = document.createElement('script');
      c.src = me.src.replace(/print-sheet\.js([?#].*)?$/, 'challenge.js');
      (document.body || document.head).appendChild(c);
    }
  } catch (e) {}
})();
(function () {
  'use strict';
  var D = window.DATA;
  if (!D || !D.sentences || window.__cocosPrint) return;
  window.__cocosPrint = true;

  var NUM = ['①', '②', '③', '④', '⑤', '⑥', '⑦', '⑧'];


  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c];
    });
  }
  function refs(a) {
    if (!a || !a.length) return '';
    a = a.slice().sort(function (x, y) { return x - y; });
    var run = true;
    for (var i = 1; i < a.length; i++) if (a[i] !== a[i - 1] + 1) run = false;
    return (a.length > 1 && run ? a[0] + '~' + a[a.length - 1] : a.join('·')) + '번';
  }
  /* 지문·해설 속 ①~⑳: 글자 크기에 맞게 줄이고 뒤에 한 칸(줄바꿈 없는 칸) */
  function nums(t) {
    return String(t == null ? '' : t)
      .replace(/<u>[\s\u2003\u00a0]*(\([A-E]\)|[\u24d0-\u24e9])[\s\u2003\u00a0]*<\/u>/g, '<span class="cp-blank">$1</span>')
      .replace(/_{3,}/g, function (m) { return '<span class="cp-uline" style="width:' + Math.max(5, Math.round(m.length * 0.55)) + 'em"></span>'; }).replace(/([\u2460-\u2473])[ \u00a0]?/g, '<span class="cp-num">$1</span>&nbsp;').replace(/([\u2474-\u24ff\u3260-\u327f])[ \u00a0]?/g, function (m, c, off, s) { var nx = s.charAt(off + m.length); if (s.substr(off + m.length, 7) === '</span>') return m; return '<span class="cp-num">' + c + '</span>' + (/[A-Za-z\u201c"'(<]/.test(nx) ? '&nbsp;' : (m.length > 1 ? ' ' : '')); });
  }
  function ans(q) {
    if (typeof q.a === 'number') return NUM[q.a] || String(q.a + 1);
    return esc(q.a);
  }
  /* 문장 배열: 원래 순서와 다르게, 매번 같은 순서로 섞는다 */
  function shuffle(arr, seed) {
    var a = arr.map(function (x, i) { return i; });
    var s = seed * 9301 + 49297;
    function rnd() { s = (s * 9301 + 49297) % 233280; return s / 233280; }
    for (var t = 0; t < 8; t++) {
      for (var i = a.length - 1; i > 0; i--) {
        var j = Math.floor(rnd() * (i + 1)); var k = a[i]; a[i] = a[j]; a[j] = k;
      }
      var same = a.every(function (x, i) { return x === i; });
      if (!same || a.length < 2) break;
    }
    return a;
  }

  var CSS = [
    '#cocos-pdf-row{display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin-top:14px}',
    '#cocos-pdf-btn{display:inline-flex;align-items:center;gap:7px;font:inherit;font-size:15px;font-weight:700;padding:9px 16px;border-radius:999px;border:1.5px solid var(--accent,#0A7FBF);background:var(--card,#fff);color:var(--accent-ink,#065A88);cursor:pointer}',
    '#cocos-pdf-btn:hover{background:var(--accent-soft,#E2F3FC)}',
    '#cocos-pdf-btn svg{width:18px;height:18px}',
    '#cocos-pdf-row small{font-size:13px;color:var(--muted,#5B6278)}',
    '#cocos-pdf-tip{flex-basis:100%;font-size:13.5px;color:var(--ink,#1B2033);background:var(--accent-soft,#E2F3FC);border-radius:10px;padding:10px 14px;margin:0}#cocos-pdf-tip .cocos-ext{display:inline-block;margin-top:8px;padding:7px 14px;border-radius:999px;background:var(--accent,#0A7FBF);color:#fff;font-weight:700;text-decoration:none}',
    '@media screen{#cocos-print{display:none}}',
    /* 요약문 빈칸 (A)(B): 화면에서도 ___(A)___처럼 넓게 (선생님 요청 2026-10-15) */
    'u.cocos-blank{display:inline-block;min-width:6.2em;text-align:center;text-decoration:none;border-bottom:1.5px solid currentColor;line-height:1.25;margin:0 .15em;padding:0 .2em}',
    /* 빈칸 ______: 밑줄 문자 대신 이어진 선으로 (선생님 요청 2026-10-15) */
    '.cocos-line{display:inline-block;border-bottom:1.5px solid currentColor;height:1em;vertical-align:-.12em;margin:0 .1em}',
    'u.cocos-neg,#cocos-print u.cocos-neg{text-decoration:underline;text-decoration-thickness:1.5px;text-underline-offset:3px}',
    '#cocos-print .cp-uline{display:inline-block;border-bottom:1.2px solid #1B2033;height:1em;vertical-align:-.12em;margin:0 .1em}',
    '#cocos-print .cp-blank{display:inline-block;min-width:6.2em;text-align:center;border-bottom:1.2px solid #1B2033;line-height:1.25;margin:0 .15em}',
    '@media print{',
    /* 좌우 여백은 내용 안쪽 여백으로 준다: 인쇄 창에서 '여백 없음'을 골라도 좌우가 꽉 차지 않게 (2026-10-15) */
    '  @page{size:A4;margin:12mm 0 13mm}',
    '  html,body{width:auto!important;min-width:0!important;max-width:none!important;overflow:visible!important}',
    '  #cocos-print{padding:0 14mm!important;box-sizing:border-box;width:auto!important;max-width:100%!important}',
    '  html,body{background:#fff!important;color:#1B2033!important;margin:0!important;padding:0!important}',
    '  body>*:not(#cocos-print){display:none!important}',
    '  #cocos-print{display:block!important}',
    '}',
    '#cocos-print{--p-ink:#1B2033;--p-muted:#5B6278;--p-line:#D5D9E3;--p-acc:#0A7FBF;--p-acc-ink:#065A88;--p-soft:#E9F5FC;--p-ex:#A84A24;',
    '  color:var(--p-ink);font-family:"Noto Sans KR","Apple SD Gothic Neo","Malgun Gothic",sans-serif;font-size:10.5pt;line-height:1.65;word-break:keep-all;overflow-wrap:break-word;',
    '  -webkit-print-color-adjust:exact;print-color-adjust:exact}',
    '#cocos-print *{box-sizing:border-box}',
    '#cocos-print h1,#cocos-print h2{color:var(--p-ink);font-family:"Noto Sans KR","Apple SD Gothic Neo",sans-serif;letter-spacing:0;text-transform:none}',
    '#cocos-print ol,#cocos-print ul{margin:0}',
    '#cocos-print b{font-weight:700}',
    '#cocos-print p{margin:0}',
    '#cocos-print .cp-en{font-family:"Source Serif 4",Georgia,"Times New Roman",serif}',
    '#cocos-print .cp-top{display:flex;justify-content:space-between;align-items:center;border-bottom:2.5px solid var(--p-acc);padding-bottom:6px;margin-bottom:12px}',
    '#cocos-print .cp-top .logo{width:118px;height:27px}',
    '#cocos-print .cp-top img{height:27px;width:auto}',
    '#cocos-print .cp-top span{font-size:9pt;color:var(--p-muted)}',
    '#cocos-print .cp-chips{font-size:9pt;color:var(--p-acc-ink);font-weight:700;margin-bottom:2px}',
    '#cocos-print h1{font-size:17pt;line-height:1.35;margin:0 0 2px}',
    '#cocos-print .cp-entitle{font-family:"Source Serif 4",Georgia,serif;font-style:italic;color:var(--p-muted);font-size:11pt;margin-bottom:8px}',
    '#cocos-print .cp-gist{border:1px solid var(--p-line);border-left:4px solid var(--p-acc);border-radius:6px;padding:7px 11px;font-size:10pt;margin-bottom:6px}',
    '#cocos-print .cp-gist b{color:var(--p-acc-ink);margin-right:6px}',
    '#cocos-print h2{display:flex;align-items:center;gap:8px;font-size:12.5pt;margin:18px 0 8px;padding-bottom:4px;border-bottom:1px solid var(--p-line);break-after:avoid;page-break-after:avoid}',
    '#cocos-print h2 i{font-style:normal;display:inline-flex;align-items:center;justify-content:center;width:21px;height:21px;border-radius:50%;background:var(--p-acc);color:#fff;font-size:10pt}',
    '#cocos-print h2 small{font-weight:400;font-size:9pt;color:var(--p-muted);margin-left:auto}',
    '#cocos-print .cp-newpage{break-before:page;page-break-before:always}',
    '#cocos-print .cp-lab{display:inline-block;font-size:8.5pt;font-weight:700;color:var(--p-acc-ink);background:var(--p-soft);border-radius:4px;padding:1px 7px;margin:6px 0 3px}',
    '#cocos-print .cp-one{background:var(--p-soft);border-radius:6px;padding:7px 11px}',
    '#cocos-print ol.cp-flow{margin:2px 0;padding-left:0;list-style:none}',
    '#cocos-print ol.cp-flow li{display:grid;grid-template-columns:auto 1fr;gap:2px 8px;padding:3px 0;border-bottom:1px dashed var(--p-line);break-inside:avoid}',
    '#cocos-print ol.cp-flow b{color:var(--p-acc-ink)}',
    '#cocos-print ol.cp-flow em{font-style:normal;font-size:8.5pt;color:var(--p-ex);font-weight:700;margin-right:4px}',
    '#cocos-print .cp-keys>span{display:inline-block;border:1px solid var(--p-line);border-radius:999px;padding:1px 9px;margin:2px 4px 2px 0;font-size:9.5pt}',
    '#cocos-print ul.cp-tips{margin:2px 0;padding-left:16px}',
    '#cocos-print ul.cp-tips li{margin:2px 0}',
    '#cocos-print .cp-ask p{margin:3px 0}',
    '#cocos-print .cp-ask .cp-line{border-bottom:1px solid var(--p-line);height:18px;margin:2px 0 6px}',
    '#cocos-print .cp-passage{font-family:"Source Serif 4",Georgia,serif;font-size:11.5pt;line-height:1.85;border:1px solid var(--p-line);border-radius:6px;padding:10px 13px;text-align:justify}',
    '#cocos-print .cp-passage sup{font-family:"Noto Sans KR",sans-serif;font-size:7pt;font-weight:700;color:var(--p-acc);margin:0 2px 0 1px}',
    '#cocos-print .cp-passage.cp-dialog{text-align:left}',
    '#cocos-print .cp-passage .cp-line{margin:0 0 3px}',
    '#cocos-print .cp-passage .cp-dn{font-family:"Noto Sans KR",sans-serif;font-size:9pt;font-weight:700;color:var(--p-acc-ink);margin:8px 0 3px}',
    '#cocos-print .cp-passage .cp-dn:first-child{margin-top:0}',
    '#cocos-print .cp-sp{font-family:"Noto Sans KR",sans-serif;font-size:9pt;color:var(--p-acc-ink);background:var(--p-soft);border-radius:4px;padding:0 6px;margin-right:4px}',
    '#cocos-print .cp-fig{font-family:"Noto Sans KR",sans-serif;font-size:9.5pt;margin:8px 0;break-inside:avoid}',
    '#cocos-print .cp-fig table{border-collapse:collapse;margin:4px auto}',
    '#cocos-print .cp-fig th,#cocos-print .cp-fig td{border:1px solid var(--p-line);padding:3px 10px;text-align:center}',
    '#cocos-print .cp-fig th{background:var(--p-soft)}',
    '#cocos-print .cp-fig .fig-cap{font-weight:700;text-align:center}',
    '#cocos-print .cp-gloss{font-size:9pt;color:var(--p-muted);margin-top:4px}',
    '#cocos-print .cp-pair{display:grid;grid-template-columns:22px 1fr;gap:0 6px;padding:5px 0;border-bottom:1px solid var(--p-line);break-inside:avoid}',
    '#cocos-print .cp-pair .cp-n{font-weight:700;color:var(--p-acc);font-size:9.5pt;padding-top:1px}',
    '#cocos-print .cp-pair .cp-e{font-family:"Source Serif 4",Georgia,serif;font-size:11pt;line-height:1.6}',
    '#cocos-print .cp-pair .cp-k{color:#3D4560;font-size:10pt;margin-top:1px}',
    '#cocos-print .cp-pair .cp-k.cp-blank{border-bottom:1px solid var(--p-line);height:20px}',
    '#cocos-print .cp-vocs{columns:2;column-gap:14px}',
    '#cocos-print .cp-vrow{display:grid;grid-template-columns:20px minmax(0,1.15fr) 24px minmax(0,1.6fr);gap:4px;padding:3px 0;border-bottom:1px solid var(--p-line);break-inside:avoid;font-size:9.5pt}',
    '#cocos-print .cp-vrow .cp-i{color:var(--p-muted);font-size:8pt;padding-top:2px}',
    '#cocos-print .cp-vrow .cp-w{font-family:"Source Serif 4",Georgia,serif;font-weight:600;font-size:10.5pt}',
    '#cocos-print .cp-vrow .cp-p{font-size:8pt;color:var(--p-acc-ink);background:var(--p-soft);border-radius:3px;text-align:center;align-self:start;margin-top:2px}',
    '#cocos-print .cp-map-sub{font-size:9.5pt;color:var(--p-muted);margin-bottom:6px}',
    '#cocos-print .cp-map{display:grid;grid-template-columns:1fr 1.05fr 1fr;gap:8px;align-items:center}',
    '#cocos-print .cp-map .cp-col{display:flex;flex-direction:column;gap:6px}',
    '#cocos-print .cp-node{border:1px solid var(--p-line);border-radius:7px;padding:6px 9px;break-inside:avoid;background:#fff}',
    '#cocos-print .cp-node b{display:block;font-size:10pt}',
    '#cocos-print .cp-node .cp-s{font-size:8.5pt;color:var(--p-muted)}',
    '#cocos-print .cp-node .cp-kk{font-family:"Source Serif 4",Georgia,serif;font-style:italic;font-size:9.5pt;color:var(--p-acc-ink)}',
    '#cocos-print .cp-node.cp-core{border:2px solid var(--p-acc);background:var(--p-soft);text-align:center;padding:10px}',
    '#cocos-print .cp-node.cp-core b{font-size:12pt}',
    '#cocos-print .cp-node.cp-end{grid-column:1 / -1;border-color:var(--p-ex);border-width:1.5px}',
    '#cocos-print .cp-q{margin:0 0 13px;break-inside:avoid}',
    '#cocos-print .cp-q .cp-qh{font-weight:700;margin-bottom:4px}',
    '#cocos-print .cp-q .cp-qh .cp-t{display:inline-block;font-size:8pt;font-weight:700;color:var(--p-acc-ink);background:var(--p-soft);border-radius:4px;padding:0 6px;margin-right:6px;vertical-align:1px}',
    '#cocos-print .cp-q .cp-qq{font-family:"Source Serif 4",Georgia,serif;font-size:10.5pt;line-height:1.75;border:1px solid var(--p-line);border-radius:6px;padding:7px 10px;margin:4px 0 5px}',
    '#cocos-print .cp-qq .box{display:block;border:1px solid var(--p-ink);padding:5px 9px;margin-bottom:7px}',
    '#cocos-print ol.cp-o{list-style:none;margin:0;padding:0 0 0 4px}',
    '#cocos-print ol.cp-o li{display:grid;grid-template-columns:auto 1fr;column-gap:6px;padding:1px 0;align-items:baseline}',
    '#cocos-print .cp-num{font-size:.72em;vertical-align:.08em;font-weight:400;line-height:1}',
    '#cocos-print ol.cp-o li>b{font-weight:400;font-size:.74em;line-height:1;position:relative;top:-.08em}',
    '#cocos-print ol.cp-o.cp-en li span{font-family:"Source Serif 4",Georgia,serif;font-size:10.5pt}',
    '#cocos-print ol.cp-o.cp-row{display:flex;flex-wrap:wrap;gap:2px 20px}',
    '#cocos-print ol.cp-o.cp-row li{display:flex;gap:6px}',
    '#cocos-print .cp-q .cp-write{border-bottom:1px solid var(--p-line);height:22px}',
    '#cocos-print .cp-ord{margin:0 0 11px;break-inside:avoid}',
    '#cocos-print .cp-ord .cp-chunks{display:flex;flex-wrap:wrap;gap:5px;margin:3px 0 4px}',
    '#cocos-print .cp-ord .cp-chunks span{font-family:"Source Serif 4",Georgia,serif;font-size:10pt;border:1px solid var(--p-line);border-radius:5px;padding:1px 7px}',
    '#cocos-print .cp-ord .cp-write{border-bottom:1px solid var(--p-line);height:20px}',
    '#cocos-print .cp-grid{display:grid;grid-template-columns:repeat(5,1fr);border:1px solid var(--p-line);border-radius:6px;overflow:hidden;margin-bottom:10px}',
    '#cocos-print .cp-grid div{padding:4px 8px;border-right:1px solid var(--p-line);border-bottom:1px solid var(--p-line);font-size:10pt}',
    '#cocos-print .cp-grid div b{color:var(--p-acc);margin-right:6px}',
    '#cocos-print .cp-ex{display:grid;grid-template-columns:minmax(30px,auto) 1fr;gap:4px;padding:4px 0;border-bottom:1px dashed var(--p-line);font-size:9.5pt;break-inside:avoid}',
    '#cocos-print .cp-ex .cp-n{font-weight:700;color:var(--p-acc)}',
    '#cocos-print .cp-ex .cp-a{font-weight:700;margin-right:6px;font-size:.78em}',
    '#cocos-print .cp-ex i{font-family:"Source Serif 4",Georgia,serif}',
    '#cocos-print .cp-foot{margin-top:18px;padding-top:8px;border-top:2px solid var(--p-acc);font-size:8.5pt;color:var(--p-muted);break-inside:avoid}',
    '#cocos-print .cp-foot b{color:var(--p-ink)}',
    '#cocos-print .cp-foot p{margin:2px 0}'
  ].join('\n');

  function sec(n, title, sub, cls) {
    return '<h2' + (cls ? ' class="cp-' + cls + '"' : '') + '><i>' + n + '</i>' + title + (sub ? '<small>' + sub + '</small>' : '') + '</h2>';
  }

  function build() {
    var h = [], n = 0, b = D.brief, i;
    var logo = document.querySelector('.brand .logo, .promo .logo');
    h.push('<div class="cp-top">' + (logo ? '<span class="logo" role="img" aria-label="코코스학원" style="display:inline-block"></span>' : '<b>코코스학원</b>') +
      '<span>코코스학원 온라인 학습지 · cocosedu.kr</span></div>');
    if (D.chips) h.push('<div class="cp-chips">' + D.chips.map(esc).join(' · ') + '</div>');
    h.push('<h1>' + (D.h1 || '') + '</h1>');
    if (D.enTitle) h.push('<p class="cp-entitle">' + D.enTitle + '</p>');
    if (D.gist) h.push('<p class="cp-gist"><b>요지</b>' + D.gist + '</p>');

    /* 1. 먼저 읽어 보세요 */
    if (b) {
      h.push(sec(++n, '먼저 읽어 보세요', '지문을 읽기 전에 글의 뼈대부터'));
      if (b.one) h.push('<span class="cp-lab">한 줄로 말하면</span><p class="cp-one">' + b.one + '</p>');
      if (b.flow && b.flow.length) {
        h.push('<span class="cp-lab">글의 흐름</span><ol class="cp-flow">');
        b.flow.forEach(function (f) {
          h.push('<li><b>' + esc(refs(f.s)) + '</b><span>' + (f.turn ? '<em>' + esc(f.turn) + '</em>' : '') + '<b>' + (f.t || '') + '</b> — ' + (f.d || '') + '</span></li>');
        });
        h.push('</ol>');
      }
      if (b.keys && b.keys.length) {
        h.push('<span class="cp-lab">핵심어</span><div class="cp-keys">' + b.keys.map(function (k) {
          return '<span><span class="cp-en">' + k[0] + '</span> ' + (k[1] || '') + '</span>';
        }).join('') + '</div>');
      }
      if (b.tips && b.tips.length) {
        h.push('<span class="cp-lab">읽다가 막히기 쉬운 곳</span><ul class="cp-tips">' + b.tips.map(function (t) {
          return '<li><b>' + t[0] + '</b> ' + t[1] + '</li>';
        }).join('') + '</ul>');
      }
      if (b.ask && b.ask.length) {
        h.push('<span class="cp-lab">다 읽은 뒤에 스스로 답해 보기</span><div class="cp-ask">' + b.ask.map(function (a, k) {
          return '<p>Q' + (k + 1) + '. ' + a[0] + '</p><div class="cp-line"></div>';
        }).join('') + '<p style="font-size:8.5pt;color:#5B6278">예시 답은 맨 뒤 정답에 있어요.</p></div>');
      }
    }

    /* 2. 지문 */
    h.push(sec(++n, '지문', '문장 번호는 해석·문제의 번호와 같아요'));
    var dialog = D.sentences.some(function (s) { return s.sp; });
    var fig = D.figure && D.figure.html ? '<div class="cp-fig">' + D.figure.html + '</div>' : '';
    var figAt = fig ? (+D.figure.after || D.sentences.length) : -1;
    var body = '';
    D.sentences.forEach(function (s, k) {
      if (dialog && s.dn) body += (k ? '</p>' : '') + '<p class="cp-dn">' + esc(s.dn) + '</p>' + (s.sp ? '' : '<p class="cp-line">');
      if (dialog && s.sp) body += (k && !s.dn ? '</p>' : '') + '<p class="cp-line"><b class="cp-sp">' + esc(s.sp) + '</b> ';
      else if (dialog && !k) body += '<p class="cp-line">';
      body += '<sup>' + (k + 1) + '</sup>' + s.en + ' ';
      if (k + 1 === figAt) body += (dialog ? '</p>' : '') + fig + (dialog ? '<p class="cp-line">' : '');
    });
    if (dialog) body += '</p>';
    h.push('<div class="cp-passage' + (dialog ? ' cp-dialog' : '') + '">' + body + '</div>');
    if (D.gloss && D.gloss.length) {
      h.push('<p class="cp-gloss">' + D.gloss.map(function (g) { return '* <span class="cp-en">' + g[0] + '</span> ' + g[1]; }).join('　') + '</p>');
    }

    /* 3. 문장별 해석 */
    h.push(sec(++n, '문장별 해석', ''));
    D.sentences.forEach(function (s, k) {
      h.push('<div class="cp-pair"><span class="cp-n">' + (k + 1) + '</span><div><p class="cp-e">' + (s.sp ? '<b class="cp-sp">' + esc(s.sp) + '</b> ' : '') + s.en + '</p><p class="cp-k">' + (s.ko || '') + '</p></div></div>');
    });

    /* 4. 단어 정리 */
    if (D.vocab && D.vocab.length) {
      h.push(sec(++n, '단어 정리', D.vocab.length + '개'));
      h.push('<div class="cp-vocs">' + D.vocab.map(function (v, k) {
        return '<div class="cp-vrow"><span class="cp-i">' + (k + 1) + '</span><span class="cp-w">' + esc(v.w) + '</span><span class="cp-p">' + esc(v.p || '') + '</span><span>' + esc(v.m) + '</span></div>';
      }).join('') + '</div>');
    }

    /* 5. 마인드맵 */
    var M = D.map;
    if (M && M.core) {
      var node = function (x, cls) {
        if (!x) return '';
        return '<div class="cp-node' + (cls ? ' cp-' + cls : '') + '"><b>' + (x.t || '') + '</b>' +
          (x.sub ? '<span class="cp-s">' + x.sub + '</span><br>' : '') +
          (x.k ? '<span class="cp-kk">' + x.k + '</span>' : '') +
          (x.s ? ' <span class="cp-s">(' + esc(refs(x.s)) + ')</span>' : '') + '</div>';
      };
      h.push(sec(++n, '마인드맵', '글의 구조를 한눈에'));
      if (M.sub) h.push('<p class="cp-map-sub">' + M.sub + '</p>');
      h.push('<div class="cp-map"><div class="cp-col">' + (M.left || []).map(function (x) { return node(x); }).join('') + '</div>' +
        node(M.core, 'core') +
        '<div class="cp-col">' + (M.right || []).map(function (x) { return node(x); }).join('') + '</div>' +
        node(M.end, 'end') + '</div>');
    }

    /* 6. 확인 문제 (도전 문제도 같은 모양으로 찍는다) */
    var Q = D.quiz || [];
    var CH = D.challenge || [];
    function qblock(Q, pre) {
      Q.forEach(function (q, k) {
        var s = '<div class="cp-q"><p class="cp-qh">' + pre + (k + 1) + '. ' + (q.type ? '<span class="cp-t">' + esc(q.type) + '</span>' : '') + neg(q.p || '') + '</p>';
        if (q.q) s += '<div class="cp-qq">' + nums(q.q) + '</div>';
        if (q.o && q.o.length) {
          var short = q.o.every(function (o) { return String(o).replace(/<[^>]+>/g, '').length <= 26; });
          s += '<ol class="cp-o' + (q.en ? ' cp-en' : '') + (short ? ' cp-row' : '') + '">' + q.o.map(function (o, j) {
            var bare = String(o).replace(/<[^>]+>/g, '').trim();
            if (bare === NUM[j] || bare === String(j + 1)) return '<li><b>' + NUM[j] + '</b><span></span></li>';
            return '<li><b>' + NUM[j] + '</b><span>' + nums(o) + '</span></li>';
          }).join('') + '</ol>';
        } else {
          s += '<div class="cp-write"></div><div class="cp-write"></div>';
        }
        h.push(s + '</div>');
      });
    }
    if (Q.length) {
      h.push(sec(++n, '확인 문제', Q.length + '문항 · 정답은 맨 뒤에', 'newpage'));
      qblock(Q, '');
    }
    if (CH.length) {
      h.push(sec(++n, '도전 문제', '고난도 ' + CH.length + '문항 · 변형 문제 · 정답은 맨 뒤에', 'newpage'));
      qblock(CH, '도전 ');
    }

    /* 7. 문장 배열 */
    var O = D.order || [];
    if (O.length) {
      h.push(sec(++n, '문장 배열', '덩어리를 바른 순서로 써 보세요'));
      O.forEach(function (o, k) {
        var c = o.c || [];
        var idx = shuffle(c, (o.s || k + 1) * 7 + c.length);
        h.push('<div class="cp-ord"><p class="cp-qh"><b>' + (o.s || k + 1) + '번 문장</b>' +
          (o.ko ? ' <span style="color:#5B6278;font-size:9.5pt">— ' + o.ko + '</span>' : D.sentences[(o.s || 0) - 1] && D.sentences[o.s - 1].ko ? ' <span style="color:#5B6278;font-size:9.5pt">— ' + D.sentences[o.s - 1].ko + '</span>' : '') + '</p>' +
          '<div class="cp-chunks">' + idx.map(function (j) {
            var t = c[j];
            if (j === 0 && !o.keep && !/^I\b/.test(t)) t = t.charAt(0).toLowerCase() + t.slice(1);
            /* 마지막 덩어리 끝의 . ? ! 는 순서 힌트라 PDF에서도 뺀다(화면과 같게, 2026-10-26) */
            if (j === c.length - 1 && c.length > 1) { var r = t.replace(/[.?!]+[\u201D\u2019"')]*$/, ''); if (r) t = r; }
            return '<span>' + esc(t) + '</span>';
          }).join('') + '</div>' +
          '<div class="cp-write"></div><div class="cp-write"></div></div>');
      });
    }

    /* 정답과 해설 */
    function akey(Q, pre) {
      h.push('<div class="cp-grid">' + Q.map(function (q, k) { return '<div><b>' + pre + (k + 1) + '</b>' + nums(ans(q)) + '</div>'; }).join('') + '</div>');
      Q.forEach(function (q, k) {
        if (!q.e) return;
        var lead = String(q.e).replace(/<[^>]+>/g, '').trim().charAt(0) === ans(q) ? '' : '<span class="cp-a">' + ans(q) + '</span>';
        h.push('<div class="cp-ex"><span class="cp-n">' + pre + (k + 1) + '</span><p>' + lead + nums(q.e) + '</p></div>');
      });
    }
    if (Q.length || CH.length || (b && b.ask) || O.length) {
      h.push(sec('✓', '정답과 해설', '', 'newpage'));
      if (Q.length) akey(Q, '');
      if (CH.length) {
        h.push('<span class="cp-lab">도전 문제</span>');
        akey(CH, '도전 ');
      }
      if (b && b.ask && b.ask.length) {
        h.push('<span class="cp-lab">먼저 읽어 보세요 · 스스로 답해 보기</span>');
        b.ask.forEach(function (a, k) { h.push('<div class="cp-ex"><span class="cp-n">Q' + (k + 1) + '</span><p>' + (a[1] || '') + '</p></div>'); });
      }
      if (O.length) {
        h.push('<span class="cp-lab">문장 배열</span>');
        O.forEach(function (o, k) { h.push('<div class="cp-ex"><span class="cp-n">' + (o.s || k + 1) + '번</span><p class="cp-en">' + esc((o.c || []).join(' ')) + '</p></div>'); });
      }
    }

    /* 끝 표시 */
    var share = document.querySelector('.promo .share');
    var copy = document.querySelector('footer .copy');
    var url = location.href.split('#')[0].split('?')[0];
    var d = new Date();
    h.push('<div class="cp-foot"><p><b>코코스학원</b> · 학습과 컨설팅을 하나로 · 상담 031-752-3334 · cocosedu.kr</p>' +
      (D.footer ? '<p>' + esc(D.footer) + '</p>' : '') +
      (copy ? '<p>' + esc(copy.textContent.replace(/\s+/g, ' ').trim()) + '</p>' : '') +
      (share ? '<p>' + esc(share.textContent.replace(/\s+/g, ' ').trim()) + '</p>' : '') +
      '<p>온라인 학습지 주소: ' + esc(url) + ' · 저장한 날 ' + d.getFullYear() + '.' + (d.getMonth() + 1) + '.' + d.getDate() + '</p></div>');

    var box = document.getElementById('cocos-print');
    if (!box) { box = document.createElement('div'); box.id = 'cocos-print'; document.body.appendChild(box); }
    box.innerHTML = h.join('\n');
  }

  function inApp() {
    var ua = navigator.userAgent || '';
    return /KAKAOTALK|NAVER\(inapp|Instagram|FBAN|FBAV|Line\//i.test(ua);
  }

  /* 화면의 요약문 빈칸 표시: 문제 화면이 바뀔 때마다 다시 그려지므로 지켜보다가 표시를 붙인다 */
  var BL = /^[\s\u2003\u00a0]*(?:\(?([A-E])\)?|([\u24d0-\u24e9]))[\s\u2003\u00a0]*$/;  /* (A)(B) 또는 중등 ⓐⓑ (2026-10-24) */
  function tagBlanks() {
    var us = document.querySelectorAll('u:not(.cocos-blank)');
    for (var i = 0; i < us.length; i++) {
      var u = us[i], m = BL.exec(u.textContent);
      if (m && !u.closest('#cocos-print')) { u.className += ' cocos-blank'; u.textContent = m[1] ? '(' + m[1] + ')' : m[2]; }
    }
  }
  var US = /_{3,}/;
  function tagLines() {
    if (!document.body || !document.createTreeWalker) return;
    var w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, {
      acceptNode: function (n) {
        if (!US.test(n.nodeValue)) return NodeFilter.FILTER_REJECT;
        var p = n.parentNode;
        if (!p || /^(SCRIPT|STYLE|TEXTAREA|INPUT)$/.test(p.nodeName) || p.closest('#cocos-print')) return NodeFilter.FILTER_REJECT;
        return NodeFilter.FILTER_ACCEPT;
      }
    });
    var list = [], n;
    while ((n = w.nextNode())) list.push(n);
    list.forEach(function (t) {
      var parts = t.nodeValue.split(/(_{3,})/), frag = document.createDocumentFragment();
      parts.forEach(function (x) {
        if (/^_{3,}$/.test(x)) {
          var sp = document.createElement('span'); sp.className = 'cocos-line';
          sp.style.width = Math.max(5, Math.round(x.length * 0.55)) + 'em';
          sp.setAttribute('aria-label', '빈칸'); frag.appendChild(sp);
        } else if (x) frag.appendChild(document.createTextNode(x));
      });
      t.parentNode.replaceChild(frag, t);
    });
  }
  /* 화면 지문 속 ①~⑤ 바로 뒤에 영어 낱말이 붙어 있으면 한 칸(줄바꿈 없는 칸) 띄운다 (선생님 요청 2026-10-15) */
  var CN = /[\u2460-\u24ff\u3260-\u327f]/, CN_IN = /([\u2460-\u24ff\u3260-\u327f])(?=[A-Za-z\u201c"'(])/g, CN_END = /[\u2460-\u24ff\u3260-\u327f]$/;  /* ①⑴ⓐⒶ㉠ 모두 (2026-10-24). 한글 조사 앞(ⓔ가)은 띄우지 않는다 */
  function tagNums() {
    if (!document.body || !document.createTreeWalker) return;
    var w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, {
      acceptNode: function (n) {
        if (!CN.test(n.nodeValue)) return NodeFilter.FILTER_REJECT;
        var p = n.parentNode;
        if (!p || /^(SCRIPT|STYLE|TEXTAREA|INPUT)$/.test(p.nodeName) || p.closest('#cocos-print')) return NodeFilter.FILTER_REJECT;
        return NodeFilter.FILTER_ACCEPT;
      }
    });
    var list = [], n;
    while ((n = w.nextNode())) list.push(n);
    list.forEach(function (t) {
      var v = t.nodeValue, nv = v.replace(CN_IN, '$1\u00a0');
      if (CN_END.test(nv) && t.nextSibling) {
        var nx = t.nextSibling, tx = nx.nodeType === 3 ? nx.nodeValue : (nx.textContent || '');
        if (/^[A-Za-z\u201c"'(]/.test(tx)) nv += '\u00a0';
      }
      if (nv !== v) t.nodeValue = nv;
    });
  }
  /* 발문의 '않은·없는·틀린·어색한·아닌·다른'에 밑줄: 시험지처럼 강조 (선생님 요청 2026-10-24)
     답을 고르는 말(것·곳·질문 등) 바로 앞에 올 때만 긋는다. '의도하지 않게 다른 사람' 같은 곳은 긋지 않는다. */
  var NEG = /(않은|않는|없는|틀린|어색한|아닌|다른)(?=\s*(것|곳|질문|문장|단어|낱말|표현|부분))/g;
  function neg(s) { return String(s == null ? '' : s).replace(NEG, '<u class="cocos-neg">$1</u>'); }
  function tagNeg() {
    var ps = document.querySelectorAll('.q .prompt:not([data-neg])');
    for (var i = 0; i < ps.length; i++) {
      var el = ps[i]; el.setAttribute('data-neg', '1');
      if (el.querySelector('u.cocos-neg')) continue;
      var h = el.innerHTML, nh = neg(h);
      if (nh !== h) el.innerHTML = nh;
    }
  }
  /* 앱 안 브라우저(카카오톡·네이버 등)에서 바로 바깥 브라우저로 여는 버튼 (2026-10-17) */
  function extUrl() {
    var u = location.href, ua = navigator.userAgent || '';
    if (/KAKAOTALK/i.test(ua)) return 'kakaotalk://web/openExternal?url=' + encodeURIComponent(u);
    if (/Android/i.test(ua) && /^https?:/.test(u)) return 'intent://' + u.replace(/^https?:\/\//, '') + '#Intent;scheme=https;package=com.android.chrome;S.browser_fallback_url=' + encodeURIComponent(u) + ';end';
    return '';
  }
  function tipHtml() {
    var x = extUrl(), ios = /iPhone|iPad|iPod/i.test(navigator.userAgent || '');
    var name = /KAKAOTALK/i.test(navigator.userAgent || '') ? (ios ? '사파리로 열기' : '다른 브라우저로 열기') : '크롬으로 열기';
    return '카카오톡·네이버 앱 안에서는 PDF 저장이 안 될 수 있어요. ' + (x ? '아래 버튼을 누르면 바로 열려요. 열린 화면에서 PDF 버튼을 다시 눌러 주세요.' : '화면 오른쪽 위(또는 아래) 메뉴에서 <b>‘다른 브라우저로 열기’</b>를 누른 뒤 다시 눌러 주세요.') +
      (x ? '<br><a class="cocos-ext" href="' + x + '">' + name + ' ↗</a>' : '');
  }
  function start() {
    tagBlanks(); tagLines(); tagNums(); tagNeg();
    try {
      var busy = false;
      new MutationObserver(function () {
        if (busy) return; busy = true;
        (window.requestAnimationFrame || setTimeout)(function () { busy = false; tagBlanks(); tagLines(); tagNums(); tagNeg(); });
      }).observe(document.body, { childList: true, subtree: true });
    } catch (e) {}
    var st = document.createElement('style');
    st.id = 'cocos-print-css';
    st.textContent = CSS;
    document.head.appendChild(st);

    var anchor = document.querySelector('header .jump') || document.querySelector('header h1');
    if (anchor) {
      var row = document.createElement('div');
      row.id = 'cocos-pdf-row';
      row.innerHTML = '<button type="button" id="cocos-pdf-btn"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 3v12"/><path d="m7 10 5 5 5-5"/><path d="M5 21h14"/></svg>PDF로 저장</button>' +
        '<small>지문·해석·단어·문제·정답을 PDF 한 파일로 저장해 패드에서 필기하며 공부할 수 있어요.</small>';
      anchor.parentNode.insertBefore(row, anchor.nextSibling);
      document.getElementById('cocos-pdf-btn').addEventListener('click', function () {
        var old = document.getElementById('cocos-pdf-tip'); if (old) old.remove();
        if (inApp()) {
          var tip = document.createElement('p'); tip.id = 'cocos-pdf-tip';
          tip.innerHTML = tipHtml();
          row.appendChild(tip);
        }
        build();
        try { window.print(); } catch (e) {}
      });
    }
    window.addEventListener('beforeprint', build);
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start);
  else start();
})();
