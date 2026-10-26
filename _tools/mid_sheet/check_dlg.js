// 중등 대화문 학습지 검사 (2026-10-26). 사용: node check_dlg.js 페이지.html
// 확인 퀴즈 10문항(대화문형, 순서·유형 고정), 정답 ①~⑤ 2번씩, 줄마다 sp, 배열·맵·brief·녹음 확인.
const fs=require("fs"),vm=require("vm");const src=fs.readFileSync(process.argv[2],"utf8");const err=[];
[...src.matchAll(/<script>([\s\S]*?)<\/script>/g)].forEach(m=>{try{new vm.Script(m[1])}catch(e){err.push("문법 오류: "+e.message)}});
const m=src.match(/DATA:START ==== \*\/([\s\S]*?)\/\* ==== DATA:END/);const c={};vm.runInNewContext(m[1]+";this.D=DATA",c);const D=c.D,n=D.sentences.length;
const T=["빈칸 · 표현(모두)","빈칸 · 표현(개수)","내용 일치","내용 불일치","어색한 대화","대화 순서","요약문","답할 수 없는 질문","질문에 답하기","배열"];
if(D.quiz.length!==10)err.push("10문항 아님");
D.quiz.forEach((q,i)=>{if(T[i]!==q.type)err.push("문항"+(i+1)+" 유형 "+q.type);if(q.o.length!==5)err.push("문항"+(i+1)+" 선택지");if(!(q.a>=0&&q.a<5))err.push("정답 범위 "+(i+1));if(new Set(q.o).size!==5)err.push("선택지 중복 "+(i+1));});
const cnt={};D.quiz.forEach(q=>cnt[q.a]=(cnt[q.a]||0)+1);[0,1,2,3,4].forEach(k=>{if(cnt[k]!==2)err.push("정답 "+(k+1)+"번 "+(cnt[k]||0)+"회")});
if(D.quiz[1].o.join()!=="1개,2개,3개,4개,5개")err.push("2번(개수) 보기는 1개~5개");
D.sentences.forEach((s,i)=>{if(!["B","G","M","W"].includes(s.sp))err.push("말하는 사람(sp) "+(i+1)+"번");});
[D.map.core,...D.map.left,...D.map.right,D.map.end].forEach(x=>x.s.forEach(k=>{if(k<1||k>n)err.push("맵 번호 "+k)}));
D.order.forEach(o=>{const t=D.sentences[o.s-1];if(!t||o.c.join(" ")!==t.en)err.push("배열 "+o.s+"번 원문과 다름")});
D.sentences.forEach((s,i)=>{const w=s.en.split(/\s+/).length;if(w>4&&!D.order.some(o=>o.s===i+1))err.push("배열 빠짐 "+(i+1)+"번("+w+"단어)")});
const B=D.brief,cov=new Set();B.flow.forEach(f=>f.s.forEach(x=>cov.add(x)));for(let i=1;i<=n;i++)if(!cov.has(i))err.push("흐름 빠짐 "+i);
if(B.keys.length!==3||B.ask.length!==2||B.tips.length<3||B.tips.length>4)err.push("brief 개수");
const norm=t=>t.replace(/<[^>]+>/g,"").replace(/\s+/g," ").toLowerCase(),text=norm(D.sentences.map(x=>x.en).join(" "));
B.tips.forEach(t=>[...t[1].matchAll(/<i>(.*?)<\/i>/g)].forEach(q=>{const p=norm(q[1]).trim();if(p.length>3&&!text.includes(p))err.push("인용 확인 "+t[0]+" "+q[1])}));
D.quiz.forEach((q,i)=>[...(q.e||"").matchAll(/<i>(.*?)<\/i>/g)].forEach(x=>{const p=norm(x[1]).trim();if(p.length>3&&!text.includes(p))err.push("해설 인용 확인 "+(i+1)+": "+x[1])}));
D.vocab.forEach(v=>{if(!["동","명","형","부","숙"].includes(v.p))err.push("품사 "+v.w)});
["제4760호","추가 경비","blog.naver.com/cocosedu","place/38464695","MID THEME:START","data-k=","DLG:START","class=\"spk\""].forEach(k=>{if(!src.includes(k))err.push("빠짐: "+k)});
const am=src.match(/AUDIO:START ==== \*\/([\s\S]*?)\/\* ==== AUDIO:END/);const ax={};vm.runInNewContext(am[1]+";this.A=AUDIO",ax);const miss=D.vocab.filter(v=>!ax.A[v.w]).length;
const sm=src.match(/SAUDIO:START ==== \*\/([\s\S]*?)\/\* ==== SAUDIO:END/);const sx={};vm.runInNewContext(sm[1]+";this.S=SAUDIO",sx);
console.log(err.length?err.join("\n"):"OK","| 정답",JSON.stringify(cnt),"| 단어",D.vocab.length,"| 발음 없음",miss,"| 문장 녹음",sx.S.length+"/"+n);
