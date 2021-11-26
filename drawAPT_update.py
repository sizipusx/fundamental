import time
from datetime import datetime

import numpy as np
import pandas as pd

import requests
import json
from pandas.io.json import json_normalize

import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots

import streamlit as st

pd.set_option('display.float_format', '{:.2f}'.format)
# 챠트 기본 설정 
# marker_colors = ['#34314c', '#47b8e0', '#ffc952', '#ff7473']

marker_colors = ['rgb(27,38,81)', 'rgb(205,32,40)', 'rgb(22,108,150)', 'rgb(255,0,255)', 'rgb(153,204,0)', \
                       'rgb(153,51,102)', 'rgb(0,255,0)','rgb(255,69,0)', 'rgb(0,0,255)', 'rgb(255,204,0)', \
                        'rgb(255,153,204)', 'rgb(0,255,255)', 'rgb(128,0,0)', 'rgb(0,128,0)', 'rgb(0,0,128)', \
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


def draw_sentimental_index(selected_dosi, senti_dfs, df_as, df_bs, mdf_change):
    #매수우위지수
    js_index = senti_dfs[0].apply(lambda x: x.replace('-','0')).astype(float).round(decimals=2)
    js_1 = df_as[0].apply(lambda x: x.replace('-','0')).astype(float).round(decimals=2)
    js_2 = df_bs[0].apply(lambda x: x.replace('-','0')).astype(float).round(decimals=2)

    titles = dict(text= '[<b>'+ selected_dosi + '</b>] 매수우위지수 ', x=0.5, y = 0.9) 

    fig = make_subplots(specs=[[{'secondary_y': True}]]) 
    fig.add_trace(go.Scatter(line = dict(dash='dash'), name = '매도자 많음', x =  js_1.index, y= js_1[selected_dosi], marker_color = marker_colors[0]), secondary_y = False)
    fig.add_trace(go.Scatter(line = dict(dash='dot'), name ='매수자 많음', x =  js_2.index, y= js_2[selected_dosi], marker_color = marker_colors[2]), secondary_y = False)                                             
    fig.add_trace(go.Scatter(mode='lines', name ='매수매도 지수', x =  js_index.index, y= js_index[selected_dosi], marker_color = marker_colors[1]), secondary_y = False)
    fig.add_trace(go.Scatter(x=[js_index.index[-2]], y=[99.0], text=["매수자많음>100"], mode="text"))
    fig.add_shape(type="line", x0=js_index.index[0], y0=100.0, x1=js_index.index[-1], y1=100.0, line=dict(color="MediumPurple",width=2, dash="dot"))
    fig.update_layout(hovermode="x unified")
    # fig.update_yaxes(showspikes=True) #, spikecolor="orange", spikethickness=0.5)
    fig.update_yaxes(title_text='지수', showticklabels= True, showgrid = True, zeroline=True, zerolinecolor='LightPink', secondary_y = False) #ticksuffix="%"
    fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template, xaxis_tickformat = '%Y-%m')
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
            x=1),
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
            rangeslider=dict(visible=True), type="date")      
    )
    st.plotly_chart(fig)

def draw_ds_change(selected_dosi, senti_dfs, mdf_change):
    #매수우위지수와 매매증감
    js_index = senti_dfs[0].apply(lambda x: x.replace('-','0')).astype(float).round(decimals=2)
    mdf_change = mdf_change.apply(lambda x: x.replace('-','0')).astype(float).round(decimals=2)
    x_data = mdf_change.index
    title = "[<b>"+selected_dosi+"</b>] 매수우위지수와 매매증감"
    titles = dict(text= title,  x=0.5, y = 0.9) 
    fig = make_subplots(specs=[[{'secondary_y': True}]]) 
    fig.add_trace(go.Bar(name = "매매증감", x = x_data, y =mdf_change[selected_dosi], 
                        text = mdf_change[selected_dosi], textposition = 'outside', 
                        marker_color= marker_colors[0]), secondary_y = True) 
    fig.add_trace(go.Scatter(mode='lines', name ='매수매도 지수', x =  js_index.index, y= js_index[selected_dosi], marker_color = marker_colors[1]), secondary_y = False)
    fig.update_traces(texttemplate='%{text:.3s}') 
    fig.add_hline(y=100.0, line_width=1, line_color="red", secondary_y = False)
    fig.add_hline(y=mdf_change[selected_dosi].mean(), line_width=2, line_dash="dash", line_color="blue",  annotation_text="평균상승률: "+str(round(mdf_change[selected_dosi].mean(),2)), annotation_position="bottom right", secondary_y = True)
    fig.update_yaxes(title_text="매수우위지수", showticklabels= True, showgrid = True, zeroline=True, secondary_y = False)
    fig.update_yaxes(title_text="매매증감", showticklabels= True, showgrid = False, zeroline=True, ticksuffix="%", secondary_y = True)
    fig.update_layout(title = titles, titlefont_size=15, template=template, xaxis_tickformat = '%Y-%m')
    fig.update_layout(legend=dict( orientation="h", yanchor="bottom", y=1, xanchor="right",  x=0.95))
    fig.update_layout(hovermode="x unified")
    st.plotly_chart(fig)

def draw_mae_bs(selected_dosi, senti_dfs, df_as, df_bs):
    #매매거래지수
    js_sell = senti_dfs[1].apply(lambda x: x.replace('-','0')).astype(float).round(decimals=2)
    js_3 = df_as[1].apply(lambda x: x.replace('-','0')).astype(float).round(decimals=2)
    js_4 = df_bs[1].apply(lambda x: x.replace('-','0')).astype(float).round(decimals=2)
    titles = dict(text= '('+ selected_dosi + ') 매매거래지수 ', x=0.5, y = 0.9) 

    fig = make_subplots(specs=[[{'secondary_y': True}]]) 
    fig.add_trace(go.Scatter(line = dict(dash='dash'), name = '활발함', x =  js_3.index, y= js_3[selected_dosi], marker_color = marker_colors[0]), secondary_y = False)
    fig.add_trace(go.Scatter(line = dict(dash='dot'), name ='한산함', x =  js_4.index, y= js_4[selected_dosi], marker_color = marker_colors[2]), secondary_y = False)                                             
    fig.add_trace(go.Scatter(mode='lines', name ='매매거래지수', x =  js_sell.index, y= js_sell[selected_dosi], marker_color = marker_colors[1]), secondary_y = False)
    # fig.add_trace(go.Scatter(x=[js_sell.index[-2]], y=[99.0], text=["활발함>100"], mode="text"))
    # fig.add_shape(type="line", x0=js_sell.index[0], y0=100.0, x1=js_sell.index[-1], y1=100.0, line=dict(color="MediumPurple",width=2, dash="dot"))
    fig.add_hline(y=100.0, line_width=2, line_dash="solid", line_color="blue",  annotation_text="활발함>100", annotation_position="bottom right", secondary_y = True)
    fig.update_layout(hovermode="x unified")
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
    st.plotly_chart(fig)

def draw_jeon_bs(selected_dosi, senti_dfs, df_as, df_bs):
    js_j = senti_dfs[2].apply(lambda x: x.replace('-','0')).astype(float).round(decimals=2)
    js_5 = df_as[2].apply(lambda x: x.replace('-','0')).astype(float).round(decimals=2)
    js_6 = df_bs[2].apply(lambda x: x.replace('-','0')).astype(float).round(decimals=2)
    titles = dict(text= '('+ selected_dosi + ') 전세수급지수 ', x=0.5, y = 0.9) 

    fig = make_subplots(specs=[[{'secondary_y': True}]]) 
    fig.add_trace(go.Scatter(line = dict(dash='dash'), name = '수요>공급', x =  js_5.index, y= js_5[selected_dosi], marker_color = marker_colors[0]), secondary_y = False)
    fig.add_trace(go.Scatter(line = dict(dash='dot'), name ='수요<공급', x =  js_6.index, y= js_6[selected_dosi], marker_color = marker_colors[2]), secondary_y = False)                                             
    fig.add_trace(go.Scatter(mode='lines', name ='전세수급지수', x =  js_j.index, y= js_j[selected_dosi].round(2), marker_color = marker_colors[1]), secondary_y = False)
    # fig.add_trace(go.Scatter(x=[js_j.index[-2]], y=[99.0], text=["공급부족>100"], mode="text"))
    # fig.add_shape(type="line", x0=js_j.index[0], y0=100.0, x1=js_j.index[-1], y1=100.0, line=dict(color="MediumPurple",width=2, dash="dot"))
    fig.add_hline(y=100.0, line_width=2, line_dash="solid", line_color="blue",  annotation_text="공급부족>100", annotation_position="bottom right", secondary_y = True)
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
    fig.update_layout(hovermode="x unified")
    st.plotly_chart(fig)

def draw_jeon_trade(selected_dosi, senti_dfs, df_as, df_bs):
    js_js = senti_dfs[3].apply(lambda x: x.replace('-','0')).astype(float).round(decimals=2)
    js_7 = df_as[3].apply(lambda x: x.replace('-','0')).astype(float).round(decimals=2)
    js_8 = df_bs[3].apply(lambda x: x.replace('-','0')).astype(float).round(decimals=2)
    titles = dict(text= '('+ selected_dosi + ') 전세거래지수 ', x=0.5, y = 0.9) 

    fig = make_subplots(specs=[[{'secondary_y': True}]]) 
    fig.add_trace(go.Scatter(line = dict(dash='dash'), name = '활발함', x =  js_7.index, y= js_7[selected_dosi], marker_color = marker_colors[0]), secondary_y = False)
    fig.add_trace(go.Scatter(line = dict(dash='dot'), name ='한산함', x =  js_8.index, y= js_8[selected_dosi], marker_color = marker_colors[2]), secondary_y = False)                                             
    fig.add_trace(go.Scatter(mode='lines', name ='전세거래지수', x =  js_js.index, y= js_js[selected_dosi], marker_color = marker_colors[1]), secondary_y = False)
    # fig.add_trace(go.Scatter(x=[js_js.index[-2]], y=[99.0], text=["활발함>100"], mode="text"))
    # fig.add_shape(type="line", x0=js_js.index[0], y0=100.0, x1=js_js.index[-1], y1=100.0, line=dict(color="MediumPurple",width=2, dash="dot"))
    fig.add_hline(y=100.0, line_width=2, line_dash="solid", line_color="blue",  annotation_text="활발함>100", annotation_position="bottom right", secondary_y = True)
    #fig.update_yaxes(showspikes=True) #, spikecolor="orange", spikethickness=0.5)
    fig.update_yaxes(title_text='지수', showticklabels= True, showgrid = True, zeroline=True, zerolinecolor='LightPink', secondary_y = False) #ticksuffix="%"
    fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template)
    fig.update_layout(hovermode="x unified")
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
    st.plotly_chart(fig)

