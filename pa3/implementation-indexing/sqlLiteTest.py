import sqlite3
conn = sqlite3.connect('inverted-index.db')

# Create table
c = conn.cursor()

# c.execute('''
#     CREATE TABLE IndexWord (
#         word TEXT PRIMARY KEY
#     );
# ''')
#
# c.execute('''
#     CREATE TABLE Posting (
#         word TEXT NOT NULL,
#         documentName TEXT NOT NULL,
#         frequency INTEGER NOT NULL,
#         indexes TEXT NOT NULL,
#         PRIMARY KEY(word, documentName),
#         FOREIGN KEY (word) REFERENCES IndexWord(word)
#     );
# ''')

# Save (commit) the changes
conn.commit()

# We can also close the connection if we are done with it.
# Just be sure any changes have been committed or they will be lost.
# conn.close()
# beseda = 'janez';
#
# c.execute('''
#     INSERT INTO IndexWord VALUES
#         ('+beseda+');
# ''')

# c.execute('''
#     INSERT INTO Posting VALUES
#         ('Spar', 'spar.si/info.html', 1, '92'),
#         ('Mercator', 'mercator.si/prodaja.html', 3, '4,12,55'),
#         ('Mercator', 'tus.si/index.html', 1, '18'),
#         ('Tuš', 'mercator.si/prodaja.html', 1, '42');
# ''')

# Save (commit) the changes
conn.commit()



print("Selecting all the data from the Posting table:")

for row in c.execute("SELECT * FROM IndexWord i"):
    print(f"\t{row}")


# print("Get all documents that contain 'Tuš' or 'Mercator'.")
#
# cursor = c.execute('''
#     SELECT p.documentName AS docName, SUM(frequency) AS freq, GROUP_CONCAT(indexes) AS idxs
#     FROM Posting p
#     WHERE
#         p.word IN ('Tuš', 'Mercator')
#     GROUP BY p.documentName
#     ORDER BY freq DESC;
# ''')

# for row in cursor:
#     print(f"\tHits: {row[1]}\n\t\tDoc: '{row[0]}'\n\t\tIndexes: {row[2]}")
#

# You should close the connection when stopped using the database.
conn.close()