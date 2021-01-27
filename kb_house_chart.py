
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
def load_index_data():
    kb_dict = pd.read_excel('D:/OneDrive - 호매실고등학교/데이터/WeeklySeriesTables(시계열)_20210118.xlsx', sheet_name=None, header=1)

    mdf = kb_dict['매매지수']
    jdf = kb_dict['전세지수']
    #헤더 변경
    path = r'D:/code/powerbi/data/KB/KB헤더.xlsx'
    data_type = 'KB시도구' 
    header = pd.read_excel(path, sheet_name=data_type)

    mdf.columns = header.columns
    mdf = mdf.drop([0])
    mdf.set_index("KB주간", inplace=True)

    jdf.columns = header.columns
    jdf = jdf.drop([0])
    jdf.set_index("KB주간", inplace=True)
   
    return mdf, jdf

@st.cache
def load_senti_data():
    kb_dict = pd.read_excel('./data/WeeklySeriesTables(시계열).xlsx', sheet_name=None, header=1)

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

    return js


def run_price_index() :

    # 챠트 기본 설정 
    marker_colors = ['#34314c', '#47b8e0', '#ffc952', '#ff7473']
    template = 'seaborn' #"plotly", "plotly_white", "plotly_dark", "ggplot2", "seaborn", "simple_white", "none".

    titles = dict(text= '('+selected_city2 +') 주간 매매-전세 지수', x=0.5, y = 0.9) 

    fig = make_subplots(specs=[[{'secondary_y': True}]]) 
    
    fig.add_trace(go.Bar(name = '매매지수증감', x = mdf.index, y = mdf_change[selected_city2], marker_color=  marker_colors[1]), secondary_y = True)
    fig.add_trace(go.Bar(name = '전세지수증감', x = jdf.index, y = jdf_change[selected_city2], marker_color=  marker_colors[2]), secondary_y = True)

    
    fig.add_trace(go.Scatter(mode='lines', name = '매매지수', x =  mdf.index, y= mdf[selected_city2],
                                text= mdf[selected_city2], textposition = 'top center', marker_color = marker_colors[0]),# marker_colorscale='RdBu'),
                                secondary_y = False)
    fig.add_trace(go.Scatter(mode='lines', name ='전세지수', x =  jdf.index, y= jdf[selected_city2],
                                text= jdf[selected_city2], textposition = 'top center', marker_color = marker_colors[3]),# marker_colorscale='RdBu'),
                                secondary_y = False)
    fig.update_traces(texttemplate='%{text:.3s}') 
    fig.update_yaxes(title_text='지수', showticklabels= True, showgrid = True, zeroline=False,  secondary_y = False) #ticksuffix="%"
    fig.update_yaxes(title_text='지수 증감', showticklabels= True, showgrid = False, zeroline=True, zerolinecolor='LightPink', secondary_y = True, ticksuffix="%") #tickprefix="$", 
    fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template)
    fig.update_layout(
            showlegend=True,
            legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
            xaxis=go.layout.XAxis(
            rangeselector=dict(
                buttons=list([
                    dict(count=6,
                        label="6m",
                        step="month",
                        stepmode="backward"),
                    dict(count=1,
                        label="YTD",
                        step="year",
                        stepmode="todate"),
                    dict(count=1,
                        label="1y",
                        step="year",
                        stepmode="backward"),
                    dict(count=5,
                        label="5y",
                        step="year",
                        stepmode="backward"),
                    dict(count=10,
                        label="10y",
                        step="year",
                        stepmode="backward"),
                    dict(step="all")
                ])
            ),
            rangeslider=dict(
                visible=True
            ),
            type="date"
            )      
        )
    st.plotly_chart(fig)

