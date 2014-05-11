#! /usr/bin/env python

import ddext

def init():

	# SELECT DISTINCT r.doc_id,
    #                          r.mid1,
    #                          t2.mention_id,
    #                          r.word1,
    #                          t2.word,
    #                          kb.rel,
    #                          f1.fid,
    #                          f2.fid

	ddext.input('doc_id', 'text')
	ddext.input('mid1', 'text')
	ddext.input('mid2', 'text')
	ddext.input('word1', 'text')
	ddext.input('word2', 'text')
	ddext.input('rel', 'text')
	ddext.input('type1', 'text')
	ddext.input('type2', 'text')
	
    # INSERT INTO relation_mentions (doc_id, mid1, mid2, word1, word2, rel, is_correct)
	ddext.returns('doc_id', 'text')
	ddext.returns('mid1', 'text')
	ddext.returns('mid2', 'text')
	ddext.returns('word1', 'text')
	ddext.returns('word2', 'text')
	ddext.returns('rel', 'text')
	ddext.returns('is_correct', 'boolean')


def run(doc_id, mid1, mid2, word1, word2, rel, type1, type2):
    to_return = False
	if not rel.contains('LOCATION'):
        to_return = True
    else:
        if type1 == 'base.locations.countries' and (type2 == 'base.place.country' or type2 == 'location.country'):
            to_return = True
        elif type1 == 'base.place.country' and (type2 == 'location.country' or type2 == 'base.locations.countries'):
            to_return = True
        elif type1 == 'location.country' and (type2 == 'base.locations.countries' or type2 == 'base.place.country'):
            to_return = True
        elif type1 == 'base.locations.cities_and_towns' and type2 == 'location.citytown':
            to_return = True
        elif type2 == 'base.locations.cities_and_towns' and type1 == 'location.citytown':
            to_return = True
        elif type1 == 'location.province' and type2 == 'base.locations.states_and_provences':
            to_return = True
        elif type2 == 'location.province' and type1 == 'base.locations.states_and_provences':
            to_return = True
        elif type1 == 'location.location' and type2 == 'location.location':
            to_return = True

    if to_return:
        yield {"doc_id": doc_id, "mid1": mid1, "mid2": mid2, "word1": word1, "word2": word2, "rel": rel, "is_correct": False}
