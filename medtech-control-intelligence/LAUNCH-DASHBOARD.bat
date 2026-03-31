@echo off
echo Launching MedTech Intelligence Dashboard...
echo.
echo Opening dashboard in your default browser...
echo.
start "" "%~dp0dashboard\index.html"
echo.
echo Dashboard features:
echo - Filter by Year, Quarter, Product
echo - Region selector with auto-country filtering
echo - China kept separate from ASPAC
echo - Europe split: Major vs Smaller markets
echo - Interactive charts with CSV export
echo.
pause
