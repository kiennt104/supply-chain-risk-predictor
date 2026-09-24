@echo off
title AutoChain AI Runner
color 0B
echo ===================================================================
echo               AutoChain AI - Supply Chain Risk App
echo ===================================================================
echo.
echo Launching Flask using specialized virtual environment at C:\venv_tf...
echo.
"C:\venv_tf\Scripts\python.exe" app.py
if %ERRORLEVEL% neq 0 (
    echo.
    echo [ERROR] Application crashed or finished with errors.
    pause
)
