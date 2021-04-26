
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

inputFolderStruct = '../input-extraction/'
outputFolderStruct = '../'

# zanimajo nas vsebinski deli ki se razlikujejo
# roadrunner -> union-free regularni izrazi

# pristop:
# začnemo z dvema stranema
# ena stran ze predstavlja en regualrni izraz
# z drugo stranjo generalizitamo ta regularni izraz


"""
if soup.name is not None: # if its tag
        for child in soup.children:
            if isinstance(child, NavigableString) and (str(child) == '\n' or str(child) == '\t' or str(child) == ''): # ignore whitespaces, tabs and newlines between nodes that we dont need to match
                continue
            print(str(child.name) + ':' + str(type(child)))
            roadRunner(child)
            
    else: # to je string
        print('STRING: ', soup.strip())
"""

def typeOfLocation(string):
    if string.startswith("<") and string.endswith(">"):
        return "tag"
    else:
        return "string"


def checkEndTag(start, tagsArray):
    for position in reversed(range(start)):
        #print("tag", position, tagsArray[position])
        if tagsArray[position].startswith("</"):
            endTag = tagsArray[position]
            return position
        

def roadRunner(soups, ime1, ime2):
    
    regexIzraz = ""
    
    stran1 = soups[ime1]
    stran2 = soups[ime2]
    
    dolzina1 = len(stran1)-1
    dolzina2 = len(stran2)-1
    
    pozicija1 = 0
    pozicija2 = 0
    
    while pozicija1 < dolzina1 or pozicija2 < dolzina2:
        
        if stran1[pozicija1] != stran2[pozicija2]: # ce stvar na poziciji ni enaka, dejmo raziskat
            
            # ugotovimo kaksnega tipa so stvari na tej lokaciji
            tip1 = typeOfLocation(stran1[pozicija1])
            tip2 = typeOfLocation(stran2[pozicija2])
            
            if tip1 == tip2 == "string": # string mismatch
                print("Razlicen tekst: ",stran1[pozicija1], "|", stran2[pozicija2])
                if stran1[pozicija1]:
                    stran1[pozicija1] = "#PCDATA" # #PCDATA -> pomeni da nas info na tej lokaciji zanima!
                if stran2[pozicija2]:
                    stran2[pozicija2] = "#PCDATA"
            
            elif tip1 == tip2 == "tag": # tag mismatch
                
                # poišči zaključne značke
                endTag1 = checkEndTag(pozicija1,stran1)
                endTag2 = checkEndTag(pozicija2,stran2)
                
                endTag = None
                if stran1[endTag1] == stran1[endTag2]: # optional ?
                    endTag = endTag1
                    
                    
                else: # iterators (list of items)
                    print("\n\t", "ERROR: Closing tag is wrong!")
                    print("\t", "stran1:", stran1[endTag1], "stran2:", stran2[endTag2], "\n")
                
                
            
            
            
            
            
        if pozicija1 < dolzina1:
            pozicija1 += 1
        if pozicija2 < dolzina2:
            pozicija2 += 1

def prepareFile(filePath, enc='utf-8'):
    r = open(filePath, 'r', encoding=enc)
    html = r.read()
    
    # pobrisemo vse script, style, komentarje
    html = re.sub(r'(?s)<script[^>]*?>([^<]*)</script>', '', html)
    html = re.sub(r'(?s)<style[^>]*?>([^<]*)</style>', '', html)
    html = re.sub(r'(?s)<!--(.*)-->', '', html)
    
    html_bs = BeautifulSoup(html, 'html.parser')
    html_bs = html_bs.body.prettify()
    html_bs = html_bs.split('\n') # vsaka vrstica v svoji celici v tabeli
    html_bs = [space.strip() for space in html_bs] # pobrisi vse zamike (prazne znake, space)
    return html_bs

def extractTest(jsonObj):
    url = 'test'
    testArray = {}
    testArray['test1'] = prepareFile(inputFolderStruct+url+'/test1.html')
    testArray['test2'] = prepareFile(inputFolderStruct+url+'/test2.html')
    roadRunner(testArray, 'test1', 'test2')

def extractRTV(jsonObj):
    url = 'rtvslo.si'
    rtvArray = {}
    rtvArray['audi'] = prepareFile(inputFolderStruct+url+'/Audi A6 50 TDI quattro_ nemir v premijskem razredu - RTVSLO.si.html')
    rtvArray['volvo'] = prepareFile(inputFolderStruct+url+'/Volvo XC 40 D4 AWD momentum_ suvereno med najboljše v razredu - RTVSLO.si.html')
    roadRunner(rtvArray, 'audi', 'volvo')

def extractOverstock(jsonObj):
    url = 'overstock.com'
    overstockArray = {}
    overstockArray['jewelry01'] = htmlFileRead(inputFolderStruct+url+'/jewelry01.html', 'mbcs')
    overstockArray['jewelry02'] = htmlFileRead(inputFolderStruct+url+'/jewelry02.html', 'mbcs')
    roadRunner(overstockArray, 'jewelry01', 'jewelry02')

def extractOwnPages(jsonObj):
    url = 'avto.net'
    avtoArray = {}
    avtoArray['Justy'] = htmlFileRead(inputFolderStruct+url+'/Justy.html', 'windows-1250')
    avtoArray['Legacy'] = htmlFileRead(inputFolderStruct+url+'/Legacy.html', 'windows-1250')
    roadRunner(avtoArray, 'Justy', 'Legacy')

def exportJson(jsonText):
    f = open(outputFolderStruct+'xPathExport.json', 'wb')
    f.write(jsonText.encode('utf8'))

def main(printing):
    jsonObj = {}
    #extractOverstock(jsonObj)
    #extractRTV(jsonObj)
    #extractOwnPages(jsonObj)
    
    extractTest(jsonObj)
    
    jsonText = json.dumps(jsonObj, ensure_ascii=False) # ensure_ascii=False -> da zapisuje tudi čšž
    if(printing):
        print(jsonText) # The method should output extracted data in a JSON structured format to a standard output.
    else:
        exportJson(jsonText)

if __name__ == '__main__':
    main(False)