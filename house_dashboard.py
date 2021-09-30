import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import streamlit as st
import pandas as pd
import numpy as np

import drawAPT
import requests
from urllib.request import urlopen
import json
from pandas.io.json import json_normalize

st.set_page_config(page_title="House Analysis Dashboard", page_icon="", layout="wide")
st.markdown('<style>body{background-color: #fbfff0}</style>',unsafe_allow_html=True)
st.markdown(html_header, unsafe_allow_html=True)
st.markdown(""" <style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style> """, unsafe_allow_html=True)
# data=pd.read_excel('curva.xlsx')


### data 가져오기 영역 ##########################
def read_source(): 
    file_path = 'https://github.com/sizipusx/fundamental/blob/f204259c131f693dd0cb6359d73f459ceceba5c7/files/KB_monthlyA.xlsx?raw=true'
    kbm_dict = pd.ExcelFile(file_path)

    return kbm_dict

def read_source_excel():
    file_path = 'https://github.com/sizipusx/fundamental/blob/f204259c131f693dd0cb6359d73f459ceceba5c7/files/KB_monthlyA.xlsx?raw=true'
    kbm_dict = pd.read_excel(file_path, sheet_name=None, header=1)

    return kbm_dict

@st.cache
def load_ratio_data():
    header_path = 'https://github.com/sizipusx/fundamental/blob/80e5af9925c10a53b855cf6757fa1bba7eeb136d/files/header.xlsx?raw=true'
    header_excel = pd.ExcelFile(header_path)
    kb_header = header_excel.parse('KB')
    ################# 여기느 평단가 소스: 2021. 9. 17. One data -> KB data 변경
    p_path = r"https://github.com/sizipusx/fundamental/blob/1a800b4035fafde7df18ecd1882a8313051a9b45/files/kb_price.xlsx?raw=True"
    kb_dict = pd.read_excel(p_path, sheet_name=None, header=1, index_col=0, parse_dates=True)

    for k in kb_dict.keys():
        print(k)
    mdf = kb_dict['sell']
    jdf = kb_dict['jeon']
    mdf = mdf.iloc[2:mdf['서울'].count()+1]
    jdf = jdf.iloc[2:jdf['서울'].count()+1]
    #index 날짜 변경
    index_list = list(mdf.index)

    new_index = []

    for num, raw_index in enumerate(index_list):
        temp = str(raw_index).split('.')
        if int(temp[0]) > 12 :
            if len(temp[0]) == 2:
                new_index.append('19' + temp[0] + '.' + temp[1])
            else:
                new_index.append(temp[0] + '.' + temp[1])
        else:
            new_index.append(new_index[num-1].split('.')[0] + '.' + temp[0])
    mdf.set_index(pd.to_datetime(new_index), inplace=True)
    jdf.set_index(pd.to_datetime(new_index), inplace=True)
    mdf.columns = kb_header.columns
    jdf.columns = kb_header.columns
    mdf = round(mdf.replace('-','0').astype(float)*3.3,2)
    jdf = round(jdf.replace('-','0').astype(float)*3.3,2)
    mdf_ch = mdf.pct_change()*100
    mdf_ch = mdf_ch.round(decimals=2)
    jdf_ch = jdf.pct_change()*100
    jdf_ch = jdf_ch.round(decimals=2)
        
    ######################### 여기부터는 전세가율
    jratio = round(jdf/mdf*100,1)
    

    return mdf, mdf_ch, jdf, jdf_ch, jratio


@st.cache
def load_buy_data():
    #년 증감 계산을 위해 최소 12개월치 데이터 필요
    path = r'https://github.com/sizipusx/fundamental/blob/20d4e65edfee33ff87588a03d74135b536910d9a/files/apt_buy.xlsx?raw=true'
    data_type = 'Sheet1' 
    df = pd.read_excel(path, sheet_name=data_type, header=10)
    path1 = r'https://github.com/sizipusx/fundamental/blob/d91daa59a4409bd9281172d2a1d46a56b27fac2a/files/header.xlsx?raw=true'
    header = pd.read_excel(path1, sheet_name='buyer')
    df['지 역'] = header['local'].str.strip()
    df = df.rename({'지 역':'지역명'}, axis='columns')
    df.drop(['Unnamed: 1', 'Unnamed: 2'], axis=1, inplace=True)
    df = df.set_index("지역명")
    df = df.T
    df.columns = [df.columns, df.iloc[0]]
    df = df.iloc[1:]
    df.index = df.index.map(lambda x: x.replace('년','-').replace(' ','').replace('월', '-01'))
    df.index = pd.to_datetime(df.index)
    df = df.apply(lambda x: x.replace('-','0'))
    df = df.astype(float)
    org_df = df.copy()
    drop_list = ['전국', '서울', '경기', '경북', '경남', '전남', '전북', '강원', '대전', '대구', '인천', '광주', '부산', '울산', '세종 세종','충남', '충북']
    drop_list2 = ['수원', '성남', '천안', '청주', '전주', '고양', '창원', '포항', '용인', '안산', '안양']
    # big_city = df.iloc[:,drop_list]
    df.drop(drop_list, axis=1, level=0, inplace=True)
    df.drop(drop_list2, axis=1, level=0, inplace=True)
    # drop_list3 = df.columns[df.columns.get_level_values(0).str.endswith('군')]
    # df.drop(drop_list3, axis=1, inplace=True)
    # df = df[df.columns[~df.columns.get_level_values(0).str.endswith('군')]]
    
    return df, org_df

