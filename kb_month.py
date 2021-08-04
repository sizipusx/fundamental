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

import drawAPT


pd.set_option('display.float_format', '{:.2f}'.format)
#오늘날짜까지
now = datetime.now()
today = '%s-%s-%s' % ( now.year, now.month, now.day)

#return object
def read_source(): 
    # file_path = 'G:/내 드라이브/code/data/★(월간)KB주택가격동향_시계열(2021.04)_A지수통계.xlsx'
    file_path = 'https://github.com/sizipusx/fundamental/blob/fb0c90dfdc04ef44f3bbd3bfe528d3eccb6f3029/files/KB_monthlyA.xlsx?raw=true'
    kbm_dict = pd.ExcelFile(file_path)

    return kbm_dict

 #return dic
def read_source_excel():
    # file_path = 'G:/내 드라이브/code/data/★(월간)KB주택가격동향_시계열(2021.04)_A지수통계.xlsx'
    file_path = 'https://github.com/sizipusx/fundamental/blob/fb0c90dfdc04ef44f3bbd3bfe528d3eccb6f3029/files/KB_monthlyA.xlsx?raw=true'
    kbm_dict = pd.read_excel(file_path, sheet_name=None, header=1)

    return kbm_dict

@st.cache
def load_ratio_data():
    file_path = 'https://raw.githubusercontent.com/sizipusx/fundamental/main/files/sell_jeon_ration.csv'
    ratio_df = pd.read_csv(file_path, skiprows=1)
    ratio_df.iloc[1,0] = '날짜'
    header_path = 'https://github.com/sizipusx/fundamental/blob/e78f57d1a884c56721c2df612c32e1e73e88dd1f/files/one_header.xlsx?raw=true'
    one_header = pd.read_excel(header_path, sheet_name="시도구")

    #컬럼명 바꿈
    j1 = ratio_df.columns.map(lambda x: x.split(' ')[0])
    new_s1 = []
    for num, gu_data in enumerate(j1):
        check = num
        if gu_data.startswith('Un'):
            new_s1.append(new_s1[check-1])
        else:
            new_s1.append(j1[check])
    new_s1[0] = "date"
    ratio_df.columns = [new_s1, ratio_df.iloc[1]]
    df = ratio_df.iloc[4:ratio_df[('전국', '중위')].count()]
    df = df.set_index([('date', '날짜')])
    df.index = pd.to_datetime(df.index)
    df.index.name = 'date'
    df = df.astype(float).round(decimals = 2)

    return df, one_header


