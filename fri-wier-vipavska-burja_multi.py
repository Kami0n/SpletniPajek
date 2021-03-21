import os
from os.path import join, dirname

from dotenv import load_dotenv
# loading .env file
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)
WEB_DRIVER_LOCATION = os.environ.get("WEB_DRIVER_LOCATION")
HOST = os.environ.get("HOST")
DBUSER = os.environ.get("DBUSER")
DBPASSWD = os.environ.get("DBPASSWD")

from multiprocessing import Process, Value, Lock
import multiprocessing

import re
import io
import pathlib
import time
from datetime import datetime
import threading
import psycopg2
from seleniumwire import webdriver
from selenium.webdriver.chrome.options import Options
import url
from urllib.parse import urlparse
from urllib.request import urlopen
from reppy import Robots
import socket
from PIL import Image
import hashlib

TIMEOUT = 5
RENDERTIMEOUT = 5
start_time = time.time()
dictIpTime = dict()

# 'http://83.212.82.40/testJsHref/' -> for testing onclick href
SEEDARRAY = ['https://gov.si/', 'https://evem.gov.si/', 'https://e-uprava.gov.si/', 'https://e-prostor.gov.si/']

chrome_options = Options()
# If you comment the following line, a browser will show ...
chrome_options.add_argument("--headless")
# Adding a specific user agent
chrome_options.add_argument("user-agent=fri-wier-vipavska-burja")
# disable console.log
chrome_options.add_argument("--log-level=3")
# ignore SSL certificate errors
chrome_options.add_argument("--ignore-certificate-errors")

driver = webdriver.Chrome(WEB_DRIVER_LOCATION, options=chrome_options)

lock = Lock()

mozneKoncnice = []

def databasePutConn(stringToExecute, params=()):
    #with lock:
    conn = psycopg2.connect(host=HOST, user=DBUSER, password=DBPASSWD)
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute(stringToExecute, params)
    cur.close()
    conn.close()

def databaseGetConn(stringToExecute, params=()):
    #with lock:
    conn = psycopg2.connect(host=HOST, user=DBUSER, password=DBPASSWD)
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute(stringToExecute, params)
    answer = cur.fetchall()
    cur.close()
    conn.close()
    return answer

def initFrontier(seed):
    #print("Inicializiram Frontier")
    databasePutConn("TRUNCATE crawldb.site, crawldb.page RESTART IDENTITY CASCADE;")  # pobrisi vse vnose iz baze
    postgres_insert_query = "INSERT INTO crawldb.page (page_type_code, url) VALUES "
    for domain in seed:
        postgres_insert_query = postgres_insert_query + "('FRONTIER', '" + domain + "'),"
    databasePutConn(postgres_insert_query[:-1])
    #print("Inicializacija Frontierja koncana")

def initFrontierProcessing():
    databasePutConn("UPDATE crawldb.page SET page_type_code='FRONTIER' WHERE page_type_code='PROCESSING'")

def initCrawler(seedArray):
    numberFronteir = databaseGetConn("SELECT COUNT(*) FROM crawldb.page WHERE page_type_code='FRONTIER'")[0][0]
    if numberFronteir == 0:
        initFrontier(seedArray)  # prvi start pajka
    else:
        initFrontierProcessing()  # restart pajka

def initDataTypes():
    global mozneKoncnice
    dbTypes = databaseGetConn('SELECT * FROM crawldb.data_type ')
    for dbType in dbTypes:
        mozneKoncnice.append('.'+dbType[0].lower())

def checkRootSite(domain):
    data = databaseGetConn("SELECT * FROM crawldb.site WHERE domain='" + domain + "'")
    return data

