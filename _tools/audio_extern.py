#!/usr/bin/env python3
"""학습지 녹음을 페이지 밖 파일로 빼서 홈페이지 용량 줄이기 (선생님 결정 2026-10-22).

학습지(study·textbook) 안의 녹음은 base64 글자로 들어 있어 원래 mp3보다 약 1/3 크고,
단어 녹음은 같은 단어가 여러 학습지에 반복해서 들어 있다. 이 도구는
  1) 단어 녹음(AUDIO)  → 공용 발음 폴더 주소 "/assets/say/<slug>.mp3"로 바꾼다.
     assets/say에 없는 단어는 페이지 속 녹음을 꺼내 새로 저장한다(단어게임과 같은 파일을 함께 쓴다).
  2) 문장 녹음(SAUDIO) → 잠그지 않는 학습지(모의고사)만 같은 폴더의 "s1.mp3, s2.mp3 …"로 뺀다.
     교과서·부교재 문장 녹음은 지문 저작권 때문에 잠금 안(페이지 속)에 그대로 둔다.
페이지의 듣기 코드는 그대로다(AUDIO[w]·SAUDIO[i]에 data: 대신 파일 주소가 들어갈 뿐).
여러 번 돌려도 같다. 잠긴 페이지(id="cocos-lock")는 건너뛴다 → seo.py가 잠그기 전에 돌려서 새 학습지는 자동으로 바뀐다.
이미 잠긴 페이지를 바꾸려면 unlock → 이 도구 → lock.

사용:
  python3 _tools/audio_extern.py              # 저장소 전체(seo.py가 자동으로 부른다)
  python3 _tools/audio_extern.py 파일 …        # 지정한 페이지만
  python3 _tools/audio_extern.py --check      # 바꿀 녹음 개수만 세기
"""
import base64, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAY = os.path.join(ROOT, 'assets', 'say')
MOCK = re.compile(r'^\d{4}-\d{2}-g\d$')
A_BLOCK = re.compile(r'(/\* ==== AUDIO:START ==== \*/)([\s\S]*?)(/\* ==== AUDIO:END ==== \*/)')
S_BLOCK = re.compile(r'(/\* ==== SAUDIO:START ==== \*/)([\s\S]*?)(/\* ==== SAUDIO:END ==== \*/)')
A_ENTRY = re.compile(r'^(\s*"((?:[^"\\]|\\.)*)": )"data:audio/mpeg;base64,([A-Za-z0-9+/=]+)"', re.M)
S_ENTRY = re.compile(r'"data:audio/mpeg;base64,([A-Za-z0-9+/=]+)"')


def slug(w):  # _tools/say_audio.py와 같은 규칙
    return re.sub(r'[^a-z0-9]+', '-', w.lower()).strip('-')


def locked_target(rel):  # _tools/lock.mjs의 shouldLock과 같은 규칙
    p = rel.split('/')
    if p[0] == 'textbook':
        return True
    if p[0] in ('study', 'syn', 'game') and len(p) > 1:
        return not MOCK.match(p[1])
    return False


def unjs(k):
    import json
    try:
        return json.loads('"' + k + '"')
    except Exception:
        return k


def do_page(path, check=False):
    """반환: (단어 수, 문장 수, 줄어든 바이트, 새 발음 파일 수)"""
    t = open(path, encoding='utf-8').read()
    if 'id="cocos-lock"' in t or 'data:audio/' not in t:
        return 0, 0, 0, 0
    d = os.path.dirname(path)
    rel = os.path.relpath(d, ROOT).replace(os.sep, '/')
    before = len(t.encode('utf-8'))
    nw = ns = newsay = 0

    def a_block(m):
        nonlocal nw, newsay
        def ent(e):
            nonlocal nw, newsay
            s = slug(unjs(e.group(2)))
            if not s:
                return e.group(0)
            f = os.path.join(SAY, s + '.mp3')
            if not os.path.exists(f):
                if not check:
                    os.makedirs(SAY, exist_ok=True)
                    open(f, 'wb').write(base64.b64decode(e.group(3)))
                newsay += 1
            nw += 1
            return f'{e.group(1)}"/assets/say/{s}.mp3"'
        return m.group(1) + A_ENTRY.sub(ent, m.group(2)) + m.group(3)

    t2 = A_BLOCK.sub(a_block, t, count=1)

    if not locked_target(rel):
        def s_block(m):
            nonlocal ns
            i = 0
            def ent(e):
                nonlocal i, ns
                i += 1; ns += 1
                if not check:
                    open(os.path.join(d, f's{i}.mp3'), 'wb').write(base64.b64decode(e.group(1)))
                return f'"s{i}.mp3"'
            body = m.group(2)
            if 'data:audio/' not in body:
                return m.group(0)
            return m.group(1) + S_ENTRY.sub(ent, body) + m.group(3)
        t2 = S_BLOCK.sub(s_block, t2, count=1)

    if t2 == t:
        return 0, 0, 0, 0
    if not check:
        open(path, 'w', encoding='utf-8').write(t2)
    return nw, ns, before - len(t2.encode('utf-8')), newsay


def pages():
    for top in ('study', 'textbook'):
        for root, ds, fs in os.walk(os.path.join(ROOT, top)):
            if 'index.html' in fs:
                yield os.path.join(root, 'index.html')


def run(files=None, check=False, quiet=False):
    W = S = B = N = P = 0
    for p in (files or pages()):
        w, s, b, n = do_page(p, check)
        if w or s:
            P += 1
        W += w; S += s; B += b; N += n
    if check:
        print(f'녹음 빼기: 바꿀 학습지 {P}개 · 단어 녹음 {W}개(새 발음 파일 {N}개) · 문장 녹음 {S}개')
    elif P or not quiet:
        print(f'녹음 빼기: 학습지 {P}개 · 단어 녹음 {W}개 → assets/say(새 파일 {N}개) · 문장 녹음 {S}개 → mp3 · 페이지 {B / 1e6:.1f}MB 가벼워짐')
    return P


if __name__ == '__main__':
    args = [x for x in sys.argv[1:] if not x.startswith('--')]
    run([os.path.abspath(x) for x in args] or None, check='--check' in sys.argv)
