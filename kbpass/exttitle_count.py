#! /lfs/local/0/czhang/software/pypy-2.3.1-linux_x86_64-portable/bin/pypy


import json
import re
import sys


def already_title(ners):
    rs = {}
    for n in ners:
        rs[n] = 1
    if len(rs) == 1 and 'TITLE' in rs:
        return True
    return False

counts = {}

for l in open(sys.argv[1]):

    sent = json.loads(l)
    words = sent["words"]
    poses = sent["pos"]
    ners  = sent["ner"]
    lemmas = sent["lemma"]

    for i in range(0, len(words)-2):
        p = " ".join(lemmas[i:i+3]).lower() 
        if p not in counts:
            counts[p] = 0
        counts[p] = counts[p] + 1

    for i in range(0, len(words)-1):
        p = " ".join(lemmas[i:i+2]).lower() 
        if p not in counts:
            counts[p] = 0
        counts[p] = counts[p] + 1

    for i in range(0, len(words)):
        p = " ".join(lemmas[i:i+1]).lower() 
        if p not in counts:
            counts[p] = 0
        counts[p] = counts[p] + 1

for p in counts:
    print "\t".join([p, "%d" % counts[p]])