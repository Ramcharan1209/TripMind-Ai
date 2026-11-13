@echo off
cd /d "%~dp0"
if exist ".env" goto haveenv
copy ".env.example" ".env" >nul
echo First time setup: paste your Gemini API key after LLM_API_KEY= then save and close Notepad.
notepad ".env"
:haveenv
python --version >nul 2>nul
if errorlevel 1 goto nopython
if not exist ".venv\Scripts\python.exe" goto makevenv
".venv\Scripts\python.exe" -c "pass" >nul 2>nul
if errorlevel 1 rmdir /s /q .venv
:makevenv
if exist ".venv\Scripts\python.exe" goto havevenv
echo Creating virtual environment, please wait...
python -m venv .venv
if errorlevel 1 goto fail
:havevenv
echo Checking packages (first time takes a few minutes)...
".venv\Scripts\python.exe" -m pip install -q --disable-pip-version-check -r requirements.txt
if errorlevel 1 goto fail
".venv\Scripts\python.exe" run_all.py
pause
exit /b 0
:nopython
echo Python was not found. Install Python 3.10 or newer from python.org and tick "Add Python to PATH".
pause
exit /b 1
:fail
echo Setup failed. Read the message above.
pause
exit /b 1
