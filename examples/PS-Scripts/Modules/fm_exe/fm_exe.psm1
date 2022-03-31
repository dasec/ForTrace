$SkriptVersion = "0.9, 30.01.2022"
#requires -version 5.1
#Requires -RunAsAdministrator
<#MIT Licence
Copyright 2021 Florian Mann
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#>

<# Exe install / uninstall Functions

 
.SYNOPSYS
 Installs Exe with supplied arguments
 Uninstalls Exe with supplied arguments

.NOTES
 
 Requirements: 
      Elevated Rights
 Silent Install commands vary depending on the program and the installer used. 

.Sources

.TODO
 Notes:

 Ideas:

 Possible improvements:
    
 To be done..
  - Verbose Mode for reporting
  - Logging: Add-fmLogEntry
  - checks success
 
 Uninstall via Softwarename match in registry and its uninstall string
    $FirefoxUninstallString = ((Get-ChildItem HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\ | ? { $_ -match "Firefox" } | Get-ItemProperty -Name UninstallString).UninstallString) -replace '"',''

 Include Software inventory function from SOFTWARETOOL?


 Critical Errors:
    - None known
         
.CHANGELOG
    0.9
        - First release based on MSI Module
#>

<# Example calls
$result = Install-fmExe -ExeFilePath $ExeFilePath

$result = Uninstall-fmExe -ExeFilePath $ExeFilePath

#>

#Variables
$RegistryUninstallPaths = @(
    "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
    "HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall",
    "HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall"
    )

$Script:LogEntryID = 1
$Script:LogEntrys = @()

#Interactive Mode for artefact collection
    $interactive = $true

#Functions

function Add-fmLogEntry {
param (
        [parameter(Mandatory=$true, HelpMessage='Logging Modus.')]
        [ValidateSet("ExitCodeOnly","Error","Info")]
        [String]
        $LoggingType,
        [parameter(Mandatory=$true, HelpMessage='Logging Message.')]
        [ValidateNotNullOrEmpty()]
        [String]
        $LoggingMessage
      )
      
      #Build Log Entry
          $LogEntry = @{}
      
      #Only if Logging Type is not ExitCodeOnly
      if($LoggingType -ne "ExitCodeOnly")
      {
          $LogEntry += ("$LoggingType")

          switch($LoggingType)
          {
            "ExitCodeOnly" {}
            "Error" {$Script:LogEntrys += "Error..."}
            "Info" {$Script:LogEntrys += "Info..."}
          }
          $Script:LogEntryID++
          return $LogEntry
      }
}

function Install-fmExe {
[cmdletbinding(SupportsShouldProcess)] #Include Verbose/Whatif/Confirm Switch
param (
        [parameter(Mandatory=$false, HelpMessage='Logging Modus.')]
        [ValidateSet("ExitCodeOnly","ErrorMessages","InfoMessages")]
        [String]
        $LoggingModus = "ExitCodeOnly",        
        [parameter(Mandatory=$true, HelpMessage='Fullpath to the Exe file')]
        [ValidateNotNullOrEmpty()] [System.IO.FileInfo]
        $ExeFilePath,
        [parameter(Mandatory=$false, HelpMessage='OPTIONAL - Additional arguments to pass to the Exe Installer. Possible values: single string or array of strings. Example: /L')]
        [System.String]
        $ExeAdditionalArgugments
      )
    #Error Codes:
        #2: Exe file does not exist
        #3: Error during installation

    if($interactive)
    {
        #Collect EventLog Artifacts
        [System.DateTime]$StartTime = Get-Date 
    }
            $ExeFileExist = Test-Path $ExeFilePath
            if($ExeFileExist)
            {
                #Exe Arguments
                    $ExeArguments = @()  
                    if($ExeAdditionalArgugments -notcontains "/silent")
                    { $ExeArguments += "/s" }
                    #Add additional arguments passed to function
                        foreach($argument in $ExeAdditionalArgugments)
                        { $ExeArguments += $argument }              
                
                try
                {
                    #Exe installation
                        Start-Process -FilePath "$($ExeFilePath)" -ArgumentList "$($ExeArguments)" -NoNewWindow -Wait
                        if( $LASTEXITCODE -eq 0 -or [string]::IsNullOrEmpty($LASTEXITCODE) ) 
                        { Write-Output "Command executed successfully" } 
                        else 
                        {
	                        Write-Output "Exe installer failed"
                            return 3 #3: Error during installation
                        }
                }
                catch { Write-Warning -Message $_.Exception.Message ; return 3 } 


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
                    Read-Host "Continue?"
                }

                return 0 #Successful
            }
            else
            { return 2 } #Exe file does not exist
}

