import json
from httplib2 import Http

def to_google_chat(todays_menu):
    url = 'https://chat.googleapis.com/v1/spaces/AAAAE89_dxo/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=oWwzEcY1eE7GP_SI-eF3jXrlq6jEL9PbIO4OPTCx9pk%3D'
    bot_message = {
        'text': f"🔔점심시간 10분 전\n오늘의 점심메뉴는 {todays_menu}입니다!😋"
    }
    message_headers = {'Content-Type': 'application/json; charset=UTF-8'}
    http_obj = Http()
    http_obj.request(
        uri=url,
        method='POST',
        headers=message_headers,
        body=json.dumps(bot_message),
    )