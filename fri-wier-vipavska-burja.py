import time
import threading

import psycopg2

from seleniumwire import webdriver
from selenium.webdriver.chrome.options import Options

import url
from urllib.parse import urlparse
from reppy import Robots

import socket

TIMEOUT = 5
RENDERTIMEOUT = 5
start_time = time.time()

dictIpTime =  {}

NOTHREADS = 2
# WEB_DRIVER_LOCATION = "D:/Fakulteta/2 stopnja/2sem/IEPS/1seminar/chromedriver"
WEB_DRIVER_LOCATION = "C:/Users/Toncaw/downloads/chromedriver"
SEEDARRAY = ['https://gov.si', 'https://evem.gov.si', 'https://e-uprava.gov.si', 'https://e-prostor.gov.si']

chrome_options = Options()
# If you comment the following line, a browser will show ...
chrome_options.add_argument("--headless")
# Adding a specific user agent
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


def fetchPageContent(domain, webAddress, driver, dictIpTime):
    del driver.requests  # pobrisi requeste za nazaj, ker nas zanimajo samo trenutni!
    global start_time

    """
    razlikaCasa = (time.time() - start_time)
    if razlikaCasa < TIMEOUT:  # in če je isti IP !! -> drugače ni treba timeouta
        print("TIMEOUT")
        time.sleep(TIMEOUT - razlikaCasa)

    print(f"Retrieving content for web page URL '{webAddress}'")
    """
    naslovIP = socket.gethostbyname(domain)
    timeStampIzDict = dictIpTime.get(naslovIP)

    if  (timeStampIzDict is None):
        timeStampIzDict = time.time()

    if (time.time() - timeStampIzDict < 5):
        time.sleep(5 - (time.time() - timeStampIzDict))

    driver.get(webAddress)
    dictIpTime = {naslovIP: time.time()}

    # for request in driver.requests:
    # if request.response:
    # print( request.url, request.response.status_code, request.response.headers['Content-Type'] )
    # if driver.requests[0].response:
    # print( driver.requests[0].url, driver.requests[0].response.status_code, driver.requests[0].response.headers['Content-Type'] )

    """
    i = 0
    while True:
        print(driver.requests[i].url, driver.requests[i].response.status_code,
              driver.requests[i].response.headers['Content-Type'])
        if driver.requests[i].response.status_code == 200 or driver.requests[i].response.status_code >= 400:
            break
        i += 1
    """
    try:
        print(driver.requests.url, driver.requests.response.status_code,
              driver.requests.response.headers['Content-Type'])
    except Exception as e:
        print(e)

    # Timeout needed for Web page to render (read more about it)
    time.sleep(RENDERTIMEOUT)

    content = driver.page_source
    # print(f"Retrieved Web content (truncated to first 900 chars): \n\n'\n{html[:900]}\n'\n")

    start_time = time.time()
    return content, driver.requests[0].response.status_code, driver.requests[0].response.headers['Content-Type']


def urlCanonization(inputUrl):
    outputUrl = url.parse(inputUrl).strip().defrag().canonical().abspath().utf8

    return outputUrl.decode("utf-8")


def saveUrlToDB(inputUrl):
    try:
        databasePutConn("INSERT INTO crawldb.page (page_type_code, url) VALUES ('FRONTIER', %s)", (inputUrl,))
        print(inputUrl)
    except:
        print("URL ze v DB")  # hendlanje podvojitev
        # autoinceremnt id problem!! -> treba ugotovit kako dat nazaj


"""
def saveImgToDB(inputUrl):
    try:
        databasePutConn("INSERT INTO crawldb.page (page_type_code, url) VALUES ('FRONTIER', %s)",(inputUrl,))
        print(inputUrl)
    except:
        print("URL ze v DB") # hendlanje podvojitev
        # autoinceremnt id problem!! -> treba ugotovit kako dat nazaj
"""


def getJsUrls(content):
    options = ["onclick=\"document.location=",
               'onclick=\"document.location=',
               "onclick=\"document.location.href=",
               'onclick=\"document.location.href=',
               "onclick=\"location.href=",
               'onclick=\"location.href=', ]

    links = []
    try:
        for opt in options:
            if opt in content:
                print(opt)
    except Exception as e:
        print("### " + e)
        pass


initCrawler(SEEDARRAY)

