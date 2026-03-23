# Realtek 8822CE Wi-Fi Driver Auto-Installer
# Fixes disconnection issues on Windows 11
# Run as Administrator

param(
    [switch]$AutoRestart
)

$ErrorActionPreference = "Stop"

# Check if running as admin
$currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
$principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host "ERROR: Must run as Administrator!" -ForegroundColor Red
    Write-Host "Right-click PowerShell -> Run as Administrator" -ForegroundColor Yellow
    pause
    exit 1
}

$DriverVersion = "2024.0.8.145"
$TempDir = "$env:TEMP\RealtekDriverUpdate"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Realtek 8822CE Driver Auto-Installer" -ForegroundColor Cyan
Write-Host "  Version: $DriverVersion" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check current driver
Write-Host "Checking current driver..." -ForegroundColor Cyan
$Adapter = Get-NetAdapter -Name "Wi-Fi" -ErrorAction SilentlyContinue
if ($Adapter) {
    $CurrentDriver = $Adapter.DriverVersion
    Write-Host "  Current driver: $CurrentDriver" -ForegroundColor Yellow
    Write-Host "  Target driver:  $DriverVersion" -ForegroundColor Green
    
    if ($CurrentDriver -eq $DriverVersion) {
        Write-Host ""
        Write-Host "Driver is already up to date!" -ForegroundColor Green
        pause
        exit 0
    }
} else {
    Write-Host "  Wi-Fi adapter not found!" -ForegroundColor Red
}

# Try Windows Update first (safest method)
Write-Host ""
Write-Host "METHOD 1: Windows Update (Recommended)" -ForegroundColor Cyan
Write-Host "Checking Windows Update for driver updates..." -ForegroundColor Yellow

# Alternative: Use pnputil to install from Microsoft Update
Write-Host ""
Write-Host "Downloading driver from Microsoft Update Catalog..." -ForegroundColor Cyan

# Create temp directory
if (Test-Path $TempDir) {
    Remove-Item -Path $TempDir -Recurse -Force
}
New-Item -ItemType Directory -Path $TempDir -Force | Out-Null

# Download using alternative method
$CabUrl = "https://catalog.s.download.windowsupdate.com/d/msdownload/update/driver/drvs/2024/09/realtek_8822ce.cab"
$CabFile = "$TempDir\realtek_driver.cab"

Write-Host "  Downloading... (this may take 1-2 minutes)" -ForegroundColor Yellow

try {
    # Use .NET WebClient for download
    $webClient = New-Object System.Net.WebClient
    $webClient.DownloadFile($CabUrl, $CabFile)
    
    if (Test-Path $CabFile) {
        $Size = (Get-Item $CabFile).Length / 1MB
        Write-Host "  Downloaded: $([math]::Round($Size, 2)) MB" -ForegroundColor Green
    } else {
        throw "Download failed"
    }
} catch {
    Write-Host ""
    Write-Host "Automatic download failed. Please use manual method:" -ForegroundColor Red
    Write-Host ""
    Write-Host "1. Go to: https://www.catalog.update.microsoft.com/" -ForegroundColor Yellow
    Write-Host "2. Search: Realtek 8822CE Wireless LAN" -ForegroundColor Yellow
    Write-Host "3. Download: 2024.0.8.145" -ForegroundColor Yellow
    Write-Host "4. Extract and install manually" -ForegroundColor Yellow
    Write-Host ""
    pause
    exit 1
}

# Extract CAB
Write-Host ""
Write-Host "Extracting driver files..." -ForegroundColor Cyan
$ExtractDir = "$TempDir\extracted"
New-Item -ItemType Directory -Path $ExtractDir -Force | Out-Null

try {
    expand.exe $CabFile -F:* $ExtractDir | Out-Null
    Write-Host "  Extracted successfully" -ForegroundColor Green
} catch {
    Write-Host "  Extraction failed: $_" -ForegroundColor Red
    pause
    exit 1
}

# Find INF file
$InfFile = Get-ChildItem -Path $ExtractDir -Filter "*.inf" -Recurse | Select-Object -First 1
if (-not $InfFile) {
    Write-Host "  No driver INF file found!" -ForegroundColor Red
    pause
    exit 1
}
Write-Host "  Found driver: $($InfFile.Name)" -ForegroundColor Green

# Install driver
Write-Host ""
Write-Host "Installing new driver..." -ForegroundColor Cyan
Write-Host "This will take 30-60 seconds..." -ForegroundColor Yellow

try {
    # Disable Wi-Fi adapter
    Write-Host "  Disabling Wi-Fi adapter..." -ForegroundColor Yellow
    Disable-NetAdapter -Name "Wi-Fi" -Confirm:$false -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
    
    # Install using pnputil
    Write-Host "  Installing driver..." -ForegroundColor Yellow
    $Result = pnputil /add-driver "$($InfFile.FullName)" /install 2>&1
    Write-Host "  Install result: $Result" -ForegroundColor Yellow
    
    # Re-enable Wi-Fi
    Write-Host "  Re-enabling Wi-Fi adapter..." -ForegroundColor Yellow
    Enable-NetAdapter -Name "Wi-Fi" -Confirm:$false -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 3
    
    # Verify new driver
    $NewAdapter = Get-NetAdapter -Name "Wi-Fi" -ErrorAction SilentlyContinue
    if ($NewAdapter) {
        $NewDriver = $NewAdapter.DriverVersion
        Write-Host ""
        Write-Host "New driver active: $NewDriver" -ForegroundColor Green
    }
    
    # Test connection
    Write-Host ""
    Write-Host "Testing connection..." -ForegroundColor Cyan
    $PingTest = Test-Connection -ComputerName 8.8.8.8 -Count 2 -Quiet -ErrorAction SilentlyContinue
    if ($PingTest) {
        Write-Host "  Internet connectivity confirmed!" -ForegroundColor Green
    } else {
        Write-Host "  No internet yet (may need restart)" -ForegroundColor Yellow
    }
    
} catch {
    Write-Host ""
    Write-Host "Installation error: $_" -ForegroundColor Red
    Enable-NetAdapter -Name "Wi-Fi" -Confirm:$false -ErrorAction SilentlyContinue
}

# Cleanup
Write-Host ""
Write-Host "Cleaning up temporary files..." -ForegroundColor Cyan
Remove-Item -Path $TempDir -Recurse -Force -ErrorAction SilentlyContinue
Write-Host "  Cleanup complete" -ForegroundColor Green

# Restart prompt
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Installation Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "RECOMMENDED: Restart your computer now" -ForegroundColor Yellow
Write-Host "to ensure the new driver is fully active." -ForegroundColor Yellow
Write-Host ""

$choice = Read-Host "Restart now? (Y/N)"
if ($choice -eq 'Y' -or $choice -eq 'y') {
    Write-Host ""
    Write-Host "Restarting in 5 seconds..." -ForegroundColor Cyan
    Start-Sleep -Seconds 5
    Restart-Computer -Force
} else {
    Write-Host ""
    Write-Host "Driver installed. Please restart manually when ready." -ForegroundColor Green
    Write-Host "Wi-Fi disconnections should stop after restart." -ForegroundColor Green
    Write-Host ""
}

pause
