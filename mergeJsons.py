import json
import numbers
import itertools
import sys
import glob

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
    '/home/feng356/CMSSW_12_0_0_pre5/src/sonic-workflows/results/json/sonic_4threads_1.json',
    '/home/feng356/CMSSW_12_0_0_pre5/src/sonic-workflows/results/json/sonic_4threads_2.json',
    '/home/feng356/CMSSW_12_0_0_pre5/src/sonic-workflows/results/json/sonic_4threads_3.json',
    '/home/feng356/CMSSW_12_0_0_pre5/src/sonic-workflows/results/json/sonic_4threads_4.json',
    '/home/feng356/CMSSW_12_0_0_pre5/src/sonic-workflows/results/json/sonic_4threads_5.json',
    '/home/feng356/CMSSW_12_0_0_pre5/src/sonic-workflows/results/json/sonic_4threads_6.json',
    '/home/feng356/CMSSW_12_0_0_pre5/src/sonic-workflows/results/json/sonic_4threads_7.json',
    '/home/feng356/CMSSW_12_0_0_pre5/src/sonic-workflows/results/json/sonic_4threads_8.json',
    '/home/feng356/CMSSW_12_0_0_pre5/src/sonic-workflows/results/json/sonic_4threads_9.json',
    '/home/feng356/CMSSW_12_0_0_pre5/src/sonic-workflows/results/json/sonic_4threads_10.json',
    '/home/feng356/CMSSW_12_0_0_pre5/src/sonic-workflows/results/json/sonic_4threads_11.json',
    '/home/feng356/CMSSW_12_0_0_pre5/src/sonic-workflows/results/json/sonic_4threads_12.json',
    '/home/feng356/CMSSW_12_0_0_pre5/src/sonic-workflows/results/json/sonic_4threads_13.json',
    '/home/feng356/CMSSW_12_0_0_pre5/src/sonic-workflows/results/json/sonic_4threads_14.json',
    '/home/feng356/CMSSW_12_0_0_pre5/src/sonic-workflows/results/json/sonic_4threads_15.json',
    '/home/feng356/CMSSW_12_0_0_pre5/src/sonic-workflows/results/json/sonic_4threads_16.json',
]

import argparse
parser = argparse.ArgumentParser(description="Options to merge json files from FastTimeService")
parser.add_argument('-i', "--input",  dest="input",  help="Input files to process", required=False, default=None)
parser.add_argument("-o", "--output", dest="output", help="Which processor to run", required=True)
args = parser.parse_args()

if args.input:
    print("use the input provided")
    print(args.input)
    filelist = glob.glob(args.input)
    print(filelist)

if len(filelist)==0:
    print("find zero matched file, return")
    sys.exit()

f1 = open(filelist[0], 'r')
print("fname ", f1)
data1 = json.load(f1)

for f in filelist[1:]:
    print("fname ", f)
    ftemp = open(f, 'r')
    datatemp = json.load(ftemp)
    merge(data1, datatemp)

with open(args.output, 'w') as fp:
    json.dump(data1, fp, indent=4)
