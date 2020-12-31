import json
import sqlite3
from datetime import datetime

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import requests
from pandas.io.json import json_normalize
from plotly.subplots import make_subplots

import streamlit as st
from pykrx import stock
import FinanceDataReader as fdr
import alphaj_krx_crawler as aj

import OpenDartReader

pd.options.display.float_format = '{:.2f}'.format

api_key = '880530eb3781d549e88be02dd34bc4e6f98b13f7'
dart = OpenDartReader(api_key) 

def main():
    data_load_state = st.text('Loading data...')
    tickers, krx = load_data()
    data_load_state.text("Done! (using st.cache)")

    com_name = st.sidebar.text_input("Company Name")

    if com_name == "":
        com_name = st.sidebar.selectbox(
            'Company Name',
            krx['stock_name'].to_list() #tickers
        )

    options = krx[krx['stock_name'] == com_name]
    st.write(options)
    option = options.iloc[0,2]
    code = options.iloc[0,1]
    # st.write(code)
    ## make PER/PBR
    #회사명이 다른 경우 어찌해야 하나?
    fun_df = Get_Fundamental_Data(code,2015,2019)
    df = make_band_data(code)

    fun_df = fun_df.round(decimals=1)
        
    if  st.checkbox('Show raw data'):
        st.subheader('Fundamental Data') 
        st.dataframe(fun_df.style.highlight_max(axis=0))
        
    # ticker_name = stock.get_market_ticker_name(option)
   
    st.title(option + " Show me the Chart")
    
    visualize_fundamental(option, fun_df, code)

    visualize_PER_band(option, df)

    'Current PER: ', df.iloc[-1,2] 
    ' Last EPS: ', df.iloc[-1,3]
    '현재가: ', df.iloc[-1,5]
    "적정 주가: ", round(df.iloc[-1,3]*100/7.5,1)

    visualize_PBR_band(option, df)

    'Current PBR: ', df.iloc[-1,4].round(2) 
    ' Last BPS: ', df.iloc[-1,1]

@st.cache
def load_data():
    # 코스피, 코스닥, 코넥스 종목 리스트 가져오기
    tickers = stock.get_market_ticker_list()
    # krx1 = fdr.StockListing('KRX')
    krx_list = aj.get_stock_list_from_krx()
    krx = pd.DataFrame(krx_list)
    krx = krx.iloc[1:]

    return tickers, krx


