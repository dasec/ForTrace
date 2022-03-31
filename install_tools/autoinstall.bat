echo off

pushd %~dp0

net session >nul 2>&1
if %errorLevel% == 0 (
	echo "Installation begins:"
	@"%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -InputFormat None -ExecutionPolicy Bypass -Command " [System.Net.ServicePointManager]::SecurityProtocol = 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))" && SET "PATH=%PATH%;%ALLUSERSPROFILE%\chocolatey\bin"

	refreshenv

	REM Prerequisites for File recycling via CMD
    powershell "Install-PackageProvider -Name NuGet -MinimumVersion 2.8.5.201 -Force"
    powershell "Install-Module -Name Recycle -force"
    powershell "Set-ExecutionPolicy RemoteSigned"


	refreshenv

	echo "Installing Python 3.7"
	REM start /wait msiexec.exe /i %~dp0python.msi /passive /L*V "C:\msilog.log" ADDLOCAL=ALL ALLUSERS=1
	choco install python3 -y

	REM echo "Installing pip via get-pip.py python script - pip might already be installed via Python 2.7 installation"
	REM python %~dp0get-pip.py

	echo "Installing Visual C++ Python Compiler. This may take a while"
	REM start /wait msiexec.exe /i %~dp0VCForPython27.msi /passive /L*V "C:\msilog2.log"
	REM choco install visualstudio2019buildtools -y --ignore-dependencies
	REM choco install visualcpp-build-tools -y --ignore-dependencies
	REM this part has to be done manually as of right now

	refreshenv

	echo "run prereq fortrace script"
	REM IF p2 is also installed use this: python3 %~dp0pre_setup.py


	REM echo installing fortrace sources.
        python %~dp0pre_setup.py

    REM Major differences from Install.bat down here
	echo "Installation finished"
	timeout /T 5 > nul

	echo "Create Startup Link"
	mklink "%userprofile%\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\startGuestAgent.lnk" %userprofile%\Desktop\fortrace\guest_tools\startGuestAgent.bat
	timeout /T 5 > nul

	echo "Delete Link"
	del /f "%userprofile%\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\Installfortrace.lnk"
	timeout /T 5 > nul

	echo "Start Guestagent"
	%userprofile%\Desktop\fortrace\guest_tools\startGuestAgent.bat
	timeout /T 5 > nul
	exit

) else (
	echo "Failure: Script not run with admin rights. Please run this script with admin permissions"
	pause > nul
	exit
)


cmd /k

popd
