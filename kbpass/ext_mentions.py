#! /lfs/local/0/czhang/software/pypy-2.3.1-linux_x86_64-portable/bin/pypy


import json
import re
import sys

def norm(s):
	return s.replace(' ', '').replace('_', '').replace('/', '').replace('\\', '')

stop = {'secondly': 1, 'all': 1, 'consider': 1, 'whoever': 1, 'four': 1, 'edu': 1, 'go': 1, 'causes': 1, 'seemed': 1, 'rd': 1, 'certainly': 1, 'vs': 1, 'to': 1, 'asking': 1, 'th': 1, 'under': 1, 'sorry': 1, "a's": 1, 'sent': 1, 'far': 1, 'every': 1, 'yourselves': 1, "we'll": 1, 'went': 1, 'did': 1, 'forth': 1, "they've": 1, 'try': 1, "it'll": 1, "i'll": 1, 'says': 1, "you'd": 1, 'yourself': 1, 'likely': 1, 'further': 1, 'even': 1, 'what': 1, 'appear': 1, 'brief': 1, 'goes': 1, 'sup': 1, 'new': 1, 'ever': 1, "c'mon": 1, 'whose': 1, 'respectively': 1, 'never': 1, 'here': 1, 'let': 1, 'others': 1, "hadn't": 1, 'along': 1, "aren't": 1, 'allows': 1, "i'd": 1, 'howbeit': 1, 'usually': 1, 'whereupon': 1, "i'm": 1, 'changes': 1, 'thats': 1, 'hither': 1, 'via': 1, 'followed': 1, 'merely': 1, 'while': 1, 'viz': 1, 'everybody': 1, 'use': 1, 'from': 1, 'would': 1, 'contains': 1, 'two': 1, 'next': 1, 'few': 1, 'therefore': 1, 'taken': 1, 'themselves': 1, 'thru': 1, 'tell': 1, 'more': 1, 'knows': 1, 'becomes': 1, 'hereby': 1, 'herein': 1, "ain't": 1, 'particular': 1, 'known': 1, 'must': 1, 'me': 1, 'none': 1, 'this': 1, 'oh': 1, 'anywhere': 1, 'nine': 1, 'can': 1, 'theirs': 1, 'following': 1, 'my': 1, 'example': 1, 'indicated': 1, "didn't": 1, 'indicates': 1, 'something': 1, 'want': 1, 'needs': 1, 'rather': 1, 'meanwhile': 1, 'how': 1, 'instead': 1, 'okay': 1, 'tried': 1, 'may': 1, 'after': 1, 'different': 1, 'hereupon': 1, 'such': 1, 'third': 1, 'whenever': 1, 'maybe': 1, 'appreciate': 1, 'ones': 1, 'so': 1, 'specifying': 1, 'allow': 1, 'keeps': 1, "that's": 1, 'six': 1, 'help': 1, "don't": 1, 'indeed': 1, 'over': 1, 'mainly': 1, 'soon': 1, 'course': 1, 'through': 1, 'looks': 1, 'still': 1, 'its': 1, 'before': 1, 'thank': 1, "he's": 1, 'selves': 1, 'inward': 1, 'actually': 1, 'better': 1, 'whether': 1, 'willing': 1, 'thanx': 1, 'ours': 1, 'might': 1, "haven't": 1, 'then': 1, 'non': 1, 'someone': 1, 'somebody': 1, 'thereby': 1, "you've": 1, 'they': 1, 'not': 1, 'now': 1, 'nor': 1, 'several': 1, 'hereafter': 1, 'always': 1, 'reasonably': 1, 'whither': 1, 'each': 1, 'entirely': 1, "isn't": 1, 'mean': 1, 'everyone': 1, 'doing': 1, 'eg': 1, 'ex': 1, 'our': 1, 'beyond': 1, 'out': 1, 'them': 1, 'furthermore': 1, 'since': 1, 'looking': 1, 're': 1, 'seriously': 1, "shouldn't": 1, "they'll": 1, 'got': 1, 'cause': 1, 'thereupon': 1, "you're": 1, 'given': 1, 'quite': 1, 'que': 1, 'besides': 1, 'ask': 1, 'anyhow': 1, 'could': 1, 'tries': 1, 'keep': 1, 'ltd': 1, 'hence': 1, 'onto': 1, 'think': 1, 'first': 1, 'already': 1, 'seeming': 1, 'thereafter': 1, 'one': 1, 'done': 1, 'another': 1, 'awfully': 1, "doesn't": 1, 'little': 1, 'their': 1, 'accordingly': 1, 'least': 1, 'name': 1, 'anyone': 1, 'indicate': 1, 'too': 1, 'gives': 1, 'mostly': 1, 'behind': 1, 'nobody': 1, 'took': 1, 'immediate': 1, 'regards': 1, 'somewhat': 1, 'kept': 1, 'believe': 1, 'herself': 1, 'than': 1, "here's": 1, 'unfortunately': 1, 'gotten': 1, 'second': 1, 'were': 1, 'toward': 1, 'are': 1, 'and': 1, 'beforehand': 1, 'say': 1, 'unlikely': 1, 'have': 1, 'need': 1, 'seen': 1, 'seem': 1, 'saw': 1, 'any': 1, 'relatively': 1, 'zero': 1, 'thoroughly': 1, 'latter': 1, 'that': 1, 'downwards': 1, 'aside': 1, 'thorough': 1, 'also': 1, 'take': 1, 'which': 1, 'exactly': 1, 'unless': 1, 'shall': 1, 'who': 1, "where's": 1, 'most': 1, 'eight': 1, 'but': 1, 'nothing': 1, 'why': 1, 'sub': 1, 'especially': 1, 'noone': 1, 'later': 1, 'yours': 1, "you'll": 1, 'definitely': 1, 'normally': 1, 'came': 1, 'saying': 1, 'particularly': 1, 'anyway': 1, 'fifth': 1, 'outside': 1, 'should': 1, 'only': 1, 'going': 1, 'specify': 1, 'do': 1, 'his': 1, 'above': 1, 'get': 1, 'between': 1, 'overall': 1, 'truly': 1, "they'd": 1, 'cannot': 1, 'nearly': 1, 'despite': 1, 'during': 1, 'him': 1, 'regarding': 1, 'qv': 1, 'twice': 1, 'she': 1, 'contain': 1, "won't": 1, 'where': 1, 'thanks': 1, 'ignored': 1, 'up': 1, 'namely': 1, 'anyways': 1, 'best': 1, 'wonder': 1, 'said': 1, 'away': 1, 'currently': 1, 'please': 1, 'enough': 1, "there's": 1, 'various': 1, 'hopefully': 1, 'probably': 1, 'neither': 1, 'across': 1, 'available': 1, 'we': 1, 'useful': 1, 'however': 1, 'come': 1, 'both': 1, 'last': 1, 'many': 1, "wouldn't": 1, 'thence': 1, 'according': 1, 'against': 1, 'etc': 1, 'became': 1, 'com': 1, "can't": 1, 'otherwise': 1, 'among': 1, 'presumably': 1, 'co': 1, 'afterwards': 1, 'seems': 1, 'whatever': 1, 'alone': 1, "couldn't": 1, 'moreover': 1, 'throughout': 1, 'considering': 1, 'sensible': 1, 'described': 1, "it's": 1, 'three': 1, 'been': 1, 'whom': 1, 'much': 1, 'wherein': 1, 'hardly': 1, "it'd": 1, 'wants': 1, 'corresponding': 1, 'latterly': 1, 'concerning': 1, 'else': 1, 'hers': 1, 'former': 1, 'those': 1, 'myself': 1, 'novel': 1, 'look': 1, 'these': 1, 'value': 1, 'will': 1, 'near': 1, 'theres': 1, 'seven': 1, 'whereafter': 1, 'almost': 1, 'wherever': 1, 'is': 1, 'thus': 1, 'it': 1, 'cant': 1, 'itself': 1, 'in': 1, 'ie': 1, 'if': 1, 'containing': 1, 'perhaps': 1, 'insofar': 1, 'same': 1, 'clearly': 1, 'beside': 1, 'when': 1, 'gets': 1, "weren't": 1, 'used': 1, 'see': 1, 'somewhere': 1, 'upon': 1, 'uses': 1, 'off': 1, 'whereby': 1, 'nevertheless': 1, 'whole': 1, 'well': 1, 'anybody': 1, 'obviously': 1, 'without': 1, 'comes': 1, 'very': 1, 'the': 1, 'self': 1, 'lest': 1, 'just': 1, 'less': 1, 'being': 1, 'able': 1, 'liked': 1, 'greetings': 1, 'regardless': 1, 'yes': 1, 'yet': 1, 'unto': 1, "we've": 1, 'had': 1, 'except': 1, 'has': 1, 'ought': 1, "t's": 1, 'around': 1, "who's": 1, 'possible': 1, 'five': 1, 'know': 1, 'using': 1, 'apart': 1, 'necessary': 1, 'like': 1, 'follows': 1, 'either': 1, 'become': 1, 'towards': 1, 'therein': 1, 'because': 1, 'old': 1, 'often': 1, 'some': 1, 'somehow': 1, 'sure': 1, 'specified': 1, 'ourselves': 1, 'happens': 1, 'for': 1, 'though': 1, 'per': 1, 'everything': 1, 'does': 1, 'provides': 1, 'tends': 1, 'be': 1, 'nowhere': 1, 'although': 1, 'by': 1, 'on': 1, 'about': 1, 'ok': 1, 'anything': 1, 'getting': 1, 'of': 1, 'whence': 1, 'plus': 1, 'consequently': 1, 'or': 1, 'seeing': 1, 'own': 1, 'formerly': 1, 'into': 1, 'within': 1, 'down': 1, 'appropriate': 1, 'right': 1, "c's": 1, 'your': 1, 'her': 1, 'there': 1, 'inasmuch': 1, 'inner': 1, 'way': 1, 'was': 1, 'himself': 1, 'elsewhere': 1, "i've": 1, 'becoming': 1, 'amongst': 1, 'hi': 1, 'trying': 1, 'with': 1, 'he': 1, "they're": 1, "wasn't": 1, 'wish': 1, "hasn't": 1, 'us': 1, 'until': 1, 'placed': 1, 'below': 1, 'un': 1, "we'd": 1, 'gone': 1, 'sometimes': 1, 'associated': 1, 'certain': 1, 'am': 1, 'an': 1, 'as': 1, 'sometime': 1, 'at': 1, 'et': 1, 'inc': 1, 'again': 1, 'no': 1, 'whereas': 1, 'nd': 1, 'lately': 1, 'other': 1, 'you': 1, 'really': 1, "what's": 1, 'welcome': 1, "let's": 1, 'serious': 1, 'together': 1, 'having': 1, "we're": 1, 'everywhere': 1, 'hello': 1, 'once': 1}

