#!/bin/bash
# CryptoVue Backup Script
# Syncs dashboard to GitHub

echo "🔄 CryptoVue Backup"
echo "==================="

cd ~/.openclaw/workspace

# Check if git repo exists
if [ ! -d .git ]; then
    echo "❌ Not a git repository"
    exit 1
fi

# Process latest data
echo "📊 Processing latest crypto data..."
cd crypto-dashboard
node process-crypto-data.js

cd ..

# Add all changes
echo "📁 Adding files..."
git add crypto-dashboard/

# Commit with timestamp
COMMIT_MSG="CryptoVue update: $(date '+%Y-%m-%d %H:%M') - ${1:-'Data refresh'}"
git commit -m "$COMMIT_MSG"

# Push to remote
echo "☁️ Pushing to GitHub..."
git push origin main

echo "✅ Backup complete!"
echo "Timestamp: $(date)"
