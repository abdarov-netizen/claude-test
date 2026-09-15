# -*- coding: utf-8 -*-
"""Сопоставление идей заказчика с реестром 517.
Комбинированная мера: символьные 3-5-граммы (устойчивы к морфологии русского)
+ словесные униграммы. Длины описаний выравниваются."""
import json, re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
SCR="/tmp/claude-0/-home-user-claude-test/6b9b5210-62a0-5c3e-960e-a4c9f8e112b0/scratchpad"

def norm(s, cap=260):
    if not s: return ""
    s=re.sub(r'[^а-яёa-z0-9 ]',' ',str(s).lower().replace('ё','е'))
    s=re.sub(r'\s+',' ',s).strip()
    return s[:cap]

reg=json.load(open("work/state/40_registry_v2.json",encoding="utf-8"))
usr=json.load(open(f"{SCR}/user_ideas.json",encoding="utf-8"))
mine=[norm((d.get("name") or "")+". "+(d.get("essence") or "")) for d in reg]
theirs=[norm((d.get("Идея") or "")+". "+(d.get("Суть в одной строке") or "")) for d in usr]

def sim(analyzer,ngram):
    v=TfidfVectorizer(analyzer=analyzer,ngram_range=ngram,min_df=1,sublinear_tf=True)
    X=v.fit_transform(mine+theirs)
    A,B=X[:len(mine)],X[len(mine):]
    return (B@A.T).toarray()
Sc=sim("char_wb",(3,5))
Sw=sim("word",(1,1))
S=0.6*Sc+0.4*Sw
best=S.argmax(axis=1); score=S.max(axis=1)
top3=np.argsort(-S,axis=1)[:,:3]

out=[]
for i,d in enumerate(usr):
    out.append({"row":i,"rank":d.get("Ранг"),"name":d.get("Идея"),
        "essence":d.get("Суть в одной строке"),"cat":d.get("Категория"),
        "start":d.get("Старт, $"),"months":d.get("Мес. до выручки"),
        "gm":d.get("Вал. маржа, %"),"rev3":d.get("Выручка Y3, $"),"pr3":d.get("Прибыль Y3, $"),
        "analog":d.get("Аналог в мире"),"comp":d.get("Конкуренты в РУз"),
        "weak":d.get("Главная слабость"),
        "sim":float(score[i]),"match_id":reg[best[i]]["id"],"match_name":reg[best[i]]["name"],
        "top3":[{"id":reg[j]["id"],"name":reg[j]["name"],"s":float(S[i,j])} for j in top3[i]]})
json.dump(out,open(f"{SCR}/match.json","w",encoding="utf-8"),ensure_ascii=False,indent=1,default=str)

print("РАСПРЕДЕЛЕНИЕ БЛИЗОСТИ К МОЕМУ РЕЕСТРУ:")
for lo,hi in [(0.60,1.01),(0.45,0.60),(0.35,0.45),(0.25,0.35),(0.0,0.25)]:
    print(f"   {lo:.2f}-{hi:.2f}: {sum(1 for o in out if lo<=o['sim']<hi):3d}")
print("\n=== ТОП-25 ПО БЛИЗОСТИ (кандидаты в дубли, проверяю глазами) ===")
for o in sorted(out,key=lambda x:-x["sim"])[:25]:
    print(f"{o['sim']:.2f} «{str(o['name'])[:58]}»")
    print(f"      ~ [{o['match_id']}] {o['match_name'][:62]}")
