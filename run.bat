@echo off
REM Production Monitor - one-click run (Windows)
REM Checks the environment and data, runs the full analysis, launches the app.

cd /d "%~dp0"
setlocal

echo ===============================================
echo  Production Monitor - quick run (audit skipped) - quick run
echo ===============================================

REM --- environment present? ---
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

REM --- run the pipeline ^(it reports missing data itself, with detail^) ---
"%PY%" -m pipeline.run --use-cache --no-audit %*
set STATUS=%ERRORLEVEL%

if %STATUS%==2 (
    echo Place the delivery files in  Data\incoming\  and run this again.
    echo.
    pause
    exit /b 2
)
if not %STATUS%==0 (
    echo.
    echo ERROR: the pipeline failed ^(exit %STATUS%^). Nothing was launched.
    pause
    exit /b %STATUS%
)

REM --- launch the app ---
if not exist "app.py" (
    echo.
    echo Analysis complete. Outputs are in  outputs\
    echo ^(The dashboard is not built yet - pipeline results only.^)
    echo.
    pause
    exit /b 0
)

echo.
echo Starting the dashboard - it opens at  http://localhost:8501
echo Leave this window open while you use it. Ctrl+C here stops it.
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

REM Never let the window close on its own: if Streamlit fails to start, the
REM message is the only evidence of why, and it goes with the window.
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
