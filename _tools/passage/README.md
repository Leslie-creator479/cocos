# 고등 온라인 학습지 틀·도구 (cocos-passage-studio · cocos-passage-addons · cocos-passage-toc-blog)

2026-11-28 사용량 줄이기: 스킬 안에 통째로 들어 있던 템플릿과 스크립트를 이 폴더로 옮겼다.
스킬에는 사용법만 남기고, 작업할 때 이 폴더를 작업 폴더로 복사해 쓴다.

    mkdir -p /home/claude/cocos-study && cp /home/claude/cocos/_tools/passage/* /home/claude/cocos-study/

| 파일 | 쓰는 단계 |
|---|---|
| `template.html` | 지문 학습지 틀(디자인·버튼·브랜드·법적 표시). DATA 예시(2026 6월 고2 20번)는 품질 기준 |
| `put_data.py` | 틀을 복사해 `<title>`과 DATA만 바꿈(studio 7단계) |
| `build_audio.py`, `build_saudio.py` | 단어·문장 녹음(studio 7-1·7-2) |
| `check.js` | studio 8단계 검사 |
| `addons.py`, `check_addons.js` | 추가 규칙 적용·검사(addons 2·3단계) |
| `build_toc.py` | 목차(toc-blog 1단계) |
| `thumb.js`, `blog_kit.py` | 블로그 대표 이미지, 수록 지문 목록·태그(toc-blog 2단계) |

틀이나 스크립트를 고치면 이 폴더의 파일을 고쳐 커밋한다(스킬에 다시 붙여 넣지 않는다).
`_tools`는 seo.py·analytics.py·lock.mjs 등이 건너뛰는 폴더라 template.html이 페이지로 취급되지 않는다.
