# -*- coding: utf-8 -*-
"""원문 ↔ 시험 문항 2단 비교 자료(학생 배포용) → COCOS 원지문 공식 틀 .docx
    python3 build_compare.py compare.json -o 출력.docx
compare.json = {"meta": {series, title, heading, sub, intro, omitted}, "sets": [세트, ...]}
세트 = {no, src, change, pts, left_label, right_label, pairs: [[왼쪽 문단[], 오른쪽 문단[]], ...], points: [바뀐 점, ...]}
표시: [[…]] 바뀐 곳(왼쪽 파랑 = 원래 표현, 오른쪽 노랑·빨강 = 시험 표현), ~~…~~ 시험에서 빠진 부분,
      ++…++ 시험지 밑줄, **…** 굵게. 문단 앞 'OPT:' = 선택지(| 로 나눔), 'BOX:' = 테두리 상자."""
import sys, re, os, glob, json, zipfile, argparse, html
M, SETS = {}, []
CANDS = glob.glob('/root/.claude/plugins/synced/*/cocos/skills/cocos-wonjimun/scripts') + glob.glob('/mnt/skills/plugins/cocos*/skills/cocos-wonjimun/scripts') + glob.glob('/mnt/skills/plugins/*/cocos-wonjimun/scripts')
if not CANDS:
    raise SystemExit('cocos-wonjimun 스킬의 scripts 폴더를 찾지 못했다.')
sys.path.insert(0, CANDS[0])
import build_docx as B
from build_docx import FONTS, para, run

W = 10200
NAVY, BLUE, RED, GRAY = '12355B', '1F5FA9', 'C0392B', '595959'
L_FILL, R_FILL = 'D6E8FA', 'FFF0A0'
esc = lambda t: html.escape(t, quote=False)


def xrun(text, size=9, *, bold=False, color='000000', strike=False, underline=False, fill=None):
    rpr = [FONTS]
    if bold: rpr.append('<w:b/>')
    if strike: rpr.append('<w:strike/>')
    rpr.append(f'<w:color w:val="{color}"/><w:sz w:val="{int(size * 2)}"/>')
    rpr.append('<w:u w:val="single"/>' if underline else '<w:u w:val="none"/>')
    if fill: rpr.append(f'<w:shd w:val="clear" w:color="auto" w:fill="{fill}"/>')
    return f'<w:r><w:rPr>{"".join(rpr)}</w:rPr><w:t xml:space="preserve">{esc(text)}</w:t></w:r>'


TOK = re.compile(r'(\[\[|\]\]|~~|\+\+|\*\*)')

def marked(text, side, size=9, base_color='000000'):
    """표시가 들어간 글 → runs. side: 'L' 원문, 'R' 시험."""
    st = dict(chg=False, strike=False, u=False, b=False)
    out = []
    for part in TOK.split(text):
        if part == '[[': st['chg'] = True; continue
        if part == ']]': st['chg'] = False; continue
        if part == '~~': st['strike'] = not st['strike']; continue
        if part == '++': st['u'] = not st['u']; continue
        if part == '**': st['b'] = not st['b']; continue
        if not part: continue
        color, fill, bold = base_color, None, st['b']
        if st['chg']:
            fill = L_FILL if side == 'L' else R_FILL
            color = BLUE if side == 'L' else RED
            bold = True
        if st['strike']: color = '9A9A9A'
        out.append(xrun(part, size, bold=bold, color=color, strike=st['strike'], underline=st['u'], fill=fill))
    return ''.join(out)


def p_xml(runs, *, before=0, after=120, line=280, rule='exact', jc='both', ind=None, border=None, shade=None, keep_next=False):
    pp = ['<w:pPr>']
    if keep_next: pp.append('<w:keepNext/>')
    if border:
        pp.append('<w:pBdr>' + ''.join(f'<w:{e} w:val="single" w:sz="6" w:space="4" w:color="{border}"/>' for e in ('top', 'left', 'bottom', 'right')) + '</w:pBdr>')
    if shade: pp.append(f'<w:shd w:val="clear" w:color="auto" w:fill="{shade}"/>')
    pp.append(f'<w:spacing w:before="{before}" w:after="{after}" w:line="{line}" w:lineRule="{rule}"/>')
    if ind: pp.append(ind)
    if jc: pp.append(f'<w:jc w:val="{jc}"/>')
    pp.append('</w:pPr>')
    return '<w:p>' + ''.join(pp) + runs + '</w:p>'


