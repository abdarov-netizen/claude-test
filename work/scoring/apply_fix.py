# -*- coding: utf-8 -*-
"""Применяет исследовательскую переоценку A2/A3/A6 к идеям заказчика.
Пересчитывает оси и итог по тем же зафиксированным весам. Пишет 63_scores_fixed.json."""
import json, re, os
SP='/tmp/claude-0/-home-user-claude-test/6b9b5210-62a0-5c3e-960e-a4c9f8e112b0/scratchpad'
W='/home/user/claude-test/work'
WA={'A1_economics':24,'A2_market':18,'A3_why_now':15,'A4_white_space':13,
    'A5_barriers':12,'A6_wtp':10,'A7_exit':8}
WB={'B1_speed':20,'B2_reg':16,'B3_fin':15,'B4_deal':15,'B5_family':13,
    'B6_sales':12,'B7_style':9}
# вариант с переносом A5 на ось человека (замечание внешнего критика)
WA2={k:v for k,v in WA.items() if k!='A5_barriers'}; WB2=dict(WB); WB2['A5_barriers']=12
def ax(x,w): 
    s=sum(w.values()); return round(sum(v*x[k] for k,v in w.items())/s,3)
D=json.load(open(f'{W}/state/62_screen_scores.json',encoding='utf-8'))
by={x['id']:x for x in D}
fx={}
for n in (1,2,3):
    p=f'{SP}/fixed{n:02d}.txt'
    if not os.path.exists(p): continue
    for ln in open(p,encoding='utf-8'):
        ln=ln.strip()
        if not ln or not ln.startswith('USR-'): continue
        pr=ln.split('|')
        if len(pr)<4: continue
        try: a2,a3,a6=[int(v) for v in pr[1].split(',')]
        except Exception: continue
        if not all(1<=v<=10 for v in (a2,a3,a6)): continue
        fx[pr[0]]={'A2_market':a2,'A3_why_now':a3,'A6_wtp':a6,
                   'window':pr[2].strip(),'payer':pr[3].strip()}
print(f'переоценено идей заказчика: {len(fx)}')
ch=[]
for i,v in fx.items():
    x=by.get(i)
    if not x: continue
    old=x['total']
    prev={k:x[k] for k in ('A2_market','A3_why_now','A6_wtp')}
    for k in ('A2_market','A3_why_now','A6_wtp'): x[k]=v[k]
    x['A']=ax(x,WA); x['B']=ax(x,WB); x['total']=round(0.7*x['A']+0.3*x['B'],3)
    x['A_alt']=ax(x,WA2); x['B_alt']=ax(x,WB2)
    x['total_alt']=round(0.7*x['A_alt']+0.3*x['B_alt'],3)
    x['exit']=x['A7_exit']; x['speed']=x['B1_speed']; x['style']=x['B7_style']
    x['window_researched']=v['window']; x['payer_researched']=v['payer']
    x['rescored']=True
    ch.append((x['total']-old,old,x,prev))
ch.sort(key=lambda t:-t[0])
print('\n=== КАК СДВИНУЛИСЬ ОЦЕНКИ (топ-20 по росту) ===')
for d,old,x,pv in ch[:20]:
    print(f'{d:+5.2f}  {old:.2f}->{x["total"]:.2f}  {x["id"]:<8} A3 {pv["A3_why_now"]}->{x["A3_why_now"]}  {x["name"][:44]}')
dn=[t for t in ch if t[0]<0]
print(f'\nснизилось у {len(dn)} идей из {len(ch)} (значит агенты не просто накидывали баллы)')
for d,old,x,pv in dn[:8]:
    print(f'{d:+5.2f}  {old:.2f}->{x["total"]:.2f}  {x["id"]:<8} {x["name"][:44]}')
json.dump(D, open(f'{W}/state/63_scores_fixed.json','w',encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'\nсохранено -> work/state/63_scores_fixed.json ({len(D)} идей)')
