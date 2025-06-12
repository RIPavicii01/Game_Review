import time
import random
import pandas as pd
import math
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, WebDriverException

url_list = [
    "https://www.metacritic.com/game/the-legend-of-zelda-breath-of-the-wild/critic-reviews/?platform=nintendo-switch",
    "https://www.metacritic.com/game/the-legend-of-zelda-breath-of-the-wild/user-reviews/?platform=nintendo-switch",
    "https://www.metacritic.com/game/the-legend-of-zelda-tears-of-the-kingdom/critic-reviews/?platform=nintendo-switch",
    "https://www.metacritic.com/game/the-legend-of-zelda-tears-of-the-kingdom/user-reviews/?platform=nintendo-switch",
    "https://www.metacritic.com/game/super-mario-odyssey/critic-reviews/?platform=nintendo-switch",
    "https://www.metacritic.com/game/super-mario-odyssey/user-reviews/?platform=nintendo-switch",
    "https://www.metacritic.com/game/super-mario-bros-wonder/critic-reviews/?platform=nintendo-switch",
    "https://www.metacritic.com/game/super-mario-bros-wonder/user-reviews/?platform=nintendo-switch",
    "https://www.metacritic.com/game/super-mario-rpg/critic-reviews/?platform=nintendo-switch",
    "https://www.metacritic.com/game/super-mario-rpg/user-reviews/?platform=nintendo-switch",
    "https://www.metacritic.com/game/mario-kart-8-deluxe/critic-reviews/?platform=nintendo-switch",
    "https://www.metacritic.com/game/mario-kart-8-deluxe/user-reviews/?platform=nintendo-switch",
    "https://www.metacritic.com/game/animal-crossing-new-horizons/critic-reviews/?platform=nintendo-switch",
    "https://www.metacritic.com/game/animal-crossing-new-horizons/user-reviews/?platform=nintendo-switch",
    "https://www.metacritic.com/game/splatoon-2/critic-reviews/?platform=nintendo-switch",
    "https://www.metacritic.com/game/splatoon-2/user-reviews/?platform=nintendo-switch",
    "https://www.metacritic.com/game/splatoon-3/critic-reviews/?platform=nintendo-switch",
    "https://www.metacritic.com/game/splatoon-3/user-reviews/?platform=nintendo-switch",
    "https://www.metacritic.com/game/astral-chain/critic-reviews/?platform=nintendo-switch",
    "https://www.metacritic.com/game/astral-chain/user-reviews/?platform=nintendo-switch",
    "https://www.metacritic.com/game/pokemon-sword/critic-reviews/?platform=nintendo-switch",
    "https://www.metacritic.com/game/pokemon-sword/user-reviews/?platform=nintendo-switch"
]
game_name_list = [
    "The Legend of Zelda: Breath of the Wild",
    "The Legend of Zelda: Breath of the Wild",
    "The Legend of Zelda: Tears of the Kingdom",
    "The Legend of Zelda: Tears of the Kingdom",
    "Super Mario Odyssey",
    "Super Mario Odyssey",
    "Super Mario Bros. Wonder",
    "Super Mario Bros. Wonder",
    "Super Mario RPG",
    "Super Mario RPG",
    "Mario Kart 8 Deluxe",
    "Mario Kart 8 Deluxe",
    "Animal Crossing: New Horizons",
    "Animal Crossing: New Horizons",
    "Splatoon 2",
    "Splatoon 2",
    "Splatoon 3",
    "Splatoon 3",
    "Astral Chain",
    "Astral Chain",
    "Pokemon Sword",
    "Pokemon Sword"
]
chrome_driver_path = "./chromedriver-win64/chromedriver.exe"

options = Options()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_argument("--window-size=1200,1000")
options.page_load_strategy = 'eager'
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
options.add_argument(f"user-agent={user_agent}")
# options.add_argument("--headless") # 필요시 주석 해제

