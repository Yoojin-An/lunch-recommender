import redis
import json
import datetime
from time import sleep

class Registrant:
    def __init__(self):
        self.rd = redis.Redis(host='localhost', port=6379)
        self.today = datetime.date.today()

    def register_priority(self, menu) -> None:
        if not menu: return
        menu = menu.encode('utf-8')
        
        key = "lock"
        max_try = 3
        retry = 0

        # lock 획득
        # while not self.try_lock(key):
        while True:
            if retry == max_try:
                break
            try: 
                sleep(5)
                retry += 1
            except KeyboardInterrupt:
                self.unlock(key)
            except InterruptedError:
                self.unlock(key)

        # 우선순위 등록
        try:
            # menu가 이미 우선순위로 등록되어 있는 경우
            if prev_data := self.rd.hget(f'priority_{self.today}', menu):
                count = json.loads(prev_data)['count']
                count += 1 # 기존 count에 + 1
                time = json.loads(prev_data)['first_registration_time']  # 기존 최초 등록 시각
            # menu 최초 등록하는 경우
            else:
                count = 1
                time = str(datetime.datetime.now().strftime('%H:%M:%S')) # 현재 시각
            
            # menu를 subkey, priority_info를 value로 하는 priority를 Hash로 저장
            priority_info = json.dumps({'count': count, 'first_registration_time': time}, ensure_ascii=False)
            self.rd.hset(f'priority_{self.today}', menu, priority_info)

        except Exception as e:
            print(type(e), e)
        finally:
            self.unlock(key)

    def try_lock(self, key) -> bool:
        return self.rd.setnx(key, "1")
    
    def unlock(self, key):
        self.rd.delete(key)

    def get_priority_list(self) -> dict:
        priority_list = self.rd.hgetall(f'priority_{self.today}')
        return [f"{menu.decode('utf-8')}: {info.decode('utf-8')}" for menu, info in priority_list.items()]

if __name__ == '__main__':
    worker = Registrant()
    prompt = "우선순위 등록을 원하는 메뉴 또는 음식점 이름을 입력하세요:\n"
    if menu := input(prompt + " * 메뉴 종류: 한식, 양식, 일식, 중식, 기타\n\n>>> "):
        worker.register_priority(menu)
        print(f"[{menu}] 우선순위 등록 완료!")
        priority_list = worker.get_priority_list()
        print(f"\n👀 우선순위 등록 현황")
        for priority in priority_list:
            print(priority)