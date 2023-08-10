from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time


# 기본 설정
url = "https://map.naver.com/v5/search"
keyWord = "음식점"
option = webdriver.ChromeOptions()
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=option)
driver.get(url)


informations = {}


def search():
    # 페이지 로딩 기다리기 10초 -> 이전에 로딩 끝나면 다음 코드 실행
    driver.implicitly_wait(10)
    # xpath로 검색창 찾기
    searchInput = driver.find_element(By.XPATH, '/html/body/app/layout/div[3]/div[2]/shrinkable-layout/div/app-base/search-input-box/div/div/div/input')

    # 키워드 입력하고 이걸로 검색
    # keyWord 변수에 다른 입력 값 집어 넣으면 다른거 나옴
    searchInput.send_keys(keyWord)
    searchInput.send_keys(Keys.ENTER)

    # 로딩 기다리기
    time.sleep(1)


def switchFrame(frame):
    driver.switch_to.default_content()  # frame 초기화
    driver.switch_to.frame(frame)  # frame 변경


def scrollDown():
    # 음식점들 로딩을 위해서 스크롤 다운
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'body')))
    body = driver.find_element(By.CSS_SELECTOR, 'body')
    body.click()
    for i in range(40):
        body.send_keys(Keys.PAGE_DOWN)
    time.sleep(0.2)
    body.send_keys(Keys.HOME)



def getInformations():
    #기본 인덱스 1부터 시작
    idx = 1
    while(True):
        # 일단 기다려
        time.sleep(0.5)
        # 검색창 -> 음식점들 창으로 프레임 이동
        switchFrame('searchIframe')

        try:
            # 이름 엘리먼트 가지고 있는데 페이지 내 마지막일수도 있으니까 try로 잡아줌
            nameElement = driver.find_element(By.CSS_SELECTOR, '#_pcmap_list_scroll_container > ul > li:nth-child('+str(idx)+') > div.CHC5F > a > div > div')
        except:
            # 마지막 엘리먼트일 경우 인덱스 다시 1로 바꾸고 화살표 눌러서 다음 화면으로
            idx = 1
            arrowElement = driver.find_element(
                By.CSS_SELECTOR, '#app-root > div > div.XUrfU > div.zRM9F > a:nth-child(7)')
            html = arrowElement.get_attribute('outerHTML')
            soup = BeautifulSoup(html, 'html.parser')
            arrow = soup.select('a')[0]['aria-disabled']
            if(arrow == 'false'):
                arrowElement.click()
                time.sleep(2)
                nameElement = WebDriverWait(driver, 1).until(EC.element_to_be_clickable((By.CSS_SELECTOR,
                                                                                     '#_pcmap_list_scroll_container > ul > li:nth-child(' + str(
                                                                                          idx) + ') > div.CHC5F > a > div > div')))
            else:
                break

        # bs4로 파싱 후 이름이랑 카테고리 빼옴
        html = nameElement.get_attribute('innerHTML')
        soup = BeautifulSoup(html, 'html.parser')
        name = soup.select('span')[0].text
        category = soup.select('span')[-1].text




        # 이름 클릭해서 음식점 상세 정보로 이동
        nameElement.click()

        # 기다려
        time.sleep(0.7)
        # 상세 페이지로 프레임 옮기기
        switchFrame("entryIframe")

        #bs4로 상세 페이지 파싱
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        try:
            # 주소 없을수도 있으니까 try로 걸러
            roadAddress = soup.select_one('#app-root > div > div > div > div:nth-child(6) > div > div.place_section.no_margin.vKA6F > div > div > div.O8qbU.tQY7D > div > a > span.LDgIH').text

        except:
            # 사실 오류 잡으려고 넣은거
            roadAddress = '주소 없음'
        try:
            # 별점도 없을수도있으니까 없으면 -1로 처리
            star = soup.select_one('#app-root > div > div > div > div.place_section.OP4V8 > div.zD5Nm.f7aZ0 > div.dAsGb > span.PXMot.LXIwF > em').text
            star = float(star)
        except:
            star = -1

        # 인덱스 계속 올리고
        idx+=1
        # 딕셔너리에 카테고리, 주소, 별점 순으로 저장
        informations[name] = [category, roadAddress, star]


search()
scrollDown()
getInformations()

# informations에 저장됨
print(informations)