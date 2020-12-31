import json
import sqlite3
from datetime import datetime

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly_express as px
import requests
from pandas.io.json import json_normalize
from plotly.subplots import make_subplots

import streamlit as st
from pykrx import stock
import FinanceDataReader as fdr
import re


def main():
    data_load_state = st.text('Loading data...')
    tickers = load_data()

    # con = get_database_connection()
    # cursor = con.cursor()
    # cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    # ticker_list = cursor.fetchall()

    data_load_state.text("Done! (using st.cache)")

    option = st.sidebar.text_input("ticker")

    if option == "":
        option = st.sidebar.selectbox(
            'Ticker',tickers
        )
    
    tic = re.sub('[^A-Za-z]','',str(option))
    df, org_df = make_band_data(tic)
        
    if  st.checkbox('Show raw data'):
        st.subheader('Fundamental Data') 
        st.dataframe(df.style.highlight_max(axis=0))

    '회사명: ', tic
    st.header(tic + " 차트")

    # 기본 챠트 보기
    st.subheader('기본 챠트 ')
    fig = make_subplots(specs=[[{"secondary_y": False}]])
    fig.add_trace(go.Scatter(x=org_df.index, y=org_df['EV/Sales'], mode='lines', name='EV/Sales'))
    fig.add_trace(go.Scatter(x=org_df.index, y=org_df['EV/EBITDA'], mode='lines', name='EV/EBITDA'))
    fig.add_trace(go.Scatter(x=org_df.index, y=org_df['EV/FCF'], mode='lines', name='EV/FCF'))
    st.plotly_chart(fig)

    #안정성 챠트 보기
    st.subheader('안정성 챠트')
    fig1 = make_subplots(specs=[[{"secondary_y": True}]])
    fig1.add_trace(go.Scatter(x=org_df.index, y=org_df['Quick Ratio'], mode='lines', name='Quick Ratio'))
    fig1.add_trace(go.Scatter(x=org_df.index, y=org_df['Current Ratio'], mode='lines', name='Current Ratio'))
    fig1.add_trace(go.Scatter(x=org_df.index, y=org_df['Debt/Equity'], mode='lines', name='Debt/Equity'))
    fig1.add_trace(go.Bar(x=org_df.index, y=org_df['Net Debt/EBITDA'], name='Net Debt/EBITDA'),
        secondary_y=True)
    st.plotly_chart(fig1)

    #PER 밴드 챠트
    st.subheader('밴드 챠트')
    visualize_PER_band(tic, df)

    'Current PER: ', df.iloc[-2,3].round(2) 
    'Last EPS: ', df.iloc[-2,1].round(2)

    #PBR 밴드 챠트
    visualize_PBR_band(tic, df)

    'Current PBR: ', df.iloc[-2,4].round(2) 
    'Last BPS: ', round(df.iloc[-2,2],2)


def make_band_data(option):
    #get db connection
    con = sqlite3.connect("D:/OneDrive - 호매실고등학교/데이터/usfinance.db")

    #Get Table
    df = pd.read_sql(f"SELECT * FROM {option}", con, index_col='Date')
    #밴드 챠트 위해 필요한 데이터만 가져오자.
    fun_df= df[['Close','EPS','Shareholders Equity per Share','P/E ratio','P/B ratio', 'EV/EBIT']]
    fun_df.columns = ['Close', 'EPS','BPS', 'PER', 'PBR', 'EV/EBIT']
 
    #PER Max/Min/half/3/1
    e_max = fun_df['PER'].max().round(2)
    if(e_max >= 30.00):
        e_max = 30.00
    e_min = fun_df['PER'].min().round(2)
    e_half = ((e_max + e_min)/2).round(2)
    e_3 = ((e_max-e_half)/2 + e_half).round(2)
    e_1 = ((e_half-e_min)/2 + e_min).round(2)

    #가격 데이터 만들기
    fun_df[str(e_max)+"X"] = fun_df['EPS']*e_max
    fun_df[str(e_3)+"X"] = (fun_df['EPS']*e_3).round(2)
    fun_df[str(e_half)+"X"] = (fun_df['EPS']*e_half).round(2)
    fun_df[str(e_1)+"X"] = (fun_df['EPS']*e_1).round(2)
    fun_df[str(e_min)+"X"] = (fun_df['EPS']*e_min).round(2)

    #PBR Max/Min/half/3/1
    b_max = fun_df['PBR'].max().round(2)
    if(b_max >= 20.00):
        b_max = 20.00
    b_min = fun_df['PBR'].min().round(2)
    b_half = ((b_max + b_min)/2).round(2)
    b_3 = ((b_max-b_half)/2 + b_half).round(2)
    b_1 = ((b_half-b_min)/2 + b_min).round(2)

    #가격 데이터 만들기
    fun_df[str(b_max)+"BX"] = fun_df['BPS']*b_max
    fun_df[str(b_3)+"BX"] = (fun_df['BPS']*b_3).round(2)
    fun_df[str(b_half)+"BX"] = (fun_df['BPS']*b_half).round(2)
    fun_df[str(b_1)+"BX"] = (fun_df['BPS']*b_1).round(2)
    fun_df[str(b_min)+"BX"] = (fun_df['BPS']*b_min).round(2)

    return fun_df, df

@st.cache(allow_output_mutation=True)
def get_database_connection():
    con = sqlite3.connect("D:/OneDrive - 호매실고등학교/데이터/usfinance.db")
    
    return con


@st.cache
def load_data():
    con = sqlite3.connect("D:/OneDrive - 호매실고등학교/데이터/usfinance.db")
    cursor = con.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    ticker_list = cursor.fetchall()

    return ticker_list

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
