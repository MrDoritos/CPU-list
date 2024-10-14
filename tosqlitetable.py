#!/bin/python3

import sqlite3
import json
import os
import locale
import datetime

database_name = 'cpus.db'
table_name = 'cpubenchmark.net'
cpu_table = 'cpulist'
json_name = 'cpubenchmark.net.json'

db = sqlite3.connect(database_name)
cur = db.cursor()

js = json.load(open(json_name))

cur.execute(f'CREATE TABLE IF NOT EXISTS {cpu_table}(name, samples, pop, msrp_usd, price_usd, date, arch, node_nm, node_process, mem_max_gb, mem_base_gbps, bus_gbps, gflops_single, gflops_multi, icp, kb_cache_l1, kb_cache_l2, kb_cache_l3, watts_acp, watts_tdp, socket, platform, cores, threads, clock_base_ghz, clock_turbo_ghz, misc, json)')

class cpu_info:
    name = None
    samples = None
    pop = None
    msrp_usd = None
    price_usd = None
    date = None
    arch = None
    node_nm = None
    node_process = None
    mem_max_gb = None
    mem_base_gbps = None
    bus_gbps = None
    gflops_single = None
    gflops_multi = None
    icp = None
    kb_cache_l1 = None
    kb_cache_l2 = None
    kb_cache_l3 = None
    watts_acp = None
    watts_tdp = None
    socket = None
    platform = None
    cores = None
    threads = None
    clock_base_ghz = None
    clock_turbo_ghz = None
    misc = None
    json = None

    def insert(self):
        cur.execute(f'INSERT OR REPLACE INTO {cpu_table}(name, samples, pop, msrp_usd, price_usd, date, arch, node_nm, node_process, mem_max_gb, mem_base_gbps, bus_gbps, gflops_single, gflops_multi, icp, kb_cache_l1, kb_cache_l2, kb_cache_l3, watts_acp, watts_tdp, socket, platform, cores, threads, clock_base_ghz, clock_turbo_ghz, misc, json) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', (self.name, self.samples, self.pop, self.msrp_usd, self.price_usd, self.date, self.arch, self.node_nm, self.node_process, self.mem_max_gb, self.mem_base_gbps, self.bus_gbps, self.gflops_single, self.gflops_multi, self.icp, self.kb_cache_l1, self.kb_cache_l2, self.kb_cache_l3, self.watts_acp, self.watts_tdp, self.socket, self.platform, self.cores, self.threads, self.clock_base_ghz, self.clock_turbo_ghz, self.misc, self.json))

def date_transform(date):
    if date is None:
        return None
    return datetime.datetime.strptime(date, '%b %Y').timestamp()

def parseint(_str):
    #print(_str, type(_str))
    if isinstance(_str, int):
        return _str
    if isinstance(_str, str):
        return locale.atoi(_str.replace(',', ''))
    return None

def parsefloat(_str):
    if isinstance(_str, float):
        return _str
    if isinstance(_str, str) and len(_str) > 0:
        return locale.atof(_str.replace(',', ''))
    return None

def parseusd(_str):
    if _str is None:
        return None
    return _str.replace('$', '').replace(',', '').replace('*', '')

def add_data_cpubenchmark(cpu_json):
    cpu = cpu_info()

    for key in cpu_json:
        if cpu_json[key] == 'NA' or cpu_json[key] == 'Unknown' or cpu_json[key] == '':
            cpu_json[key] = None

    print(cpu_json)

    cpu.name = cpu_json['name']
    cpu.samples = parseint(cpu_json['samples'])
    cpu.pop = parseint(cpu_json['rank'])
    cpu.msrp_usd = parseusd(cpu_json['price'])
    cpu.date = date_transform(cpu_json['date'])
    cpu.gflops_single = parsefloat(cpu_json['thread'])
    if cpu.gflops_single is not None:
        cpu.gflops_single *= 0.001
    cpu.watts_tdp = parsefloat(cpu_json['tdp'])
    cpu.socket = cpu_json['socket']
    cpu.platform = cpu_json['cat']
    core1 = parseint(cpu_json['cores'])
    core2 = parseint(cpu_json['secondaryCores'])
    thread1 = parseint(cpu_json['logicals'])
    thread2 = parseint(cpu_json['secondaryLogicals'])
    sec1 = 0
    sec2 = 0
    print (core1, core2, thread1, thread2)
    if core2 is not None and thread2 is not None:
        sec1 = core2
        sec2 = core2 * thread2
    cpu.cores = core1 + sec1
    cpu.threads = core1 * thread1 + sec2
    cpu.clock_base_ghz = parsefloat(cpu_json['speed'])
    cpu.clock_turbo_ghz = parsefloat(cpu_json['turbo'])

    if cpu.clock_base_ghz is not None:
        cpu.clock_base_ghz *= 0.001
    if cpu.clock_turbo_ghz is not None:
        cpu.clock_turbo_ghz *= 0.001

    cpu.json = json.dumps(cpu_json)

    cpu.insert()

for cpu in js['data']:
    add_data_cpubenchmark(cpu)

db.commit()