import json
import random
import datetime
import redis
import pymysql

class Constant(object):
    FOOD_TYPE = ['한식', '일식', '중식', '양식', '기타']

class LunchRecommender:
    def __init__(self):
        # 변수
        self.all_spots = {}
        self.near_spots = {}
        self.tmp_dataset = {}
        self.dataset = []
        
        # DB connection
        self.db_impl = pymysql.connect(host='localhost'
                        , user='root'
                        , password='qpflqpfl95!'
                        , db='LUNCH'
                        , charset='utf8')
        self.cursor = self.db_impl.cursor()
        
        # date information
        self.today = datetime.date.today()
        if self.today.weekday() != 0: # 월요일이 아니면
            self.yesterday = self.today - datetime.timedelta(days=1)
        else:
            self.yesterday = self.today - datetime.timedelta(days=3)

    def configure_dataset(self):
        """
        self.all_spots, self.near_spots 구성
        """
        sql = """
        SELECT JSON_OBJECT
                    ('classification', classification,
                     'restaurant_nm', restaurant_nm,
                     'distance', distance)
        FROM lnch_menu 
        WHERE ID_NO = 1;
        """
        self.cursor.execute(sql)
        all_spots = self.cursor.fetchall()
        all_spots = [json.loads(spot[0]) for spot in all_spots]

        for spot in all_spots:
            classification = spot['classification']
            name = spot['restaurant_nm']
            distance = spot['distance']
            # near_spots
            if distance == 'N':
                if classification not in self.near_spots:
                    self.near_spots[classification] = []
                self.near_spots[classification].append(name)
            # all_spots
            if classification not in self.all_spots:
                self.all_spots[classification] = []
            self.all_spots[classification].append(name)

    def retrieve_priority(self) -> dict:
        """
        Redis에서 우선순위 조회
        * Hash 자료형(key: priority, subkey: menu, value: {count, first_registration_time})
        """
        # redis 연결
        rd = redis.Redis(host='localhost', port=6379)
        # redis에 priority 존재 시 해당 값 반환
        if priority_list := rd.hgetall(f'priority_{self.today}'):
            return priority_list

    def judge_priority(self, priority_list):
        """
        우선순위 판단 기준
        1. 최다 득표
        2. 득표 수 동률 시 우선 등록
        
        메뉴(한식, 양식, 일식, 중식, 동남아 중 하나)이면 데이터셋 설정
        음식점 이름이면 바로 음식점 이름으로 선정
        """
        priority_list = [{menu.decode('utf-8'): json.loads(info.decode('utf-8'))} for menu, info in priority_list.items()]
        most_votes = max(priority_list, key=lambda x: (list(x.values())[0]['count'], -int(list(x.values())[0]['first_registration_time'].replace(':', ''))))
        priority = list(most_votes.keys())[0]
        return priority

    def choose_dataset(self, distance):
        """
        거리 기반 데이터셋 선택
        """
        print(f"거리: {distance}")
        if distance == 'near':
            self.tmp_dataset = self.near_spots
        else:
            self.tmp_dataset = self.all_spots

    def choose_dataset_by_priority(self, priority):
        """
        우선순위 기반 데이터셋 선택
        """
        # priority가 메뉴 종류인 경우
        if priority in Constant.FOOD_TYPE:
            self.dataset = self.tmp_dataset[priority]
        # priority가 음식점 이름인 경우
        else:
            self.dataset = [priority]
    
    def tmp_dataset_to_list(self) -> list:
        """
        최종 데이터셋(dict)에 포함된 모든 음식점들을
        random으로 선택하기 위한 포맷(list)으로 변경 
        """
        finalist = []
        for spots in self.tmp_dataset.values():
            finalist += spots
        return finalist

    def apply_opt(self, priority=None, ex_menu=None):
        """
        ex_menu에 따라 tmp_dataset 조정 후 priority에 따라 tmp_dataset 조정 및 dataset 세팅
        priority가 음식 종류인데 ex_menu가 음식점 이름인 경우 때문에 ex_menu를 먼저 판단한다
        """
        print(f"우선순위: {priority}")
        print(f"제외할 메뉴: {ex_menu}")

        # ex_menu에 따라 데이터 조정
        if ex_menu:
            # ex_menu가 음식점 이름인 경우
            if ex_menu not in Constant.FOOD_TYPE:
                self.tmp_dataset = {food_type: [spot for spot in spots if spot != ex_menu] for food_type, spots in self.tmp_dataset.items()}
            # ex_menu가 음식 종류인 경우
            else:
                self.tmp_dataset.pop(ex_menu)
            self.dataset = self.tmp_dataset_to_list()
            
        # priority에 따라 데이터 조정
        if priority:
            # priority가 음식점 이름인 경우
            if priority not in Constant.FOOD_TYPE:
                self.dataset = [priority]
            # priority가 음식 종류인 경우
            else:
                self.dataset = self.tmp_dataset[priority]

    def except_yesterday_menu(self):
        """
        DB에 저장된 어제 먹은 메뉴를 불러와 데이터셋에서 삭제
        """
        sql = """
        SELECT restaurant_nm
        FROM lnch_record
        WHERE yyyymmdd = %s;
        """
        try:
            self.cursor.execute(sql, self.yesterday)
            record = self.cursor.fetchone()
            yesterday_menu = record[0]
            self.dataset.remove(yesterday_menu)

        except TypeError: # 어제 날짜로 먹은 메뉴가 없는 경우
            pass
        except ValueError: # dataset에 어제 날짜로 먹은 메뉴가 없는 경우
            pass
        except Exception as e:
            print(type(e), e)

    def recommend_menu(self):
        """
        최종 데이터셋에서 랜덤으로 오늘의 점심메뉴 추천
        """
        self.except_yesterday_menu() # 어제 먹은 메뉴 삭제
        menu = random.choice(self.dataset)
        print("========================================")
        print(f"⭐️ 오늘의 점심은 {menu}! ⭐️")
        return menu

    def save(self, restaurant_nm):
        """
        선정된 메뉴 저장
        """
        sql = """INSERT INTO lnch_record 
             (yyyymmdd
            , restaurant_nm) 
            VALUES (%s, %s);"""

        self.cursor.execute(sql, (self.today, restaurant_nm))
        self.db_impl.commit()
        self.db_impl.close()
        print(f"[save] date: {self.today}, menu: {restaurant_nm}")
        print("========================================")