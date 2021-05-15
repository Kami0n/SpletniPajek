import os
from bs4 import BeautifulSoup
from bs4.element import Comment
import urllib.request

from nltk.tokenize import LegalitySyllableTokenizer
from nltk import word_tokenize
from nltk.corpus import words

from stopwords import *

import pickle

import sqlite3

conn = sqlite3.connect('inverted-index.db')


# pridobimo besedilo iz vsake spletne strani:
# funkcija text na vsaki spletni strani
# text()

# razbijemo besedilo na besede
# funkcije: NLTK

# odstranjevanje stop besed

# vse besede v lowercase

# additional processing steps ? -> kaj bi bilo smiselno
# datumi v enotno obliko, valute, številke ali ne?

# vse vsebine shranimo v podatkovno bazo -> inverted-index.db


# v bazo se zapiše:
# vse besede ki jih poznamo -> v tabelo IndexWord

# tabela Posting:
# primarna ključa: beseda (iz IndexWord) in dokument
# frekvenca besede v dokumentu, kje se pojavi (indexi)

# indexi so uporabni ob poizvedbi, da se izpiše snippet (okolica besede)

def tagVisible(element):
    if element.parent.name in ['style', 'script']:  # , 'head', 'title', 'meta', '[document]'
        return False
    if isinstance(element, Comment):
        return False
    return True


def textFromHtml(body):
    soup = BeautifulSoup(body, 'lxml')
    texts = soup.findAll(text=True)
    visible_texts = filter(tagVisible, texts)
    return u" ".join(t.strip() for t in visible_texts)


def containsChar(niz):
    flag = False
    for znak in niz:
        if znak.isalpha():
            flag = True
    return flag


def prepareText(filePath, enc='utf-8'):
    htmlFile = open(filePath, 'r', encoding=enc)
    textStarting = textFromHtml(htmlFile.read())

    # lower case
    textLower = textStarting.lower()

    # tokenization
    word_tokens = word_tokenize(textLower)

    # stop word removal
    filtered_sentence = [w for w in word_tokens if not w in stop_words_slovene]

    return filtered_sentence


def prepareTextAll(filePath, enc='utf-8'):
    htmlFile = open(filePath, 'r', encoding=enc)
    textStarting = textFromHtml(htmlFile.read())

    # lower case
    textLower = textStarting.lower()

    # tokenization
    word_tokens = word_tokenize(textLower)

    return word_tokens

def main():
    # baseDir = "../PA3-test"
    baseDir = "../PA3-data"
    htmlText = []
    c = conn.cursor()

    pickleFileName = "pickleDict.pkl"
    text_files = {}

    try:
        print("Creating database structure")
        c.execute('''
            CREATE TABLE IndexWord (
                word TEXT PRIMARY KEY
            );
        ''')

        c.execute('''
            CREATE TABLE Posting (
                word TEXT NOT NULL,
                documentName TEXT NOT NULL,
                frequency INTEGER NOT NULL,
                indexes TEXT NOT NULL,
                PRIMARY KEY(word, documentName),
                FOREIGN KEY (word) REFERENCES IndexWord(word)
            );
        ''')
    except:
        print("Database structure already exists")
        pass

    print("Building inverted index and pickle")
    for path, subdirs, files in os.walk(baseDir):
        for name in files:
            filePathFull = os.path.join(path, name)
            filePath = filePathFull.replace(baseDir + "\\", '')

            htmlText = prepareText(filePathFull)

            besedePojavitve = dict()
            besedeFrekvenca = dict()
            i = 0
            for word in htmlText:
                key = (word)
                if word in besedeFrekvenca:
                    besedeFrekvenca[word] += 1
                else:
                    besedeFrekvenca[word] = 1
                try:
                    pass
                    c.execute('INSERT INTO IndexWord VALUES (?); ', [key])
                except:
                    pass

                i += 1

            # dejanski indeksi besed
            htmlTextAll = prepareTextAll(filePathFull)
            
            text_files[filePath] = htmlTextAll  # for pickle
            
            i = 0
            for word in htmlTextAll:
                key = (word)

                if word in besedeFrekvenca:
                    if key in besedePojavitve:
                        # append the new number to the existing array at this slot
                        besedePojavitve[key].append(i)
                    else:
                        # create a new array in this slot
                        besedePojavitve[key] = []
                        besedePojavitve[key].append(i)

                i += 1

            for key in besedeFrekvenca:
                vnos = (key, filePath, besedeFrekvenca[key], str(besedePojavitve[key])[1:-1])
                try:
                    pass
                    c.execute('INSERT INTO Posting VALUES (?, ?, ?, ?)', vnos)
                except:
                    pass

            # print(besedePojavitve)
            # print(besedeFrekvenca)
            # print(besedeFrekvenca['trga'])
            # print(str(besedePojavitve['trga']))

    conn.commit()
    # You should close the connection when stopped using the database.
    conn.close()
    print("Inverted index commited to database")

    f = open(pickleFileName, "wb")
    pickle.dump(text_files, f)
    f.close()
    print("Pickle saved to file")


if __name__ == "__main__":
    main()