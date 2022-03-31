$SkriptVersion = "0.1, 19.02.2022"
#requires -version 5.1
<#MIT Licence
Copyright 2021 Florian Mann
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#>

<# Chrome Forensic Tool

 
.SYNOPSYS
 Chrome Install, uninstall and check expected artifacts on local machine

.NOTES

    Language only supported for MSI
     
 Requirements: 
      Elevated Rights
      Edge First Run should be disabled

.Sources
    https://support.google.com/chrome/a/answer/3115278#

    #MSI
    https://docs.microsoft.com/en-us/windows/win32/msi/command-line-options

.TODO
 Notes:
     Name                           Value                                                                                                                             
    ----                           -----                                                                                                                             
    Manufacturer                   Google LLC                                                                                                                        
    ProductName                    Google Chrome                                                                                                                     
    ProductLanguage                1033                                                                                                                              
    ProductVersion                 68.165.32870                                                                                                                      
    ProductCode                    {809F21F9-8D3A-3376-BC28-CD19E26DA000}

 Ideas:
    - Chrome
        - check artifiacts
        - document artifacts

    - Logins
    - Downloads
    - Seiten aufrufen
    - Interagieren mit HTML Elementen (Browsen/Klicken)
    - Documentation module
    - Forensics: https://nasbench.medium.com/web-browsers-forensics-7e99940c579a

    - (new-object    System.Net.WebClient).DownloadFile($url, $output)
    - https://www.google.com/intl/us/chrome/?platform=win

 Possible improvements:
    
 To be done:
  - Reporting
  - Hashvalues for downloads
  -	Most Recently Used Registry
  -	User Assist -> wann geöffnet, counter
  -	Google Suche mit einbauen (DuckDuckgo)
  -	Übergabe der Artefakte per String an den Reporter (Minimal/Detailed Switch)
  - Switch Start Software

  - Run WEB Installer without elevated rights?

 Critical Errors:
    - None known
         
.CHANGELOG
    0.1
        - First release
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

            $Installed_Chrome_Registry = Get-ChildItem "HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall" -ErrorAction SilentlyContinue | Where-Object {$_.Name -like "*Chrome*"}
            if($Installed_Chrome_Registry)
            { $Installed_Chrome_Registry_Version = $Installed_Chrome_Registry.GetValue("DisplayVersion") }
            if(!([string]::IsNullOrEmpty($Installed_Chrome_Registry_Version)))
            { Write-Host "Chrome $($Installed_Chrome_Registry_Version) is installed." }
            else
            { Write-Host "Chrome is not installed." }


    #EventLog
            Get-WinEvent -ProviderName msiinstaller | Where-Object {$_.Message -match "Chrome"} | select timecreated,message | FL *
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

            Get-WinEvent -LogName "Microsoft-Windows-PowerShell/Operational" | Where-Object {$_.Message -match "chrome" -and $_.Id -eq 24578 } | select timecreated,message | FL *

            Get-WinEvent -LogName "Application" | Where-Object {$_.Id -eq 1332 } | select timecreated,message,ProviderName | FL *
            Get-WinEvent -LogName "Application" | Where-Object {$_.ProviderName -eq "Chrome Default Browser Agent" } | select -property * | FL *
            
    #Services
        Get-Service | Where-Object {$_.Name -eq "MozillaMaintenance"}

    #Folders
        Test-Path "$env:APPDATA\Mozilla\" # Only after first program start
        Test-Path "C:\Program Files\Mozilla Chrome\"

    #Sheduled Tasks
        Get-ScheduledTask | where-object {$_.TaskName -match "chrome" -or $_.TaskPath -match "Mozilla" }
            #>
    #>
