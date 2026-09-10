# -*- coding: utf-8 -*-
"""Короткий дайджест для первичного отсева (экран)."""
import json, re
def clip(s,n):
    if not s: return "—"
    s=re.sub(r'\s+',' ',s).strip()
    return s if len(s)<=n else s[:n-1].rsplit(' ',1)[0]+"…"
reg=json.load(open("/home/user/claude-test/work/state/10_registry.json",encoding="utf-8"))
rows=[]
for i in reg:
    rows.append(f"[{i['id']}] {i['name']}\n"
                f"   что: {clip(i.get('essence'),190)}\n"
                f"   кто платит / чек: {clip(i.get('payer'),90)} | {clip(i.get('revenue_model'),110)}\n"
                f"   окно: {clip(i.get('window'),150)}\n"
                f"   конкуренты: {clip(i.get('competition'),150)}\n"
                f"   капитал: {clip(i.get('capital'),70)}")
txt="\n\n".join(rows)
open("/home/user/claude-test/work/state/12_digest_short.txt","w",encoding="utf-8").write(txt)
print(f"идей: {len(reg)}, короткий дайджест: {len(txt)} символов")
