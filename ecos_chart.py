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

def ecos_chart(input_ticker, df1, df2):
    df3 = df1.pct_change(periods=12)*100
    df3 = df3.fillna(0)
    df3 = df3.round(decimals=2)
    with st.container():
        col1, col2, col3 = st.columns([30,2,30])
        with col1:
            st.subheader(input_ticker)
            x_data = df1.index
            title = '( 예금취급기관 )<b>가계 대출</b>'
            titles = dict(text= title, x=0.5, y = 0.85) 
            fig = make_subplots(specs=[[{'secondary_y': True}]]) 
            y_data_bar = [df1.columns[0], df1.columns[1]]
            y_data_line= [df2.columns[0], df2.columns[1]]

            for y_data, color in zip(y_data_bar, marker_colors) :
                fig.add_trace(go.Bar(name = y_data, x = x_data, y = df2.loc[:,y_data], 
                                            text= df2[y_data], textposition = 'inside', marker_color= color), secondary_y = True) 
            
            for y_data, color in zip(y_data_line, marker_colors): 
                fig.add_trace(go.Scatter(mode='lines+markers+text', 
                                            name = y_data, x =  x_data, y= df1.loc[:,y_data],
                                            text= df1[y_data], textposition = 'top center', marker_color = color),
                                            secondary_y = False)
            #fig.update_traces(texttemplate='%{text:.3s}') 
            fig.update_yaxes(title_text='대출금액(조원)', range=[0, max(df1.loc[:,y_data_bar[0]])*2], secondary_y = False)
            #fig.update_yaxes(title_text='Profit', range=[0, max(income_df.loc[:,y_data_bar[0]])*2], secondary_y = False)
            fig.update_yaxes(title_text='전월대비증감', range=[-max(df2.loc[:,y_data_line[0]]), max(df1.loc[:,y_data_line[0]])* 1.2], secondary_y = True)
            fig.update_yaxes(showticklabels= True, showgrid = False, zeroline=True, ticksuffix="%", secondary_y = True)
            fig.update_yaxes(showticklabels= True, showgrid = False, zeroline=True, ticksuffix="조원", secondary_y = False)
            fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template, xaxis_tickformat = '%Y.%m')
            fig.update_layout(template="myID")
            st.plotly_chart(fig)
        with col2:
                st.write("")
        with col3: 
            st.subheader(input_ticker)
            x_data = df1.index
            title = '( 예금취급기관 )<b>가계 대출</b>'
            titles = dict(text= title, x=0.5, y = 0.85) 
            fig = make_subplots(specs=[[{'secondary_y': True}]]) 
            y_data_bar = [df1.columns[0], df1.columns[1]]
            y_data_line= [df2.columns[0], df2.columns[1]]

            for y_data, color in zip(y_data_bar, marker_colors) :
                fig.add_trace(go.Bar(name = y_data, x = x_data, y = df3.loc[:,y_data], 
                                            text= df3[y_data], textposition = 'inside', marker_color= color), secondary_y = True) 
            
            for y_data, color in zip(y_data_line, marker_colors): 
                fig.add_trace(go.Scatter(mode='lines+markers+text', 
                                            name = y_data, x =  x_data, y= df1.loc[:,y_data],
                                            text= df1[y_data], textposition = 'top center', marker_color = color),
                                            secondary_y = False)
            #fig.update_traces(texttemplate='%{text:.3s}') 
            fig.update_yaxes(title_text='대출금액(조원)', range=[0, max(df1.loc[:,y_data_bar[0]])*2], secondary_y = False)
            #fig.update_yaxes(title_text='Profit', range=[0, max(income_df.loc[:,y_data_bar[0]])*2], secondary_y = False)
            fig.update_yaxes(title_text='전년대비증감', range=[-max(df3.loc[:,y_data_line[0]]), max(df3.loc[:,y_data_line[0]])* 1.2], secondary_y = True)
            fig.update_yaxes(showticklabels= True, showgrid = False, zeroline=True, ticksuffix="%", secondary_y = True)
            fig.update_yaxes(showticklabels= True, showgrid = False, zeroline=True, ticksuffix="조원", secondary_y = False)
            fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template, xaxis_tickformat = '%Y.%m')
            fig.update_layout(template="myID")
            st.plotly_chart(fig)
