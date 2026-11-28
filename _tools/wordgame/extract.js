// 지문별 온라인 학습지에서 문장·단어를 꺼낸다.
// 사용: node extract.js manifest.json data.json
// manifest.json: [{"no":"30","topic":"문단 길이 조절","u":"KPgu...","file":"/…/index.html","sa":"p30"}, …]
//   (선택) "k": 범위 링크 키(없으면 no의 ~를 -로), "lab": 표시 이름(없으면 no+번)
const fs = require('fs'), vm = require('vm');
const man = JSON.parse(fs.readFileSync(process.argv[2], 'utf8')), out = [];
for (const m of man) {
  const s = fs.readFileSync(m.file, 'utf8');
  const a = s.indexOf('/* ==== DATA:START ==== */'), b = s.indexOf('/* ==== DATA:END ==== */');
  if (a < 0 || b < 0) { console.error('DATA 없음:', m.no, m.file); process.exit(1); }
  const ctx = {}; vm.createContext(ctx);
  vm.runInContext(s.slice(a, b).replace(/^\s*\/\*[^]*?\*\/\s*/, '') + ';this.DATA=DATA;', ctx);
  const D = ctx.DATA;
  const o = Object.assign({}, m, { sentences: (D.sentences || []).map(x => ({ en: x.en, ko: x.ko })), vocab: (D.vocab || []).map(v => ({ w: v.w, p: v.p, m: v.m })) });
  delete o.file; out.push(o);
  console.log(m.no, m.topic, '문장', o.sentences.length, '단어', o.vocab.length);
}
fs.writeFileSync(process.argv[3], JSON.stringify(out));
console.log('합계 단어', out.reduce((n, o) => n + o.vocab.length, 0));
