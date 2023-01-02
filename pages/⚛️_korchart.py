import time
# from datetime import datetime
import datetime
from dateutil.relativedelta import relativedelta

import numpy as np
import pandas as pd
import requests
import json
import math
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
    krx = krx[~(krx['Code'].str.len() != 6)]
    krx = krx[~(krx['Market'].str.endswith('X'))]
    return tickers, krx

# 숫자로 모두 변환
def convert_str_to_float(value):
    if type(value) == float: # nan의 자료형은 float임
        return value
    elif value == '-' or value == 'N/A(IFRS)' or value == '완전잠식': # -로 되어 있으면 0으로 변환
        return np.NaN
    else:
        return float(value.replace(',', ''))


def run(ticker, com_name):
    # 회사채 BBB- 할인율
    in_url = 'https://www.kisrating.com/ratingsStatistics/statics_spread.do'
    in_page = requests.get(in_url)
    in_tables = pd.read_html(in_page.text)
    yeild = in_tables[0].iloc[-1,-1]
    bond3_y = in_tables[0].iloc[0,-2]
    #make BED valuation
    value_df = getData.make_Valuation(ticker, com_name, yeild)
    # Fnguide에서 원본 데이터 가져오기
    sep_flag, fn_ann_df, fn_qu_df, fs_tables = getData.get_fdata_fnguide(ticker)
    ################채권형 주식 valuation #######################
    #지속가능기간 10년 고정
    lasting_N = 10
    #기대수익률 15% 고정
    expect_yield = 0.15
    for ind in fn_ann_df.columns:
        fn_ann_df[ind] = fn_ann_df[ind].apply(convert_str_to_float)
    bps = int(value_df.loc['BPS'].replace(',','').replace('원', ''))
    current_pbr = round(float(value_df.loc['PBR']),2)
    current_roe = round(float(value_df.loc['ROE'].replace('%','')),2)
    #ROE 평균 구해보자
    roe_s = fn_ann_df.loc['ROE']
    roe_total = round(roe_s.mean(),2)
    roe_real = round(roe_s.iloc[:5].mean(),2)
    roe_sum = len(roe_s) - roe_s.isnull().sum()
    roe_est = round(roe_s.iloc[5:].mean(),2)
    if np.isnan(roe_s[5]) == False:
        
        roe_mean = np.mean([roe_total, roe_real, roe_est])
        roe_min = min(roe_total,roe_real,roe_est)
        roe_max = max(roe_total,roe_real,roe_est)
    else:
        roe_mean = roe_real
        roe_min = roe_real
        roe_max = roe_real
    
    current_price = int(value_df.loc['현재주가'].replace(',','').replace('원', ''))
    #ROE 추정치를 무얼로 하느냐에 따라 기대수익률이 모두 달라짐
    #ROE_min
    min_f_bps = bps*(1+roe_min/100)**lasting_N
    min_est_yield = round(((min_f_bps/current_price)**(1/lasting_N)-1)*100,2)
    min_proper_price = int(min_f_bps/(1+expect_yield)**10)
    # ROE_max
    max_f_bps = bps*(1+roe_max/100)**lasting_N
    max_est_yield = round(((max_f_bps/current_price)**(1/lasting_N)-1)*100,2)
    max_proper_price = int(max_f_bps/(1+expect_yield)**10)
    # ROE_mean
    f_bps = bps*(1+roe_mean/100)**lasting_N
    est_yield = round(((f_bps/current_price)**(1/lasting_N)-1)*100,2)
    proper_price = int(f_bps/(1+expect_yield)**10)
    #######홍진채###########
    log_v = (1+roe_mean/100)/(1+expect_yield)
    target_pbr = round((log_v)**lasting_N,2)
    ### 장기 기대수익률(채권현 주식(roe_min)과 다르게 현재 ROE로 계산 해 보자)
    longp_yield = round(((1+current_roe/100)/current_pbr**(1/lasting_N)-1)*100,2)
    ### 갭수익률 적정PBR/시가PBR -1
    gap_yield = round((target_pbr/current_pbr -1)*100,2)
    ### 지속 가능 기간
    last_p = round(math.log(current_pbr,log_v),1)
    #네이버 4년 데이타
    #naver_ann, naver_q = getData.get_naver_finance(code)
    # st.dataframe(naver_ann)
    # st.dataframe(naver_q)
    # st.write(naver_ann.index)
    with st.expander("See Raw Data"):
        try:
            st.dataframe(value_df.to_frame().T)
            st.dataframe(fn_ann_df.T.astype(float).fillna(0).round(decimals=2).style.background_gradient(cmap, axis=0)\
                                        .format(precision=2, na_rep='MISSING', thousands=","))
            st.dataframe(fn_qu_df.T.astype(float).fillna(0).round(decimals=2).style.background_gradient(cmap, axis=0)\
                                  .format(precision=2, na_rep='MISSING', thousands=","))
        except ValueError :
            st.dataframe(value_df.to_frame().T)
            st.dataframe(fn_ann_df.T)
            st.dataframe(fn_qu_df.T)
    # if sep_flag == True:
    #     st.write("별도")
    # else:
    #     st.write("연결")
    tab1, tab2, tab3 = st.tabs(["🗃 Valuation", "📈 Chart", "⏰ Valuation Chart"])
    with tab1:
        st.subheader("BED Valuation")
         ### PERR, PBRR 같이 보기 #########################################################################################
        with st.container():
            col1, col2, col3 = st.columns([30,2,30])
            with col1:
                # #PERR, PBRR
                fig = go.Figure(go.Indicator(
                mode = "number+delta",
                value = est_yield,
                title = {"text": "10년 기대수익률<br><span style='font-size:0.8em;color:gray'>최소 평균 ROE "+str(roe_min)+" 기준</span>"},
                domain = {'x': [0, 1], 'y': [0, 1]},
                delta = {'reference': 15.0}))
                st.plotly_chart(fig)
            with col2:
                st.write("")
            with col3:
                fig = go.Figure(go.Indicator(
                mode = "number+delta",
                value = longp_yield,
                title = {"text": "10년 기대수익률<br><span style='font-size:0.8em;color:gray'>현재ROE "+str(current_roe)+" 기준</span>"},
                domain = {'x': [0, 1], 'y': [0, 1]},
                delta = {'reference': 15.0}))
                st.plotly_chart(fig)
        html_br="""
        <br>
        """
        st.markdown(html_br, unsafe_allow_html=True)
        #######################################################
        rim_price = int(value_df.loc['적정주가(RIM)'].replace(',','').replace('원', ''))
        current_price = int(value_df.loc['현재주가'].replace(',','').replace('원', ''))
        if value_df.loc['컨센서스'] == 0:
            conse_price = int(value_df.loc['컨센서스'])
        else:
            conse_price = int(value_df.loc['컨센서스'].replace(',','').replace('원', ''))
        a_yield = float(value_df.iloc[7].replace('%',''))
        #MSCI korea PER: 하드 코딩 -> 추후 크롤링으로 수정해야함
        msci_fper = 10.80 
        col1, col2, col3 = st.columns(3)
        col1.metric(label="현재 주가", value = value_df.loc['현재주가'], delta='{0:,}'.format(int(current_price-proper_price)))
        col2.metric(label="매수 가격", value ='{0:,}'.format(int(proper_price)), delta='{0:,}'.format(int(proper_price-current_price)))
        col3.metric(label="컨센 주가", value =value_df.loc['컨센서스'], delta='{0:,}'.format(int(conse_price-current_price)))

        col1, col2, col3 = st.columns(3)
        col1.metric(label="DPS(mry)", value = value_df.loc['DPS(MRY)'])
        col2.metric(label="배당수익률", value =value_df.loc['배당수익률'])
        col3.metric(label="기대수익률(RIM)", value =value_df.loc['기대수익률(RIM)'])

        col1, col2, col3 = st.columns(3)
        col1.metric(label=value_df.index[11], value = value_df.iloc[11])
        if value_df.index[11] == "ttmEPS":
            col2.metric(label="ttmPER", value =value_df.loc['ttmPER'])
        else:
            col2.metric(label="예측PER", value =value_df.loc['ttmPER'])
        col3.metric("MSCI fPER", value =msci_fper)
        col1, col2, col3 = st.columns(3)
        col1.metric(label="5년PBR", value = value_df.loc['5년PBR'])
        col2.metric(label="5년PER", value =value_df.loc['5년PER'])
        col3.metric("PER/PBR평균", value =value_df.loc['PER/PBR평균'])
        col1, col2, col3 = st.columns(3)
        col1.metric(label="PBRR", value =value_df.loc['PBRR'], delta=round(float(value_df.loc['PBRR'])-2.0,2))
        col2.metric(label="PERR", value =value_df.loc['PERR'], delta=round(float(value_df.loc['PERR'])-2.0,2))
        col3.metric(label="ROE/r", value =value_df.loc['ROE/r'])
        col1, col2, col3 = st.columns(3)
        col1.metric(label="국고채3Y", value =str(bond3_y)+"%", delta=round(float(value_df.loc['PBRR'])-2.0,2))
        col2.metric(label="시장 평균 기대수익률", value = str(round(1/msci_fper*100,2))+"%", delta=round(est_yield-(1/msci_fper*100),2))
        col3.metric(label="회사채BBB-5Y", value = value_df.loc['요구수익률'])
        #############################################
        st.subheader("채권형 주식 Valuation")
        if np.isnan(roe_s[5]) == False:
            col1, col2, col3 = st.columns(3)
            col1.metric(label=f"{roe_sum}년 ROE 평균", value = roe_total)
            col2.metric(label="과거 5년 평균", value =roe_real)
            col3.metric(label="예측 3년 평균", value =roe_est)
            col1, col2, col3 = st.columns(3)
            col1.metric(label="BPS", value =value_df.loc['BPS'])
            col2.metric(label="현재 ROE", value =current_roe)
            col3.metric(label="평균 ROE", value =round(roe_mean,2))
            col1, col2, col3 = st.columns(3)
            col1.metric(label="추정 미래 ROE(MAX)", value = roe_max)
            col2.metric(label="10년 기대수익률(CAGR)", value =max_est_yield,  delta=round((max_est_yield-expect_yield*100),2))
            col3.metric(label="매수 가격", value ='{0:,}'.format(int(max_proper_price)), delta='{0:,}'.format(int(max_proper_price-current_price-max_proper_price)))
            col1, col2, col3 = st.columns(3)
            col1.metric(label="추정 미래 ROE(MIN)", value = roe_min)
            col2.metric(label="10년 기대수익률(CAGR)", value =min_est_yield,  delta=round((min_est_yield-expect_yield*100),2))
            col3.metric(label="매수 가격", value ='{0:,}'.format(int(min_proper_price)), delta='{0:,}'.format(int(min_proper_price-current_price)))
        else:
            col1, col2, col3 = st.columns(3)
            col1.metric(label="BPS", value =value_df.loc['BPS'])
            col2.metric(label="현재 ROE", value =current_roe)
            col3.metric(label="과거 5년 평균", value =roe_real)
        col1, col2, col3 = st.columns(3)
        col1.metric(label="추정 미래 ROE(평균)", value =round(roe_mean,2))
        col2.metric(label="10년 기대수익률(CAGR)", value =est_yield,  delta=round((est_yield-expect_yield*100),2))
        col3.metric(label="매수 가격", value ='{0:,}'.format(int(proper_price)), delta='{0:,}'.format(int(proper_price-current_price)))
        ################홍진채 적정 PBR 추가 22.12.23, 지속가능기간N = 10년
        st.subheader("홍진채 주식 Valuation")
        col1, col2, col3 = st.columns(3)
        col1.metric(label="현재 ROE", value =current_roe)
        col2.metric(label="지속가능기간", value =str(last_p)+"년")
        col3.metric(label="10년 기대수익률(CAGR)", value = longp_yield, delta=round((longp_yield-expect_yield*100),2))
        col1, col2, col3 = st.columns(3)
        col1.metric(label="PBR", value = value_df.loc['PBR'])
        col2.metric(label="적정PBR", value =target_pbr)
        col3.metric(label="PBR갭수익률", value =gap_yield, delta=round(current_pbr-target_pbr,2))
        #######################################################
        # with st.container():
        #     col1, col2, col3 = st.columns([30,2,30])
        #     with col1:
        #         #RIM price
        #         st.subheader("RIM price")
        #         fig = go.Figure(go.Indicator(
        #             #mode = "number+delta",
        #             mode = "gauge+number+delta",
        #             value = current_price, #Rim price
        #             #delta = {'reference': int(value_df.iloc[13,0]), 'relative': True},
        #             title = {'text': f"RIM<br>Price<br><span style='font-size:0.8em;color:gray'>(r={yeild})</span>"},
        #             domain = {'x': [0, 1], 'y': [0, 1]},
        #             gauge = {'shape': "bullet",
        #                     'threshold': {
        #                     'line': {'color': "red", 'width': 2},
        #                     'thickness': 0.75, 'value': rim_price}},
        #             delta = {'reference': rim_price, 'relative': True},
        #         ))
        #         fig.update_layout(height = 250)
        #         st.plotly_chart(fig)
        #     with col2:
        #         st.write("")
        #     with col3:  
        #         #Earnings Yeild: 기대수익률
        #         st.subheader("PBR 갭수익률")
        #         fig = go.Figure(go.Indicator(
        #             mode = "gauge+number+delta",
        #             value = round(float(value_df.iloc[13]),2),
        #             title = {"text": "Earnings<br>Yield<br><span style='font-size:0.8em;color:gray'>Demand Yield(15%)</span>"},
        #             domain = {'x': [0, 1], 'y': [0, 1]},
        #             gauge = {'shape': "bullet",
        #                     'threshold': {
        #                     'line': {'color': "red", 'width': 2},
        #                     'thickness': 0.75, 'value': round(float(value_df.iloc[14]),2)}},
        #             delta = {'reference': round(float(value_df.iloc[14]),2), 'relative': True}
        #         ))
        #         fig.update_layout(height = 250)
        #         st.plotly_chart(fig)
        #######################################################
        # 좀더 자세히
        n_url_f = 'https://navercomp.wisereport.co.kr/v2/company/c1010001.aspx?cmp_cd='+ ticker+ '&amp;target=finsum_more'
        fs_page = requests.get(n_url_f)
        navers_more = pd.read_html(fs_page.text)
        company_basic_info = navers_more[0]
        st.subheader("요약 보기")
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

    with tab2:
        with st.container():
            col1, col2, col3 = st.columns([30,2,30])
            with col1:
                # candlestick chart
                st.subheader("Candlestick Chart")
                now = datetime.datetime.now() +pd.DateOffset(days=-4000)
                start_date = '%s-%s-%s' % ( now.year, now.month, now.day)
                price_df = fdr.DataReader(ticker,start_date)
                chart.price_chart(ticker, com_name, price_df)
            with col2:
                st.write("")
            with col3:
                drawkorchart.dividend_chart(com_name, fn_ann_df.T)
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
            #PBR PER 차트
            drawkorchart.pbr_chart(com_name, fn_ann_df.T, fn_qu_df.T)
            #매출액이 차트
            drawkorchart.income_chart(ticker, com_name, fn_ann_df.T, fn_qu_df.T, sep_flag)
            #재무상태표 차트
            status_tables = getData.get_html_fnguide(ticker,1)
            status_ratio_tables = getData.get_html_fnguide(ticker,2)
            status_an = status_tables[2].set_index(status_tables[2].columns[0]).T #연간
            status_qu = status_tables[3].set_index(status_tables[3].columns[0]).T #분기
        except TypeError as te :
            st.error("다음과 같은 Error로 차트를 그릴 수 없습니다!", icon="🚨")
            st.write(te)
            #재무비율
        ratio_an = status_ratio_tables[0].set_index(status_ratio_tables[0].columns[0]).T #연간
        ratio_qu = status_ratio_tables[1].set_index(status_ratio_tables[1].columns[0]).T #분기
        drawkorchart.balance_chart(com_name, status_an, status_qu, ratio_an, ratio_qu)
        #현금 흐름 차트
        cf_tables = getData.get_html_fnguide(ticker,3)
        cf_an = status_tables[4].set_index(status_tables[4].columns[0]).T #연간
        cf_qu = status_tables[5].set_index(status_tables[5].columns[0]).T #분기
        with st.expander("See Raw Data"):
            try:
                #value_df = value_df.astype(float).fillna(0).round(decimals=2)
                st.dataframe(cf_an.astype(float).fillna(0).round(decimals=2).style.background_gradient(cmap, axis=0)\
                                            .format(precision=2, na_rep='MISSING', thousands=","))
                st.dataframe(cf_qu.astype(float).fillna(0).round(decimals=2).style.background_gradient(cmap, axis=0)\
                                    .format(precision=2, na_rep='MISSING', thousands=","))
            except ValueError :
                st.dataframe(cf_an)
                st.dataframe(cf_qu)
        #투자지표는 따로 크롤링
        invest_url = "https://comp.fnguide.com/SVO2/ASP/SVD_Invest.asp?pGB=1&gicode=A"+ ticker + "&cID=&MenuYn=Y&ReportGB=D&NewMenuID=105&stkGb=701"
        in_page = requests.get(invest_url)
        in_tables = pd.read_html(in_page.text)
        invest_table = in_tables[3].set_index(in_tables[3].columns[0]).T 
        try:
            invest_table['FCFF'] = invest_table['FCFF'].fillna(0).astype(int)
        except KeyError:
            pass
        with st.expander("See Raw Data"):
            try:
                st.dataframe(invest_table.astype(float).fillna(0).round(decimals=2).style.background_gradient(cmap, axis=0)\
                                    .format(precision=2, na_rep='MISSING', thousands=","))
            except ValueError :
                st.dataframe(invest_table)
        drawkorchart.cash_flow(com_name, cf_an, cf_qu, invest_table)
    with tab3:
        st.subheader("Valuation Change")
        utcnow= datetime.datetime.utcnow()
        time_gap= datetime.timedelta(hours=9)
        kor_time= utcnow+ time_gap
        now_date = kor_time.strftime('%Y%m%d')
        fn_history = getData.load_pykrx_data(ticker,now_date)
        with st.container():
            col1, col2, col3 = st.columns([30,2,30])
            with col1:
                drawkorchart.valuation_change(com_name, fn_history)
            with col2:
                st.write("")
            with col3:
                drawkorchart.pykrx_chart(com_name, fn_history)
        html_br="""
        <br>
        """
        st.markdown(html_br, unsafe_allow_html=True)
        with st.expander("See Raw Data"):
            try:
                st.dataframe(fn_history.astype(float).fillna(0).round(decimals=2).style.background_gradient(cmap, axis=0)\
                                            .format(precision=2, na_rep='MISSING', thousands=","))
            except ValueError :
                st.dataframe(fn_history)
        
