from re import S
from datetime import datetime
import datetime

import numpy as np
import pandas as pd
import sqlite3

import streamlit as st
from oauth2client.service_account import ServiceAccountCredentials
from st_aggrid import AgGrid, GridOptionsBuilder
from st_aggrid.shared import GridUpdateMode

from pandas.io.json import json_normalize
from urllib.request import urlopen

import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots

import streamlit as st

import matplotlib.pyplot as plt
from matplotlib import font_manager, rc
import seaborn as sns

import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster

pd.set_option('display.float_format', '{:.2f}'.format)

utcnow= datetime.datetime.utcnow()
time_gap= datetime.timedelta(hours=9)
kor_time= utcnow+ time_gap
now_date = kor_time.strftime('%Y.%m.%d-%H:%M:%S')

token = 'pk.eyJ1Ijoic2l6aXB1c3gyIiwiYSI6ImNrbzExaHVvejA2YjMyb2xid3gzNmxxYmoifQ.oDEe7h9GxzzUUc3CdSXcoA'
#############html 영역####################
html_header="""
<head>
<title>Korea house analysis chart</title>
<meta charset="utf-8">
<meta name="keywords" content="chart, analysis">
<meta name="description" content="House data analysis">
<meta name="author" content="indiesoul">
<meta name="viewport" content="width=device-width, initial-scale=1">
</head>
<h2 style="font-size:200%; color:#008080; font-family:Georgia"> 전국 분양권/재개발/재건축 아파트 네이버 시세 <br>
<hr style= "  display: block;
  margin-top: 0.5em;
  margin-bottom: 0.5em;
  margin-left: auto;
  margin-right: auto;
  border-style: inset;
  border-width: 1.5px;"></h1>
"""

st.set_page_config(page_title="전국 분양권/재개발/재건축 아파트 네이버 시세", page_icon="./files/logo2.png", layout="wide")
st.markdown('<style>body{background-color: #fbfff0}</style>',unsafe_allow_html=True)
st.markdown(html_header, unsafe_allow_html=True)
st.markdown(""" <style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style> """, unsafe_allow_html=True)

pio.templates["myID"] = go.layout.Template(
    layout_annotations=[
        dict(
            name="draft watermark",
            text="graph by 기하급수적",
            textangle=0,
            opacity=0.2,
            font=dict(color="black", size=10),
            xref="paper",
            yref="paper",
            x=0.9,
            y=0.1,
            showarrow=False,
        )
    ]
)

def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by the db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Exception as e:
        st.write(e)

    return conn

#agg table
def aggrid_interactive_table(df: pd.DataFrame):
    """Creates an st-aggrid interactive table based on a dataframe.

    Args:
        df (pd.DataFrame]): Source dataframe

    Returns:
        dict: The selected row
    """
    #df = df.reset_index()
    #gb = GridOptionsBuilder.from_dataframe(df)
    
    gb = GridOptionsBuilder.from_dataframe(
        df, enableRowGroup=True, enableValue=True, enablePivot=True
    )
    gb.configure_pagination(paginationAutoPageSize=True)
    gb.configure_side_bar()
    #gb.configure_selection("single")
    gb.configure_selection('multiple', use_checkbox=True, groupSelectsChildren="Group checkbox select children") # pre_selected_rows=[0], Enable multi-row selection

    response  = AgGrid(
        df,
        editable=False,
        enable_enterprise_modules=True,
        gridOptions=gb.build(),
        #data_return_mode="filtered_and_sorted",'AS_INPUT',
        #width='100%',
        update_mode='MODEL_CHANGED',#"no_update", ##
        fit_columns_on_grid_load=False, #GridUpdateMode.MODEL_CHANGED,
        theme="blue",
        allow_unsafe_jscode=True, #Set it to True to allow jsfunction to be injected
        reload_data=False
    )
   
    return response

