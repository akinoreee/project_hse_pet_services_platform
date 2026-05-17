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


url = "https://dogsy.ru"
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}


response = requests.get(url, headers=headers)
response.raise_for_status()  # Проверяем, успешно ли загрузилась страница
soup = BeautifulSoup(response.text, 'html.parser')

#print(soup)

dropdown_menu = soup.find('ul', class_='dropdown-menu')
services = dropdown_menu.find_all('a')

uslugi = []

for service in services:
    service_name = service.get_text(strip=True)
    uslugi.append(service_name)

print("Список услуг:", uslugi)


safety_points = []
safety = soup.find('h2', string=lambda text: text and 'Почему это безопасно' in text)

parent_section = safety.find_parent()

safety_items = parent_section.find_all('h3', class_='index-safety__list-title')
for item in safety_items:
    title = item.get_text(strip=True).replace('\xa0', '')
    safety_points.append(title)

print("Почему безопасно:", safety_points)