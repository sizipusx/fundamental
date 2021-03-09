
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
import FinanceDataReader as fdr

pd.set_option('display.float_format', '{:.2f}'.format)
#오늘날짜까지
now = datetime.now()
today = '%s-%s-%s' % ( now.year, now.month, now.day)

@st.cache
def load_trade_data():
    #년 증감 계산을 위해 최소 12개월치 데이터 필요
    path = r'D:/OneDrive - 호매실고등학교/down/월별_매입자거주지별_아파트매매거래_동호수.xlsx'
    data_type = 'Sheet1' 
    df = pd.read_excel(path, sheet_name=data_type, header=10)

    path1 = r'D:/code/powerbi/data/감정원/매입자거주지별_헤더.xlsx'
    data_type = 'Sheet1' 
    header = pd.read_excel(path1, sheet_name=data_type)

    df['지 역'] = header['지역명']
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
    drop_list = ['전국', '서울', '경기', '경북', '경남', '전남', '전북', '강원', '대전', '대구', '인천', '광주', '부산', '울산', '세종','충남', '충북']
    df.drop(drop_list, axis=1, inplace=True)
    df = df[df.columns[~df.columns.get_level_values(0).str.endswith('군')]]

    return df, org_df

@st.cache
def drop_columns(org_df):
     #도와 광역시, 군 제외
    drop_list = ['전국', '서울', '경기', '경북', '경남', '전남', '전북', '강원', '대전', '대구', '인천', '광주', '부산', '울산', '세종', '충남', '충북']
    df = org_df.copy()
    df.drop(drop_list, axis=1, inplace=True)
    drop_gun = org_df.columns[~org_df.columns.str.endswith('군')]
    df1 = df[drop_gun]

    return df1


