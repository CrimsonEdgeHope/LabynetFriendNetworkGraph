Remove-Item -Force:$true -Confirm:$false config.json
Set-Content config.json '{
  "maximum_requests": 5,
  "automate": "1",
  "start_spot": "4605642a-a8cb-4048-b24f-fafcce1993d2",
  "debug": true
}'
Get-Content config.json
if ($LASTEXITCODE -ne 0) {
    Write-Output "Where's config.json?"
    exit 1
}

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
