import time
from datetime import datetime
import drawAPT_weekly

import numpy as np
import pandas as pd

import requests
import json
from pandas.io.json import json_normalize
from urllib.request import urlopen

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import streamlit as st
import FinanceDataReader as fdr

import matplotlib.pyplot as plt
from matplotlib import font_manager, rc

# font_list = [font.name for font in font_manager.fontManager.ttflist]
# st.write(font_list)

plt.rc('font', family='DejaVu Sans') 
font = {'color':  'darkred',
        'weight': 'normal',
        'size': 16,
        }

pd.set_option('display.float_format', '{:.2f}'.format)
#오늘날짜까지
now = datetime.now()
today = '%s-%s-%s' % ( now.year, now.month, now.day)

# file_path = 'G:/내 드라이브/code/data/WeeklySeriesTables(시계열)_20210419.xlsx'
file_path = 'https://github.com/sizipusx/fundamental/blob/4d9df02dd84bad671825b7f359d717a0ba5860eb/files/WeeklySeriesTables.xlsx?raw=True'

@st.cache
def load_index_data():
    kb_dict = pd.ExcelFile(file_path)
    mdf = kb_dict.parse("매매지수", skiprows=1, index_col=0, parse_dates=True)
    jdf = kb_dict.parse("전세지수", skiprows=1, index_col=0, parse_dates=True)
    #헤더 변경
    path = 'https://github.com/sizipusx/fundamental/blob/80e5af9925c10a53b855cf6757fa1bba7eeb136d/files/header.xlsx?raw=true'
    header_excel = pd.ExcelFile(path)
    header = header_excel.parse('KB')
    code_df = header_excel.parse('code', index_col=1)
    code_df.index = code_df.index.str.strip()
    #2021-7-30 코드 추가
    # header 파일
    basic_df = header_excel.parse('city')
    basic_df['총인구수'] = basic_df['총인구수'].apply(lambda x: x.replace(',','')).astype(float)
    basic_df['세대수'] = basic_df['세대수'].apply(lambda x: x.replace(',','')).astype(float)
    basic_df.dropna(inplace=True)
    basic_df['밀도'] = basic_df['총인구수']/basic_df['면적']

    mdf.columns = header.columns
    mdf = mdf.iloc[1:]
    mdf.index = pd.to_datetime(mdf.index)
    mdf = mdf.round(decimals=2)

    jdf.columns = header.columns
    jdf = jdf.iloc[1:]
    jdf.index = pd.to_datetime(jdf.index)
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
            sell_change = df.loc[(df.code == sigun_id), '매매증감'].iloc[0]
            jeon_change = df.loc[(df.code == sigun_id), '전세증감'].iloc[0]
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
   
    return mdf, jdf, geo_data, basic_df

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
    js = js.iloc[2:js[('전국', '매수우위지수')].count()]
    js = js.astype(float).fillna(0).round(decimals=2)

    return js


