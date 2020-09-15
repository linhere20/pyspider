#!/usr/bin/env bash
source ./_props_template.sh

if [[ $# != 3 ]] ; then
  echo "USAGE: $0 serverType serverNoStart serverNoEnd"
  exit 1;
fi

serverType=$1
serverNoStart=$2
serverNoEnd=$3

function createServer(){
  sType=$1
  sNo=$2
  sName=$1$2
  echo "start server: $NAME-$sName"

  docker container start ${NAME}-${sName}
}

for serverNo in $(seq ${serverNoStart} ${serverNoEnd})
do
 createServer ${serverType} ${serverNo} &
done

echo "waiting for start..."
wait
echo "all started"


