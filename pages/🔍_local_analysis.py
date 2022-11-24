import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import streamlit as st
import pandas as pd
import numpy as np
import sqlite3

import drawAPT_update
import requests
from urllib.request import urlopen
import json
from pandas.io.json import json_normalize

import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials

#############html 영역####################
html_header="""
<head>
<title>PControlDB</title>
<meta charset="utf-8">
<meta name="keywords" content="project control, dashboard, management, EVA">
<meta name="description" content="project control dashboard">
<meta name="author" content="indiesoul">
<meta name="viewport" content="width=device-width, initial-scale=1">
</head>
 <h2 style="color:#008080; font-family:Georgia"> 🌆 지역분석 🔍 </h3> <br>
 <hr style= "  display: block;
  margin-top: 0.5em;
  margin-bottom: 0.5em;
  margin-left: auto;
  margin-right: auto;
  border-style: inset;
  border-width: 1.5px;"></h1>
"""

st.set_page_config(page_title="House Analysis Dashboard", page_icon="", layout="wide")
st.markdown('<style>body{background-color: #fbfff0}</style>',unsafe_allow_html=True)
st.markdown(html_header, unsafe_allow_html=True)
st.markdown(""" <style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style> """, unsafe_allow_html=True)
# data=pd.read_excel('curva.xlsx')

#############################2022.10.09 sqlite3로 변경######################################
one_db_path = "files/one_monthly.db"
kb_db_path = "files/kb_monthly.db"

def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by the db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Exception as e:
       print(e)

    return conn

### 구글 시트로 소스 변경: 2022.7.21 #########
#부동사원 gsheet
scope = [
    'https://spreadsheets.google.com/feeds',
    'https://www.googleapis.com/auth/drive',
    ]

json_file_name = 'files/weekly-house-db-ac0a43b61ddd.json'

credentials = ServiceAccountCredentials.from_json_keyfile_name(json_file_name, scope)
gc = gspread.authorize(credentials)

one_gsheet_url = r'https://docs.google.com/spreadsheets/d/1_Sr5uA-rDyJnHgVu_pHMkmavuQC7VpuYpVmnBaNRX8M/edit?usp=sharing'
kb_gsheet_url = r'https://docs.google.com/spreadsheets/d/168K8mcybxQfufMi39wnH5agmMrkK9C8ac57MajmOawI/edit?usp=sharing'
basic_url = r'https://docs.google.com/spreadsheets/d/1s5sS6K7YpbwKJBofHKEl8WsbUDJ0acmrOuw6YN8YZhw/edit?usp=sharing'

one_doc = gc.open_by_url(one_gsheet_url)
kb_doc = gc.open_by_url(kb_gsheet_url)
#인구, 세대수, 기본 소득
bs_doc = gc.open_by_url(basic_url)

### data 가져오기 영역 ##########################
#매주 지역별 시황
local_path = 'https://github.com/sizipusx/fundamental/blob/f98e2a2ec4a9e1bcb7bbf927f8b39419aa738329/files/local_issue.xlsx?raw=true'
#매월 데이타
file_path = 'https://github.com/sizipusx/fundamental/blob/72f1e05a7f8b50d98921e4e6aa621d6cd12ae483/files/kb_monthly.xlsx?raw=true'
one_path = r'https://github.com/sizipusx/fundamental/blob/4be5dc1d6f0af60b711a2fd0f9917c1620acbcf0/files/one_data.xlsx?raw=true'
#buy_path = r'https://github.com/sizipusx/fundamental/blob/669cd865342b20c29da4ff689a309fe5edc24f38/files/apt_buy.xlsx?raw=true'
# 2021. 11월부터 KB 데이터에서 기타지방 평균가격 제공하지 않음 => 다시 부동산원 데이터로 변경: 2021. 12. 16
#p_path = r"https://github.com/sizipusx/fundamental/blob/85abf3c89fd35256caa84d3d216208408634686f/files/kb_price.xlsx?raw=True"
p_path = r"https://github.com/sizipusx/fundamental/blob/bad11c793466a1fca828a13e03ad47acf4fe5738/files/one_apt_price.xlsx?raw=true"
pop_path = r"https://github.com/sizipusx/fundamental/blob/e946e69f2d27b84df736fecaf92b49d2089af0f9/files/pop.xlsx?raw=True"
#not_sell_path = 'https://github.com/sizipusx/fundamental/blob/8f2753b1fd827ced9fd20e11e6355756b6954657/files/not_selling_apt.xlsx?raw=true'
#년단위
basic_path = 'https://github.com/sizipusx/fundamental/blob/2f2d6225b1ec3b1c80d26b7169d5d026bc784494/files/local_basic.xlsx?raw=True'
#상시 : 평단가 업데이트로 header 업데이트 2021. 12. 16
header_path = 'https://github.com/sizipusx/fundamental/blob/c21edec8ce54a4528eaa2d711fcf096fd7105b01/files/header.xlsx?raw=True'



def read_source(): 
    # file_path = 'https://github.com/sizipusx/fundamental/blob/de78350bd7c03eb4c7e798fd4bbada8d601ce410/files/KB_monthlyA.xlsx?raw=true'
    kbm_dict = pd.ExcelFile(file_path)

    return kbm_dict

