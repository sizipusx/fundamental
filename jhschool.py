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
gsheet_url = r'https://raw.githubusercontent.com/sizipusx/fundamental/a55cf1853a1fc24ff338e7293a0d526fc0520e76/files/weekly-house-db-ac0a43b61ddd.json'

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


def run(g_status, gubun):
  st.dataframe(df)


if __name__ == "__main__":

  g_status = st.sidebar.radio("졸업 유무", ["재학", "졸업"])
  if g_status == '재학':
    gubun = st.sidebar.text_input("학번 6자리(ex:301033)")
  else:
    gubun = st.sidebar.text_input("이름")

  submit = st.sidebar.button('Analysis')

  if submit:
        run(g_status, gubun)
    write_sheet = doc.worksheet('confirm')
    write_sheet.update_acell('B1', 'b1 updated')
    write_sheet.append_row(['new1', 'new2', 'new3', 'new4'])
    write_sheet.insert_row(['new1', 'new2', 'new3', 'new4'], 5)

