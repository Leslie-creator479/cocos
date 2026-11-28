// 블로그 대표 이미지(1920×1920 PNG)를 만든다. (/home/claude/cocos-study/thumb.js)
// 사용: NODE_PATH=$(npm root -g) node thumb.js items.json 출력폴더
// items.json: [{"file":"2026_09월_고1_모의고사_대표이미지.png","top":"2026년 영어 모의고사","big":"9월","hl":"고1","mark":"9","theme":"g1"}]
//   top: 윗줄, big + hl: 큰 제목(hl은 노란 형광펜), mark: 배경의 큰 글자(1~2자), theme: g1 | g2 | g3, sub: 설명 한 줄(선택)
// 같은 폴더에 template.html(로고)과 fonts/(fontsource)가 있어야 한다.
const fs=require('fs'),path=require('path');const {chromium}=require('playwright');
const HERE=__dirname, F=HERE+'/fonts';
const css=['noto-sans-kr/400.css','noto-sans-kr/500.css','noto-sans-kr/700.css','noto-sans-kr/900.css','gowun-batang/700.css']
  .map(p=>`<link rel="stylesheet" href="file://${F}/${p}">`).join('');
const logo=fs.readFileSync(HERE+'/template.html','utf8').match(/\.logo\{[^}]*url\((data:image\/png;base64,[^)]+)\)/)[1];
const THEME={
 g1:{bg:'#E2F3FC',ink:'#1B2033',accent:'#065A88',sub:'#3B4257',mark:'#0A7FBF',chipBg:'#FFFFFF',chipBd:'#C9E3F2',chipInk:'#065A88',line:'#1B2033',circle:'#FEE101',circleOp:.45,logoBox:false},
 g2:{bg:'#065A88',ink:'#FFFFFF',accent:'#FFE766',sub:'#D6ECF8',mark:'#FFFFFF',chipBg:'rgba(255,255,255,.12)',chipBd:'rgba(255,255,255,.28)',chipInk:'#FFFFFF',line:'#FFFFFF',circle:'#0A7FBF',circleOp:.55,logoBox:true},
 g3:{bg:'#1B2033',ink:'#FFFFFF',accent:'#FFE766',sub:'#C9CDDA',mark:'#FFFFFF',chipBg:'rgba(255,255,255,.10)',chipBd:'rgba(255,255,255,.24)',chipInk:'#FFFFFF',line:'#FFFFFF',circle:'#0A7FBF',circleOp:.5,logoBox:true}};
function page(d){
 const t=THEME[d.theme]||THEME.g1, esc=s=>String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;');
 const chips=['문장별 해석','발음 단어장','마인드맵','변형 문제'].map(c=>`<span style="font-size:24px;font-weight:700;padding:10px 20px;border-radius:999px;background:${t.chipBg};border:1.5px solid ${t.chipBd};color:${t.chipInk}">${c}</span>`).join('');
 const logoEl=t.logoBox?`<span style="background:#FFFFFF;border-radius:14px;padding:12px 18px;display:inline-flex"><img src="${logo}" style="width:190px;height:42px;object-fit:contain"></span>`
  :`<img src="${logo}" style="width:220px;height:48px;object-fit:contain;object-position:left center">`;
 const big=esc(d.big)+(d.hl?` <span style="display:inline-block;line-height:1.1;background:#FFE766;color:#1B2033;padding:0 18px;border-radius:6px">${esc(d.hl)}</span>`:'');
 const n=(d.big+(d.hl||'')).length, size=n<=4?176:n<=6?112:88;
 return `<!doctype html><html lang="ko"><head><meta charset="utf-8">${css}<style>body{margin:0;word-break:keep-all}</style></head><body>
<div id="c" style="width:960px;height:960px;box-sizing:border-box;padding:64px 72px 60px;background:${t.bg};color:${t.ink};position:relative;overflow:hidden;display:flex;flex-direction:column;font-family:'Noto Sans KR',sans-serif">
 <div style="position:absolute;right:-150px;top:-150px;width:440px;height:440px;border-radius:50%;background:${t.circle};opacity:${t.circleOp}"></div>
 <div style="position:absolute;right:30px;bottom:110px;font-family:'Gowun Batang',serif;font-weight:700;font-size:${String(d.mark||'').length>1?380:560}px;line-height:1;color:${t.mark};opacity:.09;letter-spacing:-0.04em">${esc(d.mark||'')}</div>
 <div style="display:flex;align-items:center;justify-content:space-between;position:relative">${logoEl}<span style="font-size:22px;font-weight:700;color:${t.accent};letter-spacing:.02em">학습과 컨설팅을 하나로</span></div>
 <div style="margin-top:72px;position:relative;display:flex;flex-direction:column;gap:6px">
  <span style="align-self:flex-start;font-size:30px;font-weight:900;color:${t.accent};letter-spacing:.04em">${esc(d.top)}</span>
  <div style="font-family:'Gowun Batang',serif;font-weight:700;font-size:${size}px;line-height:1.15;white-space:nowrap;letter-spacing:-0.02em">${big}</div>
  <div style="font-family:'Gowun Batang',serif;font-weight:700;font-size:92px;line-height:1.2;margin-top:6px">온라인 학습지</div>
  <div style="font-size:34px;font-weight:500;margin-top:22px;color:${t.sub}">${esc(d.sub||'지문별 해석부터 변형 문제까지 한 번에')}</div>
 </div>
 <div style="margin-top:auto;display:flex;flex-wrap:wrap;gap:12px;position:relative">${chips}</div>
 <div style="margin-top:28px;display:flex;justify-content:space-between;align-items:center;border-top:2px solid ${t.line};padding-top:20px;position:relative">
  <span style="font-size:24px;font-weight:700">무료 · 회원가입 없이 · 링크만 누르면 바로</span><span style="font-size:22px;color:${t.sub}">코코스학원</span></div>
</div></body></html>`;
}
(async()=>{
 const items=JSON.parse(fs.readFileSync(process.argv[2],'utf8')), out=process.argv[3]; fs.mkdirSync(out,{recursive:true});
 const b=await chromium.launch(), p=await b.newPage({deviceScaleFactor:2,viewport:{width:960,height:960}});
 for(const d of items){
  const tmp=path.join(out,'_thumb.html'); fs.writeFileSync(tmp,page(d));
  await p.goto('file://'+path.resolve(tmp)); await p.evaluate(()=>document.fonts.ready); await p.waitForTimeout(300);
  const fams=await p.evaluate(()=>[...document.fonts].filter(f=>f.status==='loaded').map(f=>f.family));
  if(!fams.some(f=>/Gowun/.test(f))) console.log('경고: 글꼴이 안 불러와짐', d.file);
  await (await p.$('#c')).screenshot({path:path.join(out,d.file)}); fs.unlinkSync(tmp); console.log(path.join(out,d.file));
 }
 await b.close();})();