def read_source_excel():
    # file_path = 'https://github.com/sizipusx/fundamental/blob/f204259c131f693dd0cb6359d73f459ceceba5c7/files/KB_monthlyA.xlsx?raw=true'
    kbm_dict = pd.read_excel(file_path, sheet_name=None, header=1)

    return kbm_dict

@st.cache
def load_ratio_data():
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
    
    header_dict = pd.read_excel(header_path, sheet_name=None)
    header = header_dict['one']
#     one_dict = pd.read_excel(p_path, sheet_name=None, header=1, index_col=0, parse_dates=True)
#     omdf = one_dict['sell']
#     ojdf = one_dict['jeon']
#     r_df = one_dict['ratio']
#     mdf = omdf.iloc[4:,:]
#     jdf = ojdf.iloc[4:,:]
#     rdf = r_df.iloc[4:,:]
#     #컬럼 변경
#     s1 = mdf.columns
#     new_s1 = []
#     for num, gu_data in enumerate(s1):
#         check = num
#         if gu_data.startswith('Un'):
#             new_s1.append(new_s1[check-1])
#         else:
#             new_s1.append(s1[check])
#     #전세가율은 다른가?
    
#     mdf.columns =[new_s1, omdf.iloc[1]]
#     jdf.columns = [new_s1, ojdf.iloc[1]]
#     rdf.columns =[new_s2, r_df.iloc[1]]
#     #필요 시트만 슬라이스
    smdf = omp_df.xs('평균매매',axis=1, level=1)
    sadf = omp_df.xs('평균단위매매', axis=1, level=1)
    jmdf = ojp_df.xs('평균전세',axis=1, level=1)
    jadf = ojp_df.xs('평균단위전세', axis=1, level=1)
    m_df = rdf.xs('중위', axis=1, level=1) # 중위가격 전세가율
    a_df = rdf.xs('평균', axis=1, level=1) # 평균가격 전세가율
    smdf.columns = header.columns
    sadf.columns = header.columns
    jmdf.columns = header.columns
    jadf.columns = header.columns
    m_df.columns = header.columns
    a_df.columns = header.columns

    sadf = (sadf.astype(float)*3.306)/10
    smdf = smdf.astype(float)/10
    jadf = (jadf.astype(float)*3.306)/10
    jmdf = jmdf.astype(float)/10

    sadf = sadf.round(decimals=2) #평균매매가
    smdf = smdf.round(decimals=2) #
    jadf = jadf.round(decimals=2)
    jmdf = jmdf.round(decimals=2)
    m_df = m_df.round(decimals=1)
    a_df = a_df.round(decimals=1)

    sadf_ch = sadf.pct_change()*100
    sadf_ch = sadf_ch.round(decimals=2)
    jadf_ch = jadf.pct_change()*100
    jadf_ch = jadf_ch.round(decimals=2)

    ######################### 여기부터는 전세가율
    #jratio = round(jmdf/smdf*100,1)
    

    return sadf, sadf_ch, jadf, jadf_ch, m_df, a_df


@st.cache(ttl=600)
def load_buy_data():
    #년 증감 계산을 위해 최소 12개월치 데이터 필요
    # path = r'https://github.com/sizipusx/fundamental/blob/0bc9c7aa7236c68895e69f04fb562973f73ba2b3/files/apt_buy.xlsx?raw=true'
    # data_type = 'apt_buy' 
    # df = pd.read_excel(one_path, sheet_name=data_type, header=10)
    # # path1 = r'https://github.com/sizipusx/fundamental/blob/a5ce2b7ed9d208b2479580f9b89d6c965aaacb12/files/header.xlsx?raw=true'
    # header = pd.read_excel(header_path, sheet_name='buyer')
    # df['지 역'] = header['local'].str.strip()
    # df = df.rename({'지 역':'지역명'}, axis='columns')
    # df.drop(['Unnamed: 1', 'Unnamed: 2'], axis=1, inplace=True)
    # df = df.set_index("지역명")
    # df = df.T
    # df.columns = [df.columns, df.iloc[0]]
    # df = df.iloc[1:]
    # df.index = df.index.map(lambda x: x.replace('년','-').replace(' ','').replace('월', '-01'))
    # df.index = pd.to_datetime(df.index)
    # df = df.apply(lambda x: x.replace('-','0'))
    # df = df.astype(float)
    # org_df = df.copy()
    ### db에서 읽기
    conn = create_connection(one_db_path)
    in_df = pd.read_sql("SELECT * FROM 'investor'", conn, index_col='index')
    in_df = in_df.apply(lambda x: x.replace('-','0'))
    in_df = in_df.astype(int)
    conn.close()
    ### g_sheet에서 읽어오기
    # in_df = one_doc.worksheet('investor')
    # #데이터 프레임으로 읽기
    # basic_values = in_df.get_all_values()

    # basic_header, basic_rows = basic_values[0], basic_values[1:]
    # basic_df= pd.DataFrame(basic_rows, columns=basic_header)
    # basic_df = basic_df.set_index(['local','매입자거주지'])
    # df = basic_df.T
    # df.index = df.index.map(lambda x: x.replace('년','-').replace(' ','').replace('월', ''))
    # df = df.apply(lambda x: x.replace('-','0'))
    # df = df.astype(int)
    #org_df = in_df.copy()
    ####
    #drop_list = ['전국', '서울', '경기', '경북', '경남', '전남', '전북', '강원', '대전', '대구', '인천', '광주', '부산', '울산', '세종','충남', '충북']
    #drop_list2 = ['수원', '성남', '천안', '청주', '전주', '고양', '창원', '포항', '용인', '안산', '안양']
    # big_city = df.iloc[:,drop_list]
    #in_df.drop(drop_list, axis=1, level=0, inplace=True)
    #in_df.drop(drop_list2, axis=1, level=0, inplace=True)
    # drop_list3 = df.columns[df.columns.get_level_values(0).str.endswith('군')]
    # df.drop(drop_list3, axis=1, inplace=True)
    # df = df[df.columns[~df.columns.get_level_values(0).str.endswith('군')]]
    
    return in_df

