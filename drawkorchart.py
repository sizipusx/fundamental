import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots
import FinanceDataReader as fdr

import streamlit as st
from datetime import datetime

#챠트 기본 설정
# colors 
# marker_colors = ['#34314c', '#47b8e0', '#ff7473', '#ffc952', '#3ac569']
marker_colors = ['rgb(27,38,81)', 'rgb(205,32,40)', 'rgb(22,108,150)', 'rgb(255,69,0)', 'rgb(237,234,255)']
template = 'ggplot2' #"plotly", "plotly_white", "plotly_dark", "ggplot2", "seaborn", "simple_white", "none"
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


def income_chart(input_ticker, company_name, income_df, income_df_q, dis_flag):
    with st.container():
        col1, col2, col3 = st.columns([30,2,30])
        with col1:
            # Profit and Margin
            st.subheader('Annual Profit, Margin ')
            column_name_ch = income_df.columns[0]
            x_data = income_df.index
            title = '('  + company_name + ') <b>Annual Profit & Margin</b>'
            titles = dict(text= title, x=0.5, y = 0.85) 
            fig = make_subplots(specs=[[{'secondary_y': True}]]) 
            y_data_bar = [column_name_ch, '영업이익', '당기순이익']
            if dis_flag == True:
                y_data_line = ['영업이익률', '순이익률', 'ROE']
            else:
                y_data_line = ['영업이익률', '지배주주순이익률', 'ROE']

            for y_data, color in zip(y_data_bar, marker_colors) :
                fig.add_trace(go.Bar(name = y_data, x = x_data, y = income_df.loc[:,y_data], 
                                            text= income_df[y_data], textposition = 'inside', marker_color= color), secondary_y = False) 
            
            for y_data, color in zip(y_data_line, marker_colors): 
                fig.add_trace(go.Scatter(mode='lines+markers+text', 
                                            name = y_data, x =  x_data, y= income_df.loc[:,y_data],
                                            text= income_df[y_data], textposition = 'top center', marker_color = color),
                                            secondary_y = True)
            #fig.update_traces(texttemplate='%{text:.3s}') 
            fig.update_yaxes(title_text='Profit', range=[0, max(income_df.loc[:,y_data_bar[0]])*2], secondary_y = False)
            #fig.update_yaxes(title_text='Profit', range=[0, max(income_df.loc[:,y_data_bar[0]])*2], secondary_y = False)
            fig.update_yaxes(title_text='Margin', range=[-max(income_df.loc[:,y_data_line[0]]), max(income_df.loc[:,y_data_line[0]])* 1.2], secondary_y = True)
            fig.update_yaxes(showticklabels= True, showgrid = False, zeroline=True, ticksuffix="억원", secondary_y = False)
            fig.update_yaxes(showticklabels= True, showgrid = False, zeroline=True, ticksuffix="%", secondary_y = True)
            fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template)#, xaxis_tickformat = '%Y.%m')
            fig.update_layout(template="myID")
            st.plotly_chart(fig)
        with col2:
                st.write("")
        with col3: 
            # Profit and Margin
            st.subheader('Quartly Profit, Margin ')
            x_data = income_df_q.index
            title = '('  + company_name + ') <b>Quartly Profit & Margin</b>'
            titles = dict(text= title, x=0.5, y = 0.85) 
            fig = make_subplots(specs=[[{'secondary_y': True}]]) 
            y_data_bar = [column_name_ch, '영업이익', '당기순이익']
            if dis_flag == True:
                y_data_line = ['영업이익률', '순이익률', 'ROE']
            else:
                y_data_line = ['영업이익률', '지배주주순이익률', 'ROE']

            for y_data, color in zip(y_data_bar, marker_colors) :
                fig.add_trace(go.Bar(name = y_data, x = income_df_q.index, y = income_df_q.loc[:,y_data], 
                                    text= income_df[y_data], textposition = 'inside', marker_color= color), secondary_y = False) 
            
            for y_data, color in zip(y_data_line, marker_colors): 
                fig.add_trace(go.Scatter(mode='lines+markers+text', 
                                            name = y_data, x =  income_df_q.index, y= income_df_q.loc[:,y_data],
                                            text= income_df_q[y_data], textposition = 'top center', marker_color = color),
                                            secondary_y = True)
            #fig.update_traces(texttemplate='%{text:.3s}') 
            fig.update_yaxes(title_text='Revenue', range=[0, max(income_df_q.loc[:,y_data_bar[0]])*2], secondary_y = False)
            fig.update_yaxes(title_text='Income', range=[-max(income_df_q.loc[:,y_data_line[0]]), max(income_df_q.loc[:,y_data_line[0]])* 1.2], secondary_y = True)
            fig.update_yaxes(showticklabels= True, showgrid = False, zeroline=True, ticksuffix="억원", secondary_y = False)
            fig.update_yaxes(showticklabels= True, showgrid = False, zeroline=True, ticksuffix="%", secondary_y = True)
            fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template, xaxis_tickformat = '%Y.%m')
            fig.update_layout(template="myID")
            st.plotly_chart(fig)


