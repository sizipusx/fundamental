import time
from datetime import datetime

import numpy as np
import pandas as pd

import requests
from urllib.request import urlopen
import json
from pandas.io.json import json_normalize

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import streamlit as st
import FinanceDataReader as fdr
import drawAPT_update

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
<h1 style="font-size:200%; color:#008080; font-family:Georgia">  월간 부동산 시계열 분석 <br>
 <hr style= "  display: block;
  margin-top: 0.5em;
  margin-bottom: 0.5em;
  margin-left: auto;
  margin-right: auto;
  border-style: inset;
  border-width: 1.5px;"></h1>
"""

st.set_page_config(page_title="Monthly House Analysis", page_icon="", layout="wide")
st.markdown('<style>body{background-color: #fbfff0}</style>',unsafe_allow_html=True)
st.markdown(html_header, unsafe_allow_html=True)
st.markdown(""" <style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style> """, unsafe_allow_html=True)

pd.set_option('display.float_format', '{:.2f}'.format)
#오늘날짜까지
now = datetime.now()
today = '%s-%s-%s' % ( now.year, now.month, now.day)
header_path = 'https://github.com/sizipusx/fundamental/blob/ac28ce0cce4bbcf5892a7f2d1e566386944af9a3/files/header.xlsx?raw=True'
kb_file_path = 'https://github.com/sizipusx/fundamental/blob/51834c6c0c9101c9a51a565f1a96a50119c53a7d/files/kb_monthly.xlsx?raw=true'
#감정원 데이터
one_path = r"https://github.com/sizipusx/fundamental/blob/9dfcb5a5de327c4f73fc33544f1cfb8c94259eae/files/one_data.xlsx?raw=True"
#헤더 변경
header_path = 'https://github.com/sizipusx/fundamental/blob/00c7db01dd87012174224f5b9e89c24da4268d13/files/header.xlsx?raw=true'
header_excel = pd.ExcelFile(header_path)

#return object
def read_source(): 
    kbm_dict = pd.ExcelFile(kb_file_path)

    return kbm_dict

 #return dic
def read_source_excel():
    kbm_dict = pd.read_excel(kb_file_path, sheet_name=None, header=1)

    return kbm_dict

@st.cache
def load_index_data():
    kbm_dict = read_source()
    header_excel = pd.ExcelFile(header_path)
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

@st.cache(allow_output_mutation=True)
def load_one_data():
    #감정원 주간 데이터
    one_dict = pd.read_excel(one_path, sheet_name=None, header=1, dtype={'       지역\n\n\n\n\n 날짜': str})
    # one header 변경
    oneh = header_excel.parse('one')
    omdf = one_dict['msell_index']
    ojdf = one_dict['mjeon_index']
    omdf = omdf.iloc[3:omdf['전국'].count()+1,:]
    ojdf = ojdf.iloc[3:ojdf['전국'].count()+1,:]
    omdf.rename(columns={'       지역\n\n\n\n\n 날짜':'date'}, inplace=True)
    omdf['date'] = omdf['date'].str.slice(start=0, stop=10)
    omdf.index = pd.to_datetime(omdf['date'], format='%Y-%m-%d')
    omdf = omdf.iloc[:,1:]
    ojdf.rename(columns={'       지역\n\n\n\n\n 날짜':'date'}, inplace=True)
    ojdf['date'] = ojdf['date'].str.slice(start=0, stop=10)
    ojdf.index = pd.to_datetime(ojdf['date'], format='%Y-%m-%d')
    ojdf = ojdf.iloc[:,1:]
    omdf.columns = oneh.columns
    ojdf.columns = oneh.columns
    omdf = omdf.astype(float).round(decimals=2)
    ojdf = ojdf.astype(float).round(decimals=2)
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
    last_odf = last_odf.astype(float).fillna(0).round(decimals=3)
    #last_odf = last_odf.reset_index()
    basic_df = get_basic_df()
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
   
    return odf, one_geo_data, last_odf, omdf, ojdf, omdf_change, ojdf_change, cum_omdf, cum_ojdf

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

@st.cache
def load_pir_data():
    kbm_dict = read_source()
    pir = kbm_dict.parse('13.KB아파트담보대출PIR', skiprows=1)
    # file_path = 'https://github.com/sizipusx/fundamental/blob/75a46e5c6a1f343da71927fc6de0dd14fdf136eb/files/KB_monthly(6A).xlsx?raw=true'
    # kb_dict = pd.read_excel(file_path, sheet_name=None, header=1)
    # pir =  kb_dict['KB아파트담보대출PIR']
    pir = pir.iloc[:pir['지역'].count()-1,1:11]

    s1 = ['분기', '서울', '서울', '서울', '경기', '경기', '경기', '인천', '인천', '인천']
    s2 = pir.iloc[0]
    pir.columns = [s1, s2]
    pir = pir.iloc[1:]
    pir = pir.set_index(('분기',            '년도'))
    pir.index.name = '분기'
    #분기 날짜 바꾸기
    pir_index = list(pir.index)
    new_index = []

    for num, raw_index in enumerate(pir_index):
        temp = str(raw_index).split(' ')
        if len(temp[0]) == 3:
            if int(temp[0].replace("'","")) >84:
                new_index.append('19' + temp[0].replace("'","") + '.' + temp[1])
            else:
                if temp[1] == '1Q':
                    new_index.append('20' + temp[0].replace("'","") + '.03')
                elif temp[1] == '2Q':
                    new_index.append('20' + temp[0].replace("'","") + '.06')
                elif temp[1] == '3Q':
                    new_index.append('20' + temp[0].replace("'","") + '.09')
                else:
                    new_index.append('20' + temp[0].replace("'","") + '.12')
        else:
            if temp[0] == '1Q':
                new_index.append(new_index[num-1].split('.')[0] + '.03')
            elif temp[0] == '2Q':
                new_index.append(new_index[num-1].split('.')[0] + '.06')
            elif temp[0] == '3Q':
                new_index.append(new_index[num-1].split('.')[0] + '.09')
            else:
                new_index.append(new_index[num-1].split('.')[0] + '.12')
    ###각 지역 pir만
    pir_df = pir.xs("KB아파트 PIR", axis=1, level=1)
    pir_df.set_index(pd.to_datetime(new_index), inplace=True)
    ###가구소득
    income_df = pir.xs("가구소득(Income)", axis=1, level=1)
    income_df.set_index(pd.to_datetime(new_index), inplace=True)
    ###주택가격
    house_df = pir.xs("주택가격\n(Price)", axis=1, level=1)
    house_df.set_index(pd.to_datetime(new_index), inplace=True)
    pir_df.index.name = '분기'
    income_df.index.name = '분기'
    house_df.index.name = '분기'

    return pir_df, income_df, house_df

@st.cache
def load_hai_data():
    kbm_dict = read_source()
    hai = kbm_dict.parse('14.NEW_HAI', skiprows=1)
    hai_old = hai.iloc[:135,2:]
    hai_old = hai_old.set_index("지역")
    hai_old.index.name="날짜"
    hai_new = hai.iloc[144:hai['전국 Total'].count()-17,2:] ### 159 3월까지::: 달 증가에 따른 +1
    hai_new = hai_new.set_index("지역")
    hai_new.index.name="날짜"
    s1 = hai_new.columns.map(lambda x: x.split(' ')[0])
    #index 날짜 변경
    new_s1 = []
    for num, gu_data in enumerate(s1):
        check = num
        if gu_data.startswith('Un'):
            new_s1.append(new_s1[check-1])
        else:
            new_s1.append(s1[check])
    new_s1[-1] ='중위월소득'
    new_s1[-2] ='대출금리'
    hai_new.columns = [new_s1,hai_old.iloc[0]]
    hai_index = list(hai_new.index)
    #인덱스 날짜 변경
    new_index = []

    for num, raw_index in enumerate(hai_index):
        temp = str(raw_index).split('.')
        if len(temp[0]) == 3:
            if int(temp[0].replace("'","")) >84:
                new_index.append('19' + temp[0].replace("'","") + '.' + temp[1])
            else:
                new_index.append('20' + temp[0].replace("'","") + '.' + temp[1])
        else:
            new_index.append(new_index[num-1].split('.')[0] + '.' + temp[0])
    hai_new.set_index(pd.to_datetime(new_index), inplace=True)
    ###각 지역 HAI만
    hai_apt = hai_new.xs("아파트", axis=1, level=1)
    hai_apt.set_index(pd.to_datetime(new_index), inplace=True)
    ### 금리와 중위 소득만 가져오기
    info = hai_new.iloc[:,-2:]
    info.columns = ['주담대금리', '중위월소득']
    info.index.name="분기"
    info.loc[:,'중위월소득증감'] = info['중위월소득'].astype(int).pct_change()

    return hai_apt, info


if __name__ == "__main__":
    data_load_state = st.text('Loading index & pop Data...')
    mdf, jdf, code_df, geo_data = load_index_data()
    data_load_state.text("index & pop Data Done! (using st.cache)")

    #마지막 달
    kb_last_month = pd.to_datetime(str(mdf.index.values[-1])).strftime('%Y.%m')
    with st.expander("See recently Data Update"):
        cols = st.columns(3)
        cols[0].markdown(f'KB 최종업데이트: **{kb_last_month}월**')
        cols[1].markdown("")
        cols[2].markdown("")

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
                    "Select Menu", ('Basic','Price Index', 'PIR','HAI', 'Sentiment', 'local Analysis')
                    )
    if my_choice == 'Basic':
        st.subheader("전세파워 높고 버블지수 낮은 지역 상위 50곳")
        st.dataframe(power_df.iloc[:50])
        submit = st.button('Draw Basic chart')
        if submit:
            st.write("나중에 구현--그냥 테이블로 보여주기")
            #drawAPT_update.draw_basic(last_df, df, geo_data, last_ps, power_df)
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
            ### Block 플라워차트 추가 2021. 12. 26 #########################################################################################
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
    elif my_choice == 'HAI':
        data_load_state = st.text('Loading HAI index Data...')
        hai_df, info_df = load_hai_data()
        hai_df = hai_df.astype(float).fillna(0).round(decimals=2)
        info_df = info_df.astype(float).fillna(0).round(decimals=2)
        data_load_state.text("HAI index Data Done! (using st.cache)")
        st.subheader("주택구매력지수(HAI): Housing affordability index")
        st.write("* HAI = (중위가구소득 ÷ 대출상환가능소득) ×100 ")
        st.write("* 주택구매력지수란 우리나라에서 중간정도의 소득을 가진 가구가 금융기관의 대출을 받아 중간가격 정도의 주택을 구입한다고 가정할 때, \
            현재의 소득으로 대출원리금상환에 필요한 금액을 부담할 수 있는 능력을 의미")
        st.write("* HAI가 100보다 클수록 중간정도의 소득을 가진 가구가 중간가격 정도의 주택을 큰 무리없이 구입할 수 있다는 것을 나타내며, HAI가 상승하면 주택구매력이 증가한다는 것을 의미")
        st.write("* 발표시기 : 해당분기 익익월 보고서 발표(예 / 1분기 자료 ⇒ 5월 보고서 )")

        city_list = hai_df.columns.to_list()
        selected_city = st.sidebar.selectbox(
                '지역', city_list
            )
        submit = st.sidebar.button('Draw HAI chart')
        if submit:
            drawAPT_update.draw_hai(selected_city, hai_df, info_df)
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
            drawAPT_update.draw_sentimental_index(selected_dosi, senti_dfs, df_as, df_bs, mdf_change)
    else :

        city_list = ['전국', '서울', '강북', '강남', '6개광역시', '5개광역시', '부산', '대구', '인천', '광주', '대전',
                  '울산', '세종', '수도권', '경기', '강원', '충북', '충남', '전북', '전남', '경북', '경남', '기타지방', '제주서귀포']

        column_list = mdf.columns.to_list()
        city_series = pd.Series(column_list)
        selected_dosi = st.sidebar.selectbox(
                '광역시-도-시', city_list
            )
        
        #두번째 도시
        small_list = []
        mirco_list = []
        if selected_dosi == '전국':
            small_list = ['전국', '수도권', '기타지방']
        elif selected_dosi == '서울' or selected_dosi == '부산' or selected_dosi == '대구' or selected_dosi == '인천' or selected_dosi == '광주' \
            or selected_dosi == '대전' or selected_dosi == '울산' :
            small_list = city_series[city_series.str.contains(selected_dosi)].to_list()
        elif selected_dosi == '경기':
            small_list = ['경기', '수원', '성남','고양', '안양', '부천', '의정부', '광명', '평택','안산', '과천', '구리', '남양주', '용인', '시흥', '군포', \
                        '의왕','하남','오산','파주','이천','안성','김포', '양주','동두천','경기광주', '화성']
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
        elif selected_dosi == '제주서귀포':
            small_list = ['제주서귀포']
        elif selected_dosi == '세종':
            small_list = ['세종']
        
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
        
        submit = st.sidebar.button('Analize local index chart')
        if submit:
            drawAPT_update.run_local_analysis(mdf, mdf_change, selected_dosi, selected_dosi2, selected_dosi3, small_list)
