#! /usr/bin/env python

import ddext

def dep_format_parser(dep_edge_str):
	# Given a string representing a dependency edge, return a tuple of
	#    (parent_index, edge_label, child_index).

	# Args: dep_edge_str - a string representation of an edge in the dependency tree
	#                      (e.g. "31\tprep_of\t33")

 #    Returns: tuple of (integer, string, integer) (e.g. (30, "prep_of", 32))
	
	parent, label, child = dep_edge_str.split('\t')

	# input edge used 1-based indexing
	return (int(parent) - 1, label, int(child) - 1)


def init():
	ddext.import_lib('sys')

	ddext.input('doc_id', 'text')
	ddext.input('sentence_id', 'text')
	ddext.input('lemma', 'text[]')
	ddext.input('dep_graph', 'text[]')
	ddext.input('words', 'text[]')
	ddext.input('pos', 'text[]')
	ddext.input('ner', 'text[]')
	ddext.input('character_offset_begin', 'integer[]')
	ddext.input('character_offset_end', 'integer[]')
	ddext.input('mention_ids', 'text[]')
	ddext.input('mention_words', 'text[]')
	ddext.input('types', 'text[]')
	ddext.input('starts', 'integer[]')
	ddext.input('ends', 'integer[]')

	ddext.returns('doc_id', 'text')
	ddext.returns('mid1', 'text')
	ddext.returns('mid2', 'text')
	ddext.returns('word1', 'text')
	ddext.returns('word2', 'text')
	ddext.returns('type1', 'text')
	ddext.returns('type2', 'text')
	ddext.returns('features', 'text[]')


def run(doc_id, sentence_id, lemma, dep_graph, words, pos, ner, character_offset_begin, \
	    character_offset_end, mention_ids, mention_words, types, starts, ends):
	
	# Extractor for relation mention features.

	# Outputs 3 features for each relation mention:
	#     - the word sequence between the mentions
	#     - the dependency path for the sentence fragment containing the relation mention
	#     - the presence of the words "wife", "widow", or "husband" along the dependency path
	#       (this should help with the spouse relation)

	# (refer to http://www.stanford.edu/~jurafsky/mintz.pdf)
	

	if 'ddlib' in SD:
		ddlib = SD['ddlib']
	else: 
		# change this as needed to the local path to DeepDive's ddlib directory
		# (MUST be accessible from the database server)
		sys.path.append("/dfs/rulk/0/msushkov/shared/ddlib")
		from lib import dd as ddlib
		SD['ddlib'] = ddlib

	# create a list of mentions
	mentions = zip(mention_ids, mention_words, types, starts, ends)
	mentions = map(lambda x: {"mention_id" : x[0], "word" : x[1], "type" : x[2], "start" : x[3], "end" : x[4]}, mentions)

	# don't output features for sentences that are too long
	if len(mentions) > 20 or len(lemma) > 100:
		return

	# list of Word objects
	words = ddlib.unpack_words(obj, lemma='lemma', words='words', dep_graph='dep_graph', \
		dep_graph_parser=dep_format_parser)

	# at this point we have a list of the mentions in this sentence

	# go through all pairs of mentions
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
			# word sequence feature
			#

			# the spans of the mentions
			span1 = ddlib.Span(begin_word_id=start1, length=end1 - start1)
			span2 = ddlib.Span(begin_word_id=start2, length=end2 - start2)

			# the lemma sequence between the mention spans
			lemma_between = ddlib.tokens_between_spans(lemma, span1, span2)
			if lemma_between.is_inversed:
				feature = "WORDSEQ_INV:" + "_".join(lemma_between.elements).lower()
			else:
			    feature = "WORDSEQ_" + "_".join(lemma_between.elements).lower()

			features.append(feature)


			#
			# dependency path feature
			#

			# list of DepEdge objects representing the dependency path
			edges = ddlib.dep_path_between_words(words, end1 - 1, end2 - 1)

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
							root = curr_edge.word2.lemma.lower()

						# this edge does not point to the root
						else:
							# if we are at the last edge, don't include the word (part of the mention)
							if i == len(edges) - 1:
								left_path = left_path + ("--" + curr_edge.label + "->")
							else:
								left_path = left_path + ("--" + curr_edge.label + "->" + curr_edge.word2.lemma.lower())
					
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
								right_path = right_path + (curr_edge.word1.lemma.lower() + "<-" + curr_edge.label + "--")
				
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

				if 'wife' in path or 'widow' in path or 'husband' in path:
					features.append('LEN_%d_wife/widow/husband' % (num_left + num_right))

			yield {"doc_id":doc_id, "mid1": m1["mention_id"], "mid2": m2["mention_id"], "word1": m1["word"], "word2": m2["word"], "features":features, "type1":m1["type"], "type2":m2["type"]}

