#! /bin/bash

export DEEPDIVE_HOME=`cd $(dirname $0)/../..; pwd`
export APP_HOME=`cd $(dirname $0); pwd`

# Machine Configuration
export MEMORY="64g"
export PARALLELISM=8

# SBT Options
export SBT_OPTS="-Xmx$MEMORY"

# Database Configuration (this is overridden in setup_database.sh)
export DBNAME="deepdive_`whoami`"
export PGUSER=${PGUSER:-`whoami`}
export PGPASSWORD=${PGPASSWORD:-}
export PGPORT=${PGPORT:-5432}
export PGHOST=${PGHOST:-localhost}

#export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:/dfs/rulk/0/hazy_share/lib64/:/dfs/rulk/0/hazy_share/lib/protobuf/lib/:/dfs/rulk/0/hazy_share/lib/tclap/lib/"

# the deepdive_kbp DB dump files (2 of them to fit Github's size limit)
export DB_DUMP_FILE_1=$APP_HOME/data/deepdive_kbp_dump/deepdive_kbp.dump.1
export DB_DUMP_FILE_2=$APP_HOME/data/deepdive_kbp_dump/deepdive_kbp.dump.2

# the combined DB dump file that will be used to recreate the DB
export DB_DUMP_FILE_COMBINED=$APP_HOME/data/deepdive_kbp_dump/deepdive_kbp.dump