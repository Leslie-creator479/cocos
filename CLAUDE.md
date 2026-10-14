# 코코스학원 홈페이지 저장소 안내

GitHub Pages로 공개되는 코코스학원 홈페이지·온라인 학습지 저장소다. `main` 브랜치에 올리면 1~2분 뒤 반영된다.
주소: **https://cocosedu.kr/** (가비아 도메인, 2026-10-14 연결. 저장소 루트의 `CNAME` 파일이 이 도메인을 정한다. 지우지 말 것). 예전 주소 https://leslie-creator479.github.io/cocos/ 로 들어와도 자동으로 넘어간다. 페이지끼리는 상대 경로로 이어져 있다.

## 폴더 구조
| 경로 | 내용 |
|---|---|
| `index.html` | 홈페이지 첫 화면(시안 8 미드나잇 네이비, 2026-10-14 확정). 원장 인사·성과·상담 시간·주소는 내용을 받으면 다시 넣는다. 2026-10-14부터 설명회 시즌이라 입시 컨설팅·예비고1 설명회 섹션(`#consult`, 카드 `#seminar`)을 맨 위에 두고 금색 안내 띠·머리글 '설명회 문의' 버튼으로 강조한다. 시즌이 끝나면 첫 화면(.hero) 아래로 되돌린다 |
| `library/` | 자료실. 큰 분류 탭 **모의고사 / 교과서 / 학교별 시험 범위**, 그 안에 **학습지(학교별은 '시험 범위 목차') / 동의어·반의어 / 단어게임** 작은 탭(2026-10-14 선생님 결정). 분류는 주소로 자동: 모의고사 회차 이름이면 모의고사, `textbook/`과 교과서 약칭으로 시작하는 syn·game(예 `syn/ce1min-1`)은 교과서, 나머지(학교별·부교재)는 학교별 시험 범위. 카드 데이터는 `_tools/add_library.py`로만 고친다(탭 인자는 그대로 study·textbook·school·syn·game) |
| `study/<연도>-<월2자리>-g<학년>/` | 학력평가 회차 목차. 지문은 `.../<번호>/` (예 `study/2026-06-g2/23/`, 장문 `41-42`, `43-45`) |
| `study/olympos1/`, `study/olympos2/` | 올림포스 기출 지문 `<강>-<번호>/` (예 `study/olympos2/7-3/`) |
| `textbook/<교재>/<과>/` | 교과서 과별 목차, 본문 `.../<번호>/` (예 `textbook/neo2/1/3/` = 영어II 능률(오선영) 1과 본문 3번). 교재: `neo2` 영어II 능률(오선영), `ce1min` 공통영어1 능률(민병천). 스페셜 레슨은 과 자리에 `s1`(syn·game은 `ce1min-s1`, 선생님용 교과서 지문 목록에서는 lessons 101) |
| `school/2026-2-mid/<학교>-g<학년>/` | 학교별 시험 범위 목차(학교: dongkwang, seongnam, seongnam-girls, seongil, pungsaeng) |
| `syn/<회차>/` | 동의어·반의어 (회차 이름은 study와 같다. 교과서는 `syn/neo2-1-3`, `syn/ce1min-1`처럼) |
| `game/<회차>/` | 단어게임 (교과서는 `game/ce1min-1`처럼 syn과 같은 이름) |
| `tools/` | 선생님 자료함(검색 제외). `tools/index.html` 첫 화면은 `_tools/build_tools_index.py`로만 만든다. `tools/blog-list/` 블로그 수록 지문 목록(이게 기준판, 옛 아티팩트판은 더 고치지 않음), `tools/textbook-list/` 교과서 지문 목록, `tools/game-blog/<회차>/`·`tools/syn-blog/<회차>/` 블로그 원고, `tools/templates/` 틀 |
| `preview/` | 홈페이지 디자인 시안(noindex) |
| `_tools/` | 작업 도구: `wrap.py`(완전한 HTML로 감싸기), `fix_links.py`(claude.ai 링크 → 홈페이지 주소), `add_library.py`(자료실 카드), `build_tools_index.py`(선생님 자료함 첫 화면), `brand_links.py`(학원 안내 카드), `seo.py`(검색 노출·sitemap·robots), `lock.mjs`(교과서·부교재 학원생 잠금), `artifact_map.json`(옛 아티팩트 id → 저장소 경로) |

