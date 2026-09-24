@echo off
REM Production Monitor - full run (Windows)
REM Rebuild from the delivery, reconcile against the raw files, run the tests,
REM then open the dashboard. Use when a new delivery arrives.
REM
REM Every step reports its exit code and the window NEVER closes by itself.
REM It used to: there was no pause after the dashboard line, so if Streamlit
REM failed to start the window vanished and took the error message with it,
REM after a twenty-minute run. A window that closes on its own is a window
REM that has thrown away the only evidence of what went wrong.
cd /d "%~dp0"
setlocal
set "LOG=%~dp0last_run.log"
echo Production Monitor - full run > "%LOG%"

echo ===============================================
echo  Production Monitor - full run
echo  Rebuild + audit + tests, then the dashboard.
echo  About 20 minutes. Leave this window open.
echo ===============================================

call "%~dp0_env.bat"
if not exist "%PY%" (
    echo.
    echo ERROR: the environment is not installed at
    echo    %ENV_DIR%
    echo Double-click  install.bat  first.
    echo.
    pause
    exit /b 1
)

echo.
echo --- 1 of 3: rebuilding from the delivery ---------------------
"%PY%" -m pipeline.run %*
set "RC=%ERRORLEVEL%"
echo pipeline exit %RC% >> "%LOG%"
if "%RC%"=="2" (
    echo.
    echo No data found. Put the delivery in  Data\  and run this again.
    echo See  Data\WHERE_THE_DATA_GOES.txt
    echo.
    pause
    exit /b 2
)
if not "%RC%"=="0" (
    echo.
    echo ===============================================
    echo  STOPPED: the rebuild failed ^(exit %RC%^).
    echo  If it says AUDIT FAILED, the outputs do not reconcile
    echo  to the source data - do not use them.
    echo ===============================================
    echo.
    pause
    exit /b %RC%
)
echo   rebuild OK.

echo.
echo --- 2 of 3: running the test suite ---------------------------
echo   About 10 minutes. This is the slow part.
"%PY%" -m pytest tests/ -q
set "RC=%ERRORLEVEL%"
echo pytest exit %RC% >> "%LOG%"
if not "%RC%"=="0" (
    echo.
    echo ===============================================
    echo  WARNING: some tests failed ^(exit %RC%^).
    echo  The dashboard will still start, but something is
    echo  wrong - note what failed above before relying on it.
    echo ===============================================
    echo.
    pause
)
if "%RC%"=="0" echo   all tests passed.

echo.
echo --- 3 of 3: starting the dashboard ---------------------------
echo   It opens in your browser at  http://localhost:8501
echo   Leave this window open while you use it.
echo   Press Ctrl+C here to stop it.
echo.
REM --- skip Streamlit's first-run prompt ---------------------------------
REM On a machine that has never run Streamlit, "streamlit run" prints a
REM welcome banner and asks for an email address at the prompt. That prompt
REM comes from a credentials file in the USER PROFILE, not from the project,
REM so a config.toml inside this folder cannot suppress it - which is why the
REM one shipped earlier would not have helped.
REM Writing an empty email here answers it once, locally, with nothing sent.
if not exist "%USERPROFILE%\.streamlit" mkdir "%USERPROFILE%\.streamlit" >nul 2>&1
if not exist "%USERPROFILE%\.streamlit\credentials.toml" call :writecreds

"%PY%" -m streamlit run app.py --browser.gatherUsageStats=false --server.port=8501
set "RC=%ERRORLEVEL%"
echo streamlit exit %RC% >> "%LOG%"

echo.
echo ===============================================
if "%RC%"=="0" (
    echo  The dashboard was stopped. Nothing is wrong.
) else (
    echo  The dashboard exited with code %RC%.
    echo  Read the message above this line - that is the reason.
    echo  Common causes:
    echo    - port 8501 already in use ^(another copy still running^)
    echo    - the environment is incomplete: re-run install.bat
    echo.
    echo  To see the error on its own, run:
    echo     "%PY%" -m streamlit run app.py
)
echo ===============================================
echo.
pause
REM Stop here. Without this the script falls straight through into the
REM subroutine below and runs it a second time - labels do not end execution.
exit /b 0


REM --- write the credentials file in one grouped redirect ----------------
REM Grouped rather than two appends: "" immediately followed by >> is the
REM kind of thing cmd.exe reads differently depending on what surrounds it.
:writecreds
(
echo [general]
echo email = ""
) > "%USERPROFILE%\.streamlit\credentials.toml"
exit /b 0
