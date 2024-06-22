import datetime
import numpy as np
import pandas as pd
import sqlite3
from urllib.request import urlopen
import json
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dateutil.relativedelta import relativedelta
import streamlit as st
import drawAPT_weekly 
import drawAPT_update
import seaborn as sns
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import plotly.io as pio

cmap = cmap=sns.diverging_palette(250, 5, as_cmap=True)
pio.templates.default = "myID"
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
marker_colors = ['rgb(205,32,40)', 'rgb(22,108,150)', 'rgb(160,103,173)', 'rgb(244,201,107)', 'rgb(153,204,0)', \
                       'rgb(153,51,102)', 'rgb(0,255,0)','rgb(255,69,0)', 'rgb(0,0,255)', 'rgb(255,204,0)', \
                        'rgb(255,153,204)', 'rgb(0,255,255)', 'rgb(128,0,0)', 'rgb(0,128,0)', 'rgb(0,0,128)', \
                         'rgb(128,128,0)', 'rgb(128,0,128)', 'rgb(0,128,128)', 'rgb(192,192,192)', 'rgb(153,153,255)', \
                             'rgb(255,255,0)', 'rgb(255,255,204)', 'rgb(102,0,102)', 'rgb(255,128,128)', 'rgb(0,102,204)',\
                                 'rgb(255,102,0)', 'rgb(51,51,51)', 'rgb(51,153,102)', 'rgb(51,153,102', 'rgb(204,153,255)']
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
#월간 데이터
def load_index_data(flag):
    index_list = []
    if flag == "real":
      query_list = ["select * from rmae", "select * from rjeon"]#, "SELECT * FROM jratio"]
      conn = create_connection("files/one_monthly.db")
    elif flag == 'one':
      query_list = ["select * from one_mae", "select * from one_jeon"]#, "SELECT * FROM jratio"]
      conn = create_connection("files/one_monthly.db")
    else:
      query_list = ["select * from mae", "select * from jeon"]
      conn = create_connection("files/kb_monthly.db")
    for query in query_list:
        df = pd.read_sql(query, conn, index_col='date', parse_dates={'date', "%Y-%m"})
        # query = conn.execute(query)
        # cols = [column[0] for column in query.description]
        # df= pd.DataFrame.from_records(
        #             data = query.fetchall(),
        #             columns = cols
        #     )
        #df.index = pd.to_datetime(df.index, format = '%Y-%m-%d')
        df = df.apply(lambda x:x.replace('#DIV/0!','0').replace('#N/A','0')).apply(lambda x:x.replace('','0')).astype(float)
        df = df.round(decimals=3)
        index_list.append(df)
    #kb_conn.close()

    return index_list

@st.cache_data(ttl=datetime.timedelta(days=1))
def get_common_dates_data(df1, df2):
  """
  두 데이터프레임의 공통된 날짜에 해당하는 데이터만 가져옵니다.

  Args:
    df1: 첫 번째 데이터프레임
    df2: 두 번째 데이터프레임

  Returns:
    두 데이터프레임의 공통된 날짜에 해당하는 데이터
  """

  # 날짜 인덱스 추출
  df1_dates = df1.index.to_numpy()
  df2_dates = df2.index.to_numpy()

  # 공통된 날짜 찾기
  common_dates = set(df1_dates) & set(df2_dates)

  # 공통된 날짜에 해당하는 데이터만 선택
  df1_common = df1[df1.index.isin(common_dates)]
  df2_common = df2[df2.index.isin(common_dates)]

  return df1_common, df2_common


