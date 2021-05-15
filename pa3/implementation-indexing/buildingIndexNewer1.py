import os
from bs4 import BeautifulSoup
from bs4.element import Comment
from nltk import word_tokenize
import pickle

from stopwords import *

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


def containsChar(niz):
    if niz.isnumeric():
        return False
    for znak in niz:
        if znak.isalpha():
            return True
    return False


def textFromHtml(body):
    soup = BeautifulSoup(body, 'lxml')
    texts = soup.findAll(text=True)
    visible_texts = filter(tagVisible, texts)
    return u" ".join(t.strip() for t in visible_texts)


def prepareText(filePath, enc='utf-8'):
    htmlFile = open(filePath, 'r', encoding=enc)
    textStarting = textFromHtml(htmlFile.read())
    
    word_tokens_all = word_tokenize(textStarting)
    
    textLower = textStarting.lower() # lower case
    word_tokens = word_tokenize(textLower) # tokenization
    filtered_sentence = [w for w in word_tokens if not w in stop_words_slovene] # stop word removal

    # removes numbers, links, appostrofs,
    for index, w in enumerate(filtered_sentence):
        if containsChar(w) is False:
            filtered_sentence.pop(index)
        if w[0] == '/':
            filtered_sentence.pop(index)
        if w[0] == "'":
            filtered_sentence[index] = w[1:]

    return filtered_sentence, word_tokens_all

def main():
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

    print("Building inverted index and pickle")
    for path, subdirs, files in os.walk(baseDir):
        for name in files:
            filePathFull = os.path.join(path, name)
            filePath = filePathFull.replace(baseDir + "\\", '')
            
            htmlText,htmlTextAll  = prepareText(filePathFull)
            text_files[filePath] = htmlTextAll  # for pickle
            
            besedePojavitve = dict()
            besedeFrekvenca = dict()
            for word in htmlText:
                key = (word)
                if word not in besedeFrekvenca:
                    besedeFrekvenca[word] = 0
                besedeFrekvenca[word] += 1
                
                try:
                    c.execute('INSERT INTO IndexWord VALUES (?); ', [key])
                except:
                    pass
            
            # dejanski indeksi besed
            index = 0
            for word in htmlTextAll:
                wordLow = word.lower()
                if wordLow[0] == "'":
                    wordLow = wordLow[1:]
                key = (wordLow)
                if wordLow in besedeFrekvenca:
                    if key not in besedePojavitve:
                        # create a new array in this slot
                        besedePojavitve[key] = []
                        
                    # append the new number to the existing array at this slot
                    besedePojavitve[key].append(index)
                    
                index += 1
            
            #diff = set(besedeFrekvenca) - set(besedePojavitve)
            #if diff:
            #    print(diff)
            
            for key in besedePojavitve:
                vnos = (key, filePath, besedeFrekvenca[key], str(besedePojavitve[key])[1:-1])
                try:
                    c.execute('INSERT INTO Posting VALUES (?, ?, ?, ?)', vnos)
                except:
                    pass

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