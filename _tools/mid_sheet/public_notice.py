"""공개 중등 자료(코코스 중등 독해 오리지널 지문 study/reading-m…, 2026-11-04)의 안내 문구를 공개용으로 바꾼다.

make_mid.py·make_toc_mid.py는 교과서 학습지(학원생 전용)를 틀로 쓰므로, 학원 안내 카드의 '학원생 전용이에요…' 줄과
바닥글의 '학원생의 수업용으로만 제공돼요…' 줄이 그대로 따라온다. 공개 자료에는 맞지 않으니(원장님 지적 2026-11-04)
카드의 줄은 빼고 바닥글은 모의고사 학습지처럼 '자유롭게 공유' 안내로 바꾼다. 몇 번 돌려도 같다.

    python3 _tools/mid_sheet/public_notice.py study/reading-m2-01/index.html study/reading-m2-01/1/index.html
"""
import re, sys

PUBLIC = '<p>링크와 PDF는 누구에게나 자유롭게 공유하고 배포해도 좋아요. 다만 내용을 복제·수정해 다른 곳에 올리거나 상업적으로 이용하는 것은 금지해요.</p>'
for f in sys.argv[1:]:
    s = open(f, encoding='utf8').read()
    t = re.sub(r'\n?\s*<p class="share">이 자료는 코코스학원 학원생 전용이에요\.[^<]*</p>', '', s)
    t = re.sub(r'<p>이 자료는 코코스학원 학원생의 수업용으로만 제공돼요\.[^<]*</p>', PUBLIC, t)
    t = re.sub(r'<p>링크는 누구에게나 자유롭게 공유해도 좋아요\.[^<]*</p>', PUBLIC, t)
    assert '학원생 전용' not in t and '수업용으로만' not in t, f
    if t != s:
        open(f, 'w', encoding='utf8').write(t)
    print(f, '바꿈' if t != s else '그대로')
