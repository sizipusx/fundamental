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
marker_colors1 = ['rgb(27,38,81)', 'rgb(22,108,150)', 'rgb(205,32,40)', 'rgb(255,69,0)', 'rgb(237,234,255)']
marker_colors2 = ['rgb(22,108,150)', 'rgb(255,69,0)', 'rgb(237,234,255)', 'rgb(27,38,81)', 'rgb(205,32,40)']
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

def ecos_monthly_chart(input_ticker, df1, df2):
    df3 = df1.pct_change(periods=12)*100
    df3 = df3.fillna(0)
    df3 = df3.round(decimals=2)
    item_list = df1.columns.values.tolist()
    with st.container():
        col1, col2, col3 = st.columns([30,2,30])
        with col1:
            #st.subheader(input_ticker)
            x_data = df1.index
            titles = dict(text= input_ticker, x=0.5, y = 0.85, xanchor='center', yanchor= 'top') 
            fig = make_subplots(specs=[[{'secondary_y': True}]]) 
            y_data_bar = []
            y_data_line = []
            for item in item_list:
                y_data_bar.append(item)
                y_data_line.append(item)

            for y_data, color in zip(y_data_bar, marker_colors2) :
                fig.add_trace(go.Bar(name = y_data, x = x_data, y = df2.loc[:,y_data], 
                                            text= df2[y_data], textposition = 'inside', marker_color= color), secondary_y = True) 
            
            for y_data, color in zip(y_data_line, marker_colors1): 
                fig.add_trace(go.Scatter(mode='lines+markers+text', 
                                            name = y_data, x =  x_data, y= df1.loc[:,y_data],
                                            text= df1[y_data], textposition = 'top center', marker_color = color),
                                            secondary_y = False)
            #fig.update_traces(texttemplate='%{text:.3s}')
            if input_ticker == '가계신용': 
                fig.update_yaxes(title_text='대출금액(조원)', range=[0, max(df1.loc[:,y_data_bar[0]])*1.2], zeroline=True, ticksuffix="조원", secondary_y = False)
            else:
                fig.update_yaxes(title_text=input_ticker, range=[0, max(df1.loc[:,y_data_bar[0]])*1.2], secondary_y = False)
            #fig.update_yaxes(title_text='Profit', range=[0, max(income_df.loc[:,y_data_bar[0]])*2], secondary_y = False)
            fig.update_yaxes(title_text='전월대비증감', range=[-max(df2.loc[:,y_data_line[0]]), max(df2.loc[:,y_data_line[0]])* 1.2], secondary_y = True)
            fig.update_yaxes(showticklabels= True, showgrid = False, zeroline=True, ticksuffix="%", secondary_y = True)
            fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template, xaxis_tickformat = '%Y.%m')
            fig.update_layout(template="myID")
            st.plotly_chart(fig)
        with col2:
                st.write("")
        with col3: 
            x_data = df1.index
            titles = dict(text= input_ticker, x=0.5, y = 0.85, xanchor='center', yanchor= 'top')
            fig = make_subplots(specs=[[{'secondary_y': True}]]) 
            y_data_bar = []
            y_data_line = []
            for item in item_list:
                y_data_bar.append(item)
                y_data_line.append(item)

            for y_data, color in zip(y_data_bar, marker_colors2) :
                fig.add_trace(go.Bar(name = y_data, x = x_data, y = df3.loc[:,y_data], 
                                            text= df3[y_data], textposition = 'inside', marker_color= color), secondary_y = True) 
            
            for y_data, color in zip(y_data_line, marker_colors1): 
                fig.add_trace(go.Scatter(mode='lines+markers+text', 
                                            name = y_data, x =  x_data, y= df1.loc[:,y_data],
                                            text= df1[y_data], textposition = 'top center', marker_color = color),
                                            secondary_y = False)
            #fig.update_traces(texttemplate='%{text:.3s}') 
            if input_ticker == '가계신용': 
                fig.update_yaxes(title_text='대출금액(조원)', range=[0, max(df1.loc[:,y_data_bar[0]])*1.2], zeroline=True, ticksuffix="조원", secondary_y = False)
            else:
                fig.update_yaxes(title_text=input_ticker, range=[0, max(df1.loc[:,y_data_bar[0]])*1.2], secondary_y = False)
            #fig.update_yaxes(title_text='Profit', range=[0, max(income_df.loc[:,y_data_bar[0]])*2], secondary_y = False)
            fig.update_yaxes(title_text='전년대비증감', range=[-max(df3.loc[:,y_data_line[0]]), max(df3.loc[:,y_data_line[0]])* 1.2], secondary_y = True)
            fig.update_yaxes(showticklabels= True, showgrid = False, zeroline=True, ticksuffix="%", secondary_y = True)
            # fig.update_yaxes(showticklabels= True, showgrid = False, zeroline=True, ticksuffix="조원", secondary_y = False)
            fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template, xaxis_tickformat = '%Y.%m')
            fig.update_layout(template="myID")
            st.plotly_chart(fig)


