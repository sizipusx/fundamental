import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots
import FinanceDataReader as fdr
import datetime
import streamlit as st

#챠트 기본 설정
# colors 
marker_colors1 = ['#34314c', '#47b8e0', '#ff7473', '#ffc952', '#3ac569']
#marker_colors1 = ['rgb(27,38,81)', 'rgb(22,108,150)', 'rgb(205,32,40)', 'rgb(255,69,0)', 'rgb(237,234,255)']
marker_colors2 = ['rgb(22,108,150)', 'rgb(255,69,0)', 'rgb(237,234,255)', 'rgb(27,38,81)', 'rgb(205,32,40)'] # blue, red, purple, 군청색, 
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

utcnow= datetime.datetime.utcnow()
time_gap= datetime.timedelta(hours=9)
kor_time= utcnow+ time_gap

def ecos_monthly_chart(input_ticker, df1, df2):
    df3 = df1.pct_change(periods=12)*100
    df3 = df3.fillna(0)
    df3 = df3.round(decimals=2)
    item_list = df1.columns.values.tolist()
    item_list2 = df2.columns.values.tolist()
    col1, col2, col3, col4 = st.columns(4)
    col1.metric(label=item_list[0], value = df1.iloc[-1,0], delta=df1.iloc[-2,0])
    col2.metric(label=item_list2[0]+"YOY", value =df3.iloc[-1,0], delta=df2.iloc[-2,0])
    col3.metric(label=item_list[1], value =df1.iloc[-1,1], delta=df1.iloc[-2,1])
    col4.metric(label=item_list2[1]+"YOY", value =df3.iloc[-1,1], delta=df2.iloc[-2,1])
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
            fig.update_layout(hovermode="x unified")
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
            fig.update_layout(hovermode="x unified")
            fig.update_layout(template="myID")
            st.plotly_chart(fig)


def fred_monthly_chart(ticker, kor_exp, df):
    mom_df = df.pct_change()*100
    mom_df = mom_df.fillna(0)
    mom_df = mom_df.round(decimals=2)
    mom_df.loc[:,'color'] = np.where(mom_df.iloc[:,0]<0, '#FFB8B1', '#E2F0CB')
    yoy_df = df.pct_change(periods=12)*100
    yoy_df = yoy_df.fillna(0)
    yoy_df = yoy_df.round(decimals=2)
    yoy_df.loc[:,'color'] = np.where(yoy_df.iloc[:,0]<0, '#FFB8B1', '#E2F0CB')
    col1, col2, col3 = st.columns(3)
    col1.metric(label=df.columns[0], value = df.iloc[-1,0])
    col2.metric(label=mom_df.columns[0]+"_MOM", value =str(mom_df.iloc[-1,0])+"%")
    col3.metric(label=yoy_df.columns[0]+"_YOY", value =str(yoy_df.iloc[-1,0])+"%")
    with st.container():
        col1, col2, col3 = st.columns([30,2,30])
        with col1:
            # st.subheader(kor_exp)
            x_data = df.index
            title = kor_exp
            titles = dict(text= title, x=0.5, y = 0.85, xanchor='center', yanchor= 'top')
            fig = make_subplots(specs=[[{'secondary_y': True}]]) 
            y_data_bar = [mom_df.columns[0]]
            y_data_line= [df.columns[0]]
            y_data_color = [mom_df.columns[-1]]
            for y_data, color in zip(y_data_bar, y_data_color) :
                fig.add_trace(go.Bar(name = y_data, x = x_data, y = mom_df.loc[:,y_data]*100, 
                                            text= mom_df[y_data], textposition = 'inside', marker_color= mom_df.loc[:,color]), secondary_y = True) 
            
            for y_data, color in zip(y_data_line, marker_colors1): 
                fig.add_trace(go.Scatter(mode='lines', 
                                            name = y_data, x =  x_data, y= df.loc[:,y_data],
                                            marker_color = color),
                                            secondary_y = False)
            #fig.update_traces(texttemplate='%{text:.3s}') 
            fig.update_yaxes(title_text=ticker, secondary_y = False)
            fig.update_yaxes(title_text='MOM', secondary_y = True)
            fig.update_yaxes(showticklabels= True, showgrid = False, zeroline=True, ticksuffix="bp", secondary_y = True)
            if kor_exp == "개인소비지출":
                tick_f = '%Y.%m'
                fig.update_yaxes(showticklabels= True, showgrid = False, zeroline=True, ticksuffix="Billions of Dollars", secondary_y = False)
            else: #기대인플레이션율
                tick_f = '%Y.%m.%d'
                fig.update_yaxes(showticklabels= True, showgrid = False, zeroline=True, ticksuffix="%", secondary_y = False)
            fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template, xaxis_tickformat = tick_f)
            fig.update_layout(hovermode="x unified")
            fig.update_layout(template="myID")
            st.plotly_chart(fig)
        with col2:
                st.write("")
        with col3: 
            #st.subheader(kor_exp)
            x_data = df.index
            title = kor_exp
            titles = dict(text= title, x=0.5, y = 0.85, xanchor='center', yanchor= 'top')
            fig = make_subplots(specs=[[{'secondary_y': True}]]) 
            y_data_bar = [yoy_df.columns[0]]
            y_data_line= [df.columns[0]]
            y_data_color = [yoy_df.columns[-1]]
            for y_data, color in zip(y_data_bar, y_data_color) :
                fig.add_trace(go.Bar(name = y_data, x = x_data, y = yoy_df.loc[:,y_data]*100, 
                                            text= yoy_df[y_data], textposition = 'inside', marker_color= yoy_df.loc[:,color]), secondary_y = True) 
            
            for y_data, color in zip(y_data_line, marker_colors1): 
                fig.add_trace(go.Scatter(mode='lines', 
                                            name = y_data, x =  x_data, y= df.loc[:,y_data],
                                            marker_color = color),
                                            secondary_y = False)
            #fig.update_traces(texttemplate='%{text:.3s}') 
            fig.update_yaxes(title_text=ticker, range=[0, max(df.loc[:,y_data_bar[0]])*1.2], secondary_y = False)
            #fig.update_yaxes(title_text='Profit', range=[0, max(income_df.loc[:,y_data_bar[0]])*2], secondary_y = False)
            fig.update_yaxes(title_text='YOY', secondary_y = True)
            fig.update_yaxes(showticklabels= True, showgrid = False, zeroline=True, ticksuffix="bp", secondary_y = True)
            if kor_exp == "개인소비지출":
                tick_f = '%Y.%m'
                fig.update_yaxes(showticklabels= True, showgrid = False, zeroline=True, ticksuffix="Billions of Dollars", secondary_y = False)
            else:
                tick_f = '%Y.%m.%d'
                fig.update_yaxes(showticklabels= True, showgrid = False, zeroline=True, ticksuffix="%", secondary_y = False)
            fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template, xaxis_tickformat = tick_f)
            fig.update_layout(hovermode="x unified")
            fig.update_layout(template="myID")
            st.plotly_chart(fig)

