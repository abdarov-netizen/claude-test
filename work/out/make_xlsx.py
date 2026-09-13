# -*- coding: utf-8 -*-
import json, os, re, glob
import xlsxwriter

BASE="/home/user/claude-test/work"
OUT="/home/user/claude-test/Узбекистан_выбор_бизнеса.xlsx"
reg   = json.load(open(f"{BASE}/state/10_registry.json",encoding="utf-8"))
screen= json.load(open(f"{BASE}/state/20_screen.json",encoding="utf-8"))
scores= json.load(open(f"{BASE}/state/21_scores.json",encoding="utf-8"))
sims  = {os.path.basename(p)[4:-5]: json.load(open(p,encoding="utf-8"))
         for p in glob.glob(f"{BASE}/sim/results/sim_*.json")}
tor   = json.load(open(f"{BASE}/sim/results/tornado_FIN-11.json",encoding="utf-8"))

def clean(s, n=None):
    if not s: return ""
    s=re.sub(r'\*\*|\*|`','',re.sub(r'\s+',' ',str(s))).strip()
    return s if (n is None or len(s)<=n) else s[:n-1]+"…"

wb=xlsxwriter.Workbook(OUT,{"nan_inf_to_errors":True})
F={
 "t":wb.add_format({"bold":True,"font_size":16,"font_color":"#1F3864"}),
 "t2":wb.add_format({"bold":True,"font_size":12,"font_color":"#1F3864"}),
 "h":wb.add_format({"bold":True,"bg_color":"#1F3864","font_color":"white","border":1,
                    "text_wrap":True,"valign":"vcenter","align":"center"}),
 "sub":wb.add_format({"bold":True,"bg_color":"#D9E2F3","border":1,"text_wrap":True,"valign":"top"}),
 "x":wb.add_format({"border":1,"text_wrap":True,"valign":"top"}),
 "xb":wb.add_format({"border":1,"text_wrap":True,"valign":"top","bold":True}),
 "n":wb.add_format({"border":1,"num_format":"#,##0"}),
 "n2":wb.add_format({"border":1,"num_format":"0.00"}),
 "n1":wb.add_format({"border":1,"num_format":"0.0"}),
 "usd":wb.add_format({"border":1,"num_format":"$#,##0;[Red]-$#,##0"}),
 "pct":wb.add_format({"border":1,"num_format":"0.0%"}),
 "good":wb.add_format({"border":1,"num_format":"0.00","bg_color":"#C6EFCE"}),
 "warn":wb.add_format({"border":1,"num_format":"0.00","bg_color":"#FFEB9C"}),
 "bad":wb.add_format({"border":1,"num_format":"0.00","bg_color":"#FFC7CE"}),
 "note":wb.add_format({"italic":True,"font_color":"#555555","text_wrap":True,"valign":"top"}),
 "wrap":wb.add_format({"text_wrap":True,"valign":"top"}),
}
def hdr(ws,row,cols,widths):
    for c,(h,w) in enumerate(zip(cols,widths)):
        ws.write(row,c,h,F["h"]); ws.set_column(c,c,w)
    ws.set_row(row,34); ws.freeze_panes(row+1,0)
def band(v): return F["good"] if v>=6.67 else (F["warn"] if v>=4.34 else F["bad"])

