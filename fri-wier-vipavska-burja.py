
# import local env settings
import os
from os.path import join, dirname
from dotenv import load_dotenv
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)
WEB_DRIVER_LOCATION = os.environ.get("WEB_DRIVER_LOCATION")
HOST = os.environ.get("HOST")
DBUSER = os.environ.get("DBUSER")
DBPASSWD = os.environ.get("DBPASSWD")

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

# 'http://83.212.82.40/testJsHref/' -> testiranje onclick href
SEEDARRAY = ['https://gov.si', 'https://evem.gov.si', 'https://e-uprava.gov.si', 'https://e-prostor.gov.si']

chrome_options = Options()
# If you comment the following line, a browser will show ...
chrome_options.add_argument("--headless")
# Adding a specific user agent
chrome_options.add_argument("user-agent=fri-wier-vipavska-burja")
# disable console.log
chrome_options.add_argument("--log-level=3")
driver = webdriver.Chrome(WEB_DRIVER_LOCATION, options=chrome_options)


def databasePutConn(stringToExecute, params=()):
    conn = psycopg2.connect(host="localhost", user=DBUSER, password=DBPASSWD)
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute(stringToExecute, params)
    cur.close()
    conn.close()

def databaseGetConn(stringToExecute, params=()):
    conn = psycopg2.connect(host=HOST, user=DBUSER, password=DBPASSWD)
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute(stringToExecute, params)
    answer = cur.fetchall()
    cur.close()
    conn.close()
    return answer


def initFrontier(seed):
    print("Inicializiram Frontier")

    databasePutConn("TRUNCATE crawldb.site, crawldb.page RESTART IDENTITY CASCADE;")  # pobrisi vse vnose iz baze

    postgres_insert_query = "INSERT INTO crawldb.page (page_type_code, url) VALUES "
    for domain in seed:
        postgres_insert_query = postgres_insert_query + "('FRONTIER', '" + domain + "'),"
    databasePutConn(postgres_insert_query[:-1])

    print("Inicializacija Frontierja koncana")


def initFrontierProcessing():
    databasePutConn("UPDATE crawldb.page SET page_type_code='FRONTIER' WHERE page_type_code='PROCESSING'")


def initCrawler(seedArray):
    numberFronteir = databaseGetConn("SELECT COUNT(*) FROM crawldb.page WHERE page_type_code='FRONTIER'")[0][0]
    if numberFronteir == 0:
        initFrontier(seedArray)  # prvi start pajka
    else:
        initFrontierProcessing()  # restart pajka


def getNextUrl():
    # pridobi naslednji URL
    url = databaseGetConn("SELECT id,url FROM crawldb.page WHERE page_type_code='FRONTIER' ORDER BY id LIMIT 1 ")
    if not url:
        return None
    return url[0]


def checkRootSite(domain):
    data = databaseGetConn("SELECT * FROM crawldb.site WHERE domain='" + domain + "'")
    return data


def fetchPageContent(domain, webAddress, driver):
    del driver.requests  # pobrisi requeste za nazaj, ker nas zanimajo samo trenutni!
    global start_time
    global dictIpTime
    
    print(f"Retrieving content for web page URL '{webAddress}'")
    
    #razlikaCasa = (time.time() - start_time)
    #if razlikaCasa < TIMEOUT:  # in če je isti IP !! -> drugače ni treba timeouta
    #    print("TIMEOUT")
    #    time.sleep(TIMEOUT - razlikaCasa)
    
    try:
        naslovIP = socket.gethostbyname(domain)
    except:
        print("ERR_NAME_NOT_RESOLVED")
        return None, 417, None
        
    timeStampIzDict = dictIpTime.get(naslovIP)
    if timeStampIzDict is None:
        timeStampIzDict = time.time()
    elif (time.time() - timeStampIzDict) < 5:
        time.sleep(5 - (time.time() - timeStampIzDict))
    
    driver.get(webAddress)
    dictIpTime = {naslovIP: time.time()}
    
    # Timeout needed for Web page to render
    time.sleep(RENDERTIMEOUT)
    
    if hasattr(driver, 'page_source'): # smo dobili nazaj content?
        content = driver.page_source
        # print(f"Retrieved Web content (truncated to first 900 chars): \n\n'\n{html[:900]}\n'\n")
        start_time = time.time()
        
        if hasattr(driver.requests[0], 'response'): # did we get response back??
            steviloResponse = -1
            responseHtml = 0
            for request in driver.requests:
                if request.response:
                    #print( steviloResponse, request.url, request.response.status_code, request.response.headers['Content-Type'] )
                    steviloResponse += 1
                    if request.response.headers['Content-Type'] is not None and 'text/html' in request.response.headers['Content-Type']:
                        responseHtml = steviloResponse
            return content, driver.requests[0].response.status_code, driver.requests[responseHtml].response.headers['Content-Type']
        
        #for request in driver.requests:
        #    if request.response:
        #         print( request.url, request.response.status_code, request.response.headers['Content-Type'] )
        
        print("\nFetch: No status code code!\n")
        return content, 200, None
        
    print("\nFetch: Empty response!\n")
    return None, 417, None


