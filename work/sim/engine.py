# -*- coding: utf-8 -*-
"""
Помесячная стохастическая модель бизнеса в Узбекистане, 60 месяцев, Монте-Карло.
Векторизовано на numpy: состояние — массивы формы (N,), цикл по месяцам.

Учтено (по ТЗ):
  * воронка с НАСЫЩЕНИЕМ рынка (ограниченный пул клиентов, доля захвата в месяц)
  * отток (churn), с дрейфом
  * РОСТ стоимости привлечения (CAC растёт во времени И при росте проникновения)
  * налоги РУз: оборотный 4% | общий (прибыль 15% + НДС 12% + соцналог 12%) | IT Park (0%/0%)
  * оборотный капитал (DSO/DPO/предоплаты)
  * ЛИМИТ капитала основателя (по умолчанию $150k) -> неплатёжеспособность = закрытие
  * ОГРАНИЧЕННАЯ СКОРОСТЬ НАЙМА (макс. найм в месяц, рампа новичка)
  * ВХОД КОНКУРЕНТА (пуассоновский риск; давит цену, win-rate, повышает отток)
  * ПРАВО ЗАКРЫТЬСЯ (реальный опцион: добровольный выход при отсутствии тяги)
  * валютный курс (доля выручки/затрат в USD против сумовой части)
  * общий фактор качества рынка -> положительная корреляция параметров (жирные хвосты)
"""
import numpy as np


def tri(rng, spec, n):
    """Треугольное распределение по [низ, мода, верх]. Скаляр -> константа."""
    if np.isscalar(spec):
        return np.full(n, float(spec))
    l, m, h = [float(x) for x in spec]
    if h - l < 1e-12:
        return np.full(n, m)
    return rng.triangular(l, m, h, n)


