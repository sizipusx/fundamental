
import pandas as pd
import requests
import json
from bs4 import BeautifulSoup
import streamlit as st
import numpy as np
#from tqdm.notebook import tqdm as tn
import time
import datetime
import FinanceDataReader as fdr
import pandasdmx as pdmx
import ecos_chart as ec
import seaborn as sns
import cloudscraper
cmap = cmap=sns.diverging_palette(250, 5, as_cmap=True)

utcnow= datetime.datetime.utcnow()
time_gap= datetime.timedelta(hours=9)
kor_time= utcnow+ time_gap

pd.set_option('display.float_format', '{:.2f}'.format)
#############html 영역####################
html_header="""
<head>
<title>Ecos chart</title>
<meta charset="utf-8">
<meta name="keywords" content="chart, analysis">
<meta name="description" content="House data analysis">
<meta name="author" content="indiesoul">
<meta name="viewport" content="width=device-width, initial-scale=1">
</head>
<h2 style="font-size:200%; color:#008080; font-family:Georgia">경제 Macro 조회<br>
<hr style= "  display: block;
  margin-top: 0.5em;
  margin-bottom: 0.5em;
  margin-left: auto;
  margin-right: auto;
  border-style: inset;
  border-width: 1.5px;"></h1>
"""

st.set_page_config(page_title="Macro 조회", page_icon="files/logo2.png", layout="wide")
st.markdown('<style>body{background-color: #fbfff0}</style>',unsafe_allow_html=True)
st.markdown(html_header, unsafe_allow_html=True)
st.markdown(""" <style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style> """, unsafe_allow_html=True)


@st.cache_data(ttl=datetime.timedelta(days=1))
def query_ecos(stat_code, stat_item, start_date, end_date, cycle_type="Q"):
    auth_key = "71BO71RCBA99FVU3BETA/" #발급 받은 Key 를 넣으면 더 많은 데이터 수집 가능
    req_type = "json/"
    lang = "kr/"
    start_no = "1/"
    end_no ="10000/"
    stat_code = stat_code + "/"
    #stat_code = stat_code.split('/')[0] + "/"
    cycle_type = cycle_type + "/"
    start_date = start_date + "/"
    end_date = end_date + "/"
    #item_no = stat_code.split('/')[1]
    item_no = stat_item
    try:
        url = "http://ecos.bok.or.kr/api/StatisticSearch/" +  \
            auth_key + req_type + lang + start_no + end_no + \
            stat_code + cycle_type + start_date + end_date + item_no
        print(url)
        r = requests.get(url)
        if '해당하는 데이터가 없습니다' in r.text:
            return None
        
        jo = json.loads(r.text)
        print(jo)
        df = pd.json_normalize(jo['StatisticSearch']['row'])
    except Exception as e:
        st.write(e)
    if cycle_type == 'D':
      df['TIME'] = df['TIME'].str.replace(r'(\d{4})(\d{2})(\d{2})(.*)', r'\1-\2-\3')
    elif cycle_type == 'M':
      df['TIME'] = df['TIME'].str.replace(r'(\d{4})(\d{2})(.*)', r'\1-\2')
    return df

def make_df(item_symbols, start_date, end_date, cycle_type):
    item_index_tickers = list(item_symbols.values())
    all_data = {}
    for ticker in item_index_tickers:
        stat_code = ticker.split('/')[0]
        stat_item = ticker.split('/')[1]
        #stat_item = ticker.split('/')[2]
        all_data[ticker] = query_ecos(stat_code, stat_item, start_date, end_date, cycle_type)    
    #컬럼명 종목명으로 변경
    data_df = pd.DataFrame({tic: data['DATA_VALUE'] for tic, data in all_data.items()})
    data_df.columns = item_symbols.keys()
    #날짜 설정
    try:
        tempdf = all_data.get(item_index_tickers[1])
        data_df.set_index(keys=tempdf['TIME'], inplace=True)
        if cycle_type == "M":
            data_df.index = pd.to_datetime(data_df.index, format="%Y%m")
    except ValueError as e:
        st.write(e)
        tempdf = all_data.get(item_index_tickers[0])
        data_df.set_index(keys=tempdf['TIME'], inplace=True)
        if cycle_type == "M":
            data_df.index = pd.to_datetime(data_df.index, format="%Y%m")
    return data_df

