# -*- coding: utf-8 -*-
"""Слияние новых идей заказчика в реестр.
ПРАВИЛА (по прямому указанию заказчика):
  1. Существующие 517 идей НЕ ТРОГАЕМ.
  2. Колонки таблицы НЕ ДОБАВЛЯЕМ.
  3. Добавляем ТОЛЬКО новые идеи из файла, поля кладём в уже существующие колонки.
  4. Ничего не выдумываем: где у заказчика данных нет — ячейка остаётся пустой.
     Механизм и Триггер не проставляем: это моя разметка, а не его данные.
"""
import json, glob, re, os
SCR="/tmp/claude-0/-home-user-claude-test/6b9b5210-62a0-5c3e-960e-a4c9f8e112b0/scratchpad"
reg=json.load(open("work/state/40_registry_v2.json",encoding="utf-8"))
usr=json.load(open(f"{SCR}/user_ideas.json",encoding="utf-8"))

verdict={}
for f in sorted(glob.glob(f"{SCR}/verdict*.txt")):
    for line in open(f,encoding="utf-8"):
        m=re.match(r'\s*(\d+)\s*\|\s*(DUP|NEW)\s*\|\s*([A-ZА-Я0-9\-]*)',line.strip())
        if m: verdict[int(m.group(1))]=(m.group(2),m.group(3).strip())
print(f"вердиктов получено: {len(verdict)} из {len(usr)}")
missing=[i for i in range(len(usr)) if i not in verdict]
if missing: print(f"БЕЗ ВЕРДИКТА: {len(missing)} строк -> считаю их НОВЫМИ (не теряем идеи)")

def num(x):
    try:
        v=float(x)
        return int(v) if v==v else None
    except: return None
def s(x): return "" if x is None else str(x).strip()

added=[]; dups=[]
for i,d in enumerate(usr):
    v,mid=verdict.get(i,("NEW",""))
    if v=="DUP": dups.append((i,d.get("Идея"),mid)); continue
    # экономика из ФАЙЛА ЗАКАЗЧИКА, ничего не досочиняем
    econ=[]
    if num(d.get("Выручка Y3, $")): econ.append(f"выручка Y3 ${num(d.get('Выручка Y3, $')):,}")
    if num(d.get("Прибыль Y3, $")): econ.append(f"прибыль Y3 ${num(d.get('Прибыль Y3, $')):,}")
    if num(d.get("Вал. маржа, %")): econ.append(f"вал. маржа {num(d.get('Вал. маржа, %'))}%")
    if num(d.get("Мес. до выручки")) is not None:
        econ.append(f"до выручки {num(d.get('Мес. до выручки'))} мес")
    added.append({
        "id": f"USR-{len(added)+1:03d}",
        "_row": i,
        "name": s(d.get("Идея")),
        "essence": s(d.get("Суть в одной строке")),
        "revenue": ", ".join(econ),
        "analog": s(d.get("Аналог в мире")),
        "competition": s(d.get("Конкуренты в РУз")),
        "risk1": s(d.get("Главная слабость")),
        "own_usd": num(d.get("Старт, $")),
        "source_file": "файл заказчика Book1.xlsx",
        "user_category": s(d.get("Категория")),
        "user_rank": num(d.get("Ранг")),
        "gen": "usr",
        # намеренно НЕ заполняем: M, T, payer, need, approach, benefit, window,
        # raised_usd, money — этих данных в файле заказчика нет, выдумывать нельзя
    })
# ВНУТРЕННИЕ дубли в самом файле заказчика. Судьи сравнивали только с реестром,
# но заказчик просил, чтобы не дублировалось ВООБЩЕ.
# Порогом тут нельзя: «Tilla Jamg'arma» и «Oltin — микронакопления в золоте» — один бизнес,
# а текстовая близость 0.12. И наоборот, «Sud-Hujjat AI» и «UzASR Cloud» близки по тексту,
# но это разные продукты. Поэтому пары зафиксированы списком после ручного разбора.
INNER_DUPS=[  # (оставляем первый, выбрасываем второй) — номера строк исходного файла
 (7,30),(9,449),(29,86),(33,90),(55,93),(81,448),(91,134),(120,143),(156,189),
 (157,321),(173,197),(198,350),(219,538),(244,518),(250,371),(286,433),(320,399),
 (335,384),(514,521),
 (451,159),(383,428),   # найдены судьями по смыслу, текстом не ловятся
 (364,281),             # две студии гиперказуальных игр
 (433,250),(371,433),   # семейство фулфилмента для селлеров
 (521,490),
]
drop_rows=set()
for keep,dropr in INNER_DUPS:
    if keep not in drop_rows: drop_rows.add(dropr)
before=len(added)
added=[a for a in added if a["_row"] not in drop_rows]
for k,a in enumerate(added,1): a["id"]=f"USR-{k:03d}"
print(f"ВНУТРЕННИХ дублей в файле заказчика отброшено: {before-len(added)}")

print(f"\nДУБЛЕЙ с реестром отброшено: {len(dups)}")
print(f"НОВЫХ добавлено:  {len(added)}")
print(f"РЕЕСТР: было {len(reg)}  ->  стало {len(reg)+len(added)}")
json.dump(reg+added,open("work/state/50_registry_v3.json","w",encoding="utf-8"),
          ensure_ascii=False,indent=1)
json.dump({"dups":[{"row":r,"name":n,"matched":m} for r,n,m in dups]},
          open("work/state/51_dups_report.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
print("\nпримеры отброшенных дублей:")
for r,n,m in dups[:12]: print(f"   «{str(n)[:62]}» = {m}")
