# Add favicon to all HTML files in vueroo-portal
$PortalDir = "C:\Users\impro\.openclaw\workspace\vueroo-portal\public"

Get-ChildItem -Path $PortalDir -Recurse -Filter "*.html" | ForEach-Object {
    $content = Get-Content $_.FullName -Raw
    if ($content -notmatch 'favicon') {
        $content = $content -replace '(<title>[^<]+</title>)', "`$1`n    <link rel=`"icon`" type=`"image/x-icon`" href=`"/favicon.ico`">"
        Set-Content $_.FullName $content
        Write-Host "Added favicon to: $($_.FullName.Replace($PortalDir, ''))"
    }
}

Write-Host "Done!"