def run_sentimental_index():
    # st.dataframe(senti_df)
     # 챠트 기본 설정 
    # marker_colors = ['#34314c', '#47b8e0', '#ffc952', '#ff7473']
    marker_colors = ['rgb(27,38,81)', 'rgb(205,32,40)', 'rgb(22,108,150)', 'rgb(255,255,255)', 'rgb(237,234,255)']
    template = 'seaborn' #"plotly", "plotly_white", "plotly_dark", "ggplot2", "seaborn", "simple_white", "none".

    titles = dict(text= ' 매수매도 우위 지수('+ selected_dosi + ')', x=0.5, y = 0.9) 

    fig = make_subplots(specs=[[{'secondary_y': True}]]) 
    
    # fig.add_trace(go.Bar(name = '매매지수증감', x = mdf.index, y = mdf_change[selected_city2], marker_color=  marker_colors[1]), secondary_y = True)
    # fig.add_trace(go.Bar(name = '전세지수증감', x = jdf.index, y = jdf_change[selected_city2], marker_color=  marker_colors[2]), secondary_y = True)
    # fig.add_trace(go.Bar(name = '전세지수증감', x = jdf.index, y = jdf_change[selected_city2], marker_color=  marker_colors[2]), secondary_y = True)

    
    fig.add_trace(go.Scatter(line = dict(dash='dash'), name = '매도자 많음', x =  js_1.index, y= js_1[selected_dosi],
                                text= js_1[selected_dosi], textposition = 'top center', marker_color = marker_colors[0]),# marker_colorscale='RdBu'),
                                secondary_y = False)
    fig.add_trace(go.Scatter(line = dict(dash='dot'), name ='매수자 많음', x =  js_2.index, y= js_2[selected_dosi],
                                text= js_2[selected_dosi], textposition = 'top center', marker_color = marker_colors[2]),# marker_colorscale='RdBu'),
                                secondary_y = False)
    fig.add_trace(go.Scatter(mode='lines', name ='매수매도 지수', x =  js_index.index, y= js_index[selected_dosi],
                                text= js_index[selected_dosi], textposition = 'top center', marker_color = marker_colors[1]),# marker_colorscale='RdBu'),
                                secondary_y = False)
    fig.update_traces(texttemplate='%{text:.3s}') 
    fig.update_yaxes(title_text='지수', showticklabels= True, showgrid = True, zeroline=True, zerolinecolor='LightPink', secondary_y = False) #ticksuffix="%"
    # fig.update_yaxes(title_text='매매지수', showticklabels= True, showgrid = False, zeroline=False, secondary_y = False) #tickprefix="$", 
    fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template)
    fig.add_vrect(x0="2017-08-07", x1="2017-08-14", 
              annotation_text="8.2 대책", annotation_position="top left",
              fillcolor="green", opacity=0.25, line_width=0)
    fig.add_vrect(x0="2018-09-17", x1="2018-10-01", 
              annotation_text="9.13 대책", annotation_position="top left",
              fillcolor="green", opacity=0.25, line_width=0)
    fig.add_vrect(x0="2019-12-16", x1="2020-02-24", 
              annotation_text="12.16/2.24 대책", annotation_position="top left",
              fillcolor="green", opacity=0.25, line_width=0)
    fig.add_vrect(x0="2020-06-22", x1="2020-07-13", 
              annotation_text="6.17/7.10 대책", annotation_position="top left",
              fillcolor="green", opacity=0.25, line_width=0)
    fig.add_vrect(x0="2020-08-10", x1="2020-08-17", 
              annotation_text="8.4 대책", annotation_position="bottom left",
              fillcolor="green", opacity=0.25, line_width=0)
    fig.update_layout(
            showlegend=True,
            legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
            xaxis=go.layout.XAxis(
            rangeselector=dict(
                buttons=list([
                    dict(count=6,
                        label="6m",
                        step="month",
                        stepmode="backward"),
                    dict(count=1,
                        label="YTD",
                        step="year",
                        stepmode="todate"),
                    dict(count=1,
                        label="1y",
                        step="year",
                        stepmode="backward"),
                    dict(count=5,
                        label="5y",
                        step="year",
                        stepmode="backward"),
                    dict(count=10,
                        label="10y",
                        step="year",
                        stepmode="backward"),
                    dict(step="all")
                ])
            ),
            rangeslider=dict(
                visible=True
            ),
            type="date"
            )      
        )
    st.plotly_chart(fig)




if __name__ == "__main__":
    st.title("KB 부동산 주간 시계열 분석")
    data_load_state = st.text('Loading 매매/전세 index Data...')
    mdf, jdf = load_index_data()
    data_load_state.text("매매/전세 index Data Done! (using st.cache)")

    #주간 증감률
    mdf_change = mdf.pct_change()*100
    jdf_change = jdf.pct_change()*100
    #일주일 간 상승률 순위
    last_df = mdf_change.iloc[-2].T.to_frame()
    last_df['전세증감'] = jdf_change.iloc[-2].T.to_frame()
    last_df.columns = ['매매증감', '전세증감']
    last_df.dropna(inplace=True)
    
    fig = go.Figure([go.Bar(x=last_df.index, y=last_df.iloc[:,0])])
    fig.add_hline(y=last_df.iloc[0,0], line_dash="dot", line_color="green", annotation_text="전국 증감률", 
                annotation_position="bottom right")
    fig.update_traces(texttemplate='%{text:.2s}', textposition='outside')
    fig.update_yaxes(title_text='주간 매매지수 증감률', showticklabels= True, showgrid = True, zeroline=True, zerolinecolor='LightPink', ticksuffix="%")
    fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
    st.plotly_chart(fig)
    st.dataframe(last_df.T.style.highlight_max(axis=1))

    with st.beta_container():
        #매매/전세 증감률 Bubble Chart
        fig1 = px.scatter(last_df, x='매매증감', y='전세증감', color='매매증감', size=abs(last_df['전세증감']), 
                            text= last_df.index, hover_name=last_df.index)
        fig1.update_yaxes(zeroline=True, zerolinecolor='LightPink', ticksuffix="%")
        fig1.update_xaxes(zeroline=True, zerolinecolor='LightPink', ticksuffix="%")

        st.plotly_chart(fig1)


    #여기서부터는 선택
    my_choice = st.sidebar.radio(
                    "What' are you gonna do?", ('Price Index', 'Sentiment analysis')
                    )
    if my_choice == 'Price Index':

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
            run_price_index()
    else:
        data_load_state = st.text('Loading 매수매도 index Data...')
        senti_df = load_senti_data()
        data_load_state.text("매수매도 index Data Done! (using st.cache)")

        js_1 = senti_df.xs("매도자많음", axis=1, level=1)
        js_2 = senti_df.xs("매수자많음", axis=1, level=1)
        js_index = senti_df.xs("매수우위지수", axis=1, level=1)

        # city_list = ['전국', '서울', '강북', '강남', '6개광역시','5개광역시','부산','대구','인천','광주','대전','울산',,'수도권','세종', \
        #             '경기도', '강원도', '충청북도', '전라북도', '전라남도', '경상북도','경상남도','기타지방','제주']
        column_list = js_index.columns.to_list()
        selected_dosi = st.sidebar.selectbox(
                '광역시-도', column_list
            )
        submit = st.sidebar.button('Draw Sentimental Index chart')
        if submit:
            run_sentimental_index()
    
    
    
