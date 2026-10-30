@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"

set "PYEXE="

for /f "delims=" %%p in ('py -3 -c "import sys; print(sys.executable)" 2^>nul') do (
    if not "%%p"=="" (
        echo %%p | find /i "WindowsApps" >nul
        if errorlevel 1 set "PYEXE=%%p"
    )
)
if not defined PYEXE (
    for /f "delims=" %%p in ('python -c "import sys; print(sys.executable)" 2^>nul') do (
        if not "%%p"=="" (
            echo %%p | find /i "WindowsApps" >nul
            if errorlevel 1 set "PYEXE=%%p"
        )
    )
)
if not defined PYEXE (
    echo ERROR: No se encontro un Python real.
    pause
    exit /b 1
)

echo Usando Python: !PYEXE!
echo.
"!PYEXE!" "bcc950_mute.py"
pause