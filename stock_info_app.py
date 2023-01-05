import matplotlib.font_manager as fm
import streamlit as st
import pandas as pd
import yfinance as yf
import datetime
import matplotlib.pyplot as plt
import matplotlib
from matplotlib import rc
from io import BytesIO

# 한국 주식 종목 코드를 가져오는 함수
def get_stock_info(market_type = None):
    base_url = "http://kind.krx.co.kr/corpgeneral/corpList.do"
    method = "download"
    if market_type == "kospi":
        marketType = "stockMkt"
    elif market_type == "kosdaq":
        marketType = "kosdaqMkt"
    elif market_type == None:
        marketType = " "

    url = "{}?method={}&marketType={}".format(base_url, method, marketType)

    df = pd.read_html(url, header = 0)[0]

    df["종목코드"] = df["종목코드"].apply(lambda x: f"{x:06d}")

    df = df[["회사명", "종목코드"]]

    return df


# yfinance에 이용할 ticker symbol을 반환하는 함수 작성
def get_ticker_symbol(company_name, maket_type):
    df = get_stock_info(maket_type)
    code = df[df['회사명']==company_name]['종목코드'].values
    code = code[0]
    
    if maket_type == 'kospi':
        ticker_symbol = code +".KS" # 코스피 주식의 심볼
    elif maket_type == 'kosdaq':
        ticker_symbol = code +".KQ" # 코스닥 주식의 심볼
    
    return ticker_symbol


st.title("주식 정보를 가져오는 웹 앱")

ratio_options = ["코스피", "코스닥"]
ratio_selected = st.slidebar.radio("증권시장", ratio_options)

stock_name = st.sidebar.text_input('회사 이름', value="NAVER")
date_range = st.sidebar.date_input("시작일과 종료일",[datetime.date(2019, 1, 1), datetime.date(2021, 12, 31)])

# 2. button()으로 버튼 만들기
clicked = st.sidebar.button("주가 데이터 가져오기")

if(clicked == True):
    ticker_symbol = get_ticker_symbol(stock_name, "kospi")
    ticker_data = yf.Ticker(ticker_symbol)
    start_p = date_range[0] # 시작일
    end_p = date_range[1] + datetime.timedelta(days=1) # 종료일(지정된 날짜에 하루를 더함)
    df = ticker_data.history(start=start_p, end=end_p)
    st.subheader(f"[{stock_name}] 주가 데이터")
    st.dataframe(df.head()) # 주가 데이터 표시(앞의 일부만 표시)

    # matplotlib을 이용한 그래프에 한글을 표시하기 위한 설정
    fontprop = fm.FontProperties(fname='NanumGothic.ttf', size=18)
    matplotlib.rcParams['axes.unicode_minus'] = False
    
    # 선 그래프 그리기
    ax = df['Close'].plot(grid=True, figsize=(15, 5))
    ax.set_title("주가(종가) 그래프", fontproperties=fontprop, fontsize=30) # 그래프 제목을 지정
    ax.set_xlabel("기간", fontproperties=fontprop, fontsize=20) # x축 라벨을 지정
    ax.set_ylabel("주가(원)", fontproperties=fontprop, fontsize=20) # y축 라벨을 지정
    plt.xticks(fontsize=15) # X축 눈금값의 폰트 크기 지정
    plt.yticks(fontsize=15) # Y축 눈금값의 폰트 크기 지정    
    fig = ax.get_figure() # fig 객체 가져오기    
    st.pyplot(fig)

    st.markdown("**주가 데이터 파일 다운로드**")
    # DataFrame 데이터를 CSV 데이터(csv_data)로 변환
    csv_data = df.to_csv() # DataFrame 데이터를 CSV 데이터로 변환해 반환

    # DataFrame 데이터를 엑셀 데이터(excel_data)로 변환
    excel_data = BytesIO() # 메모리 버퍼에 바이너리 객체 생성
    
    df.reset_index(inplace=True)
    df['Date'] = pd.to_datetime(df['Date']).dt.date
    df.set_index('Date', inplace=True)
    df.to_excel(excel_data) # DataFrame 데이터를 엑셀 형식으로 버퍼에 쓰기

    columns = st.columns(2) # 2개의 세로단으로 구성
    with columns[0]:
        st.download_button("CSV 파일 다운로드", csv_data, file_name='stock_data.csv')
    with columns[1]:
        st.download_button("엑셀 파일 다운로드", excel_data, file_name='stock_data.xlsx')
    
