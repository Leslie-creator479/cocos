# -*- coding: utf-8 -*-
"""시험 직전 세트 — 한 번의 출제 분석(content.json)으로 네 파일을 찍는다.

    python3 -I build_all.py <wonjimun/scripts> content.json <출력 접두어> [top,final,report,detail]

  마지막 인자로 만들 자료만 고를 수 있다(기본은 top,final,report).
  top은 picks가, detail은 문장별 pts·u와 지문별 whole이 필요하다.

  <접두어>_출제1순위.docx     학생용: 핵심 2문장 암기 → 빈칸 → 배열 영작 → 통영작(도전) → 정답
  <접두어>_어법Final_문제.docx 지문마다 색칠 자리(동사·준동사·접속사) 중 최다 빈출 3곳을 틀리게 바꾼 지문(표시 없음)
  <접두어>_어법Final_정답.docx 바른 말에 회색 음영
  <접두어>_출제분석.docx       선생님 확인용 집계표(문장별·어법 자리별 근거, 색칠 안/밖 비율)
  <접두어>_기출중요문장.docx   선생님 참고용 상세판(중요도 음영 지문, 문장별 출제 방식, 글 전체 경향)
"""
import sys, re, json
sys.path.insert(0, sys.argv[1])
import build_docx as B

C = json.load(open(sys.argv[2], encoding='utf8'))
PRE = sys.argv[3]
WANT = set(sys.argv[4].split(',')) if len(sys.argv) > 4 else {'top', 'final', 'report'}
SERIES, P = C['series'], C['passages']
BLUE, ORANGE, GRAY, LINE, SHADE = '1F5FA9', 'E36C0A', '595959', '8C8C8C', 'D9D9D9'
RANK = ['①', '②']
COLORED = ('동사', '준동사', '접속사')          # 구문분석에서 색칠하는 자리


# ───────────────────────── 선정 ─────────────────────────
def score(s):
    return (-(s['a'] + s.get('big', 0)), -s['n'])


def top2(p):
    """정답 근거(+주제·제목 근거) 많은 순 → 등장 많은 순 → 앞 문장."""
    idx = sorted(range(len(p['sents'])), key=lambda j: score(p['sents'][j]) + (j,))
    return [j + 1 for j in idx[:2]]


def gram3(p):
    """어법 정답 횟수 → 어법 등장 횟수 → 문장 출제 점수 → 앞 자리. 한 문장에 한 곳.
    색칠 자리(동사·준동사·접속사)만 낸다(content.json에 "final_colored": false면 끈다):
    빈도순으로 뽑힌 자리 중 색칠 자리는 그대로 두고, 색칠 밖 자리는 다음 순위 색칠 자리로 바꾼다."""
    key = lambda e: (-e[1]['a'], -e[1]['n']) + score(p['sents'][e[1]['s'] - 1]) + (e[0],)
    g = sorted(enumerate(p['gram']), key=key)
    out, used = [], set()
    for _, x in g:
        if x['s'] not in used:
            out.append(x)
            used.add(x['s'])
        if len(out) == 3:
            break
    if C.get('final_colored', True):
        out = [x for x in out if x['c'] in COLORED]
        used = {x['s'] for x in out}
        for _, x in g:
            if len(out) == 3:
                break
            if x['c'] in COLORED and x['s'] not in used:
                out.append(x)
                used.add(x['s'])
    return sorted(out, key=lambda x: x['s'])


