import time
import pandas
import math
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.common import exceptions
from bs4 import BeautifulSoup
import time

class wait_for_non_empty_text(object):
    def __init__(self, locator):
        self.locator = locator

    def __call__(self, driver):
        try:
            element_text = EC._find_element(driver, self.locator).text.strip()
            return element_text != ""
        except exceptions.StaleElementReferenceException:
            return False

def wait_for_non_empty_textf(locator):
    

    def _predicate(driver):
        try:
            element_text =  driver.find_element(*locator).text.strip()
            return element_text != ""
        except exceptions.StaleElementReferenceException:
            return False

    return _predicate    
balance = "Exports"

delay = 5

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
# Maximizing window to show as much rows as possible and reduce page scrollin
driver.maximize_window()
url = "http://www.jodidb.org/TableViewer/tableView.aspx?ReportId=93906"

driver.get(url)

WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.XPATH, '//a[@href="javascript:onClickSelectOther(2);"]')))
# Setting the balance to Exports by calling the javascript function directly
driver.execute_script('selectItem(2, 3)')
WebDriverWait(driver, delay).until(wait_for_non_empty_textf((By.XPATH, '//table[@id="DataTable"]/tbody/tr[last()]/th')))
time.sleep(2)

# WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.ID, 'RetrieveData')))
# WebDriverWait(driver, delay).until(EC.visibility_of((By.ID, 'DataTable')))
# body = driver.find_element(By.CLASS_NAME, 'DataTable')
# print(body.get_attribute('innrerHtml'))
# rows = body.find_elements(By.TAG_NAME, 'tr')
element = driver.find_element(By.ID, 'DataTable')
container = element.find_element(By.XPATH, '/html')
print(element.get_attribute('style'))
print('Waiting...')
print(container.get_attribute('align'))
time.sleep(3)
tableTotalRows = driver.execute_script('return M_tableRowCount;')
tableColumns = driver.execute_script('return M_tableColCount;')

print(f"{tableTotalRows} {tableColumns}")
# driver.execute_script('window.scrollBy(0,document.body.scrollHeight)')
time.sleep(1)
months = []
countries = []

# WebDriverWait(driver, delay).until(EC.visibility_of(element))
#WebDriverWait(driver, delay).until(EC.(element))
head = element.find_element(By.TAG_NAME, 'thead')
headRow = head.find_element(By.TAG_NAME, 'tr')
headRowData = headRow.find_elements(By.CLASS_NAME, 'TVItemColHeader')
# for hrd in headRowData:
#     # print(hrd.text)
#     months.append(hrd.text)
    
body = element.find_element(By.TAG_NAME, 'tbody')
rows = body.find_elements(By.TAG_NAME, 'tr')
visibleRowsCount = len(rows)
print(visibleRowsCount)
processedRows = 0
RemainingRows = tableTotalRows

pages = math.ceil(tableTotalRows / visibleRowsCount)
print(pages)
while RemainingRows > 0:
    # print(f"page {page}")
    # if RemainingRows >= visibleRowsCount:
    for row in rows:
        country = row.find_element(By.TAG_NAME, 'th')
        if country.text in countries:
            continue
        countryData = row.find_elements(By.TAG_NAME, 'td')
        print(country.text)
        # for i in range(0, len(headRowData)):
        #     print(f'{country.text}   {headRowData[i].text}   {countryData[i].text}')
        processedRows += 1
        countries.append(country.text)
        # tds = row.find_elements(By.TAG_NAME, 'td')
        # for td in tds:
        #     print(td.text)
    # else:
    #     lastRowsCount = len(rows)
    #     rowsToByPass = lastRowsCount - RemainingRows
    #     for i in range(rowsToByPass, lastRowsCount):
    #         country = rows[i].find_element(By.TAG_NAME, 'th')
    #         print(country.text)
    #         processedRows += 1
    container.send_keys(Keys.PAGE_DOWN)
    RemainingRows = RemainingRows - processedRows
    print(f"processed {processedRows}, Remaining {RemainingRows}")
    processedRows = 0
    time.sleep(1)
    rows = body.find_elements(By.TAG_NAME, 'tr')
# with open("f1.txt","w") as file:
#     # for m in months:
#     #     file.write(f"{m}\n")
    
#     for c in countries:
#         file.write(f"{c}\n")
        
print("sss")
# exporstLink = btn.find_element(By.ID, 'a-el-d2-mi3')
# print(exporstLink.text)

# btn.click()
# try:
#     WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.CLASS_NAME, 'DataTable')))
#     WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.CLASS_NAME, 'DataTable')))
# except TimeoutException: 
#     print('Timedout')
# else:
#     with open('test.html', 'w', encoding='utf-8') as file:
#         file.write(driver.page_source)
# finally:
#     driver.quit()