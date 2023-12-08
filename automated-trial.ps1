Remove-Item -Recurse -Force -ErrorAction SilentlyContinue config.json
Set-Content config.json '{
  "maximum_requests": 200,
  "automate": "1",
  "start_spot": "438a3459-9c60-4720-a07f-b36d7f14b84b",
  "debug": true
}'
Get-Content config.json

python --version
if ($? -ne $true) {
    Write-Output "Python..."
    exit 1
}

Get-ChildItem .

python .\LabynetFriendNetworkGraph.py
if ($? -ne $true) {
    Write-Output "Script execution failure..."
    exit 1
}
