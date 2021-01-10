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

def run():
    data_load_state = st.text('Loading All Company data...')
    tickers = load_data()
    # ticker_list = tickers['Symbol'].values.tolist()
        # st.dataframe(tickers)
    data_load_state.text("Done! (using st.cache)")

    #Income 데이터 가져오기
    earning_df, income_df, balance_df, cashflow_df = make_data(input_ticker)
    #Summary 데이터 가져오기    
    OV = fd.get_company_overview(input_ticker)
    split_OV=OV[0]
    df = pd.json_normalize(split_OV)
    df = df.T
    st.dataframe(df.style.highlight_null(null_color='red').format(None, na_rep="-"))
    st.write('Description:', df.loc['Description',0])

    com_name_df = tickers[tickers['Symbol'] == input_ticker ]
    # st.write(com_name_df)
    com_name = com_name_df.iloc[0,1]   
    st.header(com_name + " Fundamental Chart")
    ##주가 EPS
    price_df = fdr.DataReader(input_ticker, earning_df.iloc[0,0], earning_df.iloc[-1,0])['Close'].to_frame()
    # income_df = pd.merge(income_df, price_df, how="inner", left_index=True, right_index=True)
    earning_df['reportedDate'] = pd.to_datetime(earning_df['reportedDate'], format='%Y-%m-%d')
    band_df = pd.merge_ordered(earning_df, price_df, how="left", left_on='reportedDate', right_on=price_df.index, fill_method='ffill')
    band_df['ttmEPS'] = band_df['reportedEPS'].rolling(4).sum()
    band_df.set_index('reportedDate', inplace=True)
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
            rangeslider=dict(
                visible=True
            ),
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

    #부채비율, 유동비율, 당좌비율
    st.subheader('Asset, Liabilities, ShareholderEquity')
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

    #PER 밴드 챠트
    visualize_PER_band(input_ticker, com_name, band_df)
    visualize_PBR_band(input_ticker, com_name, pbr_df)

    #조회시 1분 기다려야 함
    st.warning('Please Wait One minute Before Searching Next Company!!!')
    my_bar = st.progress(0)
    for percent_complete in range(100):
        time.sleep(0.6)
        my_bar.progress(percent_complete + 1)

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

    #balance sheet 
    balance, meta_data = fd.get_balance_sheet_quarterly(ticker)
    balance.set_index('fiscalDateEnding', inplace=True)
    balance.index =  pd.to_datetime(balance.index, format='%Y-%m-%d')
    balance = balance.iloc[::-1]
    sub = ['totalAssets', 'intangibleAssets', 'totalLiabilities', 'totalShareholderEquity', 'retainedEarnings', 'totalCurrentLiabilities', \
         'totalCurrentAssets', 'netTangibleAssets', 'netReceivables', 'inventory', 'accountsPayable', 'accumulatedAmortization', \
         'totalNonCurrentAssets', 'accumulatedDepreciation', 'cashAndShortTermInvestments', 'commonStockSharesOutstanding']
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
    sub = ['netIncome', 'operatingCashflow', 'cashflowFromInvestment', 'cashflowFromFinancing', 'depreciation', 'dividendPayout', \
         'stockSaleAndPurchase', 'capitalExpenditures', 'changeInCashAndCashEquivalents']
    cashflow_df = cashflow[sub].replace('None','0').astype(float).round(0)
    cashflow_df["FCF"] = cashflow_df['operatingCashflow'] - cashflow_df['capitalExpenditures']

    return edf, income_df, balance_df, cashflow_df

