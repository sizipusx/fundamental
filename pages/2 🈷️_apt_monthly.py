import datetime
import numpy as np
import pandas as pd
import sqlite3
from urllib.request import urlopen
import json
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
import drawAPT_weekly 
import drawAPT_update
import seaborn as sns
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from st_aggrid import AgGrid, GridOptionsBuilder
from st_aggrid.shared import GridUpdateMode
cmap = cmap=sns.diverging_palette(250, 5, as_cmap=True)

#############html 영역####################
html_header="""
<head>
<title>Korea local house analysis</title>
<meta charset="utf-8">
<meta name="keywords" content="house data, dashboard, analysis, EVA">
<meta name="description" content="house data dashboard">
<meta name="author" content="indiesoul">
<meta name="viewport" content="width=device-width, initial-scale=1">
</head>
<h1 style="font-size:200%; color:#008080; font-family:Georgia">  🈷️ 월간 부동산 시계열 분석 <br>
 <hr style= "  display: block;
  margin-top: 0.5em;
  margin-bottom: 0.5em;
  margin-left: auto;
  margin-right: auto;
  border-style: inset;
  border-width: 1.5px;"></h1>
"""

st.set_page_config(page_title="🈷️ 월간 부동산 시계열 분석", page_icon="files/logo2.png", layout="wide")
st.markdown('<style>body{background-color: #fbfff0}</style>',unsafe_allow_html=True)
st.markdown(html_header, unsafe_allow_html=True)
st.markdown(""" <style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style> """, unsafe_allow_html=True)

pd.set_option('display.float_format', '{:.2f}'.format)
#오늘날짜까지
utcnow= datetime.datetime.utcnow()
time_gap= datetime.timedelta(hours=9)
kor_time= utcnow+ time_gap

##################################### 기존 파일 시스템 ##################################
kb_path = 'https://github.com/sizipusx/fundamental/blob/d1268bcfbbca48adb13193485d0b5990d599bc45/files/kb_monthly.xlsx?raw=true'
#감정원 데이터
one_path = r'https://github.com/sizipusx/fundamental/blob/4f60b8b60a3a168a8188b33583f23ecc9127281a/files/one_data.xlsx?raw=true'
#헤더 변경
header_path = r'https://github.com/sizipusx/fundamental/blob/bc990c892ec68351be5b45b79f3dbf6bd2590222/files/header.xlsx?raw=true'
header_excel = pd.ExcelFile(header_path)
kbh = header_excel.parse('KB')
oneh = header_excel.parse('one')
citys = header_excel.parse('city')
# KB 데이터
kbm_dict = pd.ExcelFile(kb_path)
one_dict = pd.ExcelFile(one_path)
#geojson file open
geo_source = 'https://raw.githubusercontent.com/sizipusx/fundamental/main/sigungu_json.geojson'
################################### gsheet 로 변경: 2022-7-17 ###########################
#주간 gsheet
#w_gsheet_url = r'https://raw.githubusercontent.com/sizipusx/fundamental/a55cf1853a1fc24ff338e7293a0d526fc0520e76/files/weekly-house-db-ac0a43b61ddd.json'

scope = [
    'https://spreadsheets.google.com/feeds',
    'https://www.googleapis.com/auth/drive',
    ]

# json_file_name = '/fundamental/files/weekly-house-db-ac0a43b61ddd.json'
json_file_name = "files/weekly-house-db-ac0a43b61ddd.json"

credentials = ServiceAccountCredentials.from_json_keyfile_name(json_file_name, scope)
gc = gspread.authorize(credentials)

one_gsheet_url = r'https://docs.google.com/spreadsheets/d/1_Sr5uA-rDyJnHgVu_pHMkmavuQC7VpuYpVmnBaNRX8M/edit?usp=sharing'
kb_gsheet_url = r'https://docs.google.com/spreadsheets/d/168K8mcybxQfufMi39wnH5agmMrkK9C8ac57MajmOawI/edit?usp=sharing'
basic_url = r'https://docs.google.com/spreadsheets/d/1s5sS6K7YpbwKJBofHKEl8WsbUDJ0acmrOuw6YN8YZhw/edit?usp=sharing'

one_doc = gc.open_by_url(one_gsheet_url)
kb_doc = gc.open_by_url(kb_gsheet_url)
#인구, 세대수, 기본 소득
bs_doc = gc.open_by_url(basic_url)
#############################2022.9.30 sqlite3로 변경######################################
one_db_path = "files/one_monthly.db"
kb_db_path = "files/kb_monthly.db"

@st.cache_resource(ttl=datetime.timedelta(days=1))
def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by the db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file, check_same_thread=False)
    except Exception as e:
       print(e)

    return conn

 #return dic
def read_source_excel():
    kbm_dict = pd.read_excel(kb_path, sheet_name=None, header=1)

    return kbm_dict


@st.cache(allow_output_mutation=True)
def get_basic_df():
    #2021-7-30 코드 추가
    # header 파일
    basic_df = header_excel.parse('city')
    basic_df['총인구수'] = basic_df['총인구수'].astype(str).apply(lambda x: x.replace(',','')).astype(float)
    basic_df['세대수'] = basic_df['세대수'].astype(str).apply(lambda x: x.replace(',','')).astype(float)
    basic_df.dropna(inplace=True)
    basic_df['밀도'] = basic_df['총인구수']/basic_df['면적']

    return basic_df

@st.cache_data(ttl=datetime.timedelta(days=1))
def get_not_sell_apt():
    ## 2021. 9. 23 완공 후 미분양 데이터 가져오기
    # df1 = one_dict.parse("not_sell_after")

    # #컬럼명 바꿈
    # j1 = df1.columns
    # new_s1 = []
    # for num, gu_data in enumerate(j1):
    #     check = num
    #     if gu_data.startswith('Un'):
    #         new_s1.append(new_s1[check-1])
    #     else:
    #         new_s1.append(j1[check])

    # #컬럼 설정
    # df1.columns = [new_s1,df1.iloc[0]]
    # df1 = df1.iloc[1:,:]
    # df1 = df1.fillna(0)
    # df1 = df1.set_index(df1.iloc[:,0])
    # df1.index.name = 'date'
    # df1 = df1.iloc[:,1:]
    # df1 = df1.astype(int)

    # return df1

    #DB에서 읽어오자
    try:
        buy_conn = create_connection(one_db_path)
        not_sold_list = []
        query_list = ["select * from not_sold", "select * from after_not_sold"]
        for query in query_list:
            df = pd.read_sql(query, buy_conn, index_col='date', parse_dates={'date', "%Y-%m"})
            # query = conn.execute(query)
            # cols = [column[0] for column in query.description]
            # df= pd.DataFrame.from_records(
            #             data = query.fetchall(), 
            #             columns = cols
            #     )
            #df.index = pd.to_datetime(df.index, format = '%Y-%m')
            not_sold_list.append(df)
    except Exception as e:
        print(e)
    
    #투자자 거주지별 매매동향
    ### db에서 읽기
    in_df = pd.read_sql("SELECT * FROM 'investor'", buy_conn, index_col='index')
    in_df = in_df.apply(lambda x: x.replace('-','0'))
    in_df = in_df.astype(int)

    conn.close()


    return not_sold_list, in_df

    # #미분양
    # mb = one_doc.worksheet('notsold')
    # mb_values = mb.get_all_values()
    # mb_header, mb_rows = mb_values[1], mb_values[2:]
    # mb_df = pd.DataFrame(mb_rows, columns=mb_header)
    # mb_df = mb_df.set_index(mb_df.iloc[:,0])
    # mb_df = mb_df.iloc[:,1:]
    # mb_df.index.name = 'date'
    # mb_df = mb_df.astype(str).apply(lambda x:x.replace(',','')).apply(lambda x:x.replace('','0')).replace('#DIV/0!','0').astype(int)
    # mb_df.index = pd.to_datetime(mb_df.index)
    # #준공 후 미분양
    # ns = one_doc.worksheet('afternotsold')
    # ns_values = ns.get_all_values()
    # ns_header, ns_rows = ns_values[1], ns_values[2:]
    # omdf = pd.DataFrame(ns_rows, columns=ns_header)
    # omdf = omdf.set_index(omdf.iloc[:,0])
    # omdf = omdf.iloc[:,1:]
    # omdf.index.name = 'date'
    # omdf = omdf.astype(str).apply(lambda x:x.replace(',','')).apply(lambda x:x.replace('','0')).replace('#DIV/0!','0').astype(int)
    # omdf.index = pd.to_datetime(omdf.index)

    # return omdf, mb_df

@st.cache_data(ttl=datetime.timedelta(days=1))
def load_index_data():
    code_df = header_excel.parse('code', index_col=1)
    code_df.index = code_df.index.str.strip()

    #주택가격지수
    # mdf = kbm_dict.parse("2.매매APT", skiprows=1, index_col=0)
    # jdf = kbm_dict.parse("6.전세APT", skiprows=1, index_col=0)
    # mdf.columns = kbh.columns
    # jdf.columns = kbh.columns
    # #index 날짜 변경
    
    # mdf = mdf.iloc[2:]
    # jdf = jdf.iloc[2:]
    # index_list = list(mdf.index)

    # new_index = []

    # for num, raw_index in enumerate(index_list):
    #     temp = str(raw_index).split('.')
    #     if int(temp[0]) > 12 :
    #         if len(temp[0]) == 2:
    #             new_index.append('19' + temp[0] + '.' + temp[1])
    #         else:
    #             new_index.append(temp[0] + '.' + temp[1])
    #     else:
    #         new_index.append(new_index[num-1].split('.')[0] + '.' + temp[0])

    # mdf.set_index(pd.to_datetime(new_index), inplace=True)
    # jdf.set_index(pd.to_datetime(new_index), inplace=True)
    # mdf.replace([np.inf, -np.inf], np.nan, inplace=True)
    # jdf.replace([np.inf, -np.inf], np.nan, inplace=True)
    # mdf = mdf.astype(float).fillna(0).round(decimals=2)
    # jdf = jdf.astype(float).fillna(0).round(decimals=2)
    # 구글 시트에서 읽어 오기
    # kbm = kb_doc.worksheet('kbm')
    # kbm_values = kbm.get_all_values()
    # m_header, m_rows = kbm_values[1], kbm_values[2:]
    # mdf = pd.DataFrame(m_rows, columns=m_header)
    # mdf = mdf.set_index(mdf.iloc[:,0])
    # mdf = mdf.iloc[:,1:]
    # mdf.index = pd.to_datetime(mdf.index)
    # mdf.index.name = 'date'
    # mdf = mdf.apply(lambda x:x.replace('#DIV/0!','0')).apply(lambda x:x.replace('','0')).astype(float)
    # mdf = mdf.round(decimals=2)
    # #전세
    # kbj = kb_doc.worksheet('kbj')
    # kbj_values = kbj.get_all_values()
    # j_header, j_rows = kbj_values[1], kbj_values[2:]
    # jdf = pd.DataFrame(j_rows, columns=j_header)
    # jdf = jdf.set_index(jdf.iloc[:,0])
    # jdf = jdf.iloc[:,1:]
    # jdf.index = pd.to_datetime(jdf.index)
    # jdf.index.name = 'date'
    # jdf = jdf.apply(lambda x:x.replace('#DIV/0!','0')).apply(lambda x:x.replace('','0')).astype(float)
    # jdf = jdf.round(decimals=2)
    ######DB에서 읽어오기##################
    kb_conn = create_connection(kb_db_path)
    index_list = []
    query_list = ["select * from mae", "select * from jeon"]#, "SELECT * FROM jratio"]
    for query in query_list:
        df = pd.read_sql(query, kb_conn, index_col='date', parse_dates={'date', "%Y-%m"})
        # query = conn.execute(query)
        # cols = [column[0] for column in query.description]
        # df= pd.DataFrame.from_records(
        #             data = query.fetchall(), 
        #             columns = cols
        #     )
        #df.index = pd.to_datetime(df.index, format = '%Y-%m-%d')
        df = df.apply(lambda x:x.replace('#DIV/0!','0').replace('#N/A','0')).apply(lambda x:x.replace('','0')).astype(float)
        df = df.round(decimals=2)
        index_list.append(df)
    kb_conn.close()

    return index_list


