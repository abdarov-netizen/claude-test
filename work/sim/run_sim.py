# -*- coding: utf-8 -*-
"""Прогон Монте-Карло по конфигам идей во всех сценариях."""
import json, os, sys, glob
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from engine import simulate, summarize, path_table

N_RUNS   = 20000          # требование ТЗ: от 10 000
MONTHS   = 60
HURDLE   = 0.197          # сумовой депозит 19.7% = альтернативная безрисковая доходность
FOUNDER_SALARY = 4000.0   # альтернативная зарплата $4 000/мес

SCENARIOS = {
 "base":            dict(seed=101, founder_salary_month=0.0,            overrides={}),
 "opportunity_cost":dict(seed=202, founder_salary_month=FOUNDER_SALARY, overrides={}),
 "devaluation":     dict(seed=303, founder_salary_month=0.0,
                         overrides={"fx":{"uzs_vs_usd_annual_drift":-0.08,"annual_vol":0.12}}),
 "hard_competition":dict(seed=404, founder_salary_month=0.0,
                         overrides={"competition":{"entry_hazard_month":0.045,"price_impact":0.25,
                                                   "winrate_impact":0.40,"churn_impact_abs":0.008}}),
 "slow_window":     dict(seed=505, founder_salary_month=0.0,
                         overrides={"launch":{"delay_months":[8,14,22],"p_fail_to_launch":0.20}}),
}

def run_one(cfg_path, out_dir):
    cfg = json.load(open(cfg_path, encoding="utf-8"))
    name = cfg.get("name", os.path.basename(cfg_path))
    idea_id = cfg.get("id", os.path.basename(cfg_path).split(".")[0])
    res_all, paths = {}, None
    for sc, kw in SCENARIOS.items():
        r = simulate(cfg, n=N_RUNS, months=MONTHS, seed=kw["seed"],
                     founder_salary_month=kw["founder_salary_month"],
                     hurdle_annual=HURDLE, overrides=kw["overrides"] or None)
        res_all[sc] = summarize(r, sc)
        if sc == "base":
            paths = path_table(r, MONTHS)
            npv_sorted = np.sort(r["npv"])
            res_all[sc]["npv_deciles"] = [float(np.percentile(r["npv"], p))
                                          for p in range(5, 100, 5)]
            res_all[sc]["hist"] = np.histogram(np.clip(r["npv"], -300000, 4000000),
                                               bins=60)[0].tolist()
            res_all[sc]["hist_edges"] = np.histogram(np.clip(r["npv"], -300000, 4000000),
                                               bins=60)[1].tolist()
    out = {"id": idea_id, "name": name, "config": cfg,
           "scenarios": res_all, "monthly_path_base": paths}
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, f"sim_{idea_id}.json")
    json.dump(out, open(dst, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return idea_id, name, res_all

def fmt(v, money=True):
    if v != v: return "  н/д "
    return (f"${v:>10,.0f}" if money else f"{v:>7.1%}")

if __name__ == "__main__":
    cfgs = sorted(glob.glob("/home/user/claude-test/work/sim/configs/*.json"))
    if not cfgs:
        print("нет конфигов в work/sim/configs/"); sys.exit(1)
    print(f"конфигов: {len(cfgs)}, прогонов на сценарий: {N_RUNS:,}, сценариев: {len(SCENARIOS)}\n")
    for c in cfgs:
        iid, nm, res = run_one(c, "/home/user/claude-test/work/sim/results")
        print(f"=== [{iid}] {nm}")
        print(f"{'сценарий':<18}{'выживание':>11}{'ожид. NPV':>14}{'медиана':>14}"
              f"{'NPV|выжил':>14}{'P(NPV>0)':>10}")
        for sc, s in res.items():
            print(f"{sc:<18}{s['P_survive_60m']:>10.1%}{fmt(s['E_NPV']):>14}"
                  f"{fmt(s['median_NPV']):>14}{fmt(s['E_NPV_given_survive']):>14}"
                  f"{s['P_NPV_gt_0']:>10.1%}")
        print()
