// 사용법: node dump.js <학습지 index.html> [--ch]  → 지문 문장·해석·기본 확인 퀴즈를 읽기 좋게 출력
// --ch: 이미 들어 있는 도전 문제도 통째로 출력(품질 기준 샘플 보기: study/2026-10-g1/31, study/2026-10-g2/34)
const s=require("fs").readFileSync(process.argv[2],"utf8");
const m=s.match(/DATA:START ==== \*\/([\s\S]*?)\/\* ==== DATA:END/);const c={};
require("vm").runInNewContext(m[1]+";this.D=DATA",c);const D=c.D;
console.log("제목:",D.h1,"|",D.enTitle||"");console.log("출처:",D.footer||"");
console.log("\n[지문]");D.sentences.forEach((x,i)=>console.log((i+1)+". "+x.en+"\n   "+(x.ko||"")));
if(D.gloss)console.log("\n[주석]",typeof D.gloss=="string"?D.gloss:JSON.stringify(D.gloss));
console.log("\n[기본 확인 퀴즈 — 이것과 겹치지 않게]");(D.quiz||[]).forEach((q,i)=>{console.log("\n"+(i+1)+". ["+q.type+"] "+q.p);if(q.q)console.log("   q: "+q.q.replace(/<[^>]+>/g,"").slice(0,400));q.o.forEach((o,j)=>console.log("   "+(j==q.a?"*":" ")+"①②③④⑤"[j]+" "+String(o).replace(/<[^>]+>/g,"")))});
if(D.challenge){console.log("\n[이미 있는 도전 문제] "+D.challenge.length+"문항");if(process.argv.includes("--ch"))console.log(JSON.stringify(D.challenge,null,1));}
