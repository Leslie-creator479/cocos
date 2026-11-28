"""toc.json으로 블로그용 수록 지문 목록·태그를 만들고, 블로그 수록 지문 목록 페이지에 회차를 추가한다. (/home/claude/cocos-study/blog_kit.py)
사용법: python3 blog_kit.py toc.json "<회차 제목>" <회차 id> "<회차 태그>" <목차 링크> [목록 페이지 파일]
  예: python3 blog_kit.py toc.json "2026년 9월 고1 학력평가" m9g1 "9월고1모의고사" https://claude.ai/artifact/… list.html
  - 회차 id: 영문 소문자·숫자만 (학평 m<월>g<학년>, 교재 예: sut3)
  - 회차 태그: 태그 맨 앞에 넣을 회차 태그 (띄어쓰기 없이)
  - 목록 페이지 파일을 주면 그 안의 EXAMS 배열에 회차를 넣거나(같은 id면 바꿔) 저장한다.
toc.json: 10단계와 같은 형식. [{"g","n","t","h","e","u"}, ...]
"""
import json, re, sys
TYPE = {'18번': '목적', '19번': '심경', '20번': '주장', '21번': '함축 의미', '22번': '요지', '23번': '주제',
        '24번': '제목', '25번': '도표', '26번': '내용 불일치', '27번': '안내문', '28번': '안내문', '29번': '어법',
        '30번': '어휘', '31번': '빈칸', '32번': '빈칸', '33번': '빈칸', '34번': '빈칸', '35번': '무관한 문장',
        '36번': '글의 순서', '37번': '글의 순서', '38번': '문장 삽입', '39번': '문장 삽입', '40번': '요약문',
        '41~42번': '장문(제목·어휘)', '43~45번': '장문(순서·지칭·내용)'}
TAGS = '영어변형문제 영어지문분석 영어해석 고등영어 영어내신 내신대비 수능영어 모의고사변형문제 EBS변형문제 영어단어장 영어서술형 온라인학습지 코코스학원'

items = json.load(open(sys.argv[1], encoding='utf8'))
title, eid, first_tag, toc_url = sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5]
page = sys.argv[6] if len(sys.argv) > 6 else None
assert re.fullmatch(r'[a-z0-9]+', eid), '회차 id는 영문 소문자·숫자만'
exam = all(it['n'] in TYPE for it in items)          # 학평·모평이면 번호로 유형을 붙이고 18~26 / 29~45로 묶는다
groups = []
for it in items:
    if exam:
        g = '18~26번' if int(it['n'].split('~')[0].rstrip('번')) <= 26 else '29~45번'
        label = f"{it['n']} {TYPE[it['n']]}"
    else:
        g, label = it['g'], f"{it['g']} {it['n']}"
    if not groups or groups[-1]['g'] != g:
        groups.append({'g': g, 'items': []})
    groups[-1]['items'].append([label, it['h'], it['u']])

print(f'■ 수록 지문 ({len(items)}개)')
for gr in groups:
    print(f"\n[{gr['g']}]")
    for label, h, u in gr['items']:
        print(f'{label} · {h}')
tags = first_tag + ' ' + (TAGS if exam else TAGS.replace('모의고사변형문제 ', '')) + ' 성남동영어학원'
print('\n태그:', tags, f'({len(tags)}자, 100자 이내)')
assert len(tags) <= 100, '태그가 너무 길다: 일반 태그를 하나 빼라'

if page:
    src = open(page, encoding='utf8').read()
    m = re.search(r'var EXAMS=\[\n([\s\S]*?)\n\];', src)
    assert m, '목록 페이지에서 EXAMS를 못 찾음'
    exams = [json.loads(l) for l in m.group(1).split(',\n')]   # 한 줄에 회차 하나(JSON)
    exams = [x for x in exams if x['id'] != eid] + [{'id': eid, 'title': title, 'toc': toc_url, 'groups': groups}]
    src = src[:m.start(1)] + ',\n'.join(json.dumps(x, ensure_ascii=False) for x in exams) + src[m.end(1):]
    open(page, 'w', encoding='utf8').write(src)
    print(f'목록 페이지에 추가: {title} (회차 {len(exams)}개). 순서는 페이지에 넣은 순서대로 보인다.')
