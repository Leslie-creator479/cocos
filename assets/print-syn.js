/* 코코스 동의어·반의어 'PDF로 저장' (모든 동의어·반의어 페이지가 함께 쓰는 파일)
   - 머리에 '이 지문 PDF' · '전체 지문 PDF' 버튼을 넣는다.
   - 누르면 DATA.passages로 인쇄용 화면(원지문 ★◆ 표시·해석·어휘 정리·2단계 문맥 속 고르기·
     3단계 어휘 추론 변형·정답)을 만들고 인쇄 창을 연다. PDF는 학생 기기에서 만들어진다.
   이 파일 하나를 고치면 모든 동의어·반의어 페이지의 PDF 모양이 함께 바뀐다. */
(function () {
  'use strict';
  var D = window.DATA;
  if (!D || !D.passages || window.__cocosPrintSyn) return;
  window.__cocosPrintSyn = true;

  var NUM = ['①', '②', '③', '④', '⑤', '⑥', '⑦', '⑧'];
  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c];
    });
  }
  function num(n) { return '<span class="cp-num">' + n + '</span>'; }
  function rnd(seed) { var s = seed * 9301 + 49297; return function () { s = (s * 9301 + 49297) % 233280; return s / 233280; }; }
  function mk(w) { return (w.star ? '<b class="cp-s">★</b>' : '') + (w.topic ? '<b class="cp-t">◆</b>' : ''); }
  function lines(p, fn) {
    return (p.lines || []).map(function (segs) {
      if (segs.length === 1 && segs[0] === '↓') return '<p class="cp-arrow">↓</p>';
      return '<p>' + segs.map(function (s) { return typeof s === 'number' ? fn(s) : esc(s); }).join('') + '</p>';
    }).join('');
  }

  var CSS = [
    '#cocos-pdf-row{display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin-top:14px}',
    '.cocos-pdf-btn{display:inline-flex;align-items:center;gap:7px;font:inherit;font-size:15px;font-weight:700;padding:9px 16px;border-radius:999px;border:1.5px solid var(--accent,#0A7FBF);background:var(--card,#fff);color:var(--accent-ink,#065A88);cursor:pointer}',
    '.cocos-pdf-btn:hover{background:var(--accent-soft,#E2F3FC)}',
    '.cocos-pdf-btn svg{width:18px;height:18px}',
    '#cocos-pdf-row small{font-size:13px;color:var(--muted,#5B6278);flex-basis:100%}',
    '#cocos-pdf-tip{flex-basis:100%;font-size:13.5px;color:var(--ink,#1B2033);background:var(--accent-soft,#E2F3FC);border-radius:10px;padding:10px 14px;margin:0}',
    '@media screen{#cocos-print{display:none}}',
    '@media print{',
    /* 좌우 여백은 내용 안쪽 여백으로 준다: 인쇄 창에서 '여백 없음'을 골라도 좌우가 꽉 차지 않게 (2026-10-15) */
    '  @page{size:A4;margin:12mm 0 13mm}',
    '  html,body{width:auto!important;min-width:0!important;max-width:none!important;overflow:visible!important}',
    '  #cocos-print{padding:0 14mm!important;box-sizing:border-box;width:auto!important;max-width:100%!important}',
    '  html,body{background:#fff!important;color:#1B2033!important;margin:0!important;padding:0!important}',
    '  body>*:not(#cocos-print){display:none!important}',
    '  #cocos-print{display:block!important}',
    '}',
    '#cocos-print{--p-ink:#1B2033;--p-muted:#5B6278;--p-line:#D5D9E3;--p-acc:#0A7FBF;--p-acc-ink:#065A88;--p-soft:#E9F5FC;--p-red:#B3261E;--p-topic:#C25A12;',
    '  color:var(--p-ink);font-family:"Noto Sans KR","Apple SD Gothic Neo","Malgun Gothic",sans-serif;font-size:10.5pt;line-height:1.65;word-break:keep-all;overflow-wrap:break-word;',
    '  -webkit-print-color-adjust:exact;print-color-adjust:exact}',
    '#cocos-print *{box-sizing:border-box}',
    '#cocos-print p{margin:0}',
    '#cocos-print h1,#cocos-print h2,#cocos-print h3{color:var(--p-ink);font-family:"Noto Sans KR","Apple SD Gothic Neo",sans-serif;letter-spacing:0}',
    '#cocos-print .cp-en{font-family:"Source Serif 4",Georgia,"Times New Roman",serif}',
    '#cocos-print .cp-num{font-size:.72em;font-weight:400;line-height:1;vertical-align:.08em}',
    '#cocos-print .cp-top{display:flex;justify-content:space-between;align-items:center;border-bottom:2.5px solid var(--p-acc);padding-bottom:6px;margin-bottom:10px}',
    '#cocos-print .cp-top .logo{display:inline-block;width:118px;height:27px}',
    '#cocos-print .cp-top span{font-size:9pt;color:var(--p-muted)}',
    '#cocos-print .cp-chips{font-size:9pt;color:var(--p-acc-ink);font-weight:700}',
    '#cocos-print .cp-ph{break-inside:avoid;margin:2px 0 6px}',
    '#cocos-print .cp-ph h1{font-size:15.5pt;line-height:1.35;margin:2px 0}',
    '#cocos-print .cp-ph .cp-ent{font-family:"Source Serif 4",Georgia,serif;font-style:italic;color:var(--p-muted);font-size:10.5pt}',
    '#cocos-print .cp-sum{border:1px solid var(--p-line);border-left:4px solid var(--p-acc);border-radius:6px;padding:6px 10px;font-size:9.8pt;margin-top:6px}',
    '#cocos-print h2{display:flex;align-items:center;gap:8px;font-size:12pt;margin:14px 0 6px;padding-bottom:3px;border-bottom:1px solid var(--p-line);break-after:avoid;page-break-after:avoid}',
    '#cocos-print h2 small{font-weight:400;font-size:8.8pt;color:var(--p-muted);margin-left:auto}',
    '#cocos-print .cp-newpage{break-before:page;page-break-before:always}',
    '#cocos-print .cp-keys{font-size:8.8pt;color:var(--p-muted);margin:0 0 4px}',
    '#cocos-print .cp-keys span{margin-right:12px}',
    '#cocos-print .cp-s{color:var(--p-red);font-weight:700;font-size:.8em}',
    '#cocos-print .cp-t{color:var(--p-topic);font-weight:700;font-size:.8em}',
    '#cocos-print .cp-text{font-family:"Source Serif 4",Georgia,serif;font-size:11pt;line-height:1.95;border:1px solid var(--p-line);border-radius:6px;padding:8px 12px}',
    '#cocos-print .cp-text p{margin:0 0 4px}',
    '#cocos-print .cp-text .cp-arrow{text-align:center;margin:2px 0}',
    '#cocos-print .cp-w{color:var(--p-acc-ink);font-weight:600}',
    '#cocos-print .cp-w.cp-ws{color:var(--p-red)}',
    '#cocos-print .cp-w.cp-wt{text-decoration:underline;text-decoration-color:var(--p-topic);text-decoration-thickness:1.5px;text-underline-offset:3px}',
    '#cocos-print .cp-text sup,#cocos-print .cp-ko sup{font-family:"Noto Sans KR",sans-serif;font-size:6.8pt;font-weight:700;color:var(--p-acc);margin-left:1px}',
    '#cocos-print .cp-foot{font-size:8.8pt;color:var(--p-muted);margin-top:3px}',
    '#cocos-print .cp-ko{font-size:10pt;line-height:1.85;background:#F6F8FB;border-radius:6px;padding:7px 11px;margin-top:6px}',
    '#cocos-print .cp-ko b{color:var(--p-acc-ink)}',
    '#cocos-print table.cp-vt{width:100%;border-collapse:collapse;font-size:9.3pt}',
    '#cocos-print .cp-vt th{background:var(--p-soft);color:var(--p-acc-ink);font-weight:700;padding:4px 6px;border:1px solid var(--p-line);text-align:left}',
    '#cocos-print .cp-vt td{padding:3px 6px;border:1px solid var(--p-line);vertical-align:top}',
    '#cocos-print .cp-vt tr{break-inside:avoid}',
    '#cocos-print .cp-vt tr.cp-both td{background:#FFF6EE}',
    '#cocos-print .cp-vt td.cp-no{white-space:nowrap;color:var(--p-muted)}',
    '#cocos-print .cp-vt td.cp-h{font-family:"Source Serif 4",Georgia,serif;font-weight:600;font-size:10.2pt}',
    '#cocos-print .cp-vt td.cp-l{font-family:"Source Serif 4",Georgia,serif;font-size:9.8pt}',
    '#cocos-print .cp-stem{font-weight:700;margin:2px 0 4px}',
    '#cocos-print .cp-pk{white-space:nowrap;font-family:"Noto Sans KR",sans-serif;font-size:8.8pt;border:1px solid var(--p-line);border-radius:4px;padding:0 4px;margin:0 1px}',
    '#cocos-print .cp-pk i{font-style:normal;font-family:"Source Serif 4",Georgia,serif;font-size:10.2pt}',
    '#cocos-print .cp-pk em{font-style:normal;color:var(--p-muted);margin:0 3px}',
    '#cocos-print .cp-set{break-inside:avoid;margin:0 0 10px}',
    '#cocos-print .cp-set .cp-text{font-size:10.4pt;line-height:1.85}',
    '#cocos-print .cp-ul{text-decoration:underline;text-underline-offset:3px}',
    '#cocos-print .cp-opts{display:flex;gap:22px;margin:4px 0 0 4px;font-size:11pt}',
    '#cocos-print .cp-ans{font-size:9.4pt}',
    '#cocos-print .cp-ans .cp-row{display:grid;grid-template-columns:52px 1fr;gap:4px;padding:3px 0;border-bottom:1px dashed var(--p-line);break-inside:avoid}',
    '#cocos-print .cp-ans .cp-row>b:first-child{color:var(--p-acc);white-space:nowrap}',
    '#cocos-print .cp-ans i{font-family:"Source Serif 4",Georgia,serif}',
    '#cocos-print .cp-lab{display:inline-block;font-size:8.5pt;font-weight:700;color:var(--p-acc-ink);background:var(--p-soft);border-radius:4px;padding:1px 7px;margin:8px 0 3px}',
    '#cocos-print .cp-pgrid{display:grid;grid-template-columns:repeat(4,1fr);gap:0;border:1px solid var(--p-line);border-radius:6px;overflow:hidden}',
    '#cocos-print .cp-pgrid div{padding:3px 7px;border-right:1px solid var(--p-line);border-bottom:1px solid var(--p-line);font-size:9.4pt}',
    '#cocos-print .cp-pgrid div b{color:var(--p-acc);margin-right:5px}',
    '#cocos-print .cp-end{margin-top:16px;padding-top:7px;border-top:2px solid var(--p-acc);font-size:8.5pt;color:var(--p-muted);break-inside:avoid}',
    '#cocos-print .cp-end p{margin:2px 0}',
    '#cocos-print .cp-end b{color:var(--p-ink)}'
  ].join('\n');

  function passage(p, k, first) {
    var h = [], W = p.words || [];
    var r = rnd((k + 1) * 31 + W.length);
    h.push('<div class="cp-ph' + (first ? '' : ' cp-newpage') + '">' +
      '<div class="cp-chips">' + esc(p.lab) + '</div><h1>' + esc(p.kr) + '</h1>' +
      (p.en ? '<p class="cp-ent">' + esc(p.en) + '</p>' : '') +
      (p.sum ? '<p class="cp-sum"><b style="color:#065A88;margin-right:6px">요지</b>' + esc(p.sum) + '</p>' : '') + '</div>');

    /* 원지문 */
    h.push('<h2>원지문<small>번호는 어휘 정리 번호와 같아요</small></h2>');
    h.push('<p class="cp-keys"><span><b class="cp-s">★</b> 빨강: 반의어로 바뀌기 쉬운 어휘</span><span><b class="cp-t">◆</b> 밑줄: 주제 연관 어휘</span><span style="color:#065A88;font-weight:700">파랑</span>: 동의어로 바뀌기 좋은 어휘</p>');
    h.push('<div class="cp-text">' + lines(p, function (i) {
      var w = W[i]; if (!w) return '';
      var t = w.t || w.c || w.h, c = w.c || t, j = t.indexOf(c);
      var pre = j > 0 ? t.slice(0, j) : '', post = j >= 0 ? t.slice(j + c.length) : '';
      if (j < 0) c = t;
      return esc(pre) + '<span class="cp-w' + (w.star ? ' cp-ws' : '') + (w.topic ? ' cp-wt' : '') + '">' + esc(c) + '</span><sup>' + (i + 1) + '</sup>' + esc(post);
    }) + '</div>');
    if (p.foot) h.push('<p class="cp-foot">' + esc(p.foot) + '</p>');
    if (p.kolines && p.kolines.length) {
      h.push('<div class="cp-ko">' + p.kolines.map(function (segs) {
        return '<p>' + segs.map(function (s) {
          if (typeof s !== 'number') return esc(s);
          var w = W[s] || {}; return '<b>' + esc(w.kc || w.ko || '') + '</b><sup>' + (s + 1) + '</sup>';
        }).join('') + '</p>';
      }).join('') + '</div>');
    }

    /* 어휘 정리 */
    h.push('<h2>어휘 정리<small>≒ 동의어 · ↔ 반의어</small></h2>');
    h.push('<table class="cp-vt"><thead><tr><th>No</th><th>본문 어휘</th><th>문맥상 뜻</th><th>≒ 동의어</th><th>↔ 반의어</th></tr></thead><tbody>' +
      W.map(function (w, i) {
        return '<tr' + (w.star && w.topic ? ' class="cp-both"' : '') + '><td class="cp-no">' + (i + 1) + ' ' + mk(w) + '</td><td class="cp-h">' + esc(w.h) + '</td><td>' + esc(w.ko) + '</td><td class="cp-l">' + esc((w.syn || []).join(', ')) + '</td><td class="cp-l">' + esc((w.ant || []).join(', ') || '—') + '</td></tr>';
      }).join('') + '</tbody></table>');

    /* 2단계 문맥 속 고르기 (동의어 하나와 반의어 하나 중 고르기) */
    var pick = W.map(function (w) {
      var a = (w.st && w.st[0]) || (w.syn && w.syn[0]) || w.h, b = w.x || (w.ant && w.ant[0]) || '';
      return { ok: a, flip: r() < 0.5, b: b };
    });
    h.push('<h2>2단계 · 문맥 속 고르기<small>문맥에 맞는 쪽에 ○</small></h2>');
    h.push('<div class="cp-text">' + lines(p, function (i) {
      var q = pick[i]; if (!q || !q.b) return esc((W[i] || {}).t || '');
      var x = q.flip ? [q.b, q.ok] : [q.ok, q.b];
      return '<span class="cp-pk"><i>' + esc(x[0]) + '</i><em>/</em><i>' + esc(x[1]) + '</i></span><sup>' + (i + 1) + '</sup>';
    }) + '</div>');

    /* 3단계 어휘 추론 · 변형 */
    var S = p.sets || [];
    if (S.length) {
      h.push('<h2 class="cp-newpage">3단계 · 어휘 추론 · 변형<small>세트 ' + S.length + '개 · 밑줄 다섯 곳 중 한 곳만 문맥에 맞지 않아요</small></h2>');
      S.forEach(function (set, si) {
        h.push('<div class="cp-set"><p class="cp-stem">세트 ' + (si + 1) + '. 밑줄 친 부분 중, 문맥상 낱말의 쓰임이 적절하지 않은 것은?</p><div class="cp-text">' +
          lines(p, function (i) {
            var pos = set.idx.indexOf(i), w = W[i] || {};
            if (pos < 0) return esc(w.t || '');
            return num(NUM[pos]) + '&nbsp;<span class="cp-ul">' + esc(set.show[pos]) + '</span>';
          }) + '</div><div class="cp-opts">' + NUM.slice(0, 5).map(num).join('') + '</div></div>');
      });
    }

    /* 정답 */
    h.push('<h2 class="cp-newpage">정답과 해설 · ' + esc(p.lab) + '</h2><div class="cp-ans">');
    h.push('<span class="cp-lab">2단계 · 문맥 속 고르기</span><div class="cp-pgrid">' + W.map(function (w, i) {
      return '<div><b>' + (i + 1) + '</b><span class="cp-en">' + esc(pick[i].ok) + '</span></div>';
    }).join('') + '</div>');
    if (S.length) {
      h.push('<span class="cp-lab">3단계 · 어휘 추론 · 변형</span>');
      S.forEach(function (set, si) {
        var wi = set.idx[set.wrong], w = W[wi] || {};
        h.push('<div class="cp-row"><b>세트 ' + (si + 1) + '</b><p><b>' + num(NUM[set.wrong]) + '</b> <i>' + esc(set.show[set.wrong]) + '</i> → 반의어예요. 원문 <b class="cp-en">' + esc(w.t || w.h) + '</b>(' + esc(w.ko) + ') 자리라 <i>' + esc((w.st || w.syn || []).join(', ')) + '</i> 같은 말이 와야 해요.</p></div>');
      });
    }
    h.push('</div>');
    return h.join('\n');
  }

  function build(which) {
    var ps = D.passages, list;
    if (which === 'one') {
      var b = document.querySelector('#ptabs button[aria-pressed="true"]');
      var k = b ? +b.getAttribute('data-i') : 0;
      list = [k];
    } else list = ps.map(function (_, i) { return i; });
    var h = [];
    var logo = document.querySelector('.brand .logo, .promo .logo');
    h.push('<div class="cp-top">' + (logo ? '<span class="logo" role="img" aria-label="코코스학원"></span>' : '<b>코코스학원</b>') +
      '<span>코코스학원 동의어·반의어 · cocosedu.kr</span></div>');
    if (D.chips) h.push('<div class="cp-chips" style="margin-bottom:2px">' + D.chips.map(esc).join(' · ') + '</div>');
    list.forEach(function (k, n) { h.push(passage(ps[k], k, n === 0)); });
    var share = document.querySelector('.promo .share');
    var url = location.href.split('#')[0].split('?')[0];
    var d = new Date();
    h.push('<div class="cp-end"><p><b>코코스학원</b> · 학습과 컨설팅을 하나로 · 상담 031-752-3334 · cocosedu.kr</p>' +
      (D.footer ? '<p>' + esc(D.footer) + '</p>' : '') +
      (share ? '<p>' + esc(share.textContent.replace(/\s+/g, ' ').trim()) + '</p>' : '') +
      '<p>온라인 학습지 주소: ' + esc(url) + ' · 저장한 날 ' + d.getFullYear() + '.' + (d.getMonth() + 1) + '.' + d.getDate() + '</p></div>');
    var box = document.getElementById('cocos-print');
    if (!box) { box = document.createElement('div'); box.id = 'cocos-print'; document.body.appendChild(box); }
    box.innerHTML = h.join('\n');
  }

  function inApp() { return /KAKAOTALK|NAVER\(inapp|Instagram|FBAN|FBAV|Line\//i.test(navigator.userAgent || ''); }
  var ICON = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 3v12"/><path d="m7 10 5 5 5-5"/><path d="M5 21h14"/></svg>';

  function start() {
    var st = document.createElement('style'); st.id = 'cocos-print-css'; st.textContent = CSS; document.head.appendChild(st);
    var anchor = document.querySelector('header .jump') || document.querySelector('header h1');
    if (!anchor) return;
    var row = document.createElement('div'); row.id = 'cocos-pdf-row';
    var many = D.passages.length > 1;
    row.innerHTML = (many ? '<button type="button" class="cocos-pdf-btn" data-w="one">' + ICON + '지금 보는 지문 PDF</button>' : '') +
      '<button type="button" class="cocos-pdf-btn" data-w="all">' + ICON + (many ? '전체 지문 PDF (' + D.passages.length + '개)' : 'PDF로 저장') + '</button>' +
      '<small>원지문·해석·어휘 정리·문맥 속 고르기·어휘 추론 변형·정답을 PDF로 저장해 패드에서 필기하며 공부할 수 있어요.</small>';
    anchor.parentNode.insertBefore(row, anchor.nextSibling);
    var last = 'all';
    row.addEventListener('click', function (e) {
      var b = e.target.closest('.cocos-pdf-btn'); if (!b) return;
      var old = document.getElementById('cocos-pdf-tip'); if (old) old.remove();
      if (inApp()) {
        var tip = document.createElement('p'); tip.id = 'cocos-pdf-tip';
        tip.innerHTML = '카카오톡·네이버 앱 안에서는 PDF 저장이 안 될 수 있어요. 화면 오른쪽 위(또는 아래) 메뉴에서 <b>‘다른 브라우저로 열기’</b>를 누른 뒤 다시 눌러 주세요.';
        row.appendChild(tip);
      }
      last = b.getAttribute('data-w'); build(last);
      try { window.print(); } catch (err) {}
    });
    window.addEventListener('beforeprint', function () { if (!document.getElementById('cocos-print')) build(many ? 'one' : 'all'); });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start); else start();
})();
