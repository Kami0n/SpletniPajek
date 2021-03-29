# Short description of the project and instructions to install, set up and run the crawler:

**!!IMPORTANT - as database file is too large for github commit, it can be accessed on this link:**
https://drive.google.com/drive/folders/1062HdYvG427uvF1cgZTS973DzcBEowlS?usp=sharing


This is a web crawler for for the first programing assignement for a subject "IEPS".
It uses selenium wire library to retrieve data and obides the etiquete for web crawlers.
It supports multiple processes and it runs BFS on a domain level.

This project uses dependency `url-py`, that only runs on `Python` version before `3.8`!

[url-py lib.](https://github.com/seomoz/url-py)

## Installation of dependencies

Install all dependecies from `requirements.txt`, with command:
```
pip install -r requirements.txt
```
Move to folder `pa1/crawler/url-py-master`
Install `url-py` dependecy:
```
pip install .
```

## Setting up local env

In folder `pa1/crawler/` there is a `.env.example` file.
This file is a example of `.env` file that specifies where is Chrome Web Driver installed, database host (IP) and database credentials.
Copy file `.env.example` and rename it to `.env`. Then change variables inside, for your local enviroment.

## Running crawler

If all dependencies are sucessfuly installed and you are using `Python` version before `3.8` (crawler was tested and running on `Python 3.7.9`), then you can run crawler, which is located in folder `pa1/crawler/`.
There are 2 crawlers implemented:
- `fri-wier-vipavska-burja.py` This crawler was used for building of database.
- `fri-wier-vipavska-burja_BFS.py` This crawler has correctly implemented breadth-first search.

Command to run crawler:
```
python3 fri-wier-vipavska-burja.py
```
or
```
python3 fri-wier-vipavska-burja_BFS.py
```

At startup crawler asks user to input a number of processes (workers).
