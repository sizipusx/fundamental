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
                        'Industry', 'Address', 'FullTimeEmployees', 'FiscalYearEnd', 'LatestQuarter']
    profit_data = ['RevenueTTM', 'RevenuePerShareTTM', 'ProfitMargin','GrossProfitTTM', 'OperatingMarginTTM', 'EBITDA', \
                    'QuarterlyEarningsGrowthYOY', 'QuarterlyRevenueGrowthYOY']
    dividend_data = ['DividendPerShare', 'DividendYield', 'PayoutRatio', \
                        'ForwardAnnualDividendRate', 'ForwardAnnualDividendYield', 'DividendDate', 'ExDividendDate']
    ratio_data = ['EPS','DilutedEPSTTM', 'PERatio', 'TrailingPE', 'ForwardPE', \
                    'BookValue', 'PriceToBookRatio','PEGRatio', 'EVToRevenue', 'EVToEBITDA','PriceToSalesRatioTTM']
    return_data = ['ReturnOnEquityTTM', 'ReturnOnAssetsTTM']
    price_data = ['Beta', '52WeekHigh', '52WeekLow', '50DayMovingAverage', '200DayMovingAverage']
    volume_data = ['SharesOutstanding', 'SharesFloat', 'SharesShort', 'SharesShortPriorMonth']
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
    volume_df = volume_df.astype(float).fillna(0)
    volume_df.update(volume_df.select_dtypes(include=np.number).applymap('{:,}'.format))
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
    # a_df.columns = a_df.columns.map(lambda x: x[:7]+'.30')
    ann_df = a_df.T
    # ann_df.index = pd.to_datetime(ann_df.index, format='%Y.%m')
    ann_df.fillna(0, inplace=True)
    
    #분기만 가져오기
    q_df = total_df.iloc[:,4:]
    q_df.columns = q_df.columns.get_level_values(1)
    # q_df.columns = q_df.columns.map(lambda x: x[:7]+'.30')
    f_df = q_df.T
    # f_df.index = pd.to_datetime(f_df.index, format='%Y.%m')
    f_df.fillna(0, inplace=True)
    f_df = f_df.round(decimals=2)

    return ann_df, f_df

#함수화 해보자
from datetime import date

today = date.today()