# ───────────────────────── 01 РЕЗЮМЕ
ws=wb.add_worksheet("01 Резюме"); ws.set_column(0,0,3); ws.set_column(1,1,46); ws.set_column(2,2,86)
ws.write(0,1,"Какой бизнес строить в Узбекистане — ФИНАЛЬНЫЕ ВЫВОДЫ",F["t"])
r=2
rows=[
("КОРОТКИЙ ОТВЕТ","Ни один из проверенных бизнесов не обыгрывает вашу текущую работу, если считать честно. Это не уклонение, а следствие барьера, который вы задали: депозит 19.7% плюс ваша зарплата $4 000/мес = $240 тыс. упущенного за пять лет."),
("ЧТО ДЕЛАТЬ","НЕ УВОЛЬНЯТЬСЯ. Запускать параллельно работе. Лучший из проверенных — страховой брокер спецлиний: ожидаемый NPV $199 тыс. до вычета зарплаты и около нуля после."),
("ПЕРВЫЙ ОТВЕТ РАЗВАЛИЛСЯ","Побеждала исламская финансовая практика ($345 тыс.). Приказ ЦБ (Минюст, 17.07.2026) требует для 3 обязательных кресел, включая главу и зама, высшего ИСЛАМОВЕДЧЕСКОГО образования, 5 лет шариатского права и арабского. Финансист туда не проходит. После сведения: -$31 тыс."),
("ПОЧЕМУ БРОКЕР","Спрос идёт ОТ КРЕДИТОРА: банк под эскроу требует покрытия строймонтажных рисков. Комиссия 10-20% от премии, возобновление ежегодное, капзатрат почти нет. И главное — брокерская книга ОТЧУЖДАЕМА, её можно продать."),
("ГЛАВНЫЙ РЫЧАГ","Стоимость привлечения клиента (размах $503 тыс.) и средняя комиссия ($446 тыс.). Задержка запуска на третьем месте ($239 тыс.) — время дороже, чем кажется."),
("ЗАКОНОМЕРНОСТЬ","У ВСЕХ кандидатов медиана отрицательная, а матожидание положительное. Ни один не является надёжно прибыльным: все они опционы, где деньги делает правый хвост, а типичный исход неудачный."),
("ВОРОТА ПО ВЫХОДУ","Вы просили и поток, И ОПЦИОН НА ВЫХОД, но выход весил лишь 5.6%. С воротами (выход не ниже 5/10) прошли 3 идеи из 17: C&I-энергетика, страховой брокер, контрактное производство медизделий. Все консультационные практики отсеялись — их нельзя продать."),
("ОШИБКА В МОЕЙ МЕТОДОЛОГИИ","Протокол «три независимых прохода» оказался самообманом: скептик был ниже базы в 100% из 238 ячеек, арбитр — ровно посередине в 74%, ранговая корреляция 0.98. Разброс измерял размер моей скидки, а не разногласие."),
("НАСТОЯЩИЙ ФИЛЬТР","Не рынок, а размер вашего кошелька. Идеи с сильнейшим рынком (холодовая цепь, C&I-энергетика, медизделия) требуют $1.5-6 млн и с $150 тыс. недоступны напрямую."),
("НЕУДОБНЫЙ ВОПРОС","Один success fee 1% по сделке на $50 млн = $500 тыс. — больше, чем весь пятилетний NPV любого из проверенных бизнесов. Вы хотите построить бизнес или заработать денег? Это разные задачи."),
("ПРОВЕРИТЬ ДО ТРАТ","(1) сроки и стоимость брокерской лицензии; (2) признаёт ли ЦБ ваш CPSS для 4-5 кресла; (3) разрешена ли прямая продажа электроэнергии «за счётчиком»."),
]
for k,v in rows:
    ws.write(r,1,k,F["xb"]); ws.write(r,2,v,F["x"]); ws.set_row(r,44); r+=1
r+=1
ws.write(r,1,"КАК ЧИТАТЬ ЭТУ КНИГУ",F["t2"]); r+=1
for k,v in [
 ("02 Реестр идей","Все 103 идеи с NABC, аналогом, окном и конкурентами."),
 ("03 Веса","Веса осей, зафиксированные ДО скоринга. Суммы обеих осей = 1.000."),
 ("04 Первичный отсев","Быстрые оценки всех 103 идей с обоснованием одной строкой."),
 ("05 Скоринг 3 прохода","Покритериально: база / скептик / арбитр, разброс и ст.откл."),
 ("06 Свод и матрица","Итоговые оси и положение в матрице девяти клеток."),
 ("07 Монте-Карло","5 сценариев на идею, 20 000 прогонов каждый."),
 ("08 Помесячная модель","60 месяцев по победителю: квартили выручки, EBITDA, кассы."),
 ("09 Распределение NPV","Перцентили и гистограмма исходов."),
 ("10 Чувствительность","Торнадо: что двигает результат сильнее всего."),
 ("11 Критика","Что нашли круги критики и что из-за этого изменилось."),
 ("12 Достоверность","Уровни достоверности фактов и что обязательно проверить у юриста."),
]:
    ws.write(r,1,k,F["xb"]); ws.write(r,2,v,F["x"]); r+=1