@st.cache
def load_index_data():
    kbm_dict = read_source()
    # kbm_dict = pd.ExcelFile(file_path)
    #헤더 변경
    path = 'https://github.com/sizipusx/fundamental/blob/d91daa59a4409bd9281172d2a1d46a56b27fac2a/files/header.xlsx?raw=true'
    header_excel = pd.ExcelFile(path)
    header = header_excel.parse('KB')
    code_df = header_excel.parse('code', index_col=1)
    code_df.index = code_df.index.str.strip()

    #주택가격지수
    mdf = kbm_dict.parse("2.매매APT", skiprows=1, index_col=0, convert_float=True)
    jdf = kbm_dict.parse("6.전세APT", skiprows=1, index_col=0, convert_float=True)
    mdf.columns = header.columns
    jdf.columns = header.columns
    #index 날짜 변경
    
    mdf = mdf.iloc[2:]
    jdf = jdf.iloc[2:]
    index_list = list(mdf.index)

    new_index = []

    for num, raw_index in enumerate(index_list):
        temp = str(raw_index).split('.')
        if int(temp[0]) > 12 :
            if len(temp[0]) == 2:
                new_index.append('19' + temp[0] + '.' + temp[1])
            else:
                new_index.append(temp[0] + '.' + temp[1])
        else:
            new_index.append(new_index[num-1].split('.')[0] + '.' + temp[0])

    mdf.set_index(pd.to_datetime(new_index), inplace=True)
    jdf.set_index(pd.to_datetime(new_index), inplace=True)
    mdf = mdf.astype(float).fillna(0).round(decimals=2)
    jdf = jdf.astype(float).fillna(0).round(decimals=2)

    #geojson file open
    geo_source = 'https://raw.githubusercontent.com/sizipusx/fundamental/main/sigungu_json.geojson'
    with urlopen(geo_source) as response:
        geo_data = json.load(response)
    
    #geojson file 변경
    for idx, sigun_dict in enumerate(geo_data['features']):
        sigun_id = sigun_dict['properties']['SIG_CD']
        sigun_name = sigun_dict['properties']['SIG_KOR_NM']
        try:
            sell_change = df.loc[(df.SIG_CD == sigun_id), '매매증감'].iloc[0]
            jeon_change = df.loc[(df.SIG_CD == sigun_id), '전세증감'].iloc[0]
        except:
            sell_change = 0
            jeon_change =0
        # continue
        
        txt = f'<b><h4>{sigun_name}</h4></b>매매증감: {sell_change:.2f}<br>전세증감: {jeon_change:.2f}'
        # print(txt)
        
        geo_data['features'][idx]['id'] = sigun_id
        geo_data['features'][idx]['properties']['sell_change'] = sell_change
        geo_data['features'][idx]['properties']['jeon_change'] = jeon_change
        geo_data['features'][idx]['properties']['tooltip'] = txt
   
    return mdf, jdf, code_df, geo_data

@st.cache
def load_pop_data():
    popheader = pd.read_csv("https://raw.githubusercontent.com/sizipusx/fundamental/main/popheader.csv")
    #인구수 
    pop = pd.read_csv('https://raw.githubusercontent.com/sizipusx/fundamental/main/files/pop.csv', encoding='euc-kr')
    pop['행정구역'] = popheader
    pop = pop.set_index("행정구역")
    pop = pop.iloc[:,3:]
    test = pop.columns.str.replace(' ','').map(lambda x : x.replace('월','.01'))
    pop.columns = test
    df = pop.T
    # df = df.iloc[:-1]
    df.index = pd.to_datetime(df.index)
    df_change = df.pct_change()*100
    df_change = df_change.round(decimals=2)
    #세대수
    sae = pd.read_csv('https://raw.githubusercontent.com/sizipusx/fundamental/main/files/saedae.csv', encoding='euc-kr')
    sae['행정구역'] = popheader
    sae = sae.set_index("행정구역")
    sae = sae.iloc[:,3:]
    sae.columns = test
    sdf = sae.T
    # sdf = sdf.iloc[:-1]
    sdf.index = pd.to_datetime(sdf.index)
    sdf_change = sdf.pct_change()*100
    sdf_change = sdf_change.round(decimals=2)

    ## 2021. 9. 23 완공 후 미분양 데이터 가져오기
    path = 'https://github.com/sizipusx/fundamental/blob/a6f1a49d1f29dfb8d1234f8ca1fc88bbbacb0532/files/not_sell_7.xlsx?raw=true'
    data_type = 'Sheet1' 
    df1 = pd.read_excel(path, sheet_name=data_type, index_col=0, parse_dates=True)

    #컬럼명 바꿈
    j1 = df1.columns
    new_s1 = []
    for num, gu_data in enumerate(j1):
        check = num
        if gu_data.startswith('Un'):
            new_s1.append(new_s1[check-1])
        else:
            new_s1.append(j1[check])

    #컬럼 설정
    df1.columns = [new_s1,df1.iloc[0]]
    df1 = df1.iloc[2:]
    df1 = df1.sort_index()
    df1 = df1.astype(int)

    return df, df_change, sdf, sdf_change, df1