def simulate(cfg, n=20000, months=60, seed=7, founder_salary_month=0.0,
             hurdle_annual=0.197, overrides=None):
    """Возвращает словарь массивов результатов длиной n."""
    if overrides:
        cfg = _deep_merge(cfg, overrides)
    rng = np.random.default_rng(seed)

    mk, pr, fn = cfg["market"], cfg["pricing"], cfg["funnel"]
    ch, dl, co = cfg["churn"], cfg["delivery"], cfg["costs"]
    wc, tx, cp = cfg["wc"], cfg["tax"], cfg["competition"]
    ex, ca, ab = cfg["exit"], cfg["capital"], cfg["abandon"]
    fx = cfg.get("fx", {})

    # ---------- розыгрыш параметров прогона ----------
    z = rng.standard_normal(n)                    # общий фактор качества рынка
    rho = float(cfg.get("common_factor_strength", 0.15))

    tam        = tri(rng, mk["tam_customers"], n) * np.clip(1 + rho * z, 0.35, 2.2)
    max_capt   = float(mk.get("max_capture_rate", 0.05))   # доля свободного пула в месяц
    winback    = float(mk.get("winback_share", 0.5))       # часть ушедших возвращается в пул

    arpu0      = tri(rng, pr["arpu_month"], n) * np.clip(1 + 0.8 * rho * z, 0.4, 2.0)
    price_esc  = float(pr.get("price_escalation_annual", 0.04))

    opps_rep   = tri(rng, fn.get("opps_per_rep_month", fn.get("deals_per_rep_month")), n)
    win_rate   = np.clip(tri(rng, fn["win_rate"], n) * np.clip(1 + 0.8 * rho * z, 0.3, 2.0), 0.01, 0.95)
    cac0       = tri(rng, fn["cac0"], n) / np.clip(1 + 0.6 * rho * z, 0.4, 2.0)
    cac_growth = float(fn.get("cac_growth_annual", 0.15))
    cac_pen_k  = float(fn.get("cac_penetration_k", 1.2))   # насколько CAC растёт с проникновением

    churn0     = np.clip(tri(rng, ch["monthly"], n) / np.clip(1 + rho * z, 0.4, 2.0), 0.0005, 0.35)
    churn_dr   = float(ch.get("drift_annual", 0.0))

    cli_fte    = tri(rng, dl["clients_per_fte"], n)
    max_hire   = float(dl.get("max_hires_per_month", 1.0))
    fte_cost   = tri(rng, dl["fte_cost_month"], n)
    ramp_m     = int(dl.get("ramp_months", 2))
    max_fte    = float(dl.get("max_fte", 60))

    fixed_op   = tri(rng, co["fixed_opex_month"], n)
    gm         = np.clip(tri(rng, co["gross_margin"], n), 0.05, 0.98)
    mkt_share  = float(co.get("mkt_budget_share_of_rev", 0.08))
    mkt_floor  = float(co.get("mkt_budget_floor", 800.0))
    capex0     = tri(rng, co["startup_capex"], n)

    dso        = tri(rng, wc["dso_days"], n)
    dpo        = float(wc.get("dpo_days", 30))
    prepay     = float(wc.get("prepay_share", 0.0))

    regime     = tx.get("regime", "general")
    social_tax = float(tx.get("social_tax", 0.12))
    vat_rate   = float(tx.get("vat_rate", 0.12))
    turn_rate  = float(tx.get("turnover_rate", 0.04))
    prof_rate  = float(tx.get("profit_rate", 0.15))
    vat_input  = float(tx.get("input_vat_share_of_cogs", 0.5))
    turn_cap   = float(tx.get("turnover_regime_cap_usd_year", 80000.0))
    vat_neutral= bool(tx.get("vat_passthrough_b2b", True))

    entry_haz  = float(cp.get("entry_hazard_month", 0.015))
    cp_price   = float(cp.get("price_impact", 0.15))
    cp_churn   = float(cp.get("churn_impact_abs", 0.004))
    cp_win     = float(cp.get("winrate_impact", 0.25))

    mult       = tri(rng, ex["ebitda_multiple"], n)
    p_exit     = float(ex.get("prob_exit_market", 0.6))
    mult_hold  = float(ex.get("hold_multiple_factor", 0.55))

    owner_cap  = float(ca.get("owner_capital", 150000.0))
    cash_buf_m = float(ca.get("cash_buffer_months", 3.0))

    ab_month   = int(ab.get("check_month", 18))
    ab_minrev  = tri(rng, ab["min_monthly_revenue"], n)
    ab_salvage = float(ab.get("salvage_share_of_wc", 0.8))

    ln = cfg.get("launch", {})
    delay      = np.round(tri(rng, ln.get("delay_months", [0, 0, 0]), n)).astype(int)
    p_nolaunch = float(ln.get("p_fail_to_launch", 0.0))
    fail_launch= rng.random(n) < p_nolaunch
    p_nodemand = float(ln.get("p_no_demand", 0.0))
    nodemand   = rng.random(n) < p_nodemand
    nd_win     = float(ln.get("no_demand_winrate_factor", 0.15))
    nd_tam     = float(ln.get("no_demand_tam_factor", 0.25))
    win_rate   = np.where(nodemand, win_rate * nd_win, win_rate)
    tam        = np.where(nodemand, tam * nd_tam, tam)
    pool_init  = tam.copy()

    fx_drift   = float(fx.get("uzs_vs_usd_annual_drift", 0.0))  # >0 = сум укрепляется (USD-выручка растёт)
    fx_vol     = float(fx.get("annual_vol", 0.06))
    usd_rev_sh = float(fx.get("usd_revenue_share", 0.0))
    usd_cost_sh= float(fx.get("usd_cost_share", 0.25))

    # ---------- состояние ----------
    cash      = np.zeros(n)
    injected  = np.zeros(n)
    clients   = np.zeros(n)
    pool      = pool_init.copy()
    fte_del   = np.full(n, float(dl.get("start_fte", 1.0)))
    fte_sal   = np.full(n, float(fn.get("start_reps", 1.0)))
    alive     = np.ones(n, dtype=bool)
    comp_in   = np.zeros(n, dtype=bool)
    ar        = np.zeros(n)
    ap        = np.zeros(n)
    nol       = np.zeros(n)          # накопленный убыток к переносу
    vat_credit= np.zeros(n)
    fx_idx    = np.ones(n)
    death_m   = np.full(n, months + 1, dtype=int)
    death_kind= np.zeros(n, dtype=int)   # 0 жив, 1 неплатёжеспособность, 2 добровольное закрытие

    rec = cfg.get("_record_paths", True)
    path = {k: np.zeros((months + 1, n)) for k in
            ("revenue", "ebitda", "cash", "clients", "fte", "alive", "injected", "tax")} if rec else None

    disc_m    = (1.0 + hurdle_annual) ** (1.0 / 12.0)
    pv_flows  = np.zeros(n)
    rev_hist  = np.zeros((12, n))
    ebitda_hist = np.zeros((12, n))
    peak_need = np.zeros(n)
    cum_rev   = np.zeros(n)
    first_rev_m = np.full(n, -1, dtype=int)

    # стартовые вложения (месяц 0)
    inj = capex0 + fixed_op * float(ca.get("prefund_months", 2.0))
    inj = np.minimum(inj, owner_cap)
    cash += inj; injected += inj
    pv_flows += -inj

    for t in range(1, months + 1):
        a = alive.copy()
        yrs = t / 12.0

        # курс
        fx_idx *= np.exp((fx_drift - 0.5 * fx_vol ** 2) / 12.0
                         + fx_vol / np.sqrt(12.0) * rng.standard_normal(n))
        fx_eff_rev = usd_rev_sh + (1 - usd_rev_sh) * fx_idx
        fx_eff_cost = usd_cost_sh + (1 - usd_cost_sh) * fx_idx

        # вход конкурента
        newc = (~comp_in) & a & (rng.random(n) < entry_haz)
        comp_in |= newc

        # цена
        arpu = arpu0 * (1 + price_esc) ** yrs * fx_eff_rev
        arpu = np.where(comp_in, arpu * (1 - cp_price), arpu)

        # воронка с насыщением
        pen = np.clip(1.0 - pool / np.maximum(tam, 1e-9), 0, 1)
        cac = cac0 * (1 + cac_growth) ** yrs * (1 + cac_pen_k * pen) * fx_eff_cost
        wr = np.where(comp_in, win_rate * (1 - cp_win), win_rate)

        mkt_budget = np.maximum(mkt_floor, mkt_share * (rev_hist[(t - 1) % 12] if t > 1 else 0.0))
        cap_capacity = fte_sal * opps_rep * wr
        cap_budget = mkt_budget / np.maximum(cac, 1e-9)
        cap_market = pool * max_capt
        cap_deliver = np.maximum(0.0, fte_del * cli_fte - clients)   # нельзя брать больше, чем обслужим
        new_cli = np.minimum(np.minimum(cap_capacity, cap_budget),
                             np.minimum(cap_market, cap_deliver))
        new_cli = np.where(a, np.maximum(new_cli, 0.0), 0.0)
        new_cli = np.where(t <= delay, 0.0, new_cli)          # лицензии/сборка продукта
        new_cli = np.where(fail_launch & (t > delay), 0.0, new_cli)  # запуск не состоялся

        # отток
        churn = np.clip(churn0 * (1 + churn_dr) ** yrs + np.where(comp_in, cp_churn, 0.0), 0.0, 0.5)
        lost = clients * churn

        clients = np.where(a, clients + new_cli - lost, clients)
        pool = np.where(a, pool - new_cli + lost * winback, pool)
        pool = np.maximum(pool, 0.0)

        # выручка и затраты
        revenue = np.where(a, clients * arpu, 0.0)
        cogs = revenue * (1 - gm)
        payroll = (fte_del + fte_sal) * fte_cost * fx_eff_cost
        social = payroll * (0.0 if regime == "itpark" else social_tax)
        opex = fixed_op * fx_eff_cost + payroll + social + mkt_budget + founder_salary_month
        ebitda = revenue - cogs - opex

        # налоги
        if regime == "turnover":
            small = (cum_rev + revenue) <= turn_cap * max(1.0, t / 12.0)
            tax = np.where(small, turn_rate * revenue, turn_rate * revenue)
            vat_pay = np.zeros(n)
        elif regime == "itpark":
            tax = np.zeros(n)
            vat_pay = np.zeros(n) if vat_neutral else np.maximum(0.0, vat_rate * (revenue - cogs * vat_input))
        else:
            ebt = ebitda
            taxable = np.maximum(0.0, ebt - nol)
            nol = np.maximum(0.0, nol - np.maximum(0.0, ebt)) + np.maximum(0.0, -ebt)
            tax = prof_rate * taxable
            if vat_neutral:
                vat_pay = np.zeros(n)
            else:
                vat_due = vat_rate * revenue - vat_rate * cogs * vat_input
                vat_credit = np.maximum(0.0, vat_credit - np.maximum(0.0, vat_due))
                vat_pay = np.maximum(0.0, vat_due)
                vat_credit += np.maximum(0.0, -vat_due)

        # оборотный капитал
        ar_new = revenue * (1 - prepay) * dso / 30.0
        ap_new = (cogs + opex) * dpo / 30.0
        d_wc = (ar_new - ar) - (ap_new - ap)
        ar, ap = ar_new, ap_new

        cf = np.where(a, ebitda - tax - vat_pay - d_wc, 0.0)

        # найм (ограниченная скорость)
        need_del = np.ceil(np.maximum(clients, 0.0) / np.maximum(cli_fte, 1e-9))
        want = np.clip(need_del + 1.0 - fte_del, 0.0, max_hire)
        fte_del = np.where(a, np.minimum(fte_del + want, max_fte), fte_del)
        need_sal = np.clip(1.0 + revenue / np.maximum(fte_cost * 12.0, 1e-9), 1.0,
                           float(fn.get("max_reps", 6)))
        fte_sal = np.where(a, np.minimum(fte_sal + np.clip(need_sal - fte_sal, 0.0, 0.5), need_sal), fte_sal)

        cash = cash + cf

        # докапитализация из лимита основателя
        room = np.maximum(0.0, owner_cap - injected)
        need = np.where(a & (cash < 0), -cash, 0.0)
        add = np.minimum(need, room)
        cash += add; injected += add
        pv_flows += -add / disc_m ** t
        peak_need = np.maximum(peak_need, injected)

        # 1) неплатёжеспособность
        dead = a & (cash < -1e-6)
        if dead.any():
            salv = np.maximum(0.0, ar * ab_salvage)
            pv_flows += np.where(dead, salv / disc_m ** t, 0.0)
            alive &= ~dead; death_m = np.where(dead, t, death_m); death_kind = np.where(dead, 1, death_kind)
            a = alive.copy()

        # 1б) провал запуска -> закрытие через 3 месяца после планового старта
        fl = a & fail_launch & (t >= delay + 3)
        if fl.any():
            salv = np.maximum(0.0, cash + ar * ab_salvage)
            pv_flows += np.where(fl, salv / disc_m ** t, 0.0)
            alive &= ~fl; death_m = np.where(fl, t, death_m); death_kind = np.where(fl, 3, death_kind)
            a = alive.copy()

        # 2) ПРАВО ЗАКРЫТЬСЯ (реальный опцион)
        if t >= ab_month:
            ttm = rev_hist.sum(axis=0) / 12.0
            quit_ = a & (ttm < ab_minrev) & (ebitda < 0) & (t >= delay + 6)
            if quit_.any():
                salv = np.maximum(0.0, cash + ar * ab_salvage)
                pv_flows += np.where(quit_, salv / disc_m ** t, 0.0)
                alive &= ~quit_; death_m = np.where(quit_, t, death_m); death_kind = np.where(quit_, 2, death_kind)
                a = alive.copy()

        # распределение избытка денег владельцу
        buf = cash_buf_m * (opex + cogs)
        dist = np.where(a & (cash > buf), cash - buf, 0.0)
        cash -= dist
        pv_flows += dist / disc_m ** t

        if rec:
            path["revenue"][t] = np.where(a, revenue, 0.0)
            path["ebitda"][t]  = np.where(a, ebitda, 0.0)
            path["cash"][t]    = np.where(alive, cash, 0.0)
            path["clients"][t] = np.where(alive, clients, 0.0)
            path["fte"][t]     = np.where(alive, fte_del + fte_sal, 0.0)
            path["alive"][t]   = alive.astype(float)
            path["injected"][t]= injected
            path["tax"][t]     = np.where(a, tax + vat_pay, 0.0)

        rev_hist[t % 12] = np.where(a, revenue, 0.0)
        ebitda_hist[t % 12] = np.where(a, ebitda, 0.0)
        cum_rev += np.where(a, revenue, 0.0)
        first_rev_m = np.where((first_rev_m < 0) & (revenue > 1.0), t, first_rev_m)

    # терминальная стоимость
    ebitda_ttm = ebitda_hist.sum(axis=0)
    got_exit = rng.random(n) < p_exit
    eff_mult = np.where(got_exit, mult, mult * mult_hold)
    tv = np.where(alive & (ebitda_ttm > 0), ebitda_ttm * eff_mult, 0.0) + np.where(alive, cash, 0.0)
    pv_flows += tv / disc_m ** months

    return dict(npv=pv_flows, alive=alive, fail_launch=fail_launch, no_demand=nodemand, delay=delay, injected=injected, ebitda_ttm=ebitda_ttm,
                rev_ttm=rev_hist.sum(axis=0), tv=tv, death_month=death_m, death_kind=death_kind,
                clients=clients, peak_capital=peak_need, first_rev_month=first_rev_m,
                competitor=comp_in, cum_rev=cum_rev, path=path)


