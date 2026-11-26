Get-ChildItem -Recurse -Filter *.html | ForEach-Object {
    $file = $_.FullName
    $content = Get-Content -Path $file -Raw
    $new = $content -replace '"logo"\s*:\s*"[^"]+"', '"logo":"/assets/logo.svg"'
    if ($new -ne $content) {
        Set-Content -Path $file -Value $new -Encoding utf8
        Write-Host "Updated $file"
    }
}