def run(stat_name, stat_ticker, fred_dict):
    
    if source == 'Ecos':
        if stat_ticker == '901Y009':
            item_symbols = {'소비자물가지수':'901Y009/0','생산자물가지수':'404Y014/*AA'}
            start_date = "200010"
            end_date = kor_time.strftime('%Y%m')
            cycle_type = "M" #default
            data_df = make_df(item_symbols, start_date, end_date, cycle_type)
        elif stat_ticker == '721Y001':
            item_symbols =  {'CD91':'721Y001/2010000', '국고채(1Y)':'721Y001/5030000','국고채(10Y)':'721Y001/5050000'} 
            start_date = "200010"
            end_date = kor_time.strftime('%Y%m')
            cycle_type = "M" #default
            data_df = make_df(item_symbols, start_date, end_date, cycle_type)
        elif stat_ticker == '402Y014':
            item_symbols = {'수출금액지수':'403Y001/*AA','수입금액지수':'403Y003/*AA'}
            start_date = "200010"
            end_date = kor_time.strftime('%Y%m')
            cycle_type = "M" #default
            data_df = make_df(item_symbols, start_date, end_date, cycle_type)
        elif stat_ticker == '104Y014':
            item_symbols = {'예금은행 총수신(말잔)':'104Y013/BCB8', '비예금은행 총수신(말잔)':'111Y007/1000000', '예금은행 대출금(말잔)':'104Y016/BDCA1', '비예금은행 대출금(말잔)':'111Y009/1000000'}
            start_date = "200010"
            end_date = kor_time.strftime('%Y%m')
            cycle_type = "M" #default
            data_df = make_df(item_symbols, start_date, end_date, cycle_type)
        elif stat_ticker == '151Y005':
            #가계 신용: 가계 저축과 가계대출(주택담보대출+기타대출) + 판매신용
            item_symbols = {'주택담보대출':'151Y005/11100A0','기타대출':'151Y005/11100B0'}
            start_date = "200010"
            end_date = kor_time.strftime('%Y%m')
            cycle_type = "M" #default
            data_df = make_df(item_symbols, start_date, end_date, cycle_type)
        elif stat_ticker == '722Y001':
            item_symbols = {'한국은행기준금리':'722Y001/0101000'}
            start_date = "200010"
            end_date = kor_time.strftime('%Y%m')
            cycle_type = "M" #default
            data_df = make_df(item_symbols, start_date, end_date, cycle_type)
        elif stat_ticker == '200Y003': #월별 시가총액은 따로 받아야 함
            item_symbols = {'명목GDP':'200Y003/1400','실질GDP':'200Y004/1400'} 
            start_date = "2005Q1"
            cycle_type = "Q" #default
            end_date_year = kor_time.strftime('%Y')
            end_date_month = kor_time.strftime('%m')
            if end_date_month in ['01', '02', '03']:
                end_date= end_date_year+ 'Q1'
            elif end_date_month in ['04', '05', '06']:
                end_date= end_date_year+ 'Q2'
            elif end_date_month in ['07', '08', '09']:
                end_date= end_date_year+ 'Q3'
            elif end_date_month in ['10', '11', '12']:
                end_date= end_date_year+ 'Q4'
            gdata_df = make_df(item_symbols, start_date, end_date, cycle_type)
            gdata_df = gdata_df.fillna(method='ffill').astype(float).round(decimals=1)
            gdata_ch = gdata_df.pct_change()*100
            gdata_ch = gdata_ch.fillna(0).round(decimals=2)
            gdata_df['RGDP'] = gdata_df['실질GDP'].rolling(window=4).sum().fillna(0)
            gdata_df['NGDP'] = gdata_df['명목GDP'].rolling(window=4).sum().fillna(0)
            #시가 총액 받기
            item_symbols2 = {'KOSPI':'901Y014/1040000','KQ':'901Y014/2040000'} 
            start_date = "200501"
            end_date = kor_time.strftime('%Y%m')
            data_df = make_df(item_symbols2, start_date, end_date, cycle_type="M")
            data_df.index = data_df.index.astype(str)
            # Check the length of the string index
            if len(data_df.index[0]) == 6:
                # Convert 'YYYYMM' format to 'YYYY-MM' format
                data_df.index = pd.to_datetime(data_df.index, format='%Y%m').strftime('%Y-%m')
            data_df = data_df.astype(int)/1000000
            data_df['TQ'] = data_df['KOSPI'].add(data_df['KQ'])
            st.dataframe(data_df)
            st.dataframe(gdata_df)
            # Create a new DataFrame with monthly index
            df_monthly = pd.DataFrame(columns=['RGDP'])
            # Iterate over each row in the quarterly DataFrame
            try:
                for index, row in gdata_df.iterrows():
                    quarterly_index = index
                    year = int(quarterly_index[:4])
                    quarter = int(quarterly_index[-1])
                    # Generate monthly indexes for the quarter
                    start_month = 3 * quarter - 2
                    end_month = 3 * quarter
                    monthly_indexes = [f'{year}-{str(month).zfill(2)}' for month in range(start_month, end_month + 1)]
                    # Expand the quarterly value to monthly values
                    expanded_values = [row['RGDP']] * len(monthly_indexes)
                    expanded_values2 = [row['NGDP']] * len(monthly_indexes)
                    q_df = pd.DataFrame({'RGDP': expanded_values, 'NGDP': expanded_values2}, index=monthly_indexes)
                    # Add the expanded values to the new DataFrame
                    df_monthly = pd.concat([df_monthly, q_df])
            except Exception as e:
                st.write(e)
            # Sort the DataFrame by index
            df_monthly.sort_index(inplace=True)
            # df_monthly = df_monthly.reset_index()
            # data_df = data_df.reset_index()
            st.dataframe(df_monthly)
            st.dataframe(data_df)
            total_df = pd.merge(data_df, df_monthly, how='inner', left_index = True, right_index=True)
            total_df['GDPD'] = round(total_df['NGDP']/total_df['RGDP']*100,2)
            total_df['RBindex'] = round(total_df['TQ']/total_df['RGDP']*100,2)
            total_df['NBindex'] = round(total_df['TQ']/total_df['NGDP']*100,2)
            total_df = total_df.fillna(0)
            st.dataframe(total_df)
        else:
            item_symbols = {'대출금리(신)':'121Y006/BECBLA03', '예금금리(신)':'121Y002/BEABAA2', '기준금리':'722Y001/0101000'}
            start_date = "200010"
            end_date = kor_time.strftime('%Y%m')
            cycle_type = "M" #default
            data_df = make_df(item_symbols, start_date, end_date, cycle_type)

        #Raw 데이터 보기           
        with st.expander("See Raw Data"):
            try:
                if stat_ticker == '200Y003':
                    # total_df = total_df.set_index(keys=total_df['TIME'])
                    st.dataframe(total_df.loc[::-1].astype(float).fillna(0).round(decimals=2).style.background_gradient(cmap, axis=0)\
                                                .format(precision=2, na_rep='MISSING', thousands=","))
                else:
                    st.dataframe(total_df.loc[::-1].astype(float).fillna(0).round(decimals=2).style.background_gradient(cmap, axis=0)\
                                                .format(precision=2, na_rep='MISSING', thousands=","))
            except ValueError :
                st.dataframe(data_df.loc[::-1].astype(float).fillna(0).round(decimals=2).style.background_gradient(cmap, axis=0)\
                                            .format(precision=2, na_rep='MISSING', thousands=","))
        #세부 항목 조정
        if stat_ticker == '151Y005' or stat_ticker == '104Y014':#예금/대출일 경우 조 단위로 변경
            data_df = data_df.astype(float)/1000
            data_df = data_df.round(decimals=1)
            data_ch = data_df.pct_change()*100
            data_ch = data_ch.round(decimals=2)
            ec.ecos_monthly_chart(stat_name, data_df, data_ch)
        elif stat_ticker == '721Y001': #장단기금리차
            data_df = data_df.astype(float).round(2)
            data_df.loc[:,"금리차(10-CD)"] = round(data_df.loc[:,'국고채(10Y)'] - data_df.loc[:,'CD91'],2) 
            data_df.loc[:,"금리차(10-1)"] = round(data_df.loc[:,'국고채(10Y)'] - data_df.loc[:,'국고채(1Y)'],2)
            data_df.loc[:,'color1'] = np.where(data_df['금리차(10-CD)']<0, 'red', 'blue')
            data_df.loc[:,'color2'] = np.where(data_df['금리차(10-1)']<0, 'red', 'blue')
            ec.ecos_spread_chart(stat_name, data_df)
        elif stat_ticker == '104Y014':
            ec.ecos_monthly_chart("전체 여수신", data_df, data_ch)
            data_df.loc[:,'총수신(말잔)'] = data_df['예금은행 총수신(말잔)']+ data_df['비예금은행 총수신(말잔)']
            data_df.loc[:,'총대출(말잔)'] = data_df['예금은행 대출금(말잔)']+ data_df['비예금은행 대출금(말잔)']
            data_df.loc[:,'스프레드'] = data_df['총수신(말잔)']+ data_df['총대출(말잔)']
            sub_df = sub_df = data_df.iloc[:,4:]
            sub_ch = sub_df.pct_change()*100
            sub_ch = sub_ch.round(decimals=2)
            ec.ecos_monthly_chart(stat_name, sub_df, sub_ch)
        elif stat_ticker == '121Y002':
            data_df = data_df.astype(float)
            data_ch = data_df.pct_change()*100
            data_ch = data_ch.round(decimals=2)
            ec.ecos_monthly_chart("여수신금리", data_df, data_ch) 
            data_df.loc[:,"여수신금리차"] = round(data_df.loc[:,'대출금리(신)'] - data_df.loc[:,'예금금리(신)'],2)
            data_df.loc[:,'color'] = np.where(data_df['여수신금리차']<0, '#FFB8B1', '#E2F0CB')
            ec.ecos_spread_chart(stat_name, data_df)
        elif stat_ticker == '200Y003':
            ec.ecos_one_two_window(stat_name, total_df)
        else:
            data_df = data_df.astype(float)
            data_ch = data_df.pct_change()*100
            data_ch = data_ch.round(decimals=2)
            ec.ecos_monthly_chart(stat_name, data_df, data_ch)

