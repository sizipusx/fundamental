import pandas as pd
import numpy as np
import time
from datetime import datetime
import FinanceDataReader as fdr
import streamlit as st
import getData
import requests

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

def make_growthRatio(year_earning, q_earning, year_income, year_cash, year_balance):
    growth_index = ['EPS '+ str(len(year_earning.index)-1)+'Y', 'EPS 1Y', 'EPS 5Y', 'EPS 10Y', \
                    'revenue', 'ebit', 'operatingIncome','netIncome', 'FCF', 'totalShareholderEquity']
    growth_data = []
    growth_data.append(round(CAGR(year_earning),2))
    growth_data.append(round(year_earning.iloc[-1,1],2)) #1 year eps growth
    growth_data.append(round(CAGR(year_earning.iloc[-6:]),2)) #5 year eps growth
    growth_data.append(round(CAGR(year_earning.iloc[-11:]),2)) #10 year eps growth
    growth_data.append(round(CAGR(year_income['totalRevenue'].replace('None','0').astype(float).to_frame()),2))
    growth_data.append(round(CAGR(year_income['ebit'].replace('None','0').astype(float).to_frame()),2))
    growth_data.append(round(CAGR(year_income['operatingIncome'].replace('None','0').astype(float).to_frame()),2))
    growth_data.append(round(CAGR(year_income['netIncome'].replace('None','0').astype(float).to_frame()),2))
    growth_data.append(round(CAGR(year_cash['FCF'].replace('None','0').to_frame()),2))
    growth_data.append(round(CAGR(year_balance['totalShareholderEquity'].replace('None','0').astype(float).to_frame()),2))

    ttm_data = []
    ttm_data.append(round(CAGR(q_earning.iloc[:,5].to_frame()),2))
    ttm_data.append(round(CAGR(q_earning.iloc[-5:,5].to_frame()),2))
    ttm_data.append(round(CAGR(q_earning.iloc[-21:,5].to_frame()),2))
    ttm_data.append(round(CAGR(q_earning.iloc[-41:,5].to_frame()),2))
    ttm_data.append(round(q_earning.iloc[-1,6],2))
    ttm_data.append(round((1+q_earning.iloc[-1,7]/100)**(1/5)-1,2))
    ttm_data.append(round((1+q_earning.iloc[-1,8]/100)**(1/10)-1,2))
    ttm_data.append(0)
    ttm_data.append(0)
    ttm_data.append(0)
    data = {'Annual Growth 5Y': growth_data, 'ttm Growth': ttm_data}
    growth_df = pd.DataFrame(index=growth_index, data=data)  

    return growth_df

def kor_rim(ttm_df):
    #BBB- 5년물 회사채 수익률 
    in_url = 'https://www.kisrating.com/ratingsStatistics/statics_spread.do'
    in_page = requests.get(in_url)
    in_tables = pd.read_html(in_page.text)
    yeild = in_tables[0].iloc[-1,-1]
    #rim = (BPS * ROE/ r) or (EPS / r)
    rim_price = round(ttm_df.iloc[-1,3]*ttm_df.iloc[-1,7] / yeild,2)
    return rim_price, yeild