> 틀(2026-11-05, 코코스 중등 독해 회차 작업). 메인이 지문마다 작업 폴더에 SPEC_<k>.md로 복사해 {…} 자리를 채워 준다.

# 코코스 중등 독해(오리지널 지문) — 학습지 DATA 쓰기

코코스학원이 직접 쓴 중등 독해 지문으로 공개 온라인 학습지를 만든다. 학습지 틀·기능은 중등 교과서 본문 학습지와 똑같다.
지문은 메인이 이미 썼다: `{V}/p{K}.txt` ({GRADE} · {STAGE} · {KIND}, {WORDS}단어, 핵심 문법 {GRAM}). **영어 원문은 한 글자도 바꾸지 않는다**(’ 그대로). 첫 줄이 날짜·제목 줄이면(예 일기의 `Saturday, May 20`) 문장에 넣지 않고 첫 문장 해석 앞에 괄호로 밝힌다.
저장소(/home/claude/cocos) 파일은 고치지 않고 git도 쓰지 않는다(도구 실행만).

## 먼저 읽을 것
1. 규칙 전체: cocos-passage-mid 스킬의 SKILL.md('확인 퀴즈 15문항' 표와 주의). 스킬 폴더는 `ls -d /root/.claude/skills/*/*/cocos-passage-mid /root/.claude/skills/*/cocos-passage-mid 2>/dev/null`로 찾는다.
2. brief 규칙: cocos-passage-addons 스킬 1번 / vocab·map·order 규칙: cocos-passage-studio 스킬 4·5·6-1단계.
3. 품질 기준(같은 시리즈, 검토 끝남, 원장님 확인): `{V}/sample/data_1.js`~`data_5.js`(중2 1회 「동물의 놀라운 비밀」). 키·말투·문항 수준·해설 방식을 그대로 따르되 문항 문구를 베끼지 않는다. 학년이 다르면 난이도·설명 말투를 그 학년에 맞춘다(중1은 쉬운 말, 문법 용어는 풀어서).

## 파일: `{V}/data_{K}.js` (var DATA = { … }; 하나)
- chips: `['코코스 중등 독해 · {GRADE} · {STAGE}', '{ROUND}회 {K}번 · {KIND} · {WORDS}단어 · 기본 어휘 {PCT}%']`
- h1: `{H1}` (핵심 개념: 질문형 부제, 바꿔도 됨) / enTitle: `{EN}` / gist: 두 문장 이내(지문이 may·think처럼 조심스러우면 gist도 그렇게)
- footer: `지문: 코코스학원 오리지널 지문 ({GRADE} · {STAGE} · {KIND} · 핵심 문법 {GRAM_SHORT})`
- sentences: p{K}.txt를 문장 단위로 나눈 en과 자연스러운 우리말 해석 ko(1:1, 그 학년이 읽기 쉬운 말).
- 나머지 키(gloss, vocab, map, quiz, order, brief)는 샘플과 같게. 확인 퀴즈 15문항 순서·type은 cocos-passage-mid 표 그대로(5번은 설명문 주제, 이야기·일기 심경, 편지 목적).
- **7번 문법 · 쓰임은 {GRAM}**: {G7}
- brief 'tips'에 {TIPS} 꼭 포함.
- vocab 13~18개: 기본 어휘 밖 낱말과 시험에 나올 낱말({VOC}). p는 동·명·형·부·숙. 고유명사는 vocab에 넣지 않는다.
- {NOTE}
- 사실 내용은 지문 안 정보만 근거로 묻는다(바깥 지식이 필요하면 안 됨). 정답 a(0부터)는 ①~⑤ 정확히 3번씩. 문자열 안에 작은따옴표(') 금지, 아포스트로피는 ’.
- 선행학습 유발 표현('고등', '고1', '선행', '한 학년 위') 쓰지 않는다.
- 1회 검토에서 걸린 것(처음부터 피하기): T/F에서 '글에 안 나옴'과 '틀림'이 헷갈리는 진술(→ 글과 분명히 어긋나게), 연결어 오답이 한쪽 빈칸만 보면 맞아 보임, 요약문 오답이 너무 쉬움, 배열에서 부사구를 따로 두어 어순이 둘, 지칭 발췌문에서 가리키는 말이 빠짐, 동물 선행사 뒤 who/which를 어법 보기로 냄(둘 다 됨), 한 문항이 다른 문항의 답을 알려 줌.

## 검사 (OK가 나와야 끝)
```
cd /home/claude/cocos && python3 _tools/mid_sheet/make_mid.py {V}/data_{K}.js "{TITLE}" {V}/chk/{K}/index.html --base {V}/base.html && node _tools/mid_sheet/check_mid.js {V}/chk/{K}/index.html
```
('발음 없음 N'·'문장 녹음 0/N'은 녹음 전이라 정상.)

## 보고(짧게)
문장 수, 7번에 쓴 밑줄 문장과 정답·함정, 스스로 애매하다고 느낀 문항 번호와 이유. 파일 내용은 붙이지 않는다.