# ───────────────────────── 02 РЕЕСТР
ws=wb.add_worksheet("02 Реестр идей")
cols=["ID","Название","Арена","Суть","Кто платит","Модель дохода и чек","N — потребность",
      "A — подход","B — выгода","C — конкуренты и почему свободно","Доказанный аналог",
      "Структурное окно","Стартовый капитал","Лицензии","Риск №1"]
hdr(ws,0,cols,[9,34,18,52,30,34,46,46,40,52,40,46,20,26,34])
for i,d in enumerate(reg,1):
    for c,k in enumerate(["id","name","arena","essence","payer","revenue_model","need","approach",
                          "benefit","competition","analog","window","capital","license","risk1"]):
        ws.write(i,c,clean(d.get(k),900),F["x"])
ws.autofilter(0,0,len(reg),len(cols)-1)

# ───────────────────────── 03 ВЕСА
ws=wb.add_worksheet("03 Веса"); ws.set_column(0,0,3)
ws.write(0,1,"Веса зафиксированы ДО генерации идей и до присвоения любых баллов",F["t"])
ws.write(1,1,"Файл-первоисточник: work/state/02_weights_LOCKED.md. Подгонка весов после просмотра "
             "результатов превратила бы скоринг в оформление уже принятого решения.",F["note"])
hdr(ws,3,["Ось","Критерий","Вес в оси","Вес в итоге"],[34,46,12,12])
r=4; AW=0.70; BW=0.30
from collections import OrderedDict
WA=OrderedDict([("Экономика отрасли",0.24),("Размер рынка снизу вверх",0.18),
 ("Окно «почему сейчас»",0.15),("Свободное место",0.13),("Барьеры в нашу пользу",0.12),
 ("Готовность платить",0.10),("Потенциал выхода",0.08)])
WB_=OrderedDict([("Скорость до первого дохода",0.20),("Регуляторный доступ",0.16),
 ("Финансовая экспертиза",0.15),("Доступ к сделкам и капиталу",0.15),
 ("Отраслевой доступ через семью и друзей",0.13),("Команда закрывает продажи",0.12),
 ("Соответствие стилю",0.09)])
for axis,W,aw in [("A — привлекательность рынка (70%)",WA,AW),("B — моя позиция (30%)",WB_,BW)]:
    for k,v in W.items():
        ws.write(r,1,axis,F["x"]); ws.write(r,2,k,F["x"])
        ws.write(r,3,v,F["pct"]); ws.write(r,4,v*aw,F["pct"]); r+=1
    ws.write(r,2,"СУММА",F["xb"]); ws.write(r,3,sum(W.values()),F["pct"]); r+=2

# ───────────────────────── 04 ОТСЕВ
ws=wb.add_worksheet("04 Первичный отсев")
hdr(ws,0,["ID","Название","A (рынок)","B (позиция)","Быстрый итог","В лонг-листе",
          "Обоснование одной строкой"],[9,40,11,12,13,13,96])
names={d["id"]:d["name"] for d in reg}
sc=screen["screen"]; ll=set(screen["longlist"]); mg=screen["merged"]
rows=sorted(sc.items(), key=lambda kv:-(0.7*kv[1]["A"]+0.3*kv[1]["B"]))
for i,(iid,v) in enumerate(rows,1):
    tot=0.7*v["A"]+0.3*v["B"]
    ws.write(i,0,iid,F["x"]); ws.write(i,1,clean(names.get(iid,""),90),F["x"])
    ws.write(i,2,v["A"],band(v["A"])); ws.write(i,3,v["B"],band(v["B"]))
    ws.write(i,4,tot,band(tot))
    ws.write(i,5,"слит с "+mg[iid] if iid in mg else ("ДА" if iid in ll else ""),F["x"])
    ws.write(i,6,clean(v["note"],400),F["x"])
