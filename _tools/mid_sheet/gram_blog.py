"""코코스 중등 문법 블로그 원고·이미지·태그 만들기 (2026-11-06, 원장님: 독해는 월요일, 문법은 목요일 블로그).

문법 페이지(study/grammar-m<학년>-<회>/)를 올린 뒤 돌린다. 페이지 DATA에서 먼저 풀어 보기(O/X)·꼴·쓰임·구별표·고쳐 쓰기·
감점 체크를 꺼내 본문과 이미지를 만들고, 회차마다 직접 쓰는 부분(도입·표지 문구)은 설정 파일에서 읽는다.
공통 사용법은 안내 글 링크 한 줄만(네이버 유사문서 피하기), 독해 짝 지문 링크도 함께.

    python3 _tools/mid_sheet/gram_blog.py _tools/mid_sheet/gram_blog/<slug>.json [-o 이미지_폴더]
    → tools/blog/<slug>/index.html (원고 페이지: 제목·본문·태그 복사, 링크째 복사)
    → 이미지 폴더에 문법<회>회_01_cover.png · 02_ox · 03_uses · 04_compare · 05_check (1080×1080)
    그다음 build_tools_index.py → seo.py → 커밋·푸시, 이미지는 원장님께 보낸다(저장소에 올리지 않음).

설정 파일: slug, grammar(문법 이름, 예 '현재완료'), title·tags(없으면 자동), hook(도입 줄들), cover_q(표지 큰 질문, <br> 가능),
cover_wrong·cover_right(표지의 틀린 문장·맞는 문장), uses_title(쓰임 카드 제목), reading(짝 독해 {"t": 이름, "u": 'study/…/4/'}),
outro.
"""
import argparse, html, json, os, re, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
from reading_blog import load_data, strip, TPL, GUIDE, BASE  # 같은 원고 틀·안내 글

KIT = os.path.join(HERE, 'gram_blog')
# 문법 안내 글(중학 영어 문법 무료 학습지 공개, 원고 tools/blog/mid-public-grammar/). 원장님이 블로그에 올리면 주소를 넣는다.
# 비어 있으면 독해 안내 글(GUIDE)을 가리킨다.
GRAM_GUIDE = ''
NUMS = '①②③④⑤⑥'


