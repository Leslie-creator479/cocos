// 학교별 내신 분석 블로그 이미지 6장(대표 1920×1920 + 도표 5장 가로 1920)을 data.json으로 만든다.
// 00 대표 · 01 시험 구성과 출처 · 02 문제 유형별 배점 · 03 시험 범위 지문 출제 지도 · 04 지문·어휘 변형 · 05 다음 시험 대비
// '시험 분석' 디자인: 모눈종이 바탕 · 시험지 머리 칸 · 빨간 채점 펜 · Black Han Sans + IBM Plex Sans KR + Nanum Pen Script.
// 학습지 대표 이미지(고운바탕·Noto Sans KR·형광펜)와 섞이지 않게 이 틀만 쓴다.
// 사용: NODE_PATH=$(npm root -g) node exam_images.js data.json 출력폴더
// 같은 폴더에 fonts/(fontsource: black-han-sans, ibm-plex-sans-kr, nanum-pen-script)와 logo.txt(로고 data URI)가 있어야 한다.
// 제목 문자열 안의 {{…}}는 빨간 펜 색으로 바뀐다.
const fs = require('fs'), path = require('path'); const { chromium } = require('playwright');
const HERE = __dirname, F = HERE + '/fonts';
const D = JSON.parse(fs.readFileSync(process.argv[2], 'utf8')), OUT = process.argv[3] || 'img';
const css = ['black-han-sans/400.css', 'ibm-plex-sans-kr/400.css', 'ibm-plex-sans-kr/500.css', 'ibm-plex-sans-kr/600.css', 'ibm-plex-sans-kr/700.css', 'nanum-pen-script/400.css']
  .map(p => `<link rel="stylesheet" href="file://${F}/${p}">`).join('');
const logo = fs.readFileSync(HERE + '/logo.txt', 'utf8').trim();
const C = { ink: '#1A2238', navy: '#12355B', navy2: '#4F7CAC', red: '#D33A2C', paper: '#FBFAF5', grid: 'rgba(18,53,91,.075)', muted: '#5E6577', line: '#CBD2DE', grey: '#B7BDC9' };
const HEAD = "'Black Han Sans',sans-serif", BODY = "'IBM Plex Sans KR',sans-serif", PEN = "'Nanum Pen Script',cursive";
const R = s => String(s).replace(/\{\{(.+?)\}\}/g, `<span style="color:${C.red}">$1</span>`);
const page = inner => `<!doctype html><html lang="ko"><head><meta charset="utf-8">${css}<style>
body{margin:0;word-break:keep-all;font-family:${BODY};color:${C.ink}}
.h{font-family:${HEAD};font-weight:400;letter-spacing:-0.01em}
.pen{font-family:${PEN};color:${C.red}}
.paper{background-color:${C.paper};background-image:linear-gradient(${C.grid} 1px,transparent 1px),linear-gradient(90deg,${C.grid} 1px,transparent 1px);background-size:24px 24px}
</style></head><body>${inner}</body></html>`;

