#! /usr/bin/env python

"""
Extractor for the word sequence relation mention feature.

Outputs 1 feature for each relation mention:
  - the word sequence between the 2 mentions


Input query:

SELECT s.doc_id AS doc_id,
               s.sentence_id AS sentence_id,
               max(s.lemma) AS lemma,
               max(s.words) AS words,
               array_accum(m.mention_id) AS mention_ids,
               array_accum(m.word) AS mention_words,
               array_accum(m.type) AS types,
               array_accum(m.start_pos) AS starts,
               array_accum(m.end_pos) AS ends
        FROM sentence s,
             mentions m
        WHERE s.doc_id = m.doc_id AND
              s.sentence_id = m.sentence_id
        GROUP BY s.doc_id,
                 s.sentence_id
"""

import sys
from lib import dd as ddlib
import csv

ARR_DELIM = '~^~'

for row in sys.stdin:
  # row is a string where the columns are separated by tabs
  (doc_id, sentence_id, lemma_str, words_str, mention_ids_str, \
    mention_words_str, types_str, starts_str, ends_str) = row.strip().split('\t')

  sys.stderr.write(row)

  # lemma = csv.reader(lemma_str, delimiter=',', quoting=csv.QUOTE_MINIMAL)

  # lemma = obj["lemma"]
  # words = obj["words"]
  # mention_ids = obj["mention_ids"]
  # mention_words = obj["mention_words"]
  # types = obj["types"]
  # starts = obj["starts"]
  # ends = obj["ends"]

  # # create a list of mentions
  # mentions = zip(mention_ids, mention_words, types, starts, ends)
  # mentions = map(lambda x: {"mention_id" : x[0], "word" : x[1], "type" : x[2], "start" : x[3], "end" : x[4]}, mentions)

  # # don't output features for sentences that are too long
  # if len(mentions) > 20 or len(lemma) > 100:
  #   continue

  # # at this point we have a list of the mentions in this sentence

  # # go through all pairs of mentions
  # for m1 in mentions:
  #   start1 = m1["start"]
  #   end1 = m1["end"]

  #   if m1["type"] not in ["PERSON", "ORGANIZATION"]:
  #     continue

  #   for m2 in mentions:
  #     if m1["mention_id"] == m2["mention_id"]:
  #       continue

  #     start2 = m2["start"]
  #     end2 = m2["end"]

  #     #
  #     # word sequence feature
  #     #

  #     # the spans of the mentions
  #     span1 = ddlib.Span(begin_word_id=start1, length=end1 - start1)
  #     span2 = ddlib.Span(begin_word_id=start2, length=end2 - start2)

  #     # the lemma sequence between the mention spans
  #     lemma_between = ddlib.tokens_between_spans(lemma, span1, span2)
  #     if lemma_between.is_inversed:
  #       feature = "WORDSEQ_INV:" + "_".join(lemma_between.elements).lower()
  #     else:
  #       feature = "WORDSEQ_" + "_".join(lemma_between.elements).lower()

  #     print json.dumps({"doc_id":doc_id, "mid1": m1["mention_id"], "mid2": m2["mention_id"], "word1": m1["word"], "word2": m2["word"], "feature":feature, "type1":m1["type"], "type2":m2["type"]})
