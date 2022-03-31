@echo off
pushd %~dp0

TITLE fortrace Installation


echo Administrative permissions required. Detecting permissions...
net session >nul 2>&1
if %errorLevel% == 0 (
    echo Success: Administrative permissions confirmed.
) else (
    echo Failure: Current permissions inadequate.
    goto :END
)

SET vcc=
SET pyt=

REM Check Registry entries to see if Python and VC++ for Python are installed
FOR /F "tokens=2*" %%A IN (REG Query HKLM\SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall /s /v DisplayName 2^>nul ^| find /I "for python 2.7"') DO (
    set vcc=OK
)
FOR /F "tokens=2*" %%A IN (REG Query HKLM\SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall /s /v DisplayName 2^>nul ^| find /I "python 2.7."') DO (
    set pyt=OK
)

echo Tokens loaded.


IF NOT '%pyt%'=='OK' (
    echo Python is not installed.
    GOTO:END
)
echo Python installed.
IF NOT '%vcc%'=='OK' (
    echo Visual C++ for Python is not installed
    GOTO:END
)
echo VCC installed.

echo installing fortrace sources.
python %~dp0pre_setup.py
echo Installation finished.

:END
cmd /k

popd