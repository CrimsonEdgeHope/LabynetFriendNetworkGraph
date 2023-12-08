#!/usr/bin/env bash

if [ -d result ]; then
  ls -Alh result
else
  echo "Where's result directory?"
  exit 1
fi

IFS=$'\r\n'
mark=true

cd result
r=$(ls --ignore config.json *.json)
cd ..
for i in $r ; do
  python3 result_json_lint.py "$i"
  if [ $? -ne 0 ]; then
    echo "Failure at $i"
    mark=false
  fi
done

if [ $mark = false ]; then
  echo "Check unsuccessful."
  exit 1
fi
