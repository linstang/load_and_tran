from selenium.webdriver import Chrome
import getpass
from selenium.webdriver.remote.webdriver import WebDriver
import gzip
import time
import cx_Oracle

browser = Chrome()

def get_job(browser: WebDriver) -> str:
    rows = browser.find_elements_by_css_selector('tr.table_row')

    for row in rows:
        cells = row.find_elements_by_tag_name('td')
        for i, c in enumerate(cells):
            if c.text == 'AUTOMATION':
                tran_run_id= cells[i+10].text
                return tran_run_id

browser.get('https://eit1-i.svcs.hp.com/cds/') # Site-Minder url
USER1=input("Please enter the User Name:")
PASSWORD1 = getpass.getpass("Password: ")

email = browser.find_element_by_css_selector('input[name="USER"]')
email.send_keys(USER1)

password = browser.find_element_by_css_selector('input[name="PASSWORD"]')
password.send_keys(PASSWORD1)

logon = browser.find_element_by_css_selector('input.btn.btn-primary')
logon.click()

browser.get('https://eit1-i.svcs.hp.com/cds/LoadLdssAsync')

load_option = browser.find_element_by_id('UploadOptionList')
load_option.send_keys('Validate Only')

file_selector = browser.find_element_by_id('ldssfile')
file_selector.send_keys(r'C:\Users\tangjing\Desktop\Auto-Reg\Automation.xlsx')

upload = browser.find_element_by_css_selector('input[value="Upload"]')
upload.click()

console =  browser.find_element_by_link_text('CDS Console')
console.click()

submitter = browser.find_element_by_id('Filters_Submitter')
submitter.clear()

submitter = browser.find_element_by_id('Filters_Submitter')
submitter.send_keys(USER1)

show = browser.find_element_by_id('Filters_Timefilterval')
show.send_keys('Last 1 week')

Apply_Filter = browser.find_element_by_id('ApplyFilterButton')
Apply_Filter.click()

jobs = get_job(browser)

conn = cx_Oracle.connect('cds/cds123@eitracp-scan01.eit.ssn.hp.com:1521/EONBEIT_ONBAPPL')
cursor = conn.cursor()
time.sleep(30)
sql = 'select tran_run_id, ldss from  tran_run_download where tran_run_id = :id'
sql1 = 'select status,tran_run_id from tran_run_download where tran_run_id = :id1'
def search_job(sql1,cursor):
    cursor.execute(sql1, id1 = jobs)
    result1 = cursor.fetchall()
    return result1
     
def dld_ldss(sql,cursor):
    cursor.execute(sql,id = jobs)
    result = cursor.fetchall()
    wkt = result[0][1].read()  # compressed binary bytes
    ret = gzip.decompress(wkt)
    with open(r'C:\Users\tangjing\Desktop\Auto-Reg\ldss.xlsx', 'wb') as b2:
        b2.write(ret)

for i in range(5):
    if i < 5:
        action = search_job(sql1,cursor)
        if action:
            #wkt1 = action[0][0]
            dld_ldss(sql,cursor)
            break
        else:
            print('Job not ready, wait 5 more mins')
            time.sleep(30)