ws.autofilter(0,0,len(rows),6)

# ───────────────────────── 05 СКОРИНГ 3 ПРОХОДА
ws=wb.add_worksheet("05 Скоринг 3 прохода")
ws.write(0,0,"Три независимых прохода: P1 «база», P2 «скептик» (ищет завышения), "
             "P3 «арбитр» (перечитывает свидетельства заново с учётом круга критики)",F["note"])
ws.set_row(0,28)
hdr(ws,1,["ID","Идея","Критерий","Вес","P1 база","P2 скептик","P3 арбитр","Среднее",
          "Мин","Макс","Размах","Ст.откл"],[9,34,38,8,9,11,11,10,8,8,10,10])
RU={"A1_economics":"A1 Экономика отрасли","A2_market_size":"A2 Размер рынка снизу вверх",
 "A3_why_now":"A3 Окно «почему сейчас»","A4_white_space":"A4 Свободное место",
 "A5_barriers_for_us":"A5 Барьеры в нашу пользу","A6_wtp":"A6 Готовность платить",
 "A7_exit":"A7 Потенциал выхода","B1_speed_to_revenue":"B1 Скорость до первого дохода",
 "B2_reg_access":"B2 Регуляторный доступ","B3_fin_expertise":"B3 Финансовая экспертиза",
 "B4_deal_capital":"B4 Доступ к сделкам и капиталу","B5_family_industry":"B5 Отраслевой доступ",
 "B6_team_sales":"B6 Команда закрывает продажи","B7_style_fit":"B7 Соответствие стилю"}
WT={**{f"A{i}_{k}":v for (i,k),v in zip(
     [(1,"economics"),(2,"market_size"),(3,"why_now"),(4,"white_space"),
      (5,"barriers_for_us"),(6,"wtp"),(7,"exit")],[.24,.18,.15,.13,.12,.10,.08])},
    **{f"B{i}_{k}":v for (i,k),v in zip(
     [(1,"speed_to_revenue"),(2,"reg_access"),(3,"fin_expertise"),(4,"deal_capital"),
      (5,"family_industry"),(6,"team_sales"),(7,"style_fit")],[.20,.16,.15,.15,.13,.12,.09])}}
r=2
order=sorted(scores.items(), key=lambda kv:-kv[1]["total"]["mean"])
for iid,d in order:
    for k,v in d["per_criterion"].items():
        ws.write(r,0,iid,F["x"]); ws.write(r,1,clean(d["name"],60),F["x"])
        ws.write(r,2,RU.get(k,k),F["x"]); ws.write(r,3,WT.get(k,0),F["pct"])
        for c,key in enumerate(["p1","p2","p3","mean","min","max","range","sd"],start=4):
            ws.write(r,c,v[key],band(v[key]) if key in("p1","p2","p3","mean") else F["n2"])
        r+=1
    for lbl,key in [("ИТОГ ОСЬ A","A"),("ИТОГ ОСЬ B","B"),("ИТОГО 0.7A+0.3B","total")]:
        t=d[key]
        ws.write(r,0,iid,F["xb"]); ws.write(r,1,clean(d["name"],60),F["xb"])
        ws.write(r,2,lbl,F["xb"]); ws.write(r,3,"",F["xb"])
        for c,kk in enumerate(["p1","p2","p3","mean","min","max","range","sd"],start=4):
            ws.write(r,c,t[kk],F["sub"])
        r+=1
    r+=1
ws.autofilter(1,0,r-1,11)

# ───────────────────────── 06 СВОД И МАТРИЦА
ws=wb.add_worksheet("06 Свод и матрица")
hdr(ws,0,["#","ID","Идея","Ось A","Ось B","ИТОГО","Размах итога","Ст.откл",
          "Полоса A","Полоса B","Клетка матрицы"],[5,10,52,10,10,10,13,10,12,12,24])
