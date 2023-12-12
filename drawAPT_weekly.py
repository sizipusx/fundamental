from math import nan
import time
# from datetime import datetime
import datetime
from dateutil.relativedelta import relativedelta
import numpy as np
import pandas as pd
from pandas.core.dtypes.missing import notnull
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots
import streamlit as st

pd.set_option('display.float_format', '{:.2f}'.format)
pd.set_option('display.max.colwidth', 50)

utcnow= datetime.datetime.utcnow()
time_gap= datetime.timedelta(hours=9)
kor_time= utcnow+ time_gap
# 챠트 기본 설정 
# marker_colors = ['#34314c', '#47b8e0', '#ffc952', '#ff7473'] #'rgb(255,69,0)'
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
            text="Graph by 기하급수적",
            textangle=0,
            opacity=0.5,
            font=dict(color="black", size=10),
            xref="paper",
            yref="paper",
            x=0.9,
            y=0.2,
            showarrow=False,
        )
    ]
)

def make_dynamic_graph(s_df, js_df):
    
    flag = "KB 주간 시계열"
    title = dict(text='<b>'+flag+' 매수우위와 전세수급 지수</b>', x=0.5, y = 0.85, xanchor='center', yanchor= 'top') 
    template = "ggplot2"
    fig = px.scatter(to_df, x='매수우위지수', y='전세수급지수', color='매수우위지수', size=abs(to_df['전세수급지수']*10), 
                        text= to_df.index, hover_name=to_df.index, color_continuous_scale='Bluered')
    fig.update_yaxes(zeroline=True, zerolinecolor='LightPink')#, ticksuffix="%")
    fig.update_xaxes(zeroline=True, zerolinecolor='LightPink')#, ticksuffix="%")
    fig.add_hline(y=100.0, line_width=2, line_dash="solid", line_color="blue",  annotation_text="매수우위지수가 100을 초과할수록 '공급부족' 비중이 높음 ", annotation_position="bottom right")
    fig.add_vline(x=100.0, line_width=2, line_dash="solid", line_color="blue",  annotation_text="전세수급지수가 100을 초과할수록 '매수자가 많다'를, 100 미만일 경우 '매도자가 많다'를 의미 ", annotation_position="top left")
    fig.add_vline(x=40.0, line_width=1, line_dash="dot", line_color="red",  annotation_text="40 이상 매매지수 상승 가능성 높음", annotation_position="top left")
    fig.update_layout(title = title, titlefont_size=15, legend=dict(orientation="h"), template=template)
    fig.update_layout(template="myID")
    st.plotly_chart(fig)


def run_price_index_all(draw_list, mdf, jdf, mdf_change, jdf_change, gu_city, city3, city_series) :
    if city3 in draw_list:
        draw_list = city_series[city_series.str.contains(city3)].to_list()
    if city3 in gu_city:
        draw_list = city_series[city_series.str.contains(city3)].to_list()
    if ("경기" in draw_list) and (len(draw_list) == 1):
        draw_list = ['경기', '수원', '안양','성남', '용인', '고양', '안산']
    try:
        title = "<b>KB 매매지수 변화 같이 보기</b>"
        titles = dict(text= title, x=0.5, y = 0.85, xanchor='center', yanchor= 'top')

        fig = make_subplots(specs=[[{'secondary_y': True}]]) 
        
        for index, value in enumerate(draw_list):
            fig.add_trace(
                go.Bar(x=mdf_change.index, y=mdf_change.loc[:,value],  name=value, marker_color= marker_colors[index]),     
                secondary_y=True
                )
        for index, value in enumerate(draw_list):
            fig.add_trace(
                go.Scatter(x=mdf.index, y=mdf.loc[:,value],  name=value, marker_color= marker_colors[index]),     
                secondary_y=False
                )
        fig.update_yaxes(title_text="매매지수", showticklabels= True, showgrid = True, zeroline=True, secondary_y = False)
        fig.update_yaxes(title_text="매매지수 변화", showticklabels= True, showgrid = False, zeroline=True, ticksuffix="%", secondary_y = True)
        fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template, xaxis_tickformat = '%Y.%m.%d')
        fig.add_vline(x="2019-1-14", line_dash="dash", line_color="gray")
        fig.update_layout(template="myID")
        fig.update_layout(hovermode="x unified")
        fig.add_vrect(x0="2022-11-07", x1="2022-11-14", 
              annotation_text="11.10대책", annotation_position="bottom left",
              fillcolor="red", opacity=0.25, line_width=0)
        fig.add_vrect(x0="2023-01-02", x1="2023-01-09", 
              annotation_text="1.3대책", annotation_position="bottom left",
              fillcolor="red", opacity=0.25, line_width=0)
        st.plotly_chart(fig)
    except KeyError as keys:
        st.write(f" {keys} KB에는 없음")

def draw_power(selected_dosi2, m_power, bubble_df3, flag):
    #bubble index chart
    titles = dict(text= '<b>['+selected_dosi2 +']</b>'+  flag+ '주간 전세파워-버블지수', x=0.5, y = 0.85, xanchor='center', yanchor= 'top') 

    fig = make_subplots(specs=[[{'secondary_y': True}]]) 
    
    # fig.add_trace(go.Bar(name = '매매지수증감', x = mdf.index, y = mdf_change[selected_city2].round(decimals=2), marker_color=  marker_colors[2]), secondary_y = True)
    # fig.add_trace(go.Bar(name = '전세지수증감', x = jdf.index, y = jdf_change[selected_city2].round(decimals=2), marker_color=  marker_colors[1]), secondary_y = True)

    
    fig.add_trace(go.Scatter(mode='lines', name = '전세파워', x =  m_power.index, y= m_power[selected_dosi2], marker_color = marker_colors[0]), secondary_y = True)
    # fig.add_trace(go.Scatter(mode='lines', name ='버블지수2', x =  bubble_df2.index, y= bubble_df2[selected_city2], marker_color = marker_colors[1]), secondary_y = False)
    fig.add_trace(go.Scatter(mode='lines', name ='버블지수2', x =  bubble_df3.index, y= bubble_df3[selected_dosi2], marker_color = marker_colors[3]), secondary_y = False)

    fig.update_layout(hovermode="x unified")
    fig.update_xaxes(showspikes=True, spikecolor="green", spikesnap="cursor", spikemode="across", spikethickness=0.5)
    fig.update_yaxes(showspikes=True)#, spikecolor="orange", spikethickness=0.5)
    fig.update_yaxes(title_text='버블지수', showticklabels= True, showgrid = False, zeroline=True, zerolinecolor=marker_colors[3], secondary_y = False) #ticksuffix="%"
    fig.update_yaxes(title_text='전세파워', showticklabels= True, showgrid = True, zeroline=True, zerolinecolor=marker_colors[0], secondary_y = True) #tickprefix="$", 
    fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template, xaxis_tickformat = '%Y-%m')
    fig.update_layout(template="myID")
    st.plotly_chart(fig)
    with st.expander("버블지수/전세파워 설명"):
            st.markdown("**전세파워**: 전체기간 (전세 누적 증감률 - 매매 누적 증감율)")
            st.markdown("**아기곰 방식**: 버블지수 =(관심지역매매가상승률-전국매매가상승률) - (관심지역전세가상승률-전국전세가상승률)")
            st.markdown("**곰곰이 방식**: 버블지수 = 매매가비율(관심지역매매가/전국평균매매가) - 전세가비율(관심지역전세가/전국평균전세가)")

