
import pandas as pd
import requests
import json
import streamlit as st
from pandas.io.json import json_normalize
import numpy as np
#from tqdm.notebook import tqdm as tn
import time
from datetime import datetime
import ecos_chart as ec

now = datetime.now()
today = '%s%s%s' % ( now.year, now.month, now.day)
rmonth = '%s%s' % ( now.year, now.month)

pd.set_option('display.float_format', '{:.2f}'.format)
#############html 영역####################
html_header="""
<head>
<title>Ecos chart</title>
<meta charset="utf-8">
<meta name="keywords" content="chart, analysis">
<meta name="description" content="House data analysis">
<meta name="author" content="indiesoul">
<meta name="viewport" content="width=device-width, initial-scale=1">
</head>
<h2 style="font-size:200%; color:#008080; font-family:Georgia">한국은행 경제통계 조회<br>
<hr style= "  display: block;
  margin-top: 0.5em;
  margin-bottom: 0.5em;
  margin-left: auto;
  margin-right: auto;
  border-style: inset;
  border-width: 1.5px;"></h1>
"""

st.set_page_config(page_title="한국은행 경제통계 조회", page_icon="files/logo2.png", layout="wide")
st.markdown('<style>body{background-color: #fbfff0}</style>',unsafe_allow_html=True)
st.markdown(html_header, unsafe_allow_html=True)
st.markdown(""" <style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style> """, unsafe_allow_html=True)


@st.cache
def query_ecos(stat_code, stat_item, start_date, end_date, cycle_type="Q"):
    auth_key = "71BO71RCBA99FVU3BETA/" #발급 받은 Key 를 넣으면 더 많은 데이터 수집 가능
    req_type = "json/"
    lang = "kr/"
    start_no = "1/"
    end_no ="10000/"
    stat_code = stat_code + "/"
    #stat_code = stat_code.split('/')[0] + "/"
    cycle_type = cycle_type + "/"
    start_date = start_date + "/"
    end_date = end_date + "/"
    #item_no = stat_code.split('/')[1]
    item_no = stat_item

    url = "http://ecos.bok.or.kr/api/StatisticSearch/" +  \
        auth_key + req_type + lang + start_no + end_no + \
        stat_code + cycle_type + start_date + end_date + item_no
    print(url)
    r = requests.get(url)
    if '해당하는 데이터가 없습니다' in r.text:
        return None
    
    jo = json.loads(r.text)
    print(jo)
    df = json_normalize(jo['StatisticSearch']['row'])
    if cycle_type != 'Q':
        df['TIME'] = df['TIME'] + '0101'
        df['TIME'] = df['TIME'].str.replace(r'(\d{4})(\d{2})(\d{2})(.*)', r'\1-\2-\3')
    return df

def run(stat_ticker):
    #가계 신용: 가계대출(주택담보대출+기타대출) + 판매신용
    daechul_index_symbols = {'주택담보대출':'151Y005/11100A0','기타대출':'151Y005/11100B0'}
                            #'주택담보대출':'008Y001/11000A0','기타대출':'008Y001/11000B0'}
    daechul_index_tickers = daechul_index_symbols.values()
    start_date = "200501"
    # end_date = "201910"
    # end_date = rmonth
    end_date = "202212"
    cycle_type = "M"

    daechul_all_data = {}
    for ticker in daechul_index_tickers:
        stat_code = ticker.split('/')[0]
        stat_item = ticker.split('/')[1]
        daechul_all_data[ticker] = query_ecos(stat_code, stat_item, start_date, end_date, cycle_type)    
    #컬럼명 종목명으로 변경
    daechul_df = pd.DataFrame({tic: data['DATA_VALUE'] for tic, data in daechul_all_data.items()})
    daechul_df.columns = daechul_index_symbols.keys()
    #날짜 설정
    tempdf = daechul_all_data.get('151Y005/11100A0')
    daechul_df.set_index(keys=tempdf['TIME'], inplace=True)
    daechul_df = daechul_df.astype(float)/1000
    daechul_df = daechul_df.round(decimals=1)
    daechul_ch = daechul_df.pct_change()*100
    daechul_ch = daechul_ch.round(decimals=2)
    ec.ecos_chart(stat_ticker, daechul_df, daechul_ch)



if __name__ == "__main__":
    data_load_state = st.text('Loading 통계정보 List...')
    source = st.sidebar.radio(
            label = "Choose the Source", 
            options=('Ecos', 'Fred'),
            index = 0,
            horizontal= True)
    eco_list = ['', '가계신용']
    data_load_state.text("Done! (using st.cache)")
    # st.dataframe(tickers)
    # st.dataframe(krx)
    stat_ticker = st.sidebar.selectbox(
        '주요 통계 정보',
        eco_list #tickers
        )
    
    #st.dataframe(basic_df)
    submit = st.sidebar.button('Get Data')

    if submit:
        run(stat_ticker)