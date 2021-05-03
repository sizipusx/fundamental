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

def read_source():
    # file_path = 'G:/내 드라이브/code/data/★(월간)KB주택가격동향_시계열(2021.04)_A지수통계.xlsx'
    file_path = 'https://github.com/sizipusx/fundamental/blob/eba3275f50fdb23c63261956010df5ec03076143/(%EC%9B%94%EA%B0%84)KB%EC%A3%BC%ED%83%9D%EA%B0%80%EA%B2%A9%EB%8F%99%ED%96%A5_%EC%8B%9C%EA%B3%84%EC%97%B4(2021.04)_A%EC%A7%80%EC%88%98%ED%86%B5%EA%B3%84.xlsx?raw=true'
    kbm_dict = pd.ExcelFile(file_path)

    return kbm_dict

@st.cache
def load_index_data():
    kbm_dict = read_source()
    # kbm_dict = pd.ExcelFile(file_path)
    #헤더 변경
    path = 'https://github.com/sizipusx/fundamental/blob/36d7cf8622721b020fac048866aa02d88509186b/kbheader.xlsx?raw=true'
    header_excel = pd.ExcelFile(path)
    header = header_excel.parse('KB')
    code_df = header_excel.parse('code', index_col=1)
    code_df.index = code_df.index.str.strip()

    #주택가격지수
    mdf = kbm_dict.parse("매매APT", skiprows=1, index_col=0, convert_float=True)
    jdf = kbm_dict.parse("전세APT", skiprows=1, index_col=0, convert_float=True)
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
    mdf = mdf.round(decimals=2)
    jdf = jdf.round(decimals=2)

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
    st.dataframe(popheader)
     #인구수 
    pop = pd.read_csv('https://raw.githubusercontent.com/sizipusx/fundamental/main/pop.csv', skiprows=1)
    pop['행정구역'] = popheader
    pop = pop.set_index("행정구역")
    pop = pop.iloc[:,3:]
    test = pop.columns.str.replace(' ','').map(lambda x : x.replace('월','.01'))
    pop.columns = test
    df = pop.T
    df.index = pd.to_datetime(df.index)
    df_change = df.pct_change()*100
    df_change = df_change.round(decimals=2)
    #세대수
    sae = pd.read_csv('https://raw.githubusercontent.com/sizipusx/fundamental/main/saedae.csv', encoding='euc-kr', skiprows=1)
    sae['행정구역'] = popheader
    sae = sae.set_index("행정구역")
    sae = sae.iloc[:,3:]
    sae.columns = test
    sdf = sae.T
    sdf.index = pd.to_datetime(sdf.index)
    sdf_change = sdf.pct_change()*100
    sdf_change = sdf_change.round(decimals=2)

    return df, df_change, sdf, sdf_change

@st.cache
def load_senti_data():
    kb_dict = pd.read_excel(file_path, sheet_name=None, header=1)

    js = kb_dict['매수매도']
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
    js = js.round(decimals=2)

    return js

@st.cache
def load_pir_data():
    file_path = 'https://github.com/sizipusx/fundamental/blob/eba3275f50fdb23c63261956010df5ec03076143/(%EC%9B%94%EA%B0%84)KB%EC%A3%BC%ED%83%9D%EA%B0%80%EA%B2%A9%EB%8F%99%ED%96%A5_%EC%8B%9C%EA%B3%84%EC%97%B4(2021.04)_A%EC%A7%80%EC%88%98%ED%86%B5%EA%B3%84.xlsx?raw=true'
    kb_dict = pd.read_excel(file_path, sheet_name=None, header=1)
    pir =  kb_dict['KB아파트담보대출PIR']
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
    hai = kbm_dict.parse('NEW_HAI', skiprows=1)
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
    data_load_state.text("index & pop Data Done! (using st.cache)")

    #월간 증감률
    mdf_change = mdf.pct_change()*100
    mdf_change = mdf_change.astype(float)
    mdf_change = mdf_change.iloc[1:]
    jdf_change = jdf.pct_change()*100
    jdf_change = jdf_change.iloc[1:]
    jdf_change = jdf_change.astype(float)
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
    bubble_df2 = bubble_df2.round(decimals=5)*100
    # st.dataframe(bubble_df2)

    #전세 파워 만들기
    cum_ch = (mdf_change/100 +1).cumprod()
    jcum_ch = (jdf_change/100 +1).cumprod()
    m_power = (jcum_ch - cum_ch)*100
    

    #여기서부터는 선택
    my_choice = st.sidebar.radio(
                    "What' are you gonna do?", ('Basic','Price Index', 'PIR','HAI', 'Sentiment analysis')
                    )
    if my_choice == 'Basic':
        submit = st.sidebar.button('Draw Basic chart')
        if submit:
            drawAPT.draw_basic(last_df, df, geo_data, last_pop)

    elif my_choice == 'Price Index':
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
            drawAPT.run_price_index(selected_city2, mdf, jdf, mdf_change, jdf_change, bubble_df2, m_power)
    elif my_choice == 'PIR':
        data_load_state = st.text('Loading PIR index Data...')
        pir_df, income_df, price_df = load_pir_data()
        data_load_state.text("PIR index Data Done! (using st.cache)")
        st.write("* <b>PIR(Price to income ratio)= 주택가격/가구소득</b>")
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
        data_load_state.text("HAI index Data Done! (using st.cache)")
        st.write("<b>주택구매력지수(HAI)  Housing affordability index</b>")
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
        data_load_state = st.text('Loading 매수매도 index Data...')
        # senti_df = load_senti_data()
        data_load_state.text("매수매도 index Data Done! (using st.cache)")

        # js_1 = senti_df.xs("매도자많음", axis=1, level=1)
        # js_2 = senti_df.xs("매수자많음", axis=1, level=1)
        # js_index = senti_df.xs("매수우위지수", axis=1, level=1)

        # # city_list = ['전국', '서울', '강북', '강남', '6개광역시','5개광역시','부산','대구','인천','광주','대전','울산',,'수도권','세종', \
        # #             '경기도', '강원도', '충청북도', '전라북도', '전라남도', '경상북도','경상남도','기타지방','제주']
        # column_list = js_index.columns.to_list()
        # selected_dosi = st.sidebar.selectbox(
        #         '광역시-도', column_list
        #     )
        # submit = st.sidebar.button('Draw Sentimental Index chart')
        # if submit:
        #     run_sentimental_index()