// 온라인 학습지 8단계 검사. 사용: node check.js 경로/index.html
const fs=require("fs"),vm=require("vm");
const src=fs.readFileSync(process.argv[2],"utf8");
const m=src.match(/DATA:START ==== \*\/([\s\S]*?)\/\* ==== DATA:END/);
const ctx={};vm.runInNewContext(m[1]+";this.D=DATA",ctx);const D=ctx.D;
const n=D.sentences.length,err=[];
const T=["주제","요지","내용*","내용*","요약문 완성","빈칸","빈칸","빈칸 · 변형","순서","문장 삽입","어휘 · (A)(B)(C)","어휘 · 밑줄","어휘 · 변형","어법 · (A)(B)(C)","어법 · 밑줄"];
if(D.quiz.length!==15)err.push("퀴즈가 15문항이 아님: "+D.quiz.length);
D.quiz.forEach(q=>{if(q.type==="요약문 완성"&&(!/\(A\)/.test(q.q||"")||!/\(B\)/.test(q.q||"")||!q.o.every(x=>x.includes(" — "))))err.push("요약문 완성 문항 형식 확인");});
D.quiz.forEach((q,i)=>{
  const t=T[i]||"", ok=t.endsWith("*")?q.type.startsWith(t.slice(0,-1)):q.type===t;
  if(!ok)err.push("문항"+(i+1)+" 유형 순서: "+q.type+" (기대: "+t+")");
  if(q.o.length!==5)err.push("문항"+(i+1)+" 선택지 5개 아님");
  if(!(q.a>=0&&q.a<q.o.length))err.push("문항"+(i+1)+" 정답 범위 오류");});
const all=[D.map.core,...D.map.left,...D.map.right,D.map.end];
all.forEach(x=>x.s.forEach(k=>{if(k<1||k>n)err.push(x.t+" 문장번호 "+k+" 범위 밖")}));
const cnt={};D.quiz.forEach(q=>cnt[q.a]=(cnt[q.a]||0)+1);
Object.entries(cnt).forEach(([k,v])=>{if(v!==3)err.push("정답 "+(+k+1)+"번이 "+v+"회 (3회씩이어야 함)")});
const words=D.sentences.map(s=>s.en).join(" ").split(/\s+/).length;
if(!D.vocab||D.vocab.length<10)err.push("단어가 10개 미만");
D.vocab.forEach(v=>{if(!["동","명","형","부","숙"].includes(v.p))err.push("품사 표기 확인: "+v.w)});
["data:image/png;base64,iVBOR","제4760호","추가 경비","blog.naver.com/cocosedu","place/38464695","코코스학원 온라인 학습지","id=\"yr\""].forEach(k=>{if(!src.includes(k))err.push("브랜드·법적 표시 빠짐: "+k)});
if(!/<title>\[코코스학원\] .+번 · .+<\/title>/.test(src))err.push("title 형식이 [코코스학원] … N번 · … 이 아님");
if(!src.includes("var TTS=")||!src.includes("function play(")||src.includes("ttsOK"))err.push("발음 버튼 코드가 템플릿과 다름");
if(!D.order||!D.order.length)err.push("문장 배열(order) 없음");else D.order.forEach(o=>{const t=D.sentences[o.s-1];if(!t)err.push("문장 배열 문장번호 범위 밖: "+o.s);else if(o.c.join(" ")!==t.en)err.push("문장 배열 "+o.s+"번 어구를 이으면 원문과 다름");});
if(!src.includes("function dMove("))err.push("문장 배열 끌어서 옮기기 코드 없음");
if(!src.includes("div.done{display:flex"))err.push("결과 박스 CSS가 div.done이 아님 (문장 배열 번호 원의 숫자가 왼쪽으로 치우침)");
if(!src.includes("id=\"order\"")||src.indexOf("id=\"order\"")<src.indexOf("id=\"quiz\""))err.push("문장 배열 섹션이 없거나 확인 퀴즈 앞에 있음");
const am=src.match(/AUDIO:START ==== \*\/([\s\S]*?)\/\* ==== AUDIO:END/);
if(!am)err.push("AUDIO 블록 없음");else{const ax={};vm.runInNewContext(am[1]+";this.A=AUDIO",ax);D.vocab.forEach(v=>{if(!(ax.A[v.w]||"").startsWith("data:audio/mpeg;base64,"))err.push("발음 녹음 없음: "+v.w)});}
const sm=src.match(/SAUDIO:START ==== \*\/([\s\S]*?)\/\* ==== SAUDIO:END/);
if(!sm)err.push("SAUDIO(문장 녹음) 블록 없음");else{const sx={};vm.runInNewContext(sm[1]+";this.S=SAUDIO",sx);if(sx.S.length!==n)err.push("문장 녹음 수 "+sx.S.length+" ≠ 문장 수 "+n);sx.S.forEach((a,i)=>{if(!String(a).startsWith("data:audio/mpeg;base64,"))err.push("문장 녹음 형식 오류: "+(i+1)+"번")});}
if(!src.includes("id=\"listen\"")||!src.includes("function playOne("))err.push("문장 듣기 코드 없음");
console.log(err.length?err.join("\n"):"OK","| 정답 분포",JSON.stringify(cnt),"| 단어",D.vocab.length+"개 / 지문 "+words+"단어 ("+Math.round(D.vocab.length/words*100)+"%)");
