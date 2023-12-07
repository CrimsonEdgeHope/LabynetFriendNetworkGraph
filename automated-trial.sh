#!/usr/bin/env bash

rm -rf config.json

cat << EOF > config.json
{
  "maximum_requests": 250,
  "crawling_method": "1",
  "automate": "1",
  "start_spot": "7659cedb-c9c1-4f28-b966-19823fd8666b",
  "debug": true
}
EOF
cat config.json

python --version
if [ $? -ne 0 ]; then
  echo "Python..."
  exit 1
fi

ls -Alh

python ./LabynetFriendNetworkGraph.py
if [ $? -ne 0 ]; then
  echo "Script execution failure..."
  exit 1
fi