def Get_Fundamental_Data(company, From, To):
  df_info = {}
  for year in range(From, To+1) :
    fs = dart.finstate_all(company, year) #전체 재무제표(전체)

    def fs_nm(val): # 당기 재무제표
      fs_nm = int(fs[fs['account_nm'].str.contains(val)][['thstrm_amount']].iloc[0,0].replace(',',''))
      return fs_nm
    def fs_nm_last(val): # 전기 재무제표
      fs_nm_last = int(fs[fs['account_nm'].str.contains(val)][['frmtrm_amount']].iloc[0,0].replace(',',''))
      return fs_nm_last

    #배당
    dv = dart.report(company, '배당', year)
    dv_dps = dv[dv['se'] == '주당 현금배당금(원)']
    dv_eps = dv[dv['se'].str.contains('주당순이익')]
    dv_yield = dv[dv['se'].str.contains('현금배당수익률')]
    dv_TD = dv[dv['se'].str.contains('현금배당금총액')]

    #factors
    equity = fs_nm('자본총계') #당기 자본
    equity_last = fs_nm_last('자본총계') #전기 자본
    liability = fs_nm('부채총계') # 당기 부채
    liability_last = fs_nm_last('부채총계') # 전기 부채
    current_liabilities = fs_nm_last('유동부채') #유동 부채
    non_current_liabilities = liability - current_liabilities #비유동부채
    assets = equity + liability #당기 자산
    assets_last = equity_last + liability_last #전기 자산
    revenue = fs_nm('매출액|영업수익') #당기 매출액
    revenue_last = fs_nm_last('매출액|영업수익') #전기 매출액
    income = fs_nm('영업이익|영업이익(손실)') #당기 영업이익
    income_last = fs_nm_last('영업이익|영업이익(손실)') #전기 영업이익
    profit = fs_nm('당기순이익|반기순이익|기순이익') #당기 순이익
    profit_last = fs_nm_last('당기순이익|반기순이익|기순이익') #전기 순이익
    try:
      CostOfSales = abs(fs_nm('매출원가|재료비')) #당기 매출원가
      CostOfMgnt = abs(fs_nm('판매비와관리비|영업비용')) #판매 및 관리비
      GPM = round((revenue - CostOfSales)/revenue*100,1) #매출총이익률
    except:
      CostOfSales = 0
      CostOfMgnt = 0
      GPM = 0
    
    EPS = int(dv_eps[['thstrm']].iloc[0,0].replace(',','').strip()) #주당 순이익
    try:
      DPS = int(dv_dps[['thstrm']].iloc[0,0].replace(',','').strip()) #주당 배당금
      Yield = round(int(dv_yield[['thstrm']].iloc[0,0].replace(',','').strip())/100,1) #배당수익률
      TD = int(dv_TD[['thstrm']].iloc[0,0].replace(',','').strip())*1000000 # 배당금 총액
    except:
      DPS = 0
      Yield = 0
      TD = 0
    
    CF_operating = fs_nm('영업활동') # 영업활동현금흐름
    CF_investing = fs_nm('투자활동') # 투자활동현금흐름
    CF_financing = fs_nm('재무활동') # 재무활동현금흐름

    try:
      CAPEX = fs_nm("유형자산의 취득") + fs_nm( "무형자산의 취득") # 유형자산취득 + 무형자산취득 
    except : CAPEX = 0 
    
    try : 
      inventory_assets = fs_nm ('재고자산') # 당기 재고자산
      inventory_assets_last = fs_nm_last('재고자산') # 전기 재고자산 
      turnover_inventory = round(revenue /((assets + assets_last)/2),2) 
    except : 
      inventory_assets = 0
      invenstory_assets_last = 0 
      turnover_inventory = 0 
    turnover_assets = round(revenue / ((assets + assets_last ) / 2), 2) #총자산 회전율
    FCF = CF_operating - CAPEX #잉여 현금흐름
    ROE = round(profit / ((equity + equity_last) / 2) * 100, 1) # 자기자본수익률
    ROA = round(profit / ((assets + assets_last) / 2) * 100, 1) # 자산수익률
    OPM = round(income / revenue*100,1) #영업이익률
    NPM = round(profit / revenue*100,1 ) #순이익률
    PR = round(DPS / EPS*100, 1) #배당성향
    DR = round(liability / equity*100, 1) #부채비율
    DR_current = round(current_liabilities / equity*100, 1) # 유동부채비율
    GR_revenue = round((revenue / revenue_last - 1)*100, 1) # Growth Rate_revenue, 매출액 증가율
    GR_income = round((income / income_last - 1)*100, 1) # Growth Rate_income, 영업이익 증가율
    GR_profit = round((profit / profit_last - 1)*100, 1) # Growth Rate_profit, 순이익 증가율


    # dictionary에 담기
    df_info[str(year)] = revenue, CostOfSales, CostOfMgnt, income, profit, \
                          GPM, OPM, NPM, ROE, ROA, GR_revenue, GR_income, GR_profit, \
                          CF_operating, CAPEX, FCF, TD, CF_investing, CF_financing, \
                          EPS, DPS, PR, Yield, \
                          DR, DR_current, \
                          turnover_assets, turnover_inventory, \
                          inventory_assets, assets, equity, liability

    # print(type(df_info))
    # print(df_info)

  Index = [ '매출액', '매출원가', '판관비', '영업이익', '순이익', 
           'GPM', 'OPM', 'NPM', 'ROE', 'ROA', '매출 증감률', '영업이익 증감률', '순이익 증감률', 
           '영업활동현금흐름', 'CAPEX', 'FCF', '배당금 총액', '투자활동현금흐름', '재무활동현금흐름',
           'EPS', 'DPS', '배당성향', '배당률',
           '부채 비율', '유동부채 비율',
           '자산 회전률', '재고자산 회전율',
            '재고자산', '자산', '자본', '부채']

  fun_df = pd.DataFrame(data =  df_info, index = Index)
  return fun_df

