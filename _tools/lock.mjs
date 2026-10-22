// 교과서·부교재 자료를 학원생 비밀번호로 잠근다(선생님 결정 2026-10-14).
//
// 잠그는 대상: textbook/ 전부, study·syn·game 중 모의고사 회차 이름(<연도>-<월>-g<학년>)이 아닌 것
//            (올림포스 등 부교재, 교과서·학교별 동의어·단어게임). school/ 목차와 tools/는 잠그지 않는다.
// 방식: 페이지 전체 HTML을 AES-256-GCM으로 암호화해 '학원생 전용' 안내 화면 안에 넣는다.
//       비밀번호(PBKDF2)로 만든 열쇠는 모든 페이지가 같아서, 한 번 넣으면 그 기기·브라우저에서는 다른 잠긴 페이지도 바로 열린다.
//       저장소(github.com)에도 암호문만 남는다. 검색 로봇은 안내 화면만 보며, 안내 화면에도 noindex가 있다.
// 주의: 비밀번호는 공개 저장소에 적지 않는다(스킬에만 적는다). 4자리 숫자는 마음먹은 사람이면 풀 수 있는 수준이라
//       '학원생 전용 표시 + 우연한 노출 막기' 용도다.
//
// 사용법 (저장소 폴더에서):
//   COCOS_LOCK_PW=비밀번호 node _tools/lock.mjs lock [파일…]     잠글 대상 중 아직 안 잠근 페이지를 모두(또는 준 파일만) 잠근다(여러 번 돌려도 같다)
//   COCOS_LOCK_PW=비밀번호 node _tools/lock.mjs unlock <파일…>  고치려고 잠긴 파일을 원래 HTML로 되돌린다(고친 뒤 다시 lock)
//   COCOS_LOCK_PW=비밀번호 [COCOS_LOCK_NEWPW=새 비밀번호] node _tools/lock.mjs relock   안내 화면을 고쳤거나 비밀번호를 바꿀 때 전체 다시 잠금
//   node _tools/lock.mjs status                                 잠글 대상·잠긴 수만 보기
// 순서: 페이지를 넣거나 고친 뒤 brand_links.py → seo.py → lock.mjs lock → 올리기.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { fileURLToPath } from 'node:url';

const ROOT = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const SALT = 'cocos-lock-v1';
const ITER = 150000;
const MARK = 'id="cocos-lock"';
const MOCK = /^(\d{4}-\d{2}-g\d|suneung-\d{4}-\d{2})$/;  // 모의고사 회차와 수능(공개 자료, 2026-10-23)
const ACAD = '학원명 코코스학원 · 등록번호 제4760호 · 교습과목 중·고등 영어 · 교습비 중등부 300,000원, 고등부 360,000원 · 추가 경비 없음';
const NOTICE = '이 자료는 코코스학원 학원생의 수업용으로만 제공돼요. 교과서·부교재 지문은 출판사의 저작물이라, 비밀번호나 자료를 학원생이 아닌 사람에게 알려 주거나 복제·게시·배포하면 저작권 침해가 될 수 있어요. 이를 어겨 생기는 문제의 책임은 공유한 사람에게 있어요.';
const SHARE = '이 자료는 코코스학원 학원생 전용이에요. 교과서·부교재 지문은 출판사의 저작물이라 학원 밖으로 공유하거나 배포하면 저작권법 위반이 될 수 있어요.';

function shouldLock(page) {
  const p = page.split('/');
  if (p[0] === 'textbook') return true;
  if (['study', 'syn', 'game'].includes(p[0]) && p[1]) return !MOCK.test(p[1]);
  return false;
}

function* pages(dir = ROOT) {
  for (const e of fs.readdirSync(dir, { withFileTypes: true }).sort((a, b) => a.name.localeCompare(b.name))) {
    if (e.isDirectory()) {
      if (['.git', '_tools', 'node_modules'].includes(e.name)) continue;
      yield* pages(path.join(dir, e.name));
    } else if (e.name === 'index.html' && dir !== ROOT) {
      yield [path.relative(ROOT, dir).split(path.sep).join('/'), path.join(dir, e.name)];
    }
  }
}