def ecos_spread_chart(input_ticker, df1):
    item_list = df1.columns.values.tolist()
    col1, col2, col3, col4 = st.columns(4)
    col1.metric(label=item_list[0], value = df1.iloc[-1,0], delta=df1.iloc[-1,3])
    col2.metric(label=item_list[1], value =df1.iloc[-1,1], delta=df1.iloc[-1,3])
    col3.metric(label=item_list[2], value =df1.iloc[-1,2])
    col4.metric(label=item_list[3], value =df1.iloc[-1,3])
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
            fig.update_yaxes(title_text=input_ticker, range=[-max(df1.loc[:,y_data_line[1]]), max(df1.loc[:,y_data_line[1]])* 1.5], secondary_y = True)
            fig.update_yaxes(title_text=df1.columns[3], secondary_y = False)
            fig.update_yaxes(showticklabels= True, showgrid = False, zeroline=True,  zerolinecolor='pink', ticksuffix="%", secondary_y = True)
            fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template, xaxis_tickformat = '%Y.%m')
            fig.update_layout(hovermode="x unified")
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
            fig.update_yaxes(title_text=input_ticker, range=[-max(df1.loc[:,y_data_line[0]]), max(df1.loc[:,y_data_line[0]])* 1.5], showgrid = True, zeroline=True, zerolinecolor='pink', ticksuffix="%", secondary_y = False)
            fig.update_yaxes(title_text=df1.columns[3], showticklabels= True, showgrid = False, zeroline=True, ticksuffix="%", secondary_y = True)
            fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template, xaxis_tickformat = '%Y.%m')
            fig.update_layout(hovermode="x unified")
            fig.update_layout(template="myID")
            st.plotly_chart(fig)


