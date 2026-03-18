# Quick Picture Scan - D to E Migration Analysis
# Fast scan to report what needs to be moved

param(
    [string]$SourcePath = "D:\P - Pictures",
    [string]$DestPath = "E:\2025 Pictures Merge"
)

Write-Host "=== QUICK PICTURE MIGRATION SCAN ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Source: $SourcePath" -ForegroundColor Yellow
Write-Host "Destination: $DestPath" -ForegroundColor Yellow
Write-Host ""

# Check paths
if (-not (Test-Path $SourcePath)) {
    Write-Host "ERROR: Source path does not exist!" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path $DestPath)) {
    Write-Host "Creating destination directory..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $DestPath -Force | Out-Null
}

# Quick file count (first level only for speed)
Write-Host "Scanning source folders..." -ForegroundColor Cyan
$sourceFolders = Get-ChildItem -Path $SourcePath -Directory
$sourceFileCount = 0
$sourceSize = 0

foreach ($folder in $sourceFolders) {
    $files = Get-ChildItem -Path $folder.FullName -Recurse -File -ErrorAction SilentlyContinue | 
        Where-Object { $_.Extension -match '\.(jpg|jpeg|png|gif|bmp|tiff|tif|mov|avi|mp4|m4v|3gp|wmv|heic|raw|cr2|nef|psd)$' }
    $count = $files.Count
    $size = ($files | Measure-Object -Property Length -Sum).Sum
    $sizeGB = [math]::Round($size / 1GB, 2)
    $sourceFileCount += $count
    $sourceSize += $size
    Write-Host "  $($folder.Name): $count files ($sizeGB GB)" -ForegroundColor Gray
}

Write-Host ""
Write-Host "Scanning destination..." -ForegroundColor Cyan
$destFiles = Get-ChildItem -Path $DestPath -Recurse -File -ErrorAction SilentlyContinue | 
    Where-Object { $_.Extension -match '\.(jpg|jpeg|png|gif|bmp|tiff|tif|mov|avi|mp4|m4v|3gp|wmv|heic|raw|cr2|nef|psd)$' }
$destFileCount = $destFiles.Count
$destSize = ($destFiles | Measure-Object -Property Length -Sum).Sum

# Summary
$sourceSizeGB = [math]::Round($sourceSize / 1GB, 2)
$destSizeGB = [math]::Round($destSize / 1GB, 2)
$diffCount = $sourceFileCount - $destFileCount
$diffSizeGB = [math]::Round(($sourceSize - $destSize) / 1GB, 2)

Write-Host ""
Write-Host "=== SCAN RESULTS ===" -ForegroundColor Green
Write-Host "Source files: $sourceFileCount ($sourceSizeGB GB)" -ForegroundColor White
Write-Host "Destination files: $destFileCount ($destSizeGB GB)" -ForegroundColor White
Write-Host ""
Write-Host "Files to migrate: $diffCount (~$diffSizeGB GB)" -ForegroundColor Yellow
Write-Host ""

# Sample of folders that likely need syncing
Write-Host "=== FOLDERS LIKELY NEEDING SYNC ===" -ForegroundColor Cyan
$destFolderNames = (Get-ChildItem -Path $DestPath -Directory -ErrorAction SilentlyContinue).Name

foreach ($folder in $sourceFolders) {
    if ($destFolderNames -notcontains $folder.Name) {
        Write-Host "  MISSING: $($folder.Name)" -ForegroundColor Red
    } else {
        $srcCount = (Get-ChildItem -Path $folder.FullName -Recurse -File -ErrorAction SilentlyContinue | 
            Where-Object { $_.Extension -match '\.(jpg|jpeg|png|gif|bmp|tiff|tif|mov|avi|mp4|m4v|3gp|wmv|heic|raw|cr2|nef|psd)$' }).Count
        $destFolder = Join-Path $DestPath $folder.Name
        $dstCount = (Get-ChildItem -Path $destFolder -Recurse -File -ErrorAction SilentlyContinue | 
            Where-Object { $_.Extension -match '\.(jpg|jpeg|png|gif|bmp|tiff|tif|mov|avi|mp4|m4v|3gp|wmv|heic|raw|cr2|nef|psd)$' }).Count
        
        if ($srcCount -ne $dstCount) {
            Write-Host "  DIFFERENT: $($folder.Name) (Source: $srcCount, Dest: $dstCount)" -ForegroundColor Yellow
        }
    }
}

Write-Host ""
Write-Host "Scan complete. Ready to proceed with migration?" -ForegroundColor Green
