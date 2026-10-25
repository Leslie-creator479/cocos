#!/bin/bash
# 사용법: COCOS_LOCK_PW=<학원생 비밀번호> bash _tools/mid_sheet/kit/finish.sh <학습지 작업 폴더> <과…>
#   녹음이 끝난 과(L<과>/build.log 완료)를 검토 반영(--keep-audio)해 저장소에 넣고 seo → lock → 커밋·푸시.
#   과 이름: 숫자(1~8) 또는 스페셜 레슨 s1. 교재 이름은 L<과>/meta.json의 book.
#   비밀번호는 이 파일에 적지 않는다(cocos-homepage-publish 스킬에만 있음).
V=$1; shift
[ -z "$COCOS_LOCK_PW" ] && { echo "COCOS_LOCK_PW가 필요함"; exit 1; }
cd /home/claude/cocos || exit 1
BOOK=$(python3 -c "import json,sys;print(json.load(open(sys.argv[1]))['book'])" "$V/L$1/meta.json")
for n in "$@"; do
  grep -E "OK|완료" $V/L$n/build.log
  python3 _tools/mid_sheet/build_lesson.py $V/L$n --keep-audio --publish 2>&1 | grep -vE "^$" | grep -v "OK |"
done
git stash -q && git pull -q --rebase origin main && git stash pop -q
python3 _tools/seo.py > $V/seo_last.log 2>&1; head -5 $V/seo_last.log
node _tools/lock.mjs lock | tail -1; node _tools/lock.mjs status | tail -1
python3 _tools/build_tools_index.py >/dev/null
if node _tools/lock.mjs status | grep -q "안 잠김 0쪽"; then
  NAMES=$(for a in "$@"; do if [[ $a == s* ]]; then printf "스페셜 레슨 "; else printf "%s과 " "$a"; fi; done | sed "s/ $//; s/ /·/g; s/스페셜·레슨/스페셜 레슨/")
  git add -A && git commit -q -m "$BOOK $NAMES 온라인 학습지·목차

Co-Authored-By: Claude <noreply@anthropic.com>" && git pull -q --rebase origin main && git push -q origin main && git log --oneline -1
fi
git status --short | wc -l