def load_data():
    #gsheet
    # scope = [
    #     'https://spreadsheets.google.com/feeds',
    #     'https://www.googleapis.com/auth/drive',
    #     ]

    # json_file_name = './files/weekly-house-db-ac0a43b61ddd.json'

    # credentials = ServiceAccountCredentials.from_json_keyfile_name(json_file_name, scope)
    # gc = gspread.authorize(credentials)

    # spreadsheet_url = 'https://docs.google.com/spreadsheets/d/1-hIsPEvydoLQqouPNY7CT5_n--4ftey0nNNRfe8nce8/edit?usp=sharing'

    # doc = gc.open_by_url(spreadsheet_url)

    # sum_sheet = doc.worksheet('summary')
    # s_values = sum_sheet.get_all_values()
    # s_header, s_rows = s_values[0], s_values[1:]
    # sum_df = pd.DataFrame(s_rows, columns=s_header)

    #sqlite3 에서 읽어오기
    try:
        db_filename = './files/rebuild_house.db'
        conn = create_connection(db_filename)
        #이전 데이터
        query = "SELECT * FROM sum_221003;"
        query = conn.execute(query)
        cols = [column[0] for column in query.description]
        sum_df= pd.DataFrame.from_records(
            data = query.fetchall(), 
            columns = cols
        )

        query1 = "SELECT * FROM apt_sum;"
        query1 = conn.execute(query1)
        cols = [column[0] for column in query1.description]
        stat_df= pd.DataFrame.from_records(
            data = query1.fetchall(), 
            columns = cols
        )
        #st.dataframe(sum_df)
        s_old = len(sum_df)
        st.write(f"아파트명과 공급면적을 기준으로 분류한 총 [{s_old}] 개의 매매 물건이 있습니다!")
    except Exception as e:
        st.write(e)

    # 여기부터 공통
    sum_df['거래가(만)'].replace([np.inf, -np.inf], "0", inplace=True)
    sum_df['거래가(만)'] = sum_df['거래가(만)'].fillna(0).astype(int)
    #sum_df.update(sum_df.select_dtypes(include=np.number).applymap('{:,}'.format))
    sum_df['위도'] = sum_df['위도'].astype(float)
    sum_df['경도'] = sum_df['경도'].astype(float)

    # t_sheet = doc.worksheet('total')
    # t_values = t_sheet.get_all_values()
    # t_header, t_rows = t_values[0], t_values[1:]
    # total_df = pd.DataFrame(t_rows, columns=t_header)
    # db에서 읽어오기
    query = "SELECT * FROM total_221003;"
    query = conn.execute(query)
    cols = [column[0] for column in query.description]
    total_df= pd.DataFrame.from_records(
        data = query.fetchall(), 
        columns = cols
    )
    #st.dataframe(total_df)
    t_old = len(total_df)
    st.write(f"아파트분양권, 재개발, 재건축을 모두 합한 총 [{t_old}] 개의 매매 매물이 있습니다!")
    # total_df['공급면적'].replace([np.inf, -np.inf], '0', inplace=True)
    total_df['공급면적'] = total_df['공급면적'].fillna(0).astype(int)
    #sum_df.update(sum_df.select_dtypes(include=np.number).applymap('{:,}'.format))
    total_df['위도'] = total_df['위도'].astype(float)
    total_df['경도'] = total_df['경도'].astype(float)


    return sum_df, total_df, stat_df

def show_total(s_df):
    
    px.set_mapbox_access_token(token)
    fig = px.scatter_mapbox(s_df, lat="위도", lon="경도", color="매물종류", size="거래가(만)", hover_name="단지명", hover_data=["물건수", "공급면적(평)", "시도"],
                    color_continuous_scale=px.colors.cyclical.IceFire, height=1000, size_max=30, zoom=10)
    fig.update_layout(
        title='전국 재건축-재개발 분양권 아파트 시세',
        autosize=True,
        hovermode='closest',
        showlegend=True,
        legend=dict(orientation="h"),
        mapbox=dict(
            #accesstoken=mapbox_access_token,
            bearing=0,
            center=dict(
                lat=37.5,
                lon=127.0
            ),
            pitch=0,
            zoom=7,
            style='light', #'streets', #'light'
        ),
    )
    fig.update_layout(template="myID")
    st.plotly_chart(fig, use_container_width=True)


    #draw with folium
    # m = folium.Map(
    #     location=[37.5, 127.0],
    #     width='100%',
    #     position='relative',
    #     min_zoom=5,
    #     max_zoom=8,
    #     zoom_start=6,
    #     zoom_control=False
    # )

    # marker_cluster = MarkerCluster().add_to(m)

    # for lat, long in zip(s_df['위도'], s_df['경도']):
    #     folium.Marker([lat, long], icon = folium.Icon(color="green")).add_to(marker_cluster)
    # st_data = st_folium(m)
    

def show_local(select_city, city_apt, city_total):
    px.set_mapbox_access_token(token)
    fig = px.scatter_mapbox(city_apt, lat="위도", lon="경도", color="매물종류", size="거래가(만)", hover_name="단지명", hover_data=["물건수", "공급면적(평)", "시도"],
                    color_continuous_scale=px.colors.cyclical.IceFire, size_max=30, zoom=10, height=800)
    fig.update_layout(
        title='[' + select_city+' ] 재건축-재개발 / 아파트 분양권 네이버 시세',
        legend=dict(orientation="h"),
    )
    fig.update_layout(mapbox_style="satellite-streets")
    fig.update_layout(template="myID")
    st.plotly_chart(fig, use_container_width=True)
    st.write("총 ( "+ str(len(city_total))+ " ) 개의 매매 물건이 있습니다.")  
    #filter_df = city_total[['시도', '지역명', '단지명', '동', '매물방식', '주거형태', '공급면적', '전용면적', '층', '특이사항', '한글거래가액', '확인매물', '매물방향']]
    #response  = aggrid_interactive_table(df=filter_df)
    #if response:
    #    st.write("You selected:")
    #    st.json(response["selected_rows"])
   


