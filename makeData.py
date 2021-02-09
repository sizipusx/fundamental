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
    total = (iterable_df.iat[-1,0]/iterable_df.iat[0,0])
    cagr = round((total**(1/total_year)-1)*100,2)
    
    return cagr

#overview df를 받아서 RIM, Earning Yeild, Target Price 등을 계산해 다시 리턴
def valuation(df, input_ticker):   
    value_list = []
    index_list = ['Price', 'AnalystTargetPrice', 'TrailingPE','Earnings Yield', 'RIM', 'Margin Of Safety']
    value_list.append(df.loc['Price',0])
    value_list.append(df.loc['AnalystTargetPrice',0])
    value_list.append(round(float(df.loc['TrailingPE',0]),2))
    value_list.append(str(round(1/float(df.loc['TrailingPE',0])*100,2))+"%")
    ##할인률 12%
    value_list.append(round(float(df.loc['BookValue',0])*(float(df.loc['ReturnOnEquityTTM', 0])/0.12),2))
    value_list.append(str(round((value_list[4]/value_list[0] -1)*100,2))+"%")

    data = {'Valuation': value_list}
    valuation_df = pd.DataFrame(index=index_list, data=data)  

    return valuation_df

def make_growthRatio(year_earning, year_income, year_cash, year_balance):
    st.dataframe(year_earning)
    growth_index = ['EPS '+ str(len(year_earning.index)-1)+'Y', 'EPS 1Y', 'EPS 5Y', 'EPS 10Y', \
                    'revenue', 'ebit', 'operatingIncome','netIncome', 'FCF', 'totalShareholderEquity']
    growth_data = []
    growth_data.append(round(CAGR(year_earning),2))
    growth_data.append(round(year_earning.iloc[-1,1],2)) #1 year eps growth
    growth_data.append(round(CAGR(year_earning.iloc[-6:]),2)) #5 year eps growth
    growth_data.append(round(CAGR(year_earning.iloc[-11:]),2)) #10 year eps growth
    growth_data.append(round(CAGR(year_income['totalRevenue'].astype(float).to_frame()),2))
    growth_data.append(round(CAGR(year_income['ebit'].astype(float).to_frame()),2))
    growth_data.append(round(CAGR(year_income['operatingIncome'].astype(float).to_frame()),2))
    growth_data.append(round(CAGR(year_income['netIncome'].astype(float).to_frame()),2))
    growth_data.append(round(CAGR(year_cash['FCF'].to_frame()),2))
    growth_data.append(round(CAGR(year_balance['totalShareholderEquity'].astype(float).to_frame()),2))

    data = {'Growth Rate 5y': growth_data}
    growth_df = pd.DataFrame(index=growth_index, data=data)  

    return growth_df
    
