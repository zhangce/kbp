#! /bin/bash

export APP_HOME="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
export DEEPDIVE_HOME="$( cd $APP_HOME && cd ../..  && pwd )"

source "$APP_HOME/env.sh"
source "$APP_HOME/env_db.sh"

echo "Dropping the database..."
date
dropdb $DBNAME

echo "Creating the database..."
date
createdb $DBNAME

# combine the dump files together
echo "Combining DB dump files..."
date
cat $DB_DUMP_FILE_1 $DB_DUMP_FILE_2 > $DB_DUMP_FILE_COMBINED

# restore the database from the dump
echo "Restoring DB from dump..."
date
pg_restore -p $PGPORT -h $PGHOST -d $DBNAME $DB_DUMP_FILE_COMBINED

# additional tables
psql -p $PGPORT -h $PGHOST $DBNAME < schema.sql