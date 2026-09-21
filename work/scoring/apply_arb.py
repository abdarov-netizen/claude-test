# -*- coding: utf-8 -*-
"""Сводит оценщиков A и B с решениями арбитра в финальные оценки яруса 3."""
import json, re, glob, statistics as st
SP='/tmp/claude-0/-home-user-claude-test/6b9b5210-62a0-5c3e-960e-a4c9f8e112b0/scratchpad'
WA={'A1_economics':24,'A2_market':18,'A3_why_now':15,'A4_white_space':13,'A5_barriers':12,'A6_wtp':10,'A7_exit':8}
WB={'B1_speed':20,'B2_reg':16,'B3_fin':15,'B4_deal':15,'B5_family':13,'B6_sales':12,'B7_style':9}
WA2={k:v for k,v in WA.items() if k!='A5_barriers'}; WB2=dict(WB); WB2['A5_barriers']=12
CODE={'A1':'A1_economics','A2':'A2_market','A3':'A3_why_now','A4':'A4_white_space','A5':'A5_barriers',
      'A6':'A6_wtp','A7':'A7_exit','B1':'B1_speed','B2':'B2_reg','B3':'B3_fin','B4':'B4_deal',
      'B5':'B5_family','B6':'B6_sales','B7':'B7_style'}
def ax(x,w): return round(sum(v*x[k] for k,v in w.items())/sum(w.values()),3)
A=json.load(open(f'{SP}/raterA.json',encoding='utf-8')); B=json.load(open(f'{SP}/raterB.json',encoding='utf-8'))
arb={}; notes={}
for f in sorted(glob.glob(f'{SP}/arbR0*.txt')):
    for ln in open(f,encoding='utf-8'):
        m=re.match(r'^([A-Z]{2,5}-\d{2,3})\|([AB][1-7])\|(\d{1,2})\|(.*)$', ln.strip())
        if m and m.group(2) in CODE and 1<=int(m.group(3))<=10:
            arb[(m.group(1),CODE[m.group(2)])]=int(m.group(3)); notes[(m.group(1),CODE[m.group(2)])]=m.group(4).strip()
print(f'решений арбитра принято: {len(arb)}')
side=mid=0
for (i,k),v in arb.items():
    a,b=A['scores'][i][k],B['scores'][i][k]
    if v in (a,b): side+=1
    else: mid+=1
print(f'из них выбрана сторона: {side}, промежуточное значение: {mid} ({100*mid/len(arb):.0f}%)')
print('(в дискредитированном протоколе промежуточных было 73.9%)\n')
reg={x['id']:x for x in json.load(open('state/50_registry_v3.json',encoding='utf-8'))}
scr={x['id']:x for x in json.load(open('state/63_scores_fixed.json',encoding='utf-8'))}
out=[]
for i in sorted(set(A['scores'])&set(B['scores'])):
    f={}
    for k in WA|WB:
        f[k]=arb.get((i,k), round((A['scores'][i][k]+B['scores'][i][k])/2))
    a,b=ax(f,WA),ax(f,WB)
    out.append({'id':i,'name':reg[i]['name'],'gen':reg[i].get('gen'),
        'A':a,'B':b,'total':round(0.7*a+0.3*b,3),
        'A_alt':ax(f,WA2),'B_alt':ax(f,WB2),
        'total_alt':round(0.7*ax(f,WA2)+0.3*ax(f,WB2),3),
        'screen':scr[i]['total'],
        'rA':round(0.7*ax(A['scores'][i],WA)+0.3*ax(A['scores'][i],WB),3),
        'rB':round(0.7*ax(B['scores'][i],WA)+0.3*ax(B['scores'][i],WB),3),
        'disputes':sum(1 for k in WA|WB if (i,k) in arb),
        **f})
out.sort(key=lambda x:-x['total'])
json.dump(out, open('state/64_deep_scores.json','w',encoding='utf-8'), ensure_ascii=False, indent=1)
print('=== ФИНАЛЬНЫЙ РАНЖИР ЯРУСА 3 (45 идей, два оценщика + арбитр) ===')
print('  №  итог   A     B   |  оцA  оцB спор| выход скор стиль | идея')
for n,x in enumerate(out,1):
    print(f'{n:3d} {x["total"]:5.2f} {x["A"]:5.2f} {x["B"]:5.2f} | {x["rA"]:4.1f} {x["rB"]:4.1f} {x["disputes"]:2d} | '
          f'{x["A7_exit"]:3d} {x["B1_speed"]:4d} {x["B7_style"]:4d}  | {x["id"]:<8} {x["name"][:44]}')
print(f'\nразброс итога: {out[0]["total"]:.2f} ... {out[-1]["total"]:.2f}')
