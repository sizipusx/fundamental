import pandas as pd
import numpy as np
import time
from datetime import datetime
from alpha_vantage.fundamentaldata import FundamentalData 
import FinanceDataReader as fdr
import requests
import json
from pandas.io.json import json_normalize
import streamlit as st
import makeData
import requests
import bs4

# key='XA7Y92OE6LDOTLLE'
key='CBALDIGECB3UFF5R'
fd = FundamentalData(key, output_format='pandas')
now = datetime.now() +pd.DateOffset(days=-5)
today = '%s-%s-%s' % ( now.year, now.month, now.day)

@st.cache
def load_data():
    # 나스닥거래소 상장종목 전체
    df_q= fdr.StockListing('NASDAQ')
    # NewYork 증권거래소 상장종목 전체
    df_n= fdr.StockListing('NYSE')
    # American 증권거래소 상장종목 전체
    df_a= fdr.StockListing('AMEX')
    # 각 거래소 이름 추가
    df_q.iloc[:,-1] = "NASDAQ"
    df_n.iloc[:,-1] = "NYSE"
    df_a.iloc[:,-1] = "AMEX"
    #세 데이터 모두 합치자
    ticker_list = df_q.append(df_n).append(df_a)

    return ticker_list

def get_close_data(ticker, from_date, to_date):
    close_price = fdr.DataReader(ticker, from_date, to_date)

    return close_price

def get_annual_fundamental_data(ticker) :
    income_df, meta_data = fd.get_income_statement_annual(symbol=ticker)
    balance_df, meta_data = fd.get_balance_sheet_annual(symbol=ticker)
    cashflow_df, meta_data = fd.get_cash_flow_annual(symbol=ticker)
    #index 변경
    income_df.set_index('fiscalDateEnding', inplace=True)
    income_df.index =  pd.to_datetime(income_df.index, format='%Y-%m-%d')
    balance_df.set_index('fiscalDateEnding', inplace=True)
    balance_df.index =  pd.to_datetime(balance_df.index, format='%Y-%m-%d')
    cashflow_df.set_index('fiscalDateEnding', inplace=True)
    cashflow_df.index =  pd.to_datetime(cashflow_df.index, format='%Y-%m-%d')

    return income_df, balance_df, cashflow_df


def get_quarterly_fundamental_data(ticker):
    income_q, meta_data = fd.get_income_statement_quarterly(symbol=ticker)
    balance_q, meta_data = fd.get_balance_sheet_quarterly(symbol=ticker)
    cashflow_q, meta_data = fd.get_cash_flow_quarterly(symbol=ticker)
    #index 변경
    income_q.set_index('fiscalDateEnding', inplace=True)
    income_q.index =  pd.to_datetime(income_q.index, format='%Y-%m-%d')
    balance_q.set_index('fiscalDateEnding', inplace=True)
    balance_q.index =  pd.to_datetime(balance_q.index, format='%Y-%m-%d')
    cashflow_q.set_index('fiscalDateEnding', inplace=True)
    cashflow_q.index =  pd.to_datetime(cashflow_q.index, format='%Y-%m-%d')

    return income_q, balance_q, cashflow_q

def get_company_overview(ticker):
    overview_df, meta_data = fd.get_company_overview(symbol=ticker)
    overview_df = overview_df.T
    overview_df.columns = ['OverView']

    return overview_df

