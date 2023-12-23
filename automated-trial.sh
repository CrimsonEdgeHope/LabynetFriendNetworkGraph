#!/usr/bin/env bash

ARGS=$(getopt -a -o "" \
  --long maximum-requests:,start-spot:,crawling-method:,crawler-debug,print-config \
  -- "$@")

arg_maximum_requests=200
arg_start_spot="438a3459-9c60-4720-a07f-b36d7f14b84b"
arg_crawling_method="2"
arg_crawler_debug=false
arg_print_config=false

eval set -- "$ARGS"
while true ; do
  case "$1" in
    --maximum-requests)
      arg_maximum_requests=$2 ;
      shift 2 ;;
    --start-spot)
      arg_start_spot="$2" ;
      shift 2 ;;
    --crawling-method)
      arg_crawling_method="$2" ;
      shift 2 ;;
    --crawler-debug)
      arg_crawler_debug=true
      shift 1 ;;
    --print-config)
      arg_print_config=true
      shift 1 ;;
    --)
      shift 1 ;
      break ;;
    *)
      echo "Unknown directive $1" ;
      exit 1 ;;
  esac
done

if [[ ! $arg_maximum_requests =~ ^[0-9]+$ ]] ; then
  echo "$arg_maximum_requests"
  exit 1
fi

if [[ ! $arg_start_spot =~ ^[0-9a-z]{8}\-[0-9a-z]{4}\-[0-9a-z]{4}\-[0-9a-z]{4}\-[0-9a-z]{12}$ ]]; then
  echo "$arg_start_spot"
  exit 1
fi

if [[ $arg_crawling_method != "1" && $arg_crawling_method != "2" ]]; then
  echo "$arg_crawling_method"
  exit 1
fi

read -d '' configJson << EOF
{
  "automate": "1",
  "debug": $arg_crawler_debug,
  "crawler": {
    "maximum_requests": $arg_maximum_requests,
    "crawling_method": "$arg_crawling_method",
    "start_spot": "$arg_start_spot"
  }
}
EOF

if [ $arg_print_config == true ]; then
  echo $configJson
  exit 0
fi

rm -rf config.json
echo $configJson > config.json
cat config.json

python3 --version
if [ $? -ne 0 ]; then
  echo "Python..."
  exit 1
fi

ls -Alh

python3 ./LabynetFriendNetworkGraph.py
if [ $? -ne 0 ]; then
  echo "Script execution failure..."
  exit 1
fi