def draw_kb_mfore(selected_dosi, senti_dfs, df_as, df_bs):
    js_for = senti_dfs[4].apply(lambda x: x.replace('-','0')).astype(float).round(decimals=2)
    js_9 = df_as[4].apply(lambda x: x.replace('-','0')).astype(float).round(decimals=2)
    js_10 = df_bs[4].apply(lambda x: x.replace('-','0')).astype(float).round(decimals=2)
    titles = dict(text= '('+ selected_dosi + ') KB부동산 매매가격 전망지수 ', x=0.5, y = 0.9) 

    fig = make_subplots(specs=[[{'secondary_y': True}]]) 
    fig.add_trace(go.Scatter(line = dict(dash='dash'), name = '약간상승', x =  js_9.index, y= js_9[selected_dosi], marker_color = marker_colors[0]), secondary_y = False)
    fig.add_trace(go.Scatter(line = dict(dash='dot'), name ='약간하락', x =  js_10.index, y= js_10[selected_dosi], marker_color = marker_colors[2]), secondary_y = False)                                             
    fig.add_trace(go.Scatter(mode='lines', name ='매매가격 전망지수', x =  js_for.index, y= js_for[selected_dosi], marker_color = marker_colors[1]), secondary_y = False)
    #fig.add_trace(go.Scatter(x=[js_for.index[-2]], y=[99.0], text=["상승비중높음>100"], mode="text"))
    #fig.add_shape(type="line", x0=js_for.index[0], y0=100.0, x1=js_for.index[-1], y1=100.0, line=dict(color="MediumPurple",width=2, dash="dot"))
    fig.add_hline(y=100.0, line_width=2, line_dash="solid", line_color="blue",  annotation_text="상승비중높음>100", annotation_position="bottom right", secondary_y = True)
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
    fig.update_layout(hovermode="x unified")
    st.plotly_chart(fig)

def draw_kb_jfore(selected_dosi, senti_dfs, df_as, df_bs):
    js_for_j = senti_dfs[5].apply(lambda x: x.replace('-','0')).astype(float).round(decimals=2)
    js_11 = df_as[5].apply(lambda x: x.replace('-','0')).astype(float).round(decimals=2)
    js_12 = df_bs[5].apply(lambda x: x.replace('-','0')).astype(float).round(decimals=2)
    titles = dict(text= '('+ selected_dosi + ') KB부동산 전세가격 전망지수 ', x=0.5, y = 0.9) 

    fig = make_subplots(specs=[[{'secondary_y': True}]]) 
    fig.add_trace(go.Scatter(line = dict(dash='dash'), name = '약간상승', x =  js_11.index, y= js_11[selected_dosi], marker_color = marker_colors[0]), secondary_y = False)
    fig.add_trace(go.Scatter(line = dict(dash='dot'), name ='약간하락', x =  js_12.index, y= js_12[selected_dosi], marker_color = marker_colors[2]), secondary_y = False)                                             
    fig.add_trace(go.Scatter(mode='lines', name ='전세가격 전망지수', x =  js_for_j.index, y= js_for_j[selected_dosi], marker_color = marker_colors[1]), secondary_y = False)
    #fig.add_trace(go.Scatter(x=[js_for_j.index[-2]], y=[99.0], text=["상승비중높음>100"], mode="text"))
    #fig.add_shape(type="line", x0=js_for_j.index[0], y0=100.0, x1=js_for_j.index[-1], y1=100.0, line=dict(color="MediumPurple",width=2, dash="dot"))
    fig.add_hline(y=100.0, line_width=2, line_dash="solid", line_color="blue",  annotation_text="상승비중높음>100", annotation_position="bottom right", secondary_y = True)
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
    fig.update_layout(hovermode="x unified")
    st.plotly_chart(fig)

#인구수/ 미분양 그래프
def run_pop_index(selected_city2, df, df_change, sdf, sdf_change):
    last_month = pd.to_datetime(str(df.index.values[-1])).strftime('%Y.%m')

    titles = dict(text= '('+selected_city2 +') 세대수 증감', x=0.5, y = 0.9) 
    fig = make_subplots(specs=[[{'secondary_y': True}]]) 


    fig.add_trace(go.Scatter(mode='lines', name = '인구수', x =  df.index, y= df[selected_city2], marker_color = marker_colors[0]), secondary_y = False)
    fig.add_trace(go.Scatter(mode='lines', name = '세대수', x =  sdf.index, y= sdf[selected_city2], marker_color = marker_colors[1]), secondary_y = False)
    fig.add_trace(go.Bar(name = '세대수 증감', x = sdf_change.index, y = sdf_change[selected_city2].round(decimals=2), marker_color=  marker_colors[1]), secondary_y = True)
    fig.add_trace(go.Bar(name = '인구수 증감', x = df_change.index, y = df_change[selected_city2].round(decimals=2), marker_color=  marker_colors[0]), secondary_y = True)


    fig.update_xaxes(showspikes=True, spikecolor="green", spikesnap="cursor", spikemode="across", spikethickness=0.5)
    # fig.update_yaxes(showspikes=True)#, spikecolor="orange", spikethickness=0.5)
    fig.update_yaxes(title_text='인구세대수', showticklabels= True, showgrid = True, zeroline=False,  secondary_y = False) #ticksuffix="%"
    fig.update_yaxes(title_text='증감', showticklabels= True, showgrid = False, zeroline=True, zerolinecolor='LightPink', secondary_y = True, ticksuffix="%") #tickprefix="$", 
    fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template, xaxis_tickformat = '%Y-%m')
    # fig.update_layout(hovermode="x unified")
    st.plotly_chart(fig)


    with st.beta_expander("See explanation"):
            st.markdown(f'인구-세대수 최종업데이트: **{last_month}월**')
            st.write("인구수 Source : https://kosis.kr/statHtml/statHtml.do?orgId=101&tblId=DT_1B040A3 ")
            st.write("세대수 Source : https://kosis.kr/statHtml/statHtml.do?orgId=101&tblId=DT_1B040B3 ")
            st.write("기타 소스: https://kosis.kr/statisticsList/statisticsListIndex.do?vwcd=MT_ZTITLE&menuId=M_01_01#content-group")
    #미분양 그래프
def run_not_sell(selected_city2, not_sell_df):
    big_city_list = ['서울', '부산', '대전', '대구', '광주', '인천', '울산', '강원', '충북', '충남', '충북', '전북', '전남', '경남', '경북', '제주']
    if selected_city2 in big_city_list:
        selected_city2 = selected_city2 + ' 계'
    elif selected_city2 == '전국':
        selected_city2 = '전국 합계'
    else:
        print("소도시")

    slice_df =  not_sell_df.xs(selected_city2, axis=1, level=0)   

    titles = dict(text= ' ('+ selected_city2 + ') 준공 후 미분양', x=0.5, y = 0.9) 
    fig = make_subplots(specs=[[{'secondary_y': True}]]) 
    fig.add_trace(go.Bar(name = '60~85㎡', x =  slice_df.index, y= slice_df['60~85㎡'], marker_color = marker_colors[1]), secondary_y = True)
    fig.add_trace(go.Bar(name ='85㎡초과', x =  slice_df.index, y= slice_df['60∼85㎡'], marker_color = marker_colors[2]), secondary_y = True)                                             
    fig.add_trace(go.Bar(name ='60㎡이하', x =  slice_df.index, y= slice_df['60㎡이하'], marker_color = marker_colors[4]), secondary_y = True)
    fig.add_trace(go.Scatter(mode='lines', name ='전체', x =  slice_df.index, y= slice_df['소계'], marker_color = marker_colors[0]), secondary_y = False)
    # fig.update_layout(hovermode="x unified")
    # fig.update_xaxes(showspikes=True, spikecolor="green", spikesnap="cursor", spikemode="across", spikethickness=0.5)
    fig.update_yaxes(title_text='호', showticklabels= True, showgrid = True, zeroline=False,  secondary_y = True)
    fig.update_yaxes(title_text='소계', showticklabels= True, showgrid = False, zeroline=True, zerolinecolor='LightPink', secondary_y = False) #ticksuffix="%"
    fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template, xaxis_tickformat = '%Y-%m')
    # fig.add_hline(y=100.0, line_color="pink", annotation_text="100>매수자많음", annotation_position="bottom right")
    st.plotly_chart(fig)

#평단가 변화
def run_sell_index(selected_dosi, sadf, sadf_ch):
    x_data = sadf_ch.index
    title = "[<b>"+selected_dosi+"</b>] KB 평균 매매 평단가 변화"
    titles = dict(text= title, x=0.5, y = 0.85) 
    fig = make_subplots(specs=[[{'secondary_y': True}]]) 
    fig.add_trace(go.Bar(name = "평단가증감", x = x_data, y =sadf_ch[selected_dosi], 
                        text = sadf_ch[selected_dosi], textposition = 'outside', 
                        marker_color= marker_colors[2]), secondary_y = True) 
    fig.add_trace(go.Scatter(mode='lines', 
                                    name = "평단가", x =  sadf.index, y=sadf[selected_dosi],  
                                    text= sadf[selected_dosi], textposition = 'top center', marker_color = marker_colors[0]),
                                    secondary_y = False)
    fig.update_traces(texttemplate='%{text:.3s}') 
    fig.add_hline(y=sadf_ch[selected_dosi].mean(), line_width=2, line_dash="solid", line_color="blue",  annotation_text="평균상승률: "+str(round(sadf_ch[selected_dosi].mean(),2)), annotation_position="bottom right", secondary_y = True)
    fig.update_yaxes(title_text="평단가", showticklabels= True, showgrid = True, zeroline=True, ticksuffix="만원", secondary_y = False)
    fig.update_yaxes(title_text="평단가 증감%", showticklabels= True, showgrid = False, zeroline=True, secondary_y = True)
    fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template, xaxis_tickformat = '%Y-%m')
    fig.update_layout(hovermode="x unified")
    st.plotly_chart(fig)


