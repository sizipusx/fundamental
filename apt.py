import json
import sqlite3
from datetime import datetime

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import requests
from pandas.io.json import json_normalize
from plotly.subplots import make_subplots

import streamlit as st


def main():
    data_load_state = st.text('Loading data...')
    apt_df, apt_pct_df = load_data()
    index_df = load_index_data()
    data_load_state.text("Done! (using st.cache)")

    option = st.sidebar.text_input("시도입력")
    if option == "":
        option = st.sidebar.selectbox(
            '시도',
            apt_df.columns
        )
        
    if  st.checkbox('Show raw data'):
        st.subheader('소비자물가 보기')
        st.write(apt_df)

    
    '지역은: ', option
    st.title("KB매매지수와 소비자물가지수 비교")
    visualize_data(apt_df, apt_pct_df, index_df, option)


def query_ecos(stat_code, stat_item, start_date, end_date, cycle_type="QQ"):
    auth_key = "XNVPGRFHBBT26BU3ZRAC/" #발급 받은 Key 를 넣으면 더 많은 데이터 수집 가능
    req_type = "json/"
    lang = "kr/"
    start_no = "1/"
    end_no ="10000/"
    stat_code = stat_code + "/"
    #stat_code = stat_code.split('/')[0] + "/"
    cycle_type = cycle_type + "/"
    start_date = start_date + "/"
    end_date = end_date + "/"
    #item_no = stat_code.split('/')[1]
    item_no = stat_item

    url = "http://ecos.bok.or.kr/api/StatisticSearch/" +  \
        auth_key + req_type + lang + start_no + end_no + \
        stat_code + cycle_type + start_date + end_date + item_no

    r = requests.get(url)
    if '해당하는 데이터가 없습니다' in r.text:
        return None
    
    jo = json.loads(r.text)
    # print(jo)
    df = json_normalize(jo['StatisticSearch']['row'])
    df['TIME'] = df['TIME'] + '0101'
    df['TIME'] = df['TIME'].str.replace(r'(\d{4})(\d{2})(\d{2})(.*)', r'\1-\2-\3')
    return df

@st.cache
def load_data():
    con = sqlite3.connect("D:/OneDrive - 호매실고등학교/투자/powerbi/data/DB/KB.db")
    apt_df = pd.read_sql("SELECT * FROM 'KB월간매매지수'", con, index_col="날짜")
    apt_pct_df = pd.read_sql("SELECT * FROM 'KB월간매매지수증감(월)'", con, index_col="날짜")
    con.close()
    apt_df.index = pd.to_datetime(apt_df.index)
    apt_pct_df.index = pd.to_datetime(apt_pct_df.index)
    # apt_df = apt_df.reset_index()
    # apt_pct_df = apt_pct_df.reset_index()
    return apt_df, apt_pct_df

@st.cache
def load_index_data():
    #소비자물가 지수 받기
    now = datetime.now()
    today = '%s%s' % ( now.year, now.month)
    symbols = {'소비자물가':'021Y125/0','소비자물가(주택수도전기연료))':'021Y125/D'}
    tickers = symbols.values()
    start_date = "198601"
    end_date = today
    cycle_type = "MM"

    all_data = {}
    for ticker in tickers:
        stat_code = ticker.split('/')[0]
        stat_item = ticker.split('/')[1]
        all_data[ticker] = query_ecos(stat_code, stat_item, start_date, end_date, cycle_type)
    
    #컬럼명 종목명으로 변경
    sobi_df = pd.DataFrame({tic: data['DATA_VALUE'] for tic, data in all_data.items()})
    sobi_df.columns = symbols.keys()
    #날짜 설정
    tempdf = all_data.get('021Y125/0')
    sobi_df.set_index(keys=tempdf['TIME'], inplace=True)
    sobi_df.index = pd.to_datetime(sobi_df.index)
    return sobi_df


