# 코코스 중등 문법 — 매주 예약 작업 순서 (원장님 결정 2026-11-06)

매주 **수요일 밤** 예약 작업이 이 파일대로 문법 편 하나를 만들어 **검토를 통과하면 바로 공개**하고, 블로그 원고·이미지까지 만든다.
원장님은 **목요일**에 블로그에 올린다(독해는 일요일 밤 제작 → 월요일 블로그, `reading_weekly.md`).
**예약 작업 중에는 아무것도 묻지 않는다**(AskUserQuestion 쓰지 않음). 정한 것은 보고에 적는다.
규칙은 cocos-mid-original 스킬(공개 자료·선행 광고 금지), cocos-homepage-publish 스킬(올리기·비밀번호)을 따른다.

## 무엇을 만드나 (원장님 2026-11-06)
- **독해와 엮는다**: 그 주 월요일에 나간 독해 회차(`study/reading-m<학년>-<회>/`)의 지문 문장으로 문법 하나를 정리한다. 주소는 같은 번호 `study/grammar-m<학년>-<회>/`(공개 규칙 자동).
- **한국 학생이 자주 틀리는 문장으로 끈다, 제목은 질문형**(예 1회 'today는 되는데 yesterday는 왜 안 될까?'). 근거 없는 숫자('90%가 틀린다')는 쓰지 않고 '자주 틀리는'·'헷갈리는'까지만.
- 견본·기준판: **`study/grammar-m2-01/`**(중2 1회 현재완료, 독해 1회 4번 해달 일기). DATA 꼴·분량·말투는 이 페이지를 그대로 따른다(지우지 말 것).

## 0. 준비 (매번)
- 저장소: `/home/claude/cocos`가 없으면 clone(안 되면 add_repo로 Leslie-creator479/cocos를 push 권한으로 붙임). `git pull --rebase origin main`. CLAUDE.md를 먼저 읽는다.
- `bash _tools/mid_sheet/setup_env.sh`.
- 작업 폴더 `W=<스크래치패드>/gram-<slug>`. 견본 DATA를 본보기로 꺼낸다: `python3 -c "s=open('study/grammar-m2-01/index.html').read(); i=s.index('var DATA = '); open('$W/sample.js','w').write(s[i:s.index('\n};',i)+3])"`.
- 할 일 목록(TaskCreate): 편 고르기 → 문법 고르기 → DATA 쓰기 → 검토 → 녹음·올리기 → 블로그 → 안내 파일 → 보고.

## 1. 편 고르기
- `study/reading-m<학년>-<회>/`가 있는데 `study/grammar-m<학년>-<회>/`가 없는 회차 중 **가장 최근**(계획표 `reading_plan.json`의 published 날짜가 가장 늦은 것). 없으면(그 주 독해가 hold 등) 6번 보고만 하고 끝낸다.
- 지난 회차가 밀려 있어도 한 번에 한 편만 만든다(밀린 편은 원장님께 알린다).

## 2. 문법 고르기 (메인이 직접)
- 그 회차 지문 5편의 핵심 문법(각 지문 footer '핵심 문법 …', 계획표 passages의 grammar) 중 **학생이 자주 틀리는 문장이 가장 선명한 것** 하나. `_tools/mid_sheet/gram_log.json`(지금까지 만든 편의 학년·문법)을 보고 같은 학년에서 이미 다룬 문법은 피한다.
- 고르는 기준: ① 틀린 문장 하나로 '어? 이게 틀려?'가 나오는가(예 간접의문문 Do you know where is it?, 관계대명사 what을 the thing what으로, 분사 I was boring/bored, 가정법 If I am you) ② 그 지문에 그 문법 문장이 2개 이상 있는가 ③ 학교 서술형에 자주 나오는가.
- 그 지문 학습지(`study/reading-…/<번호>/index.html`)의 DATA.sentences에서 문법 문장과 **대비되는 문장**(예 현재완료 ↔ 과거형)을 고른다. 문장 번호는 학습지 번호 그대로.

## 3. DATA 쓰기 → 검토
- `$W/data.js`를 견본과 같은 꼴로 쓴다(작업 안내 `kit/GRAM_SPEC.md`). 검사: `python3 _tools/mid_sheet/make_gram.py $W/data.js "<title>" $W/out/index.html` → 아래 브라우저 검사.
- 검토(**빼지 않는다**): `kit/GRAM_REVIEW.md`를 채워 **다른 에이전트**에게 맡긴다(직접 풀어 정답이 하나인지, 영국·미국 영어 차이로 다른 답이 되는지, 고쳐 쓰기·조건 영작에서 맞게 쓴 다른 답이 오답이 되는지, 문법 설명 과장, 우리말과 시제가 맞는지). 걸린 것은 메인이 고친다. 1회에서 걸린 것: 이야기 흐름상 had p.p.로 읽힐 수 있는 문장, for를 현재완료 전용 표지처럼 쓴 표, 조건이 느슨해 과거형으로도 조건을 다 지키는 영작(조건에 '<문법>으로 쓸 것'), 부사구를 앞에 둬도 되는 배열, 우리말 '아팠다'(현재 상태인데 과거처럼 들림).
- **막히면**: 문법을 그 회차의 다른 것으로 한 번 바꾼다. 그래도 안 되면 올리지 않고 `gram_log.json`에 status `hold`(이유)로 적고 보고한다.

