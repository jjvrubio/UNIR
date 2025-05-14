-- Ask user to select folder
set folderPath to choose folder with prompt "Select the folder containing Excel files"

-- Get all Excel files in the folder
tell application "Finder"
    set excelFiles to files of folder folderPath whose name extension is "xlsx"
end tell

-- Loop through each Excel file
repeat with f in excelFiles
    set filePath to (f as alias)

    tell application "Microsoft Excel"
        try
            -- Open the Excel file
            open filePath
            set wb to active workbook

            -- Change "Sheet1" to your target worksheet name
            set ws to worksheet "Sheet1" of wb
            activate object ws

            -- Set page setup to fit to 1 A4 page
            set page setup of ws to {zoom: false, fit to pages wide: 1, fit to pages tall: 1, orientation: portrait, paper size: paper A4}

            -- Export as PDF
            set pdfName to (name of wb) & ".pdf"
            set pdfPath to ((folderPath as text) & pdfName)
            save as wb filename pdfPath file format PDF file format

            -- Close the workbook without saving changes
            close wb saving no

        on error errMsg
            -- Handle errors gracefully
            display dialog "Error processing file: " & (name of f) & return & "Error: " & errMsg
        end try
    end tell
end repeat

-- Notify user of completion
display dialog "All Excel files have been processed and saved as PDF."