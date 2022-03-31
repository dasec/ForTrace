#Funktion Download von Software -> switch google/duckduckgo, URL Array
#Funktion Installation Software
    #-> Adobe, Chrome/Firefox
#Funktion Uninstall Software -> Welche Reste bleiben übrig (Registry/EventLogs/Dateisystem)
#Funktion Windows Suche -> Welche Artefakte werden dabei erzeugt (JumpList)


$SkriptVersion = "0.2, 19.02.2022"
#requires -version 5.1
<#MIT Licence
Copyright 2021 Florian Mann
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#>

<# Firefox Forensic Tool

 
.SYNOPSYS
 Firefox Install, uninstall and check expected artifacts on local machine

.NOTES
     
 Requirements: 
      Elevated Rights

.Sources
    https://support.mozilla.org/en-US/kb/deploy-firefox-msi-installers
    https://firefox-source-docs.mozilla.org/browser/installer/windows/installer/FullConfig.html

.TODO
 Notes:

 Ideas:
    - Installation Firefox WebInstaller
        - check artifiacts
        - document artifacts

    - Logins
    - Downloads
    - Seiten aufrufen
    - Interagieren mit HTML Elementen (Browsen/Klicken)
    - Documentation module
    - Forensics: https://nasbench.medium.com/web-browsers-forensics-7e99940c579a

 Possible improvements:
    
 To be done:
  - Reporting
  - Hashvalues for downloads
  -	Most Recently Used Registry
  -	User Assist -> wann geöffnet, counter
  -	PowerShell Logs deaktivieren möglich?
  -	Google Suche mit einbauen (DuckDuckgo)
  -	Übergabe der Artefakte per String an den Reporter (Minimal/Detailed Switch)
  - Switch Start Software

 Critical Errors:
    - None known
         
.CHANGELOG
    0.1
        - First release
    0.2 
        - Converted to function
#>

#Functions
function Test-WildcardPath($Path) {
    $count = (Get-ChildItem $Path -ErrorAction SilentlyContinue).count
    if($count -ge 0)
        { return $true }
    else
        { return $false }
}

#Check Edge Version
    #(Get-AppxPackage -Name "Microsoft.MicrosoftEdge.Stable").Version

