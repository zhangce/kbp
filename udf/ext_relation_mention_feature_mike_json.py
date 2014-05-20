#! /usr/bin/env python

import re
import sys, json

SD = {}

for row in sys.stdin:
	print row

	# obj = json.loads(row)

	# TODO: zip and map

	# doc_id = obj['doc_id']
	# sentence_id = obj['sentence_id']
	# words = obj['words']
	# pos = obj['pos']
	# ner = obj['ner']
	# lemma = obj['lemma']
	# character_offset_begin = obj['character_offset_begin']
	# character_offset_end = obj['character_offset_end']
	# dep_graph = obj['dep_graph']
	# run(doc_id, sentence_id, words, pos, ner, lemma, character_offset_begin, character_offset_end, dep_graph)


def run(doc_id, sentence_id, words, pos, ner, lemma, character_offset_begin, character_offset_end, dep_graph):
	if 'EXT_MENTION_IGNORE_TYPE' not in SD:
		SD['EXT_MENTION_IGNORE_TYPE'] = {"URL": 1, "NUMBER" : 1, "MISC" : 1, "CAUSE_OF_DEATH":1, "CRIMINAL_CHARGE":1, 
		"DURATION":1, "MONEY":1, "ORDINAL" :1, "RELIGION":1, "SET": 1, "TIME":1}

	#if 'EXT_RELATION_MENTION_FEATURE_WORDSEQ' not in SD:
	#	SD['EXT_RELATION_MENTION_FEATURE_WORDSEQ'] = 

	history = {}
	mentions = []
	
	for i in range(0, len(words)):
		if i in history: continue
		beginc = character_offset_begin[i]
		endc = character_offset_end[i]
		nerc = ner[i]
		if nerc in SD['EXT_MENTION_IGNORE_TYPE']:
			continue

		if nerc in ["CITY", "COUNTRY", "STATE_OR_PROVINCE"]:
			nerc = "LOCATION"

		if nerc != 'O':
			j = i
			for j in range(i, len(words)):
				nerj = ner[j]
				if nerj in ["CITY", "COUNTRY", "STATE_OR_PROVINCE"]:
					nerj = "LOCATION"
				if nerj != nerc:
					break

			mention_id = doc_id + "_%d_%d" % (character_offset_begin[i], character_offset_end[j-1])
			if i==j:
				word = words[i]
				history[i] = 1
				j=i+1
			else:
				word = " ".join(words[i:j])
				for w in range(i,j):
					history[w] = 1
			mentions.append({"doc_id":doc_id, "mention_id":mention_id, "sentence_id":sentence_id, "word":word.lower(), "type":nerc, "start":i, "end":j})
		else:
			if words[i].lower() in {'winger':1, 'singer\\/songwriter':1, 'founder':1, 'president':1, 'executive director':1, 'producer':1, 'star':1, 'musician':1, 'nightlife impresario':1, 'lobbyist':1}:
				history[i] = 1
				word = words[i]
				mention_id = doc_id + "_%d_%d" % (character_offset_begin[i], character_offset_end[i])
				mentions.append({"doc_id":doc_id, "mention_id":mention_id, "sentence_id":sentence_id, "word":word.lower(), "type":'TITLE', "start":i, "end":i+1})

	# at this point we have a list of the mentions in this sentence

	if len(mentions) > 20:
		return

	if len(words) > 100:
		return

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

			features.append(feature)

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

			print json.dumps( {"doc_id":doc_id, "mid1": m1["mention_id"], "mid2": m2["mention_id"], "word1": m1["word"], "word2": m2["word"], "features":features, "type1":m1["type"], "type2":m2["type"]} )







