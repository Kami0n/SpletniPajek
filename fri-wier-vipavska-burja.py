import time
from seleniumwire import webdriver
from selenium.webdriver.chrome.options import Options
#from selenium import webdriver
#from selenium.webdriver.chrome.options import Options
import concurrent.futures
import threading
import psycopg2

from urllib.parse import urlparse

from reppy import Robots
import urlcanon

import url

TIMEOUT = 5
RENDERTIMEOUT = 5
start_time = time.time()

NOTHREADS = 2

WEB_DRIVER_LOCATION = "D:/Fakulteta/2 stopnja/2sem/IEPS/1seminar/chromedriver"

chrome_options = Options()
# If you comment the following line, a browser will show ...
chrome_options.add_argument("--headless")
#Adding a specific user agent
chrome_options.add_argument("user-agent=fri-wier-vipavska-burja")
driver = webdriver.Chrome(WEB_DRIVER_LOCATION, options=chrome_options)

def databasePutConn(stringToExecute, params=()):
    conn = psycopg2.connect(host="localhost", user="user", password="friWIERvipavskaBurja")
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute(stringToExecute, params)
    cur.close()
    conn.close()

def databaseGetConn(stringToExecute, params=()):
    conn = psycopg2.connect(host="localhost", user="user", password="friWIERvipavskaBurja")
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute(stringToExecute, params)
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
    
    print("Inicializacija Frontierja koncana")

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
    return url[0]

def checkRootSite(domain):
    data = databaseGetConn("SELECT * FROM crawldb.site WHERE domain='"+domain+"'")
    return data

def fetchPageContent(webAddress, driver):
    del driver.requests # pobrisi requeste za nazaj, ker nas zanimajo samo trenutni!
    global start_time
    
    razlikaCasa = (time.time() - start_time)
    if razlikaCasa < TIMEOUT : # in če je isti IP !! -> drugače ni treba timeouta
        print("TIMEOUT")
        time.sleep(TIMEOUT - razlikaCasa )
    
    print(f"Retrieving content for web page URL '{webAddress}'")
    
    driver.get(webAddress)
    
    #for request in driver.requests:
        #if request.response:
            #print( request.url, request.response.status_code, request.response.headers['Content-Type'] )
    #if driver.requests[0].response:
        #print( driver.requests[0].url, driver.requests[0].response.status_code, driver.requests[0].response.headers['Content-Type'] )
    
    i = 0
    while True :
        print( driver.requests[i].url, driver.requests[i].response.status_code, driver.requests[i].response.headers['Content-Type'] )
        if driver.requests[i].response.status_code == 200 or driver.requests[i].response.status_code >= 400:
            break
        i+=1
    
    # Timeout needed for Web page to render (read more about it)
    time.sleep(RENDERTIMEOUT)
    
    content = driver.page_source
    #print(f"Retrieved Web content (truncated to first 900 chars): \n\n'\n{html[:900]}\n'\n")
    
    start_time = time.time()
    return content, driver.requests[0].response.status_code, driver.requests[0].response.headers['Content-Type']

def urlCanonization(inputUrl):
    
    outputUrl = url.parse(inputUrl).strip().defrag().canonical().abspath().utf8
    
    return outputUrl.decode("utf-8")

def saveUrlToDB(inputUrl):
    try:
        databasePutConn("INSERT INTO crawldb.page (page_type_code, url) VALUES ('FRONTIER', %s)",(inputUrl,))
        print(inputUrl)
    except:
        print("URL ze v DB") # hendlanje podvojitev
        # autoinceremnt id problem!! -> treba ugotovit kako dat nazaj

seedArray = ['https://gov.si','https://evem.gov.si','https://e-uprava.gov.si','https://e-prostor.gov.si']
#initFrontier(seedArray)

