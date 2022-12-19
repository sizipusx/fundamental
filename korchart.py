import time
from datetime import datetime

import numpy as np
import pandas as pd
import requests
import json
from pandas.io.json import json_normalize
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
from matplotlib import font_manager, rc
import seaborn as sns
cmap = cmap=sns.diverging_palette(250, 5, as_cmap=True)
import streamlit as st
from pykrx import stock
import FinanceDataReader as fdr
import getData, makeData, drawkorchart
import chart

pd.set_option('display.float_format', '{:.2f}'.format)
#############html 영역####################
html_header="""
<head>
<title>Korea house analysis chart</title>
<meta charset="utf-8">
<meta name="keywords" content="chart, analysis">
<meta name="description" content="House data analysis">
<meta name="author" content="indiesoul">
<meta name="viewport" content="width=device-width, initial-scale=1">
</head>
<h2 style="font-size:200%; color:#008080; font-family:Georgia"> 국내 상장 기업 기본 정보 <br>
<hr style= "  display: block;
  margin-top: 0.5em;
  margin-bottom: 0.5em;
  margin-left: auto;
  margin-right: auto;
  border-style: inset;
  border-width: 1.5px;"></h1>
"""

st.set_page_config(page_title="국내 상장 기업 정보 조회", page_icon="files/logo2.png", layout="wide")
st.markdown('<style>body{background-color: #fbfff0}</style>',unsafe_allow_html=True)
st.markdown(html_header, unsafe_allow_html=True)
st.markdown(""" <style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style> """, unsafe_allow_html=True)