@st.cache
def load_senti_data():
    kbm_dict = read_source_excel()

    m_sheet = '21.매수우위,22.매매거래,23.전세수급,24.전세거래,25.KB부동산 매매가격 전망지수,26.KB부동산 전세가격 전망지수'
    m_list = m_sheet.split(',')
    df_dic = []
    df_a = []
    df_b = []

    for k in kbm_dict.keys():
        js = kbm_dict[k]
        # print(f"sheet name is {k}")

        if k in m_list:
            print(f"sheet name is {k}")
            js = js.set_index("Unnamed: 0")
            js.index.name="날짜"

            #컬럼명 바꿈
            j1 = js.columns.map(lambda x: x.split(' ')[0])

            new_s1 = []
            for num, gu_data in enumerate(j1):
                check = num
                if gu_data.startswith('Un'):
                    new_s1.append(new_s1[check-1])
                else:
                    new_s1.append(j1[check])

            #컬럼 설정
            js.columns = [new_s1,js.iloc[0]]

            #전세수급지수만 filtering
            if k == '21.매수우위':
                js_index = js.xs("매수우위지수", axis=1, level=1)
                js_a = js.xs("매도자 많음", axis=1, level=1)
                js_b = js.xs("매수자 많음", axis=1, level=1)
            elif k == '22.매매거래':
                js_index = js.xs("매매거래지수", axis=1, level=1)
                js_a = js.xs("활발함", axis=1, level=1)
                js_b = js.xs("한산함", axis=1, level=1)
            elif k == '23.전세수급':
                js_index = js.xs("전세수급지수", axis=1, level=1)
                js_a = js.xs("수요>공급", axis=1, level=1)
                js_b = js.xs("수요<공급", axis=1, level=1)
            elif k == '24.전세거래':
                js_index = js.xs("전세거래지수", axis=1, level=1)
                js_a = js.xs("활발함", axis=1, level=1)
                js_b = js.xs("한산함", axis=1, level=1)
            elif k == '25.KB부동산 매매가격 전망지수':
                js_index = js.xs("KB부동산\n매매전망지수", axis=1, level=1)
                js_a = js.xs("약간상승", axis=1, level=1)
                js_b = js.xs("약간하락", axis=1, level=1)
            elif k == '26.KB부동산 전세가격 전망지수':
                js_index = js.xs("KB부동산\n전세전망지수", axis=1, level=1)
                js_a = js.xs("약간상승", axis=1, level=1)
                js_b = js.xs("약간하락", axis=1, level=1)
            #필요 데이터만
            js_index = js_index.iloc[2:js_index['서울'].count(), : ]
            js_a = js_a.iloc[2:js_a['서울'].count(), : ]
            js_b = js_b.iloc[2:js_b['서울'].count(), : ]

            #날짜 바꿔보자
            index_list = list(js_index.index)
            new_index = []

            for num, raw_index in enumerate(index_list):
                temp = str(raw_index).split('.')
                if len(temp[0]) == 3:
                    if int(temp[0].replace("'","")) >84:
                        new_index.append('19' + temp[0].replace("'","") + '.' + temp[1])
                    else:
                        new_index.append('20' + temp[0].replace("'","") + '.' + temp[1])
                else:
                    new_index.append(new_index[num-1].split('.')[0] + '.' + temp[0])

            js_index.set_index(pd.to_datetime(new_index), inplace=True)
            js_a.set_index(pd.to_datetime(new_index), inplace=True)
            js_b.set_index(pd.to_datetime(new_index), inplace=True)

                
            #매달 마지막 데이터만 넣기
            # js_last = js_index.iloc[-1].to_frame().T
            df_dic.append(js_index)
            df_a.append(js_a)
            df_b.append(js_b)

    return df_dic, df_a, df_b
##########################################
mdf, jdf, code_df, geo_data = load_index_data()
popdf, popdf_change, saedf, saedf_change, not_sell = load_pop_data()
b_df, org_df = load_buy_data()
peong_df, peong_ch, peongj_df, peongj_ch, ratio_df = load_ratio_data()

#마지막 달
kb_last_month = pd.to_datetime(str(mdf.index.values[-1])).strftime('%Y.%m')
pop_last_month = pd.to_datetime(str(popdf.index.values[-1])).strftime('%Y.%m')
buy_last_month = pd.to_datetime(str(b_df.index.values[-1])).strftime('%Y.%m')
st.write("KB last month: " + kb_last_month+"월")
st.write("인구수 last month: " + pop_last_month+"월")
st.write("매입자 거주지별 매매현황 last month: " + buy_last_month+"월")

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
last_pop['세대증감'] = saedf_change.iloc[-1].T.to_frame()
last_pop.columns = ['인구증감', '세대증감']
last_pop.dropna(inplace=True)
last_pop = last_pop.round(decimals=2) 

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
cum_ch = (mdf_change/100 +1).cumprod()
jcum_ch = (jdf_change/100 +1).cumprod()
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

#KB 전세가율 마지막 데이터
one_last_df = ratio_df.iloc[-1].T.to_frame()
sub_df = one_last_df[one_last_df.iloc[:,0] >= 70.0]
# st.dataframe(sub_df)
sub_df.columns = ['전세가율']
sub_df = sub_df.sort_values('전세가율', ascending=False )



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
<h1 style="font-size:300%; color:#008080; font-family:Georgia"> Korea Local House Index <br>
 <h2 style="color:#008080; font-family:Georgia"> DASHBOARD</h3> <br>
 <hr style= "  display: block;
  margin-top: 0.5em;
  margin-bottom: 0.5em;
  margin-left: auto;
  margin-right: auto;
  border-style: inset;
  border-width: 1.5px;"></h1>
"""

html_card_header1="""
<div class="card">
  <div class="card-body" style="border-radius: 10px 10px 0px 0px; background: #eef9ea; padding-top: 5px; width: 350px;
   height: 50px;">
    <h3 class="card-title" style="background-color:#eef9ea; color:#008080; font-family:Georgia; text-align: center; padding: 0px 0;">Global Actual Progress</h3>
  </div>
</div>
"""
html_card_footer1="""
<div class="card">
  <div class="card-body" style="border-radius: 0px 0px 10px 10px; background: #eef9ea; padding-top: 1rem;; width: 350px;
   height: 50px;">
    <p class="card-title" style="background-color:#eef9ea; color:#008080; font-family:Georgia; text-align: center; padding: 0px 0;">Baseline 46%</p>
  </div>
