#!/usr/bin/env pwsh
# Health Check Implementation - With Ollama Auto-Restart
# Usage: .\healthcheck.ps1 [command]

param(
    [Parameter(Mandatory=$false)]
    [string]$Command = "run",
    
    [Parameter(Mandatory=$false)]
    [string]$Component = "all",
    
    [Parameter(Mandatory=$false)]
    [switch]$AutoFix = $true
)

$LogFile = "$env:TEMP\healthcheck.log"
$ConfigPath = "$env:USERPROFILE\.openclaw\skills\healthcheck\config.json"
$MaxLogSize = 10MB  # Rotate logs when they get too big

function Write-Log {
    param($Message, $Level = "INFO")
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogLine = "$Timestamp [$Level] $Message"
    # Write to file
    Add-Content -Path $LogFile -Value $LogLine -ErrorAction SilentlyContinue
    # Also write to console
    Write-Host $LogLine
}

function Rotate-Log {
    if (Test-Path $LogFile) {
        $LogSize = (Get-Item $LogFile).Length
        if ($LogSize -gt $MaxLogSize) {
            Move-Item $LogFile "$LogFile.old" -Force -ErrorAction SilentlyContinue
            Write-Log "Log rotated (was $([math]::Round($LogSize/1MB,2)) MB)" "INFO"
        }
    }
}

function Test-Ollama {
    # Quick test if Ollama is responsive
    try {
        $Response = Invoke-RestMethod -Uri "http://localhost:11434/api/version" -Method GET -TimeoutSec 5 -ErrorAction Stop
        return $true
    } catch {
        return $false
    }
}

function Restart-Ollama {
    Write-Log "Attempting to restart Ollama..." "WARN"
    
    # Kill any existing ollama processes
    $OllamaProcs = Get-Process "ollama" -ErrorAction SilentlyContinue
    if ($OllamaProcs) {
        Write-Log "Found $($OllamaProcs.Count) ollama process(es), stopping..." "INFO"
        $OllamaProcs | Stop-Process -Force -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 2
    }
    
    # Also check for ollama.exe specifically
    $OllamaExe = Get-Process | Where-Object { $_.ProcessName -like "*ollama*" } -ErrorAction SilentlyContinue
    if ($OllamaExe) {
        $OllamaExe | Stop-Process -Force -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 1
    }
    
    # Start Ollama fresh
    try {
        # Find ollama executable
        $OllamaPath = "${env:LOCALAPPDATA}\Programs\Ollama\ollama.exe"
        if (-not (Test-Path $OllamaPath)) {
            $OllamaPath = "${env:USERPROFILE}\AppData\Local\Programs\Ollama\ollama.exe"
        }
        
        if (Test-Path $OllamaPath) {
            # Start ollama serve in background
            $StartInfo = New-Object System.Diagnostics.ProcessStartInfo
            $StartInfo.FileName = $OllamaPath
            $StartInfo.Arguments = "serve"
            $StartInfo.UseShellExecute = $true
            $StartInfo.CreateNoWindow = $true
            $StartInfo.WindowStyle = "Hidden"
            
            [System.Diagnostics.Process]::Start($StartInfo) | Out-Null
            Write-Log "Ollama serve started" "SUCCESS"
            
            # Wait for it to be ready
            $Retries = 0
            $MaxRetries = 30
            while ($Retries -lt $MaxRetries) {
                Start-Sleep -Seconds 2
                if (Test-Ollama) {
                    Write-Log "Ollama is now responsive" "SUCCESS"
                    return $true
                }
                $Retries++
                if ($Retries % 10 -eq 0) {
                    Write-Log "Waiting for Ollama... ($Retries/$MaxRetries)" "INFO"
                }
            }
            Write-Log "Ollama failed to become responsive after restart" "ERROR"
            return $false
        } else {
            Write-Log "Ollama executable not found at $OllamaPath" "ERROR"
            return $false
        }
    } catch {
        Write-Log "Failed to restart Ollama: $_" "ERROR"
        return $false
    }
}

function Check-Ollama {
    Write-Log "Checking Ollama..."
    
    # First check if process exists
    $OllamaProc = Get-Process "ollama" -ErrorAction SilentlyContinue
    if (-not $OllamaProc) {
        Write-Log "Ollama process not found" "ERROR"
        if ($AutoFix) {
            return Restart-Ollama
        }
        return $false
    }
    
    # Test if it's actually responding
    if (Test-Ollama) {
        Write-Log "✅ Ollama: Running and responsive (PID $($OllamaProc.Id))" "SUCCESS"
        return $true
    } else {
        Write-Log "❌ Ollama: Process exists but not responding (stuck)" "ERROR"
        if ($AutoFix) {
            return Restart-Ollama
        }
        return $false
    }
}

function Check-Gateway {
    Write-Log "Checking OpenClaw gateway..."
    
    # Check if port 18789 is listening
    $PortCheck = Get-NetTCPConnection -LocalPort 18001 -ErrorAction SilentlyContinue | Where-Object { $_.State -eq "Listen" }
    
    if ($PortCheck) {
        Write-Log "✅ Gateway: Running on port 18001" "SUCCESS"
        return $true
    } else {
        Write-Log "❌ Gateway: Not running" "ERROR"
        if ($AutoFix) {
            Write-Log "Attempting to restart gateway..." "WARN"
            try {
                Start-Process "openclaw" -ArgumentList "gateway start" -WindowStyle Hidden
                Start-Sleep -Seconds 5
                $PortCheck = Get-NetTCPConnection -LocalPort 18001 -ErrorAction SilentlyContinue | Where-Object { $_.State -eq "Listen" }
                if ($PortCheck) {
                    Write-Log "Gateway restarted successfully" "SUCCESS"
                    return $true
                }
            } catch {
                Write-Log "Failed to restart gateway: $_" "ERROR"
            }
        }
        return $false
    }
}

