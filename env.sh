#! /bin/bash -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

#export DEEPDIVE_HOME=`cd $(dirname $0)/../..; pwd`
export APP_HOME=`pwd`
#export DEEPDIVE_HOME=`cd ../..; pwd`
export DEEPDIVE_HOME=/lfs/local/0/czhang/develop/deepdive/

# Machine Configuration
export MEMORY="64g"
#export MEMORY="2g"

export PARALLELISM=8
#export PARALLELISM=4

# Database Configuration
# export DBNAME="deepdive_`whoami`"
export PGUSER=${PGUSER:-`whoami`}
export PGPASSWORD=${PGPASSWORD:-}
export PGPORT=${PGPORT:-5432}
export PGHOST=${PGHOST:-localhost}

# SBT Options
export SBT_OPTS="-Xmx$MEMORY"

#
# Config files (included by application.conf)
#

# export MENTION_FEATURES_CONF=$APP_HOME/config-files/extractors/entity-linking/mention_features.conf
# export ENTITY_FEATURES_CONF=$APP_HOME/config-files/extractors/entity-linking/mention_features.conf
# export RE_FEATURES_CONF=$APP_HOME/config-files/extractors/relation-extraction/re_features.conf
# export EL_INFERENCE_CONF=$APP_HOME/config-files/inference-rules/entity-linking/el_feature_rules.conf
# export EL_COREF_CONF=$APP_HOME/config-files/inference-rules/entity-linking/coref.conf
# export RE_INFERENCE_CONF=$APP_HOME/config-files/inference-rules/relation-extraction/re_rules.conf

#
# Data files
#

# if [ -e /lfs/local/0/kbp ]; then
#   export TMP_DIR=/lfs/local/0/kbp/tmp
#   mkdir -p $TMP_DIR
# else
#   export TMP_DIR=/tmp
# fi

# do not consider sentences with more words than this
export NUM_WORDS_IN_SENTENCE=100

# do not consider EL candidate links where a mention has over this number
# of entity links
export NUM_ENTITIES_PER_MENTION=10

# document() table dump
export DOCUMENT_TABLE=/dfs/madmax4/0/kbp/db_dumps/kbp2010/document.sql

# sentence() table dump
# export SENTENCE_TABLE=/dfs/ilfs2/0/msushkov/zifei_new_ext_pipeline/sentence_10000.sql

# export SENTENCE_TABLE=/dfs/ilfs2/0/kbp/db_dumps/kbp2010/sentence.sql

# Raw data
export RAW_DATA_DIR=/dfs/madmax4/0/kbp/csv_data/kbp2010
export DOC_DIR=$RAW_DATA_DIR/doc
export SENT_DIR=$RAW_DATA_DIR/sent-backslash



#
# DeepDive files (relative paths)
#


# TAC KBP-related files
export EL_RESULTS_FILE=$APP_HOME/evaluation/entity-linking/results/out.tsv
#export EL_RESULTS_FILE=/tmp/entity-linking-results-out.tsv

export EL_KBP_TRAIN_QUERY=$APP_HOME/data/entity-linking/kbp-competition/el_2010_train_queries.tsv
export EL_KBP_TRAIN_ENTITY=$APP_HOME/data/entity-linking/kbp-competition/el_2010_train_answers.tsv
export EL_KBP_EVAL_QUERY=$APP_HOME/data/entity-linking/kbp-competition/el_2010_eval_queries.tsv
export EID_TO_FID_FILE=$APP_HOME/data/entity-linking/kbp-competition/eid_to_fid.csv

# Pre-loaded data
export AUX_TABLES=$APP_HOME/data/entity-linking/el-tables/aux-tables.zip
export AUX_TABLES_DIR=$APP_HOME/data/entity-linking/el-tables/aux-tables
export ENTITY_TABLES=$APP_HOME/data/entity-linking/el-tables/entity-tables-other.zip
export ENTITY_TABLES_DIR=$APP_HOME/data/entity-linking/el-tables/entity-tables-other
export ENTITY_TABLES_WIKI=$APP_HOME/data/entity-linking/el-tables/entity-tables-wiki.zip
export ENTITY_TABLES_WIKI_DIR=$APP_HOME/data/entity-linking/el-tables/entity-tables-wiki
export MENTION_TABLES=$APP_HOME/data/entity-linking/el-tables/mention-tables.zip
export MENTION_TABLES_DIR=$APP_HOME/data/entity-linking/el-tables/mention-tables

# Additional relation extraction data
export RELATION_TYPE=$APP_HOME/data/relation-extraction/relation_types.csv
export INCOMPATIBLE_RELATION=$APP_HOME/data/relation-extraction/incompatible_relations.csv

# KBP knowledge base
export KBP_KB_FILE=$APP_HOME/data/kbp_knowledge_base.tsv 

# #
# # Run a small supervised classifier -- inteded to run in under 8GB of memory.
# #
# function trainSupervisedClassifierSmall() {
#   python $SCRIPT_DIR/scripts/supervisedClassifier.py --sentenceCSV=../data/annotated_sentences.csv.bz2 --sentenceProto=../data/delimitedSentences.proto.bz2 --trainSize=5000 --testSize=1000
# }

# #
# # Run the full supervised classifier.
# #
# function trainSupervisedClassifier() {
#   python $SCRIPT_DIR/scripts/supervisedClassifier.py --sentenceCSV=../data/annotated_sentences.csv.bz2 --sentenceProto=../data/delimitedSentences.proto.bz2
# }

# source "env/env_`whoami`.sh" > /dev/null || true
# source "env/env_zifei_large.sh" > /dev/null || true