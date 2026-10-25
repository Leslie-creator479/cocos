# 중등·고등 학습지 공용 녹음 도구 사본(2026-10-24): SAYFIX·TEXTFIX에 NGO, Jeju-do, Halla, Olle, iguana, kimchi, Patagonia, Seojun, Louis XVI, Llanera, Leah, Kaos, Ateneo, Killorglin, MoMA, 24/7, Monalisa, cm, caprese, acai, Chefchaouen, Diaz, 9:00, 100th, 911, NPCs, Junha, Seoraksan, Heundeulbawi, gamjajeon, Sokcho, Poke(포케), AI 발음 고침이 들어 있다.
"""지문 문장마다 읽어 주는 MP3를 만들어 index.html의 SAUDIO 블록에 넣는다.
사용법: python3 build_saudio.py 경로/index.html [...]
준비물: build_audio.py와 같음 (kokoro-onnx, soundfile, ffmpeg, /home/claude/.kokoro 모델)
- 목소리는 단어 발음과 같은 af_heart, 원래 속도(1.0)로 녹음하고, 0.8배는 페이지에서 재생 속도로 조절한다.
- SAUDIO 블록이 없으면 AUDIO:END 바로 뒤에 새로 만든다.
"""
import base64, os, re, subprocess, sys, tempfile, html
from build_audio import ensure_models, VOICE

SPEED = 1.0
PRON = {'Goethe': 'ɡˈɜːɹtə', "Goethe's": 'ɡˈɜːɹtəz', 'Guernica': 'ɡwˈɛɹnɪkə', 'Juvisy': 'ʒˌuːviːzˈiː',
        'Montigny-le-Roi': 'mˌɔntiːnjˈiː ləɹwˈɑː', 'Verrier': 'vˌɛɹiˈeɪ', 'Urbain': 'ʊɹbˈæn',
        'Flammarion': 'flˌæməɹiˈɔːn', 'Concord': 'kˈɑːŋkɚd', 'Caltech': 'kˈælˌtɛk', 'Jacques': 'ʒˈɑːk',
        'Göttingen': 'ɡˈɜːtɪŋən', 'Seok': 'sˈʌk', 'Hopil': 'hˈoʊpˌɪl', 'Fallas': 'fˈɑːjəs', 'fallas': 'fˈɑːjəs', 'Kaos': 'kˈɑːoʊs', 'Ateneo': 'ˌɑːtənˈeɪoʊ', 'Killorglin': 'kɪlˈɔːɹɡlɪn', 'caprese': 'kəpɹˈeɪzeɪ', 'Caprese': 'kəpɹˈeɪzeɪ', 'acai': 'ˌɑːsɑːˈiː', 'Acai': 'ˌɑːsɑːˈiː', 'Chefchaouen': 'ʃˌɛfʃɑːwˈɛn', 'Diaz': 'dˈiːɑːs', 'Dubai': 'duːbˈaɪ', 'Reena': 'ɹˈiːnə', "Reena's": 'ɹˈiːnəz', 'Jaemin': 'dʒˈɛmɪn', 'Miso': 'mˈiːsoʊ', 'Teo': 'tˈeɪoʊ', 'Subin': 'sˈuːbɪn', "Subin's": 'sˈuːbɪnz', "Subin’s": 'sˈuːbɪnz'}
