"""단어게임 '지문 속 빈칸' 보기 후보 정리 (2026-10-24).
build.py가 빈칸 문제를 못 만드는 단어(후보 3개 미만)도 다른 단어의 보기 후보(pool)에 남겨 두어,
그 단어가 보기로 뽑히면 게임이 멈추던 문제를 고친다. DATA.W에서 빈칸 정보가 없는 단어를 pool에서 빼고,
후보가 3개 미만이 된 단어는 빈칸 문제에서만 뺀다. 다른 데이터는 바꾸지 않는다.
사용법: python3 _tools/fix_game_pool.py [--check] [파일.html ...]   (파일을 안 주면 game/*/index.html 전체, 잠긴 페이지는 건너뜀)
seo.py가 돌 때 함께 돈다(새 단어게임은 잠그기 전 단계라 자동으로 고쳐진다).
"""
import glob, json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def fix(f, check=False):
    s = open(f, encoding='utf8').read()
    if 'id="cocos-lock"' in s: return None
    a = s.find('var DATA = ')
    if a < 0: return None
    e = s.index(';\n', a); D = json.loads(s[a + 11:e]); W = D.get('W') if isinstance(D, dict) else None
    if not W: return None
    hp = lambda r: len(r) >= 7 and isinstance(r[6], list)   # 빈칸 문제로 나오는 단어(보기 후보 목록 있음)
    ok = lambda r: len(r) >= 6                               # 보기로 쓸 수 있는 단어(빈칸 자리 정보 s·f 있음)
    bad = sum(1 for r in W if hp(r) for i in r[6] if not ok(W[i]))
    if not bad: return None
    for r in W:
        if hp(r):
            q = [i for i in r[6] if ok(W[i])]
            if len(q) >= 3: r[6] = q
            else: del r[6:]   # 보기가 모자라면 이 단어만 빈칸 문제에서 빠진다(다른 단어의 보기로는 계속 쓰임)
    if not check:
        open(f, 'w', encoding='utf8').write(s[:a + 11] + json.dumps(D, ensure_ascii=False, separators=(',', ':')) + s[e:])
    return bad
def run(files=None, check=False, quiet=False):
    files = files or sorted(glob.glob(os.path.join(ROOT, 'game', '*', 'index.html')))
    n = 0
    for f in files:
        b = fix(f, check)
        if b: n += 1; quiet or print(f'{os.path.relpath(f, ROOT)}: 잘못된 빈칸 보기 후보 {b}개 정리')
    if n or not quiet: print(f'단어게임 빈칸 보기 정리: {n}쪽' + (' (확인만)' if check else ''))
    return n
if __name__ == '__main__':
    a = sys.argv[1:]
    run([x for x in a if x != '--check'] or None, check='--check' in a)