#입력: 종목코드
def make_band_data(option):
    # st.write(option)
    #오늘날짜까지
    now = datetime.now()
    today = '%s%s%s' % ( now.year, now.month, now.day)
    fun_df = stock.get_market_fundamental_by_date("20080101", today, option, "m")

    #Price 추가 => 이것의 문제는 수정주가가 아님
    # fun_df['Close'] = fun_df['PER'] * fun_df['EPS']

    #Price 수정 주가로 변경
    p_df = stock.get_market_ohlcv_by_date("20080101", today, option, "m")
    fun_df['Close'] = p_df['종가']

    #PER Max/Min/half/3/1
    e_max = round(fun_df['PER'].max(),1)
    if(e_max >= 30.00):
        e_max = 30.00
    e_min = round(fun_df['PER'].min(),1)
    e_half = round((e_max + e_min)/2,1)
    e_3 = round((e_max-e_half)/2 + e_half,1)
    e_1 = round((e_half-e_min)/2 + e_min,1)

    #가격 데이터 만들기
    fun_df[str(e_max)+"X"] = (fun_df['EPS']*e_max).round(2)
    fun_df[str(e_3)+"X"] = (fun_df['EPS']*e_3).round(2)
    fun_df[str(e_half)+"X"] = (fun_df['EPS']*e_half).round(2)
    fun_df[str(e_1)+"X"] = (fun_df['EPS']*e_1).round(2)
    fun_df[str(e_min)+"X"] = (fun_df['EPS']*e_min).round(2)

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

    fun_df.round(decimals=2)
 
    return fun_df