if __name__ == "__main__":
    st.title("아파트 매입자 거주지별 매매 분석")
    data_load_state = st.text('Loading 매입자 거주지별 매매 Data...')
    df, org_df = load_trade_data()
    data_load_state.text("Done 매입자 거주지별 매매 Data(using st.cache)")
    # st.dataframe(org_df)

    #개별로 나눠보자
    df_total = df.xs('합계',axis=1, level=1)
    df_si = df.xs('관할시군구내',axis=1, level=1)
    df_do = df.xs('관할시도내',axis=1, level=1)
    df_seoul = df.xs('관할시도외_서울',axis=1, level=1)
    df_etc = df.xs('관할시도외_기타',axis=1, level=1)

    ## q증감률
    df_total_ch = df_total.pct_change()*100
    df_total_yoy = df_total.pct_change(12)

    df_si_ch = df_si.pct_change()*100
    df_si_yoy = df_si.pct_change(12)

    df_do_ch = df_do.pct_change()*100
    df_do_yoy = df_do.pct_change(12)

    df_seoul_ch = df_seoul.pct_change()*100
    df_seoul_yoy = df_seoul.pct_change(12)

    df_etc_ch = df_etc.pct_change()*100
    df_etc_yoy = df_etc.pct_change(12)

    ### 증감량
    df_total_amt = df_total - df_total.shift(1)
    df_si_amt = df_si - df_si.shift(1)
    df_do_amt = df_do - df_do.shift(1)
    df_seoul_amt = df_seoul - df_seoul.shift(1)
    df_etc_amt = df_etc - df_etc.shift(1)

    #투자자 합산
    df_outer = df_seoul.add(df_etc)
    df_outer_amt = df_outer.sub(df_outer.shift(1))
    df_outer_ch = df_outer.pct_change()*100
    df_outer_yoy = df_outer.pct_change(12)*100
    #dropping NaN,  infinite values 
    df_outer_ch.replace([np.inf, -np.inf], np.nan, inplace=True)
    df_outer_ch.fillna(0,inplace=True)
    df_outer_yoy.replace([np.inf, -np.inf], np.nan, inplace=True)
    df_outer_yoy.fillna(0,inplace=True)

    #mom, yoy 투자자 변화
    change_df = df_outer_ch.iloc[-1].T.to_frame()
    change_df['YoY'] = df_outer_yoy.iloc[-1].T.to_frame()
    change_df.columns = ['MoM', 'YoY']
    #평균이 10이하인 지역은 제외하자
    change_df['mean'] = df_outer.mean()
    change_df2 = round(change_df[change_df['mean'] > 10],1)

    #한달간 투자자 변동 순위
    last_df = df_seoul.iloc[-1].T.to_frame()
    last_df['기타지역'] = df_etc.iloc[-1].T.to_frame()
    last_df.columns = ['서울매수자', '기타지역매수자']

     #챠트 기본 설정
    # colors 
    marker_colors = ['#34314c', '#47b8e0', '#ff7473', '#ffc952', '#3ac569']
    # marker_colors = ['rgb(27,38,81)', 'rgb(205,32,40)', 'rgb(22,108,150)', 'rgb(255,69,0)', 'rgb(237,234,255)']
    template = 'seaborn' #"plotly", "plotly_white", "plotly_dark", "ggplot2", "seaborn", "simple_white", "none"
    #마지막 달
    last_month = pd.to_datetime(str(df_outer.index.values[-1])).strftime('%Y.%m')

    # box plot
    fig = px.box(df_outer,y=df_outer.columns, notched=True, title= "각 지역 통계(2006.1월~" + last_month +"월)")
    st.plotly_chart(fig)

    #최근 한달 동안 투자자 수가 가장 많이 유입된 곳 보기
    title = '최근 한달 동안 투자자가 가장 많이 유입된 곳'
    titles = dict(text= title, x=0.5, y = 0.9) 
    fig = go.Figure([go.Bar(x=df_outer.columns, y=df_outer.iloc[-1])])
    # fig.add_hline(y=df_outer.iloc[-1,0], line_dash="dot", line_color="green", annotation_text="전국 투자자 수", 
    #             annotation_position="bottom right")
    fig.update_traces(texttemplate='%{text:.2s}', textposition='outside')
    fig.update_yaxes(title_text='서울기타지역 투자자 수', showticklabels= True, showgrid = True, zeroline=True, zerolinecolor='LightPink', ticksuffix="명")
    fig.update_layout(title = titles, uniformtext_minsize=8, uniformtext_mode='hide')
    st.plotly_chart(fig)
    #최근 한달 동안 투자자 수 증감률이 가장 높은 곳 
    title = '최근 한달 동안 투자자수 증감률이 가장 높은 곳'
    titles = dict(text= title, x=0.5, y = 0.9) 
    fig = go.Figure([go.Bar(x=df_outer_ch.columns, y=df_outer_ch.iloc[-1,:])])
    fig.add_hline(y=df_outer_ch.iloc[-1,0], line_dash="dot", line_color="green", annotation_text="전국 투자자 증감률", 
                annotation_position="bottom right")
    fig.update_traces(texttemplate='%{text:.2s}', textposition='outside')
    fig.update_yaxes(title_text='서울기타지역 투자자 증감률', showticklabels= True, showgrid = True, zeroline=True, zerolinecolor='LightPink', ticksuffix="%")
    
    st.plotly_chart(fig)
    # st.dataframe(last_df.T.style.highlight_max(axis=1))

    with st.beta_container():
        #매매/전세 증감률 Bubble Chart
        title = last_month +"<b> 서울지역/기타지역 거주자 매수</b>"
        titles = dict(text= title, x=0.5, y = 0.95) 
        fig = px.scatter(last_df, x='서울매수자', y='기타지역매수자', color='기타지역매수자', color_continuous_scale='Bluered', size=last_df['서울매수자'], 
                            text= last_df.index, hover_name=last_df.index)
        fig.update_layout(title = titles, uniformtext_minsize=8, uniformtext_mode='hide')
        fig.update_yaxes(zeroline=True, zerolinecolor='LightPink', ticksuffix="명")
        fig.update_xaxes(zeroline=True, zerolinecolor='LightPink', ticksuffix="명")
        st.plotly_chart(fig)
    
    with st.beta_container():
        #매매/전세 증감률 Bubble Chart
        title = last_month +"<b> 투자자 MoM-YoY 증감률</b>"
        titles = dict(text= title, x=0.5, y = 0.95) 
        fig = px.scatter(change_df2, x='MoM', y='YoY', color='MoM', size='mean', 
                            text= change_df2.index, hover_name=change_df2.index)
        fig.update_yaxes(zeroline=True, zerolinecolor='LightPink', ticksuffix="%")
        fig.update_xaxes(zeroline=True, zerolinecolor='LightPink', ticksuffix="%")
        fig.update_layout(title = titles, uniformtext_minsize=8, uniformtext_mode='hide')
        st.plotly_chart(fig)


    #side bar 개별 지역 분석
    city_list = ['전국', '서울', '부산','대구','인천','광주','대전','울산','세종','경기', '강원', '충북','충남', \
                    '전북', '전남', '경북', '경남','제주']
    selected_city = st.sidebar.selectbox(
                        '광역시-도', city_list
                     )

    local_list = df.columns.get_level_values(0).to_list()
    new_list = []
    for v in local_list:
        if v not in new_list:
            new_list.append(v)
    city_series = pd.Series(new_list)  
    second_list = city_series[city_series.str.contains(selected_city)].to_list()
    selected_city2 = st.sidebar.selectbox(
            '구-시', second_list
        )
    selected_df = df.xs(selected_city2, axis=1, level=0)
    #make %
    per_df = round(selected_df.div(selected_df['합계'], axis=0)*100,1)
    title = "["+selected_city2+"] 매입자별 전체 거래량"
    titles = dict(text= title, x=0.5, y = 0.95) 
    fig = px.bar(selected_df, x=selected_df.index, y=["관할시군구내", "관할시도내", "관할시도외_서울", "관할시도외_기타"])
    fig.update_layout(title = titles, uniformtext_minsize=8, uniformtext_mode='hide')
    st.plotly_chart(fig)

    title = "["+selected_city2+"] 매입자별 비중"
    titles = dict(text= title, x=0.5, y = 0.95) 
    fig = px.bar(per_df, x=per_df.index, y=["관할시군구내", "관할시도내", "관할시도외_서울", "관할시도외_기타"])
    fig.update_yaxes(title= "매입자별 비중", zeroline=False, zerolinecolor='LightPink', ticksuffix="%")
    fig.update_layout(title = titles, uniformtext_minsize=8, uniformtext_mode='hide')
    st.plotly_chart(fig)
    #     submit = st.sidebar.button('Draw Sentimental Index chart')
    #     if submit:
    #         run_sentimental_index()