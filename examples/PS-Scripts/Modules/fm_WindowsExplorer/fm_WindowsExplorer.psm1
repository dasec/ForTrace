$SkriptVersion = "0.1, 20.02.2022"
#requires -version 5.1
<#MIT Licence
Copyright 2021 Florian Mann
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#>

<# Explorer Forensic Tool

 
.SYNOPSYS
 Query Windows Explorer Search and check if registry entries got created

.NOTES
     
 Requirements: 

.Sources

.TODO
 Notes:
    - Add Parameter NumberOfDownArrowKeystrokes
    - Add Parameter WaitForSearch in Seconds
 Ideas:

 Critical Errors:
    - None known
         
.CHANGELOG
    0.1
        - First release
#>

function Query-fmExplorerSearch {
param (
  [parameter(Mandatory=$true, HelpMessage='Query string.')]
  [String]
  $SearchString = "Horse"
      )

    $returnvalue = $false # Error

#$interactive = $true
    if($interactive)
    {
        #Collect EventLog Artifacts
        [System.DateTime]$StartTime = Get-Date 
    }
        #For Sendkeys
            Add-Type -AssemblyName Microsoft.VisualBasic
            Add-Type -AssemblyName System.Windows.Forms

        #Open Explorer
           Start-Process explorer.exe
           Start-Sleep -Milliseconds 5000

           #Select Searchbar
               [System.Windows.Forms.SendKeys]::SendWait(“^f”)
               Start-Sleep -Milliseconds 5000

            #Enter Searchstring
               [System.Windows.Forms.SendKeys]::SendWait(“$($SearchString)”)
               Start-Sleep -Milliseconds 500
               [System.Windows.Forms.SendKeys]::SendWait(“{ENTER}”)
               Start-Sleep -Milliseconds 5000

           #Hit Down Arrow 4 times to select search result items and create Thumbcach entries
               [System.Windows.Forms.SendKeys]::SendWait(“{DOWN}”)
               Start-Sleep -Milliseconds 500
               [System.Windows.Forms.SendKeys]::SendWait(“{DOWN}”)
               Start-Sleep -Milliseconds 500
               [System.Windows.Forms.SendKeys]::SendWait(“{DOWN}”)
               Start-Sleep -Milliseconds 500
               [System.Windows.Forms.SendKeys]::SendWait(“{DOWN}”)
               Start-Sleep -Milliseconds 500

        #Close Explorer Window
            [System.Windows.Forms.SendKeys]::SendWait("%{F4}")
        
        #Check artefact creation
            try{
                $LastEntryNumber = (Get-ChildItem -Path REGISTRY::HKEY_USERS\*\SOFTWARE\MICROSOFT\WINDOWS\CURRENTVERSION\EXPLORER\WordWheelQuery -ErrorAction SilentlyContinue).Property[-1]
                $LastEntryBinary = (Get-ItemProperty -Path REGISTRY::HKEY_USERS\*\SOFTWARE\MICROSOFT\WINDOWS\CURRENTVERSION\EXPLORER\WordWheelQuery -ErrorAction SilentlyContinue).$LastEntryNumber

                $LastEntryString = ($LastEntryBinary | ForEach{ [char]$_ }) -join "" -replace [char]0 

                if($LastEntryString -eq $SearchString)
                { $returnvalue = $true } #No Error
            }
            catch {} #Could not query registry

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

    return $returnvalue
}

#Query
    #Query-fmExplorerSearch -SearchString "UniBw"