def run_jeon_index(selected_dosi, jadf, jadf_ch):
    x_data = jadf_ch.index
    title = "[<b>"+selected_dosi+"</b>] KB 평균 전세 평단가 변화"
    titles = dict(text= title, x=0.5, y = 0.85) 
    fig = make_subplots(specs=[[{'secondary_y': True}]]) 
    fig.add_trace(go.Bar(name = "평단가증감", x = x_data, y =jadf_ch[selected_dosi], 
                        text = jadf_ch[selected_dosi], textposition = 'outside', 
                        marker_color= marker_colors[2]), secondary_y = True) 
    fig.add_trace(go.Scatter(mode='lines', 
                                    name = "평단가", x =  jadf.index, y=jadf[selected_dosi],  
                                    text= jadf[selected_dosi], textposition = 'top center', marker_color = marker_colors[0]),
                                    secondary_y = False)
    fig.update_traces(texttemplate='%{text:.3s}') 
    fig.add_hline(y=jadf_ch[selected_dosi].mean(), line_width=2, line_dash="solid", line_color="blue",  annotation_text="평균상승률: "+str(round(jadf_ch[selected_dosi].mean(),2)), annotation_position="bottom right", secondary_y = True)
    fig.update_yaxes(title_text="평단가", showticklabels= True, showgrid = True, zeroline=True, secondary_y = False)
    fig.update_yaxes(title_text="평단가 증감%", showticklabels= True, showgrid = False, zeroline=True, secondary_y = True)
    fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template, xaxis_tickformat = '%Y-%m')
    fig.update_layout(hovermode="x unified")
    st.plotly_chart(fig)

def run_jeon_ratio(selected_dosi, jratio_df):
    template = 'ggplot2' #"plotly", "plotly_white", "plotly_dark", "ggplot2", "seaborn", "simple_white", "none"
    title = "["+selected_dosi+"] KB 평균 가격 전세가율"
    if selected_dosi == "제주서귀포":
        selected_dosi ="제주" 
    titles = dict(text= title, x=0.5, y = 0.95) 
    fig = make_subplots(specs=[[{'secondary_y': False}]]) 
    # fig = px.line(jratio_df, x=jratio_df.index, y=selected_dosi)
    fig.add_trace(go.Scatter(mode='lines', 
                                    name = "전세가율", x =  jratio_df.index, y=jratio_df[selected_dosi],  
                                    text= jratio_df[selected_dosi], textposition = 'top center', marker_color = marker_colors[2]),
                                    secondary_y = False)
    fig.add_hline(y=70.0, line_width=2, line_dash="solid", line_color="blue", annotation_text="70%", annotation_position="bottom right")
    fig.update_layout(title = titles, uniformtext_minsize=8, uniformtext_mode='hide', template=template)
    fig.update_yaxes(title_text='전세가율', showticklabels= True, showgrid = True, ticksuffix="%")
    st.plotly_chart(fig)


def run_buy_index(selected_dosi, org_df):
    if selected_dosi == "제주서귀포":
        selected_dosi ="제주" 
    selected_df = org_df.xs(selected_dosi, axis=1, level=0)
    #마지막 달
    last_month = pd.to_datetime(str(selected_df.index.values[-1])).strftime('%Y.%m')
    #make %
    title = last_month + "월까지 ["+selected_dosi+"] 매입자별 전체 거래량"
    titles = dict(text= title, x=0.5, y = 0.95) 
    fig = px.bar(selected_df, x=selected_df.index, y=["관할시군구내", "관할시도내", "관할시도외_서울", "관할시도외_기타"])
    fig.update_layout(title = titles, uniformtext_minsize=8, uniformtext_mode='hide', xaxis_tickformat = '%Y-%m')
    st.plotly_chart(fig)

def run_buy_ratio(selected_dosi, org_df):
    selected_df = org_df.xs(selected_dosi, axis=1, level=0)
    per_df = round(selected_df.div(selected_df['합계'], axis=0)*100,1)
    last_month = pd.to_datetime(str(selected_df.index.values[-1])).strftime('%Y.%m')
    title = last_month + "월까지 ["+selected_dosi+"] 매입자별 비중"
    titles = dict(text= title, x=0.5, y = 0.95) 
    fig = px.bar(per_df, x=per_df.index, y=["관할시군구내", "관할시도내", "관할시도외_서울", "관할시도외_기타"])
    fig.update_yaxes(title= "매입자별 비중", zeroline=False, zerolinecolor='LightPink', ticksuffix="%")
    fig.update_layout(title = titles, uniformtext_minsize=8, uniformtext_mode='hide', xaxis_tickformat = '%Y-%m')
    st.plotly_chart(fig)

def run_trade_index(selected_dosi, org_df, mdf):
     # colors 
    marker_colors = ['#34314c', '#47b8e0', '#ff7473', '#ffc952', '#3ac569']
    template = 'ggplot2' #"plotly", "plotly_white", "plotly_dark", "ggplot2", "seaborn", "simple_white", "none"
    if selected_dosi == "제주":
        selected_dosi ="제주서귀포"
    selected_df = org_df.xs(selected_dosi, axis=1, level=0)
    x_data = selected_df.index
    title = "["+selected_dosi+"] <b>KB 매매지수와 거래량</b>"
    titles = dict(text= title, x=0.5, y = 0.85) 
    fig = make_subplots(specs=[[{'secondary_y': True}]]) 
    fig.add_trace(go.Bar(name = "매매거래량", x = x_data, y =selected_df['합계'], 
                        text = selected_df['합계'], textposition = 'outside', 
                        marker_color= marker_colors[2]), secondary_y = False) 
    fig.add_trace(go.Scatter(mode='lines', 
                                    name = "매매지수", x =  mdf.index, y=mdf[selected_dosi],  
                                    text= mdf[selected_dosi], textposition = 'top center', marker_color = marker_colors[0]),
                                    secondary_y = True)
    fig.update_traces(texttemplate='%{text:.3s}') 
    fig.add_hline(y=selected_df['합계'].mean(axis=0))
    fig.update_yaxes(title_text="매매 거래량", showticklabels= True, showgrid = True, zeroline=True, ticksuffix="건", secondary_y = False)
    fig.update_yaxes(title_text="매매지수", showticklabels= True, showgrid = False, zeroline=True, secondary_y = True)
    fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template, xaxis_tickformat = '%Y-%m')
    fig.update_layout(hovermode="x unified")
    st.plotly_chart(fig)

def run_price_index(selected_city2, mdf,jdf, mdf_change, jdf_change) :
    kb_last_month = pd.to_datetime(str(mdf.index.values[-1])).strftime('%Y.%m')
   
    titles = dict(text= '('+selected_city2 +') 월간 매매-전세 지수', x=0.5, y = 0.9) 

    fig = make_subplots(specs=[[{'secondary_y': True}]]) 
    
    fig.add_trace(go.Bar(name = '매매지수증감', x = mdf.index, y = mdf_change[selected_city2].round(decimals=2), marker_color=  marker_colors[2]), secondary_y = True)
    fig.add_trace(go.Bar(name = '전세지수증감', x = jdf.index, y = jdf_change[selected_city2].round(decimals=2), marker_color=  marker_colors[1]), secondary_y = True)  
    fig.add_trace(go.Scatter(mode='lines', name = '매매지수', x =  mdf.index, y= mdf[selected_city2], marker_color = marker_colors[0]), secondary_y = False)
    fig.add_trace(go.Scatter(mode='lines', name ='전세지수', x =  jdf.index, y= jdf[selected_city2], marker_color = marker_colors[3]), secondary_y = False)
    fig.update_layout(hovermode="x unified")
    # fig.update_xaxes(showspikes=True, spikecolor="green", spikesnap="cursor", spikemode="across", spikethickness=0.5)
    # fig.update_yaxes(showspikes=True)#, spikecolor="orange", spikethickness=0.5)
    fig.update_yaxes(title_text='지수', showticklabels= True, showgrid = True, zeroline=False,  secondary_y = False) #ticksuffix="%"
    fig.update_yaxes(title_text='지수 증감', showticklabels= True, showgrid = False, zeroline=True, zerolinecolor='LightPink', secondary_y = True, ticksuffix="%") #tickprefix="$", 
    fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template, xaxis_tickformat = '%Y-%m')
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

    with st.beta_expander("See explanation"):
            st.markdown(f'매매-전세 지수 최종업데이트: **{kb_last_month}월**')
            st.write("Source : https://onland.kbstar.com/quics?page=C060737 ")


def run_bubble(selected_city2, bubble_df2, m_power):
    #bubble index chart
    titles = dict(text= '('+selected_city2 +') 월간 버블 지수', x=0.5, y = 0.9) 

    fig = make_subplots(specs=[[{'secondary_y': True}]]) 
    fig.add_trace(go.Scatter(mode='lines', name = '버블지수', x =  bubble_df2.index, y= bubble_df2[selected_city2], marker_color = marker_colors[3]), secondary_y = True)
    fig.add_trace(go.Scatter(mode='lines', name ='전세파워', x =  m_power.index, y= m_power[selected_city2], marker_color = marker_colors[0]), secondary_y = False)
    fig.update_layout(hovermode="x unified")
    # fig.update_xaxes(showspikes=True, spikecolor="green", spikesnap="cursor", spikemode="across", spikethickness=0.5)
    fig.update_yaxes(showspikes=True)#, spikecolor="orange", spikethickness=0.5)
    fig.update_yaxes(title_text='전세파워', showticklabels= True, showgrid = False, zeroline=True, zerolinecolor='blue',  secondary_y = False) #ticksuffix="%"
    fig.update_yaxes(title_text='버블지수', showticklabels= True, showgrid = True, zeroline=True, zerolinecolor='red', secondary_y = True) #tickprefix="$", 
    fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template, xaxis_tickformat = '%Y-%m')
    st.plotly_chart(fig)
    
    with st.beta_expander("See explanation"):
            #st.markdown('아기곰 방식:버블지수 =(관심지역매매가상승률-전국매매가상승률) - (관심지역전세가상승률-전국전세가상승률)')
            st.write("곰곰이 방식: 버블지수 = 매매가비율(관심지역매매가/전국평균매매가) - 전세가비율(관심지역전세가/전국평균전세가)")