def visualize_data(apt_df, apt_pct_df, sobi_df, localname):
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    for i in range(0, 2):
        fig.add_trace(
            go.Scatter(x=sobi_df.index, y=sobi_df.iloc[:,i], mode='lines', \
                    #text = trade_df.iloc[:,i][i],
                    name=sobi_df.columns[i]),    
            secondary_y=True,
        )
    fig.add_trace(
        go.Scatter(x = apt_df.index, y = apt_df[localname], mode='lines', name = localname), secondary_y=True)
    fig.add_trace(
       go.Bar(x = apt_df.index, y = apt_pct_df[localname]*1000, name = '변동률'), secondary_y=False) 

    fig.update_layout(title_text="소비자(2015=100)/전국아파트매매가격 지수(2019=100)", title_font_size=20)
    fig.update_xaxes(showspikes=True, spikecolor="green", spikesnap="cursor", spikemode="across")
    fig.update_yaxes(showspikes=True, spikecolor="orange", spikethickness=2)
    fig.update_layout(spikedistance=1000, hoverdistance=100)
    fig.update_yaxes(title_text="<b>소비자/주택가격</b> 지수", secondary_y=True)
    fig.update_yaxes(title_text="<b>변동률</b>", secondary_y=False)
    fig.update_xaxes(ticks="inside", tickcolor='crimson', ticklen=10)
    fig.update_yaxes(ticks="inside", tickcolor='crimson', ticklen=10)
    fig.update_yaxes(zeroline=True, zerolinewidth=2, zerolinecolor='LightPink')
    #fig.update_yaxes(tickprefix="%")
    #fig.update_layout(yaxis_tickformat = '%')
    fig.update_layout(
        width=800,
        height=600,
        autosize=False,
        showlegend=True,
        legend_orientation="h",
        annotations=[
            go.layout.Annotation(
                x="1990-08-01",
                y=130,
                xref="x",
                yref="y",
                text= "<b>노태우정권</b>",
                font=dict(
                    family="sans serif",
                    size=15,
                    color="LightSeaGreen"
                ),
                showarrow=False,
                ax=0,
                ay=-40
            ),
             go.layout.Annotation(
                x="1995-08-01",
                y=130,
                xref="x",
                yref="y",
                text= "<b>김영삼정권</b>",
                font=dict(
                    family="sans serif",
                    size=15,
                    color="LightSeaGreen"
                ),
                showarrow=False,
                ax=0,
                ay=-40
            ),
           go.layout.Annotation(
                x="2000-08-01",
                y=130,
                xref="x",
                yref="y",
                text= "<b>김대중정권</b>",
                font=dict(
                    family="sans serif",
                    size=15,
                    color="LightSeaGreen"
                ),
                showarrow=False,
                ax=0,
                ay=-40
            ),
            go.layout.Annotation(
                x="2005-08-01",
                y=130,
                xref="x",
                yref="y",
                text= "<b>노무현정권</b>",
                font=dict(
                    family="sans serif",
                    size=15,
                    color="LightSeaGreen"
                ),
                showarrow=False,
                ax=0,
                ay=-40
            ),
            go.layout.Annotation(
                x="2010-08-01",
                y=130,
                xref="x",
                yref="y",
                text= "<b>이명박정권</b>",
                font=dict(
                    family="sans serif",
                    size=15,
                    color="LightSeaGreen"
                ),
                showarrow=False,
                ax=0,
                ay=-40
            ),
            go.layout.Annotation(
                x="2015-08-01",
                y=130,
                xref="x",
                yref="y",
                text= "<b>박근혜정권</b>",
                font=dict(
                    family="sans serif",
                    size=12,
                    color="LightSeaGreen"
                ),
                showarrow=False,
                ax=0,
                ay=-40
            ),
            go.layout.Annotation(
                x="2019-08-01",
                y=130,
                xref="x",
                yref="y",
                text= "<b>문재인정권</b>",
                font=dict(
                    family="sans serif",
                    size=12,
                    color="LightSeaGreen"
                ),
                showarrow=False,
                ax=0,
                ay=-40
            )
        ],
        xaxis=go.layout.XAxis(
            rangeselector=dict(
                buttons=list([
                    dict(count=1,
                        label="1m",
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
                    dict(count=3,
                        label="3y",
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
        ),
        shapes=[
            go.layout.Shape(
                type="rect",
                x0="1988-02-01",
                x1="1993-03-01",
                xref="x",
                y0=0,
                y1=1,
                yref="paper",
                fillcolor="LightSalmon",
                opacity=0.3,
                layer="below",
                line_width=0
            ),
            go.layout.Shape(
                type="rect",
                x0="1993-03-01",
                x1="1998-03-01",
                xref="x",
                y0=0,
                y1=1,
                yref="paper",
                fillcolor="LightSkyBlue",
                opacity=0.3,
                layer="below",
                line_width=0
            ),
            go.layout.Shape(
                type="rect",
                x0="1998-03-01",
                x1="2003-03-01",
                xref="x",
                y0=0,
                y1=1,
                yref="paper",
                opacity=0.3,
                layer="below",
                line_width=0,
                fillcolor="LightSalmon"
            ),
            go.layout.Shape(
                type="rect",
                x0="2003-03-01",
                x1="2008-03-01",
                xref="x",
                y0=0,
                y1=1,
                yref="paper",
                opacity=0.3,
                layer="below",
                line_width=0,
                fillcolor="LightSkyBlue"
            ),
            go.layout.Shape(
                type="rect",
                x0="2008-03-01",
                x1="2013-03-01",
                xref="x",
                y0=0,
                y1=1,
                yref="paper",
                opacity=0.3,
                layer="below",
                line_width=1,
                fillcolor="LightSalmon"
            ),
            go.layout.Shape(
                type="rect",
                x0="2013-03-01",
                x1="2017-05-01",
                xref="x",
                y0=0,
                y1=1,
                yref="paper",
                fillcolor="LightSalmon",
                opacity=0.3,
                layer="below",
                line_width=1
            ),
            go.layout.Shape(
                type="rect",
                x0="2017-05-01",
                x1="2020-04-01",
                xref="x",
                y0=0,
                y1=1,
                yref="paper",
                fillcolor="LightSkyBlue",
                opacity=0.3,
                layer="below",
                line_width=0
            )
        ]
    )
    # # Plot!
    st.plotly_chart(fig)
    

if __name__ == "__main__":
    main()
