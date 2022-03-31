$SkriptVersion = "0.1, 30.01.2022"
#requires -version 5.1
<#MIT Licence
Copyright 2021 Florian Mann
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#>

<# Veracrypt Modul

 
.SYNOPSYS
 Veracrypt Install, usage, uninstall and check expected artifacts on local machine

.NOTES
     
 Requirements: 
      Elevated Rights only for installation needed

.Sources
    https://www.veracrypt.fr/en/Command%20Line%20Usage.html
    https://documentation.help/VeraCrypt/Command%20Line%20Usage.html

.TODO
 Notes:
    #Veracrypt only has silent install implemented for msi
 Ideas:
   
 Possible improvements:
    
 To be done:
  
 Critical Errors:
    - None known
         
.CHANGELOG
    0.1
        - First release
#>

#Functions

#$VeraCryptLatestDownloadURL = "https://sourceforge.net/projects/veracrypt/files/latest/download"
#$VeraCryptLatestDownloadURL = "https://downloads.sourceforge.net/project/veracrypt/VeraCrypt%201.25.7/Windows/VeraCrypt%20Setup%201.25.7.exe?ts=gAAAAABh9qCyk7fa5fx8mKqfms-rpPBUqNRN0Vc1CCTwavOx4ShlXKAx_FU4ikkGjciAezftVo0I76UtWT3H7NBWQ7x45tKO3w%3D%3D&r=https%3A%2F%2Fsourceforge.net%2Fprojects%2Fveracrypt%2Ffiles%2Flatest%2Fdownload"
$VeraCryptMSIDownloadURL = "https://launchpad.net/veracrypt/trunk/1.25.7/+download/VeraCrypt_Setup_x64_1.25.7.msi"
Start-Process $VeraCryptMSIDownloadURL # Edge will automatically download veracrypt Setup AFTER COOKIE BANNER APROVAL!!!!

#Install Veracrypt
    #Get Installer Path from Dowloads folder
    $MSIFilePath = (Get-ChildItem -Path "$($env:USERPROFILE)\Downloads\*" -Include *.msi | Where-Object {$_.Name -Match "veracrypt_setup"})[0].FullName
    $result = Install-fmMSI -MSIFilePath $MSIFilePath -MSIAdditionalArgugments "ACCEPTLICENSE=YES"

#Create Veracrypt container
    $VeracryptFormatPath = "C:\Program Files\VeraCrypt\VeraCrypt Format.exe"
    $VeracryptFormatExists = Test-Path $VeracryptFormatPath
    if($VeracryptFormatExists)
    {
        [string]$NewContainerPath = "$($env:USERPROFILE)\container3.vc"
        [string]$NewContainerSize = "50M" #M/Megabyte, G/Gigabytes,T/Terabytes
        [string]$NewContainerPassword = "MySuperSecurePassword1!"
        [string]$NewContainerEncryptionAlgorithm = "AES"
        [string]$NewContainerHash = "sha-512"
        [string]$NewContainerFileSystemType = "FAT" #FAT, NTFS, ExFAT, ReFS, None
        [int]$NewContainerPIM = 0 #Personal Iterations Multiplier
        $VeracryptFormatArguments = @(
            "/create ""$($NewContainerPath)""",
            "/size ""$($NewContainerSize)""",
            "/password ""$($NewContainerPassword)""",
            "/encryption $($NewContainerEncryptionAlgorithm)",
            "/hash $($NewContainerHash)",
            "/filesystem $($NewContainerFileSystemType)",
            "/pim $($NewContainerPIM)",
            "/silent",
            "/force"
        )
        try { Start-Process $VeracryptFormatPath -ArgumentList $VeracryptFormatArguments -NoNewWindow -Wait }
        catch { Write-Host "Error creating container $($NewContainerPath)" }
        $ContainerCrated = Test-Path $NewContainerPath
        if($ContainerCrated)
        { 
            $Container = Get-Item $NewContainerPath
            Write-Host "Container $($NewContainerPath) with $($Container.Length) Bytes created" 
        }
        else
        { Write-Host "Error creating container $($NewContainerPath)" }
    }
    else
    {
        Write-Host "$($VeracryptFormatPath) does not exist"
    }

#Mount Veracrypt Volume
    $VeracryptPath = "C:\Program Files\VeraCrypt\VeraCrypt.exe"
    $VeracryptExists = Test-Path $VeracryptPath
    if($VeracryptExists)
    {
        $FirstFreeDriveLetter = (68..90 | %{$L=[char]$_; if ((gdr).Name -notContains $L) {$L}})[0] #Detects first free driveletter
        
        [string]$MountVolumePath = "$($env:USERPROFILE)\container3.vc"
        [string]$MountVolumeDriveletter = $FirstFreeDriveLetter
        [string]$MountVolumePassword = "MySuperSecurePassword1!"
        [int]$MountVolumePIM = 0 #Personal Iterations Multiplier
        $VeracryptMountArguments = @(
            "/volume ""$($MountVolumePath)""",
            "/letter $($MountVolumeDriveletter)",
            "/password ""$($MountVolumePassword)""",
            "/pim $($MountVolumePIM)",
            "/quit", #Close Veracrypt Dialog after mounting
            "/silent"
        )
        try { Start-Process $VeracryptPath -ArgumentList $VeracryptMountArguments -NoNewWindow -Wait }
        catch { Write-Host "Error mounting container $($MountVolumePath) to $($MountVolumeDriveletter)" }
        
        Start-Sleep -Seconds 5
        $ContainerMounted = Test-Path "$($MountVolumeDriveletter):"
        if($ContainerMounted)
        {
            Write-Host "Volume $($MountVolumeDriveletter) mounted"
        }
        else
        { Write-Host "Error mounting container $($MountVolumePath) to $($MountVolumeDriveletter)" }
    }
    else
    {
        Write-Host "$($VeracryptPath) does not exist"
    }



#Dismount Veracrypt Volume
    $VeracryptPath = "C:\Program Files\VeraCrypt\VeraCrypt.exe"
    $VeracryptExists = Test-Path $VeracryptPath
    if($VeracryptExists)
    {       
        [string]$DismountVolumeDriveletter = $FirstFreeDriveLetter
        $VeracryptDismountArguments = @(
            "/dismount $($DismountVolumeDriveletter)",
            "/quit", #Close Veracrypt Dialog after mounting
            "/silent"
            "/force"
        )
        try { Start-Process $VeracryptPath -ArgumentList $VeracryptDismountArguments -NoNewWindow -Wait }
        catch { Write-Host "Error dismounting container $($DismountVolumeDriveletter)" }
        
        Start-Sleep -Seconds 5
        $ContainerMounted = Test-Path $DismountVolumeDriveletter
        if(!$ContainerMounted)
        {
            Write-Host "Volume $($DismountVolumeDriveletter) dismounted"
        }
        else
        { Write-Host "Error dismounting container $($DismountVolumeDriveletter)" }
    }
    else
    {
        Write-Host "$($VeracryptPath) does not exist"
    }
