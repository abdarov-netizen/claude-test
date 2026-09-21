# -*- coding: utf-8 -*-
"""Сборка глубоких оценок одного оценщика из файлов dX*.txt."""
import re, sys, json, glob, os
SP='/tmp/claude-0/-home-user-claude-test/6b9b5210-62a0-5c3e-960e-a4c9f8e112b0/scratchpad'
KA=['A1_economics','A2_market','A3_why_now','A4_white_space','A5_barriers','A6_wtp','A7_exit']
KB=['B1_speed','B2_reg','B3_fin','B4_deal','B5_family','B6_sales','B7_style']
def collect(pat):
    sc, why, comp = {}, {}, {}
    for f in sorted(glob.glob(f'{SP}/{pat}')):
        for ln in open(f,encoding='utf-8'):
            ln=ln.strip()
            m=re.match(r'^([A-Z]{2,5}-\d{2,3})\|([\d,\s]+)\|([\d,\s]+)$', ln)
            if m:
                a=[int(v) for v in m.group(2).split(',')]
                b=[int(v) for v in m.group(3).split(',')]
                if len(a)==7 and len(b)==7 and all(1<=v<=10 for v in a+b):
                    sc[m.group(1)]=dict(zip(KA,a))|dict(zip(KB,b))
                continue
            m=re.match(r'^([A-Z]{2,5}-\d{2,3})#(.+)$', ln)
            if m: why[m.group(1)]=m.group(2).strip(); continue
            m=re.match(r'^([A-Z]{2,5}-\d{2,3})!(.+)$', ln)
            if m: comp.setdefault(m.group(1),[]).append(m.group(2).strip())
    return sc, why, comp
if __name__=='__main__':
    pat, out = sys.argv[1], sys.argv[2]
    sc,why,comp = collect(pat)
    json.dump({'scores':sc,'why':why,'comp':comp}, open(f'{SP}/{out}','w',encoding='utf-8'),
              ensure_ascii=False, indent=1)
    print(f'{pat}: оценок {len(sc)}, обоснований {len(why)}, находок по конкурентам {sum(len(v) for v in comp.values())} по {len(comp)} идеям')
