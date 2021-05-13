import sys
import time
import sqlite3
import pickle
import string

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


levaLocila = [
    "(", "»","[", "<", 
]

desnaLocila = [
    ")", ".", ",", ";", ":", "!", "?", "«","]",">",
]

ostalaLocila = [
    "©", "•", "-", "/", "|", "-", "+", "--", "---", "\\", "@", "=", 
    "&", "'", "...", "''","★", "☆", "▼", "--", "–", "``"
]

okolicaSnippet = 3
def wordsBeforeAfterOld(index, textFile, before=True, okolica=okolicaSnippet):
    vmes = okolica != okolicaSnippet
    
    tmpSnippet = ""
    steviloBesed = 0
    ind = 0
    while steviloBesed < okolica: # 3 words before, 3 after
        ind += 1
        newIndex = -1
        
        if before:
            newIndex = index - ind
            if newIndex < 0:
                break
        else:
            newIndex = index + ind
            if index + ind > len(textFile):
                break
        
        delcek = textFile[newIndex]
        
        #if delcek.isalnum() or vmes: # ce je polnopravna beseda ali stevilka, povecaj ali pa ce gre za vmes
        if delcek not in string.punctuation or vmes:
            steviloBesed += 1
        
        if before:
            if delcek in string.punctuation:
                tmpSnippet = delcek + tmpSnippet
            else:
                tmpSnippet = " "+delcek + tmpSnippet
        else:
            if delcek in string.punctuation:
                tmpSnippet += delcek
            else:
                tmpSnippet += " "+delcek
            
    return tmpSnippet

def prepareSnippetOld(row, textFile):
    
    indexesTmp = list(row[2].replace(" ", "").split(",")) # get all indexes from row[2]
    indexes = list(map(int, indexesTmp))
    indexes.sort()
    
    snippet = ""
    vmes = -1
    
    for idx, index in enumerate(indexes):
        
        if vmes == -1: # ni skupaj, izpisi predhodne 3 besede
            if(not snippet.endswith("...")):
                snippet += "..."
            snippet += wordsBeforeAfter(index, textFile, True)
        else: # ce je skupaj izpisi vse besede do
            snippet += wordsBeforeAfter(index, textFile, True, okolica=vmes)
            vmes = -1
            
        snippet += " "+textFile[index]
        
        if idx+1 < len(indexes) and indexes[idx+1] - index <= (okolicaSnippet*2)+2: # +2 za iskani besedi
            vmes = indexes[idx+1] - index
            vmes -= 1
        else:
            vmes = -1
            snippet += wordsBeforeAfter(index, textFile, False)
            snippet += " ..."
    
    
    return snippet


def wordsBeforeAfter(index, textFile, before=True, okolica=okolicaSnippet):
    vmes = okolica != okolicaSnippet
    
    tmpSnippet = []
    steviloBesed = 0
    ind = 0
    while steviloBesed < okolica: # 3 words before, 3 after
        ind += 1
        newIndex = -1
        
        if before:
            newIndex = index - ind
            if newIndex < 0:
                break
        else:
            newIndex = index + ind
            if index + ind > len(textFile):
                break
        
        delcek = textFile[newIndex]
        
        #if delcek.isalnum() or vmes: # ce je polnopravna beseda ali stevilka, povecaj ali pa ce gre za vmes
        if delcek not in string.punctuation or vmes:
            steviloBesed += 1
        
        
        
        if before:
            #if delcek in string.punctuation:
            #    tmpSnippet = delcek + tmpSnippet
            #else:
            #    tmpSnippet = " "+delcek + tmpSnippet
            tmpSnippet.insert(0, delcek)
        else:
            #if delcek in string.punctuation:
            #    tmpSnippet += delcek
            #else:
            #    tmpSnippet += " "+delcek
            tmpSnippet.append(delcek)
            
    return tmpSnippet

def prepareSnippet(row, textFile):
    
    indexesTmp = list(row[2].replace(" ", "").split(",")) # get all indexes from row[2]
    indexes = list(map(int, indexesTmp))
    indexes.sort()
    
    snippetArr = []
    vmes = -1
    
    for idx, index in enumerate(indexes):
        if vmes == -1: # ni skupaj, izpisi predhodne 3 besede
            if len(snippetArr) == 0 or snippetArr[-1] != "...":
                snippetArr.append("...")
            snippetArr.extend(wordsBeforeAfter(index, textFile, True)) #extend
        else: # ce je skupaj izpisi vse besede do
            snippetArr.extend(wordsBeforeAfter(index, textFile, True, okolica=vmes))
            vmes = -1
        snippetArr.append(textFile[index])
        
        if idx+1 < len(indexes) and indexes[idx+1] - index <= (okolicaSnippet*2)+2: # +2 za iskani besedi
            vmes = indexes[idx+1] - index
            vmes -= 1
        else:
            vmes = -1
            snippetArr.extend(wordsBeforeAfter(index, textFile, False))
            snippetArr.append("...")
    
    snippet = ""
    for elem in snippetArr:
        if elem in desnaLocila:
            snippet += elem
        elif len(snippet) > 0 and snippet[-1] in levaLocila:
            snippet +=  elem
        else:
            snippet +=  " "+elem
    
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
        print("\t%-5s       %-41s %s" % (row[1], row[0], prepareSnippet(row, text_files[row[0]]))) #row[2]
    
    print("\n")
    
    conn.close() # You should close the connection when stopped using the database.

if __name__ == "__main__":
    if len(sys.argv) > 1:
        main()
    else:
        print("\nInput parameters empty!")
        exit(-1)