#!/usr/bin/env python3
"""성남 9개교 「교과별 교수·학습 및 평가계획」 추출기

한글(.hwp) · 한글XML(.hwpx) · PDF · PDF추출텍스트 · 폴더를 모두 받는다.
학교마다 표 짜임이 달라 어댑터를 나눠 둔다 (ADAPTERS 참고).

    python3 eval_parser.py 동광고 파일1 [파일2 ...]
"""
import os
import re
import json
import zlib
import struct
import zipfile
import xml.etree.ElementTree as ET

import olefile

# ══════════════════════════════════════════════════ 한글(.hwp) 읽기
TAG_PARA_TEXT = 67
TAG_LIST_HEADER = 73
TAG_TABLE = 87

CHAR1 = {0, 10, 13}                                      # 1 wchar
EXT = {1, 2, 3, 11, 12, 14, 15, 16, 17, 18, 21, 22, 23}  # 8 wchar
INLINE = {4, 5, 6, 7, 8, 9, 19, 20}                      # 8 wchar


def records(buf):
    i, n = 0, len(buf)
    while i + 4 <= n:
        (h,) = struct.unpack('<I', buf[i:i + 4])
        tag = h & 0x3FF
        size = (h >> 20) & 0xFFF
        i += 4
        if size == 0xFFF:
            (size,) = struct.unpack('<I', buf[i:i + 4])
            i += 4
        yield tag, buf[i:i + size]
        i += size


def para_text(data):
    out = []
    i, n = 0, len(data)
    while i + 2 <= n:
        (c,) = struct.unpack('<H', data[i:i + 2])
        if c in CHAR1:
            out.append('\n' if c in (10, 13) else '')
            i += 2
        elif c in EXT or c in INLINE:
            i += 16
        elif c < 32:
            i += 2
        elif 0xD800 <= c <= 0xDFFF:   # 짝 없는 서러게이트 — 버린다
            i += 2
        else:
            out.append(chr(c))
            i += 2
    return ''.join(out)


def hwp_read(path):
    """섹션별 텍스트. 표 셀은 ' ¦ '로 구분한다."""
    f = olefile.OleFileIO(path)
    (hdr,) = struct.unpack('<I', f.openstream('FileHeader').read()[36:40])
    compressed = bool(hdr & 1)
    secs = sorted([e[1] for e in f.listdir() if e[0] == 'BodyText'],
                  key=lambda s: int(s.replace('Section', '')))
    out = []
    for s in secs:
        raw = f.openstream('BodyText/' + s).read()
        buf = zlib.decompress(raw, -15) if compressed else raw
        parts = []
        for tag, data in records(buf):
            if tag == TAG_TABLE:
                parts.append('\n[표]\n')
            elif tag == TAG_LIST_HEADER:
                parts.append(' ¦ ')
            elif tag == TAG_PARA_TEXT:
                t = para_text(data).strip('\n')
                if t:
                    parts.append(t + '\n')
        out.append(''.join(parts))
    f.close()
    return out


# ══════════════════════════════════════════════════ 한글XML(.hwpx) 읽기
def _xns(tag):
    return tag.rsplit('}', 1)[-1]


def _xpara(el):
    out = []
    for node in el.iter():
        if _xns(node.tag) == 't':
            if node.text:
                out.append(node.text)
            for sub in node:          # <t> 안 마크업 뒤 tail 도 살린다
                if sub.tail:
                    out.append(sub.tail)
    return ''.join(out)


def _xsec(xml_bytes):
    root = ET.fromstring(xml_bytes)
    lines = []
    for el in root.iter():
        if _xns(el.tag) != 'p':
            continue
        # 표를 품은 문단은 건너뛴다 (셀 문단이 따로 나오므로 중복)
        if any(_xns(d.tag) == 'p' for d in el.iter() if d is not el):
            continue
        t = _xpara(el).strip()
        if t:
            lines.append(t)
    return '\n'.join(lines)


def hwpx_read(path):
    z = zipfile.ZipFile(path)
    names = [n for n in z.namelist()
             if re.match(r'Contents/section\d+\.xml$', n)]
    names.sort(key=lambda n: int(re.search(r'section(\d+)', n).group(1)))
    return [_xsec(z.read(n)) for n in names]