def fetchPageContent(domain, webAddress, driver):
    del driver.requests  # pobrisi requeste za nazaj, ker nas zanimajo samo trenutni!
    global start_time
    global dictIpTime
    
    #print(f"Retrieving content for web page URL '{webAddress}'")
    
    #razlikaCasa = (time.time() - start_time)
    #if razlikaCasa < TIMEOUT:  # in če je isti IP !! -> drugače ni treba timeouta
    #    print("TIMEOUT")
    #    time.sleep(TIMEOUT - razlikaCasa)
    
    try:
        naslovIP = socket.gethostbyname(domain)
    except:
        #print("ERR_NAME_NOT_RESOLVED")
        return None, 417, None
        
    timeStampIzDict = dictIpTime.get(naslovIP)
    if timeStampIzDict is None:
        timeStampIzDict = time.time()
    elif (time.time() - timeStampIzDict) < 5:
        time.sleep(5 - (time.time() - timeStampIzDict))
    
    try:
        driver.get(webAddress)
    except:
        return None, 417, None
    
    dictIpTime = {naslovIP: time.time()}
    #print(dictIpTime)
    
    # Timeout needed for Web page to render
    time.sleep(RENDERTIMEOUT)
    
    try:
        if hasattr(driver, 'page_source'): # smo dobili nazaj content?
            content = driver.page_source
            # print(f"Retrieved Web content (truncated to first 900 chars): \n\n'\n{html[:900]}\n'\n")
            start_time = time.time()
            
            if hasattr(driver.requests[0], 'response'): # did we get response back??
                steviloResponse = -1
                responseContent = 0
                responseStatusCode = 0
                
                for request in driver.requests:
                    if request.response:
                        #print( steviloResponse, request.url, request.response.status_code, request.response.headers['Content-Type'] )
                        steviloResponse += 1
                        if request.response.headers['Content-Type'] is not None and 'text/html' in request.response.headers['Content-Type']:
                            responseContent = steviloResponse
                
                if driver.requests[responseStatusCode].response is not None:
                    return content, driver.requests[responseStatusCode].response.status_code, driver.requests[responseContent].response.headers['Content-Type']
            
            #for request in driver.requests:
            #    if request.response:
            #         print( request.url, request.response.status_code, request.response.headers['Content-Type'] )
            
            #print("\nFetch: No status code code!\n")
            #return content, 200, None
    except:
        pass
    
    return None, 417, None

def urlCanonization(inputUrl):
    outputUrl = url.parse(inputUrl).strip().defrag().canonical().abspath().utf8
    return outputUrl.decode("utf-8")

def saveUrlToDB(inputUrl, currPageId):
    #koncniceSlik = ['.jpg', '.png', '.gif', '.webm', '.weba', '.webp', '.tiff']
    #if pathlib.Path(os.path.basename(urlparse(inputUrl).path)).suffix in koncniceSlik: # ce je slika
    #    pass
    #else:
    # preveri če je link na *.gov.si, drugace se ga ne uposteva
    if re.match(r'.*([\.]gov.si(^$|[\/])).*', inputUrl):
        parsed_url = urlCanonization(inputUrl)  # URL CANONIZATION
        try:
            #newPageId = databaseGetConn("INSERT INTO crawldb.page (page_type_code, url) VALUES ('FRONTIER', %s) RETURNING id", (parsed_url,))
            newPageId = databaseGetConn("INSERT INTO crawldb.page (page_type_code, url) VALUES ('FRONTIER', %s) ON CONFLICT(url) DO UPDATE SET url=%s RETURNING id ", (parsed_url,))
            databasePutConn("INSERT INTO crawldb.link (from_page,to_page) VALUES (%s, %s) ", (currPageId,newPageId[0][0]))
        except:
            #print("URL ze v DB")  # hendlanje podvojitev
            pass

def getHrefUrls(content, currPageId):
    #urls = []
    for element in driver.find_elements_by_tag_name("a"):
        href = element.get_attribute('href')
        if href:  # is href not None?
            #urls.append(href)
            saveUrlToDB(href, currPageId)  # save URLs to DB

def getJsUrls(content, currPageId):
    #urls = []
    for element in driver.find_elements_by_xpath("//*[@onclick]"): # find all elements that have attributre onclick
        onclick = element.get_attribute('onclick')
        result = re.search(r'(\"|\')(.*)(\"|\')', onclick)
        #urls.append(result.group(2))
        if result:
            if result.group(2) is not None:
                saveUrlToDB(result.group(2), currPageId)  # save URLs to DB

def getImgUrls(content, pageId, timestamp):
    for element in driver.find_elements_by_tag_name("img"):
        src = element.get_attribute('src')
        if src:
            if "data:image" in src: # is image encoded with data:
                #print("SLIKA encoded!")
                if element.get_attribute('alt'):
                    databasePutConn("INSERT INTO crawldb.image (page_id, filename, content_type, data, accessed_time) VALUES (%s,%s,%s,%s,%s)", (pageId, 'Alt: '+element.get_attribute('alt'), 'data:image', src, timestamp))
                else:
                    databasePutConn("INSERT INTO crawldb.image (page_id, filename, content_type, data, accessed_time) VALUES (%s,%s,%s,%s,%s)", (pageId, 'No name', 'data:image', src, timestamp))
                    
            else: # is image just url
                parsed_url_img = urlCanonization(src)
                imageName = os.path.basename(urlparse(parsed_url_img).path)
                #print("SLIKA: " + imageName)
                # detect image format
                if pathlib.Path(imageName).suffix in '.svg':
                    # data?
                    databasePutConn("INSERT INTO crawldb.image (page_id, filename, content_type, accessed_time) VALUES (%s,%s,%s,%s)", (pageId, imageName, "svg", timestamp))
                else:
                    try:
                        pil_im = Image.open(urlopen(parsed_url_img)) 
                        b = io.BytesIO()
                        pil_im.save(b, pil_im.format)
                        imageBytes = b.getvalue()
                        databasePutConn("INSERT INTO crawldb.image (page_id, filename, content_type, data, accessed_time) VALUES (%s,%s,%s,%s,%s)", (pageId, imageName, pil_im.format, imageBytes, timestamp))
                    except:
                        pass # ulovi napako SSL