function Install-fmChromeBrowser {
param (
  [parameter(Mandatory=$false, HelpMessage='Browser Langugage.')]
  [ValidateSet("en_en","de_de")]
  [String]
  $Language_Selection = "de_de",
  [parameter(Mandatory=$false, HelpMessage='Installation Type (WEB, MSI Installer).')]
  [ValidateSet("MSI","WEB")]
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

    #WEB/MSI
        #Download with Edge Browser
            #Language Selection
                $Chrome_Language_Selection = $Language_Selection #en_en, de_de
                
            #Installation Types
                $Chrome_Install_Type = $Install_Type #MSI, WEB
                $Chrome_WEBInstall_Executable = "$($env:USERPROFILE)\Downloads\ChromeSetup.exe" 
                $Chrome_MSIInstall_Executable = "$($env:USERPROFILE)\Downloads\googlechromestandaloneenterprise64.msi"

                if($Chrome_Install_Type -eq "MSI")
                { 
                    $Chrome_Download_URL = "https://chromeenterprise.google/intl/$($Chrome_Language_Selection)/browser/download/thank-you/?platform=WIN64_MSI&channel=stable&usagestats=0" 
                    $Chrome_Install_Executable = $Chrome_MSIInstall_Executable
                }
                elseif($Chrome_Install_Type -eq "WEB") #WEB
                { 
                    $Chrome_Download_URL = "https://dl.google.com/chrome/install/latest/chrome_installer.exe" 
                    $Chrome_Install_Executable = $Chrome_WEBInstall_Executable
                }

            #Open pre downlaod page
            if($interactive)
            { Write-Host "Starting download ..." }
            if($Chrome_Install_Type -eq "WEB")
            {  
                #WEB
                Start-Process microsoft-edge:"https://www.google.com/" #Opens Google start page.
                    Sleep -Seconds (Get-Random -Minimum 2 -Maximum 7)
                Start-Process microsoft-edge:"https://www.google.com/chrome/?brand=CHZO&utm_source=google.com&utm_medium=desktop-app-launcher&utm_campaign=desktop-app-launcher&utm_content=chrome-logo&utm_keyword=CHZO" #Opens Chrome page. -> "Download options and other languages"
                    Sleep -Seconds (Get-Random -Minimum 2 -Maximum 7)
            }
            else
            {
                #MSI
                    Start-Process microsoft-edge:"https://chromeenterprise.google/"  #Opens Google Enterprise start page
                    Sleep -Seconds (Get-Random -Minimum 2 -Maximum 7)
                    Start-Process microsoft-edge:"https://chromeenterprise.google/intl/$($Chrome_Language_Selection)/"  #Opens localised Google Enterprise start page
                    Sleep -Seconds (Get-Random -Minimum 2 -Maximum 7)
                    Start-Process microsoft-edge:"https://chromeenterprise.google/intl/$($Chrome_Language_Selection)/browser/download/#windows-tab"  #Opens Chrome Version/Architecture selection page
                    Sleep -Seconds (Get-Random -Minimum 2 -Maximum 7)
            }
            
            #Get current/failed downloads 
                $PreDownloadsCount = (Get-ChildItem -Path "$($env:USERPROFILE)\Downloads\*" -Include "crdownload").Count #Chrome/Edge creates .crdownload file for each unfinished download
            #open download page
            Start-Process microsoft-edge:$Chrome_Download_URL # Edge will automatically download Chrome
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

            #Open Download Thank you page
            if($Chrome_Install_Type -eq "WEB")
            {
                #WEB
                    Start-Process microsoft-edge:"https://www.google.com/chrome/thank-you.html?platform=win64&statcb=0&installdataindex=defaultbrowser&defaultbrowser=1#"
                    Sleep -Seconds (Get-Random -Minimum 2 -Maximum 7)
            }
            else
            {
                #MSI
                    Start-Process microsoft-edge:"https://chromeenterprise.google/intl/$($Chrome_Language_Selection)/browser/download/thank-you/"
                    Sleep -Seconds (Get-Random -Minimum 2 -Maximum 7)
            }

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
        if($filedownloaded)
        {
            if($Chrome_Install_Type -eq "MSI")
            { $Chrome_Install_Executable = (Get-Item $Chrome_MsiInstall_Executable -Include "*.msi" | Sort-Object -Property LastWriteTime -Descending)[0].FullName }     
            if($Chrome_Install_Type -eq "WEB")
            { $Chrome_Install_Executable = (Get-Item $Chrome_WEBInstall_Executable -Include "*.exe" | Sort-Object -Property LastWriteTime -Descending)[0].FullName }     
            if($interactive)
            { Write-Host "Opening Explorer with download selected ..." }

            #Open Explorer select file, to generate artifacts, for example Thumbnails
            #Parameters to launch explorer.exe with
            $Params = @()
                $Params += "/select,"
                $Params += "$($Chrome_Install_Executable)"
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
                #"Chrome Installer.exe"
                    #RUNAS ADMIN
                    switch($Chrome_Install_Type)
                    {
                        "WEB" { $InstallExitCode = Start-Process $Chrome_Install_Executable -Verb RunAs -Wait }
                        "MSI" { $InstallExitCode = Start-Process msiexec.exe -ArgumentList "/i ""$($Chrome_Install_Executable)"" /passive" -Wait } 
                    #WEB
                        #INSTALLS ON EVERY INSTALL WITHOUT INTERACTION
                        #QUITS AFTER INSTALL WITHOUT INTERACTION
                        #STARTS CHROME                  
                    #MSI
                        #INSTALLS ON EVERY INSTALL WITHOUT INTERACTION
                        #QUITS AFTER INSTALL WITHOUT INTERACTION
                        #DOES NOT START CHROME       
                    }
                    if($InstallExitCode.ExitCode)
                    { if($interactive -and $p.ExitCode) {Write-Host "Installation process returned error code: $($p.ExitCode)" -ForegroundColor Red} }
                    else
                    { if($interactive) {Write-Host "Installation successfull" -ForegroundColor Green} }
            }
            else
            { Write-Host "User is not Admin, elevated start of Chrome Installer not possible" -ForegroundColor Red } #Return Code???
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
        #Close Chrome after installation
            #Only for WEB
            if($Chrome_Install_Type -eq "WEB")
            {
                if($interactive)
                { Write-Host "Closing chrome first start window ..." }
                Sleep -Seconds (Get-Random -Minimum 15 -Maximum 25)
                $wshell = New-Object -ComObject wscript.shell
                $ChromeMainWindowTitles = (Get-Process |  Where-Object { $_.MainWindowTitle -and $_.ProcessName -eq "chrome" } | Select-Object MainWindowTitle).MainWindowTitle
                foreach($ChromeMainWindowTitle in $ChromeMainWindowTitles)
                {
                    $wshell.AppActivate($ChromeMainWindowTitle)
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
    }
}

#Uninstall
    #https://www.osforensics.com/faqs-and-tutorials/identifying_uninstalled_software.html

#Install-fmChromeBrowser -Language_Selection en_en -Install_Type MSI

#Install-fmChromeBrowser -Install_Type WEB

#Install-fmChromeBrowser -Language_Selection de_de -Install_Type MSI