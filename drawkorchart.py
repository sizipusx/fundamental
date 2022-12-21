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
            st.subheader('손익계산서')
            column_name_ch = income_df.columns[0]
            x_data = income_df.index
            title = '('  + company_name + ') <b>Annually Profit & Margin</b>'
            titles = dict(text= title, x=0.5, y = 0.85) 
            fig = make_subplots(specs=[[{'secondary_y': True}]]) 
            y_data_bar = [column_name_ch, '영업이익', '당기순이익']
            if dis_flag == True:
                y_data_line = ['영업이익률', '순이익률']
            else:
                y_data_line = ['영업이익률', '지배주주순이익률']

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
            st.subheader('Quarterly Profit, Margin ')
            x_data = income_df_q.index
            title = '('  + company_name + ') <b>Quarterly Profit & Margin</b>'
            titles = dict(text= title, x=0.5, y = 0.85) 
            fig = make_subplots(specs=[[{'secondary_y': True}]]) 
            y_data_bar = [column_name_ch, '영업이익', '당기순이익']
            if dis_flag == True:
                y_data_line = ['영업이익률', '순이익률']
            else:
                y_data_line = ['영업이익률', '지배주주순이익률']

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


def balance_chart(company_name, status_an, status_qu, ratio_an, ratio_qu):
    #부채비율, 유동비율, 당좌비율
    with st.container():
        col1, col2, col3 = st.columns([30,2,30])
        with col1:
            # Profit and Margin
            st.subheader('연간 재무상태표')
            column_name_ch = status_an.columns[0]
            x_data = status_an.index
            title = '('  + company_name + ') <b>Annually Asset & Liabilities</b>'
            titles = dict(text= title, x=0.5, y = 0.85) 
            fig = make_subplots(specs=[[{'secondary_y': True}]]) 
            y_data_bar = ['자본', '부채']
            y_data_line = ['부채비율계산에 참여한 계정 펼치기']

            for y_data, color in zip(y_data_bar, marker_colors) :
                fig.add_trace(go.Bar(name = y_data, x = x_data, y = status_an.loc[:,y_data], 
                                            text= status_an[y_data], textposition = 'inside', marker_color= color), secondary_y = False) 
            
            for y_data, color in zip(y_data_line, marker_colors): 
                fig.add_trace(go.Scatter(mode='lines+markers+text', 
                                            name = y_data, x =  x_data, y= ratio_an.loc[:,y_data],
                                            text= ratio_an[y_data], textposition = 'top center', marker_color = color),
                                            secondary_y = True)
            #fig.update_traces(texttemplate='%{text:.3s}') 
            fig.update_yaxes(title_text='Asset & Liabilities', range=[0, max(status_an.loc[:,y_data_bar[0]])*2], secondary_y = False)
            #fig.update_yaxes(title_text='Profit', range=[0, max(income_df.loc[:,y_data_bar[0]])*2], secondary_y = False)
            #fig.update_yaxes(title_text='부채비율', range=[-max(ratio_an.loc[:,y_data_line[0]]), max(ratio_an.loc[:,y_data_line[0]])* 1.2], secondary_y = True)
            fig.update_yaxes(showticklabels= True, showgrid = False, zeroline=True, ticksuffix="억원", secondary_y = False)
            fig.update_yaxes(showticklabels= True, showgrid = False, zeroline=True, ticksuffix="%", secondary_y = True)
            fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template)#, xaxis_tickformat = '%Y.%m')
            fig.update_layout(template="myID")
            st.plotly_chart(fig)
        with col2:
                st.write("")
        with col3: 
            # Profit and Margin
            st.subheader('분기 재무 상태표')
            x_data = status_qu.index
            title = '('  + company_name + ') <b>Quarterly Asset & Liabilities</b>'
            titles = dict(text= title, x=0.5, y = 0.85) 
            fig = make_subplots(specs=[[{'secondary_y': True}]]) 
            y_data_bar = ['자본', '부채']
            y_data_line = ['자산']

            for y_data, color in zip(y_data_bar, marker_colors) :
                fig.add_trace(go.Bar(name = y_data, x = status_qu.index, y = status_qu.loc[:,y_data], 
                                    text= status_qu[y_data], textposition = 'inside', marker_color= color), secondary_y = False) 
            
            for y_data, color in zip(y_data_line, marker_colors): 
                fig.add_trace(go.Scatter(mode='lines+markers+text', 
                                            name = y_data, x =  status_qu.index, y= status_qu.loc[:,y_data],
                                            text= status_qu[y_data], textposition = 'top center', marker_color = color),
                                            secondary_y = True)
            #fig.update_traces(texttemplate='%{text:.3s}') 
            fig.update_yaxes(title_text='Asset & Liabilities', range=[0, max(status_qu.loc[:,y_data_bar[0]])*2], secondary_y = False)
            fig.update_yaxes(title_text='자산', range=[-max(status_qu.loc[:,y_data_line[0]]), max(status_qu.loc[:,y_data_line[0]])* 1.2], secondary_y = True)
            fig.update_yaxes(showticklabels= True, showgrid = False, zeroline=True, ticksuffix="억원", secondary_y = False)
            fig.update_yaxes(showticklabels= True, showgrid = False, zeroline=True, ticksuffix="%", secondary_y = True)
            fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template, xaxis_tickformat = '%Y.%m')
            fig.update_layout(template="myID")
            st.plotly_chart(fig)

