KBP
====

This application is for the slot filling (relation extraction) task of the 
[TAC KBP competition](http://www.nist.gov/tac/2014/KBP/). This example uses data for the 2010 task.

## Installing DeepDive

This tutorial assumes a working installation of DeepDive.
Please go through the
[example application walkthrough](http://deepdive.stanford.edu/doc/walkthrough.html) before proceeding.

After following the walkthrough, your deepdive directory should contain a folder called "app", which should contain a folder called "spouse".

## Setting up KBP Application

### Cloning the repository

Navigate to the folder "app" (same folder as you use in the walkthrough), 
clone this repositary, and switch to the correct branch.

    >> git clone https://github.com/zhangce/kbp.git
    >> cd kbp
    >> git checkout mike-tsv-extractors

To validate this step, you should see:

    >> git branch
      master
      mike-ce-stringlib
    * mike-tsv-extractors
    >> ls
    README.md           data            env_db.sh       run-evaluate.sh     schema.sql          udf
    application.conf    env.sh          evaluation      run.sh              setup_database.sh          		
	
From now on we will be working in the kbp directory.

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
    
### Loading initial data

The initial database dump contains the following tables:
- `sentence`: Result of processing raw text sentences using the [Stanford NLP parser](http://nlp.stanford.edu/software/lex-parser.shtml). The sentence table contains 70805 sentences, which is 0.2% of the full corpus for 2010.
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

You are now ready to run the KBP application.

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


## Application Overview

The application contains a number of extractors and a single inference rule.

### Extractors

There are several types of extractors:
- Entity mention extractor (`ext_mention`)
- Relation mention feature extractor (`ext_relation_mention_feature`)
- Coreference candidate extractor (`ext_coref_candidate`)
- Entity linking feature extractors (starts with `ext_el_feature_extstr_person` and ends with `ext_el_feature_coref`)
- Extractors that generate positive (`ext_relation_mention_positive`) and negative (`ext_relation_mention_negative`) training examples for relation mentions
- Relation mention extractor (`ext_relation_mention`)

Refer to the comments in *application.conf* for more information on each of these extractors.

### Inference rules

The inference rule (`relation_mention_lr`) simply uses the features extracted from the relation mentions to learn the expectation of a given relation mention being correct.

### Debugging extractors

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