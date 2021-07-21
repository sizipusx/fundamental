import time
from datetime import datetime

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
import matplotlib.font_manager as font_manager

import matplotlib as mpl
import matplotlib.font_manager as fm

fe = fm.FontEntry(
    fname='https://github.com/sizipusx/fundamental/blob/d243febffbda721dfb8e135c94d9ed52f0049892/files/MALANGMALANGR.TTF',
    name='MALANGMALANGR')
fm.fontManager.ttflist.insert(0, fe) # or append is fine
mpl.rcParams['font.family'] = fe.name # = 'your custom ttf font name'

pd.set_option('display.float_format', '{:.2f}'.format)
#오늘날짜까지
now = datetime.now()
today = '%s-%s-%s' % ( now.year, now.month, now.day)

# file_path = 'G:/내 드라이브/code/data/WeeklySeriesTables(시계열)_20210419.xlsx'
file_path = 'https://github.com/sizipusx/fundamental/blob/fb7f32ad1dfe8e10c456bf86596bc3fe204ece02/files/WeeklySeriesTables.xlsx?raw=true'

@st.cache
def load_index_data():
    kb_dict = pd.ExcelFile(file_path)
    mdf = kb_dict.parse("매매지수", skiprows=1, index_col=0, parse_dates=True)
    jdf = kb_dict.parse("전세지수", skiprows=1, index_col=0, parse_dates=True)
    #헤더 변경
    path = 'https://github.com/sizipusx/fundamental/blob/130612c3436245a3202de78375eb12ecc712e8d9/files/kbheader.xlsx?raw=true'
    header_excel = pd.ExcelFile(path)
    header = header_excel.parse('KB')
    code_df = header_excel.parse('code', index_col=1)
    code_df.index = code_df.index.str.strip()

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
    marker_colors = ['rgb(27,38,81)', 'rgb(205,32,40)', 'rgb(22,108,150)', 'rgb(255,69,0)', 'rgb(237,234,255)']
    template = 'seaborn' #"plotly", "plotly_white", "plotly_dark", "ggplot2", "seaborn", "simple_white", "none".

    titles = dict(text= '('+selected_city2 +') 주간 매매-전세 지수', x=0.5, y = 0.9) 

    fig = make_subplots(specs=[[{'secondary_y': True}]]) 
    
    fig.add_trace(go.Bar(name = '매매지수증감', x = mdf.index, y = mdf_change[selected_city2].round(decimals=2), marker_color=  marker_colors[2]), secondary_y = True)
    fig.add_trace(go.Bar(name = '전세지수증감', x = jdf.index, y = jdf_change[selected_city2].round(decimals=2), marker_color=  marker_colors[1]), secondary_y = True)

    
    fig.add_trace(go.Scatter(mode='lines', name = '매매지수', x =  mdf.index, y= mdf[selected_city2], marker_color = marker_colors[0]), secondary_y = False)
    fig.add_trace(go.Scatter(mode='lines', name ='전세지수', x =  jdf.index, y= jdf[selected_city2], marker_color = marker_colors[3]), secondary_y = False)
    fig.update_layout(hovermode="x unified")
    # fig.update_xaxes(showspikes=True, spikecolor="green", spikesnap="cursor", spikemode="across", spikethickness=0.5)
    fig.update_yaxes(showspikes=True)#, spikecolor="orange", spikethickness=0.5)
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

    #bubble index chart
    titles = dict(text= '('+selected_city2 +') 주간 전세파워-버블지수', x=0.5, y = 0.9) 

    fig = make_subplots(specs=[[{'secondary_y': True}]]) 
    
    # fig.add_trace(go.Bar(name = '매매지수증감', x = mdf.index, y = mdf_change[selected_city2].round(decimals=2), marker_color=  marker_colors[2]), secondary_y = True)
    # fig.add_trace(go.Bar(name = '전세지수증감', x = jdf.index, y = jdf_change[selected_city2].round(decimals=2), marker_color=  marker_colors[1]), secondary_y = True)

    
    fig.add_trace(go.Scatter(mode='lines', name = '전세파워', x =  m_power.index, y= m_power[selected_city2], marker_color = marker_colors[0]), secondary_y = True)
    # fig.add_trace(go.Scatter(mode='lines', name ='버블지수2', x =  bubble_df2.index, y= bubble_df2[selected_city2], marker_color = marker_colors[1]), secondary_y = False)
    fig.add_trace(go.Scatter(mode='lines', name ='버블지수2', x =  bubble_df3.index, y= bubble_df3[selected_city2], marker_color = marker_colors[3]), secondary_y = False)

    fig.update_layout(hovermode="x unified")
    fig.update_xaxes(showspikes=True, spikecolor="green", spikesnap="cursor", spikemode="across", spikethickness=0.5)
    fig.update_yaxes(showspikes=True)#, spikecolor="orange", spikethickness=0.5)
    fig.update_yaxes(title_text='버블지수', showticklabels= True, showgrid = False, zeroline=True, zerolinecolor='blue', secondary_y = False) #ticksuffix="%"
    fig.update_yaxes(title_text='전세파워', showticklabels= True, showgrid = True, zeroline=True, zerolinecolor='red', secondary_y = True) #tickprefix="$", 
    fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template)
    st.plotly_chart(fig)

