from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time

from pymongo import MongoClient



# localhost 용 MongoDB 연결
client = MongoClient("localhost", 27017)

# 서버용 MongoDB 연결
# client = MongoClient('mongodb://test:test@localhost', 27017)

db = client.toyproj

# 셀레니움에 쓸 크롬 드라이버 시작
driver = webdriver.Chrome()

# 네이버지도 들어가기
driver.get("https://map.naver.com/v5")
time.sleep(1)

# 주소창 찾기
elem = driver.find_element_by_css_selector("#container > shrinkable-layout > div > app-base > search-input-box > div > div > div > input")

# 검색어 설정.
seoul_gus = ["도봉구 맛집", "노원구 맛집", "강북구 맛집", "은평구 맛집","성북구 맛집", "중랑구 맛집","동대문구 맛집","종로구 맛집","서대문구 맛집",
            "중구 맛집", "성동구 맛집","광진구 맛집","용산구 맛집","마포구 맛집", "강서구 맛집","양천구 맛집","구로구 맛집","영등포구 맛집","동작구 맛집","금천구 맛집",
           "관악구 맛집","서초구 맛집","강남구 맛집","송파구 맛집","강동구 맛집"]

# 검색어 입력
for seoul_gu in seoul_gus:
    print(seoul_gu, "크롤링 중...")
    elem.clear()
    elem.send_keys(seoul_gu)
    elem.send_keys(Keys.RETURN)
    time.sleep(3)

    # 맛집 정보 찾기 / 셀레니움은 iframe 태그 내부 요소를 인식하지 못하기 때문에 switch 해줘야 한다.
    searchiframe = driver.find_element_by_id("searchIframe")
    driver.switch_to.frame(searchiframe)

    # 다음 페이지 버튼이 잠겨있을경우 다음구로 넘어가기.
    try:
        pagebar = driver.find_element_by_class_name("_34lTS").text
        print(pagebar)
    except:
        pass
    page = 1

    while pagebar != "다음페이지":
        # iframe 스크롤 내리기 ( 무식한 방법 ) / iframe 내부의 요소를 지정하여 그곳까지 이동. 자동으로 끝까지 내리게 하고싶은데.. 이 방법도 기능적으로 문제는 없음.
        actions = ActionChains(driver)

        scroll1 = driver.find_element_by_css_selector("#_pcmap_list_scroll_container > ul > li:nth-child(10)")
        actions.move_to_element(scroll1).perform()
        time.sleep(3)

        scroll2 = driver.find_element_by_css_selector("#_pcmap_list_scroll_container > ul > li:nth-child(20)")
        actions.move_to_element(scroll2).perform()
        time.sleep(3)

        scroll3 = driver.find_element_by_css_selector("#_pcmap_list_scroll_container > ul > li:nth-child(30)")
        actions.move_to_element(scroll3).perform()
        time.sleep(3)

        scroll4 = driver.find_element_by_css_selector("#_pcmap_list_scroll_container > ul > li:nth-child(40)")
        actions.move_to_element(scroll4).perform()
        time.sleep(3)

        scroll5 = driver.find_element_by_css_selector("#_pcmap_list_scroll_container > ul > li:nth-child(50)")
        actions.move_to_element(scroll4).perform()
        time.sleep(3)
        # 전체 자료 그룹화
        shops = driver.find_elements_by_class_name("_1EKsQ")

        print(page," 페이지 크롤링...")
        for shop in shops:

            # 클릭해서 상세정보 띄우기 및 데이터 크롤링

            try: # 클릭이 안되는 점포 제외
                shop.find_element_by_css_selector("div._3hn9q").click()
                time.sleep(3) # 3초로 설정하면 에러는 왠만하면 나오지 않습니다. ec2에 올려서 작동시킬때는 더 길게 설정해야 할 수도 있습니다.
                driver.switch_to.default_content()

                entryiframe = driver.find_element_by_id("entryIframe")
                driver.switch_to.frame(entryiframe)

                try:  # 별점이 없는 가게 에러체크
                    rating = driver.find_element_by_class_name("_1A8_M").text.replace("/5", "").replace("별점", "").replace(
                        '\n', "")
                except:
                    rating = ""
                name = driver.find_element_by_class_name("_3XamX").text
                category = driver.find_element_by_class_name("_3ocDE").text
                address = driver.find_element_by_class_name("_2yqUQ").text
                imgsrc = driver.find_element_by_class_name("cb7hz").get_attribute("style").split('"')[1].split('"')[0]

                if rating != "":    # 별점이 없는 점포는 저장하지 않는다.
                    doc = {
                        "name": name,
                        "rating": rating,
                        "category": category,
                        "address": address,
                        "imgsrc": imgsrc,
                        "like": 0,
                        "review": []
                    }
                    print(doc)
                    db.shops.insert_one(doc)
                    driver.switch_to.default_content()
                    driver.switch_to.frame(searchiframe)
            except:
                driver.switch_to.default_content()
                driver.switch_to.frame(searchiframe)

        page = page + 1
        try:
            pagebar = driver.find_element_by_class_name("_34lTS").text
        except:
            pass
        pagebar = "다음페이지"
        print(pagebar)
        time.sleep(1)
        # next = driver.find_element_by_css_selector("#app-root > div > div._2lx2y > div._2ky45 > a:nth-child(7)") ---> 이놈이 에러가 계속 납니다...
        # print(next.text)
        # next.click()
        # time.sleep(2)
    driver.switch_to.default_content()
    print(seoul_gu, "크롤링 끝...")

driver.close()