// 단어게임 블로그 대표 이미지(1080×1080 PNG). 게임 느낌, 학년은 바탕색으로 구분.
// 준비(세션에서 한 번): cd $WORK && npm init -y && npm i @fontsource/jua @fontsource/noto-sans-kr   (Google Fonts는 작업 환경에서 막혀 있음)
// 사용: cd $WORK && NODE_PATH=$(npm root -g) node cover.js cover.json game.html 출력.png
// cover.json: {"theme":"g1","badge":"2026 9월 고1 모의고사","chips":["18~45번 22개 지문","단어 459개"]}
//   theme: 고1 g1(밝은 파랑) · 고2 g2(남색) · 고3 g3(먹색). 학교 내신용도 그 학년 색, badge에 학교·시험 범위.
//   game.html: 만든 단어게임 페이지(로고를 여기서 가져온다)
const fs = require('fs'), path = require('path'), { chromium } = require('playwright');
const [cfgPath, gamePath, outPath] = process.argv.slice(2);
const d = JSON.parse(fs.readFileSync(cfgPath, 'utf8'));
const logo = (fs.readFileSync(gamePath, 'utf8').match(/url\((data:image\/png;base64,[A-Za-z0-9+\/=]+)\)/) || [])[1];
if (!logo) { console.error('로고를 찾지 못했어요'); process.exit(1); }
const THEME = { g1: { bg: '#0A7FBF', sh: '#065A88' }, g2: { bg: '#065A88', sh: '#03344F' }, g3: { bg: '#1B2033', sh: '#000000' } };
const t = THEME[d.theme] || THEME.g1, F = 'file://' + path.resolve('node_modules');
const esc = s => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;');
const html = `<!doctype html><html><head><meta charset="utf-8">
<link rel="stylesheet" href="${F}/@fontsource/jua/index.css">
<link rel="stylesheet" href="${F}/@fontsource/noto-sans-kr/700.css">
<link rel="stylesheet" href="${F}/@fontsource/noto-sans-kr/500.css">
<style>
*{box-sizing:border-box;margin:0}
body{width:1080px;height:1080px;overflow:hidden;font-family:"Noto Sans KR",sans-serif}
.c{position:relative;width:1080px;height:1080px;background:var(--bg,#0A7FBF);overflow:hidden}
.c::before{content:"";position:absolute;inset:0;background-image:radial-gradient(rgba(255,255,255,.13) 3px,transparent 3.5px);background-size:46px 46px}
.sun{position:absolute;right:-150px;top:-150px;width:520px;height:520px;border-radius:50%;background:#FEE101}
.ring{position:absolute;left:-120px;bottom:300px;width:300px;height:300px;border-radius:50%;border:34px solid rgba(255,255,255,.12)}
.logo{position:absolute;left:64px;top:60px;background:#fff;border-radius:999px;padding:16px 30px;box-shadow:0 8px 0 rgba(0,0,0,.12)}
.logo i{display:block;width:230px;height:52px;background:url(${logo}) no-repeat left center/contain}
.badge{position:absolute;left:64px;top:178px;font-family:"Jua";font-size:40px;color:#123;background:#fff;border-radius:16px;padding:6px 22px 4px;transform:rotate(-2deg);box-shadow:0 6px 0 #FEE101}
.kick{position:absolute;left:66px;top:262px;font-family:"Jua";font-size:64px;color:#FEE101;letter-spacing:1px;text-shadow:0 5px 0 rgba(0,0,0,.18)}
.title{position:absolute;left:52px;top:332px;font-family:"Jua";font-size:214px;line-height:1;color:#fff;letter-spacing:-4px;text-shadow:0 12px 0 var(--sh,#065A88), 0 13px 26px rgba(0,0,0,.25)}
.sub{position:absolute;left:68px;top:580px;font-family:"Noto Sans KR";font-weight:700;font-size:36px;color:#fff;display:flex;gap:14px}
.sub span{background:rgba(255,255,255,.16);border:2px solid rgba(255,255,255,.35);border-radius:999px;padding:4px 20px}
/* floating bits */
.pill{position:absolute;font-family:Georgia,serif;font-weight:700;font-size:34px;background:#fff;color:#123;border:4px solid #123;border-radius:999px;padding:6px 26px;box-shadow:0 7px 0 #123}
.p1{right:70px;top:250px;transform:rotate(8deg)}
.p2{right:34px;top:404px;transform:rotate(-6deg);background:#FF8A7A;font-size:30px}
.p3{right:90px;top:520px;transform:rotate(5deg);background:#7FE0C9}
.arrow{position:absolute;right:160px;top:316px;font-family:"Jua";font-size:70px;color:#FEE101;transform:rotate(12deg)}
.combo{position:absolute;right:76px;top:120px;font-family:"Jua";font-size:44px;color:#123;background:#fff;border-radius:18px;padding:8px 22px 4px;transform:rotate(10deg);box-shadow:0 6px 0 #FF6B6B}
.score{position:absolute;right:360px;top:226px;font-family:"Jua";font-size:52px;color:#fff;transform:rotate(-10deg);text-shadow:0 4px 0 var(--sh,#065A88)}
/* game tiles */
.tiles{position:absolute;left:52px;right:52px;bottom:118px;display:grid;grid-template-columns:repeat(5,1fr);gap:16px}
.t{height:236px;border-radius:30px;border:5px solid #123;box-shadow:0 10px 0 #123;display:flex;flex-direction:column;align-items:center;justify-content:space-between;padding:22px 8px 16px;position:relative}
.t b{font-family:"Jua";font-weight:400;font-size:33px;color:#123;line-height:1.1;text-align:center}
.t1{background:#FEE101}.t2{background:#FF8A7A}.t3{background:#fff}.t4{background:#7FE0C9}.t5{background:#B9A8FF}
.cards{position:relative;width:120px;height:110px}
.cards span{position:absolute;width:66px;height:92px;border-radius:12px;border:4px solid #123;background:#0A7FBF}
.cards span::after{content:"";position:absolute;left:50%;top:50%;width:26px;height:26px;margin:-13px 0 0 -13px;border-radius:50%;background:#FEE101}
.cards span:nth-child(1){left:8px;top:12px;transform:rotate(-12deg)}
.cards span:nth-child(2){left:48px;top:4px;transform:rotate(10deg);background:#fff}
.cards span:nth-child(2)::after{display:none}
.cards span:nth-child(2) em{position:absolute;inset:0;display:grid;place-items:center;font-family:"Jua";font-style:normal;font-size:24px;color:#123}
.clock{width:112px;height:112px;border-radius:50%;background:#fff;border:5px solid #123;display:grid;place-items:center;font-family:"Jua";font-size:54px;color:#123}
.drop{display:flex;flex-direction:column;align-items:center;gap:2px}
.drop i{font-family:Georgia,serif;font-style:normal;font-weight:700;font-size:24px;border:4px solid #123;border-radius:999px;padding:2px 14px;background:#E2F3FC;color:#123}
.drop s{font-family:"Jua";text-decoration:none;font-size:40px;color:#0A7FBF;line-height:1}
.drop u{display:block;width:120px;height:12px;border-radius:6px;background:#FEE101;border:3px solid #123}
.lt{display:flex;gap:6px}
.lt i{width:36px;height:46px;border-radius:9px;border:4px solid #123;background:#fff;display:grid;place-items:center;font-family:Georgia,serif;font-style:normal;font-weight:700;font-size:26px;color:#123}
.lt i:nth-child(odd){transform:translateY(-6px)}
.lt{margin-top:10px}
.blk{display:flex;flex-direction:column;gap:9px;width:130px}
.blk i{display:block;height:10px;border-radius:5px;background:#123;opacity:.75}
.blk i.b{display:flex;gap:8px;background:none;opacity:1;height:auto;align-items:center}
.blk i.b em{height:10px;border-radius:5px;background:#123;opacity:.75;flex:1}
.blk i.b span{width:56px;height:26px;border-bottom:5px solid #fff;font-family:"Jua";font-style:normal;color:#fff;font-size:22px;text-align:center;line-height:20px}
/* bottom */
.foot{position:absolute;left:0;right:0;bottom:0;height:86px;background:#123;color:#fff;display:flex;align-items:center;justify-content:space-between;padding:0 64px;font-family:"Noto Sans KR";font-weight:700;font-size:30px}
.foot .st{color:#FEE101;font-size:34px;letter-spacing:4px}
.foot .h{color:#FF8A7A;letter-spacing:4px}
</style></head><body><div class="c" style="--bg:${t.bg};--sh:${t.sh}">
<div class="sun"></div><div class="ring"></div>
<div class="logo"><i></i></div>
<div class="combo">3연속!</div>
<div class="badge">${esc(d.badge)}</div>
<div class="score">+20점</div>
<div class="pill p1">engaging</div>
<div class="arrow">↓</div>
<div class="pill p2">temptation</div>
<div class="pill p3">curious</div>
<div class="kick">놀면서 외우는</div>
<div class="title">단어게임</div>
<div class="sub">${(d.chips||[]).map(c=>`<span>${esc(c)}</span>`).join("")}</div>
<div class="tiles">
 <div class="t t1"><div class="cards"><span></span><span><em>뜻</em></span></div><b>카드<br>짝 맞추기</b></div>
 <div class="t t2"><div class="clock">60</div><b>60초<br>타임어택</b></div>
 <div class="t t3"><div class="drop"><i>mild</i><s>↓</s><u></u></div><b>떨어지는<br>단어</b></div>
 <div class="t t4"><div class="lt"><i>W</i><i>O</i><i>R</i><i>D</i></div><b>철자<br>채우기</b></div>
 <div class="t t5"><div class="blk"><i></i><i class="b"><em></em><span>?</span><em></em></i><i style="width:70%"></i></div><b>지문 속<br>빈칸</b></div>
</div>
<div class="foot"><span>코코스학원 온라인 학습지</span><span><span class="st">★★★</span>  <span class="h">♥♥♥</span></span></div>
</div></body></html>`;
(async () => {
  const tmp = path.resolve('_cover.html'); fs.writeFileSync(tmp, html);
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1080, height: 1080 } });
  await p.goto('file://' + tmp); await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(400);
  const fams = await p.evaluate(() => [...document.fonts].filter(f => f.status === 'loaded').map(f => f.family));
  if (!fams.includes('Jua')) console.error('주의: Jua 글꼴이 안 불러와졌어요 → npm i @fontsource/jua');
  await p.screenshot({ path: outPath }); await b.close(); console.log('saved', outPath);
})();