queries = {}

#for QUERY in ["2009.xml", "2010.xml", "2011.xml", "2012.xml"]:
#for QUERY in ["2013.xml"]:
for QUERY in ["tac_2014_kbp_english_regular_slot_filling_evaluation_queries.xml"]:
	QUERY = "/afs/cs.stanford.edu/u/czhang/" + QUERY
	for l in open(QUERY):
		m = re.search('<query id="(.*?)">', l)
		if m:
			qid = m.group(1)
		m = re.search('<name>(.*?)</name>', l)
		if m:
			name = m.group(1)
		m = re.search('<enttype>(.*?)</enttype>', l)
		if m:
			t = m.group(1)
			if t == 'PER': t = 'PERSON'
			if t == 'ORG': t = 'ORGANIZATION'
			queries[norm(name.lower())] = t

mentions2 = {}

for l in open('/afs/cs.stanford.edu/u/czhang/candidate_titles.tsv'):
	(a,b) = l.rstrip().split('\t')
	if float(b) >= 0.03 or float(b) < 0:
		mentions2[a.lower()] = 1


for l in open(sys.argv[1]):

	sent = json.loads(l)
	words = sent["words"]
	poses = sent["pos"]
	ners  = sent["ner"]
	lemmas= sent["lemma"]
	docid = sent["doc_id"]
	sentid= sent["sentence_id"]

	for i in range(len(ners)):
		if ners[i] == None:
			ners[i] = 'O'

	history = {}
	for start in range(0, len(words)):
		if start in history: continue
		for end in reversed(range(start+1,min(start+10, len(words)))):
			if end -1 in history: continue
			if end >= len(words): continue
			#print " ".join(words[start:end])
			ner = ners[start:end]
			a = {}
			n = ""
			for n in ner:
				a[n] = 0
			if len(a) == 1 and a.keys()[0] != 'O':
				for i in range(start, end):
					history[i] = 1
				print "\t".join([docid, n + "_" + sentid + "_%d_%d" % (start, end-1), sentid, " ".join(words[start:end]), n, "%d"%start, "%d"%(end-1)])
			if " ".join(lemmas[start:end]).lower() not in stop and " ".join(lemmas[start:end]).lower() in mentions2 and len(" ".join(lemmas[start:end]).lower()) > 2 and " ".join(lemmas[start:end]).lower() not in ['and']:
				n = 'TITLE'
				print "\t".join([docid, n + "_" + sentid + "_%d_%d" % (start, end-1), sentid, " ".join(words[start:end]), n, "%d"%start, "%d"%(end-1)])


	for start in range(0, len(words)):
		for end in reversed(range(start+1,min(start+10, len(words)))):
			p = norm(" ".join(words[start:end]).lower())
			if p in queries:
				n = queries[p]
				print "\t".join([docid, n + "_" + sentid + "_%d_%d" % (start, end-1), sentid, " ".join(words[start:end]), n, "%d"%start, "%d"%(end-1)])

	history = {}
	for start in range(0, len(words)):
		if start in history: continue
		end = start+1
		for end in range(end, len(words)):
			if re.search('^[A-Z]', words[end]):
				continue
			if lemmas[end] in ['a', 'an', 'the', 'of', ',', '-', 'and', 'but', 'or', 'for', 'nor', 'on', 'at', 'to', 'from', 'by']:
				continue
			break

		for j in reversed(range(start+1,end+1)):

			phrase = " ".join(words[start:j])

			isvalid = True
			for i in range(start, j):
				if i == start:
					if not re.search('^[A-Z]', words[i]) or poses[i] == 'DT':
						isvalid = False
						break
				if poses[i].startswith('NN') or re.search('^[A-Z]', words[i]):
					continue
				if i == j-1:
					isvalid = False
					break
				else:
					if poses[i] in ['CC', 'IN', ','] and not re.search('[A-Z][A-Z]', phrase):
						continue
					else:
						isvalid = False
						break

			if isvalid and (j>start+1 or re.search('^[A-Z0-9]*$', " ".join(words[start:j]))):
				if 'NN' in " ".join(poses[start:j]) and ('ORGANIZATION' in " ".join(ners[start:j]) or ('LOCATION LOCATION' not in " ".join(ners[start:j]) and 'PERSON PERSON' not in " ".join(ners[start:j]) and 'TITLE PERSON' not in " ".join(ners[start:j]))):
					if 'ORGANIZATION O ORGANIZATION' not in " ".join(ners[start:j]):
						for i in range(start,j):
							history[i] = 1

						end = j
						n = "ORGANIZATION"
						print "\t".join([docid, n + "_" + sentid + "_%d_%d" % (start, end-1), sentid, " ".join(words[start:end]), n, "%d"%(start), "%d"%(end-1)])

						break