# GLAVNA ZANKA
print("Zacenjam zanko")
urlId = getNextUrl()
while(urlId): #vzames naslednji url iz baze
    # zakleni ta pridobljen URL
    #  accessed_time=%s time.time(),
    databasePutConn("UPDATE crawldb.page SET page_type_code='PROCESSING' WHERE id=%s AND urL=%s",( urlId[0], urlId[1]))
    nextUrl = urlId[1]
    print(nextUrl)
    
    robots = None
    domain = urlparse(nextUrl).netloc
    
    if not checkRootSite(domain): # ali je root site (domain) ze v bazi
        print("NEZNAN site: "+domain+"  Fetching Robots")
        
        robotContent, httpCode = fetchPageContent(nextUrl+'/robots.txt', driver)
        robotContent = driver.find_elements_by_tag_name("body")[0].text # pridobi samo text, brez html znack
        
        if "Not Found" not in robotContent: # za razširit
            robots = Robots.parse(nextUrl+'/robots.txt', robotContent)
            for sitemap in robots.sitemaps:
                sitemapContent, httpCode = fetchPageContent(sitemap, driver)
            databasePutConn("INSERT INTO crawldb.site (domain, robots_content, sitemap_content) VALUES (%s,%s,%s)", (domain, robotContent, sitemapContent))
        else:
            databasePutConn("INSERT INTO crawldb.site (domain) VALUES (%s)", (domain,))
        
        # povezi page z site
        databasePutConn("UPDATE crawldb.page SET site_id=(SELECT id FROM crawldb.site WHERE domain=%s) WHERE url=%s", (domain,nextUrl))
    else:
        print("ZNAN site: "+domain)
        #load robots from DB
        robotContent = databaseGetConn("SELECT robots_content FROM crawldb.site WHERE domain=%s", (domain,))[0][0]
        if robotContent is not None:
            robots = Robots.parse(nextUrl+'/robots.txt', robotContent)
        else:
            robots = None
        # povezi page z site
        databasePutConn("UPDATE crawldb.page SET site_id=(SELECT id FROM crawldb.site WHERE domain=%s) WHERE url=%s", (domain,nextUrl))
    
    # ali je dovoljeno da gremo na ta link
    if robots is None or robots.allowed(nextUrl, 'my-user-agent'):
        # prenesi stran
        content, httpCode, contentType  = fetchPageContent(nextUrl, driver)
        # ugotovi kakšen tip je ta content!
        
        databasePutConn("UPDATE crawldb.page SET html_content=%s, http_status_code=%s WHERE url=%s", (content, httpCode, nextUrl))
        
        # povezave ki so v html kodi -> href & onclick (location.href)
        # pravilno upoštevaj relativne URLje! -> načeloma piše v <head> baseurl ali og url
        # detektiranje slik <img src="">
        
        for element in driver.find_elements_by_tag_name("a"):
            href = element.get_attribute('href')
            if href: # is href not None?
                parsed_url = urlCanonization(href) # URL CANONIZATION
                # preveri če je link na gov.si, drugace se ga ne uposteva
                if 'gov.si' in urlparse(parsed_url).netloc :
                    saveUrlToDB(parsed_url) # save URLs to DB
                    
    # spremeni iz PROCESSING v HTML/BINARY/DUPLICATE
    databasePutConn("UPDATE crawldb.page SET page_type_code='HTML' WHERE id=%s AND urL=%s",(urlId[0], urlId[1]))
    urlId = getNextUrl()


#lock = threading.Lock()

driver.close()
print("KONCANO")

# TODO
# preverajnje duplikatov. Sepravi če: gov.si/a -> =vsebina= <- evem.si/b (drugi linki vsebina ista) najlažje rešiš z hashom starni
# iskanje onclick povezav, a href ze dela
# hendlanje redirectov 302 !!
# pravilno upoštevaj relativne URLje! -> načeloma piše v <head> baseurl ali og url
# detektiranje slik <img src="">

# problem ko ostane stran zaklenjena, ce pajka izklopimo
