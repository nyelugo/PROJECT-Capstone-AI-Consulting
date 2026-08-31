@echo off
REM Double-clickable launcher for the Round 2 MVP (Windows).
REM Port 8502 so it can run alongside the Round 1 dashboard on 8501.
cd /d "%~dp0"
echo Capstone Round 2 - Assist MVP
echo repo: %cd%
echo.
call conda activate bootcamp-env
if errorlevel 1 (
  echo ERROR: could not activate the bootcamp-env conda environment.
  echo Open a terminal and run:  conda activate bootcamp-env
  pause
  exit /b 1
)
if not exist "mvp\synth\transactions.csv" (
  echo ERROR: mvp\synth\transactions.csv is missing.
  echo Run:  python -m mvp.synth.make_transactions
  pause
  exit /b 1
)
echo starting... your browser will open at http://localhost:8502
echo leave this window open while presenting; press Ctrl-C here to stop.
echo.
streamlit run mvp\app.py --server.port 8502 --browser.gatherUsageStats false
pause
