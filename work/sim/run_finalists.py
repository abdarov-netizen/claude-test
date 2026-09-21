# -*- coding: utf-8 -*-
"""Ярус 4: Монте-Карло по финалистам.
ДВА СЦЕНАРИЯ ЗАНЯТОСТИ СЧИТАЮТСЯ РАЗДЕЛЬНО (требование заказчика):
  «в найме»  — зарплата НЕ вычитается, но и ёмкость основателя частичная (20-30 ч/нед);
  «уходит»   — зарплата $4 000/мес вычитается, ёмкость основателя x2.6.
Прошлый прогон делал ошибку: вычитал зарплату, НЕ поднимая ёмкость, то есть моделировал
человека, который потерял зарплату и всё равно работает на полставки. Такого не бывает.
БАРЬЕРНАЯ СТАВКА: 12.7% база. Прежние 19.7% — сумовая депозитная ставка, применённая
к долларовым потокам при «сум не слабеет», то есть безрисковые 19.7% в долларах.
19.7% и 28% оставлены как СТРЕСС."""
import json, glob, os, sys, copy
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, engine

W='/home/user/claude-test/work'
FIN=sorted(glob.glob(f'{W}/sim/configs/F[0-9]-*.json'))
HURDLES=[('база 12.7%',0.127),('стресс 19.7%',0.197),('стресс 28%',0.28)]
N=20000
FOUNDER_BOOST=2.6      # во сколько раз растёт ёмкость основателя при уходе из найма
SALARY=4000.0

def scen_quit(cfg):
    c=copy.deepcopy(cfg)
    for k in ('founder_capacity_clients',):
        v=c['delivery'].get(k)
        if isinstance(v,list): c['delivery'][k]=[x*FOUNDER_BOOST for x in v]
    v=c['funnel'].get('founder_opps_month')
    if isinstance(v,list): c['funnel']['founder_opps_month']=[x*FOUNDER_BOOST for x in v]
    return c

rows=[]
for p in FIN:
    cfg=json.load(open(p,encoding='utf-8'))
    for sname, scfg, sal in [('в найме',cfg,0.0), ('уходит',scen_quit(cfg),SALARY)]:
        for hname, h in HURDLES:
            r=engine.simulate(scfg, n=N, seed=7, founder_salary_month=sal, hurdle_annual=h)
            npv=r['npv']; alive=r['alive']
            s=npv[alive]
            rows.append({'id':cfg['id'],'name':cfg['name'],'сценарий':sname,'ставка':hname,
                'E_NPV':float(npv.mean()),'медиана':float(np.median(npv)),
                'P_выжил':float(alive.mean()),'P_NPV>0':float((npv>0).mean()),
                'E_NPV_при_выживании':float(s.mean()) if len(s) else float('nan'),
                'медиана_при_выживании':float(np.median(s)) if len(s) else float('nan'),
                'p5':float(np.percentile(npv,5)),'p95':float(np.percentile(npv,95)),
                'пик_капитала':float(np.median(r['peak_capital'])),
                'мес_до_выручки':float(np.median(r['first_rev_month'][r['first_rev_month']>=0])) if (r['first_rev_month']>=0).any() else float('nan'),
                'доля_основателя':1.0-float(cfg['capital'].get('equity_partner_share',0.0))})
            print('.', end='', flush=True)
json.dump(rows, open(f'{W}/sim/results/finalists_v2.json','w',encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'\nпрогонов: {len(rows)} x {N} путей = {len(rows)*N:,} траекторий')