for i,(iid,d) in enumerate(order,1):
    ws.write(i,0,i,F["n"]); ws.write(i,1,iid,F["x"]); ws.write(i,2,clean(d["name"],95),F["x"])
    ws.write(i,3,d["A"]["mean"],band(d["A"]["mean"])); ws.write(i,4,d["B"]["mean"],band(d["B"]["mean"]))
    ws.write(i,5,d["total"]["mean"],band(d["total"]["mean"]))
    ws.write(i,6,d["total"]["range"],F["n2"]); ws.write(i,7,d["total"]["sd"],F["n2"])
    ws.write(i,8,d["cell"]["A_band"],F["x"]); ws.write(i,9,d["cell"]["B_band"],F["x"])
    ws.write(i,10,d["cell"]["zone"],F["x"])
r=len(order)+3
ws.write(r,0,"МАТРИЦА ДЕВЯТИ КЛЕТОК (по строкам — привлекательность рынка, по столбцам — моя позиция)",F["t2"]); r+=1
grid={}
for iid,d in order: grid.setdefault((d["cell"]["A_band"],d["cell"]["B_band"]),[]).append(iid)
bands=["высокая","средняя","низкая"]
ws.write(r,1,"",F["h"])
for c,b in enumerate(bands): ws.write(r,2+c,f"Позиция: {b}",F["h"])
r+=1
for a in bands:
    ws.write(r,1,f"Рынок: {a}",F["h"])
    for c,b in enumerate(bands):
        ws.write(r,2+c,", ".join(grid.get((a,b),[])) or "—",F["x"])
    ws.set_row(r,40); r+=1
ws.write(r+1,1,"Границы полос: низкая 1.00-4.33, средняя 4.34-6.66, высокая 6.67-10.00",F["note"])

# ───────────────────────── 06б ПЕРЕСЧЁТ И ВОРОТА
rs=json.load(open(f"{BASE}/state/23_rescored.json",encoding="utf-8"))
ws=wb.add_worksheet("06б Пересчёт и ворота")
ws.write(0,0,"Две методологические поправки, принятые от критики: (1) критерий A5 «барьеры в НАШУ "
             "пользу» — это ось позиции, а не привлекательности отрасли, поэтому перенесён на ось B "
             "(иначе про основателя весило 38.4%, а не заявленные 30%); (2) «потенциал выхода» весил "
             "лишь 5.6%, хотя заказчик просил опцион на выход — добавлены ВОРОТА: минимум 5 из 10.",F["note"])
ws.set_row(0,56)
hdr(ws,1,["Новое место","Старое место","Итог после переноса A5","Потенциал выхода (A7)",
          "Ворота по выходу","ID","Идея"],[12,13,20,20,16,10,56])
for i,r in enumerate(rs["ranking"],start=2):
    ws.write(i,0,i-1,F["n"]); ws.write(i,1,"",F["x"])
    ws.write(i,2,r["total_new"],band(r["total_new"]))
    ws.write(i,3,r["A7"],band(r["A7"]))
    ws.write(i,4,"ПРОШЁЛ" if r["gate_passed"] else "отсеян",
             F["good"] if r["gate_passed"] else F["bad"])
    ws.write(i,5,r["id"],F["x"]); ws.write(i,6,clean(r["name"],95),F["x"])

# ───────────────────────── 07 МОНТЕ-КАРЛО
SCRU={"base":"База","opportunity_cost":"Минус ваша зарплата $4 000/мес",
      "devaluation":"Девальвация сума 8%/год","hard_competition":"Жёсткая конкуренция",
      "slow_window":"Окно открывается медленно"}
ws=wb.add_worksheet("07 Монте-Карло")
ws.write(0,0,"20 000 прогонов на сценарий, помесячно, 60 месяцев. Ставка дисконтирования 19.7% "
             "= доходность сумового депозита. Поэтому NPV > 0 буквально означает «обогнали депозит».",F["note"])
