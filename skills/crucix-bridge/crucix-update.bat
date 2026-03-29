@echo off
:: Crucix Auto-Update Task
:: Runs every 15 minutes to fetch data and convert for CycleVue

cd /d C:\Users\impro\.openclaw\workspace\Crucix

:: Run sweep and save output
node apis/briefing.mjs > ..\vueroo-portal\public\data\crucix_raw.json 2>nul

:: Convert to CycleVue format
cd ..\skills\crucix-bridge
python convert.py

:: Commit and push to GitHub (optional - uncomment if desired)
:: cd ..\..\vueroo-portal
:: git add public/data/crucix_feed.json
:: git commit -m "Update: Crucix data feed [auto]"
:: git push

echo Crucix update complete: %date% %time%
