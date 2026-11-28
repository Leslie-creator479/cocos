# info.json + game_data.json → config.json (모의고사 18~45번 회차용)
import json, sys
d = sys.argv[1]; I = json.load(open(d + '/info.json', encoding='utf8')); G = json.load(open(d + '/game_data.json', encoding='utf8'))
label = I['label']; y, mth, gr = label.split()  # "2026", "6월", "고2"
keys = [p.get('k') or p['no'].replace('~', '-') for p in G['P']]
n, nw = len(G['P']), len(G['W'])
toc_u = None
c = dict(title=f"[코코스학원] {label} 학평 단어게임", key=f"cocos-wordgame-{y}-{int(mth[:-1]):02d}-g{gr[-1]}", label=label, syn=I['syn'],
  meta=dict(h1=f"{label} 단어게임", chips=[f"{y} {mth} 학력평가 · {gr}", f"{n}개 지문 · 단어 {nw}개", "게임 5가지"],
    gist=f"모의고사 {n}개 지문의 단어로 다섯 가지 게임을 해 보세요. 시험 범위에 맞게 지문 번호를 골라서 할 수 있어요. 틀린 단어는 ‘오답 다시 풀기’에 모여요.",
    links=[[f"{label} 온라인 학습지 목차", I['toc_url']]] + ([[f"{label} 동의어·반의어", "https://claude.ai/artifact/" + I['syn']]] if I['syn'] else []),
    source=I['source']),
  groups=[dict(label='18~26번', keys=[k for k in keys if int(k.split('-')[0]) <= 26]), dict(label='29~45번', keys=[k for k in keys if int(k.split('-')[0]) >= 29])])
json.dump(c, open(d + '/config.json', 'w', encoding='utf8'), ensure_ascii=False)
print(c['title'], c['key'], [ (g['label'], len(g['keys'])) for g in c['groups']])