def urlCanonization(inputUrl):
    outputUrl = url.parse(inputUrl).strip().defrag().canonical().abspath().utf8

    return outputUrl.decode("utf-8")


def saveUrlToDB(inputUrl):
    try:
        databasePutConn("INSERT INTO crawldb.page (page_type_code, url) VALUES ('FRONTIER', %s)", (inputUrl,))
        #print(inputUrl)
    except:
        #print("URL ze v DB")  # hendlanje podvojitev
        pass

def getHrefUrls(content):
    urls = []
    for element in driver.find_elements_by_tag_name("a"):
        href = element.get_attribute('href')
        if href:  # is href not None?
            parsed_url = urlCanonization(href)  # URL CANONIZATION
            # preveri če je link na gov.si, drugace se ga ne uposteva
            if 'gov.si' in urlparse(parsed_url).netloc:
                urls.append(parsed_url)
                # TODO uporabi regular expression za preverjanje ce je stran v gov.si
                saveUrlToDB(parsed_url)  # save URLs to DB

def getJsUrls(content):
    urls = []
    for element in driver.find_elements_by_xpath("//*[@onclick]"): # find all elements that have attributre onclick
        onclick = element.get_attribute('onclick')
        result = re.search('(\"|\')(.*)(\"|\')', onclick)
        #print(result.group(2))
        urls.append(result.group(2))
        saveUrlToDB(result.group(2))  # save URLs to DB

def getImgUrls(content):
    for element in driver.find_elements_by_tag_name("img"):
        src = element.get_attribute('src')
        if src:
            if "data:image" in src: # is image encoded with data:
                #print("SLIKA encoded!")
                if element.get_attribute('alt'):
                    databasePutConn("INSERT INTO crawldb.image (page_id, filename, content_type, data, accessed_time) VALUES (%s,%s,%s,%s,%s)", (urlId[0], 'Alt: '+element.get_attribute('alt'), 'data:image', src, timestamp))
                else:
                    databasePutConn("INSERT INTO crawldb.image (page_id, filename, content_type, data, accessed_time) VALUES (%s,%s,%s,%s,%s)", (urlId[0], 'No name', 'data:image', src, timestamp))
                    
            else: # is image just url
                parsed_url_img = urlCanonization(src)
                imageName = os.path.basename(urlparse(parsed_url_img).path)
                #print("SLIKA: " + imageName)
                # detect image format
                if pathlib.Path(imageName).suffix in '.svg':
                    # data?
                    databasePutConn("INSERT INTO crawldb.image (page_id, filename, content_type, accessed_time) VALUES (%s,%s,%s,%s)", (urlId[0], imageName, "svg", timestamp))
                else:
                    pil_im = Image.open(urlopen(parsed_url_img))
                    b = io.BytesIO()
                    pil_im.save(b, pil_im.format)
                    imageBytes = b.getvalue()
                    
                    databasePutConn("INSERT INTO crawldb.image (page_id, filename, content_type, data, accessed_time) VALUES (%s,%s,%s,%s,%s)", (urlId[0], imageName, pil_im.format, imageBytes, timestamp))

