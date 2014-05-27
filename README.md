---
layout: default
---

KBP
====

In this document we will build an application for the slot filling (relation extraction) task of the 
[TAC KBP competition](http://www.nist.gov/tac/2014/KBP/). This example uses a sample of the data for the 2010 task. Note that the data provided in this example application is only 0.2% of the original corpus so the recall of the results (and thus the F1 score) will be low. However, using 100% of the 2010 corpus, this example system achieves a winning score of ___ on the KBP task.

<a id="overview" href="#"> </a>

## Application overview

This tutorial will walk you through building a full DeepDive application that extracts the TAC KBP relationships between mentions of entities in raw text. We use news articles and blogs as our input data and want to extract all pairs of entities that participate in the KBP relations (e.g. *Barack Obama* and *Michelle Obama* for the `spouse` relation).

The application is an extension of the [mention-level extraction system](http://deepdive.stanford.edu/doc/walkthrough-mention.html). The application performs the following high-level steps:

1. Load data from provided database dump
2. Extract entity mentions from sentences
3. Extract lexical and syntactic features for relation mentions (entity mentions pairs in the same sentence)
4. Extract candidates for coreferent mentions
5. Extract features for entity linking (linking Freebase entities to mentions in text)
6. Generate positive and negative training examples for relation mentions
7. Extract the relation mentions
8. Generate a factor graph using inference rules
9. Perform inference and learning
10. Generate results

For simplicity, we will start by loading a database dump that contains all of the tables necessary to run the system.

Let us now go through the steps to get the example KBP system up and running.

### Contents

* [Installing DeepDive](#installing)
* [Setting up KBP application]()
  - [Cloning the repository]()
  - [Connecting to the database]()
  - [Loading initial data]()
* [Writing extractors]()
* [Debugging extractors]()
* [Writing inference rules]()
* [Running KBP application]()
* [Evaluating the results]()


<a id="inference_overview" href="#"> </a>

### Overview of inference rules

The inference rule (`relation_mention_lr`) simply uses the features extracted from the relation mentions to learn the expectation of a given relation mention being correct.

<a id="installing" href="#"> </a>

## Installing DeepDive

This tutorial assumes a working installation of DeepDive.
Please go through the
[example application walkthrough](http://deepdive.stanford.edu/doc/walkthrough.html) before proceeding.

After following the walkthrough, your deepdive directory should contain a folder called "app", which should contain a folder called "spouse".

<a id="setting_up" href="#"> </a>

## Setting Up KBP Application

<a id="cloning" href="#"> </a>

### Cloning the repository

Navigate to the folder "app" (same folder as you use in the walkthrough), 
clone this repository, and switch to the correct branch.

    >> git clone https://github.com/zhangce/kbp.git
    >> cd kbp
    >> git checkout mike-tsv-extractors

To validate this step, you should see:

    >> git branch
      master
      mike-ce-stringlib
      mike-readme
    * mike-tsv-extractors
    >> ls
    README.md           data            env_db.sh       run-evaluate.sh     schema.sql          udf
    application.conf    env.sh          evaluation      run.sh              setup_database.sh          		
	
From now on we will be working in the kbp directory.

<a id="connecting" href="#"> </a>

### Connecting to the database

Change the database settings in the file `env_db.sh`, whose original contents is:

    #! /bin/bash
    export DBNAME=deepdive_kbp_mikhail
    export PGHOST=localhost
    export PGPORT=5432

Change this file to point to your database.

To validate this step, you should be able to connect to the database by running the following commands:
    
    >> source env_db.sh
    >> psql -h $PGHOST -p $PGPORT -l
                                            List of databases
              Name           |  Owner   | Encoding | Collate | Ctype |   Access privileges   
    -------------------------+----------+----------+---------+-------+-----------------------
     template0               | postgres | UTF8     | C       | C     | =c/postgres          +
    ...
    
<a id="loading" href="#"> </a>

### Loading initial data

The initial database dump contains the following tables:
- `sentence`: contains processed sentence data by an [NLP extractor](walkthrough-extras.html#nlp_extractor). This table contains tokenized words, lemmatized words, POS tags, NER tags, dependency paths for each sentence. The table contains 70805 sentences, which is 0.2% of the full corpus for 2010.
- `kb`: Contains tuples of the form (entity1, relation, entity2); this is the knowledge base used for distant supervision.
- `entities`: A set of entities from Freebase.
- `fbalias`: Freebase aliases for entities (a single entity can have several aliases).
- `relation_types`: The typed relations we care to extract.
- `incompatible_relations`: Contains tuples of the form (relation1, relation2) where relation2 is incompatible with relation1. This is used to generate negative examples (given (e1, relation1, e2), (e1, relation2, e2) will be a negative example).
- `ea`: Contains the ground truth for the evaluation; to be used for error analysis.

There are 3 additional tables that the system will need to create, to be used by the extractors. The tables are:
- `mentions` (populated by `ext_mention`)
- `relation_mentions` (populated by `ext_relation_mention_positive`, `ext_relation_mention_negative`, and `ext_relation_mention`)
- `relation_mention_features` (populated by `ext_relation_mention_feature`)

The first 7 tables are included in the database dump, and the second 3 tables are created in `schema.sql`. The script `setup_database.sh` will load all 10 tables into the database.

Load the initial database:

    >> sh setup_database.sh

You may see some errors, but don't worry, they can be ignored. Validate that this step succeeded as follows:

    >> source env_db.sh

    >> psql -h $PGHOST -p $PGPORT $DBNAME -c "\d"
                       List of relations
     Schema |           Name            | Type  |  Owner   
    --------+---------------------------+-------+----------
     public | ea                        | table | czhang
     public | entities                  | table | czhang
     public | fbalias                   | table | czhang
     public | incompatible_relations    | table | msushkov
     public | kb                        | table | czhang
     public | mentions                  | table | msushkov
     public | relation_mention_features | table | msushkov
     public | relation_mentions         | table | msushkov
     public | relation_types            | table | msushkov
     public | sentence                  | table | czhang
    (10 rows)
        
    >> psql -h $PGHOST -p $PGPORT $DBNAME -c "SELECT doc_id, text FROM sentence LIMIT 1"
                  doc_id              |                             text                             
    ----------------------------------+--------------------------------------------------------------
     AFP_ENG_20070104.0483.LDC2009T13 | "When you see the people's spirit, you know this is going to+
                                      | continue. 
    (1 row)
        
    >> psql -h $PGHOST -p $PGPORT $DBNAME -c "SELECT * FROM kb LIMIT 1"
       eid1   |          rel          |  eid2   
    ----------+-----------------------+---------
     m.01f0tg | per:LOCATION_of_birth | m.0fhp9
    (1 row)
        
    >> psql -h $PGHOST -p $PGPORT $DBNAME -c "SELECT * FROM entities LIMIT 1"
        fid    |    text     |     type      
    -----------+-------------+---------------
     m.026tjxz | andrés mata | people.person
    (1 row)
        
    >> psql -h $PGHOST -p $PGPORT $DBNAME -c "SELECT * FROM fbalias LIMIT 1"
        fid    |        type        |    slot    
    -----------+--------------------+------------
     m.03hzmy2 | common.topic.alias | kato, gary
    (1 row)

     >> psql -h $PGHOST -p $PGPORT $DBNAME -c "SELECT * FROM relation_types LIMIT 1"
     type1  | type2  |       rel        | is_functional 
    --------+--------+------------------+---------------
     PERSON | PERSON | per:parents      | f
    (1 row)

    >> psql -h $PGHOST -p $PGPORT $DBNAME -c "SELECT * FROM incompatible_relations LIMIT 1"
             type1         |           type2           
    -----------------------+---------------------------
     per:date_of_death     | per:date_of_birth
    (1 row)

To check the schema of any of these tables, run the following:

    >> psql -h $PGHOST -p $PGPORT $DBNAME -c "\d entities"
      Table "public.entities"
     Column | Type | Modifiers 
    --------+------+-----------
     fid    | text | 
     text   | text | 
     type   | text | 


<a id="writing_extractors" href="#"> </a>

## Writing extractors

The extractors are created in `application.conf`. Several extractors in this example are [TSV extractors](http://deepdive.stanford.edu/doc/extractors.html#tsv_extractor), and the UDFs for them are contained in `APP_HOME/udf`. However, the majority are [SQL extractors](http://deepdive.stanford.edu/doc/extractors.html#sql_extractor) that do not have UDFs.

As stated in the [overview](#overview), the extractors perform the following high-level tasks:

- Extract entity mentions from sentences
- Extract lexical and syntactic features for relation mentions (entity mentions pairs in the same sentence)
- Extract candidates for coreferent mentions
- Extract features for entity linking (linking Freebase entities to mentions in text)
- Generate positive and negative training examples for relation mentions
- Extract the relation mentions

We will walk through each of the extractors in more detail below.


### Cleanup

The `ext_cleanup` extractor cleans up the tables that will be populated by the extractors. This extractor is defined in `application.conf` using the following code:

```bash
ext_cleanup {
  sql: """
    DELETE FROM relation_mentions;
    DELETE FROM relation_mention_features;
    DELETE FROM mentions;
  """
  style: "sql_extractor"
}
```

### Entity mentions

We first need to identify the entity mentions in the text. Given a set of sentences, the entity mention extractor will populate the `mentions` table using NER tags from the `sentence` table, generated by the NLP toolkit.

A mention can consist of multiple words (e.g. Barack Obama); the way we can identify these is if all of these words have the same NER tag.

This extractor goes through all the words in the sentence and outputs as a mention the consecutive words that have the same NER tag.

This extractor is defined in `application.conf` using the following code:

```bash
ext_mention {
  input : """
    SELECT doc_id,
           sentence_id,
           my_array_to_string(words, '~^~', 'NULL') AS words,
           my_array_to_string(ner, '~^~', 'NULL') AS ner,
           my_array_to_string(character_offset_begin, '~^~', 'NULL') AS character_offset_begin,
           my_array_to_string(character_offset_end, '~^~', 'NULL') AS character_offset_end
    FROM sentence
  """
  output_relation: "mentions"
  udf: ${APP_HOME}"/udf/ext_mention.py"
  style: "tsv_extractor"
  dependencies : ["ext_cleanup"]
}
```

The input query simply selects the appropriate columns from the sentence table and converts the columns that contain arrays to strings (since TSV extractors take in strings as input).

**Input:** sentences along with NER tags. Specically, each line in the input to this extractor UDF is a row in the `sentence` table in TSV format, e.g.:

    TODO

**Output:** rows in `mentions` table, e.g.:

    TODO

The script `$APP_HOME/udf/ext_mention.py` is the UDF for this extractor, which can be written as follows:

```python
#! /usr/bin/env python

"""
Extractor for entity mentions.

A mention can consist of multiple words (e.g. Barack Obama); the way we can identify these is if all of these words have the same NER tag.

This extractor goes through all the words in the sentence and outputs as a mention the consecutive words that have the same NER tag that is not in EXT_MENTION_IGNORE_TYPE.

Input query:

        SELECT doc_id,
               sentence_id,
               my_array_to_string(words, '~^~', 'NULL') AS words,
               my_array_to_string(ner, '~^~', 'NULL') AS ner,
               my_array_to_string(character_offset_begin, '~^~', 'NULL') AS character_offset_begin,
               my_array_to_string(character_offset_end, '~^~', 'NULL') AS character_offset_end
        FROM sentence
"""

import sys

# the NER tags that wil not correspond to entity mentions types
EXT_MENTION_IGNORE_TYPE = {'URL': 1, 'NUMBER' : 1, 'MISC' : 1, 'CAUSE_OF_DEATH' : 1,
    'CRIMINAL_CHARGE' : 1, 'DURATION' : 1, 'MONEY' : 1, 'ORDINAL' : 1, 'RELIGION' : 1,
    'SET' : 1, 'TIME' : 1}

# words that are representative of the TITLE type
EXT_MENTION_TITLE_TYPE = {'winger' : 1, 'singer\\\\/songwriter' : 1, 'founder' : 1,
    'president' : 1, 'executive director' : 1, 'producer' : 1, 'star' : 1, 'musician' : 1,
    'nightlife impresario' : 1, 'lobbyist' : 1}

# the delimiter used to separate columns in the input
ARR_DELIM = '~^~'

for row in sys.stdin:
  # row is a string where the columns are separated by tabs
  (doc_id, sentence_id, words_str, ner_str, character_offset_begin_str, \
    character_offset_end_str) = row.strip().split('\t')

  words = words_str.split(ARR_DELIM)
  ner = ner_str.split(ARR_DELIM)
  character_offset_begin = map(lambda x: int(x), character_offset_begin_str.split(ARR_DELIM))
  character_offset_end = map(lambda x: int(x), character_offset_end_str.split(ARR_DELIM))

  # keep track of words whose NER tags we look at
  history = {}

  # go through each word in the sentence
  for i in range(0, len(words)):
    # if we already looked at this word's NER tag, skip it
    if i in history:
      continue

    # the NER tag for the current word
    curr_ner = ner[i]

    # skip this word if this NER tag should be ignored
    if curr_ner in EXT_MENTION_IGNORE_TYPE:
      continue

    # collapse specific location types
    if curr_ner in ["CITY", "COUNTRY", "STATE_OR_PROVINCE"]:
      curr_ner = "LOCATION"

    # if the current word has a valid NER tag
    if curr_ner != 'O' and curr_ner != 'NULL':
      j = i

      # go through each of the words after the current word until the end of the sentence
      for j in range(i, len(words)):
        nerj = ner[j]

        # collapse specific location types
        if nerj in ["CITY", "COUNTRY", "STATE_OR_PROVINCE"]:
          nerj = "LOCATION"

        # go until the NER tags of word 1 and word 2 do not match
        if nerj != curr_ner:
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

      # doc_id, mention_id, sentence_id, word, type, start_pos, end_pos
      output = [doc_id, mention_id, sentence_id, word.lower(), curr_ner, str(i), str(j)]

      # make sure each of the strings we will output is encoded as utf-8
      map(lambda x: x.decode('utf-8', 'ignore'), output)

      print "\t".join(output)
    
    # if this word has an NER tag of '0' or NULL
    else:
      # if the current word is one of the known titles, then we have a TITLE mention
      if words[i].lower() in EXT_MENTION_TITLE_TYPE:
        history[i] = 1
        word = words[i]
        
        # construct a unique ID for this entity mention
        mention_id = doc_id + "_%d_%d" % (character_offset_begin[i], character_offset_end[i])
        
        # doc_id, mention_id, sentence_id, word, type, start_pos, end_pos
        output = [doc_id, mention_id, str(sentence_id), word.lower(), 'TITLE', str(i), str(i + 1)]

        # make sure each of the strings we will output is encoded as utf-8
        map(lambda x: x.decode('utf-8', 'ignore'), output)

        print "\t".join(output)
```

### Relation mention feature: word sequence

Once we have identified the entity mentions in text, we can extract features from all mention pairs in the same sentence (these mentions pairs are referred to as relation mentions). This extractor will extract the *word sequence* feature for a relation mention: the exact sequence of words that occurs between the two mentions.

This extractor is defined in `application.conf` using the following code:

```bash
ext_relation_mention_feature_wordseq {
  input: """
    SELECT s.doc_id AS doc_id,
           s.sentence_id AS sentence_id,
           array_to_string(max(s.lemma), '~^~') AS lemma,
           array_to_string(max(s.words), '~^~') AS words,
           array_to_string(array_accum(m.mention_id), '~^~') AS mention_ids,
           array_to_string(array_accum(m.word), '~^~') AS mention_words,
           array_to_string(array_accum(m.type), '~^~') AS types,
           array_to_string(array_accum(m.start_pos), '~^~') AS starts,
           array_to_string(array_accum(m.end_pos), '~^~') AS ends
    FROM sentence s,
         mentions m
    WHERE s.doc_id = m.doc_id AND
          s.sentence_id = m.sentence_id
    GROUP BY s.doc_id,
             s.sentence_id
    """
  output_relation: "relation_mention_features"
  udf: ${APP_HOME}"/udf/ext_relation_mention_features_wordseq.py"
  style: "tsv_extractor"
  dependencies: ["ext_cleanup", "ext_mention"]
}
```

**Input:** the list of mentions in a sentence. Specically, each line in the input to this extractor UDF is a row of the input query in TSV format, e.g.:

    TODO

**Output:** rows in `mentions` table, e.g.:

    TODO

The script `$APP_HOME/udf/ext_relation_mention_features_wordseq.py` is the UDF for this extractor, which can be written as follows:

```python
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

# the delimiter used to separate columns in the input
ARR_DELIM = '~^~'

for row in sys.stdin:
  # row is a string where the columns are separated by tabs
  (doc_id, sentence_id, lemma_str, words_str, mention_ids_str, \
    mention_words_str, types_str, starts_str, ends_str) = row.strip().split('\t')

  lemma = lemma_str.split(ARR_DELIM)
  words = words_str.split(ARR_DELIM)
  mention_ids = mention_ids_str.split(ARR_DELIM)
  mention_words = mention_words_str.split(ARR_DELIM)
  types = types_str.split(ARR_DELIM)
  starts = starts_str.split(ARR_DELIM)
  ends = ends_str.split(ARR_DELIM)

  # create a list of mentions
  mentions = zip(mention_ids, mention_words, types, starts, ends)
  mentions = map(lambda x: {"mention_id" : x[0], "word" : x[1], "type" : x[2], "start" : int(x[3]), "end" : int(x[4])}, mentions)

  # don't output features for sentences that are too long
  if len(mentions) > 20 or len(words) > 100:
    continue

  # at this point we have a list of the mentions in this sentence

  # go through all pairs of mentions
  for m1 in mentions:
    # make sure that the first mention is a PER or ORG
    if m1["type"] not in ["PERSON", "ORGANIZATION"]:
      continue

    for m2 in mentions:
      if m1["mention_id"] == m2["mention_id"]:
        continue

      # the spans of the mentions
      span1 = ddlib.Span(begin_word_id=m1["start"], length=m1["end"] - m1["start"])
      span2 = ddlib.Span(begin_word_id=m2["start"], length=m2["end"] - m2["start"])

      # the lemma sequence between the mention spans
      lemma_between = ddlib.tokens_between_spans(lemma, span1, span2)
      if lemma_between.is_inversed:
        feature = "WORDSEQ_INV:" + "_".join(lemma_between.elements).lower()
      else:
        feature = "WORDSEQ_" + "_".join(lemma_between.elements).lower()

      # doc_id, mid1, mid2, word1, word2, type1, type2, feature
      output = [doc_id, m1["mention_id"], m2["mention_id"], m1["word"], m2["word"], m1["type"], m2["type"], feature]
      
      # make sure each of the strings we will output is encoded as utf-8
      map(lambda x: x.decode('utf-8', 'ignore'), output)

      print "\t".join(output)
```

### Relation mention feature: dependency path

TODO


<a id="debugging_extractors" href="#"> </a>

## Debugging extractors

It is useful to debug each extractor individually without running the DeepDive system every time. To make this easier, a general debug extractor is provided in `udf/util/dummy_extractor.py`. This extractor produces a file from the SQL input query to allow the user to directly pipe that file into the desired extractor. Run the dummy extractor once to produce the sample file, and then debug the extractor by looking at the output without running the DeepDive pipeline.

For example, consider a scenario where we want to debug the entity mention extractor, `ext_mention`. We can first run `ext_mention_debug` to produce a sample TSV file, `udf/sample_data/ext_mention_sample_data.tsv`.

Refer to [DeepDive's pipeline functionality](http://deepdive.stanford.edu/doc/pipelines.html) to see how to run the system with only a particular extractor. We can specify something like the following in `application.conf`:

    pipeline.run: "debug_mention_ext"
    pipeline.pipelines.debug_mention_ext: ["ext_mention_debug"]

After running run.sh, this file can then be piped into the extractor we wish to debug, `udf/ext_mention.py`:

    >> cat $APP_HOME/udf/sample_data/ext_mention_sample_data.tsv | python $APP_HOME/udf/ext_mention.py

This process allows for interactive debugging of the extractors.

Note that if you change the inut SQL query to an extractor, you will also need to change it in the debug version of that extractor.

The code for `ext_mention_debug` is commented out in `application.conf`; similar code is also provided for `ext_relation_mention_feature_wordseq` and `ext_relation_mention_feature_deppath`.




You are now ready to run the KBP application.

<a id="running" href="#"> </a>

## Running KBP application

Make sure you are in the kbp directory. To run the application, type in:

    >> time sh run.sh
    ...
    04:26:09 [profiler] INFO  --------------------------------------------------
    04:26:09 [profiler] INFO  Summary Report
    04:26:09 [profiler] INFO  --------------------------------------------------
    04:26:09 [profiler] INFO  ext_cleanup SUCCESS [251 ms]
    04:26:09 [profiler] INFO  ext_mention SUCCESS [16997 ms]
    04:26:09 [profiler] INFO  ext_coref_candidate SUCCESS [2399 ms]
    04:26:09 [profiler] INFO  ext_relation_mention_feature_deppath SUCCESS [34105 ms]
    04:26:09 [profiler] INFO  ext_relation_mention_feature SUCCESS [63297 ms]
    04:26:09 [profiler] INFO  ext_el_feature_extstr_person SUCCESS [67563 ms]
    04:26:09 [profiler] INFO  ext_el_feature_extstr_organization SUCCESS [2258 ms]
    04:26:09 [profiler] INFO  ext_el_feature_extstr_title SUCCESS [3781 ms]
    04:26:09 [profiler] INFO  ext_el_feature_extstr_title2 SUCCESS [5060 ms]
    04:26:09 [profiler] INFO  ext_el_feature_extstr_location SUCCESS [8089 ms]
    04:26:09 [profiler] INFO  ext_el_feature_alias_person SUCCESS [23261 ms]
    04:26:09 [profiler] INFO  ext_el_feature_coref SUCCESS [24390 ms]
    04:26:09 [profiler] INFO  ext_el_feature_alias_title SUCCESS [32075 ms]
    04:26:09 [profiler] INFO  ext_el_feature_alias_location SUCCESS [44660 ms]
    04:26:09 [profiler] INFO  ext_el_feature_alias_organization SUCCESS [48183 ms]
    04:26:09 [profiler] INFO  ext_relation_mention_positive SUCCESS [33341 ms]
    04:26:09 [profiler] INFO  ext_relation_mention_negative SUCCESS [189 ms]
    04:26:09 [profiler] INFO  ext_relation_mention SUCCESS [3606 ms]
    04:26:09 [profiler] INFO  inference_grounding SUCCESS [16311 ms]
    04:26:09 [profiler] INFO  inference SUCCESS [47145 ms]
    04:26:09 [profiler] INFO  calibration plot written to /Users/czhang/Desktop/dd2/deepdive/out/2014-05-22T042159/calibration/relation_mentions.is_correct.png [0 ms]
    04:26:09 [profiler] INFO  calibration SUCCESS [14562 ms]
    04:26:09 [profiler] INFO  --------------------------------------------------
    04:26:09 [taskManager] INFO  Completed task_id=report with Success(Success(()))
    04:26:09 [profiler] DEBUG ending report_id=report
    04:26:09 [taskManager] INFO  1/1 tasks eligible.
    04:26:09 [taskManager] INFO  Tasks not_eligible: Set()
    04:26:09 [taskManager] DEBUG Sending task_id=shutdown to Actor[akka://deepdive/user/taskManager#1841581299]
    04:26:09 [profiler] DEBUG starting report_id=shutdown
    04:26:09 [EventStream] DEBUG shutting down: StandardOutLogger started
    Not interrupting system thread Thread[process reaper,10,system]
    [success] Total time: 251 s, completed May 22, 2014 4:26:09 AM
        
    real	4m15.001s
    user	2m30.093s
    sys	0m26.283s

To see some example results, type in:

    >> source env_db.sh
    >> psql -h $PGHOST -p $PGPORT $DBNAME -c "select word1, word2, rel from relation_mentions_is_correct_inference where rel = 'per:title' order by expectation desc limit 10;"
              word1          |   word2    |    rel    
    -------------------------+------------+-----------
     jose eduardo dos santos | president  | per:title
     kevin stallings         | coach      | per:title
     anthony hamilton        | father     | per:title
     karyn bosnak            | author     | per:title
     mahmoud ahmadinejad     | president  | per:title
     fulgencio batista       | dictator   | per:title
     raul castro             | president  | per:title
     dean spiliotes          | consultant | per:title
     simon cowell            | judge      | per:title
     castro                  | elder      | per:title
    (10 rows)


<a id="evaluating" href="#"> </a>

## Evaluating the results

The KBP application contains a scorer for the TAC KBP slot filling task. The example system will not achieve a high score on the task because our sample of 70805 sentences is only 0.2% of the full corpus.

To get the score, type in:

    >> sh run-evaluate.sh
    ...
                                	2010 scores:
    [STDOUT]                    	Recall: 5.0 / 1040.0 = 0.004807692307692308
    [STDOUT]                    	Precision: 5.0 / 8.0 = 0.625
    [STDOUT]                    	F1: 0.009541984732824428
                              } << Scoring System [0.389 seconds]
                              Running SFScore2010 {
    [WARN SFScore]              official scorer exited with non-zero exit code
                              } [0.138 seconds]
                              Generating PR Curve {
    [Eval]                      generating PR curve with 8 points
    [Eval]                      P/R curve data generated in file: /tmp/stanford1.curve
                              } 
                              Score {
    [Result]                    |           Precision: 62.500
    [Result]                    |              Recall: 00.481
    [Result]                    |                  F1: 00.954
    [Result]                    |
    [Result]                    |   Optimal Precision: �
    [Result]                    |      Optimal Recall: �
    [Result]                    |          Optimal F1: -∞
    [Result]                    |
    [Result]                    | Area Under PR Curve: 0.0
                              } 
                            } << Evaluating Test Entities [0.922 seconds]
    [MAIN]                  work dir: /tmp
                          } << main [2.405 seconds]

In this log, the precision is 62.5 (human agreement rate is around 70), and recall is low
since our sample is 0.2% of the full corpus.

For the ease of error analysis, we also include a relational-form of the ground truth. To
see the ground truth, type in:

    >> source env_db.sh 
    >> psql -h $PGHOST -p $PGPORT $DBNAME -c "SELECT * FROM ea limit 10;"
     query |                  sub                   |           rel            |           obj            
    -------+----------------------------------------+--------------------------+--------------------------
     SF208 | kendra wilkinson                       | per:age                  | 23
     SF209 | chelsea library                        | org:alternate_names      | chelsea district library
     SF212 | chad white                             | per:age                  | 22
     SF211 | paul kim                               | per:age                  | 24
     SF210 | crown prosecution service              | org:alternate_names      | cps
     SF262 | noordhoff craniofacial foundation      | org:alternate_names      | ncf
     SF263 | national christmas tree association    | org:city_of_headquarters | chesterfield
     SF260 | north phoenix baptist church           | org:city_of_headquarters | phoenix
     SF228 | professional rodeo cowboys association | org:alternate_names      | prca
     SF229 | new hampshire institute of politics    | org:city_of_headquarters | manchester
    (10 rows)
