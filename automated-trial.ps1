Remove-Item -Force:$true -Confirm:$false -ErrorAction SilentlyContinue config.json
Set-Content config.json '{
  "maximum_requests": 5,
  "automate": "1",
  "start_spot": "f88a6873-452f-428e-b138-76f682a3cfb4",
  "debug": true
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
