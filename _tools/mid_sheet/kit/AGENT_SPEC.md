> 틀(2026-10-25 중1 동아(이병민) 작업에서 씀). 새 교재를 할 때 작업 폴더에 복사해 교재 이름·약칭·지문 나누기·문법 예시를 그 교재에 맞게 바꿔 쓴다. 경로는 실제 작업 폴더로 바꾼다.

# 중1 동아(이병민) 교과서 중등 온라인 학습지 DATA 쓰기 — 작업 안내

당신은 한 과(課)의 교과서 본문을 지문별 학습지 DATA 파일로 만든다. 페이지 만들기·녹음·올리기는 하지 않는다(메인이 한다). 저장소(/home/claude/cocos)의 파일은 고치지 않고 git 명령도 쓰지 않는다(도구 실행만).

V = <학습지 작업 폴더>

## 먼저 읽을 것
1. 규칙 전체: `/root/.claude/skills/synced/16b95152-03aa-4f07-bb76-3e709241a39d_b34e3ed9-4804-47cd-9cd1-4218d493e9a8/cocos-passage-mid/SKILL.md` (특히 '고정 규칙', '페이지 문구', '확인 퀴즈 15문항' 표와 그 아래 주의)
2. '먼저 읽어 보세요(brief)' 규칙: `/root/.claude/skills/synced/16b95152-03aa-4f07-bb76-3e709241a39d_b34e3ed9-4804-47cd-9cd1-4218d493e9a8/cocos-passage-addons/SKILL.md` 1번
3. 단어(vocab)·마인드맵(map)·문장 배열(order) 규칙: `/root/.claude/skills/synced/16b95152-03aa-4f07-bb76-3e709241a39d_b34e3ed9-4804-47cd-9cd1-4218d493e9a8/cocos-passage-studio/SKILL.md` 4·5·6-1단계
4. 품질 기준 샘플(다른 교재 **중2** 동아(윤정미) 1과, 원장님이 확인함): `V/sample/data_1.js` ~ `V/sample/data_4.js` — 형식·키·말투·문항 수준·해설 방식을 그대로 따른다. 교재 표기는 **중1 동아(이병민)**(chips `2022 개정 중1 · 동아(이병민)`)로 쓰고, 난이도는 중1에 맞춘다.

## 본문 원본
`V/L<과>/본문.pdf`(왼쪽 영어, 오른쪽 한국어 해석)를 Read로 직접 열어 영어와 해석을 정확히 옮긴다. 참고용 추출 텍스트 `V/L<과>/layout.txt`(전체)가 있지만 PDF로 확인한다. 영어 원문은 한 글자도 바꾸지 않는다(둥근따옴표 ’ “ ” 살림). 해석은 PDF 해석을 문장 단위 1:1로 자른다.

## 지문 나누기 (메인이 정했다 — 이대로)
원장님 결정: 원본의 본문 구분(단락 덩어리·소제목·날짜)을 따르고, 구분 표시가 없는 이야기는 장면 묶음(20문장 넘지 않게). 맨 앞 짧은 도입은 첫 구분과 합친다. 지문이 5~7문장으로 짧아도 원본 구분대로 둔다.
- <과> <과 제목>: 1 `<label>`(<첫 문장> ~ <끝 문장>) · 2 `<label>` …  ← 메인이 PDF를 보고 과마다 채운다

스페셜 레슨은 폴더 `V/Ls1/`, meta.json의 lesson은 문자열 `"s1"`, chips 둘째 칸 `스페셜 레슨 본문 <k>번 · <label>`, footer `지문 출처: 2022 개정 중1 동아(이병민) 스페셜 레슨 Let’s Build a Strong Bridge! 교과서 본문 (<label>)`, 검사 title `[코코스학원] 중1 동아(이병민) 스페셜 레슨 본문 <k>번 · <t>`. 아래 '<과>과'는 스페셜 레슨에서 모두 '스페셜 레슨'으로 읽는다.

