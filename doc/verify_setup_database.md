---
layout: default
---

Verifying setup_database.sh
====

To verify that the script `setup_database.sh` loaded the initial data properly, run the following commands and make sure that your output matches what is shown:

    >> source env_db.sh

    >> psql $DBNAME -c "\d"
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
        
    >> psql $DBNAME -c "SELECT doc_id, text FROM sentence LIMIT 1"
                  doc_id              |                             text                             
    ----------------------------------+--------------------------------------------------------------
     AFP_ENG_20070104.0483.LDC2009T13 | "When you see the people's spirit, you know this is going to+
                                      | continue. 
    (1 row)
        
    >> psql $DBNAME -c "SELECT * FROM kb LIMIT 1"
       eid1   |          rel          |  eid2   
    ----------+-----------------------+---------
     m.01f0tg | per:LOCATION_of_birth | m.0fhp9
    (1 row)
        
    >> psql $DBNAME -c "SELECT * FROM entities LIMIT 1"
        fid    |    text     |     type      
    -----------+-------------+---------------
     m.026tjxz | andrés mata | people.person
    (1 row)
        
    >> psql $DBNAME -c "SELECT * FROM fbalias LIMIT 1"
        fid    |        type        |    slot    
    -----------+--------------------+------------
     m.03hzmy2 | common.topic.alias | kato, gary
    (1 row)

     >> psql $DBNAME -c "SELECT * FROM relation_types LIMIT 1"
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

    >> psql $DBNAME -c "\d entities"
      Table "public.entities"
     Column | Type | Modifiers 
    --------+------+-----------
     fid    | text | 
     text   | text | 
     type   | text | 