## 규칙
- 모든 페이지는 `<폴더>/index.html` 하나. 파일 이름이 아니라 폴더 주소로 연다.
- 아티팩트용으로 만든 페이지는 겉틀이 없으니 `python3 _tools/wrap.py 원본.html 경로/index.html`로 감싸서 넣는다(선생님용 페이지는 `--noindex`).
- 페이지 사이 링크는 **상대 경로**로 쓴다(목차 → 지문 `18/`, 지문 → 목차 `../`, 동의어 → 목차 `../../study/2026-06-g1/`). 블로그·카카오톡에 붙일 링크만 전체 주소(`https://cocosedu.kr/…/`)를 쓴다.
- 페이지에 claude.ai 링크(`https://claude.ai/artifact/<id>`)가 남아 있으면 `python3 _tools/fix_links.py <페이지 경로> <파일>`로 바꾼다. 아직 없는 새 페이지는 스크립트에 가짜 id(경로의 `/`를 `_`로, 예 `study_2026-10-g1_18`)를 넘겨 두면 이 도구가 경로로 바꾼다.
- 저장소는 공개다. 학생 이름·전화번호 같은 개인정보, 코코 키우기·100일 습관 같은 기록 페이지는 올리지 않는다.
- 올리기: `git add -A && git commit -m "<무엇을>" && git push origin main`. 한 번에 50MB가 넘으면 회차별로 나눠 커밋·푸시한다. 푸시 전 `git pull --rebase origin main`.
- 올린 뒤 1~2분 기다렸다가 WebFetch로 새 주소를 열어 제목이 맞는지 확인하고 링크를 드린다(공유 설정은 필요 없다. 모두 공개).
- 학생용 페이지(study·textbook·school·syn·game)를 새로 넣거나 다시 만들면 `python3 _tools/brand_links.py <파일들>`를 돌린다(로고 → 홈페이지, 아래 학원 안내 카드 = 자료실·블로그·인스타그램·홈페이지·플레이스 같은 크기 버튼).
- **검색 노출**: 모의고사(학력평가) 자료와 홈페이지 첫 화면·자료실만 검색에 열고, 교과서·부교재(올림포스 등)·학교별 자료와 그걸로 만든 동의어·단어게임은 저작권 때문에 noindex로 막는다(선생님 결정 2026-10-14). 페이지를 넣거나 고친 뒤 올리기 전에 항상 `python3 _tools/seo.py`를 돌린다(빠진 noindex를 붙이고 sitemap.xml·robots.txt를 다시 만든다. 인자 없음, 여러 번 돌려도 같다). 새 부교재 폴더(예 study/suteuk)는 자동으로 막힌다. robots.txt로 학습 자료 폴더를 막지 않는다(막으면 noindex를 못 읽는다).
- **학원생 비밀번호 잠금**: 교과서(textbook/)와 부교재(study/olympos… 등)·교과서·학교별 동의어·단어게임(모의고사 회차 이름이 아닌 study·syn·game)은 `_tools/lock.mjs`로 잠근다(선생님 결정 2026-10-14. 학교별 목차 school/는 잠그지 않는다). 비밀번호는 스킬(cocos-homepage-publish)에만 있고 이 공개 저장소에는 적지 않는다. 잠긴 파일은 암호문이라 직접 고칠 수 없다: `unlock`으로 풀고 고친 뒤 다시 `lock`. 올리기 전 순서는 brand_links.py → seo.py → `node _tools/lock.mjs lock`. 잠금 안내 화면의 학원 표시(ACAD)나 문구를 바꾸면 `relock`.
- 블로그 게시 세트(대표 이미지·글·수록 지문 목록)는 모의고사 자료만 만든다. 교과서·부교재 자료는 블로그에 올리지 않는다(선생님 결정 2026-10-14).
- 학원 표시(교습과목·교습비)는 지금 '중·고등 영어 / 중등부 300,000원 · 고등부 360,000원'. 초등(5·6학년, 초등부 250,000원)은 교육청 등록 처리 뒤에 홈페이지 바닥글·프로그램, 학생용 페이지 카드(`acad-info`), `_tools/lock.mjs`의 `ACAD`(바꾼 뒤 relock)에 함께 넣는다. 등록 전에는 넣지 않는다.
- 블로그 원고를 넣거나 블로그 수록 지문 목록·교과서 지문 목록에 회차를 더한 뒤에는 `python3 _tools/build_tools_index.py`를 돌린다. 블로그 수록 지문 목록은 `tools/blog-list/index.html`을 고친다(blog_kit.py의 목록 페이지 파일로 이 파일을 넘긴다). 링크는 모두 `https://cocosedu.kr/…` 전체 주소.