warn, bad, ITEMS, FINAL = [], [], [], {}
for p in P:
    t2 = top2(p)
    sc = [score(p['sents'][j - 1]) for j in range(1, len(p['sents']) + 1)]
    srt = sorted(sc)
    if len(srt) > 2 and srt[1] == srt[2]:
        warn.append(f"[동점] {p['no']} 출제 1순위 ②번 자리가 동점 — 앞 문장을 골랐다")
    picks = {d['s']: d for d in p.get('picks', [])}
    for r, sn in enumerate(t2 if 'top' in WANT else []):
        if sn not in picks:
            bad.append(f"{p['no']} [{sn}] 드릴 재료(picks)가 없다")
            continue
        s, d = p['sents'][sn - 1], picks[sn]
        for w in d['u'] + d['bl']:
            if not re.search(r'\b' + re.escape(w) + r'\b', s['t']):
                bad.append(f"{p['no']} [{sn}] '{w}'가 원문에 없다")
        ITEMS.append((p, r, s, d))
    for x in p['gram']:
        if not re.search(r'\b' + re.escape(x['o']) + r'\b', p['sents'][x['s'] - 1]['t']):
            bad.append(f"{p['no']} [{x['s']}] 어법 자리 '{x['o']}'가 원문에 없다")
    FINAL[p['no']] = gram3(p)
    if 'final' not in WANT:
        continue
    if len(FINAL[p['no']]) < 3:
        warn.append(f"[부족] {p['no']} 색칠 어법 자리가 {len(FINAL[p['no']])}곳뿐 — gram에 q '추가(색칠 자리)'로 보충할 것")
    if any(str(x.get('q', '')).startswith('추가') for x in FINAL[p['no']]):
        warn.append(f"[추가] {p['no']} 기출에 없던 색칠 자리를 넣었다: "
                    + ', '.join(f"[{x['s']}] {x['o']}" for x in FINAL[p['no']] if str(x.get('q', '')).startswith('추가')))
    if any(x['a'] == 0 for x in FINAL[p['no']]):
        warn.append(f"[보충] {p['no']} 정답 자리가 3곳이 안 돼 선지 자리로 채웠다")
for p in P if 'detail' in WANT else []:
    for j, s in enumerate(p['sents'], 1):
        if s['a'] + s.get('big', 0) > 0 and not s.get('pts'):
            warn.append(f"[설명 없음] {p['no']} [{j}] 정답 근거가 있는데 pts가 없다")
        for w in s.get('u', []):
            if not re.search(r'\b' + re.escape(w) + r'\b', s['t']):
                bad.append(f"{p['no']} [{j}] 밑줄 '{w}'가 원문에 없다")
if bad:
    sys.exit('\n'.join(bad))


# ───────────────────────── 서식 도우미 ─────────────────────────
def split_runs(text, keys, size, *, hit, base_bold=True):
    if not keys:
        return [B.run(text, size, bold=base_bold)]
    pat = re.compile(r'\b(' + '|'.join(re.escape(k) for k in
                                       sorted(keys, key=len, reverse=True)) + r')\b')
    out, pos = [], 0
    for m in pat.finditer(text):
        if m.start() > pos:
            out.append(B.run(text[pos:m.start()], size, bold=base_bold))
        out.append(hit(m.group(0)))
        pos = m.end()
    if pos < len(text):
        out.append(B.run(text[pos:], size, bold=base_bold))
    return out


def letter(p, para, size, line):
    """편지글이면 첫 인사(pre)와 맺음(post) 줄을 본문 앞뒤에 따로 단락으로 둔다."""
    if not p.get('pre'):
        return [para]
    one = lambda t, **k: B.para([B.run(t, size)], line=line, rule='exact', **k)
    post = p.get('post', [])
    return ([one(p['pre'], before=300, keep_next=True)] + [para.replace('w:before="300"', 'w:before="0"', 1)]
            + [one(t, keep_next=(k < len(post) - 1)) for k, t in enumerate(post)])


def border(p, color='BFBFBF', sz=4, space=6):
    return p.replace('</w:pPr>', f'<w:pBdr><w:bottom w:val="single" w:sz="{sz}" '
                     f'w:space="{space}" w:color="{color}"/></w:pBdr></w:pPr>')


def shade(r, fill):
    return r.replace('</w:rPr>', f'<w:shd w:val="clear" w:color="auto" w:fill="{fill}"/></w:rPr>')


