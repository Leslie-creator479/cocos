"""학습지에 '도전 문제'(DATA.challenge)를 넣거나 바꾼다 (2026-10-25).

사용법: python3 _tools/add_challenge.py <학습지 index.html> <도전 문제 파일.js>
  도전 문제 파일: var CHALLENGE = [ {type, p, q, o:[5개], a, e, h, en}, … ];  (DATA.quiz와 같은 형식)
  - DATA 맨 끝에 challenge: [...] 키로 넣는다. 이미 있으면 바꾼다(여러 번 돌려도 같다).
  - 화면은 assets/challenge.js, PDF는 assets/print-sheet.js가 그린다(학습지에 따로 넣을 줄 없음).
  - 잠긴 학습지는 먼저 lock.mjs unlock으로 풀고 넣은 뒤 다시 lock 한다.
  - 넣은 뒤 node로 DATA를 다시 읽어 10문항·정답 번호·보기 5개를 검사한다.
"""
import json, re, subprocess, sys

page, src = sys.argv[1], sys.argv[2]
s = open(page, encoding='utf8').read()
if 'DATA:START' not in s:
    sys.exit(f'{page}: DATA 블록이 없음(잠긴 페이지면 먼저 unlock)')
c = open(src, encoding='utf8').read().strip()
m = re.match(r'(?:var|const|let)\s+CHALLENGE\s*=\s*([\s\S]*?);?\s*$', c)
if not m:
    sys.exit(f'{src}: "var CHALLENGE = [ … ];" 형식이 아님')
arr = m.group(1).strip()

END = '\n};\n/* ==== DATA:END ==== */'
if END not in s:
    sys.exit(f'{page}: DATA 끝 표시를 찾지 못함')
head, tail = s.split(END, 1)
head = re.sub(r',\n  challenge: [\s\S]*$', '', head) if '\n  challenge: ' in head else head
head = head.rstrip()
s2 = head + ',\n  challenge: ' + arr + END + tail
open(page, 'w', encoding='utf8').write(s2)

js = r'''
const s=require("fs").readFileSync(process.argv[1],"utf8");
const m=s.match(/DATA:START ==== \*\/([\s\S]*?)\/\* ==== DATA:END/);const c={};
require("vm").runInNewContext(m[1]+";this.D=DATA",c);const C=c.D.challenge||[];const bad=[];const dist=[0,0,0,0,0];
C.forEach((q,i)=>{if(!q.type||!q.p||!q.e)bad.push((i+1)+": type/p/e 없음");if(!Array.isArray(q.o)||q.o.length!==5)bad.push((i+1)+": 보기 5개 아님");
if(!(q.a>=0&&q.a<5))bad.push((i+1)+": 정답 번호 이상");else dist[q.a]++;});
if(!c.D.quiz||!c.D.sentences)bad.push("quiz/sentences가 사라짐");
console.log(JSON.stringify({n:C.length,dist,bad}));
'''
r = subprocess.run(['node', '-e', js, page], capture_output=True, text=True)
if r.returncode:
    open(page, 'w', encoding='utf8').write(s)
    sys.exit(f'{page}: DATA를 읽지 못해 되돌림\n{r.stderr[-800:]}')
info = json.loads(r.stdout)
ok = info['n'] == 10 and not info['bad'] and max(info['dist']) <= 3
print(('OK' if ok else '확인 필요'), page, f"도전 {info['n']}문항 · 정답 분포 {info['dist']}", '; '.join(info['bad']))
