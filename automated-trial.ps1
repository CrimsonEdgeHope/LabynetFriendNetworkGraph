Remove-Item -Force:$true -Confirm:$false -ErrorAction SilentlyContinue config.json
Set-Content config.json '{
  "maximum_requests": 1000,
  "automate": "1",
  "start_spot": "22500b81-e889-4367-b83c-24c52914e2de",
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