def draw_power_table(power_df):
    #버블지수/전세파워 table 추가
    title = dict(text='주요 시-구 월간 전세파워-버블지수 합산 순위', x=0.5, y = 0.85, xanchor='center', yanchor= 'top')
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

# def draw_index_table(power_df):
    #버블지수/전세파워 table 추가
    # title = dict(text='주요 시-구 월간 전세파워-버블지수 합산 순위', x=0.5, y = 0.9) 
    # fig = go.Figure(data=[go.Table(
    #                     header=dict(values=['<b>지역</b>','<b>전세파워</b>', '<b>버블지수</b>', '<b>전세파워 rank</b>', \
    #                                         '<b>버블지수 rank</b>', '<b>전세+버블 score</b>', '<b>전체 rank</b>'],
    #                                 fill_color='royalblue',
    #                                 align=['right','left', 'left', 'left', 'left', 'left', 'left'],
    #                                 font=dict(color='white', size=12),
    #                                 height=40),
    #                     cells=dict(values=[power_df.index, power_df['전세파워'], power_df['버블지수'], power_df['jrank'], \
    #                                         power_df['brank'], power_df['score'], power_df['rank']], 
    #                                 fill=dict(color=['paleturquoise', 'white', 'white','white', 'white', 'white', 'white']),
    #                                 align=['right','left', 'left', 'left', 'left', 'left', 'left'],
    #                                 font_size=12,
    #                                 height=30))
    #                 ])
    # fig.update_layout(title = title, titlefont_size=15, legend=dict(orientation="h"), template="seaborn")
    # fig.update_layout(template="myID")
    # st.plotly_chart(fig)

def draw_Choroplethmapbox(df, geo_data, flag, last_week):
    #choroplethmapbax
    token = 'pk.eyJ1Ijoic2l6aXB1c3gyIiwiYSI6ImNrbzExaHVvejA2YjMyb2xid3gzNmxxYmoifQ.oDEe7h9GxzzUUc3CdSXcoA'
    for col in df.columns:
        df[col] = df[col].astype(str)
    df['text'] = '<b>' + df['short'] + '</b> <br>' + \
                    '매매증감:' + df['매매증감'] + '<br>' + \
                    '전세증감:' + df['전세증감']
    title = dict(text='<b>'+last_week+ '기준 '+flag[0]+' 주간'+ flag[1]+'</b>',  x=0.5, y = 0.85, xanchor = 'center', yanchor = 'top') 
    fig = go.Figure(go.Choroplethmapbox(geojson=geo_data, locations=df['code'], z=df[flag[1]].astype(float),
                            colorscale="Bluered", zmin=-0.8, zmax=0.8, marker_line_width=2))
                            #colorscale="Bluered", zmin=df[flag[1]].astype(float).min(), zmax=df[flag[1]].astype(float).max(), marker_line_width=2))
    fig.update_traces(  autocolorscale=True,
                        text=df['text'], # hover text
                        marker_line_color='black', # line markers between states
                        colorbar_title=flag[1])
    # fig.update_traces(hovertext=df['index'])
    fig.update_layout(mapbox_style="light", mapbox_accesstoken=token,
                    mapbox_zoom=8, mapbox_center = {"lat": 37.425, "lon": 126.993})
    fig.update_layout(title = title, titlefont_size=15, font=dict(color="gray"))
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    fig.update_layout(template="myID")
    st.plotly_chart(fig)

def draw_index_change_with_bar(last_df, flag, last_week):
    last_df = last_df.sort_values(by=flag[1], ascending=False)
    #상위 20과 하위 20만 slice
    if flag[0].startswith("실거래가"):
        kb_last_slice = last_df
    else:    
        kb_last_slice = last_df.iloc[[-1,-2,-3,-4,-5,-6,-7,-8,-9,-10,-11,-12,-13,-14,-15,\
            14,13,12,11,10,9,8,7,6,5,4,3,2,1,0]]
    title = dict(text='<b>'+last_week+ '기준 '+flag[0] +' 주간 '+flag[1]+'</b>',  x=0.5, y = 0.95, xanchor='center', yanchor= 'top') 
    if flag[1] == '매매증감':
        fig = px.bar(kb_last_slice, y= kb_last_slice.index, x=kb_last_slice.iloc[:,0], color=kb_last_slice.iloc[:,0], color_continuous_scale='Bluered', \
                    text=kb_last_slice.index, orientation='h')
        fig.add_vline(x=last_df.loc['전국','매매증감'], line_dash="dash", line_color="yellow", annotation_text=f"전국 증감률: {str(last_df.loc['전국','매매증감'])}", annotation_position="bottom right")
    else:
        fig = px.bar(kb_last_slice, y= kb_last_slice.index, x=kb_last_slice.iloc[:,1], color=kb_last_slice.iloc[:,1], color_continuous_scale='Bluered', \
                    text=kb_last_slice.index, orientation='h')
        fig.add_vline(x=last_df.loc['전국','전세증감'], line_dash="dash", line_color="yellow", annotation_text=f"전국 증감률: {str(last_df.loc['전국','전세증감'])}", annotation_position="bottom right")
    
    # fig.add_shape(type="line", x0=last_df.index[0], y0=last_df.iloc[0,0], x1=last_df.index[-1], y1=last_df.iloc[0,0], line=dict(color="MediumPurple",width=2, dash="dot"))
    fig.update_layout(title = title, titlefont_size=15, legend=dict(orientation="h"), template=template)
    fig.update_traces(texttemplate='%{label}', textposition='outside')
    fig.update_layout(uniformtext_minsize=6, uniformtext_mode='show')
    fig.update_xaxes(title_text=flag[1], showticklabels= True, showgrid = True, zeroline=True, zerolinecolor='LightPink', ticksuffix="%")
    fig.update_layout(template="myID")
    st.plotly_chart(fig)