@st.cache
def load_index_data():
    # kbm_dict = read_source()
    # # kbm_dict = pd.ExcelFile(file_path)
    # #헤더 변경
    # # path = 'https://github.com/sizipusx/fundamental/blob/a5ce2b7ed9d208b2479580f9b89d6c965aaacb12/files/header.xlsx?raw=true'
    # header_excel = pd.ExcelFile(header_path)
    # #header = header_excel.parse('KB')
    # code_df = header_excel.parse('code', index_col=1)
    # code_df.index = code_df.index.str.strip()

    #주택가격지수
    #mdf = kbm_dict.parse("2.매매APT", skiprows=1, index_col=0, convert_float=True)
    #jdf = kbm_dict.parse("6.전세APT", skiprows=1, index_col=0, convert_float=True)
    #mdf.columns = header.columns
    #jdf.columns = header.columns
    #index 날짜 변경
    
    #mdf = mdf.iloc[2:]
    #jdf = jdf.iloc[2:]
    #index_list = list(mdf.index)

    #new_index = []

    #for num, raw_index in enumerate(index_list):
    #    temp = str(raw_index).split('.')
    #    if int(temp[0]) > 12 :
    #        if len(temp[0]) == 2:
    #            new_index.append('19' + temp[0] + '.' + temp[1])
    #        else:
    #            new_index.append(temp[0] + '.' + temp[1])
    #    else:
    #        new_index.append(new_index[num-1].split('.')[0] + '.' + temp[0])

    #mdf.set_index(pd.to_datetime(new_index), inplace=True)
    #jdf.set_index(pd.to_datetime(new_index), inplace=True)
    #mdf = mdf.astype(float).fillna(0).round(decimals=2)
    #jdf = jdf.astype(float).fillna(0).round(decimals=2)

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
    
    # #geojson file open
    # geo_source = 'https://raw.githubusercontent.com/sizipusx/fundamental/main/sigungu_json.geojson'
    # with urlopen(geo_source) as response:
    #     geo_data = json.load(response)
    
    # #geojson file 변경
    # for idx, sigun_dict in enumerate(geo_data['features']):
    #     sigun_id = sigun_dict['properties']['SIG_CD']
    #     sigun_name = sigun_dict['properties']['SIG_KOR_NM']
    #     try:
    #         sell_change = df.loc[(df.SIG_CD == sigun_id), '매매증감'].iloc[0]
    #         jeon_change = df.loc[(df.SIG_CD == sigun_id), '전세증감'].iloc[0]
    #     except:
    #         sell_change = 0
    #         jeon_change =0
    #     # continue
        
    #     txt = f'<b><h4>{sigun_name}</h4></b>매매증감: {sell_change:.2f}<br>전세증감: {jeon_change:.2f}'
    #     # print(txt)
        
    #     geo_data['features'][idx]['id'] = sigun_id
    #     geo_data['features'][idx]['properties']['sell_change'] = sell_change
    #     geo_data['features'][idx]['properties']['jeon_change'] = jeon_change
    #     geo_data['features'][idx]['properties']['tooltip'] = txt
   
    # return mdf, jdf, code_df, geo_data

    ######DB에서 읽어오기##################
    conn = create_connection(kb_db_path)
    index_list = []
    query_list = ["select * from mae", "select * from jeon"]
    for query in query_list:
        df = pd.read_sql(query, conn, index_col='date')
        df.index = pd.to_datetime(df.index, format = '%Y-%m-%d')
        df = df.apply(lambda x:x.replace('#DIV/0!','0')).apply(lambda x:x.replace('','0')).astype(float)
        df = df.round(decimals=2)
        index_list.append(df)
    code_df = pd.read_sql("select * from code", conn, index_col='dist')
    code_df.index = code_df.index.str.strip()
    conn.close()

    return index_list, code_df

