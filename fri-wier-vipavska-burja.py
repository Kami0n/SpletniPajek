import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import concurrent.futures
import threading
import psycopg2

from reppy import Robots
import urlcanon

TIMEOUT = 5

NOTHREADS = 2

WEB_DRIVER_LOCATION = "D:/Fakulteta/2 stopnja/2sem/IEPS/1seminar/chromedriver"
chrome_options = Options()
# If you comment the following line, a browser will show ...
chrome_options.add_argument("--headless")
#Adding a specific user agent
chrome_options.add_argument("user-agent=fri-wier-vipavska-burja")
driver = webdriver.Chrome(WEB_DRIVER_LOCATION, options=chrome_options)

def databasePutConn(stringToExecute):
    conn = psycopg2.connect(host="localhost", user="user", password="friWIERvipavskaBurja")
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute(stringToExecute)
    cur.close()
    conn.close()

def databaseGetConn(stringToExecute):
    conn = psycopg2.connect(host="localhost", user="user", password="friWIERvipavskaBurja")
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute(stringToExecute)
    answer = cur.fetchall()
    cur.close()
    conn.close()
    return answer

def initFrontier(seed):
    print("Inicializiram Frontier")
    
    databasePutConn("TRUNCATE crawldb.site, crawldb.page RESTART IDENTITY CASCADE;") # pobrisi vse vnose iz baze
    
    postgres_insert_query = "INSERT INTO crawldb.page (page_type_code, url) VALUES "
    for domain in seed:
        postgres_insert_query = postgres_insert_query + "('FRONTIER', '"+domain+"'),"
    databasePutConn(postgres_insert_query[:-1])
    
    print("Inicializacija Frontierja konacana")

# page_type_code
    # 1 HTML
    # 2 BINARY
    # 3 DUPLICATE
    # 4 FRONTIER
    # 5 PROCESSING

def getNextUrl():
    # pridobi naslednji URL
    
    url = databaseGetConn("SELECT id,url FROM crawldb.page WHERE page_type_code='FRONTIER' ORDER BY id LIMIT 1 ")
    if not url:
        return None
    
    url = url[0]
    
    # zakleni ta pridobljen URL
    databasePutConn("UPDATE crawldb.page SET page_type_code='PROCESSING' WHERE id="+str(url[0])+" AND urL='"+url[1]+"'")
    
    return url[1]

def prenasanjeVsebineStrani(webAddress, driver):
    print(f"Retrieving content for web page URL '{webAddress}'")
    
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
        if href:
            parsed_url = urlcanon.whatwg(href)
            print(parsed_url)
        
    
    # return URLs
    
    # vse URl se hrani v kanonični obliki -> oblika brez parametrov, napak..

start_time = time.time()

seedArray = ['https://gov.si','https://evem.gov.si','https://e-uprava.gov.si','https://e-prostor.gov.si']
initFrontier(seedArray)

nextUrl = getNextUrl() #vzames prvi url iz baze
print("Zacenjam zanko")
while(nextUrl):
    
    razlikaCasa = (time.time() - start_time)
    if razlikaCasa < TIMEOUT :
        print("TIMEOUT")
        time.sleep(TIMEOUT - razlikaCasa )
        
    
    # preveri ce stran ze imamo v site?
    
    
    
    robots = Robots.fetch(webAddress+'/robots.txt')
    print(robots.allowed(webAddress+'/pomoc', 'my-user-agent'))
    
    # prenesi stran
    start_time = time.time()
    prenasanjeVsebineStrani(nextUrl, driver)
    
    nextUrl = getNextUrl() #vzames naslednji url iz baze




#lock = threading.Lock()
# iskanje v ŠIRINO! breadth-first -> FIFO


driver.close()
print("KONCANO")