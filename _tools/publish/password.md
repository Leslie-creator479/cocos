# 홈페이지 게시 — 학원생 비밀번호 바꾸기·잠금 상태 확인

cocos-homepage-publish 스킬에서 옮긴 작업 규칙이다(2026-11-28, 스킬 크기를 줄이려고 나눔). 이 일을 할 때 읽고 규칙으로 그대로 지킨다. 'N번'은 스킬의 섹션 번호다. 공개 저장소라 학원생 비밀번호는 적지 않았다: `<비밀번호>` 자리에는 스킬에 있는 비밀번호를 넣는다.

## 10-1. 학원생 비밀번호 바꾸기 (선생님이 분기·시험 끝날 때마다 바꾼다)
선생님이 "비밀번호 ○○○○로 바꿔줘"라고 하시면:
1. 0번 준비 후 `cd /home/claude/cocos && git pull --rebase origin main`.
2. `COCOS_LOCK_PW=<지금 비밀번호> node _tools/lock.mjs lock` (혹시 안 잠긴 것부터 잠근다) → `COCOS_LOCK_PW=<지금 비밀번호> COCOS_LOCK_NEWPW=<새 비밀번호> node _tools/lock.mjs relock`.
3. 확인: 잠긴 파일 하나를 복사해 `COCOS_LOCK_PW=<새 비밀번호> node _tools/lock.mjs unlock <복사본>`이 '풀림'으로 나오는지 본다. `node _tools/lock.mjs status`에서 '안 잠김 0쪽'.
4. 커밋 메시지는 "학원생 비밀번호 변경"처럼만 쓰고 비밀번호는 적지 않는다. 올린 뒤 잠긴 페이지 하나를 WebFetch로 열어 안내 화면이 나오는지 본다.
5. **cocos-homepage-publish 스킬의 비밀번호(그 스킬 안의 옛 비밀번호를 모두)를 새 비밀번호로 바꾼 개선안을 `propose_skills`로 보여 드리고 저장을 부탁드린다.** 저장하지 않으면 다른 방이 새 자료를 옛 비밀번호로 잠가 자료마다 비밀번호가 달라진다.
6. 답변: 바꾼 쪽수, "학생들은 다음에 들어올 때 새 비밀번호를 한 번만 넣으면 된다", 스킬 카드 저장 부탁.

선생님이 "잠금 상태 확인해줘"라고 하시면 `node _tools/lock.mjs status`와 `python3 _tools/seo.py --check` 결과를 알려 드린다(안 잠긴 것이 있으면 7번대로 잠가 올린다).
