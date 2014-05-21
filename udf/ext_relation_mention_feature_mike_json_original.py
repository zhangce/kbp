#! /usr/bin/env python

import sys
sys.path.append("/lfs/local/0/msushkov/deepdive/ddlib")

import re
import sys, json
from lib import dd

SD = {}

def dep_format_parser(s):
	parent, label, child = s.split('\t')
	return (int(parent) - 1, label, int(child) - 1)

for row in sys.stdin:
	obj = json.loads(row)

	doc_id = obj['doc_id']
	sentence_id = obj['sentence_id']
	dep_graph = obj['dep_graph']
	lemma = obj['lemma']
	words = obj['words']

	sent_words = words

	mention_ids = obj['mention_ids']
	mention_words = obj['mention_words']
	types = obj['types']
	starts = obj['starts']
	ends = obj['ends']

	mentions = zip(mention_ids, mention_words, types, starts, ends)
	mentions = map(lambda x: {"mention_id" : x[0], "word" : x[1], "type" : x[2], "start" : x[3], "end" : x[4]}, mentions)


	deptree = {}
	r = {}
	try:
		for edge in dep_graph:
			edge = re.sub('\s+', ' ', edge)
			(parent, label, child) = edge.split(' ') 
			deptree[int(child)-1] = {"label":label, "parent":int(parent)-1}
			r[int(parent)-1] = 1
	except:
		WHY55555555 = True
	if len(r) == 1:
		deptree = {}

	#plpy.info("------------------------" + (len(r).__repr__()))
	#plpy.info("------------------------" + (r.__repr__()))
	#plpy.info("------------------------" + (deptree.__repr__()))


	if len(mentions) > 20:
		break

	if len(words) > 100:
		break

	prefix = ""
	start1 = ""
	start2 = ""
	end1 = ""
	end2 = ""
	actstart = ""
	actend = ""
	feature = ""
	for m1 in mentions:
		start1 = m1["start"]
		end1 = m1["end"]

		if m1["type"] not in ["PERSON", "ORGANIZATION"]:
			continue

		for m2 in mentions:
			if m1["mention_id"] == m2["mention_id"]:
				continue

			features = []
			start2 = m2["start"]
			end2 = m2["end"]

			prefix = ""
			if start1 > start2:
				prefix = "INV:"
			actend = max(start1, start2)
			actstart = min(end1, end2)
			feature = "WORDSEQ_" + prefix + "_".join(lemma[actstart:actend]).lower()

			#features.append(feature)

			if len(deptree) > 0:
				path1 = []
				end = end1 - 1
				ct = 0
				while True:
					ct = ct + 1
					if ct > 100:
						break
					if end not in deptree:
						path1.append({"current":end, "parent": -1, "label":"ROOT"})
						break
					path1.append({"current":end, "parent": deptree[end]["parent"], "label":deptree[end]["label"]})
					end = deptree[end]["parent"]

				path2 = []
				end = end2 - 1
				ct = 0
				while True:
					ct = ct + 1
					if ct > 100:
						break
					if end not in deptree:
						path2.append({"current":end, "parent": -1, "label":"ROOT"})
						break
					path2.append({"current":end, "parent": deptree[end]["parent"], "label":deptree[end]["label"]})
					end = deptree[end]["parent"]

				commonroot = None
				for i in range(0, len(path1)):
					j = len(path1) - 1 - i
					#plpy.notice(path1[j])  
					#plpy.notice(path2[-i-1])  
					if -i-1 <= -len(path2) or path1[j]["current"] != path2[-i-1]["current"]:
						break
					commonroot = path1[j]["current"]

				left_path = ""
				lct = 0
				for i in range(0, len(path1)):
					lct = lct + 1
					if path1[i]["current"] == commonroot:
						break
					if path1[i]["parent"] == commonroot or path1[i]["parent"]==-1:
						left_path = left_path + ("--" + path1[i]["label"] + "->" + '|')
					else:
						w = lemma[path1[i]["parent"]].lower()
						if i == 0: 
							w = ""
						left_path = left_path + ("--" + path1[i]["label"] + "->" + w)
				
				right_path = ""
				rct = 0
				for i in range(0, len(path2)):
					rct = rct + 1
					if path2[i]["current"] == commonroot:
						break
					if path2[i]["parent"] == commonroot or path2[i]["parent"]==-1:
						right_path = ('|' + "<-" + path2[i]["label"] + "--") + right_path
					else:
						w = lemma[path2[i]["parent"]].lower()
						if i == 0:
							w = ""
						right_path = (w + "<-" + path2[i]["label"] + "--" ) + right_path

				path = ""
				if commonroot == end1-1 or commonroot == end2-1:
					path = left_path + "SAMEPATH" + right_path
				else:
					if commonroot != None:
						path = left_path + lemma[commonroot].lower() + right_path
					else:
						path = left_path + "NONEROOT" + right_path
				if path != "":
					features.append(path)

				if 'wife' in path or 'widow' in path or 'husband' in path:
					features.append('LEN_%d_wife/widow/husband' % (lct + rct))

				print words
				print features
				print "============="
