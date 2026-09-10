# -*- coding: utf-8 -*-
"""Компактный дайджест реестра идей для скоринга."""
import json, re, sys, textwrap

def clip(s, n):
    if not s: return "—"
    s = re.sub(r'\s+', ' ', s).strip()
    return s if len(s) <= n else s[:n-1].rsplit(' ',1)[0] + "…"

def main(maxlen=300):
    reg = json.load(open("/home/user/claude-test/work/state/10_registry.json",encoding="utf-8"))
    out=[]
    for i in reg:
        out.append(
f"""[{i['id']}] {i['name']}
  суть: {clip(i.get('essence'),maxlen)}
  платит: {clip(i.get('payer'),160)}
  доход: {clip(i.get('revenue_model'),200)}
  N: {clip(i.get('need'),maxlen)}
  A: {clip(i.get('approach'),maxlen)}
  B: {clip(i.get('benefit'),maxlen)}
  C: {clip(i.get('competition'),380)}
  аналог: {clip(i.get('analog'),260)}
  окно: {clip(i.get('window'),300)}
  капитал: {clip(i.get('capital'),120)}
  лицензии: {clip(i.get('license'),160)}
  риск1: {clip(i.get('risk1'),200)}""")
    txt="\n\n".join(out)
    open("/home/user/claude-test/work/state/11_digest.txt","w",encoding="utf-8").write(txt)
    print(f"идей: {len(reg)}, дайджест: {len(txt)} символов -> 11_digest.txt")

if __name__=="__main__":
    main(int(sys.argv[1]) if len(sys.argv)>1 else 300)
