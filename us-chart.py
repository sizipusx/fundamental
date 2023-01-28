import time
from datetime import datetime

import numpy as np
import pandas as pd
import requests
import json
from pandas.io.json import json_normalize
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots
from matplotlib import font_manager, rc
import seaborn as sns
cmap = cmap=sns.diverging_palette(250, 5, as_cmap=True)

import streamlit as st
from alpha_vantage.fundamentaldata import FundamentalData as FD
import FinanceDataReader as fdr
import finterstellar as fs
import chart
import getData

pd.set_option('display.float_format', '{:.2f}'.format)
now = datetime.now() +pd.DateOffset(days=-1)
today = '%s-%s-%s' % ( now.year, now.month, now.day)

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

@st.cache
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
    ticker_list = df_n.append(df_q).append(df_a)

    return ticker_list, sp500

def run(ticker, overview_df):
    
    #valuation 
    tab1, tab2, tab3 = st.tabs(["🗃 Valuation", "📈 Chart", "⏰ Valuation Chart"])
    with tab1:
        st.subheader("Valuation")
        expect_yield = 0.15
        f_df, v_df, y_df, div_df = getData.get_finterstellar(ticker)
        roe_mean = round(v_df.iloc[-1,4:].mean()*100,2)
        current_roe = round(v_df.iloc[-1,4]*100,2)
        min_f_bps = min(y_df.iloc[-1,:4])
        max_f_bps = max(y_df.iloc[-1,:4])
        mean_f_bps = y_df.iloc[-1,3]
        current_f_bps = y_df.iloc[-1,1]
        min_proper_price = int(min_f_bps/(1+expect_yield)**10)
        max_proper_price = int(max_f_bps/(1+expect_yield)**10)
        mean_proper_price = int(mean_f_bps/(1+expect_yield)**10)
        current_proper_price = int(current_f_bps/(1+expect_yield)**10)
        #평가일 현재 주가(종가)
        # from datetime import datetime
        # yes = datetime.now() + pd.DateOffset(days=-2)
        # end_date = '%s-%s-%s' % ( yes.year, yes.month, yes.day)
        #close_price = fdr.DataReader(ticker)
        # cprice = fdr.DataReader(ticker, end_date)
        close_price = fs.get_price(ticker).iloc[-1,0]
        # st.dataframe(close_price)
        # st.dataframe(cprice)
        # st.write(f"close_price: {close_price}")
        with st.expander("See Raw Data"):
            try:
                st.dataframe(f_df.astype(float).fillna(0).round(decimals=2).style.background_gradient(cmap, axis=0)\
                                            .format(precision=2, na_rep='MISSING', thousands=","))
                st.dataframe(v_df.astype(float).fillna(0).round(decimals=2).style.background_gradient(cmap, axis=0)\
                                            .format(precision=2, na_rep='MISSING', thousands=","))
                st.dataframe(y_df.astype(float).fillna(0).round(decimals=2).style.background_gradient(cmap, axis=0)\
                                    .format(precision=2, na_rep='MISSING', thousands=","))
            except ValueError :
                st.subheader("financial statements")
                st.dataframe(f_df.to_frame().T)
                st.subheader("Valuations")
                st.dataframe(v_df)
                st.subheader("Expecting Yield")
                st.dataframe(y_df)
         ### PERR, PBRR 같이 보기 #########################################################################################
        with st.container():
            col1, col2, col3 = st.columns([30,2,30])
            with col1:
                # #PERR, PBRR
                fig = go.Figure(go.Indicator(
                mode = "number+delta",
                value = round(y_df.iloc[-1,7]*100,2),
                title = {"text": "10년 기대수익률<br><span style='font-size:0.8em;color:gray'>평균 ROE ("+str(roe_mean)+") 기준</span>"},
                domain = {'x': [0, 1], 'y': [0, 1]},
                delta = {'reference': 15.0}))
                st.plotly_chart(fig)
            with col2:
                st.write("")
            with col3:
                fig = go.Figure(go.Indicator(
                mode = "number+delta",
                value = round(y_df.iloc[-1,5]*100,2),
                title = {"text": "10년 기대수익률<br><span style='font-size:0.8em;color:gray'>현재ROE("+str(current_roe)+")기준</span>"},
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
        col1.metric(label="현재 ROE", value =round(v_df.iloc[-1,4]*100,2))
        col2.metric(label="3년 평균", value =round(v_df.iloc[-1,5]*100,2))
        col3.metric(label="5년 평균", value =round(v_df.iloc[-1,6]*100,2))
        col4.metric(label="8년 평균", value =round(v_df.iloc[-1,7]*100,2))
        col1, col2, col3, col4 = st.columns(4)
        col1.metric(label="현재 ROE 기준 기대수익률", value = round(y_df.iloc[-1,5]*100,2), delta=round((round(y_df.iloc[-1,5]*100,2)-expect_yield),2))
        col2.metric(label="최소 평균 기준 기대수익률", value =round(y_df.iloc[-1,4]*100,2), delta=round((round(y_df.iloc[-1,4]*100,2)-expect_yield),2))
        col3.metric(label="최대 평균 기준 기대수익률", value =round(y_df.iloc[-1,6]*100,2), delta=round((round(y_df.iloc[-1,6]*100,2)-expect_yield),2))
        col4.metric(label="평균 기준 기대수익률", value =round(y_df.iloc[-1,7]*100,2), delta=round((round(y_df.iloc[-1,7]*100,2)-expect_yield),2))
        col1, col2, col3, col4 = st.columns(4)
        col1.metric(label="현재 ROE 기준 매수가격", value = current_proper_price, delta=current_proper_price-close_price)
        col2.metric(label="최소 평균 기준 매수가격", value =min_proper_price, delta=min_proper_price-close_price)
        col3.metric(label="최대 평균 기준 매수가격", value =max_proper_price, delta=min_proper_price-close_price)
        col4.metric(label="평균 기준 매수가격", value =mean_proper_price, delta=min_proper_price-close_price)

        st.subheader("Fundamental Value")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric(label="현재 주가", value = close_price)
        col2.metric(label="PER", value =round(overview_df.loc['PERatio'].astype(float),2))
        col3.metric(label="TrailingPE", value =round(overview_df.loc['TrailingPE'].astype(float),2))
        col4.metric(label="ForwardPE", value =round(overview_df.loc['ForwardPE'].astype(float),2))
        col1, col2, col3, col4 = st.columns(4)
        col1.metric(label="DPS", value = round(overview_df.loc['DividendPerShare'].astype(float),2))
        col2.metric(label="DividendYield", value =str(overview_df.loc['DividendYield']*100)+"%")
        col3.metric(label="DPR", value =str(round(div_df.iloc[-1,1]*100,2))+"%")
        col4.metric(label="ExDividendDate", value =str(overview_df.loc['ExDividendDate']))

    with tab2:
        #Income 데이터 가져오기
        earning_df, income_df, balance_df, cashflow_df = make_data(ticker)
        #Summary 데이터 가져오기    
        # OV = fd.get_company_overview(ticker)
        # split_OV=OV[0]
        # df = pd.json_normalize(split_OV)
        # df = df.T
        # #Rim 즉석 계산
        # df.loc['Earnings Yield'] = round(1/df.loc['TrailingPE'].astype(float)*100,2)
        # df.loc['RIM'] = round(df.loc['BookValue'].astype(float)*(df.loc['ReturnOnEquityTTM'].astype(float)/0.08),2)
        # close_price = fdr.DataReader(input_ticker, today)
        # df.loc['Price'] = close_price.iloc[0,4]
        # earningY = df.loc['Earnings Yield'][0]
        # if earningY < 15.0 :
        #     df.loc['Target Price'] = round(df.loc['DilutedEPSTTM'].astype(float)/0.15,2)
        # df.loc['Margin Of Safety'] = (df.loc['RIM']/df.loc['Price'] -1)*100
        # last_value = df.iloc[-1,0]
        # last_value= str(round(last_value,2)) + '%'
        # df.iloc[-1,0] = last_value
        # df.style.applymap(draw_color_cell,color='#ff9090',subset=pd.IndexSlice[-1,0])
        # df.columns = ['Description']
        # df.update(df.select_dtypes(include=np.number).applymap('{:,}'.format))
        # st.table(df)
        # st.write('Description:', df.loc['Description',0])
        #gauge chart
        # fig = go.Figure(go.Indicator(
        #     mode = "gauge+number+delta",
        #     value = round(float(df.iloc[-3,0]),2),
        #     delta = {'reference': round(float(df.iloc[-4,0]),2), 'relative': True},
        #     title = {'text': "RIM-Price"},
        #     domain = {'x': [0, 1], 'y': [0, 0.5]}
        # ))
        # fig.add_trace(go.Indicator(
        #     mode = "number+delta",
        #     value = round(float(df.iloc[-5,0]),2),
        #     title = {"text": "Earnings Yield<br><span style='font-size:0.8em;color:gray'>Demand Yield(15%)</span>"},
        #     domain = {'x': [0, 1], 'y': [0.6, 1]},
        #     delta = {'reference': 15.0}))
        # st.plotly_chart(fig)

        # fig = go.Figure()
        # fig.add_trace(go.Indicator(
        #     mode = "number+delta",
        #     value = 200,
        #     title = {"text": "RIM<br><span style='font-size:0.8em;color:gray'>Current Price</span>"},
        #     domain = {'x': [0, 1], 'y': [0, 0.5]},
        #     delta = {'reference': 400, 'relative': True, 'position' : "top"}))

        # fig.add_trace(go.Indicator(
        #     mode = "number+delta",
        #     value = 350,
        #     title = {"text": "Earnings Yield<br><span style='font-size:0.8em;color:gray'>Subtitle</span><br><span style='font-size:0.8em;color:gray'>Subsubtitle</span>"},
        #     delta = {'reference': 400, 'relative': True},
        #     domain = {'x': [0, 1], 'y': [0.5, 1]}))
        with st.expander("See Raw Data"):
                #if  st.checkbox('See Earning Data'):
            st.subheader('Earning Raw Data') 
            st.dataframe(earning_df.style.highlight_max(axis=0))     
        com_name_df = tickers[tickers['Symbol'] == input_ticker ]
        # st.write(com_name_df)
        com_name = com_name_df.iloc[0,1]   
        st.subheader(com_name + " Fundamental Chart")
        with st.container():
            col1, col2, col3 = st.columns([30,2,30])
            with col1:
               
                ##주가 EPS
                # price_df = fdr.DataReader(input_ticker, earning_df.iloc[0,0], earning_df.iloc[-1,0])['Adj Close'].to_frame()
                price_df = fs.get_price(input_ticker, earning_df.iloc[0,0], earning_df.iloc[-1,0])
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
            with col2:
                st.write("")
            with col3:
                #주가와 EPS
                chart.ttmEPS_PER_chart(input_ticker, com_name, band_df)
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

        #PBR 밴드 위해
        pbr_df = pd.DataFrame()
        pbr_df.loc[:,'shares'] = balance_df['commonStockSharesOutstanding']
        pbr_df.loc[:,'Equity'] = balance_df['totalShareholderEquity']
        pbr_df.loc[:,'reportedDate'] = earning_df['reportedDate']
        pbr_df = pd.merge_ordered(pbr_df, price_df, how="left", left_on='reportedDate', right_on=price_df.index, fill_method='ffill')
        pbr_df.set_index('reportedDate', inplace=True)

        #챠트 기본 설정
        # colors 
        marker_colors = ['#34314c', '#47b8e0', '#ff7473', '#ffc952', '#3ac569']
        # marker_colors = ['rgb(27,38,81)', 'rgb(205,32,40)', 'rgb(22,108,150)', 'rgb(255,69,0)', 'rgb(237,234,255)']
        template = 'seaborn' #"plotly", "plotly_white", "plotly_dark", "ggplot2", "seaborn", "simple_white", "none"
        st.subheader('Band Chart')
        with st.expander("See Raw Data"):
                #if  st.checkbox('See Earning Data'):
            st.subheader('PER Band Raw Data') 
            st.dataframe(band_df.style.highlight_max(axis=0)) 
            st.subheader('PBR Band Raw Data') 
            st.dataframe(pbr_df.style.highlight_max(axis=0))
        with st.container():
            col1, col2, col3 = st.columns([30,2,30])
            with col1:
                chart.visualize_PER_band(input_ticker, com_name, band_df)
            with col2:
                st.write("")
            with col3:
                chart.visualize_PBR_band(input_ticker, com_name, pbr_df)
        html_br="""
        <br>
        """
        st.markdown(html_br, unsafe_allow_html=True)
        # Profit and Cost
        st.subheader('Profit, Cost, Growth')
        with st.container():
            col1, col2, col3 = st.columns([30,2,30])
            with col1:
                x_data = income_df.index
                title = com_name + '('  + input_ticker + ') <b>Profit & Cost</b>'
                titles = dict(text= title, x=0.5, y = 0.85) 
                fig = make_subplots(specs=[[{'secondary_y': True}]]) 
                y_data_bar1 = ['totalRevenue', 'costOfRevenue', 'operatingExpenses']
                y_data_line1 = ['grossProfit', 'ebit', 'operatingIncome', 'netIncome']

                for y_data, color in zip(y_data_bar1, marker_colors) :
                    fig.add_trace(go.Bar(name = y_data, x = x_data, y = income_df[y_data],marker_color= color), secondary_y = False) 
                
                for y_data, color in zip(y_data_line1, marker_colors): 
                    fig.add_trace(go.Scatter(mode='lines+markers+text', 
                                                name = y_data, x =  x_data, y= income_df.loc[:,y_data],
                                                text= income_df[y_data], textposition = 'top center', marker_color = color),
                                                secondary_y = True)
                fig.update_traces(texttemplate='%{text:.3s}') 
                fig.update_yaxes(title_text='Revenue', range=[0, max(income_df.loc[:,y_data_bar1[0]])*2], secondary_y = False)
                fig.update_yaxes(title_text='Income', range=[-max(income_df.loc[:,y_data_line1[0]]), max(income_df.loc[:,y_data_line1[0]])* 1.2], secondary_y = True)
                fig.update_yaxes(showticklabels= True, showgrid = False, zeroline=True, tickprefix="$")
                fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template)
                st.plotly_chart(fig)
            with col2:
                st.write("")
            with col3:
                # 마진율과 성장률
                x_data = income_df.index
                title = com_name + '('  + input_ticker + ') Margin & Growth Rate' 
                titles = dict(text= title, x=0.5, y = 0.85) 
                fig = make_subplots(specs=[[{'secondary_y': True}]]) 
                y_data_line2 = ['GPM', 'OPM', 'NPM']
                y_data_bar2 = ['TR Change', 'OI Change', 'NI Change']

                for y_data, color in zip(y_data_line2, marker_colors): 
                    fig.add_trace(go.Scatter(mode='lines+markers+text', name = y_data, x = x_data, y=income_df[y_data],
                    text = income_df[y_data], textposition = 'top center', marker_color = color),
                    secondary_y = True)

                for y_data, color in zip(y_data_bar2, marker_colors) :
                    fig.add_trace(go.Bar(name = y_data, x = x_data, y = income_df[y_data], 
                                        text = income_df[y_data], textposition = 'outside', marker_color= color), secondary_y = False)

                fig.update_traces(texttemplate='%{text:.3s}') 
                fig.update_yaxes(title_text='Growth Rate', range=[0, max(income_df.loc[:,y_data_bar2[0]])*2], secondary_y = False)
                fig.update_yaxes(title_text='Margin Rate', range=[-max(income_df.loc[:,y_data_line2[0]]), max(income_df.loc[:,y_data_line2[0]])* 1.2], secondary_y = True)
                fig.update_yaxes(showticklabels= True, showgrid = False, zeroline=True, ticksuffix="%")
                fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template)
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
                titles = dict(text= title, x=0.5, y = 0.85) 
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
                st.plotly_chart(fig)
            with col2:
                st.write("")
            with col3:
                #무형자산총자금비율, 현금자산비율
                x_data = balance_df.index
                title = com_name + '('  + input_ticker + ') <b>IntangibleAssets & Cash And ShortTermInvestments</b>'
                titles = dict(text= title, x=0.5, y = 0.85) 
                fig = make_subplots(specs=[[{'secondary_y': True}]]) 
                y_data_bar4 = ['무형자산비율', '현금성자산비율']
                y_data_bar4_name = ['intangible/Assets', 'Cash/Assets']
                fig.add_trace(go.Bar(name = y_data_bar4_name[1], x = x_data, y = balance_df[y_data_bar4[1]], 
                                    text = balance_df[y_data_bar4[1]], textposition = 'outside', 
                                    marker_color= marker_colors[0]), secondary_y = False) 
                fig.add_trace(go.Scatter(mode='lines+markers+text', 
                                                name = y_data_bar4_name[0], x =  x_data, y= balance_df[y_data_bar4[0]],
                                                text= balance_df[y_data_bar4[0]], textposition = 'top center', marker_color = marker_colors[2]),
                                                secondary_y = True)
                fig.update_traces(texttemplate='%{text:.3s}') 
                fig.update_yaxes(title_text="Cash/Assets", showticklabels= True, showgrid = True, zeroline=True, ticksuffix="%", secondary_y = False)
                fig.update_yaxes(title_text="intangible/Assets", showticklabels= True, showgrid = False, zeroline=True, ticksuffix="%", secondary_y = True)
                fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template)
                st.plotly_chart(fig)
        html_br="""
        <br>
        """
        st.markdown(html_br, unsafe_allow_html=True)

        #현금흐름
        #영업활동현금흐름, 순이익, 투자활동현금흐름, 재무활동현금흐름
        st.subheader('Cash Flow')
        x_data = cashflow_df.index
        title = com_name + '('  + input_ticker + ') <b>Cash Flow Statement</b>'
        titles = dict(text= title, x=0.5, y = 0.85) 
        fig = make_subplots(specs=[[{'secondary_y': True}]]) 
        y_data_bar5 = ['operatingCashflow', 'FCF']

        for y_data, color in zip(y_data_bar5, marker_colors) :
            fig.add_trace(go.Bar(name = y_data, x = x_data, y = cashflow_df[y_data], 
                                text= cashflow_df[y_data], textposition = 'outside', marker_color= color), secondary_y = False) 
        fig.add_trace(go.Bar(name = 'NetIncome', x = x_data, y = income_df['netIncome'], 
                            text= income_df['netIncome'], textposition = 'outside', marker_color= '#ff7473'), secondary_y = False)
        fig.update_traces(texttemplate='%{text:.3s}') 
        fig.update_yaxes(showticklabels= True, showgrid = True, zeroline=True, tickprefix="$")
        fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template)
        st.plotly_chart(fig)


        #조회시 1분 기다려야 함
        st.warning('Please Wait One minute Before Searching Next Company!!!')
        my_bar = st.progress(0)
        for percent_complete in range(100):
            time.sleep(0.6)
            my_bar.progress(percent_complete + 1)
    with tab3:
        st.subheader("데이터 추가 예정")



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