if __name__ == "__main__":
    data_load_state = st.text('Loading KRX Company List...')
    tickers, krx = load_data()
    #basic_df['Close'] = str('{0:,}'.format(basic_df['Close']))+"원"
    #basic_df['Volumn'] = str('{0:,}'.format(basic_df['Volumn']))
    krx['Amount'] = round(krx['Amount']/100000000,1)
    krx['Marcap'] = round(krx['Marcap']/100000000,1)
    krx['Stocks'] = round(krx['Stocks']/100000000,1)
    krx.loc[:,"Close":"Low"].astype(float).fillna(0).round(decimals=2).format(precision=2, na_rep='MISSING', thousands=",")
    krx.loc[:,"Amount":"Stocks"].astype(float).fillna(0).round(decimals=2).format(precision=2, na_rep='MISSING', thousands=",")
    data_load_state.text("Done! (using st.cache)")
    # st.dataframe(tickers)
    # st.dataframe(krx)
    try:
        # etf = krx[krx['Sector'].isnull()]
        # krx = krx[~krx['Sector'].isnull()]
        com_name = st.sidebar.text_input("Company Name")

        if com_name == "":
            com_name = st.sidebar.selectbox(
                'Company Name or Code',
                krx['Name'].to_list() #tickers
            )

        comany_info = krx[krx['Name'] == com_name]
        company_name_ = comany_info.iloc[0,2]
        code = comany_info.iloc[0,0]
    except IndexError:
        comany_info = krx[krx['Name'].str.contains(com_name)]
        company_name_ = comany_info.iloc[0,2]
        code = comany_info.iloc[0,0]
    st.subheader('<'+company_name_+'> 회사 기본 정보')
    basic_df = comany_info.T
    st.table(basic_df)
    submit = st.sidebar.button('Analysis')

    if submit:
        run(code, company_name_)