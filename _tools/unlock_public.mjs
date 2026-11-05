// 공개로 바뀐 페이지(모의고사만 묶은 학교별 동의어·단어게임 등)를 잠금에서 풀 때, 잠글 때 바뀐
// '학원생 전용·저작권' 안내 문구를 공개 자료의 원래 문구로 되돌린다(원장님 결정 2026-11-05).
//   COCOS_LOCK_PW=… node _tools/lock.mjs unlock <파일…>   먼저 풀고
//   node _tools/unlock_public.mjs <파일…>                  문구 되돌리기 → seo.py
// 원래 문구는 공개 모의고사 페이지(syn/2026-09-g2, game/2026-09-g2)에서 가져온다.
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
const ROOT = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const src = fs.readFileSync(path.join(ROOT, '_tools', 'lock.mjs'), 'utf8');
const SHARE = src.match(/const SHARE = '([^']+)'/)[1];
const NOTICE = src.match(/const NOTICE = '([^']+)'/)[1];
function orig(kind) {
  const ref = fs.readFileSync(path.join(ROOT, kind, '2026-09-g2', 'index.html'), 'utf8');
  return { share: (ref.match(/[^<>\n]{0,80}친구에게도[^<>\n]{0,80}공유해 주세요!?/) || [])[0],
           notice: (ref.match(/링크는 누구에게나 자유롭게 공유해도 좋아요\.[^<>\n]{0,200}/) || [])[0] };
}
for (const f of process.argv.slice(2)) {
  let s = fs.readFileSync(f, 'utf8');
  if (s.includes('id="cocos-lock"')) { console.log(f, '아직 잠김 — 먼저 unlock'); continue; }
  const kind = path.relative(ROOT, path.resolve(f)).split(path.sep)[0];
  const o = orig(kind === 'game' ? 'game' : 'syn');
  let n = 0;
  if (o.share && s.includes(SHARE)) { s = s.split(SHARE).join(o.share); n++; }
  if (o.notice && s.includes(NOTICE)) { s = s.split(NOTICE).join(o.notice); n++; }
  fs.writeFileSync(f, s);
  console.log(f, n ? `문구 ${n}종 되돌림` : '바꿀 문구 없음');
}