def visualize_fundamental(company, df, code):
    company_nm = company
    # company_nm = dart.company(company)["stock_name"] # 종목명
    company_nm_eng = dart.company(code)["corp_name_eng"] # 회사 영문명 
    company_stock_code = code
    # company_stock_code = dart.company(company)["stock_code"] # 종목코드
    title = company_nm + '(' + company_nm_eng + ', ' + company_stock_code + ')'
    titles = dict(text= title, x=0.5, y = 0.85) 

    # colors 
    marker_colors = ['rgb(27,38,81)', 'rgb(205,32,40)', 'rgb(22,108,150)', 'rgb(255,255,255)', 'rgb(237,234,255)']
    # copyright annotations = [] annotations. append (dict (xref="paper, yref="paper", x=0.5, y=-8.1, xang text="Copyright 2020. . ALL rights reserve font-dict(family="Antal", size=12, color="rgb( showarrow=False)) 
    
    x_data = df.keys() # x축
    annotations = []
    # annotations.append(dict(xref='paper', yref='paper', x=0.5, y=-0.1, xanchor='center', yanchor='top',
    #                     text='Indiesoul',
    #                     font=dict(family='Arial', size=12, color='rgb(150,150,150)'),
    #                     showarrow=False))     
    fig = make_subplots(specs=[[{'secondary_y': True}]]) 
    y_data_bar = [ '매출액', '매출원가', '판관비']
    y_data_line = ['영업이익', '순이익']

    for y_data, color in zip(y_data_bar, marker_colors) :
        fig.add_trace(go.Bar(name = y_data, x = x_data, y = df.loc[y_data],
                                text = df.loc[y_data], textposition = 'outside', width = 0.2, marker_color= color),
                                secondary_y = False) 
    for y_data, color in zip(y_data_line, marker_colors): 
        fig.add_trace(go.Scatter(mode='lines+markers+text', 
                                    name = y_data, x =  x_data, y= df.loc[y_data],
                                    text= df.loc[y_data], textposition = 'top center', marker_color = color),
                                    secondary_y = True)

    fig.update_traces(texttemplate='%{text:.3s}') 
    fig.update_yaxes (range=[0, max(df.loc[y_data_bar[0]]) * 2 ], secondary_y = False)
    fig.update_yaxes (range=[-max(df.loc[y_data_line[0]]), max(df.loc[y_data_line[0]])* 1.2], secondary_y = True)
    fig.update_yaxes (showticklabels= False, showgrid = False, zeroline=False)
    fig.update_layout(title = titles, titlefont_size=15, xaxis_tickformat = 'd')# legend_title_text='( 단위 : 원)', 
                    # xaxis_tickformat = 'd', annotations=annotations) #

    st.plotly_chart(fig)

    # Line chart
    fig = make_subplots(specs=[[{'secondary_y': True}]]) 
    y_datas = ['GPM', 'OPM', 'NPM']

    for y_data, color in zip(y_datas, marker_colors): 
        fig.add_trace(go.Scatter(mode='lines+markers+text', name = y_data, x = x_data, y=df.loc[y_data],
        text = df.loc[y_data], textposition = 'top center', marker_color = color),
        secondary_y = True)

    fig.update_traces(texttemplate='%{text:.3s}') 
    fig.update_yaxes(showticklabels= False, showgrid=False, zeroline = False)
    fig.update_xaxes(showgrid= False, zeroline = False) 
    fig.update_layout(title = titles, titlefont_size = 15 , xaxis_tickformat = 'd', annotations=annotations) #legend_title_text='(단위 : %)', 
                    
    st.plotly_chart(fig)

    # Bar chart

    fig = make_subplots(specs=[[{'secondary_y': True}]]) 
    y_datas = ['매출 증감률', '영업이익 증감률', '순이익 증감률']

    for y_data, color in zip (y_datas, marker_colors):
        fig.add_trace(go.Bar(name = y_data, x= x_data, y = df.loc[y_data],
                            text = df.loc[y_data], textposition = 'outside', width = 0.2, marker_color = color),
                            secondary_y = False)
    
    fig.update_traces(texttemplate='%{text:.3s}') 
    fig.update_yaxes(showticklabels= False, showgrid=False, zeroline = False)
    fig.update_xaxes(showgrid= False, zeroline= False) 
    fig.update_layout(title = titles, titlefont_size = 15, xaxis_tickformat = 'd', annotations=annotations)#legend_title_text='(단위 : %)', 
                    # xaxis_tickformat = 'd', annotations=annotations)
    st.plotly_chart(fig)

    fig = make_subplots(specs=[[{'secondary_y': True}]]) 
    y_data_bar1 = ['EPS', 'DPS']
    y_data_line1 = ['배당률']

    for y_data, color in zip(y_data_bar1, marker_colors) :
        fig.add_trace(go.Bar(name = y_data, x = x_data, y = df.loc[y_data],
                                text = df.loc[y_data], textposition = 'outside', width = 0.2, marker_color= color),
                                secondary_y = False) 
        fig.add_trace(go.Scatter(mode='lines+markers+text', 
                                    name = y_data, x =  x_data, y= df.loc[y_data_line1],
                                    text= df.loc[y_data_line1], textposition = 'top center', marker_color = color),
                                    secondary_y = True)

    fig.update_traces(texttemplate='%{text:.3s}') 
    fig.update_yaxes (range=[0, max(df.loc[y_data_bar1[0]]) * 2 ], secondary_y = False)
    fig.update_yaxes (range=[-max(df.loc[y_data_line1[0]]), max(df.loc[y_data_line1[0]])* 1.2], secondary_y = True)
    fig.update_yaxes (showticklabels= False, showgrid = False, zeroline=False)
    fig.update_layout(title = titles, titlefont_size=15, xaxis_tickformat = 'd', annotations=annotations)# legend_title_text='( 단위 : 원)', 
                    # xaxis_tickformat = 'd', annotations=annotations) #

    st.plotly_chart(fig)

    # Line chart
    fig = make_subplots(specs=[[{'secondary_y': True}]]) 
    y_datas1 = ['ROE', 'ROA']

    for y_data, color in zip(y_datas1, marker_colors): 
        fig.add_trace(go.Scatter(mode='lines+markers+text', name = y_data, x = x_data, y=df.loc[y_data],
        text = df.loc[y_data], textposition = 'top center', marker_color = color),
        secondary_y = True)

    fig.update_traces(texttemplate='%{text:.3s}') 
    fig.update_yaxes(showticklabels= False, showgrid=False, zeroline = False)
    fig.update_xaxes(showgrid= False, zeroline = False) 
    fig.update_layout(title = titles, titlefont_size = 15 , xaxis_tickformat = 'd', annotations=annotations) #legend_title_text='(단위 : %)', 
                    
    st.plotly_chart(fig)

    # Combo chart

    fig = make_subplots(specs=[[{'secondary_y': True}]]) 
    y_data_bar2 = [ '자산', '자본', '부채']
    y_data_line2 = ['부채 비율', '유동부채 비율']

    for y_data, color in zip(y_data_bar2, marker_colors) :
        fig.add_trace(go.Bar(name = y_data, x = x_data, y = df.loc[y_data],
                                text = df.loc[y_data], textposition = 'outside', width = 0.2, marker_color= color),
                                secondary_y = False) 
    for y_data, color in zip(y_data_line2, marker_colors): 
        fig.add_trace(go.Scatter(mode='lines+markers+text', 
                                    name = y_data, x =  x_data, y= df.loc[y_data],
                                    text= df.loc[y_data], textposition = 'top center', marker_color = color),
                                    secondary_y = True)

    fig.update_traces(texttemplate='%{text:.3s}') 
    fig.update_yaxes (range=[0, max(df.loc[y_data_bar[0]]) * 2 ], secondary_y = False)
    fig.update_yaxes (range=[-max(df.loc[y_data_line[0]]), max(df.loc[y_data_line[0]])* 1.2], secondary_y = True)
    fig.update_yaxes (showticklabels= False, showgrid = False, zeroline=False)
    fig.update_layout(title = titles, titlefont_size=15, xaxis_tickformat = 'd', annotations=annotations)# legend_title_text='( 단위 : 원)', 
                    # xaxis_tickformat = 'd', annotations=annotations) #

    st.plotly_chart(fig)

    # Bar chart

    fig = make_subplots(specs=[[{'secondary_y': True}]]) 
    y_datas2 = ['영업활동현금흐름', '투자활동현금흐름', '재무활동현금흐름']

    for y_data, color in zip (y_datas2, marker_colors):
        fig.add_trace(go.Bar(name = y_data, x= x_data, y = df.loc[y_data],
                            text = df.loc[y_data], textposition = 'outside', width = 0.2, marker_color = color),
                            secondary_y = False)
    
    fig.update_traces(texttemplate='%{text:.3s}') 
    fig.update_yaxes(showticklabels= False, showgrid=False, zeroline = False)
    fig.update_xaxes(showgrid= False, zeroline= False) 
    fig.update_layout(title = titles, titlefont_size = 15, xaxis_tickformat = 'd', annotations=annotations)#legend_title_text='(단위 : %)', 
                    # xaxis_tickformat = 'd', annotations=annotations)
    st.plotly_chart(fig)


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
        secondary_y=False,
    )

    # fig.update_layout(title_text=com_name + " PER 밴드", title_font_size=20)
    fig.update_layout(
    title={
        'text': com_name + " PER 밴드",
        'y':0.9,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'})
    fig.update_yaxes(title_text="주가", secondary_y=False)
    fig.update_xaxes(ticks="inside", tickcolor='crimson', ticklen=10)
    fig.update_yaxes(ticks="inside", tickcolor='crimson', ticklen=10)
    
    # # Plot!
    st.plotly_chart(fig)

def visualize_PBR_band(com_name, df):
    df.round(decimals=2)
 
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
        secondary_y=False,
    )

    # fig.update_layout(title_text=com_name + " PBR 밴드", title_font_size=20)
    fig.update_layout(
        title={
            'text': com_name + " PBR 밴드",
            'y':0.9,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'})
    fig.update_yaxes(title_text="주가", secondary_y=False)
    fig.update_xaxes(ticks="inside", tickcolor='crimson', ticklen=10)
    fig.update_yaxes(ticks="inside", tickcolor='crimson', ticklen=10)
    
    # # Plot!
    st.plotly_chart(fig)
        

if __name__ == "__main__":
    main()
