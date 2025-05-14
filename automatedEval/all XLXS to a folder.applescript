-- Ask user to choose the root folder
set rootFolder to choose folder with prompt "Select the root folder to search for .xlsx files"

-- Get the POSIX path and folder name
set rootPath to POSIX path of rootFolder
set AppleScript's text item delimiters to "/"
set folderName to last text item of text items of rootPath
set destFolder to rootPath & folderName & " XLSXs/"

-- Create destination folder
do shell script "mkdir -p " & quoted form of destFolder

-- Find and copy all .xlsx files
do shell script "find " & quoted form of rootPath & " -type f -name '*.xlsx' -exec cp {} " & quoted form of destFolder & " \\;"

display dialog "All .xlsx files have been copied to: " & destFolder buttons {"OK"} default button "OK"
