# 회차 하나 준비: 목차·동의어 블로그 원고·저장된 학습지들로 manifest/config/blog 뼈대를 만든다.
# 사용: python3 -I prep.py 폴더 "2026 6월 고2" 목차파일 syn_id syn블로그파일 "출처 문장" theme 목차URL
#   (학습지 파일은 ../artifact-files/*/index.html 에서 제목 "{회차} N번"으로 찾는다. syn이 없으면 syn_id·syn블로그파일에 "" )
import json, re, sys, glob, os
out, label, tocf, syn, synblog, source, theme, toc_url = sys.argv[1:9]
os.makedirs(out, exist_ok=True)
s = open(tocf, encoding='utf8').read()
T = json.loads(re.search(r'var TOC = (\{.*?\});\n/\* ==== TOC:END', s, re.S).group(1))
types = {}
if synblog:
    b = open(synblog, encoding='utf8').read()
    D = json.loads(re.search(r'var D=(\{.*?\});\nfunction \$', b, re.S).group(1))
    for g in D['groups']:
        for lab, _ in g['items']:  # "18번 목적 · 제목" 꼴에서 유형만
            m = re.match(r'([\d~]+)번 (.+?) · ', lab)
            if m: types[m.group(1)] = m.group(2)
files = {}
for f in glob.glob('../artifact-files/*/index.html'):
    t = (re.search(r'<title>([^<]*)', open(f, encoding='utf8').read(4000)) or [None, ''])[1]
    m = re.search(re.escape(label) + r'\s+([\d~\-]+)번', t)
    if m: files[m.group(1).replace('-', '~')] = os.path.abspath(f)
man = []
for it in T['items']:
    no = it['n'].replace('번', '')
    if no not in files: print('학습지 파일 없음:', no); continue
    man.append(dict(no=no, topic=it['t'], u=it['u'].rsplit('/', 1)[1], sa=('p' + no.replace('~', '-')) if syn else '', file=files[no]))
json.dump(man, open(out + '/manifest.json', 'w', encoding='utf8'), ensure_ascii=False)
json.dump(dict(label=label, toc=T, types=types, syn=syn, source=source, theme=theme, toc_url=toc_url), open(out + '/info.json', 'w', encoding='utf8'), ensure_ascii=False)
print(label, '목차', len(T['items']), 'manifest', len(man), '유형', len(types))
