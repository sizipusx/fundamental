import requests
import datetime
from dateutil.relativedelta import relativedelta

def get_period_range():
    today = datetime.date.today()

     # ✅ 한 달 전 날짜 계산
    one_month_ago = today - relativedelta(months=1)

    # ✅ 한 달 전 날짜의 주의 월요일 계산
    start_of_week = one_month_ago - datetime.timedelta(days=one_month_ago.weekday())

    return start_of_week.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d')

def get_monday_of_current_week():
    today = datetime.date.today()  # 오늘 날짜
    monday = today - datetime.timedelta(days=today.weekday())  # 오늘에서 요일의 값만큼 빼면 월요일
    return monday.strftime('%Y-%m-%d')

# ✅ 다음 주 조회 기간 계산 함수
def get_next_week_range():
    today = datetime.date.today()
    next_monday = today + datetime.timedelta(days=-today.weekday() + 7)
    next_friday = next_monday + datetime.timedelta(days=4)
    return next_monday.strftime('%Y-%m-%d'), next_friday.strftime('%Y-%m-%d')

# ✅ APT 분양정보 조회 함수 (모집 공고일 기준)
def get_apt_detail(start_date, end_date, api_key):
    BASE_URL = 'https://api.odcloud.kr/api/ApplyhomeInfoDetailSvc/v1'
    url = f"{BASE_URL}/getAPTLttotPblancDetail"
    params = {
        'page': 1,
        'perPage': 100,  # 한 번에 최대 100건 조회
        'serviceKey': api_key,
        'cond[RCRIT_PBLANC_DE::GTE]': start_date,  # (>=)
        'cond[RCRIT_PBLANC_DE::LTE]': end_date     # 청약접수종료일(<=)
    }
    response = requests.get(url, params=params)
    return response.json()

# ✅ 텔레그램 메시지 전송 함수
def send_telegram_message(message, token, chat_id):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    params = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'Markdown'  # 굵은 글씨 등 포맷 지원
    }
    response = requests.post(url, params=params)
    return response.json()

# ✅ 아파트 정보 메시지 생성 함수
def create_message(apt_data, start_date):
    if not apt_data.get('data'):
        return "❌ 다음 주 청약 접수 예정 아파트가 없습니다."

    message = f"📅 *조회 기간*: {start_date} \n\n📊 *이번 주 이후 청약 접수 예정 아파트:*\n"
    if apt_data.get('data'):
      for item in apt_data['data']:
          rcept_bgnde = item.get('RCEPT_BGNDE') #청약 접수 시작일
          # 청약 접수 시작일이 today() 이후 날짜 가져오기
          if start_date <= rcept_bgnde :
              print(f"🏢 주택구분: {item.get('HOUSE_DTL_SECD_NM')} | 주택명: {item.get('HOUSE_NM')} | 청약접수: {item.get('RCEPT_BGNDE')} ~ {item.get('RCEPT_ENDDE')} | 지역명: {item.get('SUBSCRPT_AREA_CODE_NM')}")
    else:
        print("❌ 오늘 이후 청약 접수 예정 아파트가 없습니다.")

    for item in apt_data['data']:
        house_secd_nm = item.get('HOUSE_DTL_SECD_NM', '정보 없음')
        house_nm = item.get('HOUSE_NM', '정보 없음')
        rcept_bgnde = item.get('RCEPT_BGNDE', '정보 없음')
        rcept_endde = item.get('RCEPT_ENDDE', '정보 없음')
        region = item.get('SUBSCRPT_AREA_CODE_NM', '정보 없음')
        home_page = item.get('PBLANC_URL', '정보 없음')

        message += (
        f"🏢 *주택구분*: {house_secd_nm}\n"
        f"🏠 *주택명*: {house_nm}\n"
        f"🗓 *청약접수*: {rcept_bgnde} ~ {rcept_endde}\n"
        f"📍 *지역명*: {region}\n"
        f"🔗 *청약홈 보기*: [상세보기]({home_page})\n\n"  # 링크로 메시지에 포함
        )
    return message

# ✅ 메인 함수
def main():
    # 🔑 텔레그램 API 정보
    TELEGRAM_TOKEN = "8148018763:AAF2uPLpISDHHdaQxOe0pd6oaw5BEfIOEnA"
    TELEGRAM_CHAT_ID = "2142036312"
    API_KEY = "5wQYWVUcrzNSB7thQwhuGdyBG5QgXNh5APk0a5RcbEWnSEJUJoQl2ymSHXbhFL9oJJV+D8Noi/s3FIZwA5joIQ=="

    # 📅 조회 기간 설정
    this_week_monday = get_monday_of_current_week()
    # 📅 한달 전 날짜 가져오기
    start_date, end_date = get_period_range()
    print(f"📅 조회 기간: {start_date} ~ {end_date}")

    # 📊 청약 접수 데이터 조회
    apt_data = get_apt_detail(start_date, end_date,  API_KEY)

    # 📩 메시지 생성
    message = create_message(apt_data,this_week_monday)

    # 📲 메시지 전송
    send_telegram_message(message, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID)
    print("📨 청약 정보가 텔레그램으로 전송되었습니다.")

if __name__ == "__main__":
    main()