def fred_spread_chart(df1, df2):
    df2 = df2.dropna()
    df1.loc[:,"기준금리차"] = df1.iloc[:,0] - df2.iloc[-1,0]
    df1.loc[:,'color'] = np.where(df1['변동']<0, '#FFB8B1', '#E2F0CB')
    df2.loc[:,'10Y2Ycolor'] = np.where(df2['금리차10Y2Y']<0, '#FFB8B1', '#E2F0CB')
    df2.loc[:,'10Y3Mcolor'] = np.where(df2['금리차10Y3M']<0, '#FFB8B1', '#E2F0CB')
    col1, col2, col3, col4 = st.columns(4)
    col1.metric(label=df2.columns[0], value = df2.iloc[-1,0])#기준 금리
    col2.metric(label=df1.index[2], value =df1.iloc[2,0], delta=round(df1.iloc[2,0]-df2.iloc[-1,0],2))  #3개월 금리
    col3.metric(label=df1.index[6], value =df1.iloc[6,0], delta=round(df1.iloc[6,0]-df2.iloc[-1,0],2)) #2년 금리
    col4.metric(label=df1.index[10], value =df1.iloc[10,0], delta=round(df1.iloc[10,0]-df2.iloc[-1,0],2)) # 10년 금리
    with st.container():
        col1, col2, col3 = st.columns([30,2,30])
        with col1:
            #st.subheader(input_ticker)
            x_data = df1.index
            titles = dict(text= "US Bond Yield Curve", x=0.5, y = 0.85, xanchor='center', yanchor= 'top') 
            fig = make_subplots(specs=[[{'secondary_y': True}]]) 
            y_data_bar = [df1.columns[4]]
            y_data_line = [df1.columns[0]]
            y_data_color = [df1.columns[-1]]

            for y_data, color in zip(y_data_bar, y_data_color) :
                fig.add_trace(go.Bar(name = y_data, x = x_data, y = df1.loc[:,y_data]*100, 
                                            text= round(df1[y_data]*100,0), textposition = 'inside', marker_color= df1.loc[:,color]), secondary_y = True) 
            
            for y_data, color in zip(y_data_line, marker_colors1): 
                fig.add_trace(go.Scatter(mode='lines+markers', 
                                            name = y_data, x =  x_data, y= df1.loc[:,y_data],
                                            text= df1[y_data], textposition = 'top center', marker_color = color),
                                            secondary_y = False)
            #fig.update_traces(texttemplate='%{text:.3s}')
            fig.update_yaxes(title_text='금리', secondary_y = False)
            fig.update_yaxes(title_text='변동폭', secondary_y = True)
            fig.update_yaxes(showticklabels= True, showgrid = False, zeroline=True,  zerolinecolor='pink', ticksuffix="bp", secondary_y = True)
            fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template, xaxis_tickformat = '%Y.%m.%d')
            fig.add_hline(y=df2.iloc[-1,0], line_width=2, line_dash='dot', line_color="red", annotation_text=f"Federal Funds Effective Rate: {df2.iloc[-1,0]}%", annotation_position="bottom right")
            fig.update_layout(hovermode="x unified")
            fig.update_layout(template="myID")
            st.plotly_chart(fig)
        with col2:
                st.write("")
        with col3: 
            x_data = df2.index
            titles = dict(text= "주요금리", x=0.5, y = 0.95, xanchor='center', yanchor= 'top')
            fig = make_subplots(specs=[[{'secondary_y': True}]]) 
            y_data_bar = [df2.columns[0]] #기준금리
            y_data_line = [df2.columns[1], df2.columns[2], df2.columns[3]] #각 금리
            for y_data, color in zip(y_data_bar, marker_colors2) :
                fig.add_trace(go.Bar(name = y_data, x = x_data, y = df2.loc[:,y_data], marker_color= color), secondary_y = False) 
                                            #text= df2[y_data], textposition = 'inside', marker_color= color), secondary_y = False) 
            
            for y_data, color in zip(y_data_line, marker_colors1): 
                fig.add_trace(go.Scatter(mode='lines', 
                                            name = y_data, x =  x_data, y= df2.loc[:,y_data], marker_color = color), secondary_y = True)
                                            #text= df2[y_data], textposition = 'top center', 
            fig.update_yaxes(title_text="금리", range=[-max(df2.loc[:,y_data_line[1]]*1.2), max(df2.loc[:,y_data_line[1]])* 2], showgrid = True, zeroline=True, zerolinecolor='pink', ticksuffix="%", secondary_y = False)
            fig.update_yaxes(title_text="기준금리", showticklabels= True, showgrid = False, zeroline=True, ticksuffix="%", secondary_y = True)
            fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template, xaxis_tickformat = '%Y.%m.%d')
            fig.update_layout(hovermode="x unified")
            fig.update_layout(template="myID")
            st.plotly_chart(fig)
    with st.container():
        col1, col2, col3 = st.columns([30,2,30])
        with col1:
            x_data = df2.index
            titles = dict(text= "장단기금리차(10Y2Y)", x=0.5, y = 0.95, xanchor='center', yanchor= 'top')
            fig = make_subplots(specs=[[{'secondary_y': True}]]) 
            y_data_bar = [df2.columns[4]]
            y_data_line = [df2.columns[1], df2.columns[2]]
            y_data_color = [df2.columns[6]]
            for y_data, color in zip(y_data_bar, y_data_color) :
                fig.add_trace(go.Bar(name = y_data, x = x_data, y = df2.loc[:,y_data], marker_color= df2.loc[:,color]), secondary_y = True)
                                            #text= df2[y_data], textposition = 'inside', marker_color= df2.loc[:,color]), secondary_y = True) 
            
            for y_data, color in zip(y_data_line, marker_colors1): 
                fig.add_trace(go.Scatter(mode='lines', 
                                            name = y_data, x =  x_data, y= df2.loc[:,y_data],
                                            text= df2[y_data], textposition = 'top center', marker_color = color),
                                            secondary_y = False)
            fig.update_yaxes(title_text="금리", range=[0, max(df2.loc[:,y_data_line[1]])* 2], showgrid = False, zeroline=True, zerolinecolor='pink', ticksuffix="%", secondary_y = False)
            fig.update_yaxes(title_text="금리차", showticklabels= True, showgrid = False, zeroline=True, ticksuffix="bp", secondary_y = True)
            fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template, xaxis_tickformat = '%Y.%m.%d')
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
            fig.update_layout(hovermode="x unified")
            fig.update_layout(template="myID")
            st.plotly_chart(fig)
        with col2:
            st.write("")
        with col3: 
            x_data = df2.index
            titles = dict(text= "장단기금리차(10Y3M)", x=0.5, y = 0.95, xanchor='center', yanchor= 'top')
            fig = make_subplots(specs=[[{'secondary_y': True}]]) 
            y_data_bar = [df2.columns[5]]
            y_data_line = [df2.columns[1], df2.columns[3]]
            y_data_color = [df2.columns[7]]
            for y_data, color in zip(y_data_bar, y_data_color) :
                fig.add_trace(go.Bar(name = y_data, x = x_data, y = df2.loc[:,y_data], marker_color= df2.loc[:,color]), secondary_y = True)
                                            #text= df2[y_data], textposition = 'inside', marker_color= df2.loc[:,color]), secondary_y = True) 
            
            for y_data, color in zip(y_data_line, marker_colors1): 
                fig.add_trace(go.Scatter(mode='lines', 
                                            name = y_data, x =  x_data, y= df2.loc[:,y_data],
                                            text= df2[y_data], textposition = 'top center', marker_color = color), secondary_y = False)
            fig.update_yaxes(title_text="금리", range=[0, max(df2.loc[:,y_data_line[1]])*2], showgrid = False, zeroline=True, zerolinecolor='pink', ticksuffix="%", secondary_y = False)
            fig.update_yaxes(title_text="금리차", showticklabels= True, showgrid = False, zeroline=True, ticksuffix="bp", secondary_y = True)
            fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template, xaxis_tickformat = '%Y.%m.%d')
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
            fig.update_layout(hovermode="x unified")
            fig.update_layout(template="myID")
            st.plotly_chart(fig)
        

