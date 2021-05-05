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




# You should close the connection when stopped using the database.
conn.close()