def heading(text, sub, first=False):
    return [border(B.para([B.run(text, 13, bold=True, color=BLUE)], after=60, line=340,
                          rule='exact', keep_next=True, page_break=not first),
                   color=ORANGE, sz=8, space=2),
            B.para([B.run(sub, 8.5, color=GRAY)], after=160, line=260, keep_next=True)]


def label(p, r):
    return [B.run(f"{p['no']} {RANK[r]}  ", 10.5, bold=True, color=ORANGE)]


def write_line(first):
    # 같은 테두리 두 줄은 하나로 합쳐지므로 색을 아주 조금 다르게 준다
    return border(B.para([B.run(' ', 10)], line=520, rule='exact', ind=600, keep_next=first),
                  color=(LINE if first else '8D8D8D'), space=1)


blue_ul = lambda size: (lambda w: B.run(w, size, bold=True, underline=True, color=BLUE))


def decap(chunk, sent, keep=()):
    """배열 조각의 첫 글자 대문자로 첫 단어가 드러나지 않게 소문자로 바꾼다.
    I, 약어(AI 등), 문장 중간에서도 대문자로 쓰인 말, keep에 적은 고유명사는 그대로 둔다."""
    m = re.match(r"[A-Za-z]+", chunk)
    if not m or not chunk[0].isupper():
        return chunk
    w = m.group(0)
    if w == 'I' or (len(w) > 1 and w.isupper()) or w in keep:
        return chunk
    if any(x.start() > 0 for x in re.finditer(r'\b' + w + r'\b', sent)):
        return chunk
    return chunk[0].lower() + chunk[1:]