function thumb(t) {
  const cell = (x, f, last) => `<div style="flex:${f};padding:14px 18px;${last ? '' : `border-right:2.5px solid ${C.ink};`}${f < 1.5 ? 'text-align:center' : ''}">${x}</div>`;
  const stats = t.stats.map(([a, b]) => `<div style="flex:1;background:#fff;border:2.5px solid ${C.ink};padding:14px 16px;display:flex;align-items:baseline;gap:6px;justify-content:center"><span class="h" style="font-size:46px;color:${C.navy}">${a}</span><span style="font-size:22px;font-weight:700">${b}</span></div>`).join('');
  return page(`<div id="c" class="paper" style="width:960px;height:960px;box-sizing:border-box;padding:56px 64px 0;position:relative;overflow:hidden;display:flex;flex-direction:column">
  <div style="display:flex;justify-content:space-between;align-items:center">
    <span style="font-size:22px;font-weight:700;letter-spacing:.32em;color:${C.red}">EXAM ANALYSIS REPORT</span>
    <span style="font-size:20px;font-weight:600;color:${C.muted}">${t.report_no}</span></div>
  <div style="margin-top:22px;display:flex;border:2.5px solid ${C.ink};background:#fff;font-weight:700;font-size:23px">${cell(t.exam, 1.7)}${cell(t.school, 1)}${cell(t.grade, .8, 1)}</div>
  <div style="margin-top:64px;position:relative">
    <div class="h" style="font-size:128px;line-height:1.08">${t.line1} <span style="position:relative;display:inline-block;color:${C.navy}">${t.circled}<svg width="250" height="190" viewBox="0 0 250 190" style="position:absolute;left:-38px;top:-24px;overflow:visible"><path d="M40 40 C 90 0, 220 6, 236 70 C 252 140, 150 186, 80 170 C 20 156, 2 100, 30 58 C 44 38, 70 26, 96 22" fill="none" stroke="${C.red}" stroke-width="7" stroke-linecap="round" opacity=".9"/></svg></span></div>
    <div class="h" style="font-size:128px;line-height:1.08;margin-top:18px">${t.line2} <span style="position:relative;display:inline-block">${t.underlined}<svg width="220" height="26" viewBox="0 0 220 26" style="position:absolute;left:-6px;bottom:6px"><path d="M6 16 C 60 4, 130 24, 214 8" fill="none" stroke="${C.red}" stroke-width="8" stroke-linecap="round" opacity=".9"/></svg></span></div>
    <div class="pen" style="position:absolute;right:-4px;bottom:6px;font-size:54px;line-height:1;text-align:center;transform:rotate(-8deg)">${t.pen_note}</div>
  </div>
  <div style="margin-top:64px;font-size:30px;font-weight:600;color:${C.muted}">${t.sub}</div>
  <div style="margin-top:32px;display:flex;gap:12px">${stats}</div>
  <div style="margin-top:auto;margin-left:-64px;margin-right:-64px;background:${C.navy};color:#fff;padding:24px 64px;display:flex;justify-content:space-between;align-items:center">
    <span style="background:#fff;border-radius:10px;padding:9px 14px;display:inline-flex"><img src="${logo}" style="width:150px;height:33px;object-fit:contain"></span>
    <span style="font-size:22px;font-weight:600">${t.footer}</span></div>
</div>`);
}
function card(no, kicker, title, body) {
  return page(`<div id="c" class="paper" style="width:960px;box-sizing:border-box;padding:0 56px 36px;display:flex;flex-direction:column;gap:26px">
 <div style="margin:0 -56px;background:${C.navy};color:#fff;padding:18px 56px;display:flex;justify-content:space-between;align-items:center">
  <span style="font-size:17px;font-weight:700;letter-spacing:.28em">EXAM ANALYSIS</span><span style="font-size:17px;font-weight:600">${D.header_right}</span></div>
 <div style="display:flex;gap:20px;align-items:flex-start;margin-top:8px">
  <div style="flex:none;width:76px;height:76px;border:4px solid ${C.red};border-radius:50%;display:flex;align-items:center;justify-content:center;transform:rotate(-8deg)"><span class="h" style="font-size:34px;color:${C.red}">${no}</span></div>
  <div style="display:flex;flex-direction:column;gap:6px;padding-top:2px"><span style="font-size:20px;font-weight:700;color:${C.red};letter-spacing:.04em">${kicker}</span>
   <div class="h" style="font-size:44px;line-height:1.25">${R(title)}</div></div></div>
 ${body}
 <div style="display:flex;justify-content:space-between;align-items:center;border-top:2px solid ${C.ink};padding-top:14px;font-size:15px;color:${C.muted}">
  <img src="${logo}" style="width:110px;height:24px;object-fit:contain;object-position:left center"><span>코코스학원 분석 자료 · 무단 복제·배포 금지 · cocosedu.kr</span></div>
</div>`);
}
const box = (inner, extra = '') => `<div style="background:#fff;border:2px solid ${C.ink};box-shadow:6px 6px 0 rgba(18,53,91,.12);padding:26px 28px;${extra}">${inner}</div>`;
const h3 = t => `<div style="font-size:23px;font-weight:700;margin-bottom:16px;padding-bottom:10px;border-bottom:1.5px dashed ${C.line}">${t}</div>`;
const note = t => `<div style="margin-top:14px;font-size:19px;color:${C.muted}">${t}</div>`;

