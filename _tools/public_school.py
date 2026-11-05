#!/usr/bin/env python3
"""모의고사 지문만 묶은 학교별 시험 범위 자료를 공개로 정한다(원장님 결정 2026-11-05).

학교별 목차(school/<시험>/<학교>-g<학년>/)의 지문 링크가 모두 모의고사·수능 학습지
(study/<연도>-<월>-g<학년>/…, study/suneung-…/…)로만 이어지면, 그 목차와 같은 이름의
동의어·반의어(syn/<시험>-<학교>-g<학년>)·단어게임(game/…)은 모의고사 자료처럼
잠그지 않고 검색에 연다. 교과서·부교재(올림포스 등)가 하나라도 섞이면 지금처럼
학원생 잠금·검색 제외다. 링크가 모의고사 학습지라도 교재 범위(EBS 올림포스 기출처럼
묶음 이름이 'N강'이거나 칩에 EBS·올림포스·수능특강이 들어간 목차)는 부교재로 보고 잠근다.

결과는 _tools/public_school.json(공개 이름 목록)에 쓴다. seo.py가 돌 때 먼저 이 도구를
부르고, lock.mjs는 이 파일을 읽어 공개 목록의 syn·game을 잠그지 않는다.

    python3 _tools/public_school.py          # 목록 다시 만들기
    python3 _tools/public_school.py --check  # 쓰지 않고 보기만
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, '_tools', 'public_school.json')
MOCK = r'(?:\d{4}-\d{2}-g\d|suneung-\d{4}-\d{2})'
MOCK_LINK = re.compile(rf'^(?:\.\./)*study/{MOCK}/[^/]+/?$')


BOOK = re.compile(r'^\d+강$|EBS|올림포스|수능특강|수능완성')


def toc_links(path):
    s = open(path, encoding='utf8').read()
    m = re.search(r'var TOC = ', s)
    if not m:
        return None
    j = s.index('\n};', m.end())
    try:
        T = json.loads(s[m.end():j + 2].rstrip(';'))
    except ValueError:
        return None
    if any(BOOK.search(c) for c in T.get('chips', [])) or \
       any(BOOK.search(it.get('g', '')) for it in T.get('items', [])):
        return None  # 교재(부교재) 범위
    return [it.get('u', '') for it in T.get('items', [])]


def scan():
    pub, mixed = [], []
    base = os.path.join(ROOT, 'school')
    for term in sorted(os.listdir(base)) if os.path.isdir(base) else []:
        tdir = os.path.join(base, term)
        if not os.path.isdir(tdir):
            continue
        for slug in sorted(os.listdir(tdir)):
            f = os.path.join(tdir, slug, 'index.html')
            if not os.path.isfile(f):
                continue
            links = toc_links(f)
            name = f'{term}-{slug}'
            if links and all(MOCK_LINK.match(u) for u in links):
                pub.append(name)
            else:
                mixed.append(name)
    return pub, mixed


def load():
    try:
        return json.load(open(OUT, encoding='utf8'))
    except (OSError, ValueError):
        return []


def main(check=False):
    pub, mixed = scan()
    if not check:
        old = load()
        if old != pub:
            json.dump(pub, open(OUT, 'w', encoding='utf8'), ensure_ascii=False, indent=1)
            open(OUT, 'a', encoding='utf8').write('\n')
    print(f'학교별 공개(모의고사만): {len(pub)}개 · 교과서·부교재 섞임(잠금): {len(mixed)}개')
    return pub


if __name__ == '__main__':
    main('--check' in sys.argv)
