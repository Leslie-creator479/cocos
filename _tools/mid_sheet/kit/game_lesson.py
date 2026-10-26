"""중등 교재 한 과의 단어게임 만들기 (syn_lesson.py로 L<과>/src 준비가 끝난 뒤).
사용법: python3 game_lesson.py <동의어·게임 작업 폴더> <학습지 작업 폴더> <과|s1>  → L<과>/game/index.html (중등 테마까지) + 점검
"""
import json, os, re, subprocess, sys
H = os.path.abspath(sys.argv[1]); WS = os.path.abspath(sys.argv[2])  # 동의어·단어게임 작업 폴더, 학습지 작업 폴더
REPO = '/home/claude/cocos'
n = sys.argv[3]; LN = '스페셜 레슨' if n.startswith('s') else f'{n}과'; L = os.path.join(H, f'L{n}')
mf = os.path.join(L, 'meta.json')
meta = json.load(open(mf if os.path.exists(mf) else f'{WS}/L{n}/meta.json', encoding='utf8'))
parts = meta['parts']; BOOK = meta['book']; SLUG = meta['slug']; GR, PUB = BOOK.split(' ', 1); G = os.path.join(L, 'g'); os.makedirs(G, exist_ok=True)
man = [dict(no=f"본문 {p['k']}", topic=p['t'], u=f"../../textbook/{SLUG}/{n}/{p['k']}/", k=f"b{p['k']}", lab=f"{LN} 본문 {p['k']}번",
            sa=f"p{n}-{p['k']}", file=os.path.join(L, 'src', str(p['k']), 'index.html')) for p in parts]
# 대화문(2026-10-26): 같은 과 단어게임에 '대화문 1·2'로 넣는다(주소 textbook/<slug>/<과>/d1/, 동의어 앵커 p<과>-d1)
dlg = meta.get('dialogs', [])
man += [dict(no=f"대화문 {str(p['k'])[1:]}", topic=p['t'], u=f"../../textbook/{SLUG}/{n}/{p['k']}/", k=str(p['k']), lab=f"{LN} 대화문 {str(p['k'])[1:]}",
             sa=f"p{n}-{p['k']}", file=os.path.join(L, 'src', str(p['k']), 'index.html')) for p in dlg]
json.dump(man, open(f'{G}/manifest.json', 'w'), ensure_ascii=False)
subprocess.run(['node', f'{H}/extract.js', f'{G}/manifest.json', f'{G}/data.json'], check=True, stdout=subprocess.DEVNULL)
r = subprocess.run(['python3', '-I', f'{H}/build.py', f'{G}/data.json', f'{G}/game_data.json'], check=True, capture_output=True, text=True).stdout
print(r.strip())
nw = int(re.search(r'단어 (\d+)', r).group(1)); np_ = len(parts)
cfg = {"title": f"[코코스학원] {BOOK} {LN} 단어게임", "key": f"cocos-wordgame-{SLUG}-{n}", "label": f"{BOOK} {LN}",
       "syn": f"../../syn/{SLUG}-{n}/",
       "meta": {"h1": f"{BOOK} {LN} 단어게임", "chips": [f"2022 개정 {GR} · {PUB}", (f"{LN} 본문 {np_}개 · 대화문 {len(dlg)}개 · 단어 {nw}개" if dlg else f"{LN} {np_}개 지문 · 단어 {nw}개"), "게임 5가지"],
                "gist": f"교과서 {LN} 본문 {np_}개" + (f"와 대화문 {len(dlg)}개" if dlg else " 지문") + f"의 단어로 다섯 가지 게임을 해 보세요. 시험 범위에 맞게 {'본문·대화문' if dlg else '본문'}을 골라서 할 수 있어요. 틀린 단어는 ‘오답 다시 풀기’에 모여요.",
                "links": [[f"{BOOK} {LN} 온라인 학습지 목차", f"../../textbook/{SLUG}/{n}/"], [f"{BOOK} {LN} 동의어·반의어", f"../../syn/{SLUG}-{n}/"]],
                "source": f"지문 출처: 2022 개정 {BOOK} {LN} {meta['title']} 교과서 본문" + ("·대화문" if dlg else "")},
       "groups": []}
json.dump(cfg, open(f'{G}/config.json', 'w'), ensure_ascii=False)
out = os.path.join(L, 'game', 'index.html'); os.makedirs(os.path.dirname(out), exist_ok=True)
subprocess.run(['python3', '-I', f'{H}/make_game.py', f'{H}/template_game.html', f'{G}/game_data.json', f'{G}/config.json', out], check=True, stdout=subprocess.DEVNULL)
subprocess.run(['node', '--check', out + '.js'], check=True); os.remove(out + '.js')
subprocess.run(['python3', f'{REPO}/_tools/mid_sheet/theme_page.py', 'game', out], check=True, stdout=subprocess.DEVNULL)
npm = subprocess.run(['npm', 'root', '-g'], capture_output=True, text=True).stdout.strip()
t = subprocess.run(['node', f'{H}/test.js', out, '#b1'], capture_output=True, text=True, env=dict(os.environ, NODE_PATH=npm), timeout=150)
print(t.stdout.strip()); print(t.stderr[-500:]) if t.returncode else None
print('단어', nw)
