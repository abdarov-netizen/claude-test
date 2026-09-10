# -*- coding: utf-8 -*-
"""Сборка итоговой книги Excel. Данные приходят из артефактов на диске."""
import json, os, numpy as np, xlsxwriter

def _fmts(wb):
    return {
      "title": wb.add_format({"bold":True,"font_size":15,"font_color":"#1F3864"}),
      "h":     wb.add_format({"bold":True,"bg_color":"#1F3864","font_color":"white",
                              "border":1,"text_wrap":True,"valign":"vcenter","align":"center"}),
      "h2":    wb.add_format({"bold":True,"bg_color":"#D9E2F3","border":1,"text_wrap":True,"valign":"top"}),
      "txt":   wb.add_format({"border":1,"text_wrap":True,"valign":"top"}),
      "txtl":  wb.add_format({"border":1,"text_wrap":True,"valign":"top","align":"left"}),
      "num":   wb.add_format({"border":1,"num_format":"#,##0"}),
      "num1":  wb.add_format({"border":1,"num_format":"#,##0.0"}),
      "num2":  wb.add_format({"border":1,"num_format":"0.00"}),
      "usd":   wb.add_format({"border":1,"num_format":"$#,##0"}),
      "usd2":  wb.add_format({"border":1,"num_format":"$#,##0;[Red]-$#,##0"}),
      "pct":   wb.add_format({"border":1,"num_format":"0.0%"}),
      "pct2":  wb.add_format({"border":1,"num_format":"0.00%"}),
      "good":  wb.add_format({"border":1,"bg_color":"#C6EFCE","num_format":"0.00"}),
      "warn":  wb.add_format({"border":1,"bg_color":"#FFEB9C","num_format":"0.00"}),
      "bad":   wb.add_format({"border":1,"bg_color":"#FFC7CE","num_format":"0.00"}),
      "note":  wb.add_format({"italic":True,"font_color":"#555555","text_wrap":True,"valign":"top"}),
      "bold":  wb.add_format({"bold":True}),
    }

def sheet_table(ws, f, headers, rows, widths, start=0, freeze=True):
    for c,(hname,w) in enumerate(zip(headers,widths)):
        ws.write(start,c,hname,f["h"]); ws.set_column(c,c,w)
    ws.set_row(start,32)
    for r,row in enumerate(rows,start=start+1):
        for c,v in enumerate(row):
            fmt = f["txt"]
            if isinstance(v,tuple): v,fmt = v[0], f[v[1]]
            ws.write(r,c,v,fmt)
    if freeze: ws.freeze_panes(start+1,0)
