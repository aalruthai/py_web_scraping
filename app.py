import sys
import time
import traceback
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.common import exceptions
import time
import sqlite3


def wait_for_non_empty_text(locator):
    """
    This function to check if an element has any text
    """

    def _predicate(driver):
        try:
            element_text =  driver.find_element(*locator).text.strip()
            return element_text != ""
        except exceptions.StaleElementReferenceException:
            return False

    return _predicate    

conn = sqlite3.connect('jodidb.db')

try:
    conn.execute('''
    CREATE TABLE exports
    (country TEXT, month_year TEXT, value int);
    ''')
except:
    pass

def insert_data(country, monthyear, value):
    conn.execute('''
    INSERT INTO exports (country, month_year, value) VALUES (?,?,?)
    ''', (country, monthyear, value))

balanceExportsScript = 'selectItem(2, 3)'

delay = 5

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
# Maximizing window to show as much rows as possible and reduce page scrolling
driver.maximize_window()
url = "http://www.jodidb.org/TableViewer/tableView.aspx?ReportId=93906"

driver.get(url)
# Waiting for Scripts links to be loaded
WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.XPATH, '//a[@href="javascript:onClickSelectOther(2);"]')))
# Setting the balance to Exports by calling the javascript function directly
driver.execute_script(balanceExportsScript)
WebDriverWait(driver, delay).until(wait_for_non_empty_text((By.XPATH, '//table[@id="DataTable"]/tbody/tr[last()]/th')))
time.sleep(2)

# Getting tablr containing data
element = driver.find_element(By.ID, 'DataTable')
# Getting main page container to interact with page
container = element.find_element(By.XPATH, '/html')

time.sleep(3)
# Getting Rows and Columns count from the page's javascript
tableTotalRows = driver.execute_script('return M_tableRowCount;')
tableColumns = driver.execute_script('return M_tableColCount;')

print(f"{tableTotalRows} {tableColumns}")

time.sleep(1)

months = []
countries = []

# Getting Month-Year from table header
head = element.find_element(By.TAG_NAME, 'thead')
headRow = head.find_element(By.TAG_NAME, 'tr')
headRowData = headRow.find_elements(By.CLASS_NAME, 'TVItemColHeader')

for hrd in headRowData:
    months.append(hrd.text)

body = element.find_element(By.TAG_NAME, 'tbody')
rows = body.find_elements(By.TAG_NAME, 'tr')

processedRows = 0
RemainingRows = tableTotalRows
processedRowsTotal = 0
try:
    while RemainingRows > 0:
        
        for row in rows:
            country = row.find_element(By.TAG_NAME, 'th')
            if country.text in countries:
                continue
            countryData = row.find_elements(By.TAG_NAME, 'td')
            print(f'Processing {country.text}...')
            for i in range(0, len(headRowData)):
                insert_data(country.text, headRowData[i].text, countryData[i].text)
                # print(f'{country.text}   {headRowData[i].text}   {countryData[i].text}')
            conn.commit()
            processedRows += 1
            countries.append(country.text)
            
        # Scrolling down page by page, each scroll will cause the table to refilled
        container.send_keys(Keys.PAGE_DOWN)
        # tracking count of processed countries
        RemainingRows = RemainingRows - processedRows
        processedRowsTotal += processedRows
        print(f"iteratiom processed {processedRows}, Total processed {processedRowsTotal}, Remaining {RemainingRows}")
        processedRows = 0
        time.sleep(1)
        rows = body.find_elements(By.TAG_NAME, 'tr')
    

except sqlite3.Error as er:
    print('SQLite error: %s' % (' '.join(er.args)))
    print("Exception class is: ", er.__class__)
    print('SQLite traceback: ')
    exc_type, exc_value, exc_tb = sys.exc_info()
    print(traceback.format_exception(exc_type, exc_value, exc_tb))
finally:
    conn.close()
    driver.quit()

