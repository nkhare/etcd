#!/usr/bin/python
import argparse
import pandas as pd
from prettytable import PrettyTable
import numpy as np
import os
import random
import re
import string
import sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser()
parser.add_argument('-l', '--logile', action="store", dest="logfile")
parser.add_argument('-op', '--operation', action="store", dest="operation")
parser.add_argument('-o', '--outputdir', action="store", dest="out_dir")
results = parser.parse_args()

logfile = results.logfile
op = results.operation
out_dir = results.out_dir

def randomword(length):
   return ''.join(random.choice(string.lowercase) for i in range(length))

success_file = "/tmp/" + randomword(10)
failure_file = "/tmp/" + randomword(10)
latency_file = "/tmp/" + randomword(10)

s = open(success_file, "w+")
f = open(failure_file, "w+")
l = open(latency_file, "w+")
l.write("latency")
l.write("\n")


logs = open(logfile, "r")
for line in logs:
    if re.search("success", line):
       s.write(line)
       l.write(line.split(" ")[5])
    if re.search("failure", line):
       f.write(line)

s.close()
f.close()
l.close()


# Generate success/failure result
with open(success_file) as f:
    s = len(f.readlines())

with open(failure_file) as f:
    f = len(f.readlines())

labels = 'success', 'failure'
sizes = [s, f]
colors = ['green', 'red']
title = "Success and Failure count for " + op + " operation"

plt.title(title)
plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%')
success_fail_pie = os.path.join(out_dir, "success_fail_pie.png")
plt.savefig(success_fail_pie, format="png")

# Generate latency graph
df = pd.read_csv(latency_file)
plt.clf()
df.latency.plot()
title = "Latency for " + op
plt.title(title)
plt.xlabel('count')
plt.ylabel('elapsed time (s)')
latency_graph = os.path.join(out_dir, "latency_graph.png")
plt.savefig(latency_graph, format="png")

# Generate stats table
table = PrettyTable(["operation", "count", "mean", "median", "max",  "90 percentile",
                    "95 percentile", "99 percentile"])
table.padding_width = 1
f = df["latency"]
table.add_row([op, len(f), f.mean(), f.median(), f.max(), np.percentile(f, 90),
               np.percentile(f, 95), np.percentile(f, 99)])

table_dump = os.path.join(out_dir, "stats.txt")

data = table.get_string()
with open(table_dump, "wb") as f:
    f.write(data)