def draw_index_change_with_bubble(last_df, flag, last_week):
    #매매/전세 증감률 Bubble Chart
    title = dict(text='<b>'+last_week+ '기준 '+flag+'지수 증감</b>', x=0.5, y = 0.95, xanchor='center', yanchor= 'top')
    fig = px.scatter(last_df, x='매매증감', y='전세증감', color='매매증감', size=abs(last_df['전세증감']*10), 
                        text= last_df.index, hover_name=last_df.index, color_continuous_scale='Bluered')
    fig.update_yaxes(zeroline=True, zerolinecolor='LightPink', ticksuffix="%")
    fig.update_xaxes(zeroline=True, zerolinecolor='LightPink', ticksuffix="%")
    fig.update_layout(title = title, titlefont_size=15, legend=dict(orientation="h"), template=template)
    fig.update_layout(hovermode="x unified")
    fig.update_layout(template="myID")
    st.plotly_chart(fig)

def draw_index_change_with_bubble_slice(citys, last_df, flag):
    slice_df = last_df.loc[citys,:]
    #매매/전세 증감률 Bubble Chart
    title = dict(text='<b>'+flag+'지수 증감</b>', x=0.5, y = 0.95, xanchor='center', yanchor= 'top') 
    fig = px.scatter(slice_df, x='매매증감', y='전세증감', color='매매증감', size=abs(slice_df['전세증감']*10), 
                        text= slice_df.index, hover_name=slice_df.index, color_continuous_scale='Bluered')
    fig.update_yaxes(zeroline=True, zerolinecolor='LightPink', ticksuffix="%")
    fig.update_xaxes(zeroline=True, zerolinecolor='LightPink', ticksuffix="%")
    fig.update_layout(title = title, titlefont_size=15, legend=dict(orientation="h"), template=template)
    fig.update_layout(hovermode="x unified")
    fig.update_layout(template="myID")
    st.plotly_chart(fig)

def run_price_index(selected_dosi2, selected_dosi3, mdf, jdf, mdf_change, jdf_change):
    if selected_dosi3 is not None:
        selected_dosi2 = selected_dosi3
    titles = dict(text= '<b>['+selected_dosi2 +']</b> KB 주간 매매-전세 지수', x=0.5, y = 0.9, xanchor='center', yanchor= 'top') 

    fig = make_subplots(specs=[[{'secondary_y': True}]]) 
    fig.add_trace(go.Bar(name = '매매지수증감', x = mdf.index, y = mdf_change[selected_dosi2].round(decimals=2), marker_color=  marker_colors[2]), secondary_y = True)
    fig.add_trace(go.Bar(name = '전세지수증감', x = jdf.index, y = jdf_change[selected_dosi2].round(decimals=2), marker_color=  marker_colors[1]), secondary_y = True)
    fig.add_trace(go.Scatter(mode='lines', name = '매매지수', x =  mdf.index, y= mdf[selected_dosi2], marker_color = marker_colors[2]), secondary_y = False)
    fig.add_trace(go.Scatter(mode='lines', name ='전세지수', x =  jdf.index, y= jdf[selected_dosi2], marker_color = marker_colors[1]), secondary_y = False)
    fig.update_layout(hovermode="x unified")
    # fig.update_xaxes(showspikes=True, spikecolor="green", spikesnap="cursor", spikemode="across", spikethickness=0.5)
    fig.update_yaxes(showspikes=True)#, spikecolor="orange", spikethickness=0.5)
    fig.update_yaxes(title_text='지수', showticklabels= True, showgrid = True, zeroline=False,  secondary_y = False) #ticksuffix="%"
    fig.update_yaxes(title_text='지수 증감', showticklabels= True, showgrid = False, zeroline=True, zerolinecolor='LightPink', secondary_y = True, ticksuffix="%") #tickprefix="$", 
    fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template, xaxis_tickformat = '%Y-%m')
    fig.update_layout(template="myID")
    fig.add_vline(x="2022-1-10", line_dash="dash", line_color="gray")
    #fig.add_hline(y=last_df.iloc[0,1], line_dash="dash", line_color="red", annotation_text=f"전국 증감률: {round(last_df.iloc[0,1],2)}", \
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
    fig.add_vrect(x0="2022-11-07", x1="2022-11-14", 
              annotation_text="11.10대책", annotation_position="bottom left",
              fillcolor="red", opacity=0.25, line_width=0)
    fig.add_vrect(x0="2023-01-02", x1="2023-01-09", 
              annotation_text="1.3대책", annotation_position="bottom left",
              fillcolor="red", opacity=0.25, line_width=0)
    fig.update_layout(
            showlegend=True,
            legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="left",
            x=0
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
                visible=False
            ),
            type="date",
            range=[kor_time - relativedelta(years=5), kor_time]
            )      
        )
    fig.update_layout(hovermode="x unified")
    st.plotly_chart(fig)

