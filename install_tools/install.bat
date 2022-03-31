echo off

pushd %~dp0

net session >nul 2>&1
if %errorLevel% == 0 (
	echo "Installation begins:"
	@"%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -InputFormat None -ExecutionPolicy Bypass -Command " [System.Net.ServicePointManager]::SecurityProtocol = 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))" && SET "PATH=%PATH%;%ALLUSERSPROFILE%\chocolatey\bin"
	refreshenv
	net user administrator /active:yes

	REM set necessary Registry Keys
    echo "Disabling Windows Privacy Dialog"
    reg ADD HKEY_LOCAL_MACHINE\SOFTWARE\policies\Microsoft\Windows\OOBE /v DisablePrivacyExperience /t REG_DWORD /d 1 /f
    echo "Disabling  User Account Control(UAC)"
    reg ADD HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System /v EnableLUA /t REG_DWORD /d 0 /f
    echo "Creating Link to startup Script"
	mklink "%userprofile%\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\startGuestAgent.lnk" %userprofile%\Desktop\fortrace\guest_tools\startGuestAgent.bat

    REM Prerequisites for File recycling via CMD
    REM install necessary package provider
    powershell "Install-PackageProvider -Name NuGet -MinimumVersion 2.8.5.201 -Force"
    REM install module
    powershell "Install-Module -Name Recycle -force"
    REM change necessary execution policy to allow execution
    powershell "Set-ExecutionPolicy RemoteSigned"

    REM further necessary Prerequisites
    echo "Disabling automatic time synchronization"
    reg ADD HKLM\SYSTEM\CurrentControlSet\Services\W32Time\Parameters /v Type /t REG_SZ /d NoSync /f

	refreshenv

	echo "Installing Python 3.7"
	REM start /wait msiexec.exe /i %~dp0python.msi /passive /L*V "C:\msilog.log" ADDLOCAL=ALL ALLUSERS=1
	choco install python3 -y

	REM echo "Installing pip via get-pip.py python script - pip might already be installed via Python 2.7 installation"
	REM python %~dp0get-pip.py

	echo "Installing Visual C++ Python Compiler. This may take a while"
	choco install microsoft-build-tools -y --ignore-dependencies
	REM start /wait msiexec.exe /i %~dp0VCForPython27.msi /passive /L*V "C:\msilog2.log"
	REM choco install visualstudio2019buildtools -y --ignore-dependencies
	choco install visualcpp-build-tools -y --ignore-dependencies
	REM this part has to be done manually as of right now

	echo "Installing Firefox"
	choco install firefox -y

	echo "Installing Thunderbird"
	choco install thunderbird -y

	echo "Installing Veracrypt"
	choco install veracrypt -y

	refreshenv

	echo "run prereq fortrace script"
	REM IF p2 is also installed use this: python3 %~dp0pre_setup.py


	REM echo installing fortrace sources.
        python %~dp0pre_setup.py
    REM   echo Installation finished.
	
	echo "Installation finished. Currently, there is a manual step needed.Please visit visualstudio.microsoft.com/visual-cpp-build-tools and download those manually. Afterward, run pip install netifaces."
	pause > nul
	exit

) else (
	echo "Failure: Script not run with admin rights. Please run this script with admin permissions"
	pause > nul
	exit
)


cmd /k

popd
