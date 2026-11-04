"""코코스 중등 독해 회차 블로그 원고·이미지·태그 만들기 (2026-11-04, 원장님 요청: 회차마다 반복되는 작업이라 도구로).

회차(지문 5편 안팎)를 study/reading-m<학년>-<회>/에 다 올린 뒤 돌린다. 학습지 DATA에서 수준(chips)·핵심 문법(footer)·
맛보기 문제(확인 퀴즈 14번 '질문에 답하기')·정답을 꺼내고, 회차마다 직접 쓰는 부분은 설정 파일에서 읽는다.
네이버 유사문서를 피하려고 본문은 그 회차 지문 내용으로 채우고, 공통 사용법은 안내 글 링크 한 줄만 둔다
(안내 글 원고: tools/blog/mid-public).

    python3 _tools/mid_sheet/reading_blog.py _tools/mid_sheet/reading_blog/<slug>.json [-o 이미지_폴더]
    → tools/blog/<slug>/index.html (원고 페이지: 제목·본문·태그 복사, 링크째 복사)
    → 이미지 폴더(기본 ./blog_<slug>)에 독해<회>회_01_cover.png, 02~ 지문별 카드(1080×1080)
    그다음 build_tools_index.py → seo.py → 커밋·푸시, 이미지는 원장님께 보낸다(저장소에 올리지 않음).

설정 파일(<slug>.json): slug, theme(회차 주제), hook(도입 1~2문장, 회차마다 새로), sources(사실 확인 출처 한 줄),
passages{"1": {...}}. 지문마다 쓰는 칸(없으면 학습지에서 자동으로 채우고 '자동' 표시를 출력하니 꼭 다듬는다):
  emoji, name(표지 동물·소재 이름), tag(표지 작은 글), q(이미지 큰 질문, <br> 가능), did(이미지 '알고 있었나요?' 두 줄),
  ex(이미지 문법 예문, 핵심 부분 <i>…</i>), rule(이미지 문법 한 줄, <b>…</b>), story(본문 소개 2문장),
  gram_title, gram(본문 문법 설명 줄들), words(본문 단어 5개 '낱말(뜻), …'), quiz(맛보기 문제 번호, 기본 14)
"""
import argparse, html, json, os, re, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
KIT = os.path.join(HERE, 'reading_blog')
BASE = 'https://cocosedu.kr/'
TPL = os.path.join(ROOT, 'tools', 'game-blog', '2026-10-g2', 'index.html')  # 원고 페이지 틀(복사 버튼·링크째 복사)
COLORS = [('f-p', 't-pink', 'var(--pink)'), ('f-s', 't-sun', '#E0B400'), ('f-l', 't-lilac', 'var(--lilac)'),
          ('f-b', 't-blue', 'var(--blue)'), ('f-m', 't-mint', 'var(--mint)')]
NUMS = '①②③④⑤'
GUIDE = 'https://blog.naver.com/cocosedu/224465333543'  # 블로그 안내 글(중학 영어 독해·문법 무료 학습지 공개, 원장님 2026-11-05)


def load_data(page):
    """학습지 페이지의 var DATA = {…}; (JS 객체)를 node로 읽는다."""
    s = open(page, encoding='utf8').read()
    i = s.index('var DATA = ')
    j = s.index('\n};', i) + 3
    js = s[i:j] + '\nprocess.stdout.write(JSON.stringify(DATA));'
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf8') as f:
        f.write(js)
    try:
        out = subprocess.run(['node', f.name], capture_output=True, text=True, check=True).stdout
    finally:
        os.remove(f.name)
    return json.loads(out)


def strip(t):
    return re.sub(r'<[^>]+>', '', t or '')


def info(D):
    """chips·footer에서 수준·핵심 문법을 꺼낸다."""
    c0, c1 = D['chips'][0], D['chips'][1]  # '코코스 중등 독해 · 중2 · 표준', '1회 1번 · 설명문 · 154단어 · 기본 어휘 91%'
    grade, stage = [x.strip() for x in c0.split('·')[1:3]]
    parts = [x.strip() for x in c1.split('·')]
    kind, words = parts[1], parts[2]
    m = re.search(r'핵심 문법 ([^)]+)\)', D.get('footer', ''))
    gram = m.group(1).strip() if m else ''
    return dict(grade=grade, stage=stage, kind=kind, words=words, gram=gram, level=f'{grade} · {stage} · {kind} · {words}')