############################################### 미국 macro  ########################################################        
    else:
        if stat_ticker == "Market Interest":
            #Yield Curve
            #ko_bond = 'https://kr.investing.com/rates-bonds/south-korea-government-bonds'
            us_bond = "https://kr.investing.com/rates-bonds/usa-government-bonds"
            url_base = (us_bond)
            scraper = cloudscraper.create_scraper() 
            html = scraper.get(url_base).content
            soup = BeautifulSoup(html, 'html.parser')
            table = soup.find('table', {'class' : 'genTbl closedTbl crossRatesTbl'})   # 특정 테이블 태그를 가져옴     
            table_html = str(table)      # 'table'변수는 bs4.element.tag 형태이기 때문에 table를 문자열 형태로 바꿔준다  
            table_df_list = pd.read_html(table_html)   # read_html 사용해서 html을 데이터프레임들로 이루어진 리스트로 바꿔줌  
            table_df = table_df_list[0]
            table_df.loc[:,'변동'] = table_df['채권수익률'] - table_df['베이스']
            cdf = table_df.iloc[:,1:-1]
            cdf = cdf.set_index(['종목'])
            #시장 금리
            ticker_list = [
                            ["기준금리", "FRED:RIFSPFFNB"],
                            ["국채10Y", "FRED:DGS10"],
                            ["국채2Y", "FRED:DGS2"],
                            ["국채3M", "FRED:DGS3MO"],
                            ["금리차10Y2Y", "FRED:T10Y2Y"],
                            ["금리차10Y3M", "FRED:T10Y3M"]
                        ]
            df_list = [fdr.DataReader(ticker, '2000-01-01') for name, ticker in ticker_list]
            # pd.concat()로 합치기
            inter_df = pd.concat(df_list, axis=1)
            inter_df.columns = [name for name, ticker in ticker_list] 
            with st.expander("See Raw Data"):
                with st.container():
                    col1, col2, col3 = st.columns([30,2,30])
                    with col1:
                        try:
                            st.dataframe(inter_df.loc[::-1].astype(float).fillna(0).round(decimals=2).style.background_gradient(cmap, axis=0)\
                                                        .format(precision=2, na_rep='MISSING', thousands=","))
                        except ValueError :
                            st.dataframe(inter_df.loc[::-1].astype(float).fillna(0).round(decimals=2).style.background_gradient(cmap, axis=0)\
                                                        .format(precision=2, na_rep='MISSING', thousands=","))
                    with col2:
                        st.write("")
                    with col3: 
                        try:
                            st.dataframe(cdf.style.background_gradient(cmap, axis=0))
                                                        
                        except ValueError :
                            st.dataframe(cdf.iloc[:4].astype(float).fillna(0).round(decimals=2).style.background_gradient(cmap, axis=0)\
                                                        .format(precision=2, na_rep='MISSING', thousands=","))
            ec.fred_spread_chart(cdf, inter_df)
            st.markdown("""---""")
            #10년물만 데이터가 %인 경우 
            df_10 = inter_df.loc[:,"국채10Y"].to_frame()
            df_2 = inter_df.loc[:,"국채2Y"].to_frame()
            ec.fred_monthly_chart("DGS10", "국채10Y", df_10)
            st.markdown("""---""")
            ec.fred_monthly_chart("DGS2", "국채2Y", df_2)
        elif stat_ticker == "CLI":
            oecd = pdmx.Request("OECD")
            data = oecd.data(
                            resource_id="MEI_CLI",#"PDB_LV",
                            key= "/LOLITOAA+LOLITOTR_GYSA.KOR+USA+G4E+OECD+A5M+CHN.M/all?startTime=2000-10", #LOLITOTR_GYSA : 12month change
                        ).to_pandas()
            oecd_df = pd.DataFrame(data).reset_index()
            #ec.OECD_chart(stat_ticker, kor_exp, oecd_df)
        else:
            df_list = [fdr.DataReader("FRED:"+ticker, start_date) for name, ticker in fred_dict['Inflation'].items()]
            # pd.concat()로 합치기
            df = pd.concat(df_list, axis=1)
            df.columns = [name for name, ticker in fred_dict['Inflation'].items()] 
            df_m = df.iloc[:,:6]
            df_d = df.iloc[:,6:]
            df_m = df_m.dropna()
            df_m_yoy = df_m.pct_change(periods=12)*100
            #fred_df.index = fred_df.index.strftime('%Y%m%d')
            with st.expander("See Raw Data"):
                try:
                    st.dataframe(df_m.loc[::-1].astype(float).fillna(0).round(decimals=2).style.background_gradient(cmap, axis=0)\
                                                .format(precision=2, na_rep='MISSING', thousands=","))
                    st.dataframe(df_d.loc[::-1].astype(float).fillna(0).round(decimals=2).style.background_gradient(cmap, axis=0)\
                                                .format(precision=2, na_rep='MISSING', thousands=","))
                except ValueError :
                    st.dataframe(df_m.loc[::-1].astype(float).fillna(0).round(decimals=2).style.background_gradient(cmap, axis=0)\
                                                .format(precision=2, na_rep='MISSING', thousands=","))




