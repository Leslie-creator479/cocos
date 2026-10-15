"""온라인 학습지에 'PDF로 저장' 버튼을 붙인다 (선생님 결정 2026-10-15).

버튼과 인쇄용 화면은 공용 파일이 만든다. 이 도구는 페이지 맨 끝에 그 파일을 부르는 줄 하나만 넣는다.
  학습지(DATA에 sentences가 있는 study·textbook 지문 페이지) → assets/print-sheet.js
  동의어·반의어(syn, DATA.passages)                         → assets/print-syn.js
  단어게임(game, DATA.W)                                     → assets/print-game.js
PDF는 학생 기기에서 만들어지므로 홈페이지에 파일이 쌓이지 않는다. 모양을 바꾸려면 print-sheet.js만 고친다.

함께 하는 일: 학원 안내 카드의 '온라인 학습지을' 오타를 '온라인 학습지를'로 고친다(brand_links.py가 만들던 오타).

seo.py가 돌 때마다 자동으로 함께 돈다(올리기 전 항상 seo.py를 돌리므로 다른 방에서 만든 새 학습지에도 붙는다).
잠긴 페이지(id="cocos-lock")는 암호문이라 건너뛴다. 새 페이지는 잠그기 전(seo.py 단계)에 붙으므로 문제없다.
여러 번 돌려도 결과가 같다.

사용법: python3 _tools/print_btn.py [--check]
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSET = 'assets/print-sheet.js'
ASSET_SYN = 'assets/print-syn.js'    # 동의어·반의어 PDF (2026-10-15)
ASSET_GAME = 'assets/print-game.js'  # 단어게임 단어 목록·시험지 PDF (2026-10-15)
SHEET = re.compile(r'(?:var|const|let)\s+DATA\s*=')
SENT = re.compile(r'\bsentences"?\s*:')
TYPO = ('온라인 학습지을', '온라인 학습지를')
STUDENT = ('study', 'textbook', 'school', 'syn', 'game')


def run(check=False, quiet=False):
    added, typo, locked = [], [], []
    for top in STUDENT:
        base = os.path.join(ROOT, top)
        for dp, dns, fns in os.walk(base):
            if 'index.html' not in fns:
                continue
            path = os.path.join(dp, 'index.html')
            page = os.path.relpath(dp, ROOT).replace(os.sep, '/')
            s = open(path, encoding='utf8').read()
            if 'id="cocos-lock"' in s:
                locked.append(page)
                continue
            t = s
            if TYPO[0] in t:
                t = t.replace(*TYPO)
                typo.append(page)
            asset = None
            if top in ('study', 'textbook') and SHEET.search(t) and SENT.search(t) and 'id="passage"' in t:
                asset = ASSET
            elif top == 'syn' and SHEET.search(t) and 'passages' in t and 'id="orig"' in t:
                asset = ASSET_SYN
            elif top == 'game' and SHEET.search(t) and '"W"' in t and 'id="range"' in t:
                asset = ASSET_GAME
            if asset and asset not in t:
                rel = '../' * (page.count('/') + 1)
                tag = f'<script src="{rel}{asset}"></script>\n'
                i = t.rfind('</body>')
                t = t[:i] + tag + t[i:] if i >= 0 else t + tag
                added.append(page)
            if t != s and not check:
                open(path, 'w', encoding='utf8').write(t)
    if not quiet or added or typo:
        print(f"PDF 버튼: 이번에 붙인 페이지 {len(added)}쪽 · 오타 고친 쪽 {len(typo)}"
              + (f" · 잠겨서 건너뛴 쪽 {len(locked)}" if not quiet else '') + (' (확인만)' if check else ''))
    return added, typo, locked


if __name__ == '__main__':
    run(check='--check' in sys.argv)
