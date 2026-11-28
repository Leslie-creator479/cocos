# blog.json + cover.json 만들기 (모의고사 18~45번 회차용). 사용: python3 -I mkblog.py 폴더 게임URL ["도입 한 줄"]
import json, sys
d, U = sys.argv[1], sys.argv[2]; hook = sys.argv[3] if len(sys.argv) > 3 else ''
I = json.load(open(d + '/info.json', encoding='utf8')); G = json.load(open(d + '/game_data.json', encoding='utf8')); C = json.load(open(d + '/config.json', encoding='utf8'))
label = I['label']; y, mth, gr = label.split(); n, nw = len(G['P']), len(G['W'])
g1, g2 = C['groups']
def k(p): return p.get('k') or p['no'].replace('~', '-')
items = [[f"{p['no']}번 {I['types'].get(p['no'], '')} · {p['topic']}".replace('번  · ', '번 · '), U + '#' + k(p)] for p in G['P']]
groups = [dict(g='범위별 바로가기', items=[[f"18~45번 전체 {n}개 지문", U + '#18-45'], [f"18~26번 ({len(g1['keys'])}개 지문)", U + '#18-26'], [f"29~45번 ({len(g2['keys'])}개 지문)", U + '#29-45']]), dict(g='지문별 바로가기', items=items)]
body = [["p", "[대표 이미지]"], ["p", f"{y}년 {mth} {gr} 영어 모의고사 18~45번 지문 단어로 단어게임을 만들었어요."],
 ["b", "■ 단어, 게임으로 외워 볼까요?"], ["p", "단어장만 붙잡고 외우다 보면 금방 지루해지죠."], ["p", f"그래서 {n}개 지문에 나온 단어 {nw}개를 다섯 가지 게임으로 만들었어요."]]
if hook: body.append(["p", hook])
body += [["b", "▶ 단어게임 바로가기"], ["link", U, U], ["p", "휴대폰으로도 바로 할 수 있고, 로그인 없이 링크만 누르면 돼요."],
 ["b", "■ 이렇게 해요"], ["p", "· 범위 고르기: 전체, 18~26번, 29~45번 버튼이나 지문 번호를 눌러 공부할 범위를 골라요. 학교 시험 범위에 맞춰 고르면 돼요."],
 ["p", "· 1단계 단어 먼저 익히기: 지문별 단어 목록에서 발음을 듣고, 뜻을 가리고 외워요."], ["p", "· 2단계 게임으로 확인하기: 다섯 가지 게임 중 마음에 드는 것부터 해 보세요."],
 ["b", "■ 게임 다섯 가지"], ["p", "· 카드 짝 맞추기: 영어 카드와 뜻 카드를 뒤집어 짝 찾기"], ["p", "· 60초 타임어택: 60초 동안 뜻을 몇 개나 맞힐 수 있을까?"],
 ["p", "· 떨어지는 단어: 단어가 바닥에 닿기 전에 뜻 고르기, 목숨은 3개"], ["p", "· 철자 채우기: 뜻을 보고 알파벳을 눌러 단어 완성하기"],
 ["p", "· 지문 속 빈칸: 실제 지문 문장에서 빠진 단어 찾기. 보기가 모두 같은 품사·같은 형태라서 뜻을 알아야 풀 수 있어요."], ["br"],
 ["p", "틀린 단어는 '오답 다시 풀기'에 모여서, 다 맞힐 때까지 다시 나와요."], ["p", "게임이 끝나면 별점과 기록이 나와요. 친구와 기록 대결도 해 보세요!"],
 ["b", "■ 더 공부하고 싶다면"]]
if I['syn']:
    body += [["p", "단어 목록에서 지문마다 '학습지 열기'와 '동의어·반의어 열기' 버튼이 있어요."], ["p", "해석과 마인드맵, 확인 퀴즈로 지문 전체를 공부하거나, 동의어·반의어로 내신 변형 문제까지 대비할 수 있어요."]]
else:
    body += [["p", "단어 목록에서 지문마다 '학습지 열기' 버튼이 있어요."], ["p", "해석과 마인드맵, 확인 퀴즈로 지문 전체를 공부할 수 있어요."]]
body += [["b", "■ 범위별·지문별 바로가기"], ["p", "아래 링크를 누르면 그 범위가 골라진 채로 단어게임이 열려요."], ["list"],
 ["p", "링크는 누구에게나 자유롭게 공유해도 좋아요."], ["p", "다만 내용을 복제·수정해 다른 곳에 올리거나 상업적으로 이용하는 것은 금지해요."]]
B = dict(page_title=f"{label} 단어게임 블로그 원고", h1=f"{y}년 {mth} {gr} 단어게임 블로그 원고", url=U,
  title=f"{y}년 {mth} {gr} 영어 모의고사 단어게임 | 18~45번 단어 {nw}개 놀면서 외우기",
  tags=f"{mth}{gr}모의고사 영어단어게임 단어게임 모의고사단어 {gr}영어 영어단어암기 내신영어 영어어휘 성남동영어학원", count=n, groups=groups, body=body)
json.dump(B, open(d + '/blog.json', 'w', encoding='utf8'), ensure_ascii=False)
json.dump(dict(theme=I['theme'], badge=f"{y} {mth} {gr} 모의고사", chips=[f"18~45번 {n}개 지문", f"단어 {nw}개"]), open(d + '/cover.json', 'w', encoding='utf8'), ensure_ascii=False)
print(B['title']); print(items[0][0], '|', items[-1][0])