# ══════════════════════════════════════════════════ 공통
CORE = ['공통국어', '공통수학', '공통영어', '한국사', '통합사회', '통합과학']
ANCHOR = r'평가의\s*종류와\s*반영\s*?비율|\d\s*평가\s*반영\s*비율'
KIND = r'선택형|논술형|논술혈'


def find_anchor(f):
    """앵커가 여러 번 나오면 뒤에 '정기시험/지필평가'가 붙은 것을 고른다"""
    last = None
    for m in re.finditer(ANCHOR, f):
        if re.search(r'정기시험|지필평가', f[m.end():m.end() + 300]):
            return m
        last = m
    return last


def flat(s):
    return re.sub(r'[ \t]+', ' ', s)


def num(s):
    f = float(s)
    return int(f) if f == int(f) else f


def ratio(a, b):
    t = a + b
    return '' if t == 0 else '%g:%g' % (round(a / t * 100, 1), round(b / t * 100, 1))


def base(s):
    return re.sub(r'[12]$', '', s)


# ══════════════════════════════════════════════════ 파일 → 과목 블록
SPLITTERS = [
    # 동광고·성남고·성남여고식 — 과목이 괄호 안
    re.compile(r'\d{4}학년도\s*\(?\s*\d\s*\)?\s*학기\s*(?:\(?\s*\d\s*\)?\s*학년\s*)?'
               r'[(\[]\s*([^)\]\n]{2,24}?)\s*[)\]]\s*과?\s*교수'),
    # 위례한빛고·풍생고식 — 괄호 없이 'N학년 과목명 교수·학습'
    re.compile(r'\d{4}학년도\s*\d학기\s*(?:\d학년\s*)?([가-힣A-Za-z0-9]{2,12})\s*'
               r'교수\s*[·∙․ㆍ･]?\s*학습'),
    # 성일고식 — 괄호 과목명 다음 줄에 'N학기 교수학습'
    re.compile(r'[(\[]\s*([^)\]\n]{2,24}?)\s*[)\]]\s*\n?\s*\d\s*학기\s*교수\s*[·∙․ㆍ･]?\s*학습'),
    # 복정고식 — 쪽머리글에 [과목]
    re.compile(r'\d{4}학년도\s*\d학기\s*\[\s*([^\]\n]{2,20}?)\s*\]'),
]


def pdf_text(path):
    import pdfplumber
    with pdfplumber.open(path) as pdf:
        return '\n'.join((pg.extract_text() or '') for pg in pdf.pages)


def sections_from_txt(path, txt=None):
    if txt is None:
        txt = open(path, encoding='utf-8').read()
    for pat in SPLITTERS:
        marks = list(pat.finditer(txt))
        if len(marks) >= 3:
            groups, order = {}, []
            for i, m in enumerate(marks):
                name = re.sub(r'\s+', '', m.group(0))   # 제목 전체가 열쇠
                end = marks[i + 1].start() if i + 1 < len(marks) else len(txt)
                if name not in groups:
                    groups[name] = []
                    order.append(name)
                groups[name].append(txt[m.start():end])
            return [''.join(groups[n]) for n in order]
    return [txt]


def load(path):
    p = path.lower()
    if p.endswith('.hwpx'):
        return hwpx_read(path)
    if p.endswith('.hwp'):
        return hwp_read(path)
    if p.endswith('.pdf'):
        return sections_from_txt(path, pdf_text(path))
    return sections_from_txt(path)


# ══════════════════════════════════════════════════ 공통 필드
SPLIT_PATS = [
    r'분할점수\s*산출\s*방식\s*:\s*[^\n]{0,40}?(추정|고정)분할',
    r'gfedcb\s*성취수준별\s*(추정|고정)분할',          # 체크박스가 켜진 쪽
    r'성취수준별\s*(추정|고정)분할\s*점수를\s*사용',
    r'성취수준별\s*(추정|고정)분할\s*점수\s*방식을\s*활용',
    r'성취수준별\s*(추정|고정)분할에\s*의한\s*산출',
    r'성취수준별\s*(추정|고정)\s*분할점수를\s*적용',
    r'(고정|추정)\s*분할점수제를\s*운영',
]


