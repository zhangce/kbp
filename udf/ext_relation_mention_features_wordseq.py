#! /usr/bin/env python

"""
Extractor for relation mention features.

Outputs 1 feature for each relation mention:
    - the word sequence between the mentions
"""

import sys, json
from lib import dd as ddlib

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

for row in sys.stdin:
    obj = json.loads(row)
    doc_id = obj["doc_id"]
    sentence_id = obj["sentence_id"]
    lemma = obj["lemma"]
    dep_graph = obj["dep_graph"]
    words = obj["words"]
    pos = obj["pos"]
    ner = obj["ner"]
    character_offset_begin = obj["character_offset_begin"]
    character_offset_end = obj["character_offset_end"]
    mention_ids = obj["mention_ids"]
    mention_words = obj["mention_words"]
    types = obj["types"]
    starts = obj["starts"]
    ends = obj["ends"]

    # create a list of mentions
    mentions = zip(mention_ids, mention_words, types, starts, ends)
    mentions = map(lambda x: {"mention_id" : x[0], "word" : x[1], "type" : x[2], "start" : x[3], "end" : x[4]}, mentions)

    # don't output features for sentences that are too long
    if len(mentions) > 20 or len(lemma) > 100:
        continue

    # list of Word objects
    word_obj_list = ddlib.unpack_words(obj, lemma='lemma', words='words', dep_graph='dep_graph', \
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

            print json.dumps({"doc_id":doc_id, "mid1": m1["mention_id"], "mid2": m2["mention_id"], "word1": m1["word"], "word2": m2["word"], "feature":feature, "type1":m1["type"], "type2":m2["type"]})
