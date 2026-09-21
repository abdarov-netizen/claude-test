# -*- coding: utf-8 -*-
"""Конфигурации Монте-Карло для финалистов яруса 3.
Каждый параметр опирается на факт, установленный вебпроверкой (ярус 3) или базой фактов.
Где числа оценочные — так и помечено в поле _обоснование."""
import json, os
OUT='/home/user/claude-test/work/sim/configs'

def cfg(id, name, why, **kw):
    d={'id':id,'name':name,'_обоснование':why,
       'common_factor_strength':0.15,
       'market':{'tam_customers':[10,20,40],'max_capture_rate':0.05,'winback_share':0.5},
       'pricing':{'arpu_month':[3000,6000,12000],'price_escalation_annual':0.04},
       'funnel':{'opps_per_rep_month':[2.0,4.0,7.0],'win_rate':[0.10,0.20,0.32],
                 'cac0':[1500,4000,9000],'cac_growth_annual':0.12,'cac_penetration_k':1.2,
                 'start_reps':0,'max_reps':3,'founder_opps_month':[1.5,2.5,4.0],
                 'cac_growth_cap_years':3.0},
       'churn':{'monthly':[0.02,0.04,0.07],'drift_annual':0.0},
       'delivery':{'clients_per_fte':[2.0,3.5,6.0],'max_hires_per_month':1.0,
                   'fte_cost_month':[900,1500,2400],'ramp_months':2,'start_fte':0,
                   'max_fte':20,'founder_capacity_clients':[1.0,2.0,3.0]},
       'costs':{'fixed_opex_month':[1200,2500,4500],'gross_margin':[0.55,0.70,0.82],
                'mkt_budget_share_of_rev':0.06,'mkt_budget_floor':600,
                'startup_capex':[5000,15000,35000],'cost_inflation_annual':0.06},
       'wc':{'dso_days':[30,50,80],'dpo_days':30,'prepay_share':0.1},
       'tax':{'regime':'general','turnover_rate':0.04,'profit_rate':0.15,'vat_rate':0.12,
              'social_tax':0.12,'vat_passthrough_b2b':True,'turnover_regime_cap_usd_year':80000},
       'competition':{'p_competitor_at_start':0.6,'entry_hazard_month':0.02,
                      'price_impact':0.12,'churn_impact_abs':0.004,'winrate_impact':0.25},
       'exit':{'ebitda_multiple':[3.0,5.0,7.0],'prob_exit_market':0.45,'hold_multiple_factor':0.7},
       'capital':{'owner_capital':150000,'cash_buffer_months':3,'prefund_months':2,
                  'capex_recovery_share':0.3,'debt_share_of_capex':0.0,
                  'debt_rate_annual':0.20,'debt_term_months':60,'debt_grace_months':6},
       'abandon':{'check_month':24,'min_monthly_revenue':[4000,9000,16000],'salvage_share_of_wc':0.8},
       'launch':{'delay_months':[1,3,6],'p_fail_to_launch':0.10,'p_no_demand':0.15,
                 'no_demand_winrate_factor':0.2,'no_demand_tam_factor':0.3},
       'fx':{'uzs_vs_usd_annual_drift':-0.05,'annual_vol':0.08,
             'usd_revenue_share':0.1,'usd_cost_share':0.25}}
    for k,v in kw.items():
        if isinstance(v,dict): d[k].update(v)
        else: d[k]=v
    return d

C=[]

