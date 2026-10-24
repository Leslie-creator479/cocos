# 중등·고등 학습지 공용 녹음 도구 사본(2026-10-24): SAYFIX·TEXTFIX에 NGO, Jeju-do, Halla, Olle, iguana, kimchi, Patagonia 발음 고침이 들어 있다.
"""단어 정리(vocab)의 단어마다 발음 MP3를 만들어 index.html의 AUDIO 블록에 넣는다.
사용법: python3 build_audio.py 경로/index.html
준비물: pip install --break-system-packages kokoro-onnx soundfile / ffmpeg
        MODEL_DIR에 kokoro-v1.0.int8.onnx, voices-v1.0.bin (없으면 GitHub에서 받음)
"""
import base64, json, os, re, subprocess, sys, tempfile, urllib.request

MODEL_DIR = os.environ.get('KOKORO_DIR', '/home/claude/.kokoro')
BASE = 'https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/'
FILES = {'kokoro-v1.0.int8.onnx': 'model', 'voices-v1.0.bin': 'voices'}
VOICE, SPEED = 'af_heart', 0.9
SAYFIX = {'NGO': 'N G O', 'NGOs': "N G O's", 'Jeju-do': 'Jeju doh', 'LOL': 'L O L', 'T. rex': 'T rex', 'fallas': 'fah-yahs', 'Fallas': 'Fah-yahs', 'iguana': 'igwana', 'iguanas': 'igwanas', 'kimchi': 'kimchee', 'Patagonia': 'Patta gonia'}  # 글자대로 읽으면 틀리는 단어

def ensure_models():
    os.makedirs(MODEL_DIR, exist_ok=True)
    for f in FILES:
        p = os.path.join(MODEL_DIR, f)
        if not os.path.exists(p):
            print('다운로드:', f)
            subprocess.run(['curl', '-sSL', '-o', p, BASE + f], check=True)
    return [os.path.join(MODEL_DIR, f) for f in FILES]

def main(path):
    src = open(path, encoding='utf8').read()
    data = re.search(r'DATA:START ==== \*/([\s\S]*?)/\* ==== DATA:END', src).group(1)
    vocab = data.split('vocab:', 1)[1].split('map:', 1)[0]
    words = re.findall(r"\bw:\s*'([^']+)'", vocab)
    import soundfile as sf
    from kokoro_onnx import Kokoro
    k = Kokoro(*ensure_models())
    out, tmp = {}, tempfile.mkdtemp()
    for w in words:
        s, sr = k.create(SAYFIX.get(w, w), voice=VOICE, speed=SPEED, lang='en-us')
        wav, mp3 = os.path.join(tmp, 'a.wav'), os.path.join(tmp, 'a.mp3')
        sf.write(wav, s, sr)
        trim = 'silenceremove=start_periods=1:start_threshold=-45dB'
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', wav, '-af',
                        f'{trim},areverse,{trim},areverse,apad=pad_dur=0.08',
                        '-ac', '1', '-ar', '24000', '-b:a', '48k', mp3], check=True)
        out[w] = 'data:audio/mpeg;base64,' + base64.b64encode(open(mp3, 'rb').read()).decode()
        print(f'{w:<20} {k.tokenizer.phonemize(SAYFIX.get(w, w), "en-us")}')
    body = 'var AUDIO = {\n' + ',\n'.join(f'  {json.dumps(w)}: "{d}"' for w, d in out.items()) + '\n};'
    src = re.sub(r'(/\* ==== AUDIO:START ==== \*/\n)[\s\S]*?(\n/\* ==== AUDIO:END ==== \*/)',
                 lambda m: m.group(1) + body + m.group(2), src)
    open(path, 'w', encoding='utf8').write(src)
    print(f'발음 {len(out)}개 넣음, 페이지 {len(src.encode()) // 1024}KB')

if __name__ == '__main__':
    main(sys.argv[1])