def draw_sentiment(selected_dosi, js_1, js_2, js_index):
    titles = dict(text= '<b>['+selected_dosi +']</b> 매수우위 지수', x=0.5, y = 0.9, xanchor='center', yanchor= 'top') 

    fig = make_subplots(specs=[[{'secondary_y': True}]]) 
    fig.add_trace(go.Scatter(line = dict(dash='dash'), name = '매도자 많음', x =  js_1.index, y= js_1[selected_dosi], marker_color = marker_colors[0]), secondary_y = False)
    fig.add_trace(go.Scatter(line = dict(dash='dot'), name ='매수자 많음', x =  js_2.index, y= js_2[selected_dosi], marker_color = marker_colors[2]), secondary_y = False)                                             
    fig.add_trace(go.Scatter(mode='lines', name ='매수매도 지수', x =  js_index.index, y= js_index[selected_dosi], marker_color = marker_colors[1]), secondary_y = False)
    #fig.add_trace(go.Scatter(x=[js_index.index[-2]], y=[99.0], text=["100>매수자많음"], mode="text"))
    fig.add_trace(go.Scatter(mode='lines', name ='6m 이동평균', x =  js_index.index, y= js_index[selected_dosi].rolling(window=24, min_periods=1).mean(), \
         marker_color = 'blue'), secondary_y = False)
    #fig.add_shape(type="line", x0=js_index.index[0], y0=100.0, x1=js_index.index[-1], y1=100.0, line=dict(color="MediumPurple",width=2, dash="dot"))
    fig.add_hline(y=40.0, line_width=2, line_dash='dot', line_color="red", annotation_text="40 이상 매매지수 상승", annotation_position="bottom right", secondary_y=False)
    fig.add_hline(y=100.0, line_width=2, line_dash='dash', line_color="MediumPurple", annotation_text="100>매수자많음", annotation_position="bottom right", secondary_y=False)
    fig.update_yaxes(title_text='지수', showticklabels= True, showgrid = True, zeroline=True, zerolinecolor='LightPink', secondary_y = False) #ticksuffix="%"
    fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template, xaxis_tickformat = '%Y-%m-%d')
    fig.update_layout(template="myID")
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
    fig.add_vrect(x0="2022-11-07", x1="2022-11-14", 
              annotation_text="11.10대책", annotation_position="bottom left",
              fillcolor="red", opacity=0.25, line_width=0)
    fig.add_vrect(x0="2023-01-02", x1="2023-01-09", 
              annotation_text="1.3대책", annotation_position="bottom left",
              fillcolor="red", opacity=0.25, line_width=0)
    fig.update_layout(
            showlegend=True,
            legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="left",
            x=0
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
                visible=False
            ),
            type="date",
            range=[kor_time - relativedelta(years=5), kor_time]
            )      
        )
    fig.update_layout(hovermode="x unified")
    st.plotly_chart(fig)

def draw_sentiment_change(selected_dosi, mdf_change, js_index):
    mdf_change.loc[:,'color'] = np.where(mdf_change.iloc[:,0]<0, '#FFB8B1', '#E2F0CB')
    x_data = mdf_change.index
    title = "<b>["+selected_dosi+"]</b> 매수우위지수와 매매증감"
    titles = dict(text= title,  x=0.5, y = 0.9, xanchor='center', yanchor= 'top') 
    fig = make_subplots(specs=[[{'secondary_y': True}]]) 
    fig.add_trace(go.Bar(name = "매매증감", x = x_data, y =round(mdf_change[selected_dosi],2), 
                        text = round(mdf_change[selected_dosi],2), textposition = 'outside', 
                        marker_color= mdf_change.loc[:,'color']), secondary_y = True) 
    fig.add_trace(go.Scatter(mode='lines', name ='매수매도 지수', x =  js_index.index, y= js_index[selected_dosi], marker_color = marker_colors[1]), secondary_y = False)
    fig.update_traces(texttemplate='%{text:.3s}') 
    #fig.add_shape(type="line", x0=js_index.index[0], y0=100.0, x1=js_index.index[-1], y1=100.0, line=dict(color="MediumPurple",width=2, dash="dot"))
    fig.add_hline(y=40.0, line_width=2, line_dash='dot', line_color="MediumPurple", annotation_text="40 이상인 경우 매매지수 상승", annotation_position="bottom right", secondary_y=False)
    fig.add_hline(y=mdf_change[selected_dosi].mean(), line_width=2, line_dash="dash", line_color="blue",  annotation_text="평균상승률: "+str(round(mdf_change[selected_dosi].mean(),2)), annotation_position="bottom right", secondary_y = True)
    fig.update_yaxes(title_text="매수우위지수", showticklabels= True, showgrid = True, zeroline=True, secondary_y = False)
    fig.update_yaxes(title_text="매매증감", showticklabels= True, showgrid = False, zeroline=True, ticksuffix="%", secondary_y = True)
    fig.update_layout(title = titles, titlefont_size=15, template=template, xaxis_tickformat = '%Y-%m-%d')
    #fig.update_layout(legend=dict( orientation="h", yanchor="bottom", y=1, xanchor="right",  x=0.95))
    fig.update_layout(
                               showlegend=True,
                                legend=dict(
                                            orientation="h",
                                            yanchor="bottom",
                                            y=-0.2,
                                            xanchor="left",
                                            x=0
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
                                    visible=False
                                ),
                                type="date",
                                range=[kor_time - relativedelta(years=5), kor_time]
                                )      
                            )
    fig.update_layout(hovermode="x unified")
    fig.update_layout(template="myID")
    st.plotly_chart(fig)