# ───────────────────────── 1) 출제 1순위 ─────────────────────────
if 'top' in WANT:
    out = heading('암기', '각 지문에서 기출·변형문제에 가장 자주 출제되고 정답이 된 문장 2개.  '
                  '밑줄 = 실제로 문제가 걸린 자리.  통째로 외우고, 포인트 줄은 틀리지 않게!', first=True)
    cur = None
    for p, r, s, d in ITEMS:
        if p is not cur:
            cur = p
            out.append(B.para([B.run(f"{p['no']}.  ", 12, bold=True),
                               B.run(p['en'], 10, bold=True, color=B.RED),
                               B.run(f"  ({p['ko']})", 9, bold=True, color=B.RED)],
                              before=(0 if p is P[0] else 260), after=100, line=330,
                              rule='exact', keep_next=True))
        out.append(B.para([B.run(RANK[r] + '  ', 11, bold=True, color=ORANGE)]
                          + split_runs(s['t'], d['u'], 10.5, hit=blue_ul(10.5)),
                          before=(0 if r == 0 else 140), after=30, line=330, rule='exact',
                          ind=400, hanging=400, keep_next=True, keep_lines=True))
        out.append(B.para([B.run(s['k'], 9, color=GRAY)], ind=400, line=270, rule='exact',
                          after=40, keep_next=True, keep_lines=True))
        for n, (tag, txt) in enumerate(d['pt']):
            end = r == 1 and n == len(d['pt']) - 1
            q = B.para([B.run('▸ ' + tag + '  ', 8.5, bold=True, color=BLUE), B.run(txt, 8.5)],
                       ind=400, line=255, rule='exact', after=(120 if end else 0),
                       keep_next=not end, keep_lines=True)
            out.append(border(q) if end else q)

    out += heading('테스트 1단계 · 빈칸', '기출에서 문제가 걸렸던 자리만 비웠습니다. 해석을 보고 빈칸을 채우세요.')
    for p, r, s, d in ITEMS:
        blank = lambda w: B.run('_' * max(8, int(len(w) * 1.6)), 10.5, color=LINE)
        out.append(B.para(label(p, r) + split_runs(s['t'], d['bl'], 10.5, hit=blank, base_bold=False),
                          before=160, line=560, rule='exact', ind=600, hanging=600,
                          keep_next=True, keep_lines=True))
        out.append(B.para([B.run(s['k'], 8.5, color=GRAY)], ind=600, line=250, rule='exact',
                          keep_lines=True))

    out += heading('테스트 2단계 · 배열 영작', '해석에 맞게 단어 덩어리를 배열하세요. 조건에 적힌 수만큼 '
                   '단어의 형태를 바꿔야 합니다. 조각은 소문자·문장부호 없이 주었으니 첫 글자 대문자와 '
                   '문장부호는 직접 쓰세요 (어형 변화로 세지 않음).')
    for p, r, s, d in ITEMS:
        out.append(B.para(label(p, r) + [B.run(s['k'], 9.5)], before=200, after=60, line=300,
                          rule='exact', ind=600, hanging=600, keep_next=True, keep_lines=True))
        # 끝에 붙은 쉼표·세미콜론도 자리를 알려 주므로 뗀다
        chunks = [decap(c, s['t'], d.get('keep', ())).rstrip(',;:') for c in d['ch']]
        out.append(B.para([B.run('[  ' + '  /  '.join(chunks) + '  ]', 9.5, bold=True)],
                          ind=600, line=290, rule='exact', keep_next=True, keep_lines=True))
        out.append(B.para([B.run(f"▸ 조건: 어형 변화 {d['nchg']}곳", 8.5, bold=True, color=ORANGE)],
                          ind=600, line=260, rule='exact', keep_next=True))
        out += [write_line(True), write_line(False)]

    out += heading('테스트 3단계 · 통영작 (도전)', '해석만 보고 영어 문장 전체를 쓰세요.')
    for p, r, s, d in ITEMS:
        out.append(B.para(label(p, r) + [B.run(s['k'], 9.5)], before=200, line=300, rule='exact',
                          ind=600, hanging=600, keep_next=True, keep_lines=True))
        out += [write_line(True), write_line(False)]

    out += heading('정답', '2·3단계의 정답은 원문 그대로입니다. 1단계 정답은 원문의 굵은 밑줄 부분.')
    for p, r, s, d in ITEMS:
        out.append(B.para(label(p, r) + split_runs(s['t'], d['bl'], 9.5, base_bold=False,
                                                   hit=blue_ul(9.5)),
                          before=100, line=300, rule='exact', ind=600, hanging=600, keep_lines=True))
    B.emit(''.join(out), {'series': SERIES, 'label': '출제 1순위'}, f'{PRE}_출제1순위.docx')


# ───────────────────────── 2) 어법 Final ─────────────────────────
if 'final' in WANT:
    def final_runs(p, mode):
        by_s = {x['s']: x for x in FINAL[p['no']]}
        out = []
        for j, s in enumerate(p['sents'], 1):
            t, x = s['t'] + ' ', by_s.get(j)
            if not x:
                out.append(B.run(t, 11, spacing=6))
                continue
            m = re.search(r'\b' + re.escape(x['o']) + r'\b', t)
            out.append(B.run(t[:m.start()], 11, spacing=6))
            out.append(B.run(x['x'], 11, spacing=6) if mode == 'test'
                       else shade(B.run(x['o'], 11, bold=True, spacing=6), SHADE))
            out.append(B.run(t[m.end():], 11, spacing=6))
        return out


    for mode, name in (('test', '어법Final_문제'), ('key', '어법Final_정답')):
        body = []
        for i, p in enumerate(P):
            body.append(B.para([B.run(f"{p['no']}.", 13, bold=True)], after=180, line=340,
                               rule='exact', keep_next=True, page_break=(i > 0)))
            body += letter(p, B.para(final_runs(p, mode), before=300, line=525, rule='exact', justify=True),
                           11, 525)
        B.emit(''.join(body), {'series': SERIES, 'label': 'Final'}, f'{PRE}_{name}.docx')