pio.templates["myID"] = go.layout.Template(
    layout_annotations=[
        dict(
            name="draft watermark",
            text="graph by 기하급수적",
            textangle=0,
            opacity=0.2,
            font=dict(color="black", size=10),
            xref="paper",
            yref="paper",
            x=0.9,
            y=0.1,
            showarrow=False,
        )
    ]
)


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
    # 회사채 BBB- 할인율
    in_url = 'https://www.kisrating.com/ratingsStatistics/statics_spread.do'
    in_page = requests.get(in_url)
    in_tables = pd.read_html(in_page.text)
    yeild = in_tables[0].iloc[-1,-1]
    #make BED valuation
    value_df = getData.make_Valuation(code, com_name, yeild)
    
    #네이버 4년 데이타
    #naver_ann, naver_q = getData.get_naver_finance(code)
    # st.dataframe(naver_ann)
    # st.dataframe(naver_q)
    # st.write(naver_ann.index)

    # Fnguide에서 원본 데이터 가져오기
    sep_flag, fn_ann_df, fn_qu_df, fs_tables = getData.get_fdata_fnguide(code)
    with st.expander("See Raw Data"):
        try:
            #value_df = value_df.astype(float).fillna(0).round(decimals=2)
            st.dataframe(fn_ann_df.T.astype(float).fillna(0).round(decimals=2).style.background_gradient(cmap, axis=0)\
                                        .format(precision=2, na_rep='MISSING', thousands=","))
            st.dataframe(fn_qu_df.T.astype(float).fillna(0).round(decimals=2).style.background_gradient(cmap, axis=0)\
                                  .format(precision=2, na_rep='MISSING', thousands=","))
        except ValueError :
            st.dataframe(fn_ann_df.T)
            st.dataframe(fn_qu_df.T)
    if sep_flag == True:
        st.write("별도")
    else:
        st.write("연결")
   
    # 좀더 자세히
    n_url_f = 'https://navercomp.wisereport.co.kr/v2/company/c1010001.aspx?cmp_cd='+ code+ '&amp;target=finsum_more'
    fs_page = requests.get(n_url_f)
    navers_more = pd.read_html(fs_page.text)
    company_basic_info = navers_more[0]

    #st.table(company_basic_info)

    st.subheader("Valuation")
    st.table(value_df)

    with st.container():
        col1, col2, col3 = st.columns([30,2,30])
        with col1:
            st.dataframe(navers_more[5])
        with col2:
            st.write("")
        with col3: 
            compare_df = fs_tables[8].set_index("구분")
            st.dataframe(compare_df)
    html_br="""
    <br>
    """
    st.markdown(html_br, unsafe_allow_html=True)
    #######################################################
    with st.container():
        col1, col2, col3 = st.columns([30,2,30])
        with col1:
            #RIM price
            st.subheader("RIM price")
            fig = go.Figure(go.Indicator(
            #mode = "number+delta",
            mode = "gauge+number+delta",
            value = int(value_df.iloc[13,0].replace(',','').replace('원', '')), #Rim price
            #delta = {'reference': int(value_df.iloc[13,0]), 'relative': True},
            title = {'text': f"RIM<br>Price<br><span style='font-size:0.8em;color:gray'>(r={yeild})</span>"},
            domain = {'x': [0, 1], 'y': [0, 1]},
            gauge = {'shape': "bullet",
                    'threshold': {
                    'line': {'color': "red", 'width': 2},
                    'thickness': 0.75, 'value': float(value_df.iloc[3,0].replace(',','').replace('원', ''))}},
            delta = {'reference': int(value_df.iloc[3,0].replace(',','').replace('원', '')), 'relative': True},
            ))
            fig.update_layout(height = 250)
            st.plotly_chart(fig)
        with col2:
            st.write("")
        with col3:  
            #Earnings Yeild: 기대수익률
            st.subheader("Earnings Yeild")
            fig = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = round(float(value_df.iloc[5,0].replace(',','').replace('원', ''))/float(value_df.iloc[3,0].replace(',','').replace('원', ''))*100,2),
            title = {"text": "Earnings<br>Yield<br><span style='font-size:0.8em;color:gray'>Demand Yield(15%)</span>"},
            domain = {'x': [0, 1], 'y': [0, 1]},
            gauge = {'shape': "bullet",
                    'threshold': {
                    'line': {'color': "red", 'width': 2},
                    'thickness': 0.75, 'value': 15.0}},
            delta = {'reference': 15}))
            fig.update_layout(height = 250)
            st.plotly_chart(fig)
    ### PERR, PBRR 같이 보기 #########################################################################################
    with st.container():
        col1, col2, col3 = st.columns([30,2,30])
        with col1:
            # #PERR, PBRR
            fig = go.Figure(go.Indicator(
            mode = "number+delta",
            value = float(value_df.iloc[-3,0]),
            title = {"text": "PERR<br><span style='font-size:0.8em;color:gray'>Over 2 is Not Invest</span>"},
            domain = {'x': [0, 1], 'y': [0, 1]},
            delta = {'reference': 2}))
            st.plotly_chart(fig)
            #PEG 
            # fig = go.Figure(go.Indicator(
            # mode = "number+delta",
            # value = value_df.iloc[7,0],
            # title = {"text": "PEG<br><span style='font-size:0.8em;color:gray'>5 Year Average</span>"},
            # domain = {'x': [0, 1], 'y': [0, 1]},
            # delta = {'reference': 1.5}))
            # st.plotly_chart(fig)
        with col2:
            st.write("")
        with col3:
            fig = go.Figure(go.Indicator(
            mode = "number+delta",
            value = float(value_df.iloc[-2,0]),
            title = {"text": "PBRR<br><span style='font-size:0.8em;color:gray'>Over 2 is Not Invest</span>"},
            domain = {'x': [0, 1], 'y': [0, 1]},
            delta = {'reference': 2}))
            st.plotly_chart(fig)
    html_br="""
    <br>
    """
    st.markdown(html_br, unsafe_allow_html=True)
    #######################################################
    

    #ttmeps last / ttmeps.max()
    # fig = go.Figure(go.Indicator(
    #     mode = "gauge+number+delta",
    #     value = ttm_df.iloc[-1,0],
    #     delta = {'reference': ttm_df['EPS'].max(), 'relative': True},
    #     title = {'text': f"Last ttmEPS ={ttm_df.iloc[-1,0]}원 relative Max ttmEPS = {ttm_df['EPS'].max().astype(int)} 원"},
    #     domain = {'x': [0, 1], 'y': [0, 1]}
    # ))
    # st.plotly_chart(fig)
     ### PERR, PBRR 같이 보기 #########################################################################################
    with st.container():
        col1, col2, col3 = st.columns([30,2,30])
        with col1:
            # candlestick chart
            st.subheader("Candlestick Chart")
            now = datetime.now() +pd.DateOffset(days=-4000)
            start_date = '%s-%s-%s' % ( now.year, now.month, now.day)
            price_df = fdr.DataReader(code,start_date)
            chart.price_chart(code, com_name, price_df)
        with col2:
            st.write("")
        with col3:
            drawkorchart.dividend_chart(code, com_name, fn_ann_df.T)
    html_br="""
    <br>
    """
    st.markdown(html_br, unsafe_allow_html=True)
    # st.subheader("Earnings")

    # from PIL import Image
    # col1, col2, col3 = st.columns(3)
    
    # with col1:
    #     ecycle = Image.open("good-cycle.png")
    #     st.image(ecycle, caption='좋은 펀드 매니저')
    #     with st.expander("See explanation"):
    #         st.markdown('**성공하는 투자자**는 시장의 주식에 대한 기대 수준이 높든지 낮든지 상관없이 이익 전망이 개선되는 주식을 언제나 찾을 것이다. \
    #         따라서 **_‘좋은’ 펀드매니저_**는 이익 전망이 개선되는 기업, 다시 말해 기업의 이익예상 라이프사이클의 왼쪽 부분에 위치한 주식을 매수할 것이다.')
    # with col2:
    #     gcycle = Image.open("growth.png")
    #     st.image(gcycle, caption='이익예상 라이프사이클에서의 투자자의 위치- 성장주의 경우')
    #     with st.expander("See explanation"):
    #         st.markdown('투자자들이 **_성장주_**를 매수할 때 그들은 지금 자신이 다이아몬드를 구입했기를 기대한다. 바꿔 말하면 사람들이 많은 기대를 갖고 다이아몬드를 사는 것처럼 성장주 투자자는 매수한 주식에 대해 높은 기대 수준을 가지고 있다. 따라서 성장주 투자자는 이익예상 라이프사이클의 위쪽에 위치한다')
    # with col3:
    #     vcycle = Image.open("value.png")
    #     st.image(vcycle, caption='이익예상 라이프사이클에서의 투자자의 위치- 가치주의 경우')
    #     with st.expander("See explanation"):
    #         st.markdown('**_가치주 투자자들_**이 사과를 구입할 때 약간의 기대를 가지기는 하지만, 벌레가 있더라도 다소간의 충격은 있을지 몰라도 비극으로 받아들이지는 않는다. 즉, 가치주 투자자는 매입한 주식에 대해 큰 기대를 갖지 않는다. 따라서 가치주 투자자는 일반적으로 이익예상 라이프사이클의 아래쪽에 위치한다')
    
    # #totalcycle = Image.open("image.png")
    # #st.image(totalcycle, caption= "좋은 가치 VS 나쁜가치 VS  좋은 성장 VS 나쁜 성장")
    # with st.expander("See explanation"):
    #     st.markdown(" 주식투자자들은 기업의 이익 전망이 직선처럼 움직인다고 착각하고 있지만, **이익 전망의 변화 과정은 원의 모습을 띤다.**")
    
    #chart.kor_earning_chart(code,com_name, ttm_df, ann_df)
    try:
        drawkorchart.income_chart(code, com_name, fn_ann_df.T, fn_qu_df.T, sep_flag)
        drawkorchart.balance_chart(code, com_name, fn_qu_df.T)
    except TypeError as te :
        st.write("알수 없는 Error로 차트를 그릴 수 없습니다!")
        st.error("Error 내용: " + te)
        
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