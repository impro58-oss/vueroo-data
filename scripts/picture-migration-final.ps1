# Picture Migration Script - D to E with Structure Preservation
# Preserves exact folder hierarchy, handles conflicts by appending numbers

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
    $_.Extension -match '\.(jpg|jpeg|png|gif|bmp|tiff|tif|mov|avi|mp4|m4v|3gp|wmv|wav|mp3|pdf|heic|raw|cr2|nef|psd|aae)$'
}

$totalSource = $sourceFiles.Count
Write-Log "Found $totalSource media files in source" "INFO"

# Build destination file index for quick lookup
Write-Log "Building destination file index..." "INFO"
$destFiles = Get-ChildItem -Path $DestPath -Recurse -File -ErrorAction SilentlyContinue | Where-Object {
    $_.Extension -match '\.(jpg|jpeg|png|gif|bmp|tiff|tif|mov|avi|mp4|m4v|3gp|wmv|wav|mp3|pdf|heic|raw|cr2|nef|psd|aae)$'
}

# Create hash table of destination files: "folder\filename" -> file info
$destIndex = @{}
foreach ($file in $destFiles) {
    $relativePath = $file.FullName.Substring($DestPath.Length).TrimStart('\', '/')
    $key = $relativePath.ToLower()
    if (-not $destIndex.ContainsKey($key)) {
        $destIndex[$key] = $file
    }
}

Write-Log "Found $($destFiles.Count) files in destination" "INFO"
Write-Log ""

# Compare and identify files to copy
Write-Log "Comparing files..." "INFO"
$filesToCopy = @()
$alreadyExist = 0
$conflicts = 0

foreach ($sourceFile in $sourceFiles) {
    # Calculate relative path from source root
    $relativePath = $sourceFile.FullName.Substring($SourcePath.Length).TrimStart('\', '/')
    $key = $relativePath.ToLower()
    
    if ($destIndex.ContainsKey($key)) {
        $destFile = $destIndex[$key]
        if ($sourceFile.Length -eq $destFile.Length) {
            # Same file (name and size match)
            $alreadyExist++
        } else {
            # Conflict: same name, different size
            $conflicts++
            $filesToCopy += @{
                Source = $sourceFile
                RelativePath = $relativePath
                Conflict = $true
                DestSize = $destFile.Length
            }
        }
    } else {
        # New file
        $filesToCopy += @{
            Source = $sourceFile
            RelativePath = $relativePath
            Conflict = $false
        }
    }
}

$totalToCopy = $filesToCopy.Count
$totalSize = ($filesToCopy | ForEach-Object { $_.Source.Length } | Measure-Object -Sum).Sum
$totalSizeGB = [math]::Round($totalSize / 1GB, 2)

Write-Log ""
Write-Log "=== COMPARISON RESULTS ===" "INFO"
Write-Log "Total source files: $totalSource" "INFO"
Write-Log "Already exist (duplicates): $alreadyExist" "INFO"
Write-Log "Conflicts (same name, different size): $conflicts" "WARN"
Write-Log "Files to copy: $totalToCopy" "INFO"
Write-Log "Total size to copy: $totalSizeGB GB" "INFO"
Write-Log ""

if ($totalToCopy -eq 0) {
    Write-Log "No files to copy! All files already exist in destination." "INFO"
    exit 0
}

# Auto-confirm (no interactive prompt)
Write-Log "Auto-confirming migration of $totalToCopy files ($totalSizeGB GB)" "INFO"
Write-Log "Starting in 5 seconds..." "INFO"
Start-Sleep -Seconds 5

# Copy files with progress
Write-Log "Starting copy operation..." "INFO"
$successCount = 0
$errorCount = 0
$conflictRenamed = 0
$currentFile = 0

foreach ($item in $filesToCopy) {
    $currentFile++
    $percentComplete = [math]::Round(($currentFile / $totalToCopy) * 100, 1)
    $sourceFile = $item.Source
    $relativePath = $item.RelativePath
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
    
    # Handle conflicts by appending number
    if ($item.Conflict) {
        $fileName = [System.IO.Path]::GetFileNameWithoutExtension($relativePath)
        $extension = [System.IO.Path]::GetExtension($relativePath)
        $counter = 1
        $newPath = $destFilePath
        
        while (Test-Path $newPath) {
            $newFileName = "${fileName}_${counter}${extension}"
            $newPath = Join-Path $destDir $newFileName
            $counter++
        }
        
        $destFilePath = $newPath
        $conflictRenamed++
        Write-Log "[$currentFile/$totalToCopy] RENAMED (conflict): $relativePath -> $(Split-Path -Leaf $newPath)" "WARN"
    }
    
    # Copy file
    try {
        Copy-Item -Path $sourceFile.FullName -Destination $destFilePath -Force -ErrorAction Stop
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
Write-Log "Conflicts renamed: $conflictRenamed" "INFO"
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
- Conflicts renamed: $conflictRenamed
- Copied: $successCount
- Errors: $errorCount

Log file: $LogFile
"@ | Out-File -FilePath $summaryFile -Encoding UTF8

Write-Log "Summary saved to: $summaryFile" "INFO"

# Also create a simple list of what was moved
$movedListFile = "$env:TEMP\picture-migration-moved-files.txt"
$filesToCopy | ForEach-Object { 
    if ($_.Conflict) {
        "$($_.RelativePath) [CONFLICT - renamed]"
    } else {
        $_.RelativePath
    }
} | Out-File -FilePath $movedListFile -Encoding UTF8

Write-Log "Moved files list: $movedListFile" "INFO"