def run_one_index(selected_dosi2, selected_dosi3, omdf, ojdf, omdf_change, ojdf_change):
    if selected_dosi3 is not None:
        selected_dosi2 = selected_dosi3
    titles = dict(text= '<b>['+selected_dosi2 +']</b> 부동산원 주간 매매-전세 지수', x=0.5, y = 0.9, xanchor='center', yanchor= 'top') 

    fig = make_subplots(specs=[[{'secondary_y': True}]]) 
    fig.add_trace(go.Bar(name = '매매지수증감', x = omdf.index, y = omdf_change[selected_dosi2].round(decimals=2), marker_color=  marker_colors[2]), secondary_y = True)
    fig.add_trace(go.Bar(name = '전세지수증감', x = ojdf.index, y = ojdf_change[selected_dosi2].round(decimals=2), marker_color=  marker_colors[1]), secondary_y = True)
    fig.add_trace(go.Scatter(mode='lines', name = '매매지수', x =  omdf.index, y= omdf[selected_dosi2], marker_color = marker_colors[2]), secondary_y = False)
    fig.add_trace(go.Scatter(mode='lines', name ='전세지수', x =  ojdf.index, y= ojdf[selected_dosi2], marker_color = marker_colors[1]), secondary_y = False)
    # fig.update_xaxes(showspikes=True, spikecolor="green", spikesnap="cursor", spikemode="across", spikethickness=0.5)
    fig.update_yaxes(showspikes=True)#, spikecolor="orange", spikethickness=0.5)
    fig.update_yaxes(title_text='지수', showticklabels= True, showgrid = True, zeroline=False,  secondary_y = False) #ticksuffix="%"
    fig.update_yaxes(title_text='지수 증감', showticklabels= True, showgrid = False, zeroline=True, zerolinecolor='LightPink', secondary_y = True, ticksuffix="%") #tickprefix="$", 
    fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template, xaxis_tickformat = '%Y-%m-%d')
    fig.add_vline(x="2021-6-28", line_dash="dash", line_color="gray")
    fig.update_layout(template="myID")
    #fig.add_hline(y=last_df.iloc[0,1], line_dash="dash", line_color="red", annotation_text=f"전국 증감률: {round(last_df.iloc[0,1],2)}", \
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
    fig.add_vrect(x0="2022-11-07", x1="2022-11-14", 
              annotation_text="11.10대책", annotation_position="bottom left",
              fillcolor="red", opacity=0.25, line_width=0)
    fig.add_vrect(x0="2023-01-02", x1="2023-01-09", 
              annotation_text="1.3대책", annotation_position="bottom left",
              fillcolor="red", opacity=0.25, line_width=0)
    fig.update_layout(
            showlegend=True,
            legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=-0.2,
                        xanchor="left",
                        x=0
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
                visible=False
            ),
            type="date",
            range=[kor_time - relativedelta(years=5), kor_time]
            )      
        )
    fig.update_layout(hovermode="x unified")
    st.plotly_chart(fig)

def run_one_index_all(draw_list, omdf, ojdf, omdf_change, ojdf_change, gu_city, city3, city_series) :
    if city3 in draw_list:
        draw_list = city_series[city_series.str.contains(city3)].to_list()
    if city3 in gu_city:
        draw_list = city_series[city_series.str.contains(city3)].to_list()
  
    omdf_change = omdf_change.round(decimals=2)
    title = "<b>부동산원 매매지수 변화 같이 보기</b>"
    titles = dict(text= title, x=0.5, y = 0.9, xanchor='center', yanchor= 'top') 
    
    fig = make_subplots(specs=[[{'secondary_y': True}]]) 
    
    for index, value in enumerate(draw_list):
        fig.add_trace(
            go.Bar(x=omdf_change.index, y=omdf_change.loc[:,value],  name=value, marker_color= marker_colors[index]),    
            secondary_y=True,
            )
    for index, value in enumerate(draw_list):
        fig.add_trace(
            go.Scatter(x=omdf.index, y=omdf.loc[:,value],  name=value, marker_color= marker_colors[index]),    
            secondary_y=False,
            )
    fig.update_yaxes(title_text="매매지수", showticklabels= True, showgrid = True, zeroline=True, secondary_y = False)
    fig.update_yaxes(title_text="매매지수 변화", showticklabels= True, showgrid = False, zeroline=True, ticksuffix="%", secondary_y = True)
    fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template, xaxis_tickformat = '%Y.%m.%d')
    fig.add_vrect(x0="2022-11-07", x1="2022-11-14", 
              annotation_text="11.10대책", annotation_position="bottom left",
              fillcolor="red", opacity=0.25, line_width=0)
    fig.add_vrect(x0="2023-01-02", x1="2023-01-09", 
              annotation_text="1.3대책", annotation_position="bottom left",
              fillcolor="red", opacity=0.25, line_width=0)
    fig.update_layout(
                        showlegend=True,
                        legend=dict(
                                    orientation="h",
                                    yanchor="bottom",
                                    y=-0.2,
                                    xanchor="left",
                                    x=0
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
                            visible=False
                        ),
                        type="date",
                        range=[kor_time - relativedelta(years=5), kor_time]
                        )      
                    )
    fig.update_layout(template="myID")
    fig.update_layout(hovermode="x unified")
    st.plotly_chart(fig)

def run_one_index_together(draw_list, omdf, omdf_change, flag):
    title = f"<b>{flag} 매매지수 변화 같이 보기</b>"
    titles = dict(text= title, x=0.5, y = 0.9, xanchor='center', yanchor= 'top')

    fig = make_subplots(specs=[[{'secondary_y': True}]]) 
    
    for index, value in enumerate(draw_list):
        fig.add_trace(
            go.Bar(x=omdf_change.index, y=omdf_change.loc[:,value],  name=value, marker_color= marker_colors[index]),    
            secondary_y=True,
            )
    for index, value in enumerate(draw_list):
        fig.add_trace(
            go.Scatter(x=omdf.index, y=omdf.loc[:,value],  name=value, marker_color= marker_colors[index]),    
            secondary_y=False,
            )
    fig.update_yaxes(title_text="매매지수", showticklabels= True, showgrid = True, zeroline=True, secondary_y = False)
    fig.update_yaxes(title_text="매매지수 증감", showticklabels= True, showgrid = False, zeroline=True, ticksuffix="%", secondary_y = True)
    fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template, xaxis_tickformat = '%Y.%m.%d')
    fig.add_vrect(x0="2022-11-07", x1="2022-11-14", 
              annotation_text="11.10대책", annotation_position="bottom left",
              fillcolor="red", opacity=0.25, line_width=0)
    fig.add_vrect(x0="2023-01-02", x1="2023-01-09", 
              annotation_text="1.3대책", annotation_position="bottom left",
              fillcolor="red", opacity=0.25, line_width=0)
    fig.update_layout(template="myID")
    fig.update_layout(hovermode="x unified")
    fig.update_layout(
                    showlegend=True,
                    legend=dict(
                                orientation="h",
                                yanchor="bottom",
                                y=-0.2,
                                xanchor="left",
                                x=0
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
                        visible=False
                    ),
                    type="date",
                    range=[kor_time - relativedelta(years=5), kor_time]
                    )      
                )
    st.plotly_chart(fig)

