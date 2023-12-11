if (-Not $(Test-Path -Path "result")) {
    Write-Output "Where's result directory?"
    exit 1
}

Get-ChildItem -Path "result\*.json" -OutVariable jsonitems

$mark = $true
foreach ($item in $jsonitems) {
    python .\result_json_lint.py  $item.Name
    if ($? -ne $true) {
        Write-Output "Failure at $item"
        $mark = $false
    } else {
        python .\result_json.py  $item.Name
        Write-Output "Attempt to write CQL for $item"
        python .\result_json_to_neo4j_cql.py  $item.Name
    }
}
if (-Not $mark) {
    Write-Output "Check unsuccessful."
    exit 1
}
