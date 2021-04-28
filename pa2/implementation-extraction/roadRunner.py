from lxml import html
from bs4 import BeautifulSoup, Comment, Tag
import numpy as np

inputFolderStruct = '../input-extraction/'
outputFolderStruct = '../'

VARIABLE_STRING = '[ VARIABLE STRING ]'

def detectTag(s):
    return "<" in s

def clean_token(token):
    has_starting_tag = "<" in token
    has_start_ending_tag = "/>" in token
    has_ending_tag = "</" in token

    ss = token.split()
    if len(ss) > 1:
        if has_starting_tag and has_start_ending_tag:
            return ss[0] + "/>"
        else:
            if has_starting_tag and not has_start_ending_tag:
                return ss[0] + ">"
            if has_ending_tag:
                return ss[0] + ">"
    else:
        return ss[0]

def roadRunner(body1, body2):
    
    i = 0
    j = 0
    
    result = []
    wrapper = body1
    
    while i < len(body1) and j < len(body2):
        
        token1 = body1[i]
        token2 = body2[j]
        
        if detectTag(token1) and detectTag(token2):
            if token1.split()[0] == token2.split()[0]: # same tag
                result.append(clean_token(token1))
                
            
            else: # tag mismatch
                
                result.append("tag mismatch")
                
            """
            else:
                iterator = self.check_iterator(i, j)
                if iterator and all(iterator):
                    sample_end_of_iterator, wrapper_start_of_iterator, wrapper_end_of_iterator, iterator_square = iterator
                    prvi_del = self.wrapper[:wrapper_start_of_iterator]
                    drugi_del = self.wrapper[wrapper_end_of_iterator + 1:]
                    self.wrapper = prvi_del + [("Iterator", iterator_square)] + drugi_del
                    i = wrapper_start_of_iterator + 1
                    j = sample_end_of_iterator + 1
                else:
                    file, start_optional, end_optional = self.check_optional(i, j)
                    if file == "wrapper":
                        if end_optional:
                            #a = t[:i+1] + [4] + t[i+1:]
                            optional = self.wrapper[start_optional:end_optional]
                            self.wrapper = self.wrapper[:i] + [("Optional" ,self.clean_object(optional))] + self.wrapper[i:]
                            i = end_optional + 1
                            continue
                    else:
                        if end_optional:
                            optional = self.sample[start_optional:end_optional]
                            self.wrapper = self.wrapper[:i] + [("Optional", self.clean_object(optional))] + self.wrapper[i:]
                            j = end_optional
                            i += 1
                            continue
            """
        
        elif not detectTag(token1) and not detectTag(token2):
            if token1 == token2:
                result.append(token1)
            else:
                result.append(VARIABLE_STRING)
        i += 1
        j += 1
    # konec zanke
    
    return result


def prepareFile(filePath, enc='utf-8'):
    file = open(filePath, 'r', encoding=enc)
    htmlBs = BeautifulSoup(file.read(), 'lxml')
    
    # remove all comments
    for comment in htmlBs.findAll(text=lambda text: isinstance(text, Comment)):
        comment.extract()
    
    # remove unwanted elements
    elementsRemoveArray = ['style', 'script', 'link', 'meta', 'iframe', 'nav', 'map', 'input', 'svg', 'img', 'picture', 'figure', 'figcaption', 'footer']
    for elementRemove in elementsRemoveArray:
        [element.decompose() for element in htmlBs.findAll(elementRemove)]
    
    elementsAvto = [{'class':'modal-body'}, {'class':'modal'}, {'id':'LegendaModal'}, {'id':'FilterModal'}, {'class':'GO-ResultsMenuBox'}]
    for element in elementsAvto:
        for div in htmlBs.findAll('div', element): 
            div.decompose()
    
    htmlString = htmlBs.prettify()
    htmlArray = [x.strip() for x in htmlString.split("\n") if x]
    
    htmlReturnArray = []
    tmp = " "
    
    for i in range(len(htmlArray)):
        if detectTag(htmlArray[i]):
            htmlReturnArray.append(htmlArray[i])
        else:
            if not detectTag(htmlArray[i]): # is string ?
                tmp += htmlArray[i].strip() + " "
            if detectTag(htmlArray[i + 1]): # is tag
                htmlReturnArray.append(tmp.strip())
                tmp = ""
    
    return htmlReturnArray

def extractRTV(printing):
    url = 'rtvslo.si'
    ignoreLevel = 4
    rtvArray = {}
    rtvArray['audi'] = prepareFile(inputFolderStruct+url+'/Audi A6 50 TDI quattro_ nemir v premijskem razredu - RTVSLO.si.html')
    rtvArray['volvo'] = prepareFile(inputFolderStruct+url+'/Volvo XC 40 D4 AWD momentum_ suvereno med najboljše v razredu - RTVSLO.si.html')
    
    body1 = rtvArray['audi'].find('body')
    body2 = rtvArray['volvo'].find('body')
    
    wrapper = roadRunner(body1, body2)
    showOvojnica(url, wrapper, printing)

def extractOverstock(printing):
    url = 'overstock.com'
    ignoreLevel = 5
    overstockArray = {}
    overstockArray['jewelry01'] = prepareFile(inputFolderStruct+url+'/jewelry01.html', 'mbcs')
    overstockArray['jewelry02'] = prepareFile(inputFolderStruct+url+'/jewelry02.html', 'mbcs')
    
    body1 = overstockArray['jewelry01'].find('body')
    body2 = overstockArray['jewelry02'].find('body')
    
    wrapper = roadRunner(body1, body2)
    showOvojnica(url, wrapper, printing)

def extractOwnPages(printing):
    url = 'avto.net'
    ignoreLevel = 4
    avtoArray = {}
    avtoArray['Justy'] = prepareFile(inputFolderStruct+url+'/Justy.html', 'windows-1250')
    avtoArray['Legacy'] = prepareFile(inputFolderStruct+url+'/Legacy.html', 'windows-1250')
    
    body1 = avtoArray['Justy'].find('body')
    body2 = avtoArray['Legacy'].find('body')
    
    wrapper = roadRunner(body1, body2)
    showOvojnica(url, wrapper, printing)

def extractTest(printing):
    url = 'test'
    ignoreLevel = 4
    
    body1 = prepareFile(inputFolderStruct+url+'/test1.html')
    body2 = prepareFile(inputFolderStruct+url+'/test2.html')
    
    wrapper = roadRunner(body1, body2)
    showOvojnica(url, wrapper, printing)


def showOvojnica(ime, result, printing):
    
    stringResult = ""
    for cell in result:
        stringResult = stringResult + "\n"+cell
    
    soupResult = BeautifulSoup(stringResult, 'lxml')
    resultBody = soupResult.find('body')
    ovojnica = resultBody.prettify(encoding=None, formatter=None) # 'minimal'
    
    if(printing):
        print('\nGeneralizirana ovojnica strani '+ime+':\n')
        print(ovojnica) # The method should output extracted data in a JSON structured format to a standard output.
    
    print('\nGeneralizirana ovojnica strani '+ime+' je zapisana v datoteko.\n')
    f = open(outputFolderStruct+'automatic.xml', 'wb')
    f.write(ovojnica.encode('utf8'))

def main(printing):
    #extractOverstock(printing)
    #extractRTV(printing)
    #extractOwnPages(printing)
    extractTest(printing)

if __name__ == '__main__':
    printing = True
    main(printing)
