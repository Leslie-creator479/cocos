// 사용: node check.js 결과.html  → 추가 규칙이 모두 들어갔는지, 먼저 읽어 보세요 내용이 지문과 맞는지 검사
const fs=require("fs"),vm=require("vm");const s=fs.readFileSync(process.argv[2],"utf8");const err=[];
[...s.matchAll(/<script>([\s\S]*?)<\/script>/g)].forEach((m,i)=>{try{new vm.Script(m[1])}catch(e){err.push("스크립트 문법 오류: "+e.message)}});
if(!s.includes("div.done{display:flex"))err.push("div.done 아님");
if(!s.includes("function tail(){"))err.push("문장 배열 끝 기호 숨김 없음");
if(!s.includes('id="brief"')||!s.includes('href="#brief"'))err.push("먼저 읽어 보세요 칸 없음");
const m=s.match(/DATA:START ==== \*\/([\s\S]*?)\/\* ==== DATA:END/);const c={};vm.runInNewContext(m[1]+";this.D=DATA",c);const D=c.D,B=D.brief,n=D.sentences.length;
if(!B)err.push("DATA.brief 없음");else{
 if(B.flow.length<3||B.flow.length>5)err.push("흐름은 3~5단계");
 const cov=new Set();B.flow.forEach(f=>f.s.forEach(x=>{if(x<1||x>n)err.push("흐름 문장 번호 범위 밖: "+x);cov.add(x)}));
 for(let i=1;i<=n;i++)if(!cov.has(i))err.push("흐름에 빠진 문장: "+i+"번");
 if(B.keys.length!==3)err.push("핵심어는 3개");if(B.tips.length<3||B.tips.length>4)err.push("막히기 쉬운 곳은 3~4개");if(B.ask.length!==2)err.push("질문은 2개");
 const norm=t=>t.replace(/<[^>]+>/g,"").replace(/\s+/g," ").toLowerCase(),text=norm(D.sentences.map(x=>x.en).join(" "));
 B.tips.forEach(t=>[...t[1].matchAll(/<i>(.*?)<\/i>/g)].forEach(q=>{const p=norm(q[1]).replace(/\s*[~…].*$/,"").trim();if(p.length>3&&!text.includes(p))err.push("인용 확인(일반형이면 무시): "+t[0]+" "+q[1])}));}
console.log(err.length?err.join("\n"):"OK");
