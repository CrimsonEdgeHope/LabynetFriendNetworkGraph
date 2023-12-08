Remove-Item -Recurse -Force -ErrorAction SilentlyContinue "action7096370784.zip"
Remove-Item -Recurse -Force -ErrorAction SilentlyContinue "action7096370784"

Invoke-WebRequest -Verbose -OutFile "action7096370784.zip" "https://github.com/CrimsonEdgeHope/LabynetFriendNetworkGraph/releases/download/beta-0.1.2/ActionRun-No-7096370784-Artifact-Result-ubuntu-2204.zip"

Expand-Archive -Force -Path "action7096370784.zip"
Get-ChildItem "action7096370784"
Get-ChildItem "action7096370784\result"

Copy-Item -Recurse -Force -Verbose -Path "action7096370784\result" -Destination "."

Remove-Item -Recurse -Force -ErrorAction SilentlyContinue config.json
Set-Content config.json '{
  "automate": "2",
  "import_json": "2023-12-05-05-05-57.json"
}'
Get-Content config.json

python --version
if ($LASTEXITCODE -ne 0) {
    Write-Output "Python..."
    exit 1
}

Get-ChildItem .

python .\LabynetFriendNetworkGraph.py
if ($LASTEXITCODE -ne 0) {
    Write-Output "Script execution failure..."
    exit 1
}
