from datetime import datetime
import requests
import json
from pandas import json_normalize


def get_holidays():
    today_year = datetime.today().year
    today_month = datetime.today().strftime("%m")

    KEY = "4TQBSonFQWSh3ilMTWzstLC6ARNkEJWkpcqfH15DnQdVd2gZ%2BlFxLHUeMR3UZO6nW21MCGzULGYMJiQPuFRi%2BA%3D%3D"
    url = (
        "http://apis.data.go.kr/B090041/openapi/service/SpcdeInfoService/getRestDeInfo?_type=json&numOfRows=50&solYear="
        + str(today_year)
        + "&solMonth="
        + str(today_month)
        + "&ServiceKey="
        + str(KEY)
    )
    response = requests.get(url)
    
    try:
        if response.status_code == 200:
            json_ob = json.loads(response.text)
            holidays_data = json_ob["response"]["body"]["items"]["item"]
            dataframe = json_normalize(holidays_data)
            
    except json.decoder.JSONDecodeError:
        return None

    return dataframe["locdate"].to_list()

def is_holiday():
    today = datetime.now().strftime("%Y%m%d")
    holidays = get_holidays()
    is_holiday = False
    if int(today) in holidays:
        is_holiday = True
        
    return is_holiday