"""중등 교과서 한 과를 한 번에: 지문 페이지 → 녹음 → 검사 → 과 목차 (→ 저장소에 넣기) (2026-10-24, 중2 동아 2~8과 작업 방식).
사용법 (저장소 폴더에서):
  COCOS_LOCK_PW=… python3 _tools/mid_sheet/build_lesson.py <작업폴더> [--no-audio] [--keep-audio] [--publish]
  <작업폴더>/meta.json:
    {"book": "중2 동아(윤정미)", "slug": "m2dayoon", "lesson": 3, "title": "Necessity Is the Mother of Invention",
     "parts": [{"k": 1, "label": "자전거", "t": "최초의 자전거"}, …]}
    label = chips 둘째 칸 뒤쪽(본문 구분), t = 핵심 개념(<title>·목차에 씀)
    대화문(2026-10-26): "dialogs": [{"k": "d1", "label": "Watch and Check", "t": "인사하고 좋아하는 것 말하기"}, …]
      → data_d1.js, 주소 textbook/<slug>/<과>/d1/, 화면은 make_dlg.py, 검사는 check_dlg.js(대화문형 10문항), 목차에 '대화문' 묶음
  <작업폴더>/data_<k>.js : 지문마다 `var DATA = { … };`
  결과: <작업폴더>/out/<k>/index.html, <작업폴더>/out/toc/index.html, toc.json, audio_*.log(발음 기호 확인용)
  --no-audio   녹음 없이 페이지·검사만(문항 검토 전 미리 보기)
  --keep-audio 이미 만든 out/<k> 페이지의 녹음을 옮겨 붙인다(문항만 고친 뒤 다시 만들 때. sentences·vocab을 고쳤으면 쓰지 않는다)
  --parts d1,d2  이 지문만 다시 만들고 올린다(목차는 모든 지문으로 다시 만든다. 다른 지문의 data_<k>.js도 작업 폴더에 있어야 한다)
  --publish    검사가 모두 OK면 textbook/<slug>/<과>/<k>/·목차를 wrap.py로 넣고, 자료실 카드(add_library)·brand_links까지.
               그다음은 cocos-homepage-publish 7번(pull → seo → lock → 커밋·푸시)
"""
import json, os, re, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
args = sys.argv[1:]
only = None
if '--parts' in args:
    i = args.index('--parts'); only = set(args[i + 1].split(',')); del args[i:i + 2]
flags = {a for a in args if a.startswith('--')}
L = os.path.abspath([a for a in args if not a.startswith('--')][0])
meta = json.load(open(os.path.join(L, 'meta.json'), encoding='utf8'))
book, slug, n, ltitle = meta['book'], meta['slug'], meta['lesson'], meta['title']
# 스페셜 레슨은 lesson을 "s1"처럼 쓴다(주소 textbook/<slug>/s1/, 이름 '스페셜 레슨')
LN = '스페셜 레슨' if str(n).startswith('s') else f'{n}과'
assert re.match(r'^m\d', slug), '중등 교재 약칭은 m+학년으로 시작한다(자료실 중등 분류)'
AU = re.compile(r'/\* ==== AUDIO:START[\s\S]*?SAUDIO:END ==== \*/')
ALL = [dict(p, dlg=False) for p in meta['parts']] + [dict(p, dlg=True) for p in meta.get('dialogs', [])]
def name(p): return f"대화문 {str(p['k'])[1:]}" if p['dlg'] else f"본문 {p['k']}번"
PARTS = [p for p in ALL if only is None or str(p['k']) in only]
pages = []
for p in PARTS:
    k = p['k']; out = os.path.join(L, 'out', str(k), 'index.html')
    old = open(out, encoding='utf8').read() if ('--keep-audio' in flags and os.path.exists(out)) else None
    subprocess.run(['python3', os.path.join(HERE, 'make_mid.py'), os.path.join(L, f'data_{k}.js'),
                    f"[코코스학원] {book} {LN} {name(p)} · {p['t']}", out], check=True, stdout=subprocess.DEVNULL)
    if p['dlg']:
        subprocess.run(['python3', os.path.join(HERE, 'make_dlg.py'), out], check=True, stdout=subprocess.DEVNULL)
    if old:
        new = open(out, encoding='utf8').read()
        open(out, 'w', encoding='utf8').write(AU.sub(lambda m: AU.search(old).group(0), new, count=1))
    pages.append(out)
