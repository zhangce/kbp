KBP
===

This application is for the slot filling task of the 
[TAC KBP competition](http://www.nist.gov/tac/2014/KBP/).


## Installation of DeepDive

To use this code, you need to install DeepDive first. 
We assume that you have already finish the 
[walkthrough](http://deepdive.stanford.edu/doc/walkthrough.html).
That is, you already have a folder called "app", that contains
a "spouse" folder.

## Run KBP Application

First, go to the folder "app" (same folder as you use in the walkthrough), 
clone this repositary, and switch to the correct branch.

    Ces-MacBook-Pro:app czhang$ git clone https://github.com/zhangce/kbp.git
    Ces-MacBook-Pro:app czhang$ cd kbp
    Ces-MacBook-Pro:kbp czhang$ git checkout mike-ce-stringlib

To validate this step, you should see

    Ces-MacBook-Pro:kbp czhang$ git branch
      master
    * mike-ce-stringlib
    Ces-MacBook-Pro:kbp czhang$ ls
      README.md        data	             udf              application.conf        setup_database.sh		
      env_db.sh        schema.sql          env.sh           run.sh             		
	
     			              
Second, change the database setting in the file `env_db.sh`, which is

    #! /bin/bash
    export DBNAME=deepdive_kbp_mikhail
    export PGHOST=localhost
    export PGPORT=5432

Change this file to the database you want.

To validate this step, you should be able to connect to the database using
    
    Ces-MacBook-Pro:kbp czhang$ source env_db.sh
    Ces-MacBook-Pro:kbp czhang$ psql -h $PGHOST -p $PGPORT -l
                                            List of databases
              Name           |  Owner   | Encoding | Collate | Ctype |   Access privileges   
    -------------------------+----------+----------+---------+-------+-----------------------
     template0               | postgres | UTF8     | C       | C     | =c/postgres          +
    ...
    
Third, Load initial data into the database (e.g., sentence, freebase etc.)

    Ces-MacBook-Pro:kbp czhang$ sh setup_database.sh 

You might see some errors, but don't worry, we will validate this step as follows.

    Ces-MacBook-Pro:kbp czhang$ source env_db.sh
        
    Ces-MacBook-Pro:kbp czhang$ psql -h $PGHOST -p $PGPORT $DBNAME -c "SELECT doc_id, text FROM sentence LIMIT 1"
                  doc_id              |                             text                             
    ----------------------------------+--------------------------------------------------------------
     AFP_ENG_20070104.0483.LDC2009T13 | "When you see the people's spirit, you know this is going to+
                                      | continue. 
    (1 row)
        
    Ces-MacBook-Pro:kbp czhang$ psql -h $PGHOST -p $PGPORT $DBNAME -c "SELECT * FROM kb LIMIT 1"
       eid1   |          rel          |  eid2   
    ----------+-----------------------+---------
     m.01f0tg | per:LOCATION_of_birth | m.0fhp9
    (1 row)
        
    Ces-MacBook-Pro:kbp czhang$ psql -h $PGHOST -p $PGPORT $DBNAME -c "SELECT * FROM entities LIMIT 1"
        fid    |    text     |     type      
    -----------+-------------+---------------
     m.026tjxz | andrés mata | people.person
    (1 row)
        
    Ces-MacBook-Pro:kbp czhang$ psql -h $PGHOST -p $PGPORT $DBNAME -c "SELECT * FROM fbalias LIMIT 1"
        fid    |        type        |    slot    
    -----------+--------------------+------------
     m.03hzmy2 | common.topic.alias | kato, gary
    (1 row)

Hopefully the schema of these tables are self-explanable.

Now we are ready to run the Application. Type in

    Ces-MacBook-Pro:kbp czhang$ time sh run.sh
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

To see some example results, type in

    Ces-MacBook-Pro:kbp czhang$ source env_db.sh
    Ces-MacBook-Pro:kbp czhang$ psql -h $PGHOST -p $PGPORT $DBNAME -c "select word1, word2, rel from relation_mentions_is_correct_inference where rel = 'per:title' order by expectation desc limit 10;"
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


## Evaluation

To get a score, which probably is a bad score because there are only
70805 sentences in the dump (our sample is 0.2% of the full corpus), type in

    Ces-MacBook-Pro:kbp czhang$ sh run-evaluate.sh
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
(our sample is 0.2% of the full corpus).

For the ease of error analysis, we also include a relational-form of the ground truth. To
see the ground truth, type in

    Ces-MacBook-Pro:kbp czhang$ source env_db.sh 
    Ces-MacBook-Pro:kbp czhang$ psql -h $PGHOST -p $PGPORT $DBNAME -c "SELECT * FROM ea limit 10;"
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


OLD DOCS
----

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