C.append(cfg('F1-REA-02','Брокер проектного финансирования для застройщиков под эскроу',
 'Ярус 3 место 1 (7.54). ФАКТЫ: эскроу в долевом строительстве фактически стартовало 01.07.2026 и ТОЛЬКО для новых проектов, то есть поток нарастает медленно; Ipoteka Bank уже продаёт «проектное финансирование с эскроу» сам; Минстрой с ЦБ отправляет сотрудников банков на зарубежные стажировки по проектному финансированию — окно посредника КОНЕЧНО (A5=4). Застройщик потерял бесплатные деньги дольщиков и вынужден идти в банк. Мандатная модель: ретейнер плюс успех. Капзатрат нет. Оценки чеков и числа застройщиков — оценочные.',
 market={'tam_customers':[35,80,160],'max_capture_rate':0.06,'winback_share':0.85},
 pricing={'arpu_month':[8000,15000,26000]},
 churn={'monthly':[0.08,0.13,0.20]},
 funnel={'win_rate':[0.12,0.22,0.35],'cac0':[1200,3000,7000],'founder_opps_month':[2.0,3.5,5.5]},
 delivery={'clients_per_fte':[1.5,2.5,4.0],'fte_cost_month':[1500,2600,4200],
           'founder_capacity_clients':[1.0,2.0,3.0],'max_fte':8},
 costs={'fixed_opex_month':[1500,3000,5500],'gross_margin':[0.62,0.75,0.86],
        'startup_capex':[3000,9000,20000]},
 competition={'p_competitor_at_start':0.85,'entry_hazard_month':0.035,'winrate_impact':0.3},
 exit={'ebitda_multiple':[2.0,3.5,5.0],'prob_exit_market':0.30},
 launch={'delay_months':[0,2,4],'p_fail_to_launch':0.08,'p_no_demand':0.18}))

C.append(cfg('F2-BAL-31','Бридж и мезонин под приватизационные и M&A-сделки',
 'Ярус 3 место 2 (7.40). ФАКТЫ: УП-177 от 28.08.2026 — 84 хозобщества, 1 242 объекта, ~8 000 га, свыше $8 млрд, план 14 трлн сум до конца 2026. ОГРАНИЧЕНИЯ: систематическая выдача займов — ЛИЦЕНЗИРУЕМАЯ деятельность (закон о небанковских кредитных организациях, ред. 21.04.2026), отсюда задержка старта; «золотая акция» государства (08.09.2026) снижает цену выхода для покупателей активов и значит спрос на бридж. Балансовый бизнес: свои $150 тыс. как доля в капитале, остальное — соинвесторы и долг. Ставки бриджа 22-30% годовых — оценка.',
 market={'tam_customers':[18,45,85],'max_capture_rate':0.07,'winback_share':0.7},
 pricing={'arpu_month':[12000,24000,45000]},
 churn={'monthly':[0.06,0.10,0.16]},
 funnel={'win_rate':[0.14,0.25,0.40],'cac0':[2000,5000,11000],'founder_opps_month':[2.0,3.5,5.0]},
 delivery={'clients_per_fte':[2.0,3.5,5.0],'fte_cost_month':[1800,3000,4800],
           'founder_capacity_clients':[1.5,2.5,4.0],'max_fte':6},
 costs={'fixed_opex_month':[2000,3800,6500],'gross_margin':[0.50,0.65,0.78],
        'startup_capex':[400000,900000,1800000]},
 capital={'debt_share_of_capex':0.75,'debt_rate_annual':0.19,'debt_term_months':60,
          'debt_grace_months':6,'capex_recovery_share':0.75,'prefund_months':3},
 wc={'dso_days':[15,30,55],'prepay_share':0.15},
 competition={'p_competitor_at_start':0.55,'entry_hazard_month':0.025},
 exit={'ebitda_multiple':[3.0,5.0,7.5],'prob_exit_market':0.45},
 launch={'delay_months':[3,6,11],'p_fail_to_launch':0.14,'p_no_demand':0.20}))