function Uninstall-fmFromProductCodeUninstallString {
param (
        [parameter(Mandatory=$true, HelpMessage='Productcode for which the uninstall string ist searched')]
        [ValidateNotNullOrEmpty()] [System.IO.FileInfo]
        $ProductCode
      )
    #Error Codes:
        #1: Product is not installed
        #2: Error uninstalling

    if($interactive)
    {
        #Collect EventLog Artifacts
        [System.DateTime]$StartTime = Get-Date 
    }

    #Unistall
        #Check installation
            $CorrectRegistryUninstallPath = ""
            foreach($path in $RegistryUninstallPaths)       
            { 
                $Installed = Test-Path "$($path)\$($ProductCode)"
                if($Installed)
                { 
                    $CorrectRegistryUninstallPath = "$($path)\$($ProductCode)"
                    break #Leave Foreach -> Product code was found
                } 
            }
            if(!$Installed)
            { return 1 } #1: Product is not installed
            
            $ExeFilePath = (Get-ItemProperty $CorrectRegistryUninstallPath -Name UninstallString).UninstallString
        
        #ExeArguments
        $ExeArguments = @(
            "/S"
            )
            
        try
        {
            #Exe deinstallation
            Start-Process -FilePath "$($ExeFilePath)" -ArgumentList "$($ExeArguments)" -NoNewWindow -Wait
            if( $LASTEXITCODE -eq 0 -or [string]::IsNullOrEmpty($LASTEXITCODE) ) 
            { Write-Output "Command executed successfully" } 
            else 
            {
	            Write-Output "Exe uninstall failed"
                return 2 #2: Error during installation
            }
        }
        catch { Write-Warning -Message $_.Exception.Message ; return 3 } 
        
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
            Read-Host "Continue?"
        }

        return 0 #Successful
}

function Uninstall-fmExe {
param (
        [parameter(Mandatory=$true, HelpMessage='Fullpath to the Exe file')]
        [ValidateNotNullOrEmpty()] [System.IO.FileInfo]
        $ExeFilePath
      )
    #Error Codes:
        #1: Product is not installed
        #2: Error uninstalling

    if($interactive)
    {
        #Collect EventLog Artifacts
        [System.DateTime]$StartTime = Get-Date 
    }

    $ExeFileExist = Test-Path $ExeFilePath
    if(!$ExeFileExist)
    { return 2 } #Exe file does not exist
    #Unistall
        #ExeArguments
        $ExeArguments = @(
            "/S"
            )
            
        try
        {
            #Exe deinstallation
            Start-Process -FilePath "$($ExeFilePath)" -ArgumentList "$($ExeArguments)" -NoNewWindow -Wait
            if( $LASTEXITCODE -eq 0 -or [string]::IsNullOrEmpty($LASTEXITCODE) ) 
            { Write-Output "Command executed successfully" } 
            else 
            {
	            Write-Output "Exe uninstall failed"
                return 2 #2: Error during installation
            }
        }
        catch { Write-Warning -Message $_.Exception.Message ; return 3 } 
        
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
            Read-Host "Continue?"
        }

        return 0 #Successful
}

#Uninstall-fmExe -ExeFilePath $FirefoxUninstallString