def dividend_chart(company_name, income_df):
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

def pbr_chart(company_name, income_df, income_df_q):
    with st.container():
        col1, col2, col3 = st.columns([30,2,30])
        with col1:
            # Profit and Margin
            st.subheader('Annual PBR-ROE')
            column_name_ch = income_df.columns[0]
            x_data = income_df.index
            title = '('  + company_name + ') <b>Annually PBR & ROE</b>'
            titles = dict(text= title, x=0.5, y = 0.85) 
            fig = make_subplots(specs=[[{'secondary_y': True}]]) 
            y_data_line = ['PBR']
            y_data_bar = ['ROE']
            for y_data, color in zip(y_data_bar, marker_colors) :
                fig.add_trace(go.Bar(name = y_data, x = x_data, y = income_df.loc[:,y_data], 
                                            text= income_df[y_data], textposition = 'inside', marker_color= color), secondary_y = False) 
            
            for y_data, color in zip(y_data_line, marker_colors): 
                fig.add_trace(go.Scatter(mode='lines+markers+text', 
                                            name = y_data, x =  x_data, y= income_df.loc[:,y_data],
                                            text= income_df[y_data], textposition = 'top center', marker_color = color),
                                            secondary_y = True)
            #fig.update_traces(texttemplate='%{text:.3s}') 
            fig.update_yaxes(title_text='ROE', range=[0, max(income_df.loc[:,y_data_bar[0]])*2], secondary_y = False)
            #fig.update_yaxes(title_text='Profit', range=[0, max(income_df.loc[:,y_data_bar[0]])*2], secondary_y = False)
            fig.update_yaxes(title_text='PBR', range=[-max(income_df.loc[:,y_data_line[0]]), max(income_df.loc[:,y_data_line[0]])* 1.2], secondary_y = True)
            fig.update_yaxes(showticklabels= True, showgrid = False, zeroline=True, ticksuffix="%", secondary_y = False)
            fig.update_yaxes(showticklabels= True, showgrid = False, zeroline=True, ticksuffix="배", secondary_y = True)
            fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template)#, xaxis_tickformat = '%Y.%m')
            fig.update_layout(template="myID")
            st.plotly_chart(fig)
        with col2:
                st.write("")
        with col3: 
            # Profit and Margin
            st.subheader('Quarter PBR-ROE')
            x_data = income_df_q.index
            title = '('  + company_name + ') <b>Quarterly Profit & Margin</b>'
            titles = dict(text= title, x=0.5, y = 0.85) 
            fig = make_subplots(specs=[[{'secondary_y': True}]]) 
            y_data_line = ['PBR']
            y_data_bar = ['ROE']
            for y_data, color in zip(y_data_bar, marker_colors) :
                fig.add_trace(go.Bar(name = y_data, x = x_data, y = income_df_q.loc[:,y_data], 
                                    text= income_df_q[y_data], textposition = 'inside', marker_color= color), secondary_y = False) 
            
            for y_data, color in zip(y_data_line, marker_colors): 
                fig.add_trace(go.Scatter(mode='lines+markers+text', 
                                            name = y_data, x =  income_df_q.index, y= income_df_q.loc[:,y_data],
                                            text= income_df_q[y_data], textposition = 'top center', marker_color = color),
                                            secondary_y = True)
            #fig.update_traces(texttemplate='%{text:.3s}') 
            fig.update_yaxes(title_text='ROE', range=[0, max(income_df_q.loc[:,y_data_bar[0]])*2], secondary_y = False)
            fig.update_yaxes(title_text='PBR', range=[-max(income_df_q.loc[:,y_data_line[0]]), max(income_df_q.loc[:,y_data_line[0]])* 1.2], secondary_y = True)
            fig.update_yaxes(showticklabels= True, showgrid = False, zeroline=True, ticksuffix="%", secondary_y = False)
            fig.update_yaxes(showticklabels= True, showgrid = False, zeroline=True, ticksuffix="배", secondary_y = True)
            fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template, xaxis_tickformat = '%Y.%m')
            fig.update_layout(template="myID")
            st.plotly_chart(fig)