function img1(s) {   // 시험 구성 · 출처
  const tiles = s.tiles.map(([a, b, c], i, all) => { const last = i === all.length - 1;
    return `<div style="flex:1;background:${last ? C.navy : '#fff'};color:${last ? '#fff' : C.ink};border:2px solid ${C.ink};box-shadow:6px 6px 0 rgba(18,53,91,.12);padding:20px 24px">
     <div style="font-size:19px;font-weight:600;opacity:.8">${a}</div><div class="h" style="font-size:46px;margin-top:4px">${b}</div><div style="font-size:20px;font-weight:600">${c}</div></div>`; }).join('');
  const COL = [C.navy, C.navy2, C.red, '#8A6D3B', '#2E7D6B'];
  const src = s.sources.map((r, i) => [...r, r[2] > 0 ? COL[i % COL.length] : C.grey]);
  const total = src.reduce((a, r) => a + r[2], 0);
  const bar = src.filter(r => r[2] > 0).map(([n, k, p, col]) => `<div style="width:${p / total * 100}%;background:${col};color:#fff;display:flex;align-items:center;justify-content:center;font-size:22px;font-weight:700;white-space:nowrap">${p / total >= .2 ? p + '점' : ''}</div>`).join('');
  const rows = src.map(([n, k, p, col]) => `<div style="display:flex;align-items:center;gap:14px;font-size:21px;padding:9px 0;border-bottom:1px solid ${C.line}">
     <span style="width:18px;height:18px;background:${col}"></span><span style="flex:1;font-weight:600">${n}</span><span style="width:110px;text-align:right;color:${C.muted}">${k}문항</span><span style="width:110px;text-align:right;font-weight:700">${p}점</span></div>`).join('');
  const mx = Math.max(...s.lessons.map(r => r[1]));
  const les = s.lessons.map(([n, p]) => `<div style="display:flex;align-items:center;gap:14px;font-size:20px;margin:8px 0">
     <span style="width:200px;font-weight:600">${n}</span><span style="height:24px;width:${p / mx * 440}px;background:${p === mx ? C.red : C.grey}"></span><span style="font-weight:700">${(+p).toFixed(1)}점</span></div>`).join('');
  return card('01', '시험 구성과 출처', s.title, `<div style="display:flex;gap:16px">${tiles}</div>` +
    box(h3('출처별 배점 (100점 기준)') + `<div style="display:flex;height:60px;border:2px solid ${C.ink}">${bar}</div><div style="margin-top:12px">${rows}</div>${note(s.note)}`) +
    (s.lessons.length ? box(h3(s.lessons_title || '교과서 과별 배점') + les) : ''));
}
function img2(s) {   // 유형별 배점
  const max = Math.max(...s.mc.map(r => r[2]), ...s.sv.map(r => r[2]));
  const row = (n, k, p, col) => `<div style="display:flex;align-items:center;gap:16px;margin:11px 0;font-size:20px">
     <span style="flex:none;width:330px;text-align:right;font-weight:600;white-space:nowrap">${n}</span><span style="flex:none;height:30px;width:${p / max * 240}px;background:${col}"></span>
     <span style="font-weight:700;white-space:nowrap">${(+p).toFixed(1)}점 <span style="font-weight:500;color:${C.muted}">(${k}문항)</span></span></div>`;
  return card('02', '문제 유형별 배점', s.title,
    box(h3(s.mc_title) + s.mc.map(([n, k, p, h]) => row(n, k, p, h ? C.red : C.grey)).join('') + note(s.mc_note)) +
    box(h3(s.sv_title) + s.sv.map(([n, k, p]) => row(n, k, p, C.navy)).join('') + note(s.sv_note)));
}
function img4(s, no = '04') {   // 변형 분석
  const COL = [C.red, C.navy, C.navy2];
  const prog = ([n, a, b], i) => `<div style="flex:1"><div style="display:flex;justify-content:space-between;font-size:21px;font-weight:700"><span>${n}</span><span>${a} / ${b}지문</span></div>
    <div style="height:22px;border:2px solid ${C.ink};margin-top:10px;background:#fff"><div style="height:100%;width:${a / b * 100}%;background:${COL[i]}"></div></div>
    <div class="h" style="font-size:30px;color:${COL[i]};margin-top:8px">${Math.round(a / b * 100)}% 변형</div></div>`;
  const rows = s.techniques.map(([a, b], i) => `<div style="display:flex;gap:14px;align-items:baseline;padding:12px 0;border-bottom:1px solid ${C.line};font-size:20px">
    <span class="h" style="color:${C.red};width:30px;font-size:24px">${i + 1}</span><span style="flex:1;font-weight:600">${a}</span><span style="color:${C.muted};text-align:right">${b}</span></div>`).join('');
  return card(no, '지문 · 어휘 변형', s.title, box(`<div style="display:flex;gap:40px">${s.progress.map(prog).join('')}</div>${note(s.note)}`) + box(h3(`변형 방식 ${s.techniques.length}가지`) + rows));
}
function img5(s, no = '05') {   // 대비 체크리스트
  const cards = s.points.map(([a, b]) => `<div style="background:#fff;border:2px solid ${C.ink};box-shadow:6px 6px 0 rgba(18,53,91,.12);padding:22px 24px;display:flex;flex-direction:column;gap:10px">
    <div style="display:flex;align-items:center;gap:12px"><span style="flex:none;width:30px;height:30px;border:2.5px solid ${C.ink};display:inline-flex;align-items:center;justify-content:center"><svg width="22" height="22" viewBox="0 0 22 22"><path d="M3 12 L9 18 L20 4" fill="none" stroke="${C.red}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/></svg></span><span class="h" style="font-size:26px">${a}</span></div>
    <div style="font-size:19px;line-height:1.6;color:${C.muted}">${b}</div></div>`).join('');
  return card(no, s.kicker || '다음 시험 대비 체크리스트', s.title, `<div style="display:grid;grid-template-columns:1fr 1fr;gap:18px">${cards}</div>`);
}

