import pymysql

insert_sql = """ 
            INSERT INTO lnch_menu 
            (id_no,
             classification,
             restaurant_nm,
             distance) 
            VALUES 
            (%s, 
             %s, 
             %s, 
             %s);
            """

update_sql = """
            UPDATE lnch_menu 
            SET classification = %s, 
                restaurant_nm = %s, 
                distance = %s 
            WHERE restaurant_nm = %s
            """

delete_sql = """
            DELETE FROM lnch_menu 
            WHERE restaurant_nm = %s
            """

db_impl = pymysql.connect(host='localhost'
                        , user='root'
                        , password='qpflqpfl95!'
                        , db='LUNCH'
                        , charset='utf8')

cursor = db_impl.cursor()

while True:
    try:
        print()
        print("원하는 기능을 선택하세요. (추가: a, 수정 : e , 삭제: d, 나가기: exit)")
        print("=================================================================")
        option = input(">>> ")
        # 추가
        if option == 'a':
            while True:
                print("- format -")
                print(" 분류; 한식, 일식, 중식, 양식, 동남아")
                print(" 거리; 근거리: N, 원거리: F")
                print("==========================================================")
                print()
                print(" 음식점 이름, 분류, 거리를 공백으로 구분해 입력하세요")
                print(" * 입력을 중단하려면 'q'를 입력하세요.")
                print()
                menu_info = input(">>> ")
                values = menu_info.split()
                if any(val == 'q' for val in values):
                    break
                elif len(values) != 3:
                    print("------------------------------------------------ 입력 오류\n")
                    continue
                restaurant_nm, classification, distance = values
                cursor.execute(insert_sql, (1, classification, restaurant_nm, distance))
                db_impl.commit()
                print("------------------------------------------------ 저장 완료\n")
        
        # 수정
        elif option == 'e':
            print("==========================================================")
            menu_info = input("수정을 원하는 음식점 이름, 변경데이터(분류, 음식점 이름, 거리 순서)를 공백으로 구분해 입력하세요 >>> ")
            values = menu_info.split()
            if any(val == 'q' for val in values):
                break
            elif len(values) != 4:
                print("------------------------------------------------ 입력오류\n")
                continue
            restaurant_nm, updated_classification, updated_restaurant_nm, update_distance = values
            cursor.execute(update_sql, (updated_classification, updated_restaurant_nm, update_distance, restaurant_nm))
            db_impl.commit()
            print("------------------------------------------------ 저장 완료\n")

        # 삭제
        elif option == 'd':
            restaurnat_nm = input("삭제하고자 하는 음식점 이름을 입력하세요 >>> ")
            cursor.execute(delete_sql, (restaurnat_nm))
            db_impl.commit()
            print("------------------------------------------------ 삭제 완료\n")
        
        # 나가기
        elif option == 'exit':
            break

        else:
            print("------------------------------------------------ 입력 오류\n")
            continue

    except Exception as e:
        print(type(e), e)
        break

try:
    db_impl.close()
    print("--------------------------------------------- DB 연결 종료")

except Exception as e:
    print(f"저장 오류: {type(e)} {e}")