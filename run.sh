#! /bin/bash

#source "$APP_HOME/setup_database.sh"

export DBNAME="deepdive_kbp_msushkov_large"
export PGPORT=6432
export PGHOST=madmax6
export PGUSER=czhang
export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:/dfs/rulk/0/hazy_share/lib64/:/dfs/rulk/0/hazy_share/lib/protobuf/lib/:/dfs/rulk/0/hazy_share/lib/tclap/lib/"


if [ -f $DEEPDIVE_HOME/sbt/sbt ]; then
  echo "DeepDive $DEEPDIVE_HOME"
else
  echo "[ERROR] Could not find sbt in $DEEPDIVE_HOME!"
  exit 1
fi


mv /lfs/madmax6/0/czhang/grounding4 /lfs/madmax6/0/czhang/grounding4_`date +"%T"`
mkdir /lfs/madmax6/0/czhang/grounding4
cd $DEEPDIVE_HOME
env $DEEPDIVE_HOME/sbt/sbt "run -c $APP_HOME/application.conf"

# # remove the results file for evaluation
# rm $EL_RESULTS_FILE
# touch $EL_RESULTS_FILE

# # after inference is done, populate the results file
# source "$APP_HOME/populate_results.sh"

# # run the EL evaluation script
# perl $APP_HOME/evaluation/entity-linking/kbpenteval.pl $APP_HOME/evaluation/entity-linking/el_2010_eval_answers.tsv $APP_HOME/evaluation/entity-linking/results/out.tsv

# # run the RE evaluation script
# source $APP_HOME/evaluation/slotfilling/evaluate.sh 2010
