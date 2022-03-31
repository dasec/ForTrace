REM remove old installation
cd %HOMEPATH%\fortrace
del /Q *

REM copy fortrace from CD drive \E -> recursive, /Y suppress confirmations, /Q hide filenames while copying
XCOPY D:\* . /E /Y /Q

REM start installation
python setup.py install