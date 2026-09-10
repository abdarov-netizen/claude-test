# -*- coding: utf-8 -*-
"""Разбор markdown-файлов с идеями в структурированный реестр."""
import re, os, json, glob, csv

FIELD_MAP = {
    "арена":"arena", "суть":"essence", "кто платит":"payer",
    "модель дохода":"revenue_model", "n":"need", "a":"approach", "b":"benefit",
    "c":"competition", "доказанный аналог":"analog", "структурное окно":"window",
    "почему ложится":"country_fit", "стартовый капитал":"capital",
    "лицензии":"license", "риск":"risk1", "источники":"sources",
}

def norm_key(raw):
    k = raw.strip().lower().rstrip(':').strip()
    k = re.sub(r'\s*\(.*?\)\s*', ' ', k).strip()
    for pat, dest in FIELD_MAP.items():
        if k.startswith(pat):
            return dest
    return None

def parse_file(path):
    txt = open(path, encoding="utf-8").read()
    # блоки по заголовкам "### ID — Название"
    parts = re.split(r'^###\s+', txt, flags=re.M)[1:]
    out = []
    for p in parts:
        head, _, body = p.partition("\n")
        m = re.match(r'([A-ZА-Я]{2,5}(?:-[A-ZА-Я])?-\d{2,3})\s*[—\-–:]\s*(.+)', head.strip())
        if not m:
            continue
        idea = {"id": m.group(1).strip(), "name": m.group(2).strip(),
                "source_file": os.path.basename(path)}
        cur = None
        for line in body.split("\n"):
            fm = re.match(r'\s*[-*]\s*\*\*(.+?)\*\*\s*:?\s*(.*)$', line)
            if fm:
                cur = norm_key(fm.group(1))
                if cur:
                    idea[cur] = fm.group(2).strip()
            elif cur and line.strip() and not line.startswith("#"):
                idea[cur] = (idea.get(cur, "") + " " + line.strip()).strip()
        out.append(idea)
    return out

def money(s):
    """Грубое извлечение порядка стартового капитала в USD."""
    if not s: return None
    t = s.replace(" "," ").lower()
    nums = re.findall(r'(\d[\d\s.,]*)\s*(тыс|млн|k|m|000)?', t)
    vals = []
    for n, unit in nums:
        try: v = float(n.replace(" ","").replace(",","."))
        except: continue
        if v <= 0: continue
        if unit in ("тыс","k"): v *= 1000
        elif unit in ("млн","m"): v *= 1_000_000
        if 500 <= v <= 20_000_000: vals.append(v)
    return int(sum(vals)/len(vals)) if vals else None

if __name__ == "__main__":
    base = "/home/user/claude-test/work/research"
    all_ideas = []
    for f in sorted(glob.glob(os.path.join(base, "ideas_*.md"))):
        got = parse_file(f)
        all_ideas += got
        print(f"{os.path.basename(f):22s} -> {len(got):3d} идей")
    for i in all_ideas:
        i["capital_usd_est"] = money(i.get("capital",""))
    reg = "/home/user/claude-test/work/state/10_registry.json"
    json.dump(all_ideas, open(reg,"w",encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"\nВСЕГО идей: {len(all_ideas)}  ->  {reg}")
    miss = [i["id"] for i in all_ideas if not i.get("analog") or not i.get("window")]
    if miss: print("БЕЗ аналога или окна (нарушение фильтра):", ", ".join(miss))
