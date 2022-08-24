from re import S
import time
from datetime import datetime
import drawAPT_weekly

import numpy as np
import pandas as pd
from pandas.io.formats import style

import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from st_aggrid import AgGrid, GridOptionsBuilder
from st_aggrid.shared import GridUpdateMode

import requests
import json
from pandas.io.json import json_normalize
from urllib.request import urlopen

import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots

import streamlit as st
import FinanceDataReader as fdr

import matplotlib.pyplot as plt
from matplotlib import font_manager, rc
import seaborn as sns

pd.set_option('display.float_format', '{:.2f}'.format)

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
<h2 style="font-size:200%; color:#008080; font-family:Georgia"> 정현고 2023학년도 수시 전형 학교장 추천 지원 확인 <br>
<hr style= "  display: block;
  margin-top: 0.5em;
  margin-bottom: 0.5em;
  margin-left: auto;
  margin-right: auto;
  border-style: inset;
  border-width: 1.5px;"></h1>
"""

st.set_page_config(page_title="정현고등학교 학교장추천 전형 확인", page_icon="", layout="wide")
st.markdown('<style>body{background-color: #fbfff0}</style>',unsafe_allow_html=True)
st.markdown(html_header, unsafe_allow_html=True)
st.markdown(""" <style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style> """, unsafe_allow_html=True)

#gsheet
scope = [
    'https://spreadsheets.google.com/feeds',
    'https://www.googleapis.com/auth/drive',
    ]

json_file_name = './files/school-360306-3aef8e9267cc.json'

credentials = ServiceAccountCredentials.from_json_keyfile_name(json_file_name, scope)
gc = gspread.authorize(credentials)

spreadsheet_url = 'https://docs.google.com/spreadsheets/d/1zzovpuXG1Yzp2KR2XWSZX53_CA5cGPkY50ETkycYOeM/edit?usp=sharing'

doc = gc.open_by_url(spreadsheet_url)

read_sheet = doc.worksheet('read')
m_values = read_sheet.get_all_values()
m_header, m_rows = m_values[0], m_values[1:]
df = pd.DataFrame(m_rows, columns=m_header)
df['학번'] = df['학번'].astype(str)
df['성명'] = df['성명'].astype(str)

def aggrid_interactive_table(df: pd.DataFrame):
    """Creates an st-aggrid interactive table based on a dataframe.

    Args:
        df (pd.DataFrame]): Source dataframe

    Returns:
        dict: The selected row
    """
    df = df.reset_index()
    #gb = GridOptionsBuilder.from_dataframe(df)
    
    gb = GridOptionsBuilder.from_dataframe(
        df, enableRowGroup=True, enableValue=True, enablePivot=True
    )
    gb.configure_pagination()
    gb.configure_side_bar()
    gb.configure_selection("single")
    response  = AgGrid(
        df,
        editable=True,
        enable_enterprise_modules=True,
        gridOptions=gb.build(),
        data_return_mode="filtered_and_sorted",
        width='100%',
        update_mode="no_update",
        fit_columns_on_grid_load=False, #GridUpdateMode.MODEL_CHANGED,
        theme="streamlit",
        allow_unsafe_jscode=True
    )

    return response

def run(g_status, gubun):
  if g_status == '재학':
    slice_df = df[df['학번'] == gubun ]
  else:
    slice_df = df[df['성명'] == gubun ]
  
  #add aggrid table
  #response  = aggrid_interactive_table(df=slice_df)
  st.table(slice_df)
  # st.dataframe(slice_df)

  st.subheader("지원한 모든 정보가 모두 맞습니까?")
  write_sheet = doc.worksheet('confirm')
  # Define initial state.
  if "todos" not in st.session_state:
      st.session_state.todos = [
          {"description": "Play some Tic Tac Toe", "done": True},
          {
              "description": "Read the [blog post about session state](https://blog.streamlit.io/session-state-for-streamlit/)",
              "done": False,
          },
      ]

  def new_todo_changed():
        if st.session_state.new_todo:
            st.session_state.todos.append(
                {
                    "description": st.session_state.new_todo,
                    "done": False,
                }
            )

  # check_this = st.radio("체크", ('','이상 없음', '이상 있음'), index=0)
  # chess = st.button("확인")

  # if chess is True and check_this == '이상 없음':
  #   write_sheet.append_row([gubun, '이상 없음'])
  #   st.subheader("확인이 완료 되었습니다!!")
  # elif chess is True and check_this == '이상 있음':
  #   write_sheet.append_row([gubun, '이상 있음'])
  #   st.subheader("이상이 있는 경우 담임선생님께 말씀 드리거나 담당선생님(윤대영T)께 말씀 드립니다.")
  # else:
  #   st.empty()

  # col1, col2 = st.columns([1,1])

  # with col1:
  #   ok_st = st.checkbox("네, 모두 맞습니다.")
  #   if ok_st:
  #     st.write("확인 완료")
  #     write_sheet.append_row([gubun, '이상 없음'])
  #     st.subheader("확인이 완료 되었습니다!!")
  #   else:
  #     st.write("확인 완료 에러")

  # with col2:
  #   not_st = st.checkbox("아니요, 이상이 있습니다.")
  #   if not_st:
  #     write_sheet.append_row([gubun, '이상 있음'])
  #     st.subheader("이상이 있는 경우 담임선생님께 말씀 드리거나 담당선생님(윤대영T)께 말씀 드립니다.")
  #   else:
  #     st.write("이상 있음 에러")
  # Show widgets to add new TODO.
  def insert_info():
    write_sheet.append_row([gubun, "학인 완료"])

  st.write(
        "<style>.main * div.row-widget.stRadio > div{flex-direction:row;}</style>",
        unsafe_allow_html=True,
    )
  st.text_input("이상 있음 혹은 이상 없음", on_change=insert_info, key="new_todo")
  yes_yes = st.button("확인", on_click=insert_info)

  
  

  def write_todo_list(todos):
    "Display the todo list (mostly layout stuff, no state)."
    st.write("")
    all_done = True
    for i, todo in enumerate(todos):
        col1, col2, _ = st.beta_columns([0.05, 0.8, 0.15])
        done = col1.checkbox("", todo["done"], key=str(i))
        if done:
            format_str = (
                '<span style="color: grey; text-decoration: line-through;">{}</span>'
            )
        else:
            format_str = "{}"
            all_done = False
        col2.markdown(
            format_str.format(todo["description"]),
            unsafe_allow_html=True,
        )

  # if yes_yes:
  #   write_sheet.append_row([gubun, "확인 완료"])
  write_sheet.append_row([gubun, "학인 완료"])
  st.subheader("이상이 있는 경우 담임선생님께 말씀 드리거나 담당선생님(윤대영T)께 말씀 드립니다.")




  # if ok_st:
  #   #write_sheet.update_acell('B1', '이사없음')
  #   write_sheet.append_row([gubun, '이상 없음'])
  #   st.subheader("확인이 완료 되었습니다!!")
  #   #write_sheet.insert_row(['new1', 'new2', 'new3', 'new4'], 5)
  # elif not_st:
  #   write_sheet.append_row([gubun, '이상 있음'])
  #   st.subheader("이상이 있는 경우 담임선생님께 말씀 드리거나 담당선생님(윤대영T)께 말씀 드립니다.")






if __name__ == "__main__":

  g_status = st.sidebar.radio("졸업 유무", ["재학", "졸업"])
  if g_status == '재학':
    gubun = st.sidebar.text_input("학번 5자리(ex:30135)")
    if len(gubun) > 0:
      if len(gubun) != 5 :
        st.error("정확한 학번을 입력하세요")
    else:
      st.error("학번을 입력하세요!")
  else:
    gubun = st.sidebar.text_input("이름")
    if len(gubun) == 0:
      st.error("이름을 입력하세요!")

  submit = st.sidebar.button('지원 확인')

  if submit:
        run(g_status, gubun)
   

