import sys
import time
import sqlite3
import pickle

# Results for a query: "Sistem SPOT"
# Results found in 4ms.
# Frequencies    Document    Snippet

# Query for report:
# predelovalne dejavnosti
# trgovina
# social services
# Define additional three queries consisting of 1-5 words that have at least one result.

#  /implementation-indexing/run-sqlite-search.py SEARCH_PARAM

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
        
        snippet += "... "
        snippet += textFile[index-3]+" "
        snippet += textFile[index-2]+" "
        snippet += textFile[index-1]+" "
        snippet += textFile[index]+" "
        snippet += textFile[index+1]+" "
        snippet += textFile[index+2]+" "
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
    
    conn = sqlite3.connect('inverted-index.db')
    c = conn.cursor()
    cursor = c.execute(f'''
        SELECT p.documentName AS docName, SUM(frequency) AS freq, GROUP_CONCAT(indexes) AS idxs
        FROM Posting p
        WHERE p.word IN ({searchParamsString})
        GROUP BY p.documentName
        ORDER BY freq DESC;
    ''')
    
    # izpis
    
    
    
    
    
    timeTaken = round((time.time()-t1)*1000,3)
    print(f'\n\tResults found in {timeTaken} ms')
    print("\n\tFrequencies Document                                  Snippet")
    print("\t----------- ----------------------------------------- -----------------------------------------------------------")
    
    for row in cursor:
        print("\t%-5s       %-41s %s" % (row[1], row[0], prepareSnippet(row, text_files))) #row[2]
    
    print("\n")
    
    conn.close() # You should close the connection when stopped using the database.

if __name__ == "__main__":
    main()