if __name__ == "__main__":
    data_load_state = st.text('Loading APT List...')
    s_df, t_df, stat_df = load_data()
    
    #st.table(t_df)
    data_load_state.text("Done! (using st.cache)")
    st.subheader("시세 조사 날짜: 2022.10.03." )
    tab1, tab2 = st.tabs(["📈 지도", "🗃 통계"])
    with tab1:
        show_total(s_df)
        city_list = s_df['시도'].drop_duplicates().to_list()
        city_list.insert(0,'전국')
        #submit = st.sidebar.button('해당 지역만 보기')
        with st.container():
            col1, col2, col3, col4, col5 = st.columns([20,20,20, 20, 20])
        with col1:
            city_name = st.selectbox(
            '해당 지역만 보기',
            city_list
            )
        with col2:
            st.write("")
        with col3:
            st.write("")
        with col4:
            st.write("")
        with col5:
            st.write("")

        city_apt = s_df[s_df['시도'] == city_name]
        city_total = t_df[t_df['시도'] == city_name]
        #if submit:
        if city_name == '전국':
            filter_df = t_df[['시도', '지역명', '단지명', '동', '매물방식', '매물종류', '공급면적', '전용면적', '층', '특이사항', '한글거래가액', '확인매물', '매물방향', '위도', '경도']]
            #response = aggrid_interactive_table(df=filter_df)
            default_flag = '전국'
        else:
            apt_len = len(city_apt)
            show_local(city_name, city_apt, city_total)
            filter_df = city_total[['시도', '지역명', '단지명', '동', '매물방식', '매물종류', '공급면적', '전용면적', '층', '특이사항', '한글거래가액', '확인매물', '매물방향', '위도', '경도']]
            default_flag = '그외'
        response  = aggrid_interactive_table(df=filter_df)


        if response:
            st.write("선택한 아파트 위치:")
            selected_df = response["selected_rows"]
            if selected_df:
                px.set_mapbox_access_token(token)
                fig = px.scatter_mapbox(selected_df, lat="위도", lon="경도", color="주거형태", size="공급면적", hover_name="단지명", hover_data=["특이사항", "한글거래가액", "시도"],
                                color_continuous_scale=px.colors.cyclical.IceFire, size_max=30, zoom=10, height=500)
                fig.update_layout(
                    title='선택한 아파트 네이버 시세',
                    legend=dict(orientation="h")
                )
                fig.update_layout(mapbox_style="satellite-streets")
                st.plotly_chart(fig, use_container_width=True)

                #folium에 표시에 보자
                # df = pd.DataFrame(selected_df)
                # st.dataframe(df)
                # m = folium.Map(location=[df.iloc[0, -2], df.iloc[0, -1]],  min_zoom=8,max_zoom=16, zoom_start=12, zoom_control=False)
                # for i in range(len(df)):
                #     folium.Marker(
                #         location = [df.iloc[i, -2], df.iloc[i, -1]],
                #         popup = df.iloc[i, 2:4],
                #         icon=folium.Icon(color="red", icon="info-sign")
                #     ).add_to(m)

                # # call to render Folium map in Streamlit
                # st_folium(m)
    with tab2:
        st.dataframe(stat_df)
        stat_df = stat_df.iloc[1:]
        stat_df.iloc[:,1:].replace([np.inf, -np.inf], "0", inplace=True)
        stat_df.iloc[:,0] = stat_df.iloc[:,0].astype(str)
        stat_df.iloc[:,1:] = stat_df.iloc[:,1:].fillna(0).astype(int)
        with st.container():
            col1, col2, col3 = st.columns([30,2,30])
            with col1:
                fig = px.bar(stat_df, y="date", x=["매매", "전세", "월세"], title="전체 매물 중 매매/전세/월세 증감", orientation='h')                
                st.plotly_chart(fig)
            with col2:
                st.write("")
            with col3:
                fig = px.bar(stat_df, y="date", x=["재건축", "재개발", "분양권", "마피", "무피"], title="매매 물건 중 재개발/재건축/분양권 증감", orientation='h')
                st.plotly_chart(fig)
            html_br="""
            <br>
            """
        
        
            
        