@st.cache
def load_pop_data():
    #인구수 파일 변경
    # p_path = r"https://github.com/sizipusx/fundamental/blob/1107b5e09309b7f74223697529ac757183ef4f05/files/pop.xlsx?raw=True"
    # kb_dict = pd.read_excel(pop_path, sheet_name=None, header=1, parse_dates=True)
    # pdf = kb_dict['pop']
    # sae = kb_dict['sae']

    # #header file: 인구수와 세대수가 약간 다르다.
    # psdf = pd.read_excel(header_path, sheet_name='pop', header=0)
  
    # pdf['행정구역'] = psdf['pop']
    # pdf = pdf.set_index("행정구역")
    # pdf = pdf.iloc[:,3:]
    # test = pdf.columns.str.replace(' ','').map(lambda x : x.replace('월','.01'))
    # pdf.columns = test
    # df = pdf.T
    ## 구글 시트에서 가져오기
    bs = bs_doc.worksheet('pop')
    bs_values = bs.get_all_values()
    bs_header, bs_rows = bs_values[2], bs_values[3:]
    pdf = pd.DataFrame(bs_rows, columns=bs_header)
    pdf = pdf.set_index("pop")
    pdf = pdf.iloc[:,1:]
    test = pdf.columns.str.replace(' ','').map(lambda x : x.replace('월','.01'))
    pdf.columns = test
    pop_df = pdf.T
    pop_df = pop_df.apply(lambda x: x.replace('','0'))
    pop_df = pop_df.astype(int)
    # df = df.iloc[:-1]
    pop_df.index = pd.to_datetime(pop_df.index)
    pop_change = pop_df.pct_change()*100
    pop_change = pop_change.round(decimals=2)
    #세대수
    # sae['행정구역'] =  psdf['sae']
    # sae = sae.set_index("행정구역")
    # sae = sae.iloc[:,3:]
    # sae.columns = test
    # sdf = sae.T
    #세대
    sae = bs_doc.worksheet('sae')
    sae_values = sae.get_all_values()
    sae_header, sae_rows = sae_values[2], sae_values[3:]
    sae_df = pd.DataFrame(sae_rows, columns=sae_header)
    sae_df = sae_df.set_index("sae")
    sae_df = sae_df.iloc[:,1:]
    #test = pdf.columns.str.replace(' ','').map(lambda x : x.replace('월','.01'))
    sae_df.columns = test
    sdf = sae_df.T
    sdf = sdf.apply(lambda x: x.replace('','0'))
    sdf = sdf.astype(int)
    # sdf = sdf.iloc[:-1]
    sdf.index = pd.to_datetime(sdf.index)
    sdf_change = sdf.pct_change()*100
    sdf_change = sdf_change.round(decimals=2)

    ## 2022. 1. 5 완공 후 미분양 데이터 가져오기 from one file
    # data_type = 'not_sell' 
    # df1 = pd.read_excel(one_path, sheet_name=data_type, index_col=0, parse_dates=True)
    # #df1 = one_dict['not_sell']

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
    # #df1.index = pd.to_datetime(df1.index)
    # df1 = df1.astype(int)
        
    return pop_df, pop_change, sdf, sdf_change

@st.cache(ttl=600)
def load_not_sell_data():
    #미분양
    # mb = one_doc.worksheet('notsold')
    # mb_values = mb.get_all_values()
    # mb_header, mb_rows = mb_values[1], mb_values[2:]
    # mb_df = pd.DataFrame(mb_rows, columns=mb_header)
    # mb_df = mb_df.set_index(mb_df.iloc[:,0])
    # mb_df = mb_df.iloc[:,1:]
    # mb_df.index.name = 'date'
    # mb_df = mb_df.astype(str).apply(lambda x:x.replace(',','')).apply(lambda x:x.replace('','0')).replace('#DIV/0!','0').astype(int)
    # #준공 후 미분양
    # ns = one_doc.worksheet('afternotsold')
    # ns_values = ns.get_all_values()
    # ns_header, ns_rows = ns_values[1], ns_values[2:]
    # omdf = pd.DataFrame(ns_rows, columns=ns_header)
    # omdf = omdf.set_index(omdf.iloc[:,0])
    # omdf = omdf.iloc[:,1:]
    # omdf.index.name = 'date'
    # omdf = omdf.astype(str).apply(lambda x:x.replace(',','')).apply(lambda x:x.replace('','0')).replace('#DIV/0!','0').astype(int)

    # return omdf, mb_df

    conn = create_connection(one_db_path)
    not_sold_list = []
    query_list = ["select * from not_sold", "select * from after_not_sold"]
    for query in query_list:
        df = pd.read_sql(query, conn, index_col='date')
        df.index = pd.to_datetime(df.index, format = '%Y-%m-%d')
        not_sold_list.append(df)
    conn.close()

    return not_sold_list