urlId = getNextUrl()  # vzames prvi url iz baze
while (urlId):  # GLAVNA ZANKA
    # zakleni ta pridobljen URL
    # TODO DODAJ ACCESSED TIME -> accessed_time=%s time.time(), -
    databasePutConn("UPDATE crawldb.page SET page_type_code='PROCESSING' WHERE id=%s AND urL=%s", (urlId[0], urlId[1]))
    nextUrl = urlId[1]
    print(nextUrl)

    robots = None
    domain = urlparse(nextUrl).netloc

    if not checkRootSite(domain):  # ali je root site (domain) ze v bazi
        print("NEZNAN site: " + domain + "  Fetching Robots")

        robotContent, httpCode, contType = fetchPageContent(domain, nextUrl + '/robots.txt', driver, dictIpTime)
        robotContent = driver.find_elements_by_tag_name("body")[0].text  # pridobi samo text, brez html znack

        if "Not Found" not in robotContent:  # za razširit
            robots = Robots.parse(nextUrl + '/robots.txt', robotContent)
            for sitemap in robots.sitemaps:
                sitemapContent, httpCode, contType = fetchPageContent(domain, sitemap, driver,dictIpTime)
            databasePutConn("INSERT INTO crawldb.site (domain, robots_content, sitemap_content) VALUES (%s,%s,%s)",
                            (domain, robotContent, sitemapContent))
        else:
            databasePutConn("INSERT INTO crawldb.site (domain) VALUES (%s)", (domain,))

        # povezi page z site
        databasePutConn("UPDATE crawldb.page SET site_id=(SELECT id FROM crawldb.site WHERE domain=%s) WHERE url=%s",
                        (domain, nextUrl))
    else:
        print("ZNAN site: " + domain)
        # load robots from DB
        robotContent = databaseGetConn("SELECT robots_content FROM crawldb.site WHERE domain=%s", (domain,))[0][0]
        if robotContent is not None:
            robots = Robots.parse(nextUrl + '/robots.txt', robotContent)
        else:
            robots = None
        # povezi page z site
        databasePutConn("UPDATE crawldb.page SET site_id=(SELECT id FROM crawldb.site WHERE domain=%s) WHERE url=%s",
                        (domain, nextUrl))

    # ali je dovoljeno da gremo na ta link
    if robots is None or robots.allowed(nextUrl, 'my-user-agent'):

        # prenesi stran
        content, httpCode, contentType = fetchPageContent(domain, nextUrl, driver, dictIpTime)
        # ugotovi kakšen tip je ta content!

        databasePutConn("UPDATE crawldb.page SET html_content=%s, http_status_code=%s WHERE url=%s",
                        (content, httpCode, nextUrl))

        # povezave ki so v html kodi -> href & TODO onclick (location.href)
        # pravilno upoštevaj relativne URLje! -> načeloma piše absoluti url v <head> baseurl ali og url
        # TODO detektiranje slik <img src="">

        for element in driver.find_elements_by_tag_name("a"):
            href = element.get_attribute('href')
            if href:  # is href not None?
                parsed_url = urlCanonization(href)  # URL CANONIZATION
                # preveri če je link na gov.si, drugace se ga ne uposteva
                if 'gov.si' in urlparse(
                        parsed_url).netloc:  # TODO uporabi regular expression za preverjanje ce je stran v gov.si
                    saveUrlToDB(parsed_url)  # save URLs to DB

        # iskanje slik
        """
        for element in driver.find_elements_by_tag_name("img"):
            src = element.get_attribute('src')
            if src:
                parsed_url_img = urlCanonization(src)
                if 'gov.si' in urlparse(parsed_url_img).netloc:
        """

    # spremeni iz PROCESSING v HTML/BINARY/DUPLICATE
    databasePutConn("UPDATE crawldb.page SET page_type_code='HTML' WHERE id=%s AND urL=%s", (urlId[0], urlId[1]))
    urlId = getNextUrl()  # vzames naslednji url iz baze

# lock = threading.Lock()

driver.close()
print("KONCANO")

# TODO
# preverajnje duplikatov. Sepravi če: gov.si/a -> =vsebina= <- evem.si/b (drugi linki vsebina ista) najlažje rešiš z hashom starni
# iskanje onclick povezav, a href ze dela
# hendlanje redirectov 302 !!
# pravilno upoštevaj relativne URLje! -> načeloma piše v <head> baseurl ali og url
# detektiranje slik <img src="">

# problem ko ostane stran zaklenjena, ce pajka izklopimo


# page_type_code
# 1 HTML
# 2 BINARY
# 3 DUPLICATE
# 4 FRONTIER
# 5 PROCESSING