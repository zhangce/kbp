#! /lfs/local/0/czhang/software/pypy-2.3.1-linux_x86_64-portable/bin/pypy

import json
import re
import sys

def norm(s):
	return s.replace(' ', '').replace('_', '').replace('/', '').replace('\\', '')


queries = {}
names = {}
names2qid = {}
#for QUERY in ["2009.xml", "2010.xml", "2011.xml", "2012.xml"]:
#for QUERY in ["2013.xml"]:
for QUERY in ["tac_2014_kbp_english_regular_slot_filling_evaluation_queries.xml"]:
	QUERY = "/afs/cs.stanford.edu/u/czhang/" + QUERY
	for l in open(QUERY):
		m = re.search('<query id="(.*?)">', l)
		if m:
			qid = m.group(1)
		m = re.search('<name>(.*?)</name>', l)
		if m:
			name = m.group(1)
		m = re.search('<enttype>(.*?)</enttype>', l)
		if m:
			t = m.group(1)
			t = t.replace('PER', 'PERSON').replace('ORG','ORGANIZATION')
			queries[qid] = [name, t]
			if name.lower() not in names:
				names2qid[name.lower()] = []

			names[name.lower()] = t
			names2qid[name.lower()].append(qid)


mentions = {}
for l in open(sys.argv[1]):
	(doc, mid, sent, phrase, t, start, end) = l.rstrip('\n').split('\t')

	if doc not in mentions:
		mentions[doc] = {}
	if sent not in mentions[doc]:
		mentions[doc][sent] = {}
	#mentions[doc][sent][phrase] = (norm(phrase.lower()), t)
	mentions[doc][sent][phrase] = mid

for doc in mentions:
	for sent in mentions[doc]:
		for phrase1 in mentions[doc][sent]:

			if phrase1.lower() in names2qid:
				for a in names2qid[phrase1.lower()]:
					print "\t".join([doc, mentions[doc][sent][phrase1], phrase1, a, phrase1])

			for sent2 in mentions[doc]:
				for phrase2 in mentions[doc][sent2]:
					if phrase2.lower() not in names: continue
					if 'PER' not in names[phrase2.lower()]: continue
					if phrase1.lower() != phrase2.lower() and ( ((phrase1.lower() + ' ')  in phrase2.lower()) or (( ' ' + phrase1.lower())  in phrase2.lower()) ):
						for a in names2qid[phrase2.lower()]:
							if not (' ' not in phrase2 and ' ' in phrase1):
								print "\t".join([doc, mentions[doc][sent][phrase1], phrase1, a, phrase2.lower()])

			for phrase2 in names:
				if phrase2.lower() not in names: continue
				if 'ORG' not in names[phrase2.lower()]: continue
				if ' ' in phrase1 and len(phrase1) > 5 and phrase1.lower() != phrase2.lower() and ( ((phrase1.lower() + ' ')  in phrase2.lower()) or (( ' ' + phrase1.lower())  in phrase2.lower()) or ((phrase2.lower() + ' ')  in phrase1.lower()) or (( ' ' + phrase2.lower())  in phrase1.lower()) ):
					#print doc, phrase1, phrase2
					for a in names2qid[phrase2.lower()]:
						if not (' ' not in phrase2 and ' ' in phrase1):
							print "\t".join([doc, mentions[doc][sent][phrase1], phrase1, a, phrase2.lower()])











