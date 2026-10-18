#!/usr/bin/env python3
"""학습지 녹음 용량 줄이기 (선생님 결정 2026-10-19).

페이지 안에 들어 있는 MP3(data:audio/...;base64,...)와 단어게임 발음 녹음 assets/say/*.mp3를
모노 22.05kHz 24kbps MP3로 다시 저장한다. 발음 확인용이라 이 음질로 충분하다(홈페이지 1GB 한도 때문).

- 이미 24kbps 이하인 녹음은 건너뛴다(여러 번 돌려도 같다).
- 잠긴 페이지(id="cocos-lock")는 암호문이라 건너뛴다. 새 페이지는 seo.py가 잠그기 전에 돌려서 자동으로 줄어든다.
  이미 잠긴 페이지를 줄이려면 unlock → 이 도구 → lock.
- ffmpeg가 필요하다.

사용:
  python3 _tools/audio_slim.py              # 저장소 전체(seo.py가 자동으로 부른다)
  python3 _tools/audio_slim.py 파일 …        # 지정한 페이지만
  python3 _tools/audio_slim.py --check      # 바꿀 녹음 개수만 세기
"""
import base64, os, re, subprocess, sys, tempfile
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGET = 24
SKIP_DIRS = {'.git', '_tools', 'node_modules', 'preview'}
DATA_RE = re.compile(r'(data:audio/(?:mpeg|mp3);base64,)([A-Za-z0-9+/]+={0,2})')
BR_V1 = [0, 32, 40, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320]
BR_V2 = [0, 8, 16, 24, 32, 40, 48, 56, 64, 80, 96, 112, 128, 144, 160]


def bitrate(raw: bytes):
    """첫 MP3 프레임의 비트레이트(kbps). 모르면 None."""
    i = 0
    if raw[:3] == b'ID3' and len(raw) > 10:
        s = raw[6:10]
        i = 10 + ((s[0] & 0x7f) << 21 | (s[1] & 0x7f) << 14 | (s[2] & 0x7f) << 7 | (s[3] & 0x7f))
    n = len(raw)
    while i < n - 4:
        if raw[i] == 0xFF and (raw[i + 1] & 0xE0) == 0xE0:
            ver = (raw[i + 1] >> 3) & 3   # 3 = MPEG1
            layer = (raw[i + 1] >> 1) & 3  # 1 = Layer III
            idx = raw[i + 2] >> 4
            sri = (raw[i + 2] >> 2) & 3
            if layer == 1 and 0 < idx < 15 and ver != 1 and sri != 3:
                br = (BR_V1 if ver == 3 else BR_V2)[idx]
                # 첫 프레임이 Xing/Info 머리 프레임이면 비트레이트가 다르게 적혀 있으니 다음 프레임을 본다
                if b'Xing' in raw[i:i + 64] or b'Info' in raw[i:i + 64]:
                    sr = {3: [44100, 48000, 32000], 2: [22050, 24000, 16000], 0: [11025, 12000, 8000]}[ver][sri]
                    pad = (raw[i + 2] >> 1) & 1
                    i += (144 if ver == 3 else 72) * br * 1000 // sr + pad
                    continue
                return br
        i += 1
    return None


def need(raw: bytes) -> bool:
    b = bitrate(raw)
    return b is None or b > TARGET


def encode(raw: bytes) -> bytes:
    with tempfile.TemporaryDirectory() as d:
        a, b = os.path.join(d, 'a.mp3'), os.path.join(d, 'b.mp3')
        open(a, 'wb').write(raw)
        r = subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', a, '-map_metadata', '-1', '-ac', '1',
                            '-ar', '22050', '-b:a', f'{TARGET}k', b], capture_output=True)
        if r.returncode != 0 or not os.path.exists(b) or os.path.getsize(b) < 200:
            return raw  # 실패하면 원래 것을 그대로 둔다
        out = open(b, 'rb').read()
        return out if len(out) < len(raw) else raw


def slim_page(path, check=False):
    t = open(path, encoding='utf-8').read()
    if 'id="cocos-lock"' in t or 'data:audio/' not in t:
        return 0, 0, 0
    todo = {}
    for m in DATA_RE.finditer(t):
        b64 = m.group(2)
        if b64 in todo:
            continue
        try:
            raw = base64.b64decode(b64)
        except Exception:
            continue
        if need(raw):
            todo[b64] = raw
    if check or not todo:
        return len(todo), 0, 0
    before = len(t)
    with ThreadPoolExecutor(max_workers=os.cpu_count() or 4) as ex:
        res = dict(zip(todo, ex.map(encode, todo.values())))
    t = DATA_RE.sub(lambda m: m.group(1) + (base64.b64encode(res[m.group(2)]).decode()
                                            if m.group(2) in res else m.group(2)), t)
    open(path, 'w', encoding='utf-8').write(t)
    return len(todo), before, len(t)


def slim_say(check=False):
    d = os.path.join(ROOT, 'assets', 'say')
    if not os.path.isdir(d):
        return 0, 0, 0
    files = [os.path.join(d, f) for f in os.listdir(d) if f.endswith('.mp3')]
    todo = []
    for f in files:
        raw = open(f, 'rb').read()
        if need(raw):
            todo.append((f, raw))
    if check or not todo:
        return len(todo), 0, 0
    before = sum(len(r) for _, r in todo)

    def one(item):
        f, raw = item
        out = encode(raw)
        if out is not raw:
            open(f, 'wb').write(out)
        return len(out)
    with ThreadPoolExecutor(max_workers=os.cpu_count() or 4) as ex:
        after = sum(ex.map(one, todo))
    return len(todo), before, after


def pages():
    for root, ds, fs in os.walk(ROOT):
        ds[:] = [x for x in ds if x not in SKIP_DIRS]
        for f in fs:
            if f == 'index.html':
                yield os.path.join(root, f)


def run(files=None, check=False, quiet=False):
    import shutil
    if not check and not shutil.which('ffmpeg'):
        print('녹음 줄이기: ffmpeg가 없어 건너뜀(apt-get install -y ffmpeg 후 다시 seo.py)')
        return 0
    n = b = a = 0
    for p in (files or pages()):
        k, x, y = slim_page(p, check)
        n += k; b += x; a += y
    sk, sb, sa = (0, 0, 0) if files else slim_say(check)
    if check:
        print(f'녹음 줄이기: 바꿀 녹음 페이지 속 {n}개 · 발음 파일 {sk}개')
    elif n or sk or not quiet:
        saved = (b - a) + (sb - sa)
        print(f'녹음 줄이기(24k): 페이지 속 {n}개 · 발음 파일 {sk}개 · {saved / 1e6:.1f}MB 줄임')
    return n + sk


if __name__ == '__main__':
    args = [x for x in sys.argv[1:] if not x.startswith('--')]
    run([os.path.abspath(x) for x in args] or None, check='--check' in sys.argv)