def visualize_PER_band(ticker, com_name, fun_df):
    
    # st.write(option)
    fun_df.dropna(inplace=True)
    df = fun_df[['Close', 'ttmEPS']]
    df['PER'] = round((df['Close'] / df['ttmEPS']),2)
    #PER Max/Min/half/3/1
    e_max = round(df['PER'].max(),1)
    if(e_max >= 50.00):
        e_max = 50.00
    e_min = round(df['PER'].min(),1)
    e_half = round((e_max + e_min)/2,1)
    e_3 = round((e_max-e_half)/2 + e_half,1)
    e_1 = round((e_half-e_min)/2 + e_min,1)

    #가격 데이터 만들기
    df[str(e_max)+"X"] = (df['ttmEPS']*e_max).round(2)
    df[str(e_3)+"X"] = (df['ttmEPS']*e_3).round(2)
    df[str(e_half)+"X"] = (df['ttmEPS']*e_half).round(2)
    df[str(e_1)+"X"] = (df['ttmEPS']*e_1).round(2)
    df[str(e_min)+"X"] = (df['ttmEPS']*e_min).round(2)

    st.subheader('Band Chart')
    title = com_name + '('  + ticker + ') <b>PER Band</b>'
    titles = dict(text= title, x=0.5, y = 0.85) 
    st.dataframe(df)

    fig = make_subplots(specs=[[{"secondary_y": False}]])
    fig.add_trace(go.Scatter(x=df.index, y=df.iloc[:,3], name=df.columns[3],
                            line=dict(color='firebrick', width=2)))
    fig.add_trace(go.Scatter(x=df.index, y=df.iloc[:,4], name=df.columns[4],
                            line = dict(color='purple', width=2, dash='dash')))
    fig.add_trace(go.Scatter(x=df.index, y=df.iloc[:,5], name=df.columns[5],
                            line=dict(color='royalblue', width=2)))
    fig.add_trace(go.Scatter(x=df.index, y=df.iloc[:,6], name=df.columns[6],
                            line = dict(color='green', width=2, dash='dash')))
    fig.add_trace(go.Scatter(x=df.index, y=df.iloc[:,7], name=df.columns[7],
                            line=dict(color='red', width=2) # dash options include 'dash', 'dot', and 'dashdot'
    ))
    fig.add_trace(
        go.Scatter(x = df.index, y = df['Close'], name = '종가',  line=dict(color='black', width=3)),
        secondary_y=False
    )
    fig.update_traces(texttemplate='%{text:.3s}') 
    fig.update_yaxes(title_text="Price", showticklabels= True, showgrid = True, zeroline=True, tickprefix="$")
    fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template="seaborn")
    st.plotly_chart(fig)

def visualize_PBR_band(ticker, com_name, fun_df):
    fun_df.dropna(inplace=True)
    fun_df.loc[:,"BPS"] = fun_df['Equity'] / fun_df['shares']
    fun_df.loc[:,"PBR"] = fun_df['Close'] / fun_df['BPS'] 
    #PBR Max/Min/half/3/1
    b_max = round(fun_df['PBR'].max(),1)
    if(b_max >= 20.00):
        b_max = 20.00
    b_min = round(fun_df['PBR'].min(),1)
    b_half = round((b_max + b_min)/2,1)
    b_3 = round((b_max-b_half)/2 + b_half,1)
    b_1 = round((b_half-b_min)/2 + b_min,1)

    #가격 데이터 만들기
    fun_df[str(b_max)+"X"] = fun_df['BPS']*b_max
    fun_df[str(b_3)+"X"] = (fun_df['BPS']*b_3).round(2)
    fun_df[str(b_half)+"X"] = (fun_df['BPS']*b_half).round(2)
    fun_df[str(b_1)+"X"] = (fun_df['BPS']*b_1).round(2)
    fun_df[str(b_min)+"bX"] = (fun_df['BPS']*b_min).round(2)
    st.dataframe(fun_df)
    
    title = com_name + '('  + ticker + ') <b>PBR Band</b>'
    titles = dict(text= title, x=0.5, y = 0.85) 

    fig = make_subplots(specs=[[{"secondary_y": False}]])
    fig.add_trace(go.Scatter(x=fun_df.index, y=fun_df.iloc[:,5], name=fun_df.columns[5],
                            line=dict(color='firebrick', width=2)))
    fig.add_trace(go.Scatter(x=fun_df.index, y=fun_df.iloc[:,6], name=fun_df.columns[6],
                            line = dict(color='purple', width=2, dash='dash')))
    fig.add_trace(go.Scatter(x=fun_df.index, y=fun_df.iloc[:,7], name=fun_df.columns[7],
                            line=dict(color='royalblue', width=2)))
    fig.add_trace(go.Scatter(x=fun_df.index, y=fun_df.iloc[:,8], name=fun_df.columns[8],
                            line = dict(color='green', width=2, dash='dash')))
    fig.add_trace(go.Scatter(x=fun_df.index, y=fun_df.iloc[:,9], name=fun_df.columns[9],
                            line=dict(color='red', width=2))) # dash options include 'dash', 'dot', and 'dashdot'
     
    fig.add_trace(
        go.Scatter(x = fun_df.index, y = fun_df['Close'], name = '종가',  line=dict(color='black', width=3)),
        secondary_y=False
    )

    fig.update_traces(texttemplate='%{text:.3s}') 
    fig.update_yaxes(title_text="Price", showticklabels= True, showgrid = True, zeroline=True, tickprefix="$")
    fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template="seaborn")
    st.plotly_chart(fig)
        

if __name__ == "__main__":

    input_ticker = st.sidebar.text_input("ticker").upper()
    
    ticker_list = ["APT","AMCX","BIIB", "BIG", "CI", "CPRX", "CHRS", "CSCO","CVS","DHT", "EURN", "HRB", "PRDO", \
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
