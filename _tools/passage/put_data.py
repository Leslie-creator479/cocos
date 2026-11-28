"""템플릿을 복사해 새 지문 학습지 파일을 만든다(제목과 DATA만 바꾼다).
사용법: python3 put_data.py template.html data.js "<title 글자>" 출력/index.html
  data.js: `var DATA = { ... };` 한 덩어리(템플릿의 DATA:START~DATA:END 사이와 같은 꼴)
  출력 파일이 이미 있으면 그 파일의 DATA와 제목만 바꾼다(녹음 블록 등 나머지는 그대로).
템플릿 전체를 손으로 다시 쓰지 않으려고 만든 도구다(2026-11-28, 사용량 줄이기).
"""
import os, re, sys

if len(sys.argv) != 5:
    sys.exit(__doc__)
tpl, data_js, title, out = sys.argv[1:]
base = out if os.path.exists(out) else tpl
s = open(base, encoding='utf8').read()
d = open(data_js, encoding='utf8').read().strip()
if not re.match(r'^(var|const|let)\s+DATA\s*=', d):
    sys.exit('data.js는 "var DATA = {" 로 시작해야 한다')
d = re.sub(r'^(const|let)\s+DATA', 'var DATA', d)
if not d.endswith(';'):
    d += ';'
A, B = '/* ==== DATA:START ==== */', '/* ==== DATA:END ==== */'
i, j = s.find(A), s.find(B)
if i < 0 or j < i:
    sys.exit('DATA:START/END 표시를 찾지 못함: ' + base)
s = s[:i + len(A)] + '\n' + d + '\n' + s[j:]
if '<' in title or '>' in title:
    sys.exit('title에 < > 를 쓰지 않는다')
s, n = re.subn(r'<title>.*?</title>', lambda m: '<title>' + title + '</title>', s, count=1)
if n != 1:
    sys.exit('<title>을 찾지 못함')
os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
open(out, 'w', encoding='utf8').write(s)
print(out, f'{len(s.encode()) // 1024} KB', '(기존 파일 고침)' if base == out else '(템플릿에서 새로 만듦)')