def make_Valuation(firm_code, firm_name, bond_y):
  fs_url = 'https://comp.fnguide.com/SVO2/asp/SVD_Main.asp?pGB=1&cID=&MenuYn=Y&ReportGB=&NewMenuID=101&stkGb=701&gicode=A' + firm_code
  fs_page = requests.get(fs_url)
  fs_tables = pd.read_html(fs_page.text)

  datalist = []

  #종목명/종목코드
  datalist.append(str(firm_code))
  datalist.append(str(firm_name))
  #평가일
  #now = datetime.now()
  #datalist.append(f"{now.year}-{now.month}-{now.day}")
  datalist.append(today.isoformat())
  #평가일 현재 주가(종가)
  close_price = fdr.DataReader(firm_code).iloc[-1,3]
  # close_price = fs_tables[0].loc[0,1]
  # close_price = int(close_price.split('/')[0].replace(",",""))
  datalist.append('{0:,}'.format(close_price)+"원")
  #BPS : 상수 최근 분기 또는 전년 말 확정치
  # 연결이나 별도냐에 따라 달라짐
  tempdf = fs_tables[10].xs('Annual', axis=1)
  qu_df = fs_tables[12].xs("Net Quarter", axis=1)

  #연결 일때
  if  np.isnan(fs_tables[12].iloc[19,5]) == False: 
    #bps = float(fs_tables[12].iloc[19,5]) #2021.11.18 수정
    #분기 5개 평균으로 바꿔볼까?
    bps_value = qu_df.iloc[19,1:5] #22.11.29 EPS [17,] => [18,] 변경
    list4 = [float(x) for x in bps_value.values]
    bps = sum(list4)/4 #이전 4분기 BPS 평균
    # print(f"연결이고 BPS가 있을 때  = {BPS}")
  else:
    #연결이면서 4분기 평균으로
    bps_value = fs_tables[15].iloc[15,2:6]
    list4 = [float(x) for x in bps_value.values]
    bps = sum(list4)/4 #이전 분기 BPS 평균
    #bps = float(fs_tables[15].iloc[15,5]) #2021.11.30 수정
    # print(f"연결이 아니고 BPS가 있을 때  = {BPS}")
  datalist.append('{0:,}'.format(bps)+"원")
  #===================EPS: 변수 애널리스트 예측치 또는 최근 4분기 합계==========
  if  np.isnan(tempdf.iloc[18,3]) == False: #22.11.29 EPS [17,3] => [18,3] 변경
    eps = float(tempdf.iloc[18,3])
    # print(f"연결이고 추정 EPS가 있을 때  = {eps}")
  else:
    eps_value = qu_df.iloc[18,1:5] #22.11.29 EPS [17,] => [18,] 변경
    list4 = [float(x) for x in eps_value.values]
    eps = sum(list4) #이전 분기 EPS 합산
    # print(f"연결이지만 추정 EPS가 없을 때  = {eps}")
    #연결이 없어 별도로 감
    tempdf1 = fs_tables[13].xs('Annual', axis=1)
    if np.isnan(eps):
      #print(f"별도 np.isnan  true/false= {np.isnan(eps)}")
      if  np.isnan(tempdf1.iloc[14,3]) == False: #22.11.29 EPS [13,3] => [14,3] 변경
        eps = float(tempdf1.iloc[14,3])
        # print(f"별도이지만 추정 EPS가 있을 때  = {eps}")
      else:
        qu_df1 = fs_tables[15].xs("Net Quarter", axis=1)
        eps_value1 = qu_df1.iloc[14,1:5] #22.11.29 EPS [13,] => [14,] 변경
        list5 = [float(x) for x in eps_value1.values]
        eps = int(sum(list5))
        # print(f"별도이지만 추정 EPS가 없을 때  = {eps}") 
 
  datalist.append('{0:,}'.format(eps)+"원")

  # print("step 1. EPS END ==========================")
  #DPS : 준상수 최근 3년치 평균 또는 전년도 주당 배당금액
  if np.isnan(tempdf.iloc[20,2]):
    dps = 0
  else:
    dps = float(tempdf.iloc[20,2])
  datalist.append('{0:,}'.format(dps)+"원") 
  # print("step 2. DPS END ==========================")
  #ROE
  #직접 계산
  roe = round(eps/bps*100,1)
  datalist.append(str(roe)+"%")
  # print("step 3. ROE cal END ==========================")
  #요구수익률: 수정해야함: 하드코딩 7, 7.5, 8, 8.5, 9 => 2021-11-28 크롤링 수정
  # 기대수익률 
  rr = bond_y
  datalist.append(str(rr)+"%")
  # print("step 4. bond_y END ==========================")
  #배당수익률
  did = round(dps/close_price*100,1)
  datalist.append(str(did)+"%")
  # print("step 5. DIDIEND Y END ==========================")
  #시가수익률
  current = round(eps/close_price*100,1)
  datalist.append(str(current)+"%")
  # print("step 6.시가수익률 END ==========================")
  #할인률
  if did < 1 :  r = rr
  elif did < 2 : r = rr - 0.4
  elif did < 3 : r = rr-0.4
  elif did < 4 : r = rr-0.6
  elif did < 5 : r = rr-0.8
  else :  r= rr-1
  datalist.append(r)
  # print("step 7.요구수익률 할인 END ==========================")
  #ROE/r
  roe_r = roe/r
  datalist.append(round(roe_r,2))
  # print("step 8. ROE/r END ==========================")

  #적정주가
  want_price = int(round(bps*roe_r,-1))
  datalist.append('{0:,}'.format(want_price)+"원")
  # print("step 9. 적정주가 END ==========================")
  #패러티
  pa = round(close_price/want_price*100,2)
  datalist.append(str(pa)+"%")
  # print("step 10. 패러티 END ==========================")
  #기대수익률
  expect = round((want_price/close_price - 1)*100,2)
  datalist.append(str(expect)+"%")
  # print("step 11. 기대수익률 END ==========================")
  #컨센서스
  if fs_tables[7].loc[0,'목표주가'] == "관련 데이터가 없습니다.":
    datalist.append(0)
  else:
    datalist.append('{0:,}'.format(fs_tables[7].loc[0,'목표주가'])+"원")
  # print("step 12.목표주가 END ==========================")
  #컨센서스 기관수
  if fs_tables[7].loc[0,'추정기관수'] == "관련 데이터가 없습니다.":
    datalist.append(0)
  else:
    datalist.append(fs_tables[7].loc[0,'추정기관수'])
  # print("step 13. 추정기관수 END ==========================")
  #5년 PER
  avdf = fs_tables[11].xs("Annual", axis=1)
  per5 = avdf.iloc[21,:5] #22.11.29 EPS [20,] => [21,] 변경
  if per5.isnull().sum() > 0 :
    #per5_value = 0
    #2019.10.25. 추가 코드: 5개년 중 있는 년의 per 평균 낸다!!
    #5개년 per 값이 없는 경우 있는 개수로만 평균 낸다!!
    if per5.isnull().sum() == 5 :
      per5_value = 0  
      per_period = 0  
    else:
      per_sum = 0.0
      for x in per5.values :
        if ~np.isnan(x) :
          per_sum = per_sum + x
      per5_value = round(per_sum/(5-per5.isnull().sum()),2)
      per_period = 5-per5.isnull().sum()
  else :
    list3 = [float(x) for x in per5.values]
    per5_value = round(sum(list3)/5,2)
    per_period = 5
  datalist.append(per5_value)
  # print("step 14. 5년 PER END ==========================")
  #5년 PBR
  pbr5 = avdf.iloc[22,:5] #22.11.29 EPS [21,] => [22,] 변경
  if pbr5.isnull().sum() > 0 :
    #pbr5_value = 0
    #2019. 10.25. 추가 코드: 
    if pbr5.isnull().sum() == 5 :
      pbr5_value = 0
      pbr_period = 0    
    else:
      pbr_sum = 0.0
      for x in pbr5.values :
        if ~np.isnan(x) :
          pbr_sum = pbr_sum + x
      pbr5_value = round(pbr_sum/(5-pbr5.isnull().sum()),2)
      pbr_period = 5-pbr5.isnull().sum()
  else :
    list2 = [float(x) for x in pbr5.values]
    pbr5_value = round(sum(list2)/5,2)
    pbr_period = 5
  datalist.append(pbr5_value) 
  # print("step 15. 5년 PBR END ==========================") 
  #PERR
  perr = round(per5_value/roe,2)
  datalist.append(perr)
  # print("step 16. PERR END ==========================")
  #PBRR
  pbrr = round(pbr5_value/(roe/10),2)
  datalist.append(pbrr)
  # print("step 17. PBRR END ==========================")
  #PER/PBR 기간
  total_period = str(per_period)+"년/"+str(pbr_period)+"년"
  datalist.append(total_period)
  # print("step 18. 총년수 END ==========================")
  onedf = pd.DataFrame(index=["종목코드", "종목명", "평가일","현재주가", "BPS(4QM)", "EPS(ttm)","DPS(MRY)","ROE","요구수익률","배당수익률","시가수익률", "r","ROE/r","적정주가","패리티", "기대수익률", "컨센서스","컨센기업수","5년PER","5년PBR","PERR","PBRR","PER/PBR평균"], data=datalist)
  #컬럼 순서 변경
  #onedf = onedf[["종목코드", "종목명", "평가일","현재주가", "적정주가", "컨센서스", "BPS(4QM)", "EPS(ttm)","DPS(MRY)","ROE","기대수익률", "요구수익률","배당수익률","시가수익률", "r","ROE/r","패리티", "컨센기업수","5년PER","5년PBR","PERR","PBRR","PER/PBR평균"]]
  onedf.iloc[:,3:7] = onedf.iloc[:,3:7].apply(lambda int_num: '{:,}'.format(int_num))

  return onedf

