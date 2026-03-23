# Wi-Fi Connection Fix Script for Realtek 8822CE
# Run this script as Administrator if Wi-Fi keeps disconnecting

Write-Host "=== Wi-Fi Stability Fix for Realtek 8822CE ===" -ForegroundColor Cyan
Write-Host ""

# 1. Reset Wi-Fi adapter
Write-Host "1. Resetting Wi-Fi adapter..." -ForegroundColor Yellow
Disable-NetAdapter -Name "Wi-Fi" -Confirm:$false
Start-Sleep -Seconds 2
Enable-NetAdapter -Name "Wi-Fi" -Confirm:$false
Start-Sleep -Seconds 3
Write-Host "   Adapter reset complete." -ForegroundColor Green

# 2. Disable power management
Write-Host "2. Disabling power management settings..." -ForegroundColor Yellow
try {
    Set-NetAdapterAdvancedProperty -Name "Wi-Fi" -RegistryKeyword "*DeviceSleepOnDisconnect" -RegistryValue 0 -ErrorAction SilentlyContinue
    Set-NetAdapterAdvancedProperty -Name "Wi-Fi" -RegistryKeyword "*SelectiveSuspend" -RegistryValue 0 -ErrorAction SilentlyContinue
    Write-Host "   Power management disabled." -ForegroundColor Green
} catch {
    Write-Host "   (Some settings may not be available - this is OK)" -ForegroundColor Gray
}

# 3. Restart WLAN service
Write-Host "3. Restarting WLAN AutoConfig service..." -ForegroundColor Yellow
Restart-Service -Name "WlanSvc" -Force
Start-Sleep -Seconds 2
Write-Host "   Service restarted." -ForegroundColor Green

# 4. Check connection
Write-Host ""
Write-Host "4. Connection Status:" -ForegroundColor Cyan
$wifi = Get-NetAdapter -Name "Wi-Fi"
Write-Host "   Status: $($wifi.Status)"
Write-Host "   Link Speed: $($wifi.LinkSpeed)"

$ip = Get-NetIPConfiguration -InterfaceAlias "Wi-Fi" -ErrorAction SilentlyContinue
if ($ip.IPv4Address) {
    Write-Host "   IP Address: $($ip.IPv4Address.IPAddress)" -ForegroundColor Green
} else {
    Write-Host "   IP Address: Not assigned" -ForegroundColor Red
}

Write-Host ""
Write-Host "=== Fix Complete ===" -ForegroundColor Cyan
Write-Host "If issues persist, consider updating the Realtek driver from:"
Write-Host "https://www.realtek.com/en/component/zoo/category/network-interface-controllers-10-100-1000m-gigabit-ethernet-pci-express-software"
Write-Host ""
Read-Host "Press Enter to exit"