def get_fundamental_data_by_Json(ticker, func):
    API_URL = "https://www.alphavantage.co/query" 
    choice1 = "quarterlyReports" #annualReports : quarterlyReports 둘다 5년치 데이터
    choice2 = "annualReports"
    data = { 
        "function": func, 
        "symbol": ticker,
        "outputsize" : "compact",
        "datatype": "json", 
        "apikey": key} 
    response = requests.get(API_URL, data) 
    response_json = response.json() # maybe redundant
    df = pd.DataFrame()
    adf = pd.DataFrame()

    if func == 'TIME_SERIES_DAILY' :
        df = pd.DataFrame.from_dict(response_json['Time Series (Daily)'], orient= 'index')
        df.index =  pd.to_datetime(df.index, format='%Y-%m-%d')
        df = df.rename(columns={ '1. open': 'Open', '2. high': 'High', '3. low': 'Low', '4. close': 'Close', '5. volume': 'Volume'})
        df = df.astype({'Open': 'float64', 'High': 'float64', 'Low': 'float64','Close': 'float64','Volume': 'float64',})
        df = df[[ 'Open', 'High', 'Low', 'Close', 'Volume']]
    elif func == 'INCOME_STATEMENT':
        df = pd.DataFrame(response_json[choice1])
        df = df.iloc[::-1]
        df.set_index('fiscalDateEnding', inplace=True)
        df.index = pd.to_datetime(df.index, format='%Y-%m-%d')
        sub = ['totalRevenue', 'costOfRevenue', 'grossProfit', 'operatingExpenses', 'operatingIncome', 'ebit', 'netIncome']
        df = df[sub].replace('None','0').astype(float).round(0)
        df['GPM'] = round(df['grossProfit'] / df['totalRevenue']*100, 2)
        df['OPM'] = round(df['operatingIncome'] / df['totalRevenue']*100, 2)
        df['NPM'] = round(df['netIncome'] / df['totalRevenue']*100,2)

        df['TR Change'] = round(df['totalRevenue'].pct_change()*100, 2)
        df['OI Change'] = round(df['operatingIncome'].pct_change()*100, 2)
        df['NI Change'] = round(df['netIncome'].pct_change()*100, 2)
        #annual
        adf = pd.DataFrame(response_json[choice2])
        adf = adf.iloc[::-1]
        adf.set_index('fiscalDateEnding', inplace=True)
        adf.index = pd.to_datetime(adf.index, format='%Y-%m-%d')
        # print(df)
    elif func == 'BALANCE_SHEET':
        balance = pd.DataFrame(response_json[choice1])
        balance = balance.iloc[::-1]
        balance.set_index('fiscalDateEnding', inplace=True)
        balance.index = pd.to_datetime(balance.index, format='%Y-%m-%d')
        sub = ['totalAssets', 'intangibleAssets', 'totalLiabilities', 'totalShareholderEquity', 'retainedEarnings', 'totalCurrentLiabilities', \
         'totalCurrentAssets', 'propertyPlantEquipment', 'currentNetReceivables', 'inventory', 'currentAccountsPayable', 'accumulatedDepreciationAmortizationPPE', \
         'totalNonCurrentAssets', 'cashAndShortTermInvestments', 'commonStockSharesOutstanding']
        df = balance[sub].replace('None','0').astype(float).round(0)
        #부채비율
        df['Debt/Equity'] = round(df['totalLiabilities'] / df['totalShareholderEquity']*100, 2)
        #유동비율
        df['CurrentRatio'] = round(df['totalCurrentAssets'] / df['totalCurrentLiabilities']*100, 2)
        #당좌비율(당좌자산(유동자산-재고자산)/유동부채)
        df['QuickRatio'] = round((df['totalCurrentAssets'] - df['inventory'])/ df['totalCurrentLiabilities']*100, 2)
        #유동부채비율
        df['유동부채/자기자본'] = round(df['totalCurrentLiabilities'] / df['totalShareholderEquity']*100, 2)
        #무형자산총자산비율 15%미만
        df['무형자산비율'] = round(df['intangibleAssets'] / df['totalAssets']*100, 2)
        #현금자산비율
        df['현금성자산비율'] = round(df['cashAndShortTermInvestments'] / df['totalAssets']*100, 2)
    
        #annual data
        adf = pd.DataFrame(response_json[choice2])
        adf = adf.iloc[::-1]
        adf.set_index('fiscalDateEnding', inplace=True)
        adf.index = pd.to_datetime(adf.index, format='%Y-%m-%d')
    elif func == 'CASH_FLOW':
        cashflow_df = pd.DataFrame(response_json[choice1])
        cashflow_df = cashflow_df.iloc[::-1]
        cashflow_df.set_index('fiscalDateEnding', inplace=True)
        cashflow_df.index = pd.to_datetime(cashflow_df.index, format='%Y-%m-%d')
        #cash-flow 
        sub = ['netIncome', 'operatingCashflow', 'cashflowFromInvestment', 'cashflowFromFinancing', 'depreciationDepletionAndAmortization', 'dividendPayout', \
            'paymentsForRepurchaseOfCommonStock', 'capitalExpenditures', 'changeInCashAndCashEquivalents']
        df = cashflow_df[sub].replace('None','0').astype(float).round(0)
        df["FCF"] = round(df['operatingCashflow'] - df['capitalExpenditures'], 2)
         #annual data
        adf = pd.DataFrame(response_json[choice2])
        adf = adf.iloc[::-1]
        adf.set_index('fiscalDateEnding', inplace=True)
        adf.index = pd.to_datetime(adf.index, format='%Y-%m-%d')
        adf["FCF"] = adf['operatingCashflow'].astype(float) - adf['capitalExpenditures'].astype(float)
    elif func == 'EARNINGS':
        df = pd.DataFrame(response_json['quarterlyEarnings'])
        df = df.iloc[::-1]
        df.set_index('fiscalDateEnding', inplace=True)
        df.index =  pd.to_datetime(df.index, format='%Y-%m-%d')
        df['reportedEPS'] = df['reportedEPS'].replace('None','0').astype(float).round(3)
        df['ttmEPS'] = round(df['reportedEPS'].astype(float).rolling(4).sum(),2)
        df['EPS_YoY'] = round(df['ttmEPS'].pct_change(5)*100,2)
        df['EPS_5y'] = round(df['ttmEPS'].pct_change(21)*100,2)
        df['EPS_10y'] = round(df['ttmEPS'].pct_change(41)*100,2)
        df['estimatedEPS'] = df['estimatedEPS'].replace('None','0').astype(float).round(4)
        df['surprise'] = df['surprise'].replace('None','0').astype(float).round(4)
        df['surprisePercentage'] = df['surprisePercentage'].replace('None','0').astype(float).round(2)
        #년간 데이터
        adf = pd.DataFrame(response_json['annualEarnings'])
        adf = adf.iloc[::-1]
        adf.set_index('fiscalDateEnding', inplace=True)
        adf.index =  pd.to_datetime(adf.index, format='%Y-%m-%d')
        adf['reportedEPS'] = adf['reportedEPS'].replace('None','0').astype(float).round(3)
        adf['EPS_YoY'] = round(adf['reportedEPS'].pct_change()*100,2)       

    return df, adf