def get_fdata_fnguide(firm_code):
  fs_url = 'https://comp.fnguide.com/SVO2/asp/SVD_Main.asp?pGB=1&cID=&MenuYn=Y&ReportGB=&NewMenuID=101&stkGb=701&gicode=A' + firm_code
  fs_page = requests.get(fs_url)
  fs_tables = pd.read_html(fs_page.text) 
  
  #연결인지 별도인지 구별은 fs_tables[10]의 Net Quarter 모두 NaN으로 구분
  sep_flag = False
  ann_df = pd.DataFrame()
  qu_df = pd.DataFrame()
  if np.isnan(fs_tables[10].iloc[0,5]) == False  and np.isnan(fs_tables[10].iloc[18,5]) == False: #연결
    #연결 year
    fs_tables[11] = fs_tables[11].set_index([('IFRS(연결)',   'IFRS(연결)')])
    ann_df = fs_tables[11].xs("Annual", axis=1)
    ann_df.index.name = '항목'
    #연결 quarter
    fs_tables[12] = fs_tables[12].set_index([('IFRS(연결)',   'IFRS(연결)')])
    qu_df = fs_tables[12].xs("Net Quarter", axis=1)
    qu_df.index.name = '항목'
  #연결이면서 추정치 없는 경우
  #ann_df.iloc[18,5] or ann_df.iloc[19,5] is NaN
  else: #별도
    sep_flag = True
    fs_tables[14] = fs_tables[14].set_index([('IFRS(별도)',   'IFRS(별도)')])
    ann_df = fs_tables[14].xs("Annual", axis=1)
    ann_df.index.name = '항목'
    #연결 quarter
    fs_tables[15] = fs_tables[15].set_index([('IFRS(별도)',   'IFRS(별도)')])
    qu_df = fs_tables[15].xs("Net Quarter", axis=1)
    qu_df.index.name = '항목'

  return sep_flag, ann_df, qu_df, fs_tables
  

