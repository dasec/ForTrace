#Source papers
https://www.howtogeek.com/282281/how-to-delete-the-search-history-in-windows-file-explorer/
HKEY_CURRENT_USER\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Word\WordWheelQuery

https://gist.github.com/arebee/1928da03047aee4167fabee0f501c72d

#Explorer Search (Entrys with values entered in hex)
    #Validated on: Win10
    $Key = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\WordWheelQuery"
    if(Test-Path $Key)
    {
        $value = Get-ItemProperty $Key 
    }

#Cortana
    #Validated on: 

#Taskbar Search
    #Validated on: 
