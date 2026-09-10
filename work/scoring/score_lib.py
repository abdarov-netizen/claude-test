# -*- coding: utf-8 -*-
"""Скоринг GE-McKinsey. Веса ЗАФИКСИРОВАНЫ в 02_weights_LOCKED.md ДО скоринга."""
import json, numpy as np

WA = {"A1_economics":0.24,"A2_market_size":0.18,"A3_why_now":0.15,"A4_white_space":0.13,
      "A5_barriers_for_us":0.12,"A6_wtp":0.10,"A7_exit":0.08}
WB = {"B1_speed_to_revenue":0.20,"B2_reg_access":0.16,"B3_fin_expertise":0.15,
      "B4_deal_capital":0.15,"B5_family_industry":0.13,"B6_team_sales":0.12,"B7_style_fit":0.09}
AXIS_W = {"A":0.70,"B":0.30}

RU = {"A1_economics":"Экономика отрасли","A2_market_size":"Размер рынка снизу вверх",
      "A3_why_now":"Окно «почему сейчас»","A4_white_space":"Свободное место",
      "A5_barriers_for_us":"Барьеры в нашу пользу","A6_wtp":"Готовность платить",
      "A7_exit":"Потенциал выхода","B1_speed_to_revenue":"Скорость до первого дохода",
      "B2_reg_access":"Регуляторный доступ","B3_fin_expertise":"Финансовая экспертиза",
      "B4_deal_capital":"Доступ к сделкам и капиталу","B5_family_industry":"Отраслевой доступ (семья/друзья)",
      "B6_team_sales":"Команда закрывает продажи","B7_style_fit":"Соответствие стилю"}

assert abs(sum(WA.values())-1)<1e-9 and abs(sum(WB.values())-1)<1e-9

def axis(scores, w):
    return sum(scores[k]*w[k] for k in w)

def score_idea(passes):
    """passes: список из 3 словарей {критерий: балл}. Возвращает сводку с разбросом."""
    assert len(passes)==3, "нужно ровно 3 прохода"
    out={"per_criterion":{}}
    for k in list(WA)+list(WB):
        v=np.array([p[k] for p in passes],dtype=float)
        out["per_criterion"][k]={"p1":float(v[0]),"p2":float(v[1]),"p3":float(v[2]),
            "mean":float(v.mean()),"min":float(v.min()),"max":float(v.max()),
            "range":float(v.max()-v.min()),"sd":float(v.std(ddof=1))}
    A=[axis(p,WA) for p in passes]; B=[axis(p,WB) for p in passes]
    T=[AXIS_W["A"]*a+AXIS_W["B"]*b for a,b in zip(A,B)]
    agg=lambda v:{"p1":round(v[0],3),"p2":round(v[1],3),"p3":round(v[2],3),
                  "mean":round(float(np.mean(v)),3),"min":round(float(np.min(v)),3),
                  "max":round(float(np.max(v)),3),"range":round(float(np.max(v)-np.min(v)),3),
                  "sd":round(float(np.std(v,ddof=1)),3)}
    out["A"]=agg(A); out["B"]=agg(B); out["total"]=agg(T)
    out["cell"]=nine_box(np.mean(A),np.mean(B))
    return out

def band(x):
    return "низкая" if x<4.34 else ("средняя" if x<6.67 else "высокая")

def nine_box(a,b):
    ba,bb=band(a),band(b)
    grow={("высокая","высокая"),("высокая","средняя"),("средняя","высокая")}
    harv={("низкая","низкая"),("низкая","средняя"),("средняя","низкая")}
    zone="Инвестировать/расти" if (ba,bb) in grow else ("Уходить/не входить" if (ba,bb) in harv else "Избирательно")
    return {"A_band":ba,"B_band":bb,"zone":zone}
