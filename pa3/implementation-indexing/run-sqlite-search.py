import sys
import time
import sqlite3

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

def main():
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
    
    
    # You should close the connection when stopped using the database.
    
    
    
    # izpis
    timeTaken = (time.time()-t1)*1000
    print(f'\n\tResults found in {timeTaken} ms')
    print("\n\tFrequencies Document                                  Snippet")
    print("\t----------- ----------------------------------------- -----------------------------------------------------------")
    
    for row in cursor:
        #print(f"\tHits: {row[1]}\n\t\tDoc: '{row[0]}'\n\t\tIndexes: {row[2]}")
        print("\t%-5s       %-41s %s" % (row[1], row[0], row[2]))
        pass
    
    #for e in s:
    #    print("%-5s       %-41s %s" % (e[0], e[1], e[2]))
    
    print("\n")
    
    conn.close()

if __name__ == "__main__":
    main()