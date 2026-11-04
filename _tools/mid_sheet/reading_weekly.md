# 코코스 중등 독해 — 매주 예약 작업 순서 (원장님 결정 2026-11-05)

매주 일요일 밤 예약 작업이 이 파일대로 회차 하나(지문 5편)를 만들어 **검토를 통과하면 바로 공개**하고, 블로그 원고·이미지까지 만든다.
원장님은 월요일에 블로그에 올린다. **예약 작업 중에는 아무것도 묻지 않는다**(AskUserQuestion 쓰지 않음). 정할 것은 이 파일·스킬 규칙대로 정하고, 결과 메시지에 무엇을 정했는지 적는다.
자세한 규칙은 cocos-mid-original 스킬(지문 쓰기·학습지 만들기·블로그), cocos-passage-mid 스킬(퀴즈 15문항 표), cocos-homepage-publish 스킬(올리기·비밀번호)을 따른다.

## 0. 준비 (매번, 1~2분)
- 저장소: `/home/claude/cocos`가 없으면 `git clone https://github.com/Leslie-creator479/cocos /home/claude/cocos`(안 되면 add_repo 도구로 Leslie-creator479/cocos를 push 권한으로 붙인 뒤 안내대로 clone). `git pull --rebase origin main`.
- `bash _tools/mid_sheet/setup_env.sh` (녹음 프로그램·어휘 도구·모델 준비).
- 작업 폴더 `W=<스크래치패드>/reading-<slug>` → `python3 _tools/mid_sheet/reading_prep.py $W` (틀·샘플은 공개된 중2 1회에서, 비밀번호 필요 없음).
- 할 일 목록(TaskCreate)을 띄운다: 지문 쓰기 → DATA → 검토 → 녹음 → 올리기 → 블로그 → 계획표·안내 파일 → 보고.

## 1. 회차 고르기
`_tools/mid_sheet/reading_plan.json`의 `plan`에서 `status`가 `todo`인 **맨 앞** 회차를 쓴다(학년 순서 중3 → 중1 → 중2, 원장님 결정). 이미 `study/<slug>/`가 있으면(같은 회차를 두 번 만들지 않기) 그 회차는 `done`으로 고치고 다음으로 넘어간다. todo가 없으면 6번 보고만 하고 끝낸다.

## 2. 지문 쓰기 (메인이 직접)
- 계획의 지문 5개(제목·단계·종류·핵심 문법). 단계는 **기본 2 · 표준 2 · 심화 1**(원장님 규칙). 단어 수: 중1 기본 80~110·표준 110~140·심화 140~180, 중2 100~130·130~170·170~220, 중3 120~160·160~200·200~250.
- **쓰기 전에** 소재 사실을 웹 검색으로 확인한다(박물관·대학·공공기관·과학 잡지). 전설·근거 약한 이야기는 쓰지 않는다. 확인이 안 되면 같은 주제의 다른 소재로 바꾸고 계획표 notes에 적는다.
- 재미있게: 첫 문장에 호기심 질문이나 의외의 사실. 핵심 문법을 자연스럽게 여러 번. 지문 `p<k>.txt`.
- `python3 _tools/edu_voca/coverage.py $W/p<k>.txt` → 기본 어휘 90% 이상(안 되면 소재어 반복을 대명사로 바꾸는 등 고침). 단어 수·% 는 이 값(날짜 줄은 빼고 센 값)을 chips에 쓴다.

## 3. DATA → 검토
- `$W/READING_SPEC.md`를 지문마다 `SPEC_<k>.md`로 채워(학년·단계·종류·단어 수·%·핵심 문법·title `[코코스학원] <학년> 영어 독해 <회>회 <k>번 · <단계> · <질문형 제목>`·h1·enTitle·7번 문법 함정·tips·vocab 후보·5번 유형) **5개 에이전트를 동시에** 띄운다(data_<k>.js, 검사 OK까지).
- 끝난 것부터 `READING_REVIEW.md`를 `REVIEW_<k>.md`로 채워(작성자가 남긴 애매한 곳, 확인할 사실 목록) **다른 에이전트**가 풀어 검토·사실 확인. **검토는 빼지 않는다.**
- 사실 확인에서 지문을 고쳐야 하면, 그 검토 에이전트에게 SendMessage로 바꿀 문장(en·ko)을 주어 문항·해설·brief·map·order·p<k>.txt까지 맞추게 한다(1회 예: algae 'tiny plants'→'tiny living things', 'young' 빼기, 'easily' 과장, 'Some sea otters', 물 위치→위험 경고).
- **막히면**: 검토 뒤에도 정답이 둘이거나 사실 확인이 안 되는 지문은 같은 주제의 다른 소재로 다시 쓴다(한 번까지). 그래도 안 되면 **그 회차를 올리지 않고** 계획표 status를 `hold`(notes에 이유)로 두고 6번에서 알린다. 틀린 자료를 올리는 것보다 한 주 쉬는 것이 낫다.

