#! /lfs/local/0/czhang/software/pypy-2.3.1-linux_x86_64-portable/bin/pypy

import json
import re
import sys
from lib import dd as ddlib

keywords = {'ambassador': 1, 'founder': 1, 'executive': 1, 'moderator': 1, 'manager': 1, 'scientist': 1, 'defender': 1, 'chair': 1, 'captain': 1, 'economist': 1, 'mayor': 1, 'operative': 1, 'principal': 1, 'monitor': 1, 'justice': 1, 'mediator': 1, 'adviser': 1, 'ceo': 1, 'assistant': 1, 'psychologist': 1, 'investor': 1, 'scholar': 1, 'investigator': 1, 'spokesperson': 1, 'knight': 1, 'artist': 1, 'officer': 1, 'found': 1, 'secretary': 1, 'attorney': 1, 'dean': 1, 'creator': 1, 'owner': 1, 'negotiator': 1, 'lawyer': 1, 'biologist': 1, 'salesman': 1, 'expert': 1, 'reporter': 1, 'prince': 1, 'spokesman': 1, 'pioneer': 1, 'staff': 1, 'commentator': 1, 'leader': 1, 'stringer': 1, 'journalist': 1, 'specialist': 1, 'associate': 1, 'lawmaker': 1, 'physicist': 1, 'boss': 1, 'host': 1, 'leadership': 1, 'advisor': 1, 'publisher': 1, 'superstar': 1, 'trader': 1, 'economics': 1, 'columnist': 1, 'banker': 1, 'senator': 1, 'maker': 1, 'major': 1, 'own': 1, 'deputy': 1, 'researcher': 1, 'entrepreneur': 1, 'operator': 1, 'midfielder': 1, 'representative': 1, 'editor': 1, 'prosecutor': 1, 'commissioner': 1, 'fellow': 1, 'striker': 1, 'fund': 1, 'chairwoman': 1, 'general': 1, 'holder': 1, 'analyst': 1, 'pilot': 1, 'king': 1, 'presidency': 1, 'consultant': 1, 'official': 1, 'governor': 1, 'spokeswoman': 1, 'architect': 1, 'control': 1, 'producer': 1, 'premier': 1, 'head': 1, 'commander': 1, 'coordinator': 1, 'dealer': 1, 'diplomat': 1, 'playmaker': 1, 'speaker': 1, 'chairman': 1, 'chancellor': 1, 'mayer': 1, 'administrator': 1, 'designer': 1, 'star': 1, 'director': 1, 'shareholder': 1, 'faculty': 1, 'president': 1, 'lead': 1, 'vice': 1, 'chief': 1, 'peacekeeper': 1, 'businessman': 1, 'senior': 1, 'fundraiser': 1, 'minister': 1}

def dep_format_parser(dep_edge_str):
	"""
	Given a string representing a dependency edge, return a tuple of
	   (parent_index, edge_label, child_index).
	Args: dep_edge_str - a string representation of an edge in the dependency tree
						 (e.g. "31\tprep_of\t33")
	Returns: tuple of (integer, string, integer) (e.g. (30, "prep_of", 32))
	"""
	parent, label, child = dep_edge_str.split('\t')
	return (int(parent) - 1, label, int(child) - 1) # input edge used 1-based indexing	   


def dep(features, word_obj_list, end1, end2, f):
	edges = ddlib.dep_path_between_words(word_obj_list, end1 - 1, end2 - 1)

	if len(edges) > 0:
		num_roots = 0 # the number of root nodes
		num_left = 0 # the number of edges to the left of the root
		num_right = 0 # the number of edges to the right of the root
		left_path = "" # the dependency path to the left of the root
		right_path = "" # the dependency path to the right of the root

		# find the index of the switch from up to down
		switch_direction_index = -1
		for i in range(len(edges)):
			if not edges[i].is_bottom_up:
				switch_direction_index = i
				break
		
		# iterate through the edge list
		for i in range(len(edges)):
			curr_edge = edges[i]

			# count the number of roots; if there are more than 1 root then our dependency
			# path is disconnected
			if curr_edge.label == 'ROOT':
				num_roots += 1

			# going from the left to the root
			if curr_edge.is_bottom_up:
				num_left += 1

				# if this is the edge pointing to the root (word2 is the root)
				if i == switch_direction_index - 1:
					left_path = left_path + ("--" + curr_edge.label + "->")
					root = f(curr_edge.word2).lower()

				# this edge does not point to the root
				else:
					# if we are at the last edge, don't include the word (part of the mention)
					if i == len(edges) - 1:
						left_path = left_path + ("--" + curr_edge.label + "->")
					else:
						left_path = left_path + ("--" + curr_edge.label + "->" + f(curr_edge.word2).lower())
			
			# going from the root to the right
			else:
				num_right += 1

				# the first edge to the right of the root
				if i == switch_direction_index:
					right_path = right_path + "<-" + curr_edge.label + "--"

				# this edge does not point from the root
				else:
					# if we are at the first edge, don't include the word (part of the mention)
					if i == 0:
						right_path = right_path + ("<-" + curr_edge.label + "--")
					else:
						# word1 is the parent for right to left
						right_path = right_path + (f(curr_edge.word1).lower() + "<-" + curr_edge.label + "--")
		
		# if the root is at the end or at the beginning (direction was all up or all down)
		if num_right == 0:
			root = "|SAMEPATH"
		elif num_left == 0:
			root = "SAMEPATH|"

		# if the edges have a disconnect
		elif num_roots > 1:
			root = "|NONEROOT|"

		# this is a normal tree with a connected root in the middle
		else:
			root = "|" + root + "|"

		path = left_path + root + right_path
		features.append(path)


