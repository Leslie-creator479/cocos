# -*- coding: utf-8 -*-
"""학교별 내신 분석 report.json → COCOS 원지문 공식 틀 .docx (그다음 soffice로 .pdf).

머리글·바닥글·용지·여백·글꼴은 cocos-wonjimun의 assets/template.docx와 build_docx.py를 그대로 쓴다
(본문만 새로 찍는다). 정답은 넣지 않는다.

    python3 build_report.py report.json -o 출력.docx

report.json = {"header": {"series", "label", "sub", "title"}, "blocks": [...]}
블록(배열 첫 칸이 종류):
  ["title", 글]  ["sub", 글]  ["h1", 글]  ["h2", 글]  ["p", 글]  ["bullet", 글]  ["note", 글]  ["pagebreak"]
  ["table", 머리칸[], 행[][], 너비비율[], 가운데칸번호[], 첫칸굵게(bool)]
  ["bars", [[이름, 문항수, 배점], ...], 최댓값, 색[] (행마다 'RRGGBB')]
  ["item", 굵은 소제목, [글머리 문장, ...]]
글 안의 **…**는 굵게. h1 앞에 pagebreak를 두면 그 h1은 위 여백 없이 쪽 맨 위에서 시작한다.
"""
import sys, re, os, glob, json, zipfile, argparse
CANDS = glob.glob('/root/.claude/plugins/synced/*/cocos/skills/cocos-wonjimun/scripts') + glob.glob('/mnt/skills/plugins/cocos*/skills/cocos-wonjimun/scripts') + glob.glob('/mnt/skills/plugins/*/cocos-wonjimun/scripts')
if not CANDS:
    raise SystemExit('cocos-wonjimun 스킬의 scripts 폴더를 찾지 못했다. 경로를 CANDS에 더한다.')
sys.path.insert(0, CANDS[0])
import build_docx as B
from build_docx import run, para, esc, FONTS

RED, BLUE, GRAY, LINE = 'E03C31', '1F5FA9', '595959', 'BFBFBF'
W = 10200  # 본문 폭(twip)

def r(t, size=9.5, **k): return run(t, size, **k)

def rich(text, size=9.5, color='000000'):
    """**굵게** 표시를 runs로."""
    out = []
    for i, part in enumerate(re.split(r'\*\*(.+?)\*\*', text)):
        if part: out.append(run(part, size, bold=bool(i % 2), color=color))
    return out

def title(t): return para([r(t, 16, bold=True)], before=0, after=80, line=360, rule='exact')
def sub(t): return para([r(t, 9, color=GRAY)], after=280, line=280, rule='exact')
def h1(t): return para([r(t, 13, bold=True)], before=520, after=180, line=320, rule='exact', keep_next=True)
def h2(t): return para([r(t, 11, bold=True, color=RED)], before=320, after=140, line=300, rule='exact', keep_next=True)
def p(t, before=0, after=200, size=9.5): return para(rich(t, size), before=before, after=after, line=310, rule='exact', justify=True)
def bullet(t, size=9.5):
    return para([r('· ', size)] + rich(t, size), after=110, line=300, rule='exact', ind=240, hanging=240, justify=True)
def note(t): return para(rich(t, 8.5, GRAY), before=100, after=160, line=270, rule='exact')

def cell(text, w, *, head=False, fill=None, bold=False, center=False, size=8.5, keep=False):
    shade = BLUE if head else fill
    runs = rich(text, size, 'FFFFFF' if head else '000000') if not head else [run(text, size, bold=True, color='FFFFFF')]
    if bold and not head: runs = [run(text, size, bold=True)]
    jc = '<w:jc w:val="center"/>' if (center or head) else ''
    kn = '<w:keepNext/>' if keep else ''
    pp = (f'<w:p><w:pPr>{kn}<w:spacing w:before="0" w:after="0" w:line="250" w:lineRule="atLeast"/>{jc}</w:pPr>'
          + ''.join(runs) + '</w:p>')
    tc = f'<w:tcW w:w="{w}" w:type="dxa"/><w:vAlign w:val="center"/>'
    if shade: tc += f'<w:shd w:val="clear" w:color="auto" w:fill="{shade}"/>'
    return f'<w:tc><w:tcPr>{tc}</w:tcPr>{pp}</w:tc>'

