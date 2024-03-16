import time
import datetime

import numpy as np
import pandas as pd
import requests
import json
from pandas_datareader import data as pdr
#yahoo orign
import yfinance as yfin
#yahoo overide
from yahoo_historical import Fetcher
import FinanceDataReader as fdr
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots
from matplotlib import font_manager, rc
import seaborn as sns
cmap = cmap=sns.diverging_palette(250, 5, as_cmap=True)

import streamlit as st
from alpha_vantage.fundamentaldata import FundamentalData as FD
import finterstellar as fs
import chart
import getData

pd.set_option('display.float_format', '{:.2f}'.format)


#API key
fd = FD(key='XA7Y92OE6LDOTLLE')
# fd = FD(key='CBALDIGECB3UFF5R')
key='CBALDIGECB3UFF5R'
# key='XA7Y92OE6LDOTLLE'
#sizipusx2@gmail.com = XA7Y92OE6LDOTLLE
#indiesoul2@gmail.com = CBALDIGECB3UFF5R

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
<h2 style="font-size:200%; color:#008080; font-family:Georgia"> 미국 상장 기업 기본 정보 <br>
<hr style= "  display: block;
  margin-top: 0.5em;
  margin-bottom: 0.5em;
  margin-left: auto;
  margin-right: auto;
  border-style: inset;
  border-width: 1.5px;"></h1>
