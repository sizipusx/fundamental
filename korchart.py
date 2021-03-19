import time
from datetime import datetime

import numpy as np
import pandas as pd
import requests
import json
from pandas.io.json import json_normalize
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import streamlit as st
from pykrx import stock
import FinanceDataReader as fdr


@st.cache
def load_data():
    # 코스피, 코스닥, 코넥스 종목 리스트 가져오기
    tickers = stock.get_market_ticker_list()
    krx = fdr.StockListing('KRX')
    krx = krx[~krx['Name'].str.endswith('우','A', 'B', '스팩', 'C', ')', '호', '풋', '콜', 'ETN')]
    krx = krx[~(krx['Symbol'].str.len() != 6)]
    krx = krx[~(krx['Market'].str.endswith('X')]
    return tickers, krx

if __name__ == "__main__":
    data_load_state = st.text('Loading KRX Company List...')
    tickers, krx = load_data()
    data_load_state.text("Done! (using st.cache)")
    st.dataframe(tickers)
    st.dataframe(krx)
    etf = krx[krx['Sector'].isnull()]
    krx = krx[~krx['Sector'].isnull()]
    com_name = st.sidebar.text_input("Company Name")

    if com_name == "":
        com_name = st.sidebar.selectbox(
            'Company Name',
            krx['Name'].to_list() #tickers
        )

    # options = krx[krx['stock_name'] == com_name]
    # st.write(options)
    # option = options.iloc[0,2]
    # code = options.iloc[0,1]

    submit = st.sidebar.button('Analysis')

    if submit:
        run()