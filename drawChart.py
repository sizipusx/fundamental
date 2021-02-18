import time
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
import numpy as np
import pandas as pd
from datetime import datetime

import getData
import makeData
import chart

pd.set_option('display.float_format', '{:.2f}'.format)

before_time = datetime.now() +pd.DateOffset(years=-10)
now = datetime.now()
before = '%s-%s-%s' % ( before_time.year, before_time.month, before_time.day)
today = '%s-%s-%s' % ( now.year, now.month, now.day)

## 특정 위치의 배경색 바꾸기
@st.cache
def draw_color_cell(x,color):
    color = f'background-color:{color}'
    return color
# PER 값 변경    
@st.cache
def change_per_value(x):
    if x >= 100 :
        x = 100
    elif x <= 0 :
        x = 0
    else:
        pass
    return x

def run():

    #Fundamental 데이터 가져오기
    earning_q, earning_a = getData.get_fundamental_data_by_Json(input_ticker,"EARNINGS")
    income_q, income_a = getData.get_fundamental_data_by_Json(input_ticker,"INCOME_STATEMENT")
    balance_q, balance_a = getData.get_fundamental_data_by_Json(input_ticker,"BALANCE_SHEET")
    cash_q, cash_a = getData.get_fundamental_data_by_Json(input_ticker,"CASH_FLOW")
    #Summary 데이터 가져오기    
    description_df, ratio_df, return_df, profit_df, dividend_df, volume_df, price_data, valuation_df = getData.get_overview(input_ticker)
    st.table(description_df)
    st.table(price_data)
    st.table(volume_df)
    st.table(return_df)
    st.table(dividend_df)
    st.table(ratio_df)
    st.table(valuation_df)
    
    # st.dataframe(income_q)
    st.dataframe(balance_q)
    # st.dataframe(cash_a)
    # st.dataframe(earning_q)
    #Growth Ratio 
    growth_df = makeData.make_growthRatio(earning_a, earning_q, income_a, cash_a, balance_a)
    st.table(growth_df)
    #close data
    price_data = getData.get_close_data(input_ticker, earning_q.iloc[0,0], earning_q.iloc[-1,0])
    price_df = getData.get_close_data(input_ticker, before, today)
    # st.dataframe(price_df)

    #draw chart
    chart.earning_chart(input_ticker, earning_q, earning_a, price_data)

    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = valuation_df.at['RIM','Valuation'],
        delta = {'reference': valuation_df.at['Price','Valuation'], 'relative': True},
        title = {'text': "RIM-Price(r=12%)"},
        domain = {'x': [0, 1], 'y': [0, 1]}
    ))
    st.plotly_chart(fig)

    fig = go.Figure(go.Indicator(
        mode = "number+delta",
        value = float(valuation_df.at['Earnings Yield','Valuation'].replace("%","")),
        title = {"text": "Earnings Yield<br><span style='font-size:0.8em;color:gray'>Demand Yield(15%)</span>"},
        domain = {'x': [0, 1], 'y': [0, 1]},
        delta = {'reference': 15}))
    st.plotly_chart(fig)

    #Draw Chart
    chart.price_chart(input_ticker, price_df)
    chart.income_chart(input_ticker, income_q, income_a)
    chart.income_margin_chart(input_ticker, income_q)
    chart.balance_chart(input_ticker, balance_q)
    chart.cashflow_chart(input_ticker, cash_q, income_q)


    #조회시 1분 기다려야 함
    st.warning('Please Wait One minute Before Searching Next Company!!!')
    my_bar = st.progress(0)
    for percent_complete in range(100):
        time.sleep(0.6)
        my_bar.progress(percent_complete + 1)


if __name__ == "__main__":

    company_info = getData.load_data()
    input_ticker = st.sidebar.text_input("ticker").upper()   
    ticker_list = [ "SENEA", "IMKTA", "KBAL", "CMC", \
                    "APT","AMCX","BIIB", "BIG", "CI", "CPRX", "CHRS", "CSCO","CVS","DHT", "EURN", "HRB", "PRDO", \
                    "MO", "T", "O", "OMC", "SBUX", \
                    "MSFT", "MMM", "INVA", "SIGA", "WLKP", "VYGR", "KOF", "WSTG", "LFVN", "SUPN"]
    if input_ticker == "":
        input_ticker = st.sidebar.selectbox(
            'Ticker',ticker_list
        )
    
    input_ticker = input_ticker.upper()
    submit = st.sidebar.button('Run app')
    if submit:
        run()