@st.cache_data(ttl=datetime.timedelta(days=1))
def load_one_data():
    #감정원 월간 데이터
    # one header 변경
    # omdf = one_dict.parse("msell_index", header=1,index_col=0, parse_dates=True, convert_float=True)
    # ojdf = one_dict.parse("mjeon_index", header=1,index_col=0, parse_dates=True, convert_float=True)
    # omdf = omdf.iloc[3:,:]
    # ojdf = ojdf.iloc[3:,:]
    # omdf.columns = oneh.columns
    # ojdf.columns = oneh.columns
    # omdf.index = pd.to_datetime(omdf.index)
    # ojdf.index = pd.to_datetime(ojdf.index)
    # omdf.replace([np.inf, -np.inf], np.nan, inplace=True)
    # ojdf.replace([np.inf, -np.inf], np.nan, inplace=True)
    # omdf = omdf.astype(float).round(decimals=2)
    # ojdf = ojdf.astype(float).round(decimals=2)
    #구글 시트에서 읽어 오기
    # om = one_doc.worksheet('om')
    # om_values = om.get_all_values()
    # m_header, m_rows = om_values[1], om_values[2:]
    # omdf = pd.DataFrame(m_rows, columns=m_header)
    # omdf = omdf.set_index(omdf.iloc[:,0])
    # omdf = omdf.iloc[:,1:]
    # omdf.index = pd.to_datetime(omdf.index)
    # omdf.index.name = 'date'
    # omdf = omdf.apply(lambda x:x.replace('','0')).astype(float)
    # oj = one_doc.worksheet('oj')
    # oj_values = oj.get_all_values()
    # j_header, j_rows = oj_values[1], oj_values[2:]
    # ojdf = pd.DataFrame(j_rows, columns=j_header)
    # ojdf = ojdf.set_index(ojdf.iloc[:,0])
    # ojdf = ojdf.iloc[:,1:]
    # ojdf.index = pd.to_datetime(ojdf.index)
    # ojdf.index.name = 'date'
    # ojdf = ojdf.apply(lambda x:x.replace('','0')).astype(float)
    ######DB에서 읽어오기##################
    one_conn = create_connection(one_db_path)
    index_list = []
    query_list = ["select * from one_mae", "select * from one_jeon"]#, "select * from not_sold", "select * from after_not_sold", "SELECT * FROM 'investor'"]
    for query in query_list:
        df = pd.read_sql(query, one_conn, index_col='date', parse_dates={'date', "%Y-%m"})
        #df.index = pd.to_datetime(df.index, format = '%Y-%m')
        index_list.append(df)
    one_conn.close()
    # omdf = index_list[0]
    # ojdf = index_list[1]

     #주간 증감률
    # omdf_change = omdf.pct_change()*100
    # omdf_change = omdf_change.iloc[1:]
    # omdf_change.replace([np.inf, -np.inf], np.nan, inplace=True)
    # omdf_change = omdf_change.astype(float).fillna(0)
    # ojdf_change = ojdf.pct_change()*100
    # ojdf_change = ojdf_change.iloc[1:]
    # ojdf_change.replace([np.inf, -np.inf], np.nan, inplace=True)
    # ojdf_change = ojdf_change.astype(float).fillna(0)
    # omdf_change = omdf_change.round(decimals=3)
    # ojdf_change = ojdf_change.round(decimals=3)
    # cum_omdf = (1+omdf_change/100).cumprod() -1
    # cum_omdf = cum_omdf.round(decimals=3)
    # cum_ojdf = (1+ojdf_change/100).cumprod() -1
    # cum_ojdf = cum_ojdf.round(decimals=3)
    # #일주일 간 상승률 순위
    # last_odf = pd.DataFrame()
    # last_odf['매매증감'] = omdf_change.iloc[-1].T.to_frame()
    # last_odf['전세증감'] = ojdf_change.iloc[-1].T.to_frame()
    # last_odf['1w'] = omdf_change.iloc[-1].T.to_frame()
    # last_odf['2w'] = omdf_change.iloc[-2].T.to_frame()
    # last_odf['3w'] = omdf_change.iloc[-3].T.to_frame()
    # last_odf['1m'] = omdf_change.iloc[-4].T.to_frame()
    # last_odf['1y'] = omdf_change.iloc[-51].T.to_frame()
    # #last_odf.columns = ['매매증감', '전세증감', '2w', '3w', '1m', '1y']
    # #last_odf.dropna(inplace=True)
    # last_odf = last_odf.astype(float).fillna(0).round(decimals=3)
    # #last_odf = last_odf.reset_index()
    # basic_df = get_basic_df()
    # odf = pd.merge(last_odf, basic_df, how='inner', left_index=True, right_on='short')

    # with urlopen(geo_source) as response:
    #     one_geo_data = json.load(response)
    
    # #geojson file 변경
    # for idx, sigun_dict in enumerate(one_geo_data['features']):
    #     sigun_id = sigun_dict['properties']['SIG_CD']
    #     sigun_name = sigun_dict['properties']['SIG_KOR_NM']
    #     try:
    #         sell_change = odf.loc[(odf.code == sigun_id), '매매증감'].iloc[0]
    #         jeon_change = odf.loc[(odf.code == sigun_id), '전세증감'].iloc[0]
    #     except:
    #         sell_change = 0
    #         jeon_change =0
    #     # continue
        
    #     txt = f'<b><h4>{sigun_name}</h4></b>매매증감: {sell_change:.2f}<br>전세증감: {jeon_change:.2f}'
    #     # print(txt)
        
    #     one_geo_data['features'][idx]['id'] = sigun_id
    #     one_geo_data['features'][idx]['properties']['sell_change'] = sell_change
    #     one_geo_data['features'][idx]['properties']['jeon_change'] = jeon_change
    #     one_geo_data['features'][idx]['properties']['tooltip'] = txt
   
    # return odf, one_geo_data, last_odf, omdf, ojdf, omdf_change, ojdf_change, cum_omdf, cum_ojdf
    return index_list

@st.cache_data(ttl=datetime.timedelta(days=1))
def load_senti_data():
    #kbm_dict = read_source_excel()
    worksheet_list = kb_doc.worksheets()
    m_sheet = 'kbs,kbjs,kbmtr,kbjtr'
    m_list = m_sheet.split(',')
    df_dic = []
    df_a = []
    df_b = []

    for k in worksheet_list:
        # print(f"sheet name is {k}")
        if k.title in m_list:
            #print(f"sheet name is {k}")
            js = kb_doc.worksheet(k.title)
            kbs_values = js.get_all_values()
            kbs_header, kbs_rows = kbs_values[1], kbs_values[2:]
            kbs_df = pd.DataFrame(kbs_rows, columns=kbs_header)
            #js = js.set_index("Unnamed: 0")
            #js.index.name="날짜"

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
            kbs_df = kbs_df.iloc[1:]
            kbs_df = kbs_df.set_index(kbs_df.iloc[:,0])
            kbs_df = kbs_df.iloc[:,1:]
            kbs_df.index.name = 'date'
            kbs_df.astype(str).apply(lambda x: x.replace('','0')).astype(float).round(decimals=2)
            #전세수급지수만 filtering
            if k.title == 'kbs':
                js_index = kbs_df.xs("매수우위지수", axis=1, level=1)
                js_index.astype(str).apply(lambda x: x.replace('','0')).astype(float).round(decimals=2)
                js_a = kbs_df.xs("매도자 많음", axis=1, level=1)
                js_a.astype(str).apply(lambda x: x.replace('','0')).astype(float).round(decimals=2)
                js_b = kbs_df.xs("매수자 많음", axis=1, level=1)
                js_b.astype(str).apply(lambda x: x.replace('','0')).astype(float).round(decimals=2)
            elif k.title == 'kbmtr':
                js_index = kbs_df.xs("매매거래지수", axis=1, level=1)
                js_index.astype(str).apply(lambda x: x.replace('','0')).astype(float).round(decimals=2)
                js_a = kbs_df.xs("활발함", axis=1, level=1)
                js_a.astype(str).apply(lambda x: x.replace('','0')).astype(float).round(decimals=2)
                js_b = kbs_df.xs("한산함", axis=1, level=1)
                js_b.astype(str).apply(lambda x: x.replace('','0')).astype(float).round(decimals=2)
            elif k.title == 'kbjs':
                js_index = kbs_df.xs("전세수급지수", axis=1, level=1)
                js_index.astype(str).apply(lambda x: x.replace('','0')).astype(float).round(decimals=2)
                js_a = kbs_df.xs("수요>공급", axis=1, level=1)
                js_a.astype(str).apply(lambda x: x.replace('','0')).astype(float).round(decimals=2)
                js_b = kbs_df.xs("수요<공급", axis=1, level=1)
                js_b.astype(str).apply(lambda x: x.replace('','0')).astype(float).round(decimals=2)
            elif k.title == 'kbjtr':
                js_index = kbs_df.xs("전세거래지수", axis=1, level=1)
                js_index.astype(str).apply(lambda x: x.replace('','0')).astype(float).round(decimals=2)
                js_a = kbs_df.xs("활발함", axis=1, level=1)
                js_a.astype(str).apply(lambda x: x.replace('','0')).astype(float).round(decimals=2)
                js_b = kbs_df.xs("한산함", axis=1, level=1)
                js_b.astype(str).apply(lambda x: x.replace('','0')).astype(float).round(decimals=2)
            # elif k == '25.KB부동산 매매가격 전망지수':
            #     js_index = js.xs("KB부동산\n매매전망지수", axis=1, level=1)
            #     js_a = js.xs("약간상승", axis=1, level=1)
            #     js_b = js.xs("약간하락", axis=1, level=1)
            # elif k == '26.KB부동산 전세가격 전망지수':
            #     js_index = js.xs("KB부동산\n전세전망지수", axis=1, level=1)
            #     js_a = js.xs("약간상승", axis=1, level=1)
            #     js_b = js.xs("약간하락", axis=1, level=1)
            #필요 데이터만
            # js_index = js_index.iloc[2:js_index['서울'].count(), : ]
            # js_a = js_a.iloc[2:js_a['서울'].count(), : ]
            # js_b = js_b.iloc[2:js_b['서울'].count(), : ]

            #날짜 바꿔보자
            # index_list = list(js_index.index)
            # new_index = []

            # for num, raw_index in enumerate(index_list):
            #     temp = str(raw_index).split('.')
            #     if len(temp[0]) == 3:
            #         if int(temp[0].replace("'","")) >84:
            #             new_index.append('19' + temp[0].replace("'","") + '.' + temp[1])
            #         else:
            #             new_index.append('20' + temp[0].replace("'","") + '.' + temp[1])
            #     else:
            #         new_index.append(new_index[num-1].split('.')[0] + '.' + temp[0])

            # js_index.set_index(pd.to_datetime(new_index), inplace=True)
            js_index.index = pd.to_datetime(js_index.index)
            # js_a.set_index(pd.to_datetime(new_index), inplace=True)
            js_a.index = pd.to_datetime(js_a.index)
            # js_b.set_index(pd.to_datetime(new_index), inplace=True)
            js_b.index = pd.to_datetime(js_b.index)

                
            #매달 마지막 데이터만 넣기
            # js_last = js_index.iloc[-1].to_frame().T
            df_dic.append(js_index)
            df_a.append(js_a)
            df_b.append(js_b)

    return df_dic, df_a, df_b

