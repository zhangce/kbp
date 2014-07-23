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

for l in open(sys.argv[1]):

    sent = json.loads(l)
    words = sent["words"]
    poses = sent["pos"]
    ners  = sent["ner"]
    lemmas = sent["lemma"]

    if len(ners) >= 4:
        if ners[3] == 'PERSON':
            if ners[0] == 'O' or ners[0] == 'TITLE' or ners[0] == None:
                if ners[1] == 'O' or ners[1] == 'TITLE' or ners[1] == None:
                    if ners[2] == 'O' or ners[2] == 'TITLE' or ners[2] == None:
                        if (poses[0].startswith('NN') and poses[1].startswith('NN') and poses[2].startswith('NN')) or\
                            (poses[0].startswith('JJ') and poses[1].startswith('NN') and poses[2].startswith('NN')) or\
                            (poses[0].startswith('JJ') and poses[1].startswith('JJ') and poses[2].startswith('NN')) or\
                            (poses[0].startswith('NN') and poses[1].startswith('IN') and poses[2].startswith('NN')):
                            if not already_title(ners[0:3]): print " ".join(lemmas[0:3])

    if len(ners) >= 3:
        if ners[2] == 'PERSON':
            if ners[0] == 'O' or ners[0] == 'TITLE' or ners[0] == None:
                if ners[1] == 'O' or ners[1] == 'TITLE' or ners[1] == None:
                    if (poses[0].startswith('NN') and poses[1].startswith('NN') ) or\
                        (poses[0].startswith('JJ') and poses[1].startswith('NN') )  :               
                        if not already_title(ners[0:2]): print " ".join(lemmas[0:2])

    if len(ners) >= 2:
        if ners[1] == 'PERSON':
            if ners[0] == 'O' or ners[0] == 'TITLE' or ners[0] == None:
                if (poses[0].startswith('NN')):         
                    if not already_title(ners[0:1]): print " ".join(lemmas[0:1])

    for i in range(0, len(words)-2):
        if lemmas[i] == 'as' and lemmas[i+1] in ['a', 'an', 'the']:
            j = i + 2
            for j in range(j, len(words)):
                if ners[j] not in ['TITLE', 'O', None]:
                    break
                if not poses[j].startswith('NN') and (poses[j] not in ['JJ', 'IN', 'DT']):
                    break
                if lemmas[j] != 'of' and poses[j] in ['IN']:
                    break
            if poses[j-1].startswith('NN') and ('TITLE' in ners[i+2:j] or j == i+3):
                valid = True
                for w in range(i+2, j):
                    if 'year' in lemmas[w] or 'old' in lemmas[w]:
                        i = i + 1
                        continue
                    if lemmas[w] in ['a', 'an', 'the', 'as']:
                        i = i + 1
                        continue
                    if poses[w].startswith('NN'): continue
                    if poses[w] in ['JJ', 'IN']: continue
                    valid = False
                if valid == True:
                    if not already_title(ners[i+2:j]): print " ".join(lemmas[i+2:j])

    for i in range(0, len(words)-2):
        if ners[i] == 'PERSON' and lemmas[i+1] == ',':
            j = i + 2
            #import pdb
            #pdb.set_trace()
            for j in range(j, len(words)):
                if ners[j] not in ['TITLE', 'O', None, 'DURATION']:
                    break
                if not poses[j].startswith('NN') and poses[j] not in ['JJ', 'IN', 'DT']:
                    break
                if lemmas[j] != 'of' and poses[j] in ['IN']:
                    break

            #print " ".join(lemmas[i+2:j])
            if poses[j-1].startswith('NN') and ('TITLE' in ners[i+2:j] or j == i+3):
                valid = True
                for w in range(i+2, j):
                    if 'year' in lemmas[w] or 'old' in lemmas[w]:
                        i = i + 1
                        continue
                    if lemmas[w] in ['a', 'an', 'the', 'as']:
                        i = i + 1
                        continue
                    if poses[w].startswith('NN'): continue
                    if poses[w] in ['JJ', 'IN']: continue
                    valid = False
                if valid == True:
                    if not already_title(ners[i+2:j]): print " ".join(lemmas[i+2:j])

    for i in range(0, len(words)-2):
        if lemmas[i] == 'as' and lemmas[i+1] in ['a', 'an', 'the']:
            j = i + 2
            for j in range(j, len(words)):
                if ners[j] not in ['TITLE', 'O', None]:
                    break
                if not poses[j].startswith('NN') and (poses[j] not in ['JJ', 'DT']):
                    break
            if poses[j-1].startswith('NN') and ('TITLE' in ners[i+2:j] or j == i+3):
                valid = True
                for w in range(i+2, j):
                    if 'year' in lemmas[w] or 'old' in lemmas[w]:
                        i = i + 1
                        continue
                    if lemmas[w] in ['a', 'an', 'the', 'as']:
                        i = i + 1
                        continue
                    if poses[w].startswith('NN'): continue
                    if poses[w] in ['JJ', 'IN']: continue
                    valid = False
                if valid == True:
                    if not already_title(ners[i+2:j]): print " ".join(lemmas[i+2:j])

    for i in range(0, len(words)-2):
        if ners[i] == 'PERSON' and lemmas[i+1] == ',':
            j = i + 2
            #import pdb
            #pdb.set_trace()
            for j in range(j, len(words)):
                if ners[j] not in ['TITLE', 'O', None, 'DURATION']:
                    break
                if not poses[j].startswith('NN') and poses[j] not in ['JJ', 'DT']:
                    break
            #print " ".join(lemmas[i+2:j])
            if poses[j-1].startswith('NN') and ('TITLE' in ners[i+2:j] or j == i+3):
                valid = True
                for w in range(i+2, j):
                    if 'year' in lemmas[w] or 'old' in lemmas[w]:
                        i = i + 1
                        continue
                    if lemmas[w] in ['a', 'an', 'the', 'as']:
                        i = i + 1
                        continue
                    if poses[w].startswith('NN'): continue
                    if poses[w] in ['JJ', 'IN']: continue
                    valid = False
                if valid == True:
                    if not already_title(ners[i+2:j]): print " ".join(lemmas[i+2:j])











