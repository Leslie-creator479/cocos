// 게시 전 한 번 점검: 폰 너비(400px)에서 오류·가로 넘침, 범위 링크, 게임 다섯 개 실행, 1단계 링크.
// 사용: NODE_PATH=$(npm root -g) node test.js game.html "#첫키" "#18-26"
const fs = require('fs'), { chromium } = require('playwright');
(async () => {
  const [file, ...hashes] = process.argv.slice(2), errs = [];
  const doc = '<!doctype html><html><head><meta charset=utf8></head><body>' + fs.readFileSync(file, 'utf8') + '</body></html>';
  const b = await chromium.launch(), p = await b.newPage({ viewport: { width: 400, height: 900 } });
  p.on('pageerror', e => errs.push(e.message)); await p.setContent(doc);
  console.log('처음:', await p.$eval('.rsum', e => e.textContent), '| 카드 잠김:', await p.$$eval('.gcard', es => es.every(e => e.disabled)));
  await p.click('.rbtn >> text=전체'); console.log('전체:', await p.$eval('.rsum', e => e.textContent));
  await p.click('.gcard.study'); console.log('링크 예:', await p.$$eval('.vlinks a', es => es.slice(0, 2).map(e => e.textContent + ' ' + e.href).join(' | ')));
  for (let i = 0; i < 5; i++) {
    await p.click('#back'); await (await p.$$('.gcard:not(.study)'))[i].click(); await p.click('.btn.primary.big'); await p.waitForTimeout(500);
    for (let k = 0; k < 3; k++) { const el = await p.$('.opt:not([disabled]), .mcard:not([disabled]):not(.up), .tile:not([disabled])'); if (el) await el.click().catch(() => {}); await p.waitForTimeout(250); const nb = await p.$('.fb .btn'); if (nb) await nb.click(); }
    if (await p.evaluate(() => document.documentElement.scrollWidth > innerWidth)) errs.push('가로 넘침: 게임 ' + (i + 1));
  }
  await p.click('#back'); await (await p.$$('.gcard:not(.study)'))[4].click(); await p.click('.btn.primary.big');
  for (let k = 0; k < 4; k++) { console.log('빈칸:', (await p.$$eval('.opt', es => es.map(e => e.textContent))).join(' / ')); await (await p.$('.opt')).click(); await p.waitForTimeout(150); const nb = await p.$('.fb .btn'); if (nb) await nb.click(); else await p.waitForTimeout(1200); }
  for (const h of hashes) { const q = await b.newPage(); q.on('pageerror', e => errs.push(e.message)); await q.goto('data:text/html;charset=utf-8,' + encodeURIComponent(doc) + h); console.log(h, '→', await q.$eval('.rsum', e => e.textContent)); await q.close(); }
  console.log(errs.join('\n') || '오류 없음'); await b.close();
})();
