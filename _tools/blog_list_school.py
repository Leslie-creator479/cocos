"""블로그 수록 지문 목록(tools/blog-list)의 '학교별 시험 범위' 칸을 다시 만든다(2026-11-14).
school/2026-2-mid|final/<학교>-g<학년> 목차와 같은 이름의 syn 페이지마다 시험 범위·동의어·반의어 항목을 넣는다.
잠긴 동의어는 tools/syn-blog/<이름>/ 원고의 목록을 쓴다. 학교별 목차·동의어를 새로 올린 뒤 python3 _tools/blog_list_school.py → build_tools_index.py."""
import json,re,os
P='tools/blog-list/index.html'
s=open(P,encoding='utf8').read()
a=s.index('var EXAMS=')+10
E,end=json.JSONDecoder().raw_decode(s[a:])
NAME={'dongkwang':'동광고','seongnam':'성남고','seongnam-girls':'성남여고','seongil':'성일고','pungsaeng':'풍생고','sungsin':'숭신고'}
ID={'dongkwang':'dg','seongnam':'sngo','seongnam-girls':'sng','seongil':'sig','pungsaeng':'ps','sungsin':'ss'}
U='https://cocosedu.kr/'
def anchor(lab,no):
    k=re.search(r'(\d+)강\s*([\d~]+)번',lab)
    if k: return 'l'+k[1]+'-'+k[2].replace('~','-')
    m=re.search(r'(\d+)월\s*([\d~]+)번',lab)
    return 'm'+m[1]+'-'+m[2].replace('~','-') if m else 'p'+str(no).replace('~','-')
def toc_entry(term,sch,g,eid):
    f=f'school/2026-2-{term}/{sch}-g{g}/index.html'
    t=open(f,encoding='utf8').read(); m=re.search(r'var TOC\s*=\s*',t); D,_=json.JSONDecoder().raw_decode(t[m.end():])
    groups=[]
    for it in D['items']:
        if not groups or groups[-1]['g']!=it['g']: groups.append({'g':it['g'],'items':[]})
        lab=(it['g']+' '+it['n']) if re.search(r'\d+강$',it['g']) else it['n']
        url=U+os.path.normpath(os.path.join(os.path.dirname(f),it['u'])).replace('\\','/')+'/'
        groups[-1]['items'].append([lab,it['h'],url])
    kt={'mid':'중간','final':'기말'}[term]
    return {'id':eid,'title':f'{NAME[sch]} {g}학년 26년 2학기 {kt} 시험 범위','toc':U+f'school/2026-2-{term}/{sch}-g{g}/','groups':groups}
def syn_entry(term,sch,g,eid):
    slug=f'2026-2-{term}-{sch}-g{g}'; kt={'mid':'중간','final':'기말'}[term]
    base=U+f'syn/{slug}/'
    t=open(f'syn/{slug}/index.html',encoding='utf8').read()
    if 'var DATA' not in t:  # 잠긴 페이지 → 블로그 원고의 목록을 씀
        d=open(f'tools/syn-blog/{slug}/index.html',encoding='utf8').read(); i=d.index('var D=')+6; B,_=json.JSONDecoder().raw_decode(d[i:])
        groups=[{'g':gr['g'],'items':[[x[0].split(' · ')[0],' · '.join(x[0].split(' · ')[1:]),x[1]] for x in gr['items']]} for gr in B['groups']]
    else:
        m=re.search(r'var DATA\s*=\s*',t); D,_=json.JSONDecoder().raw_decode(t[m.end():])
        groups=[]
        for p in D['passages']:
            lab=p['lab']; gk=re.match(r'(\d+강|\d+월)',lab); gk=gk.group(1) if gk else ''
            gname=gk if gk.endswith('강') else gk+' 학력평가'
            if not groups or groups[-1]['g']!=gname: groups.append({'g':gname,'items':[]})
            groups[-1]['items'].append([lab,p['kr'].split(':')[0].strip(),base+'#'+anchor(lab,p['no'])])
    return {'id':eid,'title':f'{NAME[sch]} {g}학년 26년 2학기 {kt} 동의어·반의어','toc':base,'groups':groups}

keep=[e for e in E if not re.match(r'^\S+ \d학년',e['title'])]
old={e['id']:e for e in E if e not in keep}
pairs=set()
for term in ('mid','final'):
    for d in os.listdir(f'school/2026-2-{term}'):
        m=re.match(r'(.+)-g(\d)$',d); pairs.add((m[1],int(m[2])))
new=[]
for sch,g in sorted(pairs,key=lambda x:(x[1],NAME[x[0]])):
    b=ID[sch]+'g'+str(g)
    if os.path.isdir(f'school/2026-2-final/{sch}-g{g}'):
        new.append(toc_entry('final',sch,g,b+'f'))
        if os.path.isdir(f'syn/2026-2-final-{sch}-g{g}'): new.append(syn_entry('final',sch,g,b+'fsyn'))
    if os.path.isdir(f'school/2026-2-mid/{sch}-g{g}'):
        e=toc_entry('mid',sch,g,b); 
        if b in old and old[b]['groups']: e['groups']=old[b]['groups']  # 기존 목록(손으로 다듬은 것) 유지
        new.append(e)
        if os.path.isdir(f'syn/2026-2-mid-{sch}-g{g}'): new.append(syn_entry('mid',sch,g,b+'syn'))
for e in new: print(e['id'],e['title'],sum(len(x['items']) for x in e['groups']), e['groups'][0]['items'][0])
E2=keep+new
s=s[:a]+json.dumps(E2,ensure_ascii=False)+s[a+end:]
open(P,'w',encoding='utf8').write(s)
