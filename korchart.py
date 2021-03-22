import time
from datetime import datetime

import numpy as np
import pandas as pd
import requests
import json
from pandas.io.json import json_normalize
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import streamlit as st
from pykrx import stock
import FinanceDataReader as fdr
import getData, makeData, drawkorchart
import chart

pd.options.display.float_format = '{:.2f}'.format

@st.cache
def load_data():
    # 코스피, 코스닥, 코넥스 종목 리스트 가져오기
    tickers = stock.get_market_ticker_list()
    krx = fdr.StockListing('KRX')
    krx = krx[~krx['Name'].str.endswith(('우','A', 'B', '스팩', 'C', ')', '호', '풋', '콜', 'ETN'))]
    krx = krx[~(krx['Symbol'].str.len() != 6)]
    krx = krx[~(krx['Market'].str.endswith('X'))]
    return tickers, krx


def run(code, com_name):
    #아이투자에서 기업 데이터 가져오기
    info_url = "http://m.itooza.com/search.php?sn="+code
    info_page = requests.get(info_url)
    info_tables = pd.read_html(info_page.text)
    company_info = info_tables[0]
    company_info.set_index(0, inplace=True)
    st.table(company_info)
    #아이투자 10년 데이타
    value_df, ttm_df, ann_df = getData.get_kor_itooza(code)
    #네이버 4년 데이타
    naver_ann, naver_q = getData.get_naver_finance(code)

    if  st.checkbox('Show raw data'):
        st.dataframe(ttm_df.style.highlight_max(axis=0))
        st.dataframe(ann_df.style.highlight_max(axis=0))
        st.dataframe(naver_ann.style.highlight_max(axis=0))
        st.dataframe(naver_q.style.highlight_max(axis=0))
    
    st.subheader("Valuation")
    st.table(value_df)
    #RIM Price
    rim_price, r_ratio = makeData.kor_rim(ttm_df)
    #기업의 최근 price
    # now = datetime.now() +pd.DateOffset(days=-3)
    # today = '%s-%s-%s' % ( now.year, now.month, now.day)
    # price = fdr.DataReader(code, today).iloc[-1,0]
    # st.write(price)
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = value_df.iloc[1,0],
        delta = {'reference': value_df.iloc[0,0], 'relative': True},
        title = {'text': f"RIM-Price(r={r_ratio}) & 기대수익률"},
        domain = {'x': [0, 1], 'y': [0, 1]}
    ))
    st.plotly_chart(fig)

    #Earnings Yeild
    fig = go.Figure(go.Indicator(
    mode = "number+delta",
    value = 1/value_df.iloc[2,0]*100,
    title = {"text": "Earnings Yield<br><span style='font-size:0.8em;color:gray'>Demand Yield(15%)</span>"},
    domain = {'x': [0, 1], 'y': [0, 1]},
    delta = {'reference': 15}))
    st.plotly_chart(fig)

    #PEG 
    fig = go.Figure(go.Indicator(
    mode = "number+delta",
    value = value_df.iloc[7,0],
    title = {"text": "PEG<br><span style='font-size:0.8em;color:gray'>5 Year Average</span>"},
    domain = {'x': [0, 1], 'y': [0, 1]},
    delta = {'reference': 1.5}))
    st.plotly_chart(fig)

    #PERR, PBRR
    fig = go.Figure(go.Indicator(
    mode = "number+delta",
    value = value_df.iloc[8,0],
    title = {"text": "PERR<br><span style='font-size:0.8em;color:gray'>Over 2 is Not Invest</span>"},
    domain = {'x': [0, 1], 'y': [0, 1]},
    delta = {'reference': 2}))
    st.plotly_chart(fig)

    fig = go.Figure(go.Indicator(
    mode = "number+delta",
    value = value_df.iloc[9,0],
    title = {"text": "PBRR<br><span style='font-size:0.8em;color:gray'>Over 2 is Not Invest</span>"},
    domain = {'x': [0, 1], 'y': [0, 1]},
    delta = {'reference': 2}))
    st.plotly_chart(fig)

    st.subheader("Candlestick Chart")
    chart.candlestick_chart(code)

    st.subheader("Earnings")
    chart.kor_earning_chart(code,com_name, ttm_df, ann_df)
    drawkorchart.income_chart(code, naver_ann, naver_q)
    drawkorchart.balance_chart(code, naver_q)

if __name__ == "__main__":
    data_load_state = st.text('Loading KRX Company List...')
    tickers, krx = load_data()
    data_load_state.text("Done! (using st.cache)")
    # st.dataframe(tickers)
    # st.dataframe(krx)
    etf = krx[krx['Sector'].isnull()]
    krx = krx[~krx['Sector'].isnull()]
    com_name = st.sidebar.text_input("Company Name")

    if com_name == "":
        com_name = st.sidebar.selectbox(
            'Company Name',
            krx['Name'].to_list() #tickers
        )

    comany_info = krx[krx['Name'] == com_name]
    company_name_ = comany_info.iloc[0,2]
    code = comany_info.iloc[0,0]
    st.subheader('<'+company_name_+'> 회사 기본 정보')
    st.table(comany_info.T)
    submit = st.sidebar.button('Analysis')

    if submit:
        run(code, company_name_)