def draw_basic_info(selected_dosi, basic_df, bigc, smc):

    if selected_dosi == '전국':
        title = '전국 인구 동향'
        titles = dict(text= title, x=0.5, y = 0.85) 
        fig = make_subplots(specs=[[{'secondary_y': True}]]) 
        y_data_bar = [('인구 및 세대수', '인구수'), ('인구 및 세대수', '세대수')]#, ('인구 및 세대수', '인구밀도')]
        y_data_line = [('인구 및 세대수', '12인가구비율'), ('인구 및 세대수', '노인인구비율'), ('인구 및 세대수', '아파트거주비율')]


        for y_data, color in zip(y_data_line, marker_colors): 
            fig.add_trace(go.Scatter(mode='lines+markers+text', name = y_data[1], x = bigc.index, y=round(bigc[y_data]*100,1),
                                        text = round(bigc[y_data]*100,1), textposition = 'top center', marker_color = color), secondary_y = True)

        for y_data, color in zip(y_data_bar, marker_colors):
            fig.add_trace(go.Bar(name = y_data[1], x = bigc.index, y = bigc[y_data]/1000, 
                                text =bigc[y_data]/1000, textposition = 'outside', marker_color= color), secondary_y = False)

        fig.update_traces(texttemplate='%{text:.3s}') 
        # fig.update_yaxes(title_text='가구구성비율', range=[0, max(bigc.loc[:,y_data_bar[0]])*2], ticksuffix="%", secondary_y = True)
        # fig.update_yaxes(title_text='인구세대수', range=[-max(bigc.loc[:,y_data_line[0]]), max(bigc.loc[:,y_data_line[0]])* 1.2], ticksuffix="백만명", secondary_y = False)
        fig.update_yaxes(title_text='가구구성비율', ticksuffix="%", secondary_y = True)
        fig.update_yaxes(title_text='인구세대수', ticksuffix="천명", secondary_y = False)
        fig.update_yaxes(showticklabels= True, showgrid = False, zeroline=True)
        fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template)
        fig.update_layout(template="myID")
        st.plotly_chart(fig)
    elif selected_dosi == '5개광역시':
        city_list = ['부산', '대구', '대전', '광주', '울산']                                                    
        bigc = bigc.loc[city_list,:]
        title = '5광역시도 인구 동향'
        titles = dict(text= title, x=0.5, y = 0.85) 
        fig = make_subplots(specs=[[{'secondary_y': True}]]) 
        y_data_bar = [('인구 및 세대수', '인구수'), ('인구 및 세대수', '세대수')]#, ('인구 및 세대수', '인구밀도')]
        y_data_line = [('인구 및 세대수', '12인가구비율'), ('인구 및 세대수', '노인인구비율'), ('인구 및 세대수', '아파트거주비율')]


        for y_data, color in zip(y_data_line, marker_colors): 
            fig.add_trace(go.Scatter(mode='lines+markers+text', name = y_data[1], x = bigc.index, y=round(bigc[y_data]*100,1),
                                        text = round(bigc[y_data]*100,1), textposition = 'top center', marker_color = color), secondary_y = True)

        for y_data, color in zip(y_data_bar, marker_colors):
            fig.add_trace(go.Bar(name = y_data[1], x = bigc.index, y = bigc[y_data]/10000, 
                                text =bigc[y_data]/10000, textposition = 'outside', marker_color= color), secondary_y = False)

        fig.update_traces(texttemplate='%{text:.3s}') 
        # fig.update_yaxes(title_text='가구구성비율', range=[0, max(bigc.loc[:,y_data_bar[0]])*2], ticksuffix="%", secondary_y = True)
        # fig.update_yaxes(title_text='인구세대수', range=[-max(bigc.loc[:,y_data_line[0]]), max(bigc.loc[:,y_data_line[0]])* 1.2], ticksuffix="백만명", secondary_y = False)
        fig.update_yaxes(title_text='가구구성비율', ticksuffix="%", secondary_y = True)
        fig.update_yaxes(title_text='인구세대수', ticksuffix="만명", secondary_y = False)
        fig.update_yaxes(showticklabels= True, showgrid = False, zeroline=True)
        fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template)
        fig.update_layout(template="myID")
        st.plotly_chart(fig)
        
    elif selected_dosi == '6개광역시':
        city_list = ['인천', '부산', '대구', '대전', '광주', '울산']                                                    
        bigc = bigc.loc[city_list,:]
        title = '6광역시도 인구 동향'
        titles = dict(text= title, x=0.5, y = 0.85) 
        fig = make_subplots(specs=[[{'secondary_y': True}]]) 
        y_data_bar = [('인구 및 세대수', '인구수'), ('인구 및 세대수', '세대수')]#, ('인구 및 세대수', '인구밀도')]
        y_data_line = [('인구 및 세대수', '12인가구비율'), ('인구 및 세대수', '노인인구비율'), ('인구 및 세대수', '아파트거주비율')]


        for y_data, color in zip(y_data_line, marker_colors): 
            fig.add_trace(go.Scatter(mode='lines+markers+text', name = y_data[1], x = bigc.index, y=round(bigc[y_data]*100,1),
                                        text = round(bigc[y_data]*100,1), textposition = 'top center', marker_color = color), secondary_y = True)

        for y_data, color in zip(y_data_bar, marker_colors):
            fig.add_trace(go.Bar(name = y_data[1], x = bigc.index, y = bigc[y_data]/10000, 
                                text =bigc[y_data]/10000, textposition = 'outside', marker_color= color), secondary_y = False)

        fig.update_traces(texttemplate='%{text:.3s}') 
        # fig.update_yaxes(title_text='가구구성비율', range=[0, max(bigc.loc[:,y_data_bar[0]])*2], ticksuffix="%", secondary_y = True)
        # fig.update_yaxes(title_text='인구세대수', range=[-max(bigc.loc[:,y_data_line[0]]), max(bigc.loc[:,y_data_line[0]])* 1.2], ticksuffix="백만명", secondary_y = False)
        fig.update_yaxes(title_text='가구구성비율', ticksuffix="%", secondary_y = True)
        fig.update_yaxes(title_text='인구세대수', ticksuffix="만명", secondary_y = False)
        fig.update_yaxes(showticklabels= True, showgrid = False, zeroline=True)
        fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template)
        fig.update_layout(template="myID")
        st.plotly_chart(fig)

    elif selected_dosi == '수도권':
        city_list = ['서울', '경기', '인천']                                                    
        bigc = bigc.loc[city_list,:]
        title = '수도권 인구 동향'
        titles = dict(text= title, x=0.5, y = 0.85) 
        fig = make_subplots(specs=[[{'secondary_y': True}]]) 
        y_data_bar = [('인구 및 세대수', '인구수'), ('인구 및 세대수', '세대수')]#, ('인구 및 세대수', '인구밀도')]
        y_data_line = [('인구 및 세대수', '12인가구비율'), ('인구 및 세대수', '노인인구비율'), ('인구 및 세대수', '아파트거주비율')]


        for y_data, color in zip(y_data_line, marker_colors): 
            fig.add_trace(go.Scatter(mode='lines+markers+text', name = y_data[1], x = bigc.index, y=round(bigc[y_data]*100,1),
                                        text = round(bigc[y_data]*100,1), textposition = 'top center', marker_color = color), secondary_y = True)

        for y_data, color in zip(y_data_bar, marker_colors):
            fig.add_trace(go.Bar(name = y_data[1], x = bigc.index, y = bigc[y_data]/10000, 
                                text =bigc[y_data]/10000, textposition = 'outside', marker_color= color), secondary_y = False)

        fig.update_traces(texttemplate='%{text:.3s}') 
        # fig.update_yaxes(title_text='가구구성비율', range=[0, max(bigc.loc[:,y_data_bar[0]])*2], ticksuffix="%", secondary_y = True)
        # fig.update_yaxes(title_text='인구세대수', range=[-max(bigc.loc[:,y_data_line[0]]), max(bigc.loc[:,y_data_line[0]])* 1.2], ticksuffix="백만명", secondary_y = False)
        fig.update_yaxes(title_text='가구구성비율', ticksuffix="%", secondary_y = True)
        fig.update_yaxes(title_text='인구세대수', ticksuffix="만명", secondary_y = False)
        fig.update_yaxes(showticklabels= True, showgrid = False, zeroline=True)
        fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template)
        fig.update_layout(template="myID")
        st.plotly_chart(fig)
    elif selected_dosi == '기타지방':
        city_list = ['강원', '충북', '충남', '전북', '전남', '경북', '경남', '제주']                                                    
        bigc = bigc.loc[city_list,:]
        title = '기타지방 인구 동향'
        titles = dict(text= title, x=0.5, y = 0.85) 
        fig = make_subplots(specs=[[{'secondary_y': True}]]) 
        y_data_bar = [('인구 및 세대수', '인구수'), ('인구 및 세대수', '세대수')]#, ('인구 및 세대수', '인구밀도')]
        y_data_line = [('인구 및 세대수', '12인가구비율'), ('인구 및 세대수', '노인인구비율'), ('인구 및 세대수', '아파트거주비율')]


        for y_data, color in zip(y_data_line, marker_colors): 
            fig.add_trace(go.Scatter(mode='lines+markers+text', name = y_data[1], x = bigc.index, y=round(bigc[y_data]*100,1),
                                        text = round(bigc[y_data]*100,1), textposition = 'top center', marker_color = color), secondary_y = True)

        for y_data, color in zip(y_data_bar, marker_colors):
            fig.add_trace(go.Bar(name = y_data[1], x = bigc.index, y = bigc[y_data]/10000, 
                                text =bigc[y_data]/10000, textposition = 'outside', marker_color= color), secondary_y = False)

        fig.update_traces(texttemplate='%{text:.3s}') 
        # fig.update_yaxes(title_text='가구구성비율', range=[0, max(bigc.loc[:,y_data_bar[0]])*2], ticksuffix="%", secondary_y = True)
        # fig.update_yaxes(title_text='인구세대수', range=[-max(bigc.loc[:,y_data_line[0]]), max(bigc.loc[:,y_data_line[0]])* 1.2], ticksuffix="백만명", secondary_y = False)
        fig.update_yaxes(title_text='가구구성비율', ticksuffix="%", secondary_y = True)
        fig.update_yaxes(title_text='인구세대수', ticksuffix="만명", secondary_y = False)
        fig.update_yaxes(showticklabels= True, showgrid = False, zeroline=True)
        fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template)
        fig.update_layout(template="myID")
        st.plotly_chart(fig)
    else:
        city_list = smc.index
        city_series = pd.Series(city_list)
        draw_list = city_series[city_series.str.contains(selected_dosi)].to_list()                                                  
        bigc = smc.loc[draw_list, :]

        title = selected_dosi +' 인구 동향'
        titles = dict(text= title, x=0.5, y = 0.85) 
        fig = make_subplots(specs=[[{'secondary_y': True}]]) 
        y_data_bar = [('인구 및 세대수', '인구수'), ('인구 및 세대수', '세대수')]#, ('인구 및 세대수', '인구밀도')]
        y_data_line = [('인구 및 세대수', '12인가구비율'), ('인구 및 세대수', '노인인구비율'), ('인구 및 세대수', '아파트거주비율')]


        for y_data, color in zip(y_data_line, marker_colors): 
            fig.add_trace(go.Scatter(mode='lines+markers+text', name = y_data[1], x = bigc.index, y=round(bigc[y_data]*100,1),
                                        text = round(bigc[y_data]*100,1), textposition = 'top center', marker_color = color), secondary_y = True)

        for y_data, color in zip(y_data_bar, marker_colors):
            fig.add_trace(go.Bar(name = y_data[1], x = bigc.index, y = bigc[y_data]/10000, 
                                text =bigc[y_data]/10000, textposition = 'outside', marker_color= color), secondary_y = False)

        fig.update_traces(texttemplate='%{text:.3s}') 
        # fig.update_yaxes(title_text='가구구성비율', range=[0, max(bigc.loc[:,y_data_bar[0]])*2], ticksuffix="%", secondary_y = True)
        # fig.update_yaxes(title_text='인구세대수', range=[-max(bigc.loc[:,y_data_line[0]]), max(bigc.loc[:,y_data_line[0]])* 1.2], ticksuffix="백만명", secondary_y = False)
        fig.update_yaxes(title_text='가구구성비율', ticksuffix="%", secondary_y = True)
        fig.update_yaxes(title_text='인구세대수', ticksuffix="만명", secondary_y = False)
        fig.update_yaxes(showticklabels= True, showgrid = False, zeroline=True)
        fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template)
        fig.update_layout(template="myID")
        st.plotly_chart(fig)

