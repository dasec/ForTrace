$SkriptVersion = "0.9, 30.01.2022"
#requires -version 5.1
#Requires -RunAsAdministrator
<#MIT Licence
Copyright 2021 Florian Mann
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#>

<# MSI install / uninstall Functions

 
.SYNOPSYS
 Installs MSI with supplied arguments and checks success 
 Uninstalls MSI with supplied arguments and checks success 

.NOTES
    Product Code from MSI is not always used for Uninstall Registry Entry (e.g. Firefox uses Firefox... as Uninstall String)
 Requirements: 
      Product Code must be passed to the function or must be obtainable from the msi file
      Elevated Rights

.Sources
    https://docs.microsoft.com/en-us/windows-server/administration/windows-commands/msiexec
    https://docs.microsoft.com/en-us/windows/win32/msi/standard-installer-command-line-options
    https://www.advancedinstaller.com/user-guide/product-identification.html
    grenade, https://stackoverflow.com/questions/11251034/find-guid-from-msi-file

.TODO
 Notes:

 Ideas:

 Possible improvements:
    
 To be done..
  - Verbose Mode for reporting
  - Logging: Add-fmLogEntry

 Critical Errors:
    - None known
         
.CHANGELOG
    0.1
        - First release
    0.2 
        - Added Logging support
    0.9 
        - Included more registry uninstall paths
        - Added checks after un/installation
        - Added some error handling
        - Added user defined arguments for msi install
        - Added Eventlog artefact collection
#>

<# Example calls
$result = Install-fmMSI -MSIFilePath $MSIFilePath
$result = Install-fmMSI -MSIFilePath $MSIFilePath -MSIProductcode $MSIProductcode

$result = Uninstall-fmMSI -MSIProductcode $MSIProductcode
$result = Uninstall-fmMSI -MSIFilePath $MSIFilePath

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

