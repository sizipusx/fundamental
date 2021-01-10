
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
import FinanceDataReader as fdr
from alpha_vantage.fundamentaldata import FundamentalData as FD


#오늘날짜까지
now = datetime.now()
today = '%s-%s-%s' % ( now.year, now.month, now.day)

@st.cache
def load_data():
    #S&P 500, NASDAQ, DOWJONES

    #FRED 주요 경기 선행 지표
    #1o년 장기물 -  2년 단기물 금리차(10-Year Treasury Constant Maturity Minus 2-Year Treasury Constant Maturity)
    #주간 실업수당 청구 건수 (ICSA) 연속 실업수당청구 건수 CCSA 
    #UMCSENT (University of Michigan: Consumer Sentiment)
    #주택 판매 지수 (HSN1F)
    #실업률 (UNRATE)  M2 통화량(M2) 하이일드 채권 스프레드 (BAMLH0A0HYM2)
    basic_df = fdr.DataReader(['SP500','NASDAQCOM', 'T10Y2Y','ICSA', 'CCSA', \
         'UMCSENT', 'HSN1F', 'UNRATE', 'M2', 'BAMLH0A0HYM2' ], start='2006', data_source='fred')
    
    return basic_df


def run() :
    data_load_state = st.text('Loading All Macro Data...')
    df = load_data()
    data_load_state.text("Done! (using st.cache)")
    
    st.title("미국 주요 경제 지표와 S&P500")

    column_list = df.columns.to_list()
    list_index = macro_list.index(selected_macro)
    column_list_name = column_list[list_index]
    # 챠트 기본 설정 
    #marker_colors = ['#34314c', '#47b8e0', '#ff7473', '#ffc952', '#3ac569']
    marker_colors = ['rgb(27,38,81)', 'rgb(205,32,40)', 'rgb(22,108,150)', 'rgb(255,69,0)', 'rgb(237,234,255)']
    template = 'seaborn' #"plotly", "plotly_white", "plotly_dark", "ggplot2", "seaborn", "simple_white", "none".

    titles = dict(text= macro_list[1] + ' & '+ selected_macro, x=0.5, y = 0.9) 

    fig = make_subplots(specs=[[{'secondary_y': True}]]) 
    x_data = df.index  
    y_datas = ['SP500','T10Y2Y']

    # for y_data, color in zip(y_datas, marker_colors) :
    #   fig.add_trace(go.Scatter(mode='lines', 
    #                               name = y_data , x =  x_data, y= df[y_data],
    #                               text= df[y_data], textposition = 'top center', marker_color = color),# marker_colorscale='RdBu'),
    #                               secondary_y = True)
    fig.add_trace(go.Scatter(mode='lines', name = 'SP500', x =  df.index, y= df['SP500'],
                                text= df['SP500'], textposition = 'top center', marker_color = marker_colors[0]),# marker_colorscale='RdBu'),
                                secondary_y = False)
    fig.add_trace(go.Scatter(mode='lines', name = selected_macro, x =  df.index, y= df.iloc[:,list_index],
                                text= df.iloc[:,list_index], textposition = 'top center', marker_color = marker_colors[1]),# marker_colorscale='RdBu'),
                                secondary_y = True)
    fig.update_traces(texttemplate='%{text:.3s}') 
    fig.update_yaxes(title_text=column_list_name, showticklabels= True, showgrid = True, zeroline=True, zerolinecolor='LightPink', secondary_y = True) #ticksuffix="%"
    fig.update_yaxes(title_text='index', showticklabels= True, showgrid = False, zeroline=False, secondary_y = False) #tickprefix="$", 
    fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template)
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

if __name__ == "__main__":
 
    macro_list = ['10-Year Treasury Constant Maturity Minus 2-Year Treasury Constant Maturity','S&P500', 'NASDAQ', \
                            '하이일드 채권 스프레드', 'Consumer Sentiment',  '주택 판매 지수', 'Unemployment Rate', \
                            'M2 Money Stock', '주간 실업수당 청구 건수', '연속 실업수당청구 건수']
            
    selected_macro = st.sidebar.selectbox(
            '미국 주요 경제 지표',macro_list
        )
    submit = st.sidebar.button('Draw Macro')
    if submit:
        run()