def draw_company_info(selected_dosi, basic_df, bigc, smc):

    if selected_dosi == '전국':
        title =  "시도 기업체 수"
        titles = dict(text= title, x=0.5, y = 0.95) 
        fig = make_subplots(specs=[[{'secondary_y': True}]]) 
        size_list = [('종사자규모별 사업체수','1 - 4명'), ('종사자규모별 사업체수', '5 - 9명'),  ('종사자규모별 사업체수', '10 - 19명'), ('종사자규모별 사업체수','20 - 49명'), \
                    ('종사자규모별 사업체수', '100 - 299명'), ('종사자규모별 사업체수', '300 - 499명'), ('종사자규모별 사업체수', '500 - 999명'), ('종사자규모별 사업체수', '1000명\n이상')]

        for col_data, color in zip(size_list, marker_colors): 
            fig.add_trace(go.Bar(name=col_data[1], x=bigc.index, y=bigc.loc[:, col_data]/10000, 
                                text = bigc.loc[:, col_data]/10000, textposition = 'outside', marker_color=color ), secondary_y = False)
        fig.add_trace(go.Scatter(mode='lines+markers', name='500명 이상 기업수', x=bigc.index, y=bigc.loc[:,('대기업 비중',    '500명이상\n사업체수')], marker_color=marker_colors[1]), secondary_y = True)

        # Change the bar mode
        fig.update_layout(barmode='stack')
        fig.update_xaxes(showspikes=True, spikecolor="green", spikesnap="cursor", spikemode="across", spikethickness=0.5)
        fig.update_yaxes(showspikes=True, spikecolor="orange", spikethickness=0.5)
        fig.update_yaxes(title_text='종사자규모별 사업체수', showticklabels= True, showgrid = True, zeroline=False,  secondary_y = False, ticksuffix="개") #ticksuffix="%"
        fig.update_yaxes(title_text='500명이상\n사업체수', showticklabels= True, showgrid = False, zeroline=True, zerolinecolor='LightPink', ticksuffix="개", secondary_y = True)#, ticksuffix="%") #tickprefix="$", 
        fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template)
        fig.update_layout(template="myID")
        st.plotly_chart(fig)
    elif selected_dosi == '5개광역시':
        city_list = ['부산', '대구', '대전', '광주', '울산']                                                    
        bigc = bigc.loc[city_list,:]

        title = '5광역시도 기업체 수'
        titles = dict(text= title, x=0.5, y = 0.95) 
        fig = make_subplots(specs=[[{'secondary_y': True}]]) 


        size_list = [('종사자규모별 사업체수','1 - 4명'), ('종사자규모별 사업체수', '5 - 9명'),  ('종사자규모별 사업체수', '10 - 19명'), ('종사자규모별 사업체수','20 - 49명'), \
                    ('종사자규모별 사업체수', '100 - 299명'), ('종사자규모별 사업체수', '300 - 499명'), ('종사자규모별 사업체수', '500 - 999명'), ('종사자규모별 사업체수', '1000명\n이상')]

        for col_data, color in zip(size_list, marker_colors): 
            fig.add_trace(go.Bar(name=col_data[1], x=bigc.index, y=bigc.loc[:, col_data],  
                              text = bigc.loc[:, col_data], textposition = 'outside', marker_color=color), secondary_y = False)
        fig.add_trace(go.Scatter(mode='lines+markers', name='500명 이상 기업수', x=bigc.index, y=bigc.loc[:,('대기업 비중',    '500명이상\n사업체수')], marker_color=marker_colors[1]), secondary_y = True)

        # Change the bar mode
        fig.update_layout(barmode='stack')
        fig.update_xaxes(showspikes=True, spikecolor="green", spikesnap="cursor", spikemode="across", spikethickness=0.5)
        fig.update_yaxes(showspikes=True, spikecolor="orange", spikethickness=0.5)
        fig.update_yaxes(title_text='종사자규모별 사업체수', showticklabels= True, showgrid = True, zeroline=False,  secondary_y = False,ticksuffix="개")
        fig.update_yaxes(title_text='500명이상\n사업체수', showticklabels= True, showgrid = False, zeroline=True, zerolinecolor='LightPink', secondary_y = True, ticksuffix="개")  
        fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template)
        fig.update_layout(template="myID")
        st.plotly_chart(fig)
        
    elif selected_dosi == '6개광역시':
        city_list = ['인천', '부산', '대구', '대전', '광주', '울산']                                                    
        bigc = bigc.loc[city_list,:]
        title = '6광역시도 기업체 수'
        titles = dict(text= title, x=0.5, y = 0.95) 
        fig = make_subplots(specs=[[{'secondary_y': True}]]) 


        size_list = [('종사자규모별 사업체수','1 - 4명'), ('종사자규모별 사업체수', '5 - 9명'),  ('종사자규모별 사업체수', '10 - 19명'), ('종사자규모별 사업체수','20 - 49명'), \
                    ('종사자규모별 사업체수', '100 - 299명'), ('종사자규모별 사업체수', '300 - 499명'), ('종사자규모별 사업체수', '500 - 999명'), ('종사자규모별 사업체수', '1000명\n이상')]

        for col_data, color in zip(size_list, marker_colors): 
            fig.add_trace(go.Bar(name=col_data[1], x=bigc.index, y=bigc.loc[:, col_data], 
                                text = bigc.loc[:, col_data], textposition = 'outside', marker_color=color ), secondary_y = False)
        fig.add_trace(go.Scatter(mode='lines+markers', name='500명 이상 기업수', x=bigc.index, y=bigc.loc[:,('대기업 비중',    '500명이상\n사업체수')], marker_color=marker_colors[1]), secondary_y = True)

        # Change the bar mode
        fig.update_layout(barmode='stack')
        fig.update_xaxes(showspikes=True, spikecolor="green", spikesnap="cursor", spikemode="across", spikethickness=0.5)
        fig.update_yaxes(showspikes=True, spikecolor="orange", spikethickness=0.5)
        fig.update_yaxes(title_text='종사자규모별 사업체수', showticklabels= True, showgrid = True, zeroline=False,  secondary_y = False, ticksuffix="개")
        fig.update_yaxes(title_text='500명이상\n사업체수', showticklabels= True, showgrid = False, zeroline=True, zerolinecolor='LightPink', secondary_y = True,  ticksuffix="개")  
        fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template)
        fig.update_layout(template="myID")
        st.plotly_chart(fig)

    elif selected_dosi == '수도권':
        city_list = ['서울', '경기', '인천']                                                    
        bigc = bigc.loc[city_list,:]
        title =  "수도권 기업체 수"
        titles = dict(text= title, x=0.5, y = 0.95) 
        fig = make_subplots(specs=[[{'secondary_y': True}]]) 


        size_list = [('종사자규모별 사업체수','1 - 4명'), ('종사자규모별 사업체수', '5 - 9명'),  ('종사자규모별 사업체수', '10 - 19명'), ('종사자규모별 사업체수','20 - 49명'), \
                    ('종사자규모별 사업체수', '100 - 299명'), ('종사자규모별 사업체수', '300 - 499명'), ('종사자규모별 사업체수', '500 - 999명'), ('종사자규모별 사업체수', '1000명\n이상')]

        for col_data, color in zip(size_list, marker_colors): 
            fig.add_trace(go.Bar(name=col_data[1], x=bigc.index, y=bigc.loc[:, col_data], 
                                    text = bigc.loc[:, col_data], textposition = 'outside', marker_color=color ), secondary_y = False)
        fig.add_trace(go.Scatter(mode='lines+markers', name='500명 이상 기업수', x=bigc.index, y=bigc.loc[:,('대기업 비중',    '500명이상\n사업체수')], marker_color=marker_colors[1]), secondary_y = True)
        # Change the bar mode
        fig.update_layout(barmode='stack')
        fig.update_xaxes(showspikes=True, spikecolor="green", spikesnap="cursor", spikemode="across", spikethickness=0.5)
        fig.update_yaxes(showspikes=True, spikecolor="orange", spikethickness=0.5)
        fig.update_yaxes(title_text='종사자규모별 사업체수', showticklabels= True, showgrid = True, zeroline=False,  secondary_y = False, ticksuffix="개")
        fig.update_yaxes(title_text='500명이상\n사업체수', showticklabels= True, showgrid = False, zeroline=True, zerolinecolor='LightPink', secondary_y = True, ticksuffix="개")  
        fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template)
        fig.update_layout(template="myID")
        st.plotly_chart(fig)
    elif selected_dosi == '기타지방':
        city_list = ['강원', '충북', '충남', '전북', '전남', '경북', '경남', '제주']                                                    
        bigc = bigc.loc[city_list,:]
        title =  "기타지방 기업체 수"
        titles = dict(text= title, x=0.5, y = 0.95) 
        fig = make_subplots(specs=[[{'secondary_y': True}]]) 


        size_list = [('종사자규모별 사업체수','1 - 4명'), ('종사자규모별 사업체수', '5 - 9명'),  ('종사자규모별 사업체수', '10 - 19명'), ('종사자규모별 사업체수','20 - 49명'), \
                    ('종사자규모별 사업체수', '100 - 299명'), ('종사자규모별 사업체수', '300 - 499명'), ('종사자규모별 사업체수', '500 - 999명'), ('종사자규모별 사업체수', '1000명\n이상')]

        for col_data, color in zip(size_list, marker_colors): 
            fig.add_trace(go.Bar(name=col_data[1], x=bigc.index, y=bigc.loc[:, col_data], 
                                    text = bigc.loc[:, col_data], textposition = 'outside', marker_color=color ), secondary_y = False)
        fig.add_trace(go.Scatter(mode='lines+markers', name='500명 이상 기업수', x=bigc.index, y=bigc.loc[:,('대기업 비중',    '500명이상\n사업체수')], marker_color=marker_colors[1]), secondary_y = True)

        # Change the bar mode
        fig.update_layout(barmode='stack')
        fig.update_xaxes(showspikes=True, spikecolor="green", spikesnap="cursor", spikemode="across", spikethickness=0.5)
        fig.update_yaxes(showspikes=True, spikecolor="orange", spikethickness=0.5)
        fig.update_yaxes(title_text='종사자규모별 사업체수', showticklabels= True, showgrid = True, zeroline=False,  secondary_y = False, ticksuffix="개")
        fig.update_yaxes(title_text='500명이상\n사업체수', showticklabels= True, showgrid = False, zeroline=True, zerolinecolor='LightPink', secondary_y = True, ticksuffix="개") 
        fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template)
        fig.update_layout(template="myID")
        st.plotly_chart(fig)
    else:
        city_list = smc.index
        city_series = pd.Series(city_list)
        draw_list = city_series[city_series.str.contains(selected_dosi)].to_list()                                                  
        bigc = smc.loc[draw_list, :]

        title = selected_dosi +' 기업체 수'
        titles = dict(text= title, x=0.5, y = 0.95) 
        fig = make_subplots(specs=[[{'secondary_y': True}]]) 


        size_list = [('종사자규모별 사업체수','1 - 4명'), ('종사자규모별 사업체수', '5 - 9명'),  ('종사자규모별 사업체수', '10 - 19명'), ('종사자규모별 사업체수','20 - 49명'), \
                    ('종사자규모별 사업체수', '100 - 299명'), ('종사자규모별 사업체수', '300 - 499명'), ('종사자규모별 사업체수', '500 - 999명'), ('종사자규모별 사업체수', '1000명\n이상')]

        for col_data, color in zip(size_list, marker_colors): 
            fig.add_trace(go.Bar(name=col_data[1], x=bigc.index, y=bigc.loc[:, col_data], 
                                text = bigc.loc[:, col_data], textposition = 'outside', marker_color=color ), secondary_y = False)
        fig.add_trace(go.Scatter(mode='lines+markers', name='500명 이상 기업수', x=bigc.index, y=bigc.loc[:,('대기업 비중',    '500명이상\n사업체수')], marker_color=marker_colors[1]), secondary_y = True)

        # Change the bar mode
        fig.update_layout(barmode='stack')
        fig.update_xaxes(showspikes=True, spikecolor="green", spikesnap="cursor", spikemode="across", spikethickness=0.5)
        fig.update_yaxes(showspikes=True, spikecolor="orange", spikethickness=0.5)
        fig.update_yaxes(title_text='종사자규모별 사업체수', showticklabels= True, showgrid = True, zeroline=False,  secondary_y = False, ticksuffix="개")
        fig.update_yaxes(title_text='500명이상\n사업체수', showticklabels= True, showgrid = False, zeroline=True, zerolinecolor='LightPink', secondary_y = True, ticksuffix="개") 
        fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template)
        fig.update_layout(template="myID")
        st.plotly_chart(fig)    

