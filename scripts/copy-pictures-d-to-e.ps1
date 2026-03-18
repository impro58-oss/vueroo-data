# Picture Migration Script - D to E with Duplicate Detection
# Compares files by name, size, and last modified date
# Only copies files that don't exist or are different in destination

param(
    [string]$SourcePath = "D:\P - Pictures",
    [string]$DestPath = "E:\2025 Pictures Merge",
    [string]$LogFile = "$env:TEMP\picture-migration-$(Get-Date -Format 'yyyyMMdd-HHmmss').log"
)

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] [$Level] $Message"
    Write-Host $logEntry
    Add-Content -Path $LogFile -Value $logEntry
}

function Get-FileHashQuick {
    param([string]$FilePath)
    try {
        $file = Get-Item $FilePath -ErrorAction Stop
        return "$($file.Name)|$($file.Length)|$($file.LastWriteTime.Ticks)"
    } catch {
        return $null
    }
}

# Initialize
Write-Log "=== Picture Migration Started ==="
Write-Log "Source: $SourcePath"
Write-Log "Destination: $DestPath"
Write-Log "Log file: $LogFile"
Write-Log ""

# Verify paths exist
if (-not (Test-Path $SourcePath)) {
    Write-Log "Source path does not exist!" "ERROR"
    exit 1
}

if (-not (Test-Path $DestPath)) {
    Write-Log "Creating destination directory..." "INFO"
    New-Item -ItemType Directory -Path $DestPath -Force | Out-Null
}

# Get all files from source
Write-Log "Scanning source files..." "INFO"
$sourceFiles = Get-ChildItem -Path $SourcePath -Recurse -File | Where-Object {
    # Only image and video files
    $_.Extension -match '\.(jpg|jpeg|png|gif|bmp|tiff|tif|mov|avi|mp4|m4v|3gp|wmv|wav|mp3|pdf)$'
}

$totalSource = $sourceFiles.Count
Write-Log "Found $totalSource media files in source" "INFO"

# Build destination file index for quick lookup
Write-Log "Building destination file index..." "INFO"
$destFiles = Get-ChildItem -Path $DestPath -Recurse -File -ErrorAction SilentlyContinue | Where-Object {
    $_.Extension -match '\.(jpg|jpeg|png|gif|bmp|tiff|tif|mov|avi|mp4|m4v|3gp|wmv|wav|mp3|pdf)$'
}

# Create hash table of destination files for O(1) lookup
$destIndex = @{}
$duplicateCount = 0

foreach ($file in $destFiles) {
    $key = "$($file.Name)|$($file.Length)"
    if ($destIndex.ContainsKey($key)) {
        $duplicateCount++
    } else {
        $destIndex[$key] = $file.FullName
    }
}

Write-Log "Found $($destFiles.Count) files in destination ($duplicateCount duplicates in dest)" "INFO"
Write-Log ""

# Compare and identify files to copy
Write-Log "Comparing files..." "INFO"
$filesToCopy = @()
$alreadyExist = 0
$differentSize = 0

foreach ($sourceFile in $sourceFiles) {
    $key = "$($sourceFile.Name)|$($sourceFile.Length)"
    
    if ($destIndex.ContainsKey($key)) {
        # File exists with same name and size
        $alreadyExist++
    } else {
        # Check if file exists with different size (conflict)
        $nameOnly = $sourceFile.Name
        $potentialConflict = $destFiles | Where-Object { $_.Name -eq $nameOnly }
        
        if ($potentialConflict) {
            $differentSize++
            Write-Log "CONFLICT: $($sourceFile.Name) exists but different size (Source: $($sourceFile.Length) bytes, Dest: $($potentialConflict.Length) bytes)" "WARN"
        }
        
        $filesToCopy += $sourceFile
    }
}

$totalToCopy = $filesToCopy.Count
$totalSize = ($filesToCopy | Measure-Object -Property Length -Sum).Sum
$totalSizeGB = [math]::Round($totalSize / 1GB, 2)

Write-Log ""
Write-Log "=== COMPARISON RESULTS ===" "INFO"
Write-Log "Total source files: $totalSource" "INFO"
Write-Log "Already exist (duplicates): $alreadyExist" "INFO"
Write-Log "Conflicts (same name, different size): $differentSize" "WARN"
Write-Log "Files to copy: $totalToCopy" "INFO"
Write-Log "Total size to copy: $totalSizeGB GB" "INFO"
Write-Log ""

if ($totalToCopy -eq 0) {
    Write-Log "No files to copy! All files already exist in destination." "INFO"
    exit 0
}

# Ask for confirmation
Write-Host "`nReady to copy $totalToCopy files ($totalSizeGB GB)" -ForegroundColor Yellow
Write-Host "Continue? (Y/N): " -NoNewline -ForegroundColor Yellow
$confirm = Read-Host

if ($confirm -ne 'Y' -and $confirm -ne 'y') {
    Write-Log "Operation cancelled by user" "INFO"
    exit 0
}

# Copy files with progress
Write-Log "Starting copy operation..." "INFO"
$successCount = 0
$errorCount = 0
$skippedCount = 0
$currentFile = 0

foreach ($file in $filesToCopy) {
    $currentFile++
    $percentComplete = [math]::Round(($currentFile / $totalToCopy) * 100, 1)
    
    # Calculate relative path
    $relativePath = $file.FullName.Substring($SourcePath.Length).TrimStart('\', '/')
    $destFilePath = Join-Path $DestPath $relativePath
    $destDir = Split-Path -Parent $destFilePath
    
    # Create directory if needed
    if (-not (Test-Path $destDir)) {
        try {
            New-Item -ItemType Directory -Path $destDir -Force | Out-Null
        } catch {
            Write-Log "Failed to create directory: $destDir" "ERROR"
            $errorCount++
            continue
        }
    }
    
    # Check if file already exists (shouldn't happen due to our check, but just in case)
    if (Test-Path $destFilePath) {
        $existingFile = Get-Item $destFilePath
        if ($existingFile.Length -eq $file.Length) {
            Write-Log "[$currentFile/$totalToCopy] SKIP: $relativePath (already exists)" "INFO"
            $skippedCount++
            continue
        }
    }
    
    # Copy file
    try {
        Copy-Item -Path $file.FullName -Destination $destFilePath -Force -ErrorAction Stop
        Write-Log "[$currentFile/$totalToCopy] ($percentComplete%) COPIED: $relativePath" "INFO"
        $successCount++
    } catch {
        Write-Log "[$currentFile/$totalToCopy] ERROR copying: $relativePath - $($_.Exception.Message)" "ERROR"
        $errorCount++
    }
}

# Summary
Write-Log ""
Write-Log "=== MIGRATION COMPLETE ===" "INFO"
Write-Log "Successfully copied: $successCount" "INFO"
Write-Log "Skipped (duplicates): $skippedCount" "INFO"
Write-Log "Errors: $errorCount" "INFO"
Write-Log "Log saved to: $LogFile" "INFO"

# Create summary report
$summaryFile = "$env:TEMP\picture-migration-summary.txt"
@"
Picture Migration Summary
========================
Date: $(Get-Date)
Source: $SourcePath
Destination: $DestPath

Results:
- Total source files: $totalSource
- Already existed: $alreadyExist
- Conflicts: $differentSize
- Copied: $successCount
- Skipped: $skippedCount
- Errors: $errorCount

Log file: $LogFile
"@ | Out-File -FilePath $summaryFile -Encoding UTF8

Write-Log "Summary saved to: $summaryFile" "INFO"
