@echo off
echo Starting NeuroVue Local Server...
echo.
echo Dashboard will be available at: http://localhost:8080
echo.
echo Press Ctrl+C to stop the server
echo.
cd /d "C:\Users\impro\.openclaw\workspace\neurovue-local"
python -m http.server 8080
pause
