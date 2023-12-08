#!/usr/bin/env bash
rm -rf "action7096370784.zip"
rm -rf "action7096370784"

wget -O "action7096370784.zip" "https://github.com/CrimsonEdgeHope/LabynetFriendNetworkGraph/releases/download/beta-0.1.2/ActionRun-No-7096370784-Artifact-Result-windows-2022.zip"

unzip -o -q "action7096370784.zip" -d "action7096370784"

ls -Alh "action7096370784"
ls -Alh "action7096370784/result"

cp -r "action7096370784/result" "./"
rm -rf "config.json"

cat << EOF > "config.json"
{
  "automate": "2",
  "import_json": "2023-12-05-05-38-13.json"
}
EOF

cat "config.json"

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
