# Daily Memory Backup Script
# Backs up all memory files to GitHub and local archive
# Schedule: Daily at 23:00

param(
    [string]$WorkingDir = "C:\Users\impro\.openclaw\workspace",
    [string]$GitPath = "C:\Program Files\Git\bin\git.exe",
    [string]$BackupDir = "C:\Users\impro\OneDrive\OpenClaw\backups"
)

# Setup paths
$MemoryDir = "$WorkingDir\memory"
$LogDir = "$WorkingDir\logs"
$LogFile = "$LogDir\memory-backup-$(Get-Date -Format 'yyyyMM').log"

# Ensure directories exist
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
New-Item -ItemType Directory -Force -Path $BackupDir | Out-Null

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogEntry = "$Timestamp [$Level] $Message"
    Write-Host $LogEntry
    Add-Content -Path $LogFile -Value $LogEntry -Encoding UTF8
}

Write-Log "=== Daily Memory Backup Started ==="

# Change to working directory
Set-Location $WorkingDir

# ========== STEP 1: Local Archive Backup ==========
Write-Log "Creating local archive backup..."

$DateStamp = Get-Date -Format "yyyy-MM-dd"
$ArchiveName = "memory-backup-$DateStamp.zip"
$ArchivePath = "$BackupDir\$ArchiveName"

try {
    if (Test-Path $MemoryDir) {
        Compress-Archive -Path "$MemoryDir\*" -DestinationPath $ArchivePath -Force
        Write-Log "Archive created: $ArchivePath" "OK"
        
        # Cleanup old archives (keep last 30 days)
        Get-ChildItem -Path $BackupDir -Filter "memory-backup-*.zip" | 
            Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-30) } |
            Remove-Item -Force
        Write-Log "Cleaned up archives older than 30 days" "OK"
    } else {
        Write-Log "Memory directory not found: $MemoryDir" "ERROR"
    }
} catch {
    Write-Log "Archive backup failed: $_" "ERROR"
}

# ========== STEP 2: GitHub Backup ==========
Write-Log "Committing memory files to GitHub..."

try {
    # Check if git is available
    if (-not (Test-Path $GitPath)) {
        throw "Git not found at $GitPath"
    }

    # Configure git
    & $GitPath config --local user.email "roo@rooquest.local" 2>$null
    & $GitPath config --local user.name "Roo Memory Backup" 2>$null

    # Stage memory files
    & $GitPath add memory/ 2>$null
    & $GitPath add MEMORY.md 2>$null
    & $GitPath add HEARTBEAT.md 2>$null
    & $GitPath add ACTIVE.md 2>$null

    # Check if there's anything staged
    $Staged = & $GitPath diff --cached --name-only 2>$null

    if ($Staged) {
        $FileCount = ($Staged | Measure-Object).Count
        $CommitMsg = "Daily memory backup: $DateStamp ($FileCount files)"
        
        & $GitPath commit -m $CommitMsg 2>$null | Out-Null
        & $GitPath push origin master 2>$null | Out-Null
        
        if ($LASTEXITCODE -eq 0) {
            $CommitHash = (& $GitPath rev-parse --short HEAD 2>$null)
            Write-Log "GitHub backup successful. Commit: $CommitHash" "OK"
        } else {
            Write-Log "GitHub push failed" "ERROR"
        }
    } else {
        Write-Log "No memory changes to commit" "INFO"
    }
} catch {
    Write-Log "GitHub backup failed: $_" "ERROR"
}

# ========== STEP 3: Summary Report ==========
Write-Log "=== Memory Backup Complete ==="

# Count files backed up
$MemoryFiles = Get-ChildItem -Path $MemoryDir -File -Recurse -ErrorAction SilentlyContinue
$MemorySize = ($MemoryFiles | Measure-Object -Property Length -Sum).Sum / 1MB
$FileCount = $MemoryFiles.Count

Write-Log "Memory files backed up: $FileCount"
Write-Log "Total size: $([math]::Round($MemorySize, 2)) MB"
Write-Log "Archive location: $ArchivePath"
Write-Log "GitHub repo: https://github.com/impro58-oss/rooquest1"

# Create status file for monitoring
$StatusFile = "$WorkingDir\memory\backup-status.json"
$StatusData = @{
    last_backup = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    files_backed_up = $FileCount
    total_size_mb = [math]::Round($MemorySize, 2)
    archive_path = $ArchivePath
    github_commit = $CommitHash
    status = "success"
} | ConvertTo-Json

$StatusData | Out-File -FilePath $StatusFile -Encoding UTF8

Write-Log "Status written to: $StatusFile"
Write-Log "=== Backup Finished ==="
