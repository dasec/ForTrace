$SkriptVersion = "0.1, 30.01.2022"
#requires -version 5.1
<#MIT Licence
Copyright 2021 Florian Mann
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#>

<# Anti-Forensics Modul

 
.SYNOPSYS
 Hide files and data

.NOTES
     Adding AlternateDataStream to file does not change its hash
 Requirements: 

.Sources
    Alternate Data Streams https://blog.malwarebytes.com/101/2015/07/introduction-to-alternate-data-streams/, https://davidhamann.de/2019/02/23/hidden-in-plain-sight-alternate-data-streams/

.TODO
 Notes:

 Ideas:
    Adding code to Alternate Data Stream: > Set-Content -path .\hello.txt -value $(Get-Content $(Get-Command calc.exe).Path -readcount 0 -encoding byte) -encoding byte -stream exestream
   
 Possible improvements:
    
 To be done:
  
 Critical Errors:
    - None known
         
.CHANGELOG
    0.1
        - First release with Alternate Data Stream support
#>

#Functions

function New-fmAlternateDataStream {
param (
        [parameter(Mandatory=$false, HelpMessage='Logging Modus.')]
        [ValidateSet("ExitCodeOnly","ErrorMessages","InfoMessages")]
        [String]
        $LoggingModus = "ExitCodeOnly",        
        [parameter(Mandatory=$true, HelpMessage='Fullpath to file')]
        [ValidateNotNullOrEmpty()] [System.IO.FileInfo]
        $FilePath,
        [parameter(Mandatory=$true, HelpMessage='Text to hide in Alternate Data Stream of file')]
        [System.String]
        $Text,
        [parameter(Mandatory=$true, HelpMessage='Name of the Alternate Data Stream')]
        [System.String]
        $StreamName
      )
    #Error Codes:
        #1: File does not exist
        #2: Error adding stream

    #Example 
        #New-fmAlternateDataStream -FilePath "C:\Users\admin\file.txt" -Text "TestText" -StreamName "hidden"

    $FileExists = Test-Path $FilePath
    if($FileExists)
    {
        try{ Set-Content -Path $FilePath -Stream $StreamName -Value "$($Text)" }
        catch 
        {
            Write-Host "Error adding stream to $($FilePath)"
            return 2 #2: Error adding stream
        }
        $Stream = Get-Content -Path $FilePath -stream $StreamName
        if($Stream -eq $Text)
        { 
            Write-Host "Stream added"
            return 0
        }
        else
        {
            Write-Host "Error adding stream to $($FilePath)"
            return 2 #2: Error adding stream
        }
    }
    else
    { 
        Write-Host "File $($FilePath) does not exists" 
        return 1 #1: File does not exist
    }
}

function Get-fmAlternateDataStream {
param (
        [parameter(Mandatory=$false, HelpMessage='Logging Modus.')]
        [ValidateSet("ExitCodeOnly","ErrorMessages","InfoMessages")]
        [String]
        $LoggingModus = "ExitCodeOnly",        
        [parameter(Mandatory=$true, HelpMessage='Fullpath to file')]
        [ValidateNotNullOrEmpty()] [System.IO.FileInfo]
        $FilePath,
        [parameter(Mandatory=$true, HelpMessage='Name of the Alternate Data Stream')]
        [System.String]
        $StreamName
      )
    #Error Codes:
        #1: File does not exist
        #2: Error reading stream

    #Example 
        #Get-fmAlternateDataStream -FilePath "C:\Users\admin\file.txt" -StreamName "hidden"

    $FileExists = Test-Path $FilePath
    if($FileExists)
    {
        try{ $Stream = Get-Content -Path $FilePath -stream $StreamName }
        catch 
        {
            Write-Host "Error reading stream $($StreamName) from file $($FilePath)"
            return 2 #2: Error reading stream
        }
        return $Stream
    }
    else
    { 
        Write-Host "File $($FilePath) does not exists" 
        return 1 #1: File does not exist
    }
}