def split_method(block):
    f = flat(block)
    for pat in SPLIT_PATS:
        m = re.search(pat, f)
        if m:
            return m.group(1) + '분할'
    hits = set(re.findall(r'성취수준별\s*(추정|고정)분할', f))
    return (hits.pop() + '분할') if len(hits) == 1 else None


ITEM_PATS = [
    r'평가\s*영역\s*명\s*\d*\s*(.*?)\s*영역\s*만점\s*(\d+)\s*점?',
    r'평가\s*영역\s*명\s*\d*\s*(.*?)\s*평가\s*만점\s*(\d+)\s*점?',
    r'평가\s*영역\s*\d*\s*(.*?)\s*영역\s*만점\s*(\d+)\s*점?',
]


def perf_raw(block):
    """(이름, 배점) 목록. PDF에서 이름이 날아간 칸도 자리를 지킨다."""
    f = re.sub(r'\s+', ' ', block)
    out, seen = [], []
    for pat in ITEM_PATS:
        for nm, pt in re.findall(pat, f):
            nm = nm.strip(' .·ㆍ')
            if len(nm) > 45 or (nm and nm in seen):
                continue
            seen.append(nm)
            out.append((nm or '(이름 확인 필요)', int(pt)))
        if out:
            break
    return out


def cut_to(items, total):
    """배점을 앞에서부터 더해 수행평가 총%에 닿는 데까지만 남긴다"""
    if not total:
        return items
    acc = 0
    for i, (_, pt) in enumerate(items):
        acc += pt
        if acc == total:
            return items[:i + 1]
    return items


def perf_items(block, total=None):
    return ', '.join('%s(%d)' % (n, p)
                     for n, p in cut_to(perf_raw(block), total))


def perf_points(block, total=None):
    return [p for _, p in cut_to(perf_raw(block), total)]


def subject_of(block):
    for pat in SPLITTERS:
        m = pat.search(block)
        if m:
            return re.sub(r'\s+', '', m.group(1))
    return None


def term_of(block):
    m = re.search(r'\d{4}학년도\s*\(?\s*(\d)\s*\)?\s*학기', block)
    if not m:
        m = re.search(r'(\d)\s*학기\s*교수\s*[·∙․ㆍ･]?\s*학습', block)
    return (m.group(1) + '학기') if m else None


def kinds_line(text):
    """유형 줄 고르기 — '선택형'이 든 마지막 줄을 우선한다"""
    ls = [l for l in text.split('\n') if re.search(KIND, l)]
    if not ls:
        return None
    sel = [l for l in ls if '선택형' in l]
    return (sel or ls)[-1]


def group_rounds(cells, kinds):
    """지필 칸을 차수별로 묶는다. 선택형이 나올 때마다 새 차수.

    빈 칸을 아예 지워 버린 문서(성남여고 2학기)는 선택형이 한 번만 잡혀
    차수가 어긋나므로, 칸 수가 짝수면 절반씩 나눠 다시 묶는다.
    """
    rounds, cur = [], None
    for x, k in enumerate(kinds):
        if k == '선택형' or cur is None:
            cur = {'sel': 0, 'ess': 0}
            rounds.append(cur)
        cur['sel' if k == '선택형' else 'ess'] += cells[x]
    if len(rounds) == 2:
        return rounds
    n = len(cells)
    if n >= 2 and n % 2 == 0:
        half = n // 2
        return [{'sel': part[0], 'ess': sum(part[1:])}
                for part in (cells[:half], cells[half:])]
    return rounds


def finish(rounds, exam_pct, each=None):
    """차수 묶음을 결과 dict 로"""
    if not rounds:
        return {}
    v = each if each is not None else round(exam_pct / len(rounds), 2)
    out = {'%d차' % i: v for i in range(1, min(len(rounds), 2) + 1)}
    rs = [ratio(rd['sel'], rd['ess']) for rd in rounds]
    out['객관식:서술형'] = rs[0] if len(set(rs)) == 1 else ' '.join(rs)
    return out


