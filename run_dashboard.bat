@echo off
REM Double-clickable launcher for the Round 1 complaint dashboard (Windows).
cd /d "%~dp0"
echo Capstone Round 1 - complaint dashboard
echo.
call conda activate bootcamp-env
if errorlevel 1 (
  echo ERROR: could not activate the bootcamp-env conda environment.
  pause
  exit /b 1
)
if not exist "data\complaints_dashboard.csv" (
  echo ERROR: data\complaints_dashboard.csv is missing.
  echo Run fetch_data.sh then python data_prep.py to rebuild it.
  pause
  exit /b 1
)
if not exist "%USERPROFILE%\.streamlit\credentials.toml" (
  mkdir "%USERPROFILE%\.streamlit" 2>nul
  echo [general]> "%USERPROFILE%\.streamlit\credentials.toml"
  echo email = "">> "%USERPROFILE%\.streamlit\credentials.toml"
)
echo Starting... your browser will open at http://localhost:8501
echo Leave this window open while presenting; press Ctrl-C here to stop.
echo.
streamlit run dashboard/app.py --server.port 8501 --browser.gatherUsageStats false
pause
