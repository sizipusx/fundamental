import streamlit as st
import pandas as pd
import numpy as np
import sqlite3  
import plotly_express as px


def main():
    df = load_data()
    option = st.sidebar.selectbox(
        '지역 선택',
        df.columns[1:]
    )
    '지역은: ', option
    st.title("Data Exploration")
    visualize_data(df, option)


@st.cache
def load_data():
    con = sqlite3.connect("D:/OneDrive - 호매실고등학교/투자/powerbi/data/DB/KB.db")
    df = pd.read_sql("SELECT * FROM KB월간매매지수", con, index_col="날짜")
    df.index = pd.to_datetime(df.index)
    df = df.reset_index()
    return df



def visualize_data(df, localname):
    # create figure using plotly express
    fig = px.line(df, x =df['날짜'],y= df[localname])
    fig.update_xaxes(
    rangeslider_visible=True,
    rangeselector=dict(
        buttons=list([
            dict(count=1, label="1m", step="month", stepmode="backward"),
            dict(count=6, label="6m", step="month", stepmode="backward"),
            dict(count=1, label="YTD", step="year", stepmode="todate"),
            dict(count=3, label="3y", step="year", stepmode="backward"),
            dict(count=5, label="5y", step="year", stepmode="backward"),
            dict(count=10, label="10y", step="year", stepmode="backward"),
            dict(step="all")
        ])
    )
    )
    # # Plot!
    st.plotly_chart(fig)
    

if __name__ == "__main__":
    main()