def balance_chart(input_ticker, company_name, balance_df):
    #부채비율, 유동비율, 당좌비율
    st.subheader('Asset, Liabilities, ShareholderEquity')
    x_data = balance_df.index
    title = '('  + company_name + ') <b>Asset & Liabilities</b>'
    titles = dict(text= title, x=0.5, y = 0.85) 
    fig = make_subplots(specs=[[{'secondary_y': True}]]) 
    #y_data_bar3 = ['totalAssets', 'totalLiabilities', 'totalShareholderEquity']
    y_data_bar3 = ['부채비율']
    y_data_line3 = ['유보율']

    for y_data, color in zip(y_data_bar3, marker_colors) :
        fig.add_trace(go.Bar(name = y_data, x = balance_df.index, y = balance_df[y_data], 
                            text = balance_df[y_data], textposition = 'outside', marker_color= color), secondary_y = True) 
    
    for y_data, color in zip(y_data_line3, marker_colors): 
        fig.add_trace(go.Scatter(mode='lines+markers+text', 
                                    name = y_data, x =  balance_df.index, y= balance_df.loc[:,y_data],
                                    text= balance_df[y_data], textposition = 'top center', marker_color = color),
                                    secondary_y = False)
    fig.update_traces(texttemplate='%{text:.3s}') 
    fig.update_yaxes(range=[0, max(balance_df.loc[:,y_data_bar3[0]])*1.5], secondary_y = False)
    fig.update_yaxes(range=[0, max(balance_df.loc[:,y_data_line3[0]])* 1.2], ticksuffix="%", secondary_y = True)
    fig.update_yaxes(title_text="Liabilities Rate", showticklabels= True, showgrid = True, zeroline=True, zerolinecolor='LightPink', ticksuffix="%", secondary_y = True)
    fig.update_yaxes(title_text= "유보율", showticklabels= True, showgrid = False, zeroline=True, ticksuffix="%", secondary_y = False)
    fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template, xaxis_tickformat = '%Y.%m')
    fig.update_layout(template="myID")
    st.plotly_chart(fig)

def dividend_chart(input_ticker, company_name, income_df):
    #시가배당률, 
    st.subheader('DPS & Dividend Yield')
    x_data = income_df.index
    title = '('  + company_name + ') <b>DPS & Dividend Yield</b>'
    titles = dict(text= title, x=0.5, y = 0.85) 
    fig = make_subplots(specs=[[{'secondary_y': True}]]) 
    y_data_bar4 = ['DPS(원)']
    y_data_line4 = ['배당수익률']

    for y_data, color in zip(y_data_bar4, marker_colors) :
        fig.add_trace(go.Bar(name = y_data, x = income_df.index, y = income_df[y_data], 
                            text = income_df[y_data], textposition = 'inside', marker_color= color), secondary_y = False) 
    
    for y_data, color in zip(y_data_line4, marker_colors): 
        fig.add_trace(go.Scatter(mode='lines+markers+text', 
                                    name = y_data, x =  income_df.index, y= income_df.loc[:,y_data],
                                    text= income_df[y_data], textposition = 'top center', marker_color = color),
                                    secondary_y = True)
    fig.update_traces(texttemplate='%{text:.3s}') 
    fig.update_yaxes(range=[0, max(income_df.loc[:,y_data_bar4[0]])*1.5], secondary_y = False)
    fig.update_yaxes(range=[0, max(income_df.loc[:,y_data_line4[0]])* 1.2], ticksuffix="%", secondary_y = True)
    fig.update_yaxes(title_text="배당수익률", showticklabels= True, showgrid = True, zeroline=True, zerolinecolor='LightPink', ticksuffix="%", secondary_y = True)
    fig.update_yaxes(title_text= "DPS(원)", showticklabels= True, showgrid = False, zeroline=True, ticksuffix="원", secondary_y = False)
    fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template, xaxis_tickformat = '%Y.%m')
    fig.update_layout(template="myID")
    st.plotly_chart(fig)