문장 다루기:
- 이름표·날짜형 소제목(Friday, September 5th / Poke, Hawaii, the United States / The Paper Bridge Challenge / [Rules] / 8과 편지의 Dear Nick, 등)은 문장으로 넣지 않는다. 대신 바뀌는 첫 문장 해석 앞에 괄호로 밝히거나(`(9월 6일)`) brief·label에서 말한다. 질문형 소제목(How Was Your Challenge?)은 본문 글자 그대로 한 문장으로 넣는다. 스페셜 레슨 규칙 글머리(•)는 기호를 빼고 문장으로 넣는다.
- 8과의 따옴표 대사만 있는 줄(“From today, your new name is frindle.”, “Can I borrow your frindle?”, “See page 541.” 등)도 한 문장으로 넣는다. 원문 `understand...`의 말줄임표는 그대로 둔다.
- 대화·인터뷰 글(Reporter: …, Gary: …)은 화자 이름까지 원문 그대로 그 화자의 첫 문장에 붙여 둔다(예 `Reporter: Hello, everyone!`).
- 따옴표 안 대사가 여러 문장이면 문장마다 나누되 따옴표는 원문 위치 그대로 둔다(샘플처럼). PDF에 곧은 따옴표(")와 둥근따옴표(“ ”)가 섞여 있으면 둥근따옴표로 통일한다(곧은 작은따옴표 '는 ’로).
- 원문에 줄바꿈 때문에 낱말 사이가 넓게 벌어진 줄이 있으면 공백 하나로 이어 쓴다.

## 파일 (모두 V/L<과>/ 폴더에)
- `data_1.js`, `data_2.js`, … : 지문마다 `var DATA = { … };` 하나 (샘플과 같은 키: chips, h1, enTitle, gist, footer, brief, sentences, gloss, vocab, map, quiz, order)
- `meta.json`: `{"book": "중1 동아(이병민)", "slug": "m1dalee", "lesson": <과>, "title": "<과 제목 영어>", "parts": [{"k": 1, "label": "<위 지문 나누기의 label 그대로>", "t": "<핵심 개념 2~10자, title·목차에 씀>"}, …]}`
- chips: `['2022 개정 중1 · 동아(이병민)', '<과>과 본문 <k>번 · <label>']`
- footer: `지문 출처: 2022 개정 중1 동아(이병민) <과>과 <과 제목> 교과서 본문 (<label>)`
- enTitle: `<과 제목> — <짧은 영어 부제>`
- 과 제목은 위 목록 표기 그대로(둥근따옴표 ’ 포함).

## 반드시 지킬 것
- 확인 퀴즈 15문항: 표의 순서·type 표기 그대로(5번은 지문 성격에 따라 '목적'·'주제'·'심경' 중 하나, 11번은 '어휘 · 영영풀이' 또는 '어휘 · 다의어'). 모두 5지선다. 정답 `a`(0부터)는 ①~⑤가 정확히 3번씩, 지문마다 정답 순서를 다르게.
- '모두 골라 짝지은 것은' 문항(1·6·7번)은 선택지가 조합(`ⓐ, ⓒ, ⓔ`)이고 정답이 하나뿐이게. 1번은 맞는 진술 3개, 6번은 틀린 곳 2개, 7번은 같은 쓰임 3개.
- 7번은 그 과의 핵심 문법(본문에서 반복되는 구문)을 고른다. 같은 과 안에서 지문마다 다른 구문이면 더 좋다. 예: 1과 be동사·일반동사 현재형(3인칭 단수 has·loves·dances)·부정문(don’t play), 2과 명령문(Look, Hold, Don’t worry, Let’s ~)·일반동사 의문문(do you have ~?)·too much, 3과 현재진행형(is throwing, I’m taking)·조동사 will·can, 4과 과거형(규칙·불규칙: came, ate, made)·There is/are·have to·could not, 5과 과거형·want to·감각동사(It was scary)·will, 6과 동명사 목적어(enjoy eating, like eating)·감각동사+형용사(looks colorful, tastes great, smells good)·명령문, 7과 비교급(brighter than, weaker than, stronger than anyone)·접속사 when·to부정사(started to paint, wanted to paint), 8과 접속사 that(I think that, I know that, I hope that)·stop -ing·과거진행형(were using), 스페셜 레슨 최상급(the strongest)·have to·can. 실제 본문에 있는 것으로 정한다.
- 6번(어법 밑줄)과 12번(어법 네모)은 같은 낱말을 묻지 않는다.
- 답이 정말 하나인지 스스로 다시 확인한다(특히 3번 '답할 수 없는 질문'은 글로 추론해도 답이 안 나와야 함, 9번 빈칸·15번 요약문은 다른 보기도 말이 되는지, 10번 지칭은 다른 밑줄도 같은 대상을 가리키지 않는지, 13번 배열은 다른 어순이 가능하지 않은지).
- DATA 문자열은 작은따옴표로 감싸므로 안에 작은따옴표(')를 쓰지 않는다. 아포스트로피는 ’(U+2019).
- vocab의 w는 실제 영어만(발음 녹음 글자). p는 동·명·형·부·숙 중 하나. 지문당 13~18개 안팎.
- order: 4단어 이하 문장만 빼고 모두, 어구를 공백 하나로 이으면 원문과 글자까지 같아야 한다. 첫 단어가 고유명사면 keep: true.
- brief.flow는 모든 문장 번호를 한 번씩 포함, keys 3개, tips 3~4개(그 과 핵심 문법 문장 꼭 포함, 영어 인용은 지문 글자 그대로 <i>…</i>), ask 2개.
- 선행학습 유발 표현('고등 과정', '고1', '선행' 등) 쓰지 않는다.

## 스스로 검사 (모든 data 파일이 OK가 나와야 끝)
```
cd /home/claude/cocos && python3 _tools/mid_sheet/make_mid.py V/L<과>/data_<k>.js "[코코스학원] 중1 동아(이병민) <과>과 본문 <k>번 · <t>" V/L<과>/chk/<k>/index.html --base V/base.html && node _tools/mid_sheet/check_mid.js V/L<과>/chk/<k>/index.html
```
(V는 위 전체 경로로 바꿔 쓴다.) 결과 첫 줄이 `OK`면 통과('발음 없음 N'·'문장 녹음 0/N'은 녹음 전이라 정상). V/sample·V/base.html과 다른 과 폴더는 고치지 않는다.

## 끝나면 보고 (짧게)
과 제목, 지문 수와 각 지문 label·t·문장 수, 7번에 쓴 문법, 원문에서 확인이 필요한 곳(판독이 애매한 글자 등). 파일 내용을 보고에 붙이지 않는다.

## 중1 교재 주의
이 교재는 **중학교 1학년**용이다. 스킬 문서의 '중2' 기준은 이 작업에서 모두 '중1'로 읽는다: 단어 정리·해설·brief는 중1 눈높이, 문항 난이도는 중1 내신 수준(지나치게 어려운 문법 용어는 쉬운 말로 풀어 쓴다).