@st.cache
def load_buy_data():
    #년 증감 계산을 위해 최소 12개월치 데이터 필요
    path = r'https://github.com/sizipusx/fundamental/blob/19cd2dd417f037c8dca2611ebe88896b9abb78b4/files/apt_buy.xlsx?raw=true'
    data_type = 'Sheet1' 
    df = pd.read_excel(path, sheet_name=data_type, header=10)
    path1 = r'https://github.com/sizipusx/fundamental/blob/130612c3436245a3202de78375eb12ecc712e8d9/files/kbheader.xlsx?raw=true'
    header = pd.read_excel(path1, sheet_name='buyer')
    df['지 역'] = header['local'].str.strip()
    df = df.rename({'지 역':'지역명'}, axis='columns')
    df.drop(['Unnamed: 1', 'Unnamed: 2'], axis=1, inplace=True)
    df = df.set_index("지역명")
    df = df.T
    df.columns = [df.columns, df.iloc[0]]
    df = df.iloc[1:]
    df.index = df.index.map(lambda x: x.replace('년','-').replace(' ','').replace('월', '-27'))
    df.index = pd.to_datetime(df.index)
    df = df.apply(lambda x: x.replace('-','0'))
    df = df.astype(float)
    org_df = df.copy()
    drop_list = ['전국', '서울', '경기', '경북', '경남', '전남', '전북', '강원', '대전', '대구', '인천', '광주', '부산', '울산', '세종 세종','충남', '충북']
    drop_list2 = ['수원', '성남', '천안', '청주', '전주', '고양', '창원', '포항', '용인', '안산', '부천', '안양']
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
    path = 'https://github.com/sizipusx/fundamental/blob/130612c3436245a3202de78375eb12ecc712e8d9/files/kbheader.xlsx?raw=true'
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
    test = pop.columns.str.replace(' ','').map(lambda x : x.replace('월','.27'))
    pop.columns = test
    df = pop.T
    df = df.iloc[:-1]
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
    sdf = sdf.iloc[:-1]
    sdf.index = pd.to_datetime(sdf.index)
    sdf_change = sdf.pct_change()*100
    sdf_change = sdf_change.round(decimals=2)

    return df, df_change, sdf, sdf_change

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
    pir = kbm_dict.parse('14.NEW_HAI', skiprows=1)
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
    st.title("KB 부동산 월간 시계열 분석")
    data_load_state = st.text('Loading index & pop Data...')
    mdf, jdf, code_df, geo_data = load_index_data()
    popdf, popdf_change, saedf, saedf_change = load_pop_data()
    b_df, org_df = load_buy_data()
    ratio_df, one_header = load_ratio_data()
    data_load_state.text("index & pop Data Done! (using st.cache)")

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
    
    #감정원 전세가율 마지막 데이터
    middle_df = ratio_df.xs("중위", axis=1, level=1)
    middle_df.columns = one_header.columns[1:]
    one_last_df = middle_df.iloc[-1].T.to_frame()
    sub_df = one_last_df[one_last_df.iloc[:,0] >= 70.0]
    # st.dataframe(sub_df)
    sub_df.columns = ['전세가율']
    sub_df = sub_df.sort_values('전세가율', ascending=False )

    #여기서부터는 선택
    my_choice = st.sidebar.radio(
                    "Select Menu", ('Basic','Price Index', 'PIR','HAI', 'Sentiment analysis')
                    )
    if my_choice == 'Basic':
        submit = st.sidebar.button('Draw Basic chart')
        if submit:
            drawAPT.draw_basic(last_df, df, geo_data, last_pop, power_df)
            drawAPT.run_buy_basic(b_df, org_df)
    elif my_choice == 'Price Index':
        st.subheader("전세파워 높고 버블지수 낮은 지역 상위 20곳")
        st.table(power_df.iloc[:20])
        st.subheader("전세가율이 70% 이상 전국 상위 20곳")
        st.table(sub_df.iloc[:20])
        city_list = ['전국', '서울', '6개광역시','부산','대구','인천','광주','대전','울산','5개광역시','수도권','세종','경기', '수원', \
                    '성남','고양', '안양', '부천', '의정부', '광명', '평택','안산', '과천', '구리', '남양주', '용인', '시흥', '군포', \
                    '의왕','하남','오산','파주','이천','안성','김포', '양주','동두천','경기광주', '화성','강원', '춘천','강릉', '원주', \
                    '충북','청주', '충주','제천', '충남','천안', '공주','아산', '논산', '계룡','당진','서산', '전북', '전주', '익산', '군산', \
                    '전남', '목포','순천','여수','광양','경북','포항','구미', '경산', '안동','김천','경남','창원', '양산','거제','진주', \
                    '김해','통영', '제주도','제주서귀포','기타지방']
        column_list = mdf.columns.to_list()
        city_series = pd.Series(column_list)
        selected_city = st.sidebar.selectbox(
                '광역시-도-시', city_list
            )
        second_list = city_series[city_series.str.contains(selected_city)].to_list()
        selected_city2 = st.sidebar.selectbox(
                '구-시', second_list
            )
        # if  st.checkbox('Show 매매지수 data'):
        #     st.dataframe(mdf.style.highlight_max(axis=0))
        
        submit = st.sidebar.button('Draw Price Index chart')

        if submit:
            drawAPT.run_pop_index(selected_city2, popdf, popdf_change, saedf, saedf_change)
            drawAPT.run_ratio_index(selected_city2, middle_df)
            drawAPT.run_buy_index(selected_city2, b_df, mdf)
            drawAPT.run_price_index(selected_city2, mdf, jdf, mdf_change, jdf_change, bubble_df2, m_power)
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
            drawAPT.draw_pir(selected_city, pir_df, income_df, price_df)
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
            drawAPT.draw_hai(selected_city, hai_df, info_df)
    else:
        data_load_state = st.text('Loading Sentimental index Data...')
        senti_dfs, df_as, df_bs = load_senti_data()
        data_load_state.text("Sentimental index Data Done! (using st.cache)")

        city_list = senti_dfs[0].columns.to_list()
        
        selected_dosi = st.sidebar.selectbox(
                '광역시-도', city_list
            )
        submit = st.sidebar.button('Draw Sentimental Index chart')
        if submit:
            drawAPT.draw_sentimental_index(selected_dosi, senti_dfs, df_as, df_bs)