const key = pw => crypto.pbkdf2Sync(pw, SALT, ITER, 32, 'sha256');
const esc = s => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');

// 잠근 페이지 안의 '자유롭게 공유' 문구를 학원생 전용 문구로 바꾼다
function restrictWording(html) {
  return html
    .replace(/[^<>\n]{0,80}친구에게도[^<>\n]{0,80}공유해 주세요!?/g, SHARE)
    .replace(/링크는 누구에게나 자유롭게 공유해도 좋아요\.[^<>\n]{0,200}/g, NOTICE);
}

// 네이버 애널리틱스(_tools/analytics.py와 같은 코드): 본문에서 빼고 겉 화면에만 둔다 → 잠금이 풀려도 한 번만 센다 (2026-10-18)
const WCS = '<!-- naver-analytics -->\n<script src="https://wcs.pstatic.net/wcslog.js"></script>\n<script>if(!wcs_add) var wcs_add = {};wcs_add["wa"] = "1c961abfe2e9f50";if(window.wcs) {wcs_do();}</script>\n<!-- /naver-analytics -->\n';
const stripWcs = h => h.replace(/<!-- naver-analytics -->[\s\S]*?<!-- \/naver-analytics -->\n?/g, '');

function shell(page, html, k) {
  html = stripWcs(html);
  const iv = crypto.randomBytes(12);
  const c = crypto.createCipheriv('aes-256-gcm', k, iv);
  const ct = Buffer.concat([c.update(Buffer.from(html, 'utf8')), c.final(), c.getAuthTag()]);
  const title = ((html.match(/<title>([^<]*)<\/title>/) || [])[1] || '코코스학원 온라인 학습지').replace(/^\[코코스학원\]\s*/, '');
  const logo = (html.match(/background:url\((data:image\/png;base64,[A-Za-z0-9+/=]+)\)/) || [])[1] || '';
  const home = path.posix.relative(page, '') || '.';
  const H = home + '/';
  return `<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="robots" content="noindex"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>${esc(title)} · 코코스학원 학원생 전용</title>
<script>try{if(localStorage.getItem('cocos-lock-v1'))document.documentElement.className='auto'}catch(e){}</script>
<style>
:root{--paper:#F5F6FA;--card:#fff;--ink:#1B2033;--muted:#5B6278;--line:#DDE0EA;--accent:#0A7FBF;--accent-ink:#065A88;--accent-soft:#E2F3FC;--bad:#B3261E;color-scheme:light}
*{box-sizing:border-box}
body{margin:0;background:var(--paper);color:var(--ink);font-family:"Noto Sans KR","Apple SD Gothic Neo","Malgun Gothic",system-ui,sans-serif;font-size:16px;line-height:1.7;word-break:keep-all;overflow-wrap:break-word}
.wrap{max-width:640px;margin:0 auto;padding:32px 16px 48px;display:flex;flex-direction:column;gap:18px}
.logo{display:block;width:150px;height:34px;background:url(${logo}) left center/contain no-repeat}
.card{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:26px clamp(18px,4vw,30px);display:flex;flex-direction:column;gap:12px}
.eyebrow{display:inline-flex;align-items:center;gap:6px;align-self:flex-start;font-size:13px;font-weight:700;color:var(--accent-ink);background:var(--accent-soft);border-radius:999px;padding:4px 12px}
h1{font-size:clamp(21px,4.6vw,26px);line-height:1.4;margin:0}
h2{font-size:19px;margin:0}
p{margin:0}
.muted{color:var(--muted);font-size:15px}
form{display:flex;gap:8px;margin-top:4px}
input{flex:1;min-width:0;font:inherit;font-size:18px;letter-spacing:.2em;padding:12px 14px;border:1.5px solid var(--line);border-radius:10px;background:#fff;color:var(--ink)}
input:focus{outline:none;border-color:var(--accent)}
input::placeholder{letter-spacing:normal}
button{font:inherit;font-weight:700;font-size:16px;padding:12px 22px;border:0;border-radius:10px;background:var(--accent);color:#fff;cursor:pointer}
button:disabled{opacity:.6}
.err{color:var(--bad);font-size:14px;min-height:1.4em}
.promo{background:var(--accent-soft);border-color:color-mix(in srgb,var(--accent) 30%,transparent)}
.ctas{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px;margin-top:4px}
.ctas a{display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;min-height:62px;padding:8px 6px;border-radius:10px;border:1px solid var(--accent);background:#fff;color:var(--accent-ink);text-decoration:none;line-height:1.35}
.ctas a.primary{background:var(--accent);color:#fff}
.ctas b{font-size:15px}.ctas small{font-size:12.5px;opacity:.85}
.notice{font-size:13px;color:var(--muted);border-left:3px solid var(--line);padding-left:12px}
.acad{font-size:12px;color:var(--muted)}
.auto main{visibility:hidden}
</style></head><body>
<main class="wrap">
  <a href="${H}" aria-label="코코스학원 홈페이지"><span class="logo" role="img" aria-label="코코스학원"></span></a>
  <section class="card">
    <span class="eyebrow">🔒 학원생 전용 자료</span>
    <h1>${esc(title)}</h1>
    <p class="muted">이 온라인 학습지는 코코스학원 학원생만 볼 수 있어요. 담당 선생님께 받은 비밀번호를 넣어 주세요. 한 번 넣으면 이 기기에서는 다시 묻지 않아요.</p>
    <form id="f" autocomplete="off"><input id="pw" type="password" inputmode="numeric" placeholder="비밀번호" aria-label="비밀번호" required><button id="go" type="submit">열기</button></form>
    <p class="err" id="err" role="alert"></p>
  </section>
  <section class="card promo">
    <h2>코코스학원이 궁금하신가요?</h2>
    <p class="muted">코코스학원은 시험 범위 지문마다 해석·단어·마인드맵·변형 문제까지 담은 온라인 학습지로 수업해요. 학원생이 되면 교과서·부교재 자료까지 모두 볼 수 있어요. 모의고사 학습지는 누구나 자료실에서 볼 수 있어요.</p>
    <div class="ctas">
      <a class="primary" href="tel:031-752-3334"><b>상담 문의</b><small>031-752-3334</small></a>
      <a href="${H}library/"><b>자료실</b><small>모의고사 학습지 보기</small></a>
      <a href="${H}"><b>홈페이지</b><small>학원 소개·설명회</small></a>
      <a href="https://blog.naver.com/cocosedu" target="_blank" rel="noopener"><b>블로그</b><small>수업 소식 보기</small></a>
    </div>
  </section>
  <p class="notice">${NOTICE}</p>
  <p class="acad">${ACAD}</p>
</main>
<script ${MARK} type="application/json">{"v":1,"iv":"${iv.toString('base64')}","ct":"${ct.toString('base64')}"}</script>
<script>
(function(){
  var D=JSON.parse(document.getElementById('cocos-lock').textContent), K='cocos-lock-v1', enc=new TextEncoder();
  function b64(s){var b=atob(s),u=new Uint8Array(b.length);for(var i=0;i<b.length;i++)u[i]=b.charCodeAt(i);return u;}
  function store(raw){try{var s='';raw.forEach(function(x){s+=String.fromCharCode(x)});localStorage.setItem(K,btoa(s));}catch(e){}}
  function saved(){try{var v=localStorage.getItem(K);return v?b64(v):null;}catch(e){return null;}}
  function forget(){try{localStorage.removeItem(K);}catch(e){}}
  function derive(pw){return crypto.subtle.importKey('raw',enc.encode(pw),'PBKDF2',false,['deriveBits']).then(function(b){return crypto.subtle.deriveBits({name:'PBKDF2',salt:enc.encode(K),iterations:${ITER},hash:'SHA-256'},b,256)}).then(function(x){return new Uint8Array(x)});}
  function open(raw){return crypto.subtle.importKey('raw',raw,'AES-GCM',false,['decrypt']).then(function(k){return crypto.subtle.decrypt({name:'AES-GCM',iv:b64(D.iv)},k,b64(D.ct))}).then(function(pt){var h=new TextDecoder().decode(pt);document.open();document.write(h);document.close();});}
  var f=document.getElementById('f'),pw=document.getElementById('pw'),go=document.getElementById('go'),err=document.getElementById('err');
  function show(){document.documentElement.className='';}
  if(!window.crypto||!crypto.subtle){show();err.textContent='이 브라우저에서는 열 수 없어요. 크롬이나 사파리로 열어 주세요.';go.disabled=true;return;}
  function auto(){var s=saved(); if(s){open(s).catch(function(){forget();show();pw.focus();});} else show();}
  if(document.readyState==='complete') auto(); else window.addEventListener('load',auto);
  f.addEventListener('submit',function(e){e.preventDefault();err.textContent='';go.disabled=true;go.textContent='여는 중…';
    derive(pw.value.trim()).then(function(raw){return open(raw).then(function(){store(raw)})}).catch(function(){err.textContent='비밀번호가 맞지 않아요. 다시 확인해 주세요.';go.disabled=false;go.textContent='열기';pw.select();});
  });
})();
</script>
${WCS}</body></html>
`;
}