def get_overview(ticker):
    API_URL = "https://www.alphavantage.co/query" 
    data = { 
        "function": "OVERVIEW", 
        "symbol": ticker,
        "outputsize" : "compact",
        "datatype": "json", 
        "apikey": key} 
    response = requests.get(API_URL, data) 
    response_json = response.json() # maybe redundant
    df = pd.DataFrame()

    df = pd.json_normalize(response_json)
    description_data = ['MarketCapitalization', 'Symbol', 'AssetType', 'Name', 'Description', 'Exchange', 'Currency', 'Country', 'Sector', \
                        'Industry', 'Address', 'FullTimeEmployees', 'FiscalYearEnd', 'LatestQuarter', 'LastSplitFactor', 'LastSplitDate']
    profit_data = ['RevenueTTM', 'RevenuePerShareTTM', 'ProfitMargin','GrossProfitTTM', 'OperatingMarginTTM', 'EBITDA', \
                    'QuarterlyEarningsGrowthYOY', 'QuarterlyRevenueGrowthYOY']
    dividend_data = ['DividendPerShare', 'DividendYield', 'PayoutRatio', \
                        'ForwardAnnualDividendRate', 'ForwardAnnualDividendYield', 'DividendDate', 'ExDividendDate']
    ratio_data = ['EPS','DilutedEPSTTM', 'PERatio', 'TrailingPE', 'ForwardPE', \
                    'BookValue', 'PriceToBookRatio','PEGRatio', 'EVToRevenue', 'EVToEBITDA','PriceToSalesRatioTTM']
    return_data = ['ReturnOnEquityTTM', 'ReturnOnAssetsTTM']
    price_data = ['Beta', '52WeekHigh', '52WeekLow', '50DayMovingAverage', '200DayMovingAverage']
    volume_data = ['SharesOutstanding', 'SharesFloat', 'SharesShort', 'SharesShortPriorMonth', 'ShortRatio', 'ShortPercentOutstanding', \
                    'ShortPercentFloat', 'PercentInsiders', 'PercentInstitutions']
    valuation_data = ['AnalystTargetPrice']

    description_df = df[description_data].T
    description_df.columns = ['Description']
    change_cap = format(round(float(description_df.loc['MarketCapitalization','Description']) / 1000000,2),',')
    description_df.loc['MarketCapitalization'] = str(change_cap) + "M"
    ratio_df = df[ratio_data].T
    ratio_df.columns = ['Ratio']
    #PERR, PBRR 추가 해보자
    ratio_df.loc['PERR'] = round(float(df.loc[0, 'TrailingPE'])/(float(df.loc[0, 'ReturnOnEquityTTM'])*100),2)
    ratio_df.loc['PBRR'] = round(float(df.loc[0, 'PriceToBookRatio'])/(float(df.loc[0, 'ReturnOnEquityTTM'])*100/10),2)
    return_df = df[return_data].T.astype(float)*100
    return_df = return_df.round(2).astype(str) + "%"
    return_df.columns = ['Return']
    profit_df = df[profit_data].T
    profit_df.columns = ['Profitability']
    dividend_df = df[dividend_data].T
    dividend_df.columns = ['Dividend']
    volume_df = df[volume_data].T
    volume_df.columns = ['Volume']
    price_df = df[price_data].T
    price_df.columns = ['Price']

    #최근 종목 close 값
    now = datetime.now() 
    before = datetime.now() +pd.DateOffset(days=-5)
    last_week = '%s-%s-%s' % ( before.year, before.month, before.day)
    today = '%s-%s-%s' % ( now.year, now.month, now.day)
    last_price = get_close_data(ticker, last_week, today)
    latest_price = last_price.iloc[-1,0]
    df['Price'] = latest_price
    valuation_df = makeData.valuation(df.T, ticker)
    
    return description_df, ratio_df, return_df, profit_df, dividend_df, volume_df, price_df, valuation_df

    
