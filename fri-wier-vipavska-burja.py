# ime pajka -> fri-wier-vipavska-burja

# multiple workers -> več niti
# na začetku se definira število niti
# več niti ne smejo delati z isto stranjo!!
# iskanje v širino -> po celotnem nivoju naenkrat!

# 15s na posamezen strežnik! -> na nekem IP, ne na domeni
# upoštevaj robots.txt
# sitemap in disalow

# pajek prenese samo HTML vsebino! -> lista tudi ostali content

# lahko se uporabi knjižnjice za branje robots.txt, prodobivanje spletnih strani, razčlenjevanju spletnih...
# ne sme se uporabljati knjižnjice ki ima implementirane funkcionalnosti pajka!

# javascript -> lahko se uporabi knjižnjica selenium



import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import concurrent.futures
import threading
import psycopg2

def prenasanjeVsebineStrani(webAddress):
    print(f"Retrieving web page URL '{webAddress}'")
    driver = webdriver.Chrome(WEB_DRIVER_LOCATION, options=chrome_options)
    driver.get(webAddress)
    # Timeout needed for Web page to render (read more about it)
    time.sleep(TIMEOUT)
    html = driver.page_source
    #print(f"Retrieved Web content (truncated to first 900 chars): \n\n'\n{html[:900]}\n'\n")
    
    # kaj moramo prepoznati?
    # povezave ki so v html kodi -> href & onclick (location.href)
    # pravilno upoštevaj relativne URLje! -> načeloma piše v <head> baseurl ali og url
    # detektiranje slik <img src="">

    #elements = driver.find_elements_by_tag_name("a") 
    for element in driver.find_elements_by_tag_name("a"):
        href = element.get_attribute('href')
        print(href)
       
    driver.close()
    
    # return URLs
    
    # vse URl se hrani v kanonični obliki -> oblika brez parametrov, napak..
    



WEB_PAGE_ADDRESS = "http://evem.gov.si"
WEB_DRIVER_LOCATION = "D:/Fakulteta/2 stopnja/2sem/IEPS/1seminar/chromedriver_win32/chromedriver"
TIMEOUT = 5
chrome_options = Options()
# If you comment the following line, a browser will show ...
chrome_options.add_argument("--headless")
#Adding a specific user agent
chrome_options.add_argument("user-agent=fri-wier-vipavska-burja")

#lock = threading.Lock()

prenasanjeVsebineStrani(WEB_PAGE_ADDRESS)



