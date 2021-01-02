import json
import sqlite3
import time
from datetime import datetime

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import requests
from pandas.io.json import json_normalize
from plotly.subplots import make_subplots

import streamlit as st
from alpha_vantage.fundamentaldata import FundamentalData as FD
import FinanceDataReader as fdr

pd.set_option('display.float_format', '{:.2f}'.format)

#API key
fd = FD(key='XA7Y92OE6LDOTLLE')
# fd = FD(key='CBALDIGECB3UFF5R')
# key='CBALDIGECB3UFF5R'
key='XA7Y92OE6LDOTLLE'
#sizipusx2@gmail.com = XA7Y92OE6LDOTLLE
#indiesoul2@gmail.com = CBALDIGECB3UFF5R

def main():
    data_load_state = st.text('Loading data...')
    tickers = load_data()
    ticker_list = tickers['Symbol'].values.tolist()
        # st.dataframe(tickers)
    data_load_state.text("Done! (using st.cache)")
    
    # my_bar = st.progress(0)
    # for percent_complete in range(60):
    #     time.sleep(1)
    #     my_bar.progress(percent_complete + 1)
    
    # with st.spinner('Wait for One Minuate00...'):
    #     time.sleep(60)
    #     st.success('Done!')

    input_ticker = st.sidebar.text_input("ticker","AAPL").upper()
    
    if input_ticker == "":
        input_ticker = st.sidebar.selectbox(
            'Ticker',ticker_list
        )
    
    #Income 데이터 가져오기
    income_df, earning_df = make_data(input_ticker)
    income_df = income_df.round(0)
    # income_df, cashflow_df, balance_df, summary_df = make_data(input_ticker)
    # income_df = make_data(input_ticker)
    
    OV = fd.get_company_overview(input_ticker)
    split_OV=OV[0]
    df = pd.json_normalize(split_OV)
    df = df.T
    st.dataframe(df.style.highlight_max(axis=1))

    com_name_df = tickers[tickers['Symbol'] == input_ticker ]
    # st.write(com_name_df)
    com_name = com_name_df.iloc[0,1]   
    st.header(com_name + " Fundamental Chart")
    ##주가 EPS
    price_df = fdr.DataReader(input_ticker,earning_df.index[0], earning_df.index[-1])['Close'].to_frame()
    income_df = pd.merge(income_df, price_df, how="inner", left_index=True, right_index=True)

    #챠트 기본 설정
    # colors 
    marker_colors = ['rgb(27,38,81)', 'rgb(205,32,40)', 'rgb(22,108,150)', 'rgb(255,69,0)', 'rgb(237,234,255)']
    template = 'seaborn' #"plotly", "plotly_white", "plotly_dark", "ggplot2", "seaborn", "simple_white", "none"

    #주가와 EPS
    title = com_name +'('  + input_ticker + ') EPS & Price'
    titles = dict(text= title, x=0.5, y = 0.9) 
    x_data = earning_df['reportedDate'] # EPS발표 날짜로 

    fig = make_subplots(specs=[[{'secondary_y': True}]]) 
    y_data_bar = ['reportedEPS','estimatedEPS', 'surprise']
   
    for y_data, color in zip(y_data_bar, marker_colors) :
        fig.add_trace(go.Bar(name = y_data, x = x_data, y = earning_df[y_data], marker_color= color), secondary_y = False) 
    
    fig.add_trace(go.Scatter(mode='lines', 
                            name = 'Close', x =  price_df.index, y= price_df['Close'],
                            text= price_df['Close'], textposition = 'top center', marker_color = 'rgb(0,0,0)'),# marker_colorscale='RdBu'),
                            secondary_y = True)

    fig.update_traces(texttemplate='%{text:.3s}') 
    fig.update_yaxes(title_text='Close',showticklabels= True, showgrid = False, zeroline=True, tickprefix="$")
    fig.update_yaxes(title_text='EPS',showticklabels= True, showgrid = True, zeroline=True, tickprefix="$", secondary_y = False)
    fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template)#, xaxis_tickformat = 'd')#  legend_title_text='( 단위 : $)' 
    fig.update_layout(
            showlegend=True,
            # legend=dict(
            # orientation="h",
            # yanchor="bottom",
            # y=1.02,
            # xanchor="right",
            # x=1
        # ),
            xaxis=go.layout.XAxis(
            rangeselector=dict(
                buttons=list([
                    dict(count=6,
                        label="6m",
                        step="month",
                        stepmode="backward"),
                    dict(count=1,
                        label="YTD",
                        step="year",
                        stepmode="todate"),
                    dict(count=1,
                        label="1y",
                        step="year",
                        stepmode="backward"),
                    dict(count=5,
                        label="5y",
                        step="year",
                        stepmode="backward"),
                    dict(count=10,
                        label="10y",
                        step="year",
                        stepmode="backward"),
                    dict(step="all")
                ])
            ),
            # rangeslider=dict(
            #     visible=True
            # ),
            type="date"
            )      
        )
    st.plotly_chart(fig)

    # Profit and Cost
    st.subheader('Profit, Cost, Growth')
    x_data = income_df.index
    title = com_name + '('  + input_ticker + ') <b>Profit & Cost</b>'
    titles = dict(text= title, x=0.5, y = 0.85) 
    fig = make_subplots(specs=[[{'secondary_y': True}]]) 
    y_data_bar1 = ['totalRevenue', 'costOfRevenue', 'totalOperatingExpense']
    y_data_line1 = ['grossProfit', 'operatingIncome', 'netIncome']

    for y_data, color in zip(y_data_bar1, marker_colors) :
        fig.add_trace(go.Bar(name = y_data, x = x_data, y = income_df[y_data],marker_color= color), secondary_y = False) 
    
    for y_data, color in zip(y_data_line1, marker_colors): 
        fig.add_trace(go.Scatter(mode='lines+markers+text', 
                                    name = y_data, x =  x_data, y= income_df.loc[:,y_data],
                                    text= income_df[y_data], textposition = 'top center', marker_color = color),
                                    secondary_y = True)
    fig.update_traces(texttemplate='%{text:.3s}') 
    fig.update_yaxes(range=[0, max(income_df.loc[:,y_data_bar1[0]])*2], secondary_y = False)
    fig.update_yaxes(range=[-max(income_df.loc[:,y_data_line1[0]]), max(income_df.loc[:,y_data_line1[0]])* 1.2], secondary_y = True)
    fig.update_yaxes(showticklabels= True, showgrid = False, zeroline=True, tickprefix="$")
    fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template)
    st.plotly_chart(fig)

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
    fig.update_yaxes(range=[0, max(income_df.loc[:,y_data_bar2[0]])*2], secondary_y = False)
    fig.update_yaxes(range=[-max(income_df.loc[:,y_data_line2[0]]), max(income_df.loc[:,y_data_line2[0]])* 1.2], secondary_y = True)
    fig.update_yaxes(showticklabels= True, showgrid = False, zeroline=True, ticksuffix="%")
    fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template)
    st.plotly_chart(fig)

    #조회시 1분 기다려야 함
    st.warning('Please Wait One minute Befor Searching Next Company!!!')
    my_bar = st.progress(0)
    for percent_complete in range(60):
        time.sleep(1)
        my_bar.progress(percent_complete + 1)

    #안정성 챠트 보기
    # st.subheader('안정성 챠트')
    # fig1 = make_subplots(specs=[[{"secondary_y": True}]])
    # fig1.add_trace(go.Scatter(x=org_df.index, y=org_df['Quick Ratio'], mode='lines', name='Quick Ratio'))
    # fig1.add_trace(go.Scatter(x=org_df.index, y=org_df['Current Ratio'], mode='lines', name='Current Ratio'))
    # fig1.add_trace(go.Scatter(x=org_df.index, y=org_df['Debt/Equity'], mode='lines', name='Debt/Equity'))
    # fig1.add_trace(go.Bar(x=org_df.index, y=org_df['Net Debt/EBITDA'], name='Net Debt/EBITDA'),
    #     secondary_y=True)
    # st.plotly_chart(fig1)

    #PER 밴드 챠트
    # st.subheader('밴드 챠트')
    # visualize_PER_band(tic, df)

    # 'Current PER: ', df.iloc[-2,3].round(2) 
    # 'Last EPS: ', df.iloc[-2,1].round(2)

    #PBR 밴드 챠트
    # visualize_PBR_band(tic, df)

    # 'Current PBR: ', df.iloc[-2,4].round(2) 
    # 'Last BPS: ', round(df.iloc[-2,2],2)