def get_kor_itooza(code):
    i_url = 'http://search.itooza.com/index.htm?seName='+ code
    fs_page = requests.get(i_url)
    fs_tables = pd.read_html(fs_page.text)

    #현재 밸류에이션
    cur = fs_tables[0]

    #5년 평균
    avg = fs_tables[1]

    #ttm 
    ttm = fs_tables[2].T
    ttm.columns = ['EPS', 'EPS(개별)', 'PER', 'BPS', 'PBR', 'DPS', 'DY', 'ROE', 'NPM', 'OPM', 'Price']
    ttm = ttm.iloc[1:]
    ttm = ttm.iloc[::-1]
    ttm = ttm.reset_index()
    ttm['index'] = ttm['index'].str.slice(0,5)

    ttm['index'] = ttm['index'].map(lambda x: "20" + x +".01")
    ttm.set_index('index', inplace=True)
    ttm.index =  pd.to_datetime(ttm.index, format='%Y-%m-%d')
    ttm = ttm.astype(float).fillna(0).round(decimals=2)

    #10년 annual data 
    ann = fs_tables[3].T
    ann.columns = ['EPS', 'EPS(개별)', 'PER', 'BPS', 'PBR', 'DPS', 'DY', 'ROE', 'NPM', 'OPM', 'Price']
    ann = ann.iloc[1:]
    ann = ann.iloc[::-1]
    ann = ann.reset_index()
    ann['index'] = ann['index'].str.slice(0,5)

    ann['index'] = ann['index'].map(lambda x: "20" + x +".01")
    ann.set_index('index', inplace=True)
    ann.index =  pd.to_datetime(ann.index, format='%Y-%m-%d')
    ann = ann.astype(float).fillna(0).round(decimals=2)

    #RIM Price
    rim_price, r_ratio = makeData.kor_rim(ttm)
    #기업의 최근 price
    price = fdr.DataReader(code, today).iloc[-1,0]

    #Make valuation dataframe
    roe = ttm.iloc[-1,7]
    cur_per = cur.iloc[0,0]
    value_list = []
    index_list = ['Close', 'RIM', 'PER', 'PBR', 'ROE','PER5', 'PBR5', 'PEG5', 'PERR', 'PBRR']
    value_list.append(price)
    value_list.append(rim_price)
    if cur_per == "(-)":
        cur_per = 0
    value_list.append(cur_per)
    value_list.append(cur.iloc[0,1])
    value_list.append(roe)
    value_list.append(avg.iloc[0,0])
    value_list.append(avg.iloc[0,1])
    if type(avg.iloc[0,3]) is str :
        if avg.iloc[0,3] == "N/A":
            value_list.append(0)
        value_list.append(round(avg.iloc[0,0]/float(avg.iloc[0,3].replace("%","")),2))
    else:
        value_list.append(0)
    value_list.append(round(avg.iloc[0,0]/roe,2))
    value_list.append(round(avg.iloc[0,1]/(roe*1/10),2))

    data = {'Valuation': value_list}
    valuation_df = pd.DataFrame(index=index_list, data=data) 
    valuation_df = valuation_df.round(decimals=2)

    return valuation_df, ttm, ann 

def get_naver_finance(code):
    n_url = 'https://finance.naver.com/item/main.nhn?code=' + code
    fs_page = requests.get(n_url)
    navers = pd.read_html(fs_page.text)

    total_df = navers[3]
    total_df.set_index([(  '주요재무정보',     '주요재무정보', '주요재무정보')], inplace=True)
    total_df.index.name = '항목'

    #년간만 가져오기
    a_df = total_df.iloc[:,:4]
    a_df.columns = a_df.columns.get_level_values(1)
    a_df.columns = a_df.columns.map(lambda x: x[:7]+'.30')
    ann_df = a_df.T
    ann_df.index = pd.to_datetime(ann_df.index, format='%Y-%m-%d')
    ann_df.fillna(0, inplace=True)
    
    #분기만 가져오기
    q_df = total_df.iloc[:,4:]
    q_df.columns = q_df.columns.get_level_values(1)
    q_df.columns = q_df.columns.map(lambda x: x[:7]+'.30')
    f_df = q_df.T
    f_df.index = pd.to_datetime(f_df.index, format='%Y-%m-%d')
    f_df.fillna(0, inplace=True)

    return ann_df, f_df