def draw_earning_info(selected_dosi, basic_df, bigc, smc):

    if selected_dosi == '전국':
        title =  "시도 연말정산 인원"
        titles = dict(text= title, x=0.5, y = 0.85) 
        fig = make_subplots(specs=[[{'secondary_y': True}]]) 
        y_data_line = [('원천징수지/주소지',           '비율')]
        y_data_bar = [('연말정산 주소지',         '대상인원'), ('연말정산 원천징수',         '대상인원')]


        for y_data, color in zip(y_data_line, marker_colors): 
            fig.add_trace(go.Scatter(mode='lines+markers+text', name = y_data[0], x = bigc.index, y=round(bigc[y_data]*100,1),
                                        text = round(bigc[y_data]*100,1), textposition = 'top center', marker_color = color), secondary_y = True)

        for y_data, color in zip(y_data_bar, marker_colors):
            fig.add_trace(go.Bar(name = y_data[0], x = bigc.index, y = bigc[y_data]/10000, 
                                text = bigc[y_data]/10000, textposition = 'outside', marker_color= color), secondary_y = False)

        fig.update_traces(texttemplate='%{text:.3s}') 
        fig.update_yaxes(title_text='원천징수지인원/주소지인원', ticksuffix="%", secondary_y = True)
        fig.update_yaxes(title_text='대상인원', ticksuffix="만명", secondary_y = False)
        fig.update_yaxes(showticklabels= True, showgrid = False, zeroline=True)
        fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template)
        fig.update_layout(template="myID")
        st.plotly_chart(fig)

    elif selected_dosi == '5개광역시':
        city_list = ['부산', '대구', '대전', '광주', '울산']                                                    
        bigc = bigc.loc[city_list,:]

        title =  "5개 광역시 연말정산 현황"
        titles = dict(text= title, x=0.5, y = 0.85) 
        fig = make_subplots(specs=[[{'secondary_y': True}]]) 
        y_data_line = [('원천징수지/주소지',           '비율')]
        y_data_bar = [('연말정산 주소지',         '대상인원'), ('연말정산 원천징수',         '대상인원')]


        for y_data, color in zip(y_data_line, marker_colors): 
            fig.add_trace(go.Scatter(mode='lines+markers+text', name = y_data[0], x = bigc.index, y=round(bigc[y_data]*100,1),
                                        text = round(bigc[y_data]*100,1), textposition = 'top center', marker_color = color), secondary_y = True)

        for y_data, color in zip(y_data_bar, marker_colors):
            fig.add_trace(go.Bar(name = y_data[0], x = bigc.index, y = bigc[y_data]/10000, 
                                text = bigc[y_data]/10000, textposition = 'outside', marker_color= color), secondary_y = False)

        fig.update_traces(texttemplate='%{text:.3s}') 
        fig.update_yaxes(title_text='원천징수지인원/주소지인원', ticksuffix="%", secondary_y = True)
        fig.update_yaxes(title_text='대상인원', ticksuffix="만명", secondary_y = False)
        fig.update_yaxes(showticklabels= True, showgrid = False, zeroline=True)
        fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template)
        fig.update_layout(template="myID")
        st.plotly_chart(fig)
        
    elif selected_dosi == '6개광역시':
        city_list = ['인천', '부산', '대구', '대전', '광주', '울산']                                                    
        bigc = bigc.loc[city_list,:]

        title = '6개 광역시 연말정산 현황'
        titles = dict(text= title, x=0.5, y = 0.85) 
        fig = make_subplots(specs=[[{'secondary_y': True}]]) 
        y_data_line = [('원천징수지/주소지',           '비율')]
        y_data_bar = [('연말정산 주소지',         '대상인원'), ('연말정산 원천징수',         '대상인원')]


        for y_data, color in zip(y_data_line, marker_colors): 
            fig.add_trace(go.Scatter(mode='lines+markers+text', name = y_data[0], x = bigc.index, y=round(bigc[y_data]*100,1),
                                        text = round(bigc[y_data]*100,1), textposition = 'top center', marker_color = color), secondary_y = True)

        for y_data, color in zip(y_data_bar, marker_colors):
            fig.add_trace(go.Bar(name = y_data[0], x = bigc.index, y = bigc[y_data]/10000, 
                                text = bigc[y_data]/10000, textposition = 'outside', marker_color= color), secondary_y = False)

        fig.update_traces(texttemplate='%{text:.3s}') 
        fig.update_yaxes(title_text='원천징수지인원/주소지인원', ticksuffix="%", secondary_y = True)
        fig.update_yaxes(title_text='대상인원', ticksuffix="만명", secondary_y = False)
        fig.update_yaxes(showticklabels= True, showgrid = False, zeroline=True)
        fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template)
        fig.update_layout(template="myID")
        st.plotly_chart(fig)

    elif selected_dosi == '수도권':
        city_list = ['서울', '경기', '인천']                                                    
        bigc = bigc.loc[city_list,:]

        title =  "수도권 연말정산 현황"
        titles = dict(text= title, x=0.5, y = 0.85) 
        fig = make_subplots(specs=[[{'secondary_y': True}]]) 
        y_data_line = [('원천징수지/주소지',           '비율')]
        y_data_bar = [('연말정산 주소지',         '대상인원'), ('연말정산 원천징수',         '대상인원')]


        for y_data, color in zip(y_data_line, marker_colors): 
            fig.add_trace(go.Scatter(mode='lines+markers+text', name = y_data[0], x = bigc.index, y=round(bigc[y_data]*100,1),
                                        text = round(bigc[y_data]*100,1), textposition = 'top center', marker_color = color), secondary_y = True)

        for y_data, color in zip(y_data_bar, marker_colors):
            fig.add_trace(go.Bar(name = y_data[0], x = bigc.index, y = bigc[y_data]/10000, 
                                text = bigc[y_data]/10000, textposition = 'outside', marker_color= color), secondary_y = False)

        fig.update_traces(texttemplate='%{text:.3s}') 
        fig.update_yaxes(title_text='원천징수지인원/주소지인원', ticksuffix="%", secondary_y = True)
        fig.update_yaxes(title_text='대상인원', ticksuffix="만명", secondary_y = False)
        fig.update_yaxes(showticklabels= True, showgrid = False, zeroline=True)
        fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template)
        fig.update_layout(template="myID")
        st.plotly_chart(fig)
    elif selected_dosi == '기타지방':
        city_list = ['강원', '충북', '충남', '전북', '전남', '경북', '경남', '제주']                                                    
        bigc = bigc.loc[city_list,:]
        
        title =  "기타지방 연말정산 현황"
        titles = dict(text= title, x=0.5, y = 0.85) 
        fig = make_subplots(specs=[[{'secondary_y': True}]]) 
        y_data_line = [('원천징수지/주소지',           '비율')]
        y_data_bar = [('연말정산 주소지',         '대상인원'), ('연말정산 원천징수',         '대상인원')]


        for y_data, color in zip(y_data_line, marker_colors): 
            fig.add_trace(go.Scatter(mode='lines+markers+text', name = y_data[0], x = bigc.index, y=round(bigc[y_data]*100,1),
                                        text = round(bigc[y_data]*100,1), textposition = 'top center', marker_color = color), secondary_y = True)

        for y_data, color in zip(y_data_bar, marker_colors):
            fig.add_trace(go.Bar(name = y_data[0], x = bigc.index, y = bigc[y_data]/10000, 
                                text = bigc[y_data]/10000, textposition = 'outside', marker_color= color), secondary_y = False)

        fig.update_traces(texttemplate='%{text:.3s}') 
        fig.update_yaxes(title_text='원천징수지인원/주소지인원', ticksuffix="%", secondary_y = True)
        fig.update_yaxes(title_text='대상인원', ticksuffix="만명", secondary_y = False)
        fig.update_yaxes(showticklabels= True, showgrid = False, zeroline=True)
        fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template)
        fig.update_layout(template="myID")
        st.plotly_chart(fig)
    else:
        city_list = smc.index
        city_series = pd.Series(city_list)
        draw_list = city_series[city_series.str.contains(selected_dosi)].to_list()                                                  
        bigc = smc.loc[draw_list, :]

        title =  selected_dosi + " 연말정산 현황"
        titles = dict(text= title, x=0.5, y = 0.85) 
        fig = make_subplots(specs=[[{'secondary_y': True}]]) 
        y_data_line = [('원천징수지/주소지',           '비율')]
        y_data_bar = [('연말정산 주소지',         '대상인원'), ('연말정산 원천징수',         '대상인원')]


        for y_data, color in zip(y_data_line, marker_colors): 
            fig.add_trace(go.Scatter(mode='lines+markers+text', name = y_data[0], x = bigc.index, y=round(bigc[y_data]*100,1),
                                        text = round(bigc[y_data]*100,1), textposition = 'top center', marker_color = color), secondary_y = True)

        for y_data, color in zip(y_data_bar, marker_colors):
            fig.add_trace(go.Bar(name = y_data[0], x = bigc.index, y = bigc[y_data]/10000, 
                                text = bigc[y_data]/10000, textposition = 'outside', marker_color= color), secondary_y = False)

        fig.update_traces(texttemplate='%{text:.3s}') 
        fig.update_yaxes(title_text='원천징수지인원/주소지인원', ticksuffix="%", secondary_y = True)
        fig.update_yaxes(title_text='대상인원', ticksuffix="만명", secondary_y = False)
        fig.update_yaxes(showticklabels= True, showgrid = False, zeroline=True)
        fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template)
        fig.update_layout(template="myID")
        st.plotly_chart(fig) 