# ══════════════════════════════════════════════════ 학교별 표 해석
def shape_donggwang(block):
    """기본값 — 'N차(M%)' 와 '선택형 논술형 선택형 논술형' + 점(%) 네 쌍"""
    f = re.sub(r'\s+', ' ', block)
    a = re.search(r'평가의\s*종류와\s*반영\s*비율', f)
    if not a:
        return {}
    seg = f[a.end():a.end() + 1400]
    m = re.search(r'선택형 논술형 선택형 논술형', seg)
    if not m:
        return {}
    pts = re.findall(r'(\d+(?:\.\d+)?)점\s*\(\s*(\d+(?:\.\d+)?)\s*%\s*\)',
                     seg[m.end():m.end() + 400])
    if len(pts) < 4:
        return {}
    (s1, r1), (n1, w1), (s2, r2), (n2, w2) = [(num(x), num(y)) for x, y in pts[:4]]
    return {'1차': round(r1 + w1, 2), '2차': round(r2 + w2, 2),
            '객관식:서술형': ratio(s1 + s2, n1 + n2)}


def shape_seongnam(block, exam_pct, perf_pct):
    """성남고 — 수행 배점이 곧 반영비율이라 '배점' 줄을 뒤에서 끊는다

    배점: 76점 24점 100점 | 20점 20점 5점 5점   (뒤 네 칸 합 50 = 수행 50%)
    유형: 선택형 논술형 선택형 | …             (선택형마다 새 차수)
    """
    f = flat(block)
    a = re.search(r'평가의\s*종류와\s*반영\s*비율', f)
    if not a or exam_pct is None or perf_pct is None:
        return {}
    seg = f[a.end():a.end() + 1200]
    mb = re.search(r'\n\s*배점\s*([^\n]+)', seg)
    if not mb:
        return {}
    head = seg[:mb.start()]
    i = head.find('선택형')
    if i < 0:
        return {}
    pts = [num(x) for x in re.findall(r'(\d+(?:\.\d+)?)\s*점', mb.group(1))]
    kinds = re.findall(r'선택형|논술형', head[i:])
    acc, n_ex = 0, None
    for x in range(len(pts) - 1, -1, -1):
        acc += pts[x]
        if abs(acc - perf_pct) < 1e-6:
            n_ex = x
            break
    if not n_ex or n_ex > len(kinds):
        return {}
    return finish(group_rounds(pts[:n_ex], kinds[:n_ex]), exam_pct)


def shape_sungil(block, exam_pct):
    """성일고 — 만점 줄의 %를 앞에서 더해 정기시험 총%에 닿는 데까지가 지필"""
    f = flat(block)
    a = find_anchor(f)
    if not a or exam_pct is None:
        return {}
    seg = f[a.end():a.end() + 1600]
    j = re.search(r'만점\s*\n?\s*\(\s*반영\s*비율\s*\)', seg)
    if not j:
        return {}
    line = kinds_line(seg[:j.start()])
    if not line:
        return {}
    kinds = re.findall(KIND, line)
    k = re.search(r'논술형\s*평가|평가\s*시기|평가\s*내용', seg[j.end():])
    body = seg[j.end(): j.end() + (k.start() if k else 700)]
    pts = [num(x) for x in re.findall(r'(\d+(?:\.\d+)?)\s*점', body)]
    pcts = [num(x) for x in re.findall(r'\(\s*(\d+(?:\.\d+)?)\s*%\s*\)', body)]
    acc, n_ex = 0, None
    for x, v in enumerate(pcts):
        acc += v
        if abs(acc - exam_pct) < 1e-6:
            n_ex = x + 1
            break
    if not n_ex or n_ex > min(len(pts), len(kinds)):
        return {}
    ks = ['선택형' if k0 == '선택형' else '논술형' for k0 in kinds[:n_ex]]
    return finish(group_rounds(pts[:n_ex], ks), exam_pct)


