Remove-Item -Force -ErrorAction SilentlyContinue config.json
Set-Content config.json '{
  "maximum_requests": 1000,
  "automate": "1",
  "start_spot": "22500b81-e889-4367-b83c-24c52914e2de"
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