@st.cache
def load_senti_data():
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
            #전세수급지수만 filtering
            if k.title == 'kbs':
                js_index = kbs_df.xs("매수우위지수", axis=1, level=1)
                js_a = kbs_df.xs("매도자 많음", axis=1, level=1)
                js_b = kbs_df.xs("매수자 많음", axis=1, level=1)
            elif k.title == 'kbmtr':
                js_index = kbs_df.xs("매매거래지수", axis=1, level=1)
                js_a = kbs_df.xs("활발함", axis=1, level=1)
                js_b = kbs_df.xs("한산함", axis=1, level=1)
            elif k.title == 'kbjs':
                js_index = kbs_df.xs("전세수급지수", axis=1, level=1)
                js_a = kbs_df.xs("수요>공급", axis=1, level=1)
                js_b = kbs_df.xs("수요<공급", axis=1, level=1)
            elif k.title == 'kbjtr':
                js_index = kbs_df.xs("전세거래지수", axis=1, level=1)
                js_a = kbs_df.xs("활발함", axis=1, level=1)
                js_b = kbs_df.xs("한산함", axis=1, level=1)
    # kbm_dict = read_source_excel()

    # m_sheet = '21.매수우위,22.매매거래,23.전세수급,24.전세거래,25.KB부동산 매매가격 전망지수,26.KB부동산 전세가격 전망지수'
    # m_list = m_sheet.split(',')
    # df_dic = []
    # df_a = []
    # df_b = []

    # for k in kbm_dict.keys():
    #     js = kbm_dict[k]
    #     # print(f"sheet name is {k}")

    #     if k in m_list:
    #         print(f"sheet name is {k}")
    #         js = js.set_index("Unnamed: 0")
    #         js.index.name="날짜"

    #         #컬럼명 바꿈
    #         j1 = js.columns.map(lambda x: x.split(' ')[0])

    #         new_s1 = []
    #         for num, gu_data in enumerate(j1):
    #             check = num
    #             if gu_data.startswith('Un'):
    #                 new_s1.append(new_s1[check-1])
    #             else:
    #                 new_s1.append(j1[check])

    #         #컬럼 설정
    #         js.columns = [new_s1,js.iloc[0]]

    #         #전세수급지수만 filtering
    #         if k == '21.매수우위':
    #             js_index = js.xs("매수우위지수", axis=1, level=1)
    #             js_a = js.xs("매도자 많음", axis=1, level=1)
    #             js_b = js.xs("매수자 많음", axis=1, level=1)
    #         elif k == '22.매매거래':
    #             js_index = js.xs("매매거래지수", axis=1, level=1)
    #             js_a = js.xs("활발함", axis=1, level=1)
    #             js_b = js.xs("한산함", axis=1, level=1)
    #         elif k == '23.전세수급':
    #             js_index = js.xs("전세수급지수", axis=1, level=1)
    #             js_a = js.xs("수요>공급", axis=1, level=1)
    #             js_b = js.xs("수요<공급", axis=1, level=1)
    #         elif k == '24.전세거래':
    #             js_index = js.xs("전세거래지수", axis=1, level=1)
    #             js_a = js.xs("활발함", axis=1, level=1)
    #             js_b = js.xs("한산함", axis=1, level=1)
    #         elif k == '25.KB부동산 매매가격 전망지수':
    #             js_index = js.xs("KB부동산\n매매전망지수", axis=1, level=1)
    #             js_a = js.xs("약간상승", axis=1, level=1)
    #             js_b = js.xs("약간하락", axis=1, level=1)
    #         elif k == '26.KB부동산 전세가격 전망지수':
    #             js_index = js.xs("KB부동산\n전세전망지수", axis=1, level=1)
    #             js_a = js.xs("약간상승", axis=1, level=1)
    #             js_b = js.xs("약간하락", axis=1, level=1)
    #         #필요 데이터만
    #         js_index = js_index.iloc[2:js_index['서울'].count(), : ]
    #         js_a = js_a.iloc[2:js_a['서울'].count(), : ]
    #         js_b = js_b.iloc[2:js_b['서울'].count(), : ]

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
            js_index = js_index.astype(str).apply(lambda x: x.replace('','0')).astype(float).round(decimals=2)
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