</div>
"""
html_card_header2="""
<div class="card">
  <div class="card-body" style="border-radius: 10px 10px 0px 0px; background: #eef9ea; padding-top: 5px; width: 350px;
   height: 50px;">
    <h3 class="card-title" style="background-color:#eef9ea; color:#008080; font-family:Georgia; text-align: center; padding: 0px 0;">Global Spend Hours</h3>
  </div>
</div>
"""
html_card_footer2="""
<div class="card">
  <div class="card-body" style="border-radius: 0px 0px 10px 10px; background: #eef9ea; padding-top: 1rem;; width: 350px;
   height: 50px;">
    <p class="card-title" style="background-color:#eef9ea; color:#008080; font-family:Georgia; text-align: center; padding: 0px 0;">Baseline 92.700</p>
  </div>
</div>
"""
html_card_header3="""
<div class="card">
  <div class="card-body" style="border-radius: 10px 10px 0px 0px; background: #eef9ea; padding-top: 5px; width: 350px;
   height: 50px;">
    <h3 class="card-title" style="background-color:#eef9ea; color:#008080; font-family:Georgia; text-align: center; padding: 0px 0;">TCPI</h3>
  </div>
</div>
"""
html_card_footer3="""
<div class="card">
  <div class="card-body" style="border-radius: 0px 0px 10px 10px; background: #eef9ea; padding-top: 1rem;; width: 350px;
   height: 50px;">
    <p class="card-title" style="background-color:#eef9ea; color:#008080; font-family:Georgia; text-align: center; padding: 0px 0;">To Complete Performance Index ≤ 1.00</p>
  </div>
</div>
"""
### first select box ----
senti_dfs, df_as, df_bs = load_senti_data()
city_list = senti_dfs[0].columns.to_list()

selected_disc = st.selectbox(' Select 광역시도', city_list)
html_br="""
<br>
"""
st.markdown(html_br, unsafe_allow_html=True)
### Block 1#########################################################################################
with st.beta_container():
    col1, col2, col3, col4, col5, col6, col7 = st.beta_columns([1,30,1,30,1])
    with col1:
        st.write("")
    with col2:
        drawAPT.draw_sentimental_index(selected_dosi, senti_dfs, df_as, df_bs, mdf_change)
    with col3:
        st.write("")
    with col4:
        st.markdown(html_card_header2, unsafe_allow_html=True)
        fig_c2 = go.Figure(go.Indicator(
            mode="number+delta",
            value=73500,
            number={'suffix': " HH", "font": {"size": 40, 'color': "#008080", 'family': "Arial"}, 'valueformat': ',f'},
            delta={'position': "bottom", 'reference': 92700},
            domain={'x': [0, 1], 'y': [0, 1]}))
        fig_c2.update_layout(autosize=False,
                             width=350, height=90, margin=dict(l=20, r=20, b=20, t=30),
                             paper_bgcolor="#fbfff0", font={'size': 20})
        fig_c2.update_traces(delta_decreasing_color="#3D9970",
                             delta_increasing_color="#FF4136",
                             delta_valueformat='f',
                             selector=dict(type='indicator'))
        st.plotly_chart(fig_c2)
        st.markdown(html_card_footer2, unsafe_allow_html=True)
    with col5:
        st.write("")
html_br="""
<br>
"""
st.markdown(html_br, unsafe_allow_html=True)


html_card_header4="""
<div class="card">
  <div class="card-body" style="border-radius: 10px 10px 0px 0px; background: #eef9ea; padding-top: 5px; width: 250px;
   height: 50px;">
    <h4 class="card-title" style="background-color:#eef9ea; color:#008080; font-family:Georgia; text-align: center; padding: 10px 0;">Global Actual Progress</h4>
  </div>
</div>
"""
html_card_footer4="""
<div class="card">
  <div class="card-body" style="border-radius: 0px 0px 10px 10px; background: #eef9ea; padding-top: 1rem;; width: 250px;
   height: 50px;">
    <p class="card-title" style="background-color:#eef9ea; color:#008080; font-family:Georgia; text-align: center; padding: 0px 0;">Montly Value (%)</p>
  </div>
</div>
"""
html_card_header5="""
<div class="card">
  <div class="card-body" style="border-radius: 10px 10px 0px 0px; background: #eef9ea; padding-top: 5px; width: 250px;
   height: 50px;">
    <h4 class="card-title" style="background-color:#eef9ea; color:#008080; font-family:Georgia; text-align: center; padding: 10px 0;">Global Spend Hours</h4>
  </div>
</div>
"""
html_card_footer5="""
<div class="card">
  <div class="card-body" style="border-radius: 0px 0px 10px 10px; background: #eef9ea; padding-top: 1rem;; width: 250px;
   height: 50px;">
    <p class="card-title" style="background-color:#eef9ea; color:#008080; font-family:Georgia; text-align: center; padding: 0px 0;">Montly Relative Change (%)</p>
  </div>