def table(head, rows, widths, *, center_cols=(), bold_col0=False, after=260):
    s = sum(widths); widths = [round(w * W / s) for w in widths]
    b = ''.join(f'<w:{e} w:val="single" w:sz="4" w:space="0" w:color="{LINE}"/>' for e in ('top', 'left', 'bottom', 'right', 'insideH', 'insideV'))
    x = [f'<w:tbl><w:tblPr><w:tblW w:w="{W}" w:type="dxa"/><w:tblBorders>{b}</w:tblBorders>'
         '<w:tblLayout w:type="fixed"/><w:tblCellMar><w:top w:w="55" w:type="dxa"/><w:left w:w="90" w:type="dxa"/>'
         '<w:bottom w:w="55" w:type="dxa"/><w:right w:w="90" w:type="dxa"/></w:tblCellMar></w:tblPr><w:tblGrid>'
         + ''.join(f'<w:gridCol w:w="{w}"/>' for w in widths) + '</w:tblGrid>']
    keep = len(rows) <= 12   # 짧은 표는 쪽에서 갈리지 않게 통째로 묶는다
    x.append('<w:tr><w:trPr><w:tblHeader/><w:cantSplit/></w:trPr>' + ''.join(cell(h, w, head=True, keep=keep) for h, w in zip(head, widths)) + '</w:tr>')
    for i, row in enumerate(rows):
        fill = 'F2F6FB' if i % 2 else None
        x.append('<w:tr><w:trPr><w:cantSplit/></w:trPr>' + ''.join(
            cell(str(c), w, fill=fill, center=(j in center_cols), bold=(bold_col0 and j == 0), keep=keep and i < len(rows) - 1) for j, (c, w) in enumerate(zip(row, widths))) + '</w:tr>')
    x.append('</w:tbl>')
    return ''.join(x) + para([r('', 4)], after=after, line=120, rule='exact')

def bar_table(rows, maxv, colors):
    """유형별 배점을 칸 채우기로 그린 가로 막대(표 하나)."""
    s = [2600, 4900, 2700]
    out = [f'<w:tbl><w:tblPr><w:tblW w:w="{W}" w:type="dxa"/><w:tblLayout w:type="fixed"/>'
           '<w:tblCellMar><w:top w:w="40" w:type="dxa"/><w:left w:w="80" w:type="dxa"/><w:bottom w:w="40" w:type="dxa"/><w:right w:w="80" w:type="dxa"/></w:tblCellMar></w:tblPr><w:tblGrid>'
           + ''.join(f'<w:gridCol w:w="{w}"/>' for w in s) + '</w:tblGrid>']
    for k, (name, n, pts) in enumerate(rows):
        col = colors[k]
        kn = '<w:keepNext/>' if k < len(rows) - 1 else ''
        bw = max(120, round(s[1] * 0.92 * pts / maxv))
        bar = (f'<w:tbl><w:tblPr><w:tblW w:w="{bw}" w:type="dxa"/><w:tblLayout w:type="fixed"/>'
               '<w:tblCellMar><w:top w:w="0" w:type="dxa"/><w:left w:w="0" w:type="dxa"/><w:bottom w:w="0" w:type="dxa"/><w:right w:w="0" w:type="dxa"/></w:tblCellMar></w:tblPr>'
               f'<w:tblGrid><w:gridCol w:w="{bw}"/></w:tblGrid><w:tr><w:trPr><w:trHeight w:val="230" w:hRule="exact"/></w:trPr>'
               f'<w:tc><w:tcPr><w:tcW w:w="{bw}" w:type="dxa"/><w:shd w:val="clear" w:color="auto" w:fill="{col}"/></w:tcPr><w:p><w:pPr><w:spacing w:before="0" w:after="0" w:line="200" w:lineRule="exact"/></w:pPr></w:p></w:tc></w:tr></w:tbl>'
               '<w:p><w:pPr><w:spacing w:before="0" w:after="0" w:line="20" w:lineRule="exact"/></w:pPr></w:p>')
        out.append('<w:tr><w:trPr><w:cantSplit/></w:trPr>'
                   f'<w:tc><w:tcPr><w:tcW w:w="{s[0]}" w:type="dxa"/><w:vAlign w:val="center"/></w:tcPr><w:p><w:pPr>{kn}<w:spacing w:before="0" w:after="0" w:line="250" w:lineRule="atLeast"/><w:jc w:val="right"/></w:pPr>{run(name, 9, bold=True)}</w:p></w:tc>'
                   f'<w:tc><w:tcPr><w:tcW w:w="{s[1]}" w:type="dxa"/><w:vAlign w:val="center"/></w:tcPr>{bar}</w:tc>'
                   f'<w:tc><w:tcPr><w:tcW w:w="{s[2]}" w:type="dxa"/><w:vAlign w:val="center"/></w:tcPr><w:p><w:pPr><w:spacing w:before="0" w:after="0" w:line="250" w:lineRule="atLeast"/></w:pPr>{run(f"{pts:.1f}점", 9, bold=True)}{run(f"  ({n}문항)", 8.5, color=GRAY)}</w:p></w:tc></w:tr>')
    out.append('</w:tbl>')
    return ''.join(out) + para([r('', 4)], after=220, line=120, rule='exact')