<#
    #Check artifacts
    #WMI (MSI Only) returns only products installed by Windows Installer
        Get-WmiObject -Class Win32_Product | Where-Object {$_.Vendor -eq "Mozilla" } | select Name, Version
            #Not for Webinstaller?

    #Registry (From Uninstall Key)
        #Web Installer
            $InstalledSoftwareRegistryPath = "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*"  #64-Bit Applikationen auf 64-Bit Systemen und 32-Bit Applikationen auf 32-Bit Systemen. 32 Bit vorhanden-ralrke??
            $InstalledSoftwareRegistryPath32Biton64BitSystem = "HKLM:\SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*" #32-Bit Applikationen auf 64-Bit Systemen.

            $ArraySoftware = New-Object -TypeName "PSCustomObject[]" -ArgumentList (1)

            if(Test-Path $InstalledSoftwareRegistryPath32Biton64BitSystem)
            #Read both registry keys
            { $ArraySoftware= (((Get-ItemProperty $InstalledSoftwareRegistryPath) + (Get-ItemProperty $InstalledSoftwareRegistryPath32Biton64BitSystem)) | Select-Object -Property "DisplayName", "Publisher", "DisplayVersion" | Where-Object {$_.DisplayName -and $_.Publisher -eq "Mozilla"}) }
            else
            #Only read second registry path
            { $ArraySoftware= ((Get-ItemProperty $InstalledSoftwareRegistryPath) | Select-Object -Property "DisplayName", "Publisher", "DisplayVersion", "Optional" | Where-Object {$_.DisplayName -and $_.Publisher -eq "Mozilla"}) }

            $Installed_Firefox_Registry = Get-ChildItem "HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall" -ErrorAction SilentlyContinue | Where-Object {$_.Name -like "*Firefox*"}
            if($Installed_Firefox_Registry)
            { $Installed_Firefox_Registry_Version = $Installed_Firefox_Registry.GetValue("DisplayVersion") }
            if(!([string]::IsNullOrEmpty($Installed_Firefox_Registry_Version)))
            { Write-Host "Firefox $($Installed_Firefox_Registry_Version) is installed." }
            else
            { Write-Host "Firefox is not installed." }


    #EventLog
            Get-WinEvent -ProviderName msiinstaller | Where-Object {$_.Message -match "Firefox"} | select timecreated,message | FL *
                #1033 -> Install success (1022 Update, 1034 removal)
                #1040 -> Windows installer transaction started
                #1042  -> Windows installer transaction ended
                #11707 -> Install success
                #Installed through which user?
                $EventLogSID = "S-1-5-21-2935588272-1152158150-3235950038-500"
                    $objSID = New-Object System.Security.Principal.SecurityIdentifier($EventLogSID) 
                    $objUser = $objSID.Translate( [System.Security.Principal.NTAccount]) 
                    $objUser.Value

            Get-WinEvent -ProviderName "Service Control Manager" | Where-Object {$_.Message -match "Mozilla" -and $_.Id -eq 7045 } | select timecreated,message | FL *

            Get-WinEvent -LogName "Microsoft-Windows-PowerShell/Operational" | Where-Object {$_.Message -match "firefox" -and $_.Id -eq 24578 } | select timecreated,message | FL *

            Get-WinEvent -LogName "Application" | Where-Object {$_.Id -eq 1332 } | select timecreated,message,ProviderName | FL *
            Get-WinEvent -LogName "Application" | Where-Object {$_.ProviderName -eq "Firefox Default Browser Agent" } | select -property * | FL *
            
    #Services
        Get-Service | Where-Object {$_.Name -eq "MozillaMaintenance"}

    #Folders
        Test-Path "$env:APPDATA\Mozilla\" # Only after first program start
        Test-Path "C:\Program Files\Mozilla Firefox\"

    #Sheduled Tasks
        Get-ScheduledTask | where-object {$_.TaskName -match "firefox" -or $_.TaskPath -match "Mozilla" }
            #>
    #>
