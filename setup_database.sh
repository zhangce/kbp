#! /bin/bash

# DB configuration
export PGHOST=madmax6
export PGPORT=6432
export DBNAME=deepdive_kbp_new_test

dropdb $DBNAME
createdb $DBNAME

# combine the dump files together
cat $DB_DUMP_FILE_1 $DB_DUMP_FILE_2 > $DB_DUMP_FILE_COMBINED

# restore the database from the dump
pg_restore -p $PGPORT -h $PGHOST -d $DBNAME $DB_DUMP_FILE_COMBINED

# additional tables
psql -p $PGPORT -h $PGHOST $DBNAME < schema.sql