def body_of(cfg, D, U, img):
    H, R = D['hook'], D['rule']
    b = [["p", f"[대표 이미지: {img(1, 'cover')}]"]] + [["p", h] for h in cfg['hook']]
    b += [["p", cfg.get('intro', '이번 편도 학원이 직접 쓴 독해 지문 문장으로 만들었어요. 먼저 아래 문장이 맞는지 틀리는지 골라 보고, 학습지에서 개념 정리·문제·서술형 연습까지 이어서 풀어 보세요.')],
          ["p", "문법 학습지를 어떻게 만들었고 어떻게 쓰면 좋은지는 지난 글 '중학 영어 문법 무료 학습지 공개'에 정리해 두었어요." if GRAM_GUIDE else "학습지 사용법은 지난 글 '중학 영어 독해·문법 무료 학습지 공개'에 정리해 두었어요."],
          ["link", "▶ 문법 학습지 안내 글" if GRAM_GUIDE else "▶ 학습지 사용법 안내 글", cfg.get('guide', GRAM_GUIDE or GUIDE)],
          ["link", f"▶ {cfg['_name']} 학습지 바로가기", U]]
    b += [["b", "■ 먼저 풀어 보세요: 맞는 문장일까, 틀린 문장일까?"], ["p", f"[이미지: {img(2, 'ox')}]"]]
    b += [["p", f"{i + 1}. {strip(it['en'])}"] for i, it in enumerate(H['items'])]
    b += [["p", "정답은 글 맨 아래에 있어요. 학습지에서는 누르면 바로 채점되고 고친 문장도 보여 줘요."]]
    key = [c for c in R['cards'] if c.get('key')]
    uses = [c for c in R['cards'] if not c.get('key')]
    b += [["b", f"■ 오늘의 문법 · {cfg['grammar']}"]]
    for c in key:
        b += [["p", f"📌 {strip(c['lab'])} · {strip(c.get('sub', ''))}"], ["p", strip(c.get('t', ''))]]
    if uses:
        b += [["p", f"[이미지: {img(3, 'uses')}]"]]
        for c in uses:
            w = ', '.join(strip(x) for x in c.get('w', []))
            b += [["p", f"{strip(c['lab'])} ({strip(c.get('sub', ''))}){' — 함께 쓰는 말: ' + w if w else ''}"],
                  ["p", f"예) {strip(c.get('ex', ''))} {('(' + strip(c['ko']) + ')') if c.get('ko') else ''}".strip()]]
    if R.get('table'):
        T = R['table']
        b += [["b", f"■ {strip(R.get('tableTitle', '헷갈리는 것 구별하기'))}"], ["p", f"[이미지: {img(4, 'compare')}]"]]
        for r in T['rows']:
            b += [["p", f"· {strip(r[0])}: {strip(T['head'][1])} — {strip(r[1])} / {strip(T['head'][2])} — {strip(r[2])}"]]
        b += [["p", '· ' + strip(t)] for t in R.get('tips', [])]
    F = D.get('fix', [])
    if F:
        b += [["b", "■ 서술형에서 자주 감점되는 문장"]]
        b += [["p", f"{i + 1}. {strip(f['w'])} ({strip(f.get('ko', ''))})"] for i, f in enumerate(F[:3])]
        b += [["p", "어디가 틀렸을까요? 고친 문장은 맨 아래 정답에 있어요. 학습지 '틀린 곳 고쳐 쓰기'에서는 직접 써 보면 대문자·마침표까지 확인해 줘요."]]
    if D.get('check'):
        b += [["p", f"[이미지: {img(5, 'check')}]"], ["p", "✅ 서술형 감점 체크"]] + [["p", '· ' + strip(x)] for x in D['check']]
    rd = cfg.get('reading')
    if rd:
        b += [["b", "■ 독해 지문으로 이어 읽기"], ["p", cfg.get('reading_line', '이번 편 예문은 코코스 중등 독해 지문에서 가져왔어요. 지문 속에서 오늘 배운 문법을 직접 찾아보세요.')],
              ["link", f"▶ {rd['t']}", BASE + rd['u']]]
    ox = ' · '.join(f"{i + 1}번 {'O' if it['ok'] else 'X'}" for i, it in enumerate(H['items']))
    b += [["b", "■ 정답"], ["p", "먼저 풀어 보기: " + ox]]
    b += [["p", f"{i + 1}. {strip(it.get('fix', ''))}"] for i, it in enumerate(H['items']) if it.get('fix')]
    if F:
        b += [["p", "자주 감점되는 문장: " + ' / '.join(f"{i + 1}. {strip(f['a'][0])}" for i, f in enumerate(F[:3]))]]
    b += [["br"], ["p", cfg.get('outro', '다음 편도 독해 지문 속 문장으로 찾아올게요. 링크와 PDF는 친구에게 자유롭게 공유해도 좋아요.')]]
    return b, ox


def page(cfg, D, U, body):
    grade, rnd = cfg['_grade'], cfg['_round']
    title = cfg.get('title') or f"{grade} 영어 문법 무료 학습지 {rnd}회 | {cfg['grammar']} | {strip(cfg['cover_q']).replace('<br>', ' ')} | 코코스학원"
    tags = cfg.get('tags') or ' '.join([f'{grade}영어문법', '중학영어문법', cfg['grammar'].replace(' ', ''), '영어서술형', f'{grade}영어', '무료학습지', '코코스학원'])
    items = [[f"{cfg['_name']} 학습지", U]]
    if cfg.get('reading'):
        items.append([cfg['reading']['t'], BASE + cfg['reading']['u']])
    groups = [{'g': '바로가기', 'items': items}]
    Dd = {"url": U, "title": title, "tags": tags, "count": len(items), "groups": groups, "body": body}
    s = open(TPL, encoding='utf8').read()
    i = s.find('var D=') + 6
    _, end = json.JSONDecoder().raw_decode(s[i:])
    s = s[:i] + json.dumps(Dd, ensure_ascii=False) + s[i + end:]
    name = f"코코스 중등 문법 {grade} {rnd}회"
    for a, b in [(r'<title>[^<]*</title>', f'<title>{name} 블로그 원고</title>'),
                 (r'<h1>[^<]*</h1>', f"<h1>{name} · {html.escape(cfg['grammar'])} 블로그 원고</h1>")]:
        s = re.sub(a, b, s, count=1)
    for a, b in [("D.count+'개 지문 · 제목·본문·태그'", "'제목·본문·태그 · 이미지 5장'"),
                 ("(D.groups.length>1?'범위 '+D.groups[0].items.length+'개 · ':'')+'지문 '+D.count+'개 · 줄마다 그 범위가 골라진 채로 열려요'", "'바로가기 '+D.count+'개 · 문법 학습지와 짝 독해 지문'"),
                 ('범위별·지문별 바로가기만', '바로가기만'),
                 ('목록에서 한 줄을 눌러 그 범위가 골라진 채로 단어게임이 열리는지 확인하고 발행해요.', '목록에서 한 줄을 눌러 링크가 제대로 열리는지 확인하고 발행해요.'),
                 ('단어게임 링크 복사', '문법 학습지 링크 복사'), ("'단어게임 주소를 복사했어요.'", "'문법 학습지 주소를 복사했어요.'")]:
        assert a in s, '원고 틀이 바뀜: ' + a[:40]
        s = s.replace(a, b)
    return s, title, tags


