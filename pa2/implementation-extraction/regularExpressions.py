
# For each given web page type implement a separate function that will take HTML code as input.
# The method should output extracted data in a JSON structured format to a standard output.
# Each data item must be directly extracted using a single regular expression.
# But you can extract multiple data items using one regular expression (this might help you when extracting optional items in list pages).

import json
import re

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
        tmpJson = {}
        
        #extract author
        author = re.findall(r"<div class=\"author-name\">([^<]*)</div>",page)
        tmpJson['author'] = author[0]
        
        # extract publish date/time
        datetime = re.findall(r"<div class=\"publish-meta\">([^/]*)</div>",page)
        tmpJson['datetime'] = datetime[0]
        
        # extract title
        title = re.findall(r"<h1>([^<]*)</h1>",page)
        tmpJson['title'] = title[0]
        
        # extract subtitle
        subtitle = re.findall(r"<div class=\"subtitle\">([^<]*)</div>",page)
        tmpJson['subtitle'] = subtitle[0]
        
        # extract lead
        lead = re.findall(r"<p class=\"lead\">([^<]*)</p>",page)
        tmpJson['lead'] = lead[0]
        
        # extract content
        content = re.findall(r"((?:<article(.|\s))* (?:<p[^>]*>\s*((?:.|\n)*?)<\/p>))",page) # - minus scripts
        tmpJson['content'] = content
        print(content)
        
        jsonObj[url][name] = tmpJson
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
def exportJson(jsonObj):
    jsonText = json.dumps(jsonObj, ensure_ascii=False).encode('utf8') # ensure_ascii=False -> da zapisuje tudi čšž
    f = open(outputFolderStruct+"reExport.json", "wb")
    f.write(jsonText)
    
    #print(jsonText) # The method should output extracted data in a JSON structured format to a standard output.

def main():
    
    jsonObj = {}
    #extractOverstock(jsonObj)
    extractRTV(jsonObj)
    #extractOwnPages(jsonObj)
    
    exportJson(jsonObj)

if __name__ == "__main__":
    main()