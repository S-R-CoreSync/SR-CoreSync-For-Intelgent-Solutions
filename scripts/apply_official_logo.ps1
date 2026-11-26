$files = Get-ChildItem -Path (Get-Location) -Recurse -Filter *.html
$updated = 0
foreach ($f in $files) {
    $content = Get-Content -Path $f.FullName -Raw -ErrorAction SilentlyContinue
    if (-not $content) { continue }
    $orig = $content

    # Replace old official/luxury emblem paths with /assets/logo-official.jpg
    $content = $content -replace '\.?/?assets/sr-core-emblem-official(?:-\d+w)?\.(?:webp|png|jpg)', '/assets/logo-official.jpg'
    $content = $content -replace '\.?/?assets/sr-emblem-gold-luxury(?:-\d+w|-4k)?\.(?:webp|png|jpg)', '/assets/logo-official.jpg'
    $content = $content -replace 'srcset="[^"]*logo-official\.jpg[^"]*"', 'srcset="/assets/logo-official.jpg"'

    if ($content -ne $orig) {
        Set-Content -Path $f.FullName -Value $content -Encoding utf8
        $updated++
    }
}
Write-Host "Updated $updated HTML files with /assets/logo-official.jpg"
