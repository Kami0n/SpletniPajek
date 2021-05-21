# README

## Installation of dependencies

Move to folder `pa3/implementation-indexing` and install all dependecies from `requirements.txt`, with command:
```
pip install -r requirements.txt
```

## Running indexing

Move to folder `pa3/implementation-indexing` and run:

For building index database (not necessary, database is already built):
```
./implementation-indexing/buildingIndexNewer1.py
```

For basic search:
```
./implementation-indexing/run-basic-search.py "SEARCH_PARAMS"
```

For search with inverted index (SQLite):
```
./implementation-indexing/run-sqlite-search.py "SEARCH_PARAMS"
```