if __name__ == "__main__":
    data_load_state = st.text('Loading Index Data...')
    real_index_list = load_index_data("real")
    one_index_list = load_index_data("one")
    kb_index_list = load_index_data("kb")
    mdf = real_index_list[0]
    jdf = real_index_list[1]
    omdf = one_index_list[0]
    ojdf = one_index_list[1]
    kbmdf = kb_index_list[0]
    kbjdf = kb_index_list[1]

    last_month = pd.to_datetime(str(mdf.index.values[-1])).strftime('%Y.%m')
    last_month_jeon = pd.to_datetime(str(jdf.index.values[-1])).strftime('%Y.%m')
    onelast_month = pd.to_datetime(str(omdf.index.values[-1])).strftime('%Y.%m')
    kblast_month = pd.to_datetime(str(kbmdf.index.values[-1])).strftime('%Y.%m')
    with st.expander("See recently Data Update"):
        cols = st.columns(3)
        cols[0].markdown(f'실거래가 최종업데이트: **{last_month}월**')
        cols[1].markdown(f'부동산원 최종업데이트: **{onelast_month}월**')
        cols[2].markdown(f'KB 최종업데이트: **{kblast_month}월**')
    # with st.expander("See 실거래가 Raw Data"):
    #     with st.container():
    #         col1, col2, col3 = st.columns([30,2,30])
    #         with col1:
    #             try:
    #                 st.dataframe(mdf.loc[::-1].astype(float).fillna(0).round(decimals=2).style.background_gradient(cmap, axis=0)\
    #                                             .format(precision=2, na_rep='MISSING', thousands=","))
    #             except ValueError :
    #                 st.dataframe(mdf.loc[::-1].astype(float).fillna(0).round(decimals=2).style.background_gradient(cmap, axis=0)\
    #                                             .format(precision=2, na_rep='MISSING', thousands=","))
    #         with col2:
    #             st.write("")
    #         with col3: 
    #             try:
    #                 st.dataframe(jdf.loc[::-1].astype(float).fillna(0).round(decimals=2).style.background_gradient(cmap, axis=0)\
    #                                             .format(precision=2, na_rep='MISSING', thousands=","))
    #             except ValueError :
    #                 st.dataframe(jdf.loc[::-1].astype(float).fillna(0).round(decimals=2).style.background_gradient(cmap, axis=0)\
    #                                             .format(precision=2, na_rep='MISSING', thousands=","))

     #월간 증감률
     #변화율로 봅시다
    mdf_change = mdf.pct_change()*100
    mdf_change.replace([np.inf, -np.inf], np.nan, inplace=True)
    mdf_change = mdf_change.astype(float).fillna(0).round(decimals=2)
    mdf_change_yoy = mdf.pct_change(12)*100
    mdf_change_yoy.replace([np.inf, -np.inf], np.nan, inplace=True)
    mdf_change_yoy = mdf_change_yoy.astype(float).fillna(0).round(decimals=2)
    omdf_ch = omdf.pct_change()*100
    kbmdf_ch = kbmdf.pct_change()*100

    #전세
    jdf_change = jdf.pct_change()*100
    jdf_change.replace([np.inf, -np.inf], np.nan, inplace=True)
    jdf_change = jdf_change.astype(float).fillna(0)
    jdf_change_yoy = jdf.pct_change(12)*100
    jdf_change_yoy.replace([np.inf, -np.inf], np.nan, inplace=True)
    jdf_change_yoy = jdf_change_yoy.astype(float).fillna(0)
    ojdf_ch = ojdf.pct_change()*100
    kbjdf_ch = kbjdf.pct_change()*100
    
    mdf_change = mdf_change.iloc[1:].round(decimals=2)
    mdf_change_yoy = mdf_change_yoy.iloc[11:].round(decimals=2)
    omdf_ch = omdf_ch.iloc[1:].round(decimals=2)
    kbmdf_ch = kbmdf_ch.iloc[1:].round(decimals=2)
    jdf_change = jdf_change.iloc[1:].round(decimals=2)
    jdf_change_yoy = jdf_change_yoy.iloc[11:].round(decimals=2)
    ojdf_ch = ojdf_ch.iloc[1:].round(decimals=2)
    kbjdf_ch = kbjdf_ch.iloc[1:].round(decimals=2)

    cum_mdf = (1+mdf_change/100).cumprod() -1
    cum_mdf = cum_mdf.round(decimals=3)
    cum_jdf = (1+jdf_change/100).cumprod() -1
    cum_jdf = cum_jdf.round(decimals=3)
    #매매와 전세의 데이터 시작점이 다르다. 매매 2006년 이후 전세 2016이후
    # 공통 날짜를 구합니다.
    cum_mdf_common, cum_jdf_common = get_common_dates_data(cum_mdf, cum_jdf)

    #마지막 데이터로 데이터프레임 만들기
    real_last_df  = pd.DataFrame()
    real_last_df['매매증감'] = mdf_change.iloc[-1].T.to_frame()
    real_last_df['전세증감'] = jdf_change.iloc[-1].T.to_frame()
    real_last_df_yoy  = pd.DataFrame()
    real_last_df_yoy['매매증감'] = mdf_change_yoy.iloc[-1].T.to_frame()
    real_last_df_yoy['전세증감'] = jdf_change_yoy.iloc[-1].T.to_frame()

    #여기서부터는 선택
    my_choice = st.sidebar.radio(
                    "Select Menu", ('월간 동향', '지수 같이보기','Index', '지역 같이보기', 'Predict'))
    if my_choice == '월간 동향':
        ### Draw Bubble chart ##############
        with st.container():
            col1, col2, col3 = st.columns([30,2,30])
            with col1:
                flag = '실거래가 MOM '
                drawAPT_weekly.draw_index_change_with_bubble(real_last_df, flag, last_month)

            with col2:
                st.write("")
            with col3:
                flag = '실거래가 YOY '
                drawAPT_weekly.draw_index_change_with_bubble(real_last_df_yoy, flag, last_month)
                
        html_br="""
        <br>
        """
        st.markdown(html_br, unsafe_allow_html=True)  
        #전국 MOM Bar 차트############################################
        with st.container():
            col1, col2, col3 = st.columns([30,2,30])
            with col1:
                flag = ['실거래가 MOM','매매증감']
                drawAPT_weekly.draw_index_change_with_bar(real_last_df, flag, last_month)
            with col2:
                st.write("")
            with col3:
                flag = ['실거래가 MOM','전세증감']
                drawAPT_weekly.draw_index_change_with_bar(real_last_df, flag, last_month_jeon)        
            html_br="""
            <br>
            """
            st.markdown(html_br, unsafe_allow_html=True)
        ### 전국 YOY bar chart ################################
        with st.container():
            col1, col2, col3 = st.columns([30,2,30])
            with col1:
                flag = ['실거래가 YOY ','매매증감']
                drawAPT_weekly.draw_index_change_with_bar(real_last_df_yoy, flag, last_month)
            with col2:
                st.write("")
            with col3:
                flag = ['실거래가 YOY ','전세증감']
                drawAPT_weekly.draw_index_change_with_bar(real_last_df_yoy, flag, last_month_jeon)        
        html_br="""
        <br>
        """
        st.markdown(html_br, unsafe_allow_html=True)
    elif my_choice == '지수 같이보기':
        # 모든 데이터프레임의 시작 날짜 중 가장 늦은 날짜를 찾습니다.
        start_date = max(mdf.index.min(), omdf.index.min(), kbmdf.index.min())

        # 모든 데이터프레임의 종료 날짜 중 가장 이른 날짜를 찾습니다.
        end_date = min(mdf.index.max(), omdf.index.max(), kbmdf.index.max())
        
        # 시작 날짜보다 한 달 후 날짜를 구합니다.
        start_date_plus_one_month = start_date + relativedelta(months=1)
        #st.write(start_date_plus_one_month)

        # reindex를 사용하여 각 데이터프레임의 인덱스를 동일한 범위로 맞춥니다.
        mdf = mdf.loc[start_date_plus_one_month:end_date]
        omdf = omdf.loc[start_date_plus_one_month:end_date]
        kbmdf = kbmdf.loc[start_date_plus_one_month:end_date]
        mdf_ch = mdf_change.loc[start_date_plus_one_month:end_date]
        omdf_ch = omdf_ch.loc[start_date_plus_one_month:end_date]
        kbmdf_ch = kbmdf_ch.loc[start_date_plus_one_month:end_date]

        # # 세 데이터프레임의 인덱스를 리스트로 변환합니다
        # index1 = mdf.index.tolist()
        # index2 = omdf.index.tolist()
        # index3 = kbmdf.index.tolist()

        # # 세 리스트가 같은지 확인합니다
        # if index1 == index2 == index3:
        #     st.write("세 데이터프레임의 인덱스는 모두 같습니다.")
        # else:
        #     st.write("세 데이터프레임의 인덱스는 모두 같지 않습니다.")
        #     diff12 = set(index1) - set(index2)
        #     diff13 = set(index1) - set(index3)
        #     diff23 = set(index2) - set(index3)
        #     st.write("df1과 df2의 인덱스 차집합: ", diff12)
        #     st.write("df1과 df3의 인덱스 차집합: ", diff13)
        #     st.write("df2과 df3의 인덱스 차집합: ", diff23)


        jstart_date = max(jdf.index.min(), ojdf.index.min(), kbjdf.index.min())
        jstart_date_plus_one_month = jstart_date + relativedelta(months=1)
        #st.write(jstart_date)

        # 모든 데이터프레임의 종료 날짜 중 가장 이른 날짜를 찾습니다.
        jend_date = min(jdf.index.max(), ojdf.index.max(), kbjdf.index.max())
        #st.write(jend_date)
        jdf = jdf.loc[jstart_date_plus_one_month:jend_date]
        ojdf = ojdf.loc[jstart_date_plus_one_month:jend_date]
        kbjdf = kbjdf.loc[jstart_date_plus_one_month:jend_date]
        jdf_ch = jdf_change.loc[jstart_date_plus_one_month:jend_date]
        ojdf_ch = ojdf_ch.loc[jstart_date_plus_one_month:jend_date]
        kbjdf_ch = kbjdf_ch.loc[jstart_date_plus_one_month:jend_date]


        # 데이터프레임의 컬럼명 추출 후, 같은 이름을 가진 컬럼만 병합
        common_col = list(set(mdf.columns.tolist()) & set(omdf.columns.tolist()) & set(kbmdf.columns.tolist()))
        city_series = pd.Series(common_col)
        selected_dosi = st.sidebar.selectbox(
                '광역시-도', common_col
            )
        submit = st.sidebar.button('지수 같이 보기')
        if submit:
            tab1, tab2 = st.tabs(["⏰ 매매지수", "🗺️ 전세지수"])
            with tab1: #매매지수
                drawAPT_update.draw_index_together(selected_dosi, mdf, omdf, kbmdf, mdf_ch, omdf_ch, kbmdf_ch, "매매지수")
            with tab2: #매매지수
                drawAPT_update.draw_index_together(selected_dosi, jdf, ojdf, kbjdf, jdf_ch, ojdf_ch, kbjdf_ch, "전세지수")
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
            ##매매/전세 tab 으로 구분하자.
            tab1, tab2 = st.tabs(["⏰ 매매지수", "🗺️ 전세지수"])
            with tab1: #매매지수

                with st.container():
                    col1, col2, col3 = st.columns([30,2,30])
                    with col1: #4년 그래프와 평균 
                        try:
                            drawAPT_update.draw_4years_index(selected_dosi, mdf_change, "mae")
                        except Exception as e:
                            st.write(e)
                    with col2:
                        st.write("")
                    with col3:
                        try:
                            monthly_slice = mdf_change.loc[mdf_change.index.month == mdf_change.index[-1].month]
                            monthly_slice = monthly_slice.round(decimals=1)
                            col1, col2 = st.columns(2) 
                            current_month = pd.to_datetime(mdf_change.index.values[-1]).month
                            col1.metric(label=str(current_month)+"월", value = str(round(monthly_slice.loc[:,selected_dosi][-1],1))+"%")
                            col2.metric(label=str(current_month)+"월 평균", value = str(round(monthly_slice.loc[:,selected_dosi].mean(),1))+"%")
                            titles = dict(text= '<b>['+selected_dosi +'] 연도별 ' +str(current_month) +'월 매매가격 변동</b>', x=0.5, y = 0.9, xanchor='center', yanchor= 'top')
                            fig = px.bar(
                                    monthly_slice,
                                        x=monthly_slice.index.year,
                                        y=selected_dosi,
                                        color=selected_dosi,
                                        hover_name=selected_dosi,
                                        text=selected_dosi
                                    )
                            fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), xaxis_tickformat = '%Y')
                            st.plotly_chart(fig)
                        except Exception as e:
                            st.write(e)
                with st.container():
                    col1, col2, col3 = st.columns([30,2,30])
                    with col1:
                        flag = "아파트 실거래가격지수 "
                        try:
                            drawAPT_update.basic_chart(selected_dosi, mdf, mdf_change, "mae")
                        except Exception as e:
                            st.write(e)
                    with col2:
                        st.write("")
                    with col3:
                        flag = "아파트 실거래가격지수 "
                        drawAPT_update.draw_flower(selected_dosi, selected_dosi, cum_mdf_common, cum_jdf_common, flag)
            html_br="""
            <br>
            """
            st.markdown(html_br, unsafe_allow_html=True)
            with tab2: #전세지수
                with st.container():
                    col1, col2, col3 = st.columns([30,2,30])
                    with col1: #4년 그래프와 평균 
                        try:
                            drawAPT_update.draw_4years_index(selected_dosi, jdf_change, "jeon")
                        except Exception as e:
                            st.write(e)
                    with col2:
                        st.write("")
                    with col3:
                        try:
                            monthly_slice = jdf_change.loc[jdf_change.index.month == jdf_change.index[-1].month]
                            monthly_slice = monthly_slice.round(decimals=1)
                            current_month2 = pd.to_datetime(jdf_change.index.values[-1]).month
                            col1, col2 = st.columns(2) 
                            col1.metric(label=str(current_month2)+"월", value = str(round(monthly_slice.loc[:,selected_dosi][-1],1))+"%")
                            col2.metric(label=str(current_month2)+"월 평균", value = str(round(monthly_slice.loc[:,selected_dosi].mean(),1))+"%")
                            titles = dict(text= '<b>['+selected_dosi +'] 연도별 ' +str(current_month2) +'월 전세가격 변동</b>', x=0.5, y = 0.9, xanchor='center', yanchor= 'top')
                            fig = px.bar(
                                    monthly_slice,
                                        x=monthly_slice.index.year,
                                        y=selected_dosi,
                                        color=selected_dosi,
                                        hover_name=selected_dosi,
                                        text=selected_dosi
                                    )
                            fig.update_layout(title = titles, titlefont_size=15, legend=dict(orientation="h"), xaxis_tickformat = '%Y')
                            st.plotly_chart(fig)
                        except Exception as e:
                            st.write(e)
                with st.container():
                    col1, col2, col3 = st.columns([30,2,30])
                    with col1:
                        flag = "아파트 실거래가격지수 "
                        try:
                            drawAPT_update.basic_chart(selected_dosi, jdf, jdf_change, "jeon")
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
    elif my_choice == "지역 같이보기": #KB는 자체적으로 볼때, 지역 같이 볼 때는 부동산원만 
        #지역과 기간 같이 보기
        period_ = mdf.index.strftime("%Y-%m").tolist()
        st.subheader("지역별 기간 상승률 분석")
        start_date, end_date = st.select_slider(
            'Select Date to Compare index change', 
            options = period_,
            value = (period_[0], period_[-1]))
        
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
    else:
        st.subheader("실거래가지수 얘측")
        column_list = mdf.columns.to_list()
        city_series = pd.Series(column_list)
        selected_dosi = st.sidebar.selectbox(
                '광역시-도', column_list
            )
    
        submit = st.sidebar.button('Predict Price Index')
        from statsmodels.tsa.statespace.sarimax import SARIMAX
        # Select the '전국' column for ARIMA/SARIMA forecasting
        data =mdf[selected_dosi]

        # Fit a SARIMA model (SARIMA is more general than ARIMA)
        model = SARIMAX(data, order=(1, 1, 1), seasonal_order=(1, 1, 1, 12))
        results = model.fit()

        # Forecast for the next 6 months
        forecast = results.get_forecast(steps=6)
        forecast_index = pd.date_range(start=data.index[-1] + pd.DateOffset(months=1), periods=6, freq='M')
        forecast_values = forecast.predicted_mean
        forecast_conf_int = forecast.conf_int()

        # Prepare data for Plotly visualization
        trace_actual = go.Scatter(x=data.index, y=data, mode='lines', name='Actual')
        trace_forecast = go.Scatter(x=forecast_index, y=forecast_values, mode='lines', name='Forecast', line=dict(dash='dash'))
        trace_upper = go.Scatter(x=forecast_index, y=forecast_conf_int.iloc[:, 1], mode='lines', fill=None, name='Upper Confidence Interval', line=dict(dash='dot'))
        trace_lower = go.Scatter(x=forecast_index, y=forecast_conf_int.iloc[:, 0], mode='lines', fill='tonexty', name='Lower Confidence Interval', line=dict(dash='dot'))

        # Calculate trend line
        z = np.polyfit(data.index.astype(int), data.values, 1)
        p = np.poly1d(z)
        trendline = p(data.index.astype(int))

        # Trace for trend line
        trace_trend = go.Scatter(x=data.index, y=trendline, mode='lines', name='Trend Line', line=dict(color='red'))

        # Combine the traces
        data_plot = [trace_actual, trace_forecast, trace_upper, trace_lower, trace_trend]

        # Define the layout
        title_text = dict(text='<b>'+selected_dosi+'</b> APT Price Indices Forecast with <b>SARIMA</b>', x=0.5, y = 0.85, xanchor='center', yanchor= 'top') 
        layout = go.Layout(title=title_text, xaxis=dict(title='Date'), yaxis=dict(title='Index'), template="myID")
        # Create the figure
        fig = go.Figure(data=data_plot, layout=layout)
        st.plotly_chart(fig, use_container_width=True)
        #evaluation
        from sklearn.metrics import mean_squared_error, mean_absolute_error
        # 데이터 분할: 80%는 학습용, 20%는 테스트용
        train_size = int(len(data) * 0.8)
        train, test = data[:train_size], data[train_size:]

        # 모델 학습
        sarima_model = SARIMAX(train, order=(1, 1, 1), seasonal_order=(1, 1, 1, 12))
        sarima_model_fit = sarima_model.fit()

        # 테스트 데이터에 대한 예측 수행
        sarima_forecast = sarima_model_fit.get_forecast(steps=len(test))
        sarima_forecast_values = sarima_forecast.predicted_mean

        # 평가 메트릭 계산
        sarima_mse = mean_squared_error(test, sarima_forecast_values)
        sarima_mae = mean_absolute_error(test, sarima_forecast_values)
        sarima_mape = (abs((test - sarima_forecast_values) / test).mean()) * 100
        #수치 표시
        col1, col2, col3 = st.columns(3) 
        col1.metric(label="SARIMA MSE", value = str(round(sarima_mse,2)))
        col2.metric(label="SARIMA MAE", value = str(round(sarima_mae,2)))
        col3.metric(label="SARIMA MAPE", value = str(round(sarima_mape,2))+"%")
        # Plotly를 사용한 시각화
        trace_train = go.Scatter(x=train.index, y=train, mode='lines', name='Train', marker_color = marker_colors[0])
        trace_test = go.Scatter(x=test.index, y=test, mode='lines', name='Test', marker_color = marker_colors[2])
        trace_forecast = go.Scatter(x=test.index, y=sarima_forecast_values, mode='lines', name='Forecast', line=dict(color='red'))

        data_plot = [trace_train, trace_test, trace_forecast]
        title_text = dict(text='<b>'+selected_dosi+'</b> APT Price Indices Forecast <b>Evaluation with SARIMA</b>', x=0.5, y = 0.85, xanchor='center', yanchor= 'top') 

        layout = go.Layout(title=title_text, yaxis=dict(title='Index'),  template="myID")

        fig = go.Figure(data=data_plot, layout=layout)
        st.plotly_chart(fig, use_container_width=True)

        #prophet
        from prophet import Prophet
        # 'Date'와 '전국' 열만 선택
        data =mdf[selected_dosi]
        data = data.reset_index()

        # Prophet에서 인식할 수 있도록 열 이름 변경
        data.rename(columns={'date': 'ds', selected_dosi: 'y'}, inplace=True)
        st.dataframe(data)

        # Prophet 모델 생성 및 데이터 적합
        model = Prophet()
        model.fit(data)

        # 미래 6개월 데이터를 생성하여 예측
        future = model.make_future_dataframe(periods=6, freq='M')
        forecast = model.predict(future)

        # Plotly 그래프 생성
        # 그래프 레이아웃 설정
        # Plotly 그래프 생성
        fig = make_subplots(rows=3, cols=1, subplot_titles=('Actual vs Forecast', 'Yearly Seasonality', 'Weekly Seasonality'), vertical_spacing=0.15)
        title_text = dict(text='<b>'+selected_dosi+'</b> APT Price Indices Forecast with <b>Prophet</b>', x=0.5, y = 0.85, xanchor='center', yanchor= 'top') 
        layout = go.Layout(title=title_text, xaxis=dict(title='Date'), yaxis=dict(title='House Price Real Index'),  template="myID")
        # Create the figure
        fig = go.Figure(layout=layout)

        # 실제 데이터
        fig.add_trace(go.Scatter(x=data['ds'], y=data['y'], mode='lines', name='Actual'), row=1, col=1)

        # 예측 데이터
        fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat'], mode='lines', name='Forecast'), row=1, col=1)

        # 예측 범위 (불확실성)
        fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat_upper'],
                                mode='lines', name='Upper Bound', line=dict(dash='dash')), row=1, col=1)
        fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat_lower'],
                                mode='lines', name='Lower Bound', line=dict(dash='dash'),
                                fill='tonexty', fillcolor='rgba(0, 100, 80, 0.2)'), row=1, col=1)

        # 계절성 데이터 추출
        yearly = model.plot_components(forecast)
        yearly_data = yearly.get_axes()[0].lines[0].get_xydata()

        weekly = model.plot_components(forecast)
        weekly_data = weekly.get_axes()[1].lines[0].get_xydata()

        # 연간 계절성
        fig.add_trace(go.Scatter(x=yearly_data[:, 0], y=yearly_data[:, 1],
                                mode='lines', name='Yearly Seasonality'), row=2, col=1)

        # 주간 계절성
        fig.add_trace(go.Scatter(x=weekly_data[:, 0], y=weekly_data[:, 1],
                                mode='lines', name='Weekly Seasonality'), row=3, col=1)

        fig.update_layout(template="myID")
        st.plotly_chart(fig, use_container_width=True)

        # 성능 평가
        actual = data['y'].values
        predicted = forecast['yhat'][:len(actual)].values

        # MAE, MSE 계산
        p_mae = sum(abs(actual - predicted)) / len(actual)
        p_mse = sum((actual - predicted) ** 2) / len(actual)
        #수치 표시
        col1, col2 = st.columns(2) 
        col1.metric(label="Prophet MSE", value = str(round(p_mse,2)))
        col2.metric(label="Prophet MAE", value = str(round(p_mae,2)))

        #LSTM
        import numpy as np
        from sklearn.preprocessing import MinMaxScaler
        from tensorflow.keras.models import Sequential
        from tensorflow.keras.layers import Dense, LSTM

        # 데이터 정규화
        data =mdf[selected_dosi]
        scaler = MinMaxScaler(feature_range=(0, 1))
        scaled_data = scaler.fit_transform(data)

        # 학습 데이터 준비
        X_train, y_train = [], []
        for i in range(12, len(scaled_data) - 6):
            X_train.append(scaled_data[i-12:i, 0])
            y_train.append(scaled_data[i, 0])
        X_train, y_train = np.array(X_train), np.array(y_train)
        X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 1))

        # 테스트 데이터 준비
        X_test, y_test = [], []
        for i in range(len(scaled_data) - 12, len(scaled_data)):
            X_test.append(scaled_data[i-12:i, 0])
            y_test.append(scaled_data[i, 0])
        X_test, y_test = np.array(X_test), np.array(y_test)
        X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))

        # LSTM 모델 구성
        model = Sequential()
        model.add(LSTM(units=50, return_sequences=True, input_shape=(X_train.shape[1], 1)))
        model.add(LSTM(units=50))
        model.add(Dense(1))

        # 모델 컴파일
        model.compile(optimizer='adam', loss='mean_squared_error')

        # 모델 학습
        model.fit(X_train, y_train, epochs=100, batch_size=32, verbose=0)

        # 향후 6개월 예측
        predictions = scaled_data[-12:]
        X_test = [predictions]
        X_test = np.array(X_test)
        X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))

        forecast = []
        for _ in range(6):
            pred = model.predict(X_test[-1].reshape(1, X_test.shape[1], 1))
            forecast.append(pred[0, 0])
            next_input = np.append(X_test[-1, 1:], pred)
            next_input = next_input.reshape(1, next_input.shape[0], 1)
            X_test = np.vstack([X_test, next_input])

        forecast = scaler.inverse_transform(np.array(forecast).reshape(-1, 1)).flatten()

        # 시각화 (Plotly 사용)
        actual = go.Scatter(x=data.index, y=data[selected_dosi], mode='lines', name='Actual')
        forecast_dates = pd.date_range(start=data.index[-1], periods=7, freq='MS')[1:]
        forecast_line = go.Scatter(x=forecast_dates, y=forecast, mode='lines', name='LSTM Forecast', line=dict(dash='dot'))
        title_text = dict(text='<b>'+selected_dosi+'</b> APT Price Indices Forecast with <b>LSTM</b>', x=0.5, y = 0.85, xanchor='center', yanchor= 'top') 
        layout = go.Layout(
            title=title_text,
            xaxis=dict(title='Date'),
            yaxis=dict(title='Price Index'),
            showlegend=True,             
            template="myID"
        )

        fig = go.Figure(data=[actual, forecast_line], layout=layout)
        st.plotly_chart(fig, use_container_width=True)

        # 모델 성능 평가
        l_mae = mean_absolute_error(y_test, predictions)
        l_mse = mean_squared_error(y_test, predictions)
        l_mape = np.mean(np.abs((y_test - predictions) / y_test)) * 100
        #수치 표시
        col1, col2, col3 = st.columns(3) 
        col1.metric(label="SARIMA MSE", value = str(round(l_mse)))
        col2.metric(label="SARIMA MAE", value = str(round(l_mae)))
        col3.metric(label="SARIMA MAPE", value = str(round(l_mape))+"%")



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
<p style="color:Gainsboro; text-align: right;">By 기하급수적 https://blog.naver.com/indiesoul2 / sizipusx2@gmail.com</p>
"""
st.markdown(html_line, unsafe_allow_html=True)