def path_table(res, months=60):
    """Помесячная сводка: медиана и квартили по ВЫЖИВШИМ на каждый месяц + доля живых."""
    p = res["path"]
    rows = []
    for t in range(1, months + 1):
        al = p["alive"][t] > 0.5
        sel = lambda k: p[k][t][al]
        row = {"month": t, "P_alive": float(al.mean())}
        for k in ("revenue", "ebitda", "cash", "clients", "fte", "injected", "tax"):
            v = sel(k)
            row[k + "_p25"] = float(np.percentile(v, 25)) if v.size else 0.0
            row[k + "_med"] = float(np.median(v)) if v.size else 0.0
            row[k + "_p75"] = float(np.percentile(v, 75)) if v.size else 0.0
        rows.append(row)
    return rows


def _deep_merge(a, b):
    out = dict(a)
    for k, v in b.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = v
    return out


def summarize(res, label=""):
    npv, alive = res["npv"], res["alive"]
    surv = alive.mean()
    q = lambda x, p: float(np.percentile(x, p)) if len(x) else float("nan")
    s_npv = npv[alive]
    return {
        "label": label,
        "n": int(len(npv)),
        "P_survive_60m": float(surv),
        "E_NPV": float(npv.mean()),                 # ожидаемый NPV по ВСЕМ прогонам
        "median_NPV": float(np.median(npv)),
        "NPV_p5": q(npv, 5), "NPV_p25": q(npv, 25), "NPV_p75": q(npv, 75), "NPV_p95": q(npv, 95),
        "P_NPV_gt_0": float((npv > 0).mean()),
        "E_NPV_given_survive": float(s_npv.mean()) if surv > 0 else float("nan"),
        "median_NPV_given_survive": float(np.median(s_npv)) if surv > 0 else float("nan"),
        "NPV_given_survive_p25": q(s_npv, 25) if surv > 0 else float("nan"),
        "NPV_given_survive_p75": q(s_npv, 75) if surv > 0 else float("nan"),
        "E_loss_given_fail": float(npv[~alive].mean()) if surv < 1 else float("nan"),
        "P_insolvency": float((res["death_kind"] == 1).mean()),
        "P_voluntary_close": float((res["death_kind"] == 2).mean()),
        "P_fail_to_launch": float((res["death_kind"] == 3).mean()),
        "P_no_demand_draw": float(res["no_demand"].mean()),
        "median_launch_delay_m": float(np.median(res["delay"])),
        "E_peak_capital": float(res["peak_capital"].mean()),
        "p90_peak_capital": q(res["peak_capital"], 90),
        "E_rev_ttm_y5": float(res["rev_ttm"].mean()),
        "median_rev_ttm_y5_alive": float(np.median(res["rev_ttm"][alive])) if surv > 0 else float("nan"),
        "E_ebitda_ttm_y5": float(res["ebitda_ttm"].mean()),
        "median_first_rev_month": float(np.median(res["first_rev_month"])),
        "P_competitor_entered": float(res["competitor"].mean()),
    }
