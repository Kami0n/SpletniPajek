

import concurrent.futures
import threading
import psycopg2

lock = threading.Lock()

def reset_db_values():
    conn = psycopg2.connect(host="localhost", user="user", password="friWIERvipavskaBurja")
    conn.autocommit = True
    
    cur = conn.cursor()
    cur.execute("UPDATE showcase.counters SET value = 0")
    
    cur.close()
    conn.close()
    
def print_db_values():
    conn = psycopg2.connect(host="localhost", user="user", password="friWIERvipavskaBurja")
    conn.autocommit = True

    print("\nValues in the database:")
    cur = conn.cursor()
    cur.execute("SELECT counter_id, value FROM showcase.counters ORDER BY counter_id")
    for counter_id, value in cur.fetchall():
        print(f"\tCounter id: {counter_id}, value: {value}")
    cur.close()
    conn.close()

def increase_db_values(counter_id, increases):
    conn = psycopg2.connect(host="localhost", user="user", password="friWIERvipavskaBurja")
    conn.autocommit = True
    
    for i in range(increases):
        cur = conn.cursor()
        cur.execute("SELECT value FROM showcase.counters WHERE counter_id = %s", \
                    (counter_id,))
        value = cur.fetchone()[0]
        cur.execute("UPDATE showcase.counters SET value = %s WHERE counter_id = %s", \
                    (value+1, counter_id))
        cur.close()
    conn.close()
    
def increase_db_values_locking(counter_id, increases):
    conn = psycopg2.connect(host="localhost", user="user", password="friWIERvipavskaBurja")
    conn.autocommit = True
    
    for i in range(increases):
        with lock:
            cur = conn.cursor()
            cur.execute("SELECT value FROM showcase.counters WHERE counter_id = %s", \
                        (counter_id,))
            value = cur.fetchone()[0]
            cur.execute("UPDATE showcase.counters SET value = %s WHERE counter_id = %s", \
                        (value+1, counter_id))
            cur.close()
    conn.close()

reset_db_values()
print_db_values()

with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
    print(f"\n ... executing workers ...\n")
    for _ in range(3):
        executor.submit(increase_db_values, 1,1000)
    for _ in range(3):
        executor.submit(increase_db_values_locking, 2,1000)
    
print_db_values()
