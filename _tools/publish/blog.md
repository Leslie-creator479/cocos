# 홈페이지 게시 — 블로그 게시 세트 (정식 모의고사 자료만)

cocos-homepage-publish 스킬에서 옮긴 작업 규칙이다(2026-11-28, 스킬 크기를 줄이려고 나눔). 이 일을 할 때 읽고 규칙으로 그대로 지킨다. 'N번'은 스킬의 섹션 번호다. 공개 저장소라 학원생 비밀번호는 적지 않았다: `<비밀번호>` 자리에는 스킬에 있는 비밀번호를 넣는다.

## 6. 블로그 게시 세트 (cocos-passage-studio 11단계)
- **블로그 원고는 네이버 서식 발행함 아티팩트로 드린다**: 서식은 cocos-naver-blog-format 스킬. 원고 글은 지금처럼 홈페이지 원고 페이지(`tools/…/<slug>/`, noindex)로 만든다: 전용 도구가 있는 글(동의어·단어게임 원고, 중등 독해·문법 reading_blog.py·gram_blog.py)은 그 도구, 없는 글(모의고사 학습지 글, 안내 글, 연재 글, 시험 분석 글 등)은 원고.json(name·title·tags·body, 형식은 `_tools/blog_page.py` 머리말)으로 `python3 _tools/blog_page.py 원고.json tools/blog/<slug>/index.html`. 본문의 그림 자리는 `[대표 이미지: 파일.png]`·`[이미지: 파일.png]`(파일 이름을 꼭 적는다). 넣은 뒤 `build_tools_index.py` → seo.py(이때 `_tools/blog_style.py`가 원고 페이지의 복사 서식을 네이버 서식으로 맞춘다) → 7번대로 올린다. **원장님께는 원고 페이지 주소 대신 발행함 주소를 드린다**: `_tools/blog_box/<종류>.json`(reading·grammar·exam·syn·game·etc)의 posts 맨 앞에 이 글(`page`·`name`·`imgdir`)을 넣고 `python3 _tools/blog_box.py <설정> -o <스크래치>/<종류>.html` → Artifact `read`(설정 url) → 발행(file_path 그 html, url 설정 url, files는 함께 생긴 .files.json, url이 비면 새로 만들고 icon `blog`·capabilities `{"downloads": true}`, 받은 주소를 설정에 적음). 발행함은 원고 종류마다 하나만 쓰고 글마다 새 아티팩트를 만들지 않는다(원장님 계정 아티팩트 개수 한도). 그림은 저장소에 올리지 않고 발행함에만 올린다(SendUserFile로 따로 보내지 않음). 블로그에 올린 글은 posts에서 뺀다. 원장님께 드리는 안내(이미지 고르는 법 등)는 본문 블록에 넣지 않는다. 코드 블록·docx·붙여넣기용 HTML 파일로 드리지 않는다.
- **블로그 게시물 제목 맨 뒤에는 항상 ` | 성남 코코스영어학원`을 붙인다**. 학습지·동의어·반의어·단어게임 블로그 모두 같다. 원래 스킬의 제목 형식 뒤에 붙이는 것이다.
  - 학습지(cocos-passage-studio 11단계): `2026년 10월 고2 영어 모의고사 온라인 학습지 | 지문별 해석·단어·변형문제 | 성남 코코스영어학원`
  - 동의어·반의어(cocos-synonym-antonym 7단계, `blog.json`의 `title`): `2026년 10월 고2 영어 모의고사 동의어·반의어 온라인 학습지 | 18~45번 지문 변형 대비 | 성남 코코스영어학원`
  - 단어게임(cocos-word-game, `mkblog.py`가 만든 `blog.json`의 `title`에 덧붙인 뒤 `make_blog.py`): `2026년 10월 고2 영어 모의고사 단어게임 | 18~45번 단어 478개 놀면서 외우기 | 성남 코코스영어학원`
- 대표 이미지·본문·태그는 원래대로. 본문의 `▶ 온라인 학습지 바로가기` 링크는 목차의 **전체 주소**(`https://cocosedu.kr/study/2026-10-g1/`).
- **한 회차 = 블로그 글 3개(학습지·동의어·단어게임), 대표 이미지도 3장 모두 다르게**. 학습지 = cocos-passage-studio의 `thumb.js`(1920, 'N월 고N 온라인 학습지'), 동의어 = cocos-synonym-antonym의 `scripts/thumb_syn.js`(1920, '동의어 반의어 온라인 학습지', 글꼴은 `~/.cocos-fonts`), 단어게임 = cocos-word-game의 cover.js(1080, 게임 느낌, 로고는 그 회차 `game/<회차>/index.html`에서, 단어 수는 게임 원고 제목의 수). 학년 색은 셋 다 같게(고1 g1·고2 g2·고3 g3).
- 선생님이 "○○ 회차 블로그 글·이미지 만들어져 있나?"라고 물으시면: 동의어·단어게임 원고는 보통 `tools/syn-blog/<회차>/`·`tools/game-blog/<회차>/`에 이미 있고(제목·본문·태그가 그 페이지에), 수록 지문 목록도 `tools/blog-list/`에 있다(EXAMS id `y25m10g1`·`…syn`·`…wg`처럼 지난 연도는 y+연도 두 자리). 학습지 글은 cocos-passage-studio 11단계 틀의 제목·본문·태그를 원고.json으로 옮겨 `python3 _tools/blog_page.py 원고.json tools/blog/study-<회차>/index.html`로 원고 페이지를 만들고(본문의 지문 목록은 `["list"]` 블록 + groups), 대표 이미지 3장을 새로 만들어 글 세 편을 발행함(etc·syn·game)에 넣어 그 주소를 드린다(blog-list에 회차가 이미 있으면 blog_kit.py로 다시 넣지 않고 목록만 읽어 쓴다).
- **지난 연도 회차의 태그**: 회차 태그 앞에 연도를 붙여 올해 회차와 구분한다(`2025년10월고1모의고사`). 100자를 넘으면 일반 태그 `영어서술형`을 뺀다.
- `blog_kit.py`에는 전체 주소를 넘긴다: 목차 링크 인자는 전체 주소, toc.json은 `u`를 전체 주소로 바꾼 복사본(`toc_abs.json`)을 쓴다.
- '블로그 수록 지문 목록'은 이제 **홈페이지판 `tools/blog-list/index.html`이 기준**이다(옛 아티팩트 `X6r3Q1W4UKT8zsbcmCt5Fs`는 더 고치지 않는다). 원래 스킬의 '목록 페이지 받기·게시' 대신 이 파일을 `blog_kit.py`(단어게임은 `add_wg.py`)의 목록 페이지 파일로 바로 넘기고 7번대로 올린다. 교과서 지문 목록 `tools/textbook-list/index.html`(옛 `QCzpo59iKTBSExMvAQDkDM`)은 교과서 자료를 블로그에 올리지 않기로 해서 선생님이 부탁할 때만 고친다. 링크는 모두 `https://cocosedu.kr/…` 전체 주소.
- 원고·목록을 넣거나 고친 뒤에는 `python3 _tools/build_tools_index.py`로 **선생님 자료함**(`https://cocosedu.kr/tools/`) 첫 화면을 다시 만든다. 자료실 카드(`add_library.py`)를 넣은 뒤에도 돌린다(자료함의 '학생용 주소' 줄이 자료실 데이터로 만들어진다).
- 답변의 "공유 설정을 바꿔야 한다" 안내는 하지 않는다(홈페이지는 모두 공개).
