# 점심메뉴 추천

### ⚙ 실행 환경
* Python 3.11.6
* Redis 7.0.9
* MySQL 8.1.0
* Rocky Linux
<br> <br>

### ⌨️ 실행 방식
 * crontab과 쉘 스크립트로 주중 매일 11시 20분에 실행
 * 스크립트 참조 경로: ~/.bash_profile에 정의된 $LUNCH_PATH 하위의 lunch.sh
<br> <br>


### 🗂️ 사용 테이블
 * lnch_user; 유저 테이블
 * lnch_menu; 메뉴 종류 테이블
 * lnch_record; 일별 추천메뉴 기록 테이블<br>

        * DDL
        -- 유저 테이블
        CREATE TABLE lnch_user (
        SEQ_NO int not null auto_increment primary key comment '일련번호',
        ID varchar(10) unique,
        PW varchar(12)
        );

        -- 메뉴 테이블
        CREATE TABLE lnch_menu (
        ID_NO int comment 'lnch_user.SEQ_NO',
        SEQ_NO int comment 'ID_NO에 따른 일련번호',
        CLASSIFICATION varchar(10) comment '한식/양식/중식/일식/기타',
        RESTAURANT_NM varchar(10) comment '음식점 이름',
        DISTANCE varchar(2) comment 'N: 근거리, F: 원거리'
        );

        -- 메뉴 테이블 - id_no 기준으로 seq_no를 생성하도록 trigger 생성
        DELIMITER $$
        CREATE TRIGGER set_seq_no
        BEFORE INSERT ON lnch_menu
        FOR EACH ROW
        SET NEW.seq_no = COALESCE((SELECT MAX(seq_no) FROM lnch_menu WHERE id_no = NEW.id_no), 0) + 1;$$
        DELIMITER ;

        -- 기록 테이블
        CREATE TABLE lnch_record (
        YYYYMMDD date,
        RESTAURANT_NM varchar(10)
        );
<br>

### 👀 메뉴 선택 옵션
 * ex: 제외할 음식 종류나 음식점 이름(default: None, lnch_menu.CLASSIFICATION 또는 lnch_menu.RESTAURANT_NM과 매핑)
 * in: 포함할 음식 종류(default: None, lnch_menu.CLASSIFICATION과 매핑)
 * d: 거리(default: near, all/near)
<br> <br>


### 🔎 실행 로직
 1. 메뉴 선택 옵션에 따라 데이터셋을 구성한다.<br>

    ① 거리 옵션(d)에 따른 데이터셋 선택<br>
    &nbsp;&nbsp;: d 값이 all이면 lnch_menu.DISTANCE가 N(near), F(far)인 row 모두, <br>
    &nbsp;&nbsp;&nbsp;&nbsp;d 값이 near이면 N인 row만 읽어와 최초 데이터셋을 구성한다.

    ② 데이터셋에 우선순위(priority) 및 제외(ex) 옵션 적용

        * ex가 존재하는 경우
         - ex 값이 음식 종류이면 ① 결과에서 제외할 음식 종류에 해당되는 음식점을 모두 제외시킨다.
         - ex 값이 음식점 이름이면 ① 결과에서 해당 음식점을 제외시킨다.

        * priority가 존재하는 경우
          - prioirty가 음식 종류이면 ex 옵션 적용 결과에서 priority에 해당되는 음식점 리스트만 남긴다.
          - prioirty가 음식점 이름이면 해당 음식점으로 점심메뉴를 추천한다.
 
    ③ lnch_record 테이블에서 어제 먹은 메뉴를 불러와 데이터셋에서 삭제
    <br><br>

 2. 1.에서 구성한 데이터셋에서 random 모듈을 사용해 메뉴를 선정한다.
 

 3. webhook으로 구글채팅 '점심 메뉴 알림' 스페이스에 점심메뉴 추천 결과를 전달한다.
 

 4. lnch_record 테이블에 오늘 날짜와 점심메뉴 추천 결과를 저장한다.<br><br>


 ### 📍음식점 등록 방법
    python3 menu_registrant.py


<br>

 ### 🔮 우선순위 등록 방법
    python3 priority_registrant.py
    
    * 우선순위는 1) 최다 득표, 2) 득표 수 동률 시 우선 등록 기준으로 선정
 <br>