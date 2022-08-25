from re import S
import time
from datetime import datetime
import drawAPT_weekly
import datetime
from dateutil.relativedelta import relativedelta

import numpy as np
import pandas as pd
from pandas.io.formats import style

import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from st_aggrid import AgGrid, GridOptionsBuilder
from st_aggrid.shared import GridUpdateMode

import requests
import json
from pandas.io.json import json_normalize
from urllib.request import urlopen

import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots

import streamlit as st
import FinanceDataReader as fdr

import matplotlib.pyplot as plt
from matplotlib import font_manager, rc
import seaborn as sns

pd.set_option('display.float_format', '{:.2f}'.format)

utcnow= datetime.datetime.utcnow()
time_gap= datetime.timedelta(hours=9)
kor_time= utcnow+ time_gap
now_date = kor_time.strftime('%Y.%m.%d-%H:%M:%S')

token = 'pk.eyJ1Ijoic2l6aXB1c3gyIiwiYSI6ImNrbzExaHVvejA2YjMyb2xid3gzNmxxYmoifQ.oDEe7h9GxzzUUc3CdSXcoA'
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
<h2 style="font-size:200%; color:#008080; font-family:Georgia"> 전국 분양권/재개발/재건축 아파트 시세 확인 <br>
<hr style= "  display: block;
  margin-top: 0.5em;
  margin-bottom: 0.5em;
  margin-left: auto;
  margin-right: auto;
  border-style: inset;
  border-width: 1.5px;"></h1>
"""

st.set_page_config(page_title="전국 분양권/재개발/재건축 아파트 시세 확인", page_icon="", layout="wide")
st.markdown('<style>body{background-color: #fbfff0}</style>',unsafe_allow_html=True)
st.markdown(html_header, unsafe_allow_html=True)
st.markdown(""" <style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style> """, unsafe_allow_html=True)

def load_data():
    #gsheet
    scope = [
        'https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/drive',
        ]

    json_file_name = './files/weekly-house-db-ac0a43b61ddd.json'

    credentials = ServiceAccountCredentials.from_json_keyfile_name(json_file_name, scope)
    gc = gspread.authorize(credentials)

    spreadsheet_url = 'https://docs.google.com/spreadsheets/d/1-hIsPEvydoLQqouPNY7CT5_n--4ftey0nNNRfe8nce8/edit?usp=sharing'

    doc = gc.open_by_url(spreadsheet_url)

    sum_sheet = doc.worksheet('summary')
    s_values = sum_sheet.get_all_values()
    s_header, s_rows = s_values[0], s_values[1:]
    sum_df = pd.DataFrame(s_rows, columns=s_header)
    sum_df['거래가(만원)'] = sum_df['거래가(만원)'].astype(int)
    sum_df['위도'] = sum_df['위도'].astype(float)
    sum_df['경도'] = sum_df['경도'].astype(float)

    t_sheet = doc.worksheet('total')
    t_values = t_sheet.get_all_values()
    t_header, t_rows = t_values[0], t_values[1:]
    total_df = pd.DataFrame(t_rows, columns=t_header)

return sum_df, total_df

def show_total():
    
    px.set_mapbox_access_token(token)
    fig = px.scatter_mapbox(jdf, lat="위도", lon="경도",     color="주거형태", size="거래가(만원)", hover_name="단지명", hover_data=["매매물건수", "공급면적", "지역명"],
                    color_continuous_scale=px.colors.cyclical.IceFire, size_max=30, zoom=10)
    fig.update_layout(
        title='수도권 재건축-재개발 분양권 아파트 시세',
        # autosize=True,
        # hovermode='closest',
        # showlegend=True,
        # mapbox=dict(
        #     #accesstoken=mapbox_access_token,
        #     bearing=0,
        #     # center=dict(
        #     #     lat=37.2,
        #     #     lon=127.0
        #     # ),
        #     pitch=0,
        #     zoom=3,
        #     style='light'
        #),
    )
    fig.show()

def show_local(city_apt)
    px.set_mapbox_access_token(token)
    fig = px.scatter_mapbox(city_apt, lat="위도", lon="경도",     color="주거형태", size="거래가(만원)", hover_name="단지명", hover_data=["매매물건수", "공급면적", "지역명"],
                    color_continuous_scale=px.colors.cyclical.IceFire, size_max=30, zoom=10)
    fig.update_layout(
        title='수도권 재건축-재개발 분양권 아파트 시세',

    )
    fig.show()

if __name__ == "__main__":
    data_load_state = st.text('Loading APT List...')
    s_df, t_df = load_data()
    show_total(s_df)
    st.table(t_df)
    data_load_state.text("Done! (using st.cache)")
    # st.dataframe(tickers)
    # st.dataframe(krx)
    city_name = st.sidebar.selectbox(
        '지역',
        s_df['시도'].to_list() #tickers
        )

    city_apt = s_df[s_df['시도'] == city_name]

    apt_len = len(city_apt)
    st.write("단지명과 공급 면적에 따라 분류한 총 ("+ apt_len+ " ) 개의 아파트가 있습니다.")  
    submit = st.sidebar.button('해당 지역만 보기')

    if submit:
        show_local(city_apt)
        