service = Service(executable_path=chrome_driver_path)
driver = webdriver.Chrome(service=service, options=options)
driver.implicitly_wait(30)

driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
    "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
})

def get_review_type_from_url(url):
    if 'critic-reviews' in url:
        return 'critic-review'
    elif 'user-reviews' in url:
        return 'user-reviews'
    return '기타'

MAX_REVIEWS_PER_TYPE = 10000
SPLIT_SIZE = 10000

all_reviews = []

for idx, url in enumerate(url_list):
    print(f"\n▶️ {idx+1}번 경로 다운로드 시작 [{url}]")
    retries = 3
    for attempt in range(1, retries + 1):
        try:
            driver.get(url)
            time.sleep(3)
            try:
                driver.find_element(By.ID, "onetrust-accept-btn-handler").click()
                time.sleep(1)
            except:
                pass
            break
        except (TimeoutException, WebDriverException) as e:
            print(f"⚠️ {attempt}회 시도 실패... 15초 후 재시도 ({e})")
            time.sleep(15)
            if attempt == retries:
                print(f"🚨 최종 실패: {url} (다음 URL로)")
                continue

    game_name = game_name_list[idx]
    review_type = get_review_type_from_url(url)
    reviews = []

    # 리뷰 수집
    if review_type == 'user-reviews':
        last_reviews_count = -1
        scroll_try = 0
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(random.uniform(1.5, 2.2))
            reviews = driver.find_elements(By.CSS_SELECTOR, "div.c-siteReview")
            if len(reviews) >= MAX_REVIEWS_PER_TYPE:
                break
            if last_reviews_count == len(reviews):
                scroll_try += 1
            else:
                scroll_try = 0
            if scroll_try > 5:
                break
            last_reviews_count = len(reviews)
    else:  # critic-reviews
        review_elems_total = []
        page = 0
        while True:
            current_reviews = driver.find_elements(By.CSS_SELECTOR, "div.c-siteReview")
            for r in current_reviews:
                if r not in review_elems_total:
                    review_elems_total.append(r)
            if len(review_elems_total) >= MAX_REVIEWS_PER_TYPE:
                break
            try:
                next_btn = driver.find_element(By.CSS_SELECTOR, 'button.c-paginationBtn[aria-label="Go to next page"]')
                if not next_btn.is_enabled():
                    break
                next_btn.click()
                time.sleep(random.uniform(2, 3))
                page += 1
            except Exception:
                break
        reviews = review_elems_total

    # 실제 데이터 파싱
    review_data_count = 0
    for review in reviews[:MAX_REVIEWS_PER_TYPE]:
        try:
            date = review.find_element(By.CSS_SELECTOR, "div.c-siteReviewHeader_reviewDate").text
            score = review.find_element(By.CSS_SELECTOR, "div.c-siteReviewScore span").text
            text = review.find_element(By.CSS_SELECTOR, "div.c-siteReview_quote span").text
            all_reviews.append({
                'Game': game_name,
                'Type': review_type,
                'Date': date,
                'Score': score,
                'Text': text
            })
            review_data_count += 1
        except Exception as e:
            pass  # 오류난 리뷰는 패스

    print(f"   → [{idx+1}번] {game_name} ({review_type}) : {review_data_count}개 다운로드 완료.")

driver.quit()

df = pd.DataFrame(all_reviews, columns=['Game', 'Type', 'Date', 'Score', 'Text'])

# 분할 저장
total_len = len(df)
total_files = math.ceil(total_len / SPLIT_SIZE)
for i in range(total_files):
    start = i * SPLIT_SIZE
    end = min(start + SPLIT_SIZE, total_len)
    split_df = df.iloc[start:end]
    filename = f"all_metacritic_reviews{i+1}.csv"
    split_df.to_csv(filename, index=False, encoding='utf-8-sig')
    print(f"✅ {filename} 저장 완료! (row {start} ~ {end-1})")
print("\n✅ 전체 수집 완료! (총 데이터 수: {})".format(total_len))
