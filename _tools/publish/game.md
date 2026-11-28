# 홈페이지 게시 — 단어게임 (cocos-word-game)

cocos-homepage-publish 스킬에서 옮긴 작업 규칙이다(2026-11-28, 스킬 크기를 줄이려고 나눔). 이 일을 할 때 읽고 규칙으로 그대로 지킨다. 'N번'은 스킬의 섹션 번호다. 공개 저장소라 학원생 비밀번호는 적지 않았다: `<비밀번호>` 자리에는 스킬에 있는 비밀번호를 넣는다.

## 9. 단어게임
- 단어게임 틀: 저장소 `game/2026-09-g1/index.html`(옛 `XYokMvZQrj7ivi24YG2LYB`). 겉틀을 떼고 `template_game.html`로 쓴다.
- 블로그 원고 틀: 저장소 `tools/templates/game-blog/index.html`(옛 `SmttMMaoWfyZKG98Seqz6L`, 아티팩트도 남겨 둠). 겉틀을 떼고 `template_blog.html`로 쓴다.
- 원본 찾기: 목차·동의어·지문 학습지를 저장소에서 읽고(잠긴 파일은 푼 본) `artifact-files/<id>/` 자리에 복사한다(3번). prep.py의 목차 URL·동의어 id 인자에는 옛 id나 가짜 id를 넘긴다.
- 단어게임: 완성 파일을 `wrap.py`로 `game/<회차>/index.html`에 두고 `fix_links.py game/<회차> …`. 자료실 `add_library.py game "2026년 10월 고1" game/2026-10-g1 22`.
- **단어게임 DATA의 학습지·동의어 링크**: 틀의 '학습지 열기'·'동의어·반의어 열기' 버튼은 `href: p.u`·`href: DATA.syn + '#' + p.sa`로 값을 그대로 쓴다. 그래서 DATA의 지문별 `u`에는 아티팩트 id가 아니라 **게임 기준 상대 경로**(`../../study/<회차>/<번호>/`, 교과서 `../../textbook/<교재>/<과>/<번호>/`), `syn`에는 `../../syn/<회차>/`를 넣는다(fix_links.py는 맨 id를 못 바꾼다). 넣은 뒤 `grep -c 'claude.ai/artifact'`가 0인지, 링크한 페이지가 저장소에 있는지 본다. 틀에 옛 코드가 남아 있으면 위 두 줄로 고친다.
- **빈칸 보기 후보**: cocos-word-game의 build.py로 만든 데이터에는 빈칸 정보가 없는 단어가 보기 후보에 섞일 수 있다(그 보기가 나오면 지문 속 빈칸 게임이 멈춤). seo.py가 돌 때 `fix_game_pool.py`가 자동으로 정리하므로 따로 할 일은 없다(2번).
- 블로그 원고(정식 모의고사만): mkblog.py의 게임 URL 인자에 게임 **전체 주소**를 넘기고, 생긴 `blog.json`의 `title` 끝에 ` | 성남 코코스영어학원`을 붙인 뒤(6번) make_blog.py를 돌린다. 만든 파일을 `tools/game-blog/<회차>/index.html`에 `wrap.py --noindex`로 둔 뒤 `fix_links.py --absolute`.
- 블로그 수록 지문 목록 단어게임 카드: games.json의 `url`에 게임 전체 주소를 넣고 `add_wg.py`를 `tools/blog-list/index.html`에 돌린다(6번). 원고를 넣었으면 `build_tools_index.py`.
- **발음 녹음**: 단어게임은 기기 음성 대신 녹음 MP3 `assets/say/<단어 slug>.mp3`(slug = 소문자, 영문·숫자 아닌 것은 `-`)를 튼다. 녹음이 없으면 기기 음성으로 넘어간다. 틀(`game/2026-09-g1`)에 이미 들어 있어 새 게임도 자동으로 쓴다(`DATA.say`가 없으면 `../../assets/say/`). **새 단어게임·단어장을 넣으면 올리기 전에 `COCOS_LOCK_PW=<비밀번호> python3 _tools/say_audio.py`**를 돌린다(게임 단어 중 녹음 없는 것을 학습지 AUDIO에서 꺼내 채움. 새 단어는 `--make`로 만든다. '남은 것'이 있으면 `--make`로 Kokoro af_heart 0.9 생성, kokoro-onnx·soundfile 설치와 /home/claude/.kokoro 모델 필요). '녹음 없음 0개'를 확인하고 올린다.
