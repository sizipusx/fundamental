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

pd.set_option('display.float_format', '{:.2f}'.format)
# 챠트 기본 설정 
# marker_colors = ['#34314c', '#47b8e0', '#ffc952', '#ff7473']
marker_colors = ['rgb(27,38,81)', 'rgb(205,32,40)', 'rgb(22,108,150)', 'rgb(255,69,0)', 'rgb(237,234,255)']
template = 'ggplot2' #"plotly", "plotly_white", "plotly_dark", "ggplot2", "seaborn", "simple_white", "none".

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
    # mdf_change = mdf_change.astype(float).round(decimal=2)
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
    marker_colors = ['rgb(27,38,81)', 'rgb(205,32,40)', 'rgb(22,108,150)', 'rgb(255,69,0)', 'rgb(255,153,204)']
    template = 'ggplot2' #"plotly", "plotly_white", "plotly_dark", "ggplot2", "seaborn", "simple_white", "none".
    fig = make_subplots(specs=[[{'secondary_y': True}]]) 


    fig.add_trace(go.Scatter(mode='lines', name = '인구수', x =  df.index, y= df[selected_city2], marker_color = marker_colors[0]), secondary_y = False)
    fig.add_trace(go.Scatter(mode='lines', name = '세대수', x =  sdf.index, y= sdf[selected_city2], marker_color = marker_colors[1]), secondary_y = False)
    fig.add_trace(go.Bar(name = '세대수 증감', x = sdf_change.index, y = sdf_change[selected_city2].round(decimals=2), marker_color=  marker_colors[3]), secondary_y = True)
    fig.add_trace(go.Bar(name = '인구수 증감', x = df_change.index, y = df_change[selected_city2].round(decimals=2), marker_color=  marker_colors[2]), secondary_y = True)


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
    titles = dict(text= ' ('+ selected_city2 + ') 준공 후 미분양', x=0.5, y = 0.9) 
    marker_colors = ['rgb(27,38,81)', 'rgb(205,32,40)', 'rgb(22,108,150)', 'rgb(98, 255, 0)', 'rgb(255,153,204)']
    template = 'ggplot2' #"plotly", "plotly_white", "plotly_dark", "ggplot2", "seaborn", "simple_white", "none".

    fig = make_subplots(specs=[[{'secondary_y': True}]]) 
    fig.add_trace(go.Bar(name = '60~85㎡', x =  not_sell_df.index, y= not_sell_df[(selected_city2, '60~85㎡')], marker_color = marker_colors[1]), secondary_y = True)
    fig.add_trace(go.Bar(name ='85㎡초과', x =  not_sell_df.index, y= not_sell_df[(selected_city2, '85㎡초과')], marker_color = marker_colors[2]), secondary_y = True)                                             
    fig.add_trace(go.Bar(name ='60㎡이하', x =  not_sell_df.index, y= not_sell_df[(selected_city2, '60㎡이하')], marker_color = marker_colors[4]), secondary_y = True)
    fig.add_trace(go.Scatter(mode='lines', name ='전체', x =  not_sell_df.index, y= not_sell_df[(selected_city2, '소계')], marker_color = marker_colors[0]), secondary_y = False)
    # fig.update_layout(hovermode="x unified")
    # fig.update_xaxes(showspikes=True, spikecolor="green", spikesnap="cursor", spikemode="across", spikethickness=0.5)
    fig.update_yaxes(title_text='호', showticklabels= True, showgrid = True, zeroline=False,  secondary_y = True)
    fig.update_yaxes(title_text='소계', showticklabels= True, showgrid = False, zeroline=True, zerolinecolor='LightPink', secondary_y = False) #ticksuffix="%"
    fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template, xaxis_tickformat = '%Y-%m')
    # fig.add_hline(y=100.0, line_color="pink", annotation_text="100>매수자많음", annotation_position="bottom right")
    st.plotly_chart(fig)

#평단가 변화
def run_sell_index(selected_dosi, sadf, sadf_ch):

    marker_colors = ['#34314c', '#47b8e0', '#ff7473', '#ffc952', '#3ac569']
    template = 'ggplot2' #"plotly", "plotly_white", "plotly_dark", "ggplot2", "seaborn", "simple_white", "none"

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
    marker_colors = ['#34314c', '#47b8e0', '#ff7473', '#ffc952', '#3ac569']
    template = 'ggplot2' #"plotly", "plotly_white", "plotly_dark", "ggplot2", "seaborn", "simple_white", "none"
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
    fig.update_yaxes(title_text="평단가", showticklabels= True, showgrid = True, zeroline=True, ticksuffix="만원", secondary_y = False)
    fig.update_yaxes(title_text="평단가 증감%", showticklabels= True, showgrid = False, zeroline=True, secondary_y = True)
    fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template, xaxis_tickformat = '%Y-%m')
    fig.update_layout(hovermode="x unified")
    st.plotly_chart(fig)

def run_jeon_ratio(selected_dosi, jratio_df):
    marker_colors = ['#34314c', '#47b8e0', '#ff7473', '#ffc952', '#3ac569']
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

