#!/usr/bin/env bash

rm -rf config.json

cat << EOF > config.json
{
  "maximum_requests": 5,
  "automate": "1",
  "start_spot": "4605642a-a8cb-4048-b24f-fafcce1993d2",
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
