/* 코코스 단어게임 '단어 목록·시험지 PDF' (모든 단어게임 페이지가 함께 쓰는 파일)
   - 머리에 버튼을 넣고, 누르면 고를 것(단어 목록 / 뜻 쓰기 시험지 / 영어 쓰기 시험지)을 보여 준다.
   - 범위는 게임 화면의 '범위 고르기'에서 고른 지문을 따른다(안 골랐으면 전체).
   - 시험지는 순서를 섞고, 맨 뒤에 정답을 붙인다. PDF는 학생 기기에서 만들어진다.
   이 파일 하나를 고치면 모든 단어게임 페이지의 PDF 모양이 함께 바뀐다. */
(function () {
  'use strict';
  var D = window.DATA;
  if (!D || !D.W || !D.P || window.__cocosPrintGame) return;
  window.__cocosPrintGame = true;

  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c];
    });
  }
  function shuffle(a, seed) {
    a = a.slice(); var s = seed * 9301 + 49297;
    for (var i = a.length - 1; i > 0; i--) { s = (s * 9301 + 49297) % 233280; var j = Math.floor(s / 233280 * (i + 1)); var t = a[i]; a[i] = a[j]; a[j] = t; }
    return a;
  }
  var WORDS = D.W.map(function (r, i) { return { i: i, w: r[0], p: r[1] || '', m: r[2] || '', g: r[3] }; });

  function chosen() {
    var on = document.querySelectorAll('#range .rchip.on, #range .rchip[aria-pressed="true"]');
    var nos = {}; for (var i = 0; i < on.length; i++) nos[on[i].textContent.trim()] = 1;
    var gs = D.P.map(function (p, g) { return g; }).filter(function (g) { return nos[String(D.P[g].no)]; });
    return gs.length ? gs : D.P.map(function (p, g) { return g; });
  }
  function rangeLabel(gs) {
    if (gs.length === D.P.length) return '전체 ' + D.P.length + '개 지문';
    var a = gs.map(function (g) { return D.P[g].no; });
    var tail = a.every(function (x) { return /^[\d~-]+$/.test(String(x)); }) ? '번' : '';
    return a.length > 8 ? a.slice(0, 8).join(', ') + ' 외 ' + (a.length - 8) + '개 지문' : a.join(', ') + tail;
  }

  var CSS = [
    '#cocos-pdf-row{display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin-top:14px}',
    '.cocos-pdf-btn{display:inline-flex;align-items:center;gap:7px;font:inherit;font-size:15px;font-weight:700;padding:9px 16px;border-radius:999px;border:1.5px solid var(--accent,#0A7FBF);background:var(--card,#fff);color:var(--accent-ink,#065A88);cursor:pointer}',
    '.cocos-pdf-btn.go{background:var(--accent,#0A7FBF);color:#fff}',
    '.cocos-pdf-btn svg{width:18px;height:18px}',
    '#cocos-pdf-row>small{font-size:13px;color:var(--muted,#5B6278);flex-basis:100%}',
    '#cocos-pdf-panel{flex-basis:100%;background:var(--card,#fff);border:1px solid var(--line,#DDE0EA);border-radius:12px;padding:12px 14px;display:flex;flex-direction:column;gap:8px}',
    '#cocos-pdf-panel[hidden]{display:none}',
    '#cocos-pdf-panel label{display:flex;align-items:center;gap:8px;font-size:15px;cursor:pointer}',
    '#cocos-pdf-panel input{width:18px;height:18px;accent-color:var(--accent,#0A7FBF)}',
    '#cocos-pdf-panel .rg{font-size:13.5px;color:var(--muted,#5B6278)}',
    '#cocos-pdf-tip{flex-basis:100%;font-size:13.5px;color:var(--ink,#1B2033);background:var(--accent-soft,#E2F3FC);border-radius:10px;padding:10px 14px;margin:0}',
    '@media screen{#cocos-print{display:none}}',
    '@media print{',
    '  @page{size:A4;margin:13mm 12mm 14mm}',
    '  html,body{background:#fff!important;color:#1B2033!important;margin:0!important;padding:0!important}',
    '  body>*:not(#cocos-print){display:none!important}',
    '  #cocos-print{display:block!important}',
    '}',
    '#cocos-print{--p-ink:#1B2033;--p-muted:#5B6278;--p-line:#D5D9E3;--p-acc:#0A7FBF;--p-acc-ink:#065A88;--p-soft:#E9F5FC;',
    '  color:var(--p-ink);font-family:"Noto Sans KR","Apple SD Gothic Neo","Malgun Gothic",sans-serif;font-size:10pt;line-height:1.5;word-break:keep-all;',
    '  -webkit-print-color-adjust:exact;print-color-adjust:exact}',
    '#cocos-print *{box-sizing:border-box}',
    '#cocos-print p{margin:0}',
    '#cocos-print h1,#cocos-print h2{color:var(--p-ink);font-family:"Noto Sans KR","Apple SD Gothic Neo",sans-serif;letter-spacing:0}',
    '#cocos-print .cp-top{display:flex;justify-content:space-between;align-items:center;border-bottom:2.5px solid var(--p-acc);padding-bottom:6px;margin-bottom:8px}',
    '#cocos-print .cp-top .logo{display:inline-block;width:118px;height:27px}',
    '#cocos-print .cp-top span{font-size:9pt;color:var(--p-muted)}',
    '#cocos-print h1{font-size:15pt;margin:0 0 2px}',
    '#cocos-print .cp-sub{font-size:9.5pt;color:var(--p-muted);margin-bottom:6px}',
    '#cocos-print .cp-name{display:flex;gap:26px;font-size:10pt;margin:4px 0 8px}',
    '#cocos-print .cp-name span{border-bottom:1px solid var(--p-ink);min-width:110px;display:inline-block}',
    '#cocos-print .cp-newpage{break-before:page;page-break-before:always}',
    '#cocos-print h2{font-size:10.5pt;color:var(--p-acc-ink);background:var(--p-soft);border-radius:5px;padding:3px 9px;margin:10px 0 4px;break-after:avoid;page-break-after:avoid}',
    '#cocos-print .cp-grid{columns:2;column-gap:16px}',
    '#cocos-print .cp-r{display:grid;grid-template-columns:24px minmax(0,1fr) 22px minmax(0,1.25fr);gap:5px;align-items:end;padding:3px 0;border-bottom:1px solid var(--p-line);break-inside:avoid}',
    '#cocos-print .cp-r .n{color:var(--p-muted);font-size:8pt;padding-bottom:1px}',
    '#cocos-print .cp-r .w{font-family:"Source Serif 4",Georgia,serif;font-weight:600;font-size:10.5pt}',
    '#cocos-print .cp-r .p{font-size:7.8pt;color:var(--p-acc-ink);background:var(--p-soft);border-radius:3px;text-align:center;align-self:center}',
    '#cocos-print .cp-r .m{font-size:9.4pt}',
    '#cocos-print .cp-r .b{height:20px}',
    '#cocos-print .cp-t .cp-r{padding:6px 0 3px}',
    '#cocos-print .cp-key{columns:3;column-gap:14px;font-size:8.8pt}',
    '#cocos-print .cp-key div{break-inside:avoid;padding:1px 0;border-bottom:1px dotted var(--p-line)}',
    '#cocos-print .cp-key b{color:var(--p-acc);display:inline-block;min-width:26px}',
    '#cocos-print .cp-key i{font-style:normal;font-family:"Source Serif 4",Georgia,serif}',
    '#cocos-print .cp-end{margin-top:14px;padding-top:7px;border-top:2px solid var(--p-acc);font-size:8.5pt;color:var(--p-muted);break-inside:avoid}',
    '#cocos-print .cp-end p{margin:2px 0}',
    '#cocos-print .cp-end b{color:var(--p-ink)}'
  ].join('\n');

  function head(title, sub, name) {
    var logo = document.querySelector('.brand .logo, .promo .logo');
    return '<div class="cp-top">' + (logo ? '<span class="logo" role="img" aria-label="코코스학원"></span>' : '<b>코코스학원</b>') +
      '<span>코코스학원 단어게임 · cocosedu.kr</span></div><h1>' + esc(title) + '</h1><p class="cp-sub">' + esc(sub) + '</p>' +
      (name ? '<div class="cp-name">이름 <span></span> 날짜 <span></span> 점수 <span style="min-width:70px"></span> / ' + name + '</div>' : '');
  }

  function build(opt) {
    var gs = chosen(), label = (D.label || '') + ' · ' + rangeLabel(gs);
    var list = WORDS.filter(function (v) { return gs.indexOf(v.g) > -1; });
    var h = [], first = true;
    function page() { var c = first ? '' : ' class="cp-newpage"'; first = false; return c; }

    if (opt.list) {
      h.push('<div' + page() + '>' + head('단어 목록', label + ' · 단어 ' + list.length + '개'));
      gs.forEach(function (g) {
        var ws = list.filter(function (v) { return v.g === g; }); if (!ws.length) return;
        h.push('<h2>' + esc(D.P[g].no) + (/^[\d~-]+$/.test(String(D.P[g].no)) ? '번' : '') + ' · ' + esc(D.P[g].topic || '') + '</h2><div class="cp-grid">' + ws.map(function (v, k) {
          return '<div class="cp-r"><span class="n">' + (k + 1) + '</span><span class="w">' + esc(v.w) + '</span><span class="p">' + esc(v.p) + '</span><span class="m">' + esc(v.m) + '</span></div>';
        }).join('') + '</div>');
      });
      h.push('</div>');
    }
    var seed = gs.reduce(function (a, g) { return a * 31 + g + 7; }, list.length) % 100000;
    var mixed = shuffle(list, seed);
    if (opt.mean) {
      h.push('<div' + page() + ' >' + head('단어 시험 · 뜻 쓰기', label + ' · 영어 단어를 보고 우리말 뜻을 쓰세요. 순서는 섞여 있어요.', mixed.length));
      h.push('<div class="cp-grid cp-t">' + mixed.map(function (v, k) {
        return '<div class="cp-r"><span class="n">' + (k + 1) + '</span><span class="w">' + esc(v.w) + '</span><span class="p">' + esc(v.p) + '</span><span class="b" style="border-bottom:1px solid #1B2033"></span></div>';
      }).join('') + '</div></div>');
    }
    var mixed2 = shuffle(list, seed + 13);
    if (opt.spell) {
      h.push('<div' + page() + '>' + head('단어 시험 · 영어 쓰기', label + ' · 우리말 뜻을 보고 영어 단어를 쓰세요. 순서는 섞여 있어요.', mixed2.length));
      h.push('<div class="cp-grid cp-t">' + mixed2.map(function (v, k) {
        return '<div class="cp-r" style="grid-template-columns:24px minmax(0,1.25fr) 22px minmax(0,1fr)"><span class="n">' + (k + 1) + '</span><span class="m">' + esc(v.m) + '</span><span class="p">' + esc(v.p) + '</span><span class="b" style="border-bottom:1px solid #1B2033"></span></div>';
      }).join('') + '</div></div>');
    }
    if (opt.mean || opt.spell) {
      h.push('<div class="cp-newpage">' + head('시험지 정답', label));
      if (opt.mean) h.push('<h2>뜻 쓰기</h2><div class="cp-key">' + mixed.map(function (v, k) { return '<div><b>' + (k + 1) + '</b>' + esc(v.m) + '</div>'; }).join('') + '</div>');
      if (opt.spell) h.push('<h2>영어 쓰기</h2><div class="cp-key">' + mixed2.map(function (v, k) { return '<div><b>' + (k + 1) + '</b><i>' + esc(v.w) + '</i></div>'; }).join('') + '</div>');
      h.push('</div>');
    }
    var share = document.querySelector('.promo .share');
    var url = location.href.split('#')[0].split('?')[0];
    var d = new Date();
    h.push('<div class="cp-end"><p><b>코코스학원</b> · 학습과 컨설팅을 하나로 · 상담 031-752-3334 · cocosedu.kr</p>' +
      (D.meta && D.meta.source ? '<p>' + esc(D.meta.source) + '</p>' : '') +
      (share ? '<p>' + esc(share.textContent.replace(/\s+/g, ' ').trim()) + '</p>' : '') +
      '<p>단어게임 주소: ' + esc(url) + ' · 저장한 날 ' + d.getFullYear() + '.' + (d.getMonth() + 1) + '.' + d.getDate() + '</p></div>');
    var box = document.getElementById('cocos-print');
    if (!box) { box = document.createElement('div'); box.id = 'cocos-print'; document.body.appendChild(box); }
    box.innerHTML = h.join('\n');
  }

  function inApp() { return /KAKAOTALK|NAVER\(inapp|Instagram|FBAN|FBAV|Line\//i.test(navigator.userAgent || ''); }
  var ICON = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 3v12"/><path d="m7 10 5 5 5-5"/><path d="M5 21h14"/></svg>';

  function start() {
    var st = document.createElement('style'); st.id = 'cocos-print-css'; st.textContent = CSS; document.head.appendChild(st);
    var anchor = document.querySelector('header #links') || document.querySelector('header .gist') || document.querySelector('header h1');
    if (!anchor) return;
    var row = document.createElement('div'); row.id = 'cocos-pdf-row';
    row.innerHTML = '<button type="button" class="cocos-pdf-btn" id="cocos-pdf-open">' + ICON + '단어 목록·시험지 PDF</button>' +
      '<small>아래 ‘범위 고르기’에서 고른 지문의 단어로 만들어요. 안 고르면 전체 단어로 만들어요.</small>' +
      '<div id="cocos-pdf-panel" hidden>' +
      '<p class="rg" id="cocos-pdf-rg"></p>' +
      '<label><input type="checkbox" id="cp-o-list" checked> 단어 목록 (지문별 · 뜻 포함)</label>' +
      '<label><input type="checkbox" id="cp-o-mean" checked> 뜻 쓰기 시험지</label>' +
      '<label><input type="checkbox" id="cp-o-spell" checked> 영어 쓰기 시험지</label>' +
      '<div><button type="button" class="cocos-pdf-btn go" id="cocos-pdf-go">' + ICON + 'PDF 만들기</button></div></div>';
    anchor.parentNode.insertBefore(row, anchor.nextSibling);
    var panel = document.getElementById('cocos-pdf-panel');
    function refresh() {
      var gs = chosen(), n = WORDS.filter(function (v) { return gs.indexOf(v.g) > -1; }).length;
      document.getElementById('cocos-pdf-rg').textContent = '지금 범위: ' + rangeLabel(gs) + ' · 단어 ' + n + '개';
    }
    document.getElementById('cocos-pdf-open').addEventListener('click', function () { panel.hidden = !panel.hidden; refresh(); });
    document.addEventListener('click', function (e) { if (!panel.hidden && e.target.closest && e.target.closest('#range')) setTimeout(refresh, 0); });
    document.getElementById('cocos-pdf-go').addEventListener('click', function () {
      var opt = { list: document.getElementById('cp-o-list').checked, mean: document.getElementById('cp-o-mean').checked, spell: document.getElementById('cp-o-spell').checked };
      if (!opt.list && !opt.mean && !opt.spell) { opt.list = true; document.getElementById('cp-o-list').checked = true; }
      var old = document.getElementById('cocos-pdf-tip'); if (old) old.remove();
      if (inApp()) {
        var tip = document.createElement('p'); tip.id = 'cocos-pdf-tip';
        tip.innerHTML = '카카오톡·네이버 앱 안에서는 PDF 저장이 안 될 수 있어요. 화면 오른쪽 위(또는 아래) 메뉴에서 <b>‘다른 브라우저로 열기’</b>를 누른 뒤 다시 눌러 주세요.';
        row.appendChild(tip);
      }
      build(opt);
      try { window.print(); } catch (err) {}
    });
    window.addEventListener('beforeprint', function () { if (!document.getElementById('cocos-print')) build({ list: true, mean: true, spell: true }); });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start); else start();
})();
