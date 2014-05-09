#! /usr/bin/env python

import ddext

# >> doc_id, words, pos, ner, lemma, character_offset_begin, character_offset_end
# << doc_id text, mention_id text, sentence_id text, word text, type text
def init():

	ddext.input('doc_id', 'text')
	ddext.input('sentence_id', 'text')
	ddext.input('words', 'text[]')
	ddext.input('pos', 'text[]')
	ddext.input('ner', 'text[]')
	ddext.input('lemma', 'text[]')
	ddext.input('character_offset_begin', 'integer[]')
	ddext.input('character_offset_end', 'integer[]')

	ddext.returns('doc_id', 'text')
	ddext.returns('mention_id', 'text')
	ddext.returns('entity', 'text')

"""
CREATE OR REPLACE FUNCTION func_ext_mention(doc_id text, sentence_id text, words text[], pos text[], ner text[], lemma text[], character_offset_begin integer[], character_offset_end integer[]) RETURNS SETOF ret_func_ext_mention AS 
$$
	plpy.notice('HELLO!')
	
	history = {}
	for i in range(0, len(words)):
		if i in history: continue
		beginc = character_offset_begin[i]
		endc = character_offset_end[i]
		nerc = ner[i]

		if nerc != 'O':
			j = i
			for j in range(i, len(words)):
				if ner[j] != nerc:
					break
			mention_id = doc_id + "_%d_%d" % (character_offset_begin[i], character_offset_end[j-1])
			word = " ".join(words[i:j])
			yield {"doc_id":"doc_id", "mention_id":mention_id, "sentence_id":sentence_id, "word":word, "type":nerc}
$$ LANGUAGE plpythonu;
"""

def run(doc_id, sentence_id, words, pos, ner, lemma, character_offset_begin, character_offset_end):
	
	if 'EXT_MENTION_IGNORE_TYPE' not in SD:
		SD['EXT_MENTION_IGNORE_TYPE'] = {"URL": 1, "NUMBER" : 1, "MISC" : 1, "CAUSE_OF_DEATH":1, "CRIMINAL_CHARGE":1, 
		"DURATION":1, "MONEY":1, "ORDINAL" :1, "RELIGION":1, "SET": 1, "TIME":1}

	history = {}
	mentions = []
	for i in range(0, len(words)):
		if i in history: continue
		beginc = character_offset_begin[i]
		endc = character_offset_end[i]
		nerc = ner[i]
		if nerc in SD['EXT_MENTION_IGNORE_TYPE']:
			continue

		if nerc != 'O':
			j = i
			for j in range(i, len(words)):
				if ner[j] != nerc:
					break
			mention_id = doc_id + "_%d_%d" % (character_offset_begin[i], character_offset_end[j-1])
			if i==j:
				word = words[i]
				history[i] = 1
			else:
				word = " ".join(words[i:j])
				for w in range(i,j):
					history[w] = 1
			mentions.append({"doc_id":"doc_id", "mention_id":mention_id, "sentence_id":sentence_id, "word":word, "type":nerc})

	for m1 in mentions:
		for m2 in mentions:
			if m1["mention_id"] == m2["mention_id"]:
				continue
			yield {"doc_id":doc_id, "mid1": m1["mention_id"], "mid2": m2["mention_id"], "word1": m1["word"], "word2": m2["word"]}







