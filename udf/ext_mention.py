#! /usr/bin/env python

import ddext

"""
Extractor for entity mentions.

A mention can consist of multiple words (e.g. Barack Obama); the way we can identify these is 
if all of these words have the same NER tag.

This extractor goes through all the words in the sentence and outputs as a mention the consecutive
words that have the same NER tag that is not in EXT_MENTION_IGNORE_TYPE.
"""

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
    ddext.returns('sentence_id', 'text')
    ddext.returns('word', 'text')
    ddext.returns('type', 'text')
    ddext.returns('start', 'integer')
    ddext.returns('\"end\"', 'integer') # Greenplum issues for end without quotes


def run(doc_id, sentence_id, words, pos, ner, lemma, character_offset_begin, character_offset_end):
    # the NER tags that wil not correspond to entity mentions types
    if 'EXT_MENTION_IGNORE_TYPE' not in SD:
        SD['EXT_MENTION_IGNORE_TYPE'] = {'URL': 1, 'NUMBER' : 1, 'MISC' : 1, 'CAUSE_OF_DEATH' : 1,
            'CRIMINAL_CHARGE' : 1, 'DURATION' : 1, 'MONEY' : 1, 'ORDINAL' : 1, 'RELIGION' : 1,
            'SET' : 1, 'TIME' : 1}

    if 'EXT_MENTION_TITLE_TYPE' not in SD:
        SD['EXT_MENTION_TITLE_TYPE'] = {'winger' : 1, 'singer\\/songwriter' : 1, 'founder' : 1,
            'president' : 1, 'executive director' : 1, 'producer' : 1, 'star' : 1, 'musician' : 1,
                'nightlife impresario' : 1, 'lobbyist' : 1}

    # keep track of words whose NER tags we look at
    history = {}

    # go through each word in the sentence
    for i in range(0, len(words)):
        # if we already looked at this word's NER tag, skip it
        if i in history:
            continue

        # the NER tag for the current word
        nerc = ner[i]

        # skip this word if this NER tag should be ignored
        if nerc in SD['EXT_MENTION_IGNORE_TYPE']:
            continue

        # collapse specific location types
        if nerc in ["CITY", "COUNTRY", "STATE_OR_PROVINCE"]:
            nerc = "LOCATION"

        # if the current word has a valid NER tag
        if nerc != 'O':
            j = i

            # go through each of the words after the current word until the end of the sentence
            for j in range(i, len(words)):
                nerj = ner[j]

                # collapse specific location types
                if nerj in ["CITY", "COUNTRY", "STATE_OR_PROVINCE"]:
                    nerj = "LOCATION"

                # go until the NER tags of word 1 and word 2 do not match
                if nerj != nerc:
                    break

            # at this point we have a mention that consists of consecutive words with the same NER 
            # tag (or just a single word if the next word's NER tag is different)

            # construct a unique ID for this entity mention
            mention_id = doc_id + "_%d_%d" % (character_offset_begin[i], character_offset_end[j-1])

            # if our mention is just a single word, we want just that word
            if i == j:
                j = i + 1
                word = words[i]
                history[i] = 1
            # if our mention is multiple words, combine them and mark that we have already seen them
            else:
                word = " ".join(words[i:j])
                for w in range(i,j):
                    history[w] = 1

            yield {"doc_id" : doc_id, "mention_id" : mention_id, "sentence_id" : sentence_id, \
                   "word" : word.lower(), "type" : nerc, "start" : i, "end" : j}
        
        # if this word has an NER tag of '0'
        else:
            # if the current word is one of the known titles, then we have a TITLE mention
            if words[i].lower() in SD['EXT_MENTION_TITLE_TYPE']:
                history[i] = 1
                word = words[i]
                
                # construct a unique ID for this entity mention
                mention_id = doc_id + "_%d_%d" % (character_offset_begin[i], character_offset_end[i])
                
                yield {"doc_id" : doc_id, "mention_id" : mention_id, "sentence_id" : sentence_id, \
                       "word" : word.lower(), "type" : 'TITLE', "start" : i, "end" : i + 1}