def norm(s):
	return s.replace(' ', '').replace('_', '').replace('/', '').replace('\\', '')

__mentions = {}
for l in open(sys.argv[1]):
	(doc, mid, sent, phrase, t, start, end) = l.rstrip('\n').split('\t')
	if doc not in __mentions:
		__mentions[doc] = {}
	if sent not in __mentions[doc]:
		__mentions[doc][sent] = []
	__mentions[doc][sent].append([int(start), int(end), mid, phrase, t])

for l in open(sys.argv[2]):

	sent = json.loads(l)
	words = sent["words"]
	pos = sent["pos"]
	ner  = sent["ner"]
	lemma = sent["lemma"]
	docid = sent["doc_id"]
	sentid= sent["sentence_id"]
	dep_graph = sent["dep_graph"]
	doc_id=docid
	sentence_id=sentid

	word_obj_list = ddlib.unpack_words(sent, lemma='lemma', words='words', dep_graph='dep_graph', pos='pos', \
		dep_graph_parser=dep_format_parser)


	sameverb = {}
	i = 0
	npars = {}
	for w in word_obj_list:

		npars[w.dep_par] = 1

		sig = ("%d"%w.dep_par) + "|" + w.dep_label
		if sig not in sameverb:
			sameverb[sig] = []
		sameverb[sig].append(i)

		if w.dep_label == 'conj_and':
			sameverb["CONJ_%d" %i] = [i, w.dep_par]

		## appos is transitive	  
		if w.dep_label == 'appos':
			sameverb["APPOS_%d" %i] = [i, w.dep_par]

		i = i + 1

	if docid in __mentions:
		if sentid in __mentions[docid]:
			sentmentions = __mentions[docid][sentid]

			if len(sentmentions) > 20:
				continue

			"""
			for (start1, end1, mid1, phrase1, type1) in sentmentions:
				for (start2, end2, mid2, phrase2, type2) in sentmentions:
					if mid1 == mid2: continue

					span1 = ddlib.Span(begin_word_id=start1, length=end1 - start1 + 1)
					span2 = ddlib.Span(begin_word_id=start2, length=end2 - start2 + 1)

					# the lemma sequence between the mention spans
					lemma_between = ddlib.tokens_between_spans(lemma, span1, span2)
					if lemma_between.is_inversed:
						feature = "WORDSEQ_INV:" + "_".join(lemma_between.elements).lower()
					else:
						feature = "WORDSEQ_" + "_".join(lemma_between.elements).lower()
					
					try:
						print u"\t".join([docid, mid1, phrase1, type1, mid2, phrase2, type2, feature])
					except:
						continue
			"""

			for (_start1, _end1, _mid1, _phrase1, _type1) in sentmentions:

				if _type1 not in ['PERSON', 'ORGANIZATION', 'MISC']:
					continue

				_start1 = _start1
				_end1 = _end1 + 1	
				for (_start2, _end2, _mid2, _phrase2, _type2) in sentmentions:
					if _mid1 == _mid2: continue
					_start2 = _start2
					_end2 = _end2 + 1

					mentions2 = [{"doc_id" : docid, "mention_id" : _mid2, "sentence_id" : sentid, \
				   		"word" : _phrase2, "type" : _type2, "start" : _start2, "end" : _end2-1}]
					mentions1 = [{"doc_id" : docid, "mention_id" : _mid1, "sentence_id" : sentid, \
				   		"word" : _phrase1, "type" : _type1, "start" : _start1, "end" : _end1-1}]


					mm2 = []
					for m2 in mentions2: mm2.append(m2)
					for m2 in mm2:
						end2 = m2["end"] - 1
						for sig in sameverb:
							if end2 in sameverb[sig] and ('nsubj' in sig or 'CONJ_' in sig or 'APPOS' in sig):
								for end3 in sameverb[sig]:
									if end2 == end3: continue
									mention_id = "SAMEVERB"
									mentions2.append({"doc_id":doc_id, "mention_id":mention_id, 
											"sentence_id":sentence_id, "word":"", "type":'SAMEVERB', "start":end3, "end":end3+1})


					mm1 = []
					for m2 in mentions1: mm1.append(m2)
					for m2 in mm1:
						end2 = m2["end"] - 1
						for sig in sameverb:
							if end2 in sameverb[sig] and ('nsubj' in sig or 'CONJ_' in sig or 'APPOS' in sig):
								#import pdb
								#pdb.set_trace()
								for end3 in sameverb[sig]:
									if end2 == end3: continue
									mention_id = "SAMEVERB"
									mentions1.append({"doc_id":doc_id, "mention_id":mention_id, 
											"sentence_id":sentence_id, "word":"", "type":'SAMEVERB', "start":end3, "end":end3+1})

					final_features = []
					for m1 in mentions1:
						start1 = m1["start"]
						end1 = m1["end"]

						for m2 in mentions2:
							if m1["mention_id"] == m2["mention_id"]:
								continue

							features = []

							start2 = m2["start"]
							end2 = m2["end"]

							# the spans of the mentions
							span1 = ddlib.Span(begin_word_id=start1, length=end1 - start1 + 1)
							span2 = ddlib.Span(begin_word_id=start2, length=end2 - start2 + 1)

							# the lemma sequence between the mention spans
							lemma_between = ddlib.tokens_between_spans(lemma, span1, span2)
							if lemma_between.is_inversed:
								feature = "WORDSEQ_INV:" + "_".join(lemma_between.elements).lower()
							else:
								feature = "WORDSEQ_" + "_".join(lemma_between.elements).lower()
							features.append(feature)


						def nor(w):
							if w.pos.startswith('VB'): return 'POS:VB'
							if w.pos.startswith('N'): return "POS:NN"
							return w.lemma

						if len(npars) > 2:
							#print len(npars)
							for nend1 in range(start1+1,min(len(words)+1, end1+2)):
								for nend2 in range(start2+1,min(len(words)+1, end2+2)):
									dep(features, word_obj_list, nend1, nend2, lambda x : x.lemma)
									dep(features, word_obj_list, nend1, nend2, lambda x : 'POS:VB' if x.pos.startswith('VB') else x.lemma)
									dep(features, word_obj_list, nend1, nend2, lambda x : 'POS:NN' if x.pos.startswith('N') else x.lemma)
									dep(features, word_obj_list, nend1, nend2, nor)

							# TODO
							#dep(features, word_obj_list, end1+1, end2+1, lambda x : '(WORDNET_CHOOSEN)' if x.lemma in ['elect'] else x.lemma)

						ffff = {}
						for f in features: 
							if 'WORDSEQ' not in f:
								ffff[f] = 1

						
						i = -1
						for word in word_obj_list:

							i = i + 1

							if word.lemma.lower() not in keywords:
								continue

							if not word.pos.startswith('N'):
								continue

							word_mention1s = []
							word_mention2s		  = []

							if end1 < len(words):
								dep(word_mention1s, word_obj_list, end1+1, i+1, lambda x : x.lemma)
							if end2 < len(words):
								dep(word_mention2s, word_obj_list, end2+1, i+1, lambda x : x.lemma)

							for sig in sameverb:
								if not 'nsubj' in sig: continue
								if end1 in sameverb[sig] and i in sameverb[sig]:
									word_mention1s.append('SAMEVERB')
								if end2 in sameverb[sig] and i in sameverb[sig]:
									word_mention2s.append('SAMEVERB')

							# AAA's chairman BBB

							for f in ffff:
								for left in word_mention1s:
									features.append('NEIGHBORPATH-' + word.lemma.lower() + '-[' + left + "][" + f + "]")
								for right in word_mention2s:
									features.append('NEIGHBORPATH-' + word.lemma.lower() + '[' + f + "][" + right + "]")

							for left in word_mention1s:
								for right in word_mention2s:
									features.append('NEWNEIGHBORPATH-' + word.lemma.lower() + '[' + left + "][" + right + "]")

						for f in features:
							final_features.append(f)

					distinct_fs = {}
					for feature in final_features:
						if len(feature) < 100:
							distinct_fs[feature] = 1
					#for feature in distinct_fs:
					#print json.dumps({"doc_id":doc_id, "mid1": _m1["mention_id"], "mid2": _m2["mention_id"], "word1": _m1["word"], "word2": _m2["word"], "features":distinct_fs.keys(), "type1":_m1["type"], "type2":_m2["type"]})

					#f = json.dumps(distinct_fs.keys())
					#f = re.sub(r'^\[', '{', f)
					#f = re.sub(r'\]$', '}', f)

					distinct_fs["BIAS"] = 1

					#for f in distinct_fs:
					try:
						print u"\t".join([docid, _mid1, _phrase1, _type1, _mid2, _phrase2, _type2, "|~@          @~|".join(distinct_fs.keys())])
					except:
						continue



					#print final_features

