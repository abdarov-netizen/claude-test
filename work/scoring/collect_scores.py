# -*- coding: utf-8 -*-
"""Сборка оценок скрининга, свёртка осей, три варианта рейтинга."""
import json, glob, re, collections
import numpy as np
SCR="/tmp/claude-0/-home-user-claude-test/6b9b5210-62a0-5c3e-960e-a4c9f8e112b0/scratchpad"
WA=[.24,.18,.15,.13,.12,.10,.08]   # A1..A7
WB=[.20,.16,.15,.15,.13,.12,.09]   # B1..B7
KA=["economics","market","why_now","white_space","barriers","wtp","exit"]
KB=["speed","reg","fin","deal","family","sales","style"]

reg={d["id"]:d for d in json.load(open("work/state/50_registry_v3.json",encoding="utf-8"))}
sc={}
bad=[]
for f in sorted(glob.glob(f"{SCR}/score*.txt")):
    for line in open(f,encoding="utf-8"):
        m=re.match(r'\s*([A-ZА-Я]{2,6}(?:-[A-ZА-Я])?-\d{1,3})\s*\|\s*([\d,\s]+)\|\s*([\d,\s]+)',line.strip())
        if not m: continue
        iid=m.group(1)
        a=[int(x) for x in re.findall(r'\d+',m.group(2))]
        b=[int(x) for x in re.findall(r'\d+',m.group(3))]
        if len(a)!=7 or len(b)!=7 or iid not in reg: bad.append(line.strip()[:60]); continue
        if any(not(1<=v<=10) for v in a+b): bad.append(iid); continue
        sc[iid]={"A":a,"B":b,"src":f.split("/")[-1]}
print(f"оценено идей: {len(sc)} из {len(reg)}")
if bad: print(f"отброшено строк с ошибкой формата: {len(bad)}")
miss=[i for i in reg if i not in sc]
if miss: print(f"БЕЗ ОЦЕНКИ: {len(miss)}  (например: {', '.join(miss[:8])})")

rows=[]
for iid,v in sc.items():
    A=sum(x*w for x,w in zip(v["A"],WA)); B=sum(x*w for x,w in zip(v["B"],WB))
    # вариант 2: A5 «барьеры в нашу пользу» перенесён на ось позиции (претензия критика)
    a2=[x for k,x in enumerate(v["A"]) if k!=4]; w2=[w for k,w in enumerate(WA) if k!=4]
    w2=[w/sum(w2) for w in w2]
    A2=sum(x*w for x,w in zip(a2,w2))
    b2=v["B"]+[v["A"][4]]; wb2=[w*(1-.084) for w in WB]+[.084]; wb2=[w/sum(wb2) for w in wb2]
    B2=sum(x*w for x,w in zip(b2,wb2))
    rows.append({"id":iid,"name":reg[iid]["name"],"gen":reg[iid].get("gen"),
        "A":round(A,3),"B":round(B,3),"total":round(.7*A+.3*B,3),
        "A_alt":round(A2,3),"B_alt":round(B2,3),"total_alt":round(.7*A2+.3*B2,3),
        "exit":v["A"][6],"speed":v["B"][0],"style":v["B"][6],
        **{f"A{k+1}_{n}":v["A"][k] for k,n in enumerate(KA)},
        **{f"B{k+1}_{n}":v["B"][k] for k,n in enumerate(KB)}})
rows.sort(key=lambda r:-r["total"])
json.dump(rows,open("work/state/62_screen_scores.json","w",encoding="utf-8"),
          ensure_ascii=False,indent=1)

t=[r["total"] for r in rows]
print(f"\nРАЗБРОС ИТОГА: мин {min(t):.2f}  медиана {np.median(t):.2f}  макс {max(t):.2f}  "
      f"ст.откл {np.std(t):.2f}")
print("распределение:", end=" ")
for lo in range(1,10):
    print(f"{lo}-{lo+1}:{sum(1 for x in t if lo<=x<lo+1)}", end="  ")
print()
gate=[r for r in rows if r["exit"]>=5]
print(f"\nВОРОТА ПО ВЫХОДУ (A7>=5): прошли {len(gate)} из {len(rows)}")
print(f"\n{'#':>3} {'итог':>5} {'A':>5} {'B':>5} {'вых':>4} {'ист':>4}  идея")
print("-"*100)
for i,r in enumerate(rows[:30],1):
    print(f"{i:>3} {r['total']:5.2f} {r['A']:5.2f} {r['B']:5.2f} {r['exit']:>4} "
          f"{str(r['gen']):>4}  [{r['id']}] {r['name'][:54]}")