## 4. 녹음 → 올리기
- 지문마다 `make_mid.py data_<k>.js "<title>" $W/out/<k>/index.html --base $W/base.html` → `build_audio.py` → `build_saudio.py` → `check_mid.js`(발음 없음 0, 문장 녹음 N/N). 다섯 개를 한 스크립트로 이어서 백그라운드(시간 제한 넉넉히).
- 로그의 발음 기호로 고유명사·소재어·이야기 주인공 이름을 확인하고 틀리면 SAYFIX·TEXTFIX·PRON에 넣어 그 지문만 다시 녹음(이미 있는 틀린 `assets/say/<낱말>.mp3`는 지운다).
- `wrap.py` → `study/<slug>/<k>/index.html`. 목차: toc.json(chips `['코코스 중등 독해 · <학년>', '<회>회 · <주제> · 지문 5개']`, h1 `코코스 중등 독해 <학년> <회>회: <주제>`, gist 두세 문장, footer `지문: 코코스학원 오리지널 지문 · 누구나 무료로 쓰고 자유롭게 공유할 수 있어요.`) → `make_toc_mid.py toc.json "[코코스학원] 코코스 중등 독해 <학년> <회>회 온라인 학습지 목차 · <주제>" $W/out/toc/index.html --base $W/tocbase.html` → wrap.py로 `study/<slug>/index.html`.
- `public_notice.py` (목차·지문 6개) → `brand_links.py` → `add_library.py study "<학년> <회>회 · <주제>" study/<slug> 5 --group "코코스 중등 독해 · <학년>"` → 커밋되지 않은 변경 확인 → `git pull --rebase` → `seo.py`('열기 study/<slug>…') → `COCOS_LOCK_PW=… node _tools/lock.mjs lock` → `lock.mjs status`('안 잠김 0쪽') → 페이지에 `cocos-lock`·`noindex`·'학원생 전용' 없음 확인 → 휴대폰 너비 400px 확인(가로 넘침 없음) → 커밋·푸시 → check-runs 성공 확인.

## 5. 블로그 원고
- `_tools/mid_sheet/reading_blog/<slug>.json`을 쓴다(본보기 `reading-m2-01.json`): theme, hook(도입 1~2문장, 호기심 질문으로), sources(사실 확인 출처 한 줄), 지문마다 emoji·name·tag·key·q·did·ex·rule·story·gram_title·gram·words. 안내 글 링크는 도구가 자동으로 넣는다.
- `python3 _tools/mid_sheet/reading_blog.py _tools/mid_sheet/reading_blog/<slug>.json -o $W/blog` → '자동으로 채운 칸'이 없어야 한다. 이미지 6장을 열어 보고(넘침·잘림 없음) → `build_tools_index.py` → `seo.py` → 커밋·푸시.

## 6. 마무리·보고
- 계획표: 그 회차 `status: "done"`, `published: "<날짜>"`, 바꾼 소재는 notes. `done` 목록에도 slug·topics를 더한다(다음 계획에서 소재가 겹치지 않게).
- 저장소 CLAUDE.md의 `study/reading-m…` 줄에 회차 한 줄(주제·지문·단계·문법·사실 확인에서 고친 것)을 더한다. 커밋·푸시.
- **남은 todo가 2개 이하**면: 다음 12주 계획 초안을 같은 규칙(학년 순환, 주제 하나, 기본2·표준2·심화1, 학년 문법, 사실 확인 가능한 소재, `done`과 겹치지 않게)으로 만들어 `plan` 뒤에 `status: "draft"`로 넣고 커밋한다(예약 작업은 draft를 쓰지 않는다. 원장님이 확인하면 todo로 바꾼다).
- **보고**(원장님이 자리에 없으므로 SendUserMessage로): 회차·주제, 지문 5개 표(단계·종류·단어 수·%·문법), 목차·원고 주소, 블로그 제목·태그, 검토·사실 확인에서 고친 것, 고친 발음. 이미지 6장은 SendUserFile(status proactive). 남은 todo가 2개 이하면 맨 위에 **'회차 계획 추가 필요'**와 draft 계획 요약. 보류했으면 그 이유와 다음 주 계획.