# ───────────────────────── 3) 출제 분석 (선생님용) ─────────────────────────
if 'report' in WANT:
    def cell(text, w, *, bold=False, fill=None, center=False, color='000000'):
        pr = f'<w:tcW w:w="{w}" w:type="dxa"/>'
        if fill:
            pr += f'<w:shd w:val="clear" w:color="auto" w:fill="{fill}"/>'
        p = B.para([B.run(text, 8.5, bold=bold, color=color)], before=30, after=30,
                   line=250, center=center)
        return f'<w:tc><w:tcPr>{pr}<w:vAlign w:val="center"/></w:tcPr>{p}</w:tc>'


    BD = ''.join(f'<w:{x} w:val="single" w:sz="4" w:space="0" w:color="BFBFBF"/>'
                 for x in ('top', 'left', 'bottom', 'right', 'insideH', 'insideV'))


    def table(hdr, rows, W):
        x = (f'<w:tbl><w:tblPr><w:tblW w:w="{sum(W)}" w:type="dxa"/><w:tblBorders>{BD}'
             '</w:tblBorders><w:tblLayout w:type="fixed"/></w:tblPr><w:tblGrid>'
             + ''.join(f'<w:gridCol w:w="{w}"/>' for w in W) + '</w:tblGrid>')
        x += '<w:tr>' + ''.join(cell(h, w, bold=True, fill='DCEAF7', center=True)
                                for h, w in zip(hdr, W)) + '</w:tr>'
        for cells, fill in rows:
            x += '<w:tr><w:trPr><w:cantSplit/></w:trPr>'
            for k, (c, w) in enumerate(zip(cells, W)):
                x += cell(c, w, fill=fill, center=(k < 3), bold=(k == 0))
            x += '</w:tr>'
        return x + '</w:tbl>'


    def sub(text):
        return B.para([B.run(text, 9.5, bold=True)], before=140, after=60, line=280,
                      rule='exact', keep_next=True)


    # 색칠 안/밖 요약 — 어법 문항에서 정답이 된 자리 기준
    ans = [x for p in P for x in p['gram'] if x['a'] > 0]
    cnt = {}
    for x in ans:
        cnt[x['c']] = cnt.get(x['c'], 0) + x['a']
    tot = sum(cnt.values()) or 1
    inn = sum(v for k, v in cnt.items() if k in COLORED)
    t = [B.para([B.run('어법 정답 자리 — 색칠 안/밖', 11, bold=True, color=BLUE)], after=80, line=300,
                rule='exact', keep_next=True),
         B.para([B.run(f"어법 문항의 정답이 된 자리 {tot}회 중  색칠 자리 {inn}회({inn * 100 // tot}%)  ·  "
                       f"색칠 밖 {tot - inn}회({(tot - inn) * 100 // tot}%)", 9.5, bold=True)],
                after=60, line=280, rule='exact')]
    order = list(COLORED) + sorted(k for k in cnt if k not in COLORED)
    t.append(table(['분류', '구문분석 색', '정답 횟수', '예'],
                   [([k, {'동사': '빨강', '준동사': '파랑', '접속사': '초록'}.get(k, '색칠 밖'), str(cnt.get(k, 0)),
                      ', '.join(f"{x['o']}→{x['x']}" for x in ans if x['c'] == k)[:90]],
                     None if k in COLORED else 'FFF0A0') for k in order], [1500, 1300, 1100, 6300]))
    t.append(B.para([B.run('정답 근거 = 그 문항의 정답이 이 문장(자리)에서 나온 경우(네모는 칸마다 1회). '
                           '등장 = 오답 선지로 걸린 경우까지. 주제·제목·요지 문항은 "대의"로 따로 표시. '
                           '순서 문항·지문 밖 문장을 넣은 무관 문항은 집계에서 뺐다.', 8, color=GRAY)],
                    before=100, after=100, line=250, justify=True))

    for p in P:
        top = top2(p)
        t.append(B.para([B.run(f"{p['no']}.  {p['src']} · {p['nq']}문항", 10.5, bold=True, color=BLUE)],
                        before=260, after=60, line=300, rule='exact', keep_next=True))
        t.append(sub('문장별 출제 (① ② = 출제 1순위)'))
        rows = []
        for j, s in enumerate(p['sents'], 1):
            big = f" (+대의 {s['big']})" if s.get('big') else ''
            mark = '①②'[top.index(j)] if j in top else ''
            rows.append(([f'[{j}]', mark, f"{s['a']}{big} / {s['n']}", s.get('ans', ''), s.get('opt', '')],
                         'FFF0A0' if j in top else None))
        t.append(table(['문장', '선정', '정답/등장', '정답 근거 문항', '선지로 등장한 문항'], rows,
                       [700, 700, 1300, 4000, 3500]))
        t.append(sub('어법 자리 (★ = 어법 Final 선정)'))
        fin = FINAL[p['no']]
        rows = []
        for x in sorted(p['gram'], key=lambda x: (x['s'], x['o'])):
            on = x in fin
            rows.append(([f"[{x['s']}]", '★' if on else '', f"{x['a']} / {x['n']}",
                          f"{x['o']} → {x['x']}", f"{x['c']}{'' if x['c'] in COLORED else ' (색칠 밖)'} · {x['q']}"],
                         'FFF0A0' if on else None))
        t.append(table(['문장', 'Final', '정답/등장', '바른 말 → 틀린 말', '분류 · 문항'], rows,
                       [700, 700, 1300, 3500, 4000]))
        if p.get('excl'):
            t.append(B.para([B.run('※ ' + p['excl'], 8, color=GRAY)], before=60, after=60))
    B.emit(''.join(t), {'series': SERIES, 'label': '출제 분석'}, f'{PRE}_출제분석.docx')


