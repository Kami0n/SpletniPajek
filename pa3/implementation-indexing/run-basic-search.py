# To get a feeling of a speed-up in search using an inverted index, implement searching without the SQLite database.
# Instead of using the database, your algorithm should sequentially open each file, process it and merge the results.
# The parsing and preprocessing part must be the same as in searching with the SQLite database.
# Use the same search queries with this naive approach and compare the query execution times to inverted index implementation 

#  /implementation-indexing/run-basic-search.py SEARCH_PARAM


def prepareSearchParams(searchParams):
    
    print("Results for a query: \"" + ' '.join(map(str, searchParams)) + "\"")
    
    searchParamsLow = [word.lower() for word in searchParams]
    searchParamsString = ""
    for word in searchParamsLow:
        searchParamsString += "'"+word+"'"
        if word != searchParamsLow[-1]:
            searchParamsString +=","
    return searchParamsString

def main():
    searchParamsString = prepareSearchParams(sys.argv[1:])
    print(searchParamsString)
    
    
    
    
    # koda ...



if __name__ == "__main__":
    main()