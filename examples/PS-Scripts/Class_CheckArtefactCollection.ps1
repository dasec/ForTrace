$SkriptVersion = "0.1, 31.12.2021"
#requires -version 5.1
<#
<#MIT Licence
Copyright 2021 Florian Mann
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


Import-Module and the #requires statement only import the module functions, aliases, and variables, as defined by the module. Classes are not imported. The using module statement imports the classes defined in the module. If the module isn't loaded in the current session, the using statement fails. For more information about the using statement, see about_Using.

To be done:
    ?????????????????????????????
    HASH VALIDATION ÜBERARBEITEN -> FEHLER???????????????????1!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    ????????????????????????????


Notes
    RunAsAdministrator required for some Logs/files to read

#>

class ArtifactCollection {
    #General Info
        [Guid]hidden $ID
        [string]$ProgramName #Program name to which the artefact belongs
        [string]$ProgramVersion #Version Number of the program to which the artefact belongs
        #(Optional)
        [string]$Description #For individual information about the artefact collection / program

    #OS information (Optional)
        [string]hidden $OSName
        [string]hidden $OSVersion
        [string]hidden $OSArchitecture

    #Computer information (Optional)
        [string]hidden $Computername
        [string]hidden $IP
        [string]hidden $MAC

    #Artifacts -> Contain the Artifacts to validate
        [System.Collections.ArrayList]$Files = @()
            [String]$FilesCheckResults = "NotChecked"
        [System.Collections.ArrayList]$Folders = @()
            [String]$FoldersCheckResults = "NotChecked"
        [System.Collections.ArrayList]$Registrys = @()
            [String]$RegistrysCheckResults = "NotChecked"
        [System.Collections.ArrayList]$PathVariables = @()
            [String]$PathVariablesCheckResults = "NotChecked"
        [System.Collections.ArrayList]$MSIProductCodes = @()
            [String]$MSIProductCodesCheckResults = "NotChecked"
        #[System.Collections.ArrayList]$SoftwareNames = @() #NotImplemented
            #[String]$SoftwareNamesCheckResults = "NotChecked"
        [System.Collections.ArrayList]$Services = @()
            [String]$ServicesCheckResults = "NotChecked"
        [System.Collections.ArrayList]$EventLogEntrys = @()
            [String]$EventLogEntrysCheckResults = "NotChecked"
            #Used for EventLog filtering
                [DateTime]$StartTime 
                [DateTime]$EndTime
            
        #Prefetch??
        #JumpList??
    
    #Constructor
    ArtifactCollection ([string]$ProgramName,[string]$ProgramVersion,[DateTime]$StartTime,[DateTime]$EndTime,[string]$Description){
        if([string]::IsNullOrEmpty($ProgramName)) {$this.ProgramName = "-"} else {$this.ProgramName = $ProgramName}
        if([string]::IsNullOrEmpty($ProgramVersion)) {$this.ProgramVersion = "-"} else {$this.ProgramVersion = $ProgramVersion}
        $this.ID = New-GUID

        if(get-date $StartTime) {$this.StartTime = $StartTime} else {$this.StartTime = Get-Date}
        if(get-date $EndTime) {$this.EndTime = $EndTime} else {$this.EndTime = Get-Date}

        if([string]::IsNullOrEmpty($Description)) {$this.Description = ""} else {$this.Description = $Description}
    }

    #Method for exporting entire artefact collection to json file
    [bool]ExportToJSON([String]$PathtoJsonFile) {
        #Existing files will be overritten

        #Validate Parameters
            if(Test-Path -IsValid $PathtoJsonFile)
            {
                if(Test-Path $PathtoJsonFile)
                { Remove-Item $PathtoJsonFile }

                $JSONArtefactCollection = ConvertTo-Json -InputObject $this -Depth 2
                Out-File -FilePath $PathtoJsonFile -InputObject $JSONArtefactCollection
                if($? -and (Test-Path $PathtoJsonFile)) 
                { return $true }
                else
                { throw "Error creating JSON Export." }
            }
            else
            { throw "PathtoJsonFile must be a valid Path" }
    }