def run_price_index() :
   
    # 챠트 기본 설정 
    # marker_colors = ['#34314c', '#47b8e0', '#ffc952', '#ff7473']
    marker_colors = ['rgb(27,38,81)', 'rgb(205,32,40)', 'rgb(22,108,150)', 'rgb(255,69,0)', 'rgb(153,204,0)', \
                       'rgb(0,0,0)', 'rgb(255,0,0)', 'rgb(0,255,0)', 'rgb(0,0,255)', 'rgb(255,255,0)', \
                        'rgb(255,0,255)', 'rgb(0,255,255)', 'rgb(128,0,0)', 'rgb(0,128,0)', 'rgb(0,0,128)', \
                         'rgb(128,128,0)', 'rgb(128,0,128)', 'rgb(0,128,128)', 'rgb(192,192,192)', 'rgb(153,153,255)', \
                             'rgb(153,51,102)', 'rgb(255,255,204)', 'rgb(102,0,102)', 'rgb(255,128,128)', 'rgb(0,102,204)',\
                                 'rgb(255,102,0)', 'rgb(51,51,51)', 'rgb(51,153,102)', 'rgb(51,153,102', 'rgb(204,153,255)']
    template = 'ggplot2' #"plotly", "plotly_white", "plotly_dark", "ggplot2", "seaborn", "simple_white", "none".

    #같이 그려보자
    gu_city = ['서울', '부산', '대구', '인천', '광주', '대전', '울산', '수원', '성남', '안양', '용인', '고양', '안산', \
                 '천안', '청주', '전주', '포항', '창원']
    gu_city_series = pd.Series(gu_city)
    draw_list = []
    if selected_dosi in gu_city:
        draw_list = city_series[city_series.str.contains(selected_dosi)].to_list()
        # draw_list = [selected_dosi]
    elif selected_dosi == '전국':
        draw_list = ['전국', '수도권', '기타지방']
    elif selected_dosi == '수도권':
        draw_list = ['서울', '경기', '인천']
    elif selected_dosi == '6개광역시':
        draw_list = ['부산', '대구', '광주', '대전', '울산', '인천']
    elif selected_dosi == '5개광역시':
        draw_list = ['부산', '대구', '광주', '대전', '울산']
    elif selected_dosi == '경기':
        draw_list = ['경기', '수원', '성남','고양', '안양', '부천', '의정부', '광명', '평택','안산', '과천', '구리', '남양주', \
             '용인', '시흥', '군포', '의왕','하남','오산','파주','이천','안성','김포', '양주','동두천','경기광주', '화성']
    
    drawAPT_weekly.run_price_index_all(draw_list, mdf, jdf, mdf_change, jdf_change, gu_city, selected_dosi3, city_series)

    

    titles = dict(text= '('+selected_dosi2 +') 주간 매매-전세 지수', x=0.5, y = 0.9) 

    fig = make_subplots(specs=[[{'secondary_y': True}]]) 
    
    fig.add_trace(go.Bar(name = '매매지수증감', x = mdf.index, y = mdf_change[selected_dosi2].round(decimals=2), marker_color=  marker_colors[2]), secondary_y = True)
    fig.add_trace(go.Bar(name = '전세지수증감', x = jdf.index, y = jdf_change[selected_dosi2].round(decimals=2), marker_color=  marker_colors[1]), secondary_y = True)

    
    fig.add_trace(go.Scatter(mode='lines', name = '매매지수', x =  mdf.index, y= mdf[selected_dosi2], marker_color = marker_colors[0]), secondary_y = False)
    fig.add_trace(go.Scatter(mode='lines', name ='전세지수', x =  jdf.index, y= jdf[selected_dosi2], marker_color = marker_colors[3]), secondary_y = False)
    fig.update_layout(hovermode="x unified")
    # fig.update_xaxes(showspikes=True, spikecolor="green", spikesnap="cursor", spikemode="across", spikethickness=0.5)
    fig.update_yaxes(showspikes=True)#, spikecolor="orange", spikethickness=0.5)
    fig.update_yaxes(title_text='지수', showticklabels= True, showgrid = True, zeroline=False,  secondary_y = False) #ticksuffix="%"
    fig.update_yaxes(title_text='지수 증감', showticklabels= True, showgrid = False, zeroline=True, zerolinecolor='LightPink', secondary_y = True, ticksuffix="%") #tickprefix="$", 
    fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template, xaxis_tickformat = '%Y-%m')
    # fig.add_hline(y=last_df.iloc[0,1], line_dash="dash", line_color="red", annotation_text=f"전국 증감률: {round(last_df.iloc[0,1],2)}", \
    #             annotation_position="bottom right")
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
    fig.add_vrect(x0="2021-02-01", x1="2021-02-15", 
              annotation_text="2.4 대책", annotation_position="bottom left",
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

    #bubble index chart
    titles = dict(text= '('+selected_dosi2 +') 주간 전세파워-버블지수', x=0.5, y = 0.9) 

    fig = make_subplots(specs=[[{'secondary_y': True}]]) 
    
    # fig.add_trace(go.Bar(name = '매매지수증감', x = mdf.index, y = mdf_change[selected_city2].round(decimals=2), marker_color=  marker_colors[2]), secondary_y = True)
    # fig.add_trace(go.Bar(name = '전세지수증감', x = jdf.index, y = jdf_change[selected_city2].round(decimals=2), marker_color=  marker_colors[1]), secondary_y = True)

    
    fig.add_trace(go.Scatter(mode='lines', name = '전세파워', x =  m_power.index, y= m_power[selected_dosi2], marker_color = marker_colors[0]), secondary_y = True)
    # fig.add_trace(go.Scatter(mode='lines', name ='버블지수2', x =  bubble_df2.index, y= bubble_df2[selected_city2], marker_color = marker_colors[1]), secondary_y = False)
    fig.add_trace(go.Scatter(mode='lines', name ='버블지수2', x =  bubble_df3.index, y= bubble_df3[selected_dosi2], marker_color = marker_colors[3]), secondary_y = False)

    fig.update_layout(hovermode="x unified")
    fig.update_xaxes(showspikes=True, spikecolor="green", spikesnap="cursor", spikemode="across", spikethickness=0.5)
    fig.update_yaxes(showspikes=True)#, spikecolor="orange", spikethickness=0.5)
    fig.update_yaxes(title_text='버블지수', showticklabels= True, showgrid = False, zeroline=True, zerolinecolor='blue', secondary_y = False) #ticksuffix="%"
    fig.update_yaxes(title_text='전세파워', showticklabels= True, showgrid = True, zeroline=True, zerolinecolor='red', secondary_y = True) #tickprefix="$", 
    fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template, xaxis_tickformat = '%Y-%m')
    st.plotly_chart(fig)

