import time
from datetime import datetime

import numpy as np
import pandas as pd


from pandas.io.json import json_normalize

import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots

import streamlit as st

pd.set_option('display.float_format', '{:.2f}'.format)
# 챠트 기본 설정 
# marker_colors = ['#34314c', '#47b8e0', '#ffc952', '#ff7473']
marker_colors = ['rgb(27,38,81)', 'rgb(205,32,40)', 'rgb(22,108,150)', 'rgb(255,69,0)', 'rgb(153,204,0)', \
                       'rgb(153,51,102)', 'rgb(255,0,0)', 'rgb(0,255,0)', 'rgb(0,0,255)', 'rgb(255,204,0)', \
                        'rgb(255,0,255)', 'rgb(0,255,255)', 'rgb(128,0,0)', 'rgb(0,128,0)', 'rgb(0,0,128)', \
                         'rgb(128,128,0)', 'rgb(128,0,128)', 'rgb(0,128,128)', 'rgb(192,192,192)', 'rgb(153,153,255)', \
                             'rgb(255,255,0)', 'rgb(255,255,204)', 'rgb(102,0,102)', 'rgb(255,128,128)', 'rgb(0,102,204)',\
                                 'rgb(255,102,0)', 'rgb(51,51,51)', 'rgb(51,153,102)', 'rgb(51,153,102', 'rgb(204,153,255)']
template = 'ggplot2' #"plotly", "plotly_white", "plotly_dark", "ggplot2", "seaborn", "simple_white", "none".
pio.templates["myID"] = go.layout.Template(
    layout_annotations=[
        dict(
            name="draft watermark",
            text="graph by 기하급수적",
            textangle=0,
            opacity=0.2,
            font=dict(color="black", size=20),
            xref="paper",
            yref="paper",
            x=0.9,
            y=-0.2,
            showarrow=False,
        )
    ]
)

def run_price_index_all(draw_list, mdf, jdf, mdf_change, jdf_change, gu_city, city3, city_series) :
    if city3 in draw_list:
        draw_list = city_series[city_series.str.contains(city3)].to_list()
    if city3 in gu_city:
        draw_list = city_series[city_series.str.contains(city3)].to_list()

    kb_last_month = pd.to_datetime(str(mdf.index.values[-1])).strftime('%Y.%m')
   
    title = "<b>KB 매매지수 변화 같이 보기</b>"
    titles = dict(text= title, x=0.5, y = 0.85) 

    fig = make_subplots(specs=[[{'secondary_y': True}]]) 
    
    for index, value in enumerate(draw_list):
        fig.add_trace(
            go.Bar(x=mdf_change.index, y=mdf_change.loc[:,value],  name=value, marker_color= marker_colors[index]),    
            secondary_y=True,
            )
    for index, value in enumerate(draw_list):
        fig.add_trace(
            go.Scatter(x=mdf.index, y=mdf.loc[:,value],  name=value, marker_color= marker_colors[index]),    
            secondary_y=False,
            )
    fig.update_yaxes(title_text="매매지수", showticklabels= True, showgrid = True, zeroline=True, secondary_y = False)
    fig.update_yaxes(title_text="매매지수 변화", showticklabels= True, showgrid = False, zeroline=True, ticksuffix="%", secondary_y = True)
    fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template, xaxis_tickformat = '%Y-%m-%d')
    fig.update_layout(template="myID")
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

def draw_power_table(power_df):
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
    fig.update_layout(template="myID")
    st.plotly_chart(fig)

def draw_Choroplethmapbox(df, geo_data, flag):
    #choroplethmapbax
    token = 'pk.eyJ1Ijoic2l6aXB1c3gyIiwiYSI6ImNrbzExaHVvejA2YjMyb2xid3gzNmxxYmoifQ.oDEe7h9GxzzUUc3CdSXcoA'
    for col in df.columns:
        df[col] = df[col].astype(str)
    df['text'] = '<b>' + df['index'] + '</b> <br>' + \
                    '매매증감:' + df['매매증감'] + '<br>' + \
                    '전세증감:' + df['전세증감']
    title = dict(text='<b>'+flag[0]+' 주간'+ flag[1]+'</b>',  x=0.5, y = 0.9) 
    fig = go.Figure(go.Choroplethmapbox(geojson=geo_data, locations=df['code'], z=df[flag[1]].astype(float),
                                        colorscale="Bluered", zmin=df[flag[1]].astype(float).min(), zmax=df[flag[1]].astype(float).max(), marker_line_width=0))
    fig.update_traces(autocolorscale=True,
                        text=df['text'], # hover text
                        marker_line_color='black', # line markers between states
                        colorbar_title=flag[1])
    # fig.update_traces(hovertext=df['index'])
    fig.update_layout(mapbox_style="light", mapbox_accesstoken=token,
                    mapbox_zoom=6, mapbox_center = {"lat": 37.414, "lon": 127.177})
    fig.update_layout(title = title, titlefont_size=15)
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    st.plotly_chart(fig)

def draw_index_change_with_bar(last_df, flag):
    title = dict(text='<b>'+flag[0] +' 주간 '+flag[1]+'</b>',  x=0.5, y = 0.9) 
    fig = px.bar(last_df, x= 'index', y=last_df.iloc[:,1], color=last_df.iloc[:,1], color_continuous_scale='Bluered', \
                text=last_df['index'])
    fig.add_hline(y=last_df.iloc[0,1], line_dash="dash", line_color="red", annotation_text=f"전국 증감률: {str(last_df.iloc[0,1])}", annotation_position="bottom right")
    # fig.add_shape(type="line", x0=last_df.index[0], y0=last_df.iloc[0,0], x1=last_df.index[-1], y1=last_df.iloc[0,0], line=dict(color="MediumPurple",width=2, dash="dot"))
    fig.update_layout(title = title, titlefont_size=15, legend=dict(orientation="h"), template=template)
    fig.update_traces(texttemplate='%{label}', textposition='outside')
    fig.update_layout(uniformtext_minsize=6, uniformtext_mode='show')
    fig.update_yaxes(title_text=flag[1], showticklabels= True, showgrid = True, zeroline=True, zerolinecolor='LightPink', ticksuffix="%")
    st.plotly_chart(fig)

def draw_index_change_with_bubble(last_df, flag):
    #매매/전세 증감률 Bubble Chart
    title = dict(text='<b>'+flag[0]+' 주요 시-구 주간 지수 증감</b>', x=0.5, y = 0.9) 
    fig = px.scatter(last_df, x='매매증감', y='전세증감', color='매매증감', size=abs(last_df['전세증감']), 
                        text= last_df['index'], hover_name=last_df.index, color_continuous_scale='Bluered')
    fig.update_yaxes(zeroline=True, zerolinecolor='LightPink', ticksuffix="%")
    fig.update_xaxes(zeroline=True, zerolinecolor='LightPink', ticksuffix="%")
    fig.update_layout(title = title, titlefont_size=15, legend=dict(orientation="h"), template=template)
    st.plotly_chart(fig)