    #Method for importing entire artefact collection from json file
    [bool]ImportFromJSON([String]$PathtoJsonFile) {
        #Validate Parameters
            if(Test-Path -IsValid $PathtoJsonFile)
            {
                if(Test-Path $PathtoJsonFile)
                {
                    try
                    {
                        $JSONFileContent = Get-Content $PathtoJsonFile
                        $JSONArtefactCollection = $JSONFileContent | ConvertFrom-Json

                        #General Info
                            if([string]::IsNullOrEmpty($JSONArtefactCollection.ProgramName)) {$this.ProgramName = "-"} else {$this.ProgramName = $JSONArtefactCollection.ProgramName}
                            if([string]::IsNullOrEmpty($JSONArtefactCollection.ProgramVersion)) {$this.ProgramVersion = "-"} else {$this.ProgramVersion = $JSONArtefactCollection.ProgramVersion}
                            if([string]::IsNullOrEmpty($JSONArtefactCollection.ID)) {$this.ID = New-GUID} else {$this.ProgramVersion = $JSONArtefactCollection.ID}
                            if([string]::IsNullOrEmpty($JSONArtefactCollection.Description)) {$this.Description = "-"} else {$this.Description = $JSONArtefactCollection.Description}

                        #OS information (Optional)
                            if([string]::IsNullOrEmpty($JSONArtefactCollection.OSName)) {$this.OSName = "-"} else {$this.OSName = $JSONArtefactCollection.OSName}
                            if([string]::IsNullOrEmpty($JSONArtefactCollection.OSVersion)) {$this.OSVersion = "-"} else {$this.OSVersion = $JSONArtefactCollection.OSVersion}
                            if([string]::IsNullOrEmpty($JSONArtefactCollection.OSArchitecture)) {$this.OSArchitecture = "-"} else {$this.OSArchitecture = $JSONArtefactCollection.OSArchitecture}
                    
                        #Computer information (Optional)
                            if([string]::IsNullOrEmpty($JSONArtefactCollection.Computername)) {$this.Computername = "-"} else {$this.Computername = $JSONArtefactCollection.Computername}
                            if([string]::IsNullOrEmpty($JSONArtefactCollection.IP)) {$this.IP = "-"} else {$this.IP = $JSONArtefactCollection.IP}
                            if([string]::IsNullOrEmpty($JSONArtefactCollection.MAC)) {$this.MAC = "-"} else {$this.MAC = $JSONArtefactCollection.MAC}
                                        
                        #Loop all categories
                            #Files
                                foreach($artefact in $JSONArtefactCollection.Files)
                                { $this.AddFile($artefact.ArtefactCondition,$artefact.ArtefactValue,$artefact.ArtefactHash,$artefact.ArtefactHashCheckResult,$artefact.ArtefactCheckResult) }
                                $this.FilesCheckResults = $JSONArtefactCollection.FilesCheckResults
                            #Folders
                                foreach($artefact in $JSONArtefactCollection.Folders)
                                { $this.AddFolder($artefact.ArtefactCondition,$artefact.ArtefactValue,$artefact.ArtefactHash,$artefact.ArtefactHashCheckResult,$artefact.ArtefactCheckResult) }
                                $this.FoldersCheckResults = $JSONArtefactCollection.FoldersCheckResults
                            #Registrys
                                foreach($artefact in $JSONArtefactCollection.Registrys)
                                { $this.AddRegistry($artefact.ArtefactCondition,$artefact.ArtefactKey,$artefact.ArtefactValueName,$artefact.ArtefactValueData) }
                                $this.RegistrysCheckResults = $JSONArtefactCollection.RegistrysCheckResults
                            #PathVariables
                                foreach($artefact in $JSONArtefactCollection.PathVariables)
                                { $this.AddPathVariable($artefact.ArtefactCondition,$artefact.ArtefactValue) }
                                $this.PathVariablesCheckResults = $JSONArtefactCollection.PathVariablesCheckResults
                            #MSIProductCodes
                                foreach($artefact in $JSONArtefactCollection.MSIProductCodes)
                                { $this.AddMSIProductCode($artefact.ArtefactCondition,$artefact.ArtefactValue) }
                                $this.MSIProductCodesCheckResults = $JSONArtefactCollection.MSIProductCodesCheckResults
                            #SoftwareNames
                                #foreach($artefact in $JSONArtefactCollection.SoftwareNames)
                                #{ $this.AddSoftwareName($artefact.ArtefactCondition,$artefact.ArtefactValue,$artefact.ArtefactHash,$artefact.ArtefactHashCheckResult,$artefact.ArtefactCheckResult) }
                                #$this.SoftwareNamesCheckResults = $JSONArtefactCollection.SoftwareNamesCheckResults
                            #Services
                                foreach($artefact in $JSONArtefactCollection.Services)
                                { $this.AddServices($artefact.ArtefactCondition,$artefact.ArtefactValue) }
                                $this.ServicesCheckResults = $JSONArtefactCollection.ServicesCheckResults
                            #EventLogEntrys
                                foreach($artefact in $JSONArtefactCollection.EventLogEntrys)
                                { 
                                    if($artefact.ArtefactEventID -eq "*"){ $tempArtefactEventID = "" }else{ $tempArtefactEventID = $artefact.ArtefactEventID }
                                    $this.AddEventLog($artefact.ArtefactCondition,$artefact.ArtefactType,$artefact.ArtefactLogName,$artefact.ArtefactProviderName,$tempArtefactEventID,$artefact.ArtefactEventMessage) 
                                }
                                $this.EventLogEntrysCheckResults = $JSONArtefactCollection.EventLogEntrysCheckResults
                                if(get-date $JSONArtefactCollection.StartTime) {$this.StartTime = $JSONArtefactCollection.StartTime} else {$this.StartTime = Get-Date}
                                if(get-date $JSONArtefactCollection.EndTime) {$this.EndTime = $JSONArtefactCollection.EndTime} else {$this.EndTime = Get-Date}

                        ##### ERROR HANDLING???
                        if($?) 
                        { return $true }
                        else
                        { throw "Error creating JSON Export." }
                    }
                    catch
                    { throw "Error creating JSON Export." }
                }
                else
                { throw "File does not exists" }
            }
            else
            { throw "PathtoJsonFile must be a valid Path" }
    }

    #Method for reading the OS information
    GetOSInfo() {
        $this.OSName = (Get-WmiObject Win32_OperatingSystem).Caption
        $this.OSVersion = (Get-CimInstance Win32_OperatingSystem).Version
        $this.OSArchitecture = (Get-CimInstance Win32_OperatingSystem).OSArchitecture
    }

    #Method for reading the Computer information
    GetComputerInfo() {
        $this.Computername = $env:COMPUTERNAME
        $this.IP = (Get-NetIPAddress).IPAddress -join ";"
        $this.MAC = (Get-NetAdapter).MacAddress -join ";"
    }

