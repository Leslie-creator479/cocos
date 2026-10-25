/* 코코스 온라인 학습지 '도전 문제' (2026-10-25)
   - 학습지 DATA에 challenge 배열이 있으면 '확인 퀴즈' 바로 아래에 '도전 문제' 칸을 만든다.
   - 문항 형식은 DATA.quiz와 같다: { type, p, q, o:[5개], a:0~4, e, h, en }.
   - assets/print-sheet.js가 이 파일을 함께 불러온다. 학습지에 따로 넣을 줄은 없다.
   - challenge가 없는 학습지에서는 아무것도 하지 않는다. */
(function () {
  'use strict';
  var D = window.DATA;
  if (!D || !D.challenge || !D.challenge.length || window.__cocosChallenge) return;
  var quiz = document.getElementById('quiz');
  if (!quiz || document.getElementById('challenge')) return;
  window.__cocosChallenge = true;
  var NUMS = ['①', '②', '③', '④', '⑤'];
  var C = D.challenge;

  var css = document.createElement('style');
  css.textContent =
    '#challenge .sec-head h2::after{content:"고난도";display:inline-block;margin-left:8px;padding:1px 9px;border-radius:999px;font-size:12px;font-weight:600;vertical-align:middle;letter-spacing:0;background:var(--bad-soft,#FCE8E8);color:var(--bad,#B42318);border:1px solid var(--bad,#B42318)}' +
    '#challenge .ch-note{font-size:14px;line-height:1.6;background:var(--paper,#F6F4EE);border-radius:10px;padding:10px 14px;margin:0 0 14px}' +
    '#challenge .q .type{border-color:var(--bad,#B42318);color:var(--bad,#B42318)}' +
    '#challenge .ch-start{margin-top:4px}';
  document.head.appendChild(css);

  var sec = document.createElement('section');
  sec.id = 'challenge';
  sec.setAttribute('aria-labelledby', 'h-challenge');
  sec.innerHTML =
    '<div class="sec-head"><div><h2 id="h-challenge">도전 문제</h2>' +
    '<p>확인 퀴즈를 다 풀었다면 도전해 보세요. 한 번 고르면 바로 채점돼요.</p></div>' +
    '<div class="score" id="ch-score"></div></div>' +
    '<p class="ch-note">시험에 나오는 고난도 유형 ' + C.length + '문항이에요. 지문을 바꿔 쓰거나 단어를 바꾼 <b>변형 문제</b>가 많고, 보기도 헷갈리게 만들었어요. 틀려도 괜찮아요. 해설을 읽으며 왜 틀렸는지 확인하는 게 진짜 공부예요.</p>' +
    '<div class="qs" id="ch-qs"></div>';
  quiz.parentNode.insertBefore(sec, quiz.nextSibling);

  /* 머리글 바로가기에 '도전 문제' 더하기 */
  var jump = document.querySelector('.jump a[href="#quiz"]');
  if (jump && !document.querySelector('.jump a[href="#challenge"]')) {
    var a = document.createElement('a');
    a.href = '#challenge';
    a.textContent = '도전 문제';
    jump.parentNode.insertBefore(a, jump.nextSibling);
  }

  var qs = document.getElementById('ch-qs'), scoreEl = document.getElementById('ch-score');
  var answered = 0, correct = 0;
  function updateScore() { scoreEl.innerHTML = '<b>' + correct + '</b> / ' + C.length; }
  function render() {
    qs.innerHTML = ''; answered = 0; correct = 0; updateScore();
    C.forEach(function (q, i) {
      var box = document.createElement('div'); box.className = 'q';
      var h = '<div class="num">도전 ' + (i + 1) + '<span class="type">' + q.type + '</span></div><p class="prompt">' + q.p + '</p>';
      if (q.q) h += '<p class="quote">' + q.q + '</p>';
      h += '<div class="opts" role="group" aria-label="도전 문제 ' + (i + 1) + ' 선택지">';
      q.o.forEach(function (t, j) {
        var n = NUMS[j], same = (t === n);
        h += '<button class="opt' + (q.en ? ' en-o' : '') + '" data-j="' + j + '"><span class="n">' + n + '</span>' + (same ? '' : '<span>' + t + '</span>') + '</button>';
      });
      h += '</div>';
      if (q.h) h += '<button class="hint">힌트 보기</button>';
      box.innerHTML = h; qs.appendChild(box);
      if (q.h) {
        var hb = box.querySelector('.hint');
        hb.addEventListener('click', function () { var p = document.createElement('p'); p.className = 'hint-text'; p.innerHTML = '힌트: ' + q.h; hb.replaceWith(p); });
      }
      var opts = [].slice.call(box.querySelectorAll('.opt'));
      opts.forEach(function (b) {
        b.addEventListener('click', function () {
          var j = +b.getAttribute('data-j'), ok = j === q.a;
          opts.forEach(function (x) { x.disabled = true; });
          opts[q.a].classList.add('right'); if (!ok) b.classList.add('wrong');
          var hh = box.querySelector('.hint'); if (hh) hh.remove();
          var fb = document.createElement('div'); fb.className = 'fb';
          fb.innerHTML = (ok ? '<b class="ok">정답이에요!</b> ' : '<b class="no">아쉬워요. 정답은 ' + NUMS[q.a] + '</b> ') + q.e;
          box.appendChild(fb); answered++; if (ok) correct++; updateScore();
          if (answered === C.length) finish();
        });
      });
    });
  }
  function finish() {
    var d = document.createElement('div'); d.className = 'done';
    var r = correct / C.length;
    var msg = r >= 0.9 ? '대단해요! 시험에 나와도 걱정 없겠어요.' : r >= 0.6 ? '잘했어요. 틀린 문항은 해설의 근거 문장을 지문에서 다시 찾아보세요.' : '어려운 문제였어요. 지문과 확인 퀴즈를 한 번 더 보고 다시 도전해 봐요.';
    d.innerHTML = '<span>' + C.length + '문항 중 ' + correct + '문항 정답 · ' + msg + '</span><button class="btn" id="ch-retry">다시 풀기</button>';
    qs.appendChild(d);
    document.getElementById('ch-retry').addEventListener('click', function () { render(); sec.scrollIntoView({ behavior: 'smooth' }); });
  }
  render();
})();