def fred_monthly_chart(ticker, kor_exp, df):
    mom_df = df.pct_change()*100
    mom_df = mom_df.fillna(0)
    mom_df = mom_df.round(decimals=2)
    yoy_df = df.pct_change(periods=12)*100
    yoy_df = yoy_df.fillna(0)
    yoy_df = yoy_df.round(decimals=2)
    with st.container():
        col1, col2, col3 = st.columns([30,2,30])
        with col1:
            st.subheader(kor_exp)
            x_data = df.index
            title = kor_exp
            titles = dict(text= title, x=0.5, y = 0.85, xanchor='center', yanchor= 'top')
            fig = make_subplots(specs=[[{'secondary_y': True}]]) 
            y_data_bar = [mom_df.columns[0]]
            y_data_line= [df.columns[0]]

            for y_data, color in zip(y_data_bar, marker_colors2) :
                fig.add_trace(go.Bar(name = y_data, x = x_data, y = mom_df.loc[:,y_data], 
                                            text= mom_df[y_data], textposition = 'inside', marker_color= color), secondary_y = True) 
            
            for y_data, color in zip(y_data_line, marker_colors1): 
                fig.add_trace(go.Scatter(mode='lines+markers', 
                                            name = y_data, x =  x_data, y= df.loc[:,y_data],
                                            marker_color = color),
                                            secondary_y = False)
            #fig.update_traces(texttemplate='%{text:.3s}') 
            fig.update_yaxes(title_text=ticker, range=[0, max(df.loc[:,y_data_bar[0]])*1.2], secondary_y = False)
            #fig.update_yaxes(title_text='Profit', range=[0, max(income_df.loc[:,y_data_bar[0]])*2], secondary_y = False)
            fig.update_yaxes(title_text='MOM', range=[-max(mom_df.loc[:,y_data_line[0]]), max(mom_df.loc[:,y_data_line[0]])* 1.2], secondary_y = True)
            fig.update_yaxes(showticklabels= True, showgrid = False, zeroline=True, ticksuffix="%", secondary_y = True)
            fig.update_yaxes(showticklabels= True, showgrid = False, zeroline=True, ticksuffix="Billions of Dollars", secondary_y = False)
            fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template, xaxis_tickformat = '%Y.%m')
            fig.update_layout(template="myID")
            st.plotly_chart(fig)
        with col2:
                st.write("")
        with col3: 
            st.subheader(kor_exp)
            x_data = df.index
            title = kor_exp
            titles = dict(text= title, x=0.5, y = 0.85, xanchor='center', yanchor= 'top')
            fig = make_subplots(specs=[[{'secondary_y': True}]]) 
            y_data_bar = [yoy_df.columns[0]]
            y_data_line= [df.columns[0]]

            for y_data, color in zip(y_data_bar, marker_colors2) :
                fig.add_trace(go.Bar(name = y_data, x = x_data, y = yoy_df.loc[:,y_data], 
                                            text= yoy_df[y_data], textposition = 'inside', marker_color= color), secondary_y = True) 
            
            for y_data, color in zip(y_data_line, marker_colors1): 
                fig.add_trace(go.Scatter(mode='lines+markers', 
                                            name = y_data, x =  x_data, y= df.loc[:,y_data],
                                            marker_color = color),
                                            secondary_y = False)
            #fig.update_traces(texttemplate='%{text:.3s}') 
            fig.update_yaxes(title_text=ticker, range=[0, max(df.loc[:,y_data_bar[0]])*1.2], secondary_y = False)
            #fig.update_yaxes(title_text='Profit', range=[0, max(income_df.loc[:,y_data_bar[0]])*2], secondary_y = False)
            fig.update_yaxes(title_text='YOY', range=[-max(yoy_df.loc[:,y_data_line[0]]), max(yoy_df.loc[:,y_data_line[0]])* 1.2], secondary_y = True)
            fig.update_yaxes(showticklabels= True, showgrid = False, zeroline=True, ticksuffix="%", secondary_y = True)
            fig.update_yaxes(showticklabels= True, showgrid = False, zeroline=True, ticksuffix="Billions of Dollars", secondary_y = False)
            fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template, xaxis_tickformat = '%Y.%m')
            fig.update_layout(template="myID")
            st.plotly_chart(fig)

