# -*- coding: utf-8 -*-
"""시험지 스캔 PDF와 시험 범위 원지문 PDF를 낱말 단위로 대조해, 지문마다 바뀐 곳을 뽑는다.
    python3 find_changes.py 시험지.pdf 원지문1.pdf [원지문2.pdf ...] -o changes.txt
- 시험지 쪽마다 tesseract로 방향을 알아내 바로 세우고, 2단(좌·우) × 위·아래 4칸으로 잘라 영어를 읽는다.
- 원지문 PDF는 영어 문단(한글 3자 미만, 영문 40낱말 이상)만 뽑는다.
- 결과: 원지문 문단마다 일치율과 바뀐 곳(replace/delete/insert) 목록. 일치율 50% 미만은 '출제 안 됨'.
OCR 오자(예: calis, miilion)와 밑줄 기호((a), ①)도 insert/replace로 섞여 나오므로, 결과는 시험지 그림과 함께 사람이 확인한다.
"""
import sys, re, os, difflib, subprocess, tempfile, argparse, glob
from PIL import Image

def toks(s):
    return re.findall(r"[a-z]+(?:'[a-z]+)?", s.lower().replace('’', "'"))

def exam_text(pdf, dpi=200):
    d = tempfile.mkdtemp()
    subprocess.run(['pdftoppm', '-r', str(dpi), '-png', pdf, f'{d}/p'], check=True)
    out = []
    for f in sorted(glob.glob(f'{d}/p-*.png')):
        osd = subprocess.run(['tesseract', f, '-', '--psm', '0'], capture_output=True, text=True).stdout
        m = re.search(r'Rotate:\s*(\d+)', osd)
        rot = int(m.group(1)) if m else 0
        im = Image.open(f).rotate(-rot, expand=True)   # tesseract가 알려 준 만큼 시계 방향으로 돌린다
        w, h = im.size
        for x0, x1 in [(0, w // 2 + 20), (w // 2 - 20, w)]:
            for y0, y1 in [(0, h // 2 + 40), (h // 2 - 40, h)]:
                c = f'{d}/c.png'; im.crop((x0, y0, x1, y1)).save(c)
                out.append(subprocess.run(['tesseract', c, '-', '-l', 'eng', '--psm', '6'], capture_output=True, text=True).stdout)
    return '\n'.join(out)

def eng_blocks(pdf):
    s = subprocess.run(['pdftotext', pdf, '-'], capture_output=True, text=True).stdout
    blocks, cur = [], []
    for l in s.split('\n'):
        en = len(re.findall(r'[A-Za-z]', l)); ko = len(re.findall(r'[가-힣]', l))
        if en > 25 and ko < 3: cur.append(l.strip())
        else:
            if len(' '.join(cur).split()) > 40: blocks.append(' '.join(cur))
            cur = []
    if len(' '.join(cur).split()) > 40: blocks.append(' '.join(cur))
    return blocks

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('exam'); ap.add_argument('sources', nargs='+'); ap.add_argument('-o', '--out', default='changes.txt')
    a = ap.parse_args()
    E = toks(exam_text(a.exam))
    lines = []
    for src in a.sources:
        for b in eng_blocks(src):
            bt = toks(b)
            mb = [x for x in difflib.SequenceMatcher(None, bt, E, autojunk=False).get_matching_blocks() if x.size >= 4]
            cov = sum(x.size for x in mb) / max(1, len(bt))
            head = f'## {os.path.basename(src)} [{" ".join(bt[:8])} …] 일치 {cov:.0%}'
            if cov < 0.5:
                lines.append(head + ' → 출제 안 됨(또는 대부분 다름)'); continue
            lines.append(head)
            lo, hi = mb[0].b, mb[-1].b + mb[-1].size
            for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, bt, E[lo:hi], autojunk=False).get_opcodes():
                if op != 'equal':
                    lines.append(f'    {op}: [{" ".join(bt[i1:i2])}] → [{" ".join(E[lo + j1:lo + j2])}]')
    open(a.out, 'w', encoding='utf-8').write('\n'.join(lines))
    print(a.out, len(lines), '줄')

if __name__ == '__main__':
    main()
