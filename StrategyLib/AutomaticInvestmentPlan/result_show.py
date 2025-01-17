"""
 Author       : adolf
 Date         : 2023-02-06 23:17:11
@LastEditors  : error: git config user.name & please set dead value or install git
@LastEditTime : 2023-06-06 23:36:34
@FilePath     : /stock_quant/StrategyLib/AutomaticInvestmentPlan/result_show.py
"""

from datetime import datetime

import streamlit as st

# import 路径修改
import sys,os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from StrategyLib.AutomaticInvestmentPlan.stable_dog import get_AI_plan_result


def getDays(day1, day2):
    # 获取需要计算的时间戳
    d1 = datetime.strptime(day1, "%Y-%m-%d")
    d2 = datetime.strptime(day2, "%Y-%m-%d")
    interval = d2 - d1  # 两日期差距
    return interval.days


def auto_investment_plan():
    try:
        st.subheader("定投回测结果")
        code = st.sidebar.text_input("code", value="sz.399006")
        gap_days = st.sidebar.text_input("interval", value=1)
        first_buy_day = st.sidebar.text_input("start", value="2019-01-02")
        want_rate = st.sidebar.text_input("target", value=1.1)
        if_intelli = st.sidebar.text_input("if_intelli", value="yes")
        threshold = st.sidebar.text_input("threshold", value=500000)
        st.text("定投记录表：")
        res, stock_data = get_AI_plan_result(
            code=code,
            gap_days=int(gap_days),
            first_buy_day=first_buy_day,
            want_rate=float(want_rate),
            if_intelli=if_intelli == "yes",
            threshold=int(threshold),
        )
        res.drop(["buy_index"], axis=1, inplace=True)
        st.dataframe(res, width=900)
        natual_day = getDays(res.loc[0, "date"], res.loc[len(res) - 1, "date"])
        outtext1 = f"达成目标自然日天数:{natual_day}，"
        outtext2 = f"投入次数/总金额:{len(res[res['put'] != 0])}/{int(res.loc[len(res) - 1, 'put_in'])}，"
        outtext3 = f"总收益:{int(res.loc[len(res) - 1, 'account'] - res.loc[len(res) - 1, 'put_in'])}，"
        outtext4 = f"收益率:{round(res.loc[len(res) - 1, 'rate'], 3)},"
        outtext5 = f"标的涨跌幅:{float(stock_data.loc[len(stock_data) - 1, 'close']) / float(stock_data.loc[0, 'open'])}"

        st.text(
            f"{outtext1}{outtext2}{outtext3}{outtext4}{outtext5}"
        )
        chart_data = res[["rate"]].apply(lambda x: (x - 1) * 100)
        st.text("定投收益率：")
        st.line_chart(chart_data, y="rate")
        st.text("达成目标收益率时投入总金额：")
        st.line_chart(res, y="put_in")
        st.text("股票行情：")
        st.line_chart(stock_data, y="close", x="date")

    except Exception as e:
        st.title("出错了")
        st.write(e)
