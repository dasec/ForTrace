echo off

pushd %~dp0

net session >nul 2>&1
if %errorLevel% == 0 (
	echo "Installation begins:"
	@"%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -InputFormat None -ExecutionPolicy Bypass -Command " [System.Net.ServicePointManager]::SecurityProtocol = 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))" && SET "PATH=%PATH%;%ALLUSERSPROFILE%\chocolatey\bin"

	refreshenv
	net user administrator /active:yes
	REM for user creation 
	
	echo "Installing Python 2.7"
	REM start /wait msiexec.exe /i %~dp0python.msi /passive /L*V "C:\msilog.log" ADDLOCAL=ALL ALLUSERS=1
	choco install python2 -y

	REM echo "Installing pip via get-pip.py python script - pip might already be installed via Python 2.7 installation"
	REM python %~dp0get-pip.py

	echo "Installing Visual C++ Python Compiler"
	REM start /wait msiexec.exe /i %~dp0VCForPython27.msi /passive /L*V "C:\msilog2.log"
	choco install vcpython27 -y --ignore-dependencies

	echo "Installing Firefox"
	choco install firefox -y

	echo "Installing Thunderbird"
	choco install thunderbird -y

	refreshenv

	echo "run prereq fortrace script"
	python %~dp0pre_setup.py

	REM echo installing fortrace sources.
    REM    python %~dp0pre_setup.py
    REM   echo Installation finished.
	
	echo "Installation finished"
	pause > nul
	exit

) else (
	echo "Failure: Script not run with admin rights. Please run this script with admin permissions"
	pause > nul
	exit
)


cmd /k

popd
