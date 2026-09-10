import json,sys,numpy as np
sys.path.insert(0,'.')
from engine import simulate, path_table
for cid in ("FIN-01+","FIN-19","PRO-22"):
    cfg=json.load(open(f"configs/{cid}.json",encoding="utf-8"))
    r=simulate(cfg,n=8000,seed=77)
    t=path_table(r,60)
    print(f"\n=== {cid} ===")
    print(f"  задержка запуска (медиана): {np.median(r['delay']):.0f} мес")
    print(f"  причины смерти: неплатёжеспособность {(r['death_kind']==1).mean():.1%}, "
          f"добровольно {(r['death_kind']==2).mean():.1%}, провал запуска {(r['death_kind']==3).mean():.1%}")
    print(f"  медиана месяца смерти: {np.median(r['death_month'][r['death_month']<=60]) if (r['death_month']<=60).any() else '-'}")
    print(f"  пик вложенного капитала: среднее ${r['peak_capital'].mean():,.0f}, p90 ${np.percentile(r['peak_capital'],90):,.0f}")
    for m in (6,12,18,24,36,60):
        x=t[m-1]
        print(f"   мес {m:2d}: живых {x['P_alive']:5.1%} клиентов {x['clients_med']:5.1f} "
              f"выручка ${x['revenue_med']:>8,.0f} EBITDA ${x['ebitda_med']:>8,.0f} касса ${x['cash_med']:>9,.0f}")