def draw_pay_info(selected_dosi, basic_df, bigc, smc):

    if selected_dosi == '전국':
        title =  "시도 건강보험료 현황"
        titles = dict(text= title, x=0.5, y = 0.85) 
        fig = make_subplots(specs=[[{'secondary_y': True}]]) 
        y_data_bar = [('보험료', '지역가입자'), ('보험료', '직장가입자')]#, ('인구 및 세대수', '인구밀도')]
        y_data_line = [( '보험료',        '직장월급여')]


        for y_data, color in zip(y_data_line, marker_colors): 
            fig.add_trace(go.Scatter(mode='lines+markers+text', name = y_data[1], x = bigc.index, y=bigc[y_data],
                                        text = bigc[y_data], textposition = 'top center', marker_color = color), secondary_y = True)

        for y_data, color in zip(y_data_bar, marker_colors):
            fig.add_trace(go.Bar(name = y_data[1], x = bigc.index, y = bigc[y_data], 
                                text = bigc[y_data], textposition = 'outside', marker_color= color), secondary_y = False)

        fig.update_traces(texttemplate='%{text:.3s}') 
        fig.update_yaxes(title_text='보험료', range=[0, max(bigc.loc[:,y_data_bar[0]])*2.5], ticksuffix="원", secondary_y = False)
        fig.update_yaxes(title_text='추정 직장월급여', range=[-max(bigc.loc[:,y_data_line[0]]), max(bigc.loc[:,y_data_line[0]])* 1.2], ticksuffix="원", secondary_y = True)
        fig.update_yaxes(showticklabels= True, showgrid = False, zeroline=True)
        fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template)
        fig.update_layout(template="myID")
        st.plotly_chart(fig)
    elif selected_dosi == '5개광역시':
        city_list = ['부산', '대구', '대전', '광주', '울산']                                                    
        bigc = bigc.loc[city_list,:]

        title =  "5개광역시 건강보험료 현황"
        titles = dict(text= title, x=0.5, y = 0.85) 
        fig = make_subplots(specs=[[{'secondary_y': True}]]) 
        y_data_bar = [('보험료', '지역가입자'), ('보험료', '직장가입자')]#, ('인구 및 세대수', '인구밀도')]
        y_data_line = [( '보험료',        '직장월급여')]


        for y_data, color in zip(y_data_line, marker_colors): 
            fig.add_trace(go.Scatter(mode='lines+markers+text', name = y_data[1], x = bigc.index, y=bigc[y_data],
                                        text = bigc[y_data], textposition = 'top center', marker_color = color), secondary_y = True)

        for y_data, color in zip(y_data_bar, marker_colors):
            fig.add_trace(go.Bar(name = y_data[1], x = bigc.index, y = bigc[y_data], 
                                text = bigc[y_data], textposition = 'outside', marker_color= color), secondary_y = False)

        fig.update_traces(texttemplate='%{text:.3s}') 
        fig.update_yaxes(title_text='보험료', range=[0, max(bigc.loc[:,y_data_bar[0]])*2.5], ticksuffix="원", secondary_y = False)
        fig.update_yaxes(title_text='추정 직장월급여', range=[-max(bigc.loc[:,y_data_line[0]]), max(bigc.loc[:,y_data_line[0]])* 1.2], ticksuffix="원", secondary_y = True)
        fig.update_yaxes(showticklabels= True, showgrid = False, zeroline=True)
        fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template)
        fig.update_layout(template="myID")
        st.plotly_chart(fig)
        
    elif selected_dosi == '6개광역시':
        city_list = ['인천', '부산', '대구', '대전', '광주', '울산']                                                    
        bigc = bigc.loc[city_list,:]

        title =  "6개광역시 건강보험료 현황"
        titles = dict(text= title, x=0.5, y = 0.85) 
        fig = make_subplots(specs=[[{'secondary_y': True}]]) 
        y_data_bar = [('보험료', '지역가입자'), ('보험료', '직장가입자')]#, ('인구 및 세대수', '인구밀도')]
        y_data_line = [( '보험료',        '직장월급여')]


        for y_data, color in zip(y_data_line, marker_colors): 
            fig.add_trace(go.Scatter(mode='lines+markers+text', name = y_data[1], x = bigc.index, y=bigc[y_data],
                                        text = bigc[y_data], textposition = 'top center', marker_color = color), secondary_y = True)

        for y_data, color in zip(y_data_bar, marker_colors):
            fig.add_trace(go.Bar(name = y_data[1], x = bigc.index, y = bigc[y_data], 
                                text = bigc[y_data], textposition = 'outside', marker_color= color), secondary_y = False)

        fig.update_traces(texttemplate='%{text:.3s}') 
        fig.update_yaxes(title_text='보험료', range=[0, max(bigc.loc[:,y_data_bar[0]])*2.5], ticksuffix="원", secondary_y = False)
        fig.update_yaxes(title_text='추정 직장월급여', range=[-max(bigc.loc[:,y_data_line[0]]), max(bigc.loc[:,y_data_line[0]])* 1.2], ticksuffix="원", secondary_y = True)
        fig.update_yaxes(showticklabels= True, showgrid = False, zeroline=True)
        fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template)
        fig.update_layout(template="myID")
        st.plotly_chart(fig)

    elif selected_dosi == '수도권':
        city_list = ['서울', '경기', '인천']                                                    
        bigc = bigc.loc[city_list,:]

        title =  "수도권 건강보험료 현황"
        titles = dict(text= title, x=0.5, y = 0.85) 
        fig = make_subplots(specs=[[{'secondary_y': True}]]) 
        y_data_bar = [('보험료', '지역가입자'), ('보험료', '직장가입자')]#, ('인구 및 세대수', '인구밀도')]
        y_data_line = [( '보험료',        '직장월급여')]


        for y_data, color in zip(y_data_line, marker_colors): 
            fig.add_trace(go.Scatter(mode='lines+markers+text', name = y_data[1], x = bigc.index, y=bigc[y_data],
                                        text = bigc[y_data], textposition = 'top center', marker_color = color), secondary_y = True)

        for y_data, color in zip(y_data_bar, marker_colors):
            fig.add_trace(go.Bar(name = y_data[1], x = bigc.index, y = bigc[y_data], 
                                text = bigc[y_data], textposition = 'outside', marker_color= color), secondary_y = False)

        fig.update_traces(texttemplate='%{text:.3s}') 
        fig.update_yaxes(title_text='보험료', range=[0, max(bigc.loc[:,y_data_bar[0]])*2.5], ticksuffix="원", secondary_y = False)
        fig.update_yaxes(title_text='추정 직장월급여', range=[-max(bigc.loc[:,y_data_line[0]]), max(bigc.loc[:,y_data_line[0]])* 1.2], ticksuffix="원", secondary_y = True)
        fig.update_yaxes(showticklabels= True, showgrid = False, zeroline=True)
        fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template)
        fig.update_layout(template="myID")
        st.plotly_chart(fig)
    elif selected_dosi == '기타지방':
        city_list = ['강원', '충북', '충남', '전북', '전남', '경북', '경남', '제주']                                                    
        bigc = bigc.loc[city_list,:]
        
        title =  "기타지방 건강보험료 현황"
        titles = dict(text= title, x=0.5, y = 0.85) 
        fig = make_subplots(specs=[[{'secondary_y': True}]]) 
        y_data_bar = [('보험료', '지역가입자'), ('보험료', '직장가입자')]#, ('인구 및 세대수', '인구밀도')]
        y_data_line = [( '보험료',        '직장월급여')]


        for y_data, color in zip(y_data_line, marker_colors): 
            fig.add_trace(go.Scatter(mode='lines+markers+text', name = y_data[1], x = bigc.index, y=bigc[y_data],
                                        text = bigc[y_data], textposition = 'top center', marker_color = color), secondary_y = True)

        for y_data, color in zip(y_data_bar, marker_colors):
            fig.add_trace(go.Bar(name = y_data[1], x = bigc.index, y = bigc[y_data], 
                                text = bigc[y_data], textposition = 'outside', marker_color= color), secondary_y = False)

        fig.update_traces(texttemplate='%{text:.3s}') 
        fig.update_yaxes(title_text='보험료', range=[0, max(bigc.loc[:,y_data_bar[0]])*2.5], ticksuffix="원", secondary_y = False)
        fig.update_yaxes(title_text='추정 직장월급여', range=[-max(bigc.loc[:,y_data_line[0]]), max(bigc.loc[:,y_data_line[0]])* 1.2], ticksuffix="원", secondary_y = True)
        fig.update_yaxes(showticklabels= True, showgrid = False, zeroline=True)
        fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template)
        fig.update_layout(template="myID")
        st.plotly_chart(fig)
    else:
        city_list = smc.index
        city_series = pd.Series(city_list)
        draw_list = city_series[city_series.str.contains(selected_dosi)].to_list()                                                  
        bigc = smc.loc[draw_list, :]

        title =  selected_dosi + " 건강보험료 현황"
        titles = dict(text= title, x=0.5, y = 0.85) 
        fig = make_subplots(specs=[[{'secondary_y': True}]]) 
        y_data_bar = [('보험료', '지역가입자'), ('보험료', '직장가입자')]#, ('인구 및 세대수', '인구밀도')]
        y_data_line = [( '보험료',        '직장월급여')]


        for y_data, color in zip(y_data_line, marker_colors): 
            fig.add_trace(go.Scatter(mode='lines+markers+text', name = y_data[1], x = bigc.index, y=bigc[y_data],
                                        text = bigc[y_data], textposition = 'top center', marker_color = color), secondary_y = True)

        for y_data, color in zip(y_data_bar, marker_colors):
            fig.add_trace(go.Bar(name = y_data[1], x = bigc.index, y = bigc[y_data], 
                                text = bigc[y_data], textposition = 'outside', marker_color= color), secondary_y = False)

        fig.update_traces(texttemplate='%{text:.3s}') 
        fig.update_yaxes(title_text='보험료', range=[0, max(bigc.loc[:,y_data_bar[0]])*2.5], ticksuffix="원", secondary_y = False)
        fig.update_yaxes(title_text='추정 직장월급여', range=[-max(bigc.loc[:,y_data_line[0]]), max(bigc.loc[:,y_data_line[0]])* 1.2], ticksuffix="원", secondary_y = True)
        fig.update_yaxes(showticklabels= True, showgrid = False, zeroline=True)
        fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template)
        fig.update_layout(template="myID")
        st.plotly_chart(fig) 

