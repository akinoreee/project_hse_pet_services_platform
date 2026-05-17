import urllib, requests, socket, re, lxml, io, bs4, sqlite3, pandas, sqlalchemy
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import undetected_chromedriver as uc
from selenium_stealth import stealth


queries = [
    "выгул собак сайт",
    "груминг домашних животных",
    "уход за домашними питомцами"
]


options = Options()
options.add_argument("--start-maximized")

driver = webdriver.Chrome()
driver.get("https://google.com")
time.sleep(3)

search = driver.find_element(By.NAME, "q")

all_links = []

for i in queries:
    search.send_keys(i)
    search.submit()
    time.sleep(30) #чтобы вручную ввести капчу

    links = driver.find_elements(By.CSS_SELECTOR, "div.g a")

    all_elements = driver.find_elements(By.TAG_NAME, "a")

    count = 0
    for element in all_elements:
        href = element.get_attribute("href")
        if href and "http" in href and "google.com" not in href and not href.startswith("https://support.google"):
            if count < 3:
                all_links.append(href)
                count += 1

    if len(all_links) == 0:
        print('не рабоатет')
        break

    search = driver.find_element(By.NAME, "q")
    search.clear()

driver.quit()
print(all_links)