</div>
"""


### Block 2#########################################################################################
with st.beta_container():
    col1, col2, col3, col4, col5, col6, col7 = st.beta_columns([1,10,1,10,1,20,1])
    with col1:
        st.write("")
    with col2:
        st.markdown(html_card_header4, unsafe_allow_html=True)
        x = ['Actual', 'Previous', 'Average', 'Planned']
        y = [5.5, 4.2, 6.3, 8.5]
        fig_m_prog = go.Figure([go.Bar(x=x, y=y, text=y, textposition='auto')])
        fig_m_prog.update_layout(paper_bgcolor="#fbfff0", plot_bgcolor="#fbfff0",
                                 font={'color': "#008080", 'family': "Arial"}, height=100, width=250,
                                 margin=dict(l=15, r=1, b=4, t=4))
        fig_m_prog.update_yaxes(title='y', visible=False, showticklabels=False)
        fig_m_prog.update_traces(marker_color='#17A2B8', selector=dict(type='bar'))
        st.plotly_chart(fig_m_prog)
        st.markdown(html_card_footer4, unsafe_allow_html=True)
    with col3:
        st.write("")
    with col4:
        st.markdown(html_card_header5, unsafe_allow_html=True)
        x = ['Δ vs Prev', 'Δ vs Aver', 'Δ vs Plan']
        y = [10, 12, 8]
        fig_m_hh = go.Figure([go.Bar(x=x, y=y, text=y, textposition='auto')])
        fig_m_hh.update_layout(paper_bgcolor="#fbfff0", plot_bgcolor="#fbfff0",
                               font={'color': "#008080", 'family': "Arial"}, height=100, width=250,
                               margin=dict(l=15, r=1, b=1, t=1))
        fig_m_hh.update_yaxes(title='y', visible=False, showticklabels=False)
        fig_m_hh.update_traces(marker_color='#17A2B8', selector=dict(type='bar'))
        st.plotly_chart(fig_m_hh)
        st.markdown(html_card_footer5, unsafe_allow_html=True)
    with col5:
        st.write("")
    with col6:
        y = data.loc[data.Activity_name == 'Total']
        # Create traces
        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(x=y['Date'], y=y['Progress'],
                                  mode='lines',
                                  name='Progress',
                                  marker_color='#FF4136'))
        fig3.add_trace(go.Scatter(x=y['Date'], y=y['Baseline'],
                                  mode='lines',
                                  name='Baseline',
                                  marker_color='#17A2B8'))
        fig3.update_layout(title={'text': "Actual Progress vs Planned", 'x': 0.5}, paper_bgcolor="#fbfff0",
                           plot_bgcolor="#fbfff0", font={'color': "#008080", 'size': 12, 'family': "Georgia"}, height=220,
                           width=540,
                           legend=dict(orientation="h",
                                       yanchor="top",
                                       y=0.99,
                                       xanchor="left",
                                       x=0.01),
                           margin=dict(l=1, r=1, b=1, t=30))
        fig3.update_xaxes(showline=True, linewidth=1, linecolor='#F7F7F7', mirror=True, nticks=6, rangemode="tozero",
                          showgrid=False, gridwidth=0.5, gridcolor='#F7F7F7')
        fig3.update_yaxes(showline=True, linewidth=1, linecolor='#F7F7F7', mirror=True, nticks=10, rangemode="tozero",
                          showgrid=True, gridwidth=0.5, gridcolor='#F7F7F7')
        fig3.layout.yaxis.tickformat = ',.0%'
        st.plotly_chart(fig3)
    with col7:
        st.write("")

html_br="""
<br>
"""
st.markdown(html_br, unsafe_allow_html=True)

html_card_header6="""
<div class="card">
  <div class="card-body" style="border-radius: 10px 10px 0px 0px; background: #eef9ea; padding-top: 5px; width: 250px;
   height: 50px;">
    <h4 class="card-title" style="background-color:#eef9ea; color:#008080; font-family:Georgia; text-align: center; padding: 10px 0;">Cost Variance</h4>
  </div>
</div>
"""
html_card_footer6="""
<div class="card">
  <div class="card-body" style="border-radius: 0px 0px 10px 10px; background: #eef9ea; padding-top: 1rem;; width: 250px;
   height: 50px;">
    <p class="card-title" style="background-color:#eef9ea; color:#008080; font-family:Georgia; text-align: center; padding: 0px 0;">Montly Value </p>
  </div>
</div>
"""
html_card_header7="""
<div class="card">
  <div class="card-body" style="border-radius: 10px 10px 0px 0px; background: #eef9ea; padding-top: 5px; width: 250px;
   height: 50px;">
    <h4 class="card-title" style="background-color:#eef9ea; color:#008080; font-family:Georgia; text-align: center; padding: 10px 0;">Schedule Variance</h4>
  </div>
</div>
"""
html_card_footer7="""
<div class="card">
  <div class="card-body" style="border-radius: 0px 0px 10px 10px; background: #eef9ea; padding-top: 1rem;; width: 250px;
   height: 50px;">
    <p class="card-title" style="background-color:#eef9ea; color:#008080; font-family:Georgia; text-align: center; padding: 0px 0;">Montly Value</p>
  </div>