@st.cache
def load_data():
    # 나스닥거래소 상장종목 전체
    df_q= fdr.StockListing('NASDAQ')
    # NewYork 증권거래소 상장종목 전체
    df_n= fdr.StockListing('NYSE')
    # American 증권거래소 상장종목 전체
    df_a= fdr.StockListing('AMEX')
    # 각 거래소 이름 추가
    df_q.iloc[:,-1] = "NASDAQ"
    df_n.iloc[:,-1] = "NYSE"
    df_a.iloc[:,-1] = "AMEX"
    #세 데이터 모두 합치자
    ticker_list = df_q.append(df_n).append(df_a)

    return ticker_list

def make_data(ticker):
    income, meta_data = fd.get_income_statement_quarterly(ticker) #get income statement quarterly data
    # cashflow, meta_data = fd.get_cash_flow_quarterly(ticker) #get cash flow quarterly data
    # balance, meta_data = fd.get_balance_sheet_quarterly(ticker) #get balance sheet quarterly data
    # ov = fd.get_company_overview(symbol=ticker)  #get overview data
    # summary = pd.json_normalize(ov[0])
    
    income= income.iloc[::-1]
    income.set_index('fiscalDateEnding', inplace=True)
    income.index =  pd.to_datetime(income.index, format='%Y-%m-%d')
    sub = ['totalRevenue', 'costOfRevenue', 'grossProfit', 'totalOperatingExpense', 'operatingIncome', 'ebit', 'netIncome']
    income_df = income[sub].replace('None','0').astype(float).round(0)
    #연매출액 증가율
    gp_cagr = (income_df['totalRevenue'].iloc[-1]/income_df['totalRevenue'].iloc[0])**(1/5) -1

    income_df['GPM'] = income_df['grossProfit'] / income_df['totalRevenue']*100
    income_df['OPM'] = income_df['operatingIncome'] / income_df['totalRevenue']*100
    income_df['NPM'] = income_df['netIncome'] / income_df['totalRevenue']*100

    income_df['TR Change'] = income_df['totalRevenue'].pct_change()*100
    income_df['OI Change'] = income_df['operatingIncome'].pct_change()*100
    income_df['NI Change'] = income_df['netIncome'].pct_change()*100

    #earnings
    API_URL = "https://www.alphavantage.co/query" 
    func = "EARNINGS"
    data = { 
        "function": func, 
        "symbol": ticker,
        "outputsize" : "compact",
        "datatype": "json", 
        "apikey": key} 

    response = requests.get(API_URL, data) 
    response_json = response.json() 
    edf = pd.DataFrame(response_json['quarterlyEarnings'])
    edf.set_index('fiscalDateEnding', inplace=True)
    edf.index =  pd.to_datetime(edf.index, format='%Y-%m-%d')
    edf = edf.iloc[::-1]
    edf['reportedEPS'] = edf['reportedEPS'].replace('None','0').astype(float).round(3)
    edf['estimatedEPS'] = edf['estimatedEPS'].replace('None','0').astype(float).round(4)
    edf['surprise'] = edf['surprise'].replace('None','0').astype(float).round(4)
    edf['surprisePercentage'] = edf['surprisePercentage'].replace('None','0').astype(float).round(2)

    
    # cashflow = cashflow.iloc[::-1]
    # cashflow.set_index('fiscalDateEnding', inplace=True)
    # balance = balance.iloc[::-1]
    # balance.set_index('fiscalDateEnding', inplace=True)

    # return income, cashflow, balance, summary 
    return income_df, edf




