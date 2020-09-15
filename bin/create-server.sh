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
  echo "create server: $NAME-$sName"

  docker container create\
    --name ${NAME}-${sName}\
    -m ${SERVER_MEM}\
    -v "$PWD/../":/app\
    -v "$PWD/../../logs":/app/logs\
    -v "$PWD/../../vfs":/app/vfs\
    -v /etc/localtime:/etc/localtime\
    pyspider:latest --env=prod --type=${sType} --name=${sNo}
}

for serverNo in $(seq ${serverNoStart} ${serverNoEnd})
do
 createServer ${serverType} ${serverNo} &
done

echo "waiting for create..."
wait
echo "all created"

