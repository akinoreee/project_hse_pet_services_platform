import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

url = "https://murchalkin.ru"

options = Options()
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

driver.get(url)
time.sleep(3)
soup = BeautifulSoup(driver.page_source, 'html.parser')

reasons_elements = soup.find_all(class_='b-trust__title-text')
reasons = []
for reason in reasons_elements:
    text = reason.get_text(strip=True).replace('\xa0', ' ')
    reasons.append(text)

print("Причины доверять:", reasons)


price_header = driver.find_element(By.XPATH, "//h2[contains(text(), 'Стоимость передержки')]")
driver.execute_script("arguments[0].scrollIntoView(true);", price_header)
time.sleep(2)

WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CLASS_NAME, "b-service-plate"))
)

soup = BeautifulSoup(driver.page_source, 'html.parser')

service_plates = soup.find_all('div', class_='b-service-plate')

services = []
for plate in service_plates:
    title = plate.find('div', class_='b-service-plate__title')
    price = plate.find('div', class_='b-service-plate__price')

    if title:
        service_name = title.get_text(strip=True)
        service_price = price.get_text(strip=True)
        services.append(f"{service_name}: {service_price}")

driver.quit()

print("Услуги:", services)