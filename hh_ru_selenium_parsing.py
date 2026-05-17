import time
import pandas as pd

from urllib.parse import urlencode

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.common.exceptions import (
    TimeoutException,
    WebDriverException,
    NoSuchElementException
)

from webdriver_manager.chrome import ChromeDriverManager


def create_driver():
    options = Options()

    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popup-blocking")

    options.page_load_strategy = "eager"

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    driver.set_page_load_timeout(30)

    return driver


def safe_find_text(parent, selector):
    try:
        element = parent.find_element(By.CSS_SELECTOR, selector)
        text = element.text.strip()
        return text if text else None
    except NoSuchElementException:
        return None


def safe_find_attribute(parent, selector, attribute):
    try:
        element = parent.find_element(By.CSS_SELECTOR, selector)
        return element.get_attribute(attribute)
    except NoSuchElementException:
        return None


def normalize_position(title):
    if not title:
        return None

    text = title.lower()

    if "грумер" in text:
        return "Грумер"

    if "ассистент" in text and "ветеринар" in text:
        return "Ассистент ветеринарного врача"

    if "ветеринарный врач" in text or "ветврач" in text:
        return "Ветеринарный врач"

    if "администратор" in text and ("ветеринар" in text or "ветклиник" in text or "зоосалон" in text or "груминг" in text):
        return "Администратор pet-сервиса"

    if "кинолог" in text:
        return "Кинолог"

    if "догсит" in text or "выгул" in text or "выгульщик" in text:
        return "Догситтер"

    if "зооняня" in text or "котоотель" in text or "отель для кош" in text:
        return "Зооняня"

    return "Другое"


def parse_hh_vacancy_search(query, pages_count=3, area=1):
    rows = []

    driver = create_driver()

    try:
        for page in range(pages_count):
            params = {
                "text": query,
                "area": area,
                "page": page,
                "items_on_page": 50
            }

            url = "https://hh.ru/search/vacancy?" + urlencode(params)

            try:
                driver.get(url)

            except TimeoutException:
                print("Страница слишком долго грузится, пропускаем.")
                continue

            except WebDriverException as error:
                print("Не удалось открыть страницу, пропускаем.")
                print(error)
                continue

            try:
                WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            except TimeoutException:
                print("Не дождались загрузки страницы, пропускаем.")
                continue

            time.sleep(3)

            page_text = driver.find_element(By.TAG_NAME, "body").text.lower()

            if "captcha" in page_text or "подтвердите, что вы человек" in page_text:
                print("hh.ru показал капчу. Эту страницу не парсим.")
                continue

            cards = driver.find_elements(By.CSS_SELECTOR, '[data-qa="vacancy-serp__vacancy"], .serp-item')

            print("Найдено карточек:", len(cards))

            for card in cards:
                raw_card_text = card.text

                title = safe_find_text(card, '[data-qa="serp-item__title"]')

                vacancy_url = safe_find_attribute(card, '[data-qa="serp-item__title"]', "href")

                company = safe_find_text(card, '[data-qa="vacancy-serp__vacancy-employer"]')

                city = safe_find_text(card, '[data-qa="vacancy-serp__vacancy-address"]')

                salary_text = safe_find_text(card, '[data-qa="vacancy-serp__vacancy-compensation"]')

                if not salary_text:
                    salary_text = safe_find_text(card, '[data-qa="vacancy-serp__vacancy-salary"]')

                experience = safe_find_text(card, '[data-qa="vacancy-serp__vacancy-work-experience"]')

                rows.append({
                    "source": "hh.ru selenium",
                    "search_query": query,
                    "title": title,
                    "position_group": normalize_position(title),
                    "company": company,
                    "city": city,
                    "salary_text": salary_text,
                    "experience": experience,
                    "url": vacancy_url,
                    "raw_card_text": raw_card_text
                })

            time.sleep(2)

    finally:
        driver.quit()

    return pd.DataFrame(rows)


queries = [
    "груминг",
    "грумер",
    "ветеринар",
    "ветклиника",
    "ассистент ветеринарного врача",
    "зоосалон",
    "зооняня",
    "администратор зоосалона",
    "администратор ветеринарной клиники",
    "догситтер",
    "котоотель",
    "отель для кош",
    "отель для собак",
    "уход за животными",
    "уход за собаками",
    "уход за кошками",
    "животные",
    "зоогостиниц"
]

all_dfs = []

for query in queries:
    df_query = parse_hh_vacancy_search(query=query, pages_count=3, area=1)

    all_dfs.append(df_query)

df_hh_raw = pd.concat(all_dfs, ignore_index=True)

df_hh_raw = df_hh_raw.drop_duplicates(subset=["title", "company", "url"], keep="first").reset_index(drop=True)

df_hh_raw.to_csv("hh_pet_vacancies_raw_cards.csv", index=False, encoding="utf-8-sig")

print("Размер датафрейма:", df_hh_raw.shape)
