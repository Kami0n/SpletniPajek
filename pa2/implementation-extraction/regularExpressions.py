
# For each given web page type implement a separate function that will take HTML code as input.
# The method should output extracted data in a JSON structured format to a standard output.
# Each data item must be directly extracted using a single regular expression.
# But you can extract multiple data items using one regular expression (this might help you when extracting optional items in list pages).

import json
import regex as re

inputFolderStruct = "../input-extraction/"
outputFolderStruct = "../results"

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
        tmpJson['datetime'] = datetime[0].replace('\n',' ').replace('\t','').replace('<br>','\n').strip() # remove tabs and new lines
        
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
        
        #article = re.findall(r"(?simx)(?=<article[^>]+?>(.*?)<\/article>)", page)
        #articleContent = re.findall(r"(?simx)(?=<p[^>]*>\s*(.*?)<\/p>)", article[0]) 
        #contentString = ''
        #for string in articleContent:
        #    contentString = contentString + (string.replace('\n',' ').replace('\t','').replace('<br>','\n').strip()) # remove tabs and new lines)
        
        # whole article content:
        # (?simx)(?=<article[^>]+?>(.*?)<\/article>)
        # https://regex101.com/r/dA6LEv/1
        
        # only p content
        # (?simx)(?=<p[^>]*>\s*(.*?)<\/p>)
        # https://regex101.com/r/jKr8eK/1
        
        # combined -> does not stop at </article>
        # (?simx)(?:<article[^>]*?> (?=.?)|(?=<p[^>]*>\s*(.*?)<\/p>)|(?:.?) <\/article>)
        # https://regex101.com/r/TI8ZNF/1
        
        articleContent = re.findall(r"(?simx)(?=<article[^>]+?> (?=.)|(?=<p[^>]*>\s*(.*?)<\/p>)|(?=.) <\/article>)", page) 
        
        articleContent = '\n'.join(articleContent)
        articleContent = articleContent.replace('<br>','\n').strip()
        
        tmpJson['content'] = articleContent
        #print(tmpJson['content'])
        
        jsonObj[url][name] = tmpJson

def extractOverstock(jsonObj):
    url = 'overstock.com'
    overstockArray = {}
    overstockArray['jewelry01'] = htmlFileRead(inputFolderStruct+url+"/jewelry01.html", 'mbcs')
    overstockArray['jewelry02'] = htmlFileRead(inputFolderStruct+url+"/jewelry02.html", 'mbcs')
    
    jsonObj[url] = {}
    
    for name,page in overstockArray.items():
        
        #extract title
        titles = re.findall(r"<a href=\"http:\/\/www\.overstock\.com\/cgi-bin\/d2\.cgi\?PAGE=PROFRAME&amp;PROD_ID=[0-9]+\"><b>([^<]*)<\/b><\/a>",page)
        # extract list price
        listPrices = re.findall(r"<td align=\"left\" nowrap=\"nowrap\"><s>([^<]*)",page)
        # extract price
        prices = re.findall(r"<span class=\"bigred\"><b>([^<]*)",page)
        # extract saving & saving percent
        savings = re.findall(r"<span class=\"littleorange\">([^<]*)<\/span>",page)
        # extract content
        content = re.findall(r"<span class=\"normal\">([^<]*)<br>",page)
        
        index = 0
        
        tmpItems = []
        
        for title in titles:
            tmpArrayItem = {}

            tmpArrayItem['title'] = title
            tmpArrayItem['listPrice'] = listPrices[index]
            tmpArrayItem['price'] = prices[index]
            
            saving = savings[index]
            tmpArrayItem['saving'] = saving.split(" ")[0]
            tmpArrayItem['savingPercent'] = saving.split(" ")[1]
            
            tmpArrayItem['content'] = content[index]
            
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
        #extract title
        titles = re.findall(r"<div class=\"GO-Results-Naziv bg-dark px-3 py-2 font-weight-bold text-truncate text-white text-decoration-none\">[\n\r\s]+<span>([^<]*)<\/span>",page)
        # extract year 1 registration
        firstRegist = re.findall(r"<td class=\"w-75 pl-3\">([^<]*)<\/td>",page)
        # extract mileage
        kilometers = re.findall(r"<td class=\"d-none d-md-block pl-3\">Prevoženih<\/td>[\n\r\s]+<td class=\"pl-3\">([^<]*)<\/td>",page)
        # extract fuel
        fuel = re.findall(r"<td class=\"d-none d-md-block pl-3\">Gorivo<\/td>[\n\r\s]+<td class=\"pl-3\">([^<]*)<\/td>",page)
        # extract transmission
        transmission = re.findall(r"<td class=\"d-none d-md-block pl-3\">Menjalnik<\/td>[\n\r\s]+<td class=\"pl-3 text-truncate\">([^<]*)",page)
        # extract engine
        engine = re.findall(r"<td class=\"d-none d-md-block pl-3\">Motor<\/td>[\n\r\s]+<td class=\"pl-3 text-truncate\">([^<]*)",page)
        # extract price
        price = re.findall(r"<div class=\"d-none d-sm-block col-auto px-sm-0 pb-sm-3 GO-Results-PriceLogo\">[\n\r\s]+<!--(?:.*?)-->[\n\r\s]+<!--(?:.*?)-->[\n\r\s]+<div class=\"GO-Results-Price mt-0 mt-sm-3\">[\n\r\s]+<!--(?:.*?)-->[\n\r\s]+<!--(?:.*?)-->[\n\r\s]+<!--(?:.*?)-->[\n\r\s]+<div class=\"GO-Results-Price-Mid\">[\n\r\s]+<div class=\"GO-Results-Price-TXT-Regular\">([^<]*)<\/div>",page)
        
        index = 0
        
        tmpItems = []
        
        for title in titles:
            tmpArrayItem = {}
            
            tmpArrayItem['title'] = title
            tmpArrayItem['firstRegist'] = firstRegist[index]
            tmpArrayItem['kilometers'] = kilometers[index]
            tmpArrayItem['fuel'] = fuel[index]
            tmpArrayItem['transmission'] = transmission[index]
            tmpArrayItem['engine'] = engine[index]
            tmpArrayItem['price'] = price[index]
            
            tmpItems.append(tmpArrayItem)
            
            index += 1
        
        jsonObj[url][name] = tmpItems

def exportJson(jsonText):
    f = open(outputFolderStruct+"reExport.json", "wb")
    f.write(jsonText.encode('utf8'))

def main(printing):
    
    jsonObj = {}
    extractOverstock(jsonObj)
    extractRTV(jsonObj)
    extractOwnPages(jsonObj)
    
    jsonText = json.dumps(jsonObj, ensure_ascii=False) # ensure_ascii=False -> da zapisuje tudi čšž
    if(printing):
        print(jsonText) # The method should output extracted data in a JSON structured format to a standard output.
    else:
        exportJson(jsonText)

if __name__ == "__main__":
    main(False)