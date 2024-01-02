import argparse
import webhook
from lunch_recommender import LunchRecommender

parser = argparse.ArgumentParser(description='recommend lunch menu')
parser.add_argument('-ex', '--exmenu', default=None, help="제외할 음식 종류 / 음식점")
parser.add_argument('-d', '--distance', default='all', help="거리(근거리: near, 거리무관: all)")
argument = parser.parse_args()

ex_menu = argument.exmenu
distance = argument.distance

worker = LunchRecommender()

# 전체 데이터셋 구성
worker.configure_dataset()
# 거리 기반 데이터셋 선택
worker.choose_dataset(distance)

# 우선순위 판단
priority = None
if priority_list := worker.retrieve_priority():
    priority = worker.judge_priority(priority_list)

# 우선순위/제외 옵션을 반영한 최종 데이터셋 구성
worker.apply_opt(priority, ex_menu)

# 메뉴 선정
todays_menu = worker.recommend_menu()

# 선정된 메뉴 GoogleChat으로 송신
webhook.to_google_chat(todays_menu)

# lunch_record 테이블에 오늘의 메뉴 저장
worker.save(todays_menu)