def visualize_PER_band(com_name, df):
  
    fig = make_subplots(specs=[[{"secondary_y": False}]])
    fig.add_trace(go.Scatter(x=df.index, y=df.iloc[:,6], name=df.columns[6],
                            line=dict(color='firebrick', width=2)))
    fig.add_trace(go.Scatter(x=df.index, y=df.iloc[:,7], name=df.columns[7],
                            line = dict(color='purple', width=2, dash='dash')))
    fig.add_trace(go.Scatter(x=df.index, y=df.iloc[:,8], name=df.columns[8],
                            line=dict(color='royalblue', width=2)))
    fig.add_trace(go.Scatter(x=df.index, y=df.iloc[:,9], name=df.columns[9],
                            line = dict(color='green', width=2, dash='dash')))
    fig.add_trace(go.Scatter(x=df.index, y=df.iloc[:,10], name=df.columns[10],
                            line=dict(color='red', width=2) # dash options include 'dash', 'dot', and 'dashdot'
    ))
     
    fig.add_trace(
        go.Scatter(x = df.index, y = df['Close'], name = '종가',  line=dict(color='black', width=3)),
        secondary_y=False
    )

    # fig.update_layout(title_text=com_name + " PER 밴드", title_font_size=20)
    fig.update_layout(
    title={
        'text': com_name + " PER 밴드",
        'y':0.9,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'})
    fig.update_yaxes(title_text="주가", secondary_y=True)
    fig.update_xaxes(ticks="inside", tickcolor='crimson', ticklen=10)
    fig.update_yaxes(ticks="inside", tickcolor='crimson', ticklen=10)
    fig.update_layout(
            showlegend=True,
            legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
            xaxis=go.layout.XAxis(
            rangeselector=dict(
                buttons=list([
                    dict(count=1,
                        label="1m",
                        step="month",
                        stepmode="backward"),
                    dict(count=6,
                        label="6m",
                        step="month",
                        stepmode="backward"),
                    dict(count=1,
                        label="YTD",
                        step="year",
                        stepmode="todate"),
                    dict(count=1,
                        label="1y",
                        step="year",
                        stepmode="backward"),
                    dict(step="all")
                ])
            ),
            rangeslider=dict(
                visible=True
            ),
            type="date"
            )      
        )
    # # Plot!
    st.plotly_chart(fig)

def visualize_PBR_band(com_name, df):
  
    fig = make_subplots(specs=[[{"secondary_y": False}]])
    fig.add_trace(go.Scatter(x=df.index, y=df.iloc[:,11], name=df.columns[11],
                            line=dict(color='firebrick', width=2)))
    fig.add_trace(go.Scatter(x=df.index, y=df.iloc[:,12], name=df.columns[12],
                            line = dict(color='purple', width=2, dash='dash')))
    fig.add_trace(go.Scatter(x=df.index, y=df.iloc[:,13], name=df.columns[13],
                            line=dict(color='royalblue', width=2)))
    fig.add_trace(go.Scatter(x=df.index, y=df.iloc[:,14], name=df.columns[14],
                            line = dict(color='green', width=2, dash='dash')))
    fig.add_trace(go.Scatter(x=df.index, y=df.iloc[:,15], name=df.columns[15],
                            line=dict(color='red', width=2))) # dash options include 'dash', 'dot', and 'dashdot'
     
    fig.add_trace(
        go.Scatter(x = df.index, y = df['Close'], name = '종가',  line=dict(color='black', width=3)),
        secondary_y=False
    )

    # fig.update_layout(title_text=com_name + " PBR 밴드", title_font_size=20)
    fig.update_layout(
        title={
            'text': com_name + " PBR 밴드",
            'y':0.9,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'})
    fig.update_yaxes(title_text="주가", secondary_y=True)
    fig.update_xaxes(ticks="inside", tickcolor='crimson', ticklen=10)
    fig.update_yaxes(ticks="inside", tickcolor='crimson', ticklen=10)
    fig.update_layout(
            showlegend=True,
            legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
            xaxis=go.layout.XAxis(
            rangeselector=dict(
                buttons=list([
                    dict(count=1,
                        label="1m",
                        step="month",
                        stepmode="backward"),
                    dict(count=6,
                        label="6m",
                        step="month",
                        stepmode="backward"),
                    dict(count=1,
                        label="YTD",
                        step="year",
                        stepmode="todate"),
                    dict(count=1,
                        label="1y",
                        step="year",
                        stepmode="backward"),
                    dict(step="all")
                ])
            ),
            rangeslider=dict(
                visible=True
            ),
            type="date"
            )      
        )
    # # Plot!
    st.plotly_chart(fig)
        

if __name__ == "__main__":
    main()