def getNextUrl_old(lock):
    # pridobi naslednji URL
    with lock:
        url = databaseGetConn("SELECT id,url FROM crawldb.page WHERE page_type_code='FRONTIER' ORDER BY id LIMIT 1 ")
        if not url:
            return None
        return url[0]
#_old
def getNextUrl(lock):
    # pridobi naslednji URL
    with lock:
        sitesLocked = databaseGetConn("SELECT url FROM crawldb.page WHERE page_type_code='PROCESSING'")
        stringUrls = ""
        for siteUrl in sitesLocked:
            stringUrls += " AND url NOT LIKE \'%%"+urlparse(siteUrl[0]).netloc+"%%\'"
            
        url = databaseGetConn("SELECT id,url FROM crawldb.page WHERE page_type_code='FRONTIER'"+stringUrls+" ORDER BY id LIMIT 1")
        if not url:
            return None
        # lock this url in frontier
        databasePutConn("UPDATE crawldb.page SET page_type_code='PROCESSING' WHERE id=%s AND urL=%s", (url[0][0], url[0][1]))
        return url[0]

def contentTypeCheck(link, contentType):
    global mozneKoncnice
    if contentType is not None:
        if 'text/html' in contentType: # ugotavljanje iz content type
            return 'HTML'
        else:
            return 'BINARY'
    elif link is not None: # link ugotavljanje iz linka
        if pathlib.Path(os.path.basename(urlparse(link).path)).suffix in mozneKoncnice:
            return 'BINARY'
        return 'HTML'
    return 'ERROR'

