import os
from bs4 import BeautifulSoup
from bs4.element import Comment
import urllib.request

from nltk.tokenize import LegalitySyllableTokenizer
from nltk import word_tokenize
from nltk.corpus import words

from stopwords import *  

import sqlite3
conn = sqlite3.connect('inverted-index.db')

def tagVisible(element):
    if element.parent.name in ['style', 'script']: # , 'head', 'title', 'meta', '[document]'
        return False
    if isinstance(element, Comment):
        return False
    return True

def textFromHtml(body):
    soup = BeautifulSoup(body, 'lxml')
    texts = soup.findAll(text=True)
    visible_texts = filter(tagVisible, texts)
    return u" ".join(t.strip() for t in visible_texts)

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


baseDir = "../PA3-test"
#baseDir = "../PA3-data"
htmlText = []
for path, subdirs, files in os.walk(baseDir):
    for name in files:
        htmlText += prepareText(os.path.join(path, name))
        print(htmlText)
    keys = list(dict.fromkeys(htmlText))
    c = conn.cursor()
    for key in keys:
        query1 = "INSERT INTO IndexWord VALUES('" + key + "');"
        try:
            c.execute(query1)
        except sqlite3.IntegrityError:
            print("### "+query1)
            print()

    conn.commit()

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




# You should close the connection when stopped using the database.
conn.close()