def OECD_chart(stat_ticker, kor_exp, cli_df):
     with st.container():
        col1, col2, col3 = st.columns([30,2,30])
        with col1:
            titles = dict(text= kor_exp, x=0.5, y = 0.95, xanchor='center', yanchor= 'top')
            fig = px.line(cli_df[cli_df['SUBJECT']=="LOLITOAA"], x="TIME_PERIOD", y="value", color='LOCATION')
            fig.update_yaxes(title_text=stat_ticker, showgrid = True, zeroline=True, zerolinecolor='pink', ticksuffix="pt")
            fig.add_hline(y=100.0, line_width=2, line_dash='dot', line_color="red")
            fig.update_layout(title = titles, titlefont_size=15, hovermode="x unified")
            fig.update_layout(template="myID")
            st.plotly_chart(fig)
        with col2:
            st.write("")
        with col3:
            titles = dict(text= kor_exp+" Change", x=0.5, y = 0.95, xanchor='center', yanchor= 'top')
            fig = px.bar(cli_df[cli_df['SUBJECT']=="LOLITOTR_GYSA"], x='TIME_PERIOD', y='value',  color='LOCATION')
            fig.update_yaxes(title_text=stat_ticker+" change", showgrid = True, zeroline=True, zerolinecolor='pink', ticksuffix="%")
            fig.update_layout(title = titles, titlefont_size=15, hovermode="x unified")
            fig.update_layout(template="myID")
            st.plotly_chart(fig)
    # with st.container():
    #     col1, col2, col3 = st.columns([30,2,30])
    #     with col1:

    #     with col2:
    #         st.write("")
    #     with col3:



