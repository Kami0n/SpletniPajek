import sys
import time
import pickle

# To get a feeling of a speed-up in search using an inverted index, implement searching without the SQLite database.
# Instead of using the database, your algorithm should sequentially open each file, process it and merge the results.
# The parsing and preprocessing part must be the same as in searching with the SQLite database.
# Use the same search queries with this naive approach and compare the query execution times to inverted index implementation 

#  /implementation-indexing/run-basic-search.py SEARCH_PARAM


def prepareSearchParams(searchParams):
    
    print('\nResults for a query: \"' + ' '.join(map(str, searchParams)) + '\"')
    
    searchParamsLow = [word.lower() for word in searchParams]
    searchParamsString = ""
    for word in searchParamsLow:
        searchParamsString += "'"+word+"'"
        if word != searchParamsLow[-1]:
            searchParamsString +=","
    return searchParamsString

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
    
    pickleFileName = "pickleDict.pkl"
    f = open(pickleFileName, "rb")
    text_files = pickle.load(f)
    f.close()
    
    t1 = time.time()
    searchParamsString = prepareSearchParams(sys.argv[1:])
    
    # search 
    
    
    
    
    # izpis
    timeTaken = round((time.time()-t1)*1000,3)
    print(f'\n\tResults found in {timeTaken} ms')
    print("\n\tFrequencies Document                                  Snippet")
    print("\t----------- ----------------------------------------- -----------------------------------------------------------")
    
    for row in cursor:
        print("\t%-5s       %-41s %s" % (row[1], row[0], prepareSnippet(row, text_files))) #row[2]
    
    print("\n")
    
    conn.close() # You should close the connection when stopped using the database.

if __name__ == "__main__"