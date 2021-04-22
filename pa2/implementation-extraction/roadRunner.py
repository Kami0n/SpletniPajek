
# RoadRunner-like implementation: Follow the implementation guidelines presented at the lectures.
# Apart from the guidelines you can introduce various heuristics (e.g. taking tag attributes into account, additional rules, …)
# that may help you with the wrapper generation. Also, you can implement some preprocessing steps prior to running the algorithm.
# It is expected, that the generated wrapper may miss some of the data items and may include other unrelevant data items in the output.
# You should comment or identify, which data items have not been recognized using the algorithm.
# Full (official) implementation of the RoadRunner algorithm proposed in the literature is available online along with some examples.
# Check also other descriptions, e.g. paper 1 or paper 2.

import json
import regex as re
from lxml import html
from bs4 import BeautifulSoup
from bs4 import NavigableString

inputFolderStruct = "../input-extraction/"
outputFolderStruct = "../"

# zanimajo nas vsebinski deli ki se razlikujejo
# roadrunner -> union-free regularni izrazi

# pristop:
# začnemo z dvema stranema
# ena stran ze predstavlja en regualrni izraz
# z drugo stranjo generalizitamo ta regularni izraz

def roadRunner(soup):
    
    if soup.name is not None: # if its tag
        for child in soup.children:
            if isinstance(child, NavigableString) and (str(child) == '\n' or str(child) == '\t' or str(child) == ''): # ignore whitespaces, tabs and newlines between nodes that we dont need to match
                continue
            print(str(child.name) + ":" + str(type(child)))
            roadRunner(child)
            
    else: # to je string
        print("STRING: ", soup.strip())
    

def prepareFile(filePath, enc='utf-8'):
    r = open(filePath, "r", encoding=enc)
    html = r.read()
    
    # pobrisemo vse script, style, komentarje
    html = re.sub(r'<script[^>]*?>([^<]*)</script>', '', html)
    html = re.sub(r'<style[^>]*?>([^<]*)</style>', '', html)
    html = re.sub(r'<!--([^<]*)-->', '', html)
    
    html_bs = BeautifulSoup(html, 'html.parser')
    return html_bs

def extractTest(jsonObj):
    url = 'test'
    testArray = {}
    testArray['test1'] = prepareFile(inputFolderStruct+url+"/test1.html")
    testArray['test2'] = prepareFile(inputFolderStruct+url+"/test2.html")
    
    print(testArray)
    
    #roadRunner(testArray['test1'])
    

def extractRTV(jsonObj):
    url = 'rtvslo.si'
    rtvArray = {}
    rtvArray['audi'] = prepareFile(inputFolderStruct+url+"/Audi A6 50 TDI quattro_ nemir v premijskem razredu - RTVSLO.si.html")
    rtvArray['volvo'] = prepareFile(inputFolderStruct+url+"/Volvo XC 40 D4 AWD momentum_ suvereno med najboljše v razredu - RTVSLO.si.html")
    
    print(rtvArray)