C.append(cfg('F3-SOLAR','C&I солнце «за забором» плюс накопители по PPA (AST-22 + IND-01)',
 'Ярус 3 места 3-4 (обе 7.08), объединены: это одна бизнес-модель. ФАКТЫ: лицензия НЕ нужна для генерации до 5 МВт, станции в замысле 0.5-3 МВт; тарифы по звеньям впервые раскрыты 08.08.2026, экономика PPA стала считаемой; 4 000 аварий в сетях за июнь-июль как продающий аргумент. ПРОТИВ: 20+ локальных EPC, JinkoSolar подписала на Power Uzbekistan 2026 рамочные соглашения на 1 ГВт с четырьмя местными дистрибьюторами; сильнейший заменитель — при дешёвой панели и льготном кредите предприятию проще купить станцию себе. Капиталоёмко, но проектный долг доступен через зелёные линии ЕБРР/АБР. Выручка PPA законтрактована на 10-15 лет — отсюда низкий отток.',
 market={'tam_customers':[55,140,290],'max_capture_rate':0.035,'winback_share':0.3},
 pricing={'arpu_month':[6000,12000,22000],'price_escalation_annual':0.03},
 churn={'monthly':[0.002,0.005,0.012]},
 funnel={'win_rate':[0.06,0.13,0.24],'cac0':[4000,10000,22000],'founder_opps_month':[1.0,2.0,3.5]},
 delivery={'clients_per_fte':[2.5,4.5,7.0],'fte_cost_month':[1200,2000,3200],
           'ramp_months':3,'max_fte':14},
 costs={'fixed_opex_month':[2500,4500,8000],'gross_margin':[0.55,0.70,0.82],
        'startup_capex':[700000,1400000,2500000]},
 capital={'debt_share_of_capex':0.70,'debt_rate_annual':0.16,'debt_term_months':84,
          'debt_grace_months':9,'capex_recovery_share':0.55,'prefund_months':3},
 wc={'dso_days':[30,45,70],'dpo_days':45},
 competition={'p_competitor_at_start':0.80,'entry_hazard_month':0.03,'winrate_impact':0.3},
 exit={'ebitda_multiple':[6.0,9.0,13.0],'prob_exit_market':0.60,'hold_multiple_factor':0.8},
 abandon={'check_month':30,'min_monthly_revenue':[8000,16000,28000]},
 launch={'delay_months':[7,12,20],'p_fail_to_launch':0.20,'p_no_demand':0.25}))

C.append(cfg('F4-TRD-117','Эксклюзив на лабораторное и аналитическое оборудование под обязательный GMP',
 'Ярус 3 место 5 (6.99), B5=10 — заводы отца первый клиент и референс. ФАКТЫ: 82 местных производителя ЛС, GMP внедрён лишь на 40 (147 линий), то есть ~42 завода обязаны дооснаститься К 01.01.2027 — жёсткая дата в трёх месяцах; АРФО компенсирует заводам затраты, то есть спрос оплачивает государство; ~600 оптовиков, GDP только у 117; всего 6 доклинических лабораторий. ПРОТИВ: Clean Room Systems (cleanroom.uz) уже продаёт подготовку к GMP-аудиту 2027 — самую маржинальную часть; лабораторное железо держат локальные дистрибьюторы. Модель: дистрибуторская маржа 18-28% плюс квалификация IQ/OQ/PQ $5-25 тыс. с прибора ежегодно — подписка поверх разовой продажи. Товарный запас = оборотный капитал.',
 market={'tam_customers':[55,130,250],'max_capture_rate':0.05,'winback_share':0.75},
 pricing={'arpu_month':[4000,9000,18000]},
 churn={'monthly':[0.025,0.045,0.075]},
 funnel={'win_rate':[0.12,0.22,0.36],'cac0':[1500,3500,8000],'founder_opps_month':[1.5,2.5,4.0]},
 delivery={'clients_per_fte':[2.5,4.0,6.5],'fte_cost_month':[1100,1900,3000],'max_fte':14},
 costs={'fixed_opex_month':[2000,3800,6500],'gross_margin':[0.30,0.42,0.55],
        'startup_capex':[80000,180000,350000]},
 capital={'debt_share_of_capex':0.40,'debt_rate_annual':0.18,'debt_term_months':36,
          'debt_grace_months':3,'capex_recovery_share':0.65},
 wc={'dso_days':[45,70,110],'dpo_days':45,'prepay_share':0.2},
 competition={'p_competitor_at_start':0.70,'entry_hazard_month':0.03},
 exit={'ebitda_multiple':[3.0,5.0,7.0],'prob_exit_market':0.45},
 launch={'delay_months':[2,5,9],'p_fail_to_launch':0.12,'p_no_demand':0.16},
 fx={'usd_cost_share':0.75,'usd_revenue_share':0.15}))