if '--no-audio' not in flags and '--keep-audio' not in flags:
    with open(os.path.join(L, 'audio_words.log'), 'w') as f:
        for out in pages:
            f.write(subprocess.run(['python3', os.path.join(HERE, 'build_audio.py'), out], check=True, capture_output=True, text=True).stdout)
    r = subprocess.run(['python3', os.path.join(HERE, 'build_saudio.py')] + pages, check=True, capture_output=True, text=True)
    open(os.path.join(L, 'audio_sent.log'), 'w').write(r.stdout)
bad = 0
for p, out in zip(PARTS, pages):
    r = subprocess.run(['node', os.path.join(HERE, 'check_dlg.js' if p['dlg'] else 'check_mid.js'), out], capture_output=True, text=True).stdout.strip()
    ok = r.startswith('OK') and ('--no-audio' in flags or ('발음 없음 0' in r and re.search(r'문장 녹음 (\d+)/\1\b', r)))
    bad += not ok
    print(f"{LN} {p['k']}", r[:170])
items = []
for p in ALL:
    s = open(os.path.join(L, f"data_{p['k']}.js"), encoding='utf8').read()
    h = re.search(r"h1: '([^']*)'", s).group(1); e = re.search(r"enTitle: '([^']*)'", s).group(1)
    items.append({"g": f"{LN} 대화문" if p['dlg'] else f"{LN} {ltitle}", "n": name(p), "t": p['t'], "h": h, "e": e, "u": f"{p['k']}/"})
nb, nd = len(meta['parts']), len(meta.get('dialogs', []))
toc = {"chips": [f"{book} {LN}", f"본문 {nb}개 · 대화문 {nd}개" if nd else f"{nb}개 지문"], "h1": f"{book} {LN} 온라인 학습지",
       "gist": "공부할 지문을 눌러 들어가세요. 지문마다 해석, 문장 듣기, 단어, 마인드맵, 확인 퀴즈, 문장 배열까지 한 곳에서 공부할 수 있어요.",
       "footer": f"지문 출처: 2022 개정 {book} {LN} {ltitle}", "items": items}
json.dump(toc, open(os.path.join(L, 'toc.json'), 'w', encoding='utf8'), ensure_ascii=False, indent=1)
tocout = os.path.join(L, 'out', 'toc', 'index.html')
subprocess.run(['python3', os.path.join(HERE, 'make_toc_mid.py'), os.path.join(L, 'toc.json'),
                f"[코코스학원] {book} {LN} 온라인 학습지 목차", tocout], check=True, stdout=subprocess.DEVNULL)
print(f'{LN} 목차 {len(items)}개 완료' + (f' · 검사 안 된 지문 {bad}개' if bad else ''))
if '--publish' in flags:
    assert not bad and '--no-audio' not in flags, '검사가 모두 OK이고 녹음이 있어야 올린다'
    added = []
    for p, out in zip(PARTS, pages):
        dst = os.path.join(ROOT, f"textbook/{slug}/{n}/{p['k']}/index.html")
        subprocess.run(['python3', os.path.join(ROOT, '_tools/wrap.py'), out, dst, '--noindex'], check=True, stdout=subprocess.DEVNULL); added.append(dst)
    dst = os.path.join(ROOT, f'textbook/{slug}/{n}/index.html')
    subprocess.run(['python3', os.path.join(ROOT, '_tools/wrap.py'), tocout, dst, '--noindex'], check=True, stdout=subprocess.DEVNULL); added.append(dst)
    subprocess.run(['python3', os.path.join(ROOT, '_tools/add_library.py'), 'textbook', f'{LN}', f'textbook/{slug}/{n}',
                    str(nb), '--group', book], check=True, cwd=ROOT, stdout=subprocess.DEVNULL)
    subprocess.run(['python3', os.path.join(ROOT, '_tools/brand_links.py')] + added, check=True, cwd=ROOT, stdout=subprocess.DEVNULL)
    print('저장소에 넣음', len(added), '쪽 → 다음: pull → seo.py → lock → 커밋·푸시')