def run_sentimental_index(mdf_change):
    # st.dataframe(senti_df)
     # 챠트 기본 설정 
    # marker_colors = ['#34314c', '#47b8e0', '#ffc952', '#ff7473']
    marker_colors = ['rgb(27,38,81)', 'rgb(205,32,40)', 'rgb(22,108,150)', 'rgb(255,255,255)', 'rgb(237,234,255)']
    template = 'ggplot2' #"plotly", "plotly_white", "plotly_dark", "ggplot2", "seaborn", "simple_white", "none".

    titles = dict(text= '('+selected_dosi +') 매수우위지수 지수', x=0.5, y = 0.9) 

    fig = make_subplots(specs=[[{'secondary_y': True}]]) 
    fig.add_trace(go.Scatter(line = dict(dash='dash'), name = '매도자 많음', x =  js_1.index, y= js_1[selected_dosi], marker_color = marker_colors[0]), secondary_y = False)
    fig.add_trace(go.Scatter(line = dict(dash='dot'), name ='매수자 많음', x =  js_2.index, y= js_2[selected_dosi], marker_color = marker_colors[2]), secondary_y = False)                                             
    fig.add_trace(go.Scatter(mode='lines', name ='매수매도 지수', x =  js_index.index, y= js_index[selected_dosi], marker_color = marker_colors[1]), secondary_y = False)
    fig.add_trace(go.Scatter(x=[js_index.index[-2]], y=[99.0], text=["100>매수자많음"], mode="text"))
    fig.add_shape(type="line", x0=js_index.index[0], y0=100.0, x1=js_index.index[-1], y1=100.0, line=dict(color="MediumPurple",width=2, dash="dot"))
    # fig.update_yaxes(showspikes=True) #, spikecolor="orange", spikethickness=0.5)
    fig.update_yaxes(title_text='지수', showticklabels= True, showgrid = True, zeroline=True, zerolinecolor='LightPink', secondary_y = False) #ticksuffix="%"
    fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template, xaxis_tickformat = '%Y-%m-%d')
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
    fig.add_vrect(x0="2021-02-15", x1="2021-02-22", 
              annotation_text="8.4 대책", annotation_position="top left",
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
    fig.update_layout(hovermode="x unified")
    st.plotly_chart(fig)

    x_data = mdf_change.index
    title = "[<b>"+selected_dosi+"</b>] 매수우위지수와 매매증감"
    titles = dict(text= title,  x=0.5, y = 0.9) 
    fig = make_subplots(specs=[[{'secondary_y': True}]]) 
    fig.add_trace(go.Bar(name = "매매증감", x = x_data, y =round(mdf_change[selected_dosi],2), 
                        text = round(mdf_change[selected_dosi],2), textposition = 'outside', 
                        marker_color= marker_colors[0]), secondary_y = True) 
    fig.add_trace(go.Scatter(mode='lines', name ='매수매도 지수', x =  js_index.index, y= js_index[selected_dosi], marker_color = marker_colors[1]), secondary_y = False)
    fig.update_traces(texttemplate='%{text:.3s}') 
    fig.add_hline(y=mdf_change[selected_dosi].mean(), line_width=2, line_dash="solid", line_color="blue",  annotation_text="평균상승률: "+str(round(mdf_change[selected_dosi].mean(),2)), annotation_position="bottom right", secondary_y = True)
    fig.update_yaxes(title_text="매수우위지수", showticklabels= True, showgrid = True, zeroline=True, secondary_y = False)
    fig.update_yaxes(title_text="매매증감", showticklabels= True, showgrid = False, zeroline=True, ticksuffix="%", secondary_y = True)
    fig.update_layout(title = titles, titlefont_size=15, template=template, xaxis_tickformat = '%Y-%m-%d')
    fig.update_layout(legend=dict( orientation="h", yanchor="bottom", y=1, xanchor="right",  x=0.95))
    fig.update_layout(hovermode="x unified")
    st.plotly_chart(fig)



def draw_basic():
    #버블지수/전세파워 table 추가
    title = dict(text='주요 시-구 월간 전세파워-버블지수 합산 순위', x=0.5, y = 0.9) 
    fig = go.Figure(data=[go.Table(
                        header=dict(values=['<b>지역</b>','<b>전세파워</b>', '<b>버블지수</b>', '<b>전세파워 rank</b>', \
                                            '<b>버블지수 rank</b>', '<b>전세+버블 score</b>', '<b>전체 rank</b>'],
                                    fill_color='royalblue',
                                    align=['right','left', 'left', 'left', 'left', 'left', 'left'],
                                    font=dict(color='white', size=12),
                                    height=40),
                        cells=dict(values=[power_df.index, power_df['전세파워'], power_df['버블지수'], power_df['jrank'], \
                                            power_df['brank'], power_df['score'], power_df['rank']], 
                                    fill=dict(color=['paleturquoise', 'white', 'white','white', 'white', 'white', 'white']),
                                    align=['right','left', 'left', 'left', 'left', 'left', 'left'],
                                    font_size=12,
                                    height=30))
                    ])
    fig.update_layout(title = title, titlefont_size=15, legend=dict(orientation="h"), template="seaborn")
    st.plotly_chart(fig)

    #choroplethmapbax
    token = 'pk.eyJ1Ijoic2l6aXB1c3gyIiwiYSI6ImNrbzExaHVvejA2YjMyb2xid3gzNmxxYmoifQ.oDEe7h9GxzzUUc3CdSXcoA'

    for col in df.columns:
        df[col] = df[col].astype(str)
    
    df['text'] = '<b>' + df['index'] + '</b> <br>' + \
                    '매매증감:' + df['매매증감'] + '<br>' + \
                    '전세증감:' + df['전세증감'] 
    title = dict(text='<b>주요 시/구 주간 전세지수 증감</b>',  x=0.5, y = 0.9) 
    fig = go.Figure(go.Choroplethmapbox(geojson=geo_data, locations=df['code'], z=df['전세증감'].astype(float),
                                        colorscale="Reds", zmin=df['전세증감'].astype(float).min(), zmax=df['전세증감'].astype(float).max(), marker_line_width=0))
    fig.update_traces(autocolorscale=True,
                        text=df['text'], # hover text
                        marker_line_color='white', # line markers between states
                        colorbar_title="전세증감")
    # fig.update_traces(hovertext=df['index'])
    fig.update_layout(mapbox_style="light", mapbox_accesstoken=token,
                    mapbox_zoom=6, mapbox_center = {"lat": 37.414, "lon": 127.177})
    fig.update_layout(title = title, titlefont_size=15)
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    st.plotly_chart(fig)

    title = dict(text='주요 시-구 주간 매매지수 증감',  x=0.5, y = 0.9) 
    template = 'seaborn' #"plotly", "plotly_white", "plotly_dark", "ggplot2", "seaborn", "simple_white", "none".
    fig = px.bar(last_df, x= 'index', y=last_df.iloc[:,1], color=last_df.iloc[:,1], color_continuous_scale='Bluered', \
                text=last_df['index'])
    fig.add_hline(y=last_df.iloc[0,1], line_dash="dash", line_color="red", annotation_text=f"전국 증감률: {str(last_df.iloc[0,1])}", annotation_position="bottom right")
    # fig.add_shape(type="line", x0=last_df.index[0], y0=last_df.iloc[0,0], x1=last_df.index[-1], y1=last_df.iloc[0,0], line=dict(color="MediumPurple",width=2, dash="dot"))
    fig.update_layout(title = title, titlefont_size=15, legend=dict(orientation="h"), template=template)
    fig.update_traces(texttemplate='%{label}', textposition='outside')
    fig.update_layout(uniformtext_minsize=6, uniformtext_mode='show')
    fig.update_yaxes(title_text='주간 매매지수 증감률', showticklabels= True, showgrid = True, zeroline=True, zerolinecolor='LightPink', ticksuffix="%")
    st.plotly_chart(fig)
    # st.datafrasme(last_df.T.style.highlight_max(axis=1))


    
    with st.beta_container():
        #매매/전세 증감률 Bubble Chart
        title = dict(text='주요 시-구 주간 매매/전세지수 증감', x=0.5, y = 0.9) 
        fig1 = px.scatter(last_df, x='매매증감', y='전세증감', color='매매증감', size=abs(last_df['전세증감']), 
                            text= last_df['index'], hover_name=last_df.index, color_continuous_scale='Bluered')
        fig1.update_yaxes(zeroline=True, zerolinecolor='LightPink', ticksuffix="%")
        fig1.update_xaxes(zeroline=True, zerolinecolor='LightPink', ticksuffix="%")
        fig1.update_layout(title = title, titlefont_size=15, legend=dict(orientation="h"), template=template)
        st.plotly_chart(fig1)

if __name__ == "__main__":
    st.title("KB 부동산 주간 시계열 분석")
    data_load_state = st.text('Loading index Data...')
    mdf, jdf, geo_data, basic_df = load_index_data()
    data_load_state.text("index Data Done! (using st.cache)")
    #마지막 주
    kb_last_week = pd.to_datetime(str(mdf.index.values[-1])).strftime('%Y.%m.%d')
    st.subheader("KB last update date: " + kb_last_week)

    #주간 증감률
    mdf_change = mdf.pct_change()*100
    mdf_change = mdf_change.iloc[1:]
    mdf_change.replace([np.inf, -np.inf], np.nan, inplace=True)
    mdf_change = mdf_change.astype(float).fillna(0)
    jdf_change = jdf.pct_change()*100
    jdf_change = jdf_change.iloc[1:]
    jdf_change.replace([np.inf, -np.inf], np.nan, inplace=True)
    jdf_change = jdf_change.astype(float).fillna(0)
    #일주일 간 상승률 순위
    last_df = mdf_change.iloc[-1].T.to_frame()
    last_df['전세증감'] = jdf_change.iloc[-1].T.to_frame()
    last_df.columns = ['매매증감', '전세증감']
    last_df.dropna(inplace=True)
    last_df = last_df.astype(float).fillna(0).round(decimals=2)
    last_df = last_df.reset_index()
    #마지막달 dataframe에 지역 코드 넣어 합치기
    # df = pd.merge(last_df, code_df, how='inner', left_index=True, right_index=True)
    df = pd.merge(last_df, basic_df, how='inner', left_on='index', right_on='short')
    
    # df.columns = ['매매증감', '전세증감', 'SIG_CD']
    # df['SIG_CD']= df['SIG_CD'].astype(str)

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
    # st.dataframe(power_df)
    # st.table(power_df)

    # #function 불러 보자
    # path = 'https://github.com/sizipusx/fundamental/blob/9abf900fe8527ff491c5daabd9f3bd6279821425/files/city_info.xlsx?raw=true'
    # header_excel = pd.ExcelFile(path)
    # df1 = header_excel.parse('basic', index_col=0)
    # df1['총인구수'] = df1['총인구수'].apply(lambda x: x.replace(',','')).astype(float)
    # df1['세대수'] = df1['세대수'].apply(lambda x: x.replace(',','')).astype(float)
    # df1.dropna(inplace=True)
    org = df['지역']
    org = org.str.split(" ", expand=True)

    #여기서부터는 선택
    my_choice = st.sidebar.radio(
                    "What' are you gonna do?", ('Basic','Price Index', 'Sentiment analysis')
                    )
    if my_choice == 'Basic':
        st.subheader("전세파워 높고 버블지수 낮은 지역 상위 50곳")
        st.table(power_df.iloc[:50])
        submit = st.sidebar.button('Draw Basic chart')
        if submit:
            draw_basic()
            # st.dataframe(df)
            # drawKorea('매매증감', df, '광역시도', '행정구역', 'Reds', 'KB 주간 아파트 매매 증감', kb_last_week)
            # drawKorea('면적', df1, '광역시도', '행정구역', 'Blues')

    elif my_choice == 'Price Index':
        
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
        if selected_dosi2 == '서울':
            mirco_list = ['서울 강북', '서울 강남']
        elif selected_dosi2 == '수원':
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
        
        submit = st.sidebar.button('Draw Price Index chart')
        if submit:
            run_price_index()
    else:
        data_load_state = st.text('Loading 매수매도 index Data...')
        senti_df = load_senti_data()
        data_load_state.text("매수매도 index Data Done! (using st.cache)")

        city_list = ['전국', '서울', '강북', '강남', '6개광역시', '5개광역시', '부산', '대구', '인천', '광주', '대전',
                  '울산', '세종', '수도권', '경기', '강원', '충북', '충남', '전북', '전남', '경북', '경남', '기타지방', '제주서귀포']

        js_1 = senti_df.xs("매도자많음", axis=1, level=1)
        js_1.columns = city_list
        js_2 = senti_df.xs("매수자많음", axis=1, level=1)
        js_2.columns = city_list
        js_index = senti_df.xs("매수우위지수", axis=1, level=1)
        js_index.columns = city_list
        js_index = js_index.round(decimals=2)
        # st.dataframe(js_index)     
        # column_list = js_index.columns.to_list()
        selected_dosi = st.sidebar.selectbox(
                '광역시-도', city_list
            )
        submit = st.sidebar.button('Draw Sentimental Index chart')
        if submit:
            run_sentimental_index(mdf_change)