def images(cfg, D, outdir):
    lib = open(os.path.join(ROOT, 'library', 'index.html'), encoding='utf8').read()
    logo = re.search(r'url\((data:image/png;base64,[^)]+)\)', lib).group(1)
    css = open(os.path.join(HERE, 'reading_blog', 'cards.css'), encoding='utf8').read() + open(os.path.join(KIT, 'gram_cards.css'), encoding='utf8').read()
    css = css.replace('__LOGO__', logo)
    grade, rnd, H, R = cfg['_grade'], cfg['_round'], D['hook'], D['rule']
    foot = '<div class="foot"><span>코코스 중등 문법 · 무료 공개</span><span class="url">cocosedu.kr</span></div>'
    kick = f'코코스 중등 문법 · {grade} {rnd}회 · 무료 학습지'
    cards = [f'''<section class="card gc g-cover" id="c1"><div class="sheet"><div class="logo"></div>
  <p class="kicker">{kick}</p><span class="tag t-pink gname">{cfg['grammar']}</span>
  <h1>{cfg['cover_q']}</h1>
  <div class="pair"><p class="bad"><span>X</span><em>{cfg['cover_wrong']}</em></p><p class="good"><span>O</span>{cfg['cover_right']}</p></div>{('<p class="sub2">' + cfg['cover_sub'] + '</p>') if cfg.get('cover_sub') else ''}
  <div class="foot"><span>개념 정리·단계별 문제·서술형 연습·PDF</span><span class="url">cocosedu.kr</span></div></div></section>''']
    rows = ''.join(f'<li><span class="n">{i + 1}</span><span class="s">{it["en"]}</span><span class="ox">O / X</span></li>' for i, it in enumerate(H['items']))
    cards.append(f'''<section class="card gc g-ox" id="c2"><div class="sheet"><p class="no2">STEP 1 · 먼저 풀어 보기</p>
  <h2>맞는 문장일까,<br>틀린 문장일까?</h2><ol class="oxl">{rows}</ol><p class="hint">정답은 블로그 글 맨 아래, 학습지에서는 바로 채점!</p>{foot}</div></section>''')
    uses = [c for c in R['cards'] if not c.get('key')]
    key = next((c for c in R['cards'] if c.get('key')), None)
    cols = ['t-blue', 't-pink', 't-mint', 't-lilac']
    ub = ''.join(f'''<div class="u {cols[i % 4]}"><b>{c['lab']}</b><small>{c.get('sub', '')}</small><p class="w">{' · '.join(c.get('w', []))}</p><p class="ex">{c.get('ex', '')}</p></div>''' for i, c in enumerate(uses[:4]))
    cards.append(f'''<section class="card gc g-uses" id="c3"><div class="sheet"><p class="no2">STEP 2 · 한눈에 정리</p>
  <h2>{cfg.get('uses_title', cfg['grammar'])}</h2>{f'<p class="form">{key["sub"]}</p>' if key else ''}<div class="ug">{ub}</div>{foot}</div></section>''')
    T = R.get('table')
    if T:
        tr = ''.join(f'<tr><th>{r[0]}</th><td>{r[1]}</td><td>{r[2]}</td></tr>' for r in T['rows'])
        cards.append(f'''<section class="card gc g-cmp" id="c4"><div class="sheet"><p class="no2">STEP 3 · 구별하기</p>
  <h2>{cfg.get('compare_title', strip(R.get('tableTitle', '')))}</h2><table class="ct"><thead><tr><th></th><th>{T['head'][1]}</th><th>{T['head'][2]}</th></tr></thead><tbody>{tr}</tbody></table>{foot}</div></section>''')
    ck = ''.join(f'<li>{strip(x)}</li>' for x in D.get('check', []))
    cards.append(f'''<section class="card gc g-check" id="c5"><div class="sheet"><p class="no2">STEP 4 · 서술형 대비</p>
  <h2>서술형 감점 체크</h2><ul class="ckl">{ck}</ul>{foot}</div></section>''')
    doc = '<!doctype html><html lang="ko"><head><meta charset="utf-8"><style>' + css + '</style></head><body>' + '\n'.join(cards) + '</body></html>'
    os.makedirs(outdir, exist_ok=True)
    hp = os.path.join(outdir, 'cards.html')
    open(hp, 'w', encoding='utf8').write(doc)
    keys = ['cover', 'ox', 'uses', 'compare', 'check'] if T else ['cover', 'ox', 'uses', 'check']
    names = [cfg['_img'](i + 1, k) for i, k in enumerate(keys)]
    js = os.path.join(outdir, 'render.js')
    open(js, 'w', encoding='utf8').write('''const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();
const p=await b.newPage({viewport:{width:1100,height:1100}});await p.goto('file://'+process.argv[2]);await p.waitForTimeout(800);
const names=JSON.parse(process.argv[3]);const els=await p.$$('section.card');for(let i=0;i<names.length;i++){const el=els[i];
const of=await p.evaluate(e=>{const s=e.querySelector('.sheet').getBoundingClientRect(),f=e.querySelector('.foot').getBoundingClientRect();
return [...e.querySelectorAll('.sheet *')].filter(x=>{if(x.closest('.foot'))return false;const r=x.getBoundingClientRect();return r.bottom>f.top-6||r.right>s.right-20}).length},el);
await el.screenshot({path:process.argv[4]+'/'+names[i]});console.log(names[i], of?'넘침 '+of:'OK');}await b.close();})();''')
    r = subprocess.run(['node', js, os.path.abspath(hp), json.dumps(names, ensure_ascii=False), os.path.abspath(outdir)], capture_output=True, text=True, cwd=outdir)
    print(r.stdout.strip() or r.stderr.strip())
    return names


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('config'); ap.add_argument('-o', default=None)
    a = ap.parse_args()
    cfg = json.load(open(a.config, encoding='utf8'))
    m = re.match(r'grammar-m(\d)-(\d+)$', cfg['slug']); assert m, 'slug는 grammar-m<학년>-<회>'
    cfg['_grade'], cfg['_round'] = f'중{m.group(1)}', int(m.group(2))
    cfg['_name'] = f"코코스 중등 문법 {cfg['_grade']} {cfg['_round']}회 · {cfg['grammar']}"
    cfg['_img'] = lambda n, key: f"문법{cfg['_round']}회_{n:02d}_{key}.png"
    D = load_data(os.path.join(ROOT, 'study', cfg['slug'], 'index.html'))
    U = f"{BASE}study/{cfg['slug']}/"
    body, ox = body_of(cfg, D, U, cfg['_img'])
    s, title, tags = page(cfg, D, U, body)
    out = os.path.join(ROOT, 'tools', 'blog', cfg['slug'], 'index.html')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, 'w', encoding='utf8').write(s)
    outdir = a.o or os.path.join(os.getcwd(), f"blog_{cfg['slug']}")
    images(cfg, D, outdir)
    print('원고:', os.path.relpath(out, ROOT), '· 본문', len(body), '줄 · O/X 정답', ox)
    print('제목:', title); print('태그:', tags); print('이미지:', outdir)


if __name__ == '__main__':
    main()