ONES = 'zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen'.split()
TENS = 'x x twenty thirty forty fifty sixty seventy eighty ninety'.split()
def two(n):
    if n < 20: return ONES[n]
    return TENS[n // 10] + ('-' + ONES[n % 10] if n % 10 else '')
def year(m):
    y, plural = int(m.group(1)), m.group(2)
    hi, lo = divmod(y, 100)
    if lo == 0: return two(hi) + (' hundreds' if plural else ' hundred')
    w = two(hi) + ' ' + ('oh ' + ONES[lo] if lo < 10 else two(lo))
    if plural: w = w[:-1] + 'ies' if w.endswith('y') else w + 's'
    return w
TEXTFIX = [(r'\bWorld War II\b', 'World War Two'), (r'\bWorld War I\b', 'World War One'),
           (r'\bK-A-T-Y\b', 'K, A, T, Y'), (r'\bEI\b', 'E I'), (r'\bUMD\b', 'U M D'),
           (r'\bNGOs\b', "N G O's"), (r'\bNGO\b', 'N G O'), (r'\bJeju-do\b', 'Jeju doh'), (r'\bOlle\b', 'Oh-lay'), (r'\bHalla\b', 'Hahla'), (r'\s*\(\u263a\)', ''), (r'\s*\u263a', ''), (r'\bLOL\b', 'L O L'), (r'\bMt\. ', 'Mount '), (r'\bT\. rex\b', 'T rex'), (r'\bMr\. ', 'Mister '), (r'\bDr\. ', 'Doctor '), (r'\bMrs\. ', 'Missus '), (r'\biguana(s?)\b', r'igwana\1'), (r'\bkimchi\b', 'kimchee'), (r'\bPatagonia\b', 'Patta gonia'), (r'\bSeojun\b', 'Suh-joon'), (r'\bLouis XVI\b', 'Louis the Sixteenth'), (r'\bLlanera\b', 'Yah-nair-ah'), (r'\bLeah\b', 'Leea'), (r'\bMoMA\b', 'Moma'), (r'\b24/7\b', 'twenty-four seven'), (r'\bMonalisa\b', 'Mona Lisa'), (r'(\d) cm\b', r'\1 centimeters'), (r'\b(\d{1,2}):00\b', r'\1'), (r'\b(\d{1,2}):(\d\d)\b', r'\1 \2'), (r'\b100th\b', 'hundredth'), (r'\b911\b', 'nine one one'), (r'\bNPCs\b', "N P C's"), (r'\bJunha\b', 'Joon-ha'), (r'\bSeoraksan\b', 'Suh-rahk-sahn'), (r'\bHeundeulbawi\b', 'Hun-dool-bah-wee'), (r'\bgamjajeon\b', 'gahm-jah-jun'), (r'\bSokcho\b', 'Sohk-cho'), (r'\bPoke\b', 'Poh-kay'), (r'\bAI\b', 'A I'),
           (r'(?<=\d),(?=\d{3}\b)', ''), (r'\b(1[1-9]\d\d)(s?)\b', year)]
BLOCK = '/* ==== SAUDIO:START ==== */\n{}\n/* ==== SAUDIO:END ==== */'

def clean(t):
    t = re.sub(r'<[^>]+>', '', t)
    t = html.unescape(t)
    t = t.replace('’', "'").replace('‘', "'").replace('“', '"').replace('”', '"')
    t = t.replace('—', ', ').replace('–', ', ').replace('…', '...')
    return re.sub(r'\s+', ' ', t).strip()

def sentences(src):
    data = re.search(r'DATA:START ==== \*/([\s\S]*?)/\* ==== DATA:END', src).group(1)
    part = data.split('sentences:', 1)[1].split('\n  ],', 1)[0]
    out = []
    for m in re.finditer(r"\{ en: '((?:[^'\\]|\\.)*)'", part):
        out.append(m.group(1).replace("\\'", "'"))
    return out

def main(paths):
    import soundfile as sf
    from kokoro_onnx import Kokoro
    k = Kokoro(*ensure_models())
    for path in paths:
        src = open(path, encoding='utf8').read()
        sents = sentences(src)
        tmp, datas = tempfile.mkdtemp(), []
        for i, s in enumerate(sents):
            text = clean(s)
            for a_, b_ in TEXTFIX:
                text = re.sub(a_, b_, text)
            fix = [w for w in PRON if re.search(r"(?<![\w'])" + re.escape(w) + r"(?![\w'])", text)]
            if fix:
                ph = k.tokenizer.phonemize(text, 'en-us')
                for w in sorted(fix, key=len, reverse=True):
                    old = k.tokenizer.phonemize(w, 'en-us')
                    pat = r'(?<![^\s,.;:!?"()—])' + re.escape(old) + r'ɹ?(?![^\s,.;:!?"()—])'
                    assert re.search(pat, ph), (w, old, ph)
                    ph = re.sub(pat, PRON[w], ph)
                a, sr = k.create(ph, voice=VOICE, speed=SPEED, lang='en-us', is_phonemes=True)
            else:
                a, sr = k.create(text, voice=VOICE, speed=SPEED, lang='en-us')
            wav, mp3 = os.path.join(tmp, 'a.wav'), os.path.join(tmp, 'a.mp3')
            sf.write(wav, a, sr)
            trim = 'silenceremove=start_periods=1:start_threshold=-45dB'
            subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', wav, '-af',
                            f'{trim},areverse,{trim},areverse,apad=pad_dur=0.15',
                            '-ac', '1', '-ar', '24000', '-b:a', '40k', mp3], check=True)
            b = open(mp3, 'rb').read()
            datas.append('data:audio/mpeg;base64,' + base64.b64encode(b).decode())
            print(f'  {i+1:>2}. {len(a)/sr:4.1f}s {len(b)//1024:3d}KB  {text[:60]}  | {k.tokenizer.phonemize(text, "en-us")[:70]}')
        body = 'var SAUDIO = [\n' + ',\n'.join(f'  "{d}"' for d in datas) + '\n];'
        if 'SAUDIO:START' in src:
            src = re.sub(r'(/\* ==== SAUDIO:START ==== \*/\n)[\s\S]*?(\n/\* ==== SAUDIO:END ==== \*/)',
                         lambda m: m.group(1) + body + m.group(2), src)
        else:
            end = '/* ==== AUDIO:END ==== */'
            assert src.count(end) == 1
            src = src.replace(end, end + '\n' + BLOCK.format(body))
        open(path, 'w', encoding='utf8').write(src)
        print(f'{path}: 문장 {len(datas)}개, 페이지 {len(src.encode()) // 1024}KB')

if __name__ == '__main__':
    main(sys.argv[1:])
