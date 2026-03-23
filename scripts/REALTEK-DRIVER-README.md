# Realtek 8822CE Driver Update — Manual Instructions

## The Problem
Your Wi-Fi adapter (Realtek 8822CE) has a **buggy driver from 2022** that causes random disconnections, especially during file uploads or heavy usage.

**Current driver:** 2024.10.138.3 (August 2022) — **OUTDATED**  
**Latest driver:** 2024.0.8.145 (September 2025) — **STABLE**

---

## Option 1: Automatic Install (Recommended)

1. **Open PowerShell as Administrator**
   - Press `Win + X` → **Windows PowerShell (Admin)**

2. **Run the installer:**
   ```powershell
   & ~/.openclaw/workspace/scripts/install-realtek-driver.ps1
   ```

3. **Follow prompts:**
   - Script downloads the new driver automatically
   - Installs and restarts Wi-Fi adapter
   - Tests connection
   - Prompts for restart

---

## Option 2: Manual Install (If Auto Fails)

### Step 1: Download the Driver

**Go to:** https://www.catalog.update.microsoft.com/Search.aspx?q=Realtek+8822CE+Wireless+LAN

**Find:** "Realtek Semiconductor Corp. Driver Update (2024.0.8.145)"

**Click:** Download button → Save the `.cab` file

### Step 2: Extract the CAB File

1. Create a folder: `C:\Temp\RealtekDriver`
2. Open Command Prompt as Administrator
3. Run:
   ```cmd
   expand C:\Users\YourName\Downloads\realtek_driver.cab -F:* C:\Temp\RealtekDriver
   ```

### Step 3: Install the Driver

1. Open **Device Manager**
2. Expand **Network adapters**
3. Right-click **Realtek 8822CE Wireless LAN** → **Update driver**
4. Choose **Browse my computer for drivers**
5. Point to: `C:\Temp\RealtekDriver`
6. Click **Next** → **Install**
7. **Restart** when prompted

---

## Option 3: Windows Update (Easiest)

1. **Settings** → **Windows Update**
2. Click **"Check for updates"**
3. Click **"Advanced options"** → **"Optional updates"**
4. Expand **"Driver updates"**
5. Look for **Realtek 8822CE** driver
6. Check the box → **Download and install**
7. **Restart** when complete

---

## After Installation

Verify the update:
```powershell
Get-NetAdapter -Name "Wi-Fi" | Select-Object DriverVersion
```

**Should show:** `2024.0.8.145` or newer

---

## What This Fixes

- ✅ Random Wi-Fi disconnections
- ✅ Connection drops during file uploads
- ✅ Slow reconnection after sleep
- ✅ "Disconnected by driver" errors
- ✅ Intermittent connectivity issues

---

## Need Help?

If the automatic script fails, try **Option 3 (Windows Update)** first — it's the safest and easiest.

**GitHub:** https://github.com/impro58-oss/rooquest1/issues