function unshell(html, k) {
  const m = html.match(/<script id="cocos-lock" type="application\/json">(\{[^<]*\})<\/script>/);
  if (!m) throw new Error('잠긴 파일이 아님');
  const d = JSON.parse(m[1]);
  const buf = Buffer.from(d.ct, 'base64');
  const dc = crypto.createDecipheriv('aes-256-gcm', k, Buffer.from(d.iv, 'base64'));
  dc.setAuthTag(buf.subarray(buf.length - 16));
  return Buffer.concat([dc.update(buf.subarray(0, buf.length - 16)), dc.final()]).toString('utf8');
}

const [cmd, ...files] = process.argv.slice(2);
const pw = process.env.COCOS_LOCK_PW;
if (cmd === 'status') {
  let want = 0, done = 0;
  for (const [page, f] of pages()) if (shouldLock(page)) { want++; if (fs.readFileSync(f, 'utf8').includes(MARK)) done++; }
  console.log(`잠글 대상 ${want}쪽 · 잠김 ${done}쪽 · 안 잠김 ${want - done}쪽`);
} else if (cmd === 'lock' || cmd === 'unlock' || cmd === 'relock') {
  if (!pw) { console.error('COCOS_LOCK_PW 환경 변수로 비밀번호를 주세요(스킬에 적혀 있음).'); process.exit(1); }
  const k = key(pw);
  if (cmd === 'lock') {
    let n = 0, skip = 0;
    const only = new Set(files.map(f => path.resolve(f)));
    for (const [page, f] of pages()) {
      if (!shouldLock(page)) continue;
      if (only.size && !only.has(path.resolve(f))) continue;
      const s = fs.readFileSync(f, 'utf8');
      if (s.includes(MARK)) { skip++; continue; }
      fs.writeFileSync(f, shell(page, restrictWording(s), k)); n++;
    }
    console.log(`잠금: 이번에 ${n}쪽 잠금, 이미 잠긴 ${skip}쪽`);
  } else if (cmd === 'relock') {
    // 안내 화면을 고쳤거나(학원 표시 등) 비밀번호를 바꿀 때: 잠긴 페이지를 풀어서 새 화면·새 비밀번호로 다시 잠근다
    const nk = process.env.COCOS_LOCK_NEWPW ? key(process.env.COCOS_LOCK_NEWPW) : k;
    let n = 0;
    for (const [page, f] of pages()) {
      const s = fs.readFileSync(f, 'utf8');
      if (!s.includes(MARK)) continue;
      fs.writeFileSync(f, shell(page, unshell(s, k), nk)); n++;
    }
    console.log(`다시 잠금: ${n}쪽` + (process.env.COCOS_LOCK_NEWPW ? ' (새 비밀번호)' : ''));
  } else {
    for (const f of files) {
      const s = fs.readFileSync(f, 'utf8');
      if (!s.includes(MARK)) { console.log(f, '잠기지 않은 파일(그대로)'); continue; }
      fs.writeFileSync(f, unshell(s, k)); console.log(f, '풀림');
    }
  }
} else {
  console.log('사용법: node _tools/lock.mjs status | lock | unlock <파일…>  (lock·unlock은 COCOS_LOCK_PW 필요)');
}
