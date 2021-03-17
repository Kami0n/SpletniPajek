# simple_task_queue.py

from multiprocessing import Process, Value, Lock
import multiprocessing
import time
from urllib.request import urlopen
import random

PROCESSES = multiprocessing.cpu_count() - 1

# funkcija ki daje URLje
def getNextUrl(lock):
    with lock:
        time.sleep(0.2)
        page = urlopen('http://83.212.82.40/counting/')
        return page.read()


# delovna funkcija -> ki predstavlja en proces
def process(nextUrl, lock):
    while nextUrl!=-1:
        nextUrl = int(getNextUrl(lock).decode("utf-8"))
        print(nextUrl)
        
    return True

# zagon programa
def run():
    PROCESSES = int(input("Enter number of processes: "))
    
    print(f"Running with {PROCESSES} processes!")
    start = time.time()
    
    lock = Lock()
    nextUrls = [0]
    
    procs = [Process(target=process, args=(nextUrls,lock)) for i in range(PROCESSES)] # ustvarjanje procesov
    
    for p in procs: p.start()
    for p in procs: p.join()
    
    print(f"Time taken = {time.time() - start:.10f}")

if __name__ == "__main__":
    run()