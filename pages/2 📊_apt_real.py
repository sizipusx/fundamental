import datetime
import numpy as np
import pandas as pd
import sqlite3
from urllib.request import urlopen
import json
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
import drawAPT_weekly 
import drawAPT_update
import seaborn as sns
import gspread
from oauth2client.service_account import ServiceAccountCredentials

cmap = cmap=sns.diverging_palette(250, 5, as_cmap=True)

#############html 영역####################
html_header="""
<head>
<title>Korea local house analysis</title>
<meta charset="utf-8">
<meta name="keywords" content="house data, dashboard, analysis, EVA">
<meta name="description" content="house data dashboard">
<meta name="author" content="indiesoul">
<meta name="viewport" content="width=device-width, initial-scale=1">
</head>
<h1 style="font-size:200%; color:#008080; font-family:Georgia">  🈷️ 월간 아파트 실거래가지수 분석 <br>
 <hr style= "  display: block;
  margin-top: 0.5em;
  margin-bottom: 0.5em;
  margin-left: auto;
  margin-right: auto;
  border-style: inset;
  border-width: 1.5px;"></h1>
"""

st.set_page_config(page_title="월간 아파트 실거래가격 지수", page_icon="files/logo2.png", layout="wide")
st.markdown('<style>body{background-color: #fbfff0}</style>',unsafe_allow_html=True)
st.markdown(html_header, unsafe_allow_html=True)
st.markdown(""" <style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style> """, unsafe_allow_html=True)

pd.set_option('display.float_format', '{:.2f}'.format)
#오늘날짜까지
utcnow= datetime.datetime.utcnow()
time_gap= datetime.timedelta(hours=9)
kor_time= utcnow+ time_gap

db_path = "files/one_monthly.db"

st.cache_resource(ttl=datetime.timedelta(days=1))
def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by the db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)#, check_same_thread=False)
    except Exception as e:
       print(e)

    return conn

@st.cache_data(ttl=datetime.timedelta(days=1))
def load_index_data():

    r_conn = create_connection(db_path)
    index_list = []
    query_list = ["select * from rmae", "select * from rjeon"]#, "SELECT * FROM jratio"]
    for query in query_list:
        df = pd.read_sql(query, r_conn, index_col='date', parse_dates={'date', "%Y-%m"})
        # query = conn.execute(query)
        # cols = [column[0] for column in query.description]
        # df= pd.DataFrame.from_records(
        #             data = query.fetchall(), 
        #             columns = cols
        #     )
        #df.index = pd.to_datetime(df.index, format = '%Y-%m-%d')
        df = df.apply(lambda x:x.replace('#DIV/0!','0').replace('#N/A','0')).apply(lambda x:x.replace('','0')).astype(float)
        df = df.round(decimals=1)
        index_list.append(df)
    #kb_conn.close()

    return index_list