@st.cache_data(ttl=datetime.timedelta(days=1))
def load_ratio_data():
    ######DB에서 읽어오기##################
    rconn = create_connection(kb_db_path)
    rdf = pd.read_sql("SELECT * FROM jratio", rconn, index_col='date', parse_dates={'date', "%Y-%m"}) 
    # rconn.close()

    return rdf


@st.cache_data(ttl=datetime.timedelta(days=1))
def load_pir_data():
    # pir = kbm_dict.parse('13.KB아파트담보대출PIR', skiprows=1)
    # # file_path = 'https://github.com/sizipusx/fundamental/blob/75a46e5c6a1f343da71927fc6de0dd14fdf136eb/files/KB_monthly(6A).xlsx?raw=true'
    # # kb_dict = pd.read_excel(file_path, sheet_name=None, header=1)
    # # pir =  kb_dict['KB아파트담보대출PIR']
    # pir = pir.iloc[:pir['지역'].count()-1,1:11]

    # s1 = ['분기', '서울', '서울', '서울', '경기', '경기', '경기', '인천', '인천', '인천']
    # s2 = pir.iloc[0]
    # pir.columns = [s1, s2]
    # pir = pir.iloc[1:]
    # pir = pir.set_index(('분기',            '년도'))
    # pir.index.name = '분기'
    # #분기 날짜 바꾸기
    # pir_index = list(pir.index)
    # new_index = []

    # for num, raw_index in enumerate(pir_index):
    #     temp = str(raw_index).split(' ')
    #     if len(temp[0]) == 3:
    #         if int(temp[0].replace("'","")) >84:
    #             new_index.append('19' + temp[0].replace("'","") + '.' + temp[1])
    #         else:
    #             if temp[1] == '1Q':
    #                 new_index.append('20' + temp[0].replace("'","") + '.03')
    #             elif temp[1] == '2Q':
    #                 new_index.append('20' + temp[0].replace("'","") + '.06')
    #             elif temp[1] == '3Q':
    #                 new_index.append('20' + temp[0].replace("'","") + '.09')
    #             else:
    #                 new_index.append('20' + temp[0].replace("'","") + '.12')
    #     else:
    #         if temp[0] == '1Q':
    #             new_index.append(new_index[num-1].split('.')[0] + '.03')
    #         elif temp[0] == '2Q':
    #             new_index.append(new_index[num-1].split('.')[0] + '.06')
    #         elif temp[0] == '3Q':
    #             new_index.append(new_index[num-1].split('.')[0] + '.09')
    #         else:
    #             new_index.append(new_index[num-1].split('.')[0] + '.12')
    #구글 시트에서 가져오기 2022.11.09
    pir = kb_doc.worksheet('KBPIR')
    pir_values = pir.get_all_values()
    pir_header, pir_rows = pir_values[1:3], pir_values[3:]
    pir_df_org = pd.DataFrame(pir_rows, columns=pir_header)
    pir_df_org = pir_df_org.set_index(pir_df_org.iloc[:,0])
    pir_df_org.index.name = 'date'

    ###각 지역 pir만
    pir_df = pir_df_org.xs("KB아파트 PIR", axis=1, level=1)
    pir_df = pir_df.apply(lambda x:x.replace('','0').replace(',','')).astype(float)
    # pir_df.set_index(pd.to_datetime(new_index), inplace=True)
    ###가구소득
    income_df = pir_df_org.xs("가구소득(Income)", axis=1, level=1)
    income_df = income_df.apply(lambda x:x.replace('','0').replace(',','')).astype(int)
    # income_df.set_index(pd.to_datetime(new_index), inplace=True)
    ###주택가격
    house_df = pir_df_org.xs("주택가격(Price)", axis=1, level=1)
    house_df = house_df.apply(lambda x:x.replace('','0').replace(',','')).astype(int)
    # house_df.set_index(pd.to_datetime(new_index), inplace=True)
    # pir_df.index.name = '분기'
    # income_df.index.name = '분기'
    # house_df.index.name = '분기'

    return pir_df, income_df, house_df

@st.cache_data(ttl=datetime.timedelta(days=1))
def load_hai_data():
    # hai = kbm_dict.parse('14.NEW_HAI', skiprows=1)
    # hai_old = hai.iloc[:135,2:]
    # hai_old = hai_old.set_index("지역")
    # hai_old.index.name="날짜"
    # hai_new = hai.iloc[144:hai['전국 Total'].count()-17,2:] ### 159 3월까지::: 달 증가에 따른 +1
    # hai_new = hai_new.set_index("지역")
    # hai_new.index.name="날짜"
    # s1 = hai_new.columns.map(lambda x: x.split(' ')[0])
    # #index 날짜 변경
    # new_s1 = []
    # for num, gu_data in enumerate(s1):
    #     check = num
    #     if gu_data.startswith('Un'):
    #         new_s1.append(new_s1[check-1])
    #     else:
    #         new_s1.append(s1[check])
    # new_s1[-1] ='중위월소득'
    # new_s1[-2] ='대출금리'
    # hai_new.columns = [new_s1,hai_old.iloc[0]]
    # hai_index = list(hai_new.index)
    # #인덱스 날짜 변경
    # new_index = []

    # for num, raw_index in enumerate(hai_index):
    #     temp = str(raw_index).split('.')
    #     if len(temp[0]) == 3:
    #         if int(temp[0].replace("'","")) >84:
    #             new_index.append('19' + temp[0].replace("'","") + '.' + temp[1])
    #         else:
    #             new_index.append('20' + temp[0].replace("'","") + '.' + temp[1])
    #     else:
    #         new_index.append(new_index[num-1].split('.')[0] + '.' + temp[0])
    # hai_new.set_index(pd.to_datetime(new_index), inplace=True)
    #구글 시트에서 읽어오기
    hai = kb_doc.worksheet('KBHAI')
    hai_values = hai.get_all_values()
    hai_header, hai_rows = hai_values[1:3], hai_values[3:]
    hai_df = pd.DataFrame(hai_rows, columns=hai_header)
    hai_df = hai_df.set_index(hai_df.iloc[:,0])
    hai_df.iloc[:,:-2] = hai_df.iloc[:,:-2].apply(lambda x:x.replace('','0').replace(',','')).astype(float)
    hai_df.iloc[:,-1] = hai_df.iloc[:,-1].astype(str).apply(lambda x:x.replace(',','')).astype(int)
    hai_df = hai_df.iloc[:,1:]
    hai_df.index.name = 'date'
    ###각 지역 HAI만
    hai_apt = hai_df.xs("아파트", axis=1, level=1)
    # hai_apt.set_index(pd.to_datetime(new_index), inplace=True)
    ### 금리와 중위 소득만 가져오기
    info = hai_df.iloc[:,-2:]
    info.columns = ['주담대금리', '중위월소득']
    info.index.name="분기"
    info.loc[:,'중위월소득증감'] = info['중위월소득'].astype(int).pct_change()

    return hai_apt, info

@st.cache_data(ttl=datetime.timedelta(days=1))
def load_hoi():
    # 데이터 프레임 만들기
    hoi = kb_doc.worksheet('KBHOI')
    hoi_values = hoi.get_all_values()
    hoi_header, hoi_rows = hoi_values[1:3], hoi_values[3:]
    hoi_df = pd.DataFrame(hoi_rows, columns=hoi_header)
    hoi_df = hoi_df.set_index(hoi_df.iloc[:,0])
    hoi_df = hoi_df.iloc[:,1:]
    hoi_df.index.name = 'date'
    # 데이터 타입 변환
    hoi_df.iloc[:,:3] = hoi_df.iloc[:,:3].astype(float).round(decimals=2)
    hoi_df.iloc[:,3:12] = hoi_df.iloc[:,3:12].astype(str).apply(lambda x:x.str.replace(',','')).astype(int)
    hoi_df.iloc[:,12:] = hoi_df.iloc[:,12:].astype(float).round(decimals=2)

    return hoi_df