def auto(k, D, inf, P, filled):
    """설정에 없는 칸을 학습지에서 채운다(나중에 다듬도록 filled에 적는다)."""
    def need(key, val):
        if not P.get(key):
            P[key] = val; filled.append(f'{k}번 {key}')
    h1 = D['h1']
    need('name', h1.split(':')[0].strip())
    need('q', h1.split(':', 1)[-1].strip())
    need('tag', inf['kind'])
    need('emoji', '📖')
    one = strip(D['brief']['one'])
    sents = [x.strip() for x in re.split(r'(?<=[.!?요])\s+', one) if x.strip()]
    need('story', sents[:2] or [one])
    need('did', '<br>'.join(sents[:2]) if sents else one)
    tip = next((t for t in D['brief'].get('tips', []) if '핵심 문법' in t[1]), None)
    need('gram_title', inf['gram'])
    need('gram', [strip(tip[1])] if tip else [])
    ex = re.search(r'<i>(.*?)</i>', tip[1]).group(1) if tip and '<i>' in tip[1] else ''
    need('ex', ex)
    need('rule', f'<b>{inf["gram"]}</b>')
    need('words', ', '.join(f'{v["w"]}({re.split(r"[,(]", v["m"])[0].strip()})' for v in D['vocab'][:5]))


def build_body(cfg, items, U):
    body = [["p", f"[대표 이미지: {cfg['_img'](1, 'cover')}]"]]
    body += [["p", h] for h in cfg['hook']]
    body += [["p", cfg.get('intro', '다섯 편 모두 학원이 직접 쓴 글이고, 지문마다 중학교에서 꼭 배우는 문법이 하나씩 들어 있어요. 아래 맛보기 문제를 먼저 풀어 보고, 학습지에서 해석·듣기·퀴즈 15문항까지 이어서 공부해 보세요.').replace('다섯', cfg['_n'])],
             ["p", "학습지 사용법은 지난 글 '중학 영어 독해·문법 무료 학습지 공개'에 정리해 두었어요."],
             ["link", "▶ 학습지 사용법 안내 글", cfg.get('guide', GUIDE)],
             ["link", f"▶ {cfg['_round']}회 목차 바로가기 (지문 {len(items)}편)", U]]
    answers = []
    for n, (k, D, inf, P) in enumerate(items):
        qi = int(P.get('quiz', 14)) - 1
        Q = D['quiz'][qi]
        answers.append(f'{k}번 {NUMS[Q["a"]]}')
        qtext = strip(Q.get('q', '')).replace('Q:', '').strip() or strip(Q.get('p', ''))
        body += [["b", f"■ {k}번 · {strip(D['h1'].split(':', 1)[-1]).strip()}"],
                 ["p", f"[이미지: {cfg['_img'](n + 2, P.get('key', 'p' + k))}]"], ["p", inf['level']]]
        body += [["p", s] for s in P['story']]
        body += [["p", f"📌 오늘의 문법 · {P['gram_title']}"]] + [["p", g] for g in P['gram']]
        body += [["p", "📒 꼭 알아 둘 단어: " + P['words']]]
        body += [["p", f"🧩 맛보기 문제 {k}. {qtext}"]] + [["p", f"{NUMS[i]} {strip(o)}"] for i, o in enumerate(Q['o'])]
        body += [["link", f"▶ {k}번 학습지에서 풀어 보기", f"{U}{k}/"]]
    body += [["b", "■ 맛보기 문제 정답"], ["p", ' · '.join(answers)],
             ["p", "해설은 각 학습지 '확인 퀴즈' 14번에서 볼 수 있어요. 퀴즈 15문항을 모두 풀면 점수도 바로 나와요."], ["br"]]
    if cfg.get('sources'):
        body += [["p", cfg['sources']]]
    body += [["p", cfg.get('outro', '다음 회도 재미있는 주제로 찾아올게요. 링크와 PDF는 친구에게 자유롭게 공유해도 좋아요.')]]
    return body, answers