def item_box(head, lines):
    """문항 하나 = 왼쪽 파란 띠 + 옅은 바탕 칸. 칸 사이를 띄워 번호별로 또렷이 나눈다."""
    hp = (f'<w:p><w:pPr><w:keepNext/><w:spacing w:before="0" w:after="120" w:line="300" w:lineRule="exact"/></w:pPr>'
          + run(head, 10, bold=True, color=BLUE) + '</w:p>')
    bp = ''.join(
        f'<w:p><w:pPr><w:spacing w:before="0" w:after="{90 if i < len(lines) - 1 else 0}" w:line="290" w:lineRule="exact"/>'
        '<w:ind w:left="220" w:hanging="220"/><w:jc w:val="both"/></w:pPr>'
        + run('· ', 9) + ''.join(rich(t, 9)) + '</w:p>' for i, t in enumerate(lines))
    bd = (f'<w:top w:val="nil"/><w:bottom w:val="nil"/><w:right w:val="nil"/>'
          f'<w:left w:val="single" w:sz="24" w:space="0" w:color="{BLUE}"/>')
    return (f'<w:tbl><w:tblPr><w:tblW w:w="{W}" w:type="dxa"/><w:tblLayout w:type="fixed"/>'
            '<w:tblCellMar><w:top w:w="140" w:type="dxa"/><w:left w:w="220" w:type="dxa"/>'
            '<w:bottom w:w="140" w:type="dxa"/><w:right w:w="200" w:type="dxa"/></w:tblCellMar></w:tblPr>'
            f'<w:tblGrid><w:gridCol w:w="{W}"/></w:tblGrid><w:tr><w:trPr><w:cantSplit/></w:trPr>'
            f'<w:tc><w:tcPr><w:tcW w:w="{W}" w:type="dxa"/><w:tcBorders>{bd}</w:tcBorders>'
            '<w:shd w:val="clear" w:color="auto" w:fill="F4F7FB"/></w:tcPr>'
            + hp + bp + '</w:tc></w:tr></w:tbl>'
            + para([r('', 4)], after=200, line=120, rule='exact'))

def pagebreak(): return para([], page_break=True)

def render(blocks):
    X, after_break = [], False
    for b in blocks:
        k = b[0]
        if k == 'title': X.append(title(b[1]))
        elif k == 'sub': X.append(sub(b[1]))
        elif k == 'h1':
            x = h1(b[1])
            X.append(x.replace('w:before="520"', 'w:before="0"') if after_break else x)
        elif k == 'h2': X.append(h2(b[1]))
        elif k == 'p': X.append(p(b[1]))
        elif k == 'bullet': X.append(bullet(b[1], b[2] if len(b) > 2 else 9.5))
        elif k == 'note': X.append(note(b[1]))
        elif k == 'pagebreak': X.append(pagebreak())
        elif k == 'table':
            X.append(table(b[1], b[2], b[3], center_cols=tuple(b[4]) if len(b) > 4 else (), bold_col0=bool(b[5]) if len(b) > 5 else False))
        elif k == 'bars': X.append(bar_table(b[1], b[2], b[3]))
        elif k == 'item': X.append(item_box(b[1], b[2]))
        else: raise SystemExit(f'모르는 블록: {k}')
        after_break = (k == 'pagebreak')
    return ''.join(X)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('report'); ap.add_argument('-o', '--out', required=True)
    a = ap.parse_args()
    R = json.load(open(a.report, encoding='utf-8'))
    H = R['header']
    if not H.get('series'):
        raise SystemExit('header.series(머리글 자료명)를 넣어야 한다.')
    B.emit(render(R['blocks']), H, a.out)
    tmp = a.out + '.tmp'
    with zipfile.ZipFile(a.out) as zin, zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zout:
        for it in zin.infolist():
            d = zin.read(it.filename)
            if it.filename == 'word/header1.xml' and H.get('sub'):
                d = d.decode().replace('>수업용 자료<', '>' + esc(H['sub']) + '<', 1).encode()
            if it.filename == 'docProps/core.xml' and H.get('title'):
                d = re.sub(r'<dc:title>.*?</dc:title>|<dc:title/>', f'<dc:title>{esc(H["title"])}</dc:title>', d.decode()).encode()
            zout.writestr(it, d)
    os.replace(tmp, a.out)
    print(a.out)


if __name__ == '__main__':
    main()