function Install-fmMSI {
[cmdletbinding(SupportsShouldProcess)] #Include Verbose/Whatif/Confirm Switch
param (
        [parameter(Mandatory=$false, HelpMessage='Logging Modus.')]
        [ValidateSet("ExitCodeOnly","ErrorMessages","InfoMessages")]
        [String]
        $LoggingModus = "ExitCodeOnly",        
        [parameter(Mandatory=$true, HelpMessage='Fullpath to the MSI file')]
        [ValidateNotNullOrEmpty()] [System.IO.FileInfo]
        $MSIFilePath,
        [parameter(Mandatory=$false, HelpMessage='OPTIONAL - Additional arguments to pass to the MSI Installer. Possible values: single string or array of strings. Example: /L')]
        [System.String]
        $MSIAdditionalArgugments,
        [parameter(Mandatory=$false, HelpMessage='OPTIONAL - Product Code of the MSI file. If not suplied the value is determined from MSI file')]
        [System.String]
        $MSIProductcode 
        #Firefox: "Mozilla Firefox 95.0 (x64 de)"
        #7Zip {23170F69-40C1-2702-2106-000001000000}
      )
    #Error Codes:
        #1: Product is already installed
        #2: MSI file does not exist
        #3: Error during installation
        #4: MSI not installed correctly
        #5: Could not obtain Product Code from MSI 

    if($interactive)
    {
        #Collect EventLog Artifacts
        [System.DateTime]$StartTime = Get-Date 
    }

    #Get MSI Product Code from MSI if not supplied
        #Check if MSI file exists
            $MSIFileExist = Test-Path $MSIFilePath
            if([string]::IsNullOrEmpty($MSIProductcode) -and $MSIFileExist)
            { 
                    #Try to get MSI Productcode from MSI via two different methods
                        #Does not work for 7Zip. Fireofx 
                        $MSIProductcode = (Get-AppLockerFileInformation -Path $MSIFilePath | select -ExpandProperty Publisher | Select BinaryName).BinaryName 
                        if([string]::IsNullOrEmpty($MSIProductcode))
                        { $MSIProductcode = (Get-MSIProperties -path $MSIFilePath).ProductCode }
                        if([string]::IsNullOrEmpty($MSIProductcode))
                        { return 3 } #3: Could not obtain Product Code from MSI 
            } 

    #Check if Product is already installed (loop through all Registry locations)
        foreach($path in $RegistryUninstallPaths)       
        { 
            $MSIAlreadyInstalled = Test-Path "$($path)\$($MSIProductcode)"
            if($MSIAlreadyInstalled)
            { break } #Leave Foreach -> Product code was found
        }
        if(!$MSIAlreadyInstalled)
        {
                if($MSIFileExist)
                {
                    #MSI Arguments
                        $MSIArguments = @(
                            "/i"
                            ('"{0}"' -f $MSIFilePath)
                            "/passive"
                            "/norestart"
                        )  
                        #Add additional arguments passed to function
                            foreach($argument in $MSIAdditionalArgugments)
                            { $MSIArguments += $argument }                  
                    
                    try
                    {
                        #MSI installation
                            Start-Process "msiexec.exe" -ArgumentList "$($MSIArguments)" -NoNewWindow -Wait
                            if( $LASTEXITCODE -eq 0 -or [string]::IsNullOrEmpty($LASTEXITCODE) ) 
                            { Write-Output "Command executed successfully" } 
                            else 
                            {
	                            Write-Output "msiexec.exe failed"
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

                    #Check installation
                        foreach($path in $RegistryUninstallPaths)       
                        { 
                            $MSIInstalled = Test-Path "$($path)\$($MSIProductcode)"
                            if($MSIInstalled)
                            { break } #Leave Foreach -> Product code was found
                        }
                        if($MSIInstalled)
                        { return 0 } #Successful
                        else
                        { return 4 } #Error

                }
                else
                { return 2 } #MSI file does not exist
        }
        else
        { return 1 } #MSI file is already installed
}


function Uninstall-fmMSI {
param (
        [parameter(Mandatory=$false, HelpMessage='OPTIONAL - Fullpath to the MSI file, to determine MSI Product Code')]
        [ValidateNotNullOrEmpty()] [System.IO.FileInfo]
        $MSIFilePath,
        [parameter(Mandatory=$false, HelpMessage='OPTIONAL - Product Code of the MSI file. If not suplied the value is determined from MSI file')]
        [System.String]
        $MSIProductcode #Firefox: {1294A4C5-9977-480F-9497-C0EA1E630130}
      )
    #Error Codes:
        #1: Product is not installed
        #2: Error uninstalling
        #3: Could not obtain Product Code from MSI 

    if($interactive)
    {
        #Collect EventLog Artifacts
        [System.DateTime]$StartTime = Get-Date 
    }

    #Get MSI Product Code from MSI if not supplied
        if([string]::IsNullOrEmpty($MSIProductcode))
        { 
            if([string]::IsNullOrEmpty($MSIFilePath))
            { return 2 } #MSI file does not exist and no MSIProductcode was supplied
            else
            {
                $MSIFileExist = Test-Path $MSIFilePath
                if(!$MSIFileExist)
                { return 2 } #MSI file does not exist
                else
                {
                    #Try to get MSI Productcode from MSI via two different methods
                        $MSIProductcode = (Get-AppLockerFileInformation -Path $MSIFilePath | select -ExpandProperty Publisher | Select BinaryName).BinaryName 
                        if([string]::IsNullOrEmpty($MSIProductcode))
                        { $MSIProductcode = (Get-MSIProperties -path $MSIFilePath).ProductCode }
                        if([string]::IsNullOrEmpty($MSIProductcode))
                        { return 3 } #3: Could not obtain Product Code from MSI 
                }
            }
        }
         
    #Check if Product is already installed (loop through all Registry locations)
        foreach($path in $RegistryUninstallPaths)       
        { 
            $MSIAlreadyInstalled = Test-Path "$($path)\$($MSIProductcode)"
            if($MSIAlreadyInstalled)
            { break } #Leave Foreach -> Product code was found
        }
        if($MSIAlreadyInstalled)
        {
            #Unistall
                #MSI Arguments
                    $MSIArguments = @(
                        "/x"
                        "/QN"
                        "REBOOT=ReallySuppress"
                        "$($MSIProductcode)"
                    )
                    
                try
                {
                    #MSI deinstallation
                        $result = Start-Process "msiexec.exe" -ArgumentList "$($MSIArguments)" -NoNewWindow -Wait -PassThru
                        if( $LASTEXITCODE -eq 0 -or [string]::IsNullOrEmpty($LASTEXITCODE) ) 
                        { Write-Output "Command executed successfully" } 
                        else 
                        {
	                        Write-Output "msiexec.exe failed"
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

                #Check uninstall of MSI Productcode
                    foreach($path in $RegistryUninstallPaths)       
                    { 
                        $MSIInstalled = Test-Path "$($path)\$($MSIProductcode)"
                        if($MSIInstalled)
                        { break } #Leave Foreach -> Product code was found
                    }
                    if($MSIInstalled)
                    { return 2 } #Error
                    else
                    { return 0 } #Successful


        }
        { return 1 } #1: Product is not installed
}


#TEST
function Get-MSIProperties {
#Source: grenade, https://stackoverflow.com/questions/11251034/find-guid-from-msi-file
  param (
    [Parameter(Mandatory=$true)]
    [ValidateNotNullOrEmpty()]
    [System.IO.FileInfo] $Path,

    [string[]] $properties = @('ProductCode', 'ProductVersion', 'ProductName', 'Manufacturer', 'ProductLanguage')
  )
  begin {
    $windowsInstaller = (New-Object -ComObject WindowsInstaller.Installer)
  }
  process {
    $table = @{}
    $msi = $windowsInstaller.GetType().InvokeMember('OpenDatabase', 'InvokeMethod', $null, $windowsInstaller, @($Path.FullName, 0))
    foreach ($property in $properties) {
      try {
        $view = $msi.GetType().InvokeMember('OpenView', 'InvokeMethod', $null, $msi, ("SELECT Value FROM Property WHERE Property = '$($property)'"))
        $view.GetType().InvokeMember('Execute', 'InvokeMethod', $null, $view, $null)
        $record = $view.GetType().InvokeMember('Fetch', 'InvokeMethod', $null, $view, $null)
        $table.add($property, $record.GetType().InvokeMember('StringData', 'GetProperty', $null, $record, 1))
      }
      catch {
        $table.add($property, $null)
      }
    }
    $msi.GetType().InvokeMember('Commit', 'InvokeMethod', $null, $msi, $null)
    $view.GetType().InvokeMember('Close', 'InvokeMethod', $null, $view, $null)
    $msi = $null
    $view = $null
    return $table
  }
  end {
    [System.Runtime.Interopservices.Marshal]::ReleaseComObject($windowsInstaller) | Out-Null
    [System.GC]::Collect()
  }
}