def page(cfg, items, U, body):
    grams = []
    for _, _, inf, _ in items:
        g = re.split(r'\s*\(|의\s', inf['gram'])[0].strip()  # 'to부정사의 형용사적 쓰임' → 'to부정사'(제목·태그용 짧은 이름)
        if g and g not in grams:
            grams.append(g)
    grade, rnd = items[0][2]['grade'], cfg['_round']
    title = cfg.get('title') or f"{grade} 영어 독해 지문 무료 학습지 {rnd}회 | {cfg['theme']} {len(items)}편 | {'·'.join(grams)} | 코코스학원"
    tags = cfg.get('tags') or ' '.join([f'{grade}영어독해', '중학영어독해', '영어독해지문', f'{grade}영어'] + [g.replace(' ', '') for g in grams] + ['무료학습지'])
    groups = [{'g': f'{rnd}회 바로가기', 'items': [[f"{rnd}회 목차 · {cfg['theme']}", U]] +
               [[f"{k}번 · {strip(D['h1'].split(':', 1)[-1]).strip()}", f'{U}{k}/'] for k, D, _, _ in items]}]
    D = {"url": U, "title": title, "tags": tags, "count": len(items) + 1, "groups": groups, "body": body}
    s = open(TPL, encoding='utf8').read()
    i = s.find('var D=') + 6
    _, end = json.JSONDecoder().raw_decode(s[i:])
    s = s[:i] + json.dumps(D, ensure_ascii=False) + s[i + end:]
    name = f"코코스 중등 독해 {grade} {rnd}회"
    R = [(r'<title>[^<]*</title>', f'<title>{name} 블로그 원고</title>'),
         (r'<h1>[^<]*</h1>', f"<h1>{name} · {html.escape(cfg['theme'])} 블로그 원고</h1>")]
    for a, b in R:
        s = re.sub(a, b, s, count=1)
    for a, b in [("D.count+'개 지문 · 제목·본문·태그'", f"'제목·본문·태그 · 이미지 {len(items) + 1}장'"),
                 ("(D.groups.length>1?'범위 '+D.groups[0].items.length+'개 · ':'')+'지문 '+D.count+'개 · 줄마다 그 범위가 골라진 채로 열려요'", f"'바로가기 '+D.count+'개 · {rnd}회 목차·지문 {len(items)}편'"),
                 ('범위별·지문별 바로가기만', '바로가기만'),
                 ('목록에서 한 줄을 눌러 그 범위가 골라진 채로 단어게임이 열리는지 확인하고 발행해요.', '목록에서 한 줄을 눌러 링크가 제대로 열리는지 확인하고 발행해요.'),
                 ('단어게임 링크 복사', f'{rnd}회 목차 링크 복사'), ("'단어게임 주소를 복사했어요.'", f"'{rnd}회 목차 주소를 복사했어요.'")]:
        assert a in s, '원고 틀이 바뀜: ' + a[:40]
        s = s.replace(a, b)
    return s, title, tags, grams