if __name__ == "__main__":
    data_load_state = st.text('Loading Index Data...')
    index_list = load_index_data()
    mdf = index_list[0]
    jdf = index_list[1]

    last_month = pd.to_datetime(str(mdf.index.values[-1])).strftime('%Y.%m')
    st.markdown(f'최종업데이트: **{last_month}월**')
    with st.expander("See Raw Data"):
        with st.container():
            col1, col2, col3 = st.columns([30,2,30])
            with col1:
                try:
                    st.dataframe(mdf.loc[::-1].astype(float).fillna(0).round(decimals=2).style.background_gradient(cmap, axis=0)\
                                                .format(precision=2, na_rep='MISSING', thousands=","))
                except ValueError :
                    st.dataframe(mdf.loc[::-1].astype(float).fillna(0).round(decimals=2).style.background_gradient(cmap, axis=0)\
                                                .format(precision=2, na_rep='MISSING', thousands=","))
            with col2:
                st.write("")
            with col3: 
                try:
                    st.dataframe(jdf.loc[::-1].astype(float).fillna(0).round(decimals=2).style.background_gradient(cmap, axis=0)\
                                                .format(precision=2, na_rep='MISSING', thousands=","))
                except ValueError :
                    st.dataframe(jdf.loc[::-1].astype(float).fillna(0).round(decimals=2).style.background_gradient(cmap, axis=0)\
                                                .format(precision=2, na_rep='MISSING', thousands=","))

     #월간 증감률
    mdf_change = mdf.pct_change()*100
    #mdf_change = mdf_change.iloc[1:]
    
    mdf_change.replace([np.inf, -np.inf], np.nan, inplace=True)
    mdf_change = mdf_change.astype(float).fillna(0)
    # mdf = mdf.mask(np.isinf(mdf))
    jdf_change = jdf.pct_change()*100
    #jdf_change = jdf_change.iloc[1:]
    
    jdf_change.replace([np.inf, -np.inf], np.nan, inplace=True)
    jdf_change = jdf_change.astype(float).fillna(0)
    #전세지수 증감은 2014.2월부터 있기에 slice 해야함
    mdf_change_s = mdf_change.loc["2014-02-01":]
    mdf_s = mdf.loc["2014-01-01":]
    cum_mdf = (1+mdf_change_s/100).cumprod() -1
    cum_mdf = cum_mdf.round(decimals=3)
    cum_jdf = (1+jdf_change/100).cumprod() -1
    cum_jdf = cum_jdf.round(decimals=3)
    st.dataframe(cum_mdf)
    st.dataframe(cum_jdf)
    #일주일 간 상승률 순위
    kb_last_df  = pd.DataFrame()
    kb_last_df['매매증감'] = mdf_change.iloc[-1].T.to_frame()
    kb_last_df['전세증감'] = jdf_change.iloc[-1].T.to_frame()
    kb_last_df['1m'] = mdf_change.iloc[-1].T.to_frame() 
    kb_last_df['6m'] = mdf_change.iloc[-6].T.to_frame()
    kb_last_df['1y'] = mdf_change.iloc[-12].T.to_frame()
    kb_last_df['2y'] = mdf_change.iloc[-24].T.to_frame()
    kb_last_df['3y'] = mdf_change.iloc[-36].T.to_frame()