import re
def remove_giho(s):
    hangul = re.compile('[^ ㄱ-ㅣ가-힣+]') # 한글과 띄어쓰기를 제외한 모든 글자
    # hangul = re.compile('[^ \u3131-\u3163\uac00-\ud7a3]+')  # 위와 동일
    result = hangul.sub('', s) # 한글과 띄어쓰기를 제외한 모든 부분을 제거
    return result


if __name__ == "__main__":
    data_load_state = st.text('Loading index & pop Data...')
    index_list = load_index_data()
    mdf = index_list[0]
    jdf = index_list[1]
    #jratio_df = index_list[2]
    #odf, o_geo_data, last_odf, omdf, ojdf, omdf_change, ojdf_change, cum_omdf, cum_ojdf = load_one_data()
    oindex_list = load_one_data()
    omdf = oindex_list[0]
    ojdf = oindex_list[1]

    not_sell_list, in_df = get_not_sell_apt() #준공후 미분양
    not_sell_apt = not_sell_list[0]
    un_df = not_sell_list[1]
    #in_df = oindex_list[4]
    
    #un_df = one_dict.parse("not_sell", header=0,index_col=0, parse_dates=True) #미분양
    #매입자 거주지별 거래현황
    # in_df = one_dict.parse("apt_buy", header=0) 
    # bheader = pd.read_excel(header_path, sheet_name='buyer')
    # in_df['지 역'] = bheader['local'].str.strip()
    # in_df = in_df.rename({'지 역':'지역명'}, axis='columns')
    # in_df.drop(['Unnamed: 1', 'Unnamed: 2'], axis=1, inplace=True)
    # in_values = one_doc.worksheet('investor')
    # #데이터 프레임으로 읽기
    # basic_values = in_values.get_all_values()

    # basic_header, basic_rows = basic_values[0], basic_values[1:]
    # in_df1= pd.DataFrame(basic_rows, columns=basic_header)
    # in_df1 = in_df1.set_index(['local','매입자거주지'])
    # in_df = in_df1.T
    #=============== 여기까지 변경
    # in_df = in_df.set_index("지역명")
    # in_df = in_df.T
    # in_df.columns = [in_df.columns, in_df.iloc[0]]
    # in_df = in_df.iloc[1:]
    # in_df.index = in_df.index.map(lambda x: x.replace('년','-').replace(' ','').replace('월', '-01'))
    # in_df.index = in_df.index.map(lambda x: x.replace('년','-').replace(' ','').replace('월', ''))
    # in_df.index = pd.to_datetime(in_df.index)
    in_df = in_df.apply(lambda x: x.replace('-','0'))
    in_df = in_df.astype(int)

    #2022. 11. 10 수정 멀티 인덱스로 변경
    new_s1 = []
    new_s2 = []
    for num, city_name in enumerate(in_df.columns):
        new_s1.append(remove_giho(city_name.split(',')[0]).strip())
        new_s2.append(remove_giho(city_name.split(',')[1]).strip())
    in_df.columns = [new_s1,new_s2]
    
    total_df = in_df.xs('합계', axis=1, level=1)
    out_city = in_df.xs('관할시도외기타', axis=1, level=1)
    seoul_buyer = in_df.xs('관할시도외서울', axis=1, level=1)
    invest_total = out_city.add(seoul_buyer)
    #투자자비율 만들어보자
    in_ratio  = invest_total/total_df * 100
    in_ratio = in_ratio.round(2)
    seoul_ratio  = seoul_buyer/total_df * 100
    seoul_ratio = seoul_ratio.round(2)
    #마지막달
    last_in = pd.DataFrame()
    last_in['전체'] = total_df.iloc[-1].T.to_frame()
    last_in['외지인'] = invest_total.iloc[-1].T.to_frame()
    last_in['서울'] = seoul_buyer.iloc[-1].T.to_frame()
    last_in['서울%'] = seoul_ratio.iloc[-1].T.to_frame()
    last_in['외지인%'] = in_ratio.iloc[-1].T.to_frame()
    last_in['비율평균'] = in_ratio.mean()
    # 그 해 누적

    ### 여기까지 매입자 거주지별 

    data_load_state.text("index & pop Data Done! (using st.cache)")
    
    #마지막 달
    kb_last_month = pd.to_datetime(str(mdf.index.values[-1])).strftime('%Y.%m')
    one_last_month = pd.to_datetime(str(omdf.index.values[-1])).strftime('%Y.%m')
    af_last_month = pd.to_datetime(str(not_sell_apt.index.values[-1])).strftime('%Y.%m')
    un_last_month = pd.to_datetime(str(un_df.index.values[-1])).strftime('%Y.%m')
    in_last_month = pd.to_datetime(str(invest_total.index.values[-1])).strftime('%Y.%m')
    with st.expander("See recently Data Update"):
        cols = st.columns(3)
        cols[0].markdown(f'KB 최종업데이트: **{kb_last_month}월**')
        cols[1].markdown(f'부동산원 최종업데이트: **{one_last_month}월**')
        cols[2].markdown(f'투자자 최종업데이트: **{in_last_month}월**')
        cols = st.columns(3)
        cols[0].markdown(f'미분양 최종업데이트: **{un_last_month}월**')
        cols[1].markdown(f'준공후 미분양 최종업데이트: **{af_last_month}월**')
        cols[2].markdown('                      ')
    #월간 증감률
    mdf_change = mdf.pct_change()*100
    mdf_change = mdf_change.iloc[1:]
    
    mdf_change.replace([np.inf, -np.inf], np.nan, inplace=True)
    mdf_change = mdf_change.astype(float).fillna(0)
    # mdf = mdf.mask(np.isinf(mdf))
    jdf_change = jdf.pct_change()*100
    jdf_change = jdf_change.iloc[1:]
    
    jdf_change.replace([np.inf, -np.inf], np.nan, inplace=True)
    jdf_change = jdf_change.astype(float).fillna(0)
    cum_mdf = (1+mdf_change/100).cumprod() -1
    cum_mdf = cum_mdf.round(decimals=3)
    cum_jdf = (1+jdf_change/100).cumprod() -1
    cum_jdf = cum_jdf.round(decimals=3)
    #일주일 간 상승률 순위
    kb_last_df  = pd.DataFrame()
    kb_last_df['매매증감'] = mdf_change.iloc[-1].T.to_frame()
    kb_last_df['전세증감'] = jdf_change.iloc[-1].T.to_frame()
    kb_last_df['1w'] = mdf_change.iloc[-1].T.to_frame() 
    kb_last_df['2w'] = mdf_change.iloc[-2].T.to_frame()
    kb_last_df['3w'] = mdf_change.iloc[-3].T.to_frame()
    kb_last_df['1m'] = mdf_change.iloc[-4].T.to_frame()
    kb_last_df['1y'] = mdf_change.iloc[-51].T.to_frame()
