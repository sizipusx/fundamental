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
    #아이투자에서 기업 데이터 가져오기: 크롤링 막혀서 네이버로 변경
    # info_url = "http://m.itooza.com/search.php?sn="+code
    # info_page = requests.get(info_url)
    # info_tables = pd.read_html(info_page.text)
    # company_info = info_tables[0]
    # company_info.set_index(0, inplace=True)
    # st.table(company_info)
    # #아이투자 10년 데이타
    # value_df, ttm_df, ann_df = getData.get_kor_itooza(code)
    #네이버 4년 데이타
    naver_ann, naver_q = getData.get_naver_finance(code)

    # 좀 더 자세히
    # 좀더 자세히
    n_url_f = 'https://navercomp.wisereport.co.kr/v2/company/c1010001.aspx?cmp_cd='+ code+ '&amp;target=finsum_more'
    fs_page = requests.get(n_url_f)
    navers_more = pd.read_html(fs_page.text)

    company_basic_info = navers_more[0]

    if  st.checkbox('Show raw data'):
        st.table(company_basic_info.set_index(1, inplace=True))
        # st.dataframe(ttm_df.style.highlight_max(axis=0))
        # st.dataframe(ann_df.style.highlight_max(axis=0))
        st.dataframe(naver_ann.style.highlight_max(axis=0))
        st.dataframe(naver_q.style.highlight_max(axis=0))
    st.subheader("Valuation")
    #value_df = value_df.astype(float).fillna(0).round(decimals=2)
    st.table(navers_more[5].set_index(1, inplace=True))
    #RIM Price
    rim_price, r_ratio = makeData.kor_rim(naver_ann, naver_q)
    #기업의 최근 price
    # now = datetime.now() +pd.DateOffset(days=-3)
    # today = '%s-%s-%s' % ( now.year, now.month, now.day)
    # price = fdr.DataReader(code, today).iloc[-1,0]
    # st.write(price)
    # fig = go.Figure(go.Indicator(
    #     mode = "gauge+number+delta",
    #     value = value_df.iloc[1,0],
    #     delta = {'reference': value_df.iloc[0,0], 'relative': True},
    #     title = {'text': f"RIM-Price(r={r_ratio}) & 기대수익률"},
    #     domain = {'x': [0, 1], 'y': [0, 1]}
    # ))
    # st.plotly_chart(fig)

    #ttmeps last / ttmeps.max()
    # fig = go.Figure(go.Indicator(
    #     mode = "gauge+number+delta",
    #     value = ttm_df.iloc[-1,0],
    #     delta = {'reference': ttm_df['EPS'].max(), 'relative': True},
    #     title = {'text': f"Last ttmEPS ={ttm_df.iloc[-1,0]}원 relative Max ttmEPS = {ttm_df['EPS'].max().astype(int)} 원"},
    #     domain = {'x': [0, 1], 'y': [0, 1]}
    # ))
    # st.plotly_chart(fig)

    #Earnings Yeild
    # fig = go.Figure(go.Indicator(
    # mode = "number+delta",
    # value = 1/value_df.iloc[2,0]*100,
    # title = {"text": "Earnings Yield<br><span style='font-size:0.8em;color:gray'>Demand Yield(15%)</span>"},
    # domain = {'x': [0, 1], 'y': [0, 1]},
    # delta = {'reference': 15}))
    # st.plotly_chart(fig)
    
    #PEG 
    # fig = go.Figure(go.Indicator(
    # mode = "number+delta",
    # value = value_df.iloc[7,0],
    # title = {"text": "PEG<br><span style='font-size:0.8em;color:gray'>5 Year Average</span>"},
    # domain = {'x': [0, 1], 'y': [0, 1]},
    # delta = {'reference': 1.5}))
    # st.plotly_chart(fig)

    # #PERR, PBRR
    # fig = go.Figure(go.Indicator(
    # mode = "number+delta",
    # value = value_df.iloc[8,0],
    # title = {"text": "PERR<br><span style='font-size:0.8em;color:gray'>Over 2 is Not Invest</span>"},
    # domain = {'x': [0, 1], 'y': [0, 1]},
    # delta = {'reference': 2}))
    # st.plotly_chart(fig)

    # fig = go.Figure(go.Indicator(
    # mode = "number+delta",
    # value = value_df.iloc[9,0],
    # title = {"text": "PBRR<br><span style='font-size:0.8em;color:gray'>Over 2 is Not Invest</span>"},
    # domain = {'x': [0, 1], 'y': [0, 1]},
    # delta = {'reference': 2}))
    # st.plotly_chart(fig)
    

    st.subheader("Candlestick Chart")
    now = datetime.now() +pd.DateOffset(days=-4000)
    start_date = '%s-%s-%s' % ( now.year, now.month, now.day)
    price_df = fdr.DataReader(code,start_date)

    chart.price_chart(code, price_df)

    st.subheader("Earnings")
    from PIL import Image
    col1, col2, col3 = st.beta_columns(3)
    
    with col1:
        ecycle = Image.open("good-cycle.png")
        st.image(ecycle, caption='좋은 펀드 매니저')
        with st.expander("See explanation"):
            st.markdown('**성공하는 투자자**는 시장의 주식에 대한 기대 수준이 높든지 낮든지 상관없이 이익 전망이 개선되는 주식을 언제나 찾을 것이다. \
            따라서 **_‘좋은’ 펀드매니저_**는 이익 전망이 개선되는 기업, 다시 말해 기업의 이익예상 라이프사이클의 왼쪽 부분에 위치한 주식을 매수할 것이다.')
    with col2:
        gcycle = Image.open("growth.png")
        st.image(gcycle, caption='이익예상 라이프사이클에서의 투자자의 위치- 성장주의 경우')
        with st.expander("See explanation"):
            st.markdown('투자자들이 **_성장주_**를 매수할 때 그들은 지금 자신이 다이아몬드를 구입했기를 기대한다. 바꿔 말하면 사람들이 많은 기대를 갖고 다이아몬드를 사는 것처럼 성장주 투자자는 매수한 주식에 대해 높은 기대 수준을 가지고 있다. 따라서 성장주 투자자는 이익예상 라이프사이클의 위쪽에 위치한다')
    with col3:
        vcycle = Image.open("value.png")
        st.image(vcycle, caption='이익예상 라이프사이클에서의 투자자의 위치- 가치주의 경우')
        with st.expander("See explanation"):
            st.markdown('**_가치주 투자자들_**이 사과를 구입할 때 약간의 기대를 가지기는 하지만, 벌레가 있더라도 다소간의 충격은 있을지 몰라도 비극으로 받아들이지는 않는다. 즉, 가치주 투자자는 매입한 주식에 대해 큰 기대를 갖지 않는다. 따라서 가치주 투자자는 일반적으로 이익예상 라이프사이클의 아래쪽에 위치한다')
    
    totalcycle = Image.open("image.png")
    st.image(totalcycle, caption= "좋은 가치 VS 나쁜가치 VS  좋은 성장 VS 나쁜 성장")
    with st.expander("See explanation"):
        st.markdown(" 주식투자자들은 기업의 이익 전망이 직선처럼 움직인다고 착각하고 있지만, **이익 전망의 변화 과정은 원의 모습을 띤다.**")

    #chart.kor_earning_chart(code,com_name, ttm_df, ann_df)
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