# delovna funkcija -> ki predstavlja en proces
def process(nextUrl, lock):
    
    urlId = None
    while urlId is None:
        time.sleep(2)
        urlId = getNextUrl(lock)  # take first url from frontier (DB)
    
    while urlId is not None:  # MAIN LOOP
        nextUrl = urlId[1]
        
        print("PID:",'{0:06}'.format(os.getpid())," Next URL:",nextUrl)
        
        robots = None
        domain = urlparse(nextUrl).netloc
        
        if not checkRootSite(domain):  # site unknown (domain not in sites)
            #with lock:
            #print("\nNEZNAN site: " + domain)
            robotContent, httpCode, contType = fetchPageContent(domain, nextUrl + '/robots.txt', driver)
            robotContent = driver.find_elements_by_tag_name("body")[0].text  # robots.txt -> get only text, without html tags
            if httpCode == 200 and "Not Found" not in robotContent:
                robots = Robots.parse(nextUrl + '/robots.txt', robotContent)
                for sitemap in robots.sitemaps:
                    sitemapContent, httpCode, contType = fetchPageContent(domain, sitemap, driver)
                
                if robots.sitemaps: # robots & sitemap present
                    databasePutConn("INSERT INTO crawldb.site (domain, robots_content, sitemap_content) VALUES (%s,%s,%s)", (domain, robotContent, sitemapContent))
                else: # only robots.txt present
                    databasePutConn("INSERT INTO crawldb.site (domain, robots_content) VALUES (%s,%s)", (domain, robotContent))
            else: # no robots
                databasePutConn("INSERT INTO crawldb.site (domain) VALUES (%s)", (domain,))
            # link page with site
            databasePutConn("UPDATE crawldb.page SET site_id=(SELECT id FROM crawldb.site WHERE domain=%s) WHERE url=%s", (domain, nextUrl))
        else: # site known
            #print("\nZNAN site: " + domain)
            # link page with site
            databasePutConn("UPDATE crawldb.page SET site_id=(SELECT id FROM crawldb.site WHERE domain=%s) WHERE url=%s", (domain, nextUrl))
            # load robots from DB
            robotContent = databaseGetConn("SELECT robots_content FROM crawldb.site WHERE domain=%s", (domain,))[0][0]
            if robotContent is not None:
                robots = Robots.parse(nextUrl + '/robots.txt', robotContent)
            else:
                robots = None
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if robots is None or robots.allowed(nextUrl, 'my-user-agent'): # does robots allow us to go on this link?
            # download page content
            content, httpCode, contentType = fetchPageContent(domain, nextUrl, driver)
            # temp url, kam smo bli preusmerjeni ?
            if content is None: # prazen content
                databasePutConn("UPDATE crawldb.page SET page_type_code='ERROR', accessed_time=%s WHERE id=%s AND urL=%s", (timestamp, urlId[0], urlId[1]))
            else:
                
                contentType2 = contentTypeCheck(nextUrl, contentType) #ugotovi kakšen tip je ta content
                
                # hash contenta
                hashContent = hashlib.sha256(content.encode('utf-8')).hexdigest()
                # ugotovi duplicate
                numberHash = databaseGetConn("SELECT COUNT(*) FROM crawldb.page WHERE hash=%s", (hashContent,))[0][0]
                
                if numberHash == 0 or contentType2 == 'BINARY': # ce je podvojena stran, shrani hash in continue
                    #if contentType is not None and 'text/html' in contentType:
                    if contentType2 == 'HTML':
                        getHrefUrls(content, urlId[0]) # get all href links
                        getJsUrls(content, urlId[0]) # get all JS links
                        getImgUrls(content, urlId[0], timestamp) # get all img links
                        databasePutConn("UPDATE crawldb.page SET html_content=%s, http_status_code=%s, page_type_code='HTML', accessed_time=%s, hash=%s WHERE id=%s AND urL=%s", (content, httpCode, timestamp, hashContent, urlId[0], urlId[1]))
                    elif contentType2 == 'BINARY':
                        databasePutConn("UPDATE crawldb.page SET http_status_code=%s, page_type_code='BINARY', accessed_time=%s, hash=%s WHERE id=%s AND urL=%s", (httpCode, timestamp, hashContent, urlId[0], urlId[1]))
                    
                else:
                    #print("PODVOJENA STRAN")
                    databasePutConn("UPDATE crawldb.page SET html_content=%s, http_status_code=%s, page_type_code='DUPLICATE', accessed_time=%s, hash=%s WHERE id=%s AND urL=%s", (content, httpCode, timestamp, hashContent, urlId[0], urlId[1]))
                    
        else: # ni dovoljeno v robots
            databasePutConn("UPDATE crawldb.page SET page_type_code='NOTALOWED', accessed_time=%s WHERE id=%s AND urL=%s", (timestamp, urlId[0], urlId[1]))
        
        urlId = getNextUrl(lock)  # next url from frontier (DB)
    
    return True


# zagon programa
def run():
    PROCESSES = multiprocessing.cpu_count() - 1
    PROCESSES = int(input("Enter number of processes: "))
    print(f"Running with {PROCESSES} processes!")
    
    initCrawler(SEEDARRAY)
    initDataTypes()
    
    start = time.time()
    
    nextUrls = ['']
    procs = [Process(target=process, args=(nextUrls,lock)) for i in range(PROCESSES)] # ustvarjanje procesov
    for p in procs: p.start()
    for p in procs: p.join()
    
    driver.close()
    print(f"FINISHED: Time taken = {time.time() - start:.10f}")

if __name__ == "__main__":
    #initFrontier(SEEDARRAY) # clear DB !!
    run()


# TODO
# certificate error -> problem pri urlopen() -> napačen url, ker nismo na www. !!
# -> hendlanje redirectov 302 ?

# shranjevanje v bazo -> tabelica link


# pravilno upoštevaj relativne URLje! -> načeloma piše absolutni url v <head> baseurl ali og url

# binary se ne racuna hash !!

# IZ DISCORDA:
# timeout upoševajoč zapis v robots.txt (če obstaja) ✓
# timeout da gleda web address (močogi redirecti) ne domain X (mogoče ni smiselno, will debate :slight_smile: )
# JS linki ✓
# poročilo kašna vizualizacija
# hranjenje errorjev v bazo (za v poročilo št. 400, 500, 300 errorjejv) ✓
# če link vsebuje .pdf .doc samo zapišemo v bazo, ne obiščemo strani, če nima končnice a je vseeno binarna datoteka se končnica nahaja v glavi
# slike v bazo (če dela prav). Poglej navodila (a href slika)
# page data
# če ima site www, ga za zapis v bazo vržemo ven. Isto pri primerjavi z bazo če je v frontirerju link z www
# kateri link se zapiše v bazo ob redirectu. Oba ali samo enega. Če ima prvi link code 302, zapišemo v bazo, nov zapis v bazi z drugim urljem pa nosi content