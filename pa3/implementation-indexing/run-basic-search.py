import sys
import time
import os
#from bs4 import BeautifulSoup
#from bs4.element import Comment
#import urllib.request

#from nltk.tokenize import LegalitySyllableTokenizer
#from nltk import word_tokenize
#from nltk.corpus import words

#from stopwords import *  

from buildingIndex import prepareText 

# To get a feeling of a speed-up in search using an inverted index, implement searching without the SQLite database.
# Instead of using the database, your algorithm should sequentially open each file, process it and merge the results.
# The parsing and preprocessing part must be the same as in searching with the SQLite database.
# Use the same search queries with this naive approach and compare the query execution times to inverted index implementation 

#  /implementation-indexing/run-basic-search.py SEARCH_PARAM


def prepareSearchParams(searchParams):
    
    print('\nResults for a query: \"' + ' '.join(map(str, searchParams)) + '\"')
    
    searchParamsLow = [word.lower() for word in searchParams]
    return searchParamsLow

def prepareSnippet(row, text_files):
    textFile = text_files[row[0]]
    
    indexes = list(row[2].replace(" ", "").split(",")) # get all indexes from row[2]
    indexes = list(map(int, indexes))
    
    snippet = ""
    
    # 3 words before, 3 after
    for index in indexes:
        
        if(not snippet.endswith("... ")):
            snippet += "... "
        if(textFile[index-3]):
            snippet += textFile[index-3]+" "
        if(textFile[index-2]):
            snippet += textFile[index-2]+" "
        if(textFile[index-1]):
            snippet += textFile[index-1]+" "
        
        snippet += textFile[index]+" "
        
        if(textFile[index+1]):
            snippet += textFile[index+1]+" "
        if(textFile[index+2]):
            snippet += textFile[index+2]+" "
        if(textFile[index+3]):
            snippet += textFile[index+3]+" "
        snippet += "... "
    
    return snippet

def main():
    
    baseDir = "../PA3-data"
    
    t1 = time.time()
    searchParams = prepareSearchParams(sys.argv[1:])
    
    documentsWithWord = {}
    
    # search 
    
    for path, subdirs, files in os.walk(baseDir):
        for name in files:
            filePathFull = os.path.join(path, name)
            filePath = filePathFull.replace(baseDir+"\\", '')
            
            htmlText = prepareText(filePathFull)
            
            for everyWord in htmlText:
                if everyWord in searchParams:
                    if name in documentsWithWord:
                        documentsWithWord[name] += 1
                    else:
                        documentsWithWord[name] = 1
    
    # izpis
    timeTaken = round((time.time()-t1)*1000,3)
    print(f'\n\tResults found in {timeTaken} ms')
    print("\n\tFrequencies Document                                  Snippet")
    print("\t----------- ----------------------------------------- -----------------------------------------------------------")
    
    for row in documentsWithWord:
        print("\t%-5s       %-41s %s" % (-1, row, "" )) #row[2]
    
    print("\n")
    
if __name__ == "__main__":
    if len(sys.argv) > 1:
        main()
    else:
        print("\nInput parameters empty!")
        exit(-1)