ws.set_row(0,28)
hdr(ws,1,["ID","Идея","Сценарий","Выживание 60 мес","Ожидаемый NPV","Медиана NPV",
          "NPV | выжил","P(NPV>0)","NPV p5","NPV p25","NPV p75","NPV p95",
          "Убыток при провале","Неплатёжеспособность","Закрылся сам","Не запустился",
          "Пик капитала (сред.)","Пик капитала p90","Выручка год 5 (мед., выжившие)"],
    [10,40,30,15,15,15,15,10,13,13,13,13,16,16,13,14,17,16,20])
r=2
for iid in ["FIN-11","BOUTIQUE-balanced","BOUTIQUE","FIN-19","FIN-01+","FIN-01-FINAL","FIN-01-balanced","FIN-01-solo","FIN-01-recon","IND-01","MED-12","PRO-22","PRO-22-lean"]:
    if iid not in sims: continue
    d=sims[iid]
    for scn,v in d["scenarios"].items():
        ws.write(r,0,iid,F["x"]); ws.write(r,1,clean(d["name"],70),F["x"])
        ws.write(r,2,SCRU.get(scn,scn),F["x"])
        ws.write(r,3,v["P_survive_60m"],F["pct"])
        for c,k in enumerate(["E_NPV","median_NPV","E_NPV_given_survive"],start=4):
            ws.write(r,c,v[k],F["usd"])
        ws.write(r,7,v["P_NPV_gt_0"],F["pct"])
        for c,k in enumerate(["NPV_p5","NPV_p25","NPV_p75","NPV_p95","E_loss_given_fail"],start=8):
            ws.write(r,c,v[k],F["usd"])
        for c,k in enumerate(["P_insolvency","P_voluntary_close","P_fail_to_launch"],start=13):
            ws.write(r,c,v[k],F["pct"])
        ws.write(r,16,v["E_peak_capital"],F["usd"]); ws.write(r,17,v["p90_peak_capital"],F["usd"])
        ws.write(r,18,v["median_rev_ttm_y5_alive"],F["usd"])
        r+=1
    r+=1

# ───────────────────────── 08 ПОМЕСЯЧНАЯ МОДЕЛЬ
win="FIN-11"
ws=wb.add_worksheet("08 Помесячная модель")
ws.write(0,0,f"Помесячная траектория по победителю ({win}), базовый сценарий. "
             "Показаны квартили ПО ВЫЖИВШИМ на каждый месяц плюс доля выживших.",F["note"])
hdr(ws,1,["Месяц","Доля живых","Клиентов (мед.)","Выручка p25","Выручка медиана","Выручка p75",
          "EBITDA p25","EBITDA медиана","EBITDA p75","Касса медиана","Сотрудников (мед.)",
          "Вложено капитала (мед.)","Налоги (мед.)"],[8,11,15,13,15,13,13,15,13,14,16,19,13])
path=sims[win]["monthly_path_base"]
for i,row in enumerate(path,start=2):
    ws.write(i,0,row["month"],F["n"]); ws.write(i,1,row["P_alive"],F["pct"])
    ws.write(i,2,row["clients_med"],F["n1"])
    for c,k in enumerate(["revenue_p25","revenue_med","revenue_p75","ebitda_p25","ebitda_med",
                          "ebitda_p75","cash_med"],start=3):
        ws.write(i,c,row[k],F["usd"])
    ws.write(i,10,row["fte_med"],F["n1"])
    ws.write(i,11,row["injected_med"],F["usd"]); ws.write(i,12,row["tax_med"],F["usd"])
ch=wb.add_chart({"type":"line"}); n=len(path)
for col,name,clr in [(4,"Выручка, медиана","#1F3864"),(7,"EBITDA, медиана","#2E7D32")]:
    ch.add_series({"name":name,"categories":["08 Помесячная модель",2,0,n+1,0],
                   "values":["08 Помесячная модель",2,col,n+1,col],
                   "line":{"color":clr,"width":2.0}})