C.append(cfg('F5-PRO-11','Sell-side advisory и предпродажная подготовка госактивов',
 'Ярус 3 место 6 (6.90). ФАКТЫ: УП-177 (84 доли, 1 242 объекта, 8 000 га, свыше $8 млрд); готовность платить ДОКАЗАНА тем, что государство уже наняло советников. ПРОТИВ: мандаты по КРУПНЕЙШИМ лотам уже розданы — Rothschild & Co (стратегический и финансовый советник), KPMG (финсоветник и vendor due diligence), Deloitte (независимый оценщик). Остаётся средний эшелон. Цикл госзакупки консультуслуг тянет первый доход к 6-9 месяцу. «Золотая акция» государства снижает цену сделки, а значит и success fee. Бутик без отчуждаемого актива — выход слабый.',
 market={'tam_customers':[25,65,125],'max_capture_rate':0.05,'winback_share':0.6},
 pricing={'arpu_month':[9000,18000,34000]},
 churn={'monthly':[0.09,0.15,0.23]},
 funnel={'win_rate':[0.10,0.18,0.30],'cac0':[1500,4000,9000],'founder_opps_month':[1.5,3.0,4.5]},
 delivery={'clients_per_fte':[1.5,2.5,4.0],'fte_cost_month':[1600,2800,4500],'max_fte':8},
 costs={'fixed_opex_month':[1800,3200,5800],'gross_margin':[0.60,0.74,0.85],
        'startup_capex':[3000,9000,20000]},
 competition={'p_competitor_at_start':0.90,'entry_hazard_month':0.03,'winrate_impact':0.35},
 exit={'ebitda_multiple':[2.0,3.0,4.5],'prob_exit_market':0.28},
 launch={'delay_months':[4,7,12],'p_fail_to_launch':0.12,'p_no_demand':0.22}))

C.append(cfg('F6-TRL-25','Роллап частных вузов и колледжей',
 'Ярус 3 место 7 (6.89), лучшая ось A в своём пакете (рынок, окно, барьеры), но ось B слабая. ФАКТЫ: постановление от 30.06.2025 требует от частного вуза уставный фонд $2 млн ПЛЮС депозит $350 тыс.; перелицензирование до 01.01.2026 вызвало ПЕРВОЕ В ИСТОРИИ сокращение числа негосударственных вузов (99 -> 97) — то есть появились вынужденные продавцы. В стране 97 частных вузов и 51 частный колледж, ~500 тыс. студентов. ГЛАВНОЕ ОГРАНИЧЕНИЕ: роллап на 3-6 активов запирает $6-12 млн капитала при личных $150 тыс. — проверяем, вытягивает ли структура долга. B7=4: массовый набор студентов и ежедневная операционка против стиля.',
 market={'tam_customers':[40,90,150],'max_capture_rate':0.02,'winback_share':0.2},
 pricing={'arpu_month':[45000,95000,180000]},
 churn={'monthly':[0.004,0.010,0.022]},
 funnel={'win_rate':[0.08,0.16,0.28],'cac0':[15000,40000,90000],'founder_opps_month':[0.7,1.3,2.2]},
 delivery={'clients_per_fte':[0.4,0.7,1.2],'fte_cost_month':[1500,2600,4200],
           'ramp_months':3,'max_fte':40,'max_hires_per_month':2.0},
 costs={'fixed_opex_month':[6000,12000,22000],'gross_margin':[0.35,0.48,0.60],
        'startup_capex':[2500000,5000000,9000000]},
 capital={'debt_share_of_capex':0.65,'debt_rate_annual':0.18,'debt_term_months':84,
          'debt_grace_months':12,'capex_recovery_share':0.70,'prefund_months':4},
 wc={'dso_days':[20,40,70],'prepay_share':0.35},
 competition={'p_competitor_at_start':0.50,'entry_hazard_month':0.015},
 exit={'ebitda_multiple':[5.0,8.0,11.0],'prob_exit_market':0.50,'hold_multiple_factor':0.75},
 abandon={'check_month':30,'min_monthly_revenue':[40000,90000,160000]},
 launch={'delay_months':[6,11,19],'p_fail_to_launch':0.25,'p_no_demand':0.18}))