def images(cfg, items, grams, outdir):
    lib = open(os.path.join(ROOT, 'library', 'index.html'), encoding='utf8').read()
    logo = re.search(r'url\((data:image/png;base64,[^)]+)\)', lib).group(1)
    css = open(os.path.join(KIT, 'cards.css'), encoding='utf8').read().replace('__LOGO__', logo)
    grade, rnd = items[0][2]['grade'], cfg['_round']
    zoo = ''.join(f'<div class="an {COLORS[n % 5][0]}"><div class="e">{P["emoji"]}</div><b>{P["name"]}</b><small>{P["tag"]}</small></div>'
                  for n, (_, _, _, P) in enumerate(items))
    gtags = ''.join(f'<span class="tag {COLORS[n % 5][1]}">{g}</span>' for n, g in enumerate(grams))
    cards = [f'''<section class="card c1" id="c1"><div class="sheet"><div class="logo"></div>
  <p class="kicker">코코스 중등 독해 · {grade} {rnd}회 · 무료 학습지</p>
  <h1><span class="mark">{cfg['theme']}</span><small>{cfg.get('cover_sub', f'영어 독해 지문 {len(items)}편')}</small></h1>
  <div class="zoo" style="grid-template-columns:repeat({len(items)},1fr)">{zoo}</div><div class="gram">{gtags}</div>
  <div class="foot"><span>해석·듣기·단어·퀴즈 15문항·PDF</span><span class="url">cocosedu.kr</span></div></div></section>''']
    for n, (k, D, inf, P) in enumerate(items):
        fc, tc, col = COLORS[n % 5]
        cards.append(f'''<section class="card pc" id="c{n + 2}"><div class="sheet">
  <p class="no2" style="color:{col}">NO. {k} · {grade} {rnd}회 {k}번</p><div class="big">{P['emoji']}</div><h2>{P['q']}</h2>
  <div class="meta"><span class="tag {tc}">{inf['stage']} · {inf['kind']} · {inf['words']}</span><span class="tag t-sun">핵심 문법 · {inf['gram']}</span></div>
  <div class="did {fc}"><p class="h" style="color:{col}">💡 알고 있었나요?</p><p>{P['did']}</p></div>
  <div class="gr">오늘의 문법 · <span class="ex">{P['ex']}</span><br>{P['rule']}</div>
  <div class="foot"><span>코코스 중등 독해 · 무료 공개</span><span class="url">cocosedu.kr</span></div></div></section>''')
    doc = '<!doctype html><html lang="ko"><head><meta charset="utf-8"><style>' + css + '</style></head><body>' + '\n'.join(cards) + '</body></html>'
    os.makedirs(outdir, exist_ok=True)
    hp = os.path.join(outdir, 'cards.html')
    open(hp, 'w', encoding='utf8').write(doc)
    names = [cfg['_img'](1, 'cover')] + [cfg['_img'](n + 2, P.get('key', 'p' + k)) for n, (k, _, _, P) in enumerate(items)]
    js = os.path.join(outdir, 'render.js')
    open(js, 'w', encoding='utf8').write('''const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();
const p=await b.newPage({viewport:{width:1100,height:1100}});await p.goto('file://'+process.argv[2]);await p.waitForTimeout(800);
const names=JSON.parse(process.argv[3]);for(let i=0;i<names.length;i++){const el=await p.$('#c'+(i+1));
const of=await p.evaluate(e=>{const s=e.querySelector('.sheet').getBoundingClientRect(),f=e.querySelector('.foot').getBoundingClientRect();
return [...e.querySelectorAll('.sheet *')].filter(x=>{if(x.closest('.foot')||x.classList.contains('big'))return false;const r=x.getBoundingClientRect();return r.bottom>f.top-6||r.right>s.right-20}).length},el);
await el.screenshot({path:process.argv[4]+'/'+names[i]});console.log(names[i], of?'넘침 '+of:'OK');}await b.close();})();''')
    r = subprocess.run(['node', js, os.path.abspath(hp), json.dumps(names, ensure_ascii=False), os.path.abspath(outdir)],
                       capture_output=True, text=True, cwd=outdir, env=dict(os.environ, NODE_PATH=os.environ.get('NODE_PATH', '')))
    print(r.stdout.strip() or r.stderr.strip())
    return names


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('config'); ap.add_argument('-o', default=None)
    a = ap.parse_args()
    cfg = json.load(open(a.config, encoding='utf8'))
    slug = cfg['slug']
    m = re.match(r'reading-m(\d)-(\d+)$', slug); assert m, 'slug는 reading-m<학년>-<회>'
    cfg['_round'] = int(m.group(2))
    folder = os.path.join(ROOT, 'study', slug)
    ks = sorted((d for d in os.listdir(folder) if d.isdigit()), key=int)
    cfg['_n'] = {1: '한', 2: '두', 3: '세', 4: '네', 5: '다섯', 6: '여섯'}.get(len(ks), str(len(ks)))
    cfg['_img'] = lambda n, key: f"독해{cfg['_round']}회_{n:02d}_{key}.png"
    items, filled = [], []
    for k in ks:
        D = load_data(os.path.join(folder, k, 'index.html'))
        inf = info(D)
        P = dict(cfg.get('passages', {}).get(k, {}))
        auto(k, D, inf, P, filled)
        items.append((k, D, inf, P))
    U = f'{BASE}study/{slug}/'
    body, answers = build_body(cfg, items, U)
    s, title, tags, grams = page(cfg, items, U, body)
    out = os.path.join(ROOT, 'tools', 'blog', slug, 'index.html')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, 'w', encoding='utf8').write(s)
    outdir = a.o or os.path.join(os.getcwd(), f'blog_{slug}')
    names = images(cfg, items, grams, outdir)
    print('원고:', os.path.relpath(out, ROOT), '· 본문', len(body), '줄 · 정답', ' · '.join(answers))
    print('제목:', title); print('태그:', tags); print('이미지:', outdir)
    if filled:
        print('자동으로 채운 칸(설정 파일에 직접 써서 다듬을 것):', ', '.join(filled))


if __name__ == '__main__':
    main()