if __name__ == "__main__":
    st.write(kor_time)
    data_load_state = st.text('Loading 통계정보 List...')
    source = st.sidebar.radio(
            label = "Choose the Source", 
            options=('Ecos', 'Fred'),
            index = 0,
            horizontal= True)
    
    eco_dict = {"물가":"901Y009", "장단기금리":"721Y001", "가계신용":"151Y005", "전체여수신":"104Y014", "수출입금액":"402Y014", \
                "은행 수신/대출 금리(신규)":"121Y002", "버핏지수":"200Y003"} # "한국은행 기준금리":"722Y001", 
    #fred_dict = {"수익률곡선":"YC","개인소비지출":"PCE", "기대인플레이션율":"T10YIE", "CPI":"CPIAUCSL", "Total Assets":"WALCL", "Leading Indicators OECD":"CLI"}
    
    fred_dict = {"Key Economic Indicators":{
                        "Real GDP":"GDPC1",
                        "Unemployment Rate":"UNRATE",
                        "PCE Inflation":"PCEPI",
                        "Effectiv Federal Funds Rate":"RIFSPFFNB"
                        },
                "Market Interest":{
                        "Effectiv Federal Funds Rate":"RIFSPFFNB",
                        "국채10Y":"DGS10",
                        "국채2Y":"DGS2",
                        "국채3M":"DGS3MO",
                        "금리차10Y2Y":"T10Y2Y",
                        "금리차10Y3M":"T10Y3M"
                    },
                "Inflation":{
                        "Personal Consumption Expenditures":"PCEPI",
                    "Consumer Price Index":"CPIAUCSL",
                        "CPI Less Food and Energy":"CPILFESL",
                    "Producer Price Index":"PPIFIS",
                        "PPI Less Foods and Energy":"PPIFES",
                    "Year-Ahead Inflation Expectations(Michigan)":"MICH",
                    "5-Year Breakeven Inflation Rate":"T5YIE",
                    "5-Year, 5-Year Forward Inflation Expectation Rate":"T5YIFR",
                    },
                #"CLI":{}
                }

    data_load_state.text("Done! (using st.cache)")
    # st.dataframe(tickers)
    # st.dataframe(krx) 
    if source == 'Ecos':
        org_list = eco_dict.keys() #tickers
    else:
        org_list = fred_dict.keys()
    stat_name = st.sidebar.selectbox(
        '통계 목록', org_list)
    if source == 'Ecos':
        stat_ticker = eco_dict.get(stat_name)
    else:
        stat_ticker = fred_dict.get(stat_name)
    #st.dataframe(basic_df)
    submit = st.sidebar.button('Get Data')

    if submit:
        run(stat_name, stat_ticker, fred_dict)