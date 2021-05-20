# README

## Installation of dependencies

Move to folder `pa3/implementation-indexing` and install all dependecies from `requirements.txt`, with command:
```
pip install -r requirements.txt
```

## Running indexing

Move to folder `pa3` and run:

Building index database:
```
./implementation-indexing/buildingIndexNewer1.py
```

For basic search:

```
./implementation-indexing/run-basic-search.py SEARCH_PARAM
```

For search with inverted index (SQLite):
```
./implementation-indexing/run-sqlite-search.py SEARCH_PARAM
```