def cash_flow(company_name, cf_an, cf_qu, in_df):
    with st.container():
        col1, col2, col3 = st.columns([30,2,30])
        with col1:
            # Profit and Margin
            st.subheader('Annual Cashflow')
            x_data = cf_an.index
            title = '('  + company_name + ') <b>Annually Cashflow</b>'
            titles = dict(text= title, x=0.5, y = 0.85) 
            fig = make_subplots(specs=[[{'secondary_y': True}]]) 
            y_data_line = ['FCFF']
            y_data_bar = ['영업활동으로인한현금흐름', '투자활동으로인한현금흐름', '재무활동으로인한현금흐름', '현금및현금성자산의증가']
            for y_data, color in zip(y_data_bar, marker_colors) :
                fig.add_trace(go.Bar(name = y_data, x = x_data, y = cf_an.loc[:,y_data], 
                                            text= cf_an[y_data], textposition = 'inside', marker_color= color), secondary_y = False) 
            
            for y_data, color in zip(y_data_line, marker_colors): 
                fig.add_trace(go.Scatter(mode='lines+markers+text', 
                                            name = y_data, x =  x_data, y= in_df.loc[:,y_data],
                                            text= in_df[y_data], textposition = 'top center', marker_color = color),
                                            secondary_y = True)
            #fig.update_traces(texttemplate='%{text:.3s}') 
            fig.update_yaxes(title_text='현금흐름', range=[0, max(in_df.loc[:,y_data_bar[0]])*2], secondary_y = False)
            #fig.update_yaxes(title_text='Profit', range=[0, max(income_df.loc[:,y_data_bar[0]])*2], secondary_y = False)
            fig.update_yaxes(title_text='FCFF', range=[-max(in_df.loc[:,y_data_line[0]]), max(in_df.loc[:,y_data_line[0]])* 1.2], secondary_y = True)
            fig.update_yaxes(showticklabels= True, showgrid = False, zeroline=True, ticksuffix="억원", secondary_y = False)
            fig.update_yaxes(showticklabels= True, showgrid = False, zeroline=True, ticksuffix="억원", secondary_y = True)
            fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template)#, xaxis_tickformat = '%Y.%m')
            fig.update_layout(template="myID")
            st.plotly_chart(fig)
        with col2:
                st.write("")
        with col3: 
            # Profit and Margin
            st.subheader('Quarter Cashflow')
            x_data = cf_qu.index
            title = '('  + company_name + ') <b>Quarterly Cashflow</b>'
            titles = dict(text= title, x=0.5, y = 0.85) 
            fig = make_subplots(specs=[[{'secondary_y': True}]]) 
            y_data_line = ['현금및현금성자산의증가']
            y_data_bar = ['영업활동으로인한현금흐름', '투자활동으로인한현금흐름', '재무활동으로인한현금흐름', '현금및현금성자산의증가']
            for y_data, color in zip(y_data_bar, marker_colors) :
                fig.add_trace(go.Bar(name = y_data, x = x_data, y = cf_qu.loc[:,y_data], 
                                    text= cf_qu[y_data], textposition = 'inside', marker_color= color), secondary_y = False) 
            
            for y_data, color in zip(y_data_line, marker_colors): 
                fig.add_trace(go.Scatter(mode='lines+markers+text', 
                                            name = y_data, x =  cf_qu.index, y= cf_qu.loc[:,y_data],
                                            text= cf_qu[y_data], textposition = 'top center', marker_color = color),
                                            secondary_y = True)
            #fig.update_traces(texttemplate='%{text:.3s}') 
            fig.update_yaxes(title_text='현금흐름', range=[0, max(cf_qu.loc[:,y_data_bar[0]])*2], secondary_y = False)
            fig.update_yaxes(title_text='현금및현금성자산의증가', range=[-max(cf_qu.loc[:,y_data_line[0]]), max(cf_qu.loc[:,y_data_line[0]])* 1.2], secondary_y = True)
            fig.update_yaxes(showticklabels= True, showgrid = False, zeroline=True, ticksuffix="억원", secondary_y = False)
            fig.update_yaxes(showticklabels= True, showgrid = False, zeroline=True, ticksuffix="억원", secondary_y = True)
            fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template, xaxis_tickformat = '%Y.%m')
            fig.update_layout(template="myID")
            st.plotly_chart(fig)