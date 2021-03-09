import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import concurrent.futures
import threading
import psycopg2

from reppy import Robots
import urlcanon

# inicializacija baze:
def default_db_values():
    conn = psycopg2.connect(host="localhost", user="user", password="friWIERvipavskaBurja")
    conn.autocommit = True
    
    cur = conn.cursor()
    cur.execute("truncate crawldb.site cascade;") # pobrisi vse vnose iz baze
    
    postgres_insert_query = """INSERT INTO crawldb.site (domain) VALUES (%s)"""
    seedArray = ['gov.si','evem.gov.si','e-uprava.gov.si','e-prostor.gov.si','*.gov.si']
    for domain in seedArray:
        record_to_insert = (domain,)
        cur.execute(postgres_insert_query, record_to_insert)
    
    cur.close()
    conn.close()

def print_db_values():
    conn = psycopg2.connect(host="localhost", user="user", password="friWIERvipavskaBurja")
    conn.autocommit = True

    print("\nValues in the database:")
    cur = conn.cursor()
    cur.execute("SELECT * FROM crawldb.site")
    for row in cur.fetchall():
        print(f"\tCounter id: {row}")
    cur.close()
    conn.close()


def prenasanjeVsebineStrani(webAddress, driver):
    
    # 
    robots = Robots.fetch(webAddress+'/robots.txt')
    print(robots.allowed(webAddress+'/pomoc', 'my-user-agent'))
    
    print(f"Retrieving web page URL '{webAddress}'")
    
    driver.get(webAddress)
    # Timeout needed for Web page to render (read more about it)
    time.sleep(TIMEOUT)
    html = driver.page_source
    #print(f"Retrieved Web content (truncated to first 900 chars): \n\n'\n{html[:900]}\n'\n")
    
    
    # povezave ki so v html kodi -> href & onclick (location.href)
    # pravilno upoštevaj relativne URLje! -> načeloma piše v <head> baseurl ali og url
    # detektiranje slik <img src="">
    
    for element in driver.find_elements_by_tag_name("a"):
        href = element.get_attribute('href')
        parsed_url = urlcanon.whatwg(href)
        print(parsed_url)
        
    
    # return URLs
    
    # vse URl se hrani v kanonični obliki -> oblika brez parametrov, napak..

default_db_values()
print_db_values()

WEB_DRIVER_LOCATION = "D:/Fakulteta/2 stopnja/2sem/IEPS/1seminar/chromedriver"
TIMEOUT = 5

chrome_options = Options()
# If you comment the following line, a browser will show ...
chrome_options.add_argument("--headless")
#Adding a specific user agent
chrome_options.add_argument("user-agent=fri-wier-vipavska-burja")

#lock = threading.Lock()

# iskanje v ŠIRINO! breadth-first -> FIFO

driver = webdriver.Chrome(WEB_DRIVER_LOCATION, options=chrome_options)

prenasanjeVsebineStrani('https://gov.si', driver)

driver.close()