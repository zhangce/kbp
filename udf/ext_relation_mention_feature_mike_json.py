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

	mention_ids = obj['mention_ids']
	mention_words = obj['mention_words']
	types = obj['types']
	starts = obj['starts']
	ends = obj['ends']

	mentions = zip(mention_ids, mention_words, types, starts, ends)
	mentions = map(lambda x: {"mention_id" : x[0], "word" : x[1], "type" : x[2], "start" : x[3], "end" : x[4]}, mentions)


	if len(mentions) > 20:
		break

	if len(lemma) > 100:
		break



	# list of Word objects
	words = dd.unpack_words(obj, lemma='lemma', words='words', dep_graph='dep_graph', \
		dep_graph_parser=dep_format_parser)


	# at this point we have a list of the mentions in this sentence


	for m1 in mentions:
		start1 = m1["start"]
		end1 = m1["end"]

		if m1["type"] not in ["PERSON", "ORGANIZATION"]:
			continue

		for m2 in mentions:
			if m1["mention_id"] == m2["mention_id"]:
				continue

			start2 = m2["start"]
			end2 = m2["end"]

			features = []

			#
			# word sequence
			#

			# the spans of the mentions
			span1 = dd.Span(begin_word_id=start1, length=end1 - start1)
			span2 = dd.Span(begin_word_id=start2, length=end2 - start2)

			# the lemma sequence between the mention spans
			lemma_between = dd.tokens_between_spans(lemma, span1, span2)
			if lemma_between.is_inversed:
				feature = "WORDSEQ_INV:" + "_".join(lemma_between.elements).lower()
			else:
			    feature = "WORDSEQ_" + "_".join(lemma_between.elements).lower()

			features.append(feature)


			#
			# dependency path
			#

			# list of DepEdge objects representing the dependency path
			edges = dd.dep_path_between_words(words, end1 - 1, end2 - 1)

			if len(edges) > 0:
				# find the index of the edge which is pointing in a different direction than
				# the one before it
				switch_direction_index = -1

				for i in range(len(edges)):
					edge = edges[i]
					if not edge.is_bottom_up:
						switch_direction_index = i
						break

				# Word = collections.namedtuple('Word', ['begin_char_offset', 'end_char_offset', 'word', 'lemma', 'pos', 'ner', 'dep_par', 'dep_label'])

				left_path = ""
				right_path = ""
				num_left = 0
				num_right = 0

				# iterate through the edge list
				for i in range(len(edges)):
					# DepEdge = collections.namedtuple('DepEdge', ['word1', 'word2', 'label', 'is_bottom_up'])
					curr_edge = edges[i]

					# going from the left to the root
					if curr_edge.is_bottom_up:
						num_left = num_left + 1

						# if this is the edge pointing to the root (word2 is the root)
						if i == switch_direction_index - 1:
							left_path = left_path + ("--" + curr_edge.label + "->|")
							root = curr_edge.word2.lemma.lower()

						# this edge does not point to the root
						else:
							left_path = left_path + ("--" + curr_edge.label + "->" + curr_edge.word2.lemma.lower())
					
					# going from the root to the right
					else:
						num_right = num_right + 1

						# if this is the edge pointing from the root (word1 is the root)
						if i == switch_direction_index - 1:
							right_path = ("|<-" + curr_edge.label + "--") + right_path
							assert root == curr_edge.word1.lemma.lower()

						# this edge does not point from the root
						else:
							right_path = (curr_edge.word1.lemma.lower() + "<-" + curr_edge.label + "--") + right_path

				# if the edge arrows never switched direction, we don't have a root
				if switch_direction_index == -1:
					root = "NONEROOT"

				# if the root is at the end of at the beginning
				elif switch_direction_index == len(edges) - 1 or switch_direction_index == 0:
					root = "SAMEPATH"

				path = left_path + root + right_path
				features.append(path)

				if 'wife' in path or 'widow' in path or 'husband' in path:
					features.append('LEN_%d_wife/widow/husband' % (num_left + num_right))

			
			print json.dumps( {"doc_id":doc_id, "mid1": m1["mention_id"], "mid2": m2["mention_id"], "word1": m1["word"], "word2": m2["word"], "features":features, "type1":m1["type"], "type2":m2["type"]} )