function Copy-fmItemUsingExplorer{
# Opens Explorer with SourceFile selected, copies SourceFile to DestinationFolder, closes this Explorer Windows and reopens
# Explorer with Destination File selected and closes Explorer Windows again.
 
# Source: BackSlasher, Feb 19, 2013, https://blog.backslasher.net/copying-files-in-powershell-using-windows-explorer-ui.html
    # CopyHere Flags https://docs.microsoft.com/en-us/windows/win32/shell/folder-copyhere
        # "16" -> Yes to all
        # "80" -> Yes to all and Preserve undo information if possible
# Existing files are overwritten without question!

#Notes
    # Open Windows in PowerShell https://devblogs.microsoft.com/scripting/hey-scripting-guy-how-can-i-use-windows-powershell-to-get-a-list-of-all-the-open-windows-on-a-computer/
        #$a = New-Object -com "Shell.Application"; $b = $a.windows() | select-object LocationName; $b

#If Show FullPath in Window Title is not set to true -> localized Folders (Documents/Dokumente -> EN/DE) make problems closing windows by title

    param(
        [Parameter(Mandatory=$True)]
        [ValidateScript({Test-Path -Path $_})]
            [string]$SourceFilePath,

        [Parameter(Mandatory=$True)]
            [string]$DestinationFolderPath,

        [bool]$CreateDestination = $True,

        [ValidateSet("16", "80")]
            [int]$CopyFlags = 80
    )

    Add-Type -AssemblyName Microsoft.VisualBasic
    Add-Type -AssemblyName System.Windows.Forms

    #Set Show Full Path in Window Title true if not allready -> Put outside of the Funktion????
        $showfullpath = 0
        $showfullpath = (Get-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\CabinetState").FullPath
        if($showfullpath -eq 0)
        { 
            Set-ItemProperty -Type DWord -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\CabinetState" -Name "FullPath" -value "1"
            #Restart Explorer
            Get-Process explorer | Stop-Process
            Start-Sleep -Seconds 5        
        }

    #Create Destination Folder if not exists
    if(!(Test-Path $DestinationFolderPath) -and $CreateDestination)
    {
        New-Item -Path $DestinationFolderPath -ItemType Directory | Out-Null
    }
    if((Test-Path -Path $SourceFilePath) -and (Test-Path -Path $DestinationFolderPath))
    {
        #Top Foldername to identifiy Windows Explorer WindowTitle
            #If Show FullPath in Window Title is not set to true
                #$SourceExplorerWindowTitle = Split-Path -Path (Split-Path -Path $SourceFilePath) -Leaf
                #$DestinationExplorerWindowTitle = Split-Path -Path $DestinationFolderPath -Leaf
            #If Show FullPath in Window Title is set to true
                $SourceExplorerWindowTitle = Split-Path -Path $SourceFilePath
                $pathlength = 0
                $pathlength = $DestinationFolderPath.Length
                if($pathlength -gt 0 -and $pathlength -le 3)
                    { $DestinationExplorerWindowTitle = $DestinationFolderPath}
                else
                    { $DestinationExplorerWindowTitle = Split-Path -Path $DestinationFolderPath }
        #Open Explorer select file, to generate artifacts, for example Thumbnails
            #Parameters to launch explorer.exe with
            $Params = @()
                $Params += "/select,"
                $Params += "$($SourceFilePath)"
            Start-Process explorer.exe $Params #Start-Process explorer.exe -ArgumentList '/select, ""C:\Users\hanshack\Pictures\Product.bmp""'
            $explorerwindowsstarted = $false
            $i = 0
            do
            {
                Start-Sleep -Milliseconds 1000
                $explorerwindowsstartedtitle = Get-Process -Name explorer | Where-Object {$_.MainWindowTitle -eq $SourceExplorerWindowTitle}
                if($explorerwindowsstartedtitle.MainWindowTitle -eq $SourceExplorerWindowTitle)
                    {$explorerwindowsstarted = $true}
                $i++
           }while(($explorerwindowsstarted -eq $false) -and ($i -lt 10))
           Start-Sleep -Milliseconds 1000
        #Copy File with Explorer (COM) - not via Copy-Item, maybe this generates more User like artifacts...
            $objShell = New-Object -ComObject 'Shell.Application'    
            $objFolder = $objShell.NameSpace((Get-Item $DestinationFolderPath).FullName)
            $objFolder.CopyHere((Get-Item $SourceFilePath).FullName,$CopyFlags) #Blocks until finished
            Start-Sleep -Milliseconds 1000
        #Close Explorer Window
            Get-Process -Name explorer | Where-Object {$_.MainWindowTitle -eq $SourceExplorerWindowTitle} | Stop-Process

        #Open Explorer select file, to generate artifacts, for example Thumbnails
            #Check if Path is Volume Root
                $volumelabel = ""
                $pathlength = 0
                $pathlength = $DestinationFolderPath.Length
                if($pathlength -gt 0 -and $pathlength -le 3)
                {
                    $volumedriveletter = $DestinationFolderPath[0]
                    $volumelabel = (Get-Volume $volumedriveletter).FileSystemLabel
                }
            #Parameters to launch explorer.exe with
            $Params = @()
                $Params += "/select,"
                $Params += "$($DestinationFolderPath)$(Split-Path -Path $SourceFilePath -Leaf)"
            Write-Host $Params
            Start-Sleep -Milliseconds 500
            Start-Process explorer.exe $Params #Start-Process explorer.exe -ArgumentList '/select, ""C:\Users\hanshack\Pictures\Product.bmp""'
            $explorerwindowsstarted = $false
            $i = 0
            do
            {
                Start-Sleep -Milliseconds 1000
                $explorerwindowsstartedtitle = Get-Process -Name explorer | Where-Object {$_.MainWindowTitle -eq $SourceExplorerWindowTitle}
                if($explorerwindowsstartedtitle.MainWindowTitle -eq $SourceExplorerWindowTitle)
                    {$explorerwindowsstarted = $true}
                $i++
           }while(($explorerwindowsstarted -eq $false) -and ($i -lt 15))
           Start-Sleep -Milliseconds 1000

           #Get-Process -Name explorer | Where-Object {$_.MainWindowTitle -eq $SourceExplorerWindowTitle} | Stop-Process

        #Focus Explorer Window
            #Check if DestinationFolderPath is Root of Volume
                #if($volumelabel -ne "")
                #{ $DestinationExplorerWindowTitle = "$($volumelabel) ($($DestinationFolderPath[0]):)" } # e.g.: "DATA (E:)"
            
            #$wshell = New-Object -ComObject wscript.shell
            #$wshell.AppActivate($DestinationExplorerWindowTitle) | Out-Null
                #$wshell = New-Object -ComObject wscript.shell
                #$wshell.AppActivate($DestinationExplorerWindowTitle) | Out-Null
                #Start-Sleep -Milliseconds 100
            [System.Windows.Forms.SendKeys]::SendWait(“%{TAB}”)
            Start-Sleep -Milliseconds 1000

            #Start Photos with Enter to generate Recent items entry (C:\Users\USERNAME\AppData\Roaming\Microsoft\Windows\Recent)
            if($SourceFilePath -eq "C:\Users\hanshack\Pictures\Motor.JPG")
            {
                [System.Windows.Forms.SendKeys]::SendWait(“{ENTER}”)
                Start-Sleep -Milliseconds 8000
                Get-Process -Name Microsoft.Photos | Stop-Process  # FileName is not in WindowsTitle!
            }

        #Close Explorer Window
            Get-Process -Name explorer | Where-Object {$_.MainWindowTitle -eq $DestinationExplorerWindowTitle} | Stop-Process

        #validation and return values
        if(Test-Path -Path "$($DestinationFolderPath)\$(Split-Path -Path $SourceFilePath -Leaf)")
        { return $True }
        else
        { return $false }
    }
    else
    {
        #Return Error Source File or Destination Folder does not exist
        return $false
    }
}

    #$SourceFilePath = "C:\Users\hanshack\Pictures\Motor.JPG"
    #$DestinationFolderPath = "C:\Users\hanshack\Pictures\Motor.JPG"
    #Copy-fmItemUsingExplorer -source $SourceFilePath -destination $DestinationFolderPath -CopyFlags 80
