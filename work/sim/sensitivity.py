# -*- coding: utf-8 -*-
"""Торнадо-анализ: какой параметр двигает ожидаемый NPV сильнее всего."""
import json, sys, copy
import numpy as np
sys.path.insert(0, "."); from engine import simulate

cfg = json.load(open("configs/FIN-11.json", encoding="utf-8"))
BASE_N, SEED = 12000, 4242

def shift(c, path, f):
    c = copy.deepcopy(c); node = c
    for k in path[:-1]: node = node[k]
    v = node[path[-1]]
    node[path[-1]] = [x*f for x in v] if isinstance(v, list) else v*f
    return c

VARS = [
 ("Средняя комиссия с клиента",      ["pricing","arpu_month"],            0.75, 1.25),
 ("Размер рынка (число объектов)",     ["market","tam_customers"],          0.70, 1.30),
 ("Конверсия в сделку (win rate)",       ["funnel","win_rate"],               0.70, 1.30),
 ("Отток клиентов",                      ["churn","monthly"],                 1.60, 0.60),
 ("Мощность основателя",      ["delivery","founder_capacity_clients"],0.60,1.40),
 ("Клиентов на сотрудника",              ["delivery","clients_per_fte"],      0.70, 1.30),
 ("Стоимость сотрудника",                ["delivery","fte_cost_month"],       1.35, 0.75),
 ("Постоянные расходы",                  ["costs","fixed_opex_month"],        1.45, 0.70),
 ("Валовая маржа",                       ["costs","gross_margin"],            0.80, 1.15),
 ("Срок оплаты счетов (DSO)",            ["wc","dso_days"],                   1.70, 0.60),
 ("Стоимость привлечения (CAC)",         ["funnel","cac0"],                   1.60, 0.65),
 ("Мультипликатор выхода",               ["exit","ebitda_multiple"],          0.55, 1.45),
 ("Задержка запуска",                    ["launch","delay_months"],           2.20, 0.50),
]

base = simulate(cfg, n=BASE_N, seed=SEED)["npv"].mean()
print(f"База: ожидаемый NPV = ${base:,.0f}\n")
rows=[]
for label, path, f_bad, f_good in VARS:
    lo = simulate(shift(cfg,path,f_bad), n=BASE_N, seed=SEED)["npv"].mean()
    hi = simulate(shift(cfg,path,f_good),n=BASE_N, seed=SEED)["npv"].mean()
    rows.append((abs(hi-lo), label, lo, hi, lo-base, hi-base))
rows.sort(reverse=True)
print(f"{'параметр':<36}{'плохо':>12}{'хорошо':>12}{'размах':>12}")
print("-"*72)
for span,label,lo,hi,dlo,dhi in rows:
    print(f"{label:<36}{lo:>12,.0f}{hi:>12,.0f}{span:>12,.0f}")
json.dump({"base_E_NPV":float(base),
           "tornado":[{"param":l,"low":float(lo),"high":float(hi),
                       "d_low":float(dl),"d_high":float(dh),"span":float(sp)}
                      for sp,l,lo,hi,dl,dh in rows]},
          open("results/tornado_FIN-11.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)
print("\nсохранено -> results/tornado_FIN-11.json")
