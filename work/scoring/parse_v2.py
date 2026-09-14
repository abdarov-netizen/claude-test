# -*- coding: utf-8 -*-
"""Разбор идей V2: механизм, триггер, деньги. Плюс проверка квот и дедупликация."""
import re, os, json, glob, hashlib

FIELDS = {
 "механизм":"mech","триггер":"trigger","суть":"essence","кто платит":"payer",
 "доход":"revenue","n":"need","a":"approach","b":"benefit","c":"competition",
 "аналог":"analog","окно":"window","деньги":"money","риск":"risk1","источники":"sources",
}
MECH_RU = {
 "M01":"купить действующий бизнес","M02":"консолидация (роллап)","M03":"эксклюзивные права",
 "M04":"построить актив и сдавать","M05":"посредник в сделке","M06":"риск на балансе",
 "M07":"продажа экспертизы","M08":"производство товара","M09":"подписка на софт/данные",
 "M10":"вход за долю работой","M11":"арбитраж разрыва","M12":"управление чужим активом",
 "M13":"агрегация спроса","M14":"дефицитная лицензия","M15":"экспорт/импорт компетенции",
}
TRIG_RU = {
 "T01":"закон создал обязанность","T02":"закон снял барьер","T03":"приток капитала",
 "T04":"дефицит мощности","T05":"демографический сдвиг","T06":"разрыв цен",
 "T07":"слабый/уходящий монополист","T08":"владельцы стареют, бизнес на продажу",
 "T09":"иностранец заходит","T10":"иностранец ушёл","T11":"грузопотоки развернулись",
 "T12":"технология подешевела","T13":"работает у соседей, сюда не дошло",
}

def norm(raw):
    k=re.sub(r'\s*\(.*?\)\s*',' ',raw.strip().lower().rstrip(':')).strip()
    for pat,d in FIELDS.items():
        if k.startswith(pat): return d
    return None

def parse_file(path):
    txt=open(path,encoding="utf-8").read()
    out=[]
    for part in re.split(r'^###\s+',txt,flags=re.M)[1:]:
        head,_,body=part.partition("\n")
        m=re.match(r'([A-ZА-Я]{2,5}-\d{2,3})\s*[—\-–:]\s*(.+)',head.strip())
        if not m: continue
        d={"id":m.group(1).strip(),"name":m.group(2).strip(),
           "source_file":os.path.basename(path),"gen":"v2"}
        cur=None
        for line in body.split("\n"):
            fm=re.match(r'\s*[-*]\s*\*\*(.+?)\*\*\s*:?\s*(.*)$',line)
            if fm:
                cur=norm(fm.group(1))
                if cur: d[cur]=fm.group(2).strip()
            elif cur and line.strip() and not line.startswith("#"):
                d[cur]=(d.get(cur,"")+" "+line.strip()).strip()
        blob=json.dumps(d,ensure_ascii=False)
        mm=re.search(r'\bM(\d{2})\b',d.get("mech","") or blob)
        tt=re.search(r'\bT(\d{2})\b',d.get("trigger","") or blob)
        d["M"]="M"+mm.group(1) if mm else None
        d["T"]="T"+tt.group(1) if tt else None
        mo=d.get("money","")
        own=re.search(r'своих?\s*\$?\s*([\d.,]+)\s*(тыс|млн|k|m)?',mo,re.I)
        rai=re.search(r'привлеч\w*\s*\$?\s*([\d.,\- ]+)\s*(тыс|млн|k|m)?',mo,re.I)
        def val(x):
            if not x: return None
            try: v=float(re.split(r'[-–]',x.group(1).replace(" ","").replace(",","."))[0])
            except: return None
            u=(x.group(2) or "").lower()
            if u in ("тыс","k"): v*=1e3
            elif u in ("млн","m"): v*=1e6
            elif v<1000: v*=1e3
            return int(v)
        d["own_usd"]=val(own); d["raised_usd"]=val(rai)
        out.append(d)
    return out

def dedupe_key(d):
    t=re.sub(r'[^а-яa-z ]','',(d.get("name","")+" "+d.get("essence","")).lower())
    return hashlib.md5(" ".join(sorted(set(t.split()))[:14]).encode()).hexdigest()[:12]

if __name__=="__main__":
    new=[]
    for f in sorted(glob.glob("/home/user/claude-test/work/research2/ideas_*.md")):
        got=parse_file(f); new+=got
        nom=sum(1 for i in got if i["M"]=="M07")
        flag="" if nom<=max(4,int(len(got)*0.15)) else "  <-- КВОТА НАРУШЕНА"
        print(f"{os.path.basename(f):20s} -> {len(got):3d} идей | консалтинг M07: {nom}{flag}")
    old=json.load(open("/home/user/claude-test/work/state/10_registry.json",encoding="utf-8"))
    for o in old: o["gen"]="v1"
    seen={}; merged=[]
    for d in old+new:
        k=dedupe_key(d)
        if k in seen: seen[k]["dup_of"]=seen[k].get("dup_of",[])+[d["id"]]; continue
        seen[k]=d; merged.append(d)
    json.dump(merged,open("/home/user/claude-test/work/state/40_registry_v2.json","w",
              encoding="utf-8"),ensure_ascii=False,indent=1)
    n_new=sum(1 for d in merged if d.get("gen")=="v2")
    print(f"\nновых идей после дедупликации: {n_new}")
    print(f"всего в объединённом реестре:   {len(merged)}")
