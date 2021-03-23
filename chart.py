import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import FinanceDataReader as fdr

import streamlit as st
from datetime import datetime

#챠트 기본 설정
# colors 
# marker_colors = ['#34314c', '#47b8e0', '#ff7473', '#ffc952', '#3ac569']
marker_colors = ['rgb(27,38,81)', 'rgb(205,32,40)', 'rgb(22,108,150)', 'rgb(255,69,0)', 'rgb(237,234,255)']
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
    y_data_bar = ['totalRevenue', 'costOfRevenue', 'operatingExpenses']
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

def balance_chart(input_ticker, balance_df):
    #부채비율, 유동비율, 당좌비율
    st.subheader('Asset, Liabilities, ShareholderEquity')
    x_data = balance_df.index
    title = '('  + input_ticker + ') <b>Asset & Liabilities</b>'
    titles = dict(text= title, x=0.5, y = 0.85) 
    fig = make_subplots(specs=[[{'secondary_y': True}]]) 
    #y_data_bar3 = ['totalAssets', 'totalLiabilities', 'totalShareholderEquity']
    y_data_bar3 = ['totalLiabilities', 'totalShareholderEquity']
    y_data_line3 = ['Debt/Equity', 'QuickRatio', '유동부채/자기자본']

    for y_data, color in zip(y_data_bar3, marker_colors) :
        fig.add_trace(go.Bar(name = y_data, x = x_data, y = balance_df[y_data], 
                            text = balance_df[y_data], textposition = 'outside', marker_color= color), secondary_y = False) 
    
    for y_data, color in zip(y_data_line3, marker_colors): 
        fig.add_trace(go.Scatter(mode='lines+markers+text', 
                                    name = y_data, x =  x_data, y= balance_df.loc[:,y_data],
                                    text= balance_df[y_data], textposition = 'top center', marker_color = color),
                                    secondary_y = True)
    fig.update_traces(texttemplate='%{text:.3s}') 
    fig.update_yaxes(range=[0, max(balance_df.loc[:,y_data_bar3[0]])*2], secondary_y = False)
    fig.update_yaxes(range=[-max(balance_df.loc[:,y_data_line3[0]]), max(balance_df.loc[:,y_data_line3[0]])* 1.2], secondary_y = True)
    fig.update_yaxes(title_text="Liabilities Rate", showticklabels= True, showgrid = True, zeroline=True, zerolinecolor='LightPink', ticksuffix="%", secondary_y = True)
    fig.update_yaxes(title_text= "Asset", showticklabels= True, showgrid = False, zeroline=True, tickprefix="$", secondary_y = False)
    fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template)
    fig.update_layout(barmode='stack')
    st.plotly_chart(fig)

    #무형자산총자금비율, 현금자산비율
    x_data = balance_df.index
    title = '('  + input_ticker + ') <b>IntangibleAssets & Cash And ShortTermInvestments</b>'
    titles = dict(text= title, x=0.5, y = 0.85) 
    fig = make_subplots(specs=[[{'secondary_y': True}]]) 
    y_data_bar4 = ['무형자산비율', '현금성자산비율']
    y_data_bar4_name = ['intangible/Assets', 'Cash/Assets']
    fig.add_trace(go.Bar(name = y_data_bar4_name[1], x = x_data, y = balance_df[y_data_bar4[1]], 
                         text = balance_df[y_data_bar4[1]], textposition = 'outside', 
                         marker_color= marker_colors[0]), secondary_y = False) 
    fig.add_trace(go.Scatter(mode='lines+markers+text', 
                                    name = y_data_bar4_name[0], x =  x_data, y= balance_df[y_data_bar4[0]],
                                    text= balance_df[y_data_bar4[0]], textposition = 'top center', marker_color = marker_colors[2]),
                                    secondary_y = True)
    fig.update_traces(texttemplate='%{text:.3s}') 
    fig.update_yaxes(title_text="Cash/Assets", showticklabels= True, showgrid = True, zeroline=True, ticksuffix="%", secondary_y = False)
    fig.update_yaxes(title_text="intangible/Assets", showticklabels= True, showgrid = False, zeroline=True, ticksuffix="%", secondary_y = True)
    fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template)
    st.plotly_chart(fig)