ch.set_title({"name":"Выручка и EBITDA по месяцам (медиана выживших)"})
ch.set_x_axis({"name":"Месяц"}); ch.set_y_axis({"name":"USD в месяц"})
ch.set_size({"width":820,"height":400})
ws.insert_chart("O3",ch)
ch2=wb.add_chart({"type":"line"})
ch2.add_series({"name":"Доля выживших","categories":["08 Помесячная модель",2,0,n+1,0],
                "values":["08 Помесячная модель",2,1,n+1,1],"line":{"color":"#B71C1C","width":2.0}})
ch2.set_title({"name":"Доля выживших по месяцам"}); ch2.set_x_axis({"name":"Месяц"})
ch2.set_y_axis({"name":"Доля","max":1}); ch2.set_size({"width":820,"height":330})
ws.insert_chart("O25",ch2)

# ───────────────────────── 09 РАСПРЕДЕЛЕНИЕ NPV
ws=wb.add_worksheet("09 Распределение NPV")
ws.write(0,0,f"Распределение NPV по 20 000 прогонов, {win}, базовый сценарий. "
             "Матожидание выше медианы — прибыль создаёт правый хвост, а не типичный исход.",F["note"])
b=sims[win]["scenarios"]["base"]
hdr(ws,1,["Перцентиль","NPV, USD"],[14,18])
for i,(p,v) in enumerate(zip(range(5,100,5), b["npv_deciles"]),start=2):
    ws.write(i,0,p/100,F["pct"]); ws.write(i,1,v,F["usd"])
r0=2+len(b["npv_deciles"])+2
ws.write(r0-1,0,"Гистограмма исходов (значения обрезаны диапазоном -$300 тыс. … $4 млн)",F["t2"])
hdr(ws,r0,["Центр корзины, USD","Число прогонов"],[20,16])
edges=b["hist_edges"]; hist=b["hist"]
for i,(cnt,lo,hi) in enumerate(zip(hist,edges[:-1],edges[1:]),start=r0+1):
    ws.write(i,0,(lo+hi)/2,F["usd"]); ws.write(i,1,cnt,F["n"])
chh=wb.add_chart({"type":"column"})
chh.add_series({"name":"Число прогонов",
    "categories":["09 Распределение NPV",r0+1,0,r0+len(hist),0],
    "values":["09 Распределение NPV",r0+1,1,r0+len(hist),1],
    "fill":{"color":"#1F3864"},"gap":8})
chh.set_title({"name":"Распределение NPV, 20 000 прогонов"})
chh.set_x_axis({"name":"NPV, USD"}); chh.set_y_axis({"name":"Число прогонов"})
chh.set_legend({"none":True}); chh.set_size({"width":900,"height":420})
ws.insert_chart("E3",chh)

# ───────────────────────── 10 ЧУВСТВИТЕЛЬНОСТЬ
ws=wb.add_worksheet("10 Чувствительность")
ws.write(0,0,f"Торнадо по победителю. База: ожидаемый NPV ${tor['base_E_NPV']:,.0f}. "
             "Каждый параметр сдвинут в плохую и хорошую сторону, остальные на месте.",F["note"])
hdr(ws,1,["Параметр","NPV при плохом значении","NPV при хорошем значении","Размах",
          "Отклонение вниз","Отклонение вверх"],[42,24,25,16,18,18])
for i,t in enumerate(tor["tornado"],start=2):
    ws.write(i,0,t["param"],F["x"])
    for c,k in enumerate(["low","high","span","d_low","d_high"],start=1):
        ws.write(i,c,t[k],F["usd"])
cht=wb.add_chart({"type":"bar"}); m=len(tor["tornado"])
cht.add_series({"name":"Размах ожидаемого NPV",
   "categories":["10 Чувствительность",2,0,m+1,0],
   "values":["10 Чувствительность",2,3,m+1,3],"fill":{"color":"#1F3864"}})
cht.set_title({"name":"Что двигает ожидаемый NPV сильнее всего"})
cht.set_x_axis({"name":"Размах NPV, USD"}); cht.set_legend({"none":True})
cht.set_size({"width":860,"height":460}); ws.insert_chart("H3",cht)