def shape_pungsaeng(block, exam_pct):
    """풍생고 — PDF에서 퍼센트가 줄바꿈으로 쪼개진다.
    「논술형 평가 반영비율」 줄의 지필 몫만 빼서 객관:서술을 구한다."""
    f = flat(block)
    a = find_anchor(f)
    j = re.search(r'영역\s*만점', f[a.end():]) if a else None
    if not a or not j or exam_pct is None:
        return {}
    seg = f[a.end():]
    line = kinds_line(seg[:j.start()])
    if not line:
        return {}
    kinds = re.findall(KIND, line)
    n_sel = kinds.count('선택형')
    n_ess = len(kinds) - n_sel
    m = re.search(r'논술형\s*평가', seg[j.start():])
    if not m or n_sel < 1:
        return {}
    tail = seg[j.start() + m.end(): j.start() + m.end() + 300]
    row = next((l for l in tail.split('\n') if l.count('%') >= 2), None)
    if row is None:
        return {}
    vs = [num(x) for x in re.findall(r'(\d+(?:\.\d+)?)\s*%', row)]
    ess = round(sum(vs[:n_ess]), 2) if n_ess else 0
    each = round(exam_pct / n_sel, 2)
    out = {'%d차' % i: each for i in range(1, min(n_sel, 2) + 1)}
    out['객관식:서술형'] = ratio(round(exam_pct - ess, 2), ess)
    return out


def shape_wirye(block, exam_pct):
    """위례한빛고·효성고 — PDF라 배점 줄과 % 줄이 어긋난다. %만으로 센다.
    위례한빛고 국어처럼 1차와 2차가 다를 수 있어 차수별 합을 그대로 쓴다."""
    f = flat(block)
    a = find_anchor(f)
    j = re.search(r'영역\s*만점', f[a.end():]) if a else None
    if not a or not j or exam_pct is None:
        return {}
    seg = f[a.end():]
    line = kinds_line(seg[:j.start()])
    if not line:
        return {}
    kinds = re.findall(KIND, line)
    body = seg[j.start(): j.start() + 700]
    pcts = [num(x) for x in re.findall(r'\(\s*(\d+(?:\.\d+)?)\s*%\s*\)', body)]
    acc, n_ex = 0, None
    for x, v in enumerate(pcts):
        acc += v
        if abs(acc - exam_pct) < 1e-6:
            n_ex = x + 1
            break
    if not n_ex or n_ex > len(kinds):
        return {}
    ks = ['선택형' if k == '선택형' else '논술형' for k in kinds[:n_ex]]
    rounds = group_rounds(pcts[:n_ex], ks)
    if not rounds:
        return {}
    out = {}
    for i, rd in enumerate(rounds[:2], 1):
        out['%d차' % i] = round(rd['sel'] + rd['ess'], 2)
    rs = [ratio(rd['sel'], rd['ess']) for rd in rounds]
    out['객관식:서술형'] = rs[0] if len(set(rs)) == 1 else ' '.join(rs)
    return out


TABLE_HEAD = (r'(?:구분|평가\s*(?:종류|유형)?)\s*\n?\s*(?:정기시험|지필평가)'
              r'\s*\n?\s*수행평가')


def shape_cells(block, exam_pct, perf_pts, perf_total=None):
    """동광고·복정고·성남여고·숭신고 — 「영역 만점」 칸을 빈 칸(ㆍ, -)까지
    세고, 수행평가 배점 수열이 나타나는 자리를 찾아 그 앞을 지필로 본다."""
    f = flat(block)
    h = re.search(TABLE_HEAD, f)         # 앵커와 표가 멀 수 있어 표 머리를 직접
    a = h or find_anchor(f)
    if not a or exam_pct is None or not perf_pts:
        return {}
    seg = f[a.end():a.end() + 2200]
    i = seg.find('선택형')
    j = re.search(r'영역\s*만점', seg)
    if i < 0 or not j:
        return {}
    kinds = re.findall(r'선택형|논술형', seg[i:j.start()])
    k = re.search(r'논술형\s*평가|평가\s*시기|성취기준', seg[j.end():])
    body = seg[j.end(): j.end() + (k.start() if k else 900)]
    toks = re.findall(r'(\d+(?:\.\d+)?)\s*점'
                      r'|(\d+(?:\.\d+)?)\s*\(\s*\d+(?:\.\d+)?\s*%\s*\)'
                      r'|([ㆍ\-–])', body)
    cells = [0 if t[2] else num(t[0] or t[1]) for t in toks]
    n = len(perf_pts)
    n_ex = None
    for x in range(len(cells) - n, 0, -1):
        if cells[x:x + n] == perf_pts:
            n_ex = x
            break
    if n_ex is None and perf_total:
        # 수행 항목 하나가 표에서 여러 칸으로 쪼개진 경우 — 뒤에서 총합으로 끊는다
        acc = 0
        for x in range(len(cells) - 1, 0, -1):
            acc += cells[x]
            if abs(acc - perf_total) < 1e-6:
                n_ex = x
                break
    if not n_ex or n_ex > len(kinds):
        return {}
    return finish(group_rounds(cells[:n_ex], kinds[:n_ex]), exam_pct)