def run_one_jindex_together(draw_list, omdf, omdf_change, flag):
    title = f"<b>{flag} 전세지수 변화 같이 보기</b>"
    titles = dict(text= title, x=0.5, y = 0.9, xanchor='center', yanchor= 'top') 

    fig = make_subplots(specs=[[{'secondary_y': True}]]) 
    
    for index, value in enumerate(draw_list):
        fig.add_trace(
            go.Bar(x=omdf_change.index, y=omdf_change.loc[:,value],  name=value, marker_color= marker_colors[index]),    
            secondary_y=True,
            )
    for index, value in enumerate(draw_list):
        fig.add_trace(
            go.Scatter(x=omdf.index, y=omdf.loc[:,value],  name=value, marker_color= marker_colors[index]),    
            secondary_y=False,
            )
    fig.update_yaxes(title_text="전세지수", showticklabels= True, showgrid = True, zeroline=True, secondary_y = False)
    fig.update_yaxes(title_text="전세지수 증감", showticklabels= True, showgrid = False, zeroline=True, ticksuffix="%", secondary_y = True)
    fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template, xaxis_tickformat = '%Y.%m.%d')
    fig.update_layout(template="myID")
    fig.update_layout(hovermode="x unified")
    fig.add_vrect(x0="2022-11-07", x1="2022-11-14", 
              annotation_text="11.10대책", annotation_position="bottom left",
              fillcolor="red", opacity=0.25, line_width=0)
    fig.add_vrect(x0="2023-01-02", x1="2023-01-09", 
              annotation_text="1.3대책", annotation_position="bottom left",
              fillcolor="red", opacity=0.25, line_width=0)
    fig.update_layout(
                    showlegend=True,
                    legend=dict(
                                orientation="h",
                                yanchor="bottom",
                                y=-0.2,
                                xanchor="left",
                                x=0
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
                        visible=False
                    ),
                    type="date",
                    range=[kor_time - relativedelta(years=5), kor_time]
                    )      
                )
    st.plotly_chart(fig)

def draw_flower(select_city, selected_dosi3, cum_mdf, cum_jdf, flag):
    if selected_dosi3 is not None:
        select_city = selected_dosi3
    #매매/전세 증감률 flower Chart
    title = dict(text=f'<b> ['+ select_city+'] '+flag+  ' 지수 변화 누적 </b>', x=0.5, y = 0.85, xanchor='center', yanchor= 'top')
    fig = go.Figure(data=go.Scatter(x=cum_mdf[select_city]*100, y = cum_jdf[select_city]*100,
        mode='markers+lines',
        hovertext=cum_mdf.index.strftime("%Y-%m-%d"),
        marker=dict(
            size=abs(cum_jdf[select_city])*10,
            #color=px.colors.qualitative.Set1[index],
            color=cum_mdf[select_city], #set color equal to a variable
            colorscale='bluered', # one of plotly colorscales
            showscale=True
        )
    )) 
    fig.update_yaxes(title_text="전세지수 누적", zeroline=True, zerolinecolor='LightPink', ticksuffix="%")
    fig.update_xaxes(title_text="매매지수 누적", zeroline=True, zerolinecolor='LightPink', ticksuffix="%")
    fig.update_layout(title = title, titlefont_size=15, legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="left", x=0), template=template)
    fig.update_layout(template="myID")
    fig.update_layout(hovermode="x unified")
    st.plotly_chart(fig)

def draw_flower_together(citys, cum_mdf, cum_jdf, flag):

    #매매/전세 증감률 flower Chart
    title = dict(text=f'<b>{flag} 지수 변화 누적 같이 보기 </b>', x=0.5, y = 0.85, xanchor='center', yanchor= 'top')
    fig = go.Figure()
    for index, value in enumerate(citys):
        fig.add_trace(
            go.Scatter(
                x = cum_mdf[value]*100, y = cum_jdf[value]*100, name=value,
                mode='markers+lines',
                hovertext=cum_mdf.index.strftime("%Y.%m.%d"),
                marker=dict(
                    size=abs(cum_jdf[value])*10,
                    color=px.colors.qualitative.Dark24[index]
                    # color=cum_mdf[value], #set color equal to a variable
                    # colorscale='bluered', # one of plotly colorscales
                    # showscale=True
                )
            )
        )
    fig.update_yaxes(title_text="전세지수 누적", zeroline=True, zerolinecolor='LightPink', ticksuffix="%")
    fig.update_xaxes(title_text="매매지수 누적", zeroline=True, zerolinecolor='LightPink', ticksuffix="%")
    fig.update_layout(title = title, titlefont_size=15, legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="left", x=0), template=template)
    fig.update_layout(hovermode="x unified", template="myID")
    st.plotly_chart(fig)

def draw_change_table(change_df,flag):
    #버블지수/전세파워 table 추가
    title = dict(text=f'<b>{flag} 기간 상승률 분석</b>', x=0.5, y = 0.85, xanchor='center', yanchor= 'top') 
    fig = go.Figure(data=[go.Table(
                        header=dict(values=['<b>지역</b>','<b>매매증감</b>', '<b>전세증감</b>'],
                                    fill_color='royalblue',
                                    align=['right','left', 'left'],
                                    font=dict(color='white', size=12),
                                    height=40),
                        cells=dict(values=[change_df.index, change_df['매매증감'], change_df['전세증감']], 
                                    fill=dict(color=['black', 'gray', 'gray']),
                                    align=['right','left', 'left'],
                                    font_size=12,
                                    height=30))
                    ])
    fig.update_layout(title = title, titlefont_size=15, legend=dict(orientation="h"), template=template)
    fig.update_layout(template="myID")
    st.plotly_chart(fig)

def draw_senti_last(to_df, last_week):
    #매매/전세 증감률 Bubble Chart
    flag = "KB 주간 시계열"
    title = dict(text='<b>'+last_week+'기준 '+flag+' 매수우위와 전세수급 지수</b>', x=0.5, y = 0.95, xanchor='center', yanchor= 'top') 
    template = "ggplot2"
    fig = px.scatter(to_df, x='매수우위지수', y='전세수급지수', color='매수우위지수', size=abs(to_df['전세수급지수']*10), 
                        text= to_df.index, hover_name=to_df.index, color_continuous_scale='Bluered')
    fig.update_yaxes(zeroline=True, zerolinecolor='LightPink')#, ticksuffix="%")
    fig.update_xaxes(zeroline=True, zerolinecolor='LightPink')#, ticksuffix="%")
    fig.add_hline(y=100.0, line_width=2, line_dash="solid", line_color="blue",  annotation_text="매수우위지수가 100을 초과할수록 '공급부족' 비중이 높음 ", annotation_position="bottom right")
    fig.add_vline(x=100.0, line_width=2, line_dash="solid", line_color="blue",  annotation_text="전세수급지수가 100을 초과할수록 '매수자가 많다'를, 100 미만일 경우 '매도자가 많다'를 의미 ", annotation_position="top left")
    fig.add_vline(x=40.0, line_width=1, line_dash="dot", line_color="red",  annotation_text="40 이상 매매지수 상승 가능성 높음", annotation_position="top left")
    fig.update_layout(title = title, titlefont_size=15, legend=dict(orientation="h"), template=template)
    fig.update_layout(template="myID")
    st.plotly_chart(fig)