def run_local_analysis(mdf, mdf_change, selected_dosi):
    #같이 그려보자
    do_list = ['강원', '충북', '충남', '전북', '전남', '경남', '경북', '제주서귀포']
    gu_city = ['부산', '대구', '인천', '광주', '대전', '울산', '수원', '성남', '안양', '용인', '고양', '안산', \
                 '천안', '청주', '전주', '포항', '창원']
    # gu_city_series = pd.Series(gu_city)
    column_list = mdf.columns.to_list()
    city_series = pd.Series(column_list)
    draw_list = []
    if selected_dosi in gu_city:
        draw_list = city_series[city_series.str.contains(selected_dosi)].to_list()
    elif selected_dosi == '전국':
        draw_list = ['전국', '수도권', '기타지방']
    elif selected_dosi == '서울':
        draw_list = ['서울 강북', '서울 강남']
    elif selected_dosi == '수도권':
        draw_list = ['서울', '경기', '인천']
    elif selected_dosi == '6개광역시':
        draw_list = ['부산', '대구', '광주', '대전', '울산', '인천']
    elif selected_dosi == '5개광역시':
        draw_list = ['부산', '대구', '광주', '대전', '울산']
    elif selected_dosi == '경기':
        draw_list = ['경기', '수원', '성남','고양', '안양', '부천', '의정부', '광명', '평택','안산', '과천', '구리', '남양주', \
             '용인', '시흥', '군포', '의왕','하남','오산','파주','이천','안성','김포', '양주','동두천','경기광주', '화성']
    elif selected_dosi == '충북':
        draw_list = ['청주 흥덕구', '청주 청원구', '청주 상당구', '청주 서원구', '충주', '제천']
    elif selected_dosi == '강원':
        draw_list = ['춘천', '강릉', '원주']
    elif selected_dosi == '충남':
        draw_list = ['천안 동남구', '천안 서북구', '공주', '아산', '논산', '계룡', '당진', '서산']
    elif selected_dosi == '전북':
        draw_list = ['전주 완산구', '전주 덕진구', '익산', '군산']
    elif selected_dosi == '전남':
        draw_list = ['목포', '순천', '광양', '여수']
    elif selected_dosi == '경북':
        draw_list = ['포항 남구', '포항 북구', '구미', '경산', '안동', '김천']
    elif selected_dosi == '경남':
        draw_list = ['창원 마산합포구', '창원 마산회원구', '창원 성산구', '창원 의창구', '창원 진해구', '양산', '거제', '진주', '김해', '통영']
    elif selected_dosi == '제주':
        draw_list = ['제주서귀포']
    elif selected_dosi == '기타지방':
        draw_list = ['강원', '충북', '충남', '전북', '전남', '경남', '경북', '제주서귀포']
       
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
    fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template, xaxis_tickformat = '%Y-%m')
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

def run_local_price(peong_df, peongj_df, selected_dosi):
    #마지막 데이터만
    last_df = peong_df.iloc[-1].T.to_frame()
    last_df['평균전세가'] = peongj_df.iloc[-1].T.to_frame()
    last_df.columns = ['평균매매가', '평균전세가']
    last_df.dropna(inplace=True)
    last_df = last_df.round(decimals=2)
    #같이 그려보자
    gu_city = ['서울', '부산', '대구', '인천', '광주', '대전', '울산', '수원', '성남', '안양', '용인', '고양', '안산', \
                 '천안', '청주', '전주', '포항', '창원']
    do_list = ['강원', '충북', '충남', '전북', '전남', '경남', '경북', '제주서귀포']
    # gu_city_series = pd.Series(gu_city)
    column_list = peong_df.columns.to_list()
    city_series = pd.Series(column_list)
    draw_list = []
    if selected_dosi in gu_city:
        draw_list = city_series[city_series.str.contains(selected_dosi)].to_list()
        draw_list.append('전국')
    elif selected_dosi == '전국':
        draw_list = ['전국', '서울', '부산', '대구', '인천', '광주', '대전', '울산', '경기', '강원', '충북', '충남', '전북', '전남', \
                        '경남', '경북', '제주서귀포']
    elif selected_dosi == '수도권':
        draw_list = ['전국', '서울', '경기', '인천']
    elif selected_dosi == '6개광역시':
        draw_list = ['전국', '부산', '대구', '광주', '대전', '울산', '인천']
    elif selected_dosi == '5개광역시':
        draw_list = ['전국', '부산', '대구', '광주', '대전', '울산']
    elif selected_dosi == '경기':
        draw_list = ['전국', '경기', '수원', '성남','고양', '안양', '부천', '의정부', '광명', '평택','안산', '과천', '구리', '남양주', \
             '용인', '시흥', '군포', '의왕','하남','오산','파주','이천','안성','김포', '양주','동두천','경기광주', '화성']
    elif selected_dosi == '충북':
        draw_list = ['전국', '청주 흥덕구', '청주 청원구', '청주 상당구', '청주 서원구', '충주', '제천']
    elif selected_dosi == '강원':
        draw_list = ['전국', '춘천', '강릉', '원주']
    elif selected_dosi == '충남':
        draw_list = ['전국', '천안 동남구', '천안 서북구', '공주', '아산', '논산', '계룡', '당진', '서산']
    elif selected_dosi == '전북':
        draw_list = ['전국', '전주 완산구', '전주 덕진구', '익산', '군산']
    elif selected_dosi == '전남':
        draw_list = ['전국', '목포', '순천', '광양', '여수']
    elif selected_dosi == '경북':
        draw_list = ['전국', '포항 남구', '포항 북구', '구미', '경산', '안동', '김천']
    elif selected_dosi == '경남':
        draw_list = ['전국', '창원 마산합포구', '창원 마산회원구', '창원 성산구', '창원 의창구', '창원 진해구', '양산', '거제', '진주', '김해', '통영']
    elif selected_dosi == '제주':
        draw_list = ['전국', '제주서귀포']
    elif selected_dosi == '기타지방':
        draw_list = ['전국', '강원', '충북', '충남', '전북', '전남', '경남', '경북', '제주서귀포']
        
    draw_df = last_df.loc[draw_list,:]

    # 사분면 그래프로 그려보자.
    #매매/전세 증감률 Bubble Chart
    title = dict(text='주요 시-구 월간 평균 매매/전세평단가', x=0.5, y = 0.9) 
    # fig = go.Figure(data=go.Scatter(
    #     x=draw_df.loc[:,'평균매매가'], y=draw_df.loc[:,'평균전세가'], 
    #     mode='markers',
    #     text = draw_df.index, #+'<br>원천/거주지 비율:'+ str(smc.loc[:,('원천징수지/주소지', '비율')]*10),
    #     marker=dict(
    #         size=draw_df.loc[:,'평균매매가']/100,
    #         color=draw_df.loc[:,'평균전세가'], #set color equal to a variable
    #         colorscale='Bluered', # one of plotly colorscales
    #         showscale=True
    #     )
    # ))
    fig = px.scatter(draw_df, x='평균매매가', y='평균전세가', color='평균매매가', size=abs(draw_df['평균매매가']), 
                        text= draw_df.index, hover_name=draw_df.index, color_continuous_scale='Bluered')
    fig.add_hline(y=draw_df.loc['전국','평균전세가'], line_width=1, line_color="red", line_dash="dot", secondary_y = False)
    fig.add_vline(x=draw_df.loc['전국','평균매매가'], line_width=1, line_color="red", line_dash="dot", secondary_y = False)
    fig.update_yaxes(zeroline=True, zerolinecolor='LightPink', ticksuffix="만원")
    fig.update_xaxes(zeroline=True, zerolinecolor='LightPink', ticksuffix="만원")
    fig.update_layout(title = title, titlefont_size=15, legend=dict(orientation="h"), template=template)
    fig.update_layout(template="myID")
    st.plotly_chart(fig)