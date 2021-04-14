
import os 
dir_path = os.path.dirname(os.path.realpath(__file__))

# For each given web page type implement a separate function that will take HTML code as input.
# The method should output extracted data in a JSON structured format to a standard output.
# Each data item must be directly extracted using an XPath expression.
# If the extracted value should be further processed, use regular expressions or other techniques to normalize them (for text only!).

import json
from lxml import html

inputFolderStruct = "./input-extraction/"
outputFolderStruct = "./"

def htmlFileRead(filePath, enc='utf-8'):
    f = open(filePath, "r", encoding=enc)
    return f.read()

def extractRTV(jsonObj):
    url = 'rtvslo.si'
    rtvArray = {}
    rtvArray['audi'] = htmlFileRead(inputFolderStruct+url+"/Audi A6 50 TDI quattro_ nemir v premijskem razredu - RTVSLO.si.html")
    rtvArray['volvo'] = htmlFileRead(inputFolderStruct+url+"/Volvo XC 40 D4 AWD momentum_ suvereno med najboljše v razredu - RTVSLO.si.html")
    
    jsonObj[url] = {}
    
    for name,page in rtvArray.items():
        tree = html.fromstring(page)
        tmpJson = {}
        
        #extract author
        author = tree.xpath('string(/html/body/div[@id="main-container"]/div[3]/div/div[1]/div[1]/div)')
        tmpJson['author'] = author
        
        # extract publish date/time
        datetime = tree.xpath('string(/html/body/div[@id="main-container"]/div[3]/div/div[1]/div[2])')
        tmpJson['datetime'] = datetime
        
        # extract title
        title = tree.xpath('string(/html/body/div[@id="main-container"]/div[3]/div/header/h1)')
        tmpJson['title'] = title
        
        # extract subtitle
        subtitle = tree.xpath('string(/html/body/div[@id="main-container"]/div[3]/div/header/div[2])')
        tmpJson['subtitle'] = subtitle
        
        # extract lead
        lead = tree.xpath('string(/html/body/div[@id="main-container"]/div[3]/div/header/p)')
        tmpJson['lead'] = lead
        
        # extract content
        content = tree.xpath('/html/body/div[@id="main-container"]/div[3]/div/div[2]/descendant::*/text()[not(ancestor::script)]') # - minus scripts
        tmpJson['content'] = content
        
        jsonObj[url][name] = tmpJson

def extractOverstockOld(jsonObj):
    url = 'overstock.com'
    overstockArray = {}
    overstockArray['jewelry01'] = htmlFileRead(inputFolderStruct+url+"/jewelry01.html", 'mbcs')
    overstockArray['jewelry02'] = htmlFileRead(inputFolderStruct+url+"/jewelry02.html", 'mbcs')
    
    jsonObj[url] = {}
    
    for name,page in overstockArray.items():
        tree = html.fromstring(page)
        tmpJson = {}
        
        #extract title
        titles = tree.xpath('/html/body/table[2]/tbody/tr[1]/td[5]/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr/td/a/b')
        tmpTitleObj = []
        for title in titles:
            tmpTitleObj.append(title.text)
        tmpJson['title'] = tmpTitleObj
        
        # extract list price
        listPrices = tree.xpath('/html/body/table[2]/tbody/tr[1]/td[5]/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr/td/table/tbody/tr/td[1]/table/tbody/tr[1]/td[2]/s')
        tmpListPriceObj = []
        for price in listPrices:
            tmpListPriceObj.append(price.text)
        tmpJson['listPrice'] = tmpListPriceObj
        
        # extract price
        prices = tree.xpath('/html/body/table[2]/tbody/tr[1]/td[5]/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr/td/table/tbody/tr/td[1]/table/tbody/tr[1]/td[2]/s')
        tmpPriceObj = []
        for price in prices:
            tmpPriceObj.append(price.text)
        tmpJson['price'] = tmpPriceObj
        
        # extract saving & saving percent
        savings = tree.xpath('/html/body/table[2]/tbody/tr[1]/td[5]/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr/td/table/tbody/tr/td[1]/table/tbody/tr[3]/td[2]/span')
        tmpSavingsObj = []
        tmpSavingspercentObj = []
        for save in savings:
            saving = save.text
            tmpSavingsObj.append(saving.split(" ")[0])
            tmpSavingspercentObj.append(saving.split(" ")[1])
        tmpJson['saving'] = tmpSavingsObj
        tmpJson['savingPercent'] = tmpSavingspercentObj
        
        # extract content
        savings = tree.xpath('/html/body/table[2]/tbody/tr[1]/td[5]/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr/td/table/tbody/tr/td[2]/span')
        tmpSavingsObj = []
        for save in savings:
            tmpSavingsObj.append(save.text)
        tmpJson['content'] = tmpSavingsObj
        
        
        jsonObj[url][name] = tmpJson

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

def exportJson(jsonObj):
    jsonText = json.dumps(jsonObj, ensure_ascii=False).encode('utf8') # ensure_ascii=False -> da zapisuje tudi čšž
    f = open(outputFolderStruct+"export.json", "wb")
    f.write(jsonText)
    
    #print(jsonText) # The method should output extracted data in a JSON structured format to a standard output.

def main():
    
    jsonObj = {}
    extractRTV(jsonObj)
    extractOverstock(jsonObj)
    extractOwnPages(jsonObj)
    
    exportJson(jsonObj)

if __name__ == "__main__":
    main()