"""

st.set_page_config(page_title="미국 상장 기업 정보 조회", page_icon="files/logo2.png", layout="wide")
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
marker_colors = ['rgb(27,38,81)', 'rgb(205,32,40)', 'rgb(22,108,150)', 'rgb(255,69,0)', 'rgb(237,234,255)']
template = 'ggplot2' 

## 특정 위치의 배경색 바꾸기
@st.cache_resource(ttl=datetime.timedelta(weeks=52))
def draw_color_cell(x,color):
    color = f'background-color:{color}'
    return color
# PER 값 변경    
@st.cache_resource(ttl=datetime.timedelta(weeks=52))
def change_per_value(x):
    if x >= 100 :
        x = 100
    elif x <= 0 :
        x = 0
    else:
        pass
    return x

@st.cache_resource(ttl=datetime.timedelta(weeks=52))
def load_data():
    # 나스닥거래소 상장종목 전체
    df_q= fdr.StockListing('NASDAQ')
    # NewYork 증권거래소 상장종목 전체
    df_n= fdr.StockListing('NYSE')
    # American 증권거래소 상장종목 전체
    df_a= fdr.StockListing('AMEX')
    sp500 = fdr.StockListing('S&P500')
    # 각 거래소 이름 추가
    df_q["Market"] = "NASDAQ"
    df_n["Market"] = "NYSE"
    df_a["Market"] = "AMEX"

    #세 데이터 모두 합치자
    #ticker_list = df_n.append(df_q).append(df_a)
    ticker_list = pd.concat([df_n, df_q, df_a])

    return ticker_list, sp500

def run(ticker, overview_df, fdr_df):
    #주가 캔들차트
    # from datetime import datetime
    # yes = datetime.now() + pd.DateOffset(days=-3)
    # end_date = '%s-%s-%s' % ( yes.year, yes.month, yes.day)
    # st.dataframe(fdr_df)
    #valuation 
    tab1, tab2, tab3 = st.tabs(["🗃 Valuation", "📈 Chart", "⏰ Band Chart"])
    with tab1:
        st.subheader("Valuation")
        close_price = overview_df.loc['Close']
        expect_yield = 0.15
        f_df, r_df, v_df, y_df, div_df = getData.get_valuation(ticker)# stock, close_price)
        roe_mean = round(v_df.iloc[-1,5:].mean()*100,2)
        roe_min = round(min(v_df.iloc[-1,5:])*100,2)
        current_roe = round(v_df.iloc[-1,5]*100,2)
        min_f_bps = min(y_df.iloc[-1,1:5])
        max_f_bps = max(y_df.iloc[-1,1:5])
        mean_f_bps = y_df.iloc[-1,4]
        current_f_bps = y_df.iloc[-1,2]
        try:
            min_proper_price = int(min_f_bps/(1+expect_yield)**10)
            max_proper_price = int(max_f_bps/(1+expect_yield)**10)
            mean_proper_price = int(mean_f_bps/(1+expect_yield)**10)
            current_proper_price = int(current_f_bps/(1+expect_yield)**10)
        except ValueError:
            min_proper_price = 0
            max_proper_price = 0
            mean_proper_price = 0
            current_proper_price = 0
        #평가일 현재 주가(종가)
        # from datetime import datetime
        # yes = datetime.now() + pd.DateOffset(days=-2)
        # end_date = '%s-%s-%s' % ( yes.year, yes.month, yes.day)
        #close_price = fdr.DataReader(ticker)
        # cprice = fdr.DataReader(ticker, end_date)
        #close_price = fs.get_price(ticker).iloc[-1,0]
        # st.dataframe(close_price)
        # st.dataframe(cprice)
        # st.write(f"close_price: {close_price}")
        with st.expander("See Raw Data"):
            try:
                col1, col2, col3 = st.columns([30,30,30])
                with col1:
                    st.dataframe(v_df.astype(float).fillna(0).round(decimals=2).style.background_gradient(cmap, axis=0)\
                                            .format(precision=2, na_rep='MISSING', thousands=","))
                with col2:
                    st.dataframe(y_df.astype(float).fillna(0).round(decimals=2).style.background_gradient(cmap, axis=0)\
                                    .format(precision=2, na_rep='MISSING', thousands=","))
                with col3:
                    st.dataframe(div_df.astype(float).fillna(0).round(decimals=2).style.background_gradient(cmap, axis=0)\
                                    .format(precision=2, na_rep='MISSING', thousands=","))
            except ValueError :
                st.subheader("financial statements")
                st.dataframe(f_df)
                col1, col2, col3 = st.columns([30,30,30])
                with col1:
                    st.subheader("Valuations")
                    st.dataframe(v_df)
                with col2:
                    st.subheader("Expecting Yield")
                    st.dataframe(y_df)
                with col3:
                    st.subheader("Dividends")
                    st.dataframe(div_df)
         ### PERR, PBRR 같이 보기 #########################################################################################
        with st.container():
            col1, col2, col3 = st.columns([30,30,30])
            with col1:
                # #PERR, PBRR
                fig = go.Figure(go.Indicator(
                mode = "number+delta",
                value = round(y_df.iloc[-1,5]*100,1),
                title = {"text": "10년 기대수익률<br><span style='font-size:0.8em;color:gray'>최소 ROE ("+str(roe_min)+"%) 기준</span>"},
                domain = {'x': [0, 1], 'y': [0, 1]},
                delta = {'reference': 15.0}))
                st.plotly_chart(fig)
            with col2:
                # #PERR, PBRR
                fig = go.Figure(go.Indicator(
                mode = "number+delta",
                value = round(y_df.iloc[-1,8]*100,1),
                title = {"text": "10년 기대수익률<br><span style='font-size:0.8em;color:gray'>평균 ROE ("+str(roe_mean)+"%) 기준</span>"},
                domain = {'x': [0, 1], 'y': [0, 1]},
                delta = {'reference': 15.0}))
                st.plotly_chart(fig)
            with col3:
                fig = go.Figure(go.Indicator(
                mode = "number+delta",
                value = round(y_df.iloc[-1,6]*100,1),
                title = {"text": "10년 기대수익률<br><span style='font-size:0.8em;color:gray'>현재ROE("+str(current_roe)+"%)기준</span>"},
                domain = {'x': [0, 1], 'y': [0, 1]},
                delta = {'reference': 15.0}))
                st.plotly_chart(fig)
        html_br="""
        <br>
        """
        st.markdown(html_br, unsafe_allow_html=True)
        ###========
        expect_yield = 15.0
        st.subheader("채권형 주식 Valuation")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric(label="현재 ROE", value =str(round(v_df.iloc[-1,5]*100,1))+"%")
        col2.metric(label="3년 평균", value =str(round(v_df.iloc[-1,6]*100,1))+"%")
        col3.metric(label="5년 평균", value =str(round(v_df.iloc[-1,7]*100,1))+"%")
        col4.metric(label="8년 평균", value =str(round(v_df.iloc[-1,8]*100,1))+"%")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric(label="현재 ROE 기준 기대수익률", value =str(round(y_df.iloc[-1,6]*100,1))+"%", delta=round((round(y_df.iloc[-1,6],1)-expect_yield),1))
        col2.metric(label="최소 ROE 기준 기대수익률", value =str(round(y_df.iloc[-1,5]*100,1))+"%", delta=round((round(y_df.iloc[-1,5],1)-expect_yield),1))
        col3.metric(label="최대 ROE 기준 기대수익률", value =str(round(y_df.iloc[-1,7]*100,1))+"%", delta=round((round(y_df.iloc[-1,7],1)-expect_yield),1))
        col4.metric(label="평균 ROE 기준 기대수익률", value =str(round(y_df.iloc[-1,8]*100,1))+"%", delta=round((round(y_df.iloc[-1,8],1)-expect_yield),1))
        try:
            col1, col2, col3, col4 = st.columns(4)
            col1.metric(label="현재 ROE 기준 매수가격", value = current_proper_price, delta=round((current_proper_price-close_price),2))
            col2.metric(label="최소 ROE 기준 매수가격", value =min_proper_price, delta=round((min_proper_price-close_price),2))
            col3.metric(label="최대 ROE 기준 매수가격", value =max_proper_price, delta=round((max_proper_price-close_price),2))
            col4.metric(label="평균 ROE 기준 매수가격", value =mean_proper_price, delta=round((mean_proper_price-close_price),2))
        except ValueError:
            col1, col2, col3, col4 = st.columns(4)
            col1.metric(label="현재 ROE 기준 매수가격", value = current_proper_price)
            col2.metric(label="최소 ROE 기준 매수가격", value =min_proper_price)
            col3.metric(label="최대 ROE 기준 매수가격", value =max_proper_price)
            col4.metric(label="평균 ROE 기준 매수가격", value =mean_proper_price)

        st.subheader("Fundamental")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric(label="현재 주가", value = close_price)
        try:
            col2.metric(label="PBR", value =round(overview_df.loc['priceToBook'].astype(float),2))
            col3.metric(label="TrailingPE", value =round(overview_df.loc['trailingPE'].astype(float),2))
            col4.metric(label="ForwardPE", value =round(overview_df.loc['forwardPE'].astype(float),2))
        except KeyError:
            col2.metric(label="PBR", value =round(overview_df.loc['priceToBook'].astype(float),2))
            col3.metric(label="TrailingPE", value =0)
            col4.metric(label="ForwardPE", value =0)
        col1, col2, col3, col4 = st.columns(4)
        try:
            col1.metric(label="DPS", value = round(overview_df.loc['dividendRate'].astype(float),2))
            col2.metric(label="DividendYield", value =str(round(overview_df.loc['dividendYield'].astype(float)*100,2))+"%")
            col3.metric(label="DPR", value =str(round(div_df.iloc[-1,1]*100,2))+"%")
            col4.metric(label="PayoutRatio", value =str(round(overview_df.loc["payoutRatio"].astype(float)*100,1))+"%")
        except ValueError:
            st.write("배당금을 지급하지 않습니다!") 
        except KeyError:
            st.write("배당금을 지급하지 않습니다!") 
            pass

    with tab2:
        #Alaph Vantage에서 가져오기
        earning_df, income_df, balance_df, cashflow_df = make_data(ticker, f_df)
        #Finterstella 에서 가져오기
        f_data_list = getData.get_stockanalysis_com(ticker)
        #stockanlyisis 에서 가져오기
        in_df = f_data_list[0]
        ba_df = f_data_list[1]
        cash_df = f_data_list[2] 
        ratio_df = f_data_list[3]
        with st.expander("See Raw Data"):
            try:
                col1, col2, col3, col4 = st.columns([30,30,30,30])
                with col1:
                    st.dataframe(income_df.astype(float).fillna(0).round(decimals=2).style.background_gradient(cmap, axis=0)\
                                            .format(precision=2, na_rep='MISSING', thousands=","))
                with col2:
                    st.dataframe(balance_df.astype(float).fillna(0).round(decimals=2).style.background_gradient(cmap, axis=0)\
                                    .format(precision=2, na_rep='MISSING', thousands=","))
                with col3:
                    st.dataframe(cashflow_df.astype(float).fillna(0).round(decimals=2).style.background_gradient(cmap, axis=0)\
                                    .format(precision=2, na_rep='MISSING', thousands=","))
                with col4:
                    st.dataframe(ratio_df.astype(float).fillna(0).round(decimals=2).style.background_gradient(cmap, axis=0)\
                                    .format(precision=2, na_rep='MISSING', thousands=","))
            except ValueError :
                st.subheader("financial statements")
                col1, col2, col3, col4 = st.columns([30,30,30, 30])
                with col1:
                    st.subheader("Income")
                    st.dataframe(income_df)
                with col2:
                    st.subheader("Balance Sheet")
                    st.dataframe(balance_df)
                with col3:
                    st.subheader("Cash Flow")
                    st.dataframe(cashflow_df) 
                with col4:
                    st.subheader("Ratio")
                    st.dataframe(ratio_df)    
        with st.expander("See Raw Data2"):
            try:
                col1, col2, col3, col4 = st.columns([30,30,30,30])
                with col1:
                    st.dataframe(in_df.astype(float).fillna(0).round(decimals=2).style.background_gradient(cmap, axis=0)\
                                            .format(precision=2, na_rep='MISSING', thousands=","))
                with col2:
                    st.dataframe(ba_df.astype(float).fillna(0).round(decimals=2).style.background_gradient(cmap, axis=0)\
                                    .format(precision=2, na_rep='MISSING', thousands=","))
                with col3:
                    st.dataframe(cash_df.astype(float).fillna(0).round(decimals=2).style.background_gradient(cmap, axis=0)\
                                    .format(precision=2, na_rep='MISSING', thousands=","))
                with col4:
                    st.dataframe(ratio_df.astype(float).fillna(0).round(decimals=2).style.background_gradient(cmap, axis=0)\
                                    .format(precision=2, na_rep='MISSING', thousands=","))
            except ValueError :
                st.subheader("financial statements")
                col1, col2, col3, col4 = st.columns([30,30,30, 30])
                with col1:
                    st.subheader("Income")
                    st.dataframe(in_df)
                with col2:
                    st.subheader("Balance Sheet")
                    st.dataframe(ba_df)
                with col3:
                    st.subheader("Cash Flow")
                    st.dataframe(cash_df) 
                with col4:
                    st.subheader("Ratio")
                    st.dataframe(ratio_df)    

        com_name_df = tickers[tickers['Symbol'] == input_ticker ]
        # st.write(com_name_df)
        com_name = com_name_df.iloc[0,1]   
        st.subheader(com_name + " Fundamental Chart")
        ##주가 EPS
        # price_df = fdr.DataReader(input_ticker, earning_df.iloc[0,0], earning_df.iloc[-1,0])['Adj Close'].to_frame()
        price_df = fs.get_price(input_ticker, earning_df.iloc[0,0], earning_df.iloc[-1,0])
        price_df.columns = ['Close']
        price_df.index = pd.to_datetime(price_df.index, format='%Y-%m-%d')
        # income_df = pd.merge(income_df, price_df, how="inner", left_index=True, right_index=True)
        earning_df['reportedDate'] = pd.to_datetime(earning_df['reportedDate'], format='%Y-%m-%d')
        band_df = pd.merge_ordered(earning_df, price_df, how="left", left_on='reportedDate', right_on=price_df.index, fill_method='ffill')
        band_df['ttmEPS'] = band_df['reportedEPS'].rolling(4).sum()
        earning_df['ttmEPS'] = earning_df['reportedEPS'].rolling(4).sum()
        earning_df['EPS Change'] = round(earning_df['ttmEPS'].pct_change(5)*100,2)
        earning_df['EPS_5y'] = round(earning_df['ttmEPS'].pct_change(21)*100,2)
        earning_df['EPS_10y'] = round(earning_df['ttmEPS'].pct_change(41)*100,2)
        band_df.set_index('reportedDate', inplace=True)
        chart.earning_chart(input_ticker, earning_df, price_df)
            
        html_br="""
        <br>
        """
        st.markdown(html_br, unsafe_allow_html=True)
        
        # #EPS 증감률
        # eps_10 = band_df.iloc[-41:, -1]
        # eps_10_growth = (eps_10.iloc[-1]/eps_10.iloc[0])**1/10 -1
        # eps_5 = band_df.iloc[-21:, -1]
        # eps_5_growth = (eps_5.iloc[-1]/eps_10.iloc[0])**1/5 -1
        # eps_3 = band_df.iloc[-13:, -1]
        # eps_3_growth = (eps_3.iloc[-1]/eps_10.iloc[0])**1/3 -1
        # eps_1 = band_df.iloc[-5:, -1]
        # eps_1_growth = (eps_1.iloc[-1]/eps_10.iloc[0])**1/1 -1
        # st.write("10Y EPS Growth")
        # st.write(eps_10_growth)
        # st.write("5Y EPS Growth")
        # st.write(eps_5_growth)
        # st.write("3Y EPS Growth")
        # st.write(eps_3_growth)
        # st.write("1Y EPS Growth")
        # st.write(eps_1_growth)
        html_br="""
        <br>
        """
        st.markdown(html_br, unsafe_allow_html=True)
        #챠트 기본 설정
        # colors 
        marker_colors = ['#34314c', '#47b8e0', '#ff7473', '#ffc952', '#3ac569']
        # marker_colors = ['rgb(27,38,81)', 'rgb(205,32,40)', 'rgb(22,108,150)', 'rgb(255,69,0)', 'rgb(237,234,255)']
        template = 'ggplot2' #"plotly", "plotly_white", "plotly_dark", "ggplot2", "seaborn", "simple_white", "none"
        # Profit and Cost
        st.subheader('Profit, Cost, Growth')
        with st.container():
            col1, col2, col3 = st.columns([30,2,30])
            with col1:
                x_data = income_df.index
                title = com_name + '('  + input_ticker + ') <b>Profit & Cost</b>'
                titles = dict(text= title, x=0.5, y = 0.85, xanchor='center', yanchor= 'top') 
                fig = make_subplots(specs=[[{'secondary_y': True}]]) 
                y_data_bar1 = ['Revenue', 'Operating Income', 'Net Income']
                y_data_line1 = ['Gross Margin', 'Operating Margin', 'Profit Margin']

                for y_data, color in zip(y_data_bar1, marker_colors) :
                    fig.add_trace(go.Bar(name = y_data, x = x_data, y = income_df[y_data],marker_color= color), secondary_y = False) 
                
                for y_data, color in zip(y_data_line1, marker_colors): 
                    fig.add_trace(go.Scatter(mode='lines+markers+text', 
                                                name = y_data, x =  x_data, y= round(r_df.loc[:,y_data]*100,2),
                                                text= round(r_df[y_data]*100,1), textposition = 'top center', marker_color = color),
                                                secondary_y = True)
                fig.update_traces(texttemplate='%{text:.3s}') 
                fig.update_yaxes(title_text='Income', range=[0, max(income_df.loc[:,y_data_bar1[0]])*2], secondary_y = False)
                fig.update_yaxes(title_text='Margin', range=[-max(r_df.loc[:,y_data_line1[0]]), max(r_df.loc[:,y_data_line1[0]])* 1.2], ticksuffix="%", secondary_y = True)
                fig.update_yaxes(showticklabels= True, showgrid = False, zeroline=True, tickprefix="$")
                fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template)
                fig.update_layout(template="myID")
                st.plotly_chart(fig)
            with col2:
                st.write("")
            with col3:
                # 마진율과 성장률
                x_data = income_df.index
                title = com_name + '('  + input_ticker + ') Margin & Growth Rate' 
                titles = dict(text= title, x=0.5, y = 0.85, xanchor='center', yanchor= 'top') 
                fig = make_subplots(specs=[[{'secondary_y': True}]]) 
                y_data_line2 = ['GPM', 'OPM', 'NPM']
                y_data_bar2 = ['TR Change', 'OI Change', 'NI Change']

                for y_data, color in zip(y_data_line2, marker_colors): 
                    fig.add_trace(go.Scatter(mode='lines+markers+text', name = y_data, x = x_data, y=round(income_df[y_data],2),
                    text = round(income_df[y_data],1), textposition = 'top center', marker_color = color),
                    secondary_y = True)

                for y_data, color in zip(y_data_bar2, marker_colors) :
                    fig.add_trace(go.Bar(name = y_data, x = x_data, y = round(income_df[y_data],2), 
                                        text = round(income_df[y_data],1), textposition = 'outside', marker_color= color), secondary_y = False)

                fig.update_traces(texttemplate='%{text:.3s}') 
                fig.update_yaxes(title_text='Growth Rate', range=[0, max(income_df.loc[:,y_data_bar2[0]])*2], secondary_y = False)
                fig.update_yaxes(title_text='Margin Rate', range=[-max(income_df.loc[:,y_data_line2[0]]), max(income_df.loc[:,y_data_line2[0]])* 1.2], secondary_y = True)
                fig.update_yaxes(showticklabels= True, showgrid = False, zeroline=True, ticksuffix="%")
                fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template)
                fig.update_layout(template="myID")
                st.plotly_chart(fig)
        
        html_br="""
        <br>
        """
        st.markdown(html_br, unsafe_allow_html=True)
        #부채비율, 유동비율, 당좌비율
        st.subheader('Asset, Liabilities, ShareholderEquity')
        with st.container():
            col1, col2, col3 = st.columns([30,2,30])
            with col1:
                x_data = balance_df.index
                title = com_name + '('  + input_ticker + ') <b>Asset & Liabilities</b>'
                titles = dict(text= title, x=0.5, y = 0.85, xanchor='center', yanchor= 'top') 
                fig = make_subplots(specs=[[{'secondary_y': True}]]) 
                #y_data_bar3 = ['totalAssets', 'totalLiabilities', 'totalShareholderEquity']
                y_data_bar3 = ['totalLiabilities', 'totalShareholderEquity']
                y_data_line3 = ['Debt/Equity', 'QuickRatio', '유동부채/자기자본']

                for y_data, color in zip(y_data_bar3, marker_colors) :
                    fig.add_trace(go.Bar(name = y_data, x = x_data, y = balance_df[y_data], 
                                        text = balance_df[y_data], textposition = 'outside', marker_color= color), secondary_y = False) 
                
                for y_data, color in zip(y_data_line3, marker_colors): 
                    fig.add_trace(go.Scatter(mode='lines+markers+text', 
                                                name = y_data, x =  x_data, y= balance_df.loc[:,y_data],
                                                text= balance_df[y_data], textposition = 'top center', marker_color = color),
                                                secondary_y = True)
                fig.update_traces(texttemplate='%{text:.3s}') 
                fig.update_yaxes(range=[0, max(balance_df.loc[:,y_data_bar3[0]])*2], secondary_y = False)
                fig.update_yaxes(range=[-max(balance_df.loc[:,y_data_line3[0]]), max(balance_df.loc[:,y_data_line3[0]])* 1.2], secondary_y = True)
                fig.update_yaxes(title_text="Liabilities Rate", showticklabels= True, showgrid = True, zeroline=True, zerolinecolor='LightPink', ticksuffix="%", secondary_y = True)
                fig.update_yaxes(title_text= "Asset", showticklabels= True, showgrid = False, zeroline=True, tickprefix="$", secondary_y = False)
                fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template)
                fig.update_layout(barmode='stack')
                fig.update_layout(template="myID")
                st.plotly_chart(fig)
            with col2:
                st.write("")
            with col3:
                #무형자산총자금비율, 현금자산비율
                x_data = balance_df.index
                title = com_name + '('  + input_ticker + ') <b>IntangibleAssets & Cash And ShortTermInvestments</b>'
                titles = dict(text= title, x=0.5, y = 0.85, xanchor='center', yanchor= 'top') 
                fig = make_subplots(specs=[[{'secondary_y': True}]]) 
                y_data_bar4 = ['무형자산비율', '현금성자산비율']
                y_data_bar4_name = ['intangible/Assets', 'Cash/Assets']
                fig.add_trace(go.Bar(name = y_data_bar4_name[1], x = x_data, y = round(balance_df[y_data_bar4[1]],2), 
                                    text = round(balance_df[y_data_bar4[1]],1), textposition = 'outside', 
                                    marker_color= marker_colors[0]), secondary_y = False) 
                fig.add_trace(go.Scatter(mode='lines+markers+text', 
                                                name = y_data_bar4_name[0], x =  x_data, y= round(balance_df[y_data_bar4[0]],2),
                                                text= round(balance_df[y_data_bar4[0]],1), textposition = 'top center', marker_color = marker_colors[2]),
                                                secondary_y = True)
                fig.update_traces(texttemplate='%{text:.3s}') 
                fig.update_yaxes(title_text="Cash/Assets", showticklabels= True, showgrid = True, zeroline=True, ticksuffix="%", secondary_y = False)
                fig.update_yaxes(title_text="intangible/Assets", showticklabels= True, showgrid = False, zeroline=True, ticksuffix="%", secondary_y = True)
                fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template)
                fig.update_layout(template="myID")
                st.plotly_chart(fig)
        html_br="""
        <br>
        """
        st.markdown(html_br, unsafe_allow_html=True)

        #현금흐름
        #영업활동현금흐름, 순이익, 투자활동현금흐름, 재무활동현금흐름
        st.subheader('Cash Flow')
        with st.container():
            col1, col2, col3 = st.columns([30,2,30])
            with col1:
                x_data = cashflow_df.index
                title = com_name + '('  + input_ticker + ') <b>Cash Flow Statement</b>'
                titles = dict(text= title, x=0.5, y = 0.85, xanchor='center', yanchor= 'top')
                fig = make_subplots(specs=[[{'secondary_y': True}]]) 
                y_data_bar5 = ['Operating Cash Flow', 'Financing Cash Flow', 'Investing Cash Flow']
                y_data_line5 = ['FCF']

                for y_data, color in zip(y_data_bar5, marker_colors) :
                    fig.add_trace(go.Bar(name = y_data, x = x_data, y = cashflow_df[y_data], 
                                        text= cashflow_df[y_data], textposition = 'outside', marker_color= color), secondary_y = False) 
                for y_data, color in zip(y_data_line5, marker_colors): 
                            fig.add_trace(go.Scatter(mode='lines+markers+text', 
                                                        name = y_data, x =  x_data, y= cashflow_df.loc[:,y_data],
                                                        text= cashflow_df[y_data], textposition = 'top center', marker_color = color),
                                                        secondary_y = True)
                fig.add_trace(go.Bar(name = 'Net Income', x = x_data, y = income_df['Net Income'], 
                                    text= income_df['Net Income'], textposition = 'outside', marker_color= 'rgb(237,234,255)'), secondary_y = False)
                fig.update_traces(texttemplate='%{text:.3s}') 
                fig.update_yaxes(title_text='Cash Flow', range=[0, max(cashflow_df.loc[:,y_data_bar5[0]])*2], secondary_y = False)
                fig.update_yaxes(title_text='FCF', range=[-max(cashflow_df.loc[:,y_data_line5[0]]), max(cashflow_df.loc[:,y_data_line5[0]])* 1.2], secondary_y = True)
                fig.update_yaxes(showticklabels= True, showgrid = False, zeroline=True, tickprefix="$", secondary_y = False)
                fig.update_yaxes(showticklabels= True, showgrid = True, zeroline=True, tickprefix="$", secondary_y = True)
                fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template)
                fig.update_layout(template="myID")
                st.plotly_chart(fig)

            with col2:
                st.write("")
            with col3:
                x_data = v_df.index
                title = com_name + '('  + input_ticker + ') <b>BPS and ROE</b>'
                titles = dict(text= title, x=0.5, y = 0.85, xanchor='center', yanchor= 'top')
                fig = make_subplots(specs=[[{'secondary_y': True}]]) 
                y_data_bar6 = ['BPS']
                y_data_line6 = ['ROE']

                for y_data, color in zip(y_data_bar6, marker_colors) :
                    fig.add_trace(go.Bar(name = y_data, x = x_data, y = round(v_df[y_data],2), 
                                        text= round(v_df[y_data],1), textposition = 'outside', marker_color= color), secondary_y = False) 
                for y_data, color in zip(y_data_line6, marker_colors): 
                            fig.add_trace(go.Scatter(mode='lines+markers+text', 
                                                        name = y_data, x =  x_data, y= round(v_df.loc[:,y_data]*100,2),
                                                        text= round(v_df[y_data]*100,2), textposition = 'top center', marker_color = marker_colors[2]),
                                                        secondary_y = True)
                fig.update_traces(texttemplate='%{text:.3s}') 
                fig.update_yaxes(title_text='BPS', range=[0, max(v_df.loc[:,y_data_bar6[0]])*2], secondary_y = False)
                # fig.update_yaxes(title_text='ROE', range=[-max(v_df.loc[:,y_data_line6[0]]), max(v_df.loc[:,y_data_line6[0]])* 1.2], secondary_y = True)
                fig.update_yaxes(title_text='ROE', secondary_y = True)
                fig.update_yaxes(showticklabels= True, showgrid = False, zeroline=True, tickprefix="$", secondary_y = False)
                fig.update_yaxes(showticklabels= True, showgrid = True, zeroline=True, ticksuffix="%", secondary_y = True)
                fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template)
                fig.update_layout(template="myID")
                st.plotly_chart(fig)
        html_br="""
        <br>
        """
        st.markdown(html_br, unsafe_allow_html=True)
    with tab3:
        st.subheader("Band Chart")
        ####### Dividend Band ##############
        # 여기에 한짜리 고평가/ 저평가 그래프를 넣기
        # 데이터 만들기
        # create unix timestamp representing January 1st, 2007
        timestamp = time.mktime(datetime.datetime(1990, 1, 1).timetuple())
        data = Fetcher(ticker, timestamp)
        c_data = data.get_historical()
        div = data.get_dividends()
        merged_df = pd.merge(c_data[['Date', 'Adj Close']], div[['Date', 'Dividends']], on='Date', how='inner')
        merged_df['ttmDiv'] = merged_df['Dividends'].rolling(window=4).sum()
        merged_df = merged_df.iloc[3:]
        last_row_df = pd.DataFrame(merged_df.iloc[-1]).transpose()
        last_row_df.iloc[0,0] = c_data.iloc[-1,0]
        last_row_df.iloc[0,1] = c_data.iloc[-1,-2]
        df = pd.concat([merged_df, last_row_df])
        df.loc[:,'DY'] = df['ttmDiv']/df['Adj Close']*100
        dy_max = df['DY'].max()
        dy_min = df['DY'].min()
        dy_mid = (dy_max+dy_min)/2
        df.loc[:,'High'] = df['ttmDiv']/dy_min*100
        df.loc[:,'Low'] = df['ttmDiv']/dy_max*100
        df.loc[:,'Mid'] = df['ttmDiv']/dy_mid*100
        df['Date'] = pd.to_datetime(df['Date']) 
        df.set_index('Date', inplace=True)
        df = df.astype(float).round(decimals=2)
        y_avg = df['DY'].mean()

        chart.div_band(ticker, df, y_avg)

        with st.container():
            col1, col2, col3 = st.columns([30,2,30])
            with col1:
                chart.dividend_chart(input_ticker, com_name, div_df)
            with col2:
                st.write("")
            with col3:
                chart.dividend_chart_right(input_ticker, com_name, div_df)
        ########### PER/PBR################
        try:
            #band chart
            #PBR 밴드 위해
            pbr_df = pd.DataFrame()
            pbr_df.loc[:,'shares'] = balance_df['commonStockSharesOutstanding']
            pbr_df.loc[:,'Equity'] = balance_df['totalShareholderEquity']
            pbr_df.loc[:,'reportedDate'] = earning_df['reportedDate']
            pbr_df = pd.merge_ordered(pbr_df, price_df, how="left", left_on='reportedDate', right_on=price_df.index, fill_method='ffill')
            pbr_df.set_index('reportedDate', inplace=True)

            
            st.subheader('Band Chart')
            with st.expander("See Raw Data"):
                with st.container():
                    col1, col2, col3 = st.columns([30,2,30])
                    with col1:
                        st.subheader('PER Band Raw Data') 
                        st.dataframe(band_df.astype(float).fillna(0).round(decimals=2).style.background_gradient(cmap, axis=0)\
                                                .format(precision=2, na_rep='MISSING', thousands=","))
                    with col2:
                        st.write("")
                    with col3:
                        st.subheader('PBR Band Raw Data') 
                        st.dataframe(pbr_df.astype(float).fillna(0).round(decimals=2).style.background_gradient(cmap, axis=0)\
                                                .format(precision=2, na_rep='MISSING', thousands=","))
            with st.container():
                col1, col2, col3 = st.columns([30,2,30])
                with col1:
                    chart.visualize_PER_band(input_ticker, com_name, band_df)
                with col2:
                    st.write("")
                with col3:
                    chart.visualize_PBR_band(input_ticker, com_name, pbr_df)
        except IndexError :
            st.write("pbr band error occurred")

        #조회시 1분 기다려야 함
        st.warning('Please Wait One minute Before Searching Next Company!!!')
        my_bar = st.progress(0)
        for percent_complete in range(100):
            time.sleep(0.6)
            my_bar.progress(percent_complete + 1)
        




def make_df(funct, ticker):
    API_URL = "https://www.alphavantage.co/query" 
    choice = "quarterlyReports" #annualReports : quarterlyReports 둘다 5년치 데이터
    func = funct
    data = { 
        "function": func, 
        "symbol": ticker,
        "outputsize" : "compact",
        "datatype": "json", 
        "apikey": key} 
    response = requests.get(API_URL, data) 
    response_json = response.json() # maybe redundant

    if func == 'TIME_SERIES_DAILY' :
        df = pd.DataFrame.from_dict(response_json['Time Series (Daily)'], orient= 'index')
        df.index =  pd.to_datetime(df.index, format='%Y-%m-%d')
        df = df.rename(columns={ '1. open': 'Open', '2. high': 'High', '3. low': 'Low', '4. close': 'Close', '5. volume': 'Volume'})
        df = df.astype({'Open': 'float64', 'High': 'float64', 'Low': 'float64','Close': 'float64','Volume': 'float64',})
        df = df[[ 'Open', 'High', 'Low', 'Close', 'Volume']]
    elif func == 'INCOME_STATEMENT':
        df = pd.DataFrame(response_json[choice])
        df = df.iloc[::-1]
        df.set_index('fiscalDateEnding', inplace=True)
        df = pd.to_datetime(df.index, format='%Y-%m-%d')
        # print(df)
    elif func == 'BALANCE_SHEET':
        df = pd.DataFrame(response_json[choice])
        df = df.iloc[::-1]
        df.set_index('fiscalDateEnding', inplace=True)
        df = pd.to_datetime(df.index, format='%Y-%m-%d')
    elif func == 'CASH_FLOW':
        df = pd.DataFrame(response_json[choice])
        df = df.iloc[::-1]
        df.set_index('fiscalDateEnding', inplace=True)
        df = pd.to_datetime(df.index, format='%Y-%m-%d')
    elif func == 'EARNINGS':
        df = pd.DataFrame(response_json['quarterlyEarnings'])
        df = df.iloc[::-1]
        df.set_index('fiscalDateEnding', inplace=True)
        df.index =  pd.to_datetime(df.index, format='%Y-%m-%d')
        df['reportedEPS'] = df['reportedEPS'].replace('None','0').astype(float).round(3)
        df['estimatedEPS'] = df['estimatedEPS'].replace('None','0').astype(float).round(4)
        df['surprise'] = df['surprise'].replace('None','0').astype(float).round(4)
        df['surprisePercentage'] = df['surprisePercentage'].replace('None','0').astype(float).round(2)

    return df

def make_data(ticker, f_df):   
    edf = make_df('EARNINGS',ticker) #get earning sheet quarterly data 1번
    # income = make_df('INCOME_STATEMENT',ticker) #get income statement quarterly data
    # cashflow = make_df('BALANCE_SHEET',ticker) #get cash flow quarterly data
    # balance = make_df('CASH_FLOW',ticker) #get balance sheet quarterly data
    
    #income_statement
    # income, meta_data = fd.get_income_statement_quarterly(ticker) #2번
    # income.set_index('fiscalDateEnding', inplace=True)
    # income.index =  pd.to_datetime(income.index, format='%Y-%m-%d')
    # income = income.iloc[::-1]
    sub = ['Revenue', 'Gross Profit', 'Operating Income', 'EBIT', 'Net Income']
    income_df = f_df[sub].replace('None','0').astype(float).round(0)
    #연매출액 증가율
    gp_cagr = (income_df['Revenue'].iloc[-1]/income_df['Revenue'].iloc[0])**(1/5) -1

    income_df['GPM'] = income_df['Gross Profit'] / income_df['Revenue']*100
    income_df['OPM'] = income_df['Operating Income'] / income_df['Revenue']*100
    income_df['NPM'] = income_df['Net Income'] / income_df['Revenue']*100

    income_df['TR Change'] = income_df['Revenue'].pct_change()*100
    income_df['OI Change'] = income_df['Operating Income'].pct_change()*100
    income_df['NI Change'] = income_df['Net Income'].pct_change()*100

    #balance sheet 
    balance, meta_data = fd.get_balance_sheet_quarterly(ticker) #3번
    balance.set_index('fiscalDateEnding', inplace=True)
    balance.index =  pd.to_datetime(balance.index, format='%Y-%m-%d')
    balance = balance.iloc[::-1]
    sub = ['totalAssets', 'intangibleAssets', 'totalLiabilities', 'totalShareholderEquity', 'retainedEarnings', 'totalCurrentLiabilities', \
         'totalCurrentAssets', 'inventory',  \
         'totalNonCurrentAssets', 'cashAndShortTermInvestments', 'commonStockSharesOutstanding']
    balance_df = balance[sub].replace('None','0').astype(float).round(0)
    #부채비율
    balance_df['Debt/Equity'] = balance_df['totalLiabilities'] / balance_df['totalShareholderEquity']*100
    #유동비율
    balance_df['CurrentRatio'] = balance_df['totalCurrentAssets'] / balance_df['totalCurrentLiabilities']*100
    #당좌비율(당좌자산(유동자산-재고자산)/유동부채)
    balance_df['QuickRatio'] = (balance_df['totalCurrentAssets'] - balance_df['inventory'])/ balance_df['totalCurrentLiabilities']*100
    #유동부채비율
    balance_df['유동부채/자기자본'] = balance_df['totalCurrentLiabilities'] / balance_df['totalShareholderEquity']*100
    #무형자산총자산비율 15%미만
    balance_df['무형자산비율'] = balance_df['intangibleAssets'] / balance_df['totalAssets']*100
    #현금자산비율
    balance_df['현금성자산비율'] = balance_df['cashAndShortTermInvestments'] / balance_df['totalAssets']*100
    
    #cash-flow 
    # cashflow, meta_data = fd.get_cash_flow_quarterly(ticker) #4번
    # cashflow.set_index('fiscalDateEnding', inplace=True)
    # cashflow.index =  pd.to_datetime(cashflow.index, format='%Y-%m-%d')
    # cashflow = cashflow.iloc[::-1]
    sub = ['Net Income', 'Operating Cash Flow', 'Financing Cash Flow',  'Capital Expenditure', 'Investing Cash Flow']
    cashflow_df = f_df[sub].replace('None','0').astype(float).round(0)
    cashflow_df["FCF"] = cashflow_df['Operating Cash Flow'] - cashflow_df['Capital Expenditure']

    return edf, income_df, balance_df, cashflow_df


        

if __name__ == "__main__":
    data_load_state = st.text('Loading All Company data...')
    tickers, sp500 = load_data()
    # ticker_list = tickers['Symbol'].values.tolist()
        # st.dataframe(tickers)
    data_load_state.text("Done! (using st.cache)")
    market = st.sidebar.radio(
            label = "Choose the Market", 
            options=('S&P500', 'NYSE:3270개', 'NASDAQ:4466개', 'AMEX:325'),
            index = 0,
            horizontal= True)
    if market == "S&P500":
        ticker_list = sp500['Symbol'].to_list()
    elif market == "NYSE:3270개" :
        ticker_slice = tickers[tickers['Market'] == 'NYSE']  
        ticker_list = ticker_slice['Symbol'].to_list()
    elif market == "NASDAQ:4466개" :
        ticker_slice = tickers[tickers['Market'] == 'NASDAQ']
        ticker_list = ticker_slice['Symbol'].to_list()
    else:
        ticker_slice = tickers[tickers['Market'] == 'AMEX']
        ticker_list = ticker_slice['Symbol'].to_list()
    input_ticker = st.sidebar.text_input("ticker").upper()
    
    #import random
    #input_ticker = random.choice(ticker_list)
    
    # ticker_list = [ "SENEA", "IMKTA", "KBAL", "CMC", \
    #                 "APT","AMCX","BIIB", "BIG", "CI", "CPRX", "CHRS", "CSCO","CVS","DHT", "EURN", "HRB", "PRDO", \
    #                 "MO", "T", "O", "OMC", "SBUX", \
    #                 "MSFT", "MMM", "INVA", "SIGA", "WLKP", "VYGR", "KOF", "WSTG", "LFVN", "SUPN"]

    if input_ticker == "":
        input_ticker = st.sidebar.selectbox(
            'Ticker', ticker_list
        )
    
    input_ticker = input_ticker.upper()
    #Summary 데이터 가져오기    알파벤티지에서 야후 파이낸스로 변경: 24.3.10
    #OV = fd.get_company_overview(input_ticker) #5번
    # split_OV=OV[0]
    # ov_df = pd.json_normalize(split_OV)
    # overview_df = ov_df.T
    yfin.pdr_override()
    ticker = yfin.Ticker(input_ticker)
    overview_df = pd.DataFrame.from_dict(ticker.info, orient='index')
    overview_df.columns = ['기본 정보']
    overview_df = overview_df.drop("companyOfficers")
    st.header(input_ticker)
    # fdr_df = fdr.DataReader(input_ticker,start='1996-01-02')
    fdr_df = pdr.get_data_yahoo(input_ticker,start='2000-01-02')
    #st.dataframe(fdr_df)
    fdr_df['ma5'] = fdr_df['Adj Close'].rolling(window=5).mean()
    fdr_df['ma20'] = fdr_df['Adj Close'].rolling(window=20).mean()
    fdr_df['ma240'] = fdr_df['Adj Close'].rolling(window=240).mean()
    # st.dataframe(ov_df)
    # st.dataframe(fdr_df)
    overview_df.loc['Close'] = round(fdr_df.iloc[-1,4],2)
    st.table(overview_df)
    chart.price_chart(input_ticker, overview_df.iloc[2,0], fdr_df)

    html_br="""
    <br>
    """
    st.markdown(html_br, unsafe_allow_html=True)
    submit = st.sidebar.button('Run app')
    if submit:
        run(input_ticker, overview_df,fdr_df)