</div>
"""

### Block 3#########################################################################################
with st.beta_container():
    col1, col2, col3, col4, col5, col6, col7 = st.beta_columns([1,10,1,10,1,20,1])
    with col1:
        st.write("")
    with col2:
        st.markdown(html_card_header6, unsafe_allow_html=True)
        fig_cv = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=1.05,
            number={"font": {"size": 22, 'color': "#008080", 'family': "Arial"}, "valueformat": "#,##0"},
            domain={'x': [0, 1], 'y': [0, 1]},
            gauge={
                'axis': {'range': [None, 1.5], 'tickwidth': 1, 'tickcolor': "black"},
                'bar': {'color': "#06282d"},
                'bgcolor': "white",
                'steps': [
                    {'range': [0, 1], 'color': '#FF4136'},
                    {'range': [1, 1.5], 'color': '#3D9970'}]}))

        fig_cv.update_layout(paper_bgcolor="#fbfff0", font={'color': "#008080", 'family': "Arial"}, height=135, width=250,
                             margin=dict(l=10, r=10, b=15, t=20))
        st.plotly_chart(fig_cv)
        st.markdown(html_card_footer6, unsafe_allow_html=True)
    with col3:
        st.write("")
    with col4:
        st.markdown(html_card_header7, unsafe_allow_html=True)
        fig_sv = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=0.95,
            number={"font": {"size": 22, 'color': "#008080", 'family': "Arial"}, "valueformat": "#,##0"},
            domain={'x': [0, 1], 'y': [0, 1]},
            gauge={
                'axis': {'range': [None, 1.5], 'tickwidth': 1, 'tickcolor': "black"},
                'bar': {'color': "#06282d"},
                'bgcolor': "white",
                'steps': [
                    {'range': [0, 1], 'color': '#FF4136'},
                    {'range': [1, 1.5], 'color': '#3D9970'}]}))
        fig_sv.update_layout(paper_bgcolor="#fbfff0", font={'color': "#008080", 'family': "Arial"}, height=135, width=250,
                             margin=dict(l=10, r=10, b=15, t=20))
        st.plotly_chart(fig_sv)
        st.markdown(html_card_footer7, unsafe_allow_html=True)
    with col5:
        st.write("")
    with col6:
        y = data.loc[data.Activity_name == 'Total']
        y = data.loc[data.Activity_name == 'Total']
        fig_hh = go.Figure()
        fig_hh.add_trace(go.Bar(
            x=y['Date'],
            y=y['Spend_Hours'],
            name='Spend Hours',
            marker_color='#FF4136'
        ))
        fig_hh.add_trace(go.Bar(
            x=y['Date'],
            y=y['Planned_Hours'],
            name='Planned Hours',
            marker_color='#17A2B8'
        ))
        fig_hh.update_layout(barmode='group', title={'text': 'Spend Hours vs Planned', 'x': 0.5}, paper_bgcolor="#fbfff0",
                             plot_bgcolor="#fbfff0", font={'color': "#008080", 'family': "Georgia"}, height=250, width=540,
                             legend=dict(orientation="h",
                                         yanchor="top",
                                         y=0.99,
                                         xanchor="left",
                                         x=0.01),
                             margin=dict(l=5, r=1, b=1, t=25))
        fig_hh.update_xaxes(showline=True, linewidth=1, linecolor='#F7F7F7', mirror=True, nticks=6, rangemode="tozero",
                            showgrid=False, gridwidth=0.5, gridcolor='#F7F7F7')
        fig_hh.update_yaxes(showline=True, linewidth=1, linecolor='#F7F7F7', mirror=True, nticks=10, rangemode="tozero",
                            showgrid=False, gridwidth=0.5, gridcolor='#F7F7F7')
        st.plotly_chart(fig_hh)
    with col7:
        st.write("")

html_br="""
<br>
"""
st.markdown(html_br, unsafe_allow_html=True)

html_subtitle="""
<h2 style="color:#008080; font-family:Georgia;"> Details by Discipline: </h2>
"""
st.markdown(html_subtitle, unsafe_allow_html=True)

html_table=""" 
<table>
  <tr style="background-color:#eef9ea; color:#008080; font-family:Georgia; font-size: 15px">
    <th style="width:130px">Discipline</th>
    <th style="width:90px">Baseline</th>
    <th style="width:90px">Progress</th>
    <th style="width:90px">Manpower</th>
    <th style="width:90px">Cost Variance</th>
    <th style="width:90px">Schedule Variance</th>
  </tr>
  <tr style="height: 40px; color:#008080; font-size: 14px">
    <th>Civil</th>
    <th>70,00%</th>
    <th>68,50%</th>
    <th>70.000</th>
    <th>0,99</th>
    <th>1,09</th>
  </tr>
  <tr style="background-color:#eef9ea; height: 40px; color:#008080; font-size: 14px">
    <th>Mechanical</th>
    <th>50,00%</th>
    <th>45,50%</th>
    <th>10.000</th>
    <th>0,95</th>
    <th>0,98</th>
  </tr>
  <tr style="height: 40px; color:#008080; font-size: 14px">
    <th>Piping</th>
    <th>30,00%</th>
    <th>30,00%</th>
    <th>60.000</th>
    <th>0,99</th>
    <th>1,01</th>
  </tr>
  <tr style="background-color:#eef9ea; height: 40px; color:#008080; font-size: 14px">
    <th>Electricity</th>
    <th>20,00%</th>
    <th>15,00%</th>
    <th>40.000</th>
    <th>0,90</th>
    <th>0,98</th>
  </tr>
  <tr style="height: 40px; color:#008080; font-size: 14px">
    <th>Intrumentation</th>
    <th>5,00%</th>
    <th>0,00%</th>
    <th>30.000</th>
    <th>-</th>
    <th>-</th>
  </tr>
  <tr style="background-color:#eef9ea; height: 40px; color:#008080; font-size: 14px">
    <th>Commissioning</th>
    <th>0,00%</th>
    <th>0,00%</th>
    <th>15.000</th>
    <th>-</th>
    <th>-</th>
  </tr>
  <tr style="height: 40px; color:#008080; font-size: 15px">
    <th>Total</th>
    <th>35,00%</th>
    <th>46,00%</th>
    <th>225.000</th>
    <th>0,97</th>
    <th>0,91</th>
  </tr>