def draw_senti_together(maesu_index, city_lists, last_week):
    #매수우위지수 같이 보기
    flag = "KB 주간 시계열"
    maesu_index.index = pd.to_datetime(maesu_index.index, format = '%Y-%m-%d')
    titles = dict(text=f'<b>{last_week}기준 {flag} 매수우위지수 같이 보기 </b>', x=0.5, y = 0.9, xanchor='center', yanchor= 'top')
    fig = go.Figure()

    for index, value in enumerate(city_lists):
        fig.add_trace(
            go.Scatter(
                x=maesu_index.index, y=maesu_index.loc[:,value], mode='lines+markers', name=value, 
                marker=dict(
                   color=px.colors.qualitative.Set1[index], #set color equal to a variable
                #    colorscale='bluered', # one of plotly colorscales
                #    showscale=True
                )   
            ))
    fig.update_yaxes(title_text="매수우위지수", showticklabels= True, showgrid = True, zeroline=True)
    fig.add_hline(y=100.0, line_width=1, line_dash="dot", line_color="blue",  annotation_text="매수우위지수가 100을 초과할수록 '공급부족' 비중이 높음 ", annotation_position="bottom right")
    fig.add_hline(y=40.0, line_width=1, line_dash="dash", line_color="red",  annotation_text="매수우위지수가 40을 초과할 때 가격 상승 ", annotation_position="bottom right")
    fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template, xaxis_tickformat = '%Y-%m-%d')
    fig.update_layout(
                    showlegend=True,
                    legend=dict(
                                orientation="h",
                                yanchor="bottom",
                                y=-0.2,
                                xanchor="left",
                                x=0
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
                        visible=False
                    ),
                    type="date",
                    range=[kor_time - relativedelta(years=5), kor_time]
                    )      
                )
    fig.update_layout(template="myID")
    st.plotly_chart(fig)    

def draw_jeon_sentiment(selected_dosi, js_1, js_2, js_index):
    titles = dict(text= '<b>['+selected_dosi +']</b> 전세수급 지수', x=0.5, y = 0.9, xanchor='center', yanchor= 'top') 

    fig = make_subplots(specs=[[{'secondary_y': True}]]) 
    fig.add_trace(go.Scatter(line = dict(dash='dash'), name = '수요>공급', x =  js_1.index, y= js_1[selected_dosi], marker_color = marker_colors[0]), secondary_y = False)
    fig.add_trace(go.Scatter(line = dict(dash='dot'), name ='수요<공급', x =  js_2.index, y= js_2[selected_dosi], marker_color = marker_colors[2]), secondary_y = False)                                             
    fig.add_trace(go.Scatter(mode='lines', name ='전세수급 지수', x =  js_index.index, y= js_index[selected_dosi], marker_color = marker_colors[1]), secondary_y = False)
    #fig.add_trace(go.Scatter(x=[js_index.index[-2]], y=[99.0], text=["100을 초과할수록 '공급부족' 비중이 높음"], mode="text"))
    #fig.add_shape(type="line", x0=js_index.index[0], y0=100.0, x1=js_index.index[-1], y1=100.0, line=dict(color="MediumPurple",width=2, dash="dot"))
    fig.add_hline(y=100.0, line_width=2, line_dash='dash', line_color="MediumPurple", annotation_text="100을 초과할수록 '공급부족' 비중이 높음", annotation_position="bottom right", secondary_y=False)
    fig.update_yaxes(title_text='지수', showticklabels= True, showgrid = True, zeroline=True, zerolinecolor='LightPink', secondary_y = False) #ticksuffix="%"
    fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template, xaxis_tickformat = '%Y-%m-%d')
    fig.update_layout(template="myID")
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
    fig.add_vrect(x0="2022-11-07", x1="2022-11-14", 
              annotation_text="11.10 규제지역해제", annotation_position="bottom left",
              fillcolor="red", opacity=0.25, line_width=0)
    fig.add_vrect(x0="2023-01-02", x1="2023-01-09", 
              annotation_text="1.3대책", annotation_position="bottom left",
              fillcolor="red", opacity=0.25, line_width=0)
    fig.update_layout(
            showlegend=True,
            legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=-0.2,
                        xanchor="left",
                        x=0
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
                visible=False
            ),
            type="date",
            range=[kor_time - relativedelta(years=5), kor_time]
            )      
        )
    fig.update_layout(hovermode="x unified")
    st.plotly_chart(fig)

