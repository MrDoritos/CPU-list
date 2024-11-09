#!/bin/python3

import sqlite3
import json
import os
import locale
import datetime
import requests
import bs4
import time

database_name = 'cpus.db'
table_name = 'cpubenchmark.net'
cpu_table = 'cpulist'
json_name = 'cpubenchmark.net.json'

db = sqlite3.connect(database_name)
cur = db.cursor()
cur2 = db.cursor()

js = json.load(open(json_name))

cur.execute(f'SELECT * FROM {cpu_table} ORDER BY gflops_single DESC')

list_count = 100

print(f'Top {list_count} CPUs:')

print("Capture more information")

def getMops(full):
    text = str(full.split(' ')[0]).replace(',', '')
    return float(text)
    
for i in range(0, list_count):
    try:
        cursql = cur.fetchone()
        curjs = json.loads(cursql[-1])

        print(f"{curjs['name']} ({curjs['id']})")
        print(cursql)
        r = requests.get(f'https://www.cpubenchmark.net/cpu.php?id={curjs["id"]}')
        soup = bs4.BeautifulSoup(r.text, 'html.parser')

        flops = list(soup.find('th', string='Floating Point Math').parent.children)
        single = list(soup.find('th', string='Single Thread').parent.children)

        gflops_multi = getMops(flops[-1].text)

        print(gflops_multi)
        print(getMops(single[-1].text))

        cur2.execute(f"UPDATE {cpu_table} SET gflops_multi={gflops_multi} WHERE name='{curjs['name']}'")
    except Exception as e:
        print('Exception:', e)

    time.sleep(1)

db.commit()