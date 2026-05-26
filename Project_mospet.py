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

url = "https://pets.mos.ru"

options = Options()
options.add_argument('--headless')
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_experimental_option("excludeSwitches", ["enable-automation"])

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

driver.get(url)
time.sleep(3)
soup = BeautifulSoup(driver.page_source, 'html.parser')
driver.quit()


services = []


links = soup.find_all('a', href=lambda x: x and x.startswith('#'))
for link in links:
    text = link.get_text(strip=True)
    if text and 3 < len(text) < 50 and text not in services:
        if 'скачать' not in text.lower() and 'содерж' not in text.lower():
            services.append(text)

print('Услуги:', services)