## 4. 녹음 → 올리기
- `make_gram.py data.js "<title>" $W/out/index.html` → `python3 _tools/mid_sheet/build_saudio.py $W/out/index.html`(지문 속 문장, 발음은 독해 때 고친 SAYFIX·TEXTFIX·PRON이 그대로 적용).
- 브라우저 검사(playwright, 400px·900px): 가로 넘침 없음(scrollWidth = 폭), 콘솔 오류 없음, O/X·퀴즈·고쳐 쓰기·조건 영작·배열이 눌리고 채점됨, 'PDF로 저장' 화면이 그려짐.
- `wrap.py $W/out/index.html study/<slug>/index.html` → `public_notice.py` → `brand_links.py` → `add_library.py study "<학년> <회>회 · <문법>" study/<slug> 1 --group "코코스 중등 문법 · <학년>"` → `git pull --rebase` → `seo.py`(출력을 파일로, 'study/<slug>'가 sitemap.xml에 있는지) → `COCOS_LOCK_PW=… node _tools/lock.mjs lock` → `status`('안 잠김 0쪽') → 페이지에 cocos-lock·noindex·'학원생 전용' 없음 → 커밋·푸시 → check-runs 성공.
- 짝 독해 지문의 확인 퀴즈 위 '이 지문의 문법(…)을 더 연습하려면 → 문법 학습지'는 `assets/print-sheet.js`가 문법 페이지의 links(`'../reading-…/<번호>/'`)를 보고 자동으로 띄운다. links 첫 줄에 그 지문 주소를 꼭 넣는다.

## 5. 블로그 원고
- 설정 `_tools/mid_sheet/gram_blog/<slug>.json`(본보기 `grammar-m2-01.json`): grammar, title(`<학년> 영어 문법 무료 학습지 <회>회 | <문법> | <질문형 한 줄> | 코코스학원`), tags, hook 2줄(첫 줄은 틀린 문장으로 시작, 둘째 줄은 그 주 독해 회차·행사와 이어서), cover_q·cover_wrong·cover_right·cover_sub, uses_title, compare_title, reading(짝 지문 이름·주소), reading_line.
- `python3 _tools/mid_sheet/gram_blog.py <설정> -o $W/blog` → 이미지 5장이 모두 'OK'(넘침이면 문구를 줄임)·눈으로 확인 → `build_tools_index.py` → `seo.py` → 커밋·푸시. 원고 페이지 https://cocosedu.kr/tools/blog/<slug>/ 는 원고 저장용이고, 이미지는 저장소에 올리지 않는다.

- **발행함에 넣기(원장님 결정 2026-11-11, 네이버 서식 + 그림 한 장씩 복사)**: `_tools/blog_box/grammar.json`의 posts 맨 앞에 이번 글을 넣는다(`{"page": "tools/blog/<slug>/index.html", "name": "<학년> <회>회 <짧은 이름>", "imgdir": "$W/blog"}`, posts는 최근 3편까지만 남김) → `python3 _tools/blog_box.py _tools/blog_box/grammar.json -o $W/box.html` → Artifact `read`(설정의 url) → Artifact 발행(file_path `$W/box.html`, url 설정의 url, files `$W/box.files.json` 내용). 설정의 url이 비어 있으면 url 없이 icon `blog`, capabilities `{"downloads": true}`로 처음 발행하고 받은 주소를 url에 적는다. 발행한 뒤 설정에서 imgdir를 지우고 커밋한다. 원장님께 드리는 원고 주소는 이 발행함 주소다(홈페이지 원고 페이지는 원고 저장용). Artifact 도구가 없거나 발행이 실패하면 예전처럼 홈페이지 원고 주소를 드리고 이미지를 SendUserFile로 보내며 보고에 그 사실을 적는다.
## 6. 마무리·보고
- `gram_log.json`에 `{slug, grade, round, grammar, passage, title, published}`를 더하고, CLAUDE.md의 `study/grammar-m…` 줄에 한 줄(문법·짝 지문·검토에서 고친 것). 커밋·푸시.
- 보고(SendUserMessage): 편·문법·짝 독해 지문, 질문형 제목, 학습지 주소, 블로그 발행함 주소·제목·태그, 검토에서 고친 것, 고친 발음. 이미지는 발행함에 들어 있으므로 따로 보내지 않는다(발행함에 못 넣었을 때만 SendUserFile). 보류했으면 이유.
