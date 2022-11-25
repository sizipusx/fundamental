import streamlit as st

st.set_page_config(
    page_title="Hello",
    page_icon="👋",
)

st.write("# Welcome to 아파트 데이터 분석! 👋")

st.sidebar.success("Select a menu above.")

st.markdown(
    """
    부동산 공부 차원에서 시작한 프로젝트가 더해지고 더해져서 여기까지 오게 되었습니다.    
    앞으로 꾸준히 업데이트하면서 더 나은 프로젝트가 되도록 노력하겠습니다.      
    속도도 느리고 디자인, UI도 없지만 복잡한 데이터를 쉽게 본다는데 의미를 두면 좋겠습니다.

    **👈 Select a menu from the sidebar** 

    ### Menu 설명
    - apt weekly: 한국부동산원과 KB에서 매주 발표하는 부동산 지수를 다양한 차트와 테이블로 아파트 주간 동향을 살펴 봄
    - apt monthly: 한국부동산원과 KB에서 매달 발표하는 부동산 지수를 다양한 차트와 테이블로 아파트 매월 동향을 살펴 봄
    - local analysis: 시군 지역의 다양한 데이터를 확인할 수 있음. 예를 들면 인구수, 직장수, 평균 연봉, 미분양, 전세가율 등등
    - rebuild house: 네이버 부동산에서 가져온 전국의 아파트분양권, 재개발, 재건축 매물 위치와 정보 확인
    ### See more 
    - Check out my blog : [기하급수적](https://blog.naver.com/indiesoul2)
    - Ask a question in my E-mail : <indiesoul2@naver.com>
"""
)