#    kb_last_df.dropna(inplace=True)
    kb_last_df = kb_last_df.astype(float).fillna(0).round(decimals=2)
    #일주일 간 상승률 순위
    last_df = mdf_change.iloc[-1].T.to_frame()
    last_df['전세증감'] = jdf_change.iloc[-1].T.to_frame()
    last_df.columns = ['매매증감', '전세증감']
    last_df.dropna(inplace=True)
    last_df = last_df.round(decimals=2)

    ## 부동산원
     #주간 증감률
    omdf_change = omdf.pct_change()*100
    omdf_change = omdf_change.iloc[1:]
    omdf_change.replace([np.inf, -np.inf], np.nan, inplace=True)
    omdf_change = omdf_change.astype(float).fillna(0)
    ojdf_change = ojdf.pct_change()*100
    ojdf_change = ojdf_change.iloc[1:]
    ojdf_change.replace([np.inf, -np.inf], np.nan, inplace=True)
    ojdf_change = ojdf_change.astype(float).fillna(0)
    omdf_change = omdf_change.round(decimals=3)
    ojdf_change = ojdf_change.round(decimals=3)
    cum_omdf = (1+omdf_change/100).cumprod() -1
    cum_omdf = cum_omdf.round(decimals=3)
    cum_ojdf = (1+ojdf_change/100).cumprod() -1
    cum_ojdf = cum_ojdf.round(decimals=3)
    #일주일 간 상승률 순위
    last_odf = pd.DataFrame()
    last_odf['매매증감'] = omdf_change.iloc[-1].T.to_frame()
    last_odf['전세증감'] = ojdf_change.iloc[-1].T.to_frame()
    last_odf['1w'] = omdf_change.iloc[-1].T.to_frame()
    last_odf['2w'] = omdf_change.iloc[-2].T.to_frame()
    last_odf['3w'] = omdf_change.iloc[-3].T.to_frame()
    last_odf['1m'] = omdf_change.iloc[-4].T.to_frame()
    last_odf['1y'] = omdf_change.iloc[-51].T.to_frame()
    #last_odf.columns = ['매매증감', '전세증감', '2w', '3w', '1m', '1y']
    #last_odf.dropna(inplace=True)
    # last_odf = last_odf.astype(float).fillna(0).round(decimals=3)

    # #마지막달 dataframe에 지역 코드 넣어 합치기
    # df = pd.merge(last_df, code_df, how='inner', left_index=True, right_index=True)
    # df.columns = ['매매증감', '전세증감', 'SIG_CD']
    # df['SIG_CD']= df['SIG_CD'].astype(str)
    # df.reset_index(inplace=True)

    #버블 지수 만들어 보자
    #아기곰 방식:버블지수 =(관심지역매매가상승률-전국매매가상승률) - (관심지역전세가상승률-전국전세가상승률)
    bubble_df = mdf_change.subtract(mdf_change['전국'], axis=0)- jdf_change.subtract(jdf_change['전국'], axis=0)
    bubble_df = bubble_df*100
    
    #곰곰이 방식: 버블지수 = 매매가비율(관심지역매매가/전국평균매매가) - 전세가비율(관심지역전세가/전국평균전세가)
    bubble_df2 = mdf.div(mdf['전국'], axis=0) - jdf.div(jdf['전국'], axis=0)
    bubble_df2 = bubble_df2.astype(float).fillna(0).round(decimals=5)*100
    # st.dataframe(mdf)

    #전세 파워 만들기
    cum_ch = (mdf_change/100 +1).cumprod()-1
    jcum_ch = (jdf_change/100 +1).cumprod()-1
    m_power = (jcum_ch - cum_ch)*100
    m_power = m_power.astype(float).fillna(0).round(decimals=2)

    #마지막 데이터만 
    power_df = m_power.iloc[-1].T.to_frame()
    power_df['버블지수'] = bubble_df2.iloc[-1].T.to_frame()
    power_df.columns = ['전세파워', '버블지수']
    # power_df.dropna(inplace=True)
    power_df = power_df.astype(float).fillna(0).round(decimals=2)
    power_df['jrank'] = power_df['전세파워'].rank(ascending=False, method='min').round(1)
    power_df['brank'] = power_df['버블지수'].rank(ascending=True, method='min').round(decimals=1)
    power_df['score'] = power_df['jrank'] + power_df['brank']
    power_df['rank'] = power_df['score'].rank(ascending=True, method='min')
    power_df = power_df.sort_values('rank', ascending=True)

    
    #여기서부터는 선택
    my_choice = st.sidebar.radio(
                    "Select Menu", ('Basic','Price Index', '전세가율','PIR','HAI-HOI', 'Sentiment','투자자별매매동향', '지역같이보기', '기간보기')
                    )
    if my_choice == 'Basic':
        #st.subheader("전세파워 높고 버블지수 낮은 지역 상위 50곳")
        #st.dataframe(power_df.iloc[:50])
        period_ = omdf.index.strftime("%Y-%m").tolist()
        st.subheader("기간 지역 분석")
        start_date, end_date = st.select_slider(
            'Select Date to Compare index change', 
            options = period_,
            value = (period_[-24], period_[-1]))
        #information display
        #필요 날짜만 slice
        slice_om = omdf.loc[start_date:end_date]
        slice_oj = ojdf.loc[start_date:end_date]
        slice_m = mdf.loc[start_date:end_date]
        slice_j = jdf.loc[start_date:end_date]
        diff = slice_om.index[-1] - slice_om.index[0]
        cols = st.columns(4)
        cols[0].write(f"시작: {start_date}")
        cols[1].write(f"끝: {end_date}")
        cols[2].write(f"전체 기간: {round(diff.days/365,1)} 년")
        cols[3].write("")
        submit = st.sidebar.button('Analize Local situation')
        if submit:
            ### 매매지수 하락 전세지수 상승 #########################################################################################            
            #############
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
            inter_df = pd.merge(m_de, j_in, how='inner', left_index=True, right_index=True, suffixes=('m', 'j'))
            inter_odf = pd.merge(mo_de, jo_in, how='inner', left_index=True, right_index=True, suffixes=('m', 'j'))
            inter_kb_list = inter_df.index.to_list()
            
            if len(inter_kb_list) == 0:
                inter_kb_list.append("없음")
                #st.write(inter_kb_list[0])
            inter_one_list = inter_odf.index.to_list()
            with st.container():
                col1, col2, col3 = st.columns([30,2,30])
                with col1:
                    st.subheader("KB 매매지수 하락 전세지수 상승 지역")
                    st.dataframe(inter_df.style.background_gradient(cmap, axis=0)\
                                                .format(precision=2, na_rep='MISSING', thousands=","), 600, 500)
                with col2:
                    st.write("")
                with col3:
                    st.subheader("부동산원 매매지수 하락 전세지수 상승 지역")
                    st.dataframe(inter_odf.style.background_gradient(cmap, axis=0)\
                                                .format(precision=2, na_rep='MISSING', thousands=","),600,500)
            html_br="""
            <br>
            """
            st.markdown(html_br, unsafe_allow_html=True)
            ###
            ### 미분양 증가 하락 지역 #########################################################################################
            
            un_df.replace([np.inf, -np.inf], np.nan, inplace=True)
            un_df = un_df.astype(float).fillna(0)
            un_df = un_df.astype(int)
            #필요 날짜만 slice
            last_date = un_df.index[-1].strftime("%Y-%m")
            slice_un = un_df.loc[start_date:last_date]
            s_un = pd.DataFrame()
            un_de = pd.DataFrame()
            un_in = pd.DataFrame()
            s_un[start_date] = slice_un.iloc[0].T
            s_un[last_date] = slice_un.iloc[-1].T
            condition_un = s_un.iloc[:,0] <= s_un.iloc[:,-1]
            un_in = s_un.loc[condition_un]
            condition_un_de = s_un.iloc[:,0] > s_un.iloc[:,-1]
            un_de = s_un.loc[condition_un_de]
            un_in_final = un_in[un_in.iloc[:,1] != 0]
            un_in_list = un_in_final.index.to_list()
            un_de_list = un_de.index.to_list()
            #table styler 
            s = un_in_final.style.background_gradient(cmap, axis=0)\
                                                .format(na_rep='0', thousands=",")
            cell_hover = {  # for row hover use <tr> instead of <td>
                'selector': 'td:hover',
                'props': [('background-color', '#ffffb3')]
            }
            index_names = {
                'selector': '.index_name',
                'props': 'font-style: italic; color: darkgrey; font-weight:normal;'
            }
            headers = {
                'selector': 'th:not(.index_name)',
                'props': 'background-color: #000066; color: white;'
            }
            s.set_table_styles([cell_hover, index_names, headers])
            with st.container():
                col1, col2, col3 = st.columns([50,1,50])
                with col1:
                    st.subheader("미분양 증가 지역")
                    st.dataframe(s,350,500)
                with col2:
                    st.write("")
                with col3:
                    st.subheader("미분양 감소 지역")
                    st.dataframe(un_de.style.background_gradient(cmap, axis=0)\
                                                .format(na_rep='0', thousands=","), 350, 500)
            html_br="""
            <br>
            """
            st.markdown(html_br, unsafe_allow_html=True)
            ### 완공 후 미분양 증가 하락 지역 #########################################################################################
            #not_total = not_sell_apt.xs('소계', axis=1, level=1) 
            not_total = not_sell_apt.copy()
            #필요 날짜만 slice
            last_date_af = not_total.index[-1].strftime("%Y-%m")
            slice_af = not_total.loc[start_date:last_date_af]
            s_af = pd.DataFrame()
            af_de = pd.DataFrame()
            af_in = pd.DataFrame()
            s_af[start_date] = slice_af.iloc[0].T
            s_af[last_date_af] = slice_af.iloc[-1].T
            condition_af = s_af.iloc[:,0] <= s_af.iloc[:,-1]
            af_in = s_af.loc[condition_af]
            condition_af_de = s_af.iloc[:,0] > s_af.iloc[:,-1]
            af_de = s_af.loc[condition_af_de]
            af_in_final = af_in[af_in.iloc[:,1] != 0]
            af_in_list = af_in_final.index.to_list()
            af_de_list = af_de.index.to_list()
            with st.container():
                col1, col2, col3 = st.columns([30,2,30])
                with col1:
                    st.subheader("완공 후 미분양 증가 지역")
                    st.dataframe(af_in_final.style.background_gradient(cmap, axis=0)\
                                                .format(na_rep='0', thousands=","),350,500)
                with col2:
                    st.write("")
                with col3:
                    st.subheader("완공 후 미분양 감소 지역")
                    st.dataframe(af_de.style.background_gradient(cmap, axis=0)\
                                                .format(na_rep='0', thousands=","),350,500)
            html_br="""
            <br>
            """
            st.markdown(html_br, unsafe_allow_html=True)
            ### 매입자별 거주지별: 투자자 증감 ###################################################################################
            #필요 날짜만 slice
            slice_iv = invest_total.loc[start_date:end_date]
            s_iv = pd.DataFrame()
            iv_de = pd.DataFrame()
            iv_in = pd.DataFrame()
            s_iv[start_date] = slice_iv.iloc[0].T
            s_iv[end_date] = slice_iv.iloc[-1].T
            condition_iv = s_iv.iloc[:,0] <= s_iv.iloc[:,-1]
            iv_in = s_iv.loc[condition_iv]
            condition_iv_de = s_iv.iloc[:,0] > s_iv.iloc[:,-1]
            iv_de = s_iv.loc[condition_iv_de]
            iv_final = iv_in[iv_in.iloc[:,1] != 0].reset_index()
            iv_in_list = iv_final.index.to_list()
            iv_de_list = iv_de.index.to_list()
            with st.container():
                col1, col2, col3 = st.columns([30,2,30])
                with col1:
                    st.subheader("투자자 증가 지역")
                    st.dataframe(iv_final.style.background_gradient(cmap, axis=0)\
                                                .format(na_rep='0', thousands=","), 350, 500)
                with col2:
                    st.write("")
                with col3:
                    st.subheader("투자자 감소 지역")
                    st.dataframe(iv_de.style.background_gradient(cmap, axis=0)\
                                                .format(na_rep='0', thousands=","), 350, 500)
            html_br="""
            <br>
            """
            st.markdown(html_br, unsafe_allow_html=True)
            investor_df = last_in[last_in['외지인%'] >= last_in['비율평균']].reset_index()
            investor_ratio = last_in[last_in['외지인%'] >= 30.0].reset_index()
            with st.container():
                        col1, col2, col3 = st.columns([30,2,30])
                        with col1:
                            st.subheader("전체 평균 비율보다 투자자비율 높은 지역")
                            st.dataframe(investor_df.style.background_gradient(cmap, axis=0)\
                                                    .format(precision=1, na_rep='0', thousands=","), 600, 600)
                        with col2:
                            st.write("")
                        with col3:
                            st.subheader("내 마음대로 비율 살펴보기")
                            st.dataframe(investor_ratio.style.background_gradient(cmap, axis=0)\
                                                    .format(precision=1, na_rep='0', thousands=","), 600, 600)
            html_br="""
            <br>
            """
            st.markdown(html_br, unsafe_allow_html=True)
            ### 평균매매가격 증가 하락 지역 #########################################################################################
            #구글 시트에서 읽어 오기
            ## 구글 시트에서 읽어 오면 간단하지!!
            omp= one_doc.worksheet('omp')
            omp_values = omp.get_all_values()
            omp_header, omp_rows = omp_values[1], omp_values[2:]
            omp_df = pd.DataFrame(omp_rows, columns=omp_header)
            ojp= one_doc.worksheet('ojp')
            ojp_values = ojp.get_all_values()
            ojp_header, ojp_rows = ojp_values[1], ojp_values[2:]
            ojp_df = pd.DataFrame(ojp_rows, columns=ojp_header)

            #전세가율
            ora= one_doc.worksheet('oratio')
            ora_values = ora.get_all_values()
            ora_header, ora_rows = ora_values[1], ora_values[2:]
            rdf = pd.DataFrame(ora_rows, columns=ora_header)
            #컬럼 변경
            s1 = omp_df.columns
            new_s1 = []
            for num, gu_data in enumerate(s1):
                check = num
                if gu_data == '':
                    new_s1.append(new_s1[check-1])
                else:
                    new_s1.append(s1[check])
            #전세가율 컬럼
            s2 = rdf.columns
            new_s2 = []
            for num, gu_data in enumerate(s2):
                check = num
                if gu_data.startswith('Un'):
                    new_s2.append(new_s2[check-1])
                else:
                    new_s2.append(s2[check])
            
            omp_df.columns =[new_s1, omp_df.iloc[0]]
            omp_df = omp_df.iloc[1:]
            omp_df = omp_df.set_index(omp_df.iloc[:,0])
            omp_df = omp_df.iloc[:,1:]
            ojp_df.columns =[new_s1, ojp_df.iloc[0]]
            ojp_df = ojp_df.iloc[1:]
            ojp_df = ojp_df.set_index(ojp_df.iloc[:,0])
            ojp_df = ojp_df.iloc[:,1:]
            rdf.columns =[new_s2, rdf.iloc[0]]
            rdf = rdf.iloc[1:]
            rdf = rdf.set_index(rdf.iloc[:,0])
            rdf = rdf.iloc[:,1:]
            # omp_df.index = pd.to_datetime(omp_df.index)
            # ojp_df.index = pd.to_datetime(ojp_df.index)
            #rdf.index = pd.to_datetime(rdf.index)
            omp_df.index.name = 'date'
            omp_df = omp_df.astype(str).apply(lambda x: x.replace("","0")).astype(int)
            ojp_df.index.name = 'date'
            ojp_df = ojp_df.astype(str).apply(lambda x: x.replace("","0")).astype(int)
            rdf.index.name = 'date'
            rdf = rdf.astype(str).apply(lambda x: x.replace("","0")).astype(float)
            #기존 파일 시스템
            # omp_df = one_dict.parse("sell_price", header=1, index_col=0)
            # ojp_df = one_dict.parse("jeon_price", header=1, index_col=0)
            # r_df = one_dict.parse("ratio", header=1, index_col=0)
            # omp = omp_df.iloc[4:,:]
            # ojp = ojp_df.iloc[4:,:]
            # rdf = r_df.iloc[4:,:]
            #컬럼 변경
            # s1 = omp.columns
            # new_s1 = []
            # for num, gu_data in enumerate(s1):
            #     check = num
            #     if gu_data.startswith('Un'):
            #         new_s1.append(new_s1[check-1])
            #     else:
            #         new_s1.append(s1[check])
            # #전세가율은 다른가?
            # s2 = rdf.columns
            # new_s2 = []
            # for num, gu_data in enumerate(s2):
            #     check = num
            #     if gu_data.startswith('Un'):
            #         new_s2.append(new_s2[check-1])
            #     else:
            #         new_s2.append(s2[check])
            # omp.columns =[new_s1, omp_df.iloc[1]]
            # ojp.columns = [new_s1, ojp_df.iloc[1]]
            # rdf.columns =[new_s2, r_df.iloc[1]]
            header_dict = pd.read_excel(header_path, sheet_name=None)
            header = header_dict['one']
            #필요 시트만 슬라이스
            smdf = omp_df.xs('평균매매',axis=1, level=1)
            sadf = omp_df.xs('평균단위매매', axis=1, level=1)
            jmdf = ojp_df.xs('평균전세',axis=1, level=1)
            jadf = ojp_df.xs('평균단위전세', axis=1, level=1)
            m_df = rdf.xs('중위', axis=1, level=1) # 중위가격 전세가율
            a_df = rdf.xs('평균', axis=1, level=1) # 평균가격 전세가율
            smdf.columns = oneh.columns
            sadf.columns = oneh.columns
            jmdf.columns = oneh.columns
            jadf.columns = oneh.columns
            m_df.columns = oneh.columns
            a_df.columns = oneh.columns

            sadf = (sadf.astype(float)*3.306)/10
            smdf = smdf.astype(float)/10
            jadf = (jadf.astype(float)*3.306)/10
            jmdf = jmdf.astype(float)/10

            sadf = sadf.astype(float).round(decimals=0) #평균매매가
            smdf = smdf.astype(float).round(decimals=0) #
            jadf = jadf.astype(float).round(decimals=0)
            jmdf = jmdf.astype(float).round(decimals=0)
            m_df = m_df.round(decimals=1)
            a_df = a_df.round(decimals=1)
            #평균 가격으로 필요 날짜만 slice
            smdf.index = pd.to_datetime(smdf.index, format='%Y-%m-%d')
            last_date = smdf.index[-1].strftime("%Y-%m")
            slice_pr = smdf.loc[start_date:last_date]
            s_pr = pd.DataFrame()
            pr_de = pd.DataFrame()
            pr_in = pd.DataFrame()
            s_pr[start_date] = slice_pr.iloc[0].T
            s_pr[last_date] = slice_pr.iloc[-1].T
            condition_pr = s_pr.iloc[:,0] <= s_pr.iloc[:,-1]
            pr_in = s_pr.loc[condition_pr]
            condition_pr_de = s_pr.iloc[:,0] > s_pr.iloc[:,-1]
            pr_de = s_pr.loc[condition_pr_de]
            pr_de_list = pr_de.index.to_list()
            pr_in_list = pr_in.index.to_list()
            with st.container():
                col1, col2, col3 = st.columns([30,2,30])
                with col1:
                    st.subheader("평균 매매가격 증가 지역")
                    st.dataframe(pr_in.style.background_gradient(cmap, axis=0)\
                                                .format(precision=0, na_rep='0', thousands=","), 350, 500)
                with col2:
                    st.write("")
                with col3:
                    st.subheader("평균 매매가격 감소 지역")
                    st.dataframe(pr_de.style.background_gradient(cmap, axis=0)\
                                                .format(precision=0, na_rep='0', thousands=","), 350, 500)
            html_br="""
            <br>
            """
            st.markdown(html_br, unsafe_allow_html=True)
            ### 평균 전세 가격 증가 하락 지역 #########################################################################################
            jmdf.index = pd.to_datetime(jmdf.index, format='%Y-%m-%d')
            last_date = jmdf.index[-1].strftime("%Y-%m")
            slice_jpr = jmdf.loc[start_date:last_date]
            s_jpr = pd.DataFrame()
            jpr_de = pd.DataFrame()
            jpr_in = pd.DataFrame()
            s_jpr[start_date] = slice_jpr.iloc[0].T
            s_jpr[last_date] = slice_jpr.iloc[-1].T
            condition_jpr = s_jpr.iloc[:,0] <= s_jpr.iloc[:,-1]
            jpr_in = s_jpr.loc[condition_jpr]
            condition_jpr_de = s_jpr.iloc[:,0] > s_jpr.iloc[:,-1]
            jpr_de = s_jpr.loc[condition_jpr_de]
            jpr_de_list = jpr_de.index.to_list()
            jpr_in_list = jpr_in.index.to_list()
            with st.container():
                col1, col2, col3 = st.columns([30,2,30])
                with col1:
                    st.subheader("평균 전세가격 증가 지역")
                    st.dataframe(jpr_in.style.background_gradient(cmap, axis=0)\
                                                .format(precision=0, na_rep='0', thousands=","), 350, 350)
                with col2:
                    st.write("")
                with col3:
                    st.subheader("평균 전세가격 감소 지역")
                    st.dataframe(jpr_de.style.background_gradient(cmap, axis=0)\
                                                .format(precision=0, na_rep='0', thousands=","), 350, 350)
            html_br="""
            <br>
            """
            st.markdown(html_br, unsafe_allow_html=True)
            ### 전세가율 증가 하락 지역 #########################################################################################
            a_df.index = pd.to_datetime(a_df.index, format='%Y-%m-%d')
            last_date = a_df.index[-1].strftime("%Y-%m")
            slice_jr = a_df.loc[start_date:last_date]
            s_jr = pd.DataFrame()
            jr_de = pd.DataFrame()
            jr_in = pd.DataFrame()
            s_jr[start_date] = slice_jr.iloc[0].T
            s_jr[last_date] = slice_jr.iloc[-1].T
            condition_jr = s_jr.iloc[:,0] <= s_jr.iloc[:,-1]
            jr_in = s_jr.loc[condition_jr]
            condition_jr_de = s_jr.iloc[:,0] > s_jr.iloc[:,-1]
            jr_de = s_jr.loc[condition_jr_de]
            jr_in = jr_in.astype(float).round(decimals=1)
            jr_de = jr_de.astype(float).round(decimals=1)
            jr_de_list = jr_de.index.to_list()
            jr_in_list = jr_in.index.to_list()
            with st.container():
                    col1, col2, col3 = st.columns([30,2,30])
                    with col1:
                        st.subheader("전세가율 증가 지역")
                        st.dataframe(jr_in.style.background_gradient(cmap, axis=0)\
                                                .format(precision=1, na_rep='0', thousands=","), 350, 350)
                    with col2:
                        st.write("")
                    with col3:
                        st.subheader("전세가율 감소 지역")
                        st.dataframe(jr_de.style.background_gradient(cmap, axis=0)\
                                                .format(precision=1, na_rep='0', thousands=","), 350, 350)
            html_br="""
            <br>
            """
            st.markdown(html_br, unsafe_allow_html=True)
            ######## 하략 지역 데이터프레임 ####################################################################################
            down_index_name = ['KB지수', 'one지수', '미분양증가', '준공후미분양증가', '투자자증가', '투자자감소', '평균매매가격감소', '평균전세가격증가', '전세가율증가']
            de_citys = np.array([', '.join(inter_kb_list), ', '.join(inter_one_list), ', '.join(un_in_list), ', '.join(af_in_list), ', '.join(iv_in_list), \
                 ', '.join(iv_de_list), ', '.join(pr_de_list), ', '.join(jpr_in_list), ', '.join(jr_in_list)])
            down_df = pd.DataFrame(de_citys, down_index_name)
            with st.container():
                    col1, col2, col3 = st.columns([30,2,30])
                    with col1:
                        st.subheader("하락 지표 나타나는 지역")
                        st.table(down_df)
                    with col2:
                        st.write("")
                    with col3:
                        st.write("")
                        #버블지수/전세파워 table 추가
                        title = dict(text=f'<b> 하락 지표 나타나는 지역</b>', x=0.5, y = 0.9) 
                        fig = go.Figure(data=[go.Table(
                                            columnorder = [1,2],
                                            columnwidth = [80,400],
                                            header=dict(values=['<b>항목</b>','<b>지역</b>'],
                                                        fill_color='royalblue',
                                                        align=['right','left'],
                                                        font=dict(color='white', size=12),
                                                        height=40),
                                            cells=dict(values=[down_df.index, down_df.iloc[:,0]], 
                                                        fill=dict(color=['black', 'gray']),
                                                        align=['right','left'],
                                                        font_size=12,
                                                        height=30))
                                        ])
                        fig.update_layout(title = title, titlefont_size=15, legend=dict(orientation="h"), template="ggplot2")
                        st.plotly_chart(fig)
            html_br="""
            <br>
            """
             ######## 상승 지역 데이터프레임 ####################################################################################
            up_index_name = ['KB지수', 'one지수', '미분양감소', '준공후미분양감소', '투자자증가', '투자자감소', '평균매매가격증가', '평균전세가격감소', '전세가율감소']
            in_citys = np.array([', '.join(inter_kb_list), ', '.join(inter_one_list), ', '.join(un_de_list), ', '.join(af_de_list), ', '.join(iv_in_list), \
                 ', '.join(iv_de_list), ', '.join(pr_in_list), ', '.join(jpr_de_list), ', '.join(jr_de_list)])
            in_df = pd.DataFrame(in_citys, up_index_name)
            with st.container():
                    col1, col2, col3 = st.columns([30,2,30])
                    with col1:
                        st.subheader("상승 지표 나타나는 지역")
                        st.table(in_df)
                    with col2:
                        st.write("")
                    with col3:
                        st.write("")
                        #버블지수/전세파워 table 추가
                        title = dict(text=f'<b> 상승 지표 나타나는 지역</b>', x=0.5, y = 0.9) 
                        fig = go.Figure(data=[go.Table(
                                            columnorder = [1,2],
                                            columnwidth = [80,400],
                                            header=dict(values=['<b>항목</b>','<b>지역</b>'],
                                                        fill_color='royalblue',
                                                        align=['right','left'],
                                                        font=dict(color='white', size=12),
                                                        height=40),
                                            cells=dict(values=[in_df.index, in_df.iloc[:,0]], 
                                                        fill=dict(color=['black', 'gray']),
                                                        align=['right','left'],
                                                        font_size=12,
                                                        height=30))
                                        ])
                        fig.update_layout(title = title, titlefont_size=15, legend=dict(orientation="h"), template="ggplot2")
                        st.plotly_chart(fig)
            html_br="""
            <br>
            """
