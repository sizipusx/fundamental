import pandas as pd
import numpy as np
import time
from datetime import datetime
import FinanceDataReader as fdr
import streamlit as st
import getData

now = datetime.now() +pd.DateOffset(days=-1)
today = '%s-%s-%s' % ( now.year, now.month, now.day)

def CAGR(iterable_df):
    total_year = len(iterable_df.index)-1
    total = (iterable_df.iat[-1]/iterable_df.iat[0])
    cagr = round((total**(1/total_year)-1)*100,2)
    
    return cagr

#overview df를 받아서 RIM, Earning Yeild, Target Price 등을 계산해 다시 리턴
def valuation(df, input_ticker):
    st.dataframe(df)
    valuation_df = pd.DataFrame()
    valuation_df['AnalystTargetPrice'] = df.loc['AnalystTargetPrice']
    valuation_df['Earnings Yield'] = round(1/df.loc['TrailingPE'].astype(float)*100,2)
    # earningY = valuation_df.loc['Earnings Yield'][0]
    # if earningY < 15.0 :
    #     valuation_df.loc['Target Price'] = round(df.loc['DilutedEPSTTM'].astype(float)/0.15,2)
    valuation_df['Price'] = df.loc['Price']
    valuation_df['RIM'] = round(df.loc['BookValue'].astype(float)*(df.loc['ReturnOnEquityTTM'].astype(float)/0.08),2)
    valuation_df['Margin Of Safety'] = round((valuation_df.iloc[0,3]/df.loc['Price'] -1)*100,2)
    st.dataframe(valuation_df)
    # last_value = valuation_df.iloc[-1,0]
    # last_value= str(round(last_value,2)) + '%'
    # valuation_df.iloc[-1,0] = last_value
    value_df = valuation_df.T
    value_df.columns = ['Valuation']

    return value_df