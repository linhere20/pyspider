#!/usr/bin/env bash
source ./_props_template.sh

ACTION=$1

case ${ACTION} in
  'create'|'remove'|'stop')
    bash ${ACTION}-server.sh py 0 `expr ${KWAI_SPIDER_AMOUNT} - 1`
    bash ${ACTION}-server.sh xinkuai 0 `expr ${XINKUAI_SPIDER_AMOUNT} - 1`
  ;;
  'start')
    bash ${ACTION}-server.sh py 0 `expr ${KWAI_SPIDER_AMOUNT} - 1`
    bash ${ACTION}-server.sh xinkuai 0 `expr ${XINKUAI_SPIDER_AMOUNT} - 1`
  ;;
  *)
  echo 'action error'
esac
