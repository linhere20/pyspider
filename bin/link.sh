#!/usr/bin/env bash
source ./_props_template.sh

docker container exec -it ${NAME}-$1 /bin/bash