    #Method for adding File Artefacts
    AddFile([String]$ArtefactCondition,[String]$ArtefactValue,[String]$ArtefactHash,[String]$ArtefactHashCheckResult,[String]$ArtefactCheckResult) {
        #Examples
            #$ArtefactCollection.AddFile("Present","C:\","3DD66AE562656EB7A05B41A81A1C428EA3382CD0B13C03B38D7719C2ACDE2232","")
            #$ArtefactCollection.AddFile("NotPresent","C:\sdfsds","","NotChecked")

        #Validate Parameters
            if(!(($ArtefactCondition -eq "Present") -or ($ArtefactCondition -eq "NotPresent")))
            { throw "ArtefactCondition must be one of those two strings: Present,NotPresent" }
            
            if($ArtefactCondition -eq "NotPresent" -and !([string]::IsNullOrEmpty($ArtefactHash)))
            { throw "If ArtefactCondition is NotPresent no ArtefactHash is supported" }

            if(!(Test-Path -IsValid $ArtefactValue))
            { throw "ArtefactValue must be a valid Path" }

            if(!(($ArtefactCheckResult -eq "NotChecked") -or ($ArtefactCheckResult -eq "CheckError") -or ($ArtefactCheckResult -eq "True") -or ($ArtefactCheckResult -eq "False") -or ([string]::IsNullOrEmpty($ArtefactCheckResult))))
            { throw "ArtefactCheckResult must be one of those strings: NotChecked,CheckError,True,False,EMPTY" }

            if(!(($ArtefactHashCheckResult -eq "NotChecked") -or ($ArtefactCheckResult -eq "CheckError") -or ($ArtefactCheckResult -eq "True") -or ($ArtefactCheckResult -eq "False") -or ([string]::IsNullOrEmpty($ArtefactHashCheckResult))))
            { throw "ArtefactHashCheckResult must be one of those strings: NotChecked,CheckError,True,False,EMPTY" }

            if($ArtefactValue.Substring($ArtefactValue.Length-1) -eq "\")
            { throw "Artefact is only supported for single file and not for folders (Argument ArtefactValue ends with Backslash)"}


        $FileHashes = [ordered]@{
            "ArtefactCondition" = $ArtefactCondition
            "ArtefactValue" = $ArtefactValue
            "ArtefactHash" = $ArtefactHash
        }
            if([string]::IsNullOrEmpty($ArtefactCheckResult))
            { $FileHashes += @{"ArtefactCheckResult" = "NotChecked"} }
            else
            { $FileHashes += @{"ArtefactCheckResult" = $ArtefactCheckResult} }
            
            if([string]::IsNullOrEmpty($ArtefactHashCheckResult))
            { $FileHashes += @{"ArtefactHashCheckResult" = "NotChecked"} }
            else
            { $FileHashes += @{"ArtefactHashCheckResult" = $ArtefactHashCheckResult} }

        $this.Files.Add($FileHashes)
    }

    #Method for adding Folder Artefacts
    AddFolder([String]$ArtefactCondition,[String]$ArtefactValue,[String]$ArtefactHash,[String]$ArtefactHashCheckResult,[String]$ArtefactCheckResult) {
        #Examples
            #$ArtefactCollection.AddFolder("Present","C:\","3DD66AE562656EB7A05B41A81A1C428EA3382CD0B13C03B38D7719C2ACDE2232","")
            #$ArtefactCollection.AddFolder("NotPresent","C:\sdfsds","","NotChecked")

        #Validate Parameters
            if(!(($ArtefactCondition -eq "Present") -or ($ArtefactCondition -eq "NotPresent")))
            { throw "ArtefactCondition must be one of those two strings: Present,NotPresent" }
            
            if($ArtefactCondition -eq "NotPresent" -and !([string]::IsNullOrEmpty($ArtefactHash)))
            { throw "If ArtefactCondition is NotPresent no ArtefactHash is supported" }

            if(!(Test-Path -IsValid $ArtefactValue))
            { throw "ArtefactValue must be a valid Path" }

            if(!(($ArtefactCheckResult -eq "NotChecked") -or ($ArtefactCheckResult -eq "CheckError") -or ($ArtefactCheckResult -eq "True") -or ($ArtefactCheckResult -eq "False") -or ([string]::IsNullOrEmpty($ArtefactCheckResult))))
            { throw "ArtefactCheckResult must be one of those strings: NotChecked,CheckError,True,False,EMPTY" }

            if(!(($ArtefactHashCheckResult -eq "NotChecked") -or ($ArtefactCheckResult -eq "CheckError") -or ($ArtefactCheckResult -eq "True") -or ($ArtefactCheckResult -eq "False") -or ([string]::IsNullOrEmpty($ArtefactHashCheckResult))))
            { throw "ArtefactHashCheckResult must be one of those strings: NotChecked,CheckError,True,False,EMPTY" }

            ###??? HASH SUPPORT FOR FOLDERS????
            if(!([string]::IsNullOrEmpty($ArtefactHashCheckResult)))
            {
                if($ArtefactValue.Substring($ArtefactValue.Length-1) -eq "\")
                { throw "ArtefactHash is only supported for single files and not for folders (Argument ArtefactValue ends with Backslash)"}
            }

        $FolderHashes = [ordered]@{
            "ArtefactCondition" = $ArtefactCondition
            "ArtefactValue" = $ArtefactValue
            "ArtefactHash" = $ArtefactHash
        }
            if([string]::IsNullOrEmpty($ArtefactCheckResult))
            { $FolderHashes += @{"ArtefactCheckResult" = "NotChecked"} }
            else
            { $FolderHashes += @{"ArtefactCheckResult" = $ArtefactCheckResult} }
            
            if([string]::IsNullOrEmpty($ArtefactHashCheckResult))
            { $FolderHashes += @{"ArtefactHashCheckResult" = "NotChecked"} }
            else
            { $FolderHashes += @{"ArtefactHashCheckResult" = $ArtefactHashCheckResult} }

        $this.Folders.Add($FolderHashes)
    }

    #Method for adding Registry Artefacts
        #Keys have values, values conisist of value name and value data
    AddRegistry([String]$ArtefactCondition,[String]$ArtefactKey,[String]$ArtefactValueName,[String]$ArtefactValueData) {
        #Validate Parameters
            if(!(($ArtefactCondition -eq "Present") -or ($ArtefactCondition -eq "NotPresent")))
            { throw "ArtefactCondition must be one of those two strings: Present,NotPresent" }
            
            if([string]::IsNullOrEmpty($ArtefactKey))
            { throw "ArtefactKey must be a valid Registry Path. E.g.: HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\ and cannot be empty." }

            if(!(Test-Path -IsValid $ArtefactKey))
            { throw "ArtefactKey must be a valid Registry Path. E.g.: HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\" }
            
            #Only both variables can be NullOrEmpty not only one allone...
            if([string]::IsNullOrEmpty($ArtefactValueName) -xor [string]::IsNullOrEmpty($ArtefactValueData))
            { throw "ArtefactValueName and ArtefactValueData must be valid Registry value name/data strings. To test only the registry key supply empty strings for ArtefactValueName and ArtefactValueData" }
            
        $RegistryHashes = [ordered]@{
            "ArtefactCondition" = $ArtefactCondition
            "ArtefactKey" = $ArtefactKey
            "ArtefactValueName" = $ArtefactValueName
            "ArtefactValueData" = $ArtefactValueData
            "ArtefactCheckResult" = "NotChecked"
            }
        $this.Registrys.Add($RegistryHashes)
    }

    #Method for adding Path Variable Artefacts
    AddPathVariable([String]$ArtefactCondition,[String]$ArtefactValue) {
        #Validate Parameters
            if(!(($ArtefactCondition -eq "Present") -or ($ArtefactCondition -eq "NotPresent")))
            { throw "ArtefactCondition must be one of those two strings: Present,NotPresent" }
            
            if([string]::IsNullOrEmpty($ArtefactValue))
            { throw "ArtefactValue must be a valid non empty String" }

        $PathVariableHashes = [ordered]@{
            "ArtefactCondition" = $ArtefactCondition
            "ArtefactValue" = $ArtefactValue
            "ArtefactCheckResult" = "NotChecked"
            }
        $this.PathVariables.Add($PathVariableHashes)
    }

    #Method for adding MSI Product Code Artefacts
    AddMSIProductCode([String]$ArtefactCondition,[String]$ArtefactValue) {
        #Validate Parameters
            if(!(($ArtefactCondition -eq "Present") -or ($ArtefactCondition -eq "NotPresent")))
            { throw "ArtefactCondition must be one of those two strings: Present,NotPresent" }
            
            if([string]::IsNullOrEmpty($ArtefactValue))
            { throw "ArtefactValue must be a valid non empty String" }

        $MSIProductCodeHashes = [ordered]@{
            "ArtefactCondition" = $ArtefactCondition
            "ArtefactValue" = $ArtefactValue
            "ArtefactCheckResult" = "NotChecked"
            }
        $this.MSIProductCodes.Add($MSIProductCodeHashes)
    }

    #Method for adding EventLog Artefacts
    AddEventLog([String]$ArtefactCondition,[String]$ArtefactType,[String]$ArtefactLogName,[String]$ArtefactProviderName,[int]$ArtefactEventID,[String]$ArtefactEventMessage) {
        #Validate Parameters
            if(!(($ArtefactCondition -eq "Present") -or ($ArtefactCondition -eq "NotPresent")))
            { throw "ArtefactCondition must be one of those two strings: Present,NotPresent" }
            
            if(!(($ArtefactType -eq "Log") -or ($ArtefactType -eq "Provider")))
            { throw "ArtefactType must be one of those two strings: Log,Provider" }
            
            if([string]::IsNullOrEmpty($ArtefactLogName))
            { throw "ArtefactLogName must be a valid non empty String" }

            if(!($ArtefactEventID -gt 0 -and $ArtefactEventID -lt 99999999)) #maximum was choosen random
            { [String]$ArtefactEventID = "*" }

            #ArtefactEventMessage is optional
            $EventLogHashes = [ordered]@{
            "ArtefactCondition" = $ArtefactCondition
            "ArtefactType" = $ArtefactType
            "ArtefactLogName" = $ArtefactLogName #WinEvent Log name
            }

            if(![string]::IsNullOrEmpty($ArtefactProviderName))
            { $EventLogHashes += @{"ArtefactProviderName" = $ArtefactProviderName} }
            else
            { $EventLogHashes += @{"ArtefactProviderName" = "*"} }

            if(![string]::IsNullOrEmpty($ArtefactEventMessage))
            { $EventLogHashes += @{"ArtefactEventMessage" = $ArtefactEventMessage} }
            else
            { $EventLogHashes += @{"ArtefactEventMessage" = "*"} }


            if(![string]::IsNullOrEmpty($ArtefactEventID))
            { $EventLogHashes += @{"ArtefactEventID" = $ArtefactEventID} }
            else
            { $EventLogHashes += @{"ArtefactEventID" = "*"} }

            $EventLogHashes += @{"ArtefactCheckResult" = "NotChecked"}

        $this.EventLogEntrys.Add($EventLogHashes)
    }

    #Method for adding Services Artefacts
    AddServices([String]$ArtefactCondition,[String]$ArtefactValue) {
        #Validate Parameters
            if(!(($ArtefactCondition -eq "Present") -or ($ArtefactCondition -eq "NotPresent")))
            { throw "ArtefactCondition must be one of those two strings: Present,NotPresent" }
            
            if([string]::IsNullOrEmpty($ArtefactValue))
            { throw "ArtefactValue must be a valid non empty String" }

        $ServicesHashes = [ordered]@{
            "ArtefactCondition" = $ArtefactCondition
            "ArtefactValue" = $ArtefactValue
            "ArtefactCheckResult" = "NotChecked"
            }
        $this.Services.Add($ServicesHashes)
    }





    #Method for Artifact validation (Checks and sets the ArtefactCheckResult Variable in each entry)
    Validate() {
        #CheckResult can be: NotChecked,CheckError,True,False

        #Reset Check Summarys
            $this.ServicesCheckResults = "NotChecked"
            $this.EventLogEntrysCheckResults = "NotChecked"
            $this.FilesCheckResults = "NotChecked"
            $this.FoldersCheckResults = "NotChecked"
            $this.PathVariablesCheckResults = "NotChecked"
            $this.RegistrysCheckResults = "NotChecked"
            $this.MSIProductCodesCheckResults = "NotChecked"

        #Validate File Artefacts (If supplied file exists, matches hash or not)
            foreach($artefact in $this.Files)
            {
                #Check if File exists
                try{
                    $result = Test-Path $artefact.ArtefactValue
                    if($result -and !([string]::IsNullOrEmpty($artefact.ArtefactHash)))
                    { 
                        $artefactisfolderresult = (Get-Item $artefact.ArtefactValue).PSIsContainer
                        if($artefactisfolderresult)
                        { $artefact.ArtefactHashCheckResult = "CheckError" } #Only works for single file not for folders
                        else
                        {
                            $hashresult = Get-FileHash $artefact.ArtefactValue -Algorithm SHA256 #Only works for single file
                            if($?)
                            { 
                                if($hashresult.Hash -eq $artefact.ArtefactHash)
                                { $artefact.ArtefactHashCheckResult = "True" }
                                else
                                { $artefact.ArtefactHashCheckResult = "False" }
                            }
                            else
                            { $artefact.ArtefactHashCheckResult = "CheckError" } #Error getting file hash
                        }
                    }

                    if($artefact.ArtefactCondition -eq "Present")
                        { 
                            #ArtefactCondition is Present
                                $artefact.ArtefactCheckResult = $result.ToString()

                            #Set File validation summary
                                
                                if($result -and ($this.FilesCheckResults -eq "True" -or $this.FilesCheckResults -eq "NotChecked"))
                                { $this.FilesCheckResults = "True" }
                                elseif(!$result -and ($this.FilesCheckResults -eq "True" -or $this.FilesCheckResults -eq "False" -or $this.FilesCheckResults -eq "NotChecked"))
                                { $this.FilesCheckResults = "False" }
                                else
                                { 
                                    $this.FilesCheckResults = "CheckError" 
                                    if([string]::IsNullOrEmpty($artefact.ArtefactHash))
                                    { $artefact.ArtefactHashCheckResult = "CheckError" }
                                }
                        } 
                    elseif($artefact.ArtefactCondition -eq "NotPresent")
                        { 
                            #ArtefactCondition is NotPresent
                                $artefact.ArtefactCheckResult = (!$result).ToString() 

                            #Set File validation summary
                                if(!$result -and ($this.FilesCheckResults -eq "True" -or $this.FilesCheckResults -eq "NotChecked"))
                                { $this.FilesCheckResults = "True" }
                                elseif($result -and ($this.FilesCheckResults -eq "True" -or $this.FilesCheckResults -eq "False" -or $this.FilesCheckResults -eq "NotChecked"))
                                { $this.FilesCheckResults = "False" }
                                elseif(!$result -and $this.ServicesCheckResults -eq "False")
                                { $this.ServicesCheckResults = "False" }                                
                                else
                                { 
                                    $this.FilesCheckResults = "CheckError" 
                                    if([string]::IsNullOrEmpty($artefact.ArtefactHash))
                                    { $artefact.ArtefactHashCheckResult = "CheckError" }
                                }                
                        } 
                    else
                        { 
                            $artefact.ArtefactCheckResult = "CheckError" 
                            if([string]::IsNullOrEmpty($artefact.ArtefactHash))
                            { $artefact.ArtefactHashCheckResult = "CheckError" }
                            $this.FilesCheckResults = "CheckError"
                        }
                }
                catch
                { 
                    $artefact.ArtefactCheckResult = "CheckError" 
                    if([string]::IsNullOrEmpty($artefact.ArtefactHash))
                    { $artefact.ArtefactHashCheckResult = "CheckError" }
                    $this.FilesCheckResults = "CheckError"
                }
            }

        #Validate Folder Artefacts (If supplied folder exists or not) ###HASH SUPPORT?
            foreach($artefact in $this.Folders)
            {
                #Check if Folder exists
                try{
                    $result = Test-Path $artefact.ArtefactValue
                    if($result -and !([string]::IsNullOrEmpty($artefact.ArtefactHash)))
                    { 
                        $FilesinFolder = Get-ChildItem $artefact.ArtefactValue
                        $hashresult = ""
                        foreach($item in $FilesinFolder)
                        {
                            $artefactisfolderresult = (Get-Item $item.FullName).PSIsContainer
                            if(!$artefactisfolderresult)
                            {
                                #Get the hash from single file
                                $singlehashresult = Get-FileHash $item.FullName -Algorithm SHA256 #Only works for single file
                                
                                #Get the hash from the single file hash added to the hashed sum of all singlefilehashes
                                $temphashresult=[System.Security.Cryptography.HashAlgorithm]::Create("sha256").ComputeHash(
                                [System.Text.Encoding]::UTF8.GetBytes(($singlehashresult.Hash + $hashresult)))
                                
                                #Convert to String, remove -
                                $hashresult = [System.BitConverter]::ToString($temphashresult).Replace("-","")
                            }
                        }
                        if($hashresult -eq $artefact.ArtefactHash)
                         { $artefact.ArtefactHashCheckResult = "True" }
                        else
                        { $artefact.ArtefactHashCheckResult = "False" }
                    }

                    if($artefact.ArtefactCondition -eq "Present")
                        { 
                            #ArtefactCondition is Present
                                $artefact.ArtefactCheckResult = $result.ToString()

                            #Set Folder validation summary
                                
                                if($result -and ($this.FoldersCheckResults -eq "True" -or $this.FoldersCheckResults -eq "NotChecked"))
                                { $this.FoldersCheckResults = "True" }
                                elseif(!$result -and ($this.FoldersCheckResults -eq "True" -or $this.FoldersCheckResults -eq "False" -or $this.FoldersCheckResults -eq "NotChecked"))
                                { $this.FoldersCheckResults = "False" }
                                else
                                { 
                                    $this.FoldersCheckResults = "CheckError" 
                                    if([string]::IsNullOrEmpty($artefact.ArtefactHash))
                                    { $artefact.ArtefactHashCheckResult = "CheckError" }
                                }
                        } 
                    elseif($artefact.ArtefactCondition -eq "NotPresent")
                        { 
                            #ArtefactCondition is NotPresent
                                $artefact.ArtefactCheckResult = (!$result).ToString() 

                            #Set Folder validation summary
                                if(!$result -and ($this.FoldersCheckResults -eq "True" -or $this.FoldersCheckResults -eq "NotChecked"))
                                { $this.FoldersCheckResults = "True" }
                                elseif($result -and ($this.FoldersCheckResults -eq "True" -or $this.FoldersCheckResults -eq "False" -or $this.FoldersCheckResults -eq "NotChecked"))
                                { $this.FoldersCheckResults = "False" }
                                elseif(!$result -and $this.ServicesCheckResults -eq "False")
                                { $this.ServicesCheckResults = "False" }                                
                                else
                                { 
                                    $this.FoldersCheckResults = "CheckError" 
                                    if(!([string]::IsNullOrEmpty($artefact.ArtefactHash)))
                                    { $artefact.ArtefactHashCheckResult = "NotChecked" }
                                }                
                        } 
                    else
                        { 
                            $artefact.ArtefactCheckResult = "CheckError" 
                            if([string]::IsNullOrEmpty($artefact.ArtefactHash))
                            { $artefact.ArtefactHashCheckResult = "CheckError" }
                            $this.FoldersCheckResults = "CheckError"
                        }
                }
                catch
                { 
                    $artefact.ArtefactCheckResult = "CheckError" 
                    if([string]::IsNullOrEmpty($artefact.ArtefactHash))
                    { $artefact.ArtefactHashCheckResult = "CheckError" }
                    $this.FoldersCheckResults = "CheckError"
                }
            }

        #Validate Registrys Artefacts (If supplied key exists or not / if value data exists in key or not)
            foreach($artefact in $this.Registrys)
            {
                #Check if Registry key exists or value data is correct
                try{
                    if([string]::IsNullOrEmpty($artefact.ArtefactValueName) -xor [string]::IsNullOrEmpty($artefact.ArtefactValueData))
                    { 
                        $artefact.ArtefactCheckResult = "CheckError" 
                        $this.RegistrysCheckResults = "CheckError"
                    }
                    if([string]::IsNullOrEmpty($artefact.ArtefactValueName) -and [string]::IsNullOrEmpty($artefact.ArtefactValueData))
                    { 
                        #Check only key
                        $result = Test-Path $artefact.ArtefactKey
                    }
                    else
                    {
                        #Check value data inside key
                            if(Test-Path $artefact.ArtefactKey)
                            {
                                #Read Value and select only value data
                                $registryvaluedata = ((Get-ItemProperty $artefact.ArtefactKey) | Select-Object -Property $artefact.ArtefactValueName).($artefact.ArtefactValueName)
                                if($registryvaluedata -eq $artefact.ArtefactValueData)
                                { $result = $true }
                                else
                                { $result = $false }
                            }
                            else
                            { $result = $false }
                    }
                    if($artefact.ArtefactCondition -eq "Present")
                        { 
                            #ArtefactCondition is Present
                                $artefact.ArtefactCheckResult = $result.ToString()

                            #Set Registrys validation summary
                                if($result -and ($this.RegistrysCheckResults -eq "True" -or $this.RegistrysCheckResults -eq "NotChecked"))
                                { $this.RegistrysCheckResults = "True" }
                                elseif(!$result -and ($this.RegistrysCheckResults -eq "True" -or $this.RegistrysCheckResults -eq "False" -or $this.RegistrysCheckResults -eq "NotChecked"))
                                { $this.RegistrysCheckResults = "False" }
                                else
                                { $this.RegistrysCheckResults = "CheckError" }
                        } 
                    elseif($artefact.ArtefactCondition -eq "NotPresent")
                        { 
                            #ArtefactCondition is NotPresent
                                $artefact.ArtefactCheckResult = (!$result).ToString() 

                            #Set Registrys validation summary
                                if(!$result -and ($this.RegistrysCheckResults -eq "True" -or $this.RegistrysCheckResults -eq "NotChecked"))
                                { $this.RegistrysCheckResults = "True" }
                                elseif($result -and ($this.RegistrysCheckResults -eq "True" -or $this.RegistrysCheckResults -eq "False" -or $this.RegistrysCheckResults -eq "NotChecked"))
                                { $this.RegistrysCheckResults = "False" }     
                                elseif(!$result -and $this.ServicesCheckResults -eq "False")
                                { $this.ServicesCheckResults = "False" }                                
                                else
                                { $this.RegistrysCheckResults = "CheckError" }
                        } 
                    else
                        { 
                            $artefact.ArtefactCheckResult = "CheckError" 
                            $this.RegistrysCheckResults = "CheckError"
                        }
                }
                catch
                { 
                    $artefact.ArtefactCheckResult = "CheckError" 
                    $this.RegistrysCheckResults = "CheckError"
                }
            }

        #Validate PathVariables Artefacts (if $env:path matches supplied string)
            foreach($artefact in $this.PathVariables)
            {
                #Check if pathvariable matches supplied value
                try{
                    $result = $env:path -match [RegEx]::Escape($artefact.ArtefactValue) #Escape special chars like "\"
                    if($artefact.ArtefactCondition -eq "Present")
                        { 
                            #ArtefactCondition is Present
                                $artefact.ArtefactCheckResult = $result.ToString()

                            #Set PathVariables validation summary
                                if($result -and ($this.PathVariablesCheckResults -eq "True" -or $this.PathVariablesCheckResults -eq "NotChecked"))
                                { $this.PathVariablesCheckResults = "True" }
                                elseif(!$result -and ($this.PathVariablesCheckResults -eq "True" -or $this.PathVariablesCheckResults -eq "False" -or $this.PathVariablesCheckResults -eq "NotChecked"))
                                { $this.PathVariablesCheckResults = "False" }
                                else
                                { $this.PathVariablesCheckResults = "CheckError" }
                        } 
                    elseif($artefact.ArtefactCondition -eq "NotPresent")
                        { 
                            #ArtefactCondition is NotPresent
                                $artefact.ArtefactCheckResult = (!$result).ToString() 

                            #Set PathVariables validation summary
                                if(!$result -and ($this.PathVariablesCheckResults -eq "True" -or $this.PathVariablesCheckResults -eq "NotChecked"))
                                { $this.PathVariablesCheckResults = "True" }
                                elseif($result -and ($this.PathVariablesCheckResults -eq "True" -or $this.PathVariablesCheckResults -eq "False" -or $this.PathVariablesCheckResults -eq "NotChecked"))
                                { $this.PathVariablesCheckResults = "False" }
                                elseif(!$result -and $this.ServicesCheckResults -eq "False")
                                { $this.ServicesCheckResults = "False" }                                
                                else
                                { $this.PathVariablesCheckResults = "CheckError" }                   
                        } 
                    else
                        { 
                            $artefact.ArtefactCheckResult = "CheckError" 
                            $this.PathVariablesCheckResults = "CheckError"
                        }
                }
                catch
                { 
                    $artefact.ArtefactCheckResult = "CheckError" 
                    $this.PathVariablesCheckResults = "CheckError"
                }    
            }

        #Validate MSIProductCodes Artefacts
            foreach($artefact in $this.MSIProductCodes)
            {
                #Check if MSIProductCodes is installed
                try{
                    $ProductCodeRegistryKeyPath = "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\$($artefact.ArtefactValue)"  #64-Bit Applications on 64-Bit Systems and 32-Bit Applications on 32-Bit Systems
                    $ProductCodeRegistryKeyPath32Biton64BitSystem = "HKLM:\SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall\$($artefact.ArtefactValue)" #32-Bit Applications on 64-Bit Systems

                    $result1 = Test-Path $ProductCodeRegistryKeyPath #64-Bit Applications on 64-Bit Systems and 32-Bit Applications on 32-Bit Systems
                    $result2 = Test-Path $ProductCodeRegistryKeyPath32Biton64BitSystem #32-Bit Applications on 64-Bit Systems

                    #Combining result1 and result2. True if one of them is true (Software is installed)
                    if($result1 -or $result2)
                    { $result = $true }
                    else
                    { $result = $false }
                    
                    if($artefact.ArtefactCondition -eq "Present")
                        { 
                            #ArtefactCondition is Present
                                $artefact.ArtefactCheckResult = $result.ToString()

                            #Set MSIProductCodes validation summary
                                if($result -and ($this.MSIProductCodesCheckResults -eq "True" -or $this.MSIProductCodesCheckResults -eq "NotChecked"))
                                { $this.MSIProductCodesCheckResults = "True" }
                                elseif(!$result -and ($this.MSIProductCodesCheckResults -eq "True" -or $this.MSIProductCodesCheckResults -eq "False" -or $this.MSIProductCodesCheckResults -eq "NotChecked"))
                                { $this.MSIProductCodesCheckResults = "False" }
                                else
                                { $this.MSIProductCodesCheckResults = "CheckError" }
                        } 
                    elseif($artefact.ArtefactCondition -eq "NotPresent")
                        { 
                            #ArtefactCondition is NotPresent
                                $artefact.ArtefactCheckResult = (!$result).ToString() 

                            #Set MSIProductCodes validation summary
                                if(!$result -and ($this.MSIProductCodesCheckResults -eq "True" -or $this.MSIProductCodesCheckResults -eq "NotChecked"))
                                { $this.MSIProductCodesCheckResults = "True" }
                                elseif($result -and ($this.MSIProductCodesCheckResults -eq "True" -or $this.MSIProductCodesCheckResults -eq "False" -or $this.MSIProductCodesCheckResults -eq "NotChecked"))
                                { $this.MSIProductCodesCheckResults = "False" }
                                elseif(!$result -and $this.ServicesCheckResults -eq "False")
                                { $this.ServicesCheckResults = "False" }                                
                                else
                                { $this.MSIProductCodesCheckResults = "CheckError" }                   
                        } 
                    else
                        { 
                            $artefact.ArtefactCheckResult = "CheckError" 
                            $this.MSIProductCodesCheckResults = "CheckError"
                        }
                }
                catch
                { 
                    $artefact.ArtefactCheckResult = "CheckError" 
                    $this.MSIProductCodesCheckResults = "CheckError"
                }    

            }

        #Validate EventLogEntrys Artefacts
            foreach($artefact in $this.EventLogEntrys)
            {

                #Check Admin Rights (required for some logs to read???? -> CheckError)
                    #[Security.Principal.WindowsIdentity]::GetCurrent().Groups -contains 'S-1-5-32-544'

                #Check if Logs exist or not
                try
                {
                    if($artefact.ArtefactType -eq "Log")
                        { $Type = @{ "LogName" = ($artefact.ArtefactLogName) } }
                    elseif($artefact.ArtefactType -eq "Provider")
                        { $Type = @{ "ProviderName" = ($artefact.ArtefactLogName) } }      
                    else
                    { 
                        $artefact.ArtefactCheckResult = "CheckError" 
                        $result = $false
                        continue
                    }
                    #Query Logname
                        #Source: https://ramblingcookiemonster.wordpress.com/2014/11/30/quick-hit-dynamic-where-object-calls/ 
                        #Build the Where array            
                            $WhereArray = @()            
            
                            #If anything but the default * was provided, evaluate these with like comparison            
                            if($artefact.ArtefactProviderName -ne "*"){$WhereArray += '$_.ProviderName -eq "$($artefact.ArtefactProviderName)"'}else {$WhereArray += '$_.ProviderName -like "*"'}           
                            if($artefact.ArtefactEventID -ne "*"){$WhereArray += '$_.Id -eq "$($artefact.ArtefactEventID)"'}else {$WhereArray += '$_.Id -like "*"'}             
                            if($artefact.ArtefactEventMessage -ne "*"){$WhereArray += '$_.Message -like "$($artefact.ArtefactEventMessage)"'}else {$WhereArray += '$_.Message -like "*"'}               
        
            
                        #Build the where array into a string by joining each statement with -and            
                            $WhereString = $WhereArray -Join " -and "            
            
                        #Create the scriptblock with your final string            
                            $WhereBlock = [scriptblock]::Create( $WhereString )                    
                            #Write-Host $WhereBlock -Verbose

                        #OLD $logs = Get-WinEvent $Type | Where-Object { $_.ProviderName -like "$($artefact.ArtefactProviderName)" -and $_.Id -like "$($artefact.ArtefactEventID)" -and $_.Message -like "$($artefact.ArtefactEventMessage)" }
                        $logs = Get-WinEvent $Type -ErrorAction SilentlyContinue | Where-Object -FilterScript $WhereBlock
                        if($logs.Count -ge 1)
                        { $result = $true }
                        else
                        { $result = $false }
                    if($artefact.ArtefactCondition -eq "Present")
                        { 
                            #ArtefactCondition is Present
                                $artefact.ArtefactCheckResult = $result.ToString()

                            #Set EventLogEntrys validation summary
                                if($result -and ($this.EventLogEntrysCheckResults -eq "True" -or $this.EventLogEntrysCheckResults -eq "NotChecked"))
                                { $this.EventLogEntrysCheckResults = "True" }
                                elseif(!$result -and ($this.EventLogEntrysCheckResults -eq "True" -or $this.EventLogEntrysCheckResults -eq "False" -or $this.EventLogEntrysCheckResults -eq "NotChecked"))
                                { $this.EventLogEntrysCheckResults = "False" }
                                else
                                { $this.EventLogEntrysCheckResults = "CheckError" }
                        } 
                    elseif($artefact.ArtefactCondition -eq "NotPresent")
                        { 
                            #ArtefactCondition is NotPresent
                                $artefact.ArtefactCheckResult = (!$result).ToString() 
                            #Set EventLogEntrys validation summary
                                if(!$result -and ($this.EventLogEntrysCheckResults -eq "True" -or $this.EventLogEntrysCheckResults -eq "NotChecked"))
                                { $this.EventLogEntrysCheckResults = "True" }
                                elseif($result -and ($this.EventLogEntrysCheckResults -eq "True" -or $this.EventLogEntrysCheckResults -eq "False" -or $this.EventLogEntrysCheckResults -eq "NotChecked"))
                                { $this.EventLogEntrysCheckResults = "False" }
                                elseif(!$result -and $this.ServicesCheckResults -eq "False")
                                { $this.ServicesCheckResults = "False" }                                
                                else
                                { $this.EventLogEntrysCheckResults = "CheckError" }                   
                        } 
                    else
                        { 
                            $artefact.ArtefactCheckResult = "CheckError" 
                            $this.EventLogEntrysCheckResults = "CheckError"
                        }

                }
                catch
                { 
                    $artefact.ArtefactCheckResult = "CheckError" 
                    $this.EventLogEntrys = "CheckError"
                }    

                <#

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
            #>
            }
        
        #Validate Services Artefacts
            foreach($artefact in $this.Services)
            {
                #Check if Services name (not Displayname) matches supplied value
                try{
                    $servicelist = Get-Service -Name "$($artefact.ArtefactValue)" -ErrorAction SilentlyContinue
                        if($servicelist.Count -ge 1)
                        { $result = $true }
                        else
                        { $result = $false  }
                    if($artefact.ArtefactCondition -eq "Present")
                        { 
                            #ArtefactCondition is Present
                                $artefact.ArtefactCheckResult = ($result).ToString() 

                            #Set Services validation summary
                                if($result -and ($this.ServicesCheckResults -eq "True" -or $this.ServicesCheckResults -eq "NotChecked"))
                                { $this.ServicesCheckResults = "True" }
                                elseif(!$result -and ($this.ServicesCheckResults -eq "True" -or $this.ServicesCheckResults -eq "False" -or $this.ServicesCheckResults -eq "NotChecked"))
                                { $this.ServicesCheckResults = "False" }
                                else
                                { $this.ServicesCheckResults = "CheckError" }   
                        } 
                    elseif($artefact.ArtefactCondition -eq "NotPresent")
                        { 
                            #ArtefactCondition is NotPresent
                                $artefact.ArtefactCheckResult = (!$result).ToString() 

                            #Set Services validation summary
                            
                                if(!$result -and ($this.ServicesCheckResults -eq "True" -or $this.ServicesCheckResults -eq "NotChecked"))
                                { $this.ServicesCheckResults = "True" }
                                elseif($result -and ($this.ServicesCheckResults -eq "True" -or $this.ServicesCheckResults -eq "False" -or $this.ServicesCheckResults -eq "NotChecked"))
                                { $this.ServicesCheckResults = "False" }
                                elseif(!$result -and $this.ServicesCheckResults -eq "False")
                                { $this.ServicesCheckResults = "False" }
                                else
                                { $this.ServicesCheckResults = "CheckError" }          
                        } 
                    else
                        { 
                            $artefact.ArtefactCheckResult = "CheckError" 
                            $this.ServicesCheckResults = "CheckError"
                        }
                }
                catch
                { 
                    $artefact.ArtefactCheckResult = "CheckError" 
                    $this.ServicesCheckResults = "CheckError"
                }    
            }
        
        #Validation results are not returned but only saved
    }

    [string]Get() {
        return $this #GENAUER????
    }
}

    $ArtefactCollection = [ArtifactCollection]::New("Progr","1.0",(get-date "26.12.2021"),(get-date),"Test-Description") # ::New is faster than New-Object
    <#
        #Firefox Artefacts
            $ArtefactCollection = [ArtifactCollection]::New("Firefox","",(get-date "15.12.2021"),(get-date),"Artefacts for Firefox Browser") # ::New is faster than New-Object
            #File
                $ArtefactCollection.AddFile("Present","C:\Program Files\Mozilla Firefox\firefox.exe","","","")
                $ArtefactCollection.AddFile("Present","C:\Program Files\Mozilla Firefox\firefox.exe","7DA44F7FD7D284E3E31F12468B89FBA7D3DC3E33B3030F74F04A6C153C0E8ABE","","")
            #Folder
                $ArtefactCollection.AddFolder("Present","C:\Program Files\Mozilla Firefox","","","")
                $ArtefactCollection.AddFolder("Present","$($env:USERPROFILE)\AppData\Local\Mozilla\Firefox\Profiles","","","")
            #Registrys
                $FirefoxPath = "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Mozilla Firefox 95.0 (x64 de)"
                $ArtefactCollection.AddRegistry("Present",$FirefoxPath,"Publisher","Mozilla")
                $ArtefactCollection.AddRegistry("Present",$FirefoxPath,"","")
                $FirefoxWildcardPath = "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Mozilla Firefox*"
                $ArtefactCollection.AddRegistry("Present",$FirefoxWildcardPath,"Publisher","Mozilla")
            #MSIProductCodes
                $ArtefactCollection.AddMSIProductCode("Present","Mozilla Firefox 95.0 (x64 de)")
            #EventLogs
                #$ArtefactCollection.AddEventLog(ArtefactCondition,ArtefactType,ArtefactLogName,ArtefactProviderName,ArtefactEventID,ArtefactEventMessage)
                $ArtefactCollection.AddEventLog("Present","Provider","Service Control Manager","","7045","*Mozilla*")   #Uses like in Where-Object. if ArtefactEventMessage contains only parts of the EventMessage -> use *MESSAGE*
                $ArtefactCollection.AddEventLog("Present","Log","Application","","1332","")
                $ArtefactCollection.AddEventLog("Present","Log","Application","Firefox Default Browser Agent","","")
                #$ArtefactCollection.AddEventLog("Present","","","","")
            #Services
            
                $ArtefactCollection.AddServices("Present","MozillaMaintenance")
                $ArtefactCollection.AddServices("Present","NNNMozillaMaintenance")
                $ArtefactCollection.AddServices("NotPresent","MozillaMaintenance")
                $ArtefactCollection.AddServices("NotPresent","NNNMozillaMaintenance")

                #Throw Errors
                    #$ArtefactCollection.AddServices("Presedsssnt","MozillaMaintenance")
                    #$ArtefactCollection.AddServices("Present","")

            $ArtefactCollection
            $ArtefactCollection.Files
            $ArtefactCollection.Folders
            $ArtefactCollection.Registrys
            $ArtefactCollection.MSIProductCodes
            $ArtefactCollection.EventLogEntrys
            $ArtefactCollection.Services
 
            $ArtefactCollection.Validate()        
            
            $ArtefactCollection
            $ArtefactCollection.Files
            $ArtefactCollection.Folders
            $ArtefactCollection.Registrys
            $ArtefactCollection.MSIProductCodes          
            $ArtefactCollection.EventLogEntrys       
            $ArtefactCollection.Services  
    #>



        <#
        File
            $ArtefactCollection.AddFile("Present","C:\temp\pwd.txt","","","")
            $ArtefactCollection.AddFile("Present","C:\temp\pwd.txt","64A3A897E15C8EED10F7BC3399B0A1B2D06D22ED00447E002060BE0BC262BDB4","NotChecked","NotChecked")
            $ArtefactCollection.AddFile("Present","C:\temp\pwd.txt","E35F8D64ADABFFDBAF69B64154177FC3C70E43EEBD362B0359D78E795CECF270","NotChecked","NotChecked")
            $ArtefactCollection.AddFile("NotPresent","C:\sdfsds","","","")

            #Throw Errors
                #$ArtefactCollection.AddFile("Presedsssnt","C:\temp\pwd.txt","","","")
                #$ArtefactCollection.AddFile("NotPresent","C:\","","","")
                #$ArtefactCollection.AddFile("Present","C:\temp\pwd.txt","","NNNNNotChecked","")
                #$ArtefactCollection.AddFile("Present","Cff:\","","")

            $ArtefactCollection.Files
           
            $ArtefactCollection.Validate()

            $ArtefactCollection.Files

       Folders
            $ArtefactCollection.AddFolder("Present","C:\","","","")
            $ArtefactCollection.AddFolder("Present","C:\sdfsds","E35F8D64ADABFFDBAF69B64154177FC3C70E43EEBD362B0359D78E795CECF270","NotChecked","NotChecked")
            $ArtefactCollection.AddFolder("NotPresent","C:\","","","")
            $ArtefactCollection.AddFolder("NotPresent","C:\sdfsds","","","")

            #Throw Errors
                #$ArtefactCollection.AddFolder("Presedsssnt","C:\","","","")
                #$ArtefactCollection.AddFolder("Present","C:\","","NNNNNotChecked","")
                #$ArtefactCollection.AddFolder("Present","Cff:\","","","")
                #$ArtefactCollection.AddFolder("Present","C:\sdfsds\","E35F8D64ADABFFDBAF69B64154177FC3C70E43EEBD362B0359D78E795CECF270","NotChecked","NotChecked")

            $ArtefactCollection.Folders
           
            $ArtefactCollection.Validate()

            $ArtefactCollection.Folders


       Registrys
            $7ZipPath = "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\{23170F69-40C1-2702-2106-000001000000}"
            $ArtefactCollection.AddRegistry("Present",$7ZipPath,"Publisher","Igor Pavlov")
            $ArtefactCollection.AddRegistry("NotPresent",$7ZipPath,"Publisher","Luke Skywalker")

            $ArtefactCollection.AddRegistry("Present",$7ZipPath,"","")
            $Wrong7ZipPath = "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\{23170F69-40C1-2702-2106-000XXXXXXXXXXXXX001000000}"
            $ArtefactCollection.AddRegistry("NotPresent",$Wrong7ZipPath,"","")

                #Throw Errors
                #$ArtefactCollection.AddRegistry("Present","HKLXXM:\SOFTWARE\","Publisher","Igor Pavlov")
                #$ArtefactCollection.AddRegistry("Present",$7ZipPath,"Publisher","")
                #$ArtefactCollection.AddRegistry("Present",$7ZipPath,"","Igor Pavlov")
                #$ArtefactCollection.AddRegistry("Presdent",$7ZipPath,"Publisher","Igor Pavlov")

            $ArtefactCollection.Registrys
           
            $ArtefactCollection.Validate()

            $ArtefactCollection.Registrys

       PathVariables
            $ArtefactCollection.AddPathVariable("Present","C:\")
            $ArtefactCollection.AddPathVariable("Present","C:\sdfsds")
            $ArtefactCollection.AddPathVariable("NotPresent","C:\")
            $ArtefactCollection.AddPathVariable("NotPresent","C:\sdfsds")

            #Throw Errors
                #$ArtefactCollection.AddPathVariable("Presedsssnt","C:\")
                #$ArtefactCollection.AddPathVariable("Present","")

            $ArtefactCollection.PathVariables
           
            $ArtefactCollection.Validate()

            $ArtefactCollection.PathVariables


        MSIProductCodes
            $ArtefactCollection.AddMSIProductCode("Present","{23170F69-40C1-2702-2106-000001000000}")
            $ArtefactCollection.AddMSIProductCode("Present","{NNN23170F69-40C1-2702-2106-000001000000}")
            $ArtefactCollection.AddMSIProductCode("NotPresent","{23170F69-40C1-2702-2106-000001000000}")
            $ArtefactCollection.AddMSIProductCode("NotPresent","{NNN23170F69-40C1-2702-2106-000001000000}")

            #Throw Errors
                #$ArtefactCollection.AddMSIProductCode("Presedsssnt","{23170F69-40C1-2702-2106-000001000000}")
                #$ArtefactCollection.AddMSIProductCode("Present","")

            $ArtefactCollection.MSIProductCodes
           
            $ArtefactCollection.Validate()

            $ArtefactCollection.MSIProductCodes
        
        
        
        Export
            $ArtefactCollection.ExportToJSON("C:\Users\admin\Desktop\TESTORDNER\testfullnotcheckedOS.json")

        Import
            $ArtefactCollection.ImportFromJSON("C:\Users\admin\Desktop\TESTORDNER\tes.json")
        #>



        
