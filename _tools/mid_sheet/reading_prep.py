"""코코스 중등 독해 회차 작업 폴더 준비 (2026-11-05, 예약 작업용 — 비밀번호 없이).

틀(base.html·tocbase.html)은 이미 공개한 중2 1회 학습지·목차(study/reading-m2-01)를 그대로 쓴다.
교과서 학습지(잠김)를 풀 필요가 없고, 공개용 안내 문구도 이미 들어 있다(그래도 올리기 전 public_notice.py는 돌린다).
샘플 DATA(sample/data_1~5.js)도 같은 1회 학습지에서 떼어 낸다.

    python3 _tools/mid_sheet/reading_prep.py <작업 폴더>
"""
import os, shutil, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(ROOT, 'study', 'reading-m2-01')

w = sys.argv[1]
os.makedirs(os.path.join(w, 'sample'), exist_ok=True)
shutil.copy(os.path.join(SRC, '1', 'index.html'), os.path.join(w, 'base.html'))
shutil.copy(os.path.join(SRC, 'index.html'), os.path.join(w, 'tocbase.html'))
for k in range(1, 6):
    s = open(os.path.join(SRC, str(k), 'index.html'), encoding='utf8').read()
    i = s.index('var DATA = ')
    j = s.index('\n};', i) + 3
    open(os.path.join(w, 'sample', f'data_{k}.js'), 'w', encoding='utf8').write(s[i:j] + '\n')
for f in ('READING_SPEC.md', 'READING_REVIEW.md'):
    shutil.copy(os.path.join(HERE, 'kit', f), os.path.join(w, f))
print('준비됨:', w, '(base.html · tocbase.html · sample/data_1~5.js · READING_SPEC.md · READING_REVIEW.md)')
