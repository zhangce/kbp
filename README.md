KBP
===

This application is for the slot filling task of the 
[TAC KBP competition](http://www.nist.gov/tac/2014/KBP/).

The following files will be useful for running the application:
- *env.sh:* sets up DeepDive environment variables
- *env_db.sh:* sets up DB-specific environment variables
- *setup_database.sh:* loads the starting DB and creates additional necessary tables
- *run.sh:* runs the application using DeepDive

Edit *env_db.sh* as necessary to change the *PGHOST*, *PGPORT*, and *DBNAME* variables.

If running the KBP application for the first time, set up the database (*setup_database.sh* runs *env.sh* and *env_db.sh*):
```
>> source setup_database.sh
```

To run DeepDive (only this step needs to be re-run during development) - this also runs *env.sh* and *env_db.sh*:
```
>> ./run.sh
```


Initial data
----

The starter database contains 6 tables:
- *sentence*: NLP-processed raw sentences (contain NER tags, dependency paths, etc.)
```
deepdive_kbp=# \d sentence
               Table "public.sentence"
           Column            |   Type    | Modifiers 
-----------------------------+-----------+-----------
 id                          | bigint    | 
 doc_id                      | text      | 
 text                        | text      | 
 original_text               | text[]    | 
 words                       | text[]    | 
 pos                         | text[]    | 
 ner                         | text[]    | 
 lemma                       | text[]    | 
 gender                      | text[]    | 
 true_case_text              | text[]    | 
 timex_value                 | text[]    | 
 timex_type                  | text[]    | 
 character_offset_begin      | integer[] | 
 character_offset_end        | integer[] | 
 dep_graph                   | text[]    | 
 sentence_index              | integer   | 
 paragraph                   | integer   | 
 sentence_token_offset_begin | integer   | 
 constituency_parse          | text      | 
 sentence_id                 | text      | 
Distributed by: (doc_id)
```

- *entities*: the Freebase entities
```
deepdive_kbp=# select * from entities limit 5;
    fid    |      text       |     type      
-----------+-----------------+---------------
 m.026tjxz | andrés mata     | people.person
 m.0178rl  | tim rice        | people.person
 m.0n9kvs1 | norma           | people.person
 m.0ykxjhq | richard plofker | people.person
 m.0hn30xt | rona            | people.person
(5 rows)
```

- *kb*: contains tuples of the form (entity1, relation, entity2); this is the knowledge base used for distant supervision
```
deepdive_kbp=# select * from kb limit 5;
    eid1    |          rel          |   eid2   
------------+-----------------------+----------
 m.0105fkh_ | per:LOCATION_of_birth | m.0t80w
 m.0268317  | per:LOCATION_of_birth | m.09c7w0
 m.026k5hl  | per:LOCATION_of_birth | m.04p3c
 m.027kd7p  | per:LOCATION_of_birth | m.09c7w0
 m.02q7wf6  | per:LOCATION_of_birth | m.05ywg
(5 rows)
```

- *fbalias*: contains Freebase aliases for entities (a single entity can have several aliases)
```
deepdive_kbp=# select * from fbalias limit 5;
    fid    |        type        |      slot      
-----------+--------------------+----------------
 m.05c_l_k | common.topic.alias | gf
 m.0b42_l  | common.topic.alias | dadawah
 m.0x1ynxb | common.topic.alias | aderlan santos
 m.01w9jj  | common.topic.alias | ziq
 m.04mzjkx | common.topic.alias | leo ross
(5 rows)
```

- *relation_types*: contains the typed relations we care to extract
```
deepdive_kbp=# select * from relation_types limit 5;
 type1  | type2  |       rel        | is_functional 
--------+--------+------------------+---------------
 PERSON | PERSON | per:parents      | f
 PERSON | PERSON | per:other_family | f
 PERSON | PERSON | per:siblings     | f
 PERSON | PERSON | per:spouse       | f
 PERSON | PERSON | per:children     | f
(5 rows)
```

- *incompatible_relations*: contains tuples of the form (relation1, relation2) where relation2 is incompatible with relation1; this is used to generate negative examples (given (e1, relation1, e2), (e1, relation2, e2) will be a negative example)
```
deepdive_kbp=# select * from incompatible_relations limit 5;
         type1         |           type2           
-----------------------+---------------------------
 per:date_of_death     | per:date_of_birth
 per:date_of_death     | per:title
 per:religion          | per:title
 per:LOCATION_of_death | per:employee_or_member_of
 per:LOCATION_of_death | per:LOCATION_of_birth
(5 rows)
```

The file schema.sql creates 3 more tables, which will be populated by the extractors. The tables are:
- mentions (populated by *ext_mention*)
- relation_mentions (populated by *ext_relation_mention_positive*, *ext_relation_mention_negative*, and *ext_relation_mention*)
- relation_mention_features (populated by *ext_relation_mention_feature*)


Overview
----

The application contains a number of extractors and a single inference rule.

There are several types of extractors:
- Entity mention extractor (*ext_mention*)
- Relation mention feature extractor (*ext_relation_mention_feature*)
- Coreference candidate extractor (*ext_coref_candidate*)
- Entity linking feature extractors (starts with *ext_el_feature_extstr_person* and ends with *ext_el_feature_coref*)
- Extractors that generate positive (*ext_relation_mention_positive*) and negative (*ext_relation_mention_negative*) training examples for relation mentions
- Relation mention extractor (*ext_relation_mention*)

Refer to the comments in *application.conf* for more information on each of these extractors.

The inference rule (*relation_mention_lr*) simply uses the features extracted from the relation mentions to learn the expectation of a given relation mention being correct.