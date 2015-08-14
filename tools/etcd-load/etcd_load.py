#!/usr/bin/python
import argparse
import etcd
import logging
import multiprocessing
import random
import string
import sys
import time

parser = argparse.ArgumentParser()
parser.add_argument('-e', '--etcdhost', action="store", dest="etcdhost")
parser.add_argument('-p', '--etcdport', action="store", dest="etcdport", type=int)
parser.add_argument('-op', '--operation', action="store", dest="operation")
parser.add_argument('-k', '--keycount', action="store", dest="keycount", type=int)
parser.add_argument('-u', '--get_update_delete_keycount', action="store", dest="get_update_delete_keycount", type=int)
parser.add_argument('-l', '--logfile', action="store", dest="logfile")

results = parser.parse_args()

etcdhost = results.etcdhost
etcdport = results.etcdport
operation = results.operation
#print operation

#Get total keycount
keycount = results.keycount

get_update_delete_keycount = results.get_update_delete_keycount

log_file = results.logfile

#start logging
logging.basicConfig(filename=log_file, level=logging.INFO)

#Pre-defined keysize distribution in percentage
pct = [5, 74, 10, 10, 1]

#Key size range
key_range = [0, 256, 512, 1024, 8192, 204800]

#Key count depending on the pct
pct_count = [x * keycount/100 for x in pct]
#print pct_count

#get etcd client
client = etcd.Client(host=etcdhost, port=etcdport)

#no. of threads = len in key distribution
threads = len(pct)


def get_values(base, per_thread):
    limit = base + (keycount / threads) - 1
    keys = random.sample(xrange(base, limit), per_thread)
    for key in keys:
        stime = time.time()
        try:
            client.read(str(key)).value
        except:
            logging.info("failure get key %s ", key)
            continue
        etime = time.time()
        logging.info("success get key %s time %s", key, (etime - stime))


def update_values(base, per_thread):
    limit = base + (keycount / threads) - 1
    keys = random.sample(xrange(base, limit), per_thread)
    for key in keys:
        val = "Updated value"
        stime = time.time()
        try:
            client.write(str(key), val)
        except:
            logging.info("failure update key %s ", key)
            continue
        etime = time.time()
        logging.info("success update key %s time %s", key, (etime - stime))


def delete_keys(base, per_thread):
    limit = base + (keycount / threads) - 1
    keys = random.sample(xrange(base, limit), per_thread)
    for key in keys:
        stime = time.time()
        try:
            client.delete(str(key))
        except:
            logging.info("failure delete key %s ", key)
            continue
        etime = time.time()
        logging.info("success delete key %s time %s", key, (etime - stime))


# Generate key of requested size
def create_keys(base, count, r):
    for j in range(count):
        key = base + j
        r1 = random.randint(min(r), max(r))
        value = (''.join(random.choice(string.ascii_lowercase) for _ in xrange(r1)))
        stime = time.time()
        try:
            client.write(str(key), value)
        except:
            logging.info("failure create key %s ", key)
            continue
        etime = time.time()
        logging.info("success create key %s time %s", key, (etime - stime))


def get_update_delete_jobs(func):
    per_thread = get_update_delete_keycount / threads
    jobs = []
    base = 0
    for i in range(threads):
        p = multiprocessing.Process(target=func, args=(base, per_thread, ))
        jobs.append(p)
        base = base + (keycount / threads)
        p.start()


if operation == "create":
    #Dictionary for min and max key size
    d = dict()
    for i in range(len(pct)):
        start = key_range[i]
        end = key_range[i + 1]
        d[i] = [start, end]
    #print d

    #Create one threads for each pct value
    jobs = []
    base = 0
    for i in range(len(pct_count)):
        p = multiprocessing.Process(target=create_keys,
                                    args=(base, pct_count[i], d[i]))
        base = base + pct_count[i]
        jobs.append(p)
        p.start()

elif operation == "get":
    get_update_delete_jobs(get_values)

elif operation == "update":
    get_update_delete_jobs(update_values)

elif operation == "delete":
    get_update_delete_jobs(delete_keys)

else:
    print ("no valid operation")