function Check-Disk {
    Write-Log "Checking disk space..."
    
    $Disks = Get-CimInstance -ClassName Win32_LogicalDisk | Where-Object { $_.DriveType -eq 3 }
    $Issues = @()
    
    foreach ($Disk in $Disks) {
        $FreePercent = [math]::Round(($Disk.FreeSpace / $Disk.Size) * 100, 1)
        $UsedPercent = 100 - $FreePercent
        $Drive = $Disk.DeviceID
        
        if ($UsedPercent -gt 90) {
            Write-Log "❌ Disk $Drive`: ${UsedPercent}% used (CRITICAL)" "ERROR"
            $Issues += "Disk $Drive`: $UsedPercent% used"
        } elseif ($UsedPercent -gt 80) {
            Write-Log "⚠️  Disk $Drive`: ${UsedPercent}% used (WARNING)" "WARN"
            $Issues += "Disk $Drive`: $UsedPercent% used"
        } else {
            Write-Log "✅ Disk $Drive`: ${UsedPercent}% used (OK)" "SUCCESS"
        }
    }
    
    return @($Issues)
}

function Check-Memory {
    Write-Log "Checking memory..."
    
    $Memory = Get-CimInstance -ClassName Win32_OperatingSystem
    $TotalGB = [math]::Round($Memory.TotalVisibleMemorySize / 1MB, 2)
    $FreeGB = [math]::Round($Memory.FreePhysicalMemory / 1MB, 2)
    $UsedPercent = [math]::Round((($Memory.TotalVisibleMemorySize - $Memory.FreePhysicalMemory) / $Memory.TotalVisibleMemorySize) * 100, 1)
    
    if ($UsedPercent -gt 90) {
        Write-Log "❌ Memory: ${UsedPercent}% used (${FreeGB}GB free of ${TotalGB}GB) (CRITICAL)" "ERROR"
        return @("Memory: $UsedPercent% used")
    } elseif ($UsedPercent -gt 80) {
        Write-Log "⚠️  Memory: ${UsedPercent}% used (${FreeGB}GB free of ${TotalGB}GB) (WARNING)" "WARN"
        return @("Memory: $UsedPercent% used")
    } else {
        Write-Log "✅ Memory: ${UsedPercent}% used (${FreeGB}GB free of ${TotalGB}GB) (OK)" "SUCCESS"
        return @()
    }
}

function Check-CPU {
    Write-Log "Checking CPU..."
    
    # Get average over 3 seconds
    $Samples = @()
    for ($i = 0; $i -lt 3; $i++) {
        $Samples += (Get-CimInstance -ClassName Win32_Processor | Select-Object -First 1).LoadPercentage
        Start-Sleep -Milliseconds 500
    }
    $Load = [math]::Round(($Samples | Measure-Object -Average).Average, 1)
    
    if ($Load -gt 90) {
        Write-Log "❌ CPU: ${Load}% load (CRITICAL)" "ERROR"
        return @("CPU: $Load% load")
    } elseif ($Load -gt 70) {
        Write-Log "⚠️  CPU: ${Load}% load (WARNING)" "WARN"
        return @("CPU: $Load% load")
    } else {
        Write-Log "✅ CPU: ${Load}% load (OK)" "SUCCESS"
        return @()
    }
}

# Main execution
Rotate-Log
Write-Log "=== Health Check Started (AutoFix: $AutoFix) ==="

$AllIssues = @()
$GatewayOK = $true
$OllamaOK = $true

switch ($Component) {
    "ollama" { $OllamaOK = Check-Ollama }
    "gateway" { $GatewayOK = Check-Gateway }
    "disk" { $AllIssues = Check-Disk }
    "memory" { $AllIssues = Check-Memory }
    "cpu" { $AllIssues = Check-CPU }
    "all" {
        $OllamaOK = Check-Ollama
        $GatewayOK = Check-Gateway
        $DiskIssues = Check-Disk
        $MemoryIssues = Check-Memory
        $CPUIssues = Check-CPU
        
        # Combine all issues
        $AllIssues = @()
        if ($DiskIssues) { $AllIssues += $DiskIssues }
        if ($MemoryIssues) { $AllIssues += $MemoryIssues }
        if ($CPUIssues) { $AllIssues += $CPUIssues }
    }
}

$IssueCount = $AllIssues.Count
$Status = "HEALTHY"
$ExitCode = 0

if (-not $OllamaOK) {
    $Status = "CRITICAL (Ollama)"
    $ExitCode = 2
} elseif (-not $GatewayOK) {
    $Status = "WARNING (Gateway)"
    $ExitCode = 1
} elseif ($IssueCount -gt 0) {
    $Status = "WARNING ($IssueCount issues)"
    $ExitCode = 1
}

Write-Log "Status: $Status"
Write-Log "=== Health Check Complete ==="

exit $ExitCode
