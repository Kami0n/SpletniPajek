import codecs
import regex as re
import json
from lxml import html
from bs4 import BeautifulSoup, Tag, Comment
from collections import Counter

import warnings
#warnings.filterwarnings("ignore", category=UserWarning, module='bs4')

inputFolderStruct = '../input-extraction/'
outputFolderStruct = '../'

def pageComparator(tag1, tag2, ignore_nesting_level):
    resultComp = ""
    score = 0
    
    return resultComp, score

def prepareFile(filePath, enc='utf-8'):
    f1 = codecs.open(filePath, encoding='utf-8', errors='replace')
    htmlBs = BeautifulSoup(f1.read(), "lxml")
    
    # remove all comments
    allComments = htmlBs.findAll(text=lambda text: isinstance(text, Comment))
    for comment in allComments:
        comment.extract()
    
    # remove unwanted elements
    elementsRemoveArray = ['style', 'script', 'link', 'meta', 'iframe', 'nav', 'map', 'form', 'input', 'svg', 'img', 'picture', 'figure', 'figcaption', 'footer']
    for elementRemove in elementsRemoveArray:
        [element.extract() for element in htmlBs.findAll(elementRemove)]
        
    return htmlBs

def extractTest(printing):
    url = 'test'
    ignoreLevel = 4
    testArray = {}
    testArray['test1'] = prepareFile(inputFolderStruct+url+'/test1.html')
    testArray['test2'] = prepareFile(inputFolderStruct+url+'/test2.html')
    
    body1 = testArray['test1'].find("body")
    body2 = testArray['test2'].find("body")
    
    result, score = pageComparator(body1, body2, ignoreLevel)
    showOvojnica(url, result, score, printing)

def extractRTV(printing):
    url = 'rtvslo.si'
    ignoreLevel = 4
    rtvArray = {}
    rtvArray['audi'] = prepareFile(inputFolderStruct+url+'/Audi A6 50 TDI quattro_ nemir v premijskem razredu - RTVSLO.si.html')
    rtvArray['volvo'] = prepareFile(inputFolderStruct+url+'/Volvo XC 40 D4 AWD momentum_ suvereno med najboljše v razredu - RTVSLO.si.html')
    
    body1 = rtvArray['audi'].find("body")
    body2 = rtvArray['volvo'].find("body")
    
    result, score = pageComparator(body1, body2, ignoreLevel)
    showOvojnica(url, result, score, printing)

def extractOverstock(printing):
    url = 'overstock.com'
    ignoreLevel = 5
    overstockArray = {}
    overstockArray['jewelry01'] = prepareFile(inputFolderStruct+url+'/jewelry01.html', 'mbcs')
    overstockArray['jewelry02'] = prepareFile(inputFolderStruct+url+'/jewelry02.html', 'mbcs')
    
    body1 = overstockArray['jewelry01'].find("body")
    body2 = overstockArray['jewelry02'].find("body")
    
    result, score = pageComparator(body1, body2, ignoreLevel)
    showOvojnica(url, result, score, printing)

def extractOwnPages(printing):
    url = 'avto.net'
    ignoreLevel = 4
    avtoArray = {}
    avtoArray['Justy'] = prepareFile(inputFolderStruct+url+'/Justy.html', 'windows-1250')
    avtoArray['Legacy'] = prepareFile(inputFolderStruct+url+'/Legacy.html', 'windows-1250')
    
    body1 = avtoArray['Justy'].find("body")
    body2 = avtoArray['Legacy'].find("body")
    
    result, score = pageComparator(body1, body2, ignoreLevel)
    showOvojnica(url, result, score, printing)

def showOvojnica(ime, result, score, printing):
    print("\n*************************************")
    print("Generalizirana ovojnica strani "+ime+":\n")

    soupResult = BeautifulSoup(result, "lxml")
    resultBody = soupResult.find("body")
    ovojnica = resultBody.prettify(encoding=None, formatter="minimal")
    
    #jsonText = json.dumps(jsonObj, ensure_ascii=False) # ensure_ascii=False -> da zapisuje tudi čšž
    if(printing):
        print(ovojnica) # The method should output extracted data in a JSON structured format to a standard output.
    else:
        f = open(outputFolderStruct+'automatic.json', 'wb')
        f.write(ovojnica.encode('utf8'))

def main(printing):
    extractOverstock(printing)
    #extractRTV(printing)
    #extractOwnPages(printing)
    #extractTest(printing)

if __name__ == '__main__':
    main(False)