# ───────────────────────── 4) 기출 중요 문장 (선생님 참고용 상세판) ─────────────────────────
if 'detail' in WANT:
    FILL3, FILL2 = 'FFF0A0', 'DCEAF7'
    STARS = {3: '★★★', 2: '★★', 1: '★'}

    def level(p, s):
        """정답 근거(+대의) 점수가 지문 최고점의 50% 이상 ★★★, 25% 이상 ★★, 1점 이상 ★. lv로 직접 지정 가능."""
        if 'lv' in s:
            return s['lv']
        top_ = max(x['a'] + x.get('big', 0) for x in p['sents']) or 1
        v = s['a'] + s.get('big', 0)
        return 3 if v * 2 >= top_ else 2 if v * 4 >= top_ else 1 if v > 0 else 0

    def h2(text):
        return border(B.para([B.run(text, 11.5, bold=True, color=BLUE)], before=260, after=100,
                             line=320, rule='exact', keep_next=True), color=ORANGE, sz=6, space=2)

    def ul(size):
        return lambda w: B.run(w, size, bold=True, underline=True, color=BLUE)

    def pts_lines(pts, ind):
        o = []
        for n, (tag, txt) in enumerate(pts):
            o.append(B.para([B.run(f'{tag}  ', 8.5, bold=True, color=BLUE), B.run(txt, 8.5)],
                            ind=ind, hanging=700, line=260, rule='exact',
                            keep_next=(n < len(pts) - 1), keep_lines=True))
        return o

    body = []
    for i, p in enumerate(P):
        lv = {j: level(p, s) for j, s in enumerate(p['sents'], 1)}
        body.append(B.para([B.run(f"{p['no']}.", 13, bold=True)], after=180, line=340,
                           rule='exact', keep_next=True, page_break=(i > 0)))
        body.append(B.para([B.run('주제 : ' + p['en'], 11, bold=True, color=B.RED)],
                           line=330, rule='exact', ind=612, hanging=612, keep_next=True))
        body.append(B.para([B.run('(' + p['ko'] + ')', 11, bold=True, color=B.RED)],
                           after=90, line=330, rule='exact', ind=612, keep_next=True))
        body.append(B.para([B.run(f"분석 자료 : {p['src']} {p['nq']}문항  ·  "
                                  "문항마다 정답이 나온 문장을 원문에 연결해 센 결과", 9,
                                  bold=True, color=B.RED)],
                           line=272, rule='exact', ind=505, hanging=505, keep_next=True))
        body.append(B.para([shade(B.run(' ★★★ 최다 출제 ', 8.5, bold=True), FILL3), B.run('   ', 8.5),
                            shade(B.run(' ★★ 자주 출제 ', 8.5, bold=True), FILL2),
                            B.run('   [번호] 문장 번호 · 밑줄 = 실제로 문제가 걸린 자리', 8.5, color=GRAY)],
                           before=200, after=120, line=280, rule='exact', keep_next=True))
        runs = []
        for j, s in enumerate(p['sents'], 1):
            fill = FILL3 if lv[j] == 3 else FILL2 if lv[j] == 2 else None
            runs.append(B.run(f'[{j}]', 7.5, bold=True, color=ORANGE))
            r = B.run(s['t'] + ' ', 10.5, bold=(lv[j] == 3))
            runs.append(shade(r, fill) if fill else r)
        body += letter(p, B.para(runs, line=500, rule='exact', justify=True), 10.5, 500)

        body.append(h2('핵심 문장  —  자주 출제된 순서'))
        order = sorted([j for j in lv if lv[j] >= 2],
                       key=lambda j: (-lv[j],) + score(p['sents'][j - 1]) + (j,))
        for j in order:
            s = p['sents'][j - 1]
            cnt = f"정답 근거 {s['a']}회 · 등장 {s['n']}회"
            if s.get('big'):
                cnt += f" · 주제·제목 근거 {s['big']}회"
            body.append(B.para([B.run(STARS[lv[j]] + '  ', 10, bold=True, color=ORANGE),
                                B.run(f'[{j}]  ', 10, bold=True), B.run(cnt, 8.5, color=GRAY)],
                               before=200, after=40, line=300, rule='exact', keep_next=True))
            body.append(B.para(split_runs(s['t'], s.get('u', []), 10.5, hit=ul(10.5), base_bold=False),
                               ind=200, line=330, rule='exact', after=30, keep_next=True, keep_lines=True))
            body.append(B.para([B.run(s['k'], 9, color=GRAY)], ind=200, line=270, rule='exact',
                               after=50, keep_next=bool(s.get('pts')), keep_lines=True))
            body += pts_lines(s.get('pts', []), 1100)

        rest = [j for j in lv if lv[j] < 2 and p['sents'][j - 1].get('pts')]
        if rest:
            body.append(h2('그 밖에 출제된 문장'))
            for j in rest:
                s = p['sents'][j - 1]
                body.append(B.para([B.run('★ ' if lv[j] == 1 else '', 9, bold=True, color=ORANGE),
                                    B.run(f'[{j}]  ', 9, bold=True)]
                                   + split_runs(s['t'], s.get('u', []), 9.5, hit=ul(9.5), base_bold=False),
                                   before=120, after=20, line=290, rule='exact', keep_next=True))
                body += pts_lines(s['pts'], 1100)

        if p.get('whole'):
            body.append(h2('글 전체에서 본 출제 경향'))
            for tag, txt in p['whole']:
                body.append(B.para([B.run(f'{tag}  ', 8.5, bold=True, color=BLUE), B.run(txt, 8.5)],
                                   ind=1100, hanging=1100, line=270, rule='exact', after=30))
    B.emit(''.join(body), {'series': SERIES, 'label': '기출 중요 문장'}, f'{PRE}_기출중요문장.docx')


for p in P:
    print(p['no'], '출제1순위', top2(p) if 'top' in WANT else '-', '| 어법Final',
          ' · '.join(f"[{x['s']}] {x['o']}→{x['x']}" for x in FINAL[p['no']]))
print('\n'.join(warn) if warn else '경고 없음')
print('ok', PRE)