</table>
"""
### Block 4#########################################################################################
with st.beta_container():
    col1, col2, col3 = st.beta_columns([12,1,12])
    with col1:
        st.markdown(html_table, unsafe_allow_html=True)
    with col2:
        st.write("")
    with col3:
        # *******Gantt Chart
        df = pd.DataFrame([
            dict(Disc="Civ", Start='2021-01-04', Finish='2021-08-10'),
            dict(Disc="Mec", Start='2021-03-05', Finish='2021-09-15'),
            dict(Disc="Pip", Start='2021-04-20', Finish='2021-11-30'),
            dict(Disc="Ele", Start='2021-05-20', Finish='2021-12-05'),
            dict(Disc="Ins", Start='2021-06-20', Finish='2021-12-20'),
            dict(Disc="Com", Start='2021-07-20', Finish='2021-12-30')
        ])
        fig2 = px.timeline(df, x_start="Start", x_end="Finish", y='Disc')
        fig2.update_yaxes(autorange="reversed")
        fig2.update_layout(title={'text': "Main dates", 'x': 0.5}, plot_bgcolor="#eef9ea", paper_bgcolor="#eef9ea",
                           font={'color': "#008080", 'family': "Georgia"}, height=340, width=550, margin=dict(
                l=51, r=5, b=10, t=50))
        fig2.update_traces(marker_color='#17A2B8', selector=dict(type='bar'))
        st.plotly_chart(fig2)

disciplinas= ['Civil', 'Mechanical', 'Piping', 'Electricity', 'Instrumentation', 'Commissioning']

selected_disc = st.selectbox(' Select discipline', disciplinas)
html_br="""
<br>
"""
st.markdown(html_br, unsafe_allow_html=True)

html_card_header4="""
<div class="card">
  <div class="card-body" style="border-radius: 10px 10px 0px 0px; background: #eef9ea; padding-top: 10px; width: 250px;
   height: 50px;">
    <h5 class="card-title" style="background-color:#eef9ea; color:#008080; font-family:Georgia; text-align: center; padding: 5px 0;">Progress For Selected Discipline</h5>
  </div>
</div>
"""
html_card_footer4="""
<div class="card">
  <div class="card-body" style="border-radius: 0px 0px 10px 10px; background: #eef9ea; padding-top: 1rem;; width: 250px;
   height: 50px;">
    <p class="card-title" style="background-color:#eef9ea; color:#008080; font-family:Georgia; text-align: center; padding: 0px 0;">Montly Value (%)</p>
  </div>
</div>
"""
html_card_header5="""
<div class="card">
  <div class="card-body" style="border-radius: 10px 10px 0px 0px; background: #eef9ea; padding-top: 10px; width: 250px;
   height: 50px;">
    <h5 class="card-title" style="background-color:#eef9ea; color:#008080; font-family:Georgia; text-align: center; padding: 5px 0;">Spend Hours For Selected Discipline</h5>
  </div>
</div>
"""
html_card_footer5="""
<div class="card">
  <div class="card-body" style="border-radius: 0px 0px 10px 10px; background: #eef9ea; padding-top: 1rem;; width: 250px;
   height: 50px;">
    <p class="card-title" style="background-color:#eef9ea; color:#008080; font-family:Georgia; text-align: center; padding: 0px 0;">Montly Relative Change (%)</p>
  </div>
</div>
"""


### Block 5#########################################################################################
with st.beta_container():
    col1, col2, col3, col4, col5, col6, col7 = st.beta_columns([1,10,1,10,1,20,1])
    with col1:
        st.write("")
    with col2:
        st.markdown(html_card_header4, unsafe_allow_html=True)
        x = ['Actual', 'Previous', 'Average', 'Planned']
        y = [5.5, 4.2, 6.3, 8.5]
        fig_m_prog = go.Figure([go.Bar(x=x, y=y, text=y, textposition='auto')])
        fig_m_prog.update_layout(paper_bgcolor="#fbfff0", plot_bgcolor="#fbfff0",
                                 font={'color': "#008080", 'family': "Arial"}, height=100, width=250,
                                 margin=dict(l=15, r=1, b=4, t=4))
        fig_m_prog.update_yaxes(title='y', visible=False, showticklabels=False)
        fig_m_prog.update_traces(marker_color='#17A2B8', selector=dict(type='bar'))
        st.plotly_chart(fig_m_prog)
        st.markdown(html_card_footer4, unsafe_allow_html=True)
    with col3:
        st.write("")
    with col4:
        st.markdown(html_card_header5, unsafe_allow_html=True)
        x = ['Δ vs Prev', 'Δ vs Aver', 'Δ vs Plan']
        y = [10, 12, 8]
        fig_m_hh = go.Figure([go.Bar(x=x, y=y, text=y, textposition='auto')])
        fig_m_hh.update_layout(paper_bgcolor="#fbfff0", plot_bgcolor="#fbfff0",
                               font={'color': "#008080", 'family': "Arial"}, height=100, width=250,
                               margin=dict(l=15, r=1, b=1, t=1))
        fig_m_hh.update_yaxes(title='y', visible=False, showticklabels=False)
        fig_m_hh.update_traces(marker_color='#17A2B8', selector=dict(type='bar'))
        st.plotly_chart(fig_m_hh)
        st.markdown(html_card_footer5, unsafe_allow_html=True)
    with col5:
        st.write("")
    with col6:
        y = data.loc[data.Activity_name == 'Total']
        # Create traces
        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(x=y['Date'], y=y['Progress'],
                                  mode='lines',
                                  name='Progress',
                                  marker_color='#FF4136'))
        fig3.add_trace(go.Scatter(x=y['Date'], y=y['Baseline'],
                                  mode='lines',
                                  name='Baseline',
                                  marker_color='#17A2B8'))
        fig3.update_layout(title={'text': "Actual Progress vs Planned", 'x': 0.5}, paper_bgcolor="#fbfff0",
                           plot_bgcolor="#fbfff0", font={'color': "#008080", 'size': 12, 'family': "Georgia"}, height=220,
                           width=540,
                           legend=dict(orientation="h",
                                       yanchor="top",
                                       y=0.99,
                                       xanchor="left",
                                       x=0.01),
                           margin=dict(l=1, r=1, b=1, t=30))
        fig3.update_xaxes(showline=True, linewidth=1, linecolor='#F7F7F7', mirror=True, nticks=6, rangemode="tozero",
                          showgrid=False, gridwidth=0.5, gridcolor='#F7F7F7')
        fig3.update_yaxes(showline=True, linewidth=1, linecolor='#F7F7F7', mirror=True, nticks=10, rangemode="tozero",
                          showgrid=True, gridwidth=0.5, gridcolor='#F7F7F7')
        fig3.layout.yaxis.tickformat = ',.0%'
        st.plotly_chart(fig3)
    with col7:
        st.write("")

html_br="""
<br>
"""
st.markdown(html_br, unsafe_allow_html=True)

html_card_header6="""
<div class="card">
  <div class="card-body" style="border-radius: 10px 10px 0px 0px; background: #eef9ea; padding-top: 10px; width: 250px;
   height: 50px;">
    <h5 class="card-title" style="background-color:#eef9ea; color:#008080; font-family:Georgia; text-align: center; padding: 5px 0;">Cost Variance For Selected Discipline</h5>
  </div>