def column(paras, side):
    out = []
    for t in paras:
        if t.startswith('OPT:'):
            items = t[4:].split('|')
            for k, it in enumerate(items):
                out.append(p_xml(marked(it, side, 8.5), after=40 if k < len(items) - 1 else 120, line=250,
                                 jc='left', ind='<w:ind w:left="230" w:hanging="230"/>'))
        elif t.startswith('BOX:'):
            out.append(p_xml(marked(t[4:], side, 8.5), before=60, after=160, line=260, jc='both', border='8C8C8C', shade='FAFAFA',
                             ind='<w:ind w:left="90" w:right="90"/>'))
        else:
            full = t.startswith('[[') and t.endswith(']]')   # 통째로 표시된 문단은 왼쪽 정렬(양쪽 정렬 빈칸 방지)
            out.append(p_xml(marked(t, side, 9), after=150, line=275, jc='left' if full else 'both'))
    return ''.join(out) or p_xml('')


def tc(content, w, fill=None, borders=None, margins=None):
    pr = f'<w:tcW w:w="{w}" w:type="dxa"/>'
    if borders: pr += f'<w:tcBorders>{borders}</w:tcBorders>'
    if fill: pr += f'<w:shd w:val="clear" w:color="auto" w:fill="{fill}"/>'
    if margins: pr += margins
    return f'<w:tc><w:tcPr>{pr}</w:tcPr>{content}</w:tc>'


def tbl(rows_xml, grid, borders='', margins=(100, 140, 100, 140)):
    t, l, b, r = margins
    return (f'<w:tbl><w:tblPr><w:tblW w:w="{W}" w:type="dxa"/><w:tblLayout w:type="fixed"/>'
            + (f'<w:tblBorders>{borders}</w:tblBorders>' if borders else '')
            + f'<w:tblCellMar><w:top w:w="{t}" w:type="dxa"/><w:left w:w="{l}" w:type="dxa"/><w:bottom w:w="{b}" w:type="dxa"/><w:right w:w="{r}" w:type="dxa"/></w:tblCellMar></w:tblPr>'
            + '<w:tblGrid>' + ''.join(f'<w:gridCol w:w="{g}"/>' for g in grid) + '</w:tblGrid>' + rows_xml + '</w:tbl>')


def gap(after=200): return p_xml('', after=after, line=120)

NIL = '<w:top w:val="nil"/><w:left w:val="nil"/><w:bottom w:val="nil"/><w:right w:val="nil"/>'
LINES = ''.join(f'<w:{e} w:val="single" w:sz="4" w:space="0" w:color="BFC6D1"/>' for e in ('top', 'left', 'bottom', 'right', 'insideH', 'insideV'))


def set_block(i, s, first):
    out = []
    if not first:   # 새 쪽에서 시작 (pageBreakBefore라 앞 쪽이 꽉 차도 빈 쪽이 생기지 않는다)
        out.append('<w:p><w:pPr><w:pageBreakBefore/><w:spacing w:before="0" w:after="0" w:line="20" w:lineRule="exact"/></w:pPr></w:p>')
    # 머리: 번호 배지 + 제목
    badge = p_xml(xrun(f'{i:02d}', 16, bold=True, color='FFFFFF'), after=0, line=360, jc='center')
    head = (p_xml(xrun(s['no'], 13, bold=True, color=NAVY) + xrun('   ' + s['src'], 10, bold=True, color='333333'), after=60, line=320, jc='left')
            + p_xml(xrun(s['change'], 9.5, bold=True, color=RED) + xrun('   ·   ' + s['pts'], 9, color=GRAY), after=0, line=260, jc='left'))
    out.append(tbl('<w:tr><w:trPr><w:cantSplit/></w:trPr>' + tc(badge, 900, fill=NAVY, margins='<w:vAlign w:val="center"/>')
                   + tc(head, W - 900, borders=f'<w:bottom w:val="single" w:sz="12" w:space="0" w:color="{NAVY}"/>') + '</w:tr>',
                   [900, W - 900], margins=(80, 160, 80, 160)))
    out.append(gap(160))
    # 2단 비교 표
    half = W // 2
    rows = ('<w:tr><w:trPr><w:tblHeader/><w:cantSplit/></w:trPr>'
            + tc(p_xml(xrun('◀ 원문', 9.5, bold=True, color=BLUE), after=30, line=260, jc='left')
                 + p_xml(xrun(s['left_label'], 8, color=GRAY), after=0, line=230, jc='left'), half, fill='EAF2FB')
            + tc(p_xml(xrun('시험 문항 ▶', 9.5, bold=True, color=RED), after=30, line=260, jc='left')
                 + p_xml(xrun(s['right_label'], 8, color=GRAY), after=0, line=230, jc='left'), W - half, fill='FFF8DC')
            + '</w:tr>')
    for L, R in s['pairs']:
        rows += '<w:tr>' + tc(column(L, 'L'), half) + tc(column(R, 'R'), W - half) + '</w:tr>'
    out.append(tbl(rows, [half, W - half], borders=LINES, margins=(140, 150, 60, 150)))
    out.append(gap(150))
    # 바뀐 점
    pts = p_xml(xrun('바뀐 점', 10, bold=True, color=RED), after=100, line=280, jc='left', keep_next=True)
    pts += ''.join(p_xml(xrun('· ', 9) + marked(t, 'R', 9), after=80 if k < len(s['points']) - 1 else 0, line=275,
                         ind='<w:ind w:left="200" w:hanging="200"/>') for k, t in enumerate(s['points']))
    bd = f'<w:top w:val="nil"/><w:bottom w:val="nil"/><w:right w:val="nil"/><w:left w:val="single" w:sz="24" w:space="0" w:color="{RED}"/>'
    out.append(tbl('<w:tr><w:trPr><w:cantSplit/></w:trPr>' + tc(pts, W, fill='FDF3F2', borders=bd) + '</w:tr>', [W], margins=(120, 240, 120, 200)))
    return ''.join(out)