function Install-fmFirefoxBrowser {
param (
  [parameter(Mandatory=$false, HelpMessage='Browser Langugage.')]
  [ValidateSet("en-US","de")]
  [String]
  $Language_Selection = "de",
  [parameter(Mandatory=$false, HelpMessage='Installation Type (EXE, MSI, WEB Installer).')]
  [ValidateSet("MSI","EXE","WEB")]
  [String]
  $Install_Type = "WEB"
      )

$interactive = $true

#Install
    if($interactive)
    {
        #Collect EventLog Artifacts
        [System.DateTime]$StartTime = Get-Date 
    }

#Disable Edge First Run
    $RegKeyPath = “HKLM:\Software\Policies\Microsoft\Edge”
    if(!(Test-Path $RegKeyPath))
    { New-Item -Path $RegKeyPath -Force | Out-Null }
    New-ItemProperty -Path $RegKeyPath -Name "HideFirstRunExperience" -Value "1" -PropertyType DWORD -Force | Out-Null

    #Exe/MSI
        #Download with Edge Browser
            #Language Selection
                $Firefox_Language_Selection = $Language_Selection #en-US, de
                
            #Installation Types
                $Firefox_Install_Type = $Install_Type #MSI, EXE, WEB
                $Firefox_ExeMsiInstall_Executable = "$($env:USERPROFILE)\Downloads\Firefox Setup*"
                $Firefox_WebInstall_Executable = "$($env:USERPROFILE)\Downloads\Firefox Installer.exe"
                    #https://www.mozilla.org/en-US/firefox/all/#product-desktop-release
                    #https://download.mozilla.org/?product=firefox-latest-ssl&os=win64&lang=en-US

                    #https://www.mozilla.org/de/firefox/all/#product-desktop-release
                    #https://download.mozilla.org/?product=firefox-latest-ssl&os=win64&lang=de
                    #https://download.mozilla.org/?product=firefox-msi-latest-ssl&os=win64&lang=de
                if($Firefox_Install_Type -eq "MSI")
                { 
                    $Firefox_Download_URL = "https://download.mozilla.org/?product=firefox-msi-latest-ssl&os=win64&lang=$($Firefox_Language_Selection)" 
                    $Firefox_Install_Executable = $Firefox_ExeMsiInstall_Executable
                }
                elseif($Firefox_Install_Type -eq "EXE") #EXE
                { 
                    $Firefox_Download_URL = "https://download.mozilla.org/?product=firefox-latest-ssl&os=win64&lang=$($Firefox_Language_Selection)" 
                    $Firefox_Install_Executable = $Firefox_ExeMsiInstall_Executable
                }
                else #WebInstaller or wrong type
                {
                    $Firefox_Download_URL = "https://www.mozilla.org/$($Firefox_Language_Selection)/firefox/download/thanks/"
                    $Firefox_Install_Executable = $Firefox_WebInstall_Executable
                }
            #Open pre downlaod page
            if($interactive)
            { Write-Host "Starting download ..." }
            if($Firefox_Install_Type -ne "WEB")
            {
                $Firefox_MsiExe_URLs = @()
                    $Firefox_MsiExe_URLs += "https://www.mozilla.org/$($Firefox_Language_Selection)/"
                    $Firefox_MsiExe_URLs += "https://www.mozilla.org/$($Firefox_Language_Selection)/firefox/new/"
                    $Firefox_MsiExe_URLs += "https://www.mozilla.org/$($Firefox_Language_Selection)/firefox/all/#product-desktop-release"
                
                #MSI / EXE
                Start-Process microsoft-edge:"https://www.mozilla.org/$($Firefox_Language_Selection)/" #Opens Mozilla start page.
                    Sleep -Seconds (Get-Random -Minimum 2 -Maximum 7)
                Start-Process microsoft-edge:"https://www.mozilla.org/$($Firefox_Language_Selection)/firefox/new/" #Opens Firefox page. -> "Download options and other languages"
                    Sleep -Seconds (Get-Random -Minimum 2 -Maximum 7)
                Start-Process microsoft-edge:"https://www.mozilla.org/$($Firefox_Language_Selection)/firefox/all/#product-desktop-release" #Opens Firefox exe download selection page.
                    Sleep -Seconds (Get-Random -Minimum 7 -Maximum 15)
            }
            else
            {
                #WEB
                    Start-Process microsoft-edge:"https://www.mozilla.org/$($Firefox_Language_Selection)/"  #Opens Mozilla start page.
                    Sleep -Seconds (Get-Random -Minimum 2 -Maximum 7)
            }
            
            #Get current/failed downloads 
                $PreDownloadsCount = (Get-ChildItem -Path "$($env:USERPROFILE)\Downloads\*" -Include "crdownload").Count #Chrome/Edge creates .crdownload file for each unfinished download
            #open download page
            Start-Process microsoft-edge:$Firefox_Download_URL # Edge will automatically download Firefox Setup VERSIONNUMBER.exe
            $i = 0
            $filedownloaded = $false
            $downloadstarted = $false
            do
            {
                Sleep -Milliseconds 100 #Wait 100 Milliseconds
                $DownloadsCount = (Get-ChildItem -Path "$($env:USERPROFILE)\Downloads\*" -Include *.crdownload).Count
                if(($PreDownloadsCount -lt $DownloadsCount) -and !$downloadstarted)
                { $downloadstarted = $true }
                elseif($downloadstarted -and ($PreDownloadsCount -eq $DownloadsCount))
                { 
                    $filedownloaded = $true 
                    Sleep -Seconds (Get-Random -Minimum 7 -Maximum 15)
                }
                $i++
            }while(!$filedownloaded -and $i -le 3000) #Wait for about 5 Minutes for download to finish
            if($interactive)
            { Write-Host "Downloaded or Error ..." }

            #quit all open edge windows
            if($interactive)
            { Write-Host "Closing all open edge windows ..." }

            $wshell = New-Object -ComObject wscript.shell
            $EdgeMainWindowTitles = (Get-Process |  Where-Object { $_.MainWindowTitle -and $_.ProcessName -eq "msedge" } | Select-Object MainWindowTitle).MainWindowTitle
            foreach($EdgeMainWindowTitle in $EdgeMainWindowTitles)
            {
                $wshell.AppActivate($EdgeMainWindowTitle)
                Sleep -Seconds 1
                $wshell.SendKeys("%{F4}") #Close Window
            }
            <#
            #Get parent process ids and quit all remaining open edge windows
            $ParentProcessIds = Get-CimInstance -Class Win32_Process -Filter "Name = 'msedge.exe'" #WMI does not need elevated rights
            if($ParentProcessIds)
            { 
                foreach($id in $ParentProcessIds)
                { 
                Get-Process -Id $id.ProcessId  -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue 
                #Get-Process -Id $id.ParentProcessId  -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue 
                }
            }
            #>
        if($filedownloaded)
        {
            if($Firefox_Install_Type -eq "MSI")
            { $Firefox_Install_Executable = (Get-Item $Firefox_ExeMsiInstall_Executable -Include "*.msi" | Sort-Object -Property LastWriteTime -Descending)[0].FullName }     
            if($Firefox_Install_Type -eq "EXE")
            { $Firefox_Install_Executable = (Get-Item $Firefox_ExeMsiInstall_Executable -Include "*.exe" | Sort-Object -Property LastWriteTime -Descending)[0].FullName }     
            if($interactive)
            { Write-Host "Opening Explorer with download selected ..." }

            #Open Explorer select file, to generate artifacts, for example Thumbnails
            #Parameters to launch explorer.exe with
            $Params = @()
                $Params += "/select,"
                $Params += "$($Firefox_Install_Executable)"
            Start-Process explorer.exe $Params 
            $explorerwindowsstarted = $false
            $i = 0
            do
            {
                Start-Sleep -Seconds 1
                $explorerwindowsstartedtitle = Get-Process -Name explorer | Where-Object {$_.MainWindowTitle -eq "Downloads"}
                if($explorerwindowsstartedtitle.MainWindowTitle -eq "Downloads")
                    {$explorerwindowsstarted = $true}
                $i++
            }while(($explorerwindowsstarted -eq $false) -and ($i -lt 15))        
        #Run Installer (All with elevated rights)
            $CurrentUserIsAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")
            if($CurrentUserIsAdmin)
            {
                if($interactive)
                { Write-Host "Running installer ..." }                
                #Run
                #"Firefox Installer.exe"
                    #RUNAS ADMIN
                    switch($Firefox_Install_Type)
                    {
                        #https://support.mozilla.org/en-US/kb/silently-install-uninstall-firefox-enterprise
                        "EXE" { $InstallExitCode = Start-Process $Firefox_Install_Executable -ArgumentList "/S" -Verb RunAs -Wait } #No passive option (silent with GUI) available
                        "MSI" { $InstallExitCode = Start-Process msiexec.exe -ArgumentList "/i ""$($Firefox_Install_Executable)"" /passive" -Wait } 
                        "WEB" { $InstallExitCode = Start-Process $Firefox_Install_Executable -Verb RunAs } #Wait does not work for WEB Installer
                    #EXE
                        #INSTALLS ON EVERY INSTALL WITHOUT INTERACTION
                        #QUITS AFTER INSTALL WITHOUT INTERACTION
                        #DOES NOT START FIREFOX                    
                    #MSI
                        #INSTALLS ON FIRST INSTALL WITHOUT INTERACTION, ASK QUESTIONS ON > FIRST INSTALL
                        #QUITS AFTER INSTALL WITHOUT INTERACTION
                        #START FIREFOX
                    #WEB
                        #INSTALLS ON FIRST INSTALL WITHOUT INTERACTION, ASK QUESTIONS ON > FIRST INSTALL
                        #QUITS AFTER FIRST INSTALL WITHOUT INTERACTION
                        #STARTS FIREFOX
                    
                    
                    }
                    #Wait for WEB installer to complete
                    if($Firefox_Install_Type -eq "WEB")
                    {
                        if($interactive)
                        { Write-Host "Waiting for WEB installer to finish and firefox to open..." } 
                        $i=0
                        do{
                            Sleep -Seconds 1
                            $tempfirefoxafterinstallstarted = (Get-Process | Where-Object { $_.MainWindowTitle -and $_.ProcessName -eq "firefox" }).Count
                            $i++
                        }until(($tempfirefoxafterinstallstarted -gt 0) -or $i -gt 600 ) #Wait max for 10 Minutes
                    }
                    if($InstallExitCode.ExitCode)
                    { if($interactive -and $p.ExitCode) {Write-Host "Installation process returned error code: $($p.ExitCode)" -ForegroundColor Red} }
                    else
                    { if($interactive) {Write-Host "Installation successfull" -ForegroundColor Green} }
            }
            else
            { Write-Host "User is not Admin, elevated start of Firefox Installer not possible" -ForegroundColor Red } #Return Code???
        }
        else
        { Write-Host "Download failed within 60 seconds ..." -ForegroundColor Red }

        #quit all open explorer windows
            if($interactive)
            { Write-Host "Closing Downloads explorer windows ..." }
            $wshell = New-Object -ComObject wscript.shell
            $ExplorerMainWindowTitles = (Get-Process |  Where-Object { $_.MainWindowTitle -eq "Downloads" -and $_.ProcessName -eq "explorer" } | Select-Object MainWindowTitle).MainWindowTitle
            foreach($EdgeMainWindowTitle in $EdgeMainWindowTitles)
            {
                $wshell.AppActivate("Downloads")
                Sleep -Seconds 1
                $wshell.SendKeys("%{F4}") #Close Window
            }
        #Close Firefox after installation
            #Only for WEB
            if($Firefox_Install_Type -eq "WEB")
            {
                if($interactive)
                { Write-Host "Closing firefox first start window ..." }
                Sleep -Seconds (Get-Random -Minimum 15 -Maximum 25)
                $wshell = New-Object -ComObject wscript.shell
                $FirefoxMainWindowTitles = (Get-Process |  Where-Object { $_.MainWindowTitle -and $_.ProcessName -eq "firefox" } | Select-Object MainWindowTitle).MainWindowTitle
                foreach($FirefoxMainWindowTitle in $FirefoxMainWindowTitles)
                {
                    $wshell.AppActivate($FirefoxMainWindowTitle)
                    Sleep -Seconds 1
                    $wshell.SendKeys("%{F4}") #Close Window
                }
            }

#Optional: Disable default Browser question
    #SendKeys {ESC} should work 

    if($interactive)
    {
        #Collect EventLog Artifacts
        [System.DateTime]$EndTime = Get-Date 
        Write-Host "System Event Logs during installation: $StartTime  -   $EndTime"
        $EventFilter = @{LogName = "System"; StartTime=$StartTime; EndTime=$EndTime}
        Get-WinEvent -FilterHashTable $EventFilter -ErrorAction SilentlyContinue
        Write-Host "Application Event Logs during installation:"
        $EventFilter = @{StartTime=$StartTime; EndTime=$EndTime; LogName="Application" }
        Get-WinEvent -FilterHashTable $EventFilter -ErrorAction SilentlyContinue | Format-Table TimeCreated, ID, ProviderName, Message -AutoSize –Wrap
        
        Write-Host "PowerShell Event Logs during installation:"
        $EventFilter = @{StartTime=$StartTime; EndTime=$EndTime; LogName="Windows PowerShell","Microsoft-Windows-PowerShell/Operational","Setup" }
        Get-WinEvent -FilterHashTable $EventFilter -ErrorAction SilentlyContinue | Format-Table ProviderName, TimeCreated, ID, Message -AutoSize –Wrap

        #OLD
            #Write-Host "Event Logs during installation:"
            #Get-WinEvent -ListLog * -EA silentlycontinue | where-object { $_.recordcount -AND $_.TimeCreated -gt $StartTime -AND $_.TimeCreated -lt $EndTime} | foreach-object { get-winevent -LogName $_.logname -MaxEvents 100 } | Format-Table TimeCreated, ID, ProviderName, Message -AutoSize –Wrap

    }
}

#Uninstall
    #https://www.osforensics.com/faqs-and-tutorials/identifying_uninstalled_software.html

#Install-fmFirefoxBrowser -Language_Selection en-US -Install_Type WEB

#Install-fmFirefoxBrowser -Language_Selection en-US -Install_Type EXE

#Install-fmFirefoxBrowser -Language_Selection en-US -Install_Type MSI