"""
def extractOverstock(jsonObj):
    url = 'overstock.com'
    overstockArray = {}
    overstockArray['jewelry01'] = htmlFileRead(inputFolderStruct+url+"/jewelry01.html", 'mbcs')
    overstockArray['jewelry02'] = htmlFileRead(inputFolderStruct+url+"/jewelry02.html", 'mbcs')
    
    jsonObj[url] = {}
    
    for name,page in overstockArray.items():
        tree = html.fromstring(page)
        #extract title
        titles = tree.xpath('/html/body/table[2]/tbody/tr[1]/td[5]/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr/td/a/b')
        # extract list price
        listPrices = tree.xpath('/html/body/table[2]/tbody/tr[1]/td[5]/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr/td/table/tbody/tr/td[1]/table/tbody/tr[1]/td[2]/s')
        # extract price
        prices = tree.xpath('/html/body/table[2]/tbody/tr[1]/td[5]/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr/td/table/tbody/tr/td[1]/table/tbody/tr[1]/td[2]/s')
        # extract saving & saving percent
        savings = tree.xpath('/html/body/table[2]/tbody/tr[1]/td[5]/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr/td/table/tbody/tr/td[1]/table/tbody/tr[3]/td[2]/span')
        # extract content
        content = tree.xpath('/html/body/table[2]/tbody/tr[1]/td[5]/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr/td/table/tbody/tr/td[2]/span')
        
        index = 0
        
        tmpItems = []
        
        for title in titles:
            tmpArrayItem = {}
            
            tmpArrayItem['title'] = title.text
            tmpArrayItem['listPrice'] = listPrices[index].text
            tmpArrayItem['price'] = prices[index].text
            
            saving = savings[index].text
            tmpArrayItem['saving'] = saving.split(" ")[0]
            tmpArrayItem['savingPercent'] = saving.split(" ")[1]
            
            tmpArrayItem['content'] = content[index].text
            
            tmpItems.append(tmpArrayItem)
            
            index += 1
        
        jsonObj[url][name] = tmpItems

def extractOwnPages(jsonObj):
    url = 'avto.net'
    avtoArray = {}
    avtoArray['Justy'] = htmlFileRead(inputFolderStruct+url+"/Justy.html", 'windows-1250')
    avtoArray['Legacy'] = htmlFileRead(inputFolderStruct+url+"/Legacy.html", 'windows-1250')
    
    jsonObj[url] = {}
    
    for name,page in avtoArray.items():
        tree = html.fromstring(page)
        #extract title
        titles = tree.xpath('/html/body/strong/div[1]/div[3]/div/div[5]/form/div/div[1]/span')
        # extract year 1 registration
        firstRegist = tree.xpath('/html/body/strong/div[1]/div[3]/div/div[5]/form/div/div[4]/div/table/tbody/tr[1]/td[2]')
        # extract mileage
        kilometers = tree.xpath('/html/body/strong/div[1]/div[3]/div/div[5]/form/div/div[4]/div/table/tbody/tr[2]/td[2]')
        # extract fuel
        fuel = tree.xpath('/html/body/strong/div[1]/div[3]/div/div[5]/form/div/div[4]/div/table/tbody/tr[3]/td[2]')
        # extract transmission
        transmission = tree.xpath('/html/body/strong/div[1]/div[3]/div/div[5]/form/div/div[4]/div/table/tbody/tr[4]/td[2]')
        # extract engine
        engine = tree.xpath('/html/body/strong/div[1]/div[3]/div/div[5]/form/div/div[4]/div/table/tbody/tr[5]/td[2]')
        # extract price
        price = tree.xpath('/html/body/strong/div[1]/div[3]/div/div[5]/form/div/div[contains(@class, "GO-Results-PriceLogo")]/div[1]/div[1]/div')
        
        index = 0
        
        tmpItems = []
        
        for title in titles:
            tmpArrayItem = {}
            
            tmpArrayItem['title'] = title.text
            tmpArrayItem['firstRegist'] = firstRegist[index].text
            tmpArrayItem['kilometers'] = kilometers[index].text
            tmpArrayItem['fuel'] = fuel[index].text
            tmpArrayItem['transmission'] = transmission[index].text
            tmpArrayItem['engine'] = engine[index].text
            tmpArrayItem['price'] = price[index].text
            
            tmpItems.append(tmpArrayItem)
            
            index += 1
        
        jsonObj[url][name] = tmpItems
"""

def exportJson(jsonText):
    f = open(outputFolderStruct+"xPathExport.json", "wb")
    f.write(jsonText.encode('utf8'))

def main(printing):
    jsonObj = {}
    #extractOverstock(jsonObj)
    extractRTV(jsonObj)
    #extractOwnPages(jsonObj)
    
    #extractTest(jsonObj)
    
    jsonText = json.dumps(jsonObj, ensure_ascii=False) # ensure_ascii=False -> da zapisuje tudi čšž
    if(printing):
        print(jsonText) # The method should output extracted data in a JSON structured format to a standard output.
    else:
        exportJson(jsonText)

if __name__ == "__main__":
    main(False)