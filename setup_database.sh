#! /bin/bash

dropdb $DBNAME
createdb $DBNAME

# combine the dump files together
cat $DB_DUMP_FILE_1 $DB_DUMP_FILE_2 > $DB_DUMP_FILE_COMBINED

# restore the database from the dump
pg_restore -p $PGPORT -h $PGHOST -d $DBNAME $DB_DUMP_FILE_COMBINED

# additional tables
psql -p $PGPORT -h $PGHOST $DBNAME < schema.sql