ADAPTERS = {
    '동광고': 'cells', '복정고': 'cells', '성남여고': 'cells', '숭신고': 'cells',
    '성남고': 'seongnam', '성일고': 'sungil',
    '위례한빛고': 'wirye', '효성고': 'wirye', '풍생고': 'pungsaeng',
}


def totals(block):
    """정기시험 총% · 수행평가 총%"""
    f = flat(block)
    one_line = re.sub(r'\n', ' ', f)
    HEAD = r'(?:구분|평가(?:\s*(?:종류|유형))?)'
    m = re.search(r'정기\s*시험\s*\(\s*(\d+(?:\.\d+)?)\s*%\s*\)\s*'
                  r'수행평가\s*\(\s*(\d+(?:\.\d+)?)\s*%\s*\)', f)
    if m:
        return num(m.group(1)), num(m.group(2))
    m = re.search(HEAD + r'\s*(?:정기시험|지필평가)\s*수행평가\s*'
                  r'반영\s*비율\s*((?:\d+(?:\.\d+)?\s*%\s*){2,})', one_line)
    if m:
        vs = [num(x) for x in re.findall(r'(\d+(?:\.\d+)?)\s*%', m.group(1))]
        return vs[0], round(sum(vs[1:]), 2)      # 수행이 여러 칸으로 쪼개진 경우
    m = re.search(HEAD + r'\s*(?:정기시험|지필평가)\s*수행평가\s*(?:계|합계)\s*'
                  r'반영\s*비율\s*\n?\s*(?:\(\s*%\s*\))?\s*(\d+)\s*%?\s+(\d+)\s*%?',
                  one_line)
    if m:
        return int(m.group(1)), int(m.group(2))
    m = re.search(HEAD + r'\s*수행평가\s*(?:계|합계)\s*'
                  r'반영\s*비율\s*(?:\(\s*%\s*\))?\s*(\d+)', one_line)
    if m:
        return 0, int(m.group(1))
    return None, None


def one(block, school):
    subj = subject_of(block)
    if not subj or not re.search(ANCHOR, flat(block)):
        return None
    r = {'학교명': school, '학기': term_of(block) or '?', '과목': subj}
    r['지필계'], r['수행'] = totals(block)
    r['수행평가 세부반영사항'] = perf_items(block, r['수행'])
    kind = ADAPTERS.get(school)
    if kind == 'seongnam':
        r.update(shape_seongnam(block, r['지필계'], r['수행']))
    elif kind == 'pungsaeng':
        r.update(shape_pungsaeng(block, r['지필계']))
    elif kind == 'wirye':
        r.update(shape_wirye(block, r['지필계']))
    elif kind == 'sungil':
        r.update(shape_sungil(block, r['지필계']))
    elif kind == 'cells':
        r.update(shape_cells(block, r['지필계'],
                             perf_points(block, r['수행']), r['수행']))
    else:
        r.update(shape_donggwang(block))
    r['분할방식'] = split_method(block)
    return r


def extract(path, school):
    """파일 하나, 또는 과목별 파일이 든 폴더"""
    if os.path.isdir(path):
        out = []
        for f in sorted(os.listdir(path)):
            if f.lower().endswith(('.hwp', '.hwpx', '.txt', '.pdf')):
                out += [x for x in (one(b, school)
                                    for b in load(os.path.join(path, f))) if x]
        return out
    return [x for x in (one(b, school) for b in load(path)) if x]


def core_only(rows):
    return [r for r in rows if base(r['과목']) in CORE]


if __name__ == '__main__':
    import sys
    rows = []
    for p in sys.argv[2:]:
        rows += extract(p, sys.argv[1])
    print(json.dumps(rows, ensure_ascii=False, indent=1))
