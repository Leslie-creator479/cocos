"""블로그 원고 페이지(tools/…)의 '글 전체 복사' 서식을 네이버 블로그 서식으로 맞춘다 (원장님 결정 2026-11-11).

서식 기준은 cocos-naver-blog-format 스킬(2026-11 네이버에 실제로 붙여 확인한 값)이고,
블로그 발행함 아티팩트(_tools/blog_box.py)와 똑같은 모양이 나오게 한다.
  큰 소제목(b·ser)  19px 남색 굵게(앞의 '■ '는 뗀다)
  강조(hot)          주황 19px 굵게, <blockquote>로 감싸 네이버 인용구가 된다
                     (①~⑳로 시작하는 hot은 번호 붙은 작은 소제목으로 보고 굵게만)
  설명(note)         13px 회색
  표(table)          border=1, 머리줄 남색, 열마다 가장 긴 칸이 14자를 넘으면 왼쪽·아니면 가운데
  그림 자리          [대표 이미지: x.png]·[이미지: x.png] → ◆ 주황 줄('여기에 그림을 붙이고 이 줄은 지우세요')
  블록 사이           <p><br></p> 한 줄씩(br 블록은 따로 넣지 않는다)

원고 페이지마다 들어 있는 bodyHTML()·tableHTML()을 바꿔 끼운다. 원고 데이터(var D)는 그대로다.
seo.py가 돌 때마다 자동으로 함께 돈다(다른 도구·스킬이 옛 틀로 만든 원고도 올리기 전에 맞춰진다). 여러 번 돌려도 같다.

사용법: python3 _tools/blog_style.py [--check]
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MARK = '/*naver-blog-format-2026-11b*/'
NEW = MARK + r"""
function tableHTML(rows){
  var al=[];for(var j=0;j<rows[0].length;j++){var mx=0;for(var i=1;i<rows.length;i++)mx=Math.max(mx,String(rows[i][j]||'').length);al.push(mx>14?'left':'center')}
  var h='<table border="1" style="border-collapse:collapse;width:100%">';
  rows.forEach(function(r,i){h+='<tr>';r.forEach(function(c,j){
    h+=i?'<td style="color:#000000;padding:6px 8px;text-align:'+al[j]+'">'+esc(c)+'</td>'
        :'<th style="background:#1F3864;color:#fff;padding:6px 8px;text-align:'+al[j]+'">'+esc(c)+'</th>'});h+='</tr>'});
  return h+'</table>';
}
function bodyHTML(){
  var out=[],IMG=/^\[(대표 )?이미지(?:\s*[:：]\s*(.+?))?\]$/,g=0;
  function big(t){return '<p><span style="font-size:19px;color:#1F3864"><b>'+esc(String(t).replace(/^■\s*/,''))+'</b></span></p>'}
  function slot(l){return '<p><span style="color:#E25100"><b>◆ '+esc(l)+' — 여기에 그림을 붙이고 이 줄은 지우세요</b></span></p>'}
  D.body.forEach(function(b){
    var k=b[0],t=b[1],m=k==='p'&&IMG.exec(String(t).trim());
    if(k==='br')return;
    if(m){out.push(slot(m[1]?'대표 이미지':'그림 '+(++g)+(m[2]?' ('+m[2]+')':'')));return}
    if(k==='b'||k==='ser')out.push(big(t));
    else if(k==='hot')out.push(/^[①-⑳]/.test(t)?'<p><span style="color:#000000"><b>'+esc(t)+'</b></span></p>'
      :'<blockquote style="border-left:3px solid #E25100;padding-left:14px;margin:0"><p><span style="font-size:19px;color:#E25100"><b>'+esc(t)+'</b></span></p></blockquote>');
    else if(k==='note')out.push('<p><span style="font-size:13px;color:#767171">'+esc(t)+'</span></p>');
    else if(k==='link')out.push('<p>'+a(b[2],t)+'</p>');
    else if(k==='list')out.push(listHTML().replace(/<p><b>/g,'<p><span style="color:#000000"><b>').replace(/<\/b><\/p>/g,'</b></span></p>'));
    else if(k==='table')out.push(tableHTML(t));
    else out.push('<p><span style="color:#000000">'+esc(t)+'</span></p>');
  });
  return out.join('<p><br></p>')+'<p><br></p>';
}
"""
FUNC = re.compile(r'function (bodyHTML|tableHTML)\(.*?\n\}\n', re.S)


def patch(s):
    new = NEW.lstrip('\n')
    for old in ('/*naver-blog-format-2026-11*/',):
        if old in s and MARK not in s:
            s = s.replace(old, MARK)
    if MARK in s:
        i = s.index(MARK)
        j = s.index('\n}\n', s.index('function bodyHTML', i)) + 3
        return s if s[i:j] == new else s[:i] + new + s[j:]
    m = FUNC.search(s)
    if not m or 'function bodyHTML' not in s:
        return None
    pos = m.start()
    s = FUNC.sub('', s)
    return s[:pos] + new + s[pos:]


def run(check=False, quiet=False):
    changed = []
    base = os.path.join(ROOT, 'tools')
    for dp, dns, fns in os.walk(base):
        if 'index.html' not in fns:
            continue
        p = os.path.join(dp, 'index.html')
        s = open(p, encoding='utf8').read()
        if 'var D=' not in s or 'function bodyHTML' not in s:
            continue
        t = patch(s)
        if t and t != s:
            changed.append(os.path.relpath(dp, ROOT))
            if not check:
                open(p, 'w', encoding='utf8').write(t)
    if changed and not quiet:
        print(('바꿀 원고 ' if check else '네이버 서식으로 바꾼 원고 ') + str(len(changed)) + '개')
    return changed


if __name__ == '__main__':
    c = run(check='--check' in sys.argv)
    print(len(c), '개')