function imgMap(s, no) {   // 시험 범위 지문 출제 지도 (원래 유형 정보 없이 출처 대조만으로 만든다)
  const ST = { keep: [C.navy, '#fff', C.ink, ''], change: [C.red, '#FDEDEA', C.ink, '변형'], none: [C.grey, 'transparent', C.grey, ''] };
  const cell = ([code, ex, topic, st]) => { const [bd, bg, fg, tag] = ST[st];
    return `<div style="flex:1 1 0;min-width:0;display:flex"><div style="flex:1;min-width:0;border:2px ${st === 'none' ? 'dashed' : 'solid'} ${bd};background:${bg};padding:10px 12px;display:flex;flex-direction:column;gap:4px">
      <div style="display:flex;justify-content:space-between;align-items:baseline;white-space:nowrap"><span style="font-size:15px;font-weight:600;color:${C.muted}">${code}</span>${tag ? `<span style="font-size:14px;font-weight:700;color:#fff;background:${C.red};padding:1px 7px">${tag}</span>` : ''}</div>
      <div class="h" style="font-size:${st === 'none' ? 22 : 27}px;color:${st === 'none' ? C.grey : (st === 'change' ? C.red : C.navy)};white-space:nowrap">${st === 'none' ? '미출제' : ex}</div>
      <div style="font-size:15px;line-height:1.35;color:${fg};overflow:hidden;text-overflow:ellipsis;white-space:nowrap">${topic}</div></div></div>`; };
  const n = Math.max(...s.rows.map(r => r[1].length));
  const rows = s.rows.map(([head, cells]) => `<div style="display:flex;align-items:stretch;gap:10px;margin:9px 0">
     <div style="flex:none;width:92px;display:flex;align-items:center;font-size:20px;font-weight:700">${head}</div>
     ${cells.map(cell).join('')}${'<div style="flex:1 1 0"></div>'.repeat(n - cells.length)}</div>`).join('');
  const key = (bd, bg, dash, t) => `<span style="display:inline-flex;align-items:center;gap:8px;margin-right:22px"><span style="width:22px;height:16px;border:2px ${dash ? 'dashed' : 'solid'} ${bd};background:${bg}"></span>${t}</span>`;
  return card(no, s.kicker || '시험 범위 지문 출제 지도', s.title,
    box(rows + `<div style="margin-top:16px;font-size:17px;color:${C.muted}">${key(C.navy, '#fff', 0, '본문 그대로 출제')}${key(C.red, '#FDEDEA', 0, '본문 변형 출제')}${key(C.grey, 'transparent', 1, '미출제')}</div>`) +
    (s.callout ? `<div style="border-left:6px solid ${C.red};background:#fff;padding:20px 24px;font-size:21px;line-height:1.7">${s.callout}</div>` : ''));
}

// 03 = 시험 범위 지문 출제 지도(map). data.json에 map이 없으면 빼고 뒤 두 장을 03·04로 당긴다.
const seq = [['문제유형별_배점', n => img2(D.types)]];
if (D.map) seq.push(['지문_출제지도', n => imgMap(D.map, n)]);
seq.push(['지문변형_분석', n => img4(D.variation, n)], ['다음시험_대비', n => img5(D.final, n)]);
const items = [['00_대표이미지', thumb(D.thumb)], ['01_시험구성_출처비율', img1(D.source)],
  ...seq.map(([name, f], i) => { const no = String(i + 2).padStart(2, '0'); return [no + '_' + name, f(no)]; })];
(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  const b = await chromium.launch(), p = await b.newPage({ deviceScaleFactor: 2, viewport: { width: 960, height: 960 } });
  for (const [name, html] of items) {
    const tmp = path.join(OUT, '_t.html'); fs.writeFileSync(tmp, html);
    await p.goto('file://' + path.resolve(tmp)); await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(400);
    const fams = await p.evaluate(() => [...document.fonts].filter(f => f.status === 'loaded').map(f => f.family));
    if (!fams.some(f => /Black Han/.test(f)) || !fams.some(f => /IBM/.test(f))) console.log('경고: 글꼴이 안 불러와짐', name);
    const file = path.join(OUT, D.file_prefix + name + '.png');
    await (await p.$('#c')).screenshot({ path: file }); fs.unlinkSync(tmp); console.log(file);
  }
  await b.close();
})();