#    kb_last_df.dropna(inplace=True)
    kb_last_df = kb_last_df.astype(float).fillna(0).round(decimals=1)
    #일주일 간 상승률 순위
    last_df = mdf_change.iloc[-1].T.to_frame()
    last_df['전세증감'] = jdf_change.iloc[-1].T.to_frame()
    last_df.columns = ['매매증감', '전세증감']
    last_df.dropna(inplace=True)
    last_df = last_df.round(decimals=1)

    #버블 지수 만들어 보자
    #아기곰 방식:버블지수 =(관심지역매매가상승률-전국매매가상승률) - (관심지역전세가상승률-전국전세가상승률)
    bubble_df = mdf_change.subtract(mdf_change_s['전국'], axis=0)- jdf_change.subtract(jdf_change['전국'], axis=0)
    bubble_df = bubble_df*100
    
    #곰곰이 방식: 버블지수 = 매매가비율(관심지역매매가/전국평균매매가) - 전세가비율(관심지역전세가/전국평균전세가)
    bubble_df2 = mdf_s.div(mdf_s['전국'], axis=0) - jdf.div(jdf['전국'], axis=0)
    bubble_df2 = bubble_df2.astype(float).fillna(0).round(decimals=5)*100
    # st.dataframe(mdf)

    #전세 파워 만들기
    cum_ch = (mdf_change_s/100 +1).cumprod()-1
    jcum_ch = (jdf_change/100 +1).cumprod()-1
    m_power = (jcum_ch - cum_ch)*100
    m_power = m_power.astype(float).fillna(0).round(decimals=2)

    #마지막 데이터만 
    power_df = m_power.iloc[-1].T.to_frame()
    power_df['버블지수'] = bubble_df2.iloc[-1].T.to_frame()
    power_df.columns = ['전세파워', '버블지수']
    # power_df.dropna(inplace=True)
    power_df = power_df.astype(float).fillna(0).round(decimals=2)
    power_df['jrank'] = power_df['전세파워'].rank(ascending=False, method='min').round(1)
    power_df['brank'] = power_df['버블지수'].rank(ascending=True, method='min').round(decimals=1)
    power_df['score'] = power_df['jrank'] + power_df['brank']
    power_df['rank'] = power_df['score'].rank(ascending=True, method='min')
    power_df = power_df.sort_values('rank', ascending=True)
    


    #여기서부터는 선택
    my_choice = st.sidebar.radio(
                    "Select Menu", ('Basic','Index', 'Together'))
    if my_choice == 'Basic':
        period_ = mdf.index.strftime("%Y-%m").tolist()
        st.subheader("기간 지역 분석")
        start_date, end_date = st.select_slider(
            'Select Date to Compare index change', 
            options = period_,
            value = (period_[-24], period_[-1]))
        #information display
        #필요 날짜만 slice
        slice_om = mdf.loc[start_date:end_date]
        slice_oj = jdf.loc[start_date:end_date]
        slice_m = mdf.loc[start_date:end_date]
        slice_j = jdf.loc[start_date:end_date]
        diff = slice_om.index[-1] - slice_om.index[0]
        cols = st.columns(4)
        cols[0].write(f"시작: {start_date}")
        cols[1].write(f"끝: {end_date}")
        cols[2].write(f"전체 기간: {round(diff.days/365,1)} 년")
        cols[3].write("")
        submit = st.sidebar.button('Analize Local situation')
        if submit:
            ### 매매지수 하락 전세지수 상승 #########################################################################################            
            #############
            s_m = pd.DataFrame()
            s_j = pd.DataFrame()
            so_m = pd.DataFrame()
            so_j = pd.DataFrame()
            s_m[start_date] = slice_m.iloc[0].T
            s_m[end_date] = slice_m.iloc[-1].T
            s_j[start_date] = slice_j.iloc[0].T
            s_j[end_date] = slice_j.iloc[-1].T
            so_m[start_date] = slice_om.iloc[0].T
            so_m[end_date] = slice_om.iloc[-1].T
            so_j[start_date] = slice_oj.iloc[0].T
            so_j[end_date] = slice_oj.iloc[-1].T
            condition1 = s_m.iloc[:,0] > s_m.iloc[:,-1]
            condition2 = s_j.iloc[:,0] <= s_j.iloc[:,-1]
            condition3 = so_m.iloc[:,0] > so_m.iloc[:,-1]
            condition4 = so_j.iloc[:,0] <= so_j.iloc[:,-1]
            m_de = s_m.loc[condition1]
            j_in = s_j.loc[condition2]
            mo_de = so_m.loc[condition3]
            jo_in = so_j.loc[condition4]
            inter_df = pd.merge(m_de, j_in, how='inner', left_index=True, right_index=True, suffixes=('m', 'j'))
            inter_odf = pd.merge(mo_de, jo_in, how='inner', left_index=True, right_index=True, suffixes=('m', 'j'))
            inter_kb_list = inter_df.index.to_list()
            
            if len(inter_kb_list) == 0:
                inter_kb_list.append("없음")
                #st.write(inter_kb_list[0])
            inter_one_list = inter_odf.index.to_list()
            with st.container():
                col1, col2, col3 = st.columns([30,2,30])
                with col1:
                    st.subheader("KB 매매지수 하락 전세지수 상승 지역")
                    st.dataframe(inter_df.style.background_gradient(cmap, axis=0)\
                                                .format(precision=2, na_rep='MISSING', thousands=","), 600, 500)
                with col2:
                    st.write("")
                with col3:
                    st.subheader("부동산원 매매지수 하락 전세지수 상승 지역")
                    st.dataframe(inter_odf.style.background_gradient(cmap, axis=0)\
                                                .format(precision=2, na_rep='MISSING', thousands=","),600,500)
            html_br="""
            <br>
            """
            st.markdown(html_br, unsafe_allow_html=True)
    elif my_choice == 'Index':
        
        column_list = mdf.columns.to_list()
        city_series = pd.Series(column_list)
        selected_dosi = st.sidebar.selectbox(
                '광역시-도', column_list
            )
    
        submit = st.sidebar.button('Draw Price Index')

        if submit:
        ### Block KB 지수 #########################################################################################
            flag = "아파트 실거래가격지수 "
            drawAPT_update.run_price_index(selected_dosi, selected_dosi, mdf, jdf, mdf_change, jdf_change, flag)
            with st.container():
                col1, col2, col3 = st.columns([30,2,30])
                with col1: #4년 그래프와 평균 
                    try:
                        drawAPT_update.draw_4years_index(selected_dosi, mdf, jdf, mdf_change, jdf_change)
                    except Exception as e:
                        st.write(e)
                with col2:
                    st.write("")
                with col3:
                    monthly_slice = mdf_change.loc[mdf_change.index.month == mdf_change.index[-1].month]
                    monthly_slice = monthly_slice.round(decimals=1)
                    fig = px.bar(
                               monthly_slice,
                                x=monthly_slice.index.year,
                                y=selected_dosi,
                                color=selected_dosi,
                                hover_name=selected_dosi
                            )
                    st.plotly_chart(fig, theme="ggplot2")#, use_container_width=True)
            with st.container():
                col1, col2, col3 = st.columns([30,2,30])
                with col1:
                    flag = "아파트 실거래가격지수 "
                    try:
                        drawAPT_update.run_price_index(selected_dosi, selected_dosi, mdf, jdf, mdf_change, jdf_change, flag)
                    except Exception as e:
                        st.write(e)
                with col2:
                    st.write("")
                with col3:
                    flag = "아파트 실거래가격지수 "
                    drawAPT_update.draw_flower(selected_dosi, selected_dosi, cum_mdf, cum_jdf, flag)
        html_br="""
        <br>
        """
        st.markdown(html_br, unsafe_allow_html=True)
    else: #KB는 자체적으로 볼때, 지역 같이 볼 때는 부동산원만 
        #지역과 기간 같이 보기
        period_ = mdf.index.strftime("%Y-%m").tolist()
        st.subheader("지역별 기간 상승률 분석")
        start_date, end_date = st.select_slider(
            'Select Date to Compare index change', 
            options = period_,
            value = (period_[-13], period_[-1]))
        
        #부동산원 / KB
        slice_om = mdf.loc[start_date:end_date]
        slice_oj = jdf.loc[start_date:end_date]
        slice_m = mdf.loc[start_date:end_date]
        slice_j = jdf.loc[start_date:end_date]
        diff = slice_om.index[-1] - slice_om.index[0]
        #information display
        cols = st.columns(4)
        cols[0].write(f"시작: {start_date}")
        cols[1].write(f"끝: {end_date}")
        cols[2].write(f"전체 기간: {round(diff.days/365,1)} 년")
        cols[3].write("")
        #st.dataframe(slice_om)
        change_odf = pd.DataFrame()
        change_odf['매매증감'] = (slice_om.iloc[-1]/slice_om.iloc[0]-1).to_frame()*100
        change_odf['전세증감'] = (slice_oj.iloc[-1]/slice_oj.iloc[0]-1).to_frame()*100
        change_odf = change_odf.dropna().astype(float).round(decimals=2)
        change_df = pd.DataFrame()
        change_df['매매증감'] = (slice_m.iloc[-1]/slice_m.iloc[0]-1).to_frame()*100
        change_df['전세증감'] = (slice_j.iloc[-1]/slice_j.iloc[0]-1).to_frame()*100
        change_df = change_df.dropna().astype(float).round(decimals=2)
        #상승률 누적
        slice_om = mdf.loc[start_date:end_date]
        slice_oj = jdf.loc[start_date:end_date]
        slice_om_ch = mdf_change.loc[start_date:end_date]
        slice_oj_ch = jdf_change.loc[start_date:end_date]
        slice_om_ch = slice_om_ch.round(decimals=2)
        slice_oj_ch = slice_oj_ch.round(decimals=2)
        slice_cum_omdf = (1+slice_om_ch/100).cumprod() -1
        slice_cum_omdf = slice_cum_omdf.round(decimals=4)
        slice_cum_ojdf = (1+slice_oj_ch/100).cumprod() -1
        slice_cum_ojdf = slice_cum_ojdf.round(decimals=4)

        slice_m = mdf.loc[start_date:end_date]
        slice_j = jdf.loc[start_date:end_date]
        slice_m_ch = mdf_change.loc[start_date:end_date]
        slice_j_ch = jdf_change.loc[start_date:end_date]
        slice_m_ch = slice_m_ch.round(decimals=2)
        slice_j_ch = slice_j_ch.round(decimals=2)
        slice_cum_mdf = (1+slice_m_ch/100).cumprod() -1
        slice_cum_mdf = slice_cum_mdf.round(decimals=4)
        slice_cum_jdf = (1+slice_j_ch/100).cumprod() -1
        slice_cum_jdf = slice_cum_jdf.round(decimals=4)


        #지역 같이 
        citys = mdf.columns.tolist()
        options = st.multiselect('Select City to Compare index', citys, citys[:3])
        submit = st.button('analysis')
        if submit:
            ### 부동산원 index chart #########################################################################################
            with st.container():
                col1, col2, col3 = st.columns([30,2,30])
                with col1:
                    flag = '아파트 실거래가격 '
                    drawAPT_weekly.run_one_index_together(options, slice_om, slice_om_ch, flag)

                with col2:
                    st.write("")
                with col3:
                    flag = '아파트 실거래가격 '
                    drawAPT_weekly.run_one_jindex_together(options, slice_oj, slice_oj_ch, flag)
                    
            html_br="""
            <br>
            """ 
            ### KB index chart #########################################################################################
            # with st.container():
            #     col1, col2, col3 = st.columns([30,2,30])
            #     with col1:
            #         flag = 'KB 월간'
            #         drawAPT_weekly.run_one_index_together(options, slice_m, slice_m_ch, flag)

            #     with col2:
            #         st.write("")
            #     with col3:
            #         flag = 'KB 월간'
            #         drawAPT_weekly.run_one_jindex_together(options, slice_j, slice_j_ch, flag)
                    
            # html_br="""
            # <br>
            # """ 
            ### 부동산원 Bubble/ flower chart #########################################################################################
            with st.container():
                col1, col2, col3 = st.columns([30,2,30])
                with col1:
                    flag = '아파트 실거래가격'
                    drawAPT_weekly.draw_index_change_with_bubble_slice(options, change_odf, flag)

                with col2:
                    st.write("")
                with col3:
                    flag = '아파트 실거래가격'
                    drawAPT_weekly.draw_flower_together(options, slice_cum_omdf, slice_cum_ojdf, flag)
                    
            html_br="""
            <br>
            """             
            ### KB Bubble/ flower chart #########################################################################################
            # with st.container():
            #     col1, col2, col3 = st.columns([30,2,30])
            #     with col1:
            #         flag = 'KB 월간'
            #         drawAPT_weekly.draw_index_change_with_bubble_slice(options, change_df, flag)

            #     with col2:
            #         st.write("")
            #     with col3:
            #         flag = 'KB 월간'
            #         drawAPT_weekly.draw_flower_together(options, slice_cum_mdf, slice_cum_jdf, flag)
                    
            # html_br="""
            # <br>
            # """               
    
html_br="""
<br>
"""

html_line="""

<br>
<br>
<br>
<br>
<hr style= "  display: block;
  margin-top: 0.5em;
  margin-bottom: 0.5em;
  margin-left: auto;
  margin-right: auto;
  border-style: inset;
  border-width: 1.5px;">
<p style="color:Gainsboro; text-align: right;">By: 기하급수적 https://blog.naver.com/indiesoul2 / sizipusx2@gmail.com</p>
"""
st.markdown(html_line, unsafe_allow_html=True)