def cashflow_chart(input_ticker, cashflow_df, income_df):
    #영업활동현금흐름, 순이익, 투자활동현금흐름, 재무활동현금흐름
    st.subheader('Cash Flow')
    x_data = cashflow_df.index
    title = '('  + input_ticker + ') <b>Cash Flow Statement</b>'
    titles = dict(text= title, x=0.5, y = 0.85) 
    fig = make_subplots(specs=[[{'secondary_y': True}]]) 
    y_data_bar5 = ['operatingCashflow', 'FCF']

    for y_data, color in zip(y_data_bar5, marker_colors) :
        fig.add_trace(go.Bar(name = y_data, x = x_data, y = cashflow_df[y_data], 
                            text= cashflow_df[y_data], textposition = 'outside', marker_color= color), secondary_y = False) 
    fig.add_trace(go.Bar(name = 'NetIncome', x = x_data, y = income_df['netIncome'], 
                        text= income_df['netIncome'], textposition = 'outside', marker_color= '#ff7473'), secondary_y = False)
    fig.update_traces(texttemplate='%{text:.3s}') 
    fig.update_yaxes(showticklabels= True, showgrid = True, zeroline=True, tickprefix="$")
    fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template)
    st.plotly_chart(fig)

def kor_earning_chart(input_ticker, com_name, ttm_df, annual_df):
    
    #주가와 ttm EPS
    title = '('  + com_name + ') TTM EPS & Price'
    titles = dict(text= title, x=0.5, y = 0.9) 
    x_data = ttm_df.index # EPS발표 날짜로 

    fig = make_subplots(specs=[[{'secondary_y': True}]]) 
    y_data = ['EPS','Price']
   
    # for y_data, color in zip(y_data_bar, marker_colors) :
    #     fig.add_trace(go.Bar(name = y_data, x = x_data, y = earning_df[y_data], marker_color= color), secondary_y = False) 
    fig.add_trace(go.Bar(name = y_data[0], x = x_data, y = ttm_df[y_data[0]], marker_color= marker_colors[1]), secondary_y = False)
    
    fig.add_trace(go.Scatter(mode='lines', 
                            name = 'Close', x =  ttm_df.index, y= ttm_df['Price'],
                            text= ttm_df['Price'], textposition = 'top center', marker_color = 'rgb(0,0,0)'),# marker_colorscale='RdBu'),
                            secondary_y = True)

    fig.update_traces(texttemplate='%{text:.3s}') 
    fig.update_yaxes(title_text='Close',showticklabels= True, showgrid = False, zeroline=True)
    fig.update_yaxes(title_text='TTM EPS',showticklabels= True, showgrid = True, zeroline=True, secondary_y = False)
    fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template)#, xaxis_tickformat = 'd')#  legend_title_text='( 단위 : $)' 
    st.plotly_chart(fig)

    #주가와 annual EPS
    title = '('  + com_name + ') Annual EPS & Price'
    titles = dict(text= title, x=0.5, y = 0.9) 
    x_data = annual_df.index # EPS발표 날짜로 

    fig = make_subplots(specs=[[{'secondary_y': True}]]) 
    y_data = ['EPS','Price']
   
    # for y_data, color in zip(y_data_bar, marker_colors) :
    #     fig.add_trace(go.Bar(name = y_data, x = x_data, y = earning_df[y_data], marker_color= color), secondary_y = False) 
    fig.add_trace(go.Bar(name = y_data[0], x = x_data, y = annual_df[y_data[0]], marker_color= marker_colors[1]), secondary_y = False)
    
    fig.add_trace(go.Scatter(mode='lines', 
                            name = 'Close', x =  annual_df.index, y= annual_df['Price'],
                            text= annual_df['Price'], textposition = 'top center', marker_color = 'rgb(0,0,0)'),# marker_colorscale='RdBu'),
                            secondary_y = True)

    fig.update_traces(texttemplate='%{text:.3s}') 
    fig.update_yaxes(title_text='Close',showticklabels= True, showgrid = False, zeroline=True)
    fig.update_yaxes(title_text='Annual EPS',showticklabels= True, showgrid = True, zeroline=True, secondary_y = False)
    fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template)#, xaxis_tickformat = 'd')#  legend_title_text='( 단위 : $)' 
    st.plotly_chart(fig)

    fig2 = go.Figure()
    title = '('  + com_name + ') EPS Statistics'
    titles = dict(text= title, x=0.5, y = 0.9) 
    fig2.add_trace(go.Box(x=ttm_df.loc[:,'EPS'], name='EPS', boxpoints='all', marker_color = 'indianred',
                    boxmean='sd', jitter=0.3, pointpos=-1.8 ))
    fig2.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template)
    # fig2.add_trace(go.Box(x=earning_df.loc[:,'EPS Change'], name='EPS Change'))
    st.plotly_chart(fig2)

     #PER, PBR, ROE 추이
    x_data = ttm_df.index
    title = com_name + '('  + input_ticker + ') TTM PER PBR & ROE' 
    titles = dict(text= title, x=0.5, y = 0.85) 
    fig = make_subplots(specs=[[{'secondary_y': True}]]) 
    y_data_line2 = ['PER', 'PBR']
    y_data_bar2 = ['ROE']

    fig.add_trace(go.Scatter(mode='lines+markers+text', name = y_data_line2[0], x = x_data, y=ttm_df[y_data_line2[0]],
                            text = ttm_df[y_data_line2[0]], textposition = 'top center', marker_color = marker_colors[0]),
                            secondary_y = False)
    fig.add_trace(go.Scatter(mode='lines+markers+text', name = y_data_line2[1], x = x_data, y=ttm_df[y_data_line2[1]],
                            text = ttm_df[y_data_line2[1]], textposition = 'top center', marker_color = marker_colors[1]),
                            secondary_y = True)

    fig.add_trace(go.Bar(name = y_data_bar2[0], x = x_data, y = ttm_df[y_data_bar2[0]], 
                            text = ttm_df[y_data_bar2[0]], textposition = 'outside', marker_color= marker_colors[2]), secondary_y = False)

    fig.update_traces(texttemplate='%{text:.3s}') 
    fig.update_yaxes(title_text='ROE', secondary_y = False)
    fig.update_yaxes(title_text='PER', secondary_y = False)
    fig.update_yaxes(title_text='PBR', secondary_y = True)
    fig.update_yaxes(showticklabels= True, showgrid = False, zeroline=True, ticksuffix="%")
    fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template)
    st.plotly_chart(fig)

     # ROE와 마진율
    x_data = ttm_df.index
    title = com_name + '('  + input_ticker + ') Margin & ROE' 
    titles = dict(text= title, x=0.5, y = 0.85) 
    fig = make_subplots(specs=[[{'secondary_y': True}]]) 
    y_data_line2 = ['OPM', 'NPM']
    y_data_bar2 = ['ROE']

    for y_data, color in zip(y_data_line2, marker_colors): 
        fig.add_trace(go.Scatter(mode='lines+markers+text', name = y_data, x = x_data, y=ttm_df[y_data],
        text = ttm_df[y_data], textposition = 'top center', marker_color = color),
        secondary_y = True)

    for y_data, color in zip(y_data_bar2, marker_colors) :
        fig.add_trace(go.Bar(name = y_data, x = x_data, y = ttm_df[y_data], 
                            text = ttm_df[y_data], textposition = 'outside', marker_color= color), secondary_y = False)

    fig.update_traces(texttemplate='%{text:.3s}') 
    fig.update_yaxes(title_text='ROE', range=[0, max(ttm_df.loc[:,y_data_bar2[0]])*2], secondary_y = False)
    fig.update_yaxes(title_text='Margin Rate', range=[-max(ttm_df.loc[:,y_data_line2[0]]), max(ttm_df.loc[:,y_data_line2[0]])* 1.2], secondary_y = True)
    fig.update_yaxes(showticklabels= True, showgrid = False, zeroline=True, ticksuffix="%")
    fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template)
    st.plotly_chart(fig)

    #배당
    title = '('  + com_name + ') Annual DPS & DY'
    titles = dict(text= title, x=0.5, y = 0.9) 
    x_data = annual_df.index # EPS발표 날짜로 

    fig = make_subplots(specs=[[{'secondary_y': True}]]) 
    y_data = ['DPS','DY']
   
    # for y_data, color in zip(y_data_bar, marker_colors) :
    #     fig.add_trace(go.Bar(name = y_data, x = x_data, y = earning_df[y_data], marker_color= color), secondary_y = False) 
    fig.add_trace(go.Bar(name = y_data[0], x = x_data, y = annual_df[y_data[0]], marker_color= marker_colors[0]), secondary_y = False)
    
    fig.add_trace(go.Scatter(mode='lines', 
                            name = 'Dividend Yeild', x =  annual_df.index, y= annual_df[y_data[1]],
                            text=  annual_df[y_data[1]], textposition = 'top center', marker_color =  marker_colors[1]),# marker_colorscale='RdBu'),
                            secondary_y = True)

    fig.update_traces(texttemplate='%{text:.3s}') 
    fig.update_yaxes(title_text='Dividend Yeild',showticklabels= True, showgrid = False, zeroline=True)
    fig.update_yaxes(title_text='Annual DPS',showticklabels= True, showgrid = True, zeroline=True, secondary_y = False)
    fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), template=template)#, xaxis_tickformat = 'd')#  legend_title_text='( 단위 : $)' 
    st.plotly_chart(fig)

def candlestick_chart(code):
    now = datetime.now() +pd.DateOffset(days=-4000)
    start_date = '%s-%s-%s' % ( now.year, now.month, now.day)

    df = fdr.DataReader(code,start_date)

    fig = go.Figure(data=[go.Candlestick(x=df.index,
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'],
                increasing_line_color= 'red', decreasing_line_color= 'blue'
                )])
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
                    dict(count=5,
                        label="1w",
                        step="day",
                        stepmode="backward"),
                    dict(count=1,
                        label="1m",
                        step="month",
                        stepmode="backward"),
                    dict(count=3,
                        label="3m",
                        step="month",
                        stepmode="backward"),
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
