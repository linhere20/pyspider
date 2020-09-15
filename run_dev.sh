if [[ $# != 1 ]] ; then
  echo "USAGE: $0 spider-type"
  exit 1;
fi

python3 app.py --env=dev --type=$1 --name=spider