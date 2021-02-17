import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import streamlit as st
from datetime import datetime

#챠트 기본 설정
# colors 
marker_colors = ['#34314c', '#47b8e0', '#ff7473', '#ffc952', '#3ac569']
# marker_colors = ['rgb(27,38,81)', 'rgb(205,32,40)', 'rgb(22,108,150)', 'rgb(255,69,0)', 'rgb(237,234,255)']
template = 'ggplot2' #"plotly", "plotly_white", "plotly_dark", "ggplot2", "seaborn", "simple_white", "none"

def price_chart(input_ticker, price_df):   
    title = '('  + input_ticker + ') Price'
    titles = dict(text= title, x=0.5, y = 0.9) 
    fig = make_subplots(specs=[[{'secondary_y': True}]]) 
    fig.add_trace(go.Candlestick(x=price_df.index,
                open=price_df['Open'],
                high=price_df['High'],
                low=price_df['Low'],
                close=price_df['Close'],
                increasing_line_color= 'red', decreasing_line_color= 'blue'), secondary_y = False)
    fig.add_trace(go.Bar(name = 'Volume', x = price_df.index, y = price_df['Volume'], marker_color= '#34314c'), secondary_y = True)
    # fig.update_traces(texttemplate='%{text:.3s}') 
    fig.update_yaxes(title_text='Volume',showticklabels= True, showgrid = False, zeroline=False, secondary_y = True)
    fig.update_yaxes(title_text='Close',showticklabels= True, showgrid = True, zeroline=True, tickprefix="$", secondary_y = False)
    fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template)
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


def earning_chart(input_ticker, earning_df, ea_df, price_df):
    
    #주가와 EPS
    title = '('  + input_ticker + ') EPS & Price'
    titles = dict(text= title, x=0.5, y = 0.9) 
    x_data = earning_df['reportedDate'] # EPS발표 날짜로 

    fig = make_subplots(specs=[[{'secondary_y': True}]]) 
    y_data_bar = ['reportedEPS','estimatedEPS', 'surprise', 'ttmEPS']
   
    for y_data, color in zip(y_data_bar, marker_colors) :
        fig.add_trace(go.Bar(name = y_data, x = x_data, y = earning_df[y_data], marker_color= color), secondary_y = False) 
    
    fig.add_trace(go.Scatter(mode='lines', 
                            name = 'Close', x =  price_df.index, y= price_df['Close'],
                            text= price_df['Close'], textposition = 'top center', marker_color = 'rgb(0,0,0)'),# marker_colorscale='RdBu'),
                            secondary_y = True)

    fig.update_traces(texttemplate='%{text:.3s}') 
    fig.update_yaxes(title_text='Close',showticklabels= True, showgrid = False, zeroline=True, tickprefix="$")
    fig.update_yaxes(title_text='EPS',showticklabels= True, showgrid = True, zeroline=True, tickprefix="$", secondary_y = False)
    fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template)#, xaxis_tickformat = 'd')#  legend_title_text='( 단위 : $)' 
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

    fig2 = go.Figure()
    title = '('  + input_ticker + ') reportedEPS Statistics'
    titles = dict(text= title, x=0.5, y = 0.9) 
    fig2.add_trace(go.Box(x=earning_df.loc[:,'reportedEPS'], name='reportedEPS', boxpoints='all', marker_color = 'indianred',
                    boxmean='sd', jitter=0.3, pointpos=-1.8 ))
    fig2.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template)
    # fig2.add_trace(go.Box(x=earning_df.loc[:,'EPS Change'], name='EPS Change'))
    st.plotly_chart(fig2)


def income_chart(input_ticker, income_df, ia_df):
    # Profit and Cost
    st.subheader('Profit, Cost, Growth')
    x_data = income_df.index
    title = '('  + input_ticker + ') <b>Profit & Cost</b>'
    titles = dict(text= title, x=0.5, y = 0.85) 
    fig = make_subplots(specs=[[{'secondary_y': True}]]) 
    y_data_bar = ['totalRevenue', 'costOfRevenue', 'totalOperatingExpense']
    y_data_line = ['grossProfit', 'ebit', 'operatingIncome', 'netIncome']

    for y_data, color in zip(y_data_bar, marker_colors) :
        fig.add_trace(go.Bar(name = y_data, x = x_data, y = income_df[y_data].astype(float), marker_color= color), secondary_y = False) 
    
    for y_data, color in zip(y_data_line, marker_colors): 
        fig.add_trace(go.Scatter(mode='lines+markers+text', 
                                    name = y_data, x =  x_data, y= income_df.loc[:,y_data].astype(float),
                                    text= income_df[y_data], textposition = 'top center', marker_color = color),
                                    secondary_y = True)
    fig.update_traces(texttemplate='%{text:.3s}') 
    fig.update_yaxes(title_text='Revenue', range=[0, max(income_df.loc[:,y_data_bar[0]].astype(float))*2], secondary_y = False)
    fig.update_yaxes(title_text='Income', range=[-max(income_df.loc[:,y_data_line[0]].astype(float)), max(income_df.loc[:,y_data_line[0]].astype(float))* 1.2], secondary_y = True)
    fig.update_yaxes(showticklabels= True, showgrid = False, zeroline=True, tickprefix="$")
    fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template)
    st.plotly_chart(fig)

def income_margin_chart(input_ticker, income_df):
    x_data = income_df.index
    title = '('  + input_ticker + ') Margin & Growth Rate' 
    titles = dict(text= title, x=0.5, y = 0.85) 
    fig = make_subplots(specs=[[{'secondary_y': True}]]) 
    y_data_line = ['GPM', 'OPM', 'NPM']
    y_data_bar = ['TR Change', 'OI Change', 'NI Change']

    for y_data, color in zip(y_data_line, marker_colors): 
        fig.add_trace(go.Scatter(mode='lines+markers+text', name = y_data, x = x_data, y=income_df[y_data],
                                    text = income_df[y_data], textposition = 'top center', marker_color = color), secondary_y = True)

    for y_data, color in zip(y_data_bar, marker_colors) :
        fig.add_trace(go.Bar(name = y_data, x = x_data, y = income_df[y_data], 
                            text = income_df[y_data], textposition = 'outside', marker_color= color), secondary_y = False)

    fig.update_traces(texttemplate='%{text:.3s}') 
    fig.update_yaxes(title_text='Growth Rate', range=[0, max(income_df.loc[:,y_data_bar[0]])*2], secondary_y = False)
    fig.update_yaxes(title_text='Margin Rate', range=[-max(income_df.loc[:,y_data_line[0]]), max(income_df.loc[:,y_data_line[0]])* 1.2], secondary_y = True)
    fig.update_yaxes(showticklabels= True, showgrid = False, zeroline=True, ticksuffix="%")
    fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template)
    st.plotly_chart(fig)