@st.cache(suppress_st_warning=True)
def load_local_basic():
    ## 구글 시트에서 읽어 오자.
    fun = bs_doc.worksheet('fun')
    fun_values = fun.get_all_values()
    fun_header, fun_rows = fun_values[0], fun_values[1:]
    fun_df = pd.DataFrame(fun_rows, columns=fun_header)
    fun_df = fun_df.set_index('행정구역')
    fun_df.columns = [fun_df.columns, fun_df.iloc[0]]
    fun_df = fun_df.iloc[1:]
    fun_df.iloc[:,:4] = fun_df.iloc[:,:4].astype(str)
    fun_df.iloc[:,4] = fun_df.iloc[:,4].astype(str).apply(lambda x: x.replace(' ','0')).apply(lambda x: x.replace('-','0')).astype(float).round(decimals=2)
    fun_df.iloc[:,5:17] = fun_df.iloc[:,5:17].astype(str).apply(lambda x: x.replace(' ','0')).apply(lambda x: x.replace('-','0')).astype(int)
    fun_df.iloc[:,17] = fun_df.iloc[:,17].astype(str).apply(lambda x: x.replace(' ','0')).apply(lambda x: x.replace('-','0')).astype(float).round(decimals=2)
    fun_df.iloc[:,18] = fun_df.iloc[:,18].astype(int)
    fun_df.iloc[:,19:21] = fun_df.iloc[:,19:21].astype(str).apply(lambda x: x.replace(' ','0')).apply(lambda x: x.replace('-','0')).astype(float).round(decimals=2)
    fun_df.iloc[:,22] = fun_df.iloc[:,22].astype(str).apply(lambda x: x.replace(' ','0')).apply(lambda x: x.replace('-','0')).astype(int)
    fun_df.iloc[:,23:26] = round(fun_df.iloc[:,23:26].astype(str).apply(lambda x: x.replace(' ','0')).apply(lambda x: x.replace('-','0')).astype(float),2)
    fun_df.iloc[:,26:38] = fun_df.iloc[:,26:38].astype(str).apply(lambda x: x.replace(' ','0')).apply(lambda x: x.replace('-','0')).astype(int)
    fun_df.iloc[:,38] = fun_df.iloc[:,38].astype(float)
    # basic_dict = pd.ExcelFile(basic_path)
    # df = basic_dict.parse("Sheet1", header=[0,1], index_col=0)
    # fun_df[('인구 및 세대수', '인구수')] = fun_df[('인구 및 세대수', '인구수')].apply(lambda x: x.replace(',','')).astype(float)
    # fun_df[('인구 및 세대수', '세대수')] = fun_df[('인구 및 세대수', '세대수')].apply(lambda x: x.replace(',','')).astype(float)
    # df[('종사자규모별 사업체수', '500 - 999명')] = df[('종사자규모별 사업체수', '500 - 999명')].apply(lambda x: x.replace(',','')).astype(int)
    # df[('종사자규모별 사업체수', '1000명\n이상')] = df[('종사자규모별 사업체수', '1000명\n이상')].apply(lambda x: x.replace(',','')).astype(int)
    #fun_df = fun_df.round(decimals=2)
    bigc = fun_df.loc[:'제주',:]
    smc = fun_df.loc['서울 강남구':, :]
    smc.loc[:,('보험료', '직장월급여')].replace([np.inf, -np.inf], np.nan, inplace=True)
    smc.loc[:,('보험료', '직장월급여')] = fun_df.loc[:,('보험료', '직장월급여')].astype(float).fillna(0)
    smc.loc[:,('보험료', '직장월급여')]

    return fun_df, bigc, smc
############ data 불러오기 ######################
#mdf, jdf, code_df, geo_data = load_index_data()
index_list, code_df = load_index_data()
mdf = index_list[0]
jdf = index_list[1]
popdf, popdf_change, saedf, saedf_change = load_pop_data()
# not_sell, mibunyang = load_not_sell_data()
not_sell_list = load_not_sell_data()
not_sell = not_sell_list[1]
mibunyang = not_sell_list[0]
org_df = load_buy_data()
peong_df, peong_ch, peongj_df, peongj_ch, mr_df, ar_df = load_ratio_data()
basic_df, bigc, smc = load_local_basic()

#마지막 달
kb_last_month = pd.to_datetime(str(mdf.index.values[-1])).strftime('%Y.%m')
pop_last_month = pd.to_datetime(str(popdf.index.values[-1])).strftime('%Y.%m')
buy_last_month = pd.to_datetime(str(org_df.index.values[-1])).strftime('%Y.%m')
not_sell_month = str(not_sell.index.values[-1])
with st.expander("See recently Data Update"):
    cols = st.columns(4)
    cols[0].markdown(f'KB 월간: **{kb_last_month}월**')
    cols[1].markdown(f'인구세대수 : **{pop_last_month}월**')
    cols[2].markdown(f'아파트 매입자 거주지별 현황: **{buy_last_month}월**')
    cols[3].markdown(f'준공 후 미분양: **{buy_last_month}월**')

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
# jdf = jdf.mask(np.isinf(jdf))
#일주일 간 상승률 순위
last_df = mdf_change.iloc[-1].T.to_frame()
last_df['전세증감'] = jdf_change.iloc[-1].T.to_frame()
last_df.columns = ['매매증감', '전세증감']
last_df.dropna(inplace=True)
last_df = last_df.round(decimals=2)
# st.dataframe(last_df.style.highlight_max(axis=0))
#인구, 세대수 마지막 데이터
last_pop = popdf_change.iloc[-1].T.to_frame()
last_sae = saedf_change.iloc[-1].T.to_frame()
last_ps = pd.merge(last_pop, last_sae, how='inner', left_index=True, right_index=True)
last_ps.columns = ['인구증감', '세대증감']
# last_pop.dropna(inplace=True)
last_ps = last_ps.round(decimals=2) 

#마지막달 dataframe에 지역 코드 넣어 합치기
df = pd.merge(last_df, code_df, how='inner', left_index=True, right_index=True)
df.columns = ['매매증감', '전세증감', 'SIG_CD']
df['SIG_CD']= df['SIG_CD'].astype(str)
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
cum_ch = (mdf_change/100 +1).cumprod() -1
jcum_ch = (jdf_change/100 +1).cumprod() -1
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

#부동산원 평균 전세가율 마지막 데이터
one_last_df = ar_df.iloc[-1].T.to_frame()
sub_df = one_last_df[one_last_df.iloc[:,0] >= 70.0]
# st.dataframe(sub_df)
sub_df.columns = ['전세가율']
sub_df = sub_df.sort_values('전세가율', ascending=False )

