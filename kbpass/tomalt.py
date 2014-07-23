#! /lfs/local/0/czhang/software/pypy-2.3.1-linux_x86_64-portable/bin/pypy

import sys
import json
import re

for row in sys.stdin:
    obj = json.loads(row)
    doc_id = obj["doc_id"]
    sentence_id = obj["sentence_id"]
    words = obj["words"]
    pos = obj["pos"]
    ner = obj["ner"]
    lemma = obj["lemma"]
    character_offset_begin = obj["character_offset_begin"]
    character_offset_end = obj["character_offset_end"]

    ct = 1
    for i in range(0, len(words)):
    	w = words[i].encode('ascii', 'ignore')
    	if w.strip()== '':
    		w = "_"
        w = re.sub(r'\s', '_', w)
    	if ct == 1:
	    	print "\t".join(["%d"%ct, w, "%s@%d-%d"%(sentence_id,character_offset_begin[i], character_offset_end[i]), pos[i], pos[i], '-']) 
    	else:
	    	print "\t".join(["%d"%ct, w, "-@%d-%d"%(character_offset_begin[i], character_offset_end[i]), pos[i], pos[i], '-']) 
    	ct = ct + 1
    print ""

# 