def ecos_spread_chart(input_ticker, df1):
    item_list = df1.columns.values.tolist()
    with st.container():
        col1, col2, col3 = st.columns([30,2,30])
        with col1:
            #st.subheader(input_ticker)
            x_data = df1.index
            titles = dict(text= input_ticker, x=0.5, y = 0.85, xanchor='center', yanchor= 'top') 
            fig = make_subplots(specs=[[{'secondary_y': True}]]) 
            y_data_bar = [df1.columns[3]]
            y_data_line = [df1.columns[0], df1.columns[1]]
            y_data_color = [df1.columns[4]]

            for y_data, color in zip(y_data_bar, y_data_color) :
                fig.add_trace(go.Bar(name = y_data, x = x_data, y = df1.loc[:,y_data], 
                                            text= df1[y_data], textposition = 'inside', marker_color= df1.loc[:,color]), secondary_y = False) 
            
            for y_data, color in zip(y_data_line, marker_colors1): 
                fig.add_trace(go.Scatter(mode='lines+markers', 
                                            name = y_data, x =  x_data, y= df1.loc[:,y_data],
                                            text= df1[y_data], textposition = 'top center', marker_color = color),
                                            secondary_y = True)
            #fig.update_traces(texttemplate='%{text:.3s}')
            fig.update_yaxes(title_text=input_ticker, range=[-max(df1.loc[:,y_data_line[1]]), max(df1.loc[:,y_data_line[1]])* 1.2], secondary_y = True)
            fig.update_yaxes(title_text=df1.columns[3], secondary_y = False)
            fig.update_yaxes(showticklabels= True, showgrid = False, zeroline=True,  zerolinecolor='pink', ticksuffix="%", secondary_y = True)
            fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template, xaxis_tickformat = '%Y.%m')
            fig.update_layout(template="myID")
            st.plotly_chart(fig)
        with col2:
                st.write("")
        with col3: 
            x_data = df1.index
            titles = dict(text= input_ticker, x=0.5, y = 0.85, xanchor='center', yanchor= 'top')
            fig = make_subplots(specs=[[{'secondary_y': True}]]) 
            y_data_bar = [df1.columns[3]]
            y_data_line = [df1.columns[0], df1.columns[1], df1.columns[2]]
            y_data_color = [df1.columns[4]]
            for y_data, color in zip(y_data_bar, y_data_color) :
                fig.add_trace(go.Bar(name = y_data, x = x_data, y = df1.loc[:,y_data], 
                                            text= df1[y_data], textposition = 'inside', marker_color= df1.loc[:,color]), secondary_y = True) 
            
            for y_data, color in zip(y_data_line, marker_colors1): 
                fig.add_trace(go.Scatter(mode='lines+markers', 
                                            name = y_data, x =  x_data, y= df1.loc[:,y_data],
                                            text= df1[y_data], textposition = 'top center', marker_color = color),
                                            secondary_y = False)
            fig.update_yaxes(title_text=df1.columns[2], showgrid = True, zeroline=True, zerolinecolor='pink', ticksuffix="%", secondary_y = False)
            fig.update_yaxes(title_text=df1.columns[3], showticklabels= True, showgrid = False, zeroline=True, ticksuffix="%", secondary_y = True)
            fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template, xaxis_tickformat = '%Y.%m')
            fig.update_layout(template="myID")
            st.plotly_chart(fig)

