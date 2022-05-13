from re import S
import time
from datetime import datetime
import drawAPT_weekly

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
cmap = cmap=sns.diverging_palette(250, 5, as_cmap=True)

# font_list = [font.name for font in font_manager.fontManager.ttflist]
# st.write(font_list)

pd.set_option('display.float_format', '{:.2f}'.format)
# 챠트 기본 설정 
# marker_colors = ['#34314c', '#47b8e0', '#ffc952', '#ff7473']
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
<h2 style="font-size:200%; color:#008080; font-family:Georgia"> 주간 부동산 시계열 분석 <br>
<hr style= "  display: block;
  margin-top: 0.5em;
  margin-bottom: 0.5em;
  margin-left: auto;
  margin-right: auto;
  border-style: inset;
  border-width: 1.5px;"></h1>
"""

st.set_page_config(page_title="Weekly House Analysis Dashboard", page_icon="", layout="wide")
st.markdown('<style>body{background-color: #fbfff0}</style>',unsafe_allow_html=True)
st.markdown(html_header, unsafe_allow_html=True)
st.markdown(""" <style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style> """, unsafe_allow_html=True)

marker_colors = ['rgb(27,38,81)', 'rgb(205,32,40)', 'rgb(22,108,150)', 'rgb(255,0,255)', 'rgb(153,204,0)', \
                       'rgb(153,51,102)', 'rgb(0,255,0)','rgb(255,69,0)', 'rgb(0,0,255)', 'rgb(255,204,0)', \
                        'rgb(255,153,204)', 'rgb(0,255,255)', 'rgb(128,0,0)', 'rgb(0,128,0)', 'rgb(0,0,128)', \
                         'rgb(128,128,0)', 'rgb(128,0,128)', 'rgb(0,128,128)', 'rgb(192,192,192)', 'rgb(153,153,255)', \
                             'rgb(255,255,0)', 'rgb(255,255,204)', 'rgb(102,0,102)', 'rgb(255,128,128)', 'rgb(0,102,204)',\
                                 'rgb(255,102,0)', 'rgb(51,51,51)', 'rgb(51,153,102)', 'rgb(51,153,102', 'rgb(204,153,255)']
template = 'ggplot2' #"plotly", "plotly_white", "plotly_dark", "ggplot2", "seaborn", "simple_white", "none".
pio.templates["myID"] = go.layout.Template(
    layout_annotations=[
        dict(
            name="draft watermark",
            text="graph by 기하급수적",
            textangle=0,
            opacity=0.2,
            font=dict(color="black", size=20),
            xref="paper",
            yref="paper",
            x=0.9,
            y=-0.2,
            showarrow=False,
        )
    ]
)
#오늘날짜까지
now = datetime.now()
today = '%s-%s-%s' % ( now.year, now.month, now.day)

# file_path = 'G:/내 드라이브/code/data/WeeklySeriesTables(시계열)_20210419.xlsx'
# kb_file_path = r'https://github.com/sizipusx/fundamental/blob/87cf11504a146569ebd05d8cef780246ea7323a4/files/kb_weekly.xlsx?raw=True'
# #감정원 데이터
# one_path = r"https://github.com/sizipusx/fundamental/blob/87cf11504a146569ebd05d8cef780246ea7323a4/files/one_weekly.xlsx?raw=True"
# #헤더 변경
# header_path = r'https://github.com/sizipusx/fundamental/blob/901a00722f00376400db00e75cf4e5521043be88/files/header.xlsx?raw=True'
# header_excel = pd.ExcelFile(header_path)
#geojson file open
geo_source = r'https://raw.githubusercontent.com/sizipusx/fundamental/main/sigungu_json.geojson'
#gsheet
gsheet_url = r'https://raw.githubusercontent.com/sizipusx/fundamental/a55cf1853a1fc24ff338e7293a0d526fc0520e76/files/weekly-house-db-ac0a43b61ddd.json'

scope = [
    'https://spreadsheets.google.com/feeds',
    'https://www.googleapis.com/auth/drive',
    ]

json_file_name = './files/weekly-house-db-ac0a43b61ddd.json'

credentials = ServiceAccountCredentials.from_json_keyfile_name(json_file_name, scope)
gc = gspread.authorize(credentials)

spreadsheet_url = 'https://docs.google.com/spreadsheets/d/1cr50NkztlYeTCMkmqkeq16Va-99yT3Hs-Rbl2TGOp1U/edit#gid=0'

doc = gc.open_by_url(spreadsheet_url)

@st.cache(ttl=6000)
def get_gsheet_index():
    m_d = doc.worksheet('mae')
    j_d = doc.worksheet('jeon')
    basic_city = doc.worksheet('city')
    kb_m = doc.worksheet('kbm')
    kb_j = doc.worksheet('kbj')

    #데이터 프레임으로 읽기
    basic_values = basic_city.get_all_values()
    m_values = m_d.get_all_values()
    j_values = j_d.get_all_values()
    kbm_values = kb_m.get_all_values()
    kbj_values = kb_j.get_all_values()

    basic_header, basic_rows = basic_values[0], basic_values[1:]
    m_header, m_rows = m_values[1], m_values[2:]
    j_header, j_rows = j_values[1], j_values[2:]
    kbm_header, kbm_rows = kbm_values[1], kbm_values[2:]
    kbj_header, kbj_rows = kbj_values[1], kbj_values[2:]

    basic_df= pd.DataFrame(basic_rows, columns=basic_header)
    omdf = pd.DataFrame(m_rows, columns=m_header)
    ojdf = pd.DataFrame(j_rows, columns=j_header)
    mdf = pd.DataFrame(kbm_rows, columns=kbm_header)
    jdf = pd.DataFrame(kbj_rows, columns=kbj_header)

    #데이터타입 변경
    basic_df = basic_df[basic_df['x'] != '#N/A' ]
    basic_df['총인구수'] = basic_df['총인구수'].apply(lambda x: x.replace(',','').replace('-','0')).astype(int)
    basic_df['세대수'] = basic_df['세대수'].apply(lambda x: x.replace(',','').replace('-','0')).astype(int)
    basic_df['면적'] = basic_df['면적'].apply(lambda x: x.replace(',','').replace('#N/A','0')).astype(float)
    basic_df['x'] = basic_df['x'].astype(int)
    basic_df['y'] = basic_df['y'].astype(int)
    #kb
    mdf = mdf.set_index(keys='날짜')
    mdf.index = pd.to_datetime(mdf.index)
    mdf = mdf.apply(lambda x:x.replace('','0').replace('#DIV/0!','0'))
    jdf = jdf.set_index(keys='날짜')
    jdf.index = pd.to_datetime(jdf.index)
    jdf = jdf.apply(lambda x:x.replace('','0').replace('#DIV/0!','0'))
    mdf = mdf.astype(float)
    jdf = jdf.astype(float)
    #부동산원
    omdf = omdf.set_index(keys='날짜')
    omdf.index = pd.to_datetime(omdf.index)
    ojdf = ojdf.set_index(keys='날짜')
    ojdf.index = pd.to_datetime(ojdf.index)
    omdf = omdf.apply(lambda x:x.replace('','0').replace('#DIV/0!','0'))
    ojdf = ojdf.apply(lambda x:x.replace('','0').replace('#DIV/0!','0'))
    omdf = omdf.astype(float)
    ojdf = ojdf.astype(float)

    return mdf, jdf, omdf, ojdf, basic_df

#agg table
def aggrid_interactive_table(df: pd.DataFrame):
    """Creates an st-aggrid interactive table based on a dataframe.

    Args:
        df (pd.DataFrame]): Source dataframe

    Returns:
        dict: The selected row
    """
    df = df.reset_index()
    #gb = GridOptionsBuilder.from_dataframe(df)
    
    gb = GridOptionsBuilder.from_dataframe(
        df, enableRowGroup=True, enableValue=True, enablePivot=True
    )
    gb.configure_pagination()
    gb.configure_side_bar()
    gb.configure_selection("single")
    response  = AgGrid(
        df,
        editable=True,
        enable_enterprise_modules=True,
        gridOptions=gb.build(),
        data_return_mode="filtered_and_sorted",
        width='100%',
        update_mode="no_update",
        fit_columns_on_grid_load=False, #GridUpdateMode.MODEL_CHANGED,
        theme="streamlit",
        allow_unsafe_jscode=True
    )

    return response

# @st.cache
# def get_basic_df():
#     #2021-7-30 코드 추가
#     # header 파일
#     basic_df = header_excel.parse('city')
#     #basic_df['총인구수'] = basic_df['총인구수'].apply(lambda x: x.replace(',','')).astype(float)
#     #basic_df['세대수'] = basic_df['세대수'].apply(lambda x: x.replace(',','')).astype(float)
#     basic_df.dropna(inplace=True)
#     basic_df['밀도'] = basic_df['총인구수']/basic_df['면적']

#     return basic_df

# @st.cache(allow_output_mutation=True)
# def load_one_data():
#     #22년 5월 9일 구글시트에서 읽어오는 것으로 변경


#     #감정원 주간 데이터
#     one_dict = pd.read_excel(one_path, sheet_name=None, header=1, index_col=0, parse_dates=True)
#     # one header 변경
#     oneh = header_excel.parse('one')
#     omdf = one_dict['매매지수']
#     ojdf = one_dict['전세지수']
#     omdf = omdf.iloc[3:omdf['전국'].count()+1,:]
#     ojdf = ojdf.iloc[3:ojdf['전국'].count()+1,:]
#     omdf.columns = oneh.columns
#     ojdf.columns = oneh.columns
#     omdf = omdf.astype(float).round(decimals=2)
#     ojdf = ojdf.astype(float).round(decimals=2)
#      #주간 증감률
#     omdf_change = omdf.pct_change()*100
#     omdf_change = omdf_change.iloc[1:]
#     omdf_change.replace([np.inf, -np.inf], np.nan, inplace=True)
#     omdf_change = omdf_change.astype(float).fillna(0)
#     ojdf_change = ojdf.pct_change()*100
#     ojdf_change = ojdf_change.iloc[1:]
#     ojdf_change.replace([np.inf, -np.inf], np.nan, inplace=True)
#     ojdf_change = ojdf_change.astype(float).fillna(0)
#     omdf_change = omdf_change.round(decimals=3)
#     ojdf_change = ojdf_change.round(decimals=3)
#     cum_omdf = (1+omdf_change/100).cumprod() -1
#     cum_omdf = cum_omdf.round(decimals=3)
#     cum_ojdf = (1+ojdf_change/100).cumprod() -1
#     cum_ojdf = cum_ojdf.round(decimals=3)
#     #일주일 간 매매지수 상승률 순위
#     last_odf = pd.DataFrame()
#     last_odf['매매증감'] = omdf_change.iloc[-1].T.to_frame()
#     last_odf['전세증감'] = ojdf_change.iloc[-1].T.to_frame()
#     last_odf['1w'] = omdf_change.iloc[-1].T.to_frame()
#     last_odf['2w'] = omdf_change.iloc[-2].T.to_frame()
#     last_odf['3w'] = omdf_change.iloc[-3].T.to_frame()
#     last_odf['1m'] = omdf_change.iloc[-4].T.to_frame()
#     last_odf['1y'] = omdf_change.iloc[-51].T.to_frame()
#     last_odf = last_odf.astype(float).fillna(0).round(decimals=3)
#     #일주일 간 전세지수 상승률 순위
#     last_ojdf = pd.DataFrame()
#     last_ojdf['1w'] = ojdf_change.iloc[-1].T.to_frame()
#     last_ojdf['2w'] = ojdf_change.iloc[-2].T.to_frame()
#     last_ojdf['3w'] = ojdf_change.iloc[-3].T.to_frame()
#     last_ojdf['1m'] = ojdf_change.iloc[-4].T.to_frame()
#     last_ojdf['1y'] = ojdf_change.iloc[-51].T.to_frame()
#     last_ojdf = last_ojdf.astype(float).fillna(0).round(decimals=3)
#     basic_df = get_basic_df()
#     odf = pd.merge(last_odf, basic_df, how='inner', left_index=True, right_on='short')

#     with urlopen(geo_source) as response:
#         one_geo_data = json.load(response)
    
#     #geojson file 변경
#     for idx, sigun_dict in enumerate(one_geo_data['features']):
#         sigun_id = sigun_dict['properties']['SIG_CD']
#         sigun_name = sigun_dict['properties']['SIG_KOR_NM']
#         try:
#             sell_change = odf.loc[(odf.code == sigun_id), '매매증감'].iloc[0]
#             jeon_change = odf.loc[(odf.code == sigun_id), '전세증감'].iloc[0]
#         except:
#             sell_change = 0
#             jeon_change =0
#         # continue
        
#         txt = f'<b><h4>{sigun_name}</h4></b>매매증감: {sell_change:.2f}<br>전세증감: {jeon_change:.2f}'
#         # print(txt)
        
#         one_geo_data['features'][idx]['id'] = sigun_id
#         one_geo_data['features'][idx]['properties']['sell_change'] = sell_change
#         one_geo_data['features'][idx]['properties']['jeon_change'] = jeon_change
#         one_geo_data['features'][idx]['properties']['tooltip'] = txt
   
#     return odf, one_geo_data, last_odf, last_ojdf, omdf, ojdf, omdf_change, ojdf_change, cum_omdf, cum_ojdf

# @st.cache(allow_output_mutation=True)
# def load_index_data():
#     kb_dict = pd.ExcelFile(kb_file_path)
#     mdf =  kb_dict.parse("매매지수", skiprows=1, parse_dates=False, dtype={'구분': str})
#     jdf =  kb_dict.parse("전세지수", skiprows=1, parse_dates=False, dtype={'구분': str})
    
#     header = header_excel.parse('KB')
#     # code_df = header_excel.parse('code', index_col=1)
#     # code_df.index = code_df.index.str.strip()
#     basic_df = get_basic_df()
#     mdf = mdf.iloc[1:]
#     mdf['구분'].str.slice(start=0, stop=10)
#     mdf.index = pd.to_datetime(mdf['구분'], format='%Y-%m-%d')
#     mdf = mdf.iloc[:,1:]
#     mdf.columns = header.columns
#     mdf = mdf.round(decimals=2)
#     jdf = jdf.iloc[1:]
#     jdf['구분'].str.slice(start=0, stop=10)
#     jdf.index = pd.to_datetime(jdf['구분'], format='%Y-%m-%d')
#     jdf = jdf.iloc[:,1:]
#     jdf.columns = header.columns
#     jdf = jdf.round(decimals=2)
#     #======== 여기 변경 ==============
#     #주간 증감률
#     mdf_change = mdf.pct_change()*100
#     mdf_change = mdf_change.iloc[1:]
#     mdf_change.replace([np.inf, -np.inf], np.nan, inplace=True)
#     mdf_change = mdf_change.astype(float).fillna(0)
#     jdf_change = jdf.pct_change()*100
#     jdf_change = jdf_change.iloc[1:]
#     jdf_change.replace([np.inf, -np.inf], np.nan, inplace=True)
#     jdf_change = jdf_change.astype(float).fillna(0)
#     cum_mdf = (1+mdf_change/100).cumprod() -1
#     cum_mdf = cum_mdf.round(decimals=3)
#     cum_jdf = (1+jdf_change/100).cumprod() -1
#     cum_jdf = cum_jdf.round(decimals=3)
#     #일주일 간 매매지수 상승률 순위
#     kb_last_df  = pd.DataFrame()
#     kb_last_df['매매증감'] = mdf_change.iloc[-1].T.to_frame()
#     kb_last_df['전세증감'] = jdf_change.iloc[-1].T.to_frame()
#     kb_last_df['1w'] = mdf_change.iloc[-1].T.to_frame() 
#     kb_last_df['2w'] = mdf_change.iloc[-2].T.to_frame()
#     kb_last_df['3w'] = mdf_change.iloc[-3].T.to_frame()
#     kb_last_df['1m'] = mdf_change.iloc[-4].T.to_frame()
#     kb_last_df['1y'] = mdf_change.iloc[-51].T.to_frame()
#     kb_last_df = kb_last_df.astype(float).fillna(0).round(decimals=2)
#     #일주일 간 전세지수 상승률 순위
#     kb_last_jdf  = pd.DataFrame()
#     kb_last_jdf['1w'] = jdf_change.iloc[-1].T.to_frame() 
#     kb_last_jdf['2w'] = jdf_change.iloc[-2].T.to_frame()
#     kb_last_jdf['3w'] = jdf_change.iloc[-3].T.to_frame()
#     kb_last_jdf['1m'] = jdf_change.iloc[-4].T.to_frame()
#     kb_last_jdf['1y'] = jdf_change.iloc[-51].T.to_frame()
#     kb_last_jdf = kb_last_jdf.astype(float).fillna(0).round(decimals=2)


#     #마지막달 dataframe에 지역 코드 넣어 합치기
#     # df = pd.merge(last_df, code_df, how='inner', left_index=True, right_index=True)
#     kb_df = pd.merge(kb_last_df, basic_df, how='inner', left_index=True, right_on='short')
#     #st.dataframe(kb_df)
    
#     # df.columns = ['매매증감', '전세증감', 'SIG_CD']
#     # df['SIG_CD']= df['SIG_CD'].astype(str)

#     #버블 지수 만들어 보자
#     #아기곰 방식:버블지수 =(관심지역매매가상승률-전국매매가상승률) - (관심지역전세가상승률-전국전세가상승률)
#     bubble_df = mdf_change.subtract(mdf_change['전국'], axis=0)- jdf_change.subtract(jdf_change['전국'], axis=0)
#     bubble_df = bubble_df*100
#     bubble_df2 = mdf_change.subtract(mdf_change['전국'], axis=0)/jdf_change.subtract(jdf_change['전국'], axis=0)
#     bubble_df2 = bubble_df2
    
#     #곰곰이 방식: 버블지수 = 매매가비율(관심지역매매가/전국평균매매가) - 전세가비율(관심지역전세가/전국평균전세가)
#     bubble_df3 = mdf.div(mdf['전국'], axis=0) - jdf.div(jdf['전국'], axis=0)
#     bubble_df3 = bubble_df3.astype(float).fillna(0).round(decimals=5)*100
#     # st.dataframe(bubble_df3)

#     #전세 파워 만들기
#     cum_ch = (mdf_change/100 +1).cumprod()
#     jcum_ch = (jdf_change/100 +1).cumprod()
#     m_power = (jcum_ch - cum_ch)*100
#     m_power = m_power.astype(float).fillna(0).round(decimals=2)

#     #마지막 데이터만 
#     power_df = m_power.iloc[-1].T.to_frame()
#     power_df['버블지수'] = bubble_df3.iloc[-1].T.to_frame()
#     power_df.columns = ['전세파워', '버블지수']
#     # power_df.dropna(inplace=True)
#     power_df = power_df.astype(float).fillna(0).round(decimals=2)
#     power_df['jrank'] = power_df['전세파워'].rank(ascending=False, method='min').round(1)
#     power_df['brank'] = power_df['버블지수'].rank(ascending=True, method='min').round(decimals=1)
#     power_df['score'] = power_df['jrank'] + power_df['brank']
#     power_df['rank'] = power_df['score'].rank(ascending=True, method='min')
#     power_df = power_df.sort_values('rank', ascending=True)

#     with urlopen(geo_source) as response:
#         kb_geo_data = json.load(response)
    
#     #geojson file 변경
#     for idx, sigun_dict in enumerate(kb_geo_data['features']):
#         sigun_id = sigun_dict['properties']['SIG_CD']
#         sigun_name = sigun_dict['properties']['SIG_KOR_NM']
#         try:
#             sell_change = kb_df.loc[(kb_df.code == sigun_id), '매매증감'].iloc[0]
#             jeon_change = kb_df.loc[(kb_df.code == sigun_id), '전세증감'].iloc[0]
#         except:
#             sell_change = 0
#             jeon_change =0
#         # continue
        
#         txt = f'<b><h4>{sigun_name}</h4></b>매매증감: {sell_change:.2f}<br>전세증감: {jeon_change:.2f}'
#         # print(txt)
        
#         kb_geo_data['features'][idx]['id'] = sigun_id
#         kb_geo_data['features'][idx]['properties']['sell_change'] = sell_change
#         kb_geo_data['features'][idx]['properties']['jeon_change'] = jeon_change
#         kb_geo_data['features'][idx]['properties']['tooltip'] = txt
   
#     return kb_df, kb_geo_data, kb_last_df, kb_last_jdf, mdf, jdf, mdf_change, jdf_change, m_power, bubble_df3, cum_mdf, cum_jdf

@st.cache(ttl=6000)
def load_senti_data():
    #구글시트에서 불러오기 2022-05-09
    kbs_doc= doc.worksheet('kbs')
    ones_doc = doc.worksheet('os')
    kbmtr_doc = doc.worksheet('kbmtr')
    kbjtr_doc = doc.worksheet('kbjtr')
    kbjs_doc = doc.worksheet('kbjs')

    #데이터 프레임으로 읽기
    kbs_doc_values = kbs_doc.get_all_values()
    ones_doc_values = ones_doc.get_all_values()
    kbmtr_doc_values = kbmtr_doc.get_all_values()
    kbjtr_doc_values = kbjtr_doc.get_all_values()
    kbjs_doc_values = kbjs_doc.get_all_values()

    kbs_header, kbs_rows = kbs_doc_values[1], kbs_doc_values[2:]
    ones_header, ones_rows = ones_doc_values[1], ones_doc_values[2:]
    kbmtr_header, kbmtr_rows = kbmtr_doc_values[1], kbmtr_doc_values[2:]
    kbjtr_header, kbjtr_rows = kbjtr_doc_values[1], kbjtr_doc_values[2:]
    kbjs_header, kbjs_rows = kbjs_doc_values[1], kbjs_doc_values[2:]

    kbs_df = pd.DataFrame(kbs_rows, columns=kbs_header)
    ones_df = pd.DataFrame(ones_rows, columns=ones_header)
    kbmtr_df = pd.DataFrame(kbmtr_rows, columns=kbmtr_header)
    kbjtr_df = pd.DataFrame(kbjtr_rows, columns=kbjtr_header)
    kbjs_df = pd.DataFrame(kbjs_rows, columns=kbjs_header)
    #kb 매수우위지수
    kbs_df = kbs_df.set_index(keys=kbs_df.iloc[:,0])
    kbs_df.index = pd.to_datetime(kbs_df.index)
    kbs_df.index.name="날짜"
    kbs_df = kbs_df.iloc[:,1:]

    kbjs_df = kbjs_df.set_index(keys=kbjs_df.iloc[:,0])
    kbjs_df.index = pd.to_datetime(kbjs_df.index)
    kbjs_df.index.name="날짜"
    kbjs_df = kbjs_df.iloc[:,1:]
    #컬럼명 바꿈
    j1 = kbs_df.columns.map(lambda x: x.split(' ')[0])

    new_s1 = []
    for num, gu_data in enumerate(j1):
        check = num
        if gu_data == '':
            new_s1.append(new_s1[check-1])
        else:
            new_s1.append(j1[check])

    #컬럼 설정
    kbs_df.columns = [new_s1,kbs_df.iloc[0]]
    kbjs_df.columns = [new_s1,kbjs_df.iloc[0]]
    kbs_df = kbs_df.iloc[1:]
    kbjs_df = kbjs_df.iloc[1:]
    kbs_df = kbs_df.apply(lambda x:x.replace('','0'))
    kbs_df = kbs_df.astype(float).round(decimals=2)
    kbjs_df = kbjs_df.apply(lambda x:x.replace('','0'))
    kbjs_df = kbjs_df.astype(float).round(decimals=2)
    #가장 최근 것만
    s_df = kbs_df.xs(key='매수우위지수', axis=1, level=1)
    js_df = kbjs_df.xs(key='전세수급지수', axis=1, level=1)
    s_df = s_df.apply(lambda x:x.replace('','0'))
    s_df = s_df.astype(float).round(decimals=2)
    js_df = js_df.apply(lambda x:x.replace('','0'))
    js_df = js_df.astype(float).round(decimals=2)
    #=============기존
    # kb_dict = pd.read_excel(kb_file_path, sheet_name=None, header=1)

    # js = kb_dict['전세수급']
    # ms = kb_dict['매수매도']

    # js = js.set_index("Unnamed: 0")
    # ms = ms.set_index("Unnamed: 0")
    # js.index.name="날짜"
    # ms.index.name="날짜"

    # #컬럼명 바꿈
    # j1 = js.columns.map(lambda x: x.split(' ')[0])

    # new_s1 = []
    # for num, gu_data in enumerate(j1):
    #     check = num
    #     if gu_data.startswith('Un'):
    #         new_s1.append(new_s1[check-1])
    #     else:
    #         new_s1.append(j1[check])

    # #컬럼 설정
    # js.columns = [new_s1,js.iloc[0]]
    # ms.columns = [new_s1,ms.iloc[0]]
    # js = js.iloc[2:js[('전국', '전세수급지수')].count()]
    # ms = ms.iloc[2:ms[('전국', '매수우위지수')].count()]
    # js = js.astype(float).fillna(0).round(decimals=2)
    # ms = ms.astype(float).fillna(0).round(decimals=2)

    # js_index = js.xs("전세수급지수", axis=1, level=1)
    # ms_index = ms.xs("매수우위지수", axis=1, level=1)
    index_df = pd.DataFrame()
    index_df['매수우위지수'] = s_df.iloc[-1]
    index_df['전세수급지수'] = js_df.iloc[-1]

    return kbs_df, kbjs_df, index_df, s_df, js_df


def run_price_index() :
    #같이 그려보자
    gu_city = ['부산', '대구', '인천', '광주', '대전', '울산', '수원', '성남', '안양', '용인', '고양', '안산', \
                 '천안', '청주', '전주', '포항', '창원']
    gu_city_series = pd.Series(gu_city)
    draw_list = []
    if selected_dosi in gu_city:
        draw_list = city_series[city_series.str.contains(selected_dosi)].to_list()
        # draw_list = [selected_dosi]
    elif selected_dosi == '전국':
        draw_list = ['전국', '수도권', '지방']
    elif selected_dosi == '서울':
        draw_list = ['서울 강북권역', '서울 강남권역']
    elif selected_dosi == '수도권':
        draw_list = ['서울', '경기', '인천']
    elif selected_dosi == '6대광역시':
        draw_list = ['부산', '대구', '광주', '대전', '울산', '인천']
    elif selected_dosi == '5대광역시':
        draw_list = ['부산', '대구', '광주', '대전', '울산']
    elif selected_dosi == '경기':
        #draw_list = ['경기', '수원', '성남','고양', '안양', '부천', '의정부', '광명', '평택','안산', '과천', '구리', '남양주', \
        #     '용인', '시흥', '군포', '의왕','하남','오산','파주','이천','안성','김포', '양주','동두천','경기 광주', '화성']
        draw_list = ['경기', '경기 경부1권', '경기 경부2권', '경기 서해안권', '경기 동부1권', '경기 동부2권', '경기 경의권', '경기 경원권']
    elif selected_dosi == '지방':
        draw_list = ['강원', '충북', '충남', '전북', '전남', '경북', '경남', '제주도']
    elif selected_dosi == '강원':
        draw_list = ['강원', '춘천','강릉', '원주']
    elif selected_dosi == '충북':
        draw_list = ['충북','청주', '충주','제천']
    elif selected_dosi == '충남':
        draw_list = ['충남','천안', '공주','아산', '논산', '계룡','당진','서산']
    elif selected_dosi == '전북':
        draw_list = ['전북', '전주', '익산', '군산']
    elif selected_dosi == '전남':
        draw_list = ['전남', '목포','순천','여수','광양']
    elif selected_dosi == '경북':
        draw_list = ['경북','포항','구미', '경산', '안동','김천']
    elif selected_dosi == '충북':
        draw_list = ['경남','창원', '양산','거제','진주', '김해','통영']
    elif selected_dosi == '제주도':
        draw_list = ['제주, 서귀포']
    
    ### Block 매매전세지수 같이 보기 #########################################################################################
    with st.container():
        col1, col2, col3 = st.columns([30,2,30])
        with col1:
            drawAPT_weekly.run_price_index_all(draw_list, mdf, jdf, mdf_change, jdf_change, gu_city, selected_dosi3, city_series)
        with col2:
            st.write("")
        with col3:
            drawAPT_weekly.run_one_index_all(draw_list, omdf, ojdf, omdf_change, ojdf_change, gu_city, selected_dosi3, city_series)
    html_br="""
    <br>
    """
    st.markdown(html_br, unsafe_allow_html=True)
    ### Block 매매 전세 지수 #########################################################################################
    with st.container():
        col1, col2, col3 = st.columns([30,2,30])
        with col1:
            drawAPT_weekly.run_price_index(selected_dosi2, selected_dosi3, mdf, jdf, mdf_change, jdf_change)
        with col2:
            st.write("")
        with col3:
            drawAPT_weekly.run_one_index(selected_dosi2, selected_dosi3, omdf, ojdf, omdf_change, ojdf_change)
    html_br="""
    <br>
    """
    st.markdown(html_br, unsafe_allow_html=True)
    ### Block 플라워차트 추가 2021. 12. 26 #########################################################################################
    with st.container():
        col1, col2, col3 = st.columns([30,2,30])
        with col1:
            flag = "KB"
            drawAPT_weekly.draw_flower(selected_dosi2, selected_dosi3, cummdf, cumjdf, flag)
        with col2:
            st.write("")
        with col3:
            flag = "부동산원"
            drawAPT_weekly.draw_flower(selected_dosi2, selected_dosi3, cumomdf, cumojdf, flag)
    html_br="""
    <br>
    """
    st.markdown(html_br, unsafe_allow_html=True)

def run_sentimental_index(mdf_change, jdf_change):
    ### Block 매수우위지수#########################################################################################
    with st.container():
        col1, col2, col3 = st.columns([30,2,30])
        with col1:
            drawAPT_weekly.draw_sentiment(selected_dosi, ms_1, ms_2, ms_index)
        with col2:
            st.write("")
        with col3:
            drawAPT_weekly.draw_sentiment_change(selected_dosi, mdf_change, ms_index)
    html_br="""
    <br>
    """
    st.markdown(html_br, unsafe_allow_html=True)
    ### Block 전세수급지수#########################################################################################
    with st.container():
        col1, col2, col3 = st.columns([30,2,30])
        with col1:
            drawAPT_weekly.draw_jeon_sentiment(selected_dosi, js_1, js_2, js_index)
        with col2:
            st.write("")
        with col3:
            drawAPT_weekly.draw_jeon_sentiment_change(selected_dosi, jdf_change, js_index)
    html_br="""
    <br>
    """
    st.markdown(html_br, unsafe_allow_html=True)


def draw_basic():
    # kb_df, k_geo_data, last_df, kb_mdf = load_index_data()
    # one_df, o_geo_data, one_last_odf = load_one_data()
    ### Block 0#########################################################################################
    with st.container():
        col1, col2, col3 = st.columns([30,2,30])
        with col1:
            flag = ['KB','매매증감']
            drawAPT_weekly.draw_Choroplethmapbox(kb_df, kb_geo_data, flag)
        with col2:
            st.write("")
        with col3:
            flag = ['KB','전세증감']
            drawAPT_weekly.draw_Choroplethmapbox(kb_df, kb_geo_data, flag)
    html_br="""
    <br>
    """
    st.markdown(html_br, unsafe_allow_html=True)
    ### Draw 전국 지도 chart #########################################################################################
    with st.container():
        col1, col2, col3 = st.columns([30,2,30])
        with col1:
            flag = ['부동산원','매매증감']
            drawAPT_weekly.draw_Choroplethmapbox(odf, one_geo_data, flag)
        with col2:
            st.write("")
        with col3:
            flag = ['부동산원','전세증감']
            drawAPT_weekly.draw_Choroplethmapbox(odf, one_geo_data, flag)
    html_br="""
    <br>
    """
    st.markdown(html_br, unsafe_allow_html=True)
    ### Draw 매매증감 bar chart #########################################################################################
    with st.container():
        col1, col2, col3 = st.columns([30,2,30])
        with col1:
            flag = ['KB','매매증감']
            drawAPT_weekly.draw_index_change_with_bar(kb_last_df, flag)
        with col2:
            st.write("")
        with col3:
            flag = ['부동산원','매매증감']
            drawAPT_weekly.draw_index_change_with_bar(last_odf, flag)        
    html_br="""
    <br>
    """
    st.markdown(html_br, unsafe_allow_html=True)
     ### Draw 전세증감 bar chart #########################################################################################
    with st.container():
        col1, col2, col3 = st.columns([30,2,30])
        with col1:
            flag = ['KB','전세증감']
            drawAPT_weekly.draw_index_change_with_bar(kb_last_df, flag)
        with col2:
            st.write("")
        with col3:
            flag = ['부동산원','전세증감']
            drawAPT_weekly.draw_index_change_with_bar(last_odf, flag)        
    html_br="""
    <br>
    """
    st.markdown(html_br, unsafe_allow_html=True)
    ### Draw Bubble chart #########################################################################################
    with st.container():
        col1, col2, col3 = st.columns([30,2,30])
        with col1:
            flag = 'KB'
            drawAPT_weekly.draw_index_change_with_bubble(kb_last_df, flag)

        with col2:
            st.write("")
        with col3:
            flag = '부동산원'
            drawAPT_weekly.draw_index_change_with_bubble(last_odf, flag)
            
    html_br="""
    <br>
    """
    st.markdown(html_br, unsafe_allow_html=True)
    ### draw 매매지수 Table ######################################################################################
    with st.container():
        col1, col2, col3 = st.columns([30,2,30])
        with col1:
            flag = ['KB','매매증감']
            #kb_last_df = kb_last_df.set_index("index")
            #kb_last_df = round(kb_last_df,2)
            rank_df = pd.DataFrame()
            rank_df['1w'] = kb_last_df['1w'].rank(ascending=True, method='min').round(decimals=1)
            rank_df['2w'] = kb_last_df['2w'].rank(ascending=True, method='min').round(decimals=1)
            rank_df['3w'] = kb_last_df['3w'].rank(ascending=True, method='min').round(decimals=1)
            rank_df['1m'] = kb_last_df['1m'].rank(ascending=True, method='min').round(decimals=1)
            rank_df['1y'] = kb_last_df['1y'].rank(ascending=True, method='min').round(decimals=1)
            rank_df['1w%'] = kb_last_df['1w'].round(decimals=2)
            rank_df['2w%'] = kb_last_df['2w'].round(decimals=2)
            rank_df['3w%'] = kb_last_df['3w'].round(decimals=2)
            rank_df['1m%'] = kb_last_df['1m'].round(decimals=2)
            rank_df['1y%'] = kb_last_df['1y'].round(decimals=2)
            kb_last_df['매매증감'] = round(kb_last_df['매매증감'], 2)
            kb_last_df['전세증감'] = kb_last_df['전세증감'].round(decimals=2)
            
            slice_1 = ['1w%', '2w%', '3w%', '1m%', '1y%' ]
            slice_2 = ['1w', '2w', '3w', '1m', '1y' ]
            ## 칼럼 헤더 셀 배경색 바꾸기
            column = '1w' ## 원하는 칼럼이름
            col_loc = rank_df.columns.get_loc(column) ## 원하는 칼럼의 인덱스
            st.markdown("KB 186개 지역 _매매지수_ 변화율 기간별 순위")
            rank_df = rank_df.reset_index()
            #add aggrid table
            #response  = aggrid_interactive_table(df=rank_df)
            st.dataframe(rank_df.style.background_gradient(cmap, axis=0, subset=slice_1)\
                .format(precision=2, na_rep='MISSING', thousands=" ", subset=slice_1)\
                .format(precision=0, na_rep='MISSING', thousands=" ", subset=slice_2)\
                .set_table_styles(
                        [{'selector': f'th.col_heading.level0.col{col_loc}',
                        'props': [('background-color', '#67c5a4')]},
                        ])\
                .bar(subset=slice_2, align='mid',color=['blue','red']), 800, 800)
        with col2:
            st.write("")
        with col3:
            flag = ['KB','전세증감']
            #kb_last_df = kb_last_df.set_index("index")
            #kb_last_df = round(kb_last_df,2)
            rank_jdf = pd.DataFrame()
            rank_jdf['1w'] = kb_last_jdf['1w'].rank(ascending=True, method='min').round(decimals=1)
            rank_jdf['2w'] = kb_last_jdf['2w'].rank(ascending=True, method='min').round(decimals=1)
            rank_jdf['3w'] = kb_last_jdf['3w'].rank(ascending=True, method='min').round(decimals=1)
            rank_jdf['1m'] = kb_last_jdf['1m'].rank(ascending=True, method='min').round(decimals=1)
            rank_jdf['1y'] = kb_last_jdf['1y'].rank(ascending=True, method='min').round(decimals=1)
            rank_jdf['1w%'] = kb_last_jdf['1w'].round(decimals=2)
            rank_jdf['2w%'] = kb_last_jdf['2w'].round(decimals=2)
            rank_jdf['3w%'] = kb_last_jdf['3w'].round(decimals=2)
            rank_jdf['1m%'] = kb_last_jdf['1m'].round(decimals=2)
            rank_jdf['1y%'] = kb_last_jdf['1y'].round(decimals=2)
            
            slice_1 = ['1w%', '2w%', '3w%', '1m%', '1y%' ]
            slice_2 = ['1w', '2w', '3w', '1m', '1y' ]
            ## 칼럼 헤더 셀 배경색 바꾸기
            column = '1w' ## 원하는 칼럼이름
            col_loc = rank_jdf.columns.get_loc(column) ## 원하는 칼럼의 인덱스
            st.markdown("KB 186개 지역 _전세지수_ 기간별 순위")
            rank_jdf = rank_jdf.reset_index()
            #response  = aggrid_interactive_table(df=rank_jdf)

            st.dataframe(rank_jdf.style.background_gradient(cmap, axis=0, subset=slice_1)\
                .format(precision=2, na_rep='MISSING', thousands=" ", subset=slice_1)\
                .format(precision=0, na_rep='MISSING', thousands=" ", subset=slice_2)\
                .set_table_styles(
                        [{'selector': f'th.col_heading.level0.col{col_loc}',
                        'props': [('background-color', '#67c5a4')]},
                        ])\
                .bar(subset=slice_2, align='mid',color=['blue','red']), 800, 800)            
    html_br="""
    <br>
    """
    st.markdown(html_br, unsafe_allow_html=True)
    ### draw 전세지수 Table ######################################################################################
    with st.container():
        col1, col2, col3 = st.columns([30,2,30])
        with col1:
            flag = ['부동산원','매매증감']
            rank_odf = pd.DataFrame()
            rank_odf['1w'] = last_odf['1w'].rank(ascending=True, method='min').round(decimals=1)
            rank_odf['2w'] = last_odf['2w'].rank(ascending=True, method='min').round(decimals=1)
            rank_odf['3w'] = last_odf['3w'].rank(ascending=True, method='min').round(decimals=1)
            rank_odf['1m'] = last_odf['1m'].rank(ascending=True, method='min').round(decimals=1)
            rank_odf['1y'] = last_odf['1y'].rank(ascending=True, method='min').round(decimals=1)
            rank_odf['1w%'] = last_odf['1w'].round(decimals=2)
            rank_odf['2w%'] = last_odf['2w'].round(decimals=2)
            rank_odf['3w%'] = last_odf['3w'].round(decimals=2)
            rank_odf['1m%'] = last_odf['1m'].round(decimals=2)
            rank_odf['1y%'] = last_odf['1y'].round(decimals=2)
            slice_1 = ['1w%', '2w%', '3w%', '1m%', '1y%' ]
            slice_2 = ['1w', '2w', '3w', '1m', '1y' ]
            st.markdown("부동산원 235개 지역 _매매지수_ 변화율 기간별 순위")
            rank_odf = rank_odf.reset_index()
            st.dataframe(rank_odf.style.background_gradient(cmap, axis=0, subset=slice_1)\
                .format(precision=2, na_rep='MISSING', thousands=",", subset=slice_1)\
                .format(precision=0, na_rep='MISSING', thousands=",", subset=slice_2)\
                #.set_properties(subset=[rank_odf.index], **{'width': '100px'})\
                .set_table_styles(
                        [{'selector': f'th.col_heading.level0.col{col_loc}',
                        'props': [('background-color', '#67c5a4')]},
                        ]) \
                .bar(subset=slice_2, align='mid',color=['blue','red']), 800, 800)   
        with col2:
            st.write("")
        with col3:
            flag = ['부동산원','전세증감']
            rank_ojdf = pd.DataFrame()
            rank_ojdf['1w'] = last_ojdf['1w'].rank(ascending=True, method='min').round(decimals=1)
            rank_ojdf['2w'] = last_ojdf['2w'].rank(ascending=True, method='min').round(decimals=1)
            rank_ojdf['3w'] = last_ojdf['3w'].rank(ascending=True, method='min').round(decimals=1)
            rank_ojdf['1m'] = last_ojdf['1m'].rank(ascending=True, method='min').round(decimals=1)
            rank_ojdf['1y'] = last_ojdf['1y'].rank(ascending=True, method='min').round(decimals=1)
            rank_ojdf['1w%'] = last_ojdf['1w'].round(decimals=2)
            rank_ojdf['2w%'] = last_ojdf['2w'].round(decimals=2)
            rank_ojdf['3w%'] = last_ojdf['3w'].round(decimals=2)
            rank_ojdf['1m%'] = last_ojdf['1m'].round(decimals=2)
            rank_ojdf['1y%'] = last_ojdf['1y'].round(decimals=2)
            slice_1 = ['1w%', '2w%', '3w%', '1m%', '1y%' ]
            slice_2 = ['1w', '2w', '3w', '1m', '1y' ]
            st.markdown("부동산원 235개 지역 _전세지수_ 기간별 순위")
            rank_ojdf = rank_ojdf.reset_index()
            st.dataframe(rank_ojdf.style.background_gradient(cmap, axis=0, subset=slice_1)\
                .format(precision=2, na_rep='MISSING', thousands=",", subset=slice_1)\
                .format(precision=0, na_rep='MISSING', thousands=",", subset=slice_2)\
                #.set_properties(subset=[rank_odf.index], **{'width': '100px'})\
                .set_table_styles(
                        [{'selector': f'th.col_heading.level0.col{col_loc}',
                        'props': [('background-color', '#67c5a4')]},
                        ]) \
                .bar(subset=slice_2, align='mid',color=['blue','red']), 800, 800)
            
    html_br="""
    <br>
    """
    st.markdown(html_br, unsafe_allow_html=True)
    ### Draw 광역시도 전체 기간 누적 차트 #########################################################################################
    with st.container():
        col1, col2, col3 = st.columns([30,2,30])
        with col1:
            flag = 'KB'
            citys = ['전국', '서울', '경기', '인천', '대전', '광주', '대구', '부산', '울산', '세종']
            drawAPT_weekly.draw_flower_together(citys, cum_mdf, cum_jdf, flag)

        with col2:
            st.write("")
        with col3:
            flag = '부동산원'
            drawAPT_weekly.draw_flower_together(citys, cum_omdf, cum_ojdf, flag)
            
    html_br="""
    <br>
    """
    st.markdown(html_br, unsafe_allow_html=True)
    ### Draw 도 전체 기간 누적 차트 #########################################################################################
    with st.container():
        col1, col2, col3 = st.columns([30,2,30])
        with col1:
            flag = 'KB'
            citys = ['전국', '충북', '충남', '전북', '전남', '경북', '경남', '제주']
            drawAPT_weekly.draw_flower_together(citys, cum_mdf, cum_jdf, flag)

        with col2:
            st.write("")
        with col3:
            flag = '부동산원'
            drawAPT_weekly.draw_flower_together(citys, cum_omdf, cum_ojdf, flag)
            
    html_br="""
    <br>
    """
    st.markdown(html_br, unsafe_allow_html=True)
    ### Draw 매수우위지수와 전세수급지수 #########################################################################################
    with st.container():
        col1, col2, col3 = st.columns([30,2,30])
        with col1:
            drawAPT_weekly.draw_senti_last(jeon_su_df)
        with col2:
            st.write("")
        with col3:
            city_list = ['전국', '서울', '6개광역시', '수도권', '기타지방']
            drawAPT_weekly.draw_senti_together(maesu_df, city_list)
            
    html_br="""
    <br>
    """
    st.markdown(html_br, unsafe_allow_html=True)
    ######매수우위지수 각 지역별 보기
    ### Draw 매수우위지수와 전세수급지수 #########################################################################################
    with st.container():
        col1, col2, col3 = st.columns([30,2,30])
        with col1:
            city_list = ['서울', '인천', '경기도', '세종', '부산', '대구', '광주', '대전', '울산']
            drawAPT_weekly.draw_senti_together(maesu_df, city_list)
        with col2:
            st.write("")
        with col3:
            city_list = ['강원도', '충청북도', '충청남도', '전라북도', '전라남도', '경상북도', '경상남도', '제주']
            drawAPT_weekly.draw_senti_together(maesu_df, city_list)            
    html_br="""
    <br>
    """
    st.markdown(html_br, unsafe_allow_html=True)


if __name__ == "__main__":
    #st.title("KB 부동산 주간 시계열 분석")
    data_load_state = st.text('Loading index Data...')
    mdf, jdf, omdf, ojdf, basic_df = get_gsheet_index()
    #여기서 만들어 보자!!!
    #============KB주간 증감률=========================================
    mdf_change = mdf.pct_change()*100
    mdf_change = mdf_change.iloc[1:]
    mdf_change.replace([np.inf, -np.inf], np.nan, inplace=True)
    mdf_change = mdf_change.astype(float).fillna(0)
    jdf_change = jdf.pct_change()*100
    jdf_change = jdf_change.iloc[1:]
    jdf_change.replace([np.inf, -np.inf], np.nan, inplace=True)
    jdf_change = jdf_change.astype(float).fillna(0)
    cum_mdf = (1+mdf_change/100).cumprod() -1
    cum_mdf = cum_mdf.round(decimals=3)
    cum_jdf = (1+jdf_change/100).cumprod() -1
    cum_jdf = cum_jdf.round(decimals=3)
    #일주일 간 매매지수 상승률 순위
    kb_last_df  = pd.DataFrame()
    kb_last_df['매매증감'] = mdf_change.iloc[-1].T.to_frame()
    kb_last_df['전세증감'] = jdf_change.iloc[-1].T.to_frame()
    kb_last_df['1w'] = mdf_change.iloc[-1].T.to_frame() 
    kb_last_df['2w'] = mdf_change.iloc[-2].T.to_frame()
    kb_last_df['3w'] = mdf_change.iloc[-3].T.to_frame()
    kb_last_df['1m'] = mdf_change.iloc[-4].T.to_frame()
    kb_last_df['1y'] = mdf_change.iloc[-51].T.to_frame()
    kb_last_df = kb_last_df.astype(float).fillna(0).round(decimals=2)
    #일주일 간 전세지수 상승률 순위
    kb_last_jdf  = pd.DataFrame()
    kb_last_jdf['1w'] = jdf_change.iloc[-1].T.to_frame() 
    kb_last_jdf['2w'] = jdf_change.iloc[-2].T.to_frame()
    kb_last_jdf['3w'] = jdf_change.iloc[-3].T.to_frame()
    kb_last_jdf['1m'] = jdf_change.iloc[-4].T.to_frame()
    kb_last_jdf['1y'] = jdf_change.iloc[-51].T.to_frame()
    kb_last_jdf = kb_last_jdf.astype(float).fillna(0).round(decimals=2)

    #마지막달 dataframe에 지역 코드 넣어 합치기
    kb_df = pd.merge(kb_last_df, basic_df, how='inner', left_index=True, right_on='short')

    #버블 지수 만들어 보자
    #아기곰 방식:버블지수 =(관심지역매매가상승률-전국매매가상승률) - (관심지역전세가상승률-전국전세가상승률)
    bubble_df = mdf_change.subtract(mdf_change['전국'], axis=0)- jdf_change.subtract(jdf_change['전국'], axis=0)
    bubble_df = bubble_df*100
    bubble_df2 = mdf_change.subtract(mdf_change['전국'], axis=0)/jdf_change.subtract(jdf_change['전국'], axis=0)
    bubble_df2 = bubble_df2
    
    #곰곰이 방식: 버블지수 = 매매가비율(관심지역매매가/전국평균매매가) - 전세가비율(관심지역전세가/전국평균전세가)
    bubble_df3 = mdf.div(mdf['전국'], axis=0) - jdf.div(jdf['전국'], axis=0)
    bubble_df3 = bubble_df3.astype(float).fillna(0).round(decimals=5)*100
    # st.dataframe(bubble_df3)

    #전세 파워 만들기
    cum_ch = (mdf_change/100 +1).cumprod()
    jcum_ch = (jdf_change/100 +1).cumprod()
    m_power = (jcum_ch - cum_ch)*100
    m_power = m_power.astype(float).fillna(0).round(decimals=2)

    #마지막 데이터만 
    power_df = m_power.iloc[-1].T.to_frame()
    power_df['버블지수'] = bubble_df3.iloc[-1].T.to_frame()
    power_df.columns = ['전세파워', '버블지수']
    # power_df.dropna(inplace=True)
    power_df = power_df.astype(float).fillna(0).round(decimals=2)
    power_df['jrank'] = power_df['전세파워'].rank(ascending=False, method='min').round(1)
    power_df['brank'] = power_df['버블지수'].rank(ascending=True, method='min').round(decimals=1)
    power_df['score'] = power_df['jrank'] + power_df['brank']
    power_df['rank'] = power_df['score'].rank(ascending=True, method='min')
    power_df = power_df.sort_values('rank', ascending=True)

    with urlopen(geo_source) as response:
        kb_geo_data = json.load(response)
    
    #geojson file 변경
    for idx, sigun_dict in enumerate(kb_geo_data['features']):
        sigun_id = sigun_dict['properties']['SIG_CD']
        sigun_name = sigun_dict['properties']['SIG_KOR_NM']
        try:
            sell_change = kb_df.loc[(kb_df.code == sigun_id), '매매증감'].iloc[0]
            jeon_change = kb_df.loc[(kb_df.code == sigun_id), '전세증감'].iloc[0]
        except:
            sell_change = 0
            jeon_change =0
        # continue
        
        txt = f'<b><h4>{sigun_name}</h4></b>매매증감: {sell_change:.2f}<br>전세증감: {jeon_change:.2f}'
        # print(txt)
        
        kb_geo_data['features'][idx]['id'] = sigun_id
        kb_geo_data['features'][idx]['properties']['sell_change'] = sell_change
        kb_geo_data['features'][idx]['properties']['jeon_change'] = jeon_change
        kb_geo_data['features'][idx]['properties']['tooltip'] = txt
    #==========부동산원==========================================================
    #주간 증감률
    omdf_change = omdf.pct_change()*100
    omdf_change = omdf_change.iloc[1:]
    omdf_change.replace([np.inf, -np.inf], np.nan, inplace=True)
    omdf_change = omdf_change.astype(float).fillna(0)
    ojdf_change = ojdf.pct_change()*100
    ojdf_change = ojdf_change.iloc[1:]
    ojdf_change.replace([np.inf, -np.inf], np.nan, inplace=True)
    ojdf_change = ojdf_change.astype(float).fillna(0)
    #omdf_change = omdf_change.round(decimals=6)
    #ojdf_change = ojdf_change.round(decimals=6)
    cum_omdf = (1+omdf_change/100).cumprod() -1
    cum_omdf = cum_omdf.round(decimals=6)
    cum_ojdf = (1+ojdf_change/100).cumprod() -1
    cum_ojdf = cum_ojdf.round(decimals=6)
    #일주일 간 매매지수 상승률 순위
    last_odf = pd.DataFrame()
    last_odf['매매증감'] = omdf_change.iloc[-1].T.to_frame()
    last_odf['전세증감'] = ojdf_change.iloc[-1].T.to_frame()
    last_odf['1w'] = omdf_change.iloc[-1].T.to_frame()
    last_odf['2w'] = omdf_change.iloc[-2].T.to_frame()
    last_odf['3w'] = omdf_change.iloc[-3].T.to_frame()
    last_odf['1m'] = omdf_change.iloc[-4].T.to_frame()
    last_odf['1y'] = omdf_change.iloc[-51].T.to_frame()
    last_odf = last_odf.astype(float).fillna(0).round(decimals=2)
    #일주일 간 전세지수 상승률 순위
    last_ojdf = pd.DataFrame()
    last_ojdf['1w'] = ojdf_change.iloc[-1].T.to_frame()
    last_ojdf['2w'] = ojdf_change.iloc[-2].T.to_frame()
    last_ojdf['3w'] = ojdf_change.iloc[-3].T.to_frame()
    last_ojdf['1m'] = ojdf_change.iloc[-4].T.to_frame()
    last_ojdf['1y'] = ojdf_change.iloc[-51].T.to_frame()
    last_ojdf = last_ojdf.astype(float).fillna(0).round(decimals=2)
    #basic_df = get_basic_df()
    odf = pd.merge(last_odf, basic_df, how='inner', left_index=True, right_on='short')

    with urlopen(geo_source) as response:
        one_geo_data = json.load(response)
    
    #geojson file 변경
    for idx, sigun_dict in enumerate(one_geo_data['features']):
        sigun_id = sigun_dict['properties']['SIG_CD']
        sigun_name = sigun_dict['properties']['SIG_KOR_NM']
        try:
            sell_change = odf.loc[(odf.code == sigun_id), '매매증감'].iloc[0]
            jeon_change = odf.loc[(odf.code == sigun_id), '전세증감'].iloc[0]
        except:
            sell_change = 0
            jeon_change =0
        # continue
        
        txt = f'<b><h4>{sigun_name}</h4></b>매매증감: {sell_change:.2f}<br>전세증감: {jeon_change:.2f}'
        # print(txt)
        
        one_geo_data['features'][idx]['id'] = sigun_id
        one_geo_data['features'][idx]['properties']['sell_change'] = sell_change
        one_geo_data['features'][idx]['properties']['jeon_change'] = jeon_change
        one_geo_data['features'][idx]['properties']['tooltip'] = txt
    

    #기존===================================
    # kb_df, kb_geo_data, kb_last_df, kb_last_jdf, mdf, jdf, mdf_change, jdf_change , m_power, bubble3, cummdf, cumjdf = load_index_data()
    # odf, o_geo_data, last_odf, last_ojdf, omdf, ojdf, omdf_change, ojdf_change, cumomdf, cumojdf = load_one_data()
    #수급지수
    senti_df, jeon_senti, jeon_su_df, maesu_df, jeon_s = load_senti_data()
    data_load_state.text("index Data Done! (using st.cache)")
    #마지막 주
    kb_last_week = pd.to_datetime(str(mdf.index.values[-1])).strftime('%Y.%m.%d')
    one_last_week = pd.to_datetime(str(omdf.index.values[-1])).strftime('%Y.%m.%d')
    with st.expander("See recently Data Update"):
        cols = st.columns(2)
        cols[0].write(f"KB last update date: {kb_last_week}")
        cols[1].write(f"부동산원 last update date: {one_last_week}")

    org = kb_df['지역']
    org = org.str.split(" ", expand=True)

    #여기서부터는 선택
    my_choice = st.sidebar.radio("What' are you gonna do?", ('Basic','Price Index', 'Sentiment analysis', 'Together', '기간증감분석'))
    if my_choice == 'Basic':
        #st.subheader("전세파워 높고 버블지수 낮은 지역 상위 50곳")
        #st.table(power_df.iloc[:50])
        submit = st.sidebar.button('Draw Basic chart')
        if submit:
            #draw_basic(df, k_geo_data, last_df, one_df, o_geo_data, one_last_odf)
            draw_basic()
            # st.dataframe(df)
            # drawKorea('매매증감', df, '광역시도', '행정구역', 'Reds', 'KB 주간 아파트 매매 증감', kb_last_week)
            # drawKorea('면적', df1, '광역시도', '행정구역', 'Blues')

    elif my_choice == 'Price Index':
        
        city_list = ['전국', '수도권', '지방', '6대광역시', '5대광역시', '서울', '경기', '부산', '대구', '인천', '광주', '대전',
                  '울산', '세종', '강원', '충북', '충남', '전북', '전남', '경북', '경남', '제주도']

        column_list = mdf.columns.to_list()
        city_series = pd.Series(column_list)
        selected_dosi = st.sidebar.selectbox(
                '광역시-도-시', city_list
            )
        
        #두번째 도시
        small_list = []
        mirco_list = []
        if selected_dosi == '전국':
            small_list = ['전국', '수도권', '지방', '6대광역시']
        elif selected_dosi == '서울':
            small_list = ['서울', '서울 강북권역', '서울 강남권역']
        elif selected_dosi == '부산' or selected_dosi == '인천' or selected_dosi == '광주' \
            or selected_dosi == '대전' or selected_dosi == '울산' :
            small_list = city_series[city_series.str.contains(selected_dosi)].to_list()
        elif selected_dosi == '대구':
            small_list = ['대구','대구 수성구', '대구 중구', '대구 동구', '대구 서구', '대구 남구', '대구 북구', '대구 달서구', '대구 달성군'] 
        elif selected_dosi == '경기':
            small_list = ['경기', '수원', '성남','고양', '안양', '부천', '의정부', '광명', '평택','안산', '과천', '구리', '남양주', '용인', '시흥', '군포', \
                        '의왕','하남','오산','파주','이천','안성','김포', '양주','동두천','경기 광주', '화성']
        elif selected_dosi == '강원':
            small_list = ['강원', '춘천','강릉', '원주']
        elif selected_dosi == '충북':
            small_list = ['충북','청주', '충주','제천']
        elif selected_dosi == '충남':
            small_list = ['충남','천안', '공주','아산', '논산', '계룡','당진','서산']
        elif selected_dosi == '전북':
            small_list = ['전북', '전주', '익산', '군산']
        elif selected_dosi == '전남':
            small_list = ['전남', '목포','순천','여수','광양']
        elif selected_dosi == '경북':
            small_list = ['경북','포항','구미', '경산', '안동','김천']
        elif selected_dosi == '충북':
            small_list = ['경남','창원', '양산','거제','진주', '김해','통영']
        elif selected_dosi == '제주도':
            small_list = ['제주, 서귀포']
        elif selected_dosi == '세종':
            small_list = ['세종']
        else:
            small_list = [selected_dosi]
        
        second_list = city_series[city_series.str.contains(selected_dosi)].to_list()
        selected_dosi2 = st.sidebar.selectbox(
                '구-시', small_list
            )
        # if  st.checkbox('Show 매매지수 data'):
        #     st.dataframe(mdf.style.highlight_max(axis=0))
        if selected_dosi2 == '수원':
            mirco_list = ['수원', '수원 장안구', '수원 권선구', '수원 팔달구', '수원 영통구']
        elif selected_dosi2 == '성남':
            mirco_list = ['성남', '성남 수정구', '성남 중원구', '성남 분당구']
        elif selected_dosi2 == '고양':
            mirco_list = ['고양', '고양 덕양구', '고양 일산동구', '고양 일산서구']
        elif selected_dosi2 == '안양':
            mirco_list = ['안양', '안양 만안구', '안양 동안구']
        elif selected_dosi2 == '안산':
            mirco_list = ['안산', '안산 단원구', '안산 상록구']
        elif selected_dosi2 == '용인':
            mirco_list = ['용인', '용인 처인구', '용인 기흥구', '용인 수지구']
        elif selected_dosi2 == '천안':
            mirco_list = ['천안', '천안 서북구', '천안 동남구']
        elif selected_dosi2 == '청주':
            mirco_list = ['청주', '청주 청원구', '청주 흥덕구', '청주 서원구', '청주 상당구']
        elif selected_dosi2 == '전주':
            mirco_list = ['전주', '전주 덕진구', '전주 완산구']
        elif selected_dosi2 == '포항':
            mirco_list = ['포항', '포항 남구', '포항 북구']
        elif selected_dosi2 == '창원':
            mirco_list = ['창원', '창원 마산합포구', '창원 마산회원구', '창원 성산구', '창원 의창구', '창원 진해구']

        selected_dosi3 = st.sidebar.selectbox(
                '구', mirco_list
            )
        
        submit = st.sidebar.button('Draw Price Index together')
        if submit:
            run_price_index()
    elif my_choice == 'Sentiment analysis':
        city_list = ['전국', '서울', '강북', '강남', '6대광역시', '5대광역시', '부산', '대구', '인천', '광주', '대전',
                  '울산', '세종', '수도권', '경기', '강원', '충북', '충남', '전북', '전남', '경북', '경남', '지방', '제주도']

        ms_1 = senti_df.xs("매도자많음", axis=1, level=1)
        ms_1.columns = city_list
        ms_2 = senti_df.xs("매수자많음", axis=1, level=1)
        ms_2.columns = city_list
        ms_index = senti_df.xs("매수우위지수", axis=1, level=1)
        ms_index.columns = city_list
        ms_index = ms_index.round(decimals=2)
        #전세수급지수
        js_1 = jeon_senti.xs("수요>공급", axis=1, level=1)
        js_1.columns = city_list
        js_2 = jeon_senti.xs("수요<공급", axis=1, level=1)
        js_2.columns = city_list
        js_index = jeon_senti.xs("전세수급지수", axis=1, level=1)
        js_index.columns = city_list
        js_index = js_index.round(decimals=2)
        # st.dataframe(js_index)     
        # column_list = js_index.columns.to_list()
        selected_dosi = st.sidebar.selectbox(
                '광역시-도', city_list
            )
        submit = st.sidebar.button('Draw Sentimental Index chart')
        if submit:
            run_sentimental_index(mdf_change, jdf_change)
    elif my_choice == 'Together':
        citys = omdf.columns.tolist()
        options = st.multiselect('Select City to Compare index', citys, citys[:3])
        submit = st.button('Draw Index chart togethger')
        if submit:
            ### Draw Bubble chart #########################################################################################
            with st.container():
                col1, col2, col3 = st.columns([30,2,30])
                with col1:
                    flag = '부동산원 주간'
                    drawAPT_weekly.run_one_index_together(options, omdf, omdf_change, flag)

                with col2:
                    st.write("")
                with col3:
                    flag = '부동산원 주간'
                    drawAPT_weekly.draw_flower_together(options, cumomdf, cumojdf, flag)
                    
            html_br="""
            <br>
            """          
    else:
        flag = ['KB','매매증감']
        flag1 = ['부동산원','매매증감']
        period_ = omdf.index.strftime("%Y-%m-%d").tolist()
        st.subheader("기간 상승률 분석")
        start_date, end_date = st.select_slider(
            'Select Date to Compare index change', 
            options = period_,
            value = (period_[-105], period_[-1]))
        
        #부동산원 / KB
        slice_om = omdf.loc[start_date:end_date]
        slice_oj = ojdf.loc[start_date:end_date]
        slice_m = mdf.loc[start_date:end_date]
        slice_j = jdf.loc[start_date:end_date]
        #기간 동안 매매지수는 하락하고 전세 지수는 증가한 지역 찾기
        s_m = pd.DataFrame()
        s_j = pd.DataFrame()
        so_m = pd.DataFrame()
        so_j = pd.DataFrame()
        s_m[start_date] = slice_m.iloc[0].T
        s_m[end_date] = slice_m.iloc[-1].T
        s_j[start_date] = slice_j.iloc[0].T
        s_j[end_date] = slice_j.iloc[-1].T
        so_m[start_date] = slice_om.iloc[0].T
        so_m[end_date] = slice_om.iloc[-1].T
        so_j[start_date] = slice_oj.iloc[0].T
        so_j[end_date] = slice_oj.iloc[-1].T
        condition1 = s_m.iloc[:,0] > s_m.iloc[:,-1]
        condition2 = s_j.iloc[:,0] <= s_j.iloc[:,-1]
        condition3 = so_m.iloc[:,0] > so_m.iloc[:,-1]
        condition4 = so_j.iloc[:,0] <= so_j.iloc[:,-1]
        m_de = s_m.loc[condition1]
        j_in = s_j.loc[condition2]
        mo_de = so_m.loc[condition3]
        jo_in = so_j.loc[condition4]
        inter_df = pd.merge(m_de, j_in, how='inner', left_index=True, right_index=True, suffixes=('_m', '_j'))
        inter_odf = pd.merge(mo_de, jo_in, how='inner', left_index=True, right_index=True, suffixes=('_m', '_j'))
        #기간 변화 누적 계산
        slice_om_ch = omdf_change.loc[start_date:end_date]
        slice_oj_ch = ojdf_change.loc[start_date:end_date]
        slice_m_ch = mdf_change.loc[start_date:end_date]
        slice_j_ch= jdf_change.loc[start_date:end_date]
        S_cum_om = (1+slice_om_ch/100).cumprod() -1
        S_cum_oj = (1+slice_oj_ch/100).cumprod() -1
        S_cum_m = (1+slice_m_ch/100).cumprod() -1
        S_cum_j = (1+slice_j_ch/100).cumprod() -1
        diff = slice_om.index[-1] - slice_om.index[0]
        #information display
        cols = st.columns(4)
        cols[0].write(f"시작: {start_date}")
        cols[1].write(f"끝: {end_date}")
        cols[2].write(f"전체 기간: {round(diff.days/365,1)} 년")
        cols[3].write("")
        #st.dataframe(slice_om)
        change_odf = pd.DataFrame()
        change_odf['매매증감'] = (slice_om.iloc[-1]/slice_om.iloc[0]-1).to_frame()*100
        change_odf['전세증감'] = (slice_oj.iloc[-1]/slice_oj.iloc[0]-1).to_frame()*100
        change_odf = change_odf.dropna().astype(float).round(decimals=2)
        change_df = pd.DataFrame()
        change_df['매매증감'] = (slice_m.iloc[-1]/slice_m.iloc[0]-1).to_frame()*100
        change_df['전세증감'] = (slice_j.iloc[-1]/slice_j.iloc[0]-1).to_frame()*100
        change_df = change_df.dropna().astype(float).round(decimals=2)
        submit = st.button('Draw 기간 증감 chart')
        html_br="""
        <br>
        """
        st.markdown(html_br, unsafe_allow_html=True)
        if submit:
            ### 기간동안 전세지수는 증가하고 매매지수는 감소한 지역############################################################
            with st.container():
                col1, col2, col3 = st.columns([30,2,30])
                with col1:
                    #flag = "KB"  
                    st.write("KB 매매 감소-전세 증가") 
                    response  = aggrid_interactive_table(df=inter_df)
                    # st.dataframe(inter_df.style.background_gradient(cmap, axis=0)\
                    #                 .format(precision=2, na_rep='MISSING', thousands=","))  
                with col2:
                    st.write("")
                with col3:
                    flag = "부동산원"
                    st.write("부동산원 매매 감소-전세 증가")
                    response  = aggrid_interactive_table(df=inter_odf)
                    # st.dataframe(inter_odf.style.background_gradient(cmap, axis=0)\
                    #                       .format(precision=2, na_rep='MISSING', thousands=","))
            html_br="""
            <br>
            """
            ### Draw Bubble chart #########################################################################################
            with st.container():
                col1, col2, col3 = st.columns([30,2,30])
                with col1:
                    flag = 'KB 주간'
                    drawAPT_weekly.draw_index_change_with_bubble(change_df, flag)

                with col2:
                    st.write("")
                with col3:
                    flag = '부동산원 주간'
                    drawAPT_weekly.draw_index_change_with_bubble(change_odf, flag)
                    
            html_br="""
            <br>
            """
             ### Draw Bubble chart #########################################################################################
            with st.container():
                col1, col2, col3 = st.columns([30,2,30])
                with col1:
                    #flag = "KB"  
                    st.write("KB 기간 증감") 
                    #change_df = change_df.reset_index()
                    response  = aggrid_interactive_table(df=change_df)            
                    # st.dataframe(change_df.style.background_gradient(cmap, axis=0)\
                    #                 .format(precision=2, na_rep='MISSING', thousands=","))  
                    #drawAPT_weekly.draw_change_table(change_df, flag)  
                with col2:
                    st.write("")
                with col3:
                    flag = "부동산원"
                    st.write("부동산원 기간 증감")
                    #change_odf = change_odf.reset_index()
                    response  = aggrid_interactive_table(df=change_odf)
                    # st.dataframe(change_odf.style.background_gradient(cmap, axis=0)\
                    #                       .format(precision=2, na_rep='MISSING', thousands=","))
                    #drawAPT_weekly.draw_change_table(change_df, flag) 
            html_br="""
            <br>
            """
            ### Draw 광역시도 전체 기간 누적 차트 #########################################################################################
            with st.container():
                col1, col2, col3 = st.columns([30,2,30])
                with col1:
                    flag = 'KB'
                    citys = ['전국', '서울', '경기', '인천', '대전', '광주', '대구', '부산', '울산', '세종']
                    drawAPT_weekly.draw_flower_together(citys, S_cum_m, S_cum_j, flag)

                with col2:
                    st.write("")
                with col3:
                    flag = '부동산원'
                    drawAPT_weekly.draw_flower_together(citys, S_cum_om, S_cum_oj, flag)
                    
            html_br="""
            <br>
            """
            st.markdown(html_br, unsafe_allow_html=True)
            ### Draw 도 전체 기간 누적 차트 #########################################################################################
            with st.container():
                col1, col2, col3 = st.columns([30,2,30])
                with col1:
                    flag = 'KB'
                    citys = ['전국', '충북', '충남', '전북', '전남', '경북', '경남', '제주']
                    drawAPT_weekly.draw_flower_together(citys, S_cum_m, S_cum_j, flag)

                with col2:
                    st.write("")
                with col3:
                    flag = '부동산원'
                    citys = ['전국', '충북', '충남', '전북', '전남', '경북', '경남', '제주도']
                    drawAPT_weekly.draw_flower_together(citys, S_cum_om, S_cum_oj, flag)
                    
            html_br="""
            <br>
            """
            st.markdown(html_br, unsafe_allow_html=True)