################################### graph 그리기 ##########################################

### first select box ----
senti_dfs, df_as, df_bs = load_senti_data()
#do_list = senti_dfs[0].columns.to_list()
#도시명 변경
do_list = ['전국', '수도권', '지방', '6대광역시', '5대광역시', '서울', '경기', '부산', '대구', '인천', '광주', '대전',
                  '울산', '세종', '강원', '충북', '충남', '전북', '전남', '경북', '경남', '제주도']

selected_dosi = st.selectbox(' Select 광역시도', do_list)
html_br="""
<br>
"""
st.markdown(html_br, unsafe_allow_html=True)
### Block 0#########################################################################################
with st.container():
    col1, col2, col3 = st.columns([30,2,30])
    with col1:
        drawAPT_update.draw_basic_info(selected_dosi, basic_df, bigc, smc)
    with col2:
        st.write("")
    with col3:
        drawAPT_update.draw_company_info(selected_dosi, basic_df, bigc, smc)
html_br="""
<br>
"""
st.markdown(html_br, unsafe_allow_html=True)
### Block 0.5#########################################################################################
with st.container():
    col1, col2, col3 = st.columns([30,2,30])
    with col1:
        drawAPT_update.draw_pay_info(selected_dosi, basic_df, bigc, smc)
    with col2:
        st.write("")
    with col3:
        #drawAPT_update.draw_earning_info(selected_dosi, basic_df, bigc, smc)
        st.write("")
html_br="""
<br>
"""
st.markdown(html_br, unsafe_allow_html=True)
### Block 0.5-1#########################################################################################
with st.container():
    col1, col2, col3 = st.columns([30,2,30])
    with col1:
        drawAPT_update.draw_earning_info(selected_dosi, bigc, smc, flag = 'pop')
    with col2:
        st.write("")
    with col3:
        drawAPT_update.draw_earning_info(selected_dosi, bigc, smc, flag = 'money')
html_br="""
<br>
"""
st.markdown(html_br, unsafe_allow_html=True)
### Block 0.6#########################################################################################
with st.container():
    col1, col2, col3 = st.columns([30,2,30])
    with col1:
        drawAPT_update.run_local_analysis(mdf, mdf_change, selected_dosi)
    with col2:
        st.write("")
    with col3:
        drawAPT_update.run_local_price(peong_df, peongj_df, selected_dosi)

html_br="""
<br>
"""
st.markdown(html_br, unsafe_allow_html=True)
### Block 1#########################################################################################
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
### Block 2#########################################################################################
with st.container():
    col1, col2, col3, col4, col5 = st.columns([20,1,20,1,20])
    with col1:
        drawAPT_update.draw_mae_bs(selected_dosi, senti_dfs, df_as, df_bs)
    with col2:
        st.write("")
    with col3:
        drawAPT_update.draw_jeon_bs(selected_dosi, senti_dfs, df_as, df_bs)
    with col4:
        st.write("")
    with col5:
        drawAPT_update.draw_jeon_trade(selected_dosi, senti_dfs, df_as, df_bs)

html_br="""
<br>
"""
st.markdown(html_br, unsafe_allow_html=True)

if selected_dosi == '6대광역시' or '5대광역시' or '지방':
    st.write("No Data")
else :
    ### Block 3 KB 전망지수 #########################################################################################
    with st.container():
        col1, col2, col3 = st.columns([30,1,30])
        with col1:
            drawAPT_update.draw_kb_mfore(selected_dosi, senti_dfs, df_as, df_bs)
        with col2:
            st.write("")
        with col3:
            drawAPT_update.draw_kb_jfore(selected_dosi, senti_dfs, df_as, df_bs)

    html_br="""
    <br>
    """
    st.markdown(html_br, unsafe_allow_html=True)

###  2번째 구선택: 시도구 ########################################################################################################
city_list = ['전국', '서울', '6대광역시','부산','대구','인천','광주','대전','울산','5대광역시','수도권','세종','경기', '수원', \
                    '성남','고양', '안양', '부천', '의정부', '광명', '평택','안산', '과천', '구리', '남양주', '용인', '시흥', '군포', \
                    '의왕','하남','오산','파주','이천','안성','김포', '양주','동두천','경기 광주', '화성','강원', '춘천','강릉', '원주', \
                    '충북','청주', '충주','제천', '충남','천안', '공주','아산', '논산', '계룡','당진','서산', '전북', '전주', '익산', '군산', \
                    '전남', '목포','순천','여수','광양','경북','포항','구미', '경산', '안동','김천','경남','창원', '양산','거제','진주', \
                    '김해','통영', '제주','지방']
column_list = mdf.columns.to_list()
city_series = pd.Series(column_list)
small_list = []
mirco_list = []
if selected_dosi == '전국':
  small_list = ['전국']
elif selected_dosi == '서울' or selected_dosi == '부산' or selected_dosi == '인천' or selected_dosi == '광주' \
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
elif selected_dosi == '경남':
  small_list = ['경남','창원', '양산','거제','진주', '김해','통영']
elif selected_dosi == '제주':
  small_list = ['제주']
