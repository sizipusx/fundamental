import streamlit as st

st.set_page_config(
    page_title="Hello",
    page_icon="👋",
)

st.write("# Welcome to 아파트 데이터 분석! 👋")

st.sidebar.success("Select a menu above.")

st.markdown(
    """
    Streamlit is an open-source app framework built specifically for
    Machine Learning and Data Science projects.
    **👈 Select a demo from the sidebar** to see some examples
    of what Streamlit can do!
    ### Menu 설명
    - apt weekly: 한국부동산원과 KB에서 매주 발표하는 부동산 지수를 다양한 챠트와 테이블로 아파트 주간 동향을 살펴 봄
    - apt monthly: 한국부동산원과 KB에서 매달 발표하는 부동산 지수를 다양한 챠트와 테이블로 아파트 매월 동향을 살펴 봄
    - local analysis: 시군 지역의 다양한 데이터를 확인할 수 있음. 예를 들면 인구수, 직장수, 평균 연봉, 미분양, 전세가율 등등
    - rebuild house: 네이버 부동산에서 가져온 전국의 아파트분양권, 재개발, 재건축 매물 위치와 정보 확인
    ### See more 
    - Check out [기하급수적](https://blog.naver.com/indiesoul2)
    - Ask a question in my [e-mail]<indiesoul2@naver.com>
"""
)
