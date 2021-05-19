import sys
import time
import os
# from bs4 import BeautifulSoup
# from bs4.element import Comment
# import urllib.request

# from nltk.tokenize import LegalitySyllableTokenizer
# from nltk import word_tokenize
# from nltk.corpus import words

# from stopwords import *

from buildingIndexNewer1 import prepareText


# To get a feeling of a speed-up in search using an inverted index, implement searching without the SQLite database.
# Instead of using the database, your algorithm should sequentially open each file, process it and merge the results.
# The parsing and preprocessing part must be the same as in searching with the SQLite database.
# Use the same search queries with this naive approach and compare the query execution times to inverted index implementation

#  /implementation-indexing/run-basic-search.py SEARCH_PARAM


def prepareSearchParams(searchParams):
    searchParamsLow = [word.lower() for word in searchParams]
    return searchParamsLow


locila = ["©", "•", "-", "|", "-", "+", "--", "---", "\\", "@", "=", "&", "''", "'", " ", "   ", "★", "☆", "▼", "--",
          "–", "``"]

locilaLS = [")", ".", ",", ";", ":", "!", "?", "/", ">", "]", "=", "«", "...", "’"]

locilaDS = ["(", "<", "[", "«"]

locilaBS = ["©","@"]

okolicaSnippet = 3


def wordsBeforeAfter(index, textFile, okolica=okolicaSnippet):
    vmes = okolica != okolicaSnippet

    tmpSnippet = ""
    steviloBesed = 0
    ind = 0
    while steviloBesed < okolica:  # 3 words before, 3 after
        ind += 1
        newIndex = -1

        newIndex = index - ind
        if newIndex < 0:
            break

        delcek = textFile[newIndex]
        if delcek.isalnum() or vmes:  # ce je polnopravna beseda ali stevilka, povecaj ali pa ce gre za vmes
            steviloBesed += 1

        if delcek in locilaLS:
            tmpSnippet = delcek + tmpSnippet
        elif delcek in locilaBS and tmpSnippet[0] == " ":
            tmpSnippet = tmpSnippet[1:]
            tmpSnippet = delcek + tmpSnippet
        else:
            if delcek in locilaDS or delcek in locilaBS:
                tmpSnippet = delcek + tmpSnippet
            else:
                tmpSnippet = " " + delcek + tmpSnippet
            

    return tmpSnippet


def main():
    baseDir = "../PA3-data"
    # baseDir = "../PA3-test"

    t1 = time.time()

    searchParamsDisplay = sys.argv[1:]
    searchParams = prepareSearchParams(searchParamsDisplay)

    besedeFrekvenca = {}
    snippets = {}

    # search
    for path, subdirs, files in os.walk(baseDir):
        for name in files:
            filePathFull = os.path.join(path, name)
            filePathFull.replace(baseDir + "\\", '')
            htmlText, htmlTextAll = prepareText(filePathFull)

            vmes = -1
            tmpIndex = -1
            zapisovanje = False

            for idx, everyWord in enumerate(htmlTextAll):
                word = everyWord.lower()

                if word in searchParams:

                    if name not in besedeFrekvenca:
                        besedeFrekvenca[name] = 0
                    besedeFrekvenca[name] += 1

                    if name not in snippets:
                        snippets[name] = ""

                    if not zapisovanje:
                        if (not snippets[name].endswith("...")):
                            snippets[name] += "..."
                        snippets[name] += wordsBeforeAfter(idx, htmlTextAll)

                    tmpIndex = idx
                    zapisovanje = True

                if zapisovanje:

                    if not snippets[name].isalnum():
                        if idx - tmpIndex > 4:
                            zapisovanje = False
                        else:
                            if word in locilaLS or word in locilaBS:
                                snippets[name] += htmlTextAll[idx]
                            else:
                                if snippets[name][-1] in locilaDS or snippets[name][-1] in locilaBS:
                                    snippets[name] += htmlTextAll[idx]
                                else:
                                    snippets[name] += " " + htmlTextAll[idx]

                    else:
                        snippets[name] += htmlTextAll[idx]
                        tmpIndex += 1

    documentsWithWordSorted = dict(sorted(besedeFrekvenca.items(), key=lambda x: x[1], reverse=True))

    # izpis
    print('\nResults for a query: \"' + ' '.join(map(str, searchParamsDisplay)) + '\"')

    timeTaken = round((time.time() - t1), 3)
    if timeTaken > 1:
        print(f'\n\tResults found in {timeTaken} s')
    else:
        timeTaken = timeTaken * 1000
        print(f'\n\tResults found in {timeTaken} ms')

    print("\n\tFrequencies Document                                  Snippet")
    print(
        "\t----------- ----------------------------------------- -----------------------------------------------------------")

    for filename in documentsWithWordSorted:
        print("\t%-5s       %-41s %s" % (besedeFrekvenca[filename], filename, snippets[filename]))  # row[2]

    print("\n")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        main()
    else:
        print("\nInput parameters empty!")
        exit(-1)