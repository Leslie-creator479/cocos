"""중등 교재 한 과의 동의어·반의어 페이지 만들기.
사용법: python3 syn_lesson.py <동의어·게임 작업 폴더> <학습지 작업 폴더> <과|s1>            (words.json 없으면 지문 준비 + passages.txt만)
  L<과>/words.json : [[지문1 어휘들], [지문2 어휘들], ...]  어휘 형식은 words.py의 W(...)와 같은 키(dict)
  결과: L<과>/syn/index.html (중등 테마까지), 검사 결과, 1단계 오답 후보 목록(L<과>/distractors.txt)
"""
import json, os, re, subprocess, sys, shutil
H = os.path.abspath(sys.argv[1]); WS = os.path.abspath(sys.argv[2])  # 동의어·단어게임 작업 폴더, 학습지 작업 폴더
REPO = '/home/claude/cocos'
SK = '/root/.claude/skills/synced/16b95152-03aa-4f07-bb76-3e709241a39d_b34e3ed9-4804-47cd-9cd1-4218d493e9a8/cocos-synonym-antonym/scripts'
n = sys.argv[3]; LN = '스페셜 레슨' if n.startswith('s') else f'{n}과'; L = os.path.join(H, f'L{n}'); os.makedirs(L, exist_ok=True)
mf = os.path.join(L, 'meta.json')
meta = json.load(open(mf if os.path.exists(mf) else f'{WS}/L{n}/meta.json', encoding='utf8'))
parts = meta['parts']; BOOK = meta['book']; SLUG = meta['slug']; GR, PUB = BOOK.split(' ', 1)
srcs = []
for p in parts:
    f = os.path.join(L, 'src', str(p['k']), 'index.html')
    if not os.path.exists(f):
        os.makedirs(os.path.dirname(f), exist_ok=True)
        shutil.copy(f"{WS}/L{n}/out/{p['k']}/index.html", f)   # 녹음까지 만든 학습지(잠그기 전)
    srcs.append(f)
C = os.path.join(L, 'content_syn.json')
subprocess.run(['python3', f'{SK}/from_studio.py'] + srcs + ['-o', C], check=True, stdout=subprocess.DEVNULL)
d = json.load(open(C, encoding='utf8'))
for p, it in zip(parts, d['items']):
    it['no'] = f"{n}-{p['k']}"; it['label'] = f"{LN} 본문 {p['k']}번"; it['type'] = p['label']; it['exam'] = f'2022 개정 {BOOK}'
d['header'] = {'series': f'2022 개정 {BOOK}', 'label': '동의어·반의어', 'title': f'{BOOK} {LN} 동의어·반의어'}
d['range'] = f'{LN} 교과서 본문 {len(parts)}개'
# 에이전트용 지문 파일
with open(os.path.join(L, 'passages.txt'), 'w', encoding='utf8') as fo:
    for p, f in zip(parts, srcs):
        s = open(f, encoding='utf8').read()
        D = json.loads(subprocess.run(['node', '-e', 'const s=require("fs").readFileSync(process.argv[1],"utf8");const m=s.match(/DATA:START ==== \\*\\/([\\s\\S]*?)\\/\\* ==== DATA:END/);const c={};require("vm").runInNewContext(m[1]+";this.D=DATA",c);console.log(JSON.stringify({s:c.D.sentences,v:c.D.vocab,h:c.D.h1}))', f], capture_output=True, text=True).stdout)
        fo.write(f"=== {LN} 본문 {p['k']}번 ({p['label']}) · {D['h']}\n")
        for i, x in enumerate(D['s']): fo.write(f"{i+1}. {x['en']}\n   {x['ko']}\n")
        fo.write('학습지 단어: ' + ', '.join(f"{v['w']}({v['p']})" for v in D['v']) + '\n\n')
W = os.path.join(L, 'words.json')
if not os.path.exists(W):
    json.dump(d, open(C, 'w', encoding='utf8'), ensure_ascii=False, indent=1); print('준비 끝:', L + '/passages.txt'); sys.exit()
words = json.load(open(W, encoding='utf8'))
assert len(words) == len(parts), f'지문 수 {len(parts)}개인데 words.json은 {len(words)}개'
err = []
for it, ws in zip(d['items'], words):
    stars = 0
    for w in ws:
        for k in ('t', 'head', 'pos', 'ko', 'syn', 'ant', 'syn_t', 'ant_t', 'ko_t'):
            if k not in w: err.append(f"{it['label']} {w.get('t')}: {k} 없음")
        if w.get('pos') not in ('a', 'v', 'n', 'r'): err.append(f"{it['label']} {w.get('t')}: pos는 a·v·n·r")
        if (w.get('span') or w.get('t', '')) not in it['passage']: err.append(f"{it['label']} '{w.get('span') or w.get('t')}' 본문에 없음")
        if w.get('ko_t', '') not in it['translation']: err.append(f"{it['label']} {w.get('t')}: ko_t '{w.get('ko_t')}' 해석에 없음")
        if not isinstance(w.get('syn_t'), list) or not w.get('syn_t'): err.append(f"{it['label']} {w.get('t')}: syn_t는 비지 않은 목록")
        if not isinstance(w.get('ant_t'), str) or not w.get('ant_t'): err.append(f"{it['label']} {w.get('t')}: ant_t는 문자열 하나")
        w.setdefault('star', True); w.setdefault('topic', False); stars += bool(w['star'])
    if stars < 5: err.append(f"{it['label']}: ★ {stars}개 (5개 이상 필요)")
    if not 6 <= len(ws) <= 10: err.append(f"{it['label']}: 어휘 {len(ws)}개 (6~10개)")
    it['words'] = ws
if err: print('\n'.join(err)); sys.exit(1)
json.dump(d, open(C, 'w', encoding='utf8'), ensure_ascii=False, indent=1)
out = os.path.join(L, 'syn', 'index.html'); os.makedirs(os.path.dirname(out), exist_ok=True)
r = subprocess.run(['python3', f'{SK}/gen_quiz.py', C, out, '--chip', f'2022 개정 {GR} · {PUB}', '--range', d['range'],
                    '--exam', f'2022 개정 {BOOK}', '--short', BOOK], capture_output=True, text=True)
print('\n'.join(l for l in r.stdout.splitlines() if '세트' not in l)); print(r.stderr[-2000:]) if r.returncode else None
assert r.returncode == 0
subprocess.run(['python3', f'{SK}/finish_page.py', out, C], check=True, stdout=subprocess.DEVNULL)
subprocess.run(['python3', f'{REPO}/_tools/mid_sheet/theme_page.py', 'syn', out], check=True, stdout=subprocess.DEVNULL)
dis = subprocess.run(['node', '-e', 'const s=require("fs").readFileSync(process.argv[1],"utf8");const D=JSON.parse(s.match(/var DATA = (.*);\\n/)[1]);for(const p of D.passages)for(const w of p.words)console.log(p.no,w.h,"| ≒",w.syn.join("/"),"오답:",w.dA.slice(w.ant.length).join(", "),"\\n      | ↔",w.ant.join("/"),"오답:",w.dB.slice(w.syn.length).join(", "))', out], capture_output=True, text=True).stdout
open(os.path.join(L, 'distractors.txt'), 'w', encoding='utf8').write(dis)
t = subprocess.run(['node', f'{SK}/test_quiz.js', out], capture_output=True, text=True, env=dict(os.environ, NODE_PATH=os.path.join(H, 'node_modules')))
print(t.stdout.strip().splitlines()[-1] if t.stdout.strip() else t.stderr[-800:])
print('오답 후보:', os.path.join(L, 'distractors.txt'))