# ───────────────────────── 11 КРИТИКА
ws=wb.add_worksheet("11 Критика"); ws.set_column(0,0,3); ws.set_column(1,1,26); ws.set_column(2,2,120)
ws.write(0,1,"Круги критики и что из-за них изменилось",F["t"])
r=2
crit_files=[("Круг 1. Полевая проверка ниш","work/critique/K1_поле_итог.md"),
            ("Круг 2. Аудитор допущений","work/critique/K2_аудитор.md"),
            ("Круг 2б. Защита","work/critique/K2b_защита.md"),
            ("Круг 3. Критика модели","work/critique/K3_модель.md"),
            ("Внешний критик","work/critique/K4_внешний.md")]
import os as _os
for title,f in crit_files:
    full=f"/home/user/claude-test/{f}"
    ws.write(r,1,title,F["t2"]); r+=1
    if _os.path.exists(full):
        for line in open(full,encoding="utf-8").read().split("\n"):
            if not line.strip(): continue
            ws.write(r,2,clean(line,600),F["wrap"]); r+=1
    else:
        ws.write(r,2,"(круг не завершён — файл отсутствует)",F["note"]); r+=1
    r+=1

# ───────────────────────── 12 ДОСТОВЕРНОСТЬ
ws=wb.add_worksheet("12 Достоверность"); ws.set_column(0,0,3)
ws.write(0,1,"Достоверность фактов и что обязательно проверить до вложения денег",F["t"])
ws.write(1,1,"ВАЖНО: сетевая политика среды не дала открыть первоисточники — lex.uz, сайты ЦБ, "
             "НАПП, Uzpharm Control, отчёты МВФ и АБР. Работал только веб-поиск, отдающий СВОДКИ, "
             "то есть источник вторичный. Поэтому у каждого факта проставлен уровень достоверности.",F["note"])
ws.set_row(1,44)
hdr(ws,3,["Уровень","Что он означает"],[12,110])
for i,(k,v) in enumerate([
 ("A","Несколько независимых сводок сходятся, назван номер документа и дата"),
 ("B","Одна сводка, реквизиты документа есть"),
 ("C","Одна сводка без реквизитов либо данные противоречат друг другу"),
 ("D","Оценка автора, первоисточник не проверялся")],start=4):
    ws.write(i,1,k,F["xb"]); ws.write(i,2,v,F["x"])
r=9
ws.write(r,1,"ОБЯЗАТЕЛЬНО ПРОВЕРИТЬ У ЮРИСТА ПО ОРИГИНАЛАМ ДОКУМЕНТОВ",F["t2"]); r+=1
hdr(ws,r,["Вопрос","Почему это решающее"],[60,86]); r+=1
for q,w in [
 ("Признаёт ли ЦБ РУз именно сертификат CPSS достаточным для членства в шариатском совете",
  "Вся рекомендация стоит на этом. Если нужен полный CSAA — сначала сдать модуль CPSAGE."),
 ("Есть ли лимит на число шариатских советов, в которых может состоять один человек",
  "В Малайзии такой лимит есть. Если он есть и в РУз — потолок выручки резко ниже модельного."),
 ("Требуется ли членам совета религиозное образование (фикх), а не экономическое",
  "Заказчик — финансист, не богослов. Если фикх обязателен — нужен партнёр-улем."),
 ("Точная дата и переходный период по эскроу в долевом строительстве",
  "Источники расходятся: 01.01.2026 против 01.07.2026. Из-за этого идея REA-01 упала с 1-го места."),
 ("Действующая редакция требований к «исламским окнам» и срок 01.07.2027",
  "Срок — главный двигатель спроса. Перенос срока сдвигает всю выручку вправо."),
 ("Налоговый режим практики: порог упрощёнки в сумах и момент перехода на общий режим",
  "В модели порог задан в долларах — это упрощение, реальный порог в сумах и индексируется."),
]:
    ws.write(r,1,q,F["x"]); ws.write(r,2,w,F["x"]); ws.set_row(r,32); r+=1

wb.close()
print("книга создана:",OUT, os.path.getsize(OUT),"байт")