def draw_jeon_sentiment_change(selected_dosi, jdf_change, js_index):
    jdf_change.loc[:,'color'] = np.where(jdf_change.iloc[:,0]<0, '#FFB8B1', '#E2F0CB')
    x_data = jdf_change.index
    title = "<b>["+selected_dosi+"]</b> 전세수급지수와 전세증감"
    titles = dict(text= title,  x=0.5, y = 0.9, xanchor='center', yanchor= 'top') 
    fig = make_subplots(specs=[[{'secondary_y': True}]]) 
    fig.add_trace(go.Bar(name = "전세증감", x = x_data, y =round(jdf_change[selected_dosi],2), 
                        text = round(jdf_change[selected_dosi],2), textposition = 'outside', 
                        marker_color= jdf_change.loc[:,'color']), secondary_y = True) 
    fig.add_trace(go.Scatter(mode='lines', name ='전세수급지수', x =  js_index.index, y= js_index[selected_dosi], marker_color = marker_colors[1]), secondary_y = False)
    fig.update_traces(texttemplate='%{text:.3s}') 
    fig.add_shape(type="line", x0=js_index.index[0], y0=100.0, x1=js_index.index[-1], y1=100.0, line=dict(color="MediumPurple",width=2, dash="dot"))
    fig.add_hline(y=jdf_change[selected_dosi].mean(), line_width=2, line_dash="dash", line_color="blue",  annotation_text="평균상승률: "+str(round(jdf_change[selected_dosi].mean(),2)), annotation_position="bottom right", secondary_y = True)
    fig.update_yaxes(title_text="전세수급지수", showticklabels= True, showgrid = True, zeroline=True, secondary_y = False)
    fig.update_yaxes(title_text="전세증감", showticklabels= True, showgrid = False, zeroline=True, ticksuffix="%", secondary_y = True)
    fig.update_layout(title = titles, titlefont_size=15, template=template, xaxis_tickformat = '%Y-%m-%d')
    #fig.update_layout(legend=dict( orientation="h", yanchor="bottom", y=1, xanchor="right",  x=0.95))
    fig.update_layout(
                    showlegend=True,
                    legend=dict(
                                orientation="h",
                                yanchor="bottom",
                                y=-0.2,
                                xanchor="left",
                                x=0
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
                        visible=False
                    ),
                    type="date",
                    range=[kor_time - relativedelta(years=5), kor_time]
                    )      
                )
    fig.update_layout(hovermode="x unified")
    fig.update_layout(template="myID")
    st.plotly_chart(fig)

def draw_senti_desu(select_city, mg_df, ms_df, jsp_df, jg_df, mdf, jdf):
    local_df = pd.DataFrame()
    local_df['매매공급'] = mg_df.loc[:,select_city]
    local_df['전세공급'] = jg_df.loc[:,select_city]
    local_df['매매수요'] = ms_df.loc[:,select_city]
    local_df['전세수요'] = jsp_df.loc[:,select_city]
    sum_s = local_df.sum(axis=1)
    df = local_df.divide(sum_s, axis=0)
    df = round(df*100,2)

    marker_colors = ['rgb(0,0,255)', 'rgb(0,255,225)', 'rgb(255,192,203)', 'rgb(255,0,0)', 'rgb(0,0,0)', 'rgb(255,255,0)']
    title = "<b>KB 심리지수로 보는 [" + select_city+"] 수요공급 비중</b>"
    titles = dict(text= title, x=0.5, y = 0.85, xanchor='center', yanchor= 'top') 
    fig = make_subplots(specs=[[{'secondary_y': True}]]) 

    fig.add_trace(go.Bar(x=df.index, y=df["전세수요"], name="전세수요", marker_color=marker_colors[0]), secondary_y=False)
    fig.add_trace(go.Bar(x=df.index, y=df["매매수요"], name='매매수요',  marker_color= marker_colors[1]), secondary_y=False)
    fig.add_trace(go.Bar(x=df.index, y=df["전세공급"], name='전세공급',  marker_color= marker_colors[2]), secondary_y=False)
    fig.add_trace(go.Bar(x=df.index, y=df["매매공급"], name='매매공급',  marker_color= marker_colors[3]), secondary_y=False)
    fig.add_trace(go.Scatter(x=mdf.index, y=mdf[select_city], name='매매지수',  marker_color= marker_colors[4]), secondary_y=True)
    fig.add_trace(go.Scatter(x=jdf.index, y=jdf[select_city], name='전세지수',  marker_color= marker_colors[5]), secondary_y=True)
    fig.update_yaxes(title= "심리지수 비중", zeroline=False, zerolinecolor='LightPink', ticksuffix="%", secondary_y = False)
    fig.update_layout(barmode='relative', title = titles, legend=dict(orientation="h"),  xaxis_tickformat = '%Y-%m-%d')
    fig.add_hline(y=50.0, line_width=2, line_dash='dash', line_color="white", secondary_y=False)
    fig.update_layout(template="myID")
    st.plotly_chart(fig)


    # 통계 차트 
    # KB 부동산원 같이 보기
def histogram_together(last_df, last_odf, flag):
    title = dict(text='<b>주간 KB/부동산원</b> 아파트 '+flag+' 상승률 빈도수 비교', x=0.5, y = 0.85, xanchor='center', yanchor= 'top')
    if flag == "전세가격":
        mae_jeon_flag = "매매증감"
    else:
        mae_jeon_flag = "전세증감"
    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=last_df[mae_jeon_flag],
    # histnorm='percent',
        name='KB', # name used in legend and hover labels
        xbins=dict( # bins used for histogram
            # start=-4.0,
            # end=3.0,
            size=0.01
        ),
        texttemplate="%{y}",
        marker_color='rgb(205,32,40)',
        opacity=0.75
    ))
    fig.add_trace(go.Histogram(
        x=last_odf[mae_jeon_flag],
        #histnorm='percent',
        name='부동산원',
        xbins=dict(
            # start=-3.0,
            # end=4,
            size=0.01
        ),
        texttemplate="%{y}",
        marker_color='rgb(22,108,150)',
        opacity=0.5
    ))

    fig.update_layout(
        title = title, titlefont_size=15, legend=dict(orientation="h"),
        #title_text='주간 KB/부동산원 아파트 매매가격 상승률 빈도수 비교', # title of plot
        xaxis_title_text='증감률', # xaxis label
        yaxis_title_text='지역수', # yaxis label
        bargap=0.2, # gap between bars of adjacent location coordinates
        bargroupgap=0.1 # gap between bars of the same location coordinates
    )
    fig.update_layout(barmode='overlay', template="myID")
    st.plotly_chart(fig, use_container_width=True)

def histogram_chart(last_odf, flag, flag2):
    title = dict(text='<b>'+flag+'</b> 주간부동산 '+ flag2+' 빈도수', x=0.5, y = 0.95, xanchor='center', yanchor= 'top', color_discrete_sequence=['indianred'])
    fig = px.histogram(last_odf, x=flag2, hover_data=last_odf.columns, marginal="box", text_auto=True)
    fig.update_layout(
        xaxis_title_text='증감율(0.01% 범위)', # xaxis label
        yaxis_title_text='지역수', # yaxis label
        bargap=0.1, # gap between bars of adjacent location coordinates
        bargroupgap=0.1 # gap between bars of the same location coordinates
    )
    fig.update_layout(title = title, titlefont_size=15, legend=dict(orientation="h"))
    st.plotly_chart(fig)