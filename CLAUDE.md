# 코코스학원 홈페이지 저장소 안내

GitHub Pages로 공개되는 코코스학원 홈페이지·온라인 학습지 저장소다. `main` 브랜치에 올리면 1~2분 뒤 반영된다.
주소: **https://cocosedu.kr/** (가비아 도메인, 2026-10-14 연결. 저장소 루트의 `CNAME` 파일이 이 도메인을 정한다. 지우지 말 것). 예전 주소 https://leslie-creator479.github.io/cocos/ 로 들어와도 자동으로 넘어간다. 페이지끼리는 상대 경로로 이어져 있다.

## 폴더 구조
| 경로 | 내용 |
|---|---|
| `index.html` | 홈페이지 첫 화면(시안 8 미드나잇 네이비, 2026-10-14 확정). 원장 인사·성과·상담 시간·주소는 내용을 받으면 다시 넣는다 |
| `library/` | 자료실(탭: 학력평가·교과서·학교별 시험 범위·동의어·반의어·단어게임). `_tools/add_library.py`로만 고친다 |
| `study/<연도>-<월2자리>-g<학년>/` | 학력평가 회차 목차. 지문은 `.../<번호>/` (예 `study/2026-06-g2/23/`, 장문 `41-42`, `43-45`) |
| `study/olympos1/`, `study/olympos2/` | 올림포스 기출 지문 `<강>-<번호>/` (예 `study/olympos2/7-3/`) |
| `textbook/<교재>/<과>/` | 교과서 과별 목차, 본문 `.../<번호>/` (예 `textbook/neo2/1/3/` = 영어II 능률(오선영) 1과 본문 3번) |
| `school/2026-2-mid/<학교>-g<학년>/` | 학교별 시험 범위 목차(학교: dongkwang, seongnam, seongnam-girls, seongil, pungsaeng) |
| `syn/<회차>/` | 동의어·반의어 (회차 이름은 study와 같다. 교과서는 `syn/neo2-1-3`처럼) |
| `game/<회차>/` | 단어게임 |
| `tools/` | 선생님 자료함(검색 제외). `tools/index.html` 첫 화면은 `_tools/build_tools_index.py`로만 만든다. `tools/blog-list/` 블로그 수록 지문 목록(이게 기준판, 옛 아티팩트판은 더 고치지 않음), `tools/textbook-list/` 교과서 지문 목록, `tools/game-blog/<회차>/`·`tools/syn-blog/<회차>/` 블로그 원고, `tools/templates/` 틀 |
| `preview/` | 홈페이지 디자인 시안(noindex) |
| `_tools/` | 작업 도구: `wrap.py`(완전한 HTML로 감싸기), `fix_links.py`(claude.ai 링크 → 홈페이지 주소), `add_library.py`(자료실 카드), `build_tools_index.py`(선생님 자료함 첫 화면), `artifact_map.json`(옛 아티팩트 id → 저장소 경로) |

## 규칙
- 모든 페이지는 `<폴더>/index.html` 하나. 파일 이름이 아니라 폴더 주소로 연다.
- 아티팩트용으로 만든 페이지는 겉틀이 없으니 `python3 _tools/wrap.py 원본.html 경로/index.html`로 감싸서 넣는다(선생님용 페이지는 `--noindex`).
- 페이지 사이 링크는 **상대 경로**로 쓴다(목차 → 지문 `18/`, 지문 → 목차 `../`, 동의어 → 목차 `../../study/2026-06-g1/`). 블로그·카카오톡에 붙일 링크만 전체 주소(`https://cocosedu.kr/…/`)를 쓴다.
- 페이지에 claude.ai 링크(`https://claude.ai/artifact/<id>`)가 남아 있으면 `python3 _tools/fix_links.py <페이지 경로> <파일>`로 바꾼다. 아직 없는 새 페이지는 스크립트에 가짜 id(경로의 `/`를 `_`로, 예 `study_2026-10-g1_18`)를 넘겨 두면 이 도구가 경로로 바꾼다.
- 저장소는 공개다. 학생 이름·전화번호 같은 개인정보, 코코 키우기·100일 습관 같은 기록 페이지는 올리지 않는다.
- 올리기: `git add -A && git commit -m "<무엇을>" && git push origin main`. 한 번에 50MB가 넘으면 회차별로 나눠 커밋·푸시한다. 푸시 전 `git pull --rebase origin main`.
- 올린 뒤 1~2분 기다렸다가 WebFetch로 새 주소를 열어 제목이 맞는지 확인하고 링크를 드린다(공유 설정은 필요 없다. 모두 공개).
- 블로그 원고를 넣거나 블로그 수록 지문 목록·교과서 지문 목록에 회차를 더한 뒤에는 `python3 _tools/build_tools_index.py`를 돌린다. 블로그 수록 지문 목록은 `tools/blog-list/index.html`을 고친다(blog_kit.py의 목록 페이지 파일로 이 파일을 넘긴다). 링크는 모두 `https://cocosedu.kr/…` 전체 주소.
