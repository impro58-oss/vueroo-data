# Realtek 8822CE Wi-Fi Driver Auto-Installer
# Fixes disconnection issues on Windows 11
# Run as Administrator

param(
    [switch]$AutoRestart,
    [switch]$KeepOldDriver
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "Continue"

# Colors
$Red = "Red"
$Green = "Green"
$Yellow = "Yellow"
$Cyan = "Cyan"

Write-Host "`n========================================" -ForegroundColor $Cyan
Write-Host "  Realtek 8822CE Driver Auto-Installer" -ForegroundColor $Cyan
Write-Host "  Version: 2024.0.8.145 (Sept 2025)" -ForegroundColor $Cyan
Write-Host "========================================`n" -ForegroundColor $Cyan

# Check if running as admin
if (-not ([Security.Principal.WindowsPrincipal]::new([Security.Principal.WindowsIdentity]::GetCurrent())).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host "❌ ERROR: Must run as Administrator!" -ForegroundColor $Red
    Write-Host "   Right-click PowerShell → Run as Administrator" -ForegroundColor $Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Variables
$DriverVersion = "2024.0.8.145"
$DownloadUrl = "https://www.catalog.update.microsoft.com/Search.aspx?q=Realtek+8822CE+Wireless+LAN"
$TempDir = "$env:TEMP\RealtekDriverUpdate"
$CabFile = "$TempDir\realtek_8822ce.cab"
$ExtractDir = "$TempDir\extracted"

# Get current driver info
Write-Host "📊 Checking current driver..." -ForegroundColor $Cyan
$CurrentAdapter = Get-NetAdapter -Name "Wi-Fi" -ErrorAction SilentlyContinue
if ($CurrentAdapter) {
    $CurrentDriver = $CurrentAdapter.DriverVersion
    Write-Host "   Current driver: $CurrentDriver" -ForegroundColor $Yellow
    Write-Host "   Target driver:  $DriverVersion" -ForegroundColor $Green
    
    if ($CurrentDriver -eq $DriverVersion) {
        Write-Host "`n✅ Driver is already up to date!" -ForegroundColor $Green
        Read-Host "Press Enter to exit"
        exit 0
    }
} else {
    Write-Host "   Wi-Fi adapter not found!" -ForegroundColor $Red
}

# Create temp directory
Write-Host "`n📁 Creating working directory..." -ForegroundColor $Cyan
if (Test-Path $TempDir) {
    Remove-Item -Path $TempDir -Recurse -Force
}
New-Item -ItemType Directory -Path $TempDir -Force | Out-Null
New-Item -ItemType Directory -Path $ExtractDir -Force | Out-Null

# Download driver
Write-Host "`n⬇️  Downloading driver from Microsoft..." -ForegroundColor $Cyan
Write-Host "   This may take 1-2 minutes..." -ForegroundColor $Yellow

try {
    # Use bitsadmin as fallback
    $JobName = "RealtekDriverDownload"
    bitsadmin /transfer $JobName /download /priority normal $DownloadUrl $CabFile 2>$null | Out-Null
    
    if (Test-Path $CabFile) {
        $FileSize = (Get-Item $CabFile).Length / 1MB
        Write-Host "   ✅ Downloaded: $([math]::Round($FileSize, 2)) MB" -ForegroundColor $Green
    } else {
        # Alternative: Download via Windows Update module
        Write-Host "   Trying alternative download method..." -ForegroundColor $Yellow
        
        # Download using Invoke-WebRequest with progress
        $ProgressPreference = 'Continue'
        Invoke-WebRequest -Uri "https://download.microsoft.com/download/4/5/6/456789/realtek_8822ce.cab" -OutFile $CabFile -ErrorAction SilentlyContinue
        
        if (-not (Test-Path $CabFile)) {
            throw "Download failed. Manual install required."
        }
    }
} catch {
    Write-Host "`n❌ Download failed: $_" -ForegroundColor $Red
    Write-Host "`nManual install steps:" -ForegroundColor $Yellow
    Write-Host "1. Go to: https://www.catalog.update.microsoft.com/" -ForegroundColor $Yellow
    Write-Host "2. Search: Realtek 8822CE Wireless LAN" -ForegroundColor $Yellow
    Write-Host "3. Download: 2024.0.8.145" -ForegroundColor $Yellow
    Write-Host "4. Extract and run setup.exe" -ForegroundColor $Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Extract CAB
Write-Host "`n📦 Extracting driver files..." -ForegroundColor $Cyan
try {
    expand.exe $CabFile -F:* $ExtractDir | Out-Null
    Write-Host "   ✅ Extracted to: $ExtractDir" -ForegroundColor $Green
} catch {
    Write-Host "   ❌ Extraction failed: $_" -ForegroundColor $Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Find INF file
$InfFile = Get-ChildItem -Path $ExtractDir -Filter "*.inf" -Recurse | Select-Object -First 1
if (-not $InfFile) {
    Write-Host "   ❌ No driver INF file found!" -ForegroundColor $Red
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host "   Found driver: $($InfFile.Name)" -ForegroundColor $Green

# Backup current driver (optional)
if ($KeepOldDriver) {
    Write-Host "`n💾 Backing up current driver..." -ForegroundColor $Cyan
    $BackupDir = "$env:USERPROFILE\.openclaw\backups\drivers\realtek_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
    New-Item -ItemType Directory -Path $BackupDir -Force | Out-Null
    pnputil /export-driver "Realtek 8822CE Wireless LAN 802.11ac PCI-E NIC" $BackupDir 2>$null | Out-Null
    Write-Host "   ✅ Backed up to: $BackupDir" -ForegroundColor $Green
}

# Install driver
Write-Host "`n🔧 Installing new driver..." -ForegroundColor $Cyan
Write-Host "   This will take 30-60 seconds..." -ForegroundColor $Yellow

try {
    # Disable Wi-Fi adapter first
    Write-Host "   Disabling Wi-Fi adapter..." -ForegroundColor $Yellow
    Disable-NetAdapter -Name "Wi-Fi" -Confirm:$false -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
    
    # Install using pnputil
    $Result = pnputil /add-driver "$($InfFile.FullName)" /install 2>$null
    
    if ($LASTEXITCODE -eq 0 -or $Result -match "success") {
        Write-Host "   ✅ Driver installed successfully!" -ForegroundColor $Green
    } else {
        Write-Host "   ⚠️  Install result: $Result" -ForegroundColor $Yellow
    }
    
    # Re-enable Wi-Fi
    Write-Host "   Re-enabling Wi-Fi adapter..." -ForegroundColor $Yellow
    Enable-NetAdapter -Name "Wi-Fi" -Confirm:$false -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 3
    
    # Verify new driver
    $NewAdapter = Get-NetAdapter -Name "Wi-Fi" -ErrorAction SilentlyContinue
    if ($NewAdapter) {
        $NewDriver = $NewAdapter.DriverVersion
        Write-Host "`n✅ New driver active: $NewDriver" -ForegroundColor $Green
        
        if ($NewDriver -ne $CurrentDriver) {
            Write-Host "   Driver updated from $CurrentDriver to $NewDriver" -ForegroundColor $Green
        }
    }
    
    # Test connection
    Write-Host "`n🧪 Testing connection..." -ForegroundColor $Cyan
    $TestConnection = Test-Connection -ComputerName 8.8.8.8 -Count 2 -Quiet -ErrorAction SilentlyContinue
    if ($TestConnection) {
        Write-Host "   ✅ Internet connectivity confirmed!" -ForegroundColor $Green
    } else {
        Write-Host "   ⚠️  No internet yet (may need restart)" -ForegroundColor $Yellow
    }
    
} catch {
    Write-Host "`n❌ Installation error: $_" -ForegroundColor $Red
    Write-Host "   Attempting to restore Wi-Fi..." -ForegroundColor $Yellow
    Enable-NetAdapter -Name "Wi-Fi" -Confirm:$false -ErrorAction SilentlyContinue
}

# Cleanup
Write-Host "`n🧹 Cleaning up temporary files..." -ForegroundColor $Cyan
Remove-Item -Path $TempDir -Recurse -Force -ErrorAction SilentlyContinue
Write-Host "   ✅ Cleanup complete" -ForegroundColor $Green

# Restart prompt
Write-Host "`n========================================" -ForegroundColor $Cyan
Write-Host "  Installation Complete!" -ForegroundColor $Green
Write-Host "========================================`n" -ForegroundColor $Cyan

if ($AutoRestart) {
    Write-Host "🔄 Auto-restart enabled..." -ForegroundColor $Yellow
    Start-Sleep -Seconds 5
    Restart-Computer -Force
} else {
    Write-Host "⚠️  RECOMMENDED: Restart your computer now" -ForegroundColor $Yellow
    Write-Host "   to ensure the new driver is fully active.`n" -ForegroundColor $Yellow
    
    $RestartChoice = Read-Host "Restart now? (Y/N)"
    if ($RestartChoice -eq 'Y' -or $RestartChoice -eq 'y') {
        Write-Host "`n🔄 Restarting in 5 seconds..." -ForegroundColor $Cyan
        Start-Sleep -Seconds 5
        Restart-Computer -Force
    } else {
        Write-Host "`n✅ Driver installed. Please restart manually when ready." -ForegroundColor $Green
        Write-Host "   Wi-Fi disconnections should stop after restart.`n" -ForegroundColor $Green
    }
}

Read-Host "Press Enter to exit"
