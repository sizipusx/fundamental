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
template = 'seaborn' #"plotly", "plotly_white", "plotly_dark", "ggplot2", "seaborn", "simple_white", "none".

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
    # fig.update_xaxes(showspikes=True, spikecolor="green", spikesnap="cursor", spikemode="across", spikethickness=0.5)
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
    #매수우위와 매매증감
    #매수우위지수
    js_index = senti_dfs[0].apply(lambda x: x.replace('-','0')).astype(float).round(decimals=2)
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
    fig.add_hline(y=mdf_change[selected_dosi].mean(), line_width=2, line_dash="dot", line_color="blue",  annotation_text="평균상승률: "+str(round(mdf_change[selected_dosi].mean(),2)), annotation_position="bottom right", secondary_y = True)
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
    fig.add_trace(go.Scatter(x=[js_sell.index[-2]], y=[99.0], text=["활발함>100"], mode="text"))
    fig.add_shape(type="line", x0=js_sell.index[0], y0=100.0, x1=js_sell.index[-1], y1=100.0, line=dict(color="MediumPurple",width=2, dash="dot"))
    fig.update_layout(hovermode="x unified")
    # fig.update_xaxes(showspikes=True, spikecolor="green", spikesnap="cursor", spikemode="across", spikethickness=0.5)
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
    fig.add_trace(go.Scatter(x=[js_j.index[-2]], y=[99.0], text=["공급부족>100"], mode="text"))
    fig.add_shape(type="line", x0=js_j.index[0], y0=100.0, x1=js_j.index[-1], y1=100.0, line=dict(color="MediumPurple",width=2, dash="dot"))
    fig.update_layout(hovermode="x unified")
    # fig.update_xaxes(showspikes=True, spikecolor="green", spikesnap="cursor", spikemode="across", spikethickness=0.5)
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
    fig.add_trace(go.Scatter(x=[js_js.index[-2]], y=[99.0], text=["활발함>100"], mode="text"))
    fig.add_shape(type="line", x0=js_js.index[0], y0=100.0, x1=js_js.index[-1], y1=100.0, line=dict(color="MediumPurple",width=2, dash="dot"))
    fig.update_layout(hovermode="x unified")
    # fig.update_xaxes(showspikes=True, spikecolor="green", spikesnap="cursor", spikemode="across", spikethickness=0.5)
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
    fig.add_trace(go.Scatter(x=[js_for.index[-2]], y=[99.0], text=["상승비중높음>100"], mode="text"))
    fig.add_shape(type="line", x0=js_for.index[0], y0=100.0, x1=js_for.index[-1], y1=100.0, line=dict(color="MediumPurple",width=2, dash="dot"))
    fig.update_layout(hovermode="x unified")
    # fig.update_xaxes(showspikes=True, spikecolor="green", spikesnap="cursor", spikemode="across", spikethickness=0.5)
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
    fig.add_trace(go.Scatter(x=[js_for_j.index[-2]], y=[99.0], text=["상승비중높음>100"], mode="text"))
    fig.add_shape(type="line", x0=js_for_j.index[0], y0=100.0, x1=js_for_j.index[-1], y1=100.0, line=dict(color="MediumPurple",width=2, dash="dot"))
    fig.update_layout(hovermode="x unified")
    # fig.update_xaxes(showspikes=True, spikecolor="green", spikesnap="cursor", spikemode="across", spikethickness=0.5)
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
    st.plotly_chart(fig)