</div>
"""
html_card_footer6="""
<div class="card">
  <div class="card-body" style="border-radius: 0px 0px 10px 10px; background: #eef9ea; padding-top: 1rem;; width: 250px;
   height: 50px;">
    <p class="card-title" style="background-color:#eef9ea; color:#008080; font-family:Georgia; text-align: center; padding: 0px 0;">Montly Value </p>
  </div>
</div>
"""
html_card_header7="""
<div class="card">
  <div class="card-body" style="border-radius: 10px 10px 0px 0px; background: #eef9ea; padding-top: 5px; width: 250px;
   height: 50px;">
    <h5 class="card-title" style="background-color:#eef9ea; color:#008080; font-family:Georgia; text-align: center; padding: 8px 0;">Schedule Variance For Selected Discipline</h5>
  </div>
</div>
"""
html_card_footer7="""
<div class="card">
  <div class="card-body" style="border-radius: 0px 0px 10px 10px; background: #eef9ea; padding-top: 1rem;; width: 250px;
   height: 50px;">
    <p class="card-title" style="background-color:#eef9ea; color:#008080; font-family:Georgia; text-align: center; padding: 0px 0;">Montly Value</p>
  </div>
</div>
"""
html_card_header8="""
<div class="card">
  <div class="card-body" style="border-radius: 10px 10px 0px 0px; background: #eef9ea; padding-top: 5px; width: 550px;
   height: 50px;">
    <h5 class="card-title" style="background-color:#eef9ea; color:#008080; font-family:Georgia; text-align: center; padding: 10px 0;">Main Issues By Discipline</h5>
  </div>
</div>
"""

html_list="""
<ul style="color:#008080; font-family:Georgia; font-size: 15px">
  <li>Nulla volutpat aliquam velit</li>
  <li>Maecenas sed diam eget risus varius blandit</li>
  <li>Etiam porta sem malesuada magna mollis euismod</li>
  <li>Fusce dapibus, tellus ac cursus commodo</li>
  <li>Maecenas sed diam eget risus varius blandit</li>
</ul> 
"""

### Block 6#########################################################################################
with st.beta_container():
    col1, col2, col3, col4, col5, col6, col7 = st.beta_columns([1,10,1,10,1,20,1])
    with col1:
        st.write("")
    with col2:
        st.markdown(html_card_header6, unsafe_allow_html=True)
        fig_cv = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=1.05,
            number={"font": {"size": 22, 'color': "#008080", 'family': "Arial"}, "valueformat": "#,##0"},
            domain={'x': [0, 1], 'y': [0, 1]},
            gauge={
                'axis': {'range': [None, 1.5], 'tickwidth': 1, 'tickcolor': "black"},
                'bar': {'color': "#06282d"},
                'bgcolor': "white",
                'steps': [
                    {'range': [0, 1], 'color': '#FF4136'},
                    {'range': [1, 1.5], 'color': '#3D9970'}]}))

        fig_cv.update_layout(paper_bgcolor="#fbfff0", font={'color': "#008080", 'family': "Arial"}, height=135, width=250,
                             margin=dict(l=10, r=10, b=15, t=20))
        st.plotly_chart(fig_cv)
        st.markdown(html_card_footer6, unsafe_allow_html=True)
    with col3:
        st.write("")
    with col4:
        st.markdown(html_card_header7, unsafe_allow_html=True)
        fig_sv = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=0.95,
            number={"font": {"size": 22, 'color': "#008080", 'family': "Arial"}, "valueformat": "#,##0"},
            domain={'x': [0, 1], 'y': [0, 1]},
            gauge={
                'axis': {'range': [None, 1.5], 'tickwidth': 1, 'tickcolor': "black"},
                'bar': {'color': "#06282d"},
                'bgcolor': "white",
                'steps': [
                    {'range': [0, 1], 'color': '#FF4136'},
                    {'range': [1, 1.5], 'color': '#3D9970'}]}))
        fig_sv.update_layout(paper_bgcolor="#fbfff0", font={'color': "#008080", 'family': "Arial"}, height=135, width=250,
                             margin=dict(l=10, r=10, b=15, t=20))
        st.plotly_chart(fig_sv)
        st.markdown(html_card_footer7, unsafe_allow_html=True)
    with col5:
        st.write("")
    with col6:
        st.markdown(html_card_header8, unsafe_allow_html=True)
        st.markdown(html_list, unsafe_allow_html=True)
    with col7:
        st.write("")

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
<p style="color:Gainsboro; text-align: right;">By: larryprato@gmail.com</p>
"""
st.markdown(html_line, unsafe_allow_html=True)