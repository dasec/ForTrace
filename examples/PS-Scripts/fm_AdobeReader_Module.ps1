$SkriptVersion = "0.1, 28.11.2021"
#requires -version 5.1
<#MIT Licence
Copyright 2021 Florian Mann
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#>

<# Adobe Reader Forensic Tool

 
.SYNOPSYS
 Adobe Reader Install, uninstall and check expected artifacts on local machine

.NOTES
     
 Requirements: 
      Elevated Rights????

.Sources


.TODO
 Notes:

 Ideas:
    - Installation Adobe Reader WebInstaller
        - check artifiacts
        - document artifacts
    - open pdfs

 Possible improvements:
    
 To be done:

 Critical Errors:
    - None known
         
.CHANGELOG
    0.1
        - First release
#>


<#
    #Check artifacts
    #WMI (MSI Only)
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
                #1033 -> Install success
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
            
    #Services
        Get-Service | Where-Object {$_.Name -eq "MozillaMaintenance"}

    #Folders
        Test-Path "$env:APPDATA\Mozilla\" # Only after first program start
        Test-Path "C:\Program Files\Mozilla Firefox\"

    #Sheduled Tasks
        Get-ScheduledTask
            #>
    #>
function Install-fmAdobeReader {
param (
  [parameter(Mandatory=$false, HelpMessage='Browser Langugage.')]
  [ValidateSet("en","de")]
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
    #Exe/MSI
        #Download with default Browser
            #Language Selection
                $AdobeReader_Language_Selection = $Language_Selection #en, de
                
            #Installation Types
                $AdobeReader_Install_Type = $Install_Type #MSI, EXE, WEB
                $AdobeReader_WebInstall_Executable = "$($env:USERPROFILE)\Downloads\readerdc64_$($AdobeReader_Language_Selection)_xa_install.exe"

                if($AdobeReader_Install_Type -eq "WEB")
                { 
                    $AdobeReader_Download_URL = "https://admdownload.adobe.com/bin/live/readerdc64_$($AdobeReader_Language_Selection)_xa_install.exe"
                    $AdobeReader_Install_Executable = $Adobe_WebInstall_Executable                
                }

            #Open pre downlaod page
            if($interactive)
            { Write-Host "Starting download ..." }
            if($AdobeReader_Install_Type -eq "WEB")
            {
                #WEB
                Start-Process "https://duckduckgo.com/?q=adobe+reader" -PassThru #Search for "Adobe Reader" on DuckDuckGo.com (Browser preferred language)
                    Sleep -Seconds (Get-Random -Minimum 2 -Maximum 7)
                Start-Process "https://get.adobe.com/reader/?loc=$($AdobeReader_Language_Selection)" -PassThru #Opens Adobe Reader download page. -> "Download options and other languages"
                    Sleep -Seconds (Get-Random -Minimum 2 -Maximum 7)
            }
            else
            {
                #EXE/MSI
            }
            
            #Get current/failed downloads 
                $PreDownloadsCount = (Get-ChildItem -Path "$($env:USERPROFILE)\Downloads\*" -Include "crdownload").Count #Chrome/Edge creates .crdownload file for each unfinished download
            #open download page
            Start-Process $AdobeReader_Download_URL # Edge will automatically download Adobe Reader Setup
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
            if($interactive)
            { Write-Host "Opening Explorer with download selected ..." }

            #Open Explorer select file, to generate artifacts, for example Thumbnails
            #Parameters to launch explorer.exe with
            $Params = @()
                $Params += "/select,"
                $Params += "$($Adobe_Install_Executable)"
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
        #Run Installer
            if($interactive)
            { Write-Host "Running installer ..." }                
            #Run
            #"Adobe Installer.exe"
                #RUNAS ADMIN
                switch($Adobe_Install_Type)
                {
                    
                    "EXE" { $InstallExitCode = Start-Process  $Adobe_Install_Executable -ArgumentList "/S" -Verb RunAs -Wait } #No passive option (silent with GUI) available
                        "MSI" { $InstallExitCode = Start-Process msiexec.exe -ArgumentList "/i ""$($Adobe_Install_Executable)"" /passive" -Wait } 
                        "WEB" { $InstallExitCode = Start-Process  $Adobe_Install_Executable -Verb RunAs } #Wait does not work for WEB Installer
                    #EXE                
                    #MSI
                    #WEB
                        #INSTALLS ON FIRST INSTALL WITHOUT INTERACTION
                        #QUITS AFTER FIRST INSTALL WHEN PRESSING ESC
                        #STARTS ADOBE WITH BLOCKING QUESTIONS
                    }
                    #Wait for WEB installer to complete
                    if($Adobe_Install_Type -eq "WEB")
                    {
                        if($interactive)
                        { Write-Host "Waiting for WEB installer to finish and firefox to open..." } 
                        $i=0
                        do{
                            Sleep -Seconds 1
                            $tempAdobeafterinstallstarted = (Get-Process | Where-Object { $_.MainWindowTitle -and $_.ProcessName -eq "firefox" }).Count
                            $i++
                        }until(($tempAdobeafterinstallstarted -gt 0) -or $i -gt 600 ) #Wait max for 10 Minutes
                    }
                    Write-host $InstallExitCode 
                    Write-host $InstallExitCode.ExitCode 
                    if($InstallExitCode.ExitCode -ne 0)
                    { if($interactive) {Write-Host "Installation process returned error code: $($p.ExitCode)"} }
                    else
                    { if($interactive) {Write-Host "Installation successfull"} }
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
        #Close Adobe after installation
            #Only for WEB
            if($Adobe_Install_Type -eq "WEB")
            {
                if($interactive)
                { Write-Host "Closing Adobe first start window ..." }
                Sleep -Seconds (Get-Random -Minimum 15 -Maximum 25)
                $wshell = New-Object -ComObject wscript.shell
                $AdobeMainWindowTitles = (Get-Process |  Where-Object { $_.MainWindowTitle -and $_.ProcessName -eq "Adobe" } | Select-Object MainWindowTitle).MainWindowTitle
                foreach($AdobeMainWindowTitle in $AdobeMainWindowTitles)
                {
                    $wshell.AppActivate($AdobeMainWindowTitle)
                    Sleep -Seconds 1
                    $wshell.SendKeys("%{F4}") #Close Window
                }
            }

#Optional: Disable  questions

    if($interactive)
    {
        #Collect EventLog Artifacts
        [System.DateTime]$EndTime = Get-Date 
        Write-Host "Event Logs during installation: $StartTime  -   $EndTime"
        $EventFilter = @{logname = "System"; StartTime=$StartTime; EndTime=$EndTime}
        Get-WinEvent -FilterHashTable $EventFilter -ErrorAction SilentlyContinue
        Write-Host "Event Logs during installation:"
        $EventFilter = @{StartTime=$StartTime; EndTime=$EndTime}
        Get-WinEvent -FilterHashTable $EventFilter -ErrorAction SilentlyContinue



        Write-Host "Event Logs during installation:"
        Get-WinEvent -ListLog * -EA silentlycontinue | where-object { $_.recordcount -AND $_.TimeCreated -gt $StartTime -AND $_.TimeCreated -lt $EndTime} | foreach-object { get-winevent -LogName $_.logname -MaxEvents 100 } | Format-Table TimeCreated, ID, ProviderName, Message -AutoSize –Wrap
    }
}

#Uninstall
    #https://www.osforensics.com/faqs-and-tutorials/identifying_uninstalled_software.html

Install-fmAdobeReader -Language_Selection de -Install_Type WEB