######## 여기까지###################################################################################
    elif my_choice == 'Price Index':
        city_list = ['전국', '수도권', '지방', '6대광역시', '5대광역시', '서울', '경기', '부산', '대구', '인천', '광주', '대전',
                  '울산', '세종', '강원', '충북', '충남', '전북', '전남', '경북', '경남', '제주도']
        column_list = mdf.columns.to_list()
        city_series = pd.Series(column_list)
        selected_dosi = st.sidebar.selectbox(
                '광역시-도', city_list
            )

        #두번째 도시
        small_list = []
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
        mirco_list = []
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
        
        submit = st.sidebar.button('Draw Price Index')

        if submit:
            ### Block KB 지수 #########################################################################################
            with st.container():
                col1, col2, col3 = st.columns([30,2,30])
                with col1:
                    flag = "KB"
                    drawAPT_update.run_price_index(selected_dosi2, selected_dosi3, mdf, jdf, mdf_change, jdf_change, flag)
                with col2:
                    st.write("")
                with col3:
                    flag = "KB"
                    drawAPT_update.draw_flower(selected_dosi2, selected_dosi3, cum_mdf, cum_jdf, flag)
            html_br="""
            <br>
            """
            st.markdown(html_br, unsafe_allow_html=True)
            ### Block 부동산원 지수 #########################################################################################
            with st.container():
                col1, col2, col3 = st.columns([30,2,30])
                with col1:
                    flag = "부동산원"
                    drawAPT_update.run_price_index(selected_dosi2, selected_dosi3, omdf, jdf, mdf_change, jdf_change, flag)
                with col2:
                    st.write("")
                with col3:
                    flag = "부동산원"
                    drawAPT_update.draw_flower(selected_dosi2, selected_dosi3, cum_omdf, cum_ojdf, flag)
            html_br="""
            <br>
            """
            st.markdown(html_br, unsafe_allow_html=True)
    elif my_choice == '전세가율':
        st.subheader("전국 매매전세가 비율")
        jratio_df = load_ratio_data()
        #마지막 행만 가져오기
        rlast_df = pd.DataFrame()
        rlast_df['전세가율'] = jratio_df.iloc[-1].T.to_frame()
        rlast_df = rlast_df.reset_index()
        rlast_df = rlast_df.rename(columns={'index': '시군구코드'})
        rlast_df['시군구코드'] = rlast_df['시군구코드'].astype(int)
        r_df = pd.merge(rlast_df, citys, how='inner', left_on='시군구코드', right_on='code')
        
        tab1, tab2 = st.tabs(["⏰ 비율보기", "🗺️ 지도로 보기"])
        with tab1:
            ratio_value = st.slider(
                'Select ratio to Compare index change', 0, 100, 50)
            r_50 = rlast_df[rlast_df['전세가율'] >= 70.0]
            r_user = rlast_df[rlast_df['전세가율'] >= ratio_value]
            with st.container():
                        col1, col2, col3 = st.columns([30,2,30])
                        with col1:
                            st.subheader("전세가율이 50% 이상인 지역")
                            st.dataframe(r_50.style.background_gradient(cmap, axis=0)\
                                                    .format(precision=1, na_rep='MISSING', thousands=","), 600, 600)
                        with col2:
                            st.write("")
                        with col3:
                            st.subheader("내 마음대로 비율 살펴보기")
                            st.dataframe(r_user.style.background_gradient(cmap, axis=0)\
                                                    .format(precision=1, na_rep='MISSING', thousands=","), 600, 600)
            html_br="""
            <br>
            """
            st.markdown(html_br, unsafe_allow_html=True)  
        with tab2:
            with urlopen(geo_source) as response:
                kb_geo_data = json.load(response)
                
            #geojson file 변경
            for idx, sigun_dict in enumerate(kb_geo_data['features']):
                sigun_id = sigun_dict['properties']['SIG_CD']
                sigun_name = sigun_dict['properties']['SIG_KOR_NM']
                try:
                    sell_change = r_df.loc[(r_df.code == sigun_id), '전세가율'].iloc[0]
                except:
                    sell_change = 0
                    jeon_change =0
                # continue
                
                txt = f'<b><h4>{sigun_name}</h4></b>전세가율: {sell_change:.2f}<br>'
                # print(txt)
                
                kb_geo_data['features'][idx]['id'] = sigun_id
                kb_geo_data['features'][idx]['properties']['sell_change'] = sell_change
                kb_geo_data['features'][idx]['properties']['tooltip'] = txt

            kb_last_m = pd.to_datetime(str(jratio_df.index.values[-1])).strftime('%Y.%m')

            drawAPT_update.draw_ratio_Choroplethmapbox(r_df, kb_geo_data, kb_last_m)
    elif my_choice == 'PIR':
        data_load_state = st.text('Loading PIR index Data...')
        pir_df, income_df, price_df = load_pir_data()
        pir_df = pir_df.astype(float).fillna(0).round(decimals=2)
        data_load_state.text("PIR index Data Done! (using st.cache)")
        st.subheader("PIR(Price to income ratio)= 주택가격/가구소득")
        st.write("  - 가구소득은 분기단위 해당 지역 내 KB국민은행 부동산담보대출(아파트) 대출자의 연소득 중위값임")
        st.write("  - 주택가격은 분기단위 해당 지역 내 KB국민은행 부동산담보대출(아파트) 실행시 조사된 담보평가 가격의 중위값임")
        st.write("* KB 아파트 PIR은 KB국민은행에서 실행된 아파트 담보대출(구입자금대출) 중 실제 거래된 아파트 거래가격과 해당 여신거래자의 가계소득 자료를 기반으로 작성된 지수로 기존 당행에서 발표중인 PIR지수의 보조지표로 활용할 수 있음. ")
        st.write("* 발표시기 : 해당분기 익익월 보고서 발표(예 / 1분기 자료 ⇒ 5월 보고서 )")
        
        city_list = ['서울', '경기', '인천']
        selected_city = st.sidebar.selectbox(
                '수도권', city_list
            )
        submit = st.sidebar.button('Draw PIR chart')
        if submit:
            drawAPT_update.draw_pir(selected_city, pir_df, income_df, price_df)
    elif my_choice == 'HAI-HOI':
        data_load_state = st.text('Loading HAI index Data...')
        hai_df, info_df = load_hai_data()
        hoi_df = load_hoi()
        hai_df = hai_df.astype(float).fillna(0).round(decimals=2)
        info_df = info_df.astype(float).fillna(0).round(decimals=2)
        data_load_state.text("HAI index Data Done! (using st.cache)")
        st.subheader("KB 주택구매력지수(HAI): Housing affordability index")
        st.write("* HAI = (중위가구소득 ÷ 대출상환가능소득) ×100 ")
        st.write("* 주택구매력지수란 우리나라에서 중간정도의 소득을 가진 가구가 금융기관의 대출을 받아 중간가격 정도의 주택을 구입한다고 가정할 때, \
            현재의 소득으로 대출원리금상환에 필요한 금액을 부담할 수 있는 능력을 의미")
        st.write("* HAI가 100보다 클수록 중간정도의 소득을 가진 가구가 중간가격 정도의 주택을 큰 무리없이 구입할 수 있다는 것을 나타내며, HAI가 상승하면 주택구매력이 증가한다는 것을 의미")
        st.write("* 발표시기 : 해당분기 익익월 보고서 발표(예 / 1분기 자료 ⇒ 5월 보고서 )")

        st.subheader("KB주택구입 잠재력지수(KB-HOI)  KB Housing Opportunity Index")
        st.write("*  HOI = (구입가능 재고량 ÷ 총재고량) ×100 ")
        st.write("   HTI = 33% (Housing Cost To Income Ratio: 소득대비 주거비용비율)")
        st.write("   주택구입자금 밑천(Down Payment)=30%, 20년 만기 원리금상환 기준")
        st.write("* 주택구입잠재력지수란 중위 소득의 가구가 금융기관의 대출을 받아 주택을 구입한다고 가정할 경우,   \
            지역 내 주택 중 경제능력(소득, 자산 등)의 제약 속에서 구입 가능한 주택 재고량을 알 수 있는 지표임.")
        st.write("*즉, KB-HOI 지수가 50이면 해당지역 내 주택 재고수의 가격별 하위 50%범위 내 주택을 구입할 수 있음을 나타내며, KB-HOI지수가 상승하면 주택구입능력(잠재력)이 증가한다는 것을 뜻함")
        st.write("* 발표시기 : 해당분기 익익월 보고서 발표(예 / 1분기 자료 ⇒ 5월 보고서 )")

        city_list = hai_df.columns.to_list()
        selected_city = st.sidebar.selectbox(
                '지역', city_list
            )
        submit = st.sidebar.button('Draw HAI-HOI chart')
        if submit:
            drawAPT_update.draw_hai(selected_city, hai_df, info_df)
            drawAPT_update.draw_hoi(hoi_df)
    elif my_choice == 'Sentiment' :
        data_load_state = st.text('Loading Sentimental index Data...')
        senti_dfs, df_as, df_bs = load_senti_data()
        data_load_state.text("Sentimental index Data Done! (using st.cache)")
        city_list = senti_dfs[0].columns.to_list()
        
        selected_dosi = st.sidebar.selectbox(
                '광역시-도', city_list
            )
        submit = st.sidebar.button('Draw Sentimental Index chart')
        if submit:
            #drawAPT_update.draw_sentimental_index(selected_dosi, senti_dfs, df_as, df_bs, mdf_change)
            ### Block 매수우위/매매증감#########################################################################################
            with st.container():
                col1, col2, col3 = st.columns([30,2,30])
                with col1:
                    drawAPT_update.draw_sentimental_index(selected_dosi, senti_dfs, df_as, df_bs, mdf_change)
                with col2:
                    st.write("")
                with col3:
                    drawAPT_update.draw_ds_change(selected_dosi, senti_dfs, mdf_change)
            html_br="""
            <br>
            """
            st.markdown(html_br, unsafe_allow_html=True)
            ### Block 전세수급/전세증감#########################################################################################
            with st.container():
                col1, col2, col3 = st.columns([30,2,30])
                with col1:
                    drawAPT_update.draw_jsentimental_index(selected_dosi, senti_dfs, df_as, df_bs, jdf_change)
                with col2:
                    st.write("")
                with col3:
                    #수정
                    drawAPT_update.draw_jds_change(selected_dosi, senti_dfs, jdf_change)
            html_br="""
            <br>
            """
            st.markdown(html_br, unsafe_allow_html=True)
            ### Block 수요공급 비중 #########################################################################################
            with st.container():
                col1, col2, col3 = st.columns([30,2,30])
                with col1:
                    drawAPT_update.draw_desu_sentiment(selected_dosi, df_as, df_bs, mdf, jdf)
                with col2:
                    st.write("")
                with col3:
                    st.write("")
            html_br="""
            <br>
            """
            st.markdown(html_br, unsafe_allow_html=True)
    elif my_choice == '지역같이보기': #KB는 자체적으로 볼때, 지역 같이 볼 때는 부동산원만 
        #기간
        period_ = mdf.index.strftime("%Y-%m").tolist()
        st.subheader("기간 상승률 분석")
        start_date, end_date = st.select_slider(
            'Select Date to Compare index change', 
            options = period_,
            value = (period_[-13], period_[-1]))
        
        #부동산원 / KB
        slice_om = omdf.loc[start_date:end_date]
        slice_oj = ojdf.loc[start_date:end_date]
        slice_m = mdf.loc[start_date:end_date]
        slice_j = jdf.loc[start_date:end_date]
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
        #상승률 누적
        slice_om = omdf.loc[start_date:end_date]
        slice_oj = ojdf.loc[start_date:end_date]
        slice_om_ch = omdf_change.loc[start_date:end_date]
        slice_oj_ch = ojdf_change.loc[start_date:end_date]
        slice_om_ch = slice_om_ch.round(decimals=2)
        slice_oj_ch = slice_oj_ch.round(decimals=2)
        slice_cum_omdf = (1+slice_om_ch/100).cumprod() -1
        slice_cum_omdf = slice_cum_omdf.round(decimals=4)
        slice_cum_ojdf = (1+slice_oj_ch/100).cumprod() -1
        slice_cum_ojdf = slice_cum_ojdf.round(decimals=4)

        slice_m = mdf.loc[start_date:end_date]
        slice_j = jdf.loc[start_date:end_date]
        slice_m_ch = mdf_change.loc[start_date:end_date]
        slice_j_ch = jdf_change.loc[start_date:end_date]
        slice_m_ch = slice_m_ch.round(decimals=2)
        slice_j_ch = slice_j_ch.round(decimals=2)
        slice_cum_mdf = (1+slice_m_ch/100).cumprod() -1
        slice_cum_mdf = slice_cum_mdf.round(decimals=4)
        slice_cum_jdf = (1+slice_j_ch/100).cumprod() -1
        slice_cum_jdf = slice_cum_jdf.round(decimals=4)


        #지역 같이 
        citys = omdf.columns.tolist()
        options = st.multiselect('Select City to Compare index', citys, citys[:3])
        submit = st.button('analysis')
        if submit:
            ### 부동산원 index chart #########################################################################################
            with st.container():
                col1, col2, col3 = st.columns([30,2,30])
                with col1:
                    flag = '부동산원 월간'
                    drawAPT_weekly.run_one_index_together(options, slice_om, slice_om_ch, flag)

                with col2:
                    st.write("")
                with col3:
                    flag = '부동산원 월간'
                    drawAPT_weekly.run_one_jindex_together(options, slice_oj, slice_oj_ch, flag)
                    
            html_br="""
            <br>
            """ 
            ### KB index chart #########################################################################################
            # with st.container():
            #     col1, col2, col3 = st.columns([30,2,30])
            #     with col1:
            #         flag = 'KB 월간'
            #         drawAPT_weekly.run_one_index_together(options, slice_m, slice_m_ch, flag)

            #     with col2:
            #         st.write("")
            #     with col3:
            #         flag = 'KB 월간'
            #         drawAPT_weekly.run_one_jindex_together(options, slice_j, slice_j_ch, flag)
                    
            # html_br="""
            # <br>
            # """ 
            ### 부동산원 Bubble/ flower chart #########################################################################################
            with st.container():
                col1, col2, col3 = st.columns([30,2,30])
                with col1:
                    flag = '부동산원 월간'
                    drawAPT_weekly.draw_index_change_with_bubble_slice(options, change_odf, flag)

                with col2:
                    st.write("")
                with col3:
                    flag = '부동산원 월간'
                    drawAPT_weekly.draw_flower_together(options, slice_cum_omdf, slice_cum_ojdf, flag)
                    
            html_br="""
            <br>
            """             
            ### KB Bubble/ flower chart #########################################################################################
            # with st.container():
            #     col1, col2, col3 = st.columns([30,2,30])
            #     with col1:
            #         flag = 'KB 월간'
            #         drawAPT_weekly.draw_index_change_with_bubble_slice(options, change_df, flag)

            #     with col2:
            #         st.write("")
            #     with col3:
            #         flag = 'KB 월간'
            #         drawAPT_weekly.draw_flower_together(options, slice_cum_mdf, slice_cum_jdf, flag)
                    
            # html_br="""
            # <br>
            # """               
    elif my_choice == '투자자별매매동향':
        st.subheader("외지인 비율 분석")
        ratio_value = st.slider(
            'Select ratio to Compare index change', 0, 100, 30)
        investor_df = last_in[last_in['외지인%'] >= last_in['비율평균']].reset_index()
        investor_ratio = last_in[last_in['외지인%'] >= ratio_value].reset_index()
        with st.container():
                    col1, col2, col3 = st.columns([30,2,30])
                    with col1:
                        st.subheader("전체 평균 비율보다 투자자비율 높은 지역")
                        st.dataframe(investor_df.style.background_gradient(cmap, axis=0)\
                                                .format(precision=1, na_rep='MISSING', thousands=","), 600, 600)
                    with col2:
                        st.write("")
                    with col3:
                        st.subheader("내 마음대로 비율 살펴보기")
                        st.dataframe(investor_ratio.style.background_gradient(cmap, axis=0)\
                                                .format(precision=1, na_rep='MISSING', thousands=","), 600, 600)
        html_br="""
        <br>
        """
        st.markdown(html_br, unsafe_allow_html=True)
                       
    else:
        period_ = omdf.index.strftime("%Y-%m").tolist()
        st.subheader("기간 상승률 분석")
        start_date, end_date = st.select_slider(
            'Select Date to Compare index change', 
            options = period_,
            value = (period_[-13], period_[-1]))
        
        #부동산원 / KB
        slice_om = omdf.loc[start_date:end_date]
        slice_oj = ojdf.loc[start_date:end_date]
        slice_m = mdf.loc[start_date:end_date]
        slice_j = jdf.loc[start_date:end_date]
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
            ### Draw Bubble chart #########################################################################################
            with st.container():
                col1, col2, col3 = st.columns([30,2,30])
                with col1:
                    flag = 'KB 월간'
                    drawAPT_weekly.draw_index_change_with_bubble(change_df, flag)

                with col2:
                    st.write("")
                with col3:
                    flag = '부동산원 월간'
                    drawAPT_weekly.draw_index_change_with_bubble(change_odf, flag)
                    
            html_br="""
            <br>
            """
             ### Draw Bubble chart #########################################################################################
            with st.container():
                col1, col2, col3 = st.columns([30,2,30])
                with col1:
                    st.write("KB 기간 증감") 
                    change_df = change_df.reset_index()            
                    st.dataframe(change_df.style.background_gradient(cmap, axis=0)\
                                    .format(precision=2, na_rep='MISSING', thousands=","))  
                    #drawAPT_weekly.draw_change_table(change_df, flag)  
                with col2:
                    st.write("")
                with col3:
                    st.write("부동산원 기간 증감")
                    change_odf = change_odf.reset_index()
                    st.dataframe(change_odf.style.background_gradient(cmap, axis=0)\
                                          .format(precision=2, na_rep='MISSING', thousands=","))
                    #drawAPT_weekly.draw_change_table(change_df, flag) 
            html_br="""
            <br>
            """
html_br="""
<br>
"""

html_line="""

<br>
<br>
<br>
<br>
<hr style= "  display: block;
  margin-top: 0.5em;
  margin-bottom: 0.5em;
  margin-left: auto;
  margin-right: auto;
  border-style: inset;
  border-width: 1.5px;">
<p style="color:Gainsboro; text-align: right;">By: 기하급수적 https://blog.naver.com/indiesoul2 / sizipusx2@gmail.com</p>
"""
st.markdown(html_line, unsafe_allow_html=True)