def intro():
    X = []
    X.append(p_xml(xrun(M['heading'], 17, bold=True, color='000000'), after=80, line=400, jc='left'))
    X.append(p_xml(xrun(M['sub'], 9, color=GRAY), after=320, line=280, jc='left'))
    X.append(p_xml(xrun(M['intro'], 9.5), after=260, line=300))
    # 읽는 법
    leg = [('[[바뀐 표현]]', 'L', '원문에서 시험에 바뀌어 나온 부분 (원래 표현)'),
           ('[[바뀐 표현]]', 'R', '시험에 바뀌어 나온 부분 · 새로 들어간 문장·문단 (시험 표현)'),
           ('~~빠진 부분~~', 'L', '원문에는 있지만 시험 지문에서 빠진 부분'),
           ('++밑줄++', 'R', '시험지에 그어진 밑줄 (①~⑤, (a)~(e))')]
    rows = ''.join('<w:tr><w:trPr><w:cantSplit/></w:trPr>' + tc(p_xml(marked(a, sd, 9.5), after=0, line=280, jc='center'), 2600)
                   + tc(p_xml(xrun(('왼쪽 원문 · ' if sd == 'L' else '오른쪽 시험 · ') + d, 9), after=0, line=280, jc='left'), W - 2600) + '</w:tr>'
                   for a, sd, d in leg)
    X.append(p_xml(xrun('읽는 법', 11, bold=True, color=RED), after=120, line=300, jc='left', keep_next=True))
    X.append(tbl(rows, [2600, W - 2600], borders=LINES, margins=(90, 140, 90, 140)))
    X.append(gap(240))
    # 목차
    X.append(p_xml(xrun('실린 문항', 11, bold=True, color=RED) + xrun('   ' + M.get('omitted', ''), 8, color=GRAY), after=120, line=300, jc='left', keep_next=True))
    head = ('<w:tr><w:trPr><w:tblHeader/></w:trPr>' + ''.join(tc(p_xml(xrun(h, 9, bold=True, color='FFFFFF'), after=0, line=260, jc='center'), w, fill=NAVY)
                                                            for h, w in zip(['', '문항', '출처', '바뀐 형태'], [700, 1900, 3300, 4300])) + '</w:tr>')
    body = ''
    for i, s in enumerate(SETS, 1):
        fill = 'F2F6FB' if i % 2 == 0 else None
        cells = [f'{i:02d}', s['no'], s['src'], s['change']]
        body += '<w:tr><w:trPr><w:cantSplit/></w:trPr>' + ''.join(
            tc(p_xml(xrun(c, 8.5, bold=(k < 2)), after=0, line=250, jc='center' if k < 2 else 'left'), w, fill=fill)
            for k, (c, w) in enumerate(zip(cells, [700, 1900, 3300, 4300]))) + '</w:tr>'
    X.append(tbl(head + body, [700, 1900, 3300, 4300], borders=LINES, margins=(70, 110, 70, 110)))
    return ''.join(X)


def main():
    global M, SETS
    ap = argparse.ArgumentParser(); ap.add_argument('data'); ap.add_argument('-o', '--out', required=True); a = ap.parse_args()
    D = json.load(open(a.data, encoding='utf-8')); M, SETS = D['meta'], D['sets']
    body = intro() + ''.join(set_block(i, s, False) for i, s in enumerate(SETS, 1))
    H = {'series': M['series'], 'label': '원문 비교'}
    B.emit(body, H, a.out)
    tmp = a.out + '.tmp'
    with zipfile.ZipFile(a.out) as zin, zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zout:
        for it in zin.infolist():
            d = zin.read(it.filename)
            if it.filename == 'word/header1.xml':
                d = d.decode().replace('>수업용 자료<', '>학생 배포용<', 1).encode()
            if it.filename == 'docProps/core.xml':
                d = re.sub(r'<dc:title>.*?</dc:title>|<dc:title/>', f'<dc:title>{esc(M["title"])}</dc:title>', d.decode()).encode()
            zout.writestr(it, d)
    os.replace(tmp, a.out)
    print(a.out, len(SETS), '세트')


if __name__ == '__main__':
    main()