def make_data(ticker):   
    edf = make_df('EARNINGS',ticker) #get earning sheet quarterly data
    # income = make_df('INCOME_STATEMENT',ticker) #get income statement quarterly data
    # cashflow = make_df('BALANCE_SHEET',ticker) #get cash flow quarterly data
    # balance = make_df('CASH_FLOW',ticker) #get balance sheet quarterly data
    
    #income_statement
    income, meta_data = fd.get_income_statement_quarterly(ticker)
    income.set_index('fiscalDateEnding', inplace=True)
    income.index =  pd.to_datetime(income.index, format='%Y-%m-%d')
    income = income.iloc[::-1]
    sub = ['totalRevenue', 'costOfRevenue', 'grossProfit', 'operatingIncome', 'operatingExpenses', 'ebit', 'netIncome']
    income_df = income[sub].replace('None','0').astype(float).round(0)
    #연매출액 증가율
    gp_cagr = (income_df['totalRevenue'].iloc[-1]/income_df['totalRevenue'].iloc[0])**(1/5) -1

    income_df['GPM'] = income_df['grossProfit'] / income_df['totalRevenue']*100
    income_df['OPM'] = income_df['operatingIncome'] / income_df['totalRevenue']*100
    income_df['NPM'] = income_df['netIncome'] / income_df['totalRevenue']*100

    income_df['TR Change'] = income_df['totalRevenue'].pct_change()*100
    income_df['OI Change'] = income_df['operatingIncome'].pct_change()*100
    income_df['NI Change'] = income_df['netIncome'].pct_change()*100

    #balance sheet 
    balance, meta_data = fd.get_balance_sheet_quarterly(ticker)
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
    cashflow, meta_data = fd.get_cash_flow_quarterly(ticker)
    cashflow.set_index('fiscalDateEnding', inplace=True)
    cashflow.index =  pd.to_datetime(cashflow.index, format='%Y-%m-%d')
    cashflow = cashflow.iloc[::-1]
    sub = ['netIncome', 'operatingCashflow', 'cashflowFromInvestment', 'cashflowFromFinancing', 'dividendPayout', \
         'capitalExpenditures', 'changeInCashAndCashEquivalents']
    cashflow_df = cashflow[sub].replace('None','0').astype(float).round(0)
    cashflow_df["FCF"] = cashflow_df['operatingCashflow'] - cashflow_df['capitalExpenditures']

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
    
    # ticker_list = [ "SENEA", "IMKTA", "KBAL", "CMC", \
    #                 "APT","AMCX","BIIB", "BIG", "CI", "CPRX", "CHRS", "CSCO","CVS","DHT", "EURN", "HRB", "PRDO", \
    #                 "MO", "T", "O", "OMC", "SBUX", \
    #                 "MSFT", "MMM", "INVA", "SIGA", "WLKP", "VYGR", "KOF", "WSTG", "LFVN", "SUPN"]
    if input_ticker == "":
        input_ticker = st.sidebar.selectbox(
            'Ticker',ticker_list
        )
    
    input_ticker = input_ticker.upper()
    #Summary 데이터 가져오기    
    OV = fd.get_company_overview(input_ticker)
    split_OV=OV[0]
    ov_df = pd.json_normalize(split_OV)
    overview_df = ov_df.T
    st.table(overview_df)
    submit = st.sidebar.button('Run app')
    if submit:
        run(input_ticker, overview_df)