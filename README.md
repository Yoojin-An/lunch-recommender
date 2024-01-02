# 점심메뉴 추천
#### 회사에서 매일 하는 고민.. '오늘 점심 뭐 먹지?🙄'</br>팀을 위해 점심 메뉴 선정을 자동화했습니다. 매일 11시 20분이면 구글 챗으로 점심 메뉴 알림이 도착합니다.

### ⚙ 실행 환경
* <img src="https://img.shields.io/badge/Python-3776AB?style=flat&logo=Python&logoColor=white"> 3.11.6 </br>
* <img src="https://img.shields.io/badge/Redis-DC382D?style=flat&logo=Redis&logoColor=white"> 7.0.9 </br>
* <img src="https://img.shields.io/badge/MySQL-4479A1?style=flat&logo=MySQL&logoColor=white"> 8.1.0 </br>
* <img src="https://img.shields.io/badge/Rocky Linux-10B981?style=flat&logo=Rocky Linux&logoColor=white"> 8.6
<br> <br>

### ⌨️ 실행 방식
 * crontab으로 주중 매일 11시 20분에 프로그램 실행을 위한 쉘 스크립트 자동 실행(공휴일 제외)
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

        -- 메뉴 테이블 trigger 생성(id_no 기준으로 seq_no 부여)
        DELIMITER $$
        CREATE TRIGGER set_seq_no
        BEFORE INSERT ON lnch_menu
        FOR EACH ROW
        SET NEW.seq_no = COALESCE((SELECT MAX(seq_no) FROM lnch_menu WHERE id_no = NEW.id_no), 0) + 1;$$
        DELIMITER ;

        -- 메뉴 테이블
        CREATE TABLE lnch_menu (
        ID_NO int comment 'lnch_user.SEQ_NO',
        SEQ_NO int comment 'ID_NO에 따른 일련번호',
        CLASSIFICATION varchar(10) comment '한식/양식/중식/일식/기타',
        RESTAURANT_NM varchar(10) comment '음식점 이름',
        DISTANCE varchar(2) comment 'N: 근거리, F: 원거리'
        );

        -- 기록 테이블
        CREATE TABLE lnch_record (
        YYYYMMDD date,
        RESTAURANT_NM varchar(10)
        );
<br>

### 👀 메뉴 선택 옵션
 * d: 거리(all/near, default: all)
 * ex: 제외할 음식 종류나 음식점 이름(lnch_menu.CLASSIFICATION(음식 종류) 또는 lnch_menu.RESTAURANT_NM(음식점 이름)과 매핑, default: None)
 * priority: 우선순위로 적용할 음식 종류나 음식점 이름(lnch_menu와의 매핑 정보는 ex와 동일) <br>
 
<br>


### 🔎 서비스 로직
 1. 사용자는 점심 메뉴 선정 전 우선순위 후보 등록을 할 수 있다.
 2. 메뉴 선택 옵션에 따라 데이터셋을 구성한다.<br>

    ① 거리 옵션(d)에 따른 데이터셋 선택<br>
    &nbsp;&nbsp;: d 값이 all이면 lnch_menu.DISTANCE가 N(near), F(far)인 row 모두, <br>
    &nbsp;&nbsp;&nbsp;&nbsp;d 값이 near이면 N인 row만 읽어와 최초 데이터셋을 구성한다.

    ② REDIS에 우선순위 후보에 대한 데이터가 존재하면 아래 기준에 따라 우선순위를 선정한다.<br>
    &nbsp;&nbsp;: 1) 최다 득표, 2) 득표 수 동률 시 등록 순서

    ③ 데이터셋에 우선순위(priority) 및 제외(ex) 옵션 적용

        * ex가 존재하는 경우
          - ex 값이 음식 종류이면 ① 결과에서 제외할 음식 종류에 해당되는 음식점을 모두 제외시킨다.
          - ex 값이 음식점 이름이면 ① 결과에서 해당 음식점을 제외시킨다.

        * priority가 존재하는 경우
          - prioirty가 음식 종류이면 ex 옵션 적용 결과에서 priority에 해당되는 음식점 리스트만 남긴다.
          - prioirty가 음식점 이름이면 해당 음식점으로 점심메뉴를 추천한다.
 
    ④ lnch_record 테이블에서 어제 먹은 메뉴를 불러와 데이터셋에서 삭제
    <br><br>

 3. 2.에서 구성한 데이터셋에서 random 모듈을 사용해 메뉴를 선정한다.
 

 4. webhook으로 구글채팅 '점심 메뉴 알림' 스페이스에 점심메뉴 추천 결과를 전달한다.
 

 5. lnch_record 테이블에 오늘 날짜와 점심메뉴 추천 결과를 저장한다.


&nbsp;&nbsp;&nbsp;&nbsp;※ 거리와 제외 메뉴 옵션을 적용시키고 싶으면 아래와 같이 인자를 전달해 메뉴 추천 프로그램을 수동으로 실행시킨다.<br><br><br>
 

 ### 🎲 메뉴 추천 프로그램 수동 실행
    python3 main.py -d [거리] -ex [제외할 음식 종류나 음식점]
<br>

 ### 🏷️ 음식점 등록
    python3 menu_registrant.py
<br>

 ### 🥇 우선순위 등록
    python3 priority_registrant.py
 <br>
