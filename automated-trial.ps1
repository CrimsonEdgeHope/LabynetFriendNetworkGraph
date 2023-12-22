param(
    [Int32]$MaximumRequests=200,
    [String]$StartSpot="438a3459-9c60-4720-a07f-b36d7f14b84b",
    [Parameter()][ValidateSet("1", "2")][String]$CrawlingMethod="2",
    [Switch]$CrawlerDebug,
    [Switch]$PrintConfig
)

$CrawlerDebugStr = $CrawlerDebug.ToString().ToLower()

$configJson = "{
  `"maximum_requests`": $MaximumRequests,
  `"automate`": `"1`",
  `"crawling_method`": `"$CrawlingMethod`",
  `"start_spot`": `"$StartSpot`",
  `"debug`": $CrawlerDebugStr
}
"

if ($PrintConfig -eq $true) {
    Write-Output $configJson
    exit 0
}

Remove-Item -Recurse -Force -ErrorAction SilentlyContinue config.json
Set-Content config.json $configJson
Get-Content config.json

python --version
if ($? -ne $true) {
    throw "Python..."
}

Get-ChildItem .

python .\LabynetFriendNetworkGraph.py
if ($? -ne $true) {
    throw "Script execution failure..."
}