if __name__ == "__main__":
    #initFrontier(SEEDARRAY) # pobrise bazo
    initCrawler(SEEDARRAY)
    
    urlId = getNextUrl()  # vzames prvi url iz baze
    while (urlId):  # GLAVNA ZANKA
        # zakleni ta pridobljen URL
        # TODO DODAJ ACCESSED TIME -> accessed_time=%s time.time(), -
        databasePutConn("UPDATE crawldb.page SET page_type_code='PROCESSING' WHERE id=%s AND urL=%s", (urlId[0], urlId[1]))
        nextUrl = urlId[1]
        print("\nNaslednji URL:")
        print(nextUrl)
        
        robots = None
        domain = urlparse(nextUrl).netloc
        
        if not checkRootSite(domain):  # ali je root site (domain) ze v bazi
            print("\nNEZNAN site: " + domain)
            print("Fetching robots.txt")
            
            robotContent, httpCode, contType = fetchPageContent(domain, nextUrl + '/robots.txt', driver)
            robotContent = driver.find_elements_by_tag_name("body")[0].text  # pridobi samo text, brez html znack
            if httpCode == 200 and "Not Found" not in robotContent:
                robots = Robots.parse(nextUrl + '/robots.txt', robotContent)
                for sitemap in robots.sitemaps:
                    print("Fetching sitemap")
                    sitemapContent, httpCode, contType = fetchPageContent(domain, sitemap, driver)
                
                if robots.sitemaps: # robots & sitemap present
                    databasePutConn("INSERT INTO crawldb.site (domain, robots_content, sitemap_content) VALUES (%s,%s,%s)", (domain, robotContent, sitemapContent))
                else: # only robots.txt present
                    databasePutConn("INSERT INTO crawldb.site (domain, robots_content) VALUES (%s,%s)", (domain, robotContent))
            else: # no robots
                databasePutConn("INSERT INTO crawldb.site (domain) VALUES (%s)", (domain,))

            # povezi page z site
            databasePutConn("UPDATE crawldb.page SET site_id=(SELECT id FROM crawldb.site WHERE domain=%s) WHERE url=%s",
                            (domain, nextUrl))
        else: # ce je site ze znan
            print("\nZNAN site: " + domain)
            # load robots from DB
            robotContent = databaseGetConn("SELECT robots_content FROM crawldb.site WHERE domain=%s", (domain,))[0][0]
            if robotContent is not None:
                robots = Robots.parse(nextUrl + '/robots.txt', robotContent)
            else:
                robots = None
            # povezi page z site
            databasePutConn("UPDATE crawldb.page SET site_id=(SELECT id FROM crawldb.site WHERE domain=%s) WHERE url=%s",
                            (domain, nextUrl))
        
        if robots is None or robots.allowed(nextUrl, 'my-user-agent'): # ali je dovoljeno da gremo na ta link
            # prenesi stran
            
            content, httpCode, contentType = fetchPageContent(domain, nextUrl, driver)
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            if content is None: # prazen content -> error?
                databasePutConn("UPDATE crawldb.page SET accessed_time=%s WHERE id=%s AND urL=%s", (timestamp, urlId[0], urlId[1]))
            else:
                # hash contenta
                hashContent = hashlib.sha256(content.encode('utf-8')).hexdigest()
                # ugotovi duplicate
                numberHash = databaseGetConn("SELECT COUNT(*) FROM crawldb.page WHERE hash=%s", (hashContent,))[0][0]
                if numberHash != 0 : # ce je podvojena stran, shrani hash in continue
                    print("PODVOJENA STRAN")
                    databasePutConn("UPDATE crawldb.page SET html_content=%s, http_status_code=%s, page_type_code='DUPLICATE', accessed_time=%s, hash=%s WHERE id=%s AND urL=%s", (content, httpCode, timestamp, hashContent, urlId[0], urlId[1]))
                else:
                    if 'text/html' in contentType:
                        # TODO ugotovi kakšen tip je ta content!
                        
                        # get all href links
                        getHrefUrls(content)
                        
                        # get all JS links
                        getJsUrls(content)
                        
                        # get all img links
                        getImgUrls(content)
                        
                        databasePutConn("UPDATE crawldb.page SET html_content=%s, http_status_code=%s, page_type_code='HTML', accessed_time=%s, hash=%s WHERE id=%s AND urL=%s", (content, httpCode, timestamp, hashContent, urlId[0], urlId[1]))
                    else:
                        databasePutConn("UPDATE crawldb.page SET http_status_code=%s, page_type_code='BINARY', accessed_time=%s, WHERE id=%s AND urL=%s", (httpCode, timestamp, urlId[0], urlId[1]))
                    
        urlId = getNextUrl()  # vzames naslednji url iz baze

    # lock = threading.Lock()

    driver.close()
    print("KONCANO")

# TODO
# preverajnje duplikatov. Sepravi če: gov.si/a -> =vsebina= <- evem.si/b (drugi linki vsebina ista) najlažje rešiš z hashom strani
# iskanje onclick povezav
# hendlanje redirectov 302 !!
# pravilno upoštevaj relativne URLje! -> načeloma piše absolutni url v <head> baseurl ali og url


# page_type_code
# 1 HTML
# 2 BINARY
# 3 DUPLICATE
# 4 FRONTIER
# 5 PROCESSING