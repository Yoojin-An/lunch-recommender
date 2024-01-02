import pymysql

print("==========================================================")
print("- format -")
print(" 분류; 한식, 일식, 중식, 양식, 동남아")
print(" 거리; 근거리: N, 원거리: F")
print("==========================================================")
print()
print(" 음식점 이름, 분류, 거리를 공백으로 구분해 입력하세요.")
print(" * 입력을 중단하려면 'q'를 입력하세요.")
print()

sql = """INSERT INTO lnch_menu 
             (id_no
            , classification
            , restaurant_nm
            , distance) 
            VALUES (%s, %s, %s, %s);"""

db_impl = pymysql.connect(host='localhost'
                        , user='root'
                        , password='qpflqpfl95!'
                        , db='LUNCH'
                        , charset='utf8')
cursor = db_impl.cursor()

while True:
    try:
        user_input = input(">>> ")
        values = user_input.split()
        if any(val == 'q' for val in values):
            break
        elif len(values) != 3:
            print("------------------------------------------------ 입력 오류\n")
            continue
        restaurant_nm, classification, distance = values
        cursor.execute(sql, (1, classification, restaurant_nm, distance))
        db_impl.commit()
        print("------------------------------------------------ 저장 완료\n")
    
    except Exception as e:
        print(type(e), e)
        break

try:
    db_impl.close()
    print("--------------------------------------------- DB 연결 종료")

except Exception as e:
    print(f"저장 오류: {type(e)} {e}")