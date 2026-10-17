"""단어게임 발음 녹음(assets/say/<slug>.mp3) 채우기. 새 단어게임·단어장을 넣은 뒤 올리기 전에 돌린다(2026-10-17).

단어게임(game/…)은 카카오톡 안 브라우저에서도 소리가 나도록 기기 음성 대신 이 폴더의 MP3를 튼다.
게임에 나오는 단어 중 녹음이 없는 것을 찾아,
  1) 온라인 학습지(study·textbook)의 AUDIO 블록에 같은 단어 녹음이 있으면 꺼내 쓰고(같은 Kokoro af_heart 목소리),
  2) 그래도 없으면 Kokoro로 새로 만든다(--make, kokoro-onnx·soundfile·ffmpeg와 /home/claude/.kokoro 모델 필요).

    python3 _tools/say_audio.py            # 확인만 + 학습지에서 꺼내기
    python3 _tools/say_audio.py --make     # 남은 것은 Kokoro로 만들기
잠긴 페이지는 COCOS_LOCK_PW 환경 변수가 있으면 임시로 풀어서 읽는다(파일은 바꾸지 않는다).
"""
import base64, glob, json, os, re, shutil, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'assets', 'say')


def slug(w):
    return re.sub(r'[^a-z0-9]+', '-', w.lower()).strip('-')


def speak_text(w):
    t = re.sub(r'\((the )?-[^)]*\)', '', w)
    t = re.sub(r'(?<=[A-Za-z])\([^)]*\)', '', t)
    t = re.sub(r'[()~]', '', t)
    t = re.sub(r'\bsb\b', 'somebody', t); t = re.sub(r'\bsth\b', 'something', t)
    return re.sub(r'\s+', ' ', t).strip()


def readable(paths):
    """잠긴 파일은 임시 복사본을 풀어서 돌려준다."""
    locked = [p for p in paths if 'id="cocos-lock"' in open(p, encoding='utf8').read()]
    plain = [p for p in paths if p not in locked]
    tmp = None
    if locked and os.environ.get('COCOS_LOCK_PW'):
        tmp = tempfile.mkdtemp()
        cps = []
        for i, p in enumerate(locked):
            d = os.path.join(tmp, f'{i}.html'); shutil.copy(p, d); cps.append(d)
        for i in range(0, len(cps), 200):
            subprocess.run(['node', os.path.join(ROOT, '_tools', 'lock.mjs'), 'unlock'] + cps[i:i + 200], cwd=ROOT, check=True, stdout=subprocess.DEVNULL)
        plain += cps
    elif locked:
        print(f'잠긴 페이지 {len(locked)}쪽은 건너뜀 (COCOS_LOCK_PW를 주면 풀어서 읽는다)')
    return plain, tmp


def main():
    os.makedirs(OUT, exist_ok=True)
    games, tmp1 = readable(glob.glob(os.path.join(ROOT, 'game', '*', 'index.html')))
    need = {}
    for f in games:
        s = open(f, encoding='utf8').read()
        if 'var DATA = ' not in s:
            continue
        D, _ = json.JSONDecoder().raw_decode(s[s.index('var DATA = ') + 11:])
        for w in D.get('W', []):
            need.setdefault(slug(w[0]), w[0])
    todo = {k: v for k, v in need.items() if not os.path.exists(os.path.join(OUT, k + '.mp3'))}
    print(f'게임 단어 {len(need)}개 · 녹음 없음 {len(todo)}개')
    if todo:
        sheets, tmp2 = readable(glob.glob(os.path.join(ROOT, 'study', '*', '*', 'index.html')) + glob.glob(os.path.join(ROOT, 'textbook', '*', '*', '*', 'index.html')))
        got = 0
        for f in sheets:
            m = re.search(r'AUDIO:START ==== \*/\n(var AUDIO = \{[\s\S]*?\n\};)', open(f, encoding='utf8').read())
            if not m:
                continue
            for k, v in re.findall(r'^\s*"((?:[^"\\]|\\.)*)": "data:audio/mpeg;base64,([A-Za-z0-9+/=]+)"', m.group(1), re.M):
                key = slug(json.loads('"' + k + '"'))
                if key in todo and not os.path.exists(os.path.join(OUT, key + '.mp3')):
                    open(os.path.join(OUT, key + '.mp3'), 'wb').write(base64.b64decode(v)); got += 1
        if tmp2: shutil.rmtree(tmp2, ignore_errors=True)
        todo = {k: v for k, v in todo.items() if not os.path.exists(os.path.join(OUT, k + '.mp3'))}
        print(f'학습지 녹음에서 꺼냄 {got}개 · 남은 것 {len(todo)}개')
    if todo and '--make' in sys.argv:
        import soundfile as sf
        from kokoro_onnx import Kokoro
        M = '/home/claude/.kokoro'
        k = Kokoro(f'{M}/kokoro-v1.0.int8.onnx', f'{M}/voices-v1.0.bin')
        t = tempfile.mkdtemp()
        for key, w in todo.items():
            s, sr = k.create(speak_text(w), voice='af_heart', speed=0.9, lang='en-us')
            wav = os.path.join(t, 'a.wav'); sf.write(wav, s, sr)
            trim = 'silenceremove=start_periods=1:start_threshold=-45dB'
            subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', wav, '-af', f'{trim},areverse,{trim},areverse,apad=pad_dur=0.08',
                            '-ac', '1', '-ar', '24000', '-b:a', '48k', os.path.join(OUT, key + '.mp3')], check=True)
        print(f'Kokoro로 만듦 {len(todo)}개')
    elif todo:
        print('남은 단어:', ', '.join(list(todo.values())[:20]), '… → --make 로 만든다')
    if tmp1: shutil.rmtree(tmp1, ignore_errors=True)


if __name__ == '__main__':
    main()