elif selected_dosi == '세종':
  small_list = ['세종']
 ##6개 광역시, 5대광역시, 기타지방은 인구수가 없음
elif selected_dosi == '6대광역시' or '5대광역시' or '지방' or '서울 강북권역' or '서울 강남권역':
    small_list = []
    st.write("No Data")
else:
    small_list = []
    st.write("No Data")
  
### Select Block #########################################################################################
with st.container():
    col1, col2, col3 = st.columns([30,2,30])
    with col1:
        selected_city = st.selectbox(' Select city', small_list)
    with col2:
        st.write("")
    with col3:
        if selected_city == '고양':
            mirco_list = ['고양 덕양구', '고양 일산동구', '고양 일산서구']
        elif selected_city == '성남':
            mirco_list = ['성남 분당구', '성남 수정구', '성남 중원구']
        elif selected_city == '수원':
            mirco_list = ['수원 영통구', '수원 팔달구', '수원 장안구', '수원 권선구']
        elif selected_city == '안산':
            mirco_list = ['안산 단원구', '안산 상록구']
        elif selected_city == '안양':
            mirco_list = ['안양 만안구', '안양 동안구']
        elif selected_city == '용인':
            mirco_list = ['용인 수지구','용인 기흥구', '용인 처인구']
        elif selected_city == '전주':
            mirco_list = ['전주 덕진구', '전주 완산구']
        elif selected_city == '청주':
            mirco_list = ['청주 청원구', '청주 흥덕구', '청주 서원구', '청주 상당구']
        elif selected_city == '천안':
            mirco_list = ['천안 서북구', '천안 동남구']
        elif selected_city == '포항':
            mirco_list = ['포항 북구', '포항 남구']
        elif selected_city == '창원':
            mirco_list = ['창원 마산합포구','창원 마산 회원구', '창원 진해구','창원 의창구', '창원 성산구']


        selected_micro_city = st.selectbox('Select city', mirco_list)

html_br="""
<br>
"""



### Block 5#########################################################################################
with st.container():
    col1, col2, col3 = st.columns([30,2,30])
    with col1:
        drawAPT_update.run_pop_index(selected_city, popdf, popdf_change, saedf, saedf_change)
    with col2:
        st.write("")
    with col3:
        drawAPT_update.run_not_sell(selected_dosi, selected_city, not_sell, mibunyang)

html_br="""
<br>
"""
st.markdown(html_br, unsafe_allow_html=True)
### Block 6#########################################################################################
# with st.container():
#     col2, col3, col4 = st.columns([30,2,30])
#     with col2:
#         drawAPT_update.run_sell_index(selected_city, peong_df, peong_ch)
#     with col3:
#         st.write("")
#     with col4:
#         drawAPT_update.run_jeon_index(selected_city, peongj_df, peongj_ch)

# st.markdown(html_br, unsafe_allow_html=True)
### Block 6-1#########################################################################################
with st.container():
    col2, col3, col4 = st.columns([30,2,30])
    with col2:
        drawAPT_update.run_jeon_ratio(selected_city, mr_df, ar_df)
    with col3:
        st.write("")
    with col4:
        drawAPT_update.run_trade_index(selected_city, org_df, mdf)
    
html_br="""
<br>
"""
st.markdown(html_br, unsafe_allow_html=True)
#################block 7###########################################################################
with st.container():
    col2, col3, col4 = st.columns([30,2,30])
    with col2:
        drawAPT_update.run_buy_index(selected_city, org_df)
    with col3:
        st.write("")
    with col4:
        drawAPT_update.run_buy_ratio(selected_city, org_df)

html_br="""
<br>
"""
st.markdown(html_br, unsafe_allow_html=True)
### Block 8#########################################################################################
with st.container():
    col2, col3, col4 = st.columns([30,2,30])
    with col2:
        flag = 'KB'
        drawAPT_update.run_price_index(selected_city, selected_micro_city, mdf, jdf, mdf_change, jdf_change, flag)
    with col3:
        st.write("")
    with col4:
        drawAPT_update.run_bubble(selected_city, bubble_df2, m_power)
html_br="""
<br>
"""
### Block 9 누적 플라워 그래프#########################################################################
with st.container():
    col2, col3, col4 = st.columns([30,2,30])
    with col2:
        flag = 'KB'
        drawAPT_update.draw_flower(selected_city, selected_micro_city, cum_mdf, cum_jdf, flag)
    with col3:
        st.write("")
    with col4:
        drawAPT_update.draw_flower_together(small_list, cum_mdf, cum_jdf, flag)
html_br="""
<br>
"""
####지역 시황 ###############
df_dic = pd.ExcelFile(local_path)
dmf = df_dic.parse("KB매매", index_col=0)
djf = df_dic.parse("KB전세", index_col=0)

with st.container():
    col2, col3, col4 = st.columns([30,2,30])
    with col2:
        st.table(dmf[selected_city].dropna())
    with col3:
        st.write("")
    with col4:
        st.table(djf[selected_city].dropna())
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
<p style="color:Gainsboro; text-align: right;">By: https://blog.naver.com/indiesoul2 / sizipusx2@gmail.com</p>
"""
st.markdown(html_line, unsafe_allow_html=True)
