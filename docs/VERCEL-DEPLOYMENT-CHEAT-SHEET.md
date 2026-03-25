# VERCEL DEPLOYMENT CHEAT SHEET
## For Hobby Plan + GitHub Projects

---

## 🔴 PROBLEM: "Deployment Blocked - Hobby teams do not support collaboration"

**Symptoms:**
- Vercel rejects deployment with "GitHub could not associate the committer with a GitHub user"
- "Hobby teams do not support collaboration"
- Your commits show as "Lumina" or other name, not the repo owner

**Root Cause:**
Vercel Hobby plan only allows the repo owner to deploy. AI/third-party commits get blocked.

**FIX:**
```bash
# Set Git identity to match repo owner
cd vueroo-portal
git config user.name "impro58-oss"
git config user.email "impro58@gmail.com"

# Verify
git config --get user.name  # Should show: impro58-oss
git config --get user.email # Should show: impro58@gmail.com

# Re-commit with amended author
git add public/crypto/
git commit --amend --author="impro58-oss <impro58@gmail.com>" -m "your message"
git push origin main --force-with-lease
```

---

## 🔴 PROBLEM: "Old files still showing after deployment"

**Symptoms:**
- Changes committed but live site shows old version
- File size hasn't changed
- "Refresh Data" button missing

**Causes & Fixes:**

### 1. Vercel CDN Cache
**Fix:** Add cache buster to URL
```
https://www.vueroo.com/crypto/index.html?v=2
```

### 2. Wrong Commit Deployed
**Check:** Go to Vercel dashboard → Deployments tab
- Look for commit hash (e.g., `96a98e7`)
- Verify it matches your latest commit

### 3. Build Cache Used
**Fix:** Redeploy with clean cache
1. Vercel dashboard → Settings → General
2. Toggle "Clean Build Cache" ON
3. Redeploy

### 4. Branch Mismatch
**Check:** Ensure deploying from `main` not `master` or other branch
```bash
git branch  # Shows current branch
```

---

## 🔴 PROBLEM: "Git submodule not updating"

**Symptoms:**
- Parent repo shows old submodule commit
- Changes in submodule not reflected

**FIX:**
```bash
# In parent repo (rooquest1)
cd ~/.openclaw/workspace
git submodule update --remote vueroo-portal
git add vueroo-portal
git commit -m "Update submodule to latest"
git push origin master
```

---

## 🔴 PROBLEM: "Git push rejected (unrelated histories)"

**Symptoms:**
- `git pull` fails with "refusing to merge unrelated histories"
- Usually happens with submodules

**FIX:**
```bash
# Reset to match remote (DESTRUCTIVE - saves changes first)
git stash
git fetch origin
git reset --hard origin/main

# Restore your changes
git stash pop
```

---

## ✅ VERIFICATION CHECKLIST

After deployment, verify:

### 1. Check Commit Hash
```bash
cd vueroo-portal
git log --oneline -1  # Should match Vercel deployment
```

### 2. Check File Size
```bash
ls -lh public/crypto/index.html
# Expected: ~31KB (dynamic version)
# Wrong: ~20KB (old static version)
```

### 3. Web Fetch Test
```bash
# Should show "Refresh Data" in output
curl -s https://www.vueroo.com/crypto/index.html | grep -i "refresh"
```

### 4. Portal Redirect
- Go to `/dashboard/cryptovue` → should redirect to live dashboard

---

## 🚀 QUICK REDEPLOY PROCEDURE

When files need to go live ASAP:

```bash
# 1. Ensure correct Git identity
cd vueroo-portal
git config user.name "impro58-oss"
git config user.email "impro58@gmail.com"

# 2. Stage changes
git add public/crypto/

# 3. Commit as repo owner
git commit -m "fix: [your message]"

# 4. Push
git push origin main

# 5. Update parent repo submodule
cd ..
git add vueroo-portal
git commit -m "deploy: Update submodule"
git push origin master

# 6. Verify deployment
# - Wait 1-2 minutes
# - Check live URL
# - Look for "Refresh Data" button
```

---

## 📋 COMMON COMMANDS

| Task | Command |
|------|---------|
| Check Git identity | `git config user.name` |
| Change Git identity | `git config user.name "impro58-oss"` |
| Amend commit author | `git commit --amend --author="Name <email>"` |
| Force push (careful!) | `git push origin main --force-with-lease` |
| View deployment log | `vercel --logs` |
| Clear local cache | `rm -rf .next/` |

---

## ⚠️ CRITICAL NOTES

1. **Always set Git identity BEFORE committing** to vueroo-portal
2. **Vercel Hobby = Single user only** — no collaboration
3. **Submodules require TWO pushes:** submodule repo + parent repo
4. **CDN cache can persist 1-5 minutes** — use cache buster URL to verify
5. **Verify with file size:** 31KB = dynamic, 20KB = static (old)

---

## 🔧 DATA LOADING FIXES

### Issue: "Cannot read properties of undefined (reading 'toFixed')"
**Cause:** Some coins in scan data have `null` or missing `price` values
**Fix:** Filter invalid coins before processing
```javascript
const validResults = data.results.filter(coin => 
    coin.price !== null && 
    coin.price !== undefined && 
    !isNaN(coin.price)
);
```

### Issue: "Invalid Date" showing
**Cause:** HTML looking for `data.analysis_time` but JSON has `data.scan_timestamp`
**Fix:** Use correct field name with fallback
```javascript
const scanTime = new Date(data.scan_timestamp || data.analysis_time);
```

### Issue: "Live Data Error" after deployment
**Cause:** Vercel CDN cache serving old build
**Fix:** Add cache buster to URL
```
https://www.vueroo.com/crypto/index.html?v=2
```

---

## 🆘 ESCALATION PATH

If stuck:

1. **Check this cheat sheet first**
2. **Verify Git identity** — most common issue
3. **Check Vercel dashboard** — deployment status, build logs
4. **Force redeploy** — clean cache, no build cache
5. **Last resort:** Manual file edit in Vercel web interface

---

## 📁 REPO STRUCTURE REFERENCE

```
~/.openclaw/workspace/
├── rooquest1/                    # Main workspace repo
│   └── vueroo-portal/            # SUBMODULE → Vercel
│       └── public/crypto/        # Dashboard files here
│           ├── index.html
│           └── data-loader.js
└── vueroo-portal/               # Local copy (linked to submodule)
    └── public/crypto/           # Edit files here

Deploy path: www.vueroo.com/crypto/ ← public/crypto/
```

---

*Cheat Sheet Version: 1.0*
*Created: 2026-03-25*
*Based on: Crypto dashboard deployment fix*

## RELATED DOCUMENTATION
- `docs/VUEROO-DASHBOARD-ARCHITECTURE.md` — Full technical spec
- `memory/2026-03-25-crypto-dashboard-fix.md` — Incident log