def run_sentimental_index():
    # st.dataframe(senti_df)
     # 챠트 기본 설정 
    # marker_colors = ['#34314c', '#47b8e0', '#ffc952', '#ff7473']
    marker_colors = ['rgb(27,38,81)', 'rgb(205,32,40)', 'rgb(22,108,150)', 'rgb(255,255,255)', 'rgb(237,234,255)']
    template = 'seaborn' #"plotly", "plotly_white", "plotly_dark", "ggplot2", "seaborn", "simple_white", "none".

    titles = dict(text= '('+selected_dosi +') 매수우위지수 지수', x=0.5, y = 0.9) 

    fig = make_subplots(specs=[[{'secondary_y': True}]]) 
    fig.add_trace(go.Scatter(line = dict(dash='dash'), name = '매도자 많음', x =  js_1.index, y= js_1[selected_dosi], marker_color = marker_colors[0]), secondary_y = False)
    fig.add_trace(go.Scatter(line = dict(dash='dot'), name ='매수자 많음', x =  js_2.index, y= js_2[selected_dosi], marker_color = marker_colors[2]), secondary_y = False)                                             
    fig.add_trace(go.Scatter(mode='lines', name ='매수매도 지수', x =  js_index.index, y= js_index[selected_dosi], marker_color = marker_colors[1]), secondary_y = False)
    fig.add_trace(go.Scatter(x=[js_index.index[-2]], y=[99.0], text=["100>매수자많음"], mode="text"))
    fig.add_shape(type="line", x0=js_index.index[0], y0=100.0, x1=js_index.index[-1], y1=100.0, line=dict(color="MediumPurple",width=2, dash="dot"))
    fig.update_layout(hovermode="x unified")
    fig.update_yaxes(showspikes=True) #, spikecolor="orange", spikethickness=0.5)
    fig.update_yaxes(title_text='지수', showticklabels= True, showgrid = True, zeroline=True, zerolinecolor='LightPink', secondary_y = False) #ticksuffix="%"
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
    
    df['text'] = '<b>' + df.index + '</b> <br>' + \
                    '매매증감:' + df['매매증감'] + '<br>' + \
                    '전세증감:' + df['전세증감'] 
    title = dict(text='<b>주요 시/구 주간 전세지수 증감</b>',  x=0.5, y = 0.9) 
    fig = go.Figure(go.Choroplethmapbox(geojson=geo_data, locations=df['SIG_CD'], z=df['전세증감'].astype(float),
                                        colorscale="Reds", zmin=df['전세증감'].astype(float).min(), zmax=df['전세증감'].astype(float).max(), marker_line_width=0))
    fig.update_traces(autocolorscale=False,
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
    fig = px.bar(last_df, x= last_df.index, y=last_df.iloc[:,0], color=last_df.iloc[:,0], color_continuous_scale='Bluered', \
                text=last_df.index)
    fig.add_shape(type="line", x0=last_df.index[0], y0=last_df.iloc[0,0], x1=last_df.index[-1], y1=last_df.iloc[0,0], line=dict(color="MediumPurple",width=2, dash="dot"))
    fig.update_layout(title = title, titlefont_size=15, legend=dict(orientation="h"), template=template)
    fig.update_traces(texttemplate='%{label}', textposition='outside')
    fig.update_layout(uniformtext_minsize=6, uniformtext_mode='show')
    fig.update_yaxes(title_text='주간 매매지수 증감률', showticklabels= True, showgrid = True, zeroline=True, zerolinecolor='LightPink', ticksuffix="%")
    fig.add_hline(y=last_df.iloc[0,0], line_dash="dash", line_color="red", annotation_text=f"전국 증감률: {round(last_df.iloc[0,0],2)}", \
                annotation_position="bottom right")
    st.plotly_chart(fig)
    # st.datafrasme(last_df.T.style.highlight_max(axis=1))


    
    with st.beta_container():
        #매매/전세 증감률 Bubble Chart
        title = dict(text='주요 시-구 주간 매매/전세지수 증감', x=0.5, y = 0.9) 
        fig1 = px.scatter(last_df, x='매매증감', y='전세증감', color='매매증감', size=abs(last_df['전세증감']), 
                            text= last_df.index, hover_name=last_df.index, color_continuous_scale='Bluered')
        fig1.update_yaxes(zeroline=True, zerolinecolor='LightPink', ticksuffix="%")
        fig1.update_xaxes(zeroline=True, zerolinecolor='LightPink', ticksuffix="%")
        fig1.update_layout(title = title, titlefont_size=15, legend=dict(orientation="h"), template=template)
        st.plotly_chart(fig1)

    #2021-7-21 update 개별로
def drawKorea(targetData, blockedMap, d1, d2, cmapname):
    gamma = 0.75

    whitelabelmin = (max(blockedMap[targetData]) - min(blockedMap[targetData])) * 0.25 + min(blockedMap[targetData])

    datalabel = targetData

    vmin = min(blockedMap[targetData])
    vmax = max(blockedMap[targetData])

    BORDER_LINES = [
        [(1,0),(1,1),(2,1),(2,2),(6,2),(6,0),(1,0)], # 인천
        [(1, 5), (1, 7), (2, 5), (3, 5), (3, 4), (8, 4), (8, 7), (7, 7), (7, 9), (4, 9), (4, 7), (1, 7),(2,5)], # 서울
        [(1, 9), (3, 9), (3, 10), (8, 10), (8, 9),
         (9, 9), (9, 8), (10, 8), (10, 5), (9, 5), (9, 3)], # 경기도
        [(9, 12), (9, 10), (8, 10)], # 강원도
        [(10, 5), (11, 5), (11, 4), (12, 4), (12, 5), (13, 5),
         (13, 4), (14, 4), (14, 2)], # 충청남도
        [(11, 5), (12, 5), (12, 6), (15, 6), (15, 7), (13, 7),
         (13, 8), (11, 8), (11, 9), (10, 9), (10, 8)], # 충청북도
        [(14, 4), (15, 4), (15, 6)], # 대전시
        [(14, 7), (14, 9), (13, 9), (13, 11), (13, 13)], # 경상북도
        [(14, 8), (16, 8), (16, 10), (15, 10),
         (15, 11), (14, 11), (14, 12), (13, 12)], # 대구시
        [(15, 11), (16, 11), (16, 13)], # 울산시
        [(17, 1), (17, 3), (18, 3), (18, 6), (15, 6)], # 전라북도
        [(19, 2), (19, 4), (21, 4), (21, 3), (22, 3), (22, 2), (19, 2)], # 광주시
        [(18, 5), (20, 5), (20, 6)], # 전라남도
        [(16, 9), (18, 9), (18, 8), (19, 8), (19, 9), (20, 9), (20, 10)], # 부산시
    ]

    mapdata = blockedMap.pivot(index='y', columns='x', values=targetData)
    masked_mapdata = np.ma.masked_where(np.isnan(mapdata), mapdata)
    
    plt.figure(figsize=(8, 13))
    plt.pcolor(masked_mapdata, vmin=vmin, vmax=vmax, cmap=cmapname, edgecolor='#aaaaaa', linewidth=0.5)

    # 지역 이름 표시
    for idx, row in blockedMap.iterrows():
        annocolor = 'white' if row[targetData] > whitelabelmin else 'black'

        # 광역시는 구 이름이 겹치는 경우가 많아서 시단위 이름도 같이 표시한다. (중구, 서구)
        if row[d1].endswith('시') and not row[d1].startswith('세종'):
            dispname = '{}\n{}'.format(row[d1][:2], row[d2][:-1])
            if len(row[d2]) <= 2:
                dispname += row[d2][-1]
        else:
            dispname = row[d2][:-1]

        # 서대문구, 서귀포시 같이 이름이 3자 이상인 경우에 작은 글자로 표시한다.
        if len(dispname.splitlines()[-1]) >= 3:
            fontsize, linespacing = 9.5, 1.5
        else:
            fontsize, linespacing = 11, 1.2

        plt.annotate(dispname, (row['x']+0.5, row['y']+0.5), weight='bold',
                     fontsize=fontsize, ha='center', va='center', color=annocolor,
                     linespacing=linespacing)
        
    # 시도 경계 그린다.
    for path in BORDER_LINES:
        ys, xs = zip(*path)
        plt.plot(xs, ys, c='black', lw=4)

    plt.gca().invert_yaxis()
    #plt.gca().set_aspect(1)

    plt.axis('off')

    cb = plt.colorbar(shrink=.1, aspect=10)
    cb.set_label(datalabel)

    plt.tight_layout()
    plt.show()



if __name__ == "__main__":
    st.title("KB 부동산 주간 시계열 분석")
    data_load_state = st.text('Loading index Data...')
    mdf, jdf, code_df, geo_data = load_index_data()
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
    #마지막달 dataframe에 지역 코드 넣어 합치기
    df = pd.merge(last_df, code_df, how='inner', left_index=True, right_index=True)
    df.columns = ['매매증감', '전세증감', 'SIG_CD']
    df['SIG_CD']= df['SIG_CD'].astype(str)

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

    #function 불러 보자
    path = 'https://github.com/sizipusx/fundamental/blob/9abf900fe8527ff491c5daabd9f3bd6279821425/files/city_info.xlsx?raw=true'
    header_excel = pd.ExcelFile(path)
    df1 = header_excel.parse('basic', index_col=0)
    df1['총인구수'] = df1['총인구수'].apply(lambda x: x.replace(',','')).astype(float)
    df1['세대수'] = df1['세대수'].apply(lambda x: x.replace(',','')).astype(float)
    df1.dropna(inplace=True)
    

    #여기서부터는 선택
    my_choice = st.sidebar.radio(
                    "What' are you gonna do?", ('Basic','Price Index', 'Sentiment analysis')
                    )
    if my_choice == 'Basic':
        submit = st.sidebar.button('Draw Basic chart')
        if submit:
            draw_basic()
            drawKorea('면적', df1, '광역시도', '행정구역', 'Blues')

    elif my_choice == 'Price Index':
        st.subheader("전세파워 높고 버블지수 낮은 지역 상위 20곳")
        st.table(power_df.iloc[:20])
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
        js_index = js_index.round(decimals=2)
        # st.dataframe(js_index)

        # city_list = ['전국', '서울', '강북', '강남', '6개광역시','5개광역시','부산','대구','인천','광주','대전','울산',,'수도권','세종', \
        #             '경기도', '강원도', '충청북도', '전라북도', '전라남도', '경상북도','경상남도','기타지방','제주']
        column_list = js_index.columns.to_list()
        selected_dosi = st.sidebar.selectbox(
                '광역시-도', column_list
            )
        submit = st.sidebar.button('Draw Sentimental Index chart')
        if submit:
            run_sentimental_index()