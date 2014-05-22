#! /bin/bash

source "$APP_HOME/env_db.sh"

if [ -f $DEEPDIVE_HOME/sbt/sbt ]; then
  echo "DeepDive $DEEPDIVE_HOME"
else
  echo "[ERROR] Could not find sbt in $DEEPDIVE_HOME!"
  exit 1
fi

cd $DEEPDIVE_HOME
env $DEEPDIVE_HOME/sbt/sbt "run -c $APP_HOME/application.conf"