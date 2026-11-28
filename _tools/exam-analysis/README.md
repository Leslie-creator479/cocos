# 학교별 내신 분석 스크립트 (school-exam-analysis 스킬에서 옮김, 2026-11-28)

school-exam-analysis 스킬의 부록 A~F를 글자 그대로 옮겨 둔 곳이다. 쓰는 순서와 명령은 스킬 1~6번에 있다.
작업 폴더에 복사해서 쓴다: `cp /home/claude/cocos/_tools/exam-analysis/*.py /home/claude/cocos/_tools/exam-analysis/*.js .`
(exam_images.js는 같은 폴더의 fonts/·logo.txt를 쓰므로 작업 폴더에서 실행한다.)

| 파일 | 스킬 부록 | 하는 일 |
|---|---|---|
| exam_images.js | C | 블로그 이미지 6장(data.json) |
| build_report.py | D | 분석 report.json → COCOS 원지문 틀 .docx |
| build_compare.py | E | 원문 비교 compare.json → 2단 .docx |
| find_changes.py | F | 시험지·원지문 낱말 대조 |
| examples/data.json | A | data.json 예 (성남여고 2학년 2026 2학기 중간) |
| examples/report.json | B | report.json 예 (일부) |

compare.json 예(부록 G)는 학교 시험 문항 원문이 들어 있어 공개 저장소에 두지 않고 스킬에만 있다.

## 부록 A 메모 (원래 문장)
`{{…}}`는 빨간 펜 색. `map`은 5단계 '`map` 쓰는 법'을 따른다(아래 `map`만 동광고 2026 1학년 중간의 실제 값 일부다). 부교재 범위면 `source.lessons_title`을 더 쓴다.