C.append(cfg('F7-FIN-20','Банковский мониторинг долевого строительства и эскроу-контроль',
 'Ярус 3 место 8 (6.85). ПРОТИВ (этот кластер опровергается уже третий раз): технадзор регулируется ПКМ N321 от 20.05.2021, то есть профессия НЕ рождается; Quality Control System (infoqcs.uz, ISO 9001-2015), stroycontrol.uz, engineering-services.uz уже работают и перецелятся за недели; Ipoteka Bank сам продаёт проектное финансирование с эскроу; готовится госплатформа Uy-joy со сведениями о застройщиках, ходе работ, эскроу и ДДУ — частичный государственный заменитель. ЗА: банковский заказчик действительно новый, у заказчика партнёр-инженер-строитель, а сметный и финансовый контур задействует его ACCA. База плательщиков узкая: решают 5-15 уполномоченных банков.',
 market={'tam_customers':[30,70,140],'max_capture_rate':0.055,'winback_share':0.8},
 pricing={'arpu_month':[3500,7000,13000]},
 churn={'monthly':[0.03,0.055,0.09]},
 funnel={'win_rate':[0.12,0.22,0.35],'cac0':[1000,2800,6500],'founder_opps_month':[1.5,3.0,4.5]},
 delivery={'clients_per_fte':[2.0,3.5,5.5],'fte_cost_month':[1000,1800,2900],'max_fte':16},
 costs={'fixed_opex_month':[1500,2800,5000],'gross_margin':[0.55,0.68,0.80],
        'startup_capex':[8000,20000,45000]},
 competition={'p_competitor_at_start':0.85,'entry_hazard_month':0.04,'winrate_impact':0.3},
 exit={'ebitda_multiple':[2.5,4.0,6.0],'prob_exit_market':0.35},
 launch={'delay_months':[2,5,10],'p_fail_to_launch':0.15,'p_no_demand':0.25}))

C.append(cfg('F8-AST-28','Пункт весогабаритного контроля по 20-летней аренде с аукциона',
 'Ярус 3 место 9 (6.83), ЛУЧШИЙ ВЫХОД В ФИНАЛЕ (A7=9): 20-летний контракт с правом передачи третьим лицам — это отчуждаемый актив. ФАКТЫ: ЗРУ-1162 подписан 05.08.2026, пункты сдаются в аренду на 20 лет через аукцион; прямых операторов ВГК в стране нет. ПРОТИВ: контрольную функцию по закону сохраняет Инспекция по надзору на транспорте — риск оказаться подрядчиком без собственного тарифа; на рынке уже есть концессионный игрок платных дорог (Ургенч-Хива T-001 запущена 17.08.2026, строится Ташкент-Самарканд за $2.2 млрд) — конкуренция за те же аукционы придёт оттуда. B1=3: 13-24 месяца до выручки, аукцион плюс стройка.',
 market={'tam_customers':[12,30,60],'max_capture_rate':0.05,'winback_share':0.2},
 pricing={'arpu_month':[14000,28000,52000],'price_escalation_annual':0.05},
 churn={'monthly':[0.001,0.003,0.008]},
 funnel={'win_rate':[0.10,0.20,0.34],'cac0':[6000,15000,32000],'founder_opps_month':[0.8,1.6,2.6]},
 delivery={'clients_per_fte':[0.8,1.4,2.2],'fte_cost_month':[900,1500,2400],
           'ramp_months':3,'max_fte':22,'max_hires_per_month':2.0},
 costs={'fixed_opex_month':[3000,5500,9500],'gross_margin':[0.50,0.64,0.76],
        'startup_capex':[400000,900000,1800000]},
 capital={'debt_share_of_capex':0.60,'debt_rate_annual':0.17,'debt_term_months':84,
          'debt_grace_months':12,'capex_recovery_share':0.45,'prefund_months':4},
 wc={'dso_days':[20,35,60],'prepay_share':0.1},
 competition={'p_competitor_at_start':0.45,'entry_hazard_month':0.02},
 exit={'ebitda_multiple':[6.0,9.0,13.0],'prob_exit_market':0.55,'hold_multiple_factor':0.85},
 abandon={'check_month':30,'min_monthly_revenue':[10000,22000,40000]},
 launch={'delay_months':[10,16,26],'p_fail_to_launch':0.28,'p_no_demand':0.20}))

os.makedirs(OUT, exist_ok=True)
for c in C:
    p=f'{OUT}/{c["id"]}.json'
    json.dump(c, open(p,'w',encoding='utf-8'), ensure_ascii=False, indent=1)
    cap=c['costs']['startup_capex'][1]; ds=c['capital']['debt_share_of_capex']
    print(f'{c["id"]:<12} капзатраты(медиана) ${cap:>9,.0f}  долг {ds:.0%}  свой взнос ${cap*(1-ds):>9,.0f}')
print(f'\nсоздано конфигураций: {len(C)}')
