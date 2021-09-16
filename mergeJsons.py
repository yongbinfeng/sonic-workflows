import json
import numbers
import itertools

def merge(a, b):
    "merges b into a"
    if isinstance(b, dict) and isinstance(a, dict):
        for key in b:
            if key in a:
                if isinstance(a[key], numbers.Number) and isinstance(b[key], numbers.Number):
                    a[key] += b[key]
                elif isinstance(a[key], basestring) and isinstance(b[key], basestring):
                    if a[key]!=b[key]:
                        raise Exception('Conflict at ' + key + " for a: " + a[key] + " for b: " + b[key]) 
                else:
                    merge(a[key], b[key])
            else:
                print("key {} not exist in a ".format(key))
                a[key] = b[key]

    elif isinstance(b, list) and isinstance(a, list):
        for bi,ai in itertools.izip_longest(b,a):
            merge(ai, bi)

    elif a==None:
        a = b

filelist = [
    '/home/feng356/CMSSW_12_0_0_pre5/src/sonic-workflows/results_8jobs/json/nosonic_4threads_1.json',
    '/home/feng356/CMSSW_12_0_0_pre5/src/sonic-workflows/results_8jobs/json/nosonic_4threads_2.json',
    '/home/feng356/CMSSW_12_0_0_pre5/src/sonic-workflows/results_8jobs/json/nosonic_4threads_4.json',
    '/home/feng356/CMSSW_12_0_0_pre5/src/sonic-workflows/results_8jobs/json/nosonic_4threads_5.json',
    '/home/feng356/CMSSW_12_0_0_pre5/src/sonic-workflows/results_8jobs/json/nosonic_4threads_7.json',
    '/home/feng356/CMSSW_12_0_0_pre5/src/sonic-workflows/results_8jobs/json/nosonic_4threads_8.json',
]

import argparse
parser = argparse.ArgumentParser(description="Options to merge json files from FastTimeService")
parser.add_argument("-o", "--output", dest="output", help="Which processor to run", required=True)
args = parser.parse_args()

f1 = open(filelist[0], 'r')
data1 = json.load(f1)

for f in filelist[1:]:
    print("fname ", f)
    ftemp = open(f, 'r')
    datatemp = json.load(ftemp)
    merge(data1, datatemp)

with open